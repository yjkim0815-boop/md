---
문서유형: ARCHIVE
프로젝트: ha_api
관련프로젝트: ha_admin
이슈키: HA25H101 · HA25H204 (1차, 2025) / HA26H197 (2차, 2026 상반기) · WORK-7213 [YAWJ-225] Phase.2
작성일: 2026-07-28
최종수정: 2026-07-28
작성자: dominic
상태: 완료
요약: 이벤트 템플릿 프로젝트 — 1차(2025) Rule Based 고도화 + 2차(2026 상반기) 프로모션폼·Rule Based 클래스 바인딩 컴포넌트. 이벤트 개발을 JSP 개별개발에서 설정(Configuration) 기반 Campaign Builder로 전환
---

# 📦 이벤트 템플릿 프로젝트 — 완료 아카이브

> **크로스 프로젝트 정본 문서.** 메인 = `ha_api`(해피포인트앱 API 서버, 런타임), 서브 = [`ha_admin`](../../../ha_admin/INDEX.md)(관리자 BO, 등록·빌더).
> 한쪽만 보고 판단하지 말고 **양쪽을 함께** 확인한다.

> 🔍 **상세 내용은 별도 번들에 있다** → **[ARCHIVE-event-template/00-INDEX.md](./ARCHIVE-event-template/00-INDEX.md)**
> 이 문서는 **요약·연혁 허브**다. DDL 전문·클래스 바인딩 명세·Rule 카탈로그·검수·원본 목록 등 **상세 질문은 번들 폴더를 검색**한다.
>
> | 찾는 것 | 파일 |
> |---------|------|
> | DDL 전문 | [30-ddl-event-tmpl](./ARCHIVE-event-template/30-ddl-event-tmpl.md) · [31-ddl-event-proc](./ARCHIVE-event-template/31-ddl-event-proc.md) |
> | class 규칙·공통 JS | [21-class-binding-spec](./ARCHIVE-event-template/21-class-binding-spec.md) |
> | Rule 카탈로그(22종) | [40-rule-catalog](./ARCHIVE-event-template/40-rule-catalog.md) |
> | ERD·META_JSON·SQL | [32-erd-concept](./ARCHIVE-event-template/32-erd-concept.md) · [33-meta-json-spec](./ARCHIVE-event-template/33-meta-json-spec.md) · [34-operational-sql](./ARCHIVE-event-template/34-operational-sql.md) |
> | 1차/2차 상세 | [10-phase1](./ARCHIVE-event-template/10-phase1-ha25h101.md) · [11-roadmap](./ARCHIVE-event-template/11-roadmap-ha25h204.md) · [20-phase2](./ARCHIVE-event-template/20-phase2-ha26h197.md) |
> | AS-IS·BO화면 | [50-asis-analysis](./ARCHIVE-event-template/50-asis-analysis.md) · [60-admin-screens](./ARCHIVE-event-template/60-admin-screens.md) |
> | 검수·리스크·원본 | [70-qa-checklist](./ARCHIVE-event-template/70-qa-checklist.md) · [71-risks-followups](./ARCHIVE-event-template/71-risks-followups.md) · [90-source-manifest](./ARCHIVE-event-template/90-source-manifest.md) |

## 1. 개요

| 항목 | 내용 |
|------|------|
| 프로젝트명 | 이벤트 템플릿 프로젝트 (내부 Campaign Builder 고도화) |
| 목적 | 반복되는 이벤트 기능을 **설정 기반으로 전환**하여 개발자 개입 최소화 |
| 1차 | **2025년** (`HA25H101`) — Rule Based 기능확장 + Admin Rule 등록 템플릿 고도화 + 이벤트 템플릿 플랫폼. 착수 2025-01-13, 16주 과업 (→ §3) |
| 1차 후속기획 | `HA25H204` — **프로모션폼 시각화 4단계 로드맵**(Phase 2 초안). **2차 과업의 설계 원본** (→ §3-1) |
| 2차 | **2026년 상반기** (`HA26H197` Step2) — **프로모션폼 고도화** + **Rule Based 클래스 바인딩 컴포넌트** (→ §4) |
| 관련 저장소 | **메인 `ha_api`** (앱 런타임·Rule 실행) · **서브 `ha_admin`** (BO 등록·페이지 빌더) |
| 대상 서비스 | 해피포인트앱 이벤트 (쿠폰·포인트·응모·클릭 등) |
| DB | Oracle — 1차 `EVENT_PROC_*` / 2차 `EVENT_TMPL_*` (스키마 `SPCADMIN`) |

