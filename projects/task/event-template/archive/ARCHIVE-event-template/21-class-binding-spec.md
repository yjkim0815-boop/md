---
문서유형: ARCHIVE
상위문서: ../ARCHIVE-event-template.md
프로젝트: ha_api
관련프로젝트: ha_admin
이슈키: HA26H197
작성일: 2026-07-28
최종수정: 2026-07-28
작성자: dominic
상태: 완료
요약: Rule Based 컴포넌트 클래스 바인딩 명세 — 표준 class·role 코드·공통 JS 함수·CTA/Submit 실행 흐름
---

# ⚙️ 클래스 바인딩 명세 (Rule Based 컴포넌트)

> 2차(`HA26H197`)의 핵심 산출물. `HA25H204` 로드맵 **3차·4차 단계**의 구현 결과.

## 🔴 최우선 주의 — class prefix 혼재
프로젝트 이력에 **두 형태가 공존**한다.

| 용도 | 형태 |
|------|------|
| **설계·보고서 문구** | `ha-btn-{slotNo}-{role}` (예: `ha-btn-001-cta`) |
| **실제 JSP / 전역 JS 구현** | `ha-rule-btn-{btnNo}-{role}` (예: `ha-rule-btn-01-cta`) 일 수 있음 |

기존 구현 메모:
```javascript
document.addEventListener(...)
→ ha-rule-btn-(01~99)-cta 매칭
→ fn_clickHaRuleBtnCta(btnNo)
```

> ⚠️ **새로 코드를 수정할 때는 현재 운영 소스의 class 규칙을 먼저 확인해야 한다.**
> 보고서에서는 개념 구조(`ha-btn-*`)를 설명하되, **개발 반영 시 실제 소스 기준으로 통일**한다.
> 대응: 공통 CSS/JS/JSP 일괄 통일, migration 시 **호환 selector** 검토.

## 1. 핵심 개념
프로모션폼 내 사용자 액션 요소에 **표준 class**를 부여하고, **공통 JavaScript**가 해당 class를 인식해 연결된 Rule을 실행.

```text
프로모션폼 HTML 요소
→ 표준 class
→ 공통 JS class 파싱
→ slotNo / role 추출
→ 버튼 / Rule 조회
→ Rule Meta 조회
→ Rule Handler 실행
→ 결과 반영
```

## 2. 표준 class 규칙

```text
ha-btn-{slotNo}-{role}
```

| 구분 | 설명 |
|------|------|
| `ha-btn` | Rule Based 컴포넌트 prefix |
| `slotNo` | 화면 내 버튼/컴포넌트 **슬롯 번호** (3자리) |
| `role` | 요소 **역할** |

### role 코드 (8종)
| role | 의미 |
|------|------|
| `init` | 페이지 진입 / 초기 상태 조회 대상 |
| `cta` | 단순 CTA Rule 실행 버튼 |
| `sbm` | 입력값을 수집한 후 Rule을 실행하는 **Submit** 버튼 |
| `ipt` | Input 값 |
| `frm` | Form serialize 대상 |
| `sel` | Select 값 |
| `chk` | Checkbox 값 |
| `rdo` | Radio 값 |

### 예시
```text
ha-btn-001-cta
ha-btn-002-sbm
ha-btn-002-ipt
ha-btn-002-frm
ha-btn-002-sel
ha-btn-002-chk
ha-btn-002-rdo
```

## 3. CTA Rule 실행

```html
<button type="button" class="ha-btn-001-cta">
    쿠폰 받기
</button>
```

```text
사용자 클릭
→ class 감지
→ slotNo = 001
→ role = cta
→ EVENT_SEQ + BTN_ID/slotNo로 버튼 조회
→ RULE_ID 확인
→ Rule Meta 확인
→ Rule Handler 실행
→ 결과 메시지 반영
```

## 4. Submit Rule 실행

```html
<input type="text" class="ha-btn-002-ipt" name="answer" />
<button type="button" class="ha-btn-002-sbm">
    정답 제출
</button>
```

```text
Submit 버튼 클릭
→ slotNo = 002
→ 동일 slotNo 입력 요소 탐색
→ input / select / checkbox / radio / form 값 수집
→ inputData 생성
→ Rule 실행
→ 결과 반영
```

> 💡 **동일 `slotNo` 로 버튼과 입력요소를 묶는 것**이 핵심 설계. 그래서 slotNo 중복이 곧 매핑 오류가 된다(→ [71](./71-risks-followups.md)).

## 5. 공통 JavaScript 구조

```text
HappyEventRule.init()
 ├─ initStatus()
 ├─ bindTrigger()
 ├─ parseHaBtnClass()
 ├─ collectInputData()
 ├─ executeRule()
 └─ applyResult()
```

### 5-1. `initStatus`
페이지 진입 시 초기 상태 조회:
- 참여 여부 · 발급 여부 · 소진 여부
- 사용 기간 · 테스트 여부
- **버튼 비활성화 / 문구 변경**

### 5-2. `bindTrigger`
- **document 이벤트 위임**
- **동적 HTML 대응**
- 각 버튼에 개별 listener를 붙이지 않음

### 5-3. `parseHaBtnClass`
class 목록에서 Rule class 탐색 → slotNo / role 파싱

```javascript
function parseHaBtnClass($el) {
    var classList = ($el.attr('class') || '').split(/\s+/);
    var regex = /^ha-btn-(\d{3})-(init|cta|sbm|ipt|frm|sel|chk|rdo)$/;

    for (var i = 0; i < classList.length; i++) {
        var matched = classList[i].match(regex);
        if (matched) {
            return {
                className: classList[i],
                slotNo: matched[1],
                role: matched[2]
            };
        }
    }

    return null;
}
```
> 정규식이 **slotNo 3자리(`\d{3}`)** 와 **role 화이트리스트**를 강제한다.

### 5-4. `collectInputData`
| role | 수집 방식 |
|------|-----------|
| `ipt` | input value |
| `frm` | form serialize |
| `sel` | selected value |
| `chk` | **checked value 배열** |
| `rdo` | checked value 단일 |

### 5-5. `executeRule`
Rule 실행 API로 전달하는 데이터:
- `EVENT_SEQ`
- `BTN_ID` 또는 `slotNo`
- `RULE_ID`
- `inputData`
- 인증 / 회원 정보
- Rule Meta

### 5-6. `applyResult`
예상 결과 처리: alert · 버튼 disable · 버튼 text 변경 · reload · redirect · 팝업 · 성공/실패 메시지 · 상태 갱신

## 6. class 유효성 검증 항목
- prefix 일치
- **slotNo 자리수 일치**(3자리)
- role 허용값 일치
- **동일 slotNo 중복 확인**
- **Rule-role 호환성 확인** (예: 단순 CTA Rule에 Submit 입력요소 연결 금지)
- Submit용 입력 요소 누락 확인
- **동적 HTML에서도 이벤트 위임 동작 확인**

→ 전체 검수 목록: [70-qa-checklist.md](./70-qa-checklist.md)

## 참고
- [상위 허브](../ARCHIVE-event-template.md) · [번들 인덱스](./00-INDEX.md)
- [30-ddl-event-tmpl.md](./30-ddl-event-tmpl.md) — `EVENT_TMPL_BTN` / `EVENT_TMPL_RULE(_META)`
- [33-meta-json-spec.md](./33-meta-json-spec.md) — Rule Meta 구조
- [40-rule-catalog.md](./40-rule-catalog.md) — 실행 대상 Rule 목록
