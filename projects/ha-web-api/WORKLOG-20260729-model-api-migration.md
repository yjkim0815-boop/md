---
문서유형: WORKLOG
프로젝트: ha-web-api
작성일: 2026-07-29
최종수정: 2026-07-29
작성자: dominic
상태: 진행중
요약: 레거시 Spring MVC 페이지 컨트롤러 → 신규 모델API(com.spc.hpc.api.model) 전수 이식(A 스텁 → B 신규 → C 라우트)
---

# 🔁 모델API 전수 이식 (레거시 페이지 컨트롤러 → /api/model)

레거시 `/page/*.spc` 화면 컨트롤러 로직을 신규 **모델API**(`com.spc.hpc.api.model.*`, `*ModelApiResource`)로 이식.
매핑: `/page/X.spc` → 프론트 라우트 `/page/X` + 백엔드 `/api/X`.

## 전수조사 결과 (2026-07-29 기준)
- 완료(이식+계약): ~45 / 스텁(notImplemented): 32 / 모델API 없음: ~35 / 라우트만 없음: 9
- 3구분: **A**=스텁 이식(로직만 이식) / **B**=신규 모델API+계약 / **C**=프론트 라우트만 추가
- 진행: **A 완료(32/32)** · **B 백엔드 완료(compile OK)** · **C 완료(9/9, tsc 신규 에러 0)** — 전 클러스터 이식 완료

## 응답 컨벤션 (이식 공통)
레거시의 view반환/redirect/쿠키를 **엔벨로프 `code "00"` + `result`** 로 통일:
- `landing`(boolean) + `landingType`(진행 화면) / `alertType`(안내 화면)
- 실패·안내는 헬퍼로: `commComplete(code,msg)`(brand H891/H871/H874/H499 등) · `ownershipProc(code)`(점유인증 03/04) · `confirmRedirect(cd)`(비번확인 재유도) · none-auth/auth 등
- 쿠키(`_AUTH_INFO_TOKEN_`·`_EXOG_MEMBER_INFO_INSAUT_`·`_MEMBER_CONFIRMED_` 등)·리다이렉트 배관은 프론트(미들웨어 쿠키 브리지 + `/page/common/alert`)로 넘김 — **테스트하며 마무리(사용자 결정)**.

## 진행 현황
### ✅ A — 스텁 이식 32/32 완료
| 도메인 | 개수 | 파일 |
|---|---|---|
| A-1 brand/member | 21 | `BrandMemberModelApiResource` — 회원가입(5)·휴면(3)·찾기(3)·비번확인/점유인증(4)·정보수정(2)·비번변경(2)·탈퇴(2) |
| A-2 member-info | 6 | `MemberInfoModelApiResource` — modify-info/change-pw/withdrawal-process, find-id-pw-process/complete, confirm-pw-process |
| A-3 join | 3 | `JoinModelApiResource` — form, optional-form, welcome |
| A-4 dormancy | 2 | `DormancyModelApiResource` — auth-process, dormancy-process |
- 이식 근거: `BrandMemberController`/`MemberInfoController`/`JoinController`/`DormancyController` 그대로(authInfo 복호화·5분/180일 유효·checkMemberByCi·점유인증(sucToken/loginToken/ownershipHist)·brand 로그인체크(INSTCD/ENCAUT)·resetPw/changePw/withdrawal/releaseDormancy·안내메일·OUNF encTime).

