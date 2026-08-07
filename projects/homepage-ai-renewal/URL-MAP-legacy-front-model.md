---
문서유형: REFERENCE
프로젝트: homepage-ai-renewal (태스크)
관련프로젝트: happypoint-web2, ha-web-api, ha_web(레거시)
작성일: 2026-08-06
최종수정: 2026-08-06
작성자: dominic
상태: 진행중
요약: 레거시(ha-web) 페이지 URL ↔ rewrite 상태 ↔ 현재 프론트(happypoint-web2) URL ↔ 모델 API(ha-web-api) 4열 매핑표. Confluence 페이지(https://secta9ine.atlassian.net/wiki/x/AQDZgw) 게시용 정본 — Claude Code 앱에서 MCP(Atlassian) 연결해 이 표를 발행/수정 예정.
---

# 🔗 레거시 ↔ 프론트 ↔ 모델API URL 매핑표

> **목적**: 레거시 URL 전량 기준으로 rewrite 상태·현재 프론트 URL·모델 API 를 한눈에.
> **Confluence 게시 대상**: https://secta9ine.atlassian.net/wiki/x/AQDZgw (MCP 연결 후 이 표를 발행/수정)
> **수집(2026-08-06)**: ha-web 레거시 컨트롤러 ~144 URL · j-ha-web-api 모델 API 119 · happypoint-web2 현재 라우트 87 (3개 저장소 병렬 스캔).

## 범례 — 상태(status)
| 값 | 의미 |
|---|---|
| (빈칸) | `.spc` 만 제거하고 경로 동일 (단순 rewrite) |
| `rewrite` | 경로가 바뀌는 내부 재작성(통합/브랜드/브리지/미이관 대상 등) |
| `변경` | 경로 자체가 다르게 바뀜(예: main → `/`) |
| `에러` | 에러 페이지 |
| `삭제` | 프론트·모델 API 삭제됨(2026-08-06) |
| `신규` | 레거시에 없는 신규 URL |

> OPBS = 파바앱(instCd=OPBS) 특례 rewrite. `(미이관)` = 모델 API 는 있으나 프론트 화면 미구축. `(bridge)` = POST→GET 브리지 경유.

## 매핑표

| No | 레거시 URL | 상태 | 현재 URL | 모델 API |
|---|---|---|---|---|
| 1 | `/page/main/index.spc` | 변경 | `/` · `/mobile` | `/api/main` |
| 2 | `/error/{400,403,404,500,503}.spc` | 에러 | `/page/error` · `50x.html` | — |
| 3 | `/page/join` | rewrite | `/page/join/index` (OPBS:`/page/brand/join/index`) | `/api/join/index` |
| 4 | `/page/join/auth.spc` | rewrite | `/page/join/index` (OPBS:`/page/brand/join/index`) | `/api/join/index` |
| 5 | `/page/join/index.spc` | rewrite | `/page/join/index` (OPBS:`/page/brand/join/index`) | `/api/join/index` |
| 6 | `/page/join/policy.spc` |  | `/page/join/policy` | `POST /api/join/policy` |
| 7 | `/page/join/form.spc` |  | `/page/join/form` | `/api/join/form` |
| 8 | `/page/join/optional-form.spc` |  | `/page/join/optional-form` | `/api/join/optional-form` |
| 9 | `/page/join/welcome.spc` |  | `/page/join/welcome` | `/api/join/welcome` |
| 10 | `/page/join/policyTerm.spc` | rewrite | (policy 통합) | `/api/join/policy-term` |
| 11 | `/page/notice/temp-id-app.spc` |  | `/page/notice/temp-id-app` | `/api/join/temp-id-app` |
| 12 | `/page/member-info/index.spc` |  | `/page/member-info/index` | `/api/member-info/index` |
| 13 | `/page/member-info/indexForWithdrawal.spc` | rewrite | (index 통합) | `/api/member-info/index-for-withdrawal` |
| 14 | `/page/member-info/find-id-pw-form.spc` | rewrite | `/page/member-info/find-id-pw-form` (OPBS:`/page/brand/member-info/find-id-pw-form`) | `/api/member-info/find-id-pw-form` |
| 15 | `/page/member-info/find-id-pw-process.spc` |  | `/page/member-info/find-id-pw-process` | `POST /api/member-info/find-id-pw-process` |
| 16 | `/page/member-info/find-id-pw-complete.spc` |  | `/page/member-info/find-id-pw-complete` | `POST /api/member-info/find-id-pw-complete` |
| 17 | `/page/member-info/confirm-pw-form.spc` |  | `/page/member-info/confirm-pw-form` | `/api/member-info/confirm-pw-form` |
| 18 | `/page/member-info/confirm-pw-process.spc` | rewrite | (bridge) | `POST /api/member-info/confirm-pw-process` |
| 19 | `/page/member-info/confirm-ownership-form.spc` | rewrite | (일반 미이관) | `/api/member-info/confirm-ownership-form` |
| 20 | `/page/member-info/confirm-ownership-proc.spc` | rewrite | (bridge) | `POST /api/member-info/confirm-ownership-proc` |
| 21 | `/page/member-info/modify-info-form.spc` | rewrite | `/page/member-info/modify-info-form` (OPBS:`/page/brand/member/modify-info-view`) | `POST /api/member-info/modify-info-form` |
| 22 | `/page/member-info/modify-info-process.spc` | rewrite | (bridge) | `POST /api/member-info/modify-info-process` |
| 23 | `/page/member-info/change-pw-form.spc` | rewrite | `/page/member-info/change-pw-form` (OPBS:`/page/brand/member/modify-pw-view`) | `/api/member-info/change-pw-form` |
| 24 | `/page/member-info/change-pw-process.spc` | rewrite | (bridge) | `POST /api/member-info/change-pw-process` |
| 25 | `/page/member-info/withdrawal-form.spc` | rewrite | `/page/member-info/withdrawal-form` (OPBS:`/page/brand/member/withdrawal-view`) | `/api/member-info/withdrawal-form` |
| 26 | `/page/member-info/withdrawal-process.spc` | rewrite | (bridge) | `POST /api/member-info/withdrawal-process` |
| 27 | `/page/member-info/change-email-form.spc` | rewrite | (미이관) | `/api/member-info/change-email-{form,process,complete}` |
| 28 | `/page/dormancy/auth-form.spc` | rewrite | `/page/dormancy/auth-form` (OPBS:`/page/brand/member/dormancy-auth`) | `/api/dormancy/auth-form` |
| 29 | `/page/dormancy/auth-process.spc` | rewrite | `/page/dormancy/dormancy-view` (bridge) | `POST /api/dormancy/auth-process` |
| 30 | `/page/dormancy/dormancy-process.spc` | rewrite | `/page/dormancy/dormancy-complete` | `POST /api/dormancy/dormancy-process` · `/api/dormancy/status` |
| 31 | `/page/customer/faq.spc` (+`-more`) |  | `/page/customer/faq` | `/api/customer/faq` |
| 32 | `/page/customer/notice-list.spc` (+`-more`) |  | `/page/customer/notice-list` | `/api/customer/notice-list` |
| 33 | `/page/customer/notice-view.spc` |  | `/page/customer/notice-view` | `/api/customer/notice-view` |
| 34 | `/page/customer/qna.spc` |  | `/page/customer/qna` | `/api/customer/qna` |
| 35 | `/page/customer/term.spc` |  | `/page/customer/term` | `/api/customer/term` |
| 36 | `/page/customer/voc.spc` | rewrite | (미이관) | `/api/customer/voc` |
| 37 | `/page/store/search.spc` |  | `/page/store/search` | `/api/store/search` |
| 38 | `/page/store/city-more.spc` |  | `/page/store/city-more` | `/api/store/city` |
| 39 | `/page/alliance/card.spc` |  | `/page/alliance/card` | `/api/alliance/card` |
| 40 | `/page/alliance/corporation.spc` |  | `/page/alliance/corporation` | `/api/alliance/corporation` |
| 41 | `/page/alliance/culture.spc` | rewrite | (미이관) | `/api/alliance/culture` |
| 42 | `/page/alliance/gate-check.spc` | rewrite | (미이관) | `/api/alliance/gate-check` |
| 43 | `/page/alliance/agree-proc.spc` | rewrite | (미이관) | `/api/alliance/agree-proc` |
| 44 | `/page/mypage/card/register.spc` |  | `/page/mypage/card/register` | `/api/mypage/card/register` |
| 45 | `/page/mypage/card/password.spc` |  | `/page/mypage/card/password` | `/api/mypage/card/password` |
| 46 | `/page/mypage/card/reissue.spc` |  | `/page/mypage/card/reissue` | `/api/mypage/card/reissue` |
| 47 | `/page/mypage/card/reissue-status.spc` |  | `/page/mypage/card/reissue-status` | `/api/mypage/card/reissue-status` |
| 48 | `/page/mypage/card/platinum.spc` | rewrite | (미이관) | `/api/mypage/card/platinum` |
| 49 | `/page/mypage/card/platinum-status.spc` | rewrite | (미이관) | `/api/mypage/card/platinum-status` |
| 50 | `/page/mypage/my-point.spc` (+`-more`) |  | `/page/mypage/my-point` | `/api/mypage/my-point` |
| 51 | `/page/mypage/donation-point.spc` | rewrite | `/page/mypage/my-point/donation` | `/api/mypage/donation-point` |
| 52 | `/page/event/event-list.spc` (+`-more`) | 삭제 | 삭제 | 삭제 |
| 53 | `/page/event/coupon-info.spc` | 삭제 | 삭제 | 삭제 |
| 54 | `/page/event/event-view.spc` | rewrite | (미이관) | `/api/event/event-view` |
| 55 | `/page/event/ai-jukebox.spc` | rewrite | (미이관) | `/api/event/ai-jukebox` |
| 56 | `/event/eventProc.spc` | rewrite | (미이관) | `/api/event/event-proc` |
| 57 | `/page/event/winner-list.spc` (+`-more`) | rewrite | (미이관) | `/api/event/winner-list` |
| 58 | `/page/event/winner-view.spc` | rewrite | (미이관) | `/api/event/winner-view` |
| 59 | `/page/mypage/event/event-my-list.spc` (+`-more`) | rewrite | (미이관) | `/api/mypage/event/event-my-list` |
| 60 | `/page/donation/intro.spc` (+`-more`) |  | `/page/donation/intro` | `/api/donation/intro` |
| 61 | `/page/donation/happyBirthDay.spc` |  | `/page/donation/happyBirthDay` | `/api/donation/happy-birthday` |
| 62 | `/page/donation/voteList.spc` (+`-more`) |  | `/page/donation/voteList` | `/api/donation/vote-list` |
| 63 | `/page/donation/voteView.spc` |  | `/page/donation/voteView` | `/api/donation/vote-view` |
| 64 | `/page/donation/winnerList.spc` |  | `/page/donation/winnerList` | `/api/donation/winner-list` |
| 65 | `/page/donation/winnerView.spc` |  | `/page/donation/winnerView` | `/api/donation/winner-view` |
| 66 | `/page/presentation/point.spc` |  | `/page/presentation/point` | `/api/presentation/point` |
| 67 | `/page/presentation/brand.spc` |  | `/page/presentation/brand` | `/api/presentation/brand` |
| 68 | `/page/presentation/membership.spc` |  | `/page/presentation/membership` | `/api/presentation/membership` |
| 69 | `/page/presentation/card.spc` |  | `/page/presentation/card` | `/api/presentation/card` |
| 70 | `/page/presentation/app.spc` |  | `/page/presentation/app` | `/api/presentation/app` |
| 71 | `/page/cert/phone/request.spc` · `/ipin/request.spc` | rewrite | (백엔드 팝업) | `/api/cert/phone/request` · `/api/cert/ipin/request` |
| 72 | `/page/cert/phone/complete.spc` · `/ipin/complete.spc` | rewrite | (백엔드 팝업) | `/api/cert/phone/complete` · `/api/cert/ipin/complete` |
| 73 | `/page/cert/nice/...(6종)` | rewrite | (백엔드 팝업) | `/api/cert/nice/...` (6종) |
| 74 | `/page/email/reject.spc` |  | `/page/email/reject` | `/api/email/reject` |
| 75 | `/page/email/unsubscribe.spc` | rewrite | (bridge) | `POST /api/email/unsubscribe` |
| 76 | `/page/live/grip-live-show.spc` |  | `/page/live/grip-live-show` | `/api/live/grip-live-show` |
| 77 | `/page/live/secta9ine.spc` |  | `/page/live/secta9ine` (stg) | `/api/live/secta9ine` |
| 78 | `/page/live/live-show.spc` | rewrite | (미이관) | `/api/live/live-show` |
| 79 | `/page/live/secta9ine-live-show.spc` | rewrite | (미이관) | `/api/live/secta9ine-live-show` |
| 80 | `/page/reception-agree.spc` · `-proc.spc` |  | `/page/reception-agree` | `/api/reception-agree` · `-proc` |
| 81 | `/page/survey/coretype.spc` · `/error.spc` | rewrite | (미이관) | `/api/survey/coretype` · `/error` |
| 82 | `/page/brand/member/join-gate.spc` |  | `/page/brand/member/join-gate` | `/api/brand/member/join-gate` |
| 83 | `/page/brand/member/join-auth.spc` | rewrite | `/page/brand/join/index` | `/api/brand/join/index` |
| 84 | `/page/brand/member/join-policy.spc` | rewrite | `/page/brand/join/policy` | `POST /api/brand/join/policy` |
| 85 | `/page/brand/member/join-view.spc` | rewrite | `/page/brand/join/form` | `POST /api/brand/join/form` |
| 86 | `/page/brand/member/join-optional.spc` | rewrite | `/page/brand/join/optional-form` | `POST /api/brand/join/optional-form` |
| 87 | `/page/brand/member/join-complete.spc` | rewrite | `/page/brand/join/welcome` | `/api/brand/join/welcome` |
| 88 | `/page/brand/member/dormancy-{auth,view,complete}.spc` |  | `/page/brand/member/dormancy-{auth,view,complete}` | `/api/brand/member/dormancy-{auth,view,complete}` |
| 89 | `/page/brand/member/find-{auth,view,complete}.spc` | rewrite | `/page/brand/member-info/find-id-pw-{form,process,complete}` | `/api/brand/member-info/find-id-pw-{form,process,complete}` |
| 90 | (없음) | 신규 | `/page/auth/login` | `/api/auth/login` |
| 91 | (없음) | 신규 | `/page/join/popup` | — |
| 92 | (없음) | 신규 | `/page/search` | `/api/search` |
| 93 | (없음) | 신규 | `/page/common/alert` | — |
| 94 | (없음) | 신규 | `/page/brand/common/alert` | — |
| 95 | (없음) | 신규 | `/page/error` | — |
| 96 | (없음) | 신규 | `/page/mypage/inquiry` | — |
| 97 | (없음) | 신규 | `/page/about` | — |
| 98 | (없음) | 신규 | `/page/points` | — |
| 99 | (없음) | 신규 | `/page/services` | — |
| 100 | (없음) | 신규 | `/page/styleguide` (개발용) | — |
| 101 | (없음) | 신규 | `/event/sleeveQr` | `/api/sleeve-qr` |

## 미이관 (모델 API 有 · 프론트 화면 미구축)
change-email · confirm-ownership(일반) · voc · alliance(culture/gate-check/agree-proc) · mypage(platinum/platinum-status) · event(event-view/ai-jukebox/eventProc/winner-list/winner-view/event-my-list) · live(live-show/secta9ine-live-show) · survey(coretype/error)

## ⚠️ 미확정 / 후속
- 89·100(`/page/auth/login`·`/event/sleeveQr`)는 레거시 대응 화면 존재 가능성 있으나 ha-web 페이지 컨트롤러 스캔엔 미포착 → 잠정 `신규` 분류.
- 파바앱(OPBS) rewrite 정책은 별도 미완료(사용자 수정 예정) — `middleware.ts` `/page/join/index.spc` 매핑 재검토 대상.

---

## 📋 Confluence 붙여넣기용 CSV
Confluence 신편집기: 표 삽입 후 셀에 붙여넣기(자동 표 변환) 또는 "CSV 가져오기". Excel: 붙여넣기 → 텍스트 나누기(쉼표).

```csv
No,레거시 URL,상태,현재 URL,모델 API
1,/page/main/index.spc,변경,/ · /mobile,/api/main
2,"/error/{400,403,404,500,503}.spc",에러,/page/error · 50x.html,—
3,/page/join,rewrite,/page/join/index (OPBS:/page/brand/join/index),/api/join/index
4,/page/join/auth.spc,rewrite,/page/join/index (OPBS:/page/brand/join/index),/api/join/index
5,/page/join/index.spc,rewrite,/page/join/index (OPBS:/page/brand/join/index),/api/join/index
6,/page/join/policy.spc,,/page/join/policy,POST /api/join/policy
7,/page/join/form.spc,,/page/join/form,/api/join/form
8,/page/join/optional-form.spc,,/page/join/optional-form,/api/join/optional-form
9,/page/join/welcome.spc,,/page/join/welcome,/api/join/welcome
10,/page/join/policyTerm.spc,rewrite,(policy 통합),/api/join/policy-term
11,/page/notice/temp-id-app.spc,,/page/notice/temp-id-app,/api/join/temp-id-app
12,/page/member-info/index.spc,,/page/member-info/index,/api/member-info/index
13,/page/member-info/indexForWithdrawal.spc,rewrite,(index 통합),/api/member-info/index-for-withdrawal
14,/page/member-info/find-id-pw-form.spc,rewrite,/page/member-info/find-id-pw-form (OPBS:/page/brand/member-info/find-id-pw-form),/api/member-info/find-id-pw-form
15,/page/member-info/find-id-pw-process.spc,,/page/member-info/find-id-pw-process,POST /api/member-info/find-id-pw-process
16,/page/member-info/find-id-pw-complete.spc,,/page/member-info/find-id-pw-complete,POST /api/member-info/find-id-pw-complete
17,/page/member-info/confirm-pw-form.spc,,/page/member-info/confirm-pw-form,/api/member-info/confirm-pw-form
18,/page/member-info/confirm-pw-process.spc,rewrite,(bridge),POST /api/member-info/confirm-pw-process
19,/page/member-info/confirm-ownership-form.spc,rewrite,(일반 미이관),/api/member-info/confirm-ownership-form
20,/page/member-info/confirm-ownership-proc.spc,rewrite,(bridge),POST /api/member-info/confirm-ownership-proc
21,/page/member-info/modify-info-form.spc,rewrite,/page/member-info/modify-info-form (OPBS:/page/brand/member/modify-info-view),POST /api/member-info/modify-info-form
22,/page/member-info/modify-info-process.spc,rewrite,(bridge),POST /api/member-info/modify-info-process
23,/page/member-info/change-pw-form.spc,rewrite,/page/member-info/change-pw-form (OPBS:/page/brand/member/modify-pw-view),/api/member-info/change-pw-form
24,/page/member-info/change-pw-process.spc,rewrite,(bridge),POST /api/member-info/change-pw-process
25,/page/member-info/withdrawal-form.spc,rewrite,/page/member-info/withdrawal-form (OPBS:/page/brand/member/withdrawal-view),/api/member-info/withdrawal-form
26,/page/member-info/withdrawal-process.spc,rewrite,(bridge),POST /api/member-info/withdrawal-process
27,/page/member-info/change-email-form.spc,rewrite,(미이관),"/api/member-info/change-email-{form,process,complete}"
28,/page/dormancy/auth-form.spc,rewrite,/page/dormancy/auth-form (OPBS:/page/brand/member/dormancy-auth),/api/dormancy/auth-form
29,/page/dormancy/auth-process.spc,rewrite,/page/dormancy/dormancy-view (bridge),POST /api/dormancy/auth-process
30,/page/dormancy/dormancy-process.spc,rewrite,/page/dormancy/dormancy-complete,POST /api/dormancy/dormancy-process · /api/dormancy/status
31,/page/customer/faq.spc (+-more),,/page/customer/faq,/api/customer/faq
32,/page/customer/notice-list.spc (+-more),,/page/customer/notice-list,/api/customer/notice-list
33,/page/customer/notice-view.spc,,/page/customer/notice-view,/api/customer/notice-view
34,/page/customer/qna.spc,,/page/customer/qna,/api/customer/qna
35,/page/customer/term.spc,,/page/customer/term,/api/customer/term
36,/page/customer/voc.spc,rewrite,(미이관),/api/customer/voc
37,/page/store/search.spc,,/page/store/search,/api/store/search
38,/page/store/city-more.spc,,/page/store/city-more,/api/store/city
39,/page/alliance/card.spc,,/page/alliance/card,/api/alliance/card
40,/page/alliance/corporation.spc,,/page/alliance/corporation,/api/alliance/corporation
41,/page/alliance/culture.spc,rewrite,(미이관),/api/alliance/culture
42,/page/alliance/gate-check.spc,rewrite,(미이관),/api/alliance/gate-check
43,/page/alliance/agree-proc.spc,rewrite,(미이관),/api/alliance/agree-proc
44,/page/mypage/card/register.spc,,/page/mypage/card/register,/api/mypage/card/register
45,/page/mypage/card/password.spc,,/page/mypage/card/password,/api/mypage/card/password
46,/page/mypage/card/reissue.spc,,/page/mypage/card/reissue,/api/mypage/card/reissue
47,/page/mypage/card/reissue-status.spc,,/page/mypage/card/reissue-status,/api/mypage/card/reissue-status
48,/page/mypage/card/platinum.spc,rewrite,(미이관),/api/mypage/card/platinum
49,/page/mypage/card/platinum-status.spc,rewrite,(미이관),/api/mypage/card/platinum-status
50,/page/mypage/my-point.spc (+-more),,/page/mypage/my-point,/api/mypage/my-point
51,/page/mypage/donation-point.spc,rewrite,/page/mypage/my-point/donation,/api/mypage/donation-point
52,/page/event/event-list.spc (+-more),삭제,삭제,삭제
53,/page/event/coupon-info.spc,삭제,삭제,삭제
54,/page/event/event-view.spc,rewrite,(미이관),/api/event/event-view
55,/page/event/ai-jukebox.spc,rewrite,(미이관),/api/event/ai-jukebox
56,/event/eventProc.spc,rewrite,(미이관),/api/event/event-proc
57,/page/event/winner-list.spc (+-more),rewrite,(미이관),/api/event/winner-list
58,/page/event/winner-view.spc,rewrite,(미이관),/api/event/winner-view
59,/page/mypage/event/event-my-list.spc (+-more),rewrite,(미이관),/api/mypage/event/event-my-list
60,/page/donation/intro.spc (+-more),,/page/donation/intro,/api/donation/intro
61,/page/donation/happyBirthDay.spc,,/page/donation/happyBirthDay,/api/donation/happy-birthday
62,/page/donation/voteList.spc (+-more),,/page/donation/voteList,/api/donation/vote-list
63,/page/donation/voteView.spc,,/page/donation/voteView,/api/donation/vote-view
64,/page/donation/winnerList.spc,,/page/donation/winnerList,/api/donation/winner-list
65,/page/donation/winnerView.spc,,/page/donation/winnerView,/api/donation/winner-view
66,/page/presentation/point.spc,,/page/presentation/point,/api/presentation/point
67,/page/presentation/brand.spc,,/page/presentation/brand,/api/presentation/brand
68,/page/presentation/membership.spc,,/page/presentation/membership,/api/presentation/membership
69,/page/presentation/card.spc,,/page/presentation/card,/api/presentation/card
70,/page/presentation/app.spc,,/page/presentation/app,/api/presentation/app
71,/page/cert/phone/request.spc · /ipin/request.spc,rewrite,(백엔드 팝업),/api/cert/phone/request · /api/cert/ipin/request
72,/page/cert/phone/complete.spc · /ipin/complete.spc,rewrite,(백엔드 팝업),/api/cert/phone/complete · /api/cert/ipin/complete
73,/page/cert/nice/...(6종),rewrite,(백엔드 팝업),/api/cert/nice/... (6종)
74,/page/email/reject.spc,,/page/email/reject,/api/email/reject
75,/page/email/unsubscribe.spc,rewrite,(bridge),POST /api/email/unsubscribe
76,/page/live/grip-live-show.spc,,/page/live/grip-live-show,/api/live/grip-live-show
77,/page/live/secta9ine.spc,,/page/live/secta9ine (stg),/api/live/secta9ine
78,/page/live/live-show.spc,rewrite,(미이관),/api/live/live-show
79,/page/live/secta9ine-live-show.spc,rewrite,(미이관),/api/live/secta9ine-live-show
80,/page/reception-agree.spc · -proc.spc,,/page/reception-agree,/api/reception-agree · -proc
81,/page/survey/coretype.spc · /error.spc,rewrite,(미이관),/api/survey/coretype · /error
82,/page/brand/member/join-gate.spc,,/page/brand/member/join-gate,/api/brand/member/join-gate
83,/page/brand/member/join-auth.spc,rewrite,/page/brand/join/index,/api/brand/join/index
84,/page/brand/member/join-policy.spc,rewrite,/page/brand/join/policy,POST /api/brand/join/policy
85,/page/brand/member/join-view.spc,rewrite,/page/brand/join/form,POST /api/brand/join/form
86,/page/brand/member/join-optional.spc,rewrite,/page/brand/join/optional-form,POST /api/brand/join/optional-form
87,/page/brand/member/join-complete.spc,rewrite,/page/brand/join/welcome,/api/brand/join/welcome
88,"/page/brand/member/dormancy-{auth,view,complete}.spc",,"/page/brand/member/dormancy-{auth,view,complete}","/api/brand/member/dormancy-{auth,view,complete}"
89,"/page/brand/member/find-{auth,view,complete}.spc",rewrite,"/page/brand/member-info/find-id-pw-{form,process,complete}","/api/brand/member-info/find-id-pw-{form,process,complete}"
90,(없음),신규,/page/auth/login,/api/auth/login
91,(없음),신규,/page/join/popup,—
92,(없음),신규,/page/search,/api/search
93,(없음),신규,/page/common/alert,—
94,(없음),신규,/page/brand/common/alert,—
95,(없음),신규,/page/error,—
96,(없음),신규,/page/mypage/inquiry,—
97,(없음),신규,/page/about,—
98,(없음),신규,/page/points,—
99,(없음),신규,/page/services,—
100,(없음),신규,/page/styleguide (개발용),—
101,(없음),신규,/event/sleeveQr,/api/sleeve-qr
```
