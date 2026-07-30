---
문서유형: WORKLOG
범위: 프로젝트(happypoint-web2)
주기: 주
기간: 2026-W31 (07-27~)
이슈키: WORK-16611
작성일: 2026-07-27
최종수정: 2026-07-29
작성자: dominic
상태: 진행중
요약: KCB 본인인증(휴대폰·아이핀) React 연동, SSR 로그인 판별, 서버 파일 로그, /api 라우팅 통일 (+07-29: 로그인체크 최소화·dev 도메인·로컬로그인 BFF프록시 일원화)
---

# 🛠️ happypoint-web2 주간 작업내역 — 2026-W31

## 1. SSR 로그인 판별 (전 페이지)
- `lib/auth-server.ts` `getCurrentUser()` — 모든 요청 쿠키(JSESSIONID)를 백엔드 `GET /api/auth/check` 로 전달, 타임아웃 4초, 오류/타임아웃/미로그인 → null.
- `components/auth/auth-provider.tsx` — SSR 판별값을 클라 컨텍스트로 전달(`useAuth`). `auth-actions.tsx` 가 이걸로 로그인/로그아웃 UI + 로그아웃 BFF(`/api/logout`).
- 루트 `layout.tsx` `export const dynamic = "force-dynamic"` — 전 페이지 동적 렌더 강제 → 정적 프리렌더로 check 를 건너뛰던 문제 해결(`/`·presentation 등 포함).
- `check` 규약: HTTP 항상 200, `code:"00"`=로그인 / `code:"50"`=미로그인(`ApiResponseWrapper`+`ApiError.unauthorized`). 백엔드 `me`→`check` 리네임.
- 원요청 파라미터를 check 로 전달: 미들웨어가 `x-hp-query`/`x-hp-method` 헤더로 넘기고 `getCurrentUser` 가 check URL 에 쿼리 부착 + 로그.

## 2. 인증 3종 통일
- `POST /api/auth/login` · `POST /api/auth/logout` · `GET /api/auth/check` (기존 me).

## 3. KCB 본인인증(휴대폰·아이핀) 연동 ★
- **방식**: React가 백엔드 JSP 팝업을 열고(window.open), 완료 시 `postMessage` 로 결과 수신. 크립토·복호화는 100% 백엔드.
- **프론트**: `join/index/join-auth.tsx`(client) — 휴대폰/아이핀 버튼 → 팝업(500×800) → `message` 리스너. 성공(phone `B000`/ipin `T000`) → 결과 sessionStorage 저장 + `/page/join/policy` 이동. `subpage.tsx` `AuthMethod` 에 `onSelect` 추가.
- **백엔드 JSP**: `cert/kcb/{phone,ipin}/complete.jsp` 에 `window.opener.postMessage(result,'*')` 추가(기존 `opener.page.authCallback` 유지 → JSP 부모 호환).
- **팝업 파라미터**(레거시 join-auth.jsp 동일): `reqChnl=NONE, reqPage=join, reqPath=`.
- **결과 로깅**: `join-auth` → `/api/cert/log`(신규 route) POST → `apiLog` 서버 파일 로그 + 브라우저 콘솔. ⚠️ 디버깅용, 완료 후 제거 권장(개인정보).

## 4. /api 라우팅 통일 (ELB: /api/* → 백엔드)
- 본인인증 호출·콜백 URL 전부 `/api/page/cert/...` 로:
  - 프론트 팝업 `join-auth.tsx`, 레거시 `unvus.util.js`(callPhonePopup/callIpinPopup), KCB `config.jsp` RETURN_URL, NICE `config.jsp`(FAIL/PROCESS/RETURN).
  - 컨트롤러 `CertController`·`CertPhoneController`·`CertIpinController` → `@RequestMapping("/api/page/cert")` (구 `/page/cert` 제거).
  - `SitemeshFilter` `/api/page/cert/*` 제외(+`/api/*`), `DeviceRedirectFilter` `/api/**` 커버. 구 `/page/cert` 제외 라인 제거.
- ⚠️ **전제**: ELB 가 `/api` 를 strip 하지 않고 그대로 백엔드 전달. strip 하면 컨트롤러를 `/page/cert` 로 되돌려야 함 → 배포 후 팝업 도달로 검증.

## 5. 서버 요청/응답 파일 로그
- `lib/log.ts` `apiLog` — 파일(`LOG_DIR`) + 콘솔. 날짜별 `ha-web-fo-YYYYMMDD.log`. 길이 4000자 캡. 로컬=`D:/logs/ha-web-fo`, 서버(dev/stg/prod)=`/app/server/ha-web-fo`. (운영 포함 전 환경 기록; `LOG_ENABLED=false` 로만 off)
- 계측: `legacyGet`(계약 API 성공/실패 본문), `fetchLegacy`(레거시 스크래핑), `/api/login`·`/api/logout`(비번 마스킹), `getCurrentUser`(check).
- **모든 페이지 진입 로그**: 미들웨어 `x-hp-req` 헤더 → 레이아웃 `apiLog("[page]", ...)` (GET 파라미터 포함). POST 바디는 RSC에서 못 읽어 미기록(BFF/route 에서 개별 로깅).

