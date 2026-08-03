---
문서유형: INDEX
프로젝트: sms-agent-replacement (과업/엄브렐러)
이슈키: --
작성일: 2026-08-03
최종수정: 2026-08-03
작성자: dominic
상태: 진행중(분석)
요약: 배치서버(ip-10-0-70-71)의 (주)엔디소프트 NDMG SMS 에이전트(/app/ndsoft) → **섹타나인 Agent v2.0.1(Legacy 호환)** 전환 개발 과업. "2차 문자 서비스 전환" 건. 현행 실사 + 신규 배포본/매뉴얼 분석 완료, 리스크 12건 도출
---

# 📇 SMS Agent 교체 프로젝트 (sms-agent-replacement)

> ⚠️ **이 슬러그는 저장소가 아니라 "과업 묶음"이다.** 코드 저장소가 아직 특정되지 않았고(현행 에이전트는 벤더 납품 바이너리), 배치서버 인프라·발송 연동에 걸쳐 있어 **과업 단위**로 등록한다. (폴더명=저장소명 규칙의 예외 — [homepage-ai-renewal](../homepage-ai-renewal/INDEX.md) 선례)
>
> 🔕 **자동 주입 제외.** 사용자 지시(2026-08-03)에 따라 SessionStart 훅 화이트리스트에 등록하지 않는다. 필요 시 `sms agent 교체 컨텍스트 연결해` 로 수동 연결(4시간).

## 프로젝트 정의
- **목표**: 배치서버의 **레거시 SMS 발송 에이전트(엔디소프트 NDMG) → 섹타나인 Agent v2.0.1(Legacy 호환) 전환 개발**.
- **배경**: 전사 **"2차 문자 서비스 전환"** 과업. 현행 에이전트 바이너리는 **2016-12 빌드**로 약 10년째 무교체 상주.
- **현재 단계**: **2단계 — 신규 배포본 분석 완료**. 다음은 사전 조사(Phase 1) 및 계정·환경 확보(Phase 2).
- **상태**: 진행중(분석)

## 🔄 전환 개요 — 현행 → 신규

| | 현행 | 신규 |
|---|---|---|
| 벤더 | **(주)엔디소프트** NDMG | **섹타나인(SECTA9INE)** Agent v2.0.1 Legacy호환 |
| 실행 | `nd-message-agent-spc.jar` (2016-12) | `secta-agent.jar` (2026-06, 27MB) |
| 스택 | Spring 구버전 + Hibernate + log4j1 | Spring Boot 1.5.22 + MyBatis + HikariCP + Netty |
| 런타임 | Java 8 | **Java 8 호환**(class major 52) — 서버 JDK 교체 불필요 ✅ |
| DB 테이블 | `EM_TRAN` / `EM_TRAN_MMS` / `EM_LOG` | **동일** ✅ |

> ✅ **핵심**: 신규는 "Legacy 호환" 빌드라 **같은 테이블을 그대로 사용** → **발송 요청 주체(배치·앱)의 INSERT 코드는 원칙적으로 수정 불필요.** 교체 범위는 에이전트 프로세스·설정에 국한된다.
>
> 🔴 **단, 결과코드 체계·발송 정책은 다르다.** 특히 **같은 숫자 코드가 다른 의미**라 현행 매핑을 그대로 이식하면 안 된다. 상세: [WORKLOG-20260803 분석](./WORKLOG-20260803-secta-agent-analysis.md)

### 최우선 리스크 4건 (상세는 분석 문서)
| # | 리스크 | 영향 |
|---|---|---|
| 1 | **결과코드 체계 상이** — `3001`·`3002`·`3004`·`3005` 등 의미가 다름 | 결과코드 오염 → 통계·재발송·CS 오류 |
| 2 | **`fetch.hour=1`** (현행 무제한) | 1시간 초과 대기건 **자동 실패 처리** |
| 3 | **`TRAN_TYPE=5`(URL) 미조회** | 사용 중이면 해당 건 **영구 적체** |
| 4 | **로그테이블 `TRAN_REFKEY` 20 vs 전송테이블 40** | 이관 시 `ORA-12899` 실패 |

