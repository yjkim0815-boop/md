---
문서유형: INDEX
프로젝트: gcs_fo
작성일: 2026-07-22
최종수정: 2026-08-03
작성자: dominic
상태: 진행중
요약: 해피포인트 앱 내 기프트카드 프론트 FO — React18 + TypeScript + CRA/CRACO SPA. KB 최초의 웹 프론트엔드 프로젝트이며 백엔드 짝은 `gcs`(Spring Boot 3.4 / Java21, 미등록)
---

# 📇 기프트카드 프론트 FO (gcs_fo)

> 📛 **폴더/슬러그 명명 규칙**: `projects/<slug>/` 의 `<slug>` 는 **Bitbucket 저장소명과 정확히 일치**시킨다. 매핑표는 [루트 README](../../README.md) 참조.

## 프로젝트 개요
- **저장소명(=KB 슬러그)**: `gcs_fo` ⚠️ **언더스코어** (로컬 폴더는 하이픈)
- **로컬 폴더**: 워크스페이스 루트 하위 `gcs-fo` (KB 기준 `../../../gcs-fo`)
- **설명**: **해피포인트 앱에 임베드되는 기프트카드 프론트 FO**. 카드 등록/관리 · 충전(결제) · 이용내역 · 환불 · 현금영수증 · 결제 비밀번호를 담당한다.
- **스택**: React 18 / TypeScript 4.9 / CRA(`react-scripts` 5) + **CRACO** / TanStack Query v5 + Zustand / axios / styled-components·Emotion·MUI·Tailwind
- **remote/브랜치**: `bitbucket.org/sectanine/gcs_fo.git` / `main`(기본) · `dev`(작업) · `WORK-*`(이슈 브랜치, PR 머지 방식)
- **규모**: `src` 약 **10,900줄** / TS·TSX 기준. 테스트 **0건**

### 🔗 짝 프로젝트 (중요)
| 구분 | 저장소 | 로컬 | 상태 |
|------|--------|------|------|
| 프론트 (이 문서) | `gcs_fo` | `gcs-fo` | ✅ 등록 |
| **백엔드** | **[`gcs`](../gcs/INDEX.md)** | `gcs` | ✅ **등록 완료(2026-07-22)** — Spring Boot **3.4.2** / **Java21** / Gradle / JPA + QueryDSL / PostgreSQL / Redis |
| 임베드 호스트(앱) | [thehappy_ios](../thehappy_ios/INDEX.md) · [thehappy_aos](../thehappy_aos/INDEX.md) | `ha-ios` · `ha-aos` | ✅ 등록 |

> 🟢 **[gcs](../gcs/INDEX.md) 백엔드는 [ha-push-batch](../ha-push-batch/INDEX.md)에 이어 KB 두 번째 Spring Boot·Gradle 프로젝트**이며, ECC `springboot-*`·`jpa-patterns` 를 **예시 코드 수준까지 직접 적용 가능한 대상**이다. → [ecc-reference §4-5](../../shared/ecc-reference.md)
> 🔐 **인증·CORS 이슈는 백엔드와 반드시 대조한다**: 아래 인증 흐름의 `POST /api/gcs/v1/common/api/token` 상대편은 `gcs` 의 `api/common/CommonApi` 이고, **CORS 허용 Origin 목록은 `gcs` 의 `ApiAuthInterceptor.checkPreFlight()` 에 하드코딩**돼 있다. 프론트에서 CORS가 막히면 백엔드 소스를 먼저 확인한다.
> 📱 **앱 웹뷰 이슈는 앱 2종과 함께 본다**: 이 프론트는 `window.android.*` / `window.webkit.messageHandlers.*` 브릿지로 네이티브를 호출한다(`src/util/nativeFunction.ts`). 브릿지 시그니처가 바뀌면 iOS·AOS `JavascriptBridge`(양쪽 902줄)와 **3자 동기화**가 필요하다.

## 문서 목록
| 문서 | 유형 | 상태 | 요약 |
|------|------|------|------|
| [WORKLOG-20260722-codebase-analysis.md](./WORKLOG-20260722-codebase-analysis.md) | WORKLOG | 진행중 | 최초 코드베이스 분석 + ECC `rules/react`·`rules/typescript` 기준 1차 진단 (🔴 Critical 1 / High 2) |

## 🗂️ 구조 (src)
```
src/
├─ api/            도메인별 API 호출 (auth, card, cashReceipt, order, password, payment, refund, term, verification)
│  └─ core/axios.config.ts   ⭐ 토큰 발급·인터셉터 등 통신 코어
├─ hooks/          query/ (조회) · mutations/ (변경) — TanStack Query 래퍼
├─ store/          Zustand 5종 (card / common / modal / toast / barcodeTime)
├─ pages/          화면 단위
├─ components/     화면별 컴포넌트 + common/ + modals/ + style/
├─ route/          router.tsx (createBrowserRouter) + Layout.tsx
├─ middleware/     apiLoggerMiddleware.ts
├─ util/           nativeFunction.ts(⭐ 네이티브 브릿지) · storage.ts(localStorage 래퍼)
├─ constant/ models/ types/ theme/ context/ assets/
```

