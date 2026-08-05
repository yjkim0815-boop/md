---
문서유형: INDEX
프로젝트: homepage-ai-renewal (상위/엄브렐러)
작성일: 2026-07-29
최종수정: 2026-08-05
작성자: dominic
상태: 진행중
요약: 해피포인트 홈페이지 AI 리뉴얼 — 프론트(happypoint-web2)·백엔드(ha-web-api)를 하나로 묶는 상위 프로젝트. 완료까지 지속 현행화·디벨롭. (2026-08-05 연결 태스크 통합 관리 구조 도입 — 통합 작업로그(마일스톤)·통합 TODO(SSOT·검증상태), 갱신 리마인더 훅 연동)
---

# 📇 홈페이지 AI 리뉴얼 (homepage-ai-renewal) — 상위 프로젝트 인덱스

> ⚠️ **이 슬러그는 Bitbucket 저장소가 아니라 "상위 묶음(엄브렐러)"이다.** 실제 코드는 아래 두 저장소에 있으며, 이 문서는 둘을 **하나의 프로젝트로 연결·총괄**한다. (폴더명=저장소명 규칙의 예외 — 통합 관점 문서)

## 프로젝트 정의
- **목표**: 레거시 홈페이지([`ha_web`](../ha_web/INDEX.md))를 대체하는 **신규 홈페이지 리뉴얼**. 프론트+백엔드를 한 몸으로 개발.
- **범위**: 프론트엔드 + 계약 API 백엔드 + 로컬/개발/스테이징/운영 환경 + 배포/인프라(ELB·nginx·PM2·Tomcat) 연동.
- **상태**: 진행중 (완료 시점까지 이 INDEX + 하위 worklog를 **지속 현행화·디벨롭**).

## 🔗 구성 (프론트 ↔ 백엔드 연결)
| 축 | 저장소(KB 슬러그) | 스택 | 배포처 | 문서 |
|---|---|---|---|---|
| **프론트엔드** | [`happypoint-web2`](../happypoint-web2/INDEX.md) | Next.js 16 / React 19 / TS / TailwindCSS v4 / pnpm | dev/stg/prod (PM2 `ha-web-fo`, 포트 3000) | [INDEX](../happypoint-web2/INDEX.md) · [W31 worklog](../happypoint-web2/worklog/weekly/WORKLOG-2026-W31.md) |
| **백엔드** | [`ha-web-api`](../ha-web-api/INDEX.md) | Java21 / Spring6 / Jakarta / MyBatis / Tomcat10.1 (WAR) | `dev.happypointcard.com` 등 | [INDEX](../ha-web-api/INDEX.md) · [W31 worklog](../ha-web-api/worklog/weekly/WORKLOG-2026-W31.md) |
| (대체 대상) | [`ha_web`](../ha_web/INDEX.md) | Java8 / Spring5.2 / JSP | — | 레거시 홈페이지 |

- **로컬 체크아웃**: 프론트 `happypoint-web2`, 백엔드 `j-ha-web-api`(브랜치 `dev-j`).
- **연동 규약**: 브라우저/SSR → `{도메인}/api/*` → (ELB) → 백엔드. `com.spc.hpc.api.*` 응답은 `ApiResponseWrapper`로 `{code,message,data}` 엔벨로프 자동 래핑(HTTP 항상 200, `00`=성공/로그인·`50`=미로그인).

## 아키텍처 통합 관점 (프론트↔백엔드 접점)
- **인증**: 프론트 로그인폼 → `POST /api/auth/login`(백엔드). 전 페이지 SSR `GET /api/auth/check`로 로그인여부 판별 → `AuthProvider` 컨텍스트. 인증 3종 `/api/auth/{login,logout,check}`.
- **로컬 로그인**: **프론트 BFF 프록시**(`app/api/auth/[...path]/route.ts`)가 `/api/auth/*`를 `LEGACY_BASE`로 서버-투-서버 중계 + 쿠키 `Domain/Secure` 제거. → 백엔드 CORS/CSRF 커스터마이징 불필요(회사IP CORS 방식은 폐기·원복).
- **본인인증(KCB 휴대폰·아이핀)**: 프론트가 백엔드 JSP 팝업(`/api/page/cert/...`) 열고 `postMessage`로 결과 수신. 복호화는 100% 백엔드(`MEMBER_AUTH_INFO` HttpOnly 쿠키).
- **데이터**: (A) 신규 계약 API 직접 호출 (B) 레거시 HTML 스크래핑 — A로 전환 중.
- **도메인**: dev = **`dev-www.happypointcard.com`** (2026-08-05 `dev`→`dev-www` 재변경 · 2026-07-29 `dev-www→dev` 통합의 역방향). `dev.happypointcard.com` 진입 시 프론트 미들웨어가 `dev-www` 로 307 리다이렉트(`APP_ENV=dev` 한정).