### 프로젝트 본질 (중요)
> **JSP를 완전히 제거하는 것이 목적이 아니다.** 반복되는 이벤트 기능을 설정 기반으로 전환해 **개발자 개입이 필요한 영역을 줄이는 것**이 목표다.
> 마케터가 이미지 업로드·문구 입력·Rule 연결만으로 이벤트를 생성할 수 있는 환경을 지향한다. 복합 조건은 여전히 `proc.jsp`가 처리한다.

---

## 2. 추진 배경 (AS-IS 문제점)

### AS-IS 이벤트 개발 흐름
```text
마케팅/기획 요청(Jira JSM)
→ PPT 기획안
→ Figma 디자인
→ FE: eventView.jsp 개발
→ BE: eventProc.jsp 개발
→ Stage 검증
→ 운영 반영
```

### 상세 업무흐름 (MKT 프로모션)
```text
프로모션 기획안 전달 → FE 퍼블리싱 → 리소스 업로드 → 리워드 셋팅(Rule)
→ BE 기능개발 → 기획안 수정 → QA → 프로모션 오픈 → 수정 → 종료
```
→ 오류수정·기획변경 시 **다수의 되돌림 루프** 발생

### 문제점
- **이벤트별 개별 JSP 개발** — 반복 기능도 이벤트마다 재구현
- 이벤트마다 복합기능이 달라 **명확한 공수산정 불가**
- 주요 이벤트는 **기능·디자인 수정이 지속 발생 → 추가공수 누적**
- 리소스 반영이 **파일 업로드 방식**
- 화면 스크립트와 서버 처리 로직이 **분산**
- **개발자 의존도 증가** (운영자가 직접 구성 불가) · 이벤트 **복사·재사용 어려움**

> 참고: AS-IS 샘플 `eventView.jsp`(약 29KB) / `eventProc.jsp`(약 100KB) — 이벤트 1건당 이 규모의 JSP를 개별 작성.
> 리워드 이력도 **이벤트별 동적 테이블**(`EV_EN_{YYMMDD}_{seq}`)로 개별 생성해 왔다.

### 이벤트 현황 (착수보고 기준 · AS-IS 실측)
| 구분 | 월 건수 | FE 공수 | BE 공수 |
|------|--------:|---------|---------|
| 단순안내 | 20~30건 | 2H 이하 | – |
| 단순 리워드형(허들 유/무) | 10~20건 | 2~4H | – |
| 참여형(룰렛·퀴즈·투표·난수·게임·스탬프) | 4~8건 | 2~8H | 2~5H |
| MKT(대형·복합) | 2~4건 | 8~24H+ | 4~20H+ |

- 월 이벤트 총량 **약 36~62건**
- **BE 공수 불필요 구간(단순안내+단순 리워드형)이 월 30~50건** → 이미 Rule 등록만으로 처리 가능한 비중이 큼
- BE 개발 필요 구간은 월 6~12건 → **1차 Rule 확장이 겨눈 타깃 = 참여형 구간**(난수·출첵·스탬프·댓글·리워드 선택발급 등)

### 연계 시스템
| 시스템 | 역할 |
|--------|------|
| HPC | 회원·인증·포인트·승인 |
| CMS | 쿠폰 발급·관리 |
| POS | 매장 할인·결제 |
| 이벤트 서버 | 참여·리워드 오케스트레이션 |

---

## 3. 1차 — Rule Based 고도화 (2025, `HA25H101`)

### 과업 정보
| 항목 | 내용 |
|------|------|
| 과업명 | 해피포인트앱 **이벤트 Rule Based 고도화 + 이벤트 템플릿** (Phase 1) |
| 착수 | **2025-01-13** (착수보고 v1.0.0) |
| 참여 | 김영준(기획 및 개발) · 유지민(개발지원) |
| 문서 | 착수보고 · 중간보고 · 개발DOC 3종 |