### 📁 원본 자료 (로컬)
`D:\백업_김영준_업무 관리 문서 20260430\02_김영준\20_개발\20260803_FW [업무] 2차 문자 서비스 전환 일정 회신 및 사전 준비 사항 안내\`
— 현행 conf 4종 · 신규 배포본 `secta-agent-oracle_내부그룹사용` · 벤더 매뉴얼 PDF(24p) · 내부 설치가이드 PPTX(10슬라이드)

## 🖥️ 현행 구성 — 실사 결과 (2026-08-03)

### 설치 위치
| 구분 | 경로/값 |
|---|---|
| 서버 | 배치서버 **`ip-10-0-70-71`** (EC2, Amazon Linux) |
| 실행 계정 | `ec2-user` |
| 설치 루트 | **`/app/ndsoft`** |
| 실행 디렉터리(cwd) | `/app/ndsoft/bin` |
| 라이브러리 | `/app/ndsoft/lib/nd-message-agent-spc.jar` |
| 설정 | `/app/ndsoft/conf` |
| 로그 | `/app/ndsoft/logs` |

### 프로세스 구성
```
java -Dprocess.id=ndsoft-agnet-sms \
     -Xms64m -Xmx64m -XX:+PrintGCDetails \
     -Dfile.encoding=KSC5601 \
     -cp ..//lib/nd-message-agent-spc.jar \
     ndsoft.message.agent.base.executor.ConsoleExecutor
```
- **PID** 110132 (2026-08-03 기준) · **PPID = 1** → systemd 서비스가 아닌 **nohup 백그라운드 상주**로 추정
- **기동 시점 2025년** · 누적 CPU **2일 13시간** → 상시 폴링형 동작 정황
- `-cp` 가 **상대경로(`..//lib/`)** → **반드시 `bin`에서 기동해야 함**. cwd가 다르면 기동 실패
- `process.id` 값의 `agnet` 은 **벤더 원문 오타** — 임의 수정 금지(운영 스크립트·모니터링이 이 문자열에 의존할 수 있음)

### 설정파일 (`/app/ndsoft/conf`)
| 파일 | 크기 | 최종수정 | 역할 |
|---|---|---|---|
| `agent.conf` | 2,071 | 2017-04-05 | **메인 설정** — 에이전트 동작·연동·폴링 |
| `agent.bak` | 2,069 | 2016-12-06 | 2017-04 수정 전 원본 백업 (**2바이트 차 = 단일 값 변경**) |
| `jdbc.conf` | 618 | 2016-12-06 | **DB 접속정보** — 발송 큐 폴링용 |
| `log4j.properties` | 1,483 | 2016-12-06 | 로그 경로·로테이션 |
| `result.properties` | 4,966 | 2016-12-06 | **발송결과 코드 매핑**(통신사 리턴코드) |

> ⚠️ `agent.conf`·`jdbc.conf` 에 계정·인증정보가 **평문**일 가능성이 높다. **KB 문서에는 어떤 값도 기재하지 않는다.** 조회 시 마스킹 필수.

### 디렉터리 타임스탬프 (변경 이력 단서)
| 경로 | 최종수정 | 해석 |
|---|---|---|
| `/app/ndsoft` | 2023-11-06 | 설치 루트 |
| `/app/ndsoft/bin` | **2026-04-21** | 올해 4월 변경 |
| `/app/ndsoft/conf` | **2026-04-10** | 내부 파일은 전부 2016~2017 → **파일 추가/삭제/이름변경**이 있었다는 의미 |
| `/app/ndsoft/lib` | 2016-12-06 | **바이너리 10년 무변경** |
| `/app/ndsoft/logs` | 2026-08-03 | 가동중. 디렉터리 크기 16KB → 파일 다수 누적 |

## 🏢 벤더
| 항목 | 내용 |
|---|---|
| 회사 | **(주)엔디소프트 (NDSoft)** — `ndsoft.co.kr` / `nd1.co.kr` |
| 제품 | **NDMG** (NDSOFT Message Gateway) |
| 납품 이력 | 회사 연혁에 **"NDMG를 ㈜SPC Networks에 구축·운영"** 명시 → jar 접미사 `-spc` 와 일치 |
| 기타 이력 | 수원시청 SMS 맞춤형 Agent, 신한은행 MQ 기반 Agent, KBS 메시징 고도화 |
| 문의 | 042-610-3800 (평일 09:00~18:00) |

> 📛 **명칭 주의**: **엔**디소프트(NDSoft)다. **엠**디소프트(MDSoft, `md-soft.co.kr`)는 의료 EMR 업체로 **무관**하다. 초기 조사에서 혼동이 있었다.

