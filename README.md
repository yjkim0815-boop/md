---
문서유형: INDEX
프로젝트: 공통(지식 베이스 루트)
작성일: 2026-07-21
최종수정: 2026-07-22
작성자: dominic
상태: 진행중
요약: happypointcard 백엔드/앱서버 개발 개인 지식 베이스의 루트 인덱스 — 작업 프로토콜·공통 문서·프로젝트 인덱스 허브 (2026-07-22 ha-push-batch·ha_panel·thehappy_ios·thehappy_aos·gcs_fo 등록 + **gcs 등록 = 미등록 우선순위 1위 해소 · KB 최초 JPA/PostgreSQL/Redis 프로젝트**)
---

# 📚 happypointcard 지식 베이스 (md)

> dominic 개인 지식 베이스. `happypointcard` **백엔드 / 앱서버 개발**의 공통 규칙·서버 환경·프로젝트별 진행 기록을 모아 **모든 채팅에서 공통 참조**한다.
> 이 문서(`README.md`)는 지식 베이스의 **루트 허브**다. 하위 모든 문서가 `../README.md` / `../../README.md` 로 여기를 가리킨다.

## 🔑 작업 프로토콜 (최우선)
1. **학습 최우선순위 = ECC.** 새 채팅/작업 시작 시 ECC(해커톤 우승자 컨텍스트)의 관련 규칙·스킬을 **먼저 참조**한다.
2. **ECC를 근거로 사용자가 시킨 작업을 수행**한다.
3. 수행 결과·확정 사항을 **이 `md` 지식 베이스에 업데이트**한다(공통/프로젝트 지속 고도화).
4. **ECC는 참조 전용(수정 금지), `md`는 갱신 대상.** 두 경로를 혼동하지 않는다.
> 상세: [shared/ecc-reference.md](./shared/ecc-reference.md)

## 🗂️ 디렉토리 구조
```
md/
├─ README.md              ← (이 문서) 루트 허브
├─ shared/                공통 문서 (전 프로젝트·전 채팅 공통 적용)
│  ├─ ecc-reference.md    ECC 정체·작업 프로토콜·백엔드 매핑
│  ├─ server-env.md       개발/스테이징 서버(EC2·Tomcat) 공통 환경
│  ├─ security-review.md  보안 리뷰/취약점 진단 기준
│  └─ conventions/        기술별 코드 컨벤션 (java/spring/sql-mybatis/js/react/html-css)
├─ templates/             문서 작성용 템플릿 (INDEX/ARCHIVE/WORKLOG)
└─ projects/              프로젝트별 인덱스 + 아카이브 + 워크로그
   ├─ ha_api/          해피포인트 앱 API 서버 (하이브리드 앱 / Spring5.2 / Java8)
   ├─ ha_web/          레거시 홈페이지 (Spring MVC / Java8)
   ├─ ha-web-api/      신규 홈페이지 리뉴얼 백엔드 (Spring6 / Java21)
   ├─ ha-push-batch/   출석체크 리마인드 푸시 배치 (Spring Boot3.5 / Java17 / Spring Batch)
   ├─ ha_panel/        앱 설문 패널 "패널KOK" (Spring MVC / Java8 / WebLogic / 자체 SPA=AMP)
   ├─ thehappy_ios/    해피포인트 iOS 네이티브 앱 (Swift5 / iOS13+ / UIKit / 웹뷰 하이브리드)
   ├─ thehappy_aos/    해피포인트 Android 네이티브 앱 (Kotlin2.0 / minSdk26 / XML+ViewBinding / 웹뷰 하이브리드)
   ├─ gcs_fo/          기프트카드 웹뷰 프론트 (React18 / TypeScript / CRA+CRACO) ← 앱 안에서 뜨는 화면
   └─ gcs/             기프트카드 백엔드 API 서버 (Spring Boot3.4 / Java21 / JPA+QueryDSL / PostgreSQL) ← gcs_fo의 서버 짝
```
> 📛 **폴더명 규칙(2026-07-22 변경)**: `projects/` 하위 폴더명은 **Bitbucket 저장소명과 1:1로 일치**시킨다. 이전에는 로컬 임포트 폴더명 기반 `j-ha-*` slug를 썼으나, 머신마다 다를 수 있는 임포트명 대신 **원격 저장소라는 단일 기준**으로 통일했다. 신규 프로젝트 등록 시에도 `git remote get-url origin`의 저장소명을 그대로 쓴다.
>
> ⚠️ **저장소명 ≠ 로컬 폴더명.** 대부분 다르므로 아래 매핑표를 기준으로 삼는다. 문서 안에서 **KB 슬러그는 저장소명**, **`../` 상대경로는 로컬 폴더명**을 쓴다(경로는 실제 디스크를 따라가야 하므로).
>
> | KB 슬러그 (=Bitbucket 저장소명) | 로컬 워크스페이스 폴더 | 구분자 |
> |---|---|---|
> | `ha_api` | `ha-api` | ⚠️ 언더스코어 |
> | `ha_web` | `ha-web` | ⚠️ 언더스코어 |
> | `ha-web-api` | `ha-web-api` | ✅ 동일 |
> | `ha-push-batch` | `ha-batch` | ⚠️ 이름 자체가 다름 |
> | `ha_panel` | `ha-panel` | ⚠️ 언더스코어 |
> | `thehappy_ios` | `ha-ios` | ⚠️ 이름 자체가 다름 |
> | `thehappy_aos` | `ha-aos` | ⚠️ 이름 자체가 다름 |
> | `gcs_fo` | `gcs-fo` | ⚠️ 언더스코어 |
> | `gcs` | `gcs` | ✅ 동일 |
>
> (미등록: `ha_admin`↔`ha-admin`, `happypoint-web2`↔`happypoint-web2`)