### 목표
- 이벤트 기능(**백엔드 영역**)의 **자동화(Rule Based) 확장** → **백엔드 인적자원 확보**
- 템플릿 시스템으로 **기능 정형화** → 신뢰성 향상 + 업무절차 간소화
- 구조: **`BTN → RULE → Spring Service`**. 단순 응모·쿠폰발급·포인트지급은 Rule 처리, **복합조건은 `proc.jsp` 유지**

### 2단계 오픈 계획
1. **1차 오픈** — 이벤트 Rule Based **기능확장** + Admin **Rule 등록 템플릿 고도화**
2. **2차 오픈** — 이벤트 템플릿 **등록/관리 플랫폼** 구현

### 1차 완료 항목 (중간보고 기준 = 실제 구현 범위) ⭐
- **BO Rule 등록 템플릿 고도화**
- **리워드 소진 시 추가 포인트지급 API**
- **난수입력 참여횟수 API**
- **리워드 선택발급 API**
- **서비스(출첵·스탬프·댓글) 참여여부 API**

### 1차 진행/후속 항목
- BO 이벤트 템플릿: 등록 및 **마크업(Page Build Panel)** · **반영(발행) API**
- APP 템플릿 연동: 마크업&스타일 연동개발
- BO 이벤트 관리: 템플릿 등록관리 · 모니터링 · 테스터 관리 · 리소스 관리
- 검토 항목: **반영 히스토리 기반 롤백**, 소스코드 업로드

### 일정 실적
| 트랙 | 기간(16주 간트) |
|------|-----------------|
| 이벤트 Rule | 1w ~ 5w (25.01 ~ 25.02 초) |
| 이벤트 템플릿 | 6w ~ 14w (25.02 ~ 25.04 중) |
| 이벤트 관리 | 9w ~ 14w (25.03 ~ 25.04 중) |
| QA 및 배포 | 15w ~ 16w (25.04 말) |

- 중간보고 시점 **진행률 80% 완료 / 20% 잔여**, **파일럿 테스트 4월 둘째주**
- DDL 생성 스크립트 **250508**(`EVENT_TMPL_*`) · **250514**(`EVENT_PROC_BRG`) → 실제 오픈은 **2025-05 이후로 추정**

### 1차 데이터 모델
**기존 Rule 엔진 (`EVENT_PROC_*`)**
| 테이블 | PK | 주요 컬럼 |
|--------|----|-----------|
| `EVENT_PROC_RULE` | `RULE_ID`+`ORDER_NUM` | `RULE_NM`, **`FUNC_ID`**, **`BUTTON_TYPE`**, `RULE_KEYWORD`, `RULE_DESC`, `USE_YN` |
| `EVENT_PROC_BTN` | `EVENT_SEQ`+`BTN_ID`(추정) | `BTN_NM`, `SDATE`/`EDATE`, `STIME`/`ETIME`, **`FLAG_TEST`**, **`RULE_ID`** |
| `EVENT_PROC_BRG` | UNIQUE idx | `EVENT_SEQ`, `BRIDGE_TYPE`, `BRIDGE_SEQ`, `ISUE_TYPE` — **이벤트 간 연계(브리지), 2025-05-14 추가** |

**1차 신규 템플릿 테이블 (개발DOC, 스키마 `SPCADMIN`)**
`EVENT_TMPL_CONTENTS`(HTML/CSS/JS) · `EVENT_TMPL_CONTENTS_HIST`(PROFILE=PROD/STAGE/DEV, 발행이력·롤백 근거) · `EVENT_TMPL_ASSETS` · `EVENT_TMPL_TESTER` · `EVENT_TMPL_TESTER_SEQ`
→ **2차 `EVENT_TMPL_*` 체계의 기반이 1차에서 이미 설계됨**

### 룰 엔진 동작 방식
- 하나의 `RULE_ID`가 **`ORDER_NUM` 순서로 여러 `FUNC_ID`를 체이닝**
  - 예: `RULE-022` = ① `FN-407`(난수입력) → ② `FN-001`(CMS쿠폰발급) / `RULE-561` = 투표 → CMS쿠폰 / `RULE-402·412` = 신규회원체크 → CMS쿠폰
