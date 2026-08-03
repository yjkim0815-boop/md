---
문서유형: WORKLOG
프로젝트: sms-agent-replacement
이슈키: --
작성일: 2026-08-03
최종수정: 2026-08-03
작성자: dominic
상태: 진행중
요약: 신규 섹타나인 Agent v2.0.1(Legacy 호환) 배포본·매뉴얼·설치가이드 전수 분석 — 현행 NDSoft 대비 차이·전환 설계·리스크 12건
---

# 🛠️ WORKLOG — 섹타나인 Agent v2 전환 분석 (2026-08-03)

## 배경 / 목적
"2차 문자 서비스 전환" 건으로 **현행 NDSoft 에이전트 → 신규 섹타나인(SECTA9INE) Agent v2** 교체 개발이 확정됐다. 전달받은 배포본·매뉴얼·설치가이드를 전수 분석해 **전환 설계와 리스크**를 확정한다.

## 분석 대상 자료
로컬 원본: `D:\백업_김영준_업무 관리 문서 20260430\02_김영준\20_개발\20260803_FW [업무] 2차 문자 서비스 전환 일정 회신 및 사전 준비 사항 안내\`

| 자료 | 내용 |
|---|---|
| `NDSoft (현재 agent)/` | **현행** 설정 4종 (`agent.conf`·`jdbc.conf`·`log4j.properties`·`result.properties`) |
| `secta-agent-oracle_내부그룹사용/` | **신규** 배포본 (bin_linux·conf·lib·contents·queue·logs) |
| `섹타나인 Agent 사용자 메뉴얼 v2.0.1-Legacy호환.pdf` | 벤더 매뉴얼 (2026-04-14, 24p) |
| `20260429_섹타나인 Agent 설치 가이드_추가본_보안해제.pptx` | 내부 Dev1팀 설치 가이드 (2026-04-23, 10슬라이드) |

> 🔴 **자료 내 크리덴셜은 KB에 일절 기재하지 않는다.** 아래 분석은 구조·키 이름만 다룬다.

---

## 1. 핵심 결론 — DB 스키마가 동일하다

신규 에이전트는 **"Legacy 호환"** 빌드로, 현행과 **같은 테이블(`EM_TRAN` / `EM_TRAN_MMS` / `EM_LOG`)을 그대로 사용**한다.

> ✅ **발송 요청 주체(배치·앱)의 INSERT 코드는 원칙적으로 수정 불필요.**
> 교체 범위는 **에이전트 프로세스와 설정**에 국한된다. 이게 이번 전환의 최대 이점이다.

다만 **동작 정책·결과코드 체계는 다르다** → 아래 4·5장.

---

## 2. 현행(NDSoft) vs 신규(SECTA9INE) 대조

| 항목 | 현행 NDSoft | 신규 SECTA9INE v2.0.1 |
|---|---|---|
| 설치 경로 | `/app/ndsoft` | 배포본 기본 `/home/webdev/secta-agent` (**변경 예정**) |
| 실행 jar | `nd-message-agent-spc.jar` (2016-12) | `secta-agent.jar` (**27MB**, 2026-06) |
| 메인 클래스 | `ndsoft.message.agent.base.executor.ConsoleExecutor` | `agent.v2.Application` |
| 프레임워크 | Spring(구버전) + Hibernate + log4j 1.x | **Spring Boot 1.5.22** + MyBatis 3.4.6 + HikariCP + logback |
| 통신 | (미확인) | **Netty 4.1.128** |
| 클래스 타깃 | Java 8 | **major 52 = Java 8** ✅ |
| JVM 힙 | `-Xms64m -Xmx64m` (고정) | `XMS=128M / XMX=256M` |
| 인코딩 | `-Dfile.encoding=KSC5601` (JVM 전역) | **설정으로 제어** (`agent.sms.charset=EUC-KR`, relay 전문은 UTF-8) |
| 기동 | nohup 상주, 스크립트 미확인 | **`runner.sh {start\|stop\|status}`** ✅ |
| `process.id` | `ndsoft-agnet-sms` (오타 원문) | `secta-agent-legacy` |
| 프로파일 | 없음 | `development` / `production` (`APP_PROFILE`) |
| 인증 방식 | **소켓 직접** — 인증서버 IP:PORT + sid/mid/password | **HTTP Grant** (`{grant.url}:{port}/v2.1/auth`) → **Relay 정보 동적 수신** |
| 계정 체계 | 단일 마스터ID 1개 | **SMS·MMS 각각 별도 ID/PW** (관리자 발급) |
| 이중화 | 없음 | **멀티 host fail-over** (id×host 카르테시안 커넥션) |
| 전문 암호화 | 없음 | **AES / LEA**, level 0~3 (수신·발신번호·제목·본문) |
| 발송 금지시간 | 주석 처리(미사용) | `agent.break.use` + `break.hours` + `break.type` |
| 결과코드 매핑 | `result.properties` (약 90건) | `code.conf` (51건 + `*=d` fallback) |
| 확장 채널 | SMS/LMS/MMS | **+ 알림톡(KKO)·친구톡(KKF)·RCS** (현재 false) |
| 크리덴셜 암호화 | 불가(평문) | **Jasypt 1.9.2 내장** → `ENC()` 적용 가능성 ⭐ |

### 신규 배포본 의존 라이브러리 (fat jar, 17,176 엔트리)
`spring-boot 1.5.22.RELEASE` · `mybatis 3.4.6` · `mybatis-spring-boot-starter` · `HikariCP-java7 2.4.13` · `netty-all 4.1.128.Final` · `jasypt 1.9.2` + `jasypt-spring-boot` · `logback` · `log4jdbc-log4j2` · `tika-core` · `jackson` · Oracle JDBC · `mssql-jdbc` · `mariadb-java-client`

> ⚠️ **Spring Boot 1.5.x는 2019년 EOL.** 신규지만 프레임워크 자체는 최신이 아니다. 보안 패치 관점에서 벤더에 확인이 필요하다.

---

## 3. 신규 에이전트 구조

### 3-1. 디렉터리
```
secta-agent/
├─ bin_linux/   runner.sh(start|stop|status) · setting.sh(경로·힙·프로파일) · checkVersion.sh
├─ conf/        agent.conf · jdbc.conf · brand.conf · code.conf · mapper/oracle-secta-legacy.xml
├─ lib/         secta-agent.jar
├─ contents/    MMS 이미지 저장 (초기 비어있음)
├─ queue/       Agent Queue File (초기 비어있음)
└─ logs/        secta-agent.log (일별 롤링)
```

### 3-2. 설정 파일 역할
| 파일 | 역할 |
|---|---|
| `agent.conf` | Grant 인증·채널별 계정/정책·주기·건수·암호화·로그테이블 규칙 |
| `jdbc.conf` | Oracle 접속 + **MyBatis 매퍼 경로 지정** |
| `mapper/oracle-secta-legacy.xml` | **DDL·조회·상태변경·로그이관 SQL 전부** (테이블 자동생성 포함) |
| `code.conf` | Agent 결과코드 → **Legacy 1바이트 코드** 변환표 |
| `brand.conf` | 로그/배너/스레드명 브랜딩 (`SECTA9INE`) |

### 3-3. 동작 흐름
1. 기동 → `runner.sh` 가 `setting.sh` 로드 → `-Dagent.dir` · `-Dspring.profiles.active` 로 `java -jar` 실행
2. Grant 서버에 HTTP 인증 → **Relay(GW) 접속 정보 동적 수신**
3. `agent.conf` 의 테이블명으로 **테이블 존재 확인 → 없으면 자동 생성**(`checkTable`/`createTranTable`/`createLogTable`)
4. `fetch.delay` 주기로 `TRAN_STATUS='1'` 건을 `fetch.count` 만큼 로딩 → Relay 전송
5. 리포트 수신 → `TRAN_RSLT`·`TRAN_NET`·`TRAN_RSLTDATE` UPDATE, `TRAN_STATUS` 전이
6. `complete.delay` 주기로 완료건을 `EM_LOG_YYYYMM` 으로 이관 후 원본 DELETE

### 3-4. 상태값 / 타입 (매뉴얼 + mapper 확인)
- `TRAN_STATUS`: **1 대기 → 2 전송진행 → 3 전송성공 → 4 처리완료 → 5 DB처리실패**
- `TRAN_TYPE`: **4 = SMS**, **6 = MMS/LMS**, (매뉴얼상 **5 = URL**)
- 내부 `messageState` = `TO_NUMBER(TRAN_STATUS) - 1`

---

## 4. 🔴 결과코드 체계가 다르다 (최대 함정)

현행 `result.properties`와 신규 `code.conf`는 **둘 다 "→ Legacy 1바이트 코드" 변환표지만, 좌변(벤더 내부코드)의 의미가 다르다.**

| 코드 | 현행 NDSoft 의미 → 매핑 | 신규 SECTA9INE 의미 → 매핑 |
|---|---|---|
| `3001` | 전송큐 INSERT 실패(ID중복) → **`j`** | `E_MSG_FULL` 단말기 저장초과 → **`D`** |
| `3002` | reserved_dttm 오류 → **`q`** | `E_TIMEOUT` 전송시간 초과 → **`1`** |
| `3004` | snd_phn_id 오류 → **`q`** | `E_POWER_OFF` 전원꺼짐 → **`C`** |
| `3005` | 발송시 패스워드 오류 → **`f`** | `E_HIDDEN` 음영지역 → **`B`** |
| `1002` | 패스워드 틀림 → `d` | (해당없음) |
| `1102` | (해당없음) | `E_INVALID_PWD` 잘못된 암호 → `d` |

> 🔴 **같은 숫자가 전혀 다른 의미다.** 현행 `result.properties`를 신규에 그대로 이식하면 **결과코드가 조용히 오염**된다. 실패 통계·재발송 로직·CS 응대가 전부 틀어진다.
> ✅ **반드시 신규 `code.conf`(벤더 제공본)를 기준으로 하고, 현행 매핑은 "Legacy 1바이트 코드 쪽"만 대조 검증한다.**

### 커버리지 차이
- 현행: 약 90개 코드 정의, **fallback 없음**
- 신규: 51개 + **`*=d`(미정의 전부 '기타')**
- → 신규는 미정의 코드가 전부 `d`로 뭉개진다. **운영 초기 `d` 비율 급증 여부를 모니터링**해야 한다.

### Legacy 1바이트 코드 (양쪽 공통 목적지)
`0`성공 · `1`TIMEOUT · `A`호처리중 · `B`음영 · `C`전원꺼짐 · `D`저장초과 · `2`잘못된번호 · `a`서비스정지 · `b`단말기문제 · `c`착신거절 · `d`기타 · `e`SMC형식오류 · `f`대행사형식오류 · `g`MMS불가단말 · `i`대행사삭제 · `j`SMC운영자삭제 · `k`Que Full · `l`이통사스팸 · `n`대행사스팸 · `o`건수제한 · `p`길이초과 · `q`번호형식오류 · `x`필드형식오류 · `z`MMS콘텐츠참조불가

---

## 5. 🔴 발송 정책 차이 (운영 사고 직결)

| 항목 | 현행 | 신규 배포본 | 매뉴얼 권장/제약 | 판정 |
|---|---|---|---|---|
| **발송 대기 유효시간** | `spc.db.fetch.before.hour=0` (**무제한**) | `agent.sms.fetch.hour=1` | 기본 4, 1~100 | 🔴 **1시간 지난 대기건은 실패 처리 후 로그이관.** 배치 지연 시 **대량 자동 실패** 가능 |
| **결과 타임아웃** | — | `agent.sms.timeout.hour=5` | 기본 25, **24~100 이내** | 🟠 **매뉴얼 허용 범위(24~100) 밖.** 벤더 확인 필요 |
| MMS 대기/타임아웃 | — | 24 / 48 | 4 / 48 | 🟡 대기 24h는 기본(4)보다 김 |
| fetch 주기 | 1000ms | `fetch.delay=1`(초) | 1~10 | ✅ 동일 |
| 완료 이관 주기 | 60000ms(60초) | `complete.delay=10`(초) | 1~10 | 🟡 **6배 빨라짐** — DB 부하 재평가 |
| SMS fetch 건수 | (설정 없음) | 600 | 기본 200 | 🟠 기본값의 3배. 속도 영향 경고 있음 |
| MMS 이미지 최대크기 | — | 500KB / 합계 1500KB | 300 / 1024 | 🟠 매뉴얼 상한 초과 |
| 발송금지시간 | 미사용 | `break.use=false` | 기본 true | ✅ 현행 유지 |

> ⚠️ **`agent.break.hours` 라인은 `break.use=false` 여도 절대 삭제 금지.** 배포본 주석에 명시 — `FetchServiceImpl` 생성자가 `@Value` 로 무조건 resolve 하므로 **라인이 없으면 기동 실패**한다.

---

## 6. 🔴 배포본 mapper의 스키마 결함

`oracle-secta-legacy.xml` 의 DDL에서 **전송 테이블과 로그 테이블의 `TRAN_REFKEY` 길이가 다르다.**

| 테이블 | 컬럼 | 길이 |
|---|---|---|
| `createTranTable` (EM_TRAN) | `TRAN_REFKEY` | **VARCHAR2(40)** |
| `createLogTable` (EM_LOG) | `TRAN_REFKEY` | **VARCHAR2(20)** |

`insertLogTranTable` 은 `EM_TRAN → EM_LOG` 로 **컬럼 그대로 복사**한다.
> 🔴 **`TRAN_REFKEY` 가 21자 이상이면 로그 이관 시 `ORA-12899` 로 실패** → `TRAN_STATUS=5`(DB 처리 실패)로 남는다.
> 현행 운영에서 `TRAN_REFKEY` 를 쓰는지 먼저 확인하고, 쓴다면 **벤더에 DDL 정정 요청** 또는 로그 테이블 컬럼을 40으로 맞춘다.

**추가 확인 필요**: 매뉴얼 5장 표는 `TRAN_ID VARCHAR2(20)`·`TRAN_PHONE VARCHAR2(20)` 등 표 정렬이 깨져 있어 **mapper DDL을 정본으로 삼아야 한다**(mapper: `TRAN_ID VARCHAR2(20)`, `TRAN_PHONE VARCHAR2(15)`, `TRAN_MSG VARCHAR2(255)`).

### 시퀀스 명칭 불일치
- 매뉴얼 5장 표: `EM_TRAN_PR` (EM_TRAN용), `EM_TRAN_MMS_SEQ`
- 매뉴얼 5장 서두: **"시퀀스는 Table name 에 `_SEQ` 형태로 생성"** → `EM_TRAN_SEQ`
- 테스트 SQL: `em_tran_pr.nextval`
> 🟠 **매뉴얼 내부에서 이미 불일치.** 현행 DB의 실제 시퀀스명을 조회해 확정해야 한다. (mapper DDL에는 시퀀스 생성문이 **없음** → 기존 시퀀스 재사용 전제)

---

## 7. 🔴 URL 타입(TRAN_TYPE=5) 미처리

매뉴얼은 `tran_type` 을 **4=SMS / 5=URL / 6=MMS** 로 정의하지만, `oracle-secta-legacy.xml` 의 `fetchMessages`·`selectMessages` 는 **`TRAN_TYPE = 4` 또는 `= 6` 만 조회**한다.

> 🔴 **현행에서 `TRAN_TYPE=5`(URL 전송)를 사용 중이라면, 전환 후 해당 건은 영원히 fetch되지 않고 `TRAN_STATUS=1`로 적체된다.**
> **사전 확인 필수**: `SELECT TRAN_TYPE, COUNT(*) FROM EM_TRAN GROUP BY TRAN_TYPE` + 로그 테이블 동일 집계.

---

## 8. 접속 정보 — 배포본 값과 내부 가이드가 불일치

| 항목 | 배포본 `agent.conf` | 내부 설치가이드(PPTX) |
|---|---|---|
| Grant 서버 | `50.0.111.73` : `5100` | **사내망 `10.0.111.252`(L4 VIP)** / 외부 공인 `110.45.199.252` |
| DB | `50.0.113.73:1521:SMSON` (SMS_WEB) | 업무별 DB — Dev1팀 VAN은 `TMS` 계정 |
| TABLESPACE (mapper) | `TS_SMS_WEB` (**6곳**) | 업무 DB에 맞게 **인프라팀 문의 후 6곳 전부 수정** |
| 계정 | `secta-test-01-SMS/MMS` (테스트) | **관리자가 Agent별 ID/PW 발급 예정** |
| 이미지 경로 | `/home/webdev/secta-agent/contents` | 업무별 경로(NAS 등), **에이전트 서버와 동일 경로여야 함** |

> 🟠 **배포본은 "내부그룹사용" 샘플이다.** 위 5개 값은 전부 우리 환경 값으로 교체해야 하며, 특히 **Grant 서버는 사내망 L4 VIP(`10.0.111.252`)를 써야 할 가능성이 높다** — 배치서버가 IDC 사내망이므로. 벤더/인프라 확인 필요.

우리 환경 전제:
- DB는 **현행 NDSoft가 붙는 것과 동일한 Oracle**(SPC 홈페이지 RDS)로 맞춰야 한다 → 현행 `jdbc.conf` 기준
- 설치 경로는 `/home/webdev/...` 가 아니라 **`/app/` 하위**(현행 `/app/ndsoft` 관례)로 통일 권장

---

## 9. ⭐ 전환으로 개선되는 점

1. **`runner.sh start|stop|status`** — 현행의 수동 nohup 대비 운영성 개선. `status` 로 헬스체크 가능
2. **`checkVersion.sh`** — 배포 버전 검증 수단 확보 (현행에는 없음)
3. **Jasypt 내장** → `jdbc.password` 를 `ENC(...)` 로 암호화 가능성. **현행 평문 크리덴셜 문제를 해결할 수 있는 지점** (벤더에 지원 여부 확인 필요)
4. **전문 암호화(AES/LEA, level 0~3)** — 수신번호·본문까지 암호화 가능. 개인정보 관점에서 **level 상향 검토 권장**(배포본은 0)
5. **멀티 host fail-over** — 단일 게이트웨이 장애 대응
6. **알림톡·친구톡·RCS 확장 여지** — 향후 채널 확대 시 에이전트 교체 불필요
7. **힙 64MB → 128/256MB**, logback 일별 롤링
8. **로그 테이블 사전 생성**(`table.log.spare`) — 월 경계 장애 예방

---

## 10. 리스크 정리 (12건)

| # | 심각도 | 리스크 | 대응 |
|---|---|---|---|
| 1 | 🔴 | **결과코드 체계 상이** — 같은 숫자 다른 의미 | 벤더 `code.conf` 기준 채택, 현행 매핑은 Legacy 코드 쪽만 대조 |
| 2 | 🔴 | **`fetch.hour=1`** — 1시간 초과 대기건 자동 실패 | 현행 무제한 → 정책 변경. 배치 지연 패턴 분석 후 값 상향 |
| 3 | 🔴 | **`TRAN_TYPE=5`(URL) 미처리** | 사전 사용량 집계 → 사용 중이면 벤더에 mapper 수정 요청 |
| 4 | 🔴 | **로그 테이블 `TRAN_REFKEY` 20 vs 40** | 이관 실패(ORA-12899) 위험. DDL 정정 |
| 5 | 🔴 | **운영 DB 크리덴셜 평문 노출** (현행·신규 공통, 백업 폴더 포함) | Jasypt 암호화 검토 + 파일 권한 + 백업본 정리 |
| 6 | 🟠 | `timeout.hour=5` 가 매뉴얼 허용범위(24~100) 밖 | 벤더 확인 |
| 7 | 🟠 | Grant 서버 IP 배포본 vs 가이드 불일치 | 사내망 L4 VIP 여부 확인 |
| 8 | 🟠 | `fetch.count=600` (기본 200의 3배) | 속도 영향 경고 — 부하 테스트로 확정 |
| 9 | 🟠 | MMS 이미지 상한이 매뉴얼 초과(500/1500KB) | 벤더 확인 |
| 10 | 🟡 | `complete.delay` 60초 → 10초 (DB 부하 6배) | 이관 배치 부하 측정 |
| 11 | 🟡 | Spring Boot 1.5.22 = **2019 EOL** | 보안 패치 정책 벤더 확인 |
| 12 | 🟡 | 여전히 systemd 미등록(nohup) | 이번 기회에 **systemd 유닛 등록 검토** |

---

## 11. 전환 작업 계획 (초안)

### Phase 1 — 사전 조사 (현행 운영 실측)
- [ ] `SELECT TRAN_TYPE, COUNT(*) FROM EM_TRAN GROUP BY TRAN_TYPE` (+ 로그 테이블) → **URL 타입 사용 여부**
- [ ] `TRAN_REFKEY` 사용 여부 및 최대 길이
- [ ] 현행 EM_LOG 월테이블 **실제 명명 규칙**(`EM_LOG_YYYYMM` 여부)
- [ ] 현행 시퀀스 실제 명칭
- [ ] 일/시간대별 발송량 피크, 대기건 적체 패턴 → `fetch.hour`·`fetch.count` 산정 근거
- [ ] 현행 `TRAN_RSLT` 값 분포 → 신규 `code.conf` 매핑 커버리지 검증

### Phase 2 — 계정·환경 확보
- [ ] 섹타나인 관리자로부터 **SMS·MMS ID/PW 발급**
- [ ] Grant 서버 접속 경로 확정 (사내망 L4 VIP vs 공인 IP) + **방화벽 오픈**
- [ ] 배치서버 → Relay 서버 구간 정책 확인
- [ ] TABLESPACE 확인 (인프라팀) → mapper **6곳 전부** 치환
- [ ] MMS 이미지 경로 확정 (현행 경로 승계)

### Phase 3 — 설치·설정
- [ ] 설치 경로 `/app/secta-agent`(가칭) — `/home/webdev` 아님
- [ ] `setting.sh`: `APP_HOME`·`JAVA_HOME`(기존 JDK8 재사용)·`XMS/XMX`·`APP_PROFILE=production`
- [ ] `jdbc.conf`: 현행과 동일 Oracle. **Jasypt 암호화 적용 검토**
- [ ] `agent.conf`: 계정·테이블명·주기·건수·`break.hours` 라인 유지
- [ ] `code.conf`: 벤더 제공본 기준 + 현행 대조 검증

### Phase 4 — 검증
- [ ] `checkVersion.sh` 로 버전 확인
- [ ] `runner.sh start` → `logs/secta-agent.log` 에 ERROR/FAIL 없는지, **Connection 로그** 확인
- [ ] 테스트 번호로 SMS/LMS/MMS 각 1건 INSERT → `TRAN_STATUS` 1→3→4 전이 확인
- [ ] `EM_LOG_YYYYMM` 이관 확인 (`TRAN_STATUS=5` 없는지)
- [ ] `TRAN_RSLT` 값이 Legacy 1바이트 코드로 저장되는지

### Phase 5 — 전환
- [ ] **병행 운영 불가** — 같은 테이블을 두 에이전트가 폴링하면 **중복 발송**. 반드시 **현행 정지 → 신규 기동** 순서
- [ ] 전환 시점 대기건(`TRAN_STATUS=1,2`) 처리 방안 확정
- [ ] 롤백 절차 확보 (현행 `/app/ndsoft` **삭제 금지**, 원복 가능 상태 유지)
- [ ] systemd 등록 검토

---

## 12. 🔴 보안 조치 필요 (즉시)

분석 대상 폴더에 **운영 Oracle 접속 크리덴셜이 평문**으로 존재한다. 현행 `jdbc.conf` 의 접속 대상은 [server-env.md](../../../shared/server-env.md) 에 기록된 **SPC 홈페이지 운영 Oracle RDS**와 동일하며, 계정도 **관리자 권한 계정**이다.

- 위치: 개인 PC의 백업 폴더(`D:\백업_...`) + 배치서버 `/app/ndsoft/conf/jdbc.conf`
- 신규 배포본 `conf/` 에도 샘플 크리덴셜 평문 존재
- 대응: ① 백업 폴더 접근 통제/정리 ② 서버 conf 파일 권한 최소화(`600`) ③ **Jasypt 암호화 적용** ④ 전환 완료 후 **DB 계정 비밀번호 교체** 검토

> [README 횡단 취약 패턴](../../../README.md)의 **하드코딩 시크릿 7번째 사례**. 기준: [security-review.md](../../../shared/security-review.md)

---

# 13. 현행 NDSoft 에이전트 전수 분석 (2026-08-03 추가)

서버 `/app/ndsoft` 전체(로그 제외)를 확보해 **jar 내부까지 해부**했다. 로컬: `…\NDSoft (현재 agent)\ndsoft\`

## 13-1. 실물 구성 — 11개 파일 / 15.09 MB

| 경로 | 크기 | 날짜 | 비고 |
|---|---:|---|---|
| `bin/runner` | 1,474 | 2016-12-06 | **`runner-unix.sh` 와 SHA256 동일**(중복본) |
| `bin/runner-unix.sh` | 1,474 | 2016-12-06 | **실기동 스크립트**(start\|stop) |
| `bin/serviceInstall.bat` | 454 | 2016-12-06 | Windows 서비스 등록 — **리눅스 불필요** |
| `bin/JavaService32.exe` | 98,304 | 2016-12-06 | Windows 래퍼 — 불필요 |
| `bin/JavaService64.exe` | 139,264 | 2016-12-06 | 〃 |
| `conf/agent.conf` | 2,071 | **2017-04-05** | 메인 설정 |
| `conf/agent.bak` | 2,069 | 2016-12-06 | 백업 |
| `conf/jdbc.conf` | 618 | 2016-12-06 | DB 접속 |
| `conf/log4j.properties` | 1,483 | 2016-12-06 | 로그 |
| `conf/result.properties` | 4,966 | 2016-12-06 | 결과코드 매핑 |
| `lib/nd-message-agent-spc.jar` | **15,569,534** | 2016-12-06 | 본체 |

> 📌 **2026-04 변경 이력 규명**: `bin`·`conf` **디렉터리** mtime 만 2026-04 이고 **내부 파일은 전부 2016~2017 원본**이다. 4월 작업은 내용 수정이 아니라 **엔트리 추가/삭제/이름변경**이었다. ⚠️ **운영 커스터마이징이 전혀 없다** → 이관 범위가 conf 로 한정된다.

## 13-2. 기동 스크립트 해부 (`runner-unix.sh`)

```sh
APP_BASE=../ ;  EXECUTE_JAR=$APP_BASE/lib/nd-message-agent-spc.jar
XMS=64m ; XMX=64m ; JVM_OPTS="-XX:+PrintGCDetails"
PROCESS_ID=ndsoft-agnet-sms ; APP_NAME="ND-SMSAgent"
APP_LOG_FILE=$LOG_BASE/ndsoft-agent.out       # = ../logs/ndsoft-agent.out
# start: cd $APP_HOME/bin → nohup java … -cp $EXECUTE_JAR $EXECUTE_CLASS 1>$APP_LOG_FILE 2>&1 &
# stop : kill $PID        (SIGTERM)
```
- ✅ **`ps` 출력과 완전 일치.** `-cp ..//lib/…` 의 이중 슬래시는 `APP_BASE=../` + `/lib/` 조합 결과였다.
- ✅ **기동 절차 확정**: `cd /app/ndsoft/bin && sh runner-unix.sh start` · 정지 `sh runner-unix.sh stop`
- 🔴 **`status` 옵션 없음**(start\|stop 만). 신규 섹타나인 `runner.sh` 는 status 지원 → 운영성 개선
- 🔴 프로세스 판정이 `ps -ef | grep java | grep $PROCESS_ID` — **경계 없는 grep**(신규는 `-- "-Dprocess.id=$PROCESS_ID "` 공백 경계) → 오탐 여지
- 🟡 `bin/runner` 는 바이트 동일 **중복본**
- 🟡 `serviceInstall.bat` 은 **JDK `1.6.0_25` 하드코딩** + `-Xmx%XMS% -Xmx%XMX%`(**`-Xms` 누락 오타**). 리눅스 운영 영향은 없으나 패키지 품질의 방증

