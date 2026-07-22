---
문서유형: SHARED
프로젝트: 공통
이슈키: --
작성일: 2026-07-21
최종수정: 2026-07-22
작성자: dominic
상태: 진행중
요약: ECC(Everything Claude Code) 우승자 컨텍스트 — 정체·작업 프로토콜·해피포인트 백엔드 매핑·프로젝트별 적용 강도(2026-07-22 ha_panel·thehappy_ios(§4-2)·thehappy_aos(§4-3)·gcs_fo(React/TypeScript §4-4)·**gcs(Spring Boot+JPA 매핑 §4-5) 추가**). 참조 전용(수정 금지)
---

# 🏆 ECC 참조 (Everything Claude Code)

> ⚠️ **경로**: `../ECC` (워크스페이스 루트 하위, KB `md/`와 나란히 위치) — **엔트로피 해커톤 우승자 컨텍스트**.
> **읽기·참조 전용. 절대 수정 금지.** 컨텍스트 학습 **최우선순위** 소스.

## 1. 작업 프로토콜 (중요)
1. **학습 최우선순위 = ECC.** 새 채팅/작업 시작 시 ECC의 관련 규칙·스킬을 먼저 참조한다.
2. **ECC를 근거로 사용자가 시킨 작업을 수행**한다.
3. 수행 결과·확정 사항을 **`md` 지식 베이스에 업데이트**한다 (공통/프로젝트 지속 고도화).
4. ECC는 참조만, `md`는 갱신 대상. 두 경로를 혼동하지 않는다.

## 2. ECC란
- **정체**: "Everything Claude Code" — 에이전트 하네스 운영체제(플러그인). 단순 config 모음이 아니라 agents/skills/hooks/rules/commands + 메모리·학습·보안 스캔·검증 루프를 갖춘 시스템.
- **버전**: v2.0.0 (로컬 체크아웃 기준 `5deee34c`, 2026-07-20). 원본 `github.com/affaan-m/ECC`.
- **규모**: 약 67 agents / 278 skills / 94 legacy command shims. 다중 하네스(Codex/Claude Code/Cursor/OpenCode/Gemini/Zed/Copilot) 지원.
- **핵심 철학(SOUL)**: Agent-First / Test-Driven / Security-First / Immutability / Plan-Before-Execute.

## 3. ECC 핵심 규칙 요약 (RULES.md · rules/common)
- **Must Always**: 도메인 작업은 전문 에이전트에 위임 · 구현 전 테스트 작성 · 입력 검증/보안 체크 유지 · 불변 업데이트 우선 · 기존 패턴 우선(새로 발명 금지) · 변경은 작고 리뷰 가능하게.
- **Must Never**: 비밀정보/시스템 절대경로 출력 · 미검증 변경 제출 · 보안 훅 우회 · 근거 없는 기능 중복 · 테스트 미확인 코드 배포.
- **coding-style**: KISS/DRY/YAGNI, 작은 파일(200~400줄, 최대 800), 함수 <50줄, 중첩 ≤4, early return, 매직넘버 금지, 명시적 에러 처리(조용한 catch 금지), 경계에서 입력 검증.
- **security(commit 전 필수)**: 하드코딩 비밀정보 0 · 입력 검증 · SQL 인젝션 방지(파라미터 바인딩) · XSS · CSRF · 인증/인가 · 레이트리밋 · 에러 메시지 정보 누출 금지.
- **agents(즉시 위임)**: 복잡 기능→planner, 코드 작성 직후→code-reviewer, 버그/신규→tdd-guide, 아키텍처 결정→architect. 위임 시 **완료 계약**: "백그라운드 대기 중"으로 턴 종료 금지, 위임하면 수집·통합까지 책임.

## 4. 해피포인트 백엔드 ↔ ECC 매핑
> 대상: [ha-web-api](../projects/ha-web-api/INDEX.md) (Java21/Spring6/Jakarta/MyBatis, WAR + 외장 Tomcat). ⚠️ Spring **MVC + JSP + MyBatis**이며 Boot/JPA 아님 → ECC의 Boot/JPA 예시는 **개념만** 차용.

