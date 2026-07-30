---
문서유형: INDEX
프로젝트: 공통(지식 베이스 루트)
작성일: 2026-07-21
최종수정: 2026-07-30
작성자: dominic
상태: 진행중
요약: happypointcard 백엔드/앱서버 개발 개인 지식 베이스의 루트 인덱스 — 작업 프로토콜·공통 문서·프로젝트 인덱스 허브 (2026-07-22 ha-push-batch·ha_panel·thehappy_ios·thehappy_aos·gcs_fo 등록 + **gcs 등록 = 미등록 우선순위 1위 해소 · KB 최초 JPA/PostgreSQL/Redis 프로젝트**)
---

# 📚 happypointcard 지식 베이스 (md)

> 🚨 **[최우선 · 상시 규칙] md 현행화는 "작업할 때마다" 즉시 한다.**
> 파일 생성·수정·명령 실행 등 **실제 작업을 수행하면, 그 즉시** 관련 프로젝트의 `INDEX.md`/`WORKLOG-*` 등 해당 문서를 갱신한다. 세션 끝까지 미루거나, 사용자가 "현행화 해"라고 말할 때까지 기다리지 않는다. **이 현행화는 별도 지시 없이 자동 수행하는 상시 작업**이다(실행 vs 확인 구분의 예외 — 프로토콜 6번 참조). 확정 사항·의사결정·미결 이슈도 그때그때 기록한다.

> dominic 개인 지식 베이스. `happypointcard` **백엔드 / 앱서버 개발**의 공통 규칙·서버 환경·프로젝트별 진행 기록을 모아 **모든 채팅에서 공통 참조**한다.
> 이 문서(`README.md`)는 지식 베이스의 **루트 허브**다. 하위 모든 문서가 `../README.md` / `../../README.md` 로 여기를 가리킨다.

## 🔑 작업 프로토콜 (최우선)
1. **학습 최우선순위 = ECC.** 새 채팅/작업 시작 시 ECC(해커톤 우승자 컨텍스트)의 관련 규칙·스킬을 **먼저 참조**한다.
2. **ECC를 근거로 사용자가 시킨 작업을 수행**한다.
3. 수행 결과·확정 사항을 **이 `md` 지식 베이스에 업데이트**한다(공통/프로젝트 지속 고도화). ⚠ **작업할 때마다 즉시** 갱신(상단 🚨 상시 규칙) — 미루지 않는다.
4. **ECC는 참조 전용(수정 금지), `md`는 갱신 대상.** 두 경로를 혼동하지 않는다.
5. **회고 기반 작업(중요)**: 새 요청을 받으면 해당 프로젝트의 **최근 3개월치 `monthly/TENDENCY-*` + `weekly/WEEKLY-*` 를 먼저 읽어** 작업 성향·진행 맥락·미결 과제를 파악한 뒤 진행한다. 매달 성향(TENDENCY)·매주 요약(WEEKLY)을 누적 작성한다.
6. **실행 vs 확인 구분(중요)**: 사용자가 **명시적으로 실행을 지시**("~해줘/만들어줘/적용해줘/바꿔줘/진행해")할 때만 **실제 작업(파일 생성·수정·이동·명령 실행)**을 수행한다.
   - **질문·확인·의견 요청**("이건 어때?", "이거 맞아?", "이거 확인해줘", "~할 수 있어?", "~하면 안 돼?")에는 **답변만** 하고 **실제 작업은 하지 않는다.** 필요하면 끝에 **"작업할까요?"** 로 물어보고, 사용자가 "해줘"라고 하면 그때 실행한다.
   - 애매하면 실행하지 말고 먼저 확인한다. (문서 현행화 등 사용자가 "수시로 하라"고 이미 지시한 항목은 예외로 자동 수행)
> 상세: [shared/ecc-reference.md](./shared/ecc-reference.md)

