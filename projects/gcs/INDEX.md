---
문서유형: INDEX
프로젝트: gcs
작성일: 2026-07-22
최종수정: 2026-07-22
작성자: dominic
상태: 진행중
요약: 해피포인트 앱 내 기프트카드(상품권) 서비스 백엔드 API 서버 — Spring Boot 3.4 / Java21 / Gradle / JPA + QueryDSL / PostgreSQL / Redis(Redisson). KB 두 번째 Boot·Gradle 프로젝트이자 **최초의 JPA 프로젝트**. 프론트 짝은 `gcs_fo`
---

# 📇 gcs 문서 인덱스

> 📛 **폴더/슬러그 명명 규칙**: `projects/<slug>/` 의 `<slug>` 는 **Bitbucket 저장소명과 정확히 일치**시킨다. 매핑표는 [루트 README](../../README.md) 참조.

## 프로젝트 개요
- **저장소명(=KB 슬러그)**: `gcs` ✅ 로컬 폴더명과 동일 (드물게 일치하는 케이스)
- **로컬 폴더**: 워크스페이스 루트 하위 `gcs` (KB 기준 `../../../gcs`)
- **설명**: **해피포인트 앱 기프트카드(상품권) 서비스의 백엔드 API 서버**. 카드 발급·활성화·충전·승인(결제)·환불·정산을 **채널별 API**로 제공한다.
- **스택**: Java **21**(Corretto) / **Spring Boot 3.4.2** / **Gradle** / **JPA(Hibernate) + QueryDSL 5** / **PostgreSQL 17** / **Redis(Redisson)** / Jasypt / AWS KMS·S3 / Micrometer Tracing(Zipkin) / springdoc(Swagger·Redoc)
- **remote/브랜치**: `bitbucket.org/sectanine/gcs.git` / `master`(기본) · `develop`(작업) · `qa` · `release` · `feature/WORK-*`·`feature/SQD-*`(이슈 브랜치, PR 머지)
- **규모**: `src/main/java` **713 파일 / 약 57,300줄** · 테스트 **48 파일** (KB 내 **테스트가 실재하는 유일 수준**의 프로젝트)
- **버전**: `build.gradle` `version = '1.0.5'`
- **베이스 패키지**: `com.spc.gcs` ⚠️ 주류(`com.spc.hpc`)와 다름

### 🔗 짝 프로젝트 (중요)
| 구분 | 저장소 | 로컬 | 상태 |
|------|--------|------|------|
| **백엔드 (이 문서)** | `gcs` | `gcs` | ✅ 등록 |
| 웹뷰 프론트 | [gcs_fo](../gcs_fo/INDEX.md) | `gcs-fo` | ✅ 등록 |
| 임베드 호스트(앱) | [thehappy_ios](../thehappy_ios/INDEX.md) · [thehappy_aos](../thehappy_aos/INDEX.md) | `ha-ios` · `ha-aos` | ✅ 등록 |

> 🎁 **GCS 서비스 프론트/백 분리 해소(2026-07-22)**: `gcs_fo` 등록 시 "서버 측 판정 불가"로 남겨뒀던 선행 과제가 이 문서로 **해소**됐다. 토큰 발급·CORS·결제 검증의 **서버 측 판정은 이제 여기서** 한다.
> 🟢 **ECC 적용 강도 최상위**: [ha-push-batch](../ha-push-batch/INDEX.md)에 이은 **두 번째 Boot·Gradle** 프로젝트이자 **KB 최초로 JPA를 실제 사용**한다 → 그동안 "JPA 예시는 미적용"이던 단서가 **여기서는 반대로 유효**해진다. 상세는 [ecc-reference §4-5](../../shared/ecc-reference.md).

## 문서 목록
| 문서 | 유형 | 상태 | 요약 |
|------|------|------|------|
| [WORKLOG-20260722-codebase-analysis.md](./WORKLOG-20260722-codebase-analysis.md) | WORKLOG | 진행중 | 최초 코드베이스 분석 + ECC `rules/java/security.md` 기준 1차 진단 (🔴 Critical 1 / High 2 / Medium 2) |