### 직접 적용 가능한 ECC 스킬 (경로: `ECC/skills/<name>/SKILL.md`)
| ECC 스킬 | 용도 | 해피포인트 적용 시 주의 |
|----------|------|------------------------|
| `java-coding-standards` | Java17+ 네이밍/불변/Optional/스트림/예외/DI | Java21 기능(record/var/switch) OK. 포맷은 프로젝트 정본(space/4) 우선 |
| `springboot-patterns` | 계층구조·REST·검증·예외·페이징·필터·레이트리밋 | Controller→Service→Repository 개념·GlobalExceptionHandler·`OncePerRequestFilter`·생성자주입은 유효. **Spring Data JPA/`@Cacheable` 예시는 미사용**(MyBatis 기반) |
| `springboot-security` | 인증/인가·검증·CSRF·헤더·시크릿·레이트리밋 체크리스트 | 개념 유효. 이 프로젝트는 `SecurityFilterChain`(Security6)·`CookieCsrfTokenRepository` 사용 중. **SQL 인젝션 방지는 MyBatis `#{}` 로 대응** |
| `api-design` | REST URL/페이지네이션/에러응답(RFC7807) | 신규 API 설계 시 |
| `backend-patterns` | API·DB·캐싱 일반 패턴 | 개념 참조 |
| `security-review` / `security-scan` | 보안 리뷰 체크리스트 / AgentShield | [shared/security-review.md](./security-review.md) 확정 시 근거로 활용 |
| `search-first` | 코딩 전 조사 우선 워크플로 | 대규모 변경 전 표준 절차 |
| `tdd-workflow` · `verification-loop` · `eval-harness` | RED-GREEN-리팩터 / 검증 루프 | 실검증 TODO 진행 시 |
| `iterative-retrieval` · `strategic-compact` · `continuous-learning-v2` | 서브에이전트 컨텍스트/압축/학습 | 하네스 운용 |

### 관련 ECC 에이전트 (`ECC/agents/<name>.md`)
- `java-reviewer`, `java-build-resolver`(Maven/Gradle 빌드오류), `planner`, `architect`, `code-reviewer`, `security-reviewer`, `refactor-cleaner`, `doc-updater`, `e2e-runner`.

### 관련 ECC 규칙 (`ECC/rules/`)
- `rules/common/*` (coding-style·security·testing·git-workflow·agents·patterns·performance·hooks) — 언어 무관 공통.
- ✅ **정정(2026-07-22)**: `rules/java/` **팩이 실제로 존재한다** — `coding-style.md` · `security.md` · `patterns.md` · `testing.md` · `hooks.md` 5개. (이전 기술 "Java 전용 규칙 팩 없음"은 오기)
  - 각 파일은 프론트매터 `paths: ["**/*.java"]` 로 **Java 파일 편집 시 자동 적용되는 규칙 팩**이며, 대응하는 `rules/common/*` 를 상속·확장하는 구조다.
  - **보안 진단의 1차 근거는 `rules/java/security.md`** (Secrets Management / SQL Injection / Input Validation / Dependency Security / Error Messages).
  - 스킬(`java-coding-standards` 등)과 중복되는 부분이 있으나, **규칙(rules) = 상시 강제 / 스킬(skills) = 호출형 가이드**로 구분해 쓴다.

## 4-1. 프로젝트별 ECC 적용 강도 (중요)
> ECC 예시 코드 대부분이 **Spring Boot + JPA** 전제다. 우리 프로젝트는 대부분 그렇지 않으므로 적용 강도를 구분한다.