## 13-3. 🔴 발송 방식 확정 — **DB 폴링 + 소켓 상주 하이브리드**

미해결 항목이 jar 내부 `applicationContext-custom.xml` 로 확정됐다. **Spring `task:scheduled` 7종**(스레드풀 7).

| 메서드 | 주기 | 역할 |
|---|---|---|
| `handleFetch` | `${agent.queue.fetch.milisecond}` = **1,000ms** | **DB 발송대기 로딩** |
| `handleSendMessage` | **10ms** | 큐 → **소켓 전송** |
| `handleCheckAlive` | 1,000ms | **게이트웨이 연결 확인** |
| `handleException` | 15,000ms | 예외 처리 |
| `handleTransferCompleted` | `${agent.complete.transfer.milisecond}` = **60,000ms** | 완료건 이력 이관 |
| `handleCheckHistoryTable` | **cron `0 0 * * * *`**(매시 정각) | 이력 테이블 확인·생성 |
| `monitorResource` | 10,000ms | 힙 모니터 |

- **DB 접근**: `RequestInfoDAO` → **JdbcTemplate**. `persistence.xml`·Hibernate 가 동봉돼 있으나 **DAO 는 JPA 미사용**(잔재)
- **커넥션풀**: **c3p0** `ComboPooledDataSource` — init 10 / min 10 / max 50, `acquireRetryAttempts=30`, `idleConnectionTestPeriod=300`, `testConnectionOnCheckin=true`, `preferredTestQuery=SELECT 1 FROM DUAL`
- **소켓**: **Netty 3.5.8** — `MessageAgentAuthorizePipelineFactory`(인증) → `MessageAgentWorkerPipelineFactory`(전송), `ChannelManager` 로 채널 유지
- ⚠️ `resultCdProperties` 가 **`file:../conf/result.properties`** 상대경로 → **`bin` 에서 기동해야 하는 두 번째 이유**

