---
문서유형: ARCHIVE
상위문서: ../ARCHIVE-event-template.md
프로젝트: ha_api
관련프로젝트: ha_admin
작성일: 2026-07-28
최종수정: 2026-07-28
작성자: dominic
상태: 완료
요약: 이벤트 템플릿 운영 SQL 예시 — 버튼 조회·프로모션폼 목록·연결 조회·Rule Meta 조회
---

# 🔎 운영 SQL 예시

> 기준: v10(20260706) "운영 SQL 예시". 바인딩은 `:param` 표기이나 **프로젝트 정본은 MyBatis `#{}`** 이므로 실제 매퍼 작성 시 변환할 것 → [sql-mybatis 컨벤션](../../../../shared/conventions/sql-mybatis.md)

## 1. 이벤트별 사용 가능한 버튼 조회

```sql
SELECT EVENT_SEQ,
       BTN_ID,
       BTN_NM,
       RULE_ID,
       USE_YN,
       START_DT,
       END_DT,
       FLAG_TEST
FROM EVENT_TMPL_BTN
WHERE EVENT_SEQ = :eventSeq
AND USE_YN = 'Y'
AND SYSDATE BETWEEN START_DT AND END_DT
ORDER BY BTN_ID;
```
> 💡 **`SYSDATE BETWEEN START_DT AND END_DT`** 로 노출기간을 서버시각 기준 필터. `FLAG_TEST` 는 조회에 포함해 두고 **애플리케이션에서 테스터 여부와 대조**하는 구조.

## 2. 프로모션폼 선택 페이지 목록 조회

```sql
SELECT FORM_SEQ,
       FORM_NM,
       FORM_DESC,
       FORM_TYPE_NM,
       PREVIEW_IMG_URL,
       TARGET_RULE,
       ORDER_NUM
FROM EVENT_TMPL_FORM
WHERE USE_YN = 'Y'
ORDER BY ORDER_NUM, FORM_SEQ;
```
> `FORM_TYPE_NM`(유형 뱃지) · `PREVIEW_IMG_URL`(카드 이미지)이 **카드형 UI의 표시 데이터**.

## 3. 이벤트와 프로모션폼 연결 조회

```sql
SELECT B.EVENT_SEQ,
       B.EVENT_CHNL,
       B.FORM_SEQ,
       B.PROMOTION_YN,
       F.FORM_NM,
       F.FORM_TYPE_NM,
       F.PREVIEW_IMG_URL
FROM EVENT_TMPL_BRIDGE B
LEFT JOIN EVENT_TMPL_FORM F
       ON B.FORM_SEQ = F.FORM_SEQ
WHERE B.EVENT_SEQ = :eventSeq;
```
> **LEFT JOIN** — `FORM_SEQ` 가 NULL(폼 미선택 상태)일 수 있으므로 INNER JOIN 금지.

## 4. Rule Meta 조회

```sql
SELECT EVENT_SEQ,
       BTN_ID,
       RULE_ID,
       META_JSON
FROM EVENT_TMPL_RULE_META
WHERE EVENT_SEQ = :eventSeq
AND BTN_ID = :btnId
AND RULE_ID = :ruleId;
```
> PK 3개 전체를 조건으로 사용 → 단건 조회. 이 결과가 **약 3분 캐시** 대상 → [33](./33-meta-json-spec.md)

## 5. 인덱스 활용 메모
| 조회 | 활용 인덱스 |
|------|-------------|
| 버튼 목록(이벤트별) | `IDX_EVENT_TMPL_BTN_01 (EVENT_SEQ)` |
| Rule 역추적(룰별 버튼) | `IDX_EVENT_TMPL_BTN_02 (RULE_ID)` |
| Rule Meta 역추적 | `IDX_EVENT_TMPL_RULE_META_01 (RULE_ID)` |
| 폼 대상 Rule | `IDX_EVENT_TMPL_FORM_01 (TARGET_RULE)` |
| Rule 컴포넌트별 | `IDX_EVENT_TMPL_RULE_01 (COMPONENT)` |

## 참고
- [상위 허브](../ARCHIVE-event-template.md) · [번들 인덱스](./00-INDEX.md)
- [30-ddl-event-tmpl.md](./30-ddl-event-tmpl.md) · [32-erd-concept.md](./32-erd-concept.md)