### ✅ B — 신규 모델API 완료 (backend compile OK)
- **member-info**: confirm-ownership-form/proc, change-email-form/process, change-email-complete, index, indexForWithdrawal
- **customer**: qna(1:1문의 암호화 파라미터), voc(상담내역 action=등록/목록 URL), term(약관 no==4→1) — `StringEncrypter(spc,,123_400001001005/ghi20130701)`·`ApiService.send(MB2200H0)`·`FieldMap`, hpNo 대시제거 미대입 레거시버그 보존
- **live**(`LiveModelApiResource`): secta9ine(stage전용, LIVE_NICKNAME 쿠키), live-show(S3 HappyLivePublish.json 파싱+AES128 딥링크), secta9ine-live-show(stage전용, LIVE_USERID/NICKNAME 쿠키+getLiveLoginToken). *grip-live-show 는 기존 구현*
- **alliance**: culture(정적), gate-check(allianceMallHit+파라미터에코), agree-proc(로그인체크→setAkAgr 등 세션갱신+getAllianceAgreeProc→gate-check 리다이렉트)
- **mypage-card**: index(→password 리다이렉트), register(로그인+정적)
- **cert**: nice/phone/fail, nice/phone-order/fail(getCertNiceLicense), nice/ipin/process(정적)
- **join**: policy-term(no 기본1), temp-id-app(정적)
- **event**: ai-jukebox(data 에코), event-proc(getEvent 메타; S3 JSP passthrough는 eventView와 동일하게 미수행·프론트 TODO)
- **sleeveqr**: qr-banner-count(updateQrBannerCount POST)
- **email**: unsubscribe(key복호화→MB2220H0 수신동의전송+Insertagreelog, rpsDtlCd 0000분기)
- **reception**: reception-agree-proc(E/S/P/D/T+세션기타항목 MB2220H0 전송→RECEPTION_REDIRECT_URI 리다이렉트)
- **survey**: error(공통 에러 정적). *coretype 는 기존 구현*
  - ※ `*-proc`/`eventProc`/`unsubscribe`/`agree-proc`/`qr-banner-count` 는 POST 액션(페이지 아님) → 프론트 route.ts 성격. 응답은 landing/redirectTo 로 통일.

### ✅ C — 프론트 라우트 추가 완료 (9/9, happypoint-web2)
- 9개 모두 기존 백엔드 모델API + 계약(interface) 존재 → `donation/intro` 패턴(SSR force-dynamic·`legacyContractGet`·`isApiOk`·`@/components/ui/subpage`)으로 api-lib + page.tsx(+error/not-found) 생성:
  - donation: happyBirthDay, voteList, voteView(+not-found), winnerList, winnerView(+not-found) → `/api/donation/{happy-birthday,vote-list,vote-view,winner-list,winner-view}`
  - reception-agree(로그인 게이트, `getCurrentUser`→AuthGate) → `/api/reception-agree`
  - event/sleeveQr(레거시 URL 유지) → `/api/sleeve-qr`
  - store/city-more(metro/cityName) → `/api/store/city`
  - live/grip-live-show(liveKey) → `/api/live/grip-live-show`
- ⚠ 서브에이전트가 계약 `[API]` 표기(`/api/page/...`, `/api/event/sleeveQr`)를 따라간 api-lib 3개(reception-agree/sleeveQr/grip-live-show)를 **실제 백엔드 경로로 수정 완료**. donation/store는 경로·파라미터(seq/center_gubun/metro) 일치 확인.
- 계약 수정 1건: `interface/page/live/grip-live-show.ts` 주석 내 `lk*/vk*` 가 `*/` 로 블록주석 조기종료 → `lk* / vk*` 로 정정(타입 불변).
- `npx tsc --noEmit`: 신규 9라우트+api-lib **타입에러 0**.