> ✅ 신규 섹타나인도 **DB 폴링 + Relay 소켓** 이라 **아키텍처가 개념적으로 동일**하다. 전환 난이도를 낮추는 요소.

## 13-4. 프로토콜 — `skb` 패킷 체계

`ndsoft.framework.message.protocol.skb.*` 에 **요청/응답 6쌍**이 정의돼 있다.

| 패킷 | 용도 |
|---|---|
| `RequestAuthenticationBody` / `Response~` | 인증 (`agent.sid`/`mid`/`password`) |
| `RequestServerListBody` / `Response~` + `SubmitServerInfo` | **발송 서버 목록 동적 수신** |
| `RequestSendMessageBody` / `Response~` | 메시지 전송 |
| `RequestSendResultBody` / `Response~` | 발송 결과 수신 |
| `RequestCheckAliveBody` / `Response~` | 헬스체크 |
| `RequestControlCommandBody` / `Response~` | 제어 명령 |

> ⭐ 현행도 **인증 서버에서 발송 서버 목록을 동적으로 받는다.** 신규의 **Grant 인증 → Relay 정보 동적 수신**과 **같은 패턴** → "인증서버만 열면 나머지는 동적"이라는 **방화벽 설계를 그대로 재사용** 가능.

## 13-5. 🔴 암호화 알고리즘이 다르다 — ARIA vs AES/LEA

