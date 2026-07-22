---
문서유형: WORKLOG
프로젝트: gcs_fo
이슈키: --
작성일: 2026-07-22
최종수정: 2026-07-22
작성자: dominic
상태: 진행중
요약: gcs_fo(기프트 웹뷰 프론트) 최초 코드베이스 분석 + ECC `rules/react`·`rules/typescript` 기준 1차 진단 — 🔴 인증 크리덴셜 하드코딩 커밋(5개 프로젝트 연속) 1건 / 🟠 High 2건
---

# 🛠️ WORKLOG — 코드베이스 분석 & 1차 진단 (2026-07-22)

## 배경 / 목적
사용자 요청은 "가벼운 분석"이었으나, `gcs_fo`는 KB **미등록 프로젝트**였고 [루트 README](../../README.md)의 미등록 목록에 명시돼 있었다. 또한 [security-review.md](../../shared/security-review.md)가 **"아직 진단하지 않은 프로젝트(… `gcs` …)도 같은 스윕을 우선 수행"** 하라고 지목한 대상이다.

- **KB 최초의 웹 프론트엔드** → ECC React/TypeScript 규칙 팩의 KB 적용 선례를 만든다.
- 충전(결제)·환불·현금영수증을 다루므로 **금전성 자산**이 걸려 있다. [ha_panel](../ha_panel/WORKLOG-20260722-codebase-analysis.md)과 같은 기준으로 우선순위를 높게 잡았다.

진단 기준(참조 전용): ECC `rules/react/security.md` · `rules/typescript/security.md` · `rules/web/security.md` · `rules/common/{security,coding-style}.md`.

## 진행 내용
1. 전수 스캔 — `package.json`/`craco.config.js`/`tsconfig.json`/`.env*`/`nginx.conf`, `src` 전체(약 10,900줄), git remote·브랜치·추적 파일.
2. 라우팅 맵 · 인증 흐름 · 디렉토리 규약 · 빌드 파이프라인 정리 → [INDEX.md](./INDEX.md)에 영구 반영.
3. **시크릿 스윕** — 기존 KB 명령의 ①(설정 파일) ②(Java 상수) ②-K(Kotlin)에 더해 **JS/TS·`.env` 계열(②-JS)** 을 새로 수행 → 신규 유형 검출.
4. ECC React 보안 규칙 축(`dangerouslySetInnerHTML` / 안전하지 않은 URL 스킴 / `target="_blank"` / **환경변수 시크릿 노출** / **소스맵 노출** / CSP) 대조.

### 확인된 규모 (2026-07-22 기준)
| 항목 | 수치 |
|------|------|
| `src` TS/TSX 라인 | 약 **10,901줄** |
| 라우트 | 18개 (+주석처리 1) |
| API 도메인 모듈 | 10개 (auth/card/cashReceipt/order/password/payment/refund/term/verification/core) |
| Zustand 스토어 | 5개 |
| 최대 파일 | `components/payment/PaymentComponent.tsx` **508줄** |
| **테스트** | **0건** (`*.test.*`/`*.spec.*` 없음) |
| **CI** | **없음** |
| `any` / `@ts-ignore` 출현 | **76건** (`tsconfig` 는 `strict: true` 인데 경계에서 무력화) |
| `console.log` | 4건 |

