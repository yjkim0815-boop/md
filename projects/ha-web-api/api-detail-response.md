---
문서유형: SHARED
프로젝트: ha-web-api
이슈키: --
작성일: 2026-07-27
최종수정: 2026-07-27
작성자: dominic
상태: 진행중
요약: ha-web-api 신규 API의 detailCode/detailMessage·도메인별 message·로그인 rpsCd 등 상세 응답코드 카탈로그
---

# 📑 ha-web-api API 상세 응답코드 (detailCode / detailMessage)

> 공통 규격(엔벨로프·code 대역 00/01/50/60/70/80/99)은 [shared/conventions/api-response.md](../../shared/conventions/api-response.md) 정본.
> 이 문서는 **ha-web-api 고유의 detailCode/detailMessage·도메인 message·레거시 rpsCd** 를 정리한다.
> 구현: `com.spc.hpc.api` — 공통 헬퍼 `api/common/ApiError` + `ApiResponseWrapper`(성공 자동 래핑).

## 1. 도메인별 실제 사용 message (대분류 code)
| code | message | 위치 |
|------|---------|------|
| 40 | 로그인이 필요합니다. | `unauthorized()` — 로그인 필요 화면 전반(mypage/event-my/reception/survey 등) |
| 50 | PLATINUM 카드 발급 신청 기간이 아닙니다. | mypage 카드(platinum/platinum-status) — `policy()` |
| 50 | PLATINUM 등급 회원만 이용 가능합니다. | mypage 카드(platinum/platinum-status) — `policy()` |
| 91 | 유효하지 않은 eventseq 입니다. | event(event-view) — `badRequest()` |
| 91 | 유효하지 않은 prizeSeq 입니다. | event(winner-view) — `badRequest()` |
| 91 | instCd, attrCd 는 필수입니다. | brand(brand-attr) — `badRequest()` |
| 93 | 이벤트를 찾을 수 없습니다. / 당첨자 발표를 찾을 수 없습니다. | event — (조회 결과 없음) |
| 91 | 잘못된 접근입니다. | email(reject) — `badRequest()` |
| 93 | (message 없음) | survey(coretype) — `data()` 원본 에러뷰라 코드만 |
| 99 | 회원정보를 불러오지 못했습니다. | member(member-info detail) |
| 99 | 일시적인 오류가 발생했습니다. | 전역 예외(`ApiExceptionHandler`) |
| 99 | cookie/redirect(/vendor) flow — needs manual port | TODO 스텁(member 12 + brand 21) — 미구현 표시 |

## 2. detailCode 구조 (앞 2자리 code + 뒤 2자리 Suffix)
`detailCode` = **앞 2자리(상위 `code`, 공통 규격) + 뒤 2자리(Suffix, 상세)**. 성공 시 항상 `0000`.

### Suffix (뒤 2자리 — 상세)
| Suffix | 내용 |
|--------|------|
| `00` | 정상 |
| `01` | 정보없음(대상자 아님) |
| `02` | 정보없음(대상자임) |
| `03` | 유효기간 |
| `04` | 중복오류 |
| `05` | 일치하지않음 |
| `08` | 정보있음(대상자 아님) |
| `09` | 정보있음(대상자임) |
| `11` | 데이터 누락 오류(필수정보) |
| `12` | 데이터 검증 오류(유효하지 않는 값) |
| `13` | 데이터 타입 오류(유효하지 않는 타입) |
| `14` | 데이터 변환 오류(암호화) |
| `15` | 데이터 변환 오류(복호화) |
| `16` | 데이터 검증 오류(형식에 맞지 않은 값) |
| `17` | 데이터 변경 오류(등록/수정 시 프로세스 오류) |
| `31` | 연결오류 |
| `71` | 제한(특정 조건 만족, ex. 실패 5회 이상) |
| `99` | 기타 |

> 예(앞2=code / 뒤2=Suffix): `0000` 정상/정상, `9101` 파라미터·정보없음, `8031` 내부시스템 연동·연결오류, `5071` 정책·제한.