jar 에 **국산 표준 블록암호 ARIA** 구현이 내장돼 있다: `kr.cipher.aria.{ARIA, ARIAEngine, Cipher}` · `kr.cipher.padding.{AnsiX923Padding, BlockPadding}` · `kr.cipher.base64.Base64` · `ndsoft.framework.core.helper.CryptoHelper`.

| | 현행 NDSoft | 신규 섹타나인 |
|---|---|---|
| 지원 암호 | **ARIA** | **AES / LEA** (`agent.encrypt.kind`) |
| 적용 범위 | 미확인 | level 0~3(수신·발신번호·제목·본문) |
| 현재 설정 | `agent.conf` 에 **암호화 키 없음 → 미사용 추정** | 배포본 `encrypt.level=0`(미사용) |

> 🟠 양쪽 다 현재는 미사용으로 보이나 **알고리즘 자체가 다르다.** 현행이 실제로 암호화를 쓰고 있었다면 게이트웨이 복호화 규격까지 바뀌므로 **벤더 확인 필요**(다만 관련 키 부재로 미사용 가능성이 높다).

## 13-6. 런타임·의존성 (EOL 심각)

| 항목 | 현행 NDSoft | 신규 섹타나인 |
|---|---|---|
| **클래스 타깃** | **major 49 = Java 5** | major 52 = Java 8 |
| 빌드 JDK | **`1.6.0_29`** (2011) | 2026-06 빌드 |
| 빌드 주체 | `Built-By: NDS-GWB$` / Apache Maven | — |
| **버전** | **`nd-message-agent-spc 1.6.9-SNAPSHOT`** | `v2.0.1` (정식) |
| 프레임워크 | `ndsoft-framework-* 1.6.6` | — |
| ORM | Hibernate **3.6.9**(2012) + JPA 2.0 *(실사용 JdbcTemplate)* | MyBatis 3.4.6 |
| 네트워크 | Netty **3.5.8**(2012) | Netty **4.1.128** |
| DI | Spring 3.x | Spring Boot 1.5.22 |
| 로깅 | slf4j 1.5.8 + log4j 1.x | logback |
| 커넥션풀 | **c3p0** | **HikariCP** |
| 드라이버 | Oracle + **MSSQL**(`microsoft.sql.*`) | Oracle + MSSQL + MariaDB |

