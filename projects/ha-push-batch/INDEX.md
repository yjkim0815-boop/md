---
문서유형: INDEX
프로젝트: ha-push-batch
작성일: 2026-07-22
최종수정: 2026-08-03
작성자: dominic
상태: 진행중
요약: 해피포인트 배치서버 (Spring Boot 3.5 / Java17 / Spring Batch / Oracle JdbcTemplate) — 유일한 Boot 기반 프로젝트
---

# 📇 해피포인트 배치서버 (ha-push-batch)

## 프로젝트 정체성 (중요)
- **이 프로젝트 = 출석체크(룰렛 응모) 리마인드 푸시 발송 배치**. 사용자 트래픽을 받는 서버가 아니라 **스케줄 구동 배치**다.
- ⚠️ **KB 내 유일한 Spring Boot / Gradle / Java 17 프로젝트**다.
  - `ha_api`·`ha_web`·`ha-web-api`는 전부 **WAR + 외장 Tomcat + Maven + JSP/MyBatis** 레거시 계열.
  - 따라서 **ECC의 Spring Boot 계열 스킬(`springboot-patterns` 등)을 예시 코드 수준까지 직접 적용할 수 있는 유일한 대상**이다(타 프로젝트는 개념만 차용). → [ecc-reference.md](../../shared/ecc-reference.md)
- ⚠️ **MyBatis를 쓰지 않는다.** SQL은 `NamedParameterJdbcTemplate` + Java **텍스트 블록**에 직접 작성 → [sql-mybatis.md](../../shared/conventions/sql-mybatis.md)의 `#{}` 규칙이 아니라 **`:파라미터` 바인딩** 규칙이 적용된다.

## 프로젝트 개요
- **워크스페이스 폴더**: `ha-batch` (KB 기준 `../../../ha-batch`) — ⚠️ 폴더명은 `ha-batch`지만 **Gradle rootProject / 저장소명은 `ha-push-batch`**
- **Bitbucket remote**: `bitbucket.org/sectanine/ha-push-batch.git`
- **브랜치**: `master` 단일 (develop/release 없음)
- **스택**: Java 17(toolchain) / Spring Boot **3.5.14** / Spring Batch / `spring-boot-starter-jdbc` / **WebFlux(WebClient)** / Lombok / Gradle 8.14.5
- **DB 드라이버**: `com.oracle.database.jdbc:ojdbc11:23.26.0.0.0` (runtimeOnly)
- **패키징**: 실행형 JAR (WAR/외장 톰캣 아님)
- **규모**: Java 클래스 17개 / 전체 약 1,257줄 — 소규모
- **테스트**: `HaPushBatchApplicationTests.contextLoads()` **1건뿐** (실질 0)

## 아키텍처 (com.example.hapushbatch)
> ⚠️ 베이스 패키지가 **`com.example`** 그대로다. 타 프로젝트는 `com.spc.hpc`. 정식 운영 전 패키지 정리 검토 필요.

```
HaPushBatchApplication      @SpringBootApplication + @EnableScheduling
├─ scheduler/DailyPushScheduler     @Scheduled(cron) → JobLauncher.run(dailyPushJob)
├─ job/DailyPushJobConfig           Job 1개 + Step 2개(Tasklet 방식, Chunk 방식 아님)
│   ├─ job/tasklet/TargetPrepareTasklet   ① 대상 적재
│   ├─ job/tasklet/PushSendTasklet        ② 발송
│   └─ job/listener/PushJobListener       Job 전후 훅(현재 본문 대부분 주석)
├─ repository/  PushMasterRepository · PushTargetRepository · RouletteEntryTableResolver
├─ service/     PushApiService(WebClient) · SlackService · TelegramService
├─ config/      WebClientConfig
└─ dto/         PushMaster · PushTarget · PushStatusCount · PushApiRequest · PushApiResponse  (전부 record)
```

### 배치 흐름
| 순서 | Step | 하는 일 |
|------|------|---------|
| 1 | `targetPrepareStep` | `PUSH_MASTER`에서 pushType으로 pushId 조회 → `PUSH_TARGET` **전체 DELETE** → 대상 INSERT → ExecutionContext에 `pushId` 저장 |
| 2 | `pushSendStep` | 타임아웃 `SENDING` 복구 → `READY/RETRY` 청크(1000) 조회 → `SENDING` 마킹 → 푸시 API 호출 → `SENT` 마킹 → 대상 소진까지 반복 |

- `spring.batch.job.enabled=false` + `@Scheduled` 조합 → **앱 기동 시 자동 실행 안 함**, 크론으로만 구동.
- JobParameters: `pushType`(고정값) + `runAt`(현재 millis, 중복 실행 회피용).
- `spring.batch.jdbc.initialize-schema=never` → **Spring Batch 메타 테이블(BATCH_*)은 수동 생성 전제**.

### 도메인 데이터
- **`PUSH_MASTER`**: 푸시 유형별 마스터(PUSH_ID / PUSH_TYPE / TITLE / CONTENT). 현재 `PUSH_TYPE='ATTENDANCE'` 하나만 사용.
- **`PUSH_TARGET`**: 발송 대상 + 상태머신 `READY → SENDING → SENT` / `RETRY` / `FAILED`. 시퀀스 `SEQ_PUSH_TARGET`.
- **`ROULETTEENTRY_yyyyMM`**: 룰렛 응모 **월별 분리 테이블**. `RouletteEntryTableResolver`가 기간(오늘-10일 ~ 오늘)에 걸친 월 테이블명을 생성 → `USER_TABLES`로 실존 확인 → `UNION ALL`로 조립.
- **대상 조건**: 최근 10일 내 응모 이력 있음 `AND` 오늘 00:00~08:00 응모 없음 → 즉 "출석 안 한 사람 리마인드".

