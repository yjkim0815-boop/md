---
문서유형: INDEX
프로젝트: 공통(지식 베이스 루트)
작성일: 2026-07-21
최종수정: 2026-08-03
작성자: dominic
상태: 진행중
요약: happypointcard 백엔드/앱서버 개발 개인 지식 베이스의 루트 인덱스 — 작업 프로토콜·공통 문서·프로젝트 인덱스 허브 (2026-08-03 과업 프로젝트 2건 신설[`sms-agent-replacement`·`store-search-upgrade`], 배치서버·검색서버 환경 등록, 프로젝트 목록 표시 규칙 6열 확정)
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

## ⏲️ 컨텍스트 활성화 정책 — 자동 주입과 수동 연결

- **자동 주입**: SessionStart 훅의 사용자 관리 화이트리스트에 등록된 항목만 자동 주입한다. 새 프로젝트·`ai/`·아카이브는 기본적으로 자동 주입하지 않으며, 화이트리스트 변경은 사용자만 지시한다.
- **수동 연결**: 사용자가 **`<프로젝트 또는 주제> 컨텍스트 연결해`** 라고 말하면 해당 범위의 정본·직접 관련 문서를 현재 대화에 연결한다. 예: `ai 컨텍스트 연결해`, `이벤트 템플릿 컨텍스트 연결해`.
- **유지 시간**: 수동 컨텍스트는 활성화 시점부터 **12시간** 유지한다. 기간 중에는 해당 범위를 참조하고, 확정된 결과는 해당 KB 문서에 기록한다. 실제 시스템·코드·설정 변경에는 별도 명시적 실행 지시가 필요하다.
- **만료**: 12시간이 지나면 해당 범위를 더 이상 자동 참조·기록하지 않는다. Codex는 해당 대화의 알림 자동화가 사용 가능한 경우 만료 알림을 예약하며, 모든 하네스는 다음 응답에서 만료 사실을 알린다. Claude Code의 독립 모바일 푸시는 별도 외부 알림 연동이 있어야 보장된다. 재사용하려면 같은 연결 명령으로 새 12시간을 시작한다.
- **대화 경계**: 수동 연결은 현재 대화에만 적용하며, 새 대화는 비활성으로 시작한다.

### 📋 프로젝트 목록 표시 규칙 (2026-08-03 확정 · Claude Code·Codex 공통)
사용자가 **"프로젝트 목록"**을 요청하면 아래 **6열 표**로 응답한다.

| 열 | 내용 |
|---|---|
| `No` | 일련번호 |
| `이름` | KB 슬러그 |
| `설명` | 한 줄 설명 + 핵심 스택 |
| `상태` | INDEX 프론트매터의 `상태:` 값 |
| **`컨텍스트 자동주입`** | 현재 세션에 자동 주입되는지 `예` 또는 `아니오` |
| `구분` | **`태스크`** 또는 **`프로젝트`** |

#### 용어 정의 (⚠️ 표기 고정)
| KB 실체 | **표기 용어** | 의미 |
|---|---|---|
| `projects/` 하위 **저장소** 단위 | **프로젝트** | Bitbucket·CodeCommit 저장소와 1:1 대응하는 코드베이스 |
| `projects/` 하위 **과업(엄브렐러)** 단위 | **태스크** | 저장소가 아닌 업무 단위. 여러 저장소·인프라에 걸치거나 코드 저장소가 없는 건 |

- ⚠️ 사용자 대면 표기는 **"저장소"·"과업"이 아니라 "프로젝트"·"태스크"** 를 쓴다.
- 📌 **정렬 규칙: `태스크`를 표 상단에, `프로젝트`를 그 아래에 배치한다.** 각 구분 내부는 최근 갱신순 또는 관련도순.

#### 표시명 (⚠️ `설명` 열 고정값 · 2026-08-03 확정)
목록의 `설명` 열에는 아래 **고정 표시명만** 쓴다. 벤더명·제품버전·상세 스택·부연설명(`— NDSoft NDMG → 섹타나인 v2.0.1`, `(Next.js16 / React19 / TS)` 등)을 덧붙이지 않는다.

**태스크**
| 슬러그 | **표시명(고정)** |
|---|---|
| `event-template` | **이벤트 템플릿** |
| `homepage-ai-renewal` | **홈페이지 AI 리뉴얼** |
| `sms-agent-replacement` | **SMS Agent 전환** |
| `store-search-upgrade` | **매장검색엔진 고도화 (와이즈넛->엘라스틱서치)** |

