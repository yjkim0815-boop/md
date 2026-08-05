---
문서유형: INDEX
프로젝트: event-template (태스크)
이슈키: HA25H101 · HA25H204 · HA26H197 (사내 과제) / WORK-2802 · SQD-853·862·863·864 · WORK-7213 [YAWJ-225] · YAWJ-284 (Jira)
작성일: 2026-08-03
최종수정: 2026-08-03
작성자: dominic
상태: 완료(Phase.1·2) · Phase.3 준비
요약: 이벤트 템플릿 프로젝트 — 이벤트 개발을 개별 JSP에서 설정 기반 Campaign Builder로 전환. 1차(2025) Rule Based 고도화 + 2차(2026 상반기) 프로모션폼·Rule Based 클래스 바인딩 완료, **Phase 3 준비 단계**. 크로스 프로젝트(ha_api + ha_admin), 2026-08-03 task/ 이관
---

# 📇 이벤트 템플릿 (event-template) — 태스크 인덱스

> ⚠️ **저장소가 아니라 과업(태스크)이다.** 실제 코드는 **[ha_api](../../ha_api/INDEX.md)**(앱 런타임·Rule 실행)와 **[ha_admin](../../ha_admin/INDEX.md)**(관리자 BO·페이지 빌더) 두 저장소에 있다. 한쪽만 보고 판단하지 않는다.
>
> 🔕 **자동 주입 제외.** 필요 시 `이벤트 템플릿 컨텍스트 연결해` 로 수동 연결(12시간).

## 과업 정의
| 항목 | 내용 |
|---|---|
| 명칭 | **이벤트 템플릿 프로젝트** (내부 Campaign Builder 고도화) |
| 목적 | 반복되는 이벤트 기능을 **설정 기반으로 전환**해 개발자 개입 최소화 |
| 1차 | **2025년** `HA25H101` — Rule Based 기능확장 + Admin Rule 등록 템플릿 고도화 (착수 2025-01-13, 16주) |
| 1차 후속기획 | `HA25H204` — 프로모션폼 시각화 **4단계 로드맵**(2차의 설계 원본) |
| 2차 | **2026 상반기** `HA26H197` Step2 — 프로모션폼 고도화 + **Rule Based 클래스 바인딩 컴포넌트** (2026-06-26 완료) |
| 투입 공수 | **총 645.0 h (80.6 MD)** — Phase.1 226.2h · Phase.2 376.4h · 안정화/부대 42.4h ([워크로그 집계](./WORKLOG-20260804-confluence-jira-inventory.md)) |
| 대상 프로젝트 | [ha_api](../../ha_api/INDEX.md) (메인·런타임) · [ha_admin](../../ha_admin/INDEX.md) (서브·BO) |
| DB | Oracle `SPCADMIN` — 1차 `EVENT_PROC_*` / 2차 `EVENT_TMPL_*` |
| 상태 | **완료** — Phase.1 **2025년 마무리** · Phase.2 **2026 상반기 완료**. Phase.3는 준비 단계. ⚠️ Jira `WORK-7213`·`WORK-15822` **티켓만 미마감**(작업은 완료) |

### 🔜 제공 로드맵 — 4단계 (2026-08-03 확정)

마케터 자립 범위를 넓히는 **프로모션폼 제공 단계**. 설명회 자료 작성 과정에서 확정됐다.

| 단계 | 제공 내용 | 상태 |
|---|---|---|
| **1단계** | **안내형**(버튼 없음, **통 이미지 1장**) + **1버튼형**(상·중·하 3장, **중앙 이미지에 Rule 연결**, **조건 없는** 단순 쿠폰/포인트 발급) | ✅ **제공 중** |
| **2단계** | **2버튼형** + **응모** / **클릭** Rule 추가 | 예정 |
| **3단계** | **이미지 영역 지정** — 자르지 않고 한 장 위에서 영역별 Rule 연결. 예: 상품 10개 나열 이미지에 **클릭 Rule 10개를 영역별로 설정** | 확장 |
| **4단계** | **참여형 프로모션폼** — 퀴즈 · 투표 · 출석체크 · 룰렛 | 계획 |

> 📌 **3단계가 이미지 분할 마찰을 해소한다.** 현재 1버튼형은 Rule 연결을 위해 상·중·하 3분할이 필요한데, 마케터가 통 이미지를 받아 직접 자르는 부담이 있다. 3단계(영역 지정)가 적용되면 **통 이미지 한 장으로 여러 Rule 연결이 가능**해져 분할 자체가 불필요해진다.
> 📌 **단계 순서는 수요에 따라 조정**한다. 반복 요청되는 유형이 곧 다음 템플릿 후보다.