## 🗂️ 디렉토리 구조
```
md/
├─ README.md              ← (이 문서) 루트 허브
├─ shared/                공통 문서 (전 프로젝트·전 채팅 공통 적용)
│  ├─ ecc-reference.md    ECC 정체·작업 프로토콜·백엔드 매핑
│  ├─ server-env.md       개발/스테이징 서버(EC2·Tomcat) 공통 환경
│  ├─ security-review.md  보안 리뷰/취약점 진단 기준
│  └─ conventions/        기술별 코드 컨벤션 (java/spring/sql-mybatis/js/react/html-css) + api-response.md(전 프로젝트 API 응답 표준)
├─ templates/             문서 작성용 템플릿 (INDEX/ARCHIVE/WORKLOG/MEETING/TENDENCY/WEEKLY)
└─ projects/              프로젝트별 인덱스 + 아카이브 + 워크로그 + 회고(월/주)
   └─ <프로젝트>/
      ├─ INDEX.md         프로젝트 인덱스
      ├─ WORKLOG-*.md / MEETING-*.md
      ├─ archive/         완료 프로젝트 아카이브 ARCHIVE-*.md (크로스 건은 정본 1곳)
      ├─ monthly/         월별 작업성향  TENDENCY-YYYY-MM.md
      └─ weekly/          주차별 작업요약 WEEKLY-YYYY-Www.md (ISO주차, 상단에 날짜범위)
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
> | `happypoint-web2` | `happypoint-web2` | ✅ 동일 |
> | `ha_admin` | `ha-admin` (+`j-ha-admin`) | ⚠️ 언더스코어 |
> | `spc_batch` | `spc_batch` | ✅ 동일 (CodeCommit) |
> | `spc_spring_batch` | `spc_spring_batch` | ✅ 동일 (CodeCommit) |
>

## ⏱️ 운영 규칙 — 성향·동향·작업내역 주기 (2026-07-26 확정, 최우선)

> 🔴 **모든 작업 시작 전, 아래 "반영 범위"에 해당하는 문서를 먼저 읽고 맥락·성향을 반영한 뒤 진행한다.**
> 🔁 **모든 질문/작업 내역은 md 컨텍스트에 수시로 반영·업데이트한다.**

| # | 대상 | 저장 주기 | 저장 위치 | 작업 전 반영(읽기) 범위 |
|---|------|----------|----------|------------------------|
| 1 | **성향(전역)** | 월 단위 | `personal/tendency/monthly/TENDENCY-YYYY-MM.md` | 최근 **6개월** |
| 2 | **작업동향(전역)** | 주 단위 | `personal/worktrend/weekly/WORKTREND-YYYY-Www.md` | 최근 **3개월** |
| 3 | **성향(프로젝트)** | 주 단위 | `projects/<slug>/tendency/weekly/TENDENCY-YYYY-Www.md` | 최근 **3개월** |
| 4 | **작업내역(프로젝트)** | 주 단위 | `projects/<slug>/worklog/weekly/WORKLOG-YYYY-Www.md` | 최근 **3개월** |

- **전역 = 공통영역(`personal/`)** — 프로젝트 무관 개인 성향/동향. `personal/work-tendency.md`(KPI 기반 롤링 요약)는 유지하고, 월 스냅샷을 `tendency/monthly/`에 누적.
- **주차 표기**: ISO 주차 `YYYY-Www`(예: `2026-W30`). 월 표기: `YYYY-MM`.
- **작업 시작 시 읽기 순서**: ① 전역 성향(6개월) → ② 전역 작업동향(3개월) → ③ 해당 프로젝트 성향(3개월) → ④ 해당 프로젝트 작업내역(3개월).
- **저장 시점**: 성향/동향은 주기 종료 시 또는 유의미한 변화 발생 시, 작업내역은 작업 수시 누적(주 단위 파일에 append).
- 기존 `projects/<slug>/monthly/`·`weekly/` 문서는 이 규칙에 맞춰 `tendency/`·`worklog/`로 정리·이관(발생 시).

## 📄 공통 문서 (shared)
| 문서 | 상태 | 요약 |
|------|------|------|
| [ecc-reference.md](./shared/ecc-reference.md) | 진행중 | ECC 정체·핵심 규칙·해피포인트 백엔드↔ECC 스킬/에이전트 매핑 (참조 전용 안내) |
| [server-env.md](./shared/server-env.md) | 진행중 | 개발/스테이징 EC2·Tomcat 인스턴스·포트·DB(JNDI)·Scouter APM·배포 원칙 |
| [conventions/api-response.md](./shared/conventions/api-response.md) | 진행중 | **전 프로젝트 공통** API 응답 표준 — 엔벨로프·code 대역(00/01/50/70/80/99)·detailCode 규칙 (+ha-web-api 참조 구현) |
| [security-review.md](./shared/security-review.md) | 초안 | OWASP 기반 취약점 진단/보안 리뷰 개인 기준 + ECC 커밋 전 체크리스트·시크릿 스윕·대응 프로토콜·진단 이력 |
| [conventions/README.md](./shared/conventions/README.md) | 초안 | 기술별 코드 컨벤션 인덱스 (개발자 개인 공통 규칙) |

## 📇 프로젝트 인덱스 (projects)
| 프로젝트 | 상태 | 스택 | 요약 |
|----------|------|------|------|
| ⭐ [homepage-ai-renewal](./projects/homepage-ai-renewal/INDEX.md) | 진행중 | **(상위/엄브렐러)** Next.js16 프론트 + Spring6 백엔드 | **홈페이지 AI 리뉴얼** — 프론트([happypoint-web2](./projects/happypoint-web2/INDEX.md))·백엔드([ha-web-api](./projects/ha-web-api/INDEX.md))를 하나로 묶는 상위 프로젝트. 저장소 아님. 완료까지 지속 현행화 |
| [ha_api](./projects/ha_api/INDEX.md) | 진행중 | Java8 / Spring5.2 / Spring MVC + JSP(SiteMesh3) / MyBatis | 해피포인트 **앱** 백엔드 API 서버 (하이브리드 앱: 웹뷰 + REST). 홈페이지 프로젝트와 구분 |
| [ha-web-api](./projects/ha-web-api/INDEX.md) | 진행중 | Java21 / Spring6 / Jakarta / MyBatis / Tomcat10.1 | 신규 홈페이지 리뉴얼 Spring API 백엔드 (마이그레이션 작업물의 정식 귀속처) |
| [ha_web](./projects/ha_web/INDEX.md) | 유지(레거시) | Java8 / Spring5.2 / Spring MVC + JSP / Tomcat9 | 기존 홈페이지(레거시). 소스 원복 예정 |
| [ha-push-batch](./projects/ha-push-batch/INDEX.md) | 진행중 | **Java17 / Spring Boot 3.5 / Spring Batch / JdbcTemplate / Gradle** | 출석체크 리마인드 푸시 발송 배치(저장소명 `ha-push-batch`). ⚠️ KB 내 **유일한 Boot·Gradle 프로젝트**이자 MyBatis 미사용 |
| [ha_panel](./projects/ha_panel/INDEX.md) | 진행중 | Java8 / Spring MVC + JSP / MyBatis / **WebLogic** | 앱 설문 패널 서비스 **"패널KOK(SURVEY KOK)"** — 설문 참여 → 해피포인트 적립(저장소명 `ha_panel`, **언더스코어**). ⚠️ KB 내 유일한 **자체 SPA 프레임워크(AMP)** · **빌드 파일 부재** |
| [thehappy_ios](./projects/thehappy_ios/INDEX.md) | 진행중 | **Swift5 / iOS13+ / UIKit + Storyboard / MVVM + Combine** | 해피포인트 **iOS 네이티브 앱 `TheHappy`**(저장소명 `thehappy_ios`). 웹뷰 하이브리드 — 백엔드 짝은 `ha_api`. ⚠️ KB 내 **첫 비(非)JVM·클라이언트 프로젝트** → java/spring/sql 컨벤션 미적용 |
| [thehappy_aos](./projects/thehappy_aos/INDEX.md) | 진행중 | **Kotlin2.0 / minSdk26 / XML + ViewBinding / Activity+ViewModel+Repository / Gradle KTS** | 해피포인트 **Android 네이티브 앱 `TheHappy`**(저장소명 `thehappy_aos`). **`thehappy_ios`의 짝 — 구조가 1:1 대응**. ⚠️ **하드코딩 크리덴셜 Critical 1건** 검출 · release 난독화 비활성 |
| [gcs_fo](./projects/gcs_fo/INDEX.md) | 진행중 | **React18 / TypeScript4.9 / CRA + CRACO / TanStack Query v5 + Zustand** | 해피포인트 앱 내 **기프트카드(상품권) 웹뷰 프론트**(저장소명 `gcs_fo`, **언더스코어**). 충전·환불·현금영수증 등 **금전 거래 화면**. ⚠️ KB **최초 웹 프론트엔드** · **하드코딩 크리덴셜 Critical 1건** 검출 · 테스트/CI 0건. 백엔드 짝 = [gcs](./projects/gcs/INDEX.md) |
| [gcs](./projects/gcs/INDEX.md) | 진행중 | **Java21 / Spring Boot 3.4.2 / Gradle / JPA + QueryDSL / PostgreSQL17 / Redis(Redisson)** | 기프트카드 **백엔드 API 서버**(저장소명 `gcs`). **채널별(승인·월렛·판매·관리자·공통) API** 구조. 🟢 **ECC 적용 강도 최상위** — KB 최초 **JPA·PostgreSQL·Redis** 사용, **테스트 48개 실재**(KB 최대). ⚠️ **운영 크리덴셜 평문 커밋 Critical 1건** · **Spring Security 미사용**(커스텀 인터셉터 인증) · CI 0건 |
| [happypoint-web2](./projects/happypoint-web2/INDEX.md) | 진행중 | **Next.js 16 / React 19 / TypeScript / TailwindCSS v4 / pnpm / oracledb** | 신규 홈페이지 리뉴얼 **프론트엔드**(저장소명 `happypoint-web2`). PC/모바일 미들웨어 분리·계약 API(ha-web-api) 연동·로그인 BFF. 백엔드 짝 = [ha-web-api](./projects/ha-web-api/INDEX.md), 대체 대상 = [ha_web](./projects/ha_web/INDEX.md) |
| [ha_admin](./projects/ha_admin/INDEX.md) | 진행중 | Java8 / Spring MVC + JSP / MyBatis / Oracle / WAR | 해피포인트 **관리자(백오피스)** 웹(저장소명 `ha_admin`, **언더스코어**) |
| [spc_batch](./projects/spc_batch/INDEX.md) | 진행중 | Java / Maven (jar) — 상세 확인 필요 | SPC 배치(저장소 `spc_batch`, **AWS CodeCommit**) |
| [spc_spring_batch](./projects/spc_spring_batch/INDEX.md) | 진행중 | Java / Spring Batch(추정) — 상세 확인 필요 | SPC Spring Batch(저장소 `spc_spring_batch`, **AWS CodeCommit**) |

> 📱 **네이티브 앱 2종은 반드시 함께 본다**: [thehappy_ios](./projects/thehappy_ios/INDEX.md) ↔ [thehappy_aos](./projects/thehappy_aos/INDEX.md) 는 **같은 백엔드([ha_api](./projects/ha_api/INDEX.md))** 를 쓰고 파일명·줄수까지 대응하는 **동일 설계**다(`JavascriptBridge` 양쪽 902줄 등). 앱 이슈는 한쪽만 고치지 말고 **동기화 여부를 항상 확인**한다. 상세 대응표는 [thehappy_aos INDEX](./projects/thehappy_aos/INDEX.md#-ios--aos-구조-대응표-짝-프로젝트-대조용).

> 🎁 **기프트(GCS) 서비스는 프론트/백을 함께 본다**: [gcs_fo](./projects/gcs_fo/INDEX.md)(웹뷰 프론트) ↔ [gcs](./projects/gcs/INDEX.md)(백엔드). ✅ **2026-07-22 `gcs` 등록 완료**로 "서버 측 판정 불가" 제약이 해소됐다. 프론트의 토큰 발급(`axios.config.ts`)은 백엔드 `POST /v1/common/api/token` 과 직결되고, **CORS 실패 원인이 백엔드 `ApiAuthInterceptor` 의 하드코딩 Origin 목록**인 경우가 있으므로 **인증·CORS 이슈는 반드시 양쪽을 대조**한다. 웹뷰라 실제로는 앱 2종을 포함한 **3자 동기화** 대상이기도 하다.
> 🟢 **`gcs` 는 ECC 적용 강도가 KB 최상위다**: [ha-push-batch](./projects/ha-push-batch/INDEX.md)에 이은 **두 번째 Boot·Gradle** 프로젝트이자 **JPA·PostgreSQL·Redis를 실제로 쓰는 최초 프로젝트** → `jpa-patterns`·`postgres-patterns`·`redis-patterns` 가 **KB에서 처음으로 적용 대상을 갖게 됐다**. 또한 **테스트 48개가 실재**해 `tdd-workflow`·`verification-loop` 를 온전히 돌릴 수 있는 유일 프로젝트다(단 CI 부재로 로컬 수동). 상세: [ecc-reference §4-5](./shared/ecc-reference.md).

> ⚙️ **이벤트 템플릿 프로젝트는 `ha_api` ↔ `ha_admin` 을 함께 본다** (✅ 완료, 2026-07-28 아카이브 등록): 이벤트 개발을 개별 JSP에서 **설정 기반 Campaign Builder**로 전환한 과업. **1차(2025)** Rule Based 고도화(`EVENT_PROC_*`) → **2차(2026 상반기)** 프로모션폼 + Rule Based 클래스 바인딩(`EVENT_TMPL_*`). **BO 등록·페이지빌더 = [ha_admin](./projects/ha_admin/INDEX.md) / 앱 런타임·Rule 실행 = [ha_api](./projects/ha_api/INDEX.md)** 로 양쪽에 걸쳐 있어 한쪽만 고치면 안 된다. **정본 = [ha_api 아카이브](./projects/ha_api/archive/ARCHIVE-event-template.md)** — 크로스 프로젝트 **"정본 1곳 + 서브 INDEX 포인터"** 규칙의 첫 적용 사례다.

> ℹ️ **등록 현황(2026-07-26 현행화)**: 워크스페이스의 git 저장소를 모두 등록 완료 — `happypoint-web2`, `ha_admin`, `spc_batch`, `spc_spring_batch` 신규 추가. 로컬 전용 미체크아웃(`thehappy_ios`/`thehappy_aos`는 인덱스만 존재). ⚠️ `ECC`(github `affaan-m/ECC`)는 해피포인트 프로젝트가 아니라 컨텍스트/스킬 참조물 → [shared/ecc-reference.md](./shared/ecc-reference.md)에서 다룸(프로젝트 미등록). 신규 저장소는 `git remote get-url origin`의 저장소명으로 `projects/<slug>/INDEX.md` 추가.
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
- **문서유형**: `INDEX`(프로젝트/루트 허브) · `SHARED`(공통) · `ARCHIVE`(완료 기록) · `WORKLOG`(진행 기록) · `MEETING`(회의록).
- **네이밍**: `ARCHIVE-<WORK-이슈키>-<주제>.md`, `WORKLOG-<YYYYMMDD>-<주제>.md`, `MEETING-<YYYYMMDD>-<주제>.md`.
  - **회의록**: 회의 때마다 `MEETING-<YYYYMMDD>-<주제>.md` 로 각 프로젝트 폴더에 누적한다(`templates/MEETING_TEMPLATE.md` 복사). 회의 요약을 공유받으면 이 양식으로 기록한다.
- **완료 프로젝트 아카이브는 `projects/<프로젝트>/archive/` 에 모은다** (진행 문서와 성격이 달라 분리. `tendency/`·`worklog/` 서브폴더와 동일 패턴). 이슈키가 있으면 `ARCHIVE-<이슈키>-<주제>.md`, 없으면 `ARCHIVE-<주제>.md`.
  - ⚠️ 기존 플랫 배치 아카이브(`ha-web-api/ARCHIVE-WORK-16665-*.md`)는 링크 보존을 위해 그대로 두고, 해당 프로젝트에 아카이브가 늘어날 때 이동한다.
- **아카이브는 2계층 구조로 만든다 (2026-07-28 확정)** — 요약만으로는 "DDL·설계 상세"를 답할 수 없으므로 **허브 + 상세 번들**로 분리한다.
  ```
  archive/
  ├─ ARCHIVE-<주제>.md        ← 허브: 요약·연혁·번들 목차 (여기서 "언제/왜/무엇"에 답)
  └─ ARCHIVE-<주제>/          ← 상세 번들: 주제별 분할 (여기서 "DDL/명세/원본"에 답)
     ├─ 00-INDEX.md           ← 필수. 키워드→파일 매핑 = 검색 진입점
     ├─ 10-…, 20-…            연혁·범위
     ├─ 30-…, 40-…            설계·DDL·규격
     ├─ 50-…, 60-…            분석·화면
     ├─ 70-…, 71-…            검수·리스크
     └─ 90-source-manifest.md 원본 자료 위치·주의사항
  ```
  - **파일당 1MB 이내**(실질 10~60KB 목표) — grep·부분 읽기 효율 확보
  - **번호 prefix**로 주제군 구분·정렬. `00-INDEX.md` 는 **반드시** 두고 허브와 상호링크
  - **대용량 원본(데이터 샘플 등)은 번들에 넣지 않고 `90-source-manifest.md` 에 위치·주의사항만 기록**
  - 원본이 중복·padding 구조면 **큐레이션(주제별 재편성)** 하되, **DDL은 원문 보존**
  - 적용 사례: [ha_api 이벤트 템플릿](./projects/ha_api/archive/ARCHIVE-event-template.md) + [번들 16파일](./projects/ha_api/archive/ARCHIVE-event-template/00-INDEX.md)
- **크로스 프로젝트(여러 저장소에 걸친) 완료건은 "정본 1곳 + 상대 INDEX 포인터"** 로 관리한다. 양쪽 복사 금지(내용이 갈라짐).
  - 메인 프로젝트에 풀버전 아카이브를 두고, 프론트매터에 **`관련프로젝트:`** 필드로 서브 프로젝트를 명시한다(→ `grep "관련프로젝트"` 로 크로스 건 일괄 검색).
  - 서브 프로젝트 `INDEX.md` 문서목록에는 **정본을 가리키는 링크 행 1줄**만 추가한다.
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
