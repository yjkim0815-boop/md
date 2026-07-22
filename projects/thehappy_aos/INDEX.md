---
문서유형: INDEX
프로젝트: thehappy_aos
작성일: 2026-07-22
최종수정: 2026-07-22
작성자: dominic
상태: 진행중
요약: 해피포인트 Android 네이티브 앱(TheHappy) — Kotlin/minSdk26/Activity+ViewModel+Repository, XML+ViewBinding 기반 웹뷰 하이브리드. thehappy_ios의 안드로이드 짝. ⚠️ 하드코딩 크리덴셜 Critical 1건 검출
---

# 📇 thehappy_aos 문서 인덱스

## 프로젝트 정체성 (중요)
- **이 프로젝트 = 해피포인트 Android 네이티브 앱 (`TheHappy`)**. 서버가 아니라 **클라이언트**다.
- ⚠️ **[thehappy_ios](../thehappy_ios/INDEX.md)의 안드로이드 짝**이다. 두 앱은 **같은 백엔드([ha_api](../ha_api/INDEX.md))** 를 바라보고 **동일한 웹뷰 하이브리드 구조**를 공유한다. → **앱 공통 이슈는 반드시 양쪽을 함께 검토**한다.
- ⚠️ **비(非)JVM은 아니지만 Spring 백엔드도 아니다.** Kotlin/JVM이되 Android 클라이언트이므로 **`shared/conventions/{java,spring,sql-mybatis}.md` 는 적용되지 않는다.** (java.md의 일반 원칙 일부만 개념 차용)
- ⚠️ 실질적으로 **웹뷰 하이브리드 앱**이다. 네이티브 셸 + 웹 콘텐츠 + JS 브릿지 구조라, 화면 로직 상당수가 앱이 아니라 **웹에 있다**.

### 🔗 iOS ↔ AOS 구조 대응표 (짝 프로젝트 대조용)
| 역할 | thehappy_ios (Swift) | thehappy_aos (Kotlin) |
|------|------------------|-------------------|
| 웹뷰 컨테이너 | `WebViewController.swift` (1,474줄) | `WebActivity.kt` (2,216줄) |
| 메인 화면 | `MainViewController.swift` (1,098줄) | `MainActivity.kt` (1,194줄) |
| JS 브릿지 | `JavascriptBridge.swift` (902줄) | `JavascriptBridge.kt` (902줄) |
| 웹 팝업 | `WebPopup.swift` (859줄) | `WebPopup.kt` (1,135줄) |
| 로그인 | `HappyLogin.swift` (852줄) | `HappyLogin.kt` (853줄) |
| 라우팅 | `HappyRouter.swift` | `HappyRouter.kt` (422줄) |
| 런타임 상태 | `VolatileRepo` | `VolatileRepo` |

> 파일명·줄수까지 거의 1:1 대응한다 → **두 앱이 동일 설계로 병행 개발**되고 있음을 의미. 한쪽 수정 시 다른 쪽 동기화 여부를 항상 확인할 것.

## 프로젝트 개요
- **워크스페이스 폴더**: `ha-aos` (KB 기준 `../../../ha-aos`) — ⚠️ 폴더명은 `ha-aos`지만 **Gradle 루트 프로젝트명은 `TheHappy_AOS`, 저장소명은 `thehappy_aos`**
- **Bitbucket remote**: `bitbucket.org/sectanine/thehappy_aos.git`
- **브랜치**: `master`(main) / `dev`(작업) — PR 기반. 피처 브랜치는 `feature/WORK-<이슈키>` 규칙
- **스택**: **Kotlin 2.0.20** (Java 파일 단 1개) / **minSdk 26 (Android 8.0+)** / compileSdk·targetSdk 35 / JDK 17
- **아키텍처**: **Activity + ViewModel + Repository** (`UiState` 기반 상태 관리)
- **UI**: **XML + ViewBinding / DataBinding** (Compose 미사용) — 레이아웃 113개
- **비동기**: **RxJava3 + Coroutines 병행** ⚠️
- **빌드**: Gradle **Kotlin DSL** + **Version Catalog**(`gradle/libs.versions.toml`) + **`buildSrc`** / AGP 8.7.2 / Wrapper 8.9
- **규모**: Kotlin 394개 파일 / 약 34,000줄 — 중형 (iOS 246개·33,675줄과 유사)
- **저장소 자체 규약 문서**: `ha-aos/AGENTS.md` (실행 규칙·검증 매트릭스 — **1차 정본**), `README.md`, `doc/`