## 🧭 라우팅 맵 (`src/route/router.tsx`)
| 경로 | 화면 | 비고 |
|------|------|------|
| `/` | `Check` | 진입 분기 |
| `/main` | 메인(카드 목록/바코드) | |
| `/payment` · `/pg/callback` · `/pg/success` · `/pg/fail` | 충전/결제 + PG 콜백 | 외부 PG 리다이렉트 복귀 지점 |
| `/password/setup` · `/password` · `/password/reset` | 결제 비밀번호 설정/검증/재설정 | |
| `/terms` · `/register` | 약관 · 카드 등록 | |
| `/management` · `/management/edit` | 카드 관리 · 수정 | |
| `/history` · `/history/:id` | 이용내역 | |
| `/settings` · `/refund` | 설정 · 환불 | |
| `/cash-receipt` | 현금영수증 | ⚠️ **진입 메뉴가 주석처리된 상태**(`230f220`, 자동충전 dev 배포용). 재오픈 시 주석 해제 필요 |
| ~~`/biopass`~~ | 생체인증 | 라우트 자체가 주석처리됨(`SetBioPassPage` 코드는 존재) |

## 🔐 인증 흐름 (`src/api/core/axios.config.ts`)
1. `REACT_APP_RELAY_URL` + `/…/hpc-token` 으로 **릴레이 서버에서 `hpcAut`(앱 인증 크리덴셜) 획득** → 모듈 전역 `cachedHpcAut`에 캐싱.
2. `POST /api/gcs/v1/common/api/token` 에 `apiAuthKey`(=`REACT_APP_API_AUTH_KEY`) · `channelCode`(`CH00000005`) · `authCredential`(=hpcAut) · `userAgent` 전송, `withCredentials: true`.
3. 발급 토큰으로 이후 GCS API 호출.

> ⚠️ 이 흐름에 **Critical 이슈 1건 · High 1건**이 있다 → [WORKLOG](./WORKLOG-20260722-codebase-analysis.md) 참조.

## ⚙️ 빌드 / 환경
- **빌드**: `yarn build:dev`(`.env.development`) · `yarn build:prod`(`.env.production`) — `env-cmd` + `craco build`
- **개발서버**: `craco start` (포트 **4000**), 파일 감시 폴링 사용(`CHOKIDAR_USEPOLLING`)
- **경로 별칭**: `craco.config.js` 와 `tsconfig.json` **양쪽에 중복 정의** (`@pages` `@components` `@api` …) → 별칭 추가 시 **두 곳 모두** 수정해야 한다.
- **배포**: `nginx.conf` 동봉 (SPA fallback)
- **환경변수**: `REACT_APP_ENV` / `REACT_APP_API_URL` / `REACT_APP_HAPPYAPPURL` / `REACT_APP_RELAY_URL` / `REACT_APP_API_AUTH_KEY` / `REACT_APP_CHANNEL_CODE` / `REACT_APP_MOBILE_OK_SCRIPT`
  - ⚠️ **`REACT_APP_*` 는 전부 번들에 인라인된다**(CRA 사양). 비밀값을 넣으면 안 된다.

## 현재 상태 / 핵심 메모
- **최근 작업 흐름**: 현금영수증 발급/삭제 → 사업자등록번호 validation → **전역·라우팅 레벨 ErrorBoundary + FallbackUI 도입**(`react-error-boundary`, `RouterErrorElement`) → 현금영수증 메뉴 임시 차단(자동충전 dev 배포).
- **현재 브랜치 `dev`**, 워킹트리 클린.
- **테스트 0건 · CI 없음 · ESLint 설정은 CRA 기본(`react-app`)만** → ECC `tdd-workflow`/`verification-loop` 즉시 적용 불가.
- **스타일 라이브러리 4종 혼재**(styled-components + Emotion + MUI + Tailwind). 새 UI 작성 시 **해당 화면이 이미 쓰는 방식을 따른다**(ECC "기존 패턴 우선").
- **패키지 매니저 이중화**: `yarn.lock` 과 `package-lock.json` 이 **둘 다 커밋**돼 있다. 스크립트·`env-cmd` 사용 정황상 **yarn 기준**으로 보이나 확정 필요.
- `package.json` 의 `"gcs_fo": "file:"`, `"po-frontend": "file:"` 는 **자기참조 더미 의존성**으로 보인다(제거 후보).

## 참고 (공통 문서)
- [공유 지식 베이스 README](../../README.md)
- [ECC 참조 · 작업 프로토콜](../../shared/ecc-reference.md) — React/TS 매핑은 **§4-4**
- [보안 리뷰 기준](../../shared/security-review.md)
- [conventions/react.md](../../shared/conventions/react.md) · [conventions/javascript.md](../../shared/conventions/javascript.md) · [conventions/html-css.md](../../shared/conventions/html-css.md)
- ⛔ **적용 안 됨**: [server-env.md](../../shared/server-env.md), `conventions/{java,spring,sql-mybatis}.md` (프론트엔드라 무관 — 서버 측은 [gcs INDEX](../gcs/INDEX.md)에서 판정)