## 📓 통합 작업로그(연결) — 마일스톤 단위
> 상세는 각 저장소 worklog(링크)가 정본. 여기는 **프론트+백엔드 통합 관점 + 검증상태**만. 검증: `⏳배포대기`·`🧪스테이징확인`·`✅실기기/운영확인`·`❌실패`.

### M1. 로그인/세션 무상태 인증(`_HPC_AUT`) [FE+BE] — 검증 ✅
- [BE] `_HPC_AUT`(AES-256-GCM, SessionUser 전체) 발급 + AuthBootstrapFilter 세션복원. 슬라이딩 게이트 30분→**3분**(`AuthCookieService`). → [ha-web-api W31](../ha-web-api/worklog/weekly/WORKLOG-2026-W31.md)
- [BE] 점유인증 레이스 **nonce 상관키**로 해소(`SmsService`/`SmsRepository.xml` `APP_UUID`→`NONCE`). ✅ 실기기 확인(08-04).
- [FE] 슬라이딩 renewal을 **미들웨어로 이관**(`_HPC_AUT` relay + `x-hp-user`). → [web2 W31](../happypoint-web2/worklog/weekly/WORKLOG-2026-W31.md)
- [인프라] ALB 스티키 해제 → **라운드로빈 전환** 검증 완료(08-05).

### M2. 회원정보수정/탈퇴 dev 라우팅 정합 [FE+BE] — 검증 🧪 (일부 미결)
- [FE] process API(form+`backendApiUrl`) 통일, 탈퇴 흐름 레거시 정합. ✅ 탈퇴 dev 완주(08-03).
- **미결**: `modify-info` 진입(ownership SMS 게이트) route handler 의존 → 수정 필요. change-pw 응답 shape dev 확인.

### M3. 파바앱(OPBS) 회원가입 재설계 [FE+BE] — 검증 ⏳배포대기
- [FE] URL 이관(`/page/brand/join/*` + POST 브리지), 공유 폼(Policy/JoinInfo/Referral), PC차단, alert 케이스별 버튼, 복귀버튼(웹홈 이동 없음), UA 포워딩.
- [BE] 채널코드 **A005/30**(reqPath=instCd 존재 시), 브랜드 생성 API `/api/brand/join/joinProc` 통일.
- [FE] (08-05) 본인인증 페이지 **일반과 레이아웃 통일**(타이틀 "해피포인트 생활 첫단계"·브레드크럼·Section 제거) + **아이핀 복원**. → [web2 W31](../happypoint-web2/worklog/weekly/WORKLOG-2026-W31.md)
- [FE] (08-05) **임시 디버그 alert**(실제 유입 URL 확인용) — 파바앱이 일반 회원가입으로 유입되는 정황 → 브랜드에서 제거하고 **일반 `join/index/join-auth.tsx`로 이동**. 확인 후 제거 예정.
- [FE] (08-05) **파바앱 유입 rewrite 보강 + 헤더 감지** — dev 파바앱은 param 없이 `index.spc`로만 옴(UA 구분 불가). 운영 스카우터 로그로 확정: 파바앱은 **`x-requested-with=com.pb.android` 헤더**를 항상 실음(운영은 `/page/join/auth.spc?instCd=OPBS`). → `middleware.ts` OPBS 감지에 **instCd(주·iOS+Android 공통)·헤더 `com.pb.android`(Android 보조)·reqPath 3중 신호** + instCd 보강 → 브랜드 가로채기. ⚠️ iOS 파바앱은 `x-requested-with` 없음(instCd 파라미터에만 의존). → [web2 W31](../happypoint-web2/worklog/weekly/WORKLOG-2026-W31.md)
- **남은 실검증**: 실기기 가입 완주(2100 헤더 A005/30), PC차단, alert 버튼, nonce 회귀, **본인인증 레이아웃/아이핀**, **유입 URL 확인**.

### M4. 공지 상세 500 [FE] — 검증 ❌ 미해결
- notice-view/voteView: Turbopack 프로덕션 빌드 external `sanitize-html` resolve 실패. → 클린 재빌드/웹팩 전환 검토.

### M5. Airbridge 가입완료 트래킹 [FE] — ⏸️ 보류(배포 실패로 롤백)
- 확정값: channel `ha-web`·campaign `ha-web-sign-up`·deeplink napi event-view. 재적용 시 **pnpm add+lockfile 커밋** 필수(frozen-lockfile 교훈).