## 📄 공통 문서 (shared)
| 문서 | 상태 | 요약 |
|------|------|------|
| [ecc-reference.md](./shared/ecc-reference.md) | 진행중 | ECC 정체·핵심 규칙·해피포인트 백엔드↔ECC 스킬/에이전트 매핑 (참조 전용 안내) |
| [server-env.md](./shared/server-env.md) | 진행중 | 개발/스테이징 EC2·Tomcat 인스턴스·포트·DB(JNDI)·Scouter APM·배포 원칙 |
| [security-review.md](./shared/security-review.md) | 초안 | OWASP 기반 취약점 진단/보안 리뷰 개인 기준 + ECC 커밋 전 체크리스트·시크릿 스윕·대응 프로토콜·진단 이력 |
| [conventions/README.md](./shared/conventions/README.md) | 초안 | 기술별 코드 컨벤션 인덱스 (개발자 개인 공통 규칙) |

## 📇 프로젝트 인덱스 (projects)
| 프로젝트 | 상태 | 스택 | 요약 |
|----------|------|------|------|
| [ha_api](./projects/ha_api/INDEX.md) | 진행중 | Java8 / Spring5.2 / Spring MVC + JSP(SiteMesh3) / MyBatis | 해피포인트 **앱** 백엔드 API 서버 (하이브리드 앱: 웹뷰 + REST). 홈페이지 프로젝트와 구분 |
| [ha-web-api](./projects/ha-web-api/INDEX.md) | 진행중 | Java21 / Spring6 / Jakarta / MyBatis / Tomcat10.1 | 신규 홈페이지 리뉴얼 Spring API 백엔드 (마이그레이션 작업물의 정식 귀속처) |
| [ha_web](./projects/ha_web/INDEX.md) | 유지(레거시) | Java8 / Spring5.2 / Spring MVC + JSP / Tomcat9 | 기존 홈페이지(레거시). 소스 원복 예정 |
| [ha-push-batch](./projects/ha-push-batch/INDEX.md) | 진행중 | **Java17 / Spring Boot 3.5 / Spring Batch / JdbcTemplate / Gradle** | 출석체크 리마인드 푸시 발송 배치(저장소명 `ha-push-batch`). ⚠️ KB 내 **유일한 Boot·Gradle 프로젝트**이자 MyBatis 미사용 |
| [ha_panel](./projects/ha_panel/INDEX.md) | 진행중 | Java8 / Spring MVC + JSP / MyBatis / **WebLogic** | 앱 설문 패널 서비스 **"패널KOK(SURVEY KOK)"** — 설문 참여 → 해피포인트 적립(저장소명 `ha_panel`, **언더스코어**). ⚠️ KB 내 유일한 **자체 SPA 프레임워크(AMP)** · **빌드 파일 부재** |
| [thehappy_ios](./projects/thehappy_ios/INDEX.md) | 진행중 | **Swift5 / iOS13+ / UIKit + Storyboard / MVVM + Combine** | 해피포인트 **iOS 네이티브 앱 `TheHappy`**(저장소명 `thehappy_ios`). 웹뷰 하이브리드 — 백엔드 짝은 `ha_api`. ⚠️ KB 내 **첫 비(非)JVM·클라이언트 프로젝트** → java/spring/sql 컨벤션 미적용 |
| [thehappy_aos](./projects/thehappy_aos/INDEX.md) | 진행중 | **Kotlin2.0 / minSdk26 / XML + ViewBinding / Activity+ViewModel+Repository / Gradle KTS** | 해피포인트 **Android 네이티브 앱 `TheHappy`**(저장소명 `thehappy_aos`). **`thehappy_ios`의 짝 — 구조가 1:1 대응**. ⚠️ **하드코딩 크리덴셜 Critical 1건** 검출 · release 난독화 비활성 |
| [gcs_fo](./projects/gcs_fo/INDEX.md) | 진행중 | **React18 / TypeScript4.9 / CRA + CRACO / TanStack Query v5 + Zustand** | 해피포인트 앱 내 **기프트카드(상품권) 웹뷰 프론트**(저장소명 `gcs_fo`, **언더스코어**). 충전·환불·현금영수증 등 **금전 거래 화면**. ⚠️ KB **최초 웹 프론트엔드** · **하드코딩 크리덴셜 Critical 1건** 검출 · 테스트/CI 0건. 백엔드 짝 = [gcs](./projects/gcs/INDEX.md) |
| [gcs](./projects/gcs/INDEX.md) | 진행중 | **Java21 / Spring Boot 3.4.2 / Gradle / JPA + QueryDSL / PostgreSQL17 / Redis(Redisson)** | 기프트카드 **백엔드 API 서버**(저장소명 `gcs`). **채널별(승인·월렛·판매·관리자·공통) API** 구조. 🟢 **ECC 적용 강도 최상위** — KB 최초 **JPA·PostgreSQL·Redis** 사용, **테스트 48개 실재**(KB 최대). ⚠️ **운영 크리덴셜 평문 커밋 Critical 1건** · **Spring Security 미사용**(커스텀 인터셉터 인증) · CI 0건 |