> 🔴 **운영에 SNAPSHOT 빌드가 배포돼 있다**(`1.6.9-SNAPSHOT`). 정식 릴리스가 아니며 **형상 재현이 보장되지 않는 상태로 10년 운영**됐다.
> 🔴 **Java 5 타깃 · 2011~2012년 의존성** — 보안 패치가 사실상 불가능. **교체 정당성이 명확해졌다.**
> 🟡 jar 10,249 엔트리 중 **자체 코드는 112 클래스뿐**(나머지는 동봉 의존성: `org` 7,076 · `oracle` 861 등).

## 13-7. 🔴 로그 미정리 원인 규명

| 파일 | 출처 | 로테이션 |
|---|---|---|
| `logs/ndsoft-agent.out` | `runner-unix.sh` stdout 리다이렉트 | **없음 — 무한 증가** |
| `logs/ndsoft-agent-sms-real-full.log` | log4j `DailyRollingFileAppender` | 일별 회전, **삭제 정책 없음** |
| `logs/ndsoft-agent-sms-real-simple.log` | 〃 | 〃 |

- 🔴 `DailyRollingFileAppender` 는 **`maxBackupIndex` 미지원** → 일별 파일 **영구 누적**. `logs` 엔트리 과다의 직접 원인.
- 🔴 `-XX:+PrintGCDetails` 상시 활성 출력이 `.out` 으로 흘러 **회전 없이 계속 증가**.
- ✅ 신규는 logback 일별 롤링 → 개선. 단 **보관 기간 정책은 별도 설정 필요**.

## 13-8. 이관 자산 목록 (확정)

| 자산 | 이관 | 사유 |
|---|:---:|---|
| `conf/agent.conf` | ✅ 값 참조 | 계정·주기·건수·테이블명의 **현행 기준값** |
| `conf/jdbc.conf` | ✅ 값 참조 | 신규도 **동일 DB** 사용 |
| `conf/result.properties` | ⚠️ 대조만 | 코드 체계 상이 — **그대로 이식 금지**(§4) |
| `conf/log4j.properties` | ❌ | 신규는 logback |
| `conf/agent.bak` | ❌ | 2016 백업본 |
| `lib/*.jar` · `bin/runner*` | ❌ | 폐기 / 신규 `runner.sh` 사용 |
| `bin/*.exe` · `*.bat` | ❌ | Windows 전용 |

> ✅ **운영 중 추가된 커스텀 파일·스크립트가 없다** → 이관 범위가 conf 3개(참조용)로 한정, 전환 리스크가 낮다.

## 13-9. 해소된 미확인 항목

| 기존 미확인 | 결과 |
|---|---|
| 발송 방식 | ✅ **하이브리드** — 1초 DB 폴링 + Netty 소켓 상주 |
| 큐 테이블·주기 | ✅ `EM_TRAN`/`EM_LOG`/`EM_TRAN_MMS`, fetch 1s / 완료이관 60s / 이력테이블 매시 정각 |
| 게이트웨이 엔드포인트 | ✅ 인증서버 1개 고정, **발송 서버는 동적 수신**(`RequestServerListBody`) |
| 기동/재기동 스크립트 | ✅ `bin/runner-unix.sh {start\|stop}` (status 없음) |
| 2026-04 변경 이력 | ✅ **내용 변경 아님** — 디렉터리 엔트리 변동. 커스터마이징 없음 |
| 로그 미정리 원인 | ✅ `.out` 무회전 + `DailyRollingFileAppender` 삭제정책 부재 |
| `agent.bak` → `agent.conf` diff | ✅ **실행 완료** — 아래 13-11 |

## 13-11. ✅ 2017-04-05 변경 내용 규명 (`agent.bak` → `agent.conf`)

2바이트 차이의 정체는 **단일 값 조정이 아니라 연동 계정 3종의 통째 교체**였다.

| 키 | 변경 |
|---|---|
| `agent.sid.0` | 4자리 ID **변경** |
| `agent.mid.0` | 마스터ID **`happypass_*` 계열 → `happycustom_*` 계열** |
| `agent.password.0` | **교체** (값 미기재) |

