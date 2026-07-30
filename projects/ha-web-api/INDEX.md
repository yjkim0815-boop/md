---
문서유형: INDEX
프로젝트: ha-web-api
작성일: 2026-07-16
최종수정: 2026-07-26
상태: 진행중
요약: 신규 홈페이지 리뉴얼 Spring API 백엔드 — Java 21 / Spring 6 기반. Spring6/Jakarta/Tomcat10.1 세팅 완료(빌드·기동), 실검증 진행중. 코드베이스 구조 맵 반영(2026-07-22)
---

# 📇 ha-web-api 문서 인덱스

> 🔗 **상위 프로젝트**: [homepage-ai-renewal(홈페이지 AI 리뉴얼)](../homepage-ai-renewal/INDEX.md) — 프론트 [`happypoint-web2`](../happypoint-web2/INDEX.md)와 한 프로젝트.

## 프로젝트 정체성 (중요)
- **이 프로젝트 = 신규 홈페이지 리뉴얼의 Spring API 백엔드.**
- **Java 21 / Spring 6** 기반. 지금까지 진행한 Spring6/Jakarta/Java21/Tomcat10.1 마이그레이션 작업물이 **실제로 속하는 프로젝트**이다.
- 레거시 기존 홈페이지(Spring MVC)는 별도 프로젝트 **`ha_web`** 이며 혼동 금지 → [ha_web INDEX](../ha_web/INDEX.md)

## 프로젝트 개요
- **워크스페이스 폴더**: `ha-web-api` (KB 기준 `../../../ha-web-api`). ⚠️ **별도 체크아웃 `j-ha-web-api`(브랜치 `dev-j`)** 에 신규 프론트(happypoint-web2) 연동용 **계약 API 레이어(`com.spc.hpc.api.*`)** 가 있음 — 아래 "계약 API" 절 참조.
- **Bitbucket remote**: `bitbucket.org/sectanine/ha-web-api.git`
- **스택**: Java 21 / Spring 6.1.14 / Spring Security 6.2.6 / Jakarta EE / Tomcat 10.1.57 / MyBatis 3.5.16
- **주요 브랜치**: `feature/WORK-16665`(Spring6 이관), **`dev-j`(계약 API·개발서버 dev-www 배포)**
- **개발서버 배포처**: `dev-www.happypointcard.com` (프론트 happypoint-web2의 `LEGACY_BASE`가 이곳을 호출)

## 문서 목록
| 문서 | 유형 | 상태 | 요약 |
|------|------|------|------|
| [ARCHIVE-WORK-16665-spring-upgrade.md](./ARCHIVE-WORK-16665-spring-upgrade.md) | ARCHIVE | 완료(빌드·기동) | Spring6/Java21/Jakarta/Tomcat10.1 전면 세팅·마이그레이션 풀 기록 |
| [WORKLOG-20260729-model-api-migration.md](./WORKLOG-20260729-model-api-migration.md) | WORKLOG | 진행중 | 레거시 페이지 컨트롤러 → 모델API 전수 이식(A 스텁32 완료 / B 신규 진행 / C 라우트) |
| [WORKLOG-20260721-nextjs-api-migration-map.md](./WORKLOG-20260721-nextjs-api-migration-map.md) | WORKLOG | 진행중 | JSP 페이지→Next.js(happypoint-web2) 이관용 "페이지 URL↔API" 매핑 인벤토리 |
| [WORKLOG-20260722-codebase-analysis.md](./WORKLOG-20260722-codebase-analysis.md) | WORKLOG | 진행중 | 코드베이스 구조 전수 파악 + ECC 기준 보안 1차 진단(크리덴셜 평문 Critical) |
| [api-detail-response.md](./api-detail-response.md) | SHARED | 진행중 | ha-web-api 상세 응답코드(detailCode/detailMessage·도메인 message·로그인 rpsCd) — 공통 규격은 conventions/api-response.md |
| [tendency/weekly/TENDENCY-2026-W30.md](./tendency/weekly/TENDENCY-2026-W30.md) | TENDENCY | 진행중 | 프로젝트 주간 성향 — 인프라·이관설계·문서정비, 확인/안전/현행화 선호 |
| [worklog/weekly/WORKLOG-2026-W31.md](./worklog/weekly/WORKLOG-2026-W31.md) | WORKLOG | 진행중 | 2026-W31 — 인증 me→check, KCB 본인인증 postMessage, /api/page/cert 라우팅 통일 |
| [worklog/weekly/WORKLOG-2026-W30.md](./worklog/weekly/WORKLOG-2026-W30.md) | WORKLOG | 진행중 | 2026-W30(07-20~26) 주간작업 — 스테이징톰캣/Scouter, 이관매핑, 계약API/로그인 |

