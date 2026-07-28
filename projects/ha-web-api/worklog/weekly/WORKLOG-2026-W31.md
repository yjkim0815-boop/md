---
문서유형: WORKLOG
범위: 프로젝트(ha-web-api)
주기: 주
기간: 2026-W31 (07-27~)
작성일: 2026-07-27
최종수정: 2026-07-27
작성자: AI(Claude)
상태: 진행중
요약: 인증 API(me→check), KCB 본인인증 complete postMessage, /api/page/cert 라우팅 통일
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

## 다음 할 일 (TODO)
- [ ] 신규 계약 API 에 join-policy(authInfo 수신)/join-view(복호화 반환) 존재 확인·없으면 추가
- [ ] ELB /api strip 여부 확인 → cert 컨트롤러 매핑 확정
- [ ] KCB complete postMessage targetOrigin 을 '*' → 프론트 오리진 제한(운영 보안)

## 배포 목록 (dev-www)
- Java: `AuthApiResource`, `CertController`, `CertPhoneController`, `CertIpinController`, `SitemeshFilter`, `DeviceRedirectFilter`
- JSP/JS: `cert/kcb/{phone,ipin}/complete.jsp`, `cert/kcb/config.jsp`, `cert/nice/*/config.jsp`, `unvus.util.js`

## 참고
- 이전 주차: [WORKLOG-2026-W30](./WORKLOG-2026-W30.md)