### 🔧 후속 — 회원가입 본인인증 진입로 통합 보강 (2026-07-30)
- **join/index reqPath 배관 복원**: 진입 URL 4개→`/page/join/index` 통합 과정에서 끊겨 있던 마지막 연결 수정. `join-auth.tsx` props에 `reqPath?` 추가 + 인증요청 파라미터 `reqPath:""`(하드코딩) → `reqPath ?? ""`(URL 유입경로값 전달). 레거시 `mobile/join/index.jsp`의 `reqPath:'${reqPath}'` 동작 복원. → `tsc --noEmit` 전체 **에러 0**(기존 prop 타입에러 해소).
- **레거시 진입로 전수 재확인**: 일반 가입 본인인증 진입 URL = `/page/join`·`/page/join/`·`/page/join/index.spc`·`/page/join/auth.spc` + **`/member/term.spc`**(RedirectFilter가 `/page/join/index.spc`로 변환하던 구 URL). middleware `JOIN_ENTRY_PATHS`에 **`/member/term.spc` 추가** → 5개 전부 `/page/join/index` 통합 rewrite. (누락 시 일반 `.spc` 규칙 타서 `/member/term` 404 였음)
- **로그인 체크 URL = rewrite 이후 경로로 통일 (2026-07-30)**: `getCurrentUser()`가 `POST /api/auth/check` 로 보내는 `body.url`이 기존엔 **rewrite 전 원본 경로**(예 `/page/join/auth.spc`)였음. middleware의 **모든 rewrite 분기**(OPBS·join진입·일반`.spc`·모바일`/`→`/mobile`)에서 `reqHeaders.set("x-hp-path", url.pathname)`로 **rewrite 이후 실제 렌더 경로**를 넘기도록 변경. 예: `/page/join/auth.spc?reqPath=APP` → 체크API `url=/page/join/index?reqPath=APP`. 쿼리는 clone 보존. `tsc --noEmit` 0.
- **일반 회원가입 reqPath 전달 보강 (2026-07-30, 브랜드 제외)**: ① reqPath 는 파라미터 미유입 시 **빈값 `""`**(join/index/page.tsx·join-auth.tsx 이미 준수). ② **본인인증 완료 시 다음 페이지(policy)로 reqPath 함께 전달**. 수신측 `policy/page.tsx`는 기존 `hp_join_auth` 쿠키 + **쿼리 reqPath 도 수신**(쿠키 우선) 보완.
- **policy 전달 파라미터에 reqPage/reqChnl 추가 (2026-07-30)**: 레거시 확인 결과 `reqChnl` 값은 **`pc`/`mo`**(JSP 전수: pc 19·mo 14곳). 회원가입 본인인증→policy 핸드오프에 `reqPage=join` + `reqChnl=pc|mo` 추가.
  - `join/index/page.tsx`: 서버에서 `isMobileUa(UA)` → `channel="mo"|"pc"` 계산해 `<JoinAuth channel>` 전달.
  - `join-auth.tsx`: `channel` prop 수신 → 인증성공 form POST hidden 에 `reqPage="join"`·`reqChnl=channel` 추가.
  - `middleware.ts`(POST /page/join/policy): `hp_join_auth` 쿠키에 `reqPage`·`reqChnl` 도 저장.
  - `policy/page.tsx`: 쿠키에서 읽어 `POST /api/join/policy` 바디에 `reqPage`·`reqChnl` 포함.
  - 백엔드: 이미 `params.get("reqChnl/reqPage")` 읽어 result 에 echo(noneAuth·성공 모두) → **로직 변경 없음**, 주석 `"pc"|"mobile"`→`"pc"|"mo"` 정정만.
  - 파라미터 흐름: form POST(authInfo,reqPath,**reqPage,reqChnl**)→쿠키→policy→`/api/join/policy`→result echo. 프론트 tsc 0 / 백엔드 compile 0.
  - ※ cert 팝업 요청의 `reqChnl`(현 `"NONE"`)은 이번 범위 밖으로 미변경(추후 확인). 브랜드/파바앱 미포함.
- **본인인증 성공 → policy form POST 전환 (2026-07-30)**: 기존 `join-auth.tsx` 인증성공 처리가 `sessionStorage.setItem("hp_cert_result") + router.push(GET)` 였음 → **RSC policy 는 sessionStorage 를 못 읽어 authInfo 전달 안 되는 갭**이 있었음. **동적 `<form method=POST action=/page/join/policy>` 생성해 hidden `authInfo`(=data.authInfo)·`reqPath` 담아 submit** 로 변경. 미들웨어 POST 핸들러가 이를 가로채 `hp_join_auth` 쿠키(authInfo/reqPath)로 저장→303 GET→policy(RSC)가 쿠키의 authInfo 를 `/api/join/policy` 로 전달. 미사용된 `useRouter`/`hp_cert_result`(아무 데서도 안 읽힘) 제거, useEffect deps 정리. `tsc --noEmit` 0.
### 🔧 후속 — OPBS(브랜드앱) 리다이렉트 전수 복원 (2026-07-30)
- **전수조사**: OPBS 리다이렉트 = `RedirectUtil.sendPbAppRedirect()` 단일 유틸의 **6 브랜치**(호출 7곳). 일반 회원화면→브랜드 회원화면 바운스 용도.
  | 진입 URL(.spc) | OPBS 목적지(브랜드) | 파라미터 |
  |---|---|---|
  | /page/join/auth.spc | /page/brand/member/join-auth.spc | instCd,as,ad |
  | /page/dormancy/auth-form.spc | /page/brand/member/dormancy-auth.spc | instCd |
  | /page/member-info/find-id-pw-form.spc | /page/brand/member/find-auth.spc | instCd |
  | /page/member-info/modify-info-form.spc | /page/brand/member/modify-info-view.spc | instCd,encAut |
  | /page/member-info/change-pw-form.spc | /page/brand/member/modify-pw-view.spc | instCd,encAut |
  | /page/member-info/withdrawal-form.spc | /page/brand/member/withdrawal-view.spc | instCd,encAut |