- `EVENT_PROC_BTN.RULE_ID` 로 버튼에 룰 바인딩 → **버튼 = 실행 단위**
- **룰 카탈로그**: 쿠폰받기(연계/직접등록) · CMS쿠폰발급 · 포인트발급 · 제휴쿠폰발급 · 난수제휴쿠폰 · 응모적재 · 클릭적재 · 신규회원체크 · 투표+CMS쿠폰 등 **22종**(샘플 27행) × 허들(**기간 내 1회 / 1일 1회 / 날짜지정 / 무제한**) 조합
- `RULE_KEYWORD` 는 `제휴쿠폰|기간내1회` 형태 **파이프 구분 검색 키워드**(BO 룰 검색·선택용)
- `BUTTON_TYPE` 은 `RAA`/`RCB`/`RPA`/`RLA`/`RNA` 등 **3자리 코드 체계**
- Rule 데이터 최초 적재 **2024-05** → 1차는 이 기반을 **확장·고도화**한 과업

### 1차 관리자 화면 (개발DOC 화면설계)
- **이벤트 관리** — 좌측 모바일 미리보기 + 우측 탭 **기본정보 / HTML / CSS / JS / RULE / 리소스**, 하단 저장 + 상단 **반영(발행)**
- **DOM Page 빌더** 탭 — HTML / CSS / JS / PROC
- 부가: 이벤트 리소스 관리(이미지 업로드 팝업) · 이벤트 모니터링(리스트/상세) · 테스터 관리

---

## 3-1. `HA25H204` — 프로모션폼 시각화 4단계 로드맵 (Phase 2 초안)

> ⭐ **2차(`HA26H197`) 과업의 설계 원본.** 1차 말미에 수립된 이 4단계 계획이 2026 상반기에 실행됐다.
> 연결 이슈: **WORK-7213 / [YAWJ-225] [EMP] 이벤트 템플릿 Phase.2** · 목표 "2025년 하반기 內"

| 단계 | 내용 | 2차 실행 결과 |
|------|------|---------------|
| 1차 | 이벤트 마크업(BO) **Label 기능** — Label 부여/필터링 + **기존 이벤트 복사** | ✅ `FORM_TYPE_NM` 유형 뱃지로 구현 |
| 2차 | **프로모션폼(form) 기본기능** — 양식 선택 페이지, 쉬운 UI → **개발인력 투입 없이 이벤트 셋팅** | ✅ Step2 프로모션폼 선택·연결 |
| 3차 | **Rule Based 컴포넌트 단위 모듈화 (클래스 바인딩)** — 클릭/조회/입력/체크 상호작용 기능화 | ✅ `ha-btn-{slotNo}-{role}` 표준 class |
| 4차 | **프로모션폼 + Rule Based 컴포넌트 연동** — 기능제한 제약 해소, 비정형 요구 대응 | ✅ Step2에서 연동 완료 |

- 부가 구상: 외부 API 등 **일회성 특수기능용 스크립틀릿** 제공
- 흐름: `프로모션폼 선택 → 폼 마크업 → 폼 커스터마이징` (필요 시 이벤트 마크업과 연동해 추가 커스터마이징)

---

## 4. 2차 — 프로모션폼 + Rule Based 클래스 바인딩 (2026 상반기, `HA26H197` Step2)

### 4-1. 프로모션폼 기능
**목적**: 이벤트 상세 화면에서 운영자가 **재사용 가능한 프로모션폼을 선택·연결**

| 기능 | 내용 |
|------|------|
| 프로모션폼 선택 | 카드형 UI · 폼명/설명 · **유형 뱃지** · **미리보기 이미지** |
| 프로모션폼 연결 | `EVENT` → `EVENT_TMPL_BRIDGE` → `EVENT_TMPL_FORM` |
| 임시 HTML 저장 | `EVENT_TMPL_FORM_HIST` (페이지 빌더 작업 중 임시 저장) |

- **유형**: 쿠폰 · 포인트 · 응모 · 클릭 (확장 후보: 퀴즈·투표·난수·출석·스탬프·룰렛·댓글·설문)
- **Label 기능**(유형 뱃지)은 `EVENT_TMPL_FORM.FORM_TYPE_NM` 으로 표시 → 검색·필터·복사 재사용성 향상