- **인증서버 IP·포트, 폴링 주기, 테이블명 등 나머지 설정은 전부 동일**하다.
- 즉 2017-04-05 작업은 **"발송 계정 전환"** 이었다. `happypass`(구) → `happycustom`(현) 으로 **서비스 계정 자체가 바뀌었다**.
- 🟠 **전환 시 시사점**: 신규 섹타나인도 **SMS/MMS 계정을 관리자에게 신규 발급**받아야 한다(§8). 현행 계정을 그대로 쓰는 것이 아니므로, **과거에도 계정 전환 선례가 있었다**는 점이 참고가 된다.
- ⚠️ 값은 KB에 기재하지 않는다. 필요 시 서버 `conf/agent.conf` 원본 참조.

## 13-10. 추가 리스크 (기존 12건 + 6건)

| # | 심각도 | 리스크 |
|---|---|---|
| 13 | 🔴 | **운영에 SNAPSHOT 빌드 배포**(`1.6.9-SNAPSHOT`) — 형상 재현 불가 |
| 14 | 🔴 | **Java 5 타깃 / 2011~2012 의존성** — 보안 패치 불가 |
| 15 | 🟠 | **ARIA ↔ AES/LEA 알고리즘 상이** — 현행 암호화 사용 여부 확인 필요 |
| 16 | 🟠 | `runner-unix.sh` **경계 없는 grep** 프로세스 판정 → 오탐 여지 |
| 17 | 🟡 | `ndsoft-agent.out` **무회전** — 디스크 증가 지속 |
| 18 | 🟡 | `bin/runner` 중복본 · Windows 파일 3종 사장 |

---

# 14. 설정 이식 가능성 분석 — "현행 값으로 배포본을 그대로 올려도 되나?" (2026-08-03)

## 14-1. 결론: **불가.** 신규 발급·신규 확인이 필요한 값이 3종 있다

| 판정 | 항목 | 사유 |
|---|---|---|
| 🔴 **불가** | `agent.sms.api.id` / `pw`, `agent.mms.api.id` / `pw` | 현행 `agent.sid/mid/password` 는 **NDSoft 게이트웨이 전용 자격증명**. 섹타나인 망에서 인증 불가 → **섹타나인 관리자 신규 발급 필수**(SMS·MMS 별도) |
| 🔴 **불가** | `agent.grant.url` / `port` | 현행 인증서버(NDSoft)와 **완전히 다른 인프라**. 배포본 값 vs 내부 가이드 값 불일치(§8) → 확정 + **방화벽 오픈** 필요 |
| 🔴 **불가** | mapper `TABLESPACE` (6곳) | 배포본은 `TS_SMS_WEB` 샘플. **현행 DB의 실제 TABLESPACE 확인 필요**(인프라팀) |
| ✅ 승계 | `jdbc.conf` 접속정보 | **동일 Oracle·동일 스키마** 사용 |
| ✅ 승계 | 테이블명 `EM_TRAN` / `EM_LOG` / `EM_TRAN_MMS` | Legacy 호환 빌드라 동일 |
| ⚠️ 대조만 | `result.properties` → `code.conf` | **코드 체계 상이 — 그대로 이식 금지**(§4) |

> ✅ **DB·테이블은 그대로 간다.** 막힌 건 **게이트웨이 연동 3종(계정·주소·방화벽)** 뿐이며, 이는 벤더/인프라 협조 사항이지 개발 이슈가 아니다.

## 14-2. 설정 1:1 매핑표 (현행 → 신규)

| 현행 NDSoft `agent.conf` | 현행 값 | 신규 섹타나인 대응 | 판정 |
|---|---|---|---|
| `agent.authentication.server.ip.0` / `.port.0` | 사내 IP:24901 | `agent.grant.url` / `agent.grant.port` (+`grant.auth.path=v2.1/auth`) | 🔴 **신규 확인** |
| `agent.sid.0` / `mid.0` / `password.0` | (계정 3종) | `agent.sms.api.id`/`pw`, `agent.mms.api.id`/`pw` | 🔴 **신규 발급** |
| `agent.account.count=1` | 1 | (없음 — id 콤마 다중입력으로 대체) | — |
| `agent.async.pool.size=10` | 10 | `agent.send.proc.count` / `report.proc.count` / `wait.proc.count` | 🟡 구조 다름 |
| `agent.queue.fetch.milisecond=1000` | 1초 | `agent.fetch.delay=1` (초) | ✅ **동등** |
| `agent.complete.transfer.milisecond=60000` | 60초 | `agent.complete.delay=10` (초) | 🟠 **6배 빨라짐** |
| `agent.complete.transfer.use=1` | 사용 | (상시 동작) | ✅ |
| `spc.db.fetch.before.hour=0` | **무제한** | `agent.sms.fetch.hour=1` | 🔴 **정책 변경**(§5) |
| `spc.db.order.by=1` | 사용 | mapper `ORDER BY A.TRAN_PR ASC` 고정 | ✅ **동등** |
| `spc.manage.history.table=month` | 월별 | `agent.table.log.type=2` + `table.log.year=4` | ✅ **동등** |
| `spc.manage.send.time.start/finish` | **주석(미사용)** | `agent.break.use=false` + `break.hours` | ✅ 동등(미사용 유지) |
| `db.table.name.em_tran` | `EM_TRAN` | `agent.sms.table.name.tran` / `agent.mms.table.name.tran` | ✅ |
| `db.table.name.em_log` | `EM_LOG` | `agent.sms.table.name.log` / `agent.mms.table.name.log` | ✅ |
| `db.table.name.em_tran_mms` | `EM_TRAN_MMS` | **키 없음** — mapper가 `${tableName}_MMS` 로 자동 참조 | ✅ **자동** |
| `spc.db.charset=WE8DEC` | 주석 | `agent.sms.charset=EUC-KR` / `mms.charset` | 🟡 확인 |
| `-Dfile.encoding=KSC5601` (JVM) | JVM 전역 | **설정으로 이동**(`*.charset`), relay 전문은 UTF-8 고정 | ✅ 개선 |
| `agent.protocol.version` / `client.version` / `client.type` | NDSoft 규격 | (섹타나인 자체 규격) | — |
| — | — | `agent.encrypt.kind=AES` / `*.encrypt.level` | 🟠 현행 ARIA와 상이(§13-5) |

| 현행 `jdbc.conf` | 신규 `jdbc.conf` | 판정 |
|---|---|---|
| `jdbc.driver` / `url` / `username` / `password` | 동일 키 | ✅ **값 승계** |
| `jdbc.init/max/min.pool.size` (10/50/10) | **키 없음** — HikariCP 기본값 | 🟡 부하 재평가 |
| `jdbc.validation.query=SELECT 1 FROM DUAL` | 키 없음 | 🟡 |
| — | `mybatis.mapper.location` | 신규 필수 |

> 🟠 **배포본 `jdbc.driver` 가 `net.sf.log4jdbc.sql.jdbcapi.DriverSpy`, url 이 `jdbc:log4jdbc:oracle:thin:@…`** 로 **SQL 로깅 래퍼**가 끼워져 있다. 개발·디버깅용이며 **운영에는 성능 부담**이다. → **순수 `oracle.jdbc.OracleDriver` + `jdbc:oracle:thin:@…` 로 변경 권장**(벤더 확인).

## 14-3. 그 외 반드시 손봐야 할 값