| 프로젝트 | 스택 | ECC Boot 계열 스킬 적용 강도 |
|----------|------|------------------------------|
| [ha-push-batch](../projects/ha-push-batch/INDEX.md) | **Spring Boot 3.5 / Java17 / Gradle / Spring Batch** | 🟢 **예시 코드 수준까지 직접 적용 가능** — KB 내 유일한 Boot·Gradle 프로젝트. `springboot-patterns`·`springboot-tdd`·`springboot-verification`을 그대로 적용해도 되는 유일 대상 |
| ha-web-api · ha_api · ha_web | WAR + 외장 Tomcat / Maven / Spring MVC + JSP / MyBatis | 🟡 **개념만 차용** — Boot 자동설정·JPA·`@Cacheable` 예시는 그대로 쓸 수 없음 |
| [ha_panel](../projects/ha_panel/INDEX.md) | WAR + **WebLogic** / **빌드툴 없음** / Spring MVC(4.x 스키마) / MyBatis / 자체 SPA(AMP) | 🔴 **보안·코딩 규칙만 적용. 구조 규칙은 적용 불가** — 아래 주의 참조 |
| [thehappy_ios](../projects/thehappy_ios/INDEX.md) | **Swift5 / iOS13+ / UIKit + Storyboard / Combine / CocoaPods+SPM** | ⛔ **Java/Spring 계열 전부 적용 불가.** 대신 **`rules/swift/*` 팩 + Swift 스킬/에이전트**를 쓴다 — 아래 §4-2 참조 |
| [thehappy_aos](../projects/thehappy_aos/INDEX.md) | **Kotlin2.0 / Android minSdk26 / XML+ViewBinding / Gradle KTS + buildSrc** | ⛔ **Java/Spring 계열 적용 불가**(Kotlin/JVM이지만 Android 클라이언트). 대신 **`rules/kotlin/*` 팩 + Kotlin 스킬/에이전트** — 아래 §4-3 참조 |
| [gcs_fo](../projects/gcs_fo/INDEX.md) | **React18 / TypeScript4.9 / CRA + CRACO / TanStack Query + Zustand** | ⛔ **Java/Spring 계열 적용 불가.** 대신 **`rules/react` + `rules/typescript` + `rules/web` 3중 팩** — 아래 §4-4 참조 |
| [gcs](../projects/gcs/INDEX.md) | **Spring Boot 3.4.2 / Java21 / Gradle / JPA + QueryDSL / PostgreSQL / Redis** | 🟢 **ha-push-batch에 이은 두 번째 "예시 코드 수준 직접 적용" 대상 (2026-07-22 등록 완료).** ⚠️ **JPA를 실제로 쓰는 KB 최초 프로젝트** → 지금까지 "JPA 예시는 미적용"이던 단서가 **여기서는 반대로 유효**해진다. 단 **Spring Security 미사용** → 보안 스킬은 개념만. 아래 §4-5 참조 |

- ⚠️ **SQL 바인딩 규칙이 프로젝트마다 다르다**: MyBatis 계열은 `#{}`, **`ha-push-batch`는 `NamedParameterJdbcTemplate`의 `:param`**. 인젝션 방지 판정 시 혼동 금지.
- ⚠️ 베이스 패키지가 제각각이다: `com.spc.hpc`(주류) / `com.example`(ha-push-batch) / **`hp.panel`(ha_panel)**.

### ⚠️ ha_panel 특이사항 (ECC 적용 시 주의)
1. **`api-design`(REST) 스킬을 적용하지 말 것** — 이 프로젝트는 `*.do` + 쿼리 파라미터 `method=` 로 분기하는 레거시 방식이다. ECC `rules/common/patterns.md`의 **"기존 패턴 우선(새로 발명 금지)"** 원칙에 따라 **현행 관례를 유지**한다.
2. **`dependency security`(CVE 스캔)는 현 상태로 수행 불가** — `pom.xml`/`build.gradle`이 없어 의존성 목록 자체가 저장소에 없다. 스캔 요구 시 **빌드 파일 도입이 선행 과제**다.
3. **`tdd-workflow`/`verification-loop`는 즉시 적용 불가** — 테스트 소스 디렉토리 자체가 없다. 빌드 파일 도입 후에야 가능.
4. **여기서 가장 실효성 있는 ECC 자산 = `rules/java/security.md`(Secrets Management) + `rules/common/coding-style.md`(명시적 에러 처리)** — 실제로 이 두 규칙으로 Critical 2 / High 2가 검출됐다. → [진단 기록](../projects/ha_panel/WORKLOG-20260722-codebase-analysis.md)
5. **프론트 규약은 ECC가 아니라 저장소 자체 문서가 정본** — `ha-panel/META-INF/read/coding-conventions.txt`(케밥케이스·CSS 속성 순서·AMP API). ECC의 React/JS 스킬은 AMP에 맞지 않는다.

