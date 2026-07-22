---
문서유형: INDEX
프로젝트: thehappy_ios
작성일: 2026-07-22
최종수정: 2026-07-22
작성자: dominic
상태: 진행중
요약: 해피포인트 iOS 네이티브 앱(TheHappy) — Swift5/iOS13+/MVVM+Combine, UIKit+Storyboard 기반 웹뷰 하이브리드. KB 내 첫 비(非)JVM·네이티브 앱 프로젝트
---

# 📇 thehappy_ios 문서 인덱스

## 프로젝트 정체성 (중요)
- **이 프로젝트 = 해피포인트 iOS 네이티브 앱 (`TheHappy`)**. 서버가 아니라 **클라이언트**다.
- ⚠️ **KB 내 첫 비(非)JVM 프로젝트**다. 기존 `ha_*`/`ha-*` 계열은 전부 Java/Spring 백엔드 → **`shared/conventions/java.md`·`spring.md`·`sql-mybatis.md`는 이 프로젝트에 적용되지 않는다.**
- ⚠️ **백엔드 짝은 [ha_api](../ha_api/INDEX.md)** (해피포인트 앱 API 서버, 하이브리드 앱용 웹뷰 + REST). 이 앱이 호출하는 서버가 ha_api다. **앱 이슈 추적 시 두 프로젝트를 함께 봐야 한다.**
- ⚠️ 실질적으로 **웹뷰 하이브리드 앱**이다. 네이티브 셸 + 웹 콘텐츠 + JS 브릿지 구조라, 화면 로직 상당수가 앱이 아니라 **웹(`ha_web` 계열)에 있다**.

## 프로젝트 개요
- **워크스페이스 폴더**: `ha-ios` (KB 기준 `../../../ha-ios`) — ⚠️ 폴더명은 `ha-ios`지만 **Xcode 프로젝트명/저장소명은 `TheHappy` / `thehappy_ios`**
- **Bitbucket remote**: `bitbucket.org/sectanine/thehappy_ios.git`
- **브랜치**: `master`(main) / `dev`(작업) — PR 기반
- **스택**: Swift 5+ (ObjC 브릿징 일부) / **iOS 13.0+** / Xcode 15+ / **UIKit + Storyboard** / Combine
- **아키텍처**: MVVM + Repository 패턴
- **의존성**: **CocoaPods**(`PointHome` 2.0.3 단 1개) + **SPM 38개 패키지** 병행
- **규모**: Swift 246개 파일 / 약 33,675줄 — 중형
- **저장소 자체 규약 문서**: `ha-ios/AGENTS.md` (작업 규칙·검증 기준·보고 형식), `README.md`, 폴더별 `README.md`

### ⚠️ 진입점 규칙
**반드시 `TheHappy.xcworkspace`로 연다** (`.xcodeproj` 아님). CocoaPods 사용 프로젝트라 workspace가 정본이다.

```
pod install            # 최초 1회 필수 (Pods/ 는 git 미추적)
open TheHappy.xcworkspace
# 스킴 TheHappy_DEV 선택 후 실행
```

## 빌드 스킴 (6종)
| 스킴 | 환경 | API 도메인 | 용도 |
|------|------|-----------|------|
| `TheHappy_DEV` / `_DEV_E` | 개발 | `dev-napi.happypointcard.com` | 개발·테스트 |
| `TheHappy_STG` / `_STG_E` | 스테이징 | `stg-napi.happypointcard.com` | QA |
| `TheHappy_LIVE` / `_LIVE_E` | 운영 | `napi.happypointcard.com` | App Store(TestFlight) |

- `_E` 접미사 = **엔터프라이즈 배포판**(AWS 배포). 일반판은 App Store.
- 환경값은 `TheHappy/Resources/Config.xcconfig` / `Config_*.xcconfig`, entitlements도 스킴별 6개 분리.
- 테스트 플랜: `TheHappy_{DEV,STG,LIVE}_Tests.xctestplan` — **환경별 설정 검증 위주**, 로직 테스트는 빈약.

## 아키텍처 구조
```
TheHappy/
├─ AppDelegate.swift (67줄) / SceneDelegate.swift
├─ Common/           핵심 인프라
│   ├─ Gateway.swift        앱 초기화 + 딥링크/스킴 진입의 중앙 조정자
│   ├─ HappyRouter.swift    싱글톤. 딥링크·푸시·네비게이션 라우팅
│   ├─ PageCode.swift       indirect enum. 모든 네비게이션 목적지 정의
│   ├─ VolatileRepo         런타임/세션 상태 (로그인 사용자 등)
│   ├─ HappyUserDefaults    영구 저장소 (설정, 자동로그인)
│   ├─ HappyKeychain        보안 저장소 (생체인증 토큰 등)
│   └─ Module/ · Publics/
├─ Network/          HappyProvider(Moya+Combine) · Dto/ · Repository/
│   └─ Repository/   Affiliate · AppSetting · Brand · Etc · Home · Logging · Login · Setting · Splash
├─ View/             BaseViewController · BaseViewModel<T> · ViewModelBinding
│   └─ Intro · Login · Main · Menu · WebView · Receipt · ImageScan · CustomView · Widget
├─ Extension/ · Resources/ · Frameworks/
├─ NotificationServiceExtension/   Rich 푸시
└─ NotificationContentExtension/
```