### ⚠️ 진입점 규칙 — 빌드 전 필수 설정
`settings.gradle.kts`가 **사내 Nexus 자격증명을 강제**한다. 없으면 `error()`로 **settings 평가 단계에서 빌드 전체가 중단**된다(= APK 생성 불가, 우회 불가).

```
local.properties          nexus.username / nexus.password  ← 필수. 없으면 빌드 시작조차 안 됨
KeyStore/keystore.properties                               ← release 서명 시 필수
app/src/<flavor>/google-services.json                      ← Firebase (git 미추적)
```
- 자격증명이 필요한 이유: 사내 Nexus(`dev-nexus.happypointcard.com`)에서 `com.happypointcard` 그룹 + 광고 SDK 프록시를 조달한다. `error()` 라인을 지워도 **의존성 해석 단계에서 401로 재실패**한다.
- ⚠️ 빌드 시 사내 Nexus에 **인증된 요청**이 나가므로 계정·시각·아티팩트가 **서버 접근 로그에 남는다**(정상 개발 활동).

## 모듈 구성
```
TheHappy_AOS/
├─ app/                메인 앱 모듈 (namespace·applicationId = com.hpapp)
├─ buildSrc/           flavor·URL·SDK 상수·자격증명 정의 (⭐ 이 프로젝트의 핵심 설계)
├─ TMS_SDK/            로컬 AAR 래퍼 (푸시)
├─ sdk-netfunnel/      로컬 AAR 래퍼 (대기열/넷퍼넬)
└─ KeyStore/           서명 키 (요청 없이 수정 금지)
```

### ⭐ buildSrc 중심 설계 (이 프로젝트 최대 특징)
flavor를 `build.gradle.kts`에 직접 쓰지 않고, **`buildSrc`의 `sealed class Flavors`로 정의한 뒤 리플렉션(`sealedSubclasses` + `objectInstance`)으로 productFlavors를 자동 생성**한다.

- `Flavors.kt` — flavor 정의(versionCode/Name, storeType, URL·패키지·소셜키 묶음)
- `Urls.kt` · `Packages.kt` · `AppConfig.kt` · `Credentials.kt` · `SocialConfigs.kt` · `AmplitudeConfigs.kt` · `AvatyeConfigs.kt` · `PincruxConfigs.kt` · `KakaoAdConfigs.kt` · `NetfunnelConfigs.kt` · `AirbridgeConfigs.kt` · `Field.kt`
- 🟢 **`buildSrc/src/test/kotlin/`에 설정값 단위테스트 11종 존재** (`UrlsTest`·`CredentialsTest`·`AppConfigTest` 등) → `./gradlew verifyBuildValues`로 검증. **KB 내에서 설정값을 테스트로 지키는 유일한 사례**로 참고 가치가 높다.
- ⚠️ `buildSrc` 수정 시 **반드시 대응 테스트를 갱신**한다(`AGENTS.md` 명시).

## 빌드 Flavor (4종)
| Flavor | 환경 | 용도 | 비고 |
|--------|------|------|------|
| `dev` | 개발 | 개발·기능 테스트 | |
| `stage` | 스테이징 | QA/사전 검증 | |
| `product` | 운영 | Play 스토어 배포 (`storeType=A`) | 현재 **8.8.83** |
| `onestore` | 운영 | OneStore 배포 (`storeType=O`) | 현재 **8.8.82**, `IS_ONESTORE_APP=true` |

- 운영 API 도메인 `napi.happypointcard.com` — **iOS와 동일**(짝 확인됨).
- 앱 설정은 S3 정적 JSON(`appsetting.json`)에서 원격 조달.

## 아키텍처 구조
```
app/src/main/java/com/hpapp/
├─ TheHappyApplication.kt   앱 진입점. ProcessLifecycleOwner 기반 포그라운드/백그라운드 감지
├─ view/
│   ├─ webview/             ⭐ 앱의 실질 중심
│   │   ├─ WebActivity.kt (2,216줄) · WebPopup.kt (1,135줄) · WebViewModel.kt (512줄)
│   │   └─ javascript/      JavascriptBridge · JavascriptBridge2 · HappyBridge
│   │                       LimitedJavascriptBridge (제한 브릿지) + 각 Delegate
│   ├─ main/ · intro/ · login/ · menu/ · dialog/ · customview/
│   └─ camera/ · crop/ · youtube/
├─ network/                 retrofit/ · repository/ · dto/ · cookie/ · link/(HappyRouter) · image/ · exception/
├─ common/                  CommonUtils · vo/ · publics/ · module/(HappyLogin·Firebase·Amplitude·광고) · utils/
├─ module/                  sms/ · gcm/ · biometric/
├─ widget/ · extension/
```

