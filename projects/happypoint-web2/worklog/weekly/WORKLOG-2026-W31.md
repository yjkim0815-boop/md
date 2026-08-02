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

## 11. (07-31) 회원가입 흐름 정리 — 공통 alert·필드 리네임·브랜드 라우트 이동
- **공통 안내 페이지**: `/page/join/popup` → **`/page/common/alert`** 이관(구 경로는 완전 이동 아님/리다이렉트 스텁 유지). alert 랜딩 규격(type 5종·문구·버튼)은 이 페이지가 **정본(SSOT)**, 백엔드는 값만 내려줌.
- **백엔드 `/api/join/policy` 응답 변경**: `landingType`→**`alertType`**, `landing` 유지, 요청 컨텍스트 `reqPath`/`reqChnl`/`reqPage` **전 분기 항상 포함**(없으면 빈값). 주석은 alert 규격 제거 후 프론트 SSOT 포인터만.
- **디버그 제거**: `join-auth.tsx`의 클라이언트 `console.log("[cert]", data)`(개인정보) + 죽은 `/api/cert/log` fetch 제거 → 클라이언트 `console.log` 0건. (서버 `apiLog`는 유지, `next start`라 브라우저 미노출)
- **as/ad**: 앰플리튜드(분석) 전용 → 회원가입 policy 체인엔 **넘기지 않음**(확정). 레거시 model명 `app_as`/`app_ad`, 신규 API 응답 `appAs`/`appAd`, 요청 파라미터는 공통 `as`/`ad`.
- **브랜드 본인인증 라우트 이동**: `/page/brand/member/join-auth` → **`/page/brand/member/join/index`** (완전 이동, 하위호환 스텁 없음). 참조 갱신: join-gate CTA, middleware `OPBS_REDIRECT_MAP`(`/page/join/auth.spc`→새 경로), canonical, error 태그, interface 주석. 백엔드 계약 API `/api/brand/member/join-auth`·lib는 **불변**.
  - ⚠️ 브랜드 `join/index` 페이지는 아직 **KCB 팝업 미연동(정적 placeholder)** — 일반 `join-auth.tsx`의 `openCert` 이식 필요(미결).

