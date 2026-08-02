---
문서유형: WORKLOG
범위: 프로젝트(ha-web-api)
주기: 주
기간: 2026-W31 (07-27~)
작성일: 2026-07-27
최종수정: 2026-07-31
작성자: AI(Claude)
상태: 진행중
요약: 인증 API(me→check), KCB 본인인증 complete postMessage, /api/page/cert 라우팅 통일 (+07-29: check 로그인여부만·dev 도메인·회사IP CORS 폐기 원복) (+07-31: 파바앱 본인인증/브랜드 join 정합·모델API 룰셋·auth/check 유입URL 로깅)
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

## 9. (07-31) 파바앱 본인인증/브랜드 join 정합
- `BrandMemberModelApiResource.joinAuth`: 응답 `reqPath` `"APP"`→**`"OPBS"`**.
- `JoinModelApiResource.policy`: `landingType`→**`alertType`**, 요청 컨텍스트 `reqPath`/`reqChnl`/`reqPage` 전 분기 항상 포함(빈값 기본), javadoc 에서 alert 규격 제거(프론트 SSOT 포인터만). `/api/join/index` 파라미터 에코 제거(빈 data).
- (프론트 짝) 브랜드 본인인증 팝업 신설·약관 라우트 `join-policy`→`policy` 이동은 happypoint-web2 W31 §12·§13 참조.

## 10. (07-31) 룰셋 "1 page ↔ 1 model API" — 백엔드 신규/스텁 엔드포인트
- 프론트 진입 핑(`pingModel`) 대상 중 백엔드 미존재/POST전용 경로에 **GET 성공 스텁** 추가:
  - POST 전용 form 계열 진입 핑용 GET: `join/form`, `join/optional-form`, `member-info/modify-info-form`.
  - 그룹2 신규 GET(성공만 반환): `event/my-coupon`, `search`(page/search), `dormancy/auth-form`, `member-info/{withdrawal-form, find-id-pw-form, confirm-pw-form, change-pw-form}`.
- 룰: page 진입 시 대응 모델 API 1회 호출. 없으면 백엔드 생성(동작 없어도 `{code:"00"}`). 실로직 이식은 후속.

## 11. (07-31) 유입 트래킹 로깅(26컬럼 TSV) — ha1-api 포맷 정합 ★
- **포맷 정합**: 참조 로그 `ha1-api-*.log`(앱API 트래킹, 26컬럼 TSV)와 동일하게. ha-web-api엔 이미 `TrackingInterceptor`(26컬럼)+`TrackingLogger`가 XML(`dispatcher-config.xml`)로 `/api/**` 등록·활성 상태였음(초기 오판정정). 커스텀 `url=…` 로거는 폐기.
- **파일명**: `TrackingAppender` 파일패턴 → **`${LOG_DIR}/tracking/ha-web-%d{yyyyMMdd_HH}_ip-${serverip:}.log`**(매시간 롤링·168시간 보관, 헤더 유지). 커스텀 Lookup `ServerIpLookup`(`${serverip:}`=서버IP 대시, EC2 `ip-12-12-12-12` 형식) + `<Configuration packages="com.spc.hpc.home.config.log">`.
- **로깅 2종**:
  1. `AuthApiResource.check()` — 프론트가 body로 넘긴 **원본 페이지 url을 service_url**로 단건 기록(`TrackingInterceptor.write(...)`, 페이지 진입=check 호출=1줄).
  2. `TrackingInterceptor` `/api/**` — **2제외**: `dispatcher-config.xml`에 `/api/auth/check` exclude(중복방지) + 인터셉터 코드에서 핸들러 패키지 `com.spc.hpc.api.model.*` skip(모델API 제외).
- `TrackingInterceptor.write(...)` static 추출(인터셉터·check 공용), 파라미터 password 마스킹 유지.

## 12. (07-31) 스테이징 도메인 확인
- `application-stage.yml`: `cert.return-server`·`site.url` **이미 `stg-www.happypointcard.com`**(변경 불필요). `application-stagep.yml`은 프록시(stg-napi)만. 프론트 짝 `.env.stg`는 stg-www로 수정(web2 W31 §16).