### 4-2. Rule Based 클래스 바인딩 컴포넌트 ⭐ (2차 신규)
프로모션폼 내 사용자 액션 요소에 **표준 class**를 부여하고, **공통 JavaScript**가 이를 파싱해 연결된 Rule을 실행하는 구조.

**표준 class 형식**
```text
ha-btn-{slotNo}-{role}
```
| 구분 | 설명 |
|------|------|
| `ha-btn` | Rule Based 컴포넌트 prefix |
| `slotNo` | 화면 내 버튼/컴포넌트 슬롯 번호 |
| `role` | 요소 역할 |

**role 코드**
| role | 의미 |
|------|------|
| `init` | 페이지 진입/초기 상태 조회 |
| `cta` | 단순 CTA Rule 실행 버튼 |
| `sbm` | 입력값 수집 후 Rule 실행(Submit) |
| `ipt` / `frm` | Input 값 / Form serialize 대상 |
| `sel` / `chk` / `rdo` | Select / Checkbox / Radio 값 |

> ⚠️ **class prefix 혼재 주의**: 설계·보고서 문구는 `ha-btn-{slotNo}-{role}` 이지만, **실제 운영 소스는 `ha-rule-btn-{btnNo}-{role}`** 형태일 수 있다(전역 JS가 `ha-rule-btn-(01~99)-cta` 매칭 → `fn_clickHaRuleBtnCta(btnNo)`). **코드 수정 시 반드시 현재 운영 소스 기준을 먼저 확인**한다.

**공통 JavaScript 역할**
`initStatus`(초기 상태) · `bindTrigger`(이벤트 위임) · `parseHaBtnClass`(class 파싱) · `collectInputData`(입력값 수집) · `executeRule`(Rule 실행) · `applyResult`(결과 반영)

### 4-3. Runtime 실행 흐름
```text
프로모션폼 HTML 요소
→ 표준 class
→ 공통 JS class 파싱 (slotNo/role 추출)
→ 버튼/Rule 조회 (EVENT_TMPL_BTN → EVENT_TMPL_RULE)
→ Rule Meta 조회 (EVENT_TMPL_RULE_META.META_JSON)
→ Rule Handler 실행
→ 결과 반영 (성공/중복/실패 메시지, 리워드·응모·클릭 적재)
```
- **동적 HTML에도 동작**하도록 **이벤트 위임** 방식 사용
- 버튼 **실행기간(`START_DT`/`END_DT`)·테스트여부(`FLAG_TEST`)** 체크 포함

---

## 5. 프로젝트별 변경 범위 (크로스)

### 🅰️ `ha_api` (메인 — 앱 런타임 / `front.happypointcard.com`)
- 프로모션폼 **렌더링** 및 표준 class 기반 **공통 JavaScript**
- **Rule 실행 API** — Rule/Rule Meta 조회 → Rule Handler 실행 → 결과 반환
- **1차 신규 API**: 리워드 소진 시 추가 포인트지급 · 난수입력 참여횟수 · 리워드 선택발급 · 서비스(출첵/스탬프/댓글) 참여여부
- 리워드 처리(쿠폰 발급·포인트 지급·응모/클릭 적재) 및 CMS/HPC 연계
- 착수보고상 역할: **"Event FRONT — WEB APP 內 WEB/API 개발"**
- 리소스 경로: `.../upfiles/common/event/EV_EN_/{YYYYMMDD}/{eventSeq}/*.png` (S3 버킷 `happy-app`)
- 관련 도메인(추정): `services/event` + 대응 `mybatis/**/event` mapper → **착수 시 짝으로 확인 필요**

### 🅱️ `ha_admin` (서브 — 관리자 BO / `admin.happypointcard.com`)
| 화면 | URL |
|------|-----|
| 이벤트 관리(기본정보/HTML/CSS/JS/RULE/리소스) | `/page/event/template-dom-mgmt.spc?eventSeq=...` |
| 이벤트 리소스 관리 | `/page/event/template-asset-mgmt.spc?eventSeq=...` |
| 이벤트 모니터링(리스트/상세) | `/page/event/template-monitoring-mgmt(-list).spc` |
| 테스터 관리 | `/page/event/template-tester-mgmt.spc` |