## 12. (07-31) 파바앱(브랜드) 본인인증 팝업 이식 — 일반과 정합 ★
- **레거시 확인**: 브랜드 `join-auth.spc`는 `instCd`를 **INSAUT 쿠키**로 저장, cert 팝업(config.jsp)은 `reqChnl/reqPage/reqPath`만 읽음(instCd 안 읽음). 즉 팝업 파라미터 세트는 일반과 동일, **reqChnl 자리에 브랜드 코드(instCd)** 를 싣는 구조.
- **일반 `join-auth.tsx`**: 팝업 `reqChnl` `"NONE"` → **`channel`(pc/mo, 없으면 빈값)**.
- **신규 `brand/member/join/index/join-auth.tsx`**(일반 포팅): cert 팝업 `reqChnl=instCd`·`reqPage=join`·`reqPath=OPBS`. 성공 → form POST → `/page/brand/member/join-policy` (hidden: authInfo/reqPath=OPBS/reqPage=join/reqChnl=instCd/**instCd**). `brand/member/join/index/page.tsx`는 정적 → `BrandJoinAuth` 렌더(휴대폰만), `getJoinAuth` SSR 검증 유지.
- **미들웨어**: `POST /page/brand/member/join-policy` 브랜치 추가 → `hp_join_auth` 쿠키(+instCd) 저장 후 303 GET(일반과 동일 방식).
- **브랜드 `join-policy/page.tsx`**: searchParams → **쿠키(hp_join_auth)에서 authInfo/instCd/reqPath 읽어 `postJoinPolicy`** 호출로 정합(쿠키 없으면 searchParams 폴백).
- **백엔드 `BrandMemberModelApiResource.joinAuth`**: `reqPath` `"APP"`→**`"OPBS"`**.
- 확정 규칙: 일반 reqChnl=pc/mo(없으면 빈값), 파바앱 reqChnl=instCd. as/ad는 앰플리튜드용(policy 미전달).

## 13. (07-31) 브랜드 약관 라우트 이동 + as/ad 앰플리튜드 버그 수정
- **라우트 완전 이동**: `/page/brand/member/join-policy` → **`/page/brand/member/policy`** (하위호환 스텁 없음). 갱신: 이동된 page/error, `join/index/join-auth.tsx` form.action+주석, `middleware.ts`(브랜드 policy POST 브랜치 pathname·쿠키 path), interface 주석. 백엔드 API `/api/brand/member/join-policy`·lib는 불변.
- **as/ad 앰플리튜드 연결 버그 수정**: `analytics-provider.tsx`가 URL에서 `app_as`/`app_ad`(레거시 **model 속성명**)를 읽어 `setSessionId`/`setDeviceId`가 **한 번도 동작 안 하던** 문제 → 실제 URL 파라미터 **`as`/`ad`** 로 교체. 앰플리튜드 초기화는 **전역 프로바이더 단일 지점**(중복 없음)이라 이 한 파일로 전량 수정됨.

## 14. (07-31) 룰셋 "1 page ↔ 1 model API" 확립 + 그룹1 배선
- **룰셋 확정**: 모든 프론트 page.tsx는 진입 시 대응 모델 API 1회 호출(데이터 불필요해도). `lib/model-ping.ts` `pingModel()` 신설(fire-and-forget). 없으면 백엔드 생성(성공만 반환). → INDEX 아키텍처 핵심 + 메모리(page-model-api-rule)에 저장.
- **전수조사**: 79개 page 중 33개 모델 API 미호출 → 대응 API 존재(그룹1 17~18) / 이름확인 필요(그룹2 8) / 정적(그룹3 8)로 분류.
- **그룹1 배선(진행)**: 18개 page에 `pingModel("/api/...")` 추가. POST 전용 3개(join/form·join/optional-form·member-info/modify-info-form)는 백엔드에 **진입 핑용 GET 엔드포인트**(빈 `LinkedHashMap` 성공) 추가. 백엔드 컴파일 ✅.
- **`/api/join/index`**: 파라미터 에코 제거(빈 data 반환) — 프론트는 URL에서 직접 읽으므로 불필요.
- 그룹2·3은 사용자 검토 대기.

## 15. (07-31) 그룹2 배선 — 신규 모델 API 6개 + 스텁 + 핑
- **백엔드 신규 GET 모델 API 7개**(전부 성공만 반환 스텁, `com.spc.hpc.api.model.*`): `event/my-coupon`, `search`(page/search용), `dormancy/auth-form`, `member-info/{withdrawal-form, find-id-pw-form, confirm-pw-form, change-pw-form}`. 컴파일 ✅.
- **`page/search`**: 삭제하려 했으나 **실사용 검색 결과 페이지**(header-search·mobile-header·site-nav·layout SearchAction·robots 참조) 확인 → 삭제 대신 빈 모델 API(`/api/search`) 신설·연결로 방향 전환.
- **프론트 그룹2 8개 page** `pingModel` 배선: `join/auth`→`/api/join/index`, `event/my-coupon`, `dormancy/auth-form`, `search`, `member-info/{withdrawal-form,change-pw-form,confirm-pw-form,find-id-pw-form}`.
- ※ 신규 6개는 현재 **성공만 반환하는 스텁**. 레거시 컨트롤러(MemberInfoController form 계열·DormancyController·couponService) 실로직 이식은 후속 과제.

## 16. (07-31) main 머지 + 스테이징 도메인 정합
- **머지**: `feature/WORK-16613` → `main`(커밋 `a31b9de`). 충돌 10파일 해결(중요: `lib/legacy-http.ts` git auto-merge 함수중복 → main버전 복원). main 실기능 보존 + 16613 산출물(pingModel·브랜드흐름·analytics·common/alert) 전량 반영. tsc 신규에러 0(main baseline 17=머지 17). push는 미실행.
- **스테이징 도메인**: 프론트 `.env.stg` `LEGACY_BASE` `www`(오류)→**`stg-www.happypointcard.com`** + `LEGACY_BASE_FALLBACK`·`NEXT_PUBLIC_API_BASE=""` 추가. 백엔드 `application-stage.yml`은 이미 stg-www(불변). 구동=PM2 `ha-web-fo` `pnpm start:stg`.

## 17. (07-31) `/page/auth/login` 개발 서버 404 수정
- **증상**: `app/(site)/page/auth/login/page.tsx` 파일과 Next 개발 산출물은 존재했지만, 로컬 `pnpm dev`에서 `/page/auth/login`이 404로 응답.
- **원인/조치**: 해당 페이지가 정적으로 최적화되는 경로로 처리되어 `(site)` 라우트 등록이 불안정했다. 로그인 상태 확인은 요청 단위 SSR이므로 `page.tsx`에 `export const dynamic = "force-dynamic"`을 명시했다.
- **검증**: `http://localhost:3000/page/auth/login` HTTP 200, 페이지 제목 `로그인 | Happy Point` 및 로그인 폼 렌더링 확인. `/api/auth/check`도 정상 200 응답.

## 18. (07-31) 모델 API param/model 디버그 로깅 (운영 제외)
- `lib/model-ping.ts` `pingModel()`: 모델 API 호출 후 **받은 파라미터 + 모델 응답**을 `apiLog`로 출력.
  - 형식: `[model] <path>` / `param=<x-hp-query & x-hp-body>` / `model=<응답 JSON>`.
  - param 출처 = 미들웨어가 심은 원요청 GET쿼리(`x-hp-query`) + POST바디(`x-hp-body`) → **페이지 수정 0**(24개 page가 이미 `pingModel` 호출).
- **노출 게이트**: `process.env.APP_ENV !== "prod"` → local/dev/stg 노출, **운영만 제외**(개인정보 보호). apiLog 경유(서버 로그파일 + 콘솔).
- tsc: 신규 에러 0(baseline 17 유지).

## 19. (07-31) 메인 일반 배너 계약 API 연동
- 홈(/, PC/모바일 공통) 하단의 "지금 가장 인기 있는 이벤트만 모았어요" 마키를 정적 배너 대신 새 배너 API 응답으로 교체.
- AppHomeBanner가 서버에서 세션 쿠키를 전달해 호출하고, 이미지·브랜드·제목·부제목·링크를 카드에 렌더링한다. Oracle/MyBatis Map 직렬화의 대문자 키도 함께 수용.
- 각 카드에 API의 모든 원시 필드를 `data-*`로 자동 전개한다(예: `BN_INFO_ID` → `data-bn-info-id`). `IMG_URL`/`imgUrl`은 HTTP(S)·상대경로 검증 후 실제 img 태그에 적용.
- 후속 정합: 실제 응답의 스네이크 케이스(`img_url`, `brand_nm` 등)도 카멜/대문자 키와 동일시해 읽도록 키 정규화. 데이터 속성만 보이고 이미지·문구가 비던 현상을 해결.
- 배너 카드의 `promo-card-text` 텍스트 오버레이를 제거하고 이미지 단독 노출로 확정. `data-*`와 링크 동작은 유지.
- 링크는 상대 경로 또는 HTTP(S)만 허용하며 외부 링크는 새 탭으로 연다. 조회 실패 또는 빈 목록이면 섹션을 숨긴다.
- 검증: pnpm exec tsc --noEmit 실행. 이번 변경 오류 0건, 기존 회원정보/마이페이지 타입 오류 16건으로 전체는 실패.

- 배너 클릭은 `returnUrl` 없이 `/page/auth/login?bninfoid=<BN_INFO_ID>&linkvalue=<LINK_VALUE>`로 이동한다. 로그인 GET 랜딩 시 middleware가 두 URL 값을 동일 이름의 `httpOnly` 쿠키(`SameSite=Lax`, `Path=/`, 30분)로 저장해 후속 로그인 처리에서 사용할 수 있게 했다.

## 20. (07-31) 세션 stickiness 이슈 — ALB 앱쿠키 방식 (Redis 미사용) ★미결
- **증상(스테이징)**: ALB 스티키를 duration(ELB세션)으로 뒀는데, **프론트 SSR→백엔드** 구간이 스티키로 못 붙어 JSESSIONID 세션 미스. 프론트는 한쪽에 붙지만 백엔드는 라운드로빈.
- **원인**: ALB 스티키는 브라우저가 `AWSALB` 쿠키를 저장·재전송해야 유지되는데, **SSR(front 서버)은 브라우저가 아니라 쿠키잼이 없어** 매 요청 새 방문자로 인식 → 라운드로빈. (front·백엔드 동일 도메인이라 `AWSALB` 쿠키명 충돌도 겹침)
- **채택 방향(Redis 안 씀)**: ALB **애플리케이션 기반 stickiness** + **앱 쿠키명 `HA_AWSALB`**. 단, **프론트가 모든 SSR 호출에 요청 쿠키(JSESSIONID+`HA_AWSALB`)를 forward** 해야 실효.
- **현재 프론트 쿠키 forward 실태**: `getCurrentUser`(check)만 forward ✅ / `pingModel`·`join/policy` raw fetch·`legacyContractGet/Post`(기본) ❌ → 이 호출들은 여전히 라운드로빈.

## 21. (07-31) 회원가입 약관(policy) 정합 — 동의값 POST 전달 + 약관 전문 이식 ★
- **Part 2 (기능)**: PolicyForm이 **앞단계에서 받은 값 + 화면 동의값을 전부 form POST**로 다음 단계 전달.
  - `AGREE_CODE` 매핑(레거시 pc/join/policy.jsp hidden name): 필수 `EUTL`(이용약관)·`ETDP`(제3자), 안내 `EIND=Y 고정`, 선택 `SIND/SBRD/STDP/SLOC`, 제휴사 `SBRD2~5`(신한/SK브로드/메리츠/SK엠앤). 멤플러스·광고성은 레거시처럼 **미제출**. 필수 체크 2개 = EUTL+ETDP.
  - PolicyForm props로 `authInfo(무조건)/reqPath/reqPage/reqChnl/joinInfo` 수신 → 히든필드로 POST. `router.push` 제거.
  - `policy/page.tsx`: 응답 `joinInfo` 읽어 props 전달. `middleware.ts`: **`POST /page/join/form` 브랜치** → policyInfo 전체 `hp_join_policy` 쿠키(303 GET). `join/form/page.tsx`: 쿠키→**`POST /api/join/form`**(백엔드 setPolicyCookie + `_AUTH_INFO_TOKEN_` 복호화 프리필), none-auth/error→공통 alert.
- **Part 1 (약관 전문)**: 프론트 모달 근사치 → 레거시 `popupTerms` 순수텍스트 **1:1 이식**.
  - 교체: `ETDP`(03)·`SIND`(04)·`SBRD`(07)·**`STDP`(05, ~40개 제휴사 전량**→`ALLIANCE_GROUPS` 온·오프라인 그룹핑)·제휴사 `SBRD2~5`(09~12)·멤플러스(08)·광고성(13/14). 제네릭 `affiliateTerm`/`AFFILIATES` 제거→업체별 실데이터.
  - 유지: `EUTL`(01, 399줄)·`SLOC`(06, 494줄)는 전체 법령문서라 **외부 링크 유지**. `notice`(02)는 이미 일치.
- **약관 대조 방법**: HTML 태그 제거 순수 텍스트로 비교 → `notice`(EIND)만 기존 일치, 나머지는 프론트 임의요약이었음(제3자=SPC 계열사 실명 누락 등) 확인 후 교체.
- tsc: 신규 에러 0(baseline 17 유지).
- 후속(미결): `join/form` 프리필(RSLT_NAME/TEL_NO/isUnder14/joinInfoObj)을 JoinInfoForm에 연결(현재 폼 props 미수신).

- `pingModel()` 서버 로그의 페이지 파라미터를 원본 query/body 문자열 대신 JSON 객체로 직렬화하도록 변경했다. 빈 값은 `param={}`, 예: `?redirectUrl=HCHP&cd=HPWW`는 `param={"redirectUrl":"HCHP","cd":"HPWW"}`로 기록하며 중복 키는 배열로 보존한다. `model=`은 기존과 같이 API 응답 JSON을 기록한다. 전체 `tsc` 및 eslint 실행은 패키지 프로세스가 시간 제한을 넘어 완료 결과를 얻지 못했다.

- `/page/join/policy`는 `pingModel()` 대신 직접 `POST /api/join/policy`를 호출하므로 별도 디버그 로그를 추가했다. local/dev/stg(`APP_ENV !== "prod"`)에서만 `param={authInfo,reqPath,reqPage,reqChnl}`과 `model={...}`을 출력하며 운영에는 인증 정보가 기록되지 않는다.

## 다음 할 일 (TODO)
- [ ] (07-31) 회원가입 form 단계 프리필: 백엔드 `/api/join/form` 응답(RSLT_NAME/TEL_NO/TEL_COM_CD/isUnder14/joinInfoObj/encMnm)을 `JoinInfoForm`에 연결
- [ ] (07-31) modify-info-form: 프론트가 `result.alertType`(need-confirm-pw/need-ownership) 분기 처리(현재 result.code만 봐서 깨짐) + 백엔드 alertType 숫자 prefix(`1need-…`) 제거
- [ ] (07-31) ★ **[인프라] ALB 앱쿠키 stickiness 설정** — 백엔드 TG 애플리케이션 기반 stickiness, 앱 쿠키명 **`HA_AWSALB`**, 기간=세션 수명. 프론트 TG stickiness는 끄기(쿠키명 충돌 방지).
- [ ] (07-31) ★ **[프론트] 모든 SSR 백엔드 호출에 요청 쿠키 forward 통일** — `legacyContractGet/Post` 기본 `forwardCookies:true`, `pingModel` 쿠키 전달, `join/policy` 등 raw fetch에 `cookie` 헤더 추가. (ALB 설정만으론 안 됨 — 이게 핵심 전제)
- [ ] (07-31) [백엔드] `HA_AWSALB` 쿠키가 로그인/응답 Set-Cookie로 브라우저까지 전파되는지(BFF 프록시 경유) 확인. 세션 TTL·스케일인 재분배 엣지 점검.
- [ ] (07-31) (대안 보류) Spring Session + Redis(ElastiCache) — 앱쿠키 방식의 취약점(충돌·TTL·재분배) 재발 시 근본 전환 검토.
- [ ] (07-31) 그룹2 신규 스텁 API 실로직 이식(레거시 컨트롤러 기반) 여부 결정
- [ ] (07-31) 그룹3(정적: about/points/services/mypage-inquiry 등) 처리 방침 결정
- [ ] (07-31) 브랜드 policy 이후(join-view/optional/complete)로 instCd·authInfo 전파 검증(쿠키/API)
- [ ] (07-31) cert `request.spc`가 reqChnl=instCd(브랜드) 처리에 문제없는지 dev 확인
- [ ] (07-31) 회원가입 none-auth 근본원인(sessionStorage↔쿠키 불일치 + `_AUTH_INFO_TOKEN_` 크로스오리진 전달) 수정
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

## 14. (2026-07-31) Login empty model API
- `app/(site)/page/auth/login/page.tsx` now calls `await pingModel("/api/auth/login")` at page entry.
- The login page query (for example `returnUrl`) is therefore logged as `param={...}` and the empty backend response as `model={...}` in local/dev/stg only, following the existing `pingModel` logging rule.

## 15. (2026-07-31) One-time POST bridge cookie
- Standardized the POST-to-GET RSC bridge cookie naming rule as `hpw_` plus the target URL segments after `/page/`: `/page/join/policy` becomes `hpw_join_policy`.
- `getPostBridgeCookieName()` is shared by middleware and RSC pages. Current flows are `hpw_join_policy`, `hpw_join_form`, and `hpw_brand_member_policy`; each keeps its own cookie `Path`, so values cannot collide.
- On the target GET request, middleware passes the original request cookie to the RSC once and returns `Set-Cookie` with `maxAge: 0` for the matching path. The browser therefore removes the bridge cookie immediately after it is consumed.

## 16. (2026-08-02) 회원가입 policy→form `_AUTH_INFO_TOKEN_` 쿠키 자동연동 (SSR 유지)
- **문제**: 백엔드 `join/policy`가 재암호화 토큰(`flagCertifiTime=Y`)을 `_AUTH_INFO_TOKEN_` 쿠키(Set-Cookie)로 심는데, `policy/page.tsx`가 **SSR fetch**로 호출 → 이 Set-Cookie가 Next 서버까지만 오고 **브라우저로 전파 안 됨**. 다음 단계 `form()`은 이 쿠키로 인증 판별 → 항상 `none-auth`.
- **원인(구조적)**: Next의 서버 `fetch`엔 쿠키 jar 없음 + **RSC(page 렌더)는 `cookies().set()` 불가**(Route Handler/Server Action/middleware 에서만 가능). 모놀리식(브라우저↔백엔드 직결)→BFF/SSR(브라우저↔Next↔백엔드)로 바뀌며 중간 Next 계층이 Set-Cookie를 가로챈 것.
- **해결(모델API·로그인체크 서버사이드 유지, 클라이언트 fetch·백엔드 변경 없음)**:
  1. `policy/page.tsx`(SSR) — 응답 `res.headers.getSetCookie()`에서 `_AUTH_INFO_TOKEN_` **값만 읽어**(RSC는 읽기 가능) PolicyForm에 `authToken` prop 전달. 겸해서 policy 호출에 `cookie: store.toString()`로 요청 쿠키 upstream 자동 첨부.
  2. `policy-form.tsx` — `authToken`을 form POST hidden 필드 `_AUTH_INFO_TOKEN_`로 실어 `/page/join/form` 전송.
  3. `middleware.ts` — `/page/join/form` POST 가로챌 때 `_AUTH_INFO_TOKEN_`을 **진짜 브라우저 쿠키**(httpOnly, path=/, 30분)로 set + 백엔드로 보내는 `policyInfo`에서는 제외.
  → 이후 `form/page.tsx`(SSR)가 `store.toString()`(그 쿠키 포함)을 upstream 전달 → 백엔드 `form()` 인증 통과.
- **일반 원칙 확립**: SSR fetch로 유실되는 "백엔드 발급 쿠키"는, 쿠키 쓰기 가능한 계층(middleware/Route Handler/Server Action)에서 복원해야 한다. 브라우저가 Route Handler(`/api/auth`,`/api/legacy`) 경유로 호출하면 그 핸들러가 `getSetCookie()`를 relay하므로 자동(로그인이 되는 이유).
- tsc: 변경 파일(policy/page, policy-form, middleware) 에러 0.

## 17. (2026-08-02) 회원가입 none-auth 근본원인 — 미들웨어 Edge 바디읽기 + 브리지쿠키 one-time 삭제
- **증상**: 본인인증 성공 후 policy에서 authInfo 빈값 → `none-auth`. 프론트 로그 `param={"authInfo":"",...}` 전부 빈값.
- **원인 2겹**:
  1. `join-auth.tsx`가 `/page/join/policy`로 form POST → 미들웨어(Edge)가 바디를 읽어 브리지 쿠키 생성하는 구조인데 Edge 바디읽기 불안정. → **POST 수신을 Node Route Handler로 이전**: `app/api/join/policy-bridge/route.ts`(`runtime="nodejs"`, formData 안정 read), `join-auth.tsx` action=`/api/join/policy-bridge`.
  2. **진짜 근본원인**: `middleware.ts`의 "브리지 쿠키 one-time 삭제" 블록이 GET `/page/join/policy`에서 `hpw_join_policy`를 응답 `maxAge=0` 삭제 → **Next가 이 삭제를 같은 요청 RSC `cookies()` 뷰에 반영** → RSC가 읽기도 전에 비워짐(구 flow도 동일하게 당함). → **해당 블록 제거**(브리지 쿠키는 짧은 maxAge/덮어쓰기로 만료).
- 검증: 프론트 로그 `[JOIN-POLICY-BRIDGE] authInfoLen=896` + policy `landing=true,type=policy` 확인.

## 18. (2026-08-02) 회원가입 form→optional 파라미터 전송 + 프리필 연결
- **form 프리필**: `form/page.tsx`가 백엔드 `form()` 응답(`RSLT_NAME/RSLT_BIRTHDAY/TEL_NO` + 컨텍스트 `encMnm/telNo/telComCd/reqPath·reqChnl·reqPage/isUnder14/joinInfoObj`)을 `JoinInfoForm`에 전달. 이름/생년월일/휴대폰 표시(하드코딩 "본인인증 후 표시" 제거).
- **form→optional 전송**: 기존 `router.push(id)`(id만) → **레거시 hidden 필드 1:1 전부 POST**(userId/pwd/postInput/homeRoadNmAddr1·2/mailId/telNo/telComCd/encMnm/reqPath·reqChnl·reqPage/regPath=PC/hpAuthYn=Y/checkIdResult/mkt*/juniorYn/보호자필드) → `app/api/join/optional-form-bridge/route.ts`(신규 Node) → `hpw_join_optional_form` 쿠키 → `optional-form/page.tsx`가 `POST /api/join/optional-form`(백엔드 encMnm 무결성 검증). 최종 joinProc는 범위 외.