- **결정적 발견 2**: ① 모델API 계층은 requestURI 가 `/api/...` 라 `sendPbAppRedirect`의 `.spc` 매칭이 **절대 성립 안 됨** → 이식됐다던 #4(modify-info-form)의 OPBS 분기도 **死코드**였음(6개 전부 신규스택에서 미작동). ② 프론트에 브랜드 회원 라우트(`app/(site)/page/brand/member/*`)가 **미존재**(백엔드 `BrandMemberModelApiResource`만 있음).
- **조치(미들웨어 이관)**: `sendPbAppRedirect`는 DB·세션 없는 순수 URL 매핑이므로 프론트 **엣지 미들웨어**로 이관.
  - `middleware.ts`: `OPBS_REDIRECT_MAP`(6매핑) + `LEGACY_BASE` 추가. 진입 `.spc` + `instCd===OPBS` 면 `${LEGACY_BASE}/page/brand/member/<target>.spc?<원본쿼리>` 로 **절대경로 리다이렉트**(브랜드 프론트 라우트 미존재 → 현재도 동작하는 레거시 백엔드 JSP로 복원). join/auth.spc 는 통합 rewrite보다 **먼저** 판별.
  - `MemberInfoModelApiResource`: #4의 inert `sendPbAppRedirect` 호출·import 제거(주석으로 미들웨어 이관 명시). 레거시 `RedirectUtil`·컨트롤러는 그대로 유지.
  - 검증: 백엔드 `mvn compile` OK / 프론트 `tsc --noEmit` 0.
- **잔여 TODO**: 브랜드 회원 프론트 라우트 6개 마련되면 `OPBS_REDIRECT_MAP` 목적지를 내부 라우트로 교체(현재는 레거시 백엔드 절대경로). → **D 클러스터로 라우트는 마련됨**(아래). 실동작 테스트 후 내부 라우트 전환 여부 결정.

### ✅ D — 브랜드 회원 프론트 라우트 클러스터 (22/22, 2026-07-30)
- 배경: `app/(site)/page/brand/member/*` 프론트 라우트가 **전무**(백엔드 모델API 23개 + 계약 23개는 존재). 사용자 지시로 전체 구축.
- **공통 기반**: `lib/legacy-http.ts`에 **`legacyContractPost`** 신규 추가(form-urlencoded 바디 + 쿠키 포워딩, `legacyContractGet` 대칭). GET=Get/POST=Post 헬퍼로 통일.
- **22개 라우트**(각 page.tsx+error.tsx, 필요시 not-found) + **22개 api-lib** 생성. `donation/intro`(GET)·`reception-agree`(인증 쿠키) 패턴 준수, 계약 UI 메모 반영.
  - join: join-gate, join-auth, join-policy, join-view, join-optional, join-complete
  - dormancy: dormancy-auth, dormancy-view, dormancy-complete
  - find: find-auth, find-view, find-complete
  - confirm: confirm-view, confirm-ownership-form, confirm-ownership-proc, confirm-complete(리다이렉트 전용)
  - modify-info: modify-info-view, modify-info-complete / modify-pw: modify-pw-view, modify-pw-complete
  - withdrawal: withdrawal-view, withdrawal-complete
  - ※ `brand-attr`는 계약·화면 없는 내부 헬퍼 엔드포인트 → 페이지 라우트 아님(23−1=22).
- **엔드포인트 정합성**: 계약 `[API]`의 `/api/page/brand/member/...` 표기 오류 → **전부 실제 백엔드 `/api/brand/member/...`로 교정 확인**(22개 lib 전수 grep). 인증 필요 흐름은 `forwardCookies:true`(instCd/encAut/JSESSIONID).
- **작업 방식**: 서브에이전트 4그룹 병렬 착수 → 세션 한도로 중단(6 page + 일부 error 누락). **누락분(join-complete/find-complete/confirm-complete/modify-info-view/modify-info-complete/withdrawal-complete page + error 7종)은 직접 완성.**
- 검증: 프론트 `npx tsc --noEmit` **에러 0**(신규 44파일 포함 전체).

