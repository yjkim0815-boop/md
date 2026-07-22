---
문서유형: WORKLOG
프로젝트: ha-push-batch
이슈키: --
작성일: 2026-07-22
최종수정: 2026-07-22
작성자: dominic
상태: 진행중
요약: ha-batch(ha-push-batch) 코드베이스 전수 분석 — 배치 흐름/도메인 테이블 맵, ECC 규칙 기준 리스크 진단(크리덴셜 평문 커밋·stage가 운영DB 참조 = Critical 2건)
---

# 🛠️ WORKLOG — 코드베이스 분석 & 1차 진단 (2026-07-22)

## 배경 / 목적
`ha-batch`는 KB **미등록 프로젝트**였고, 동시에 워크스페이스에서 **유일한 Spring Boot / Gradle / Java17** 프로젝트다.
- 배치 흐름과 도메인 테이블 구조를 KB에 남겨 매 채팅 재탐색 비용을 없앤다.
- ECC의 Spring Boot 계열 스킬을 **예시 수준까지 직접 적용 가능한 유일한 대상**이므로, 그 관계를 KB에 명시한다.

진단 기준(참조 전용): ECC `rules/common/security.md` · `rules/java/security.md` · `rules/common/coding-style.md` · `skills/springboot-patterns`.

## 진행 내용
1. 전수 스캔 — `build.gradle`, 소스 17개 클래스 전량, `config/*.yml` 5개, `logback-spring.xml`, git remote/브랜치.
2. 배치 흐름·도메인 테이블·프로파일 맵 정리 → [INDEX.md](./INDEX.md)에 영구 반영.
3. ECC 보안 체크리스트 기준 시크릿 스윕.
4. ECC 코딩 규칙(명시적 에러 처리·죽은 코드·트랜잭션 경계) 기준 코드 리스크 진단.

### 확인된 규모 (2026-07-22 기준)
| 항목 | 수치 |
|------|------|
| Java 클래스 | 17 |
| 전체 라인 수(src+build.gradle) | 약 1,257 |
| Step | 2 (둘 다 Tasklet) |
| 테스트 | 1 (`contextLoads`만 — 실질 0) |
| 추적 중인 설정 파일 | `config/*.yml` **5개 전부 git 추적** |

### 확인된 구성 요점
- **Tasklet 방식 배치** — Spring Batch의 Chunk(Reader/Processor/Writer) 모델을 쓰지 않고 Tasklet 안에서 `while` 루프로 직접 청킹한다. → **재시작/스킵/롤백 등 Batch 프레임워크 기능을 사실상 포기한 구조**.
- **MyBatis 미사용** — `NamedParameterJdbcTemplate` + Java 텍스트 블록에 SQL 직접 작성. 바인딩은 `:param` 형식.
- **월별 분리 테이블 동적 조립** — `ROULETTEENTRY_yyyyMM`을 `RouletteEntryTableResolver`가 생성하고 `USER_TABLES`로 실존 확인 후 `UNION ALL`. 테이블명이 SQL 문자열에 concat되지만 **입력이 `LocalDate` 기반 생성값 + `USER_TABLES` 화이트리스트 교집합**이라 인젝션 경로는 성립하지 않음(오탐 배제).
- **알림 미연결** — `SlackService`/`TelegramService`는 빈 주입만 되고 호출부가 전부 주석. 즉 **현재 배치 실패를 아무도 통보받지 못한다.**
- **베이스 패키지가 `com.example`** — 타 프로젝트(`com.spc.hpc`)와 불일치.

## 발생 이슈 & 해결
| 이슈 | 원인 | 해결 |
|------|------|------|
| 🔴 크리덴셜 평문 커밋 | `config/*.yml`에 DB 비번·API 키·웹훅·봇 토큰 직접 기재 | **미해결 — TODO** |
| 🔴 stage가 운영 DB 참조 | `application-stage.yml` datasource가 prod와 동일 호스트 | **미해결 — TODO** |
| 🔴 발송 루프 단일 트랜잭션 | Tasklet 1개 = 트랜잭션 1개인데 루프 전체를 그 안에서 처리 | **미해결 — 설계 변경 필요** |

---

### 🔴 Critical-1: 크리덴셜 평문 커밋
> ⚠️ KB 규칙에 따라 **값은 기재하지 않는다**. 위치·유형·건수만 기록.

- **위치**: `src/main/resources/config/` 의 `application.yml` · `-local` · `-dev` · `-stage` · `-prod` — **5개 전부 git 추적 중**.
- **유형/건수**:
  | 유형 | 건수 | 위치 |
  |------|------|------|
  | Oracle DB 계정+비밀번호 | 4 (dev/local 공용 1, stage/prod 공용 1 — **운영 관리자 계정 포함**) | 각 프로파일 `spring.datasource` |
  | 푸시 API 키 (`X-Spc-Api-Key`) | 2 (dev용 1, **운영용 1**) | 각 프로파일 `push.api.api-key` |
  | Slack Incoming Webhook URL | 1 (전 프로파일 동일) | `slack.webhook-url` |
  | Telegram Bot Token + chat-id | 1 | `application.yml` 기준 파일 |