| 파일 | 항목 | 배포본 값 | 조치 |
|---|---|---|---|
| `bin_linux/setting.sh` | `APP_HOME` | `/home/webdev/secta-agent` | **`/app/secta-agent`**(가칭)로 변경 — 현행 `/app/` 관례 |
| 〃 | `JAVA_HOME` | `/usr` | 서버 `which java` 기준(기존 JDK8 재사용 가능) |
| 〃 | `APP_PROFILE` | `development` | **`production`** |
| 〃 | `XMS/XMX` | 128M/256M | 현행 64M 대비 상향 — 유지 권장 |
| `conf/agent.conf` | `agent.contents.path` | `/home/webdev/secta-agent/contents` | **MMS 이미지 경로** — 현행 경로 승계, **에이전트 서버와 동일 경로여야 함** |
| 〃 | `agent.break.hours` | `0,1,2,3,4,5` | ⚠️ **`break.use=false` 여도 라인 삭제 금지**(삭제 시 기동 실패) |
| 〃 | `agent.sms.fetch.count` | 600 | 매뉴얼 기본 200의 3배 — 부하 테스트로 확정 |
| 〃 | `agent.sms.timeout.hour` | 5 | **매뉴얼 허용범위(24~100) 밖** — 벤더 확인 |
| `conf/brand.conf` | — | `SECTA9INE` | 변경 불요 |

## 14-4. 🔴 병행 구동 절대 금지

**두 에이전트가 같은 `EM_TRAN` 을 폴링하면 동일 건을 중복 발송한다.**
현행은 1초 주기, 신규는 1초 주기 폴링이므로 **동시 기동 시 즉시 중복 발송이 발생**한다.

> ✅ **반드시 `현행 정지 → 신규 기동`** 순서. 테스트 단계에서도 **현행이 떠 있는 상태로 신규를 올리면 안 된다.**
> 부득이 검증이 필요하면 **별도 테스트 테이블명**(`agent.sms.table.name.tran`)으로 분리해 기동한다.

## 14-5. 실제 구동까지 남은 단계

1. **[블로커]** 섹타나인 관리자에게 **SMS·MMS 계정 발급** 요청
2. **[블로커]** Grant 서버 주소 확정(사내망 L4 VIP 여부) + **방화벽 오픈**
3. **[블로커]** 현행 DB의 **TABLESPACE 확인** → mapper 6곳 치환
4. 설치 경로 결정 → `setting.sh` 4개 항목 수정
5. `jdbc.conf` 현행 값 승계(+ log4jdbc 래퍼 제거 검토)
6. `agent.conf` 위 표대로 조정(특히 `fetch.hour`)
7. `code.conf` 는 **벤더 제공본 유지**, 현행 `result.properties` 와는 **대조만**
8. `checkVersion.sh` → `runner.sh start` → 로그 `Connection` 확인
9. 테스트 번호로 SMS/LMS/MMS 각 1건 (**현행 정지 상태에서**)

> **1~3번은 개발이 아니라 협조 요청 건**이다. 지금 바로 착수해야 전체 일정이 밀리지 않는다.

---

# 15. 벤더 공식 안내 메일 분석 + 전환 계획 (2026-08-03)

원본: `[2026-07-28 오후 4_37][박진수…] FW_ [업무] 2차 문자 서비스 전환 일정 회신 및 사전 준비 사항 안내.eml`

## 15-1. 메일 체인

| 일자 | 발신 → 수신 | 내용 |
|---|---|---|
| **2026-07-24 17:36** | 섹타나인 Dev2팀 **이봄** → **전사 14명**(eHR·CIM·서비스개발·Infra·데이터서비스·플랫폼개발·SPC GFS·SL물류·Smart Factory·**모바일개발팀**) | **2차 전환 일정 회신 요청** + 사전 준비 안내 |
| **2026-07-28 15:38** | 이봄 → 박진수 팀장 | **재안내** + 방화벽/JDK/계정발급 절차 + 첨부 3종 |
| **2026-07-28 16:37** | **박진수 팀장(대행)** → **김영준(dominic)** | 포워딩 (담당 배정) |

- **벤더 담당**: 섹타나인 Dev2팀 **이봄 프로** (`bom.lee@spc.co.kr` / 010-3345-1425), 팀장 이호승
- **2차 전환은 전사 다수 팀이 동시 진행**하는 과업이며, 우리는 **모바일개발팀 몫**이다.
- 첨부 다운로드 기간 **2026-07-28 ~ 08-04** (로컬 확보 완료 — 만료 무관)

> 🔴 **일정은 벤더가 지정한 게 아니라 "언제까지 가능한지 우리가 회신"하는 구조다.** 7-24 최초 요청 → 7-28 재안내 → **2026-08-03 현재 회신 여부 미확인**. 회신이 늦어질수록 **계정 발급이 시작되지 않아** 전체가 밀린다.

## 15-2. ✅ 미확정이던 항목 해소 — 방화벽 정보 확정

| 대상 | IP | 비고 |
|---|---|---|
| **SMS 운영 L4 (VIP)** | **`10.0.111.252`** | 공인 IP `110.45.199.252` |
| SMS 운영 #1 | `10.0.111.253` | 개별 노드 |
| SMS 운영 #2 | `10.0.111.254` | 개별 노드 |

| 서비스 | 포트 |
|---|---|
| **SMS** | **5200** |
| MMS / 알림톡 | **8200** |
| RCS | 8400 |

- ✅ **§8의 불확실성 해소**: 배포본 `agent.grant.url=http://50.0.111.73:5100` 은 **내부그룹용 샘플이 맞았다.** 실제는 **`10.0.111.252`(사내 L4)**.
- ⚠️ **방화벽은 단방향(업무서버 → 메시지서버)** 이며 **각 업무 담당자가 직접 신청**한다.
- ⚠️ 메일의 포트는 **Relay(발송) 포트** 기준으로 보인다. 배포본 `grant.port=5100` 과 값이 다르므로 **Grant(인증) 포트를 별도로 확인**해야 한다. 안전하게 **3개 IP × 필요한 포트 전부** 신청 권장.
- 💡 **이중화 활용 여지**: 배포본 주석의 멀티 host 기능(`agent.sms.api.host=IP1,IP2`)으로 **#1·#2 직접 지정**이 가능하다. L4(252) 단일 사용 vs 개별 2대 fail-over 중 택일 → 벤더 권고 확인.

## 15-3. ✅ Agent 계정 발급 절차 확정 (2단계)

가장 큰 블로커였던 계정 발급 경로가 명확해졌다.

```
① 모니터링 계정 회원가입   https://sms.secta9ine.co.kr/register/signup
   └ 연동방식 = "Agent 직연동" 선택 (필수)
② 벤더에 회신: (1) 가입 계정  (2) Agent 네트워크 유형 [외부 / 내부]
   └ ※ 네트워크 유형 미기재 시 계정 생성 불가
③ 섹타나인이 Agent ID / Agent Password 생성·전달   ← 여기서 conf 값 확보
```

> 📌 **우리 배치서버(`ip-10-0-70-71`)는 사내망이므로 네트워크 유형 = `내부`** 로 회신하면 된다(사내 L4 `10.0.111.252` 사용 전제).
> 📌 계정은 **SMS·MMS 별도**(§8)이므로 발급 시 둘 다 요청한다.

## 15-4. 🆕 신규 요구사항 — 발송번호 통신사 가입증빙원

**기존 분석에 없던 항목이다.** 발송번호 인증 강화 정책에 따라, 신규 서비스에 발송번호를 등록하려면 **해당 번호의 통신사 가입증빙원**이 필요하다.

- 🔴 **통신사 발급 서류라 리드타임이 있다** → 계정 가입과 **병행 착수** 필요
- ❓ 현행 발송번호(`EM_TRAN.TRAN_CALLBACK` 로 들어가는 발신번호) 목록부터 확정해야 한다
- ❓ 번호 명의가 SPC/섹타나인 중 어디인지에 따라 발급 주체가 갈린다

## 15-5. ✅ JDK 요구사항 충족

벤더 요구: **최소 JDK 1.8 이상**. 미만이면 업그레이드 또는 JDK 1.8 추가 설치 후 Agent만 해당 버전으로 실행.
→ ✅ **배치서버는 이미 JDK 8 사용 중**(`/opt/java/java-se-8u43`, 시스템 기본 1.8). **추가 조치 불필요.**