## 🗂️ 구조 (`src/main/java/com/spc/gcs`)
```
com/spc/gcs/
├─ controller/
│  ├─ api/          채널별 REST 엔드포인트 (아래 §채널 구성 참조)
│  └─ view/         JSP/템플릿 뷰 (약관·결제·정기결제·이미지)
├─ service/         29개 도메인 패키지 — 실제 비즈니스 로직
├─ repository/      JPA Repository + QueryDSL Custom 구현체(*RepositoryCustomImpl)
├─ entity/          JPA 엔티티 47종 + converter/
├─ dto/ mapper/ enums/ constant/ vo/
├─ config/          Redisson·Jasypt·AwsKms·S3·WebClient·Querydsl·Swagger·Async·transacion/
├─ interceptor/     ApiAuthInterceptor(⭐ 인증 관문) · JwtSecuredUrisConfig
├─ filter/          LogEscapeFilter · LogbackMdcFilter(추적 MDC)
├─ aspect/          S9DistributedLockAop(⭐ 분산락) · AopForTransaction
├─ util/            JwtUtil · Aes256Util · HpcAutUtil · RedissonCommandUtil · MaskingUtil …
└─ exception/ handler/ annotation/ serializer/ wrapper/
```

## 📡 채널 구성 (이 프로젝트의 핵심 설계축)
GCS는 **"어느 채널에서 들어온 요청인가"** 로 API가 갈린다. 신규 기능은 반드시 채널을 먼저 특정한다.

| 채널 | 컨트롤러 | 소비자 | 역할 |
|------|----------|--------|------|
| **승인** | `api/approvechannel/ApproveChannelApiController` | 오프라인 POS | 카드 승인·충전·결제 |
| **월렛** | `api/walletchannel/WalletChannelApiController` | 해피앱 월렛 / [gcs_fo](../gcs_fo/INDEX.md) | 회원·카드·환불·본인인증 |
| **판매** | `api/salechannel/SaleChannelApiController` | 카카오톡 선물하기 등 | 카드 발급·활성화 |
| **관리자** | `api/{brand,product,orderform,corp,adminvoc,statistics,calculation,…}` | 해피콘 BO | 운영·정산·통계 |
| **공통** | `api/common/CommonApi` | 전 채널 | ⭐ **인증 토큰 발행** |

## 🔐 인증 / 접근제어 (⚠️ Spring Security 미사용)
- **Spring Security 의존성이 없다.** 인증은 **직접 구현한 `HandlerInterceptor`** (`interceptor/ApiAuthInterceptor.java`)가 담당한다.
  - → ECC `springboot-security` 스킬의 `SecurityFilterChain`·`CookieCsrfTokenRepository` 예시는 **그대로 적용 불가**. 개념만 차용한다.
- **토큰 흐름**: 프론트/채널 → `POST /v1/common/api/token` (`apiAuthKey` + `channelCode` + `authCredential`(hpcAut) + `userAgent`) → **JWT 발급**(`util/JwtUtil`) → 이후 `Authorization: Bearer` 로 호출.
  - 프론트 측 대응 코드는 [gcs_fo](../gcs_fo/INDEX.md) `src/api/core/axios.config.ts`.
- **보호 URI 지정**: `application-*.yml` 의 `application.jwtSecuredUris` 목록 + `interceptor/JwtSecuredUrisConfig`.
  - ⚠️ **화이트리스트가 아니라 "보호할 URI 열거" 방식**이다. 신규 엔드포인트 추가 시 **yml에 등록하지 않으면 인증 없이 열린다**(누락이 곧 취약점). → 신규 API PR 체크 필수 항목.
- **CORS**: `ApiAuthInterceptor.checkPreFlight()` 에서 **Java 소스에 하드코딩된 Origin 화이트리스트**로 판정. dev 환경은 추가로 **하드코딩된 사내 IP 목록**을 허용한다. → [WORKLOG](./WORKLOG-20260722-codebase-analysis.md) High-2.

## 🔒 동시성 — 분산락 (금전 도메인 핵심)
- 커스텀 어노테이션 **`@S9DistributedLock(key = "#lockName")`** (SpEL) + `aspect/S9DistributedLockAop` + Redisson `RLock`. 현재 **10개 파일**에서 사용.
- `@Transactional` 은 **67개 파일**에 분포.
- ⚠️ **`-parameters` 컴파일 옵션이 필수**다. Spring Boot 3.1+ 부터 파라미터명이 바이트코드에 안 들어가 SpEL이 깨진다. IntelliJ: `Java Compiler → Additional command line parameters` 에 `-parameters`, 그리고 `out/` 삭제 후 재컴파일. (출처: 저장소 `README.md`)
- 📌 **최근 작업 맥락**: `WORK-16085` 에서 **RLock·`@Transactional` 중복 호출 제거**와 `executeWithTimeout` 버그 수정이 진행됐다. 락 관련 코드를 건드릴 때 이 이슈의 커밋들(`157eba63`·`98bf32b1`·`7def00fd`)을 먼저 읽는다.