- **프로모션폼 선택 화면**(카드형 목록·유형 뱃지·미리보기)
- **Rule Based 관리 화면** — 버튼 선택, Rule 선택, 버튼 기본정보·실행기간·테스트여부, **Rule Meta 입력**
- **페이지 빌더** — 이벤트 마크업(HTML/CSS/JS) 등록, 임시 HTML 저장, Assets 업로드, **반영(발행)**/미리보기
- 테스터 관리(`EVENT_TMPL_TESTER`, `EVENT_TMPL_TESTER_SEQ`)
- `.spc` 확장자 + **`SPCADMIN` 스키마 소유** → 어드민 애플리케이션 소유 영역

> 💡 Rule/템플릿 정의 테이블은 **공용 DB(`SPCADMIN` 스키마)** 에서 양쪽이 참조하는 구조로 **추정**. 스키마 변경 시 양쪽 영향도를 함께 본다.

### BO 등록 흐름 (운영자)
```text
1. 프로모션폼 내 CTA/Submit 요소 확인 → 2. class/slotNo 확인
3. Rule Based 관리 화면에서 버튼 선택 → 4. 쿠폰/포인트/응모/클릭 Rule 선택
5. 버튼 기본정보 입력 → 6. 실행기간 설정 → 7. 테스트 여부 설정
8. Rule Meta 입력 → 9. 저장 → 10. 사용자 클릭 시 class 기반 Rule 실행
```

---

## 6. 데이터 모델 (2차 최종 · `EVENT_TMPL_*`)

### 개념 구조
```text
EVENT
 ├─ EVENT_TMPL_BTN
 │    ├─ EVENT_TMPL_RULE
 │    └─ EVENT_TMPL_RULE_META
 ├─ EVENT_TMPL_BRIDGE
 │    └─ EVENT_TMPL_FORM
 │         └─ EVENT_TMPL_FORM_HIST
 ├─ EVENT_TMPL_CONTENTS  (└─ EVENT_TMPL_CONTENTS_HIST)
 └─ EVENT_TMPL_ASSETS
```

### 테이블 역할
| 테이블 | 역할 | 비고 |
|--------|------|------|
| `EVENT_TMPL_BTN` | 버튼/컴포넌트 실행 단위 | `EVENT_SEQ`+`BTN_ID`(PK), `RULE_ID`, `START_DT`/`END_DT`, `FLAG_TEST` |
| `EVENT_TMPL_RULE` | Rule 마스터 | 쿠폰·포인트·응모·클릭·퀴즈·투표·난수·출석 등 |
| `EVENT_TMPL_RULE_META` | 실행조건·메시지·후처리·리워드 | `META_JSON CLOB` 통합 |
| `EVENT_TMPL_FORM` | 프로모션폼 마스터 | 폼명·설명·유형뱃지·미리보기·Header/HTML/Script |
| `EVENT_TMPL_BRIDGE` | 이벤트↔프로모션폼 연결 | `PROMOTION_YN` (기존 `MARKUP_YN` 미사용) |
| `EVENT_TMPL_FORM_HIST` | 프로모션폼 HTML **임시 저장** | ⚠️ 이름은 HIST지만 **이력 누적용 아님** |
| `EVENT_TMPL_CONTENTS` | 이벤트 마크업 | `CONTENTS_TYPE`(HTML/CSS/JS), CLOB |
| `EVENT_TMPL_CONTENTS_HIST` | 마크업 이력 | `PROFILE`(PROD/STAGE/DEV) 별 |
| `EVENT_TMPL_ASSETS` | 이미지 등 자산 | `EVENT_SEQ`+`ASSET_FILE_NM`(PK) |
| `EVENT_TMPL_TESTER(_SEQ)` | 테스터 관리 | 타입 100:개발자/200:담당자/300:관계자 |