## 3. 레거시 detailCode (rpsCd / rpsDtlCd) 카탈로그
전문(MB2000H0 등) 응답의 세부코드. **원본 그대로 보존**해 전달한다(대분류 code 는 유지, 세부는 detail/데이터로).
| rpsCd | rpsDtlCd | 의미 |
|-------|----------|------|
| `00` | `0000` | 정상 |
| `88` | `0011` / `0012` | 휴면 회원 |
| `44` | `2728` | 비밀번호 5회 오류(로그인 제한) |
| `44` | `2200` | 모바일카드 인증 오류 |
| (그 외) | — | 시스템/기타 오류 |

## 4. 로그인 API 응답 (`/api/auth/*`) — checkauth.jsp 이식
로그인은 rpsCd 분기 계열은 **원본 rpsCd/rpsDtlCd 를 `result` 안에 보존**한다(엔벨로프 code 는 "00", `result.success=false` 로 구분). 단 권한/검증 실패는 대분류 code(41/40)로 내린다.

### POST /api/auth/login
- **성공**: `result = { returnUrl }` (code "00" 으로 성공 판별, success 플래그 없음. 회원정보 미포함 — MVC 동일: 세션 적재 후 이동)
- **실패/분기** (아래 rpsCd 계열은 code "00" + `result.success=false` + 원본 rpsCd/rpsDtlCd 그대로):
  | 조건(rpsCd/rpsDtlCd) | message | redirect/action |
  |------|---------|------|
  | 44 / 2728 | 비밀번호 5회 오류로 로그인이 제한되었습니다.\n비밀번호 찾기에서 재설정 해주시기 바랍니다. | redirect `/page/member-info/find-id-pw-form.spc?findType=pw` |
  | 44 / 2200 | 시스템오류(모바일카드 인증오류)로 로그인할 수 없습니다. | redirect `/sso/login.jsp` |
  | 88 / 0011·0012 | (휴면, 메시지 없음) | action `/page/dormancy/auth-form.spc` (+returnUrl,userId) |
  | 88 / 그외 | 아이디나 패스워드를 확인해주세요. | redirect `/sso/login.jsp` |
  | 그외 rpsCd | 시스템오류로 로그인 페이지 호출이 지연되고 있습니다. | redirect `/sso/login.jsp` |

  ※ 권한/검증 실패는 rpsCd 계열과 달리 **대분류 code 로** 내린다(엔벨로프 실패, `result:{}`):
  | 조건 | code | message |
  |------|------|---------|
  | resultCode=3 (권한 없음) | **41** | 접근 권한이 없습니다. |
  | resultCode≠1,3 (인증/검증 실패) | **40** | 아이디 또는 비밀번호를 확인해주세요. |

### POST /api/auth/check (로그인 여부) — POST 전용
- 요청 body(JSON): `{ url, method, params }` — 프론트(미들웨어→layout→auth-server)가 **원요청 컨텍스트**를 실어 보냄.
  - `url` = 원본 경로에서 끝 `.spc` 제거(쿼리 포함). `params` = **GET 쿼리 → POST 바디 순 병합**(같은 키면 POST 값이 최종).
  - 백엔드는 이 컨텍스트를 **로깅만** 하고 판별 로직/응답 형태는 불변.
- `result = { isAuthenticated: true|false }` + 로그인 시 `userId, userNm, mbrGrCd, mbrGrCdNm`(회원명/아이디/등급)
  - 필드명 `isAuthenticated` = 레거시 JSP 변수(`SecurityUtils.isAuthenticatedInJsp`=세션 authToken 존재)와 동일.

### POST /api/auth/logout
- `data = { loggedOut: true }`

---
> 근거 소스: `api/common/ApiError.java`, `api/common/ApiResponseWrapper.java`, `api/auth/AuthApiResource.java`(checkauth.jsp 이식), 각 도메인 `*ApiResource`.