## 6. 레거시 authInfo 흐름 파악 (다음 단계 근거)
- `BrandMemberController`: `POST /join-policy.spc` 가 authInfo(암호문) 받아 `AES128Util.decrypt(cert.key)` 복호화 → `MEMBER_AUTH_INFO` **HttpOnly 쿠키(30분)** 로 저장. `join-view.spc` 가 그 쿠키로 이름/생년/휴대폰 복호화해 폼 채움.
- 시사점: authInfo·CI/DI 는 프론트가 다루지 않고, **약관동의 API 에 authInfo 넘기면 백엔드가 HttpOnly 쿠키로 유지**하는 구조로 React 연동해야 함.

## 7. (07-29) 로그인 체크 API 최소화
- `/api/auth/check` 응답을 **"로그인 여부"만**으로 축소 결정. 백엔드는 로그인 시 `{code:"00", data:{loggedIn:true}}`, 미로그인 `code:"50"`.
- 프론트 `lib/auth-server.ts`: `getCurrentUser` → **`checkLoggedIn(): Promise<boolean>`** (개인정보 미수신). `auth-provider.tsx`/`layout.tsx` 는 로그인여부만 클라이언트 전달.
- 원리 정리: SSR fetch 자체는 브라우저 미노출이나, **AuthProvider(클라이언트 컴포넌트)로 넘기는 값이 곧 유출 지점** → 최소 필드만 전달. 개인정보는 렌더 후 사용자 액션 시점에 백엔드 직접 호출로 취득.
- ※ 이후 워킹트리에서 `AuthProvider`가 GA/Amplitude용 `mbrNo` 포함 버전으로 되돌아옴(seokej 라인) — 최종 필드 범위는 정합 필요.

## 8. (07-29) dev 도메인 정리
- `dev-www.happypointcard.com` → **`dev.happypointcard.com`** 전체 치환: 프론트 `.env.local`/`.env.dev`(`LEGACY_BASE`·`LEGACY_BASE_FALLBACK`·`NEXT_PUBLIC_API_BASE`), `.env.stg`/`.env.prod` 주석.

## 9. (07-29) 로컬 로그인 — BFF 프록시 방식으로 일원화 ★
- **문제**: 로컬(localhost:3000) → dev 백엔드 크로스오리진 로그인이 CORS/Secure쿠키로 실패. `NEXT_PUBLIC_API_BASE` 유실로 self(localhost) 호출되던 버그도 확인.
- **검토①(폐기) 백엔드 회사IP CORS**: dev/stg 한정 + 회사IP(14.32.109.30)에서만 localhost CORS/CSRF예외/SameSite=None. → nginx preflight 403·Secure쿠키·배포 불일치로 난항. **커밋 삭제·원복**.
- **채택 = 프론트 BFF 프록시** (seokej `7977955`, `app/api/auth/[...path]/route.ts`): 브라우저는 동일오리진 `/api/auth/{login,logout,check}` 만 호출 → Next 서버가 `LEGACY_BASE` 로 중계 + `Set-Cookie`의 `Domain`/`Secure` 제거(로컬). **서버-투-서버라 CORS/CSRF 완화 불필요**.
- 결론: **백엔드 인증 커스터마이징 0** (원본 `SecurityConfig` = permitAll + 전역 CSRF). 로컬 로그인은 프론트 프록시 단독으로 완결.

## 10. (07-29) 로그인 보안 논의 (설계 단계, 미구현)
- 서버-투-서버 로그인은 원리상 완전차단 불가(브라우저 신호 위조 가능). 남용 방지가 목표 → CAPTCHA(폼에 자리 존재)·rate limit·계정 잠금·WAF.
- DynamoDB **nonce** 검토: 리플레이 차단·발급지점 방어훅으론 유효하나 봇 차단은 불가 → **세션/IP 바인딩 + single-use TTL + rate limit + CAPTCHA 결합** 조건 하에서만 실효.

## 다음 할 일 (TODO)
- [ ] (07-29) 로그인 nonce(+CAPTCHA/rate limit) 실제 구현 여부 결정
- [ ] (07-29) `AuthProvider` 최종 노출 필드 범위 확정(로그인여부 최소화 vs GA용 mbrNo)
- [ ] 신규 계약 API(`JoinApiResource`/`BrandMemberApiResource`)에 join-policy(authInfo 수신)·join-view(복호화 정보 반환) 존재 여부 확인
- [ ] 약관동의 → 정보입력폼 authInfo 연동 (HttpOnly 쿠키 방식)
- [ ] ELB /api strip 여부 확인 후 cert 컨트롤러 매핑 확정
- [ ] `/api/cert/log` 디버깅 로깅 제거(운영 전)
- [ ] 로그인 세션 유지 후속(마이페이지 등 게이트)

## 참고
- 상세 이전 주차: [WORKLOG-2026-W30](./WORKLOG-2026-W30.md)
- 백엔드 짝: [ha-web-api INDEX](../../ha-web-api/INDEX.md)
