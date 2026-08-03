---
문서유형: ARCHIVE
상위문서: ../ARCHIVE-event-template.md
프로젝트: ha_api
관련프로젝트: ha_admin
작성일: 2026-07-28
최종수정: 2026-07-28
작성자: dominic
상태: 완료
요약: 1차/AS-IS EVENT_PROC_* DDL — Rule·BTN·BRG 및 EVENT_PROC_BTN 컬럼 구성
---

# 🗄️ `EVENT_PROC_*` DDL (1차 / AS-IS Rule 엔진)

> 2차의 `EVENT_TMPL_*` 로 전환되기 전, **기존 Rule 엔진** 테이블. 현재도 레거시 이벤트가 참조할 수 있으니 **양쪽 체계를 구분**해서 볼 것.

## 요약

| 테이블 | PK | 역할 | DDL 원문 |
|--------|----|------|----------|
| `EVENT_PROC_RULE` | `RULE_ID`+`ORDER_NUM` | Rule 마스터 | ✅ 보유 |
| `EVENT_PROC_BTN` | `EVENT_SEQ`+`BTN_ID`(추정) | 이벤트별 버튼↔Rule 바인딩 | ❌ **원문 없음**(파일 오류) |
| `EVENT_PROC_BRG` | UNIQUE idx | 이벤트 간 연계(브리지) | ❌ 컬럼만 확인 |

---

## 1. EVENT_PROC_RULE

```sql
CREATE TABLE "EVENT_PROC_RULE" (
	"RULE_ID"      VARCHAR2(10)  NOT NULL ENABLE,
	"RULE_NM"      VARCHAR2(256),
	"ORDER_NUM"    NUMBER,
	"FUNC_ID"      VARCHAR2(10),
	"BUTTON_TYPE"  VARCHAR2(10),
	"RULE_KEYWORD" VARCHAR2(256),
	"RULE_DESC"    VARCHAR2(256),
	"USE_YN"       VARCHAR2(1),
	"INS_DT"       DATE DEFAULT SYSDATE,
	"INS_ID"       VARCHAR2(20)
) TABLESPACE "USERS";

CREATE UNIQUE INDEX "EVENT_PROC_RULE_PK"
ON "EVENT_PROC_RULE" ("RULE_ID", "ORDER_NUM");

ALTER TABLE "EVENT_PROC_RULE"
ADD CONSTRAINT "EVENT_PROC_RULE_PK" PRIMARY KEY ("RULE_ID", "ORDER_NUM")
USING INDEX "EVENT_PROC_RULE_PK" ENABLE;

COMMENT ON COLUMN EVENT_PROC_RULE.RULE_ID IS '룰 아이디';
COMMENT ON COLUMN EVENT_PROC_RULE.RULE_NM IS '룰 명';
COMMENT ON COLUMN EVENT_PROC_RULE.ORDER_NUM IS '순번';
COMMENT ON COLUMN EVENT_PROC_RULE.FUNC_ID IS 'FUNC_ID';
COMMENT ON COLUMN EVENT_PROC_RULE.BUTTON_TYPE IS 'BUTTON_TYPE';
COMMENT ON COLUMN EVENT_PROC_RULE.RULE_KEYWORD IS '키워드 (검색)';
COMMENT ON COLUMN EVENT_PROC_RULE.RULE_DESC IS '설명';
COMMENT ON COLUMN EVENT_PROC_RULE.USE_YN IS '사용여부';
COMMENT ON COLUMN EVENT_PROC_RULE.INS_DT IS '생성일';
COMMENT ON COLUMN EVENT_PROC_RULE.INS_ID IS '생성자';
```

### 1차 vs 2차 Rule 테이블 비교 (중요)
| 항목 | 1차 `EVENT_PROC_RULE` | 2차 `EVENT_TMPL_RULE` |
|------|----------------------|----------------------|
| PK | **`RULE_ID` + `ORDER_NUM`** | **`RULE_ID` 단일** |
| 실행 체인 | `ORDER_NUM` 으로 **여러 FUNC_ID 체이닝** (같은 RULE_ID가 복수 행) | `ORDER_NUM` 컬럼은 있으나 PK 아님 |
| 기능 식별 | **`FUNC_ID`** (FN-001 등) | **`COMPONENT` / `COMPONENT_NM`** |
| 버튼 유형 | **`BUTTON_TYPE`** (RAA/RCB 등 3자리) | 없음 (class `role` 로 대체) |
| 검색 | **`RULE_KEYWORD`** (파이프 구분) | `RULE_TYPE_NM` (표기용) |
| 설명 길이 | `VARCHAR2(256)` | `VARCHAR2(1024)` |