## 🔗 같은 서버의 별도 시스템 (혼동 주의)
동일 서버 `ip-10-0-70-71`에 **삼성SDS Anyframe 배치**가 별도로 돈다. SMS 에이전트와 **다른 프로세스**다.
- 경로 `/app/batch` · JDK `/opt/java/java-se-8u43`
- 런처 `com.sds.anyframe.batch.launcher.BatchJobLauncher`
- 스택: Spring 2.5.6 / spring-batch 1.1.4 / log4j 1.2.17 / ojdbc8 · mysql-connector-j 8.0.32 · sqljdbc4
- 예: `hp/batch/wthr/gov/GovForecastGrib_CFG.xml`(기상청 예보) 잡이 분 단위 기동
- 관련 KB: [spc_batch](../spc_batch/INDEX.md) · [spc_spring_batch](../spc_spring_batch/INDEX.md) — **동일 여부 미확인**

## 🔴 리스크 (교체 근거)
| # | 리스크 | 내용 |
|---|---|---|
| 1 | **바이너리 EOL** | jar 2016-12 빌드, 약 10년 무교체. 벤더 지원 범위 미확인 |
| 2 | **레거시 런타임** | JDK8 · `KSC5601`(EUC-KR 계열) 인코딩 → 이모지·유니코드 메시지 처리 한계 우려 |
| 3 | **힙 64MB 고정** | `-Xms64m -Xmx64m`. 대량 발송 시 여유 없음. `PrintGCDetails` 상시 활성(로그 부담) |
| 4 | **무감시 상주** | PPID=1, systemd 미등록 → **프로세스 사망 시 자동 재기동 없음**. 헬스체크·알람 부재 추정 |
| 5 | **기동 취약성** | `-cp` 상대경로 → cwd 의존. 잘못된 위치에서 기동 시 실패 |
| 6 | **크리덴셜 평문** | `jdbc.conf`·`agent.conf` 평문 우려 → KB 횡단 취약 패턴(하드코딩 시크릿)과 동일 계열 |
| 7 | **로그 미정리** | logs 디렉터리 엔트리 다수 누적. 디스크 여유 미확인 |
| 8 | **미상 변경 이력** | 2026-04-10(conf)·2026-04-21(bin) 변경 주체·내용 불명 |

> 🔴 6번은 [README 횡단 취약 패턴](../../README.md)의 **하드코딩 시크릿** 사례와 같은 계열이다. 진단 시 [security-review.md](../../shared/security-review.md) 시크릿 스윕을 적용한다.

## ❓ 미확인 (다음 실사 항목)
> 📌 2026-08-03 분석으로 **신규 에이전트 쪽은 대부분 해소**됐다. 아래는 **현행 운영 실측**이 필요한 항목이다. 신규 관련 미결(벤더 문의 항목 포함)은 [분석 문서 §11 Phase 1](./WORKLOG-20260803-secta-agent-analysis.md)에 정리.
- [ ] **발송 방식 확정** — DB 폴링형 vs 소켓 상주형 (`jdbc.conf` 존재로 **폴링형 유력**)
- [ ] **발송 큐 테이블명** 및 폴링 주기 (`agent.conf`)
- [ ] **게이트웨이 엔드포인트**(NDMG 서버 IP/포트) 및 연결 상태
- [ ] **기동/재기동 스크립트** (`/app/ndsoft/bin/*.sh`)
- [ ] `agent.bak` → `agent.conf` **diff**(2바이트 차, 단일 값 변경)
- [ ] **2026-04 변경 이력**의 주체·내용
- [ ] **발송 요청 주체** — `/app/batch` 잡인지, 다른 앱([ha_api](../ha_api/INDEX.md) 등)인지
- [ ] 로그 용량·디스크 여유 (`du -sh /app/ndsoft/logs`, `df -h /app`)
- [ ] 벤더 지원 계약 유효 여부

## 📄 문서 목록
| 문서 | 상태 | 요약 |
|---|---|---|
| ⭐ [WORKLOG-20260803 섹타나인 Agent 전환 분석](./WORKLOG-20260803-secta-agent-analysis.md) | 진행중 | **정본 분석** — 현행/신규 전수 대조, 결과코드·발송정책 차이, 스키마 결함, 리스크 12건, Phase 1~5 전환 계획 |
| [WORKLOG-2026-W32](./worklog/weekly/WORKLOG-2026-W32.md) | 진행중 | 주간 기록 — 현행 에이전트 실사 (설치경로·설정·벤더 특정) |

## 참고 (공통 문서)
- [공유 KB README](../../README.md)
- [shared/server-env.md](../../shared/server-env.md) — 서버 환경 (배치서버 항목 추가됨)
- [shared/security-review.md](../../shared/security-review.md) — 시크릿 스윕 기준
