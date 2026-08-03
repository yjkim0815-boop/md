---
문서유형: INDEX
프로젝트: event-template (태스크)
이슈키: HA25H101 · HA25H204 (1차, 2025) / HA26H197 (2차, 2026 상반기) · WORK-7213 [YAWJ-225] Phase.2
작성일: 2026-08-03
최종수정: 2026-08-03
작성자: dominic
상태: 완료(phase3 준비)
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
| 2차 | **2026 상반기** `HA26H197` Step2 — 프로모션폼 고도화 + **Rule Based 클래스 바인딩 컴포넌트** |
| 대상 프로젝트 | [ha_api](../../ha_api/INDEX.md) (메인·런타임) · [ha_admin](../../ha_admin/INDEX.md) (서브·BO) |
| DB | Oracle `SPCADMIN` — 1차 `EVENT_PROC_*` / 2차 `EVENT_TMPL_*` |
| 상태 | **완료(phase3 준비)** — 1·2차 완료(2026-07-28 아카이브 등록), **Phase 3 준비 단계** |

### 🔜 Phase 3 (준비 중)
1·2차 완료 후 이어질 차기 단계. **범위·일정 미확정** — 확정되면 이 절과 상태를 갱신한다.
후보는 [ARCHIVE §9 후속 개선 후보](./archive/ARCHIVE-event-template.md)의 항목들이다.
- 프로모션폼 **유형 확장**(퀴즈·투표·난수·출석·스탬프·룰렛·댓글·설문)
- **class 규칙 통일**(`ha-btn-` vs `ha-rule-btn-` 혼재 해소 — 인수인계 리스크 #1)
- Label 기능 독립 문서화 · API 명세/DTO/MyBatis 매핑·TC 문서화
- 성능·보안 검토, 사용자 매뉴얼

> **본질**: JSP 완전 제거가 목적이 아니다. 반복 기능을 설정 기반으로 옮겨 **개발자 개입 영역을 줄이는 것**이 목표이며, 복합 조건은 여전히 `proc.jsp`가 처리한다.

## 📄 문서 — 정본은 아카이브에 있다
| 문서 | 내용 |
|---|---|
| ⭐ [ARCHIVE-event-template.md](./archive/ARCHIVE-event-template.md) | **정본 허브** — 개요·배경·1/2차 상세·데이터모델·리스크 |
| [번들 00-INDEX.md](./archive/ARCHIVE-event-template/00-INDEX.md) | **상세 번들 16파일** 진입점 (키워드→파일 매핑) |

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
