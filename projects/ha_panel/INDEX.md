---
문서유형: INDEX
프로젝트: ha_panel
작성일: 2026-07-22
최종수정: 2026-08-05
작성자: dominic
상태: 진행중
요약: 해피포인트 앱 설문 패널 서비스 "패널KOK / SURVEY KOK" (Java8 / Spring MVC + JSP / MyBatis / WebLogic) — 자체 SPA 프레임워크 AMP 기반 웹뷰 (2026-08-05 앱 내 탑재 관계=ha_api 느슨한 연결·용어 라우팅 명시)
---

# 📇 ha_panel 문서 인덱스

> 🧩 **앱 내 탑재 관계(느슨함, 짝 아님)**: 이 서비스는 해피포인트 앱(베이스 = [`ha_api`](../ha_api/INDEX.md)) **안에서 웹뷰로 뜨지만, 코드/DB/운영이 완전히 독립된 별개 시스템**이다. ha_api 와 함께 판단하는 "짝(pairing)"이 **아니다** — **용어 라우팅 정도로만** 연결한다: 사용자가 **"패널"·"설문"·"패널KOK"·"SURVEY KOK"** 이라고 하면 이 `ha_panel` 로 인식한다.

## 프로젝트 정체성 (중요)
- **이 프로젝트 = 해피포인트 앱 안에서 웹뷰로 도는 설문 패널 서비스.** 서비스명 **"SURVEY KOK"**, 패널명 **"패널KOK"**.
- 사용자가 **설문·투표에 참여하고 그 대가로 해피포인트를 적립**하는 구조 → **포인트(금전성 자산)를 발생시키는 서비스**다. 인증 위·변조의 영향도가 단순 조회 서비스보다 크다.
- ⚠️ **KB 내에서 유일하게 "자체 SPA 프레임워크(AMP)"를 쓰는 프로젝트.** JSP는 껍데기만 내려주고 화면은 `control/**.html + .js` 모듈이 그린다. 타 프로젝트의 JSP/SiteMesh 감각으로 접근하면 안 된다.
- ⚠️ **빌드 파일이 없다** (`pom.xml`/`build.gradle` 부재). IntelliJ `.iml` 기반 수동 빌드 → **의존성 목록조차 저장소에 없다**. ECC `rules/java/security.md`의 "Dependency Security(CVE 스캔)"를 **현 상태로는 수행 불가**.
- ⚠️ **앱 서버가 WebLogic** (`weblogic.xml`). 타 프로젝트(Tomcat 9/10.1)와 다르다.

## 프로젝트 개요
- **워크스페이스 폴더**: `ha-panel` (KB 기준 `../../../ha-panel`)
- **Bitbucket remote**: `bitbucket.org/sectanine/ha_panel.git` (⚠️ 타 저장소는 하이픈, 여기만 **언더스코어** `ha_panel`)
- **브랜치**: `master` 단일. 커밋 4개뿐 (사실상 기존 소스 이관 스냅샷)
- **스택**: Java 8 / **Spring MVC (Anyframe 계열)** / **MyBatis** / Oracle / **Quartz(`task:scheduled`)** / **WebLogic**
- **프론트**: 자체 SPA 프레임워크 **AMP v5.0** ("VUE + NODEJS 결합, JQUERY 제외") + Vue + Swiper + `.ald` 레이아웃
- **패키징**: WAR (아티팩트명 `KOK_war`)
- **베이스 패키지**: **`hp.panel`** (⚠️ 타 프로젝트 `com.spc.hpc` / `com.example` 와 또 다름)
- **규모**: Java 66개 파일 / 약 7,667줄 · 화면 JS(`control/`) 약 9,986줄
- **테스트**: **0건** (테스트 디렉토리 자체가 없음)

