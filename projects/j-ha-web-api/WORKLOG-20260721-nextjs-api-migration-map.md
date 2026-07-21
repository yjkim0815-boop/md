---
문서유형: WORKLOG
프로젝트: j-ha-web-api
이슈키: --
작성일: 2026-07-21
최종수정: 2026-07-21
작성자: dominic
상태: 진행중
요약: JSP(ModelAndView) 페이지를 Next.js(happypoint-web2)로 이관하기 위한 "분리 대상 페이지 URL ↔ 필요 API" 매핑 인벤토리
---

# 🔀 Next.js 이관 매핑 — 페이지 URL ↔ API 인벤토리

> **목표**: 이 프로젝트(Spring MVC + JSP)의 서버렌더링 페이지(ModelAndView)를 프론트 `D:\200_DEV\230_WORKSPACE\happypointcard\happypoint-web2`(Next.js)로 이관.
> 이관하려면 각 페이지가 뷰에 넣던 Model 데이터를 **JSON API로 노출**해야 한다. 이 문서는 페이지별로 (a) 현재 URL, (b) 넣던 데이터, (c) 매칭되는 기존 `/api`, (d) 신규로 만들어야 할 API 를 정리한다.

## 아키텍처 현황 (분리 기준)
- **페이지 컨트롤러**: `@Controller`, base `/page/**`(+`.spc`), JSP 뷰 + Model 반환 → **이관 대상**
- **REST**: `@RestController`, base `/api/**` → 이미 JSON. 액션(POST) 위주로 존재, **조회(GET)는 부족**
- **디바이스 분기**: 대부분 `pc/*` vs `mobile/*` 뷰를 코드로 분기 → Next.js에선 반응형/단일 컴포넌트로 통합(뷰 분기 불필요)
- **핵심 격차**: 기존 `/api`는 대부분 **쓰기/검증(join, cert, sms, card 액션)** 위주. **목록/상세 조회(main/notice/faq/event/store/donation/mypoint)** 는 페이지 컨트롤러가 직접 서비스 호출 → **신규 조회 API 대량 필요**.

범례: ✅=기존 API 재사용 / 🆕=신규 API 필요 / 🔁=리다이렉트·서버로직(프론트 라우팅으로 대체) / 🔒=로그인 필요

---

## 1. 메인 / 매장 / 제휴 (공개 페이지, 조회 API 신규 필요)

| 페이지 URL | 넣던 데이터 | 기존 API | 신규 필요 API |
|---|---|---|---|
| `GET /page/main/index.spc` | noticeList, mainBlogList, bannerList, allianceList, latest | — | 🆕 `GET /api/main` (또는 분리: `/api/notice/main`, `/api/main/blog`, `/api/banner`, `/api/alliance/corp`) |
| `GET /page/store/search.spc` | storeList (brandCode/metro/city 필터) | — | 🆕 `GET /api/store/search?brandCode&metro&city` |
| `GET /page/store/city-more.spc` | cityList | — | 🆕 `GET /api/store/city?metro&cityName` |
| `GET /page/alliance/card.spc` | cardList (category/cardCorporation) | — | 🆕 `GET /api/alliance/card?category&corp` |
| `GET /page/alliance/corporation.spc` | corpList (category/onOff), spcids | — | 🆕 `GET /api/alliance/corp?category&onOff` |
| `GET /page/alliance/culture.spc` | (정적) | — | 🔁 정적 페이지 (API 불요) |
| `POST /page/alliance/agree` | 팝업용 파라미터 에코(JSON) | — | 🔁 프론트에서 처리 or 🆕 경량 API |
| `.../alliance/gate-check.spc`, `agree-proc.spc` | 제휴몰 게이트/리다이렉트 | ✅ `oil-bank-*` 유사 | 🔁 리다이렉트 로직 재설계(SSR route 또는 🆕 `POST /api/alliance/gate`) |

## 2. 나눔/기부 (donation, 전부 조회 → 신규 필요)