## 🗄️ 영속 계층
- **JPA(Hibernate) + QueryDSL 5**(`jakarta` classifier). 동적 쿼리는 `*RepositoryCustomImpl` 에 QueryDSL로 구현하는 게 이 프로젝트 관례.
- **네이티브 쿼리 0건 / `@Query` 4개** → SQL 인젝션 표면이 매우 좁다. ✅
  - ⚠️ **바인딩 규칙이 KB 내 또 다른 변종**이다: MyBatis 계열 `#{}` · ha-push-batch `:param` · **`gcs` 는 QueryDSL 타입세이프 API + JPQL `:param`**. 인젝션 판정 시 혼동 금지.
  - 예외: `WORK-16523`에서 대량 업서트 성능 목적으로 **`JdbcTemplate` 을 부분 도입**(`service/memberstore`). 이 경로만 바인딩을 별도 확인한다.
- **`ddl-auto: validate` · `open-in-view: false`** — 전 환경 동일. ✅ ECC/Boot 모범사례와 일치하므로 **바꾸지 말 것**.
- DDL 정본은 저장소 `docs/DDL.sql` · `SequenceDDL.sql` · `HappyconDDL.sql`.

## ⚙️ 빌드 / 환경
- **Gradle** + Boot 3.4.2 plugin, Java 21. 로컬 `lib/` **flatDir 저장소**를 사용한다(외부 JAR 직접 포함) → 의존성 스캔 시 mavenCentral 밖의 JAR 존재를 감안한다.
- **프로파일**: `application-local.yml` · `application-dev.yml` · `application-real.yml` (3종 모두 저장소에 커밋됨).
- **설정 암호화**: **Jasypt `ENC(...)`** 사용 — 단 **DB 비밀번호·MobileOK 키비번 3건에만** 적용돼 있다. ⚠️ AWS·PG 크리덴셜은 평문 → [WORKLOG](./WORKLOG-20260722-codebase-analysis.md) **Critical-1**.
- **Swagger/Redoc**: `real` 에서 `swagger-ui.enabled: false` ✅ (접근주소 `/swagger-ui`, `/docs/redoc.html`)
- **도메인**: dev `dev-gcs-api.happypointcard.com` · real `gcs-api.happypointcard.com` (어드민은 `*-gcs-admin-api.*`)
  - ⚠️ 저장소 `README.md` 에는 도메인이 "(미정)"으로 남아 있다 — **문서가 코드보다 뒤처져 있음**.
- **CI 없음**: `bitbucket-pipelines.yml`·`Jenkinsfile`·`Dockerfile` 모두 부재. 48개 테스트가 **자동 실행되지 않는다**.

## 현재 상태 / 핵심 메모
- **현재 브랜치 `develop`**, 워킹트리 클린.
- **최근 작업 흐름**: `WORK-16085`(분산락·트랜잭션 중복 호출 정리 / 예외 로그 고도화) → `WORK-16523`(MEMBER_STORE_CODE 벌크 업서트 + JdbcTemplate 성능 개선 → 기프트카드 동의여부 필드 → Admin SwaggerConfig → 이니시스 계좌인증 DTO `mTxid` 명시).
- **테스트 48개는 KB 내 최대 자산**이다. ECC `tdd-workflow`·`springboot-verification`·`verification-loop` 를 **KB에서 유일하게 온전히 적용할 수 있는 프로젝트**. (다만 CI 부재라 실행은 로컬 수동)
- ⚠️ **저장소 `README.md` 의 패키지 구조 설명이 완전히 다른 프로젝트 기준**이다(`com.spc.happymarket`, 샵바이·쿠폰·기획전 등). 실제는 `com.spc.gcs`. **저장소 README를 구조 근거로 삼지 말 것** — 이 INDEX가 정본이다.
- 💰 **금전성 자산 프로젝트**: 카드 충전·승인·환불·정산을 직접 다룬다. [ha_panel](../ha_panel/INDEX.md)·[gcs_fo](../gcs_fo/INDEX.md)와 함께 **보안 심각도를 한 단계 높여** 판정한다.

## 참고 (공통 문서)
- [공유 지식 베이스 README](../../README.md)
- [ECC 참조 · 작업 프로토콜](../../shared/ecc-reference.md) — Spring Boot/JPA 매핑은 **§4-5**
- [보안 리뷰 기준](../../shared/security-review.md)
- [conventions/java.md](../../shared/conventions/java.md) · [conventions/spring.md](../../shared/conventions/spring.md) ✅ 적용 대상
- ⛔ **적용 안 됨**: [conventions/sql-mybatis.md](../../shared/conventions/sql-mybatis.md) (MyBatis 미사용 — JPA/QueryDSL), [server-env.md](../../shared/server-env.md) (외장 Tomcat/WAR 아님 — Boot 실행형)
