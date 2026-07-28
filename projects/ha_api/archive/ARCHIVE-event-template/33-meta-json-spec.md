---
문서유형: ARCHIVE
상위문서: ../ARCHIVE-event-template.md
프로젝트: ha_api
관련프로젝트: ha_admin
작성일: 2026-07-28
최종수정: 2026-07-28
작성자: dominic
상태: 완료
요약: EVENT_TMPL_RULE_META.META_JSON 스키마·전체 예시·캐시 정책
---

# 📋 `META_JSON` 명세

> 저장 위치: `EVENT_TMPL_RULE_META.META_JSON` (CLOB)
> PK: `EVENT_SEQ` + `BTN_ID` + `RULE_ID`
> 역할: **실행 조건 · 메시지 · 후처리 · 리워드**를 하나의 JSON으로 통합 (컬럼 폭발 방지)

## 1. 전체 예시

```json
{
  "msg": {
    "ok": "쿠폰이 발급되었습니다.",
    "dup": "이미 발급된 쿠폰입니다.",
    "fail": "발급 조건을 충족하지 않았습니다."
  },
  "cond": {
    "type": "PERIOD_N",
    "pCnt": 1,
    "dCnt": 1
  },
  "post": {
    "soldoutPtYn": "Y",
    "fcYn": "Y",
    "fcTm": "10:00"
  },
  "rwd": {
    "cpn": [
      {
        "offrId": "OFFR202606001",
        "campId": "CAMP202606001",
        "name": "6월 멤버십 쿠폰",
        "maxCnt": 10000
      }
    ],
    "pt": [
      {
        "amt": 1000,
        "mchtNo": "100000",
        "name": "대체 포인트",
        "maxCnt": 10000
      }
    ]
  }
}
```

## 2. 블록별 규격

### 2-1. `msg` — 상황별 메시지
| 키 | 의미 |
|----|------|
| `ok` | 성공 메시지 |
| `dup` | **중복(기발급/기참여)** 메시지 |
| `fail` | 조건 미충족 실패 메시지 |

> 💡 1차 착수보고의 **"Message Binding"** 개념이 여기로 구체화됐다.

### 2-2. `cond` — 실행 조건
| 키 | 의미 |
|----|------|
| `type` | 조건 유형 (예: `PERIOD_N` = 기간 내 N회) |
| `pCnt` | **기간(period) 허용 횟수** |
| `dCnt` | **일(day) 허용 횟수** |

관련 허들 개념(1차 Rule 카탈로그와 대응): 기간 내 1회 · 1일 1회 · 날짜지정 · 무제한 → [40](./40-rule-catalog.md)

### 2-3. `post` — 후처리
| 키 | 의미 |
|----|------|
| `soldoutPtYn` | **리워드 소진 시 대체 포인트 지급 여부** |
| `fcYn` | **선착순(first come) 적용 여부** |
| `fcTm` | 선착순 시작 시각 (`HH:mm`) |

> 💡 `soldoutPtYn` 은 1차에서 만든 **"리워드 소진 시 추가 포인트지급 API"** 와 연결된다 → [10](./10-phase1-ha25h101.md)

### 2-4. `rwd` — 리워드
**`cpn`(쿠폰) 배열**
| 키 | 의미 |
|----|------|
| `offrId` | 오퍼 ID |
| `campId` | 캠페인 ID |
| `name` | 표기명 |
| `maxCnt` | 최대 발급 수량 |

**`pt`(포인트) 배열**
| 키 | 의미 |
|----|------|
| `amt` | 지급 포인트 금액 |
| `mchtNo` | 가맹점 번호 |
| `name` | 표기명 |
| `maxCnt` | 최대 지급 수량 |

> 배열 구조라 **복수 리워드**(쿠폰 여러 종 / 소진 시 대체 포인트) 표현이 가능하다.

## 3. 런타임 캐시 정책

```text
DB 저장  : META_JSON CLOB
캐시 키  : EVENT_SEQ + BTN_ID + RULE_ID
예       : 30644:BTN-01:R1080
캐시 유지: 약 3분
BO 저장/반영 시 flush 고려
```

> ⚠️ **캐시 3분** 때문에 BO에서 Rule Meta를 수정해도 즉시 반영되지 않을 수 있다. 운영 문의("바꿨는데 안 바뀐다") 시 **1차 확인 지점**.

## 4. 설계 의도 · 주의
- **장점**: 조건·메시지·리워드가 Rule마다 제각각인데도 스키마 변경 없이 확장 가능
- **주의**: JSON이라 **DB 제약으로 검증 불가** → BO 저장 시 애플리케이션 레벨 유효성 검사가 필수
- **주의**: 키 이름이 축약형(`pCnt`, `fcTm`, `rwd`)이라 **신규 개발자 진입 장벽** → 이 문서를 규격 정본으로 참조

## 참고
- [상위 허브](../ARCHIVE-event-template.md) · [번들 인덱스](./00-INDEX.md)
- [30-ddl-event-tmpl.md](./30-ddl-event-tmpl.md#3-event_tmpl_rule_meta) — 테이블 DDL
- [21-class-binding-spec.md](./21-class-binding-spec.md) — `executeRule` 이 Meta를 전달
- [40-rule-catalog.md](./40-rule-catalog.md) — 조건 허들 유형