| 페이지 URL | 넣던 데이터 | 신규 필요 API |
|---|---|---|
| `GET /page/donation/intro.spc` (+`-more`) | contributionList | 🆕 `GET /api/donation/contribution?page` |
| `GET /page/donation/happyBirthDay.spc` | thisMonthArea, rankingList, month/year | 🆕 `GET /api/donation/happy-birthday` |
| `GET /page/donation/voteList.spc` (+`-more`) | centerList, happyMonth, ctSort | 🆕 `GET /api/donation/vote?sort&page` |
| `GET /page/donation/voteView.spc` | centerDetail, commentList, reCnt, isValidDate | 🆕 `GET /api/donation/vote/{seq}` + 댓글 ✅`/api/donation/saveNanumComment` 등 존재 |
| `GET /page/donation/winnerList.spc` | winnerList | 🆕 `GET /api/donation/winner?page` |
| `GET /page/donation/winnerView.spc` | winnerDetail | 🆕 `GET /api/donation/winner/{seq}` |

> 기부 액션 API는 존재: ✅ `/api/donation/saveNanumComment`, `/removeNanumRecommend`, `/saveNanumRecommend`, `/winnerUserInfo`

## 3. 이벤트 (event)

| 페이지 URL | 넣던 데이터 | 기존 API | 신규 필요 API |
|---|---|---|---|
| `GET /page/event/event-list.spc` (+`-more`) | eventList, categoryList | — | 🆕 `GET /api/event?category&page` |
| `GET /page/event/event-view.spc` | result(이벤트 상세), userInfo, testUser | — | 🆕 `GET /api/event/{eventseq}` |
| `GET /page/event/winner-list.spc` (+`-more`) | eventList(당첨) | ✅ `/api/event/win-check`(개인) | 🆕 `GET /api/event/prize?page` (목록) |
| `GET /page/event/winner-view.spc` | event(당첨상세), imgUrl | — | 🆕 `GET /api/event/prize/{prizeSeq}` |
| `GET /page/mypage/event/event-my-list.spc` 🔒 (+`-more`) | eventList(내 당첨) | ✅ `/api/event/win-check` | 🆕 `GET /api/user/event-win?page` |
| `GET /page/event/coupon-info.spc` | addDownLoad(플랫폼별 URL) | — | 🔁 정적/프론트 UA 분기 |
| `GET /page/event/ai-jukebox.spc` | data(KMS 복호화) | — | 🆕 필요시 복호화 API |
| `GET /event/eventProc.spc` | 이벤트 홈 프록시(S3) | — | 🆕 SSR/프록시 재설계 |
| SNS 공유 로그 | — | ✅ `/api/event/event-share-log` | — |

## 4. 고객센터 (customer)

| 페이지 URL | 넣던 데이터 | 신규 필요 API |
|---|---|---|
| `GET /page/customer/faq.spc` (+`-more`) | faqList (category/text 검색) | 🆕 `GET /api/customer/faq?category&q&page` |
| `GET /page/customer/notice-list.spc` (+`-more`) | noticeList | 🆕 `GET /api/customer/notice?page` |
| `GET /page/customer/notice-view.spc` | notice(상세) + 조회수증가 | 🆕 `GET /api/customer/notice/{seq}` |
| `GET /page/customer/term.spc` / `/term` | 약관 뷰(pre별) | 🆕 `GET /api/customer/term?pre` (또는 정적) |
| `GET /page/customer/qna.spc` 🔒 / `voc.spc` | 외부 API(MB2200H0) 결과 + 사용자정보 | 🆕 `GET /api/customer/qna`(외부연계 래핑) |

> ✅ 긴급공지: `/api/emergency/notice` 존재

## 5. 마이페이지 - 포인트/카드 (🔒 로그인)

