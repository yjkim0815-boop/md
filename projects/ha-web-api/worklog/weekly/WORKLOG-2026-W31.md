---
문서유형: WORKLOG
범위: 프로젝트(ha-web-api)
주기: 주
기간: 2026-W31 (07-27~)
작성일: 2026-07-27
최종수정: 2026-07-29
작성자: AI(Claude)
상태: 진행중
요약: 인증 API(me→check), KCB 본인인증 complete postMessage, /api/page/cert 라우팅 통일 (+07-29: check 로그인여부만·dev 도메인·회사IP CORS 폐기 원복)
---

# 🛠️ ha-web-api 주간 작업내역 — 2026-W31 (프론트 happypoint-web2 연동)

> 로컬 체크아웃 `j-ha-web-api`(브랜치 `dev-j`). 배포처 dev-www. 프론트 짝 = [happypoint-web2](../../happypoint-web2/INDEX.md).

## 1. 인증 API
- `AuthApiResource`: `GET /api/auth/me` → **`GET /api/auth/check`** 리네임. (login/logout/check 3종)
- 규약 확인: `ApiResponseWrapper` 가 `com.spc.hpc.api.*` 응답을 `{code,message,data}` 로 자동 래핑. check 로그인=`code:00`+data, 미로그인=`ApiError.unauthorized()`=`code:50`, HTTP 항상 200.

## 2. KCB 본인인증 complete → 프론트 전달
- `cert/kcb/phone/complete.jsp`, `cert/kcb/ipin/complete.jsp`: 성공/실패 함수에 `window.opener.postMessage(result,'*')` 추가(result.type='HP_CERT_RESULT'). 기존 `opener.page.authCallback` 유지(JSP 부모 호환) → React(다른 오리진)도 결과 수신.

## 3. /api/page/cert 라우팅 통일 (ELB /api/* → 백엔드)
- 컨트롤러 클래스 매핑 `@RequestMapping("/page/cert")` → **`@RequestMapping("/api/page/cert")`**: `CertController`·`CertPhoneController`·`CertIpinController`.
- 콜백 URL `/api` 접두: `cert/kcb/config.jsp` RETURN_URL, `cert/nice/{ipin,phone,phone-order}/config.jsp` FAIL/PROCESS/RETURN.
- 레거시 팝업 오프너 `assets/shared/js/unvus/unvus.util.js` `callPhonePopup`/`callIpinPopup` → `/api/page/cert/...`.
- 필터: `SitemeshFilter` `/api/page/cert/*` 제외 추가(+기존 `/api/*`), `DeviceRedirectFilter` 는 `/api/**` 로 커버. 구 `/page/cert` 제외 라인 제거.
- ⚠️ **전제**: ELB 가 `/api` 를 strip 하지 않고 전달. strip 시 컨트롤러를 `/page/cert` 로 원복 필요.
- 검증: `mvn -o compile` 통과.

## 4. 레거시 authInfo 처리 (참고, 프론트 연동 근거)
- `BrandMemberController`: `join-policy.spc` 가 authInfo AES 복호화(cert.key) → `MEMBER_AUTH_INFO` HttpOnly 쿠키(30분) 저장, `join-view.spc` 가 쿠키로 이름/생년/휴대폰 복호화.

## 5. (07-29) check 응답 = 로그인 여부만
- `AuthApiResource.check()` → 로그인 시 `{code:"00", data:{loggedIn:true}}`, 미로그인 `ApiError.unauthorized()`(`code:"50"`). SessionUser 개인정보는 응답/로그에 미노출.

## 6. (07-29) dev 도메인 정리
- `dev-www.happypointcard.com` → **`dev.happypointcard.com`**: `application-dev.yml`(`cert.return-server`·`site.url`), `application-local.yml`(`site.url`), `README.md`.

## 7. (07-29) 회사IP CORS 시도 → 폐기·원복 ★
- 로컬 프론트 크로스오리진 로그인용으로 `SecurityConfig` 에 회사IP(14.32.109.30) 한정 CORS/CSRF예외/SameSite=None 필터 + 프로파일(비운영) 분기 + `X-Real-IP` 폴백을 구현(커밋 `fa8dd55`·`dc83440`).
- 진단: nginx preflight 403, 배포본이 소스와 불일치(`GET /api/auth/check` 405), Secure쿠키 이슈. 프론트가 **BFF 프록시**(서버-투-서버, CORS 불필요)로 확정됨에 따라 **불필요 판정**.
- 조치: **해당 커밋 삭제 → `SecurityConfig` 원본(permitAll + 전역 CSRF, `31fae35`)으로 완전 원복**. 워킹트리 clean 확인.

## 8. (07-29) 로그인 보안 (설계, 미구현)
- 서버-투-서버 로그인 완전차단 불가 → 남용방지(CAPTCHA·rate limit·lockout·WAF). DynamoDB nonce 는 리플레이/발급훅용, 바인딩+TTL+CAPTCHA 결합 시에만 실효.

## 다음 할 일 (TODO)
- [ ] (07-29) 로그인 nonce/rate limit/CAPTCHA 백엔드 구현 여부 결정
- [ ] 신규 계약 API 에 join-policy(authInfo 수신)/join-view(복호화 반환) 존재 확인·없으면 추가
- [ ] ELB /api strip 여부 확인 → cert 컨트롤러 매핑 확정
- [ ] KCB complete postMessage targetOrigin 을 '*' → 프론트 오리진 제한(운영 보안)

## 배포 목록 (dev-www)
- Java: `AuthApiResource`, `CertController`, `CertPhoneController`, `CertIpinController`, `SitemeshFilter`, `DeviceRedirectFilter`
- JSP/JS: `cert/kcb/{phone,ipin}/complete.jsp`, `cert/kcb/config.jsp`, `cert/nice/*/config.jsp`, `unvus.util.js`

## 참고
- 이전 주차: [WORKLOG-2026-W30](./WORKLOG-2026-W30.md)