## 아키텍처 (hp.panel)
```
hp.panel
├─ filter/WebFilter              전역 no-cache 헤더 (SameSite 메서드는 정의만 되고 미호출)
├─ common/
│  ├─ util/  SessionUtils(인증 핵심) · EncryptUtils · AES256Utils · SessionUtils
│  │         BizUtils · DateUtils · StringUtils · DecimalUtils · JsonUtil
│  │         SocketUtils · SslHttpClientBuilder · ConstantsUtils · FieldMap
│  ├─ aspect/ MdcInterceptor(로그 MDC) · PanelBizException
│  ├─ socket/ HttpManager
│  └─ service/ CommonSvc + CommonSrvyDao
├─ survey/                       ★ 핵심 도메인
│  ├─ web/     BaseSrvyMgCtl · PollSrvyMgCtl · BaseAgrCtl · PanelAgrCtl
│  ├─ service/ BaseSrvySvc · PollSrvySvc · BaseAgrSvc · PanelAgrSvc (+ impl/*Dao)
│  └─ dvo/     SrvySvo · SrvyItemVo · PollVo · ProfileVo · AgreeVo · SubmitPanelVo · SmsVo …
└─ schedule/                     포인트/HPC 배치
   ├─ PointUpdateJob · HpcUpdateJob (quartz-main.xml 크론)
   ├─ service/ PointService · HpcService (+ PointDao · HpcDao)
   └─ legacy/  ApiService · LegacyHeader/Tralier/Base · PT5110X0 · FtpUploader · FtpDownload
```

### 요청 처리 방식 (⚠️ 특이)
- **URL 패턴이 `*.do` 단일 + 쿼리 파라미터 `method=` 로 분기**한다. REST 아님.
  - `@RequestMapping(value="/panel.do")` + `@RequestMapping(params="method=main")` 형태.
- 엔드포인트 그룹:
  | 컨트롤러 | 기본 URL | 주요 method |
  |----------|----------|-------------|
  | `BaseSrvyMgCtl` | `/panel.do` | `auth`(진입/인증) · `main` · `base` · `survey` · `submit` · `refresh` · `faq` · `action-log` · `test` |
  | `PollSrvyMgCtl` | `/panel.do` | `survey-panel` · `submit-panel` · `get-result-poll` · `setting` · `profile` · `save-profile` · `survey-record` · `policy` · `sms` |
  | `BaseAgrCtl` | `/base-agree.do` | `agree` · `inquiry` |
  | `PanelAgrCtl` | `/agree.do` | `agree` · `inquiry` · `agreeHappy` |

### 인증 방식 (⚠️ 가장 중요)
> **네이티브 앱이 URL 파라미터로 토큰을 넘기고, 서버가 복호화해 쿠키를 발급**하는 구조.

1. 앱 → `GET /panel.do?method=auth&token=<AES암호문>` (`BaseSrvyMgCtl:74`)
2. `SessionUtils.getToknAuth()` 가 **고정 키/IV로 AES-CBC 복호화** → `mbrNo$$...|||mbrNm$$...` 파싱
3. `SessionUtils.setCookieUser()` 가 동일 방식으로 재암호화 → `Set-Cookie: PANEL_AUTH=...; Max-Age=86400; Secure; SameSite=strict`
4. 이후 요청은 `PANEL_AUTH` 쿠키를 복호화해 회원 식별

- 🔴 **키/IV가 소스에 하드코딩되어 저장소에 커밋되어 있다** (`SessionUtils.java:14-15`, `AES256Utils.java:13`).
- 🔴 토큰에 **무결성(MAC/서명)·만료·nonce가 전혀 없다** → 키를 아는 사람은 임의 `mbrNo` 토큰을 영구 생성 가능.
- 상세: [WORKLOG-20260722-codebase-analysis.md](./WORKLOG-20260722-codebase-analysis.md) Critical-1.

## 프론트엔드 (AMP 프레임워크)
- **엔진**: `jslib/cndf/amp.js` (v5.0.0) — 모듈 로더 + 레이아웃(`.ald`) + Vue 바인딩. jQuery는 별도 로드되나 AMP 자체는 미의존.
- **모듈 규약**: `control/<경로>.html`(뷰) + `control/<경로>.js`(`AMP.module = {...}`) 한 쌍. `init()` 이 진입점.
- **공통 모듈**: `common`, `include/header`, `include/footer`, `commonPopup`, `commonPoll`
- **화면 API**: `AMP.move()`(이동) · `AMP.showDialog()/hideDialog()`(팝업) · `@click` · `:class` · `:disabled`
- **네이티브 브릿지**: `control/native.js` (앱↔웹뷰 통신)
- **레이아웃**: `ald/AMP.ald` · `ald/SITE.ald` · `ald/board1.ald`, 레이아웃 ID `panelLayout`
- ⚠️ 컨벤션(케밥케이스 class/id, CSS 속성 순서)이 저장소 자체 문서에 있다 → `META-INF/read/coding-conventions.txt`. [conventions/html-css.md](../../shared/conventions/html-css.md) 고도화 시 1차 근거로 쓸 것.

