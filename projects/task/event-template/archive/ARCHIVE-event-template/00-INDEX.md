---
문서유형: ARCHIVE
상위문서: ../ARCHIVE-event-template.md
프로젝트: ha_api
관련프로젝트: ha_admin
작성일: 2026-07-28
최종수정: 2026-07-28
작성자: dominic
상태: 완료
요약: 이벤트 템플릿 프로젝트 상세 번들 인덱스 — 키워드→파일 매핑 검색 진입점
---

# 🔍 이벤트 템플릿 상세 번들 — 인덱스

> **여기가 검색 진입점.** 요약·연혁은 [상위 허브 문서](../ARCHIVE-event-template.md), **상세 내용은 이 폴더**에 있다.
> 각 파일은 1MB 이내로 주제별 분할되어 있어 필요한 파일만 열면 된다.

## 파일 목록

| 파일 | 주제 | 이런 질문에 |
|------|------|-------------|
| [10-phase1-ha25h101.md](./10-phase1-ha25h101.md) | **1차(2025) 상세** — 착수·중간·개발DOC 판독 | "1차 때 뭐 만들었어?" "일정·진행률?" "신규 API 목록?" |
| [11-roadmap-ha25h204.md](./11-roadmap-ha25h204.md) | **HA25H204 4단계 로드맵** | "프로모션폼 계획이 원래 뭐였어?" "Phase2 단계 구분?" |
| [20-phase2-ha26h197.md](./20-phase2-ha26h197.md) | **2차(2026 상반기) 상세** — 프로모션폼·Label | "프로모션폼 기능?" "유형·미리보기?" "Label이 뭐야?" |
| [21-class-binding-spec.md](./21-class-binding-spec.md) | **클래스 바인딩 명세** — class·role·JS 함수 | "class 규칙?" "role 코드?" "공통 JS 함수?" "CTA/Submit 흐름?" |
| [30-ddl-event-tmpl.md](./30-ddl-event-tmpl.md) | **2차 `EVENT_TMPL_*` DDL 전문** (11테이블) | "DDL 보여줘" "컬럼 뭐야?" "PK가 뭐야?" |
| [31-ddl-event-proc.md](./31-ddl-event-proc.md) | **1차 `EVENT_PROC_*` DDL** | "기존 룰 테이블 구조?" "EVENT_PROC_BTN 컬럼?" |
| [32-erd-concept.md](./32-erd-concept.md) | **ERD + 개념구조 + 조회 축** | "테이블 관계?" "ERD 보여줘" "실행 흐름?" |
| [33-meta-json-spec.md](./33-meta-json-spec.md) | **META_JSON 스키마·예시·캐시** | "메타 JSON 구조?" "조건·메시지·리워드 설정?" "캐시 정책?" |
| [34-operational-sql.md](./34-operational-sql.md) | **운영 SQL 예시** | "버튼 조회 쿼리?" "프로모션폼 목록 쿼리?" |
| [40-rule-catalog.md](./40-rule-catalog.md) | **Rule 카탈로그 22종 + FUNC_ID 체인** | "룰 몇 종?" "어떤 룰 있어?" "룰 체이닝?" "BUTTON_TYPE 코드?" |
| [50-asis-analysis.md](./50-asis-analysis.md) | **AS-IS 분석** — JSP·동적테이블·업무흐름·현황표 | "예전엔 어떻게 했어?" "AS-IS 문제점?" "월 이벤트 몇 건?" |
| [60-admin-screens.md](./60-admin-screens.md) | **BO 화면·URL·리소스 경로 인벤토리** | "어드민 화면 URL?" "탭 구성?" "이미지 경로·S3?" |
| [70-qa-checklist.md](./70-qa-checklist.md) | **검수 체크리스트 전문** | "검수 항목?" "QA 뭐 확인했어?" |
| [71-risks-followups.md](./71-risks-followups.md) | **리스크 6건 + 후속 14건** | "미해결 이슈?" "주의할 점?" "다음에 뭐 해야 해?" |
| [90-source-manifest.md](./90-source-manifest.md) | **원본 자료 목록·위치·주의사항** | "원본 어디 있어?" "인코딩 문제?" "없는 문서?" |

## 주제별 빠른 찾기

**설계·구조** → 32(ERD) · 30/31(DDL) · 33(META_JSON)
**구현 규칙** → 21(class 바인딩) · 40(Rule 카탈로그) · 34(SQL)
**연혁·범위** → 10(1차) · 11(로드맵) · 20(2차)
**운영·화면** → 60(BO 화면) · 20(프로모션폼)
**품질·인수인계** → 70(검수) · 71(리스크) · 90(원본)

## ⚠️ 최우선 주의사항 (전 파일 공통)
1. **class prefix 혼재** — 설계문서 `ha-btn-{slotNo}-{role}` vs 실제 소스 `ha-rule-btn-{btnNo}-{role}` 가능. **코드 수정 전 운영 소스 확인 필수** → [21](./21-class-binding-spec.md)
2. **`EVENT_TMPL_FORM_HIST` 는 이력이 아니라 임시저장** 테이블 → [30](./30-ddl-event-tmpl.md)
3. **`EVENT_SEQ` 타입 불일치** — `EVENT.EVENTSEQ`(NUMBER) vs `EVENT_TMPL_*.EVENT_SEQ`(VARCHAR2), 물리 FK 없음 → [71](./71-risks-followups.md)
4. **크로스 프로젝트** — BO=`ha_admin`, 런타임=`ha_api`. 한쪽만 고치면 안 됨.

## 자료 신뢰 우선순위
① 2차 최종 정본(20260728) → ② v10(20260706) → ③ v9(20260617) → ④ v1~v7·원본 참고자료
→ 충돌 시 상위 기준. 상세: [90-source-manifest.md](./90-source-manifest.md)