> 🔁 **회고 규칙(2026-07-26 개정)**: [운영 규칙](../../README.md#️-운영-규칙--성향작업내역-주기-2026-07-26-확정-최우선) 준수. 프로젝트 성향/작업내역은 **주 단위**(`tendency/weekly/`·`worklog/weekly/`), 작업 전 **최근 3개월치**를 먼저 읽고 반영.

## 🧱 코드베이스 구조 (2026-07-22 실측)

### 규모
| 항목 | 수치 |
|------|------|
| `src` 전체 파일 | 약 2,048 |
| Java 클래스 | 335 |
| JSP | 516 |
| 서비스 도메인 패키지 | 22 |
| 테스트 | **0** (`src/test` 없음) |

### 패키지 트리 (`com.spc.hpc`)
```
home/
├─ controller/   pc · mobile · survey · shared · rest   ← 화면(JSP) + REST 분리
├─ services/     22개 도메인: coupon event user card donation brand store
│                alliance survey sms cert social common attach external
│                banner sleeveqr emergency legacy board pcweb shared
├─ restapi/      model(RestResponse·ResponseBuilder) · util · exception
├─ config/       spring(SecurityConfig·KMSConfig·YmlConfig·Log4j2ConfigurationFactory)
│                mybatis · converter · error · jsp · properties
├─ filter/       Hsts · Sitemesh · Redirect · Paging · Spc · DeviceRedirect
│                security/AntiSamyFilter
├─ security/     @Login · @Bearer 어노테이션 + LoginAspect · BearerAspect · SessionUser
├─ interceptor/  SpcInterceptor
├─ listener/ util/
common/          vo · util · service
dao/
```

### 핵심 구성 요점
- **Spring Boot 아님**: 순수 WAR + `web.xml` + `classpath:/*/context-*.xml`(XML 빈) + `@Configuration` 혼용.
- **DataSource는 JNDI 2개** — `jdbc/ha`(Oracle) · `jdbc/cms`(MySQL). 각각 별도 `SqlSessionFactory` / `TransactionManager`.
  매퍼 스캔은 `com.spc.hpc.home.services` 하위를 어노테이션(`@DefaultMapper` 등)으로 분기. 매퍼 XML은 `resources/mybatis/{default,cms}/**`.
- **DataSource 로깅 래핑**: `log4jdbc-remix`(`Log4jdbcProxyDataSource`) + 커스텀 `RemoveEmptyLineFormatter`.
- **인증**: `@Login` / `@Bearer` 커스텀 어노테이션 + AspectJ 인터셉트 방식(Spring Security 필터체인 단독 아님).
- **필터 순서**(web.xml): `hsts` → `encoding`(UTF-8) → `spc` → `redirect` → `sitemesh` → `paging` → `antiSamy`(정책 `xss/antisamy-myspace.xml`). `deviceRedirect`는 주석 처리됨.
- **세션 쿠키** `secure=true` 적용.
- **뷰**: JSP + JSTL 3 + SiteMesh 3(레이아웃 `WEB-INF/layout/*.jsp`) + urlrewrite.
- **SSO**: `webapp/sso/*.jsp`(isignplus 연동). `application.yml`상 `sso.enable=false`.

### 외부 연동 인벤토리
SPC 사내 전문 API(happypointcard `processHpc`) · 해피오더 · 해피마켓 · KCB/OKNAME 본인인증(NiceID·IPIN2Client·okname, `ext-libs` 로컬 jar) ·
SSO(isignplus) · 인터파크 · 현대오일뱅크 · SKT 에이닷 · 카카오 공유 · 네이버 지도 · Instagram/Facebook/YouTube Graph ·
VOC(homevoc-hpc) · Cloudflare Turnstile · GA4 · Amplitude · AWS(S3 · KMS · DynamoDB).

## 🔌 계약 API 레이어 (신규 프론트 happypoint-web2 연동) — 2026-07-26 추가
- **위치**: `j-ha-web-api`(dev-j) 의 `com.spc.hpc.api.*` — HTML 스크래핑이 아닌 **JSON 계약 API**. 프론트는 `{LEGACY_BASE=dev-www}/api/...` 로 호출.
- **패키지**: `api/{auth,alliance,brand,cert,customer,donation,email,event,live,main,member,mypage,presentation,reception,sleeveqr,store,survey,common}`
- **응답 규약**: HTTP는 항상 200, 성공/실패는 body `code`(또는 `success`)로 판별 (`ApiError`/공통 응답).
- **인증 API** (`api/auth/AuthApiResource`):
  - `POST /api/auth/login` — body `{ login, password, rememberMe }`(`LoginVm`). 성공 시 `{success:true, returnUrl, userId, userNm, mbrGrCd, ...}` + **HttpSession(JSESSIONID) 쿠키**. 실패 시 `{success:false, message, redirect}`. (checkauth.jsp 로직 이식, `sso.enable=false` 경로 `SsoService.devAuth` = MB2000H0 전문)
  - `POST /api/auth/logout` — 세션 무효화
  - `GET /api/auth/me` — 현재 사용자(미로그인 401)
- **프론트 연동**: happypoint-web2가 BFF `app/api/login/route.ts`로 프록시해 JSESSIONID를 프론트 오리진으로 relay. 상세: [happypoint-web2 INDEX](../happypoint-web2/INDEX.md).
- 예) `GET /api/alliance/corporation?category&onOff&page` — 제휴사 계약 API(`api/alliance/AllianceApiResource`).