**프로젝트**
| 슬러그 | **표시명(고정)** |
|---|---|
| `happypoint-web2` | **홈페이지 리뉴얼 프론트 FO** |
| `ha-web-api` | **홈페이지 리뉴얼 백엔드 API** |
| `ha_api` | **해피포인트앱 백엔드 API (Spring MVC)** |
| `ha_web` | **해피포인트 홈페이지 (Spring MVC)** |
| `ha_admin` | **해피포인트 앱/웹 어드민** |
| `ha-push-batch` | **해피포인트 배치서버** |
| `ha_panel` | **해피포인트 패널 서비스 (설문)** |
| `thehappy_ios` | **해피포인트 네이티브 iOS** |
| `thehappy_aos` | **해피포인트 네이티브 AOS** |
| `gcs_fo` | 기프트카드 프론트 FO |
| `gcs` | 기프트카드 백엔드 API |
| `spc_batch` | SPC 배치 (CodeCommit) |
| `spc_spring_batch` | SPC Spring Batch (CodeCommit) |

> 스택·아키텍처 상세는 `설명` 열이 아니라 아래 [📁 프로젝트 목록](#-프로젝트-목록) 표의 `스택`·`요약` 열과 각 `INDEX.md` 에서 다룬다.

#### 목록 제외 대상 (⚠️ 2026-08-03 확정)
아래 항목은 **"프로젝트 목록" 응답 표에 표시하지 않는다.** 단 **KB 문서는 그대로 유지**하며, 해당 저장소를 직접 다루는 작업에서는 정상적으로 참조·갱신한다.

| 슬러그 | 제외 사유 |
|---|---|
| `spc_batch` | 상시 관리 대상 아님 (독립 스케줄러 묶음, 최근 커밋 2024-08) |
| `spc_spring_batch` | 상시 관리 대상 아님 (Anyframe Batch, 저장소 2019년 이후 정지) |

- 제외 항목은 목록 번호(`No`)에도 포함하지 않는다 → 현재 목록은 **태스크 4 + 프로젝트 11 = 총 15건**.
- 제외 대상 추가·해제는 **사용자 지시로만** 변경한다.

#### 컨텍스트 자동주입 열 규칙
- ⚠️ 열 이름은 **"컨텍스트 자동주입"** 이다. 수동 연결 여부와 잔여 시간은 표에 표시하지 않는다.
- `예`는 SessionStart 훅으로 해당 항목이 자동 주입되는 경우, `아니오`는 그 외 경우다.
- 현재 SessionStart 훅은 `README.md`·`shared/ecc-reference.md`만 고정 주입하므로, 개별 `projects/` 항목은 모두 `아니오`로 표기한다.

> ℹ️ **현재 훅 구현 상태(2026-08-03)**: `~/.claude/hooks/inject-readme.js` 는 `README.md` + `shared/ecc-reference.md` **2개 파일만 고정 주입**하며, **화이트리스트 구조가 없다.** 따라서 `projects/` 하위는 **전부 수동 주입 대상**이다. 위 "자동 주입" 항목의 화이트리스트 표현은 **향후 구현 예정 사항**이다.

## 🔄 Codex·Claude Code 공통 규칙 적용

- 사용자가 공통 규칙의 적용을 지시하면 **Codex와 Claude Code 양쪽에 적용 가능한지 먼저 판정**한다.
- 양쪽에 동일하게 적용 가능하면 전역 지침·공유 훅·설정 중 필요한 범위를 함께 반영하고, 양쪽 설정과 공유 파일 정합성을 검증한다.
- 기능·설정 형식·알림 방식처럼 하네스별 차이로 동일 적용이 불가능하거나 예외가 있으면, 적용 전에 또는 즉시 **차이와 영향 범위를 사용자에게 알린다**. 한쪽만 적용된 상태를 “공통 적용 완료”로 표현하지 않는다.
- 공유 훅을 바꿀 때는 `~/.codex/hooks/inject-readme.js`와 `~/.claude/hooks/inject-readme.js`를 byte-for-byte 동일하게 유지하고 양쪽 실행 가능 여부를 확인한다.

## 🗂️ 디렉토리 구조
```
md/
├─ README.md              ← (이 문서) 루트 허브
├─ shared/                공통 문서 (전 프로젝트·전 채팅 공통 적용)
│  ├─ ecc-reference.md    ECC 정체·작업 프로토콜·백엔드 매핑
│  ├─ server-env.md       개발/스테이징 서버(EC2·Tomcat) 공통 환경
│  ├─ security-review.md  보안 리뷰/취약점 진단 기준
│  └─ conventions/        기술별 코드 컨벤션 (java/spring/sql-mybatis/js/react/html-css) + api-response.md(전 프로젝트 API 응답 표준)
├─ ai/                    개인 AI 활용 — 하네스·컨텍스트·로컬 모델 (`ai 컨텍스트 연결해`로 12시간 수동 참조, 자동 주입 제외)
│  └─ README.md           역할·경계·단계적 구성 계획
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
   ├─ ha-push-batch/   해피포인트 배치서버 (Spring Boot3.5 / Java17 / Spring Batch)
   ├─ ha_panel/        앱 설문 패널 "패널KOK" (Spring MVC / Java8 / WebLogic / 자체 SPA=AMP)
   ├─ thehappy_ios/    해피포인트 iOS 네이티브 앱 (Swift5 / iOS13+ / UIKit / 웹뷰 하이브리드)
   ├─ thehappy_aos/    해피포인트 Android 네이티브 앱 (Kotlin2.0 / minSdk26 / XML+ViewBinding / 웹뷰 하이브리드)
   ├─ gcs_fo/          기프트카드 프론트 FO (React18 / TypeScript / CRA+CRACO) ← 앱 안에서 뜨는 화면
   ├─ gcs/             기프트카드 백엔드 API 서버 (Spring Boot3.4 / Java21 / JPA+QueryDSL / PostgreSQL) ← gcs_fo의 서버 짝
   ├─ homepage-ai-renewal/    홈페이지 AI 리뉴얼 (엄브렐러) ⚠️ task/ 이관 예정
   └─ task/                ★ 태스크(저장소 아닌 과업) 전용 폴더 — 2026-08-03 신설
      ├─ event-template/         이벤트 템플릿 (INDEX + archive/ 정본허브+번들16)
      ├─ sms-agent-replacement/  SMS Agent 전환 (INDEX + WORKLOG + worklog/weekly)
      └─ store-search-upgrade/   매장검색엔진 고도화 (와이즈넛 -> 엘라스틱서치) 2026-03
```

### 📂 태스크 폴더 관리 규칙 (2026-08-03 확정)
- **위치**: 태스크는 **`projects/task/<슬러그>/`** 아래 둔다. 저장소 프로젝트는 기존대로 `projects/<저장소명>/`.
- **폴더명**: 태스크 슬러그는 **저장소명이 아닌 과업명(kebab-case)** 을 쓴다 → 아래 [폴더명 규칙]의 **명시적 예외**.
- **내부 구조**: 프로젝트와 동일 (`INDEX.md` + `WORKLOG-YYYYMMDD-<주제>.md` + `worklog/weekly/`).
- **작업로그 위치**:
  - **대상 프로젝트(저장소)가 있는 태스크** → 작업로그는 **각 프로젝트 폴더**에 쌓고, 태스크 INDEX가 링크로 참조한다. (예: `homepage-ai-renewal` → `happypoint-web2`·`ha-web-api`의 `worklog/weekly/`)
  - **대상 저장소가 없는 태스크** → **태스크 폴더 안**에 `worklog/weekly/` 를 둔다. (예: `sms-agent-replacement` — 벤더 납품 바이너리라 저장소 없음)
- **이관 현황(2026-08-03)**: `sms-agent-replacement` · `store-search-upgrade` · `event-template` **이관 완료**. `homepage-ai-renewal` 은 **작업 진행 후 이관 예정**(사용자 지시).
> 📛 **폴더명 규칙(2026-07-22 변경 · 2026-08-03 예외 추가)**: `projects/` 하위 폴더명은 **Bitbucket 저장소명과 1:1로 일치**시킨다. ⚠️ **단 `projects/task/` 하위(태스크)는 예외** — 저장소가 없으므로 과업명 kebab-case 를 쓴다(위 [태스크 폴더 관리 규칙] 참조). 이전에는 로컬 임포트 폴더명 기반 `j-ha-*` slug를 썼으나, 머신마다 다를 수 있는 임포트명 대신 **원격 저장소라는 단일 기준**으로 통일했다. 신규 프로젝트 등록 시에도 `git remote get-url origin`의 저장소명을 그대로 쓴다.
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
| [atlassian-access.md](./shared/atlassian-access.md) | 진행중 | **Bitbucket·Jira·Confluence 접근 수단** — SSH 키(git)+API 토큰 2종의 저장 위치·조회법·엔드포인트·기능 범위·함정 (macOS/Windows 병기, 값은 미기록) + **API 호출 속도 제한** + 🔴 **App password 폐기 → git은 SSH 필수**(2026-08-02) |
| [git-sync-routine.md](./shared/git-sync-routine.md) | 진행중 | 🔄 **"비트버켓 페치 받아줘" 트리거 루틴** — 전체 fetch + 안전조건 충족분만 `pull --ff-only`. 판정 기준 8종·실행 절차·함정 |

> 🔄 **[트리거 규칙] "비트버켓 페치 받아줘"** → [shared/git-sync-routine.md](./shared/git-sync-routine.md) 절차를 수행한다. **먼저 전 저장소 fetch를 모두 완료하고, 그 결과를 기준으로 안전조건 충족분은 모든 로컬 추적 브랜치까지 fast-forward 반영**한다(현재 브랜치=`pull --ff-only`, 비체크아웃 브랜치=SSH refspec fetch). fetch 단계가 끝나기 전에는 브랜치 반영을 시작하지 않는다. 수정중·스테이징·**로컬 커밋(ahead>0)**·충돌·진행중작업·detached·upstream없음·diverged 는 **그냥 둔다**. 전제: **git 은 SSH 경로**(App password 폐기로 HTTPS 410).

> 🚦 **[상시 규칙] Bitbucket · Jira · Confluence API 와 Bitbucket SSH Git 요청은 초당 1회를 초과해 호출하지 않는다.** 연속 호출 사이에 **최소 1초** 간격을 둔다. 페이지네이션·저장소 순회 루프에 반드시 `sleep 1` 을 넣고, 병렬 호출은 금지한다. 호출 횟수 자체를 줄이려면 `pagelen=100`/`maxResults=100` 으로 페이지 크기를 키운다. 429 수신 시 즉시 중단하고 지수 백오프(1s→2s→4s). 상세: [shared/atlassian-access.md §3-1](./shared/atlassian-access.md), [shared/git-sync-routine.md](./shared/git-sync-routine.md).
| [conventions/api-response.md](./shared/conventions/api-response.md) | 진행중 | **전 프로젝트 공통** API 응답 표준 — 엔벨로프·code 대역(00/01/50/70/80/99)·detailCode 규칙 (+ha-web-api 참조 구현) |
| [security-review.md](./shared/security-review.md) | 초안 | OWASP 기반 취약점 진단/보안 리뷰 개인 기준 + ECC 커밋 전 체크리스트·시크릿 스윕·대응 프로토콜·진단 이력 |
| [conventions/README.md](./shared/conventions/README.md) | 초안 | 기술별 코드 컨벤션 인덱스 (개발자 개인 공통 규칙) |

## ✅ 태스크 목록
| 태스크 | 상태 | 대상 프로젝트 | 요약 |
|--------|------|---------------|------|
| [event-template](./projects/task/event-template/INDEX.md) | **완료(phase3 준비)** | [ha_api](./projects/ha_api/INDEX.md) + [ha_admin](./projects/ha_admin/INDEX.md) | **이벤트 템플릿** — 이벤트 개발을 개별 JSP에서 설정 기반 Campaign Builder로 전환. 1·2차(2025/2026 상반기) 완료, **Phase 3 준비 중**. 저장소 아님 |
| ⭐ [homepage-ai-renewal](./projects/homepage-ai-renewal/INDEX.md) | 진행중 | [happypoint-web2](./projects/happypoint-web2/INDEX.md) + [ha-web-api](./projects/ha-web-api/INDEX.md) | **홈페이지 AI 리뉴얼** — 프론트·백엔드를 함께 이행하는 과업. 저장소 아님 |
| [sms-agent-replacement](./projects/task/sms-agent-replacement/INDEX.md) | 진행중(분석) | 배치 서버 `/app/ndsoft` + 섹타나인 Agent | **SMS Agent 전환** — 현행 NDSoft에서 신규 Agent v2.0.1로 전환. 저장소 아님 |
| [store-search-upgrade](./projects/task/store-search-upgrade/INDEX.md) | 완료(잔여정리) | 검색 서버 Elasticsearch 8.19.12 | **매장검색엔진 고도화 (와이즈넛 -> 엘라스틱서치)** — SF-1 라이선스 만료 대응 전환. 저장소 아님 |

## 📁 프로젝트 목록
| 프로젝트 | 상태 | 스택 | 요약 |
|----------|------|------|------|
| [ha_api](./projects/ha_api/INDEX.md) | 진행중 | Java8 / Spring5.2 / Spring MVC + JSP(SiteMesh3) / MyBatis | 해피포인트 **앱** 백엔드 API 서버 (하이브리드 앱: 웹뷰 + REST). 홈페이지 프로젝트와 구분 |
| [ha-web-api](./projects/ha-web-api/INDEX.md) | 진행중 | Java21 / Spring6 / Jakarta / MyBatis / Tomcat10.1 | 신규 홈페이지 리뉴얼 Spring API 백엔드 (마이그레이션 작업물의 정식 귀속처) |
| [ha_web](./projects/ha_web/INDEX.md) | 유지(레거시) | Java8 / Spring5.2 / Spring MVC + JSP / Tomcat9 | 기존 홈페이지(레거시). 소스 원복 예정 |
| [ha-push-batch](./projects/ha-push-batch/INDEX.md) | 진행중 | **Java17 / Spring Boot 3.5 / Spring Batch / JdbcTemplate / Gradle** | 해피포인트 배치서버(저장소명 `ha-push-batch`). ⚠️ KB 내 **유일한 Boot·Gradle 프로젝트**이자 MyBatis 미사용 |
| [ha_panel](./projects/ha_panel/INDEX.md) | 진행중 | Java8 / Spring MVC + JSP / MyBatis / **WebLogic** | 앱 설문 패널 서비스 **"패널KOK(SURVEY KOK)"** — 설문 참여 → 해피포인트 적립(저장소명 `ha_panel`, **언더스코어**). ⚠️ KB 내 유일한 **자체 SPA 프레임워크(AMP)** · **빌드 파일 부재** |
| [thehappy_ios](./projects/thehappy_ios/INDEX.md) | 진행중 | **Swift5 / iOS13+ / UIKit + Storyboard / MVVM + Combine** | 해피포인트 **iOS 네이티브 앱 `TheHappy`**(저장소명 `thehappy_ios`). 웹뷰 하이브리드 — 백엔드 짝은 `ha_api`. ⚠️ KB 내 **첫 비(非)JVM·클라이언트 프로젝트** → java/spring/sql 컨벤션 미적용 |
| [thehappy_aos](./projects/thehappy_aos/INDEX.md) | 진행중 | **Kotlin2.0 / minSdk26 / XML + ViewBinding / Activity+ViewModel+Repository / Gradle KTS** | 해피포인트 **Android 네이티브 앱 `TheHappy`**(저장소명 `thehappy_aos`). **`thehappy_ios`의 짝 — 구조가 1:1 대응**. ⚠️ **하드코딩 크리덴셜 Critical 1건** 검출 · release 난독화 비활성 |
| [gcs_fo](./projects/gcs_fo/INDEX.md) | 진행중 | **React18 / TypeScript4.9 / CRA + CRACO / TanStack Query v5 + Zustand** | 해피포인트 앱 내 **기프트카드 프론트 FO**(저장소명 `gcs_fo`, **언더스코어**). 충전·환불·현금영수증 등 **금전 거래 화면**. ⚠️ KB **최초 웹 프론트엔드** · **하드코딩 크리덴셜 Critical 1건** 검출 · 테스트/CI 0건. 백엔드 짝 = [gcs](./projects/gcs/INDEX.md) |
| [gcs](./projects/gcs/INDEX.md) | 진행중 | **Java21 / Spring Boot 3.4.2 / Gradle / JPA + QueryDSL / PostgreSQL17 / Redis(Redisson)** | 기프트카드 **백엔드 API 서버**(저장소명 `gcs`). **채널별(승인·월렛·판매·관리자·공통) API** 구조. 🟢 **ECC 적용 강도 최상위** — KB 최초 **JPA·PostgreSQL·Redis** 사용, **테스트 48개 실재**(KB 최대). ⚠️ **운영 크리덴셜 평문 커밋 Critical 1건** · **Spring Security 미사용**(커스텀 인터셉터 인증) · CI 0건 |
| [happypoint-web2](./projects/happypoint-web2/INDEX.md) | 진행중 | **Next.js 16 / React 19 / TypeScript / TailwindCSS v4 / pnpm / oracledb** | 신규 홈페이지 리뉴얼 **프론트엔드**(저장소명 `happypoint-web2`). PC/모바일 미들웨어 분리·계약 API(ha-web-api) 연동·로그인 BFF. 백엔드 짝 = [ha-web-api](./projects/ha-web-api/INDEX.md), 대체 대상 = [ha_web](./projects/ha_web/INDEX.md) |
| [ha_admin](./projects/ha_admin/INDEX.md) | 진행중 | Java8 / Spring MVC + JSP / MyBatis / Oracle / WAR | 해피포인트 **관리자(백오피스)** 웹(저장소명 `ha_admin`, **언더스코어**) |

### 🚫 목록 제외 저장소 (문서는 유지 · "프로젝트 목록" 표에는 미표시)
| 프로젝트 | 상태 | 스택 | 요약 |
|----------|------|------|------|
| [spc_batch](./projects/spc_batch/INDEX.md) | 진행중 | Java / **Maven 단일 jar**(`hpc_batch`) / javax.mail · ojdbc6 | SPC 배치(**AWS CodeCommit**). **독립 실행형 스케줄러 묶음**(Spring Batch 아님) — 배너종료·배포·해피오더동기화·로또·메일발송(Slack/Telegram)·기상청 날씨/미세먼지·**매장 좌표변환(KATEC→위경도)**. 커밋 319, 최근 2024-08 |
| [spc_spring_batch](./projects/spc_spring_batch/INDEX.md) | 진행중(형상 정합 확인 필요) | **삼성SDS Anyframe Batch 1.0.0** / Java8 / 빌드파일 없음(lib 동봉) | SPC 배치(**AWS CodeCommit**). ⚠️ **이름과 달리 Spring Batch 아님**. ✅ **배치서버 `ip-10-0-70-71` 의 `/app/batch` 가동 소스로 확정**(2026-08-03, lib 목록 일치). 기상청 예보·미세먼지 수집. 🔴 **커밋 2개·2019년 이후 정지 + 서버의 `wthr/gov` 패키지가 저장소에 없음** → 형상관리 누락 의심 |

> 📋 **"프로젝트 목록" 응답 규칙 (요약 · 정본은 [§컨텍스트 활성화 정책 > 프로젝트 목록 표시 규칙](#-프로젝트-목록-표시-규칙-2026-08-03-확정--claude-codecodex-공통))**
> 사용자가 "프로젝트 목록"을 요청하면 태스크와 프로젝트를 **한 개의 Markdown 표**로 제공한다. 열 순서는 반드시 **`No | 이름 | 설명 | 상태 | 컨텍스트 주입 | 구분`** 이다.
> 설명 고정값: `sms-agent-replacement` = **SMS Agent 전환**, `ha-push-batch` = **해피포인트 배치서버**, `gcs_fo` = **기프트카드 프론트 FO**.
> - **이름**: KB 슬러그(영문, backtick 표기). **설명**: 사람이 읽는 한글 명칭 + 핵심 스택. **구분**: `태스크` 또는 `프로젝트`.
> - ⚠️ **`컨텍스트 주입`**(구 "컨텍스트 자동주입" 폐기): **주입 여부 + 잔여 시간**을 표기한다(예: `✅ 11h 24m`). 미주입은 `❌`. 상시 주입 대상은 `상시`. 잔여 시간은 **주입 시각 + 12시간** 기준.
> - **정렬**: **태스크를 먼저, 프로젝트를 다음에** 표시한다. 현재 고정 순서는 `event-template` → `homepage-ai-renewal` → `sms-agent-replacement` → `store-search-upgrade` → `happypoint-web2` → `ha-web-api` → `ha_api` → `ha_web` → `ha_admin` → `ha-push-batch` → `ha_panel` → `thehappy_ios` → `thehappy_aos` → `gcs_fo` → `gcs` 이다(**총 15건**).
> - 🚫 **제외**: `spc_batch` · `spc_spring_batch` 는 목록에 표시하지 않는다(문서는 유지). 상세는 위 [목록 제외 대상](#목록-제외-대상--2026-08-03-확정).
> - **태스크** = 코드 저장소가 아닌, 여러 프로젝트 또는 인프라 전환을 묶는 과업. **프로젝트** = 저장소 1:1 대응 코드베이스.
> - 현재 `projects/` 하위는 **전부 미주입**이 기본이며, `md/README.md`·`shared/ecc-reference.md`만 세션 시작 시 상시 주입된다.

> 📱 **네이티브 앱 2종은 반드시 함께 본다**: [thehappy_ios](./projects/thehappy_ios/INDEX.md) ↔ [thehappy_aos](./projects/thehappy_aos/INDEX.md) 는 **같은 백엔드([ha_api](./projects/ha_api/INDEX.md))** 를 쓰고 파일명·줄수까지 대응하는 **동일 설계**다(`JavascriptBridge` 양쪽 902줄 등). 앱 이슈는 한쪽만 고치지 말고 **동기화 여부를 항상 확인**한다. 상세 대응표는 [thehappy_aos INDEX](./projects/thehappy_aos/INDEX.md#-ios--aos-구조-대응표-짝-프로젝트-대조용).

> 🎁 **기프트(GCS) 서비스는 프론트/백을 함께 본다**: [gcs_fo](./projects/gcs_fo/INDEX.md)(웹뷰 프론트) ↔ [gcs](./projects/gcs/INDEX.md)(백엔드). ✅ **2026-07-22 `gcs` 등록 완료**로 "서버 측 판정 불가" 제약이 해소됐다. 프론트의 토큰 발급(`axios.config.ts`)은 백엔드 `POST /v1/common/api/token` 과 직결되고, **CORS 실패 원인이 백엔드 `ApiAuthInterceptor` 의 하드코딩 Origin 목록**인 경우가 있으므로 **인증·CORS 이슈는 반드시 양쪽을 대조**한다. 웹뷰라 실제로는 앱 2종을 포함한 **3자 동기화** 대상이기도 하다.
> 🟢 **`gcs` 는 ECC 적용 강도가 KB 최상위다**: [ha-push-batch](./projects/ha-push-batch/INDEX.md)에 이은 **두 번째 Boot·Gradle** 프로젝트이자 **JPA·PostgreSQL·Redis를 실제로 쓰는 최초 프로젝트** → `jpa-patterns`·`postgres-patterns`·`redis-patterns` 가 **KB에서 처음으로 적용 대상을 갖게 됐다**. 또한 **테스트 48개가 실재**해 `tdd-workflow`·`verification-loop` 를 온전히 돌릴 수 있는 유일 프로젝트다(단 CI 부재로 로컬 수동). 상세: [ecc-reference §4-5](./shared/ecc-reference.md).

> ⚙️ **이벤트 템플릿 프로젝트는 `ha_api` ↔ `ha_admin` 을 함께 본다** (✅ 완료, 2026-07-28 아카이브 등록): 이벤트 개발을 개별 JSP에서 **설정 기반 Campaign Builder**로 전환한 과업. **1차(2025)** Rule Based 고도화(`EVENT_PROC_*`) → **2차(2026 상반기)** 프로모션폼 + Rule Based 클래스 바인딩(`EVENT_TMPL_*`). **BO 등록·페이지빌더 = [ha_admin](./projects/ha_admin/INDEX.md) / 앱 런타임·Rule 실행 = [ha_api](./projects/ha_api/INDEX.md)** 로 양쪽에 걸쳐 있어 한쪽만 고치면 안 된다. **정본 = [event-template 태스크 아카이브](./projects/task/event-template/archive/ARCHIVE-event-template.md)** (2026-08-03 `task/` 이관) — 크로스 프로젝트 **"정본 1곳 + 서브 INDEX 포인터"** 규칙의 첫 적용 사례다.

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
  - 적용 사례: [이벤트 템플릿](./projects/task/event-template/archive/ARCHIVE-event-template.md) + [번들 16파일](./projects/task/event-template/archive/ARCHIVE-event-template/00-INDEX.md)
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