### 대형 파일 (ECC 코딩스타일 상한 800줄 초과)
| 파일 | 줄수 |
|------|------|
| `view/webview/WebActivity.kt` | 2,216 |
| `view/main/MainActivity.kt` | 1,194 |
| `view/webview/WebPopup.kt` | 1,135 |
| `view/webview/javascript/JavascriptBridge.kt` | 902 |
| `common/module/HappyLogin.kt` | 853 |

> 상위 5개 중 3개가 WebView 계열 → **웹뷰·JS브릿지가 이 앱의 실질 중심**임을 뒷받침 (iOS와 동일한 경향).

## 주요 기능
| 기능 | 비고 |
|------|------|
| 소셜 로그인 | 카카오 / 네이버 / 페이스북 + 휴대폰번호 + ID·PW (iOS의 애플로그인 대응은 미확인) |
| 생체 인증 | `module/biometric` |
| 포인트 | 조회·내역·사용·적립 (웹뷰 기반) |
| 광고/오퍼월 | **다중 광고 SDK 대거 탑재** — Anick · Avatye · Pincrux · KakaoAd + 프록시(Pangle·Mintegral·Chartboost·IronSource·Smaato·PubMatic·Verve 등) |
| 푸시 | TMS_SDK + HappyPush + FCM(`module/gcm`) |
| 대기열 | sdk-netfunnel (넷퍼넬) |
| 분석 | Firebase(Analytics·Crashlytics·Performance) · Amplitude · Airbridge |
| 보안 | **TouchEn mVaccine** · **SmartMedic(secureland)** · **HPTVI** · **Tky(goggles)** 등 다중 보안 SDK, `LocalShieldActivity` |

## CI / 배포
- **`bitbucket-pipelines.yml`**: PR 생성 시 `scripts/ai_pr_reviewer.py` 실행 — **AI 코드리뷰(gpt-4o)** 자동 수행. **빌드/테스트 파이프라인 없음.**
  - ⚠️ **iOS와 완전히 동일한 CI 구성** → 두 앱 공통 개선 과제.
- 산출물 APK/AAB 파일명은 `androidComponents.onVariants`에서 **버전+타임스탬프**로 자동 생성.

## 🔴 현재 상태 / 관찰된 이슈
> ⚠️ 이 항목은 **1차 구조 분석 + ECC 규칙 대조** 결과다. ha-push-batch·ha_panel 수준의 **전수 보안 진단은 아직 미수행**.
> 판정 기준: ECC `rules/kotlin/security.md` · `rules/kotlin/coding-style.md` · `rules/common/*` (참조 전용).

| # | 심각도 | 항목 | 근거 규칙 | 요약 |
|---|--------|------|-----------|------|
| 1 | 🔴 **Critical** | **하드코딩 크리덴셜이 git에 커밋됨** | `rules/kotlin/security.md` §Secrets Management | `buildSrc/src/main/java/com/hpapp/Credentials.kt` 에 **AES 키·IV·로그인 salt가 평문 상수**로 존재하며 **git 추적 대상**이다(`.gitignore` 미포함). 저장소 접근자 전원이 앱 암호화 키를 열람 가능. → `local.properties`/Nexus/시크릿 저장소로 외부화 필요 (`nexus.*`는 이미 그렇게 처리 중이라 **동일 패턴 적용 가능**) |
| 2 | 🔴 **High** | **release 빌드 난독화 비활성** | `rules/kotlin/security.md` §ProGuard/R8 | `app/build.gradle.kts` release 블록이 `isMinifyEnabled = false`, `isShrinkResources = false`. `proguardFiles`는 지정돼 있으나 **실제로 적용되지 않는다.** #1과 결합 시 APK 디컴파일로 키 노출이 더 쉬워짐 |
| 3 | 🟠 확인필요 | **`usesCleartextTraffic="true"`** | `rules/kotlin/security.md` §Network Security | `AndroidManifest.xml`에서 **평문 HTTP 전면 허용**. `networkSecurityConfig` 미설정이라 도메인별 예외 제한도 없음. 실제 http 통신 대상 식별 후 축소 필요 |
| 4 | 🟠 확인필요 | **JS 브릿지 노출면 과대** | `rules/kotlin/security.md` §WebView Security | `JavascriptBridge.kt` 한 파일에 **`@JavascriptInterface` 133개**. `LimitedJavascriptBridge`(1개)와 분리 설계는 되어 있으나, **어떤 URL에 어느 브릿지가 주입되는지 화이트리스트 검증**이 최우선 점검 포인트. iOS `JavascriptBridge.swift`와 **동일 이슈로 병행 점검** |
| 5 | 🟡 관찰 | 대형 파일 5개가 ECC 상한(800줄) 초과, 최대 2,216줄 | `rules/common/coding-style.md` | 리팩터링 후보 |
| 6 | 🟡 관찰 | **앱 모듈 테스트 사실상 부재** | `rules/kotlin/testing.md` | `app/src/test`에 2개(`MockApplication`·`HappyPushConfigsTest`), `androidTest`는 템플릿 1개뿐. 반면 **`buildSrc`는 11종 테스트 보유** → 정작 앱 로직이 무방비 |
| 7 | 🟡 관찰 | **RxJava3 + Coroutines 병행** | `rules/kotlin/patterns.md` | 비동기 패러다임 이중화. 신규 코드 기준 정립 필요 |
| 8 | 🟡 관찰 | CI에 **빌드·테스트 단계 없음** (AI 리뷰만) | `rules/common/testing.md` | iOS와 공통 |
| 9 | ℹ️ 정보 | 권한 20종 선언 | — | 최소권한 원칙 대조는 미수행 |
| 10 | ℹ️ 정보 | `KeyStore/`·서명·자격증명은 `AGENTS.md`에서 **요청 없이 수정 금지** | — | 작업 시 준수 |