### 화면 맵
| 구분 | 모듈 경로 |
|------|-----------|
| 홈 | `main/main` |
| 프로필 수정 | `main/profile` |
| 설정 | `main/setting` |
| 조사 참여이력(포인트 리워드) | `main/survey-record` |
| 문의/FAQ | `main/faq` · 약관 `main/policy` |
| 기초조사 | 리스트 `basic-survey/basic-survey-list` + 상세 `basic-survey-detail-<YYYYMM>-<A~F>` |
| 패널조사/투표 | `panel-survey/poll-survey-detail-1 ~ 8` |
| 팝업 | `popup/activity-agreement` · `mobile-authentication` · `base-agreement` · `no-reward-agreement` · `reward-agreement` · `withdrawal` · `available-survey` · `terms-*` · `privacy-usage-*` · `poll-result` · `push-alert` |

- ⚠️ **기초조사 상세가 회차(연도)마다 파일 복제로 증식**한다: `202301-A~D` → `202401-A~F` → `202501-A~F` (현재 16쌍). 신규 회차마다 HTML/JS 한 쌍씩 추가되는 구조 → DRY 위반이지만 **회차별 문항이 확정 스냅샷이어야 하는 업무 특성**도 있어 단순 통합은 위험. 변경 시 반드시 회차 범위를 먼저 확인할 것.

## 도메인 데이터 (Oracle)
> 근거: `META-INF/read/api-documents.txt` (저장소 자체 문서, 샘플 DML 포함)

| 테이블 | 용도 |
|--------|------|
| `TB_BASE_SRVY` / `TB_BASE_SRVY_DTL` | 기초조사 회차(`BASE_NO`=202301/202401/202501) + 상세 문항(`SRVY_NO`=A~F), 회차별 지급 포인트 `RESV_PT` |
| `TB_PANEL_SRVY` / `TB_PANEL_SRVY_DTL` | 패널조사. `PANEL_TYPE`= **`LINK`(외부 설문 링크) / `POLL`(앱 내 투표)**, 대상자 조건 `PANEL_TG_CD` |
| `TB_PROFILE` / `TB_PROFILE_DTL` | 프로필 관리 항목(직업/거주지/가족수/결혼/자녀 등) + 항목별 선택지 |
| `TB_MBR_PANL` / `TH_MBR_PANL_CHG_HST` | 패널 회원 정보 + 변경 이력 |
| `TH_MBR_SRVY_HST` / `_DTL` | 회원 **기초조사** 참여 이력 |
| `TH_MBR_PANEL_SRVY_HST` / `_DTL` | 회원 **패널조사** 참여 이력 |
| `TH_MBR_PROFILE_HST` / `_DTL` / `_CHG_HST` | 회원 프로필 이력 |
| `EM_TRAN` | 휴대폰 인증번호 발송 이력 |

- 키는 **회원번호 `MBR_NO`** 중심. MyBatis 매퍼: `mapper-base-survey` · `mapper-poll-survey` · `mapper-survey` · `mapper-base-agree` · `mapper-panel-agree` · `mapper-schedule`.
- ✅ **SQL 인젝션 관점 클린** — 매퍼 전체에 `${}` **0건**, 전부 `#{}` 바인딩. → [sql-mybatis.md](../../shared/conventions/sql-mybatis.md) 규칙 준수.

## 배치 / 외부 연동
| 잡 | 크론 | 내용 |
|----|------|------|
| `PointUpdateJob.selectPoint` | `0 00 07 * * *` (매일 07:00) | 지급 대상 포인트 조회 |
| `PointUpdateJob.updatePoint` | `0 00 08 * * *` (매일 08:00) | 포인트 지급 반영 |
| `HpcUpdateJob.updateHpc` | `0 30 08 * * *` (매일 08:30) | HPC(해피포인트카드) 회원 상태 동기화 — 휴면↔정상, 탈회 처리 |