#### 병행 과제 (단계와 무관)
- **class 규칙 통일**(`ha-btn-` vs `ha-rule-btn-` 혼재 해소 — 인수인계 리스크 #1)
- **참여 조건(허들) 개방** — 기간 내 1회·1일 1회 등. 1단계는 조건 없는 발급만 제공
- **GA4 · Amplitude 택소노미** 표준 설계안 자동 적용 (설명회에서 공표)
- Label 기능 독립 문서화 · API 명세/DTO/MyBatis 매핑·TC 문서화
- 성능·보안 검토, 사용자 매뉴얼
- 상세 후보: [ARCHIVE §9 후속 개선 후보](./archive/ARCHIVE-event-template.md)

### 📣 마케터 자립 전환 (2026-08-04 설명회 1차)
사업부 마케팅 담당자가 **직접 이벤트를 등록·오픈**하도록 전환하는 활동.

- **근거**: [HA26H197. 성과 요약](https://secta9ine.atlassian.net/wiki/spaces/eIPO7ntW5NBQ/pages/2158919868) — 최근 6개월 개발 이벤트 **248건 중 181건(72.9%)** 이 정형화 가능. 월평균 42건 중 약 30건.
- **핵심 메시지**: 템플릿은 완성품이 아니라 **출발점**. 마케터가 기본형 생성 → 필요 시 개발부문이 **커스터마이징**으로 기능을 얹음 → 반복되면 템플릿으로 흡수(선순환).
- **약속 사항**(미이행 시 신뢰 문제): 디자인 요청서 양식(상/버튼/하 3분할 + PNG 규격) · **디자인팀 3분할 납품 규격 협의**
- 자료: 아래 문서 목록의 Confluence 링크

> ⚠️ **2026-08-04 R&R 변경**: 이미지 분할을 **개발부문 도구 제공 → 디자인팀 납품**으로 넘겼다. "이미지 분할 도구(설치 불필요)" 약속은 **철회**됐고, 대신 디자인 요청 단계에서 3장으로 받는 구조가 된다. 분할 주체가 한 곳으로 고정돼 마찰 지점이 사라졌다.

> **본질**: JSP 완전 제거가 목적이 아니다. 반복 기능을 설정 기반으로 옮겨 **개발자 개입 영역을 줄이는 것**이 목표이며, 복합 조건은 여전히 `proc.jsp`가 처리한다.

### ✅ 설명회 1차 결과 (2026-08-04 14:00~15:00 · 마케팅기획팀 · 7층 1번 회의실)

| 항목 | 결과 |
|---|---|
| 반응 | **긍정적** |
| 수용 여부 | 마케터가 **직접 등록하겠다고 확답** |
| 후속 합의 | **개선사항은 마케터 측에서 정리해 전달**하기로 함 |

> 🎯 **이 과업의 성패 기준이 충족됐다.** 72.9%는 어디까지나 **기술적 가능성**이었고, 실제 성과는 **"마케터가 직접 하느냐"** 에 달려 있었다. 그 확답을 받았다.
>
> 🔜 **다음 병목은 기술이 아니라 계정이다.** 직접 하겠다고 해도 **관리자 계정이 없으면 시작할 수 없다.** 설명회 후속 항목 중 **계정 발급이 크리티컬 패스**로 올라섰다. 여기서 막히면 오늘의 긍정적 반응이 식는다.
>
> 📥 **개선사항 수렴 채널이 열렸다.** 들어오는 요청이 곧 **다음 템플릿 후보**이며(위 선순환 구조), **2단계 우선순위를 이 요청들로 정한다.** 회신이 늦으면 관심이 식으므로 취합·회신 주기를 짧게 가져간다.
>
> 📌 **어드민 실측 반영 필요**: 자료에 **Rule 저장 단계 누락**, "참여 조건 없음"과 화면 불일치, HTML/CSS/JS/PROC 탭 주의 안내 없음 — 3건은 미반영 상태다(일정 S-012).

## 📄 문서 — 정본은 아카이브에 있다
| 문서 | 내용 |
|---|---|
| ⭐ [ARCHIVE-event-template.md](./archive/ARCHIVE-event-template.md) | **정본 허브** — 개요·배경·1/2차 상세·데이터모델·리스크 |
| [번들 00-INDEX.md](./archive/ARCHIVE-event-template/00-INDEX.md) | **상세 번들 16파일** 진입점 (키워드→파일 매핑) |
| 📋 [WORKLOG-20260804 Confluence·Jira 자산 인벤토리](./WORKLOG-20260804-confluence-jira-inventory.md) | **자산 지도** — Phase.1 컨플 4건 + **Jira 81건** 전수. WBS·에픽 계층·참여인력·🔴 상태 불일치 |
| 🔗 [HA26H197. 이벤트 템플릿 설명회 1차](https://secta9ine.atlassian.net/wiki/pages/resumedraft.action?draftId=2199552076) (Confluence) | **초안** — 사업부 마케터 대상 설명회 자료(2026-08-04 14:00, 7층 1번 회의실). 작성 규격: [confluence-authoring.md](../../../shared/confluence-authoring.md) |

| 찾는 것 | 파일 |
|---|---|
| DDL 전문 | [30-ddl-event-tmpl](./archive/ARCHIVE-event-template/30-ddl-event-tmpl.md) · [31-ddl-event-proc](./archive/ARCHIVE-event-template/31-ddl-event-proc.md) |
| class 규칙·공통 JS | [21-class-binding-spec](./archive/ARCHIVE-event-template/21-class-binding-spec.md) |
| Rule 카탈로그(22종) | [40-rule-catalog](./archive/ARCHIVE-event-template/40-rule-catalog.md) |
| ERD·META_JSON·SQL | [32-erd-concept](./archive/ARCHIVE-event-template/32-erd-concept.md) · [33-meta-json-spec](./archive/ARCHIVE-event-template/33-meta-json-spec.md) · [34-operational-sql](./archive/ARCHIVE-event-template/34-operational-sql.md) |
| 1차/2차 상세 | [10-phase1](./archive/ARCHIVE-event-template/10-phase1-ha25h101.md) · [11-roadmap](./archive/ARCHIVE-event-template/11-roadmap-ha25h204.md) · [20-phase2](./archive/ARCHIVE-event-template/20-phase2-ha26h197.md) |
| AS-IS·BO화면 | [50-asis-analysis](./archive/ARCHIVE-event-template/50-asis-analysis.md) · [60-admin-screens](./archive/ARCHIVE-event-template/60-admin-screens.md) |
| 검수·리스크·원본 | [70-qa-checklist](./archive/ARCHIVE-event-template/70-qa-checklist.md) · [71-risks-followups](./archive/ARCHIVE-event-template/71-risks-followups.md) · [90-source-manifest](./archive/ARCHIVE-event-template/90-source-manifest.md) |

## 🔴 인수인계 리스크 (요약 · 상세는 [71-risks-followups](./archive/ARCHIVE-event-template/71-risks-followups.md))
| # | 이슈 | 요지 |
|---|---|---|
| 1 | **class prefix 혼재** | 설계는 `ha-btn-{slotNo}-{role}`, **운영 소스는 `ha-rule-btn-`** 일 수 있음 → **코드 수정 전 운영 소스 확인 필수** |
| 2 | slotNo 중복 | 동일 폼 내 중복 시 입력값/Rule 매핑 오류 |
| 3 | Rule-role 불일치 | CTA Rule에 Submit 요소 연결 등 |
| 4 | `EVENT_TMPL_FORM_HIST` 명칭 | 이력이 아니라 **임시 저장**용 |
| 5 | Bridge 단일 PK | `EVENT_SEQ` 단일 PK → 이벤트당 1폼만 |
| 6 | `EVENT_SEQ` 타입 불일치 | `EVENT.EVENTSEQ`=NUMBER vs `EVENT_TMPL_*`=VARCHAR2 |

## 📦 이관 이력
- **2026-07-28**: `ha_api/archive/` 에 완료 아카이브 등록(크로스 프로젝트 "정본 1곳 + 서브 포인터" 규칙 첫 적용)
- **2026-08-03**: 태스크 폴더 규칙 신설에 따라 **`projects/ha_api/archive/` → `projects/task/event-template/archive/`** 이관(`git mv`, 이력 보존). 정본 위치는 그대로 **아카이브 문서**이며, 이 INDEX는 태스크 진입점 역할만 한다.

## 참고 (공통 문서)
- [공유 KB README](../../../README.md)
- [shared/ecc-reference.md](../../../shared/ecc-reference.md)
- 관련 진행 문서: [ha_api WORKLOG-20260724 출석체크 개편](../../ha_api/WORKLOG-20260724-attendance-check-revamp.md)
