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

분석 대상 폴더에 **운영 Oracle 접속 크리덴셜이 평문**으로 존재한다. 현행 `jdbc.conf` 의 접속 대상은 [server-env.md](../../shared/server-env.md) 에 기록된 **SPC 홈페이지 운영 Oracle RDS**와 동일하며, 계정도 **관리자 권한 계정**이다.

- 위치: 개인 PC의 백업 폴더(`D:\백업_...`) + 배치서버 `/app/ndsoft/conf/jdbc.conf`
- 신규 배포본 `conf/` 에도 샘플 크리덴셜 평문 존재
- 대응: ① 백업 폴더 접근 통제/정리 ② 서버 conf 파일 권한 최소화(`600`) ③ **Jasypt 암호화 적용** ④ 전환 완료 후 **DB 계정 비밀번호 교체** 검토

> [README 횡단 취약 패턴](../../README.md)의 **하드코딩 시크릿 7번째 사례**. 기준: [security-review.md](../../shared/security-review.md)

---

## 다음 할 일 (TODO)
- [ ] **전환 일정 확인** — 자료 폴더명이 "2차 문자 서비스 전환 일정 회신 및 사전 준비 사항 안내"인데 **메일 본문이 폴더에 없다.** 일정·사전준비 요구사항 원문 확보 필요
- [ ] **1차 전환 범위** 확인 (2차가 있다는 건 1차가 선행됐다는 뜻 — 선례에서 배울 점 확보)
- [ ] Phase 1 사전 조사 SQL 실행
- [ ] 벤더 확인 항목 취합 후 일괄 문의 (리스크 #1·3·4·6·9·11)

## 참고 링크
- [프로젝트 INDEX](./INDEX.md)
- [WORKLOG-2026-W32](./worklog/weekly/WORKLOG-2026-W32.md)
- [shared/server-env.md](../../shared/server-env.md)
- [shared/security-review.md](../../shared/security-review.md)