### MVVM 패턴
- `BaseViewModel<T>` — `@Published var uiState: T` + `@Published var happyError: HappyError?` + `cancellables`
- `ViewModelBinding` 프로토콜 — `onBinding()` / `handleUIState(_:)` / `handleHappyError(_:)`
- 피처마다 **`UIState` enum**으로 화면 상태 전이 표현 (`.ShowLoading` / `.BannerData` / `.MoveNext(PageCode)` …)
- Repository 3종 세트: `{Feature}APIRepository`(프로토콜) → `{Feature}Repository`(구현) → `{Feature}Service`(엔드포인트)

### 대형 파일 (리팩터링 후보)
| 파일 | 줄수 |
|------|------|
| `View/WebView/WebViewController.swift` | 1,474 |
| `View/Main/MainViewController.swift` | 1,098 |
| `View/WebView/JavascriptBridge.swift` | 902 |
| `View/WebView/WebPopup.swift` | 859 |
| `View/Login/HappyLogin.swift` | 852 |

> 상위 5개 중 3개가 WebView 계열 → **웹뷰·JS브릿지가 이 앱의 실질 중심**임을 뒷받침.
> ECC `rules/common/coding-style.md`(파일 200~400줄, 최대 800) 기준으로는 **5개 모두 초과**.

## 주요 기능
| 기능 | 비고 |
|------|------|
| 소셜 로그인 | 카카오 / 네이버 / 페이스북 / 애플 + 휴대폰번호 + ID·PW |
| 생체 인증 | Face ID / Touch ID (`BiometricModule`), 토큰은 Keychain |
| 포인트 | 조회·내역·사용·적립 |
| 광고/오퍼월 | 다중 광고 SDK, Avatye 오퍼월(사설 CocoaPods 소스) |
| 위젯 | iOS 13 / iOS 14+ 위젯, **App Groups**로 데이터 공유 |
| 푸시 | TMS + HappyPush, Rich Notification (확장 타깃 2개) |
| 분석 | Firebase Analytics · Amplitude · Session Replay |
| 보안 | **PureApp** 위변조 검증 · CryptoSwift 암호화 · 전 URL XSS 검증(`CommonUtils.isXss`) |

## CI / 배포
- **`bitbucket-pipelines.yml`**: PR 생성 시 `scripts/ai_pr_reviewer.py` 실행 — **AI 코드리뷰(gpt-4o)** 자동 수행. 빌드/테스트 파이프라인은 **없음**.
- App Store: `TheHappy_LIVE` → TestFlight / 엔터프라이즈: `TheHappy_LIVE_E` → AWS

## 🟠 현재 상태 / 관찰된 이슈
> ⚠️ **이 항목은 1차 "가벼운" 구조 분석 결과**다. ha-push-batch·ha_panel 수준의 **정식 보안 진단은 아직 미수행**.
> 판정 기준: ECC `rules/swift/*` · `rules/common/coding-style.md` (참조 전용).

| # | 심각도 | 요약 |
|---|--------|------|
| 1 | 🟠 확인필요 | **`Podfile.lock`이 `.gitignore`에 포함**되어 git 미추적 → 팀원·CI 간 **Pod 버전 재현성 미보장**. CocoaPods 공식 권장(lock은 커밋)과 반대 |
| 2 | 🟠 확인필요 | 웹뷰 하이브리드 + `JavascriptBridge`(902줄) → **JS↔네이티브 브릿지 노출면**이 넓다. ECC `rules/swift/security.md` 기준 브릿지 입력 검증 점검 필요 |
| 3 | 🟡 관찰 | 대형 파일 5개가 ECC 코딩스타일 상한(800줄) 초과 |
| 4 | 🟡 관찰 | 테스트가 **환경 설정 검증 위주**, 비즈니스 로직 테스트 사실상 부재 |
| 5 | 🟡 관찰 | CI에 **빌드·테스트 단계 없음** (AI 리뷰만) |
| 6 | ℹ️ 정보 | `Config*.xcconfig` / entitlements / 인증서 관련은 `AGENTS.md`에서 **요청 없이 수정 금지**로 명시 |

## 🧩 ECC 적용 매핑 (thehappy_ios)
> ECC Swift 자산은 **SwiftUI + Swift 6.2 동시성 + Swift Testing** 전제가 많다. 이 프로젝트는 **iOS 13 / Swift 5 / UIKit / Combine**이라 적용 강도를 구분한다.