| 페이지 URL | 넣던 데이터 | 기존 API | 신규 필요 API |
|---|---|---|---|
| `GET /page/mypage/my-point.spc` (+`-more`) | totalPoint, exPoint, pointHistory, champion | ✅ `/api/user/point`(잔액만) | 🆕 `GET /api/user/point-history?div&start&end&month&page` + champion |
| `GET /page/mypage/donation-point.spc` | donation, cardList, pointHistory(year) | ✅ `/api/card/my-card` | 🆕 `GET /api/user/donation-point?year` |
| `GET /page/mypage/card/password.spc` | hasPassword, hasCard | ✅ `/api/card/*`(set/reset/clear password) | 🆕 `GET /api/card/password-status` |
| `GET /page/mypage/card/register.spc` | (폼) | ✅ `POST /api/card/register` | — |
| `GET /page/mypage/card/reissue.spc` | cardList, memberInfo(마스킹) | ✅ `/api/card/my-card`, `POST /api/card/reissue` | 🆕 `GET /api/member-info/summary`(마스킹 정보) |
| `GET /page/mypage/card/reissue-status.spc` | state(신청/대기/완료), result | — | 🆕 `GET /api/card/reissue-status` |
| `GET /page/mypage/card/platinum.spc` | memberInfo, 발급기간 | ✅ `POST /api/card/issue-platinum` | 🆕 `GET /api/card/platinum-status` |
| `GET /page/mypage/card/platinum-status.spc` | state, result | — | 🆕 `GET /api/card/platinum-status` |

## 6. 회원 - 가입/찾기/정보수정/탈퇴/휴면 (member-info, join, dormancy)
> 이 도메인은 **액션 API가 이미 상당수 존재**. 페이지는 대부분 "인증→폼→처리→완료" 다단계라 **화면 흐름은 Next.js 라우팅**, 각 단계 데이터/처리는 아래 API로.

| 페이지 흐름 | 기존 API (재사용) | 신규 필요 API |
|---|---|---|
| 가입 `/page/join/*` (index/policy/form/optional/welcome) | ✅ `/api/join/check-id`, `/check-email`, `POST /api/join/joinProc` | 🆕 약관/정책 조회 `GET /api/join/policy`, 단계 상태 관리(프론트) |
| ID/PW 찾기 `/page/member-info/find-id-pw-*` | ✅ `/api/member-info/check-name`, `/parse-phone` | 🆕 `POST /api/member-info/find-id`, `/reset-pw` |
| 정보수정 `/page/member-info/modify-info-*` | ✅ `/api/member-info/chg-phone` | 🆕 `GET /api/member-info/detail`, `POST /api/member-info/modify` |
| 비번변경 `/page/member-info/change-pw-*` | ✅ `POST /api/user/change-pw` | — |
| 탈퇴 `/page/member-info/withdrawal-*` | — | 🆕 `GET /api/member-info/withdrawal-info`(point/couponCnt), `POST /api/member-info/withdrawal` |
| 이메일변경 `/page/member-info/change-email-*` | ✅ `/api/member-info/*` | 🆕 `POST /api/member-info/change-email` |
| 본인확인(소유권) `confirm-*` | ✅ `/api/sms/send-ownership`, `/check-ownership`, `/verify-ownership` | 🆕 `GET /api/member-info/ownership-status`(마스킹번호/차단여부) |
| 휴면해제 `/page/dormancy/*` | — | 🆕 `GET /api/dormancy/info`, `POST /api/dormancy/release` (또는 ✅`/api/dormancy` 확장) |

## 7. 브랜드 회원 (brand/member — instCd별 멀티브랜드)
> 위 6번과 동일 흐름의 **브랜드 버전**. 뷰가 `jspPath(instCd)`로 브랜드별 분기 → Next.js에선 `instCd` 파라미터 라우팅.

| 흐름 | 기존 API | 신규 필요 API |
|---|---|---|
| 가입 gate/auth/policy/view/optional/complete | ✅ `/api/brand/member/check-id`, `/check-email`, `POST /join-proc` | 🆕 브랜드별 약관/URL맵 `GET /api/brand/member/config?instCd` |
| 비번변경 | ✅ `POST /api/brand/member/change-pw` | — |
| 이름/휴대폰 변경 | ✅ `/api/brand/member/check-name`, `/chg-phone` | — |
| 찾기/휴면/탈퇴/정보수정/본인확인 | (공통 user/sms API 일부 재사용) | 🆕 6번과 동일 항목의 brand 변형 |

## 8. 인증 (cert — 본인인증 벤더 연동)
> KCB/NICE 벤더 SDK 연동. 콜백/완료 페이지가 벤더에서 리다이렉트로 진입 → **프론트 콜백 라우트 + 결과 조회 API**로 재구성.