## 19. (2026-08-02) 회원가입 데이터컨트롤 레거시 정합 (#2 중복확인 · #3 주소 · #4 인증)
- **레거시 대조 결론**: 기존 form은 입력UI+목업검증만, 실 데이터컨트롤/제출 누락이었음. form.jsp 기준 이식.
- **#2 아이디/이메일 중복확인 실 API**: `join-info-form.tsx`가 가짜 `TAKEN_IDS`/무조건ok 제거 → `GET /api/join/check-id`(`result.onlnIdUsePossYn`)·`check-email`(`useFlag`) 실호출. 프록시 `app/api/legacy/[...path]` 허용목록에 `api/join/check-id`·`api/join/check-email` 추가(백엔드 `JoinResource @RequestMapping /api/join`).
- **#3 주소검색(키리스 Daum, 임베드)**: 레거시는 `postcode.v2.js`+`findZipcode.js`의 **키 없는 Daum 임베드**(appkey/confmKey 없음). 프론트도 `new window.daum.Postcode({oncomplete,onresize,width,height}).embed(el)` 동적로드로 포팅(레거시 `findZipcodeNewIframe` 동일 인라인 iframe 방식 — `#findZipCodeArea` 대응 컨테이너 div ref). zonecode→postInput, 도로명 참고항목 조합→homeRoadNmAddr1, 상세주소→homeRoadNmAddr2. 가짜 ADDRESS_BOOK 제거.
  - **CSP 원인·해결(중요)**: 최초 미동작 원인 = `next.config.mjs` CSP가 Daum 도메인 차단(`script-src`에 `t1.kakaocdn.net` 없음, `frame-src 'self'`). → 레거시 `header-ga4.jsp` CSP 미러: `script-src` += `https://t1.kakaocdn.net`, `frame-src` += `https://postcode.map.daum.net https://postcode.map.kakao.com`. **CSP는 응답헤더라 dev 서버 재시작 필요.**