- **레거시 연동**: `schedule/legacy/` — 전문 기반(`PT5110X0`, `LegacyHeader`/`LegacyTralier`) **소켓 통신 + FTP 업/다운로드**(`FtpUploader`/`FtpDownload`). 채널 코드 `H0/H1/H2/X0`.
- **설정**: `ApiProps`(`@InjectProperties("api")`) 로 URL·`rcgnKey`·`key`/`iv` 등을 **외부 프로퍼티에서 주입**. ✅ 저장소 내 `.properties` 파일 **0건** → 이 계열 시크릿은 커밋되지 않았다.
- **DB 접속**: **JNDI `jdbc/panel`** (`context-transaction.xml`). ✅ DB 크리덴셜 저장소 미포함. `META-INF/context.xml`의 `SCOTT/TIGER`는 톰캣 템플릿 기본값(실 계정 아님).

## 🔴 현재 상태 / 핵심 리스크
> 상세 근거·재현 시나리오는 [WORKLOG-20260722-codebase-analysis.md](./WORKLOG-20260722-codebase-analysis.md).
> 판정 기준: ECC `rules/java/security.md` · `rules/common/security.md` · `rules/common/coding-style.md` (참조 전용).

| # | 심각도 | 요약 |
|---|--------|------|
| 1 | 🔴 Critical | **인증 토큰 암호화 키/IV가 소스에 하드코딩 + 커밋** (`SessionUtils.java:14-15`, `AES256Utils.java:13`) → 임의 회원 사칭 가능 |
| 2 | 🔴 Critical | 인증 토큰에 **무결성·만료·nonce 없음** → 한 번 유출된 토큰은 **영구 유효**, 재사용 차단 수단 없음 |
| 3 | 🟠 High | **인증 토큰 원문을 평문 로깅** (`BaseSrvyMgCtl.java:86`) — 로그 열람자가 곧 사칭 가능 |
| 4 | 🟠 High | **인증 실패가 조용히 삼켜진다** — `SessionUtils`의 빈 `catch` 4개. 복호화 실패 시 예외 대신 **빈 Map 반환**으로 흐름 계속 |
| 5 | 🟠 Medium | **빌드 파일 부재**(`pom.xml`/`build.gradle` 없음) → 재현 빌드·의존성 CVE 스캔 불가 |
| 6 | 🟠 Medium | **빌드 산출물 git 추적** — `out/` 538개 + `WEB-INF/classes/` 13개 설정 중복 → **설정 드리프트**(수정본과 배포본 불일치) 위험 |
| 7 | 🟡 Low | 클라이언트 `AMP._GET("am")` → `AMP.run(am)` — URL 파라미터로 로드 모듈 경로 결정 |
| 8 | 🟡 Low | 인증 쿠키 `Set-Cookie` 수동 조립인데 **`HttpOnly` 누락**, 테스트 0건, 미사용 `addSameSiteAttribute()` 등 죽은 코드 |

- ✅ **클린 판정**: SQL 인젝션(전부 `#{}`) · DB 크리덴셜 미커밋(JNDI) · API 프로퍼티 미커밋 · `web.xml`에서 PUT/DELETE/TRACE/OPTIONS 차단 및 세션 쿠키 `HttpOnly`+`Secure` 설정.

## 문서 목록
| 문서 | 유형 | 상태 | 요약 |
|------|------|------|------|
| [WORKLOG-20260722-codebase-analysis.md](./WORKLOG-20260722-codebase-analysis.md) | WORKLOG | 진행중 | 코드베이스 구조 분석 + ECC 기준 1차 진단(Critical 2건 — 인증 키 하드코딩·토큰 무결성 부재) |

## 참고 (공통 문서)
- [공유 지식 베이스 README](../../README.md)
- [ECC 참조 · 작업 프로토콜](../../shared/ecc-reference.md)
- [보안/취약점 진단 기준](../../shared/security-review.md)
- [코드 컨벤션](../../shared/conventions/README.md) · [java](../../shared/conventions/java.md) · [spring](../../shared/conventions/spring.md) · [sql-mybatis](../../shared/conventions/sql-mybatis.md) · [javascript](../../shared/conventions/javascript.md) · [html-css](../../shared/conventions/html-css.md)
- [서버 환경](../../shared/server-env.md) — ⚠️ 이 서비스의 **WebLogic 인스턴스/배포 경로는 미확인**(현재 문서의 Tomcat 목록에 없음)
- 저장소 내 자체 문서(참고): `META-INF/read/file-info.txt`(화면 맵) · `coding-conventions.txt`(프론트 규약) · `api-documents.txt`(테이블·샘플 DML)