| 페이지 | 데이터 | 신규 필요 API |
|---|---|---|
| `/page/cert/phone/request.spc`, `/ipin/request.spc` | certProps, certMap(벤더 라이선스) | 🆕 `GET /api/cert/init?type=phone|ipin` |
| `.../nice|kcb/phone|ipin/complete.spc` | RSLT_CD, authInfo, pInfo | 🆕 `POST /api/cert/complete`(벤더 결과 파싱) |
| `.../fail.spc` | certMap | 🔁 프론트 실패 라우트 |
> ✅ SMS 인증: `/api/cert/request-auth-number`, `/confirm-auth-number` 존재

## 9. 기타 (presentation / live / survey / sleeveQr)

| 페이지 | 데이터 | 신규 필요 API |
|---|---|---|
| `/page/presentation/*` (point/brand/membership/card/app) | 대부분 정적, membership만 champion | 🔁 정적 페이지 / champion은 ✅`/api/user/point` 확장 |
| `/page/live/*` (grip/secta9ine live show) | liveInfo(S3 JSON), liveKey | 🆕 `GET /api/live/{liveKey}` |
| `/page/survey/coretype.spc` | coreTypeInfo, encCtNo(토큰) | 🆕 `GET /api/survey/coretype?ctData` (✅ check-barcode/progress/complete 존재) |
| `/event/sleeveQr.spc` | bannerList, brandInfo | 🆕 `GET /api/sleeve-qr?brandCd` (✅ 카운트: qrBannerCountUpdate) |
| `/page/email/reject.spc`, `unsubscribe.spc` | 수신거부 | 🆕 `POST /api/email/unsubscribe` |
| `/page/reception-agree*.spc` 🔒 | receptionAgree | 🆕 `GET/POST /api/reception-agree` |

## 10. 이관 불필요 / 프론트 대체 (redirect·error·정적)
- `PageController` 전체(`/`, `/page`, `/m/*` → main 리다이렉트) → 🔁 Next.js 라우팅으로 대체
- `ErrorController`(400/403/404/405/500/503) → 🔁 Next.js error/not-found 페이지
- `MyCardController` `/page/mypage/card` → password 리다이렉트 → 🔁 프론트 가드

---

## 요약 통계 & 우선순위
- **분리 대상 페이지 컨트롤러**: 28개(≈97개 매핑). 이 중 순수 리다이렉트/에러 ~20개는 프론트 라우팅으로 대체.
- **기존 재사용 가능 API(/api)**: 약 50개 — 대부분 **쓰기/검증**(join, card, sms, cert, user, brand, donation 액션).
- **신규로 만들어야 할 API**: 주로 **조회(GET)** — main, store, alliance, donation(6), event(5), customer(4), mypoint(3), card-status(3), live, survey, sleeveQr, member-info 상세/탈퇴정보 등 **약 30~35개**.

### 권장 착수 순서 (의존도·트래픽 기준)
1. **공개 조회 페이지 우선**(로그인 불요, API 단순): main, notice, faq, event-list/view, store, alliance, donation → 신규 GET API 위주, 이관 리스크 최소.
2. **마이페이지 조회**(🔒): point-history, card-status, member-info detail.
3. **다단계 인증 흐름**(가입/찾기/수정/탈퇴/휴면/cert/brand): 액션 API는 있으니 **흐름 상태관리 + 부족한 조회/처리 API 보강**. 벤더 인증(cert) 콜백 재설계가 가장 까다로움.

### 미결정/확인 필요
- 인증/세션 방식: 현재 세션+쿠키(`_AUTH_INFO_TOKEN_`, `_MEMBER_CONFIRMED_` 등). Next.js 분리 시 **토큰(JWT/세션) 전략** 결정 필요.
- 본인인증 벤더(NICE/KCB) 콜백 URL이 서버 페이지로 리다이렉트됨 → 프론트 도메인 콜백 허용 여부(벤더 등록) 확인.
- `siteCtx()`/디바이스 분기 제거 → 반응형 단일 UI로 통합 전제.