> 💡 **설계 변화의 핵심**: 1차는 **`FUNC_ID` 체인 + `BUTTON_TYPE` 코드**로 기능을 표현했고, 2차는 **`COMPONENT` + 표준 class role**로 옮겼다. 즉 **서버 코드 테이블 → 프론트 class 규약**으로 바인딩 지점이 이동했다.

## 2. EVENT_PROC_BTN

> 🔴 **DDL 원문 확보 불가.** 첨부파일 `02_이벤트 Rule Based EVENT_PROC_BTN 테이블.txt` 의 **내용이 `EVENT_PROC_RULE` DDL로 잘못 채워져 있음**(파일명 불일치).
> 아래는 **데이터 샘플 헤더에서 역추출한 컬럼 구성**이다.

| 컬럼 | 추정 타입 | 설명 |
|------|-----------|------|
| `EVENT_SEQ` | NUMBER | 이벤트 번호 |
| `BTN_ID` | VARCHAR2 | 버튼 ID (`BTN-01`, `BTN-02` …) |
| `BTN_NM` | VARCHAR2 | 버튼 명 |
| `USE_YN` | VARCHAR2(1) | 사용 여부 |
| `SDATE` / `EDATE` | VARCHAR2(8) | 시작·종료일 `YYYYMMDD` |
| `STIME` / `ETIME` | VARCHAR2(4) | 시작·종료시각 `HHMM` (예: `1000`, `2359`) |
| `FLAG_TEST` | VARCHAR2(1) | 테스트 여부 |
| `INS_DT` / `INS_ID` | DATE / VARCHAR2 | 등록일시·등록자 |
| `UPD_DT` / `UPD_ID` | DATE / VARCHAR2 | 수정일시·수정자 |
| `RULE_ID` | VARCHAR2(10) | **연결 Rule ID** (미설정 = 공백 가능) |

> ⚠️ **2차에서 `SDATE`/`EDATE`/`STIME`/`ETIME` 4개가 `START_DT`/`END_DT`(DATE) 2개로 통합**됐다. 마이그레이션 시 문자열→DATE 변환 규칙 확인 필요.
> 📌 데이터 샘플에는 `RULE_ID` 가 **비어 있는 행이 다수** → 초기엔 Rule 미연결 버튼(단순 표시용)도 존재했음.

## 3. EVENT_PROC_BRG (1차 신규, 2025-05-14)

> 개발DOC에 DDL 첨부. 컬럼 구성만 확인됨(전문 미보유).

| 컬럼 | 설명 |
|------|------|
| `EVENT_SEQ` | 이벤트 번호 |
| `BRIDGE_TYPE` | 브리지 유형 |
| `BRIDGE_SEQ` | 브리지 대상 번호 |
| `ISUE_TYPE` | 발급 유형 |

- **UNIQUE 인덱스 존재**
- 용도: **이벤트 간 연계(브리지)** — 한 이벤트의 참여가 다른 이벤트/발급으로 이어지는 관계 표현
- ⚠️ 2차의 `EVENT_TMPL_BRIDGE`(이벤트↔프로모션폼 연결)와 **이름이 비슷하지만 완전히 다른 목적**이다. 혼동 금지.

## 4. 관련 AS-IS 테이블

| 테이블 | 역할 |
|--------|------|
| `EVENT` | 이벤트 전체 마스터. PK `EVENTSEQ` (**NUMBER**) |
| `EVENT_OFFR_META` | 이벤트 전체 리워드 정보 |
| `EV_EN_{YYMMDD}_{seq}` | **이벤트별 리워드 이력 적재 테이블 — 동적 생성** (예: `EV_EN_260512_30537`) |

> 🔴 **`EVENT.EVENTSEQ` 는 NUMBER, `EVENT_TMPL_*.EVENT_SEQ` 는 VARCHAR2(100)** → 타입 불일치. **물리 FK 미적용, 논리 관계만 유지**. Java/SQL 변환 기준을 통일해야 한다(→ [71](./71-risks-followups.md)).
> 🔴 **리워드 이력이 이벤트마다 동적 테이블로 생성**되는 구조는 AS-IS의 핵심 부채다 → [50-asis-analysis.md](./50-asis-analysis.md)

## 참고
- [상위 허브](../ARCHIVE-event-template.md) · [번들 인덱스](./00-INDEX.md)
- [40-rule-catalog.md](./40-rule-catalog.md) — `EVENT_PROC_RULE` 실적재 데이터(룰 22종·FUNC_ID 체인)
- [30-ddl-event-tmpl.md](./30-ddl-event-tmpl.md) — 2차 체계
- [90-source-manifest.md](./90-source-manifest.md) — 파일 오류·인코딩 주의