## 외부 연동
| 연동처 | 용도 | 구현 | 상태 |
|--------|------|------|------|
| 푸시 발송 API (`push-producer.happypointcard.com`) | 실제 푸시 발송 | `PushApiService` + WebClient, 헤더 `X-Spc-Api-Key`, `POST /api/v1/send` | 사용중 |
| Slack Webhook | 배치 결과 알림 | `SlackService` | **주입만 되고 호출부 전부 주석** |
| Telegram Bot | 배치 결과 알림 | `TelegramService` | **주입만 되고 호출부 전부 주석** |

## 프로파일 / 스케줄
| 프로파일 | DB | cron | mock 발송 | 비고 |
|----------|-----|------|-----------|------|
| local | `127.0.0.1:11521` (터널) | `0 */1 * * * *` (1분) | true | |
| dev | `dev-hp-oracle` RDS | `0 */1 * * * *` (1분) | true | 기본 active 프로파일 |
| stage | **`happy-app-homepage` RDS = 운영과 동일** | `0 */2 * * * *` (2분) | true | ⚠️ 아래 리스크 참조 |
| prod | `happy-app-homepage` RDS | `0 6 8 * * *` (매일 08:06) | false | |

- `mock-send-enabled=true`면 실제 `PUSH_TARGET` 조회를 건너뛰고 **코드에 하드코딩된 테스트 회원번호 5건 + 더미**로 발송한다(`PushSendTasklet.createMockTargets`).
- 기본값 `spring.profiles.active: dev` → **기동 시 프로파일 미지정이면 dev DB로 붙는다**.

## 로깅
- `logback-spring.xml` — 발송 이력 전용 로거 **`PUSH_SEND_HISTORY`** (`push-send-history.log`, 일단위 롤링 90일 보관, `mbrNo=..., sendDateTime=...`).
- 일반 로그는 `catalina.log`(100MB/30일). ⚠️ `FILE` 어펜더 패턴이 `${FILE_LOG_PATTERN}`인데 Boot가 이 프로퍼티를 정의하는 건 `defaults.xml` include 시점 — **현재 include가 없어 미정의**일 수 있음.
- 로그 경로: `${LOG_PATH:./logs}`.

## 🔴 현재 상태 / 핵심 리스크
> 상세 근거·재현 시나리오는 [WORKLOG-20260722-codebase-analysis.md](./WORKLOG-20260722-codebase-analysis.md).
> 판정 기준: ECC `rules/common/security.md` · `rules/java/security.md` · `rules/common/coding-style.md` (참조 전용).

| # | 심각도 | 요약 |
|---|--------|------|
| 1 | 🔴 Critical | **운영 DB 계정·푸시 API 키·Slack Webhook·Telegram 봇 토큰이 평문으로 git 커밋됨** (`config/*.yml` 5개 전부 추적 중) |
| 2 | 🔴 Critical | **stage 프로파일이 운영 DB를 가리키며 2분 주기 크론** → 운영 `PUSH_TARGET` 반복 전체 삭제·재적재 |
| 3 | 🔴 High | 발송 루프 전체가 **단일 트랜잭션** → 중간 실패 시 `SENT` 마킹까지 롤백, 재실행 시 **중복 발송** |
| 4 | 🟠 High | `pushId`가 null이면 `ExecutionContext.putLong`에서 **언박싱 NPE** |
| 5 | 🟠 Medium | `DELETE FROM PUSH_TARGET` — **pushId 조건 없는 전체 삭제** |
| 6 | 🟠 Medium | `WHERE TARGET_ID IN (:ids)` + chunk-size 1000 → Oracle **IN 절 1000개 한계 경계값** |
| 7 | 🟠 Medium | 실패 시 `markRetryOrFailed` 호출이 주석 처리 → **재시도/FAILED 상태머신이 사실상 미동작** |
| 8 | 🟡 Low | 미사용 변수 다수, 알림 서비스 미연결, 테스트 부재, `com.example` 패키지, WebFlux로 인한 불필요한 웹서버 기동 |

## 문서 목록
| 문서 | 유형 | 상태 | 요약 |
|------|------|------|------|
| [WORKLOG-20260722-codebase-analysis.md](./WORKLOG-20260722-codebase-analysis.md) | WORKLOG | 진행중 | 코드베이스 구조 분석 + ECC 기준 1차 진단(Critical 2건) |

## 참고 (공통 문서)
- [공유 지식 베이스 README](../../README.md)
- [ECC 참조 · 작업 프로토콜](../../shared/ecc-reference.md)
- [보안/취약점 진단 기준](../../shared/security-review.md)
- [코드 컨벤션](../../shared/conventions/README.md) · [java](../../shared/conventions/java.md) · [spring](../../shared/conventions/spring.md)
- [서버 환경](../../shared/server-env.md) — ⚠️ 이 배치의 실행 서버/배포 방식은 **아직 미확인**(외장 톰캣 인스턴스 목록에 없음)