## ✅ 통합 TODO (SSOT) — 프론트+백엔드 한 목록 · 검증상태 포함
> 코드 완료만으론 `[x]` 금지. 배포·실기기 확인까지 되어야 검증완료. "투두 보여줘"의 정본.

**M3 파바앱 (최우선)**
- [ ] [FE+BE] 파바앱 가입 **실기기 완주** — 2100 헤더 A005/30 · PC차단 · alert 버튼 · nonce 회귀 | ⏳배포대기
- [ ] [FE] 본인인증 페이지 일반과 레이아웃 통일 + 아이핀 복원 **실기기 확인** | ⏳배포대기
- [ ] [FE] 파바앱(**OPBS만**) 크롬 숨김 — 헤더·브레드크럼(공백 유지)+푸터(제거), 모든 OPBS 페이지 자동적용 **실기기 확인** | ⏳배포대기
- [ ] [FE] 파바앱 유입 rewrite(`x-requested-with=com.pb.android` 헤더 감지→브랜드) **실기기 확인** | ⏳배포대기
- [x] [FE] dev→dev-www 리다이렉트 **원복 완료**(08-05) — 임시 비활성 주석 해제 | ✅원복됨
- [x] [FE] 임시 디버그 alert(유입 URL) **제거 완료**(08-05) — `join/index/join-auth.tsx` useEffect + `page.tsx` debugServer 삭제 | ✅제거됨
- [ ] [FE] 브랜드 policy 이후(form/optional/welcome) instCd·authInfo 전파 검증(쿠키/API) | ⏳
- [ ] [FE] 브랜드 raw fetch 4종(policy/form/optional/common-alert)에 `AbortSignal.timeout(10s)` + 정적 에러페이지 | ⏳

**M2 회원정보수정**
- [ ] [FE] `modify-info` 진입 게이트(ownership SMS + MODIFY_INFO_AUTH_COOKIE) route handler 의존 제거 | ⏳
- [ ] [FE] modify-info-form `result.alertType`(need-confirm-pw/need-ownership) 분기 + [BE] alertType 숫자 prefix 제거 | ⏳

**M4 공지**
- [ ] [FE] 공지 상세 500(notice-view/voteView) — 클린 재빌드 결과 확인 → 웹팩 전환 여부 | ❌미해결

**로그인 2단계·보안**
- [ ] [BE] [2단계] 로그인 완전 무상태화(세션 제거, 쿠키만) — 1단계 운영 안착 후 | ⏳
- [ ] [FE] `AuthProvider` 최종 노출 필드 범위 확정(최소화 vs GA용 mbrNo) | —
- [ ] [FE+BE] 로그인 남용 방지(nonce/CAPTCHA/rate limit) 구현 여부 결정 | —
- [ ] [BE] KCB complete postMessage `targetOrigin` `'*'`→프론트 오리진 제한(운영 보안) | —
- [ ] [FE] `/api/cert/log` 디버깅 로깅 제거(운영 전) · `/api/auth/*` 프록시 화이트리스트·로깅 점검 | —

**Airbridge(보류)**
- [ ] [FE] 가입완료 Airbridge 재적용(pnpm add+lockfile+CSP) + userId SHA-512 해시 UTM | ⏸️보류

**기타 결정 대기**
- [ ] [BE] 그룹2 스텁 API 실로직 이식 여부 · 그룹3(정적 page) 모델API 처리 방침 | —

## 운영 규칙 (이 상위 프로젝트)
- **동시 갱신(강제)**: 연결 저장소에서 작업하면 **① 저장소 worklog + ② 이 INDEX 의 통합 작업로그·통합 TODO** 를 같은 타이밍에 갱신. 한쪽만 갱신 금지. (README [연결 태스크 통합 관리 규칙])
- **검증상태 필수**: 통합 TODO·작업로그 항목은 `⏳배포대기`·`🧪스테이징확인`·`✅실기기/운영확인`·`❌실패` 를 붙인다. 코드 완료만으론 `[x]` 금지.
- **정본 트리거**: "투두 보여줘"·"작업내역 보여줘"(리뉴얼 문맥) → 이 INDEX 의 통합 TODO·통합 작업로그가 정본.
- **자동 넛지**: `~/.claude/hooks/remind-worklog.js`(10분 쓰로틀)가 md/web2/ha-web-api 수정 시 위 갱신을 상기.
- **커밋/푸시**: md 커밋·푸시는 **사용자가 직접** (Claude는 파일 편집만).
- **읽기 순서**: 전역 성향(6M) → 전역 작업동향(3M) → 하위 프로젝트 성향(3M) → 하위 작업내역(3M).

## 참고
- [KB 루트 README](../../README.md) · [서버 환경](../../shared/server-env.md) · [API 응답 표준](../../shared/conventions/api-response.md)