## 4-2. Swift / iOS 매핑 (thehappy_ios)
> 대상: [thehappy_ios](../projects/thehappy_ios/INDEX.md). ⚠️ ECC Swift 자산은 **SwiftUI + Swift 6.2 동시성 + Swift Testing** 전제가 많은데, 이 앱은 **iOS 13 / Swift 5 / UIKit + Storyboard / Combine**이다. 강도 구분 필수.

- **규칙 `rules/swift/`** — `coding-style` · `patterns` · `security` · `testing` · `hooks` **5종 존재**. 프론트매터 `paths: ["**/*.swift","**/Package.swift"]` → Swift 파일 편집 시 **상시 자동 적용**. 🟢
  - **보안 진단 1차 근거 = `rules/swift/security.md`**. 핵심 규칙 *"민감정보는 Keychain, `UserDefaults` 금지"* → 이 앱은 `HappyKeychain`·`HappyUserDefaults`가 **공존**하므로 **저장 항목 분류 점검이 최우선 진단 포인트**.
- **스킬**: `swift-protocol-di-testing` 🟢(Repository 프로토콜 구조와 일치, 테스트 보강 1순위) · `ios-icon-gen` 🟢 · `swift-actor-persistence` 🟡(개념만) · `swiftui-patterns` 🔴(UIKit이라 미적용) · `swift-concurrency-6-2` 🔴(Swift5+Combine이라 미적용)
- **에이전트**: `swift-reviewer`(*"MUST BE USED for Swift projects"* → Swift 변경 시 기본 위임) · `swift-build-resolver`(Xcode/SPM/CocoaPods 빌드오류)
- ⛔ **이름 함정**: `skills/cisco-ios-patterns` 는 **Cisco 네트워크 장비 IOS**다. Apple iOS와 무관하니 혼동 금지.
- ⚠️ **Swift 컨벤션은 KB에 없다.** 1차 정본은 **저장소 자체 `ha-ios/AGENTS.md`**(들여쓰기 4칸, 기능 폴더 유지, 요청 없는 리팩터링 금지). ECC보다 이쪽이 우선.
- ⚠️ **SQL 바인딩 규칙 무관**: 클라이언트라 DB 직접 접근이 없다. 서버 측은 [ha_api](../projects/ha_api/INDEX.md)에서 판정.
- ✅ **안드로이드 짝 [thehappy_aos](../projects/thehappy_aos/INDEX.md) 등록 완료(2026-07-22)** → 매핑은 아래 §4-3.

## 4-3. Kotlin / Android 매핑 (thehappy_aos)
> 대상: [thehappy_aos](../projects/thehappy_aos/INDEX.md). ⚠️ ECC Kotlin 자산은 **Compose + KMP + Koin/Hilt + Kotest/MockK** 전제가 많은데, 이 앱은 **XML View + 단일 모듈 + DI 프레임워크 부재 + JUnit4**다. 강도 구분 필수.

- **규칙 `rules/kotlin/`** — `coding-style` · `patterns` · `security` · `testing` · `hooks` **5종 존재**. 프론트매터 `paths: ["**/*.kt","**/*.kts"]` → Kotlin 파일 편집 시 **상시 자동 적용**. 🟢
  - `hooks.md`만 `**/build.gradle.kts`를 추가 대상으로 잡는다 → **Gradle 스크립트 편집 시에도 규칙이 걸린다**.
  - **보안 진단 1차 근거 = `rules/kotlin/security.md`** — 섹션: Secrets Management / Network Security / Input Validation / Data Protection / Authentication / **ProGuard·R8** / **WebView Security**.
  - ⭐ **§WebView Security · §ProGuard/R8 은 KB 내 다른 언어 팩에 없는 신규 판정축**이다. 웹뷰 하이브리드 앱 진단의 핵심 무기.