## 13. (07-31) 홈페이지 메인 일반 배너 계약 API
- 대상 정정: 레거시 `ha-api`가 아닌 **`j-ha-web-api`(ha-web-api dev-j)** 에 구현.
- **GET `/api/home/banner-list`**: `com.spc.hpc.api.home.HomeBannerApiResource`의 비-모델 전용 홈 API. `ApiResponseWrapper`가 `{code:"00", ..., result:[...]}`로 래핑.
- `BannerInfoRepository.listNormalBannerInfo`에 `ha-api`의 동일 조회 조건을 이식하고, 서비스에서 `areaCode=HA_11101`·웹 기기코드 `W`·S3 이미지 URL·세션 회원 등급/세그먼트/임직원 조건을 조립.
- 검증: `mvn -o -DskipTests compile` **BUILD SUCCESS**.

- `listNormalBannerInfo`의 최종 CTE 조회에서 파생 테이블을 제거한 뒤 남은 `) PA` 때문에 ORA-00933이 발생했다. `A.WEBP_YN = 'N'` 필터를 `VW_BANNER_LIST A` 조회에 직접 적용하고, 정렬 별칭도 `A`로 통일해 수정했다. `mvn -o -DskipTests compile` BUILD SUCCESS로 검증했다.

- `POST /api/member-info/confirm-pw-process`에서 비밀번호 불일치 시 기존 성공 응답 대신 `ApiError.AUTH`를 반환하도록 변경했다. 응답 `code`는 `40`이며, 비밀번호 확인 성공 시에만 확인 쿠키와 랜딩 정보를 반환한다. `mvn -o -DskipTests compile` BUILD SUCCESS로 검증했다.

## 다음 할 일 (TODO)
- [ ] (07-31) 그룹2 신규 스텁 API 실로직 이식(레거시 컨트롤러 기반) 여부
- [ ] (07-31) 그룹3(정적 page) 모델API 처리 방침
- [ ] (07-29) 로그인 nonce/rate limit/CAPTCHA 백엔드 구현 여부 결정
- [ ] 신규 계약 API 에 join-policy(authInfo 수신)/join-view(복호화 반환) 존재 확인·없으면 추가
- [ ] ELB /api strip 여부 확인 → cert 컨트롤러 매핑 확정
- [ ] KCB complete postMessage targetOrigin 을 '*' → 프론트 오리진 제한(운영 보안)

## 배포 목록 (dev-www)
- Java: `AuthApiResource`, `CertController`, `CertPhoneController`, `CertIpinController`, `SitemeshFilter`, `DeviceRedirectFilter`
- JSP/JS: `cert/kcb/{phone,ipin}/complete.jsp`, `cert/kcb/config.jsp`, `cert/nice/*/config.jsp`, `unvus.util.js`

## 참고
- 이전 주차: [WORKLOG-2026-W30](./WORKLOG-2026-W30.md)

## 14. (2026-07-31) Login empty model API
- Added `GET /api/auth/login` in `com.spc.hpc.api.model.auth.AuthModelApiResource`.
- It returns the standard successful `ApiOkBody` with an empty result for login page entry. The existing `POST /api/auth/login` remains the authentication submission endpoint.
- Verification: `mvn -o -DskipTests compile` completed with `BUILD SUCCESS`.

## 15. (2026-08-02) Tracking interceptor instance cleanup
- `TrackingInterceptor` has no external static calls. Converted `write()` and its helper methods, hostname/object-name state, and loggers to instance members.
- Converted all remaining constants too, leaving no `static` member in `TrackingInterceptor`.
- Verification: `mvn -o -DskipTests compile` completed with `BUILD SUCCESS`.

## 16. (2026-08-02) Dev tracking appender repair
- Cause of missing dev tracking output: `TrackingAppender` had `filePattern` only, without `fileName` or `DirectWriteRolloverStrategy`; its generic log layout also did not preserve the 26-column TSV contract.
- Updated `log4j/dev/log4j2.xml` to use `${LOG_DIR}/tracking/tracking.log`, hourly rollover, the 26-column TSV header with `%m%n`, and the same 200-file retention policy as stage/prod.
- Verification: dev/stage/prod Log4j files parse as XML and `mvn -o -DskipTests compile` completed with `BUILD SUCCESS`. Runtime file creation still requires Tomcat restart and one `/api/**` request.