## 현재 상태 / 핵심 메모
- ✅ Java21/Spring6/Jakarta 세팅 완료 → `mvn clean package -P dev` BUILD SUCCESS, Tomcat 10.1.57 기동 성공(컨텍스트 초기화까지).
- ✅ **계약 API(`api/*`) + 인증(`/api/auth/*`) 구현됨** → dev-j/dev-www 기준 프론트 로그인 연동 대상. 프론트 짝 = [happypoint-web2](../happypoint-web2/INDEX.md).
- ⏭ **실검증 TODO**: JSP 화면 렌더링, SiteMesh 레이아웃, DB(jdbc/ha·jdbc/cms), 본인인증 벤더 jar(NiceID/okname) JDK21 동작 — 아카이브 16절 참조.
- **포트**: HTTP 9022 / shutdown 8010. **빌드 산출물**: `ha-web.war`(전 프로파일 동일명).
- **SiteMesh**: `ext-libs`의 `sitemesh:3.0.1-jakarta` 커밋본 사용.
- **빌드 환경**: JDK 21 + Maven 3.9.x (Windows). IntelliJ Runner JRE 21.
- **pom 특이점**: parent가 `spring-framework-bom`(Boot parent 아님). 로컬 `ext-libs`를 maven repository로 등록해 벤더 jar 사용.
- 🔴 **미해결 Critical**: `config/application*.yml`에 AWS 키 3세트 + 벤더 API 키가 **평문으로 git 커밋**됨(값 미기재).
  Jasypt 의존성은 있으나 미사용. 조치 순서·상세는 [코드베이스 분석 워크로그](./WORKLOG-20260722-codebase-analysis.md) 참조.
- ⚠️ **기술부채 메모**: 테스트 0건 / AWS SDK v1 사용(EOL 단계) / Log4j2 `2.17.0` 고정(BOM 무시) /
  `NiceID-1.1.jar`가 프로젝트 루트·`ext-libs` 양쪽 중복 / pom에 node v8.12.0 프론트 빌드 설정 잔존(유물).

> ⚠️ 아카이브 문서 본문은 작업 당시 `ha_web` 폴더에서 진행한 경로가 다수 언급되지만, **작업 결과물의 귀속 프로젝트는 ha-web-api** 이다. (경로 표기는 당시 작업 위치 기준)

## 참고 (공통 문서)
- [공유 지식 베이스 README](../../README.md)
- [서버 환경](../../shared/server-env.md)