### 2차 DDL 최종 변경점
```sql
-- EVENT_TMPL_FORM 추가
FORM_TYPE_NM     VARCHAR2(100 BYTE)  NOT NULL,  -- 유형 뱃지 표기용(쿠폰/포인트/응모/클릭)
PREVIEW_IMG_URL  VARCHAR2(1000 BYTE) NOT NULL   -- 미리보기 이미지 URL

-- EVENT_TMPL_BRIDGE
PROMOTION_YN VARCHAR2(1 BYTE) DEFAULT 'Y' NOT NULL   -- 기존 MARKUP_YN 대체

-- EVENT_TMPL_BTN : SDATE/EDATE/STIME/ETIME 제거 → START_DT/END_DT (DATE) 통합
```

### META_JSON 운영 기준
`msg`(성공/중복/실패 메시지) · `cond`(조건: 기간·일/기간 횟수) · `post`(후처리: 소진시 대체포인트·선착순 시각) · `rwd`(리워드: 쿠폰 `offrId`/`campId`/`maxCnt`, 포인트 `amt`/`mchtNo`)

**런타임 캐시**: 키 = `EVENT_SEQ + BTN_ID + RULE_ID` (예: `30644:BTN-01:R1080`), 유지 **약 3분**, BO 저장·반영 시 flush 고려

---

## 7. 기대 효과
- 이벤트 화면 구성 **표준화** + 유형별 프로모션폼 **재사용**
- 반복 JSP 개발 **공수 절감** (정형화 가능한 이벤트를 템플릿으로 대체)
- 운영자·마케터의 **직접 구성 가능** 범위 확대 → 개발자 의존도 감소
- Rule·화면·실행로직의 **역할 분리**로 유지보수성 향상

> 📊 정량 효과(정형화 가능 이벤트 비율·개발공수/비용 절감액)는 **별도 통계자료 기준으로 산출**되었으며 본 문서에는 미기재. 필요 시 해당 통계 원본 참조.

---

## 8. 리스크 및 개선 과제 (인수인계 필수)

| # | 이슈 | 내용 | 대응 |
|---|------|------|------|
| 1 | **class 규칙 혼재** | `ha-btn-` vs `ha-rule-btn-` 두 prefix 공존 | 운영 소스 기준 확인 → 공통 CSS/JS/JSP 일괄 통일, migration 시 호환 selector |
| 2 | **slotNo 중복** | 동일 폼 내 중복 시 입력값/Rule 매핑 오류 | 빌더 저장 전 검증, 관리화면 자동 번호 부여 |
| 3 | **Rule-role 불일치** | CTA Rule에 Submit 요소 연결, 퀴즈 Rule에 input 누락 등 | Rule 마스터에 **허용 role 정의** + 저장 시 유효성 검사 |
| 4 | **FORM_HIST 명칭 혼동** | 이력이 아니라 임시 저장 | COMMENT/서비스명을 temp·draft 의미로 정정 |
| 5 | **Bridge 단일 PK** | `EVENT_SEQ` 단일 PK → 이벤트당 1폼만 | 채널별 복수 폼 필요 시 `EVENT_SEQ + EVENT_CHNL` 로 재검토 |
| 6 | **EVENT_SEQ 타입 불일치** | `EVENT.EVENTSEQ`=NUMBER vs `EVENT_TMPL_*.EVENT_SEQ`=VARCHAR2 | 물리 FK 미적용·논리 관계 유지, Java/SQL 변환 기준 통일 |

### 검수 체크리스트 (요약)
- **프로모션폼**: 목록 조회 · 유형뱃지 · 미리보기 · Bridge 저장 · `PROMOTION_YN` 반영 · 임시 HTML 저장 · 기존 기능 영향 없음
- **Rule Based**: class/slotNo/role 파싱 · CTA·Submit 인식 · Input/Select/Checkbox(배열)/Radio 수집 · Form serialize · Rule·Meta 조회 · 기간·테스트 체크 · 결과 반영
- **class 유효성**: prefix·slotNo 자리수·role 허용값 · slotNo 중복 · Rule-role 호환성 · 동적 HTML 이벤트 위임

---