> 📱 **네이티브 앱 2종은 반드시 함께 본다**: [thehappy_ios](./projects/thehappy_ios/INDEX.md) ↔ [thehappy_aos](./projects/thehappy_aos/INDEX.md) 는 **같은 백엔드([ha_api](./projects/ha_api/INDEX.md))** 를 쓰고 파일명·줄수까지 대응하는 **동일 설계**다(`JavascriptBridge` 양쪽 902줄 등). 앱 이슈는 한쪽만 고치지 말고 **동기화 여부를 항상 확인**한다. 상세 대응표는 [thehappy_aos INDEX](./projects/thehappy_aos/INDEX.md#-ios--aos-구조-대응표-짝-프로젝트-대조용).

> 🎁 **기프트(GCS) 서비스는 프론트/백을 함께 본다**: [gcs_fo](./projects/gcs_fo/INDEX.md)(웹뷰 프론트) ↔ [gcs](./projects/gcs/INDEX.md)(백엔드). ✅ **2026-07-22 `gcs` 등록 완료**로 "서버 측 판정 불가" 제약이 해소됐다. 프론트의 토큰 발급(`axios.config.ts`)은 백엔드 `POST /v1/common/api/token` 과 직결되고, **CORS 실패 원인이 백엔드 `ApiAuthInterceptor` 의 하드코딩 Origin 목록**인 경우가 있으므로 **인증·CORS 이슈는 반드시 양쪽을 대조**한다. 웹뷰라 실제로는 앱 2종을 포함한 **3자 동기화** 대상이기도 하다.
> 🟢 **`gcs` 는 ECC 적용 강도가 KB 최상위다**: [ha-push-batch](./projects/ha-push-batch/INDEX.md)에 이은 **두 번째 Boot·Gradle** 프로젝트이자 **JPA·PostgreSQL·Redis를 실제로 쓰는 최초 프로젝트** → `jpa-patterns`·`postgres-patterns`·`redis-patterns` 가 **KB에서 처음으로 적용 대상을 갖게 됐다**. 또한 **테스트 48개가 실재**해 `tdd-workflow`·`verification-loop` 를 온전히 돌릴 수 있는 유일 프로젝트다(단 CI 부재로 로컬 수동). 상세: [ecc-reference §4-5](./shared/ecc-reference.md).

> ℹ️ **미등록 프로젝트**: 현재 IntelliJ 워크스페이스에는 `ha-admin`(관리자), `happypoint-web2` 가 남아 있다(인덱스 미작성). 작업이 발생하면 `templates/PROJECT_INDEX_TEMPLATE.md` 로 `projects/<slug>/INDEX.md` 를 추가한다. ✅ 종전 **우선순위 1위였던 `gcs` 는 2026-07-22 등록 완료**.
>
> ⚠️ **KB 스코프 확장(2026-07-22)**: 본래 이 KB는 **백엔드/앱서버** 전용이었으나 ① `thehappy_ios`·`thehappy_aos` 로 **네이티브 클라이언트(iOS·Android)**, ② `gcs_fo` 로 **웹 프론트엔드(React/TS)** 까지 포함하게 됐다. 클라이언트·프론트 프로젝트에는 `shared/conventions/{java,spring,sql-mybatis}.md` 와 `shared/server-env.md` 가 **적용되지 않는다**.
>
> 🔴 **횡단 취약 패턴(2026-07-22 갱신)**: **하드코딩 시크릿**이 `ha-web-api`·`ha-push-batch`·`ha_panel`·`thehappy_aos`·`gcs_fo`·**`gcs`** 까지 **6개 프로젝트 연속**으로 검출됐다. 언어·플랫폼(Java/Kotlin/TypeScript/**YAML 설정**)과 무관하게 나타나는 **조직 공통 패턴**으로 확정한다. 신규 프로젝트 진단 시 [security-review.md](./shared/security-review.md)의 시크릿 스윕을 **최우선 항목**으로 수행한다.
> - ⚠️ **`gcs` 에서 처음으로 "운영(real) 크리덴셜"이 나왔다** — 같은 파일에서 DB 비밀번호는 Jasypt `ENC()` 로 감쌌는데 AWS·PG 키만 평문이다. **암호화 수단이 이미 있는데 누락된** 유형이므로, 진단 시 "암호화 여부"가 아니라 **"모든 시크릿에 일관 적용됐는지"** 를 본다.
> - ⚠️ **GCS는 프론트·백 양쪽 끝에서 동시에 Critical 이 나왔다**([gcs_fo](./projects/gcs_fo/INDEX.md) 번들 인라인 / [gcs](./projects/gcs/INDEX.md) 평문 커밋) → 시크릿 관리를 **서비스 단위 과제**로 다룬다.
>
> 💰 **금전성 자산 프로젝트는 심각도를 한 단계 높인다**: [ha_panel](./projects/ha_panel/INDEX.md)(포인트 적립) · [gcs_fo](./projects/gcs_fo/INDEX.md) · **[gcs](./projects/gcs/INDEX.md)(상품권 충전·승인·환불·정산)**. 인증 우회가 곧 금전 손실로 직결된다. 특히 `gcs` 는 인증 보호가 **deny-by-default 가 아니라 `jwtSecuredUris` 열거식**이라 **신규 엔드포인트 등록 누락이 곧 공개 API**가 된다.

## 🧩 문서 작성 규칙
- 모든 문서 최상단에 **YAML 프론트매터**: `문서유형 / 프로젝트 / (이슈키) / 작성일 / 최종수정 / 작성자 / 상태 / 요약`.
- **문서유형**: `INDEX`(프로젝트/루트 허브) · `SHARED`(공통) · `ARCHIVE`(완료 기록) · `WORKLOG`(진행 기록).
- **네이밍**: `ARCHIVE-<WORK-이슈키>-<주제>.md`, `WORKLOG-<YYYYMMDD>-<주제>.md`.
- 새 문서는 `templates/` 의 해당 템플릿을 복사해 시작한다.
- 날짜는 절대표기(YYYY-MM-DD). **비밀번호·키·크리덴셜은 어떤 문서에도 적지 않는다**(별도 보안 저장소).

## 🖥️ 경로 표기 규칙 (상대경로 우선)
- KB 내 프로젝트 참조는 **워크스페이스 상대경로 / 프로젝트명**을 쓴다(OS·머신 독립).
- **워크스페이스 루트** = 이 KB(`md/`)의 **상위 폴더** — 모든 프로젝트(`ECC`, `ha-web-api`, `ha-admin` …)가 나란히 위치한다.
  - macOS: `/Users/joon/IdeaProjects/` · (과거) Windows: `…\happypointcard\`. 어느 환경이든 **폴더 배치는 동일**.
- 다른 프로젝트는 KB 기준 `../<프로젝트명>` 으로 가리킨다. 예: ECC=`../ECC`, 리뉴얼 백엔드=`../ha-web-api`.
- **절대경로는 상대화 불가한 경우에만** 남긴다: 원격 서버 배포경로(`/app/...`), 로컬 톰캣 설치본, 아카이브에 기록된 실제 실행 명령 등.

## 🔗 참조 (수정 금지)
- **ECC** (해커톤 우승자 컨텍스트, 읽기 전용): `../ECC` — 가이드 원문 `the-shortform-guide.md` / `the-longform-guide.md` / `the-security-guide.md`, 한국어 `docs/ko-KR/`.