- **영향**: 저장소 접근 = **운영 Oracle 관리자 계정 + 운영 푸시 발송 권한** 획득. 푸시 API 키는 전 회원 대상 임의 푸시 발송으로 이어질 수 있어 DB 계정과 동급 위험.
- **판정 근거**: ECC `rules/java/security.md` "Secrets Management — Never hardcode API keys, tokens, or credentials in source code" 및 `rules/common/security.md` "No hardcoded secrets" 위반.
- **참고**: 코드에도 이미 자각이 남아 있다 — `PushApiService.java:29` `// apiKey는 꼭 환경변수쪽에 세팅해놓을 것 (보안에 걸릴 수 있음)`.
- **ECC 대응 프로토콜**: STOP → **로테이션 최우선**(이미 커밋된 이상 파일 삭제만으로는 무효화되지 않음) → 환경변수/시크릿 매니저 이관 → 전수 재점검.

### 🔴 Critical-2: stage 프로파일이 운영 DB를 2분 주기로 변경
- **위치**: `application-stage.yml` (datasource) + `TargetPrepareTasklet` → `PushTargetRepository.deletePushTarget()`
- **내용**: stage의 datasource 호스트가 prod와 **동일한 `happy-app-homepage` RDS**인데 cron이 `0 */2 * * * *`(2분 주기).
- **영향**: 스테이징 인스턴스가 떠 있는 동안 **운영 `PUSH_TARGET` 테이블이 2분마다 전체 DELETE 후 재INSERT** 된다. 운영 배치가 같은 시간대에 돌면 대상 데이터가 유실되거나 상태가 뒤섞인다.
- **완화 요소**: stage는 `mock-send-enabled: true`라 실제 발송 대상은 코드 하드코딩 5건 → **실제 푸시 오발송은 막혀 있으나 DB 파괴는 그대로 발생**.

### 🔴 High-3: 발송 루프 전체가 단일 트랜잭션 → 중복 발송 가능
- **위치**: `PushSendTasklet.execute()` (`while(true)` 루프 전체)
- **내용**: Tasklet은 Step 트랜잭션 1개 안에서 실행된다. 루프 안 `markSending`/`markSent`는 **커밋되지 않고 쌓이기만** 한다.
- **재현 시나리오**: 대상 5,000건 → 1~4청크 발송 성공(`SENT` 마킹) → 5청크에서 API 타임아웃 → 예외 재throw → **Step 롤백** → 앞선 4,000건의 `SENT`가 전부 `READY`로 되돌아감 → 다음 크론(운영은 하루 1회이나 dev/stage는 1~2분) 재실행 시 **동일 4,000명에게 중복 푸시**.
- **부수 효과**: `markSending`으로 의도한 동시 실행 중복 방지도 커밋되지 않으므로 무효. 대량 건수에서 장기 트랜잭션 → UNDO 압박.
- **권고 방향**: Tasklet 자체 루프를 걷어내고 **Chunk 지향 Step**(`JdbcPagingItemReader` + `ItemWriter`)으로 전환해 청크 단위 커밋을 프레임워크에 위임. 최소 조치로는 청크 처리를 `REQUIRES_NEW` 별도 트랜잭션으로 분리.

### 🟠 High-4: pushId null 시 NPE
- **위치**: `TargetPrepareTasklet.java:43`
- **내용**: `PUSH_MASTER` 미존재 시 `pushId`가 `null`인 채 진행 → `ExecutionContext.putLong("pushId", pushId)`에서 `Long → long` 언박싱 NPE.
- **권고**: 조회 직후 `orElseThrow`로 fail-fast. (ECC `rules/common/coding-style.md` — 명시적 에러 처리)

### 🟠 Medium-5: 조건 없는 전체 DELETE
- **위치**: `PushTargetRepository.deletePushTarget()` — `DELETE FROM PUSH_TARGET` (WHERE 없음)
- **내용**: 주석상 truncate의 트랜잭션 이슈를 피해 delete로 바꾼 흔적. pushType이 `ATTENDANCE` 하나뿐인 현재는 무해하나, 유형이 늘면 타 유형 대상까지 삭제한다.
- **권고**: `WHERE PUSH_ID = :pushId` 추가.

### 🟠 Medium-6: Oracle IN 절 1000개 한계
- **위치**: `markSending` / `markSent` / `markRetryOrFailed` 의 `WHERE TARGET_ID IN (:ids)`
- **내용**: `chunk-size` 기본값이 정확히 **1000** = Oracle IN 리스트 상한. 값을 조금만 올리면 `ORA-01795`로 즉시 실패.
- **권고**: chunk-size 상향 대비해 배치 UPDATE(`batchUpdate`) 또는 `IN` 분할.