## 9. 후속 개선 후보
1. Rule Based 컴포넌트 연동을 Step2 본문에 통합 / **Label 기능 독립 문서화**
2. **실제 class 규칙 검증 및 공통 JS 함수명 확정**(리스크 #1 해소)
3. API 명세 · DTO/VO/MyBatis 매핑 · 테스트 케이스 문서화
4. Before/After 비교표 · 화면 캡처 추가
5. 성능/보안 검토, 사용자 매뉴얼 작성
6. 프로모션폼 유형 확장(퀴즈·투표·난수·출석·스탬프·룰렛·댓글·설문)

---

## 10. 원본 자료 (외부 보관)

> ⚠️ 원본은 KB 밖 로컬에 있다. 대용량(데이터 샘플 최대 약 80MB)이라 KB에 포함하지 않는다.
> 위치: 로컬 다운로드 폴더 `이벤트 템플릿 첨부파일` (총 37개 파일)

| 자료 | 성격 |
|------|------|
| `20260728_HA26H197_Step2_프로모션폼_RuleBased_완료보고_영구아카이브.md` | **2차 최종 정본**(약 17,600행) — 본 문서의 1차 출처 |
| `20260706_아카이브_이벤트 템플릿 설계.md` (v10) | 최신 DDL/ERD 확정본 |
| `20260617_..._v9`, `20260601~0617 v1~v7` | 설계 변경 이력 |
| `HA25H101. 착수보고 / 중간보고 / 개발DOC` (PDF) | **1차(2025)** 사업 문서 |
| `HA25H204. 초안` (PDF) | 프로모션폼·Rule Component 전략 |
| `AS-IS ... 이벤트 Rule Based 테이블/데이터 샘플` | `EVENT_PROC_RULE`·`EVENT_PROC_BTN` DDL·데이터 |
| `AS-IS ... 이벤트 테이블/데이터 구조 샘플` | `EVENT`·`EVENT_OFFR_META`·리워드 이력, `eventView/eventProc.jsp` |
| `이벤트 마크업 DB스키마/` | `EVENT_TMPL_CONTENTS(_HIST)`·`ASSETS`·`TESTER(_SEQ)` DDL |
| `20260617_BO 스타일 샘플.zip` | BO 화면 스타일 |

> 📌 자료 우선순위: **① 2차 최종 정본 → ② v10 → ③ v9 → ④ v1~v7·원본 참고자료.** 충돌 시 상위 문서 기준.

### 자료 이용 시 주의
- ⚠️ `02_이벤트 Rule Based EVENT_PROC_BTN 테이블.txt` 는 **내용이 `EVENT_PROC_RULE` DDL로 잘못 채워져 있음**(파일명 불일치). `EVENT_PROC_BTN` 컬럼 구성은 **데이터 샘플 헤더로만** 확인 가능.
- ⚠️ 데이터 샘플 `.txt` 는 **CP949 인코딩** (UTF-8로 읽으면 한글 깨짐).
- ⚠️ 개발DOC PDF의 SQL 코드블록은 **우측이 잘려 렌더링**됨 → 완전한 DDL은 `이벤트 마크업 DB스키마/*.txt` 로 교차 확인.
- ⚠️ 착수보고 "이벤트 템플릿(예상) — 위메프 템플릿 기능 분석 List" 표는 **헤더만 있고 내용 미작성**(착수 시점 공백).
- 📎 **첨부 폴더에 없는 참조 산출물**(개발DOC에 열거됨, 필요 시 별도 확보):
  `해피앱_화면설계서_이벤트 템플릿_v0.7.pptx` · `해피앱_TC문서_이벤트 템플릿_v0.3.xlsx` · `해피앱_가이드_어드민 이벤트 템플릿_v1.0.pptx` · `해피앱_가이드_어드민 이벤트 마크업 등록_v1.0.pptx` · `해피앱_기능목록_이벤트 Rule Based_v1.1.xlsx` · `해피앱_가이드_이벤트 Rule 등록_v1.0.pdf`

---

## 11. 참고 링크
- [ha_api INDEX](../../../ha_api/INDEX.md) · [ha_admin INDEX](../../../ha_admin/INDEX.md)
- [KB 루트 README](../../../../README.md) · [ECC 참조](../../../../shared/ecc-reference.md)
- 관련 진행 문서: [출석체크 개편 기획](../../../ha_api/WORKLOG-20260724-attendance-check-revamp.md)