### 🔧 후속 — 로그인 체크 요청당 1회·일관성 보장 (2026-07-30)
- 문제: `getCurrentUser()`(→`POST /api/auth/check`)가 `cache()` 미적용이라, **루트 레이아웃 + 페이지가 각각 독립 fetch**. mypage/reception-agree 등은 요청당 2회 호출 + **두 결과가 어긋나면(타임아웃/세션변경) 레이아웃과 본문이 서로 다른 로그인 상태로 렌더**될 위험.
- 조치: `lib/auth-server.ts` `getCurrentUser` 를 **React `cache()`** 로 래핑. 같은 요청 내 모든 호출이 최초 1회 결과 공유 → **단일 로그인 상태(일관성)** + 요청당 fetch 1회. 새로고침·이동은 새 요청이라 매번 새로 1회(정상). 호출부 변경 없음. `tsc --noEmit` 0.
- ※ 목적은 절약이 아니라 **일관성**(동일 구조의 로그인 필요 페이지에서 체크 결과로 페이지 정보가 달라지지 않도록). 회원가입 흐름은 체크 불필요라 무관.

### 🔧 후속 — 모델API 체크 + 프론트 계약(interface) 현행화 (2026-07-30)
- **모델API 체크**: `mvn compile` 통과, 모델API 114 엔드포인트. 문제 없음.
- **계약 드리프트 스캔**(백엔드 엔드포인트 ↔ interface/lib 참조 대조):
  - **갭B 수정완료**: 계약 `[API]` 주석이 `/api/page/...`로 stale → 실제 백엔드 `/api/...`로 일괄 교정. 브랜드회원 22 계약(`/api/page/brand/member/`→`/api/brand/member/`) + email(reject/unsubscribe) + reception-agree(+proc) + survey/coretype + live/grip-live-show + presentation/membership + `event/sleeveQr`→`sleeve-qr`. **api-lib은 이미 정경로(D클러스터) — 계약 주석만 stale이었음.** cert(`/api/page/cert`는 실경로)는 미변경. grep 0건 / `tsc` 0.
  - **join/policy 계약 현행화**: 요청에 `reqPage`/`reqChnl` 추가, 응답 필드명 `landingType`→`alertType`(백엔드 실제), `reqPage`/`reqChnl` echo 추가, 랜딩 대상 `/page/join/popup`→`/page/common/alert` 반영, 백엔드 표기 `JoinController`→`JoinModelApiResource`. (문서 전용 계약 — import처 없음 확인)
  - **갭A 완료(계약 신규 작성 21개)**: 백엔드 응답(`res.put` 키)을 그대로 미러링해 도메인별 신규 계약 작성(서브에이전트 4그룹 병렬). 실제 경로 `/api/...` 사용, 전 파일 `tsc --noEmit` 0.
    - customer: qna/voc/term (암호화 cust 파라미터 + action/isList/no)
    - live: secta9ine/live-show/secta9ine-live-show (stage 게이트 landing/redirectTo + liveInfo/deepSeq/sessionKey)
    - alliance: culture/gate-check/agree-proc (landing/landingType + W_* 파라미터 + login-required 분기)
    - mypage-card: index(→password redirect)/register (인증 게이트 401)
    - join: temp-id-app 신규 / *policy-term 은 기존 `policyTerm.ts` 존재로 스킵*
    - cert-NICE: nice/phone/fail·phone-order/fail(license)·ipin/process
    - event: ai-jukebox(data)/event-proc(eventseq/tableNm/…/importView)
    - sleeveqr: qr-banner-count(success) → `interface/event/qr-banner-count.ts`
    - email: unsubscribe / reception: reception-agree-proc / survey: coretype-error
    - 참조 경로 전수 대조: 신규 계약 21개 전부 백엔드 엔드포인트와 **일치(불일치 0)**.
    - ✅ 정리완료: `interface/page/email/reject.ts` 의 구 `EmailUnsubscribeRequest/Response` 선언 제거 → 정본은 신규 `interface/page/email/unsubscribe.ts`(success/fail union). reject.ts 는 GET reject 전용으로 정리, [API] 주석에 unsubscribe 계약 위치 명시. `tsc` 0.

## 검증
- 각 flow 이식 후 `mvn compile` 통과 유지(현재 BACKEND OK).
- 빌드/배포·실동작 테스트는 dominic 직접.

## TODO (잔여)
- 빌드/배포·실동작 통합 테스트(dominic 직접): B POST 액션(unsubscribe/agree-proc/qr-banner-count 등) 실연동, C 9라우트 SSR 렌더
- 쿠키/토큰 브리지(미들웨어) 실연동 시 landingType↔프론트 화면 매핑 확정
- 선행 이슈: `join/index/page.tsx` `reqPath` prop 타입에러(본 이관과 무관, 별도 처리 필요)
- 계약(interface) 정합화: B POST 액션들 계약 문서 추가(현재 백엔드 응답 landing/redirectTo 기준)