> ⚠️ **#1은 KB 내 다른 프로젝트에서도 반복된 유형**이다(ha_panel Critical과 동일 계열: Secrets Management). **하드코딩 시크릿이 조직 공통 취약 패턴**일 가능성이 높다 → [security-review.md](../../shared/security-review.md)에 횡단 점검 항목으로 반영 검토.
> 🔒 이 문서에는 KB 규칙에 따라 **실제 키 값을 기재하지 않는다**. 값 확인은 저장소 원본 파일에서 직접 할 것.

## 🧩 ECC 적용 매핑 (thehappy_aos)
> ECC Kotlin 자산은 **Compose + KMP + Koin/Hilt + Kotest/MockK** 전제가 많다. 이 프로젝트는 **XML View + 단일 Android 모듈 + DI 프레임워크 부재**라 적용 강도를 구분한다.

### 규칙 (`ECC/rules/kotlin/`) — 🟢 상시 적용
`coding-style.md` · `patterns.md` · `security.md` · `testing.md` · `hooks.md` **5종**.
프론트매터 `paths: ["**/*.kt", "**/*.kts"]` → **Kotlin/KTS 파일 편집 시 자동 적용되는 규칙 팩**이며 대응 `rules/common/*`을 상속·확장.
- **보안 진단 1차 근거 = `rules/kotlin/security.md`** — 섹션: Secrets Management / Network Security / Input Validation / Data Protection / Authentication / **ProGuard·R8** / **WebView Security**.
  - ⭐ **§WebView Security와 §ProGuard/R8은 KB 내 다른 어떤 프로젝트에도 없던 신규 판정축**이다. 이 프로젝트에서 실제로 위 #2·#4를 검출했다.
- `hooks.md`는 `**/build.gradle.kts`도 대상에 포함 → **Gradle 스크립트 편집 시에도 규칙이 걸린다**.