## 15-6. ✅ 벤더 제시 전환 순서 = 기존 분석과 일치

```
기존 Agent 중지 → 신규 Agent 설치 및 실행 → 테스트(Dummy) 메시지 발송 → 정상 수신 확인
```
→ §14-4의 **병행 구동 금지** 판단과 동일. 벤더도 "중지 후 설치"를 전제한다.

---

## 15-7. 📋 전환 실행 계획

### Phase 0 — 즉시 착수 (지연 중, 최우선)
| # | 작업 | 담당 | 비고 |
|---|---|---|---|
| 0-1 | **전환 가능 일정 회신** | dominic | 🔴 **7-24 요청 건, 미회신 상태** |
| 0-2 | 서버 네트워크 환경 회신 = **내부망** | dominic | 배치서버 사내망 |
| 0-3 | 모니터링 계정 **회원가입** (연동방식 **Agent 직연동**) | dominic | `sms.secta9ine.co.kr/register/signup` |
| 0-4 | 가입 계정 + 네트워크 유형(**내부**) 회신 → **Agent ID/PW 발급 요청**(SMS·MMS) | dominic | ③단계 트리거 |
| 0-5 | **발송번호 목록 확정** → 통신사 **가입증빙원 발급 신청** | dominic + 유관부서 | 🔴 리드타임 김 |

### Phase 1 — 발급 대기 중 병행 (인프라·조사)
| # | 작업 | 산출물 |
|---|---|---|
| 1-1 | **방화벽 신청** — 배치서버 → `10.0.111.252/.253/.254`, 포트 5200(SMS)·8200(MMS) | 신청서 |
| 1-2 | Grant(인증) 포트 별도 확인 → 방화벽에 포함 | 벤더 회신 |
| 1-3 | **TABLESPACE 확인**(인프라팀) → mapper 6곳 치환값 | `SELECT TABLESPACE_NAME …` |
| 1-4 | **`TRAN_TYPE` 분포 조사** — `=5`(URL) 사용 여부 | 🔴 리스크 #3 판정 |
| 1-5 | **`TRAN_REFKEY` 최대길이** 조사 | 🔴 리스크 #4 판정 |
| 1-6 | 발송량 피크·대기건 적체 패턴 → `fetch.hour`·`fetch.count` 산정 | 🔴 리스크 #2 판정 |
| 1-7 | `TRAN_RSLT` 값 분포 → `code.conf` 커버리지 검증 | 🔴 리스크 #1 판정 |
| 1-8 | 현행 ARIA 암호화 실사용 여부 벤더 확인 | 🟠 리스크 #15 |
| 1-9 | 벤더 문의 일괄 발송 (리스크 #1·3·4·6·9·11·15) | 문의서 |

### Phase 2 — 설치·설정 (계정 수령 후)
| # | 작업 |
|---|---|
| 2-1 | 설치 경로 확정 → `/app/secta-agent` (현행 `/app/` 관례) |
| 2-2 | `setting.sh`: `APP_HOME`·`JAVA_HOME`·`XMS/XMX`·`APP_PROFILE=production` |
| 2-3 | `jdbc.conf`: 현행 값 승계 + **log4jdbc 래퍼 제거 검토** + Jasypt 암호화 검토 |
| 2-4 | `agent.conf`: 계정·Grant주소·테이블명·주기·건수. ⚠️ **`break.hours` 라인 삭제 금지** |
| 2-5 | `agent.contents.path`: MMS 이미지 경로 현행 승계 |
| 2-6 | mapper `TABLESPACE` **6곳** 치환 |
| 2-7 | `code.conf`: **벤더 제공본 유지**, 현행 `result.properties` 와 대조만 |

### Phase 3 — 검증 (⚠️ 현행 정지 상태에서)
| # | 작업 |
|---|---|
| 3-1 | `checkVersion.sh` 로 버전 확인 |
| 3-2 | `runner.sh start` → `logs/secta-agent.log` **ERROR/FAIL 없음 + Connection 로그** 확인 |
| 3-3 | **Dummy 발송** — 테스트 번호로 SMS/LMS/MMS 각 1건 |
| 3-4 | `TRAN_STATUS` **1→3→4** 전이 확인 (`5` 발생 시 중단) |
| 3-5 | `EM_LOG_YYYYMM` 이관 확인 |
| 3-6 | `TRAN_RSLT` 가 Legacy 1바이트 코드로 저장되는지 |

### Phase 4 — 전환 (D-day)
| # | 작업 |
|---|---|
| 4-1 | 전환 시점 **대기건(`TRAN_STATUS=1,2`) 처리 방안** 확정 |
| 4-2 | **현행 정지**: `cd /app/ndsoft/bin && sh runner-unix.sh stop` |
| 4-3 | **신규 기동**: `cd /app/secta-agent/bin_linux && ./runner.sh start` |
| 4-4 | 실발송 모니터링 (모니터링 웹 + 로그) |
| 4-5 | 🔴 **롤백 대비**: `/app/ndsoft` **삭제 금지**, 원복 커맨드 보존 |

### Phase 5 — 안정화
| # | 작업 |
|---|---|
| 5-1 | **`d`(기타) 결과코드 비율 모니터링** — `code.conf` 미정의 코드 뭉개짐 감지 |
| 5-2 | `fetch.hour=1` 로 인한 **자동 실패 발생 여부** 추적 |
| 5-3 | `complete.delay` 10초의 **DB 부하** 측정 |
| 5-4 | **systemd 등록** 검토 (현행·신규 모두 미등록) |
| 5-5 | 로그 **보관 기간 정책** 설정 (logback) |
| 5-6 | 구 `/app/ndsoft` 정리 판단 (관찰 후) |

## 15-8. 🔴 크리티컬 패스

```
[0-1 일정회신] → [0-4 계정요청] → [벤더 발급] → [Phase 2 설치] → [Phase 3 검증] → [Phase 4 전환]
                      ↕ (병행)
[0-5 가입증빙원] ─ 통신사 리드타임 ─┘
[1-1 방화벽] ─ 사내 승인 리드타임 ─┘
```
> **일정을 결정하는 건 개발이 아니라 ① 계정 발급 ② 가입증빙원 ③ 방화벽 승인 세 가지 외부 리드타임이다.**
> Phase 1의 DB 조사(1-3~1-7)는 **오늘 바로 가능**하며, 여기서 리스크 #1~#4의 실제 영향도가 판정된다.

---

## 다음 할 일 (TODO)
- [x] ~~`diff conf/agent.bak conf/agent.conf`~~ → **완료**(§13-11)
- [x] ~~전환 일정·사전준비 메일 원문 확보~~ → **완료**(§15)
- [ ] 현행 암호화(ARIA) 실사용 여부 벤더 확인
- [ ] **전환 일정 확인** — 자료 폴더명이 "2차 문자 서비스 전환 일정 회신 및 사전 준비 사항 안내"인데 **메일 본문이 폴더에 없다.** 일정·사전준비 요구사항 원문 확보 필요
- [ ] **1차 전환 범위** 확인 (2차가 있다는 건 1차가 선행됐다는 뜻 — 선례에서 배울 점 확보)
- [ ] Phase 1 사전 조사 SQL 실행
- [ ] 벤더 확인 항목 취합 후 일괄 문의 (리스크 #1·3·4·6·9·11)

## 참고 링크
- [프로젝트 INDEX](./INDEX.md)
- [WORKLOG-2026-W32](./worklog/weekly/WORKLOG-2026-W32.md)
- [shared/server-env.md](../../../shared/server-env.md)
- [shared/security-review.md](../../../shared/security-review.md)