### 확인된 구성 요점
- **하이브리드 웹뷰**: `src/util/nativeFunction.ts` 가 `window.android.*`(AOS) / `window.webkit.messageHandlers.*`(iOS)로 분기해 헤더·네비게이션 등 네이티브 UI를 제어한다. → **앱 2종과 브릿지 계약을 공유**한다.
- **인증은 2단 토큰 교환**: 릴레이 서버에서 `hpcAut` 획득(모듈 전역 캐싱) → GCS `common/api/token` 으로 서비스 토큰 발급. 상세는 [INDEX.md](./INDEX.md#-인증-흐름-srcapicoreaxiosconfigts).
- **서버 상태는 TanStack Query, 클라이언트 상태는 Zustand** 로 역할이 깔끔히 분리돼 있다 — ECC `rules/react/patterns.md`의 "State Location Decision Tree"에 부합. 👍
- **에러 처리는 최근 정비됨** — 전역 + 라우팅 레벨 ErrorBoundary(`RouterErrorElement`) 도입 완료. ECC `rules/react/patterns.md` "Suspense + Error Boundaries" 충족. 👍
- **스타일 라이브러리 4종 혼재**(styled-components / Emotion / MUI / Tailwind) — 번들·일관성 양쪽에서 비용.
- `.gitignore`(52~55행)에 `.env*` 4개가 **전부 등재돼 있는데도 4개 모두 git에 추적 중**이다. → **이미 커밋된 뒤에 무시 규칙을 추가한 전형적 케이스**(`.gitignore` 는 추적 중인 파일에 소급 적용되지 않음).

## 발생 이슈 & 해결
| 이슈 | 원인 | 해결 |
|------|------|------|
| 🔴 앱 인증 크리덴셜(`hpcAut`) 소스 하드코딩 + 커밋 | 디버깅용 조기 return 을 주석으로 남김 | **미해결 — TODO(즉시 삭제 + 로테이션)** |
| 🟠 `REACT_APP_API_AUTH_KEY` 가 번들 인라인 + 저장소 커밋 | CRA `REACT_APP_*` 사양 + `.env*` 4종 git 추적 | **미해결 — TODO(서버 이관 검토)** |
| 🟠 운영 빌드 소스맵 노출 | `GENERATE_SOURCEMAP` 미설정(CRA 기본 = 생성) | **미해결 — TODO(1줄 수정)** |
| 🟡 테스트·CI 0건 | 도입된 적 없음 | **미해결 — 별도 과제** |

---

### 🔴 Critical-1: 앱 인증 크리덴셜(`hpcAut`) 하드코딩 + 저장소 커밋
> ⚠️ KB 규칙에 따라 **값은 기재하지 않는다**. 위치·유형만 기록.

- **위치**: `src/api/core/axios.config.ts:17` — `getHpcAut()` 함수 **첫 줄의 주석처리된 조기 `return`**.
  ```
  const getHpcAut = async (): Promise<string> => {
    // return '<URL 인코딩된 300자+ 크리덴셜>';   ← 여기
    if (cachedHpcAut) { ... }
  ```
- **유형**: 릴레이 서버가 발급하는 **앱 사용자 인증 크리덴셜(`authCredential`)** 실값. 로컬 테스트용으로 박아두고 주석 처리한 것으로 보인다.
- **영향(악용 시나리오)**:
  1. 저장소 접근자(또는 **배포된 번들·소스맵**)에서 값을 획득한다. 주석은 빌드 시 제거되지만, **git 히스토리에는 영구히 남는다**.
  2. 이 값을 `authCredential` 로 `POST /v1/common/api/token` 에 그대로 보내면 **해당 회원의 GCS 서비스 토큰이 발급**된다.
  3. 발급 토큰으로 **기프트카드 잔액 조회 · 이용내역 · 카드 관리 · 환불 요청**이 가능하다. 결제수단(빌키) 관련 API 접근면도 열린다.
- **판정 근거**: ECC `rules/typescript/security.md` §Secret Management, `rules/common/security.md` — *"소스에 시크릿을 절대 하드코딩하지 않는다 / 노출 가능성이 있으면 무조건 로테이션한다."*
- **권고 조치**:
  1. **해당 크리덴셜 즉시 무효화(로테이션)** — 파일에서 지우는 것만으로는 무효화되지 않는다(KB 시크릿 관리 원칙).
  2. 주석 라인 삭제. 로컬 테스트가 필요하면 **`.env.local`(git 미추적) 기반 개발 전용 분기**로 대체한다.
  3. git 히스토리 정리 여부는 별도 판단(강제 push 영향 범위 확인 필요).

### 🟠 High-1: `REACT_APP_API_AUTH_KEY` 번들 인라인 + `.env*` 4종 git 추적
- **위치**: `.env` · `.env.development` · `.env.development.local` · `.env.production` (**4개 모두 git 추적 중**, `.gitignore` 등재에도 불구하고) → `src/api/core/axios.config.ts` 의 `apiAuthKey` 로 사용.
- **유형**: GCS API 발급용 **`apiAuthKey`(운영/개발 각각)**.
- **영향**:
  - CRA는 `REACT_APP_*` 를 **빌드 시 번들에 문자열로 인라인**한다. 즉 **이 키는 배포 시점에 이미 공개 정보**다. "커밋 안 하면 안전"이 성립하지 않는다 — [thehappy_aos](../thehappy_aos/INDEX.md)에서 확인된 *"클라이언트 시크릿은 배포로 회수 가능"* 패턴과 **동일 구조**다.
  - 다만 단독으로는 토큰 발급이 안 되고 `authCredential`(hpcAut)이 함께 필요하다 → **Critical-1과 결합될 때 실제 위험이 완성**된다. 그래서 이 항목만으로는 High.
- **판정 근거**: ECC `rules/react/security.md` §**Secret Exposure via Env Vars** — *"클라이언트 번들에 들어가는 환경변수에 비밀값을 두지 않는다."*
- **권고 조치**:
  1. **판정 우선**: 이 키가 *애초에 클라이언트가 보유해도 되는 값인지* 결정한다. 아니라면 **토큰 발급을 릴레이/BFF 서버로 이관**(`REACT_APP_RELAY_URL` 경유 방식이 이미 있으므로 확장이 자연스럽다).
  2. 클라이언트 보유가 불가피하면 **채널 식별자 수준으로 강등**하고 서버 측 검증(오리진·레이트리밋)을 보강한다.
  3. `.env.production` 은 `git rm --cached` 후 배포 파이프라인 주입으로 전환. `.env.development.local` 은 **추적 자체가 규약 위반**(로컬 전용 파일).

### 🟠 High-2: 운영 빌드 소스맵 노출
- **위치**: `.env.production` — `GENERATE_SOURCEMAP` **미설정** (`craco.config.js` 에도 관련 설정 없음).
- **영향**: CRA 기본값이 `true` 라 **운영 번들과 함께 `.map` 파일이 배포**된다. 원본 TS 코드·주석·내부 API 경로·로직이 그대로 공개되어, 위 Critical-1/High-1의 **공격 난이도를 크게 낮춘다**.
- **판정 근거**: ECC `rules/react/security.md` §**Source Map Exposure in Production**.
- **권고 조치**: `.env.production` 에 `GENERATE_SOURCEMAP=false` 추가(1줄). 에러 추적이 필요하면 **소스맵은 Sentry 등에만 업로드하고 정적 서빙에서 제외**한다.

### 🟡 Medium / Low
| 심각도 | 항목 | 근거(ECC) | 메모 |
|--------|------|-----------|------|
| 🟡 M-1 | **테스트 0건 · CI 0건** | `rules/common/testing.md` · `tdd-workflow` | `@testing-library/*` 는 설치돼 있으나 테스트 파일 없음. 결제/환불 금액 계산부터 착수 권장 |
| 🟡 M-2 | **`any`/`@ts-ignore` 76건** | `rules/typescript/coding-style.md` | `tsconfig` 는 `strict: true` 인데 API 응답·네이티브 브릿지 경계에서 무력화됨. `window.android`/`window.webkit` 타입 선언(`global.d.ts`) 보강이 실효 |
| 🟡 M-3 | **CSP 미설정** | `rules/web/security.md` §CSP | `public/index.html`·`nginx.conf` 모두 CSP 헤더 없음. 외부 스크립트(`REACT_APP_MOBILE_OK_SCRIPT`, PG) 로드가 있어 검토 가치 있음 |
| 🟢 L-1 | `PaymentComponent.tsx` 508줄 | `rules/common/coding-style.md`(200~400줄, 최대 800) | 임계 초과. 결제 로직/렌더 분리 후보 |
| 🟢 L-2 | 락파일 이중화(`yarn.lock` + `package-lock.json`) | `rules/common/patterns.md` | 설치 결과가 환경마다 갈릴 수 있음. 하나로 통일 |
| 🟢 L-3 | 자기참조 더미 의존성 (`"gcs_fo": "file:"`, `"po-frontend": "file:"`) | — | 제거 후보 |

### ✅ 클린 판정 (오탐 방지용 기록)
ECC React 보안 규칙 중 **다음 축은 실제로 위반 0건**이다. 재진단 시 중복 조사 불필요:
- `dangerouslySetInnerHTML` — **0건**
- `target="_blank"`(rel 누락) — **0건**
- `localStorage` 사용 — `src/util/storage.ts` 래퍼 **4개 호출뿐이며 토큰·크리덴셜 저장 용도 아님**
- SSR/서버액션 관련 항목 — CSR 전용 SPA라 **해당 없음**

## 다음 액션 (TODO)
1. 🔴 **`axios.config.ts:17` 크리덴셜 로테이션 + 라인 삭제** (ECC 대응 프로토콜: 로테이션이 1순위)
2. 🟠 `GENERATE_SOURCEMAP=false` (즉시 가능, 1줄)
3. 🟠 `apiAuthKey` 서버 이관 검토 + `.env*` 추적 해제
4. 🟢 **백엔드 짝 `gcs` 를 KB에 등록** — Spring Boot 3.4.2/Java21/Gradle이라 ECC Boot 스킬 🟢 직접 적용 대상이며, 이 프론트의 토큰 발급 API 실체가 거기 있다. **위 Critical/High 조치의 서버 측 판정도 `gcs` 없이는 불가능**하다
5. 🟡 결제/환불 금액 로직부터 테스트 도입 → CI 파이프라인(빌드+타입체크) 신설

## 참고
- [gcs_fo INDEX](./INDEX.md) · [루트 README](../../README.md)
- [ECC 참조 — §4-4 React/TypeScript 매핑](../../shared/ecc-reference.md)
- [보안 리뷰 기준 — 시크릿 스윕 ②-JS](../../shared/security-review.md)
- 유사 사례: [ha_panel](../ha_panel/WORKLOG-20260722-codebase-analysis.md)(소스 상수) · [thehappy_aos](../thehappy_aos/INDEX.md)(buildSrc + 클라이언트 배포 회수)