### 스킬 (`ECC/skills/<name>/SKILL.md`)
| 스킬 | 적용 강도 | 사유 |
|------|-----------|------|
| `kotlin-patterns` | 🟢 **직접 적용** | 관용적 Kotlin·널안전성·코루틴·DSL 빌더. 프레임워크 중립이라 그대로 사용 가능 |
| `kotlin-coroutines-flows` | 🟢 **직접 적용** | 구조적 동시성·Flow·StateFlow. **RxJava3→Coroutines 정리(#7) 시 1순위 근거** |
| `kotlin-testing` | 🟡 개념 적용 | Kotest·MockK·Kover 전제. 현 프로젝트는 JUnit4 기반이라 **도구는 다르되 TDD 절차·구조는 차용** |
| `android-clean-architecture` | 🟡 개념만 | 멀티모듈·UseCase·Room/SQLDelight 전제. 현재는 **단일 `app` 모듈 + Repository만** 존재 → 모듈 분리 논의 시 참조 |
| `compose-multiplatform-patterns` | 🔴 **미적용** | 이 앱은 **XML + ViewBinding/DataBinding**. Compose 미사용 |
| `kotlin-ktor-patterns` | 🔴 **미적용** | Ktor **서버** 패턴. 이 앱은 클라이언트(Retrofit 사용) |
| `kotlin-exposed-patterns` | 🔴 **미적용** | Exposed **ORM/DB** 패턴. 클라이언트라 DB 직접 접근 없음 |
| `security-review` / `security-scan` | 🟢 | 정식 진단 수행 시 |

### 에이전트 (`ECC/agents/`)
- `kotlin-reviewer` — *"Kotlin and Android/KMP code reviewer"* (관용 패턴·**코루틴 안전성**·클린아키텍처 위반·**Android 흔한 함정**). → **Kotlin 변경 시 기본 위임 대상**
- `kotlin-build-resolver` — Kotlin/**Gradle 빌드·의존성 오류** 해결. → Nexus·AGP·Version Catalog 이슈 시 우선 후보
- 공통: `planner` · `architect` · `code-reviewer` · `security-reviewer` · `refactor-cleaner` · `doc-updater`

### ⚠️ thehappy_aos 특이사항
1. **`shared/conventions/{java,spring,sql-mybatis}.md`는 적용 대상 아님.** Kotlin 컨벤션은 현재 KB에 없고, **저장소 자체 `ha-aos/AGENTS.md`가 1차 정본**(Kotlin 공식 스타일, 들여쓰기 4칸, 네이밍 `*Activity`/`*ViewModel`/`*UiState`/`*Repository`, 요청 없는 리팩터링 금지, 기능 작업 중 라이브러리 버전 변경 금지).
2. **ECC의 ktlint/Detekt 권고는 현재 미도입.** 도입 시 대량 diff가 발생하므로 **`AGENTS.md`의 "변경 범위를 좁게" 원칙과 충돌** → 별도 과제로 분리할 것.
3. **DI 프레임워크가 없다.** ECC `rules/kotlin/patterns.md`는 Koin/Hilt 생성자 주입을 권하지만 이 앱은 미도입 → **개념(생성자 주입 지향)만 적용**, 프레임워크 도입은 별도 결정 사항.
4. **검증은 `./gradlew`로.** `AGENTS.md` 검증 매트릭스가 정본:
   - `buildSrc` 변경 → `./gradlew verifyBuildValues` + 관련 `*Test`
   - 네트워크/도메인 변경 → `NetworkModule.kt` 확인 + `:app:assemble<Flavor>Debug`
   - WebView/브릿지 변경 → `view/webview/javascript/*` 확인 + `:app:assembleDevDebug`
   - 릴리즈 → `:app:assembleProductRelease` / `bundleProductRelease`
   - ⚠️ **모든 검증은 Nexus 자격증명이 있어야 실행 가능**(위 진입점 규칙 참조).
5. **탐색 제외 경로**(`AGENTS.md` 명시): `plan/` · `doc/` · `jadx/` · `jcenter_backup/` · `KeyStore/` · `gradle/` — 단서가 있을 때만 열람.
6. **iOS와 동기화 확인 필수.** JS 브릿지·라우팅·로그인은 [thehappy_ios](../thehappy_ios/INDEX.md)와 1:1 대응 구조다.

## 문서 목록
| 문서 | 유형 | 상태 | 요약 |
|------|------|------|------|
| *(없음)* | — | — | 정식 코드베이스 분석 WORKLOG 미작성 — 본 INDEX는 1차 구조 파악 + ECC 규칙 대조 수준 |

## 다음 할 일 (제안)
1. 🔴 **#1 하드코딩 크리덴셜 외부화** — `nexus.*`와 동일하게 `local.properties` 주입 방식으로. **키 로테이션 동반 필요**(이미 git 이력에 남아 있음).
2. 🔴 **#2 release `isMinifyEnabled = true` 검토** — 보안 SDK·리플렉션(`sealedSubclasses`) 사용처가 있어 **ProGuard 룰 정비가 선행**돼야 한다.
3. 🟠 **#4 JS 브릿지 URL 화이트리스트 점검** — iOS와 병행.
4. 정식 보안 진단 WORKLOG 작성 (ha_panel 사례 형식 준용).

## 참고 (공통 문서)
- [공유 지식 베이스 README](../../README.md)
- [ECC 참조 · 작업 프로토콜](../../shared/ecc-reference.md)
- [보안/취약점 진단 기준](../../shared/security-review.md)
- [thehappy_ios INDEX](../thehappy_ios/INDEX.md) — **이 앱의 iOS 짝 (구조 1:1 대응)**
- [ha_api INDEX](../ha_api/INDEX.md) — 이 앱의 백엔드 API 서버
- ⚠️ [서버 환경](../../shared/server-env.md) — **클라이언트 프로젝트라 해당 없음**(EC2/Tomcat 배포 아님)
