---
문서유형: ARCHIVE
상위문서: ../ARCHIVE-event-template.md
프로젝트: ha_api
관련프로젝트: ha_admin
작성일: 2026-07-28
최종수정: 2026-07-28
작성자: dominic
상태: 완료
요약: 2차 검수 체크리스트 전문 — 프로모션폼·Rule Based 컴포넌트·class 유효성
---

# ✅ 검수 체크리스트 (2차 `HA26H197`)

> 출처: 2차 최종 정본 "11. 검수 체크리스트". **재검증·회귀 테스트 시 그대로 재사용** 가능.

## 1. 프로모션폼

- [ ] 프로모션폼 **목록 정상 조회**
- [ ] 폼명 / 설명 표시
- [ ] **유형 뱃지 표시** (`FORM_TYPE_NM`)
- [ ] **미리보기 이미지 표시** (`PREVIEW_IMG_URL`)
- [ ] 선택 후 **Bridge 저장** (`EVENT_TMPL_BRIDGE`)
- [ ] 선택된 폼 조회
- [ ] **`PROMOTION_YN` 반영**
- [ ] **임시 HTML 저장** (`EVENT_TMPL_FORM_HIST`)
- [ ] **기존 기능 영향 없음** (회귀)

## 2. Rule Based 컴포넌트

**class 파싱**
- [ ] class 규칙 적용
- [ ] **slotNo 파싱**
- [ ] **role 파싱**

**트리거 인식**
- [ ] **CTA 클릭 인식**
- [ ] **Submit 클릭 인식**

**입력값 수집**
- [ ] Input 값 수집 (`ipt`)
- [ ] Select 값 수집 (`sel`)
- [ ] **Checkbox 배열 수집** (`chk`)
- [ ] **Radio 단일값 수집** (`rdo`)
- [ ] **Form serialize** (`frm`)

**Rule 실행**
- [ ] Rule 조회 (`EVENT_TMPL_RULE`)
- [ ] Rule Meta 조회 (`EVENT_TMPL_RULE_META`)
- [ ] **버튼 기간 체크** (`START_DT` ~ `END_DT`)
- [ ] **테스트 여부 체크** (`FLAG_TEST`)
- [ ] **성공 / 실패 결과 반영**

## 3. class 유효성

- [ ] **prefix 일치** (⚠️ `ha-btn-` vs `ha-rule-btn-` → [21](./21-class-binding-spec.md))
- [ ] **slotNo 자리수 일치** (3자리 `\d{3}`)
- [ ] **role 허용값 일치** (init/cta/sbm/ipt/frm/sel/chk/rdo)
- [ ] **동일 slotNo 중복 확인** (→ 리스크 [71](./71-risks-followups.md))
- [ ] **Rule-role 호환성 확인** (예: 단순 CTA Rule에 Submit 입력요소 연결 금지)
- [ ] Submit용 **입력 요소 누락 확인**
- [ ] **동적 HTML에서도 이벤트 위임 동작 확인**

## 4. 검수 시 권장 추가 항목 (ECC 기준 보강)
> 원문 체크리스트에는 없으나, [ECC `security-review`](../../../../../shared/security-review.md) 기준으로 금전성 기능에 필요한 항목.

- [ ] **중복 지급 방지** — 동일 사용자·동일 조건 재요청/동시요청(따닥) 시 1회만 처리되는지
- [ ] **정원·소진 처리** — `maxCnt` 초과 발급이 발생하지 않는지 (동시성)
- [ ] **본인 검증(IDOR)** — 타인 계정 대상 실행이 불가한지
- [ ] **Rule Meta 캐시(3분)** — BO 수정 후 반영 지연을 검수자가 인지하고 있는지
- [ ] **입력값 검증** — `ipt`/`frm` 수집값의 서버측 검증(길이·형식·XSS)
- [ ] **에러 메시지** — 실패 시 내부 정보(테이블·쿼리·스택) 노출 없는지

## 참고
- [상위 허브](../ARCHIVE-event-template.md) · [번들 인덱스](./00-INDEX.md)
- [21-class-binding-spec.md](./21-class-binding-spec.md) — 검수 대상 규칙
- [71-risks-followups.md](./71-risks-followups.md) — 검수에서 드러난 리스크