- **#4 인증 정합(정정 2026-08-02)**: 처음엔 "아이핀 폐지(A안)"로 이해해 진입 아이핀을 제거했으나, 사용자 재확인 결과 요구는 **"진입은 휴대폰+아이핀 2종 유지, 보호자 인증만 휴대폰 팝업"**이었음 → **진입(`join/index`·`join/auth`) 아이핀 복원**. 보호자만 휴대폰 단일.
  - 14세미만(`isUnder14`) 보호자 동의 블록(form) → `useKcbCert(reqPage='parent')` 팝업(진입 휴대폰과 동일 KCB 모듈) → postMessage(`reqPage==='parent' && pFlag==='Y'`) → `P_authYn=Y/P_authInfo/P_userName(pInfo)/ptorFamyRelCd=90`. 미인증 제출 차단.
  - **아이핀 회원 휴대폰 SMS 점유인증(구현 완료)**: form에서 `TEL_NO` 없으면(=아이핀 회원) 통신사 select + 번호입력 + 인증요청/확인 블록 표시. 백엔드 SMS API는 이미 존재(`SmsResource @RequestMapping /api/sms`, `POST /send·/check/mobileOwnerAuthNo`, `@RequestBody` JSON). 프록시 `/api/legacy` 허용목록에 두 경로 추가. send `{mobileNo}`→`result.authNo`(암호화)+3분타이머, check `{mobileAuthNo,authNo,mobileNo,userNm=RSLT_NAME}`→성공 시 `telNo`/`encMnm(=result.data)` 로컬 state 확정. 아이핀 회원은 점유인증 완료 전 제출 차단. 제출 시 `certType=ipin|mobile` + verified telNo/encMnm/telComCd 전송.
  - 판별: `form()` 응답 `TEL_NO` 유무(휴대폰 회원=프리필 읽기전용 / 아이핀 회원=SMS 블록).