- **스킬**: `kotlin-patterns` 🟢 · `kotlin-coroutines-flows` 🟢(**RxJava3↔Coroutines 병행 정리 시 1순위 근거**) · `kotlin-testing` 🟡(Kotest/MockK 전제, 절차만 차용) · `android-clean-architecture` 🟡(멀티모듈·Room 전제, 개념만) · `compose-multiplatform-patterns` 🔴(XML View라 미적용) · `kotlin-ktor-patterns`/`kotlin-exposed-patterns` 🔴(**서버/ORM용** — 클라이언트와 무관)
- **에이전트**: `kotlin-reviewer`(관용 패턴·코루틴 안전성·Android 함정 → Kotlin 변경 시 기본 위임) · `kotlin-build-resolver`(Kotlin/**Gradle 빌드·의존성** 오류 — Nexus·AGP·Version Catalog 이슈 시 우선)
- ⚠️ **Kotlin 컨벤션은 KB에 없다.** 1차 정본은 **저장소 자체 `ha-aos/AGENTS.md`**(Kotlin 공식 스타일·4칸, 네이밍 `*Activity`/`*ViewModel`/`*UiState`/`*Repository`, 요청 없는 리팩터링 금지, 기능 작업 중 라이브러리 버전 변경 금지). ECC보다 이쪽이 우선.
- ⚠️ **ktlint/Detekt 미도입.** ECC 권고사항이나 도입 시 대량 diff 발생 → `AGENTS.md`의 "변경 범위를 좁게"와 충돌하므로 **별도 과제로 분리**한다.
- ⚠️ **DI 프레임워크 없음.** `rules/kotlin/patterns.md`의 Koin/Hilt 권고는 **개념(생성자 주입)만** 적용.
- ⚠️ **빌드 검증에 사내 Nexus 자격증명이 선행 조건.** `settings.gradle.kts`가 `local.properties`의 `nexus.*`를 강제하며, 없으면 **settings 평가 단계에서 빌드 전체 중단**(우회 불가). → `tdd-workflow`·`verification-loop` 적용 전 반드시 확인.
- ⚠️ **SQL 바인딩 규칙 무관**: 클라이언트라 DB 직접 접근 없음. 서버 측은 [ha_api](../projects/ha_api/INDEX.md)에서 판정.

### 📱 네이티브 앱 공통 운용 원칙 (thehappy_ios ↔ thehappy_aos)
- 두 앱은 **같은 백엔드(ha_api) + 동일 설계**다. `JavascriptBridge`가 **양쪽 모두 902줄**일 정도로 1:1 대응한다.
- → **JS 브릿지·라우팅·로그인 관련 이슈는 반드시 양쪽을 함께 진단**한다. 한쪽만 수정하면 플랫폼 간 동작이 갈라진다.
- → 두 앱 모두 CI가 **AI 리뷰(gpt-4o)만 존재하고 빌드·테스트 단계가 없다** — 공통 개선 과제.
- 보안 판정축 대응: iOS는 `rules/swift/security.md`(Keychain vs UserDefaults), Android는 `rules/kotlin/security.md`(**WebView Security · ProGuard/R8 · Secrets**).

## 4-4. React / TypeScript 매핑 (gcs_fo)
> 대상: [gcs_fo](../projects/gcs_fo/INDEX.md). ⚠️ ECC React 자산은 **Next.js App Router · RSC · React 19 · Vite** 전제가 상당히 섞여 있는데, 이 프로젝트는 **CRA(webpack) + React 18 + 순수 CSR SPA**다. 강도 구분 필수.

- **규칙이 3중으로 겹쳐 걸린다** — KB 내 유일한 케이스다. 한 파일에 여러 팩이 동시에 적용된다.
  | 팩 | `paths` | `.tsx` 파일에 적용? |
  |---|---|---|
  | `rules/typescript/*` | `**/*.{ts,tsx,js,jsx}` | ✅ (기반) |
  | `rules/react/*` | `**/*.{tsx,jsx}` + `components/`·`hooks/`·`pages/` 하위 `.ts` | ✅ (typescript 팩을 **상속·확장**) |
  | `rules/web/*` | `**/*.{css,scss,html,tsx,jsx,vue,svelte}` | ✅ (디자인·성능·접근성 축 추가) |
  - 각 5종(`coding-style`/`patterns`/`security`/`testing`/`hooks`) + `rules/web/`에는 **`design-quality.md`·`performance.md` 가 추가로 존재**한다.
  - **보안 진단 1차 근거 = `rules/react/security.md`**. 섹션: XSS(`dangerouslySetInnerHTML`) / 안전하지 않은 URL 스킴 / `target="_blank"` / Server Action 검증 / ⭐**Secret Exposure via Env Vars** / 인증·인가 / CSP / 프로토타입 오염 / SSR 템플릿 인젝션 / 서드파티 컴포넌트 / ⭐**Source Map Exposure in Production**.
  - ⭐ **`Secret Exposure via Env Vars` · `Source Map Exposure` 는 KB 내 다른 언어 팩에 없는 신규 판정축**이다. 실제로 `gcs_fo` 진단에서 이 두 축으로 High 2건이 나왔다. → [진단 기록](../projects/gcs_fo/WORKLOG-20260722-codebase-analysis.md)
- **스킬**: `react-patterns` 🟢 · `react-performance` 🟢 · `frontend-patterns` 🟢 · `frontend-a11y` 🟢 · `react-testing` 🟡(RTL 기반이라 절차는 유효하나 **테스트가 0건이라 도입부터**) · `design-system` 🟡(스타일 4종 혼재 정리 시 근거) · `e2e-testing` 🟡 · `api-design` 🟡(호출 측이라 참고만) · `vite-patterns` 🔴(**CRA/webpack**) · `nextjs-turbopack` 🔴 · `react-native-patterns` 🔴 · `ui-to-vue` 🔴
- **에이전트**: `react-reviewer`(*"MUST BE USED for React projects"*) · `typescript-reviewer`(*"MUST BE USED for TypeScript/JavaScript projects"*) → **`.tsx` 변경 시 두 리뷰어를 함께 위임**하는 게 기본값. 빌드 실패 시 `react-build-resolver`(CRA 명시 지원), 타입 설계 이슈는 `type-design-analyzer`.
- ⚠️ **RSC / Server Component / Server Action 관련 규칙은 전부 무시한다.** 이 앱은 `createBrowserRouter` 기반 **100% 클라이언트 렌더링**이다. ECC React 문서에서 가장 자주 나오는 축이라 오적용 위험이 크다.
- ⚠️ **프론트 컨벤션 정본은 `shared/conventions/{react,javascript,html-css}.md`** 지만 셋 다 **"초안"** 상태다. `gcs_fo` 등록으로 **실제 적용 대상이 처음 생겼으므로**, 이 3개 문서를 ECC `rules/react`·`rules/typescript`·`rules/web` 기준으로 확정(고도화)하는 것이 다음 과제다.
- ⚠️ **`tsconfig`가 `strict: true` 여도 안심하지 말 것.** `gcs_fo`는 strict인데도 `any`/`@ts-ignore`가 76건이다. API 응답·**네이티브 브릿지(`window.android`/`window.webkit`) 경계**에서 타입이 무력화되는 게 전형적 지점이다.
- ⚠️ **SQL 바인딩 규칙 무관**: 프론트라 DB 직접 접근 없음. 서버 측 판정은 ✅ **[gcs](../projects/gcs/INDEX.md) 등록 완료(2026-07-22)** → §4-5.

### 🌐 웹뷰 3자 동기화 원칙 (gcs_fo ↔ thehappy_ios ↔ thehappy_aos)
- `gcs_fo`는 **앱 안에서 뜨는 화면**이다. `src/util/nativeFunction.ts` 가 `window.android.*` / `window.webkit.messageHandlers.*` 를 호출하고, 반대편은 두 앱의 `JavascriptBridge`(양쪽 902줄)다.
- → **브릿지 함수 시그니처가 바뀌는 변경은 3개 저장소를 함께 확인**한다. 프론트만 배포하면 구버전 앱에서 조용히 실패한다(앱은 스토어 배포라 즉시 롤아웃 불가 — **프론트가 하위호환을 지는 쪽**).
- → 보안 판정도 층이 다르다: 웹 층은 `rules/react/security.md`(env 시크릿·소스맵·CSP), 안드로이드 층은 `rules/kotlin/security.md`(**WebView Security**), iOS 층은 `rules/swift/security.md`. **같은 화면인데 판정축이 3개**다.

## 4-5. Spring Boot / JPA 매핑 (gcs) 🟢 **적용 강도 최상위**
> 대상: [gcs](../projects/gcs/INDEX.md). **ECC 예시 코드의 기본 전제(Spring Boot + JPA + Gradle)와 스택이 거의 정확히 일치하는 KB 유일 프로젝트**다. 다른 프로젝트에서 "개념만 차용"이라 단서를 달았던 항목 대부분이 **여기서는 그대로 적용된다**.

- **규칙 `rules/java/`** — `coding-style` · `patterns` · `security` · `testing` · `hooks` 5종. `paths: ["**/*.java"]` → **Java 파일 편집 시 상시 자동 적용**. 🟢
  - **보안 진단 1차 근거 = `rules/java/security.md`**. 실제로 이 규칙의 §Secrets Management 로 `gcs` 에서 **Critical 1 / High 2** 가 검출됐다. → [진단 기록](../projects/gcs/WORKLOG-20260722-codebase-analysis.md)
- **스킬 적용 강도**
  | 스킬 | 강도 | 비고 |
  |---|---|---|
  | `springboot-patterns` | 🟢 | 계층구조·REST·검증·예외·페이징·필터가 **예시 코드 수준으로** 유효 |
  | **`jpa-patterns`** | 🟢 | ⭐ **KB에서 처음으로 실제 적용 대상이 생긴 스킬.** N+1·페치조인·`open-in-view`·영속성 컨텍스트 규칙이 전부 유효 |
  | **`postgres-patterns`** | 🟢 | ⭐ KB 내 유일한 PostgreSQL 프로젝트(다른 곳은 Oracle/MySQL 계열) |
  | **`redis-patterns`** | 🟢 | ⭐ Redisson 분산락(`@S9DistributedLock`)·캐시. KB 최초 Redis 사용처 |
  | `springboot-tdd` · `springboot-verification` · `tdd-workflow` · `verification-loop` | 🟢 | **테스트 48개가 실재하는 KB 유일 프로젝트** → 검증 루프를 온전히 돌릴 수 있다. 단 **CI 부재**로 실행은 로컬 수동 |
  | `java-coding-standards` | 🟢 | Java21(record/var/switch) 전부 사용 가능 |
  | `api-design` | 🟢 | 신규 채널 API 설계 시 |
  | **`springboot-security`** | 🟡 | ⚠️ **아래 주의 필수** |
  | `sql-mybatis` 계열 | 🔴 | MyBatis 미사용 |
- **에이전트**: `java-reviewer`(Java 변경 시 기본 위임) · `java-build-resolver`(**Gradle** 빌드오류) · `architect`(채널 구조 변경 시) · `security-reviewer`

### ⚠️ gcs 특이사항 (ECC 적용 시 주의)
1. **`springboot-security` 를 예시 코드대로 쓰면 안 된다 — Spring Security 의존성 자체가 없다.** 인증은 커스텀 `HandlerInterceptor`(`ApiAuthInterceptor`) + `JwtUtil` 구현이다. `SecurityFilterChain`·`CookieCsrfTokenRepository`·`@PreAuthorize` 예시는 **전부 미적용**. **체크리스트(인증/인가·레이트리밋·헤더·시크릿)만 차용**한다.
2. **인증 보호가 deny-by-default 가 아니다.** `application-*.yml` 의 `jwtSecuredUris` 에 **보호할 URI를 열거**하는 방식이라, **신규 엔드포인트를 등록하지 않으면 인증 없이 열린다**. ECC `api-design`으로 신규 API를 설계할 때 **yml 등록을 완료 조건에 포함**시킨다.
3. **SQL 바인딩 규칙이 KB 내 또 다른 변종**: MyBatis `#{}` · ha-push-batch `:param` · **`gcs` 는 QueryDSL 타입세이프 API + JPQL `:param`**. 단 `service/memberstore` 의 벌크 업서트만 **`JdbcTemplate`** 예외 경로다.
4. **`-parameters` 컴파일 옵션이 없으면 분산락이 깨진다.** `@S9DistributedLock(key = "#lockName")` 이 SpEL로 파라미터명을 참조하는데, Boot 3.1+ 는 파라미터명을 바이트코드에 넣지 않는다. **테스트·검증 루프 적용 전 IDE 설정 확인이 선행 조건**이다(ha-push-batch의 Nexus 자격증명 선행조건과 같은 성격).
5. **저장소 `README.md` 를 구조 근거로 삼지 말 것.** 완전히 다른 프로젝트(`com.spc.happymarket`) 기준으로 작성돼 있다. 정본은 [gcs INDEX](../projects/gcs/INDEX.md).
6. **`build.gradle` 이 로컬 `lib/` flatDir 저장소를 쓴다** → `dependency security`(CVE 스캔) 시 mavenCentral 밖의 JAR 존재를 감안한다.

### 🎁 GCS 서비스 2자 대조 원칙 (gcs ↔ gcs_fo)
- [gcs_fo](../projects/gcs_fo/INDEX.md)(웹뷰 프론트) ↔ [gcs](../projects/gcs/INDEX.md)(백엔드)는 **같은 서비스의 양쪽 끝**이다. 프론트 `src/api/core/axios.config.ts` 의 토큰 발급이 백엔드 `POST /v1/common/api/token`(`api/common/CommonApi`)과 **직결**된다.
- → **인증·CORS 이슈는 반드시 양쪽을 함께 본다.** 프론트의 CORS 실패 원인이 백엔드 `ApiAuthInterceptor.checkPreFlight()` 의 **하드코딩 Origin 목록**에 있는 경우가 있다.
- → 보안 판정축이 다르다: 프론트는 `rules/react/security.md`(env 시크릿 번들 인라인·소스맵), 백엔드는 `rules/java/security.md`(설정 파일 평문 크리덴셜). **양쪽 모두에서 Critical 시크릿 이슈가 나왔다** — GCS는 시크릿 관리를 **서비스 단위 과제**로 다룬다.
- → 웹뷰라 실제로는 **3자(+iOS·AOS)** 다. 브릿지 관련은 §4-4 웹뷰 3자 동기화 원칙 참조.

## 5. ECC vs 기존 md conventions 관계
- `md/shared/conventions/*` 는 현재 **"초안"** 상태. ECC의 `java-coding-standards`·`springboot-patterns`·`springboot-security` 가 더 구체적 → **conventions 확정(고도화) 시 ECC를 1차 근거로 사용**.
- 단, **충돌 시 프로젝트 정본이 우선**: 들여쓰기 space/4, 줄길이 200자, LF, MyBatis(`#{}`) 등 [conventions](./conventions/README.md)·[.editorconfig] 규칙은 ECC의 일반 예시보다 우선한다.

## 6. 참고
- [공유 지식 베이스 README](../README.md)
- ECC 가이드 원문: `ECC/the-shortform-guide.md`, `the-longform-guide.md`, `the-security-guide.md` (참조 전용)
- 한국어 문서: `ECC/docs/ko-KR/` (README·skills·rules 번역 존재)