## 17. (2026-08-02) Tracking interceptor package alignment
- Moved `TrackingInterceptor` from `com.spc.hpc.api.common` to `com.spc.hpc.home.interceptor`, alongside `SpcInterceptor`.
- Updated `dispatcher-config.xml` to register `com.spc.hpc.home.interceptor.TrackingInterceptor` for `/api/**`.
- Verification: no old package reference remains and `mvn -o -DskipTests compile` completed with `BUILD SUCCESS`.

## 18. (2026-08-02) Log4j runtime loading and SLF4J 2 bridge repair
- `Log4j2ConfigurationFactory` now resolves `/log4j/<profile>/log4j2.xml` from the WAR classpath before passing its URI to Log4j.
- Replaced the SLF4J 1.x bridge `log4j-slf4j-impl:2.17.0` with the SLF4J 2.x bridge `log4j-slf4j2-impl:2.20.0`, and aligned `log4j-api` and `log4j-core` to `2.20.0`.
- Verification: `mvn -Pdev -DskipTests package` completed with `BUILD SUCCESS`; the WAR includes the dev Log4j XML, `log4j-api/core-2.20.0`, `log4j-slf4j2-impl-2.20.0`, and `slf4j-api-2.0.16`.
- Remaining runtime check: redeploy and restart the dev Tomcat, then request a non-API page for `SpcInterceptor` and an `/api/**` endpoint for `TrackingInterceptor`.

## 19. (2026-08-02) Tracking log profile scope confirmed
- Tracking logging is enabled only for `dev`, `stage`, and `prod`; `local/log4j2.xml` has no `TrackingAppender`, `TrackingLogger`, or tracking log path.
- The enabled profiles write the 26-column header and data rows as TSV: 25 tab delimiters in the header and `%m%n` preserves the tab-delimited message body.
- User-applied Log4j changes were preserved. No Java source or Log4j XML was modified during this confirmation; all four profile XML files parse successfully.

## 18. (2026-08-02) 트래킹 로그 미기록 실환경 근본원인 — DirectWrite vs fileName
- 증상: 트래킹 폴더(`logs/tracking/`)는 생성되나 로그 파일이 안 쌓임. `write()` 호출 자체는 정상(임시 `System.out` 진단으로 catalina.out 확인됨).
- **서버 디렉토리 실사로 판별**: `member/alliance/dormancy`(= `fileName=` 기반 appender)는 **파일 존재**, `happyAds/hpcapi/sendMail/tracking`(= `DirectWriteRolloverStrategy`)는 **디렉토리만 있고 파일 0개**. → **이 배포 환경(ec2-user Tomcat)에서 DirectWrite가 파일을 생성하지 않음**이 확정. 권한/설정로딩은 정상(폴더 생성됨).
- **처방**: `TrackingAppender`를 검증된 `fileName=` 방식으로 확정 — `fileName="${LOG_DIR}/tracking/tracking.log"` + `filePattern=".../tracking.%d{yyyyMMdd_HH}.log"`(시간별) + `DefaultRolloverStrategy`+`Delete`(`IfAccumulatedFileCount exceeds=200`, 최대 200개 보관). 4개 프로파일(local/dev/stage/prod) 동일 적용. 26컬럼 TSV header 유지.
- 부수정리: 미사용 `${serverip:}` 제거로 `ServerIpLookup.java` 삭제 + `<Configuration packages=...>` 속성 제거(ConfigurationFactory는 `Log4j2Plugins.dat`로 등록되어 무관). `mvn -o clean compile` BUILD SUCCESS, dat에서 serverip 제거 확인.
- **미결**: 배포 후에도 `tracking.log` 미생성 시 → 배포된 WAR의 `log4j2.xml`이 `fileName=` 버전인지(구버전 WAR 여부), Tomcat work/ 캐시, 재기동 확인 필요. (진단표는 대화 참조)
- 설계원칙: DirectWrite는 첫 이벤트 전까지 파일 미생성 + 이 환경에서 미작동 → 트래킹처럼 확실한 산출이 필요한 로그는 `fileName=` 기반 사용.