### 🟠 Medium-7: 재시도 상태머신 미동작
- **위치**: `PushSendTasklet.java:119` — `pushTargetRepository.markRetryOrFailed(targets);` 주석 처리
- **내용**: 실패 건이 `SENDING`에 남고 예외만 재throw. 복구는 `recoverStuckSendingTargets`(5분 타임아웃)에만 의존한다.
- **영향**: `max-retry-count: 3` 설정과 `FAILED` 상태, `RETRY_COUNT` 컬럼이 **실질적으로 사용되지 않음**.

### 🟡 Low-8: 코드 위생 (ECC coding-style 기준)
- **미사용 변수**: `beforeCount` · `afterCount` · `insertedCount`(TargetPrepareTasklet), `recoveredCount` · 3곳의 `count` · `finalCount`(PushSendTasklet) — 로깅/알림에 쓰려다 만 흔적. ECC "죽은 코드 제거" 위반.
- **실회원번호 하드코딩**: `PushSendTasklet.createMockTargets()`에 실제 회원번호 5건 + 실명 주석. mock 데이터라도 **PII 커밋**에 해당.
- **테스트 부재**: `contextLoads` 1건. ECC는 Test-Driven이 SOUL 원칙.
- **`bodyToFlux(...).blockFirst()`**: 단건 응답이므로 `bodyToMono(...).block()`이 의미상 정확 (`PushApiService.java:47`).
- **불필요한 웹서버**: WebClient만 쓰는데 `spring-boot-starter-webflux` 때문에 8080 리액티브 서버가 기동. `spring.main.web-application-type: none` 권고.
- **로그백 `${FILE_LOG_PATTERN}` 미정의 가능성**: `logback-spring.xml`에 Boot `defaults.xml` include가 없음.

## 명령/코드 스니펫
```bash
# 시크릿 위치만 확인 (값 노출 없이)
git ls-files src/main/resources/config/
grep -rn -E "password|api-key|bot-token|webhook-url" src/main/resources/config/ | sed -E 's/:.*/: <REDACTED>/'

# stage/prod DB 호스트 동일 여부 확인
grep -h "url:" src/main/resources/config/application-{stage,prod}.yml
```

## 결과
- `ha-push-batch` KB 신규 등록 — [INDEX.md](./INDEX.md)에 배치 흐름·도메인 테이블·프로파일·외부연동 맵 영구 반영.
- ECC 기준 1차 진단: **Critical 2 / High 2 / Medium 3 / Low 1**. 조치는 전부 미착수(사용자 판단 필요).
- 공통 문서 갱신: [README.md](../../README.md) 프로젝트 표 등록, [security-review.md](../../shared/security-review.md) 적용 이력 추가, [ecc-reference.md](../../shared/ecc-reference.md)에 Boot 프로젝트 매핑 추가 + `rules/java` 존재 오기 정정.

## 다음 할 일 (TODO)
- [ ] **(Critical) 노출 크리덴셜 전량 로테이션** — 운영 Oracle 계정, 운영 푸시 API 키, Slack 웹훅, 텔레그램 봇 토큰. 저장소 접근 이력이 있는 이상 **파일만 지워도 유효한 자격증명은 살아있다. 로테이션이 1순위.**
- [ ] **(Critical) 설정 외부화** — `config/*.yml`을 환경변수(`${DB_PASSWORD}` 등)/시크릿 매니저로 이관 후 git 추적 제외. `git filter-repo`로 히스토리 정리 검토.
- [ ] **(Critical) stage datasource를 스테이징 DB로 분리** — 분리 전까지는 stage 인스턴스 기동 금지 또는 cron 비활성.
- [ ] **(High) 발송 Step을 Chunk 지향으로 재설계** — 청크 단위 커밋 + 재시작 지점 확보로 중복 발송 차단.
- [ ] **(High) `pushId` fail-fast 처리.**
- [ ] **(Medium) `deletePushTarget`에 `WHERE PUSH_ID` 추가 / IN 절 분할 / `markRetryOrFailed` 복구.**
- [ ] **(Low) mock 실회원번호 제거, 미사용 변수 정리, Slack·Telegram 알림 연결**(현재 실패 무통보 상태).
- [ ] 배포/운영 환경 확인 — 이 배치가 **어느 서버에서 어떻게 기동되는지 미확인**. 확인 후 [server-env.md](../../shared/server-env.md)에 추가.
- [ ] `com.example` 패키지를 `com.spc.hpc` 계열로 정리할지 결정.

## 참고 링크
- [ha-push-batch INDEX](./INDEX.md)
- [ECC 참조 · 작업 프로토콜](../../shared/ecc-reference.md)
- [보안 진단 기준](../../shared/security-review.md)
- ECC 원문(참조 전용): `../../../ECC/rules/java/security.md`, `../../../ECC/rules/common/coding-style.md`, `../../../ECC/skills/springboot-patterns/SKILL.md`
