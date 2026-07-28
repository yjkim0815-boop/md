---
문서유형: WORKLOG
범위: 프로젝트(happypoint-web2)
주기: 주
기간: 2026-W31 (07-27~)
이슈키: WORK-16611
작성일: 2026-07-27
최종수정: 2026-07-27
작성자: dominic
상태: 진행중
요약: KCB 본인인증(휴대폰·아이핀) React 연동, SSR 로그인 판별, 서버 파일 로그, /api 라우팅 통일
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

## 다음 할 일 (TODO)
- [ ] 신규 계약 API(`JoinApiResource`/`BrandMemberApiResource`)에 join-policy(authInfo 수신)·join-view(복호화 정보 반환) 존재 여부 확인
- [ ] 약관동의 → 정보입력폼 authInfo 연동 (HttpOnly 쿠키 방식)
- [ ] ELB /api strip 여부 확인 후 cert 컨트롤러 매핑 확정
- [ ] `/api/cert/log` 디버깅 로깅 제거(운영 전)
- [ ] 로그인 세션 유지 후속(마이페이지 등 게이트)

## 참고
- 상세 이전 주차: [WORKLOG-2026-W30](./WORKLOG-2026-W30.md)
- 백엔드 짝: [ha-web-api INDEX](../../ha-web-api/INDEX.md)