### 규칙 (`ECC/rules/swift/`) — 🟢 상시 적용
`coding-style.md` · `patterns.md` · `security.md` · `testing.md` · `hooks.md` 5종.
프론트매터 `paths: ["**/*.swift", "**/Package.swift"]` → **Swift 파일 편집 시 자동 적용되는 규칙 팩**이며 대응 `rules/common/*`을 상속·확장.
- **보안 진단 1차 근거 = `rules/swift/security.md`**. 핵심 규칙 *"민감정보는 Keychain, 절대 UserDefaults 금지"* → 이 앱은 `HappyKeychain`/`HappyUserDefaults`가 **둘 다 존재**하므로 **저장 항목 분류 점검이 최우선 진단 포인트**다.

### 스킬 (`ECC/skills/<name>/SKILL.md`)
| 스킬 | 적용 강도 | 사유 |
|------|-----------|------|
| `swift-protocol-di-testing` | 🟢 **직접 적용** | 프로토콜 기반 DI로 네트워크 목킹 → 이 프로젝트의 `{Feature}APIRepository` 프로토콜 구조와 정확히 일치. **테스트 보강 시 1순위 근거** |
| `ios-icon-gen` | 🟢 보조 | 앱 아이콘 생성 |
| `swift-actor-persistence` | 🟡 개념만 | actor 기반. iOS 13 타깃 + Combine 구조라 그대로 도입 불가 |
| `swiftui-patterns` | 🔴 **미적용** | 이 앱은 **UIKit + Storyboard**. `@Observable`·SwiftUI 네비게이션 예시 사용 불가 |
| `swift-concurrency-6-2` | 🔴 **미적용** | Swift 6.2 Approachable Concurrency 전제. 이 앱은 **Swift 5 + Combine** |
| `cisco-ios-patterns` | ⛔ **무관** | ⚠️ 이름만 "ios" — **Cisco 네트워크 장비 IOS**다. 혼동 금지 |

### 에이전트 (`ECC/agents/`)
- `swift-reviewer` — 프로토콜지향·값의미론·**ARC 메모리 관리**·동시성 리뷰. 설명에 *"MUST BE USED for Swift projects"* → **Swift 변경 시 기본 위임 대상**
- `swift-build-resolver` — Xcode/SPM/CocoaPods 빌드 오류 해결
- 공통: `planner` · `architect` · `code-reviewer` · `security-reviewer` · `refactor-cleaner` · `doc-updater`

### ⚠️ thehappy_ios 특이사항
1. **`shared/conventions/*`(java·spring·sql-mybatis)는 적용 대상 아님.** Swift 컨벤션은 현재 KB에 없고, **저장소 자체 `ha-ios/AGENTS.md`가 1차 정본**(들여쓰기 4칸, `UpperCamelCase`/`lowerCamelCase`, 기능 폴더 유지, 요청 없는 리팩터링 금지).
2. **ECC `tdd-workflow`/`verification-loop`는 부분 적용.** 테스트 타깃(`TheHappy_Tests`)은 존재하나 환경 검증 위주 → 로직 테스트 기반부터 필요.
3. **검증은 `xcodebuild`로.** `AGENTS.md` 기준 — `xcodebuild build -workspace TheHappy.xcworkspace -scheme TheHappy_DEV -destination 'generic/platform=iOS'`. 실행 어려우면 `build-for-testing`까지 수행 후 사유 기록.
4. **[thehappy_aos](../thehappy_aos/INDEX.md)(안드로이드)와 짝**이다 — ✅ 2026-07-22 KB 등록 완료. 파일명·줄수까지 1:1 대응하는 **동일 설계**(`JavascriptBridge` 양쪽 902줄)이므로 **앱 공통 이슈는 반드시 양쪽을 함께 검토**한다. ECC 매핑은 `rules/kotlin/*` + `kotlin-*` 스킬 → [ecc-reference §4-3](../../shared/ecc-reference.md).
5. 🔴 **미점검 과제(thehappy_aos 진단에서 파생)**: 안드로이드 짝에서 **하드코딩 크리덴셜(Critical)** 과 **release 난독화 비활성(High)** 이 검출됐다. 설계가 대응되므로 iOS도 **동일 유형 시크릿 스윕 + 바이너리 보호 설정 점검**이 필요하다 → [security-review 패턴 확장 2](../../shared/security-review.md).

## 문서 목록
| 문서 | 유형 | 상태 | 요약 |
|------|------|------|------|
| *(없음)* | — | — | 정식 코드베이스 분석 WORKLOG 미작성 — 본 INDEX는 1차 구조 파악 수준 |

## 참고 (공통 문서)
- [공유 지식 베이스 README](../../README.md)
- [ECC 참조 · 작업 프로토콜](../../shared/ecc-reference.md)
- [보안/취약점 진단 기준](../../shared/security-review.md)
- [ha_api INDEX](../ha_api/INDEX.md) — 이 앱의 백엔드 API 서버
- ⚠️ [서버 환경](../../shared/server-env.md) — **클라이언트 프로젝트라 해당 없음**(EC2/Tomcat 배포 아님)
