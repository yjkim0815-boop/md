---
문서유형: ARCHIVE
상위문서: ../ARCHIVE-event-template.md
프로젝트: ha_api
관련프로젝트: ha_admin
작성일: 2026-07-28
최종수정: 2026-07-28
작성자: dominic
상태: 완료
요약: 미해결 리스크 6건 상세 대응 + 후속 작업 후보 14건 — 인수인계 필수 문서
---

# ⚠️ 리스크 및 후속 과제

> **인수인계 필수.** 이 프로젝트를 이어받거나 코드를 수정하기 전에 반드시 읽을 것.

## 1. 미해결 리스크 6건

### 🔴 1-1. class 규칙 혼재 (최우선)
문서/설계와 실제 구현에서 **두 prefix 가 혼재**할 수 있다.
```text
ha-btn-           ← 설계·보고서 문구
ha-rule-btn-      ← 실제 JSP / 전역 JS 구현
```
**대응**
- **실제 운영 소스 기준 확인** (코드 수정 전 필수)
- 공통 CSS / JS / JSP **일괄 통일**
- 보고서 문구와 구현 문구 **구분**해 관리
- migration 시 **호환 selector** 검토 (두 형태 동시 지원 후 단계적 제거)

→ 상세: [21-class-binding-spec.md](./21-class-binding-spec.md)

### 🟠 1-2. slotNo 중복
같은 프로모션폼에서 **동일 `slotNo` 가 중복**되면 입력값/Rule 매핑 오류 발생.
> 원인: Submit 버튼과 입력요소를 **동일 slotNo 로 묶는 설계**이므로, 중복 시 엉뚱한 입력값이 수집된다.

**대응**
- **빌더 저장 전 중복 검증**
- 관리 화면 **자동 번호 부여**
- DOM 검사

### 🟠 1-3. Rule-role 불일치
예시:
- 단순 CTA Rule 에 **Submit 입력값 요소 연결**
- 퀴즈 Rule 에 **input 누락**
- Checkbox Rule 에 **radio 연결**

**대응**
- **Rule 마스터에 허용 role 정의**
- 저장 시 **유효성 검사**
- 화면에서 **허용 컴포넌트만 표시**

### 🟡 1-4. `FORM_HIST` 명칭 혼동
이름은 `_HIST` 지만 **실제 이력 누적용이 아니다**(임시 저장).
> PK가 `EVENT_SEQ`+`FORM_SEQ` → 조합당 1행만 존재.

**대응**
- **COMMENT 에 임시 저장 명시** (현재 반영됨)
- **API / 서비스명도 temp / draft 의미로** 사용
- 향후 **실제 이력 테이블과 분리** 설계

### 🟡 1-5. Bridge 단일 PK
현재 `EVENT_TMPL_BRIDGE` PK = **`EVENT_SEQ` 단일** → **이벤트당 프로모션폼 1개**만 연결 가능.
> `EVENT_CHNL` 컬럼은 이미 존재하나 PK에 미포함.

**향후 채널별 복수 폼이 필요해지면**
```text
EVENT_SEQ + EVENT_CHNL
```
또는
```text
EVENT_SEQ + FORM_SEQ + EVENT_CHNL
```
→ **구조 재검토 필요.** 채널 코드는 `OMBA`(해피앱) / `OHOD`(해피오더앱) / `OSCO`(해피마켓) / `HAPC`(홈PC) / `HAMO`(홈모바일) 5종.

### 🟡 1-6. `EVENT_SEQ` 타입 불일치
| 대상 | 타입 |
|------|------|
| `EVENT.EVENTSEQ` (기존) | **NUMBER** |
| `EVENT_TMPL_*.EVENT_SEQ` (신규) | **VARCHAR2(100)** |

**대응**
- **물리 FK 미적용**
- **논리 관계 유지**
- **Java / SQL 변환 기준 통일** (암묵적 형변환으로 인한 인덱스 미사용·성능 저하 주의)

---

## 2. 후속 작업 후보 14건

### 문서화 (1~5)
1. `HA26H197` 완료보고서 **최종 편집**
2. Rule Based 컴포넌트 연동 내용을 **Step2 본문에 통합**
3. **Label 완료보고 별도 문서화** (현재 KEEP 상태)
4. 프로모션폼 **화면 캡처 추가**
5. **Before/After 비교표** 추가

### 구현 검증 (6~7) ⭐ 우선
6. **실제 class 규칙 검증** (리스크 1-1 해소)
7. **공통 JS 함수명 실제 소스 기준 확정**

### 기술 문서 (8~10)
8. **API 명세 추가**
9. **DTO / VO / MyBatis 매핑 문서** 추가
10. **테스트 케이스 문서** 추가

### 배포·품질 (11~14)
11. 컨플루언스용 목차 / Expand 구성
12. **운영 배포 결과 추가**
13. **성능 / 보안 검토**
14. **사용자 매뉴얼 작성**

### 추가 제안 (ECC 기준)
- **프로모션폼 유형 확장** — 퀴즈 · 투표 · 난수 · 출석 · 스탬프 · 룰렛 · 댓글 · 설문
- **동시성·멱등성 검증** — 금전성 기능이므로 중복지급/정원초과 시나리오 테스트 ([70](./70-qa-checklist.md#4-검수-시-권장-추가-항목-ecc-기준-보강))
- **AS-IS 동적 리워드 테이블**(`EV_EN_*`) 통합 방안 검토 ([50](./50-asis-analysis.md#-동적-리워드-이력-테이블))

---

## 3. 신규 채팅/인수자 적용 컨텍스트

```text
프로젝트: 이벤트 템플릿 프로젝트 개발
업무번호: HA26H197 (2차) / HA25H101·HA25H204 (1차)
현재 단계: Step2 프로모션폼 및 Rule Based 컴포넌트 연동 완료, 후속 개발

핵심 구조:
- EVENT_TMPL_FORM       : 프로모션폼 마스터
- EVENT_TMPL_BRIDGE     : 이벤트-프로모션폼 연결
- EVENT_TMPL_FORM_HIST  : 프로모션폼 HTML 임시 저장 (이력 아님)
- EVENT_TMPL_BTN        : 버튼/컴포넌트 실행 단위
- EVENT_TMPL_RULE       : Rule 마스터
- EVENT_TMPL_RULE_META  : 실행 조건/메시지/리워드 JSON

클래스 바인딩:
- 보고서 기준: ha-btn-{slotNo}-{role}
- role: init, cta, sbm, ipt, frm, sel, chk, rdo
- 실제 소스에서 ha-rule-btn-* 사용 여부 확인 필요
- 공통 JavaScript가 class 파싱 후 Rule 실행

DDL 작성 형식:
- 스키마 prefix 미사용
- CREATE TABLE 내부 PK 미사용 → ALTER TABLE로 PK 분리
- 테이블 하나당 SQL 코드블록 하나
- COMMENT 포함
```

## 참고
- [상위 허브](../ARCHIVE-event-template.md) · [번들 인덱스](./00-INDEX.md)
- [70-qa-checklist.md](./70-qa-checklist.md) · [21-class-binding-spec.md](./21-class-binding-spec.md)
- [ECC 보안 리뷰 기준](../../../../../shared/security-review.md)