- tsc: 변경 파일 전부 에러 0.

## 20. (2026-08-02) 회원가입 최종 저장(joinProc) 파이프라인 연결 — optional→welcome
- **레거시 대조**: `optional-form.jsp` → `page.joinProc(data)` = `$.ajax POST /api/join/joinProc` (JSON: 전 단계 암호화 joinInfo + intrFildCd) → code 00 시 `welcome.spc`. 백엔드 `JoinResource.joinProc`가 `_AUTH_INFO_TOKEN_`(flagCertifiTime=Y) + `getPolicyCookie()`(join_policy_info) + 각 값 복호화(intrFildCd 제외) → `saveNewMember` → `_HPC_USER_ID_`/`_HPC_EN_MBR_NO_` 쿠키 세팅.
- **발견 문제 & 해결**:
  1. **encMnm 검증은 안전**(SHAUtil.checkEncMnm: reqChnl/reqPage/reqPath는 로그용, 해시는 `SHA512(userNm|telNo)+salt`) → 프론트가 RSLT_NAME(쿠키)·telNo만 맞추면 통과(현 구현 OK).
  2. **`join_policy_info`(동의값) 쿠키 SSR 유실** → `form/page.tsx`가 form() 응답 Set-Cookie에서 값 캡처 → `JoinInfoForm` `policyCookie` prop → 제출 hidden `__join_policy_info` → `optional-form-bridge`가 **raw Set-Cookie**(이중인코딩 방지)로 `join_policy_info` 브라우저 쿠키 복원.
  3. **암호화 joinInfo 미전달** → `optional-form/page.tsx`가 optionalForm 응답 `result.joinInfo`(암호화) 캡처 → `ReferralForm`에 전달.
  4. **최종 joinProc 미구현** → `ReferralForm`: 레거시 intrFildCd 코드(J1~J7/P1~P3/JZ, 나중에하기=JY) + `POST /api/legacy/api/join/joinProc {...joinInfo, intrFildCd}`(프록시가 쿠키·Set-Cookie relay) → code 00 시 `/page/join/welcome` push. 프록시 허용목록에 `api/join/joinProc` 추가.
  5. **welcome(완료) 페이지** → `pingModel` 대신 **SSR `GET /api/join/welcome`(쿠키 forward)** 로 joinProc 가 심은 `_HPC_USER_ID_` 쿠키에서 실제 가입 아이디를 읽어 표시(쿼리 id 폴백). 축하화면+아이디+로그인 버튼.
- ✅ **PC 회원가입 E2E 성공(2026-08-02)** — 본인인증→약관→정보입력→가입경로→joinProc→welcome 완주, 실제 회원 저장 확인. (PC 휴대폰 인증 경로 기준)
- **누락 필드 보정**(form→optional 제출): `homeRoadNmPostNo`, `labelAddress`, `ptorTelNo`/`ptorEmlAddr`(빈값) 추가.
- **옵셔널 페이지 = 레거시 정합 확정(2026-08-02)**: 레거시 `optional-form.jsp`에서 수신매체(infoRetnMda)/직업(jobCd)/결혼기념일(maryCeleDay)은 **주석처리(비활성)** → 실사용 필드는 `intrFildCd` 하나뿐. `ReferralForm`이 intrFildCd + 전단계 암호화 joinInfo 전달 + 나중에하기(JY)/가입완료로 이미 동일. **추가 이식 대상 아님(사용자 1번 선택).**
- **미결(런타임 검증 필요)**: dev 재기동 후 전 구간 E2E(휴대폰/아이핀/14세) 테스트, 임시 진단 로그(`[ADDR]`,`[JOIN-*-BRIDGE]`) 제거, welcome 페이지 표시값 확인.
