---
문서유형: ARCHIVE
상위문서: ../ARCHIVE-event-template.md
프로젝트: ha_admin
관련프로젝트: ha_api
작성일: 2026-07-28
최종수정: 2026-07-28
작성자: dominic
상태: 완료
요약: BO(관리자) 화면·URL·탭 구성·리소스 경로·S3 규약 인벤토리 — ha_admin 측 산출물
---

# 🖥️ BO 관리자 화면 인벤토리

> ⚠️ 이 문서는 **`ha_admin`(관리자) 측 산출물**을 다룬다. 런타임(`ha_api`)과 구분할 것.
> 출처: 1차 개발DOC 화면설계 + 2차 완료보고

## 1. 화면 URL 목록 (`admin.happypointcard.com`)

| 화면 | URL |
|------|-----|
| **이벤트 관리** (템플릿 DOM) | `/page/event/template-dom-mgmt.spc?eventSeq=...` |
| **이벤트 리소스 관리** | `/page/event/template-asset-mgmt.spc?eventSeq=...` |
| **이벤트 모니터링** (리스트) | `/page/event/template-monitoring-mgmt.spc` |
| **이벤트 모니터링** (상세) | `/page/event/template-monitoring-mgmt-list.spc` |
| **테스터 관리** | `/page/event/template-tester-mgmt.spc` |

- 확장자 **`.spc`** (레거시 Spring MVC 관례) + 스키마 **`SPCADMIN`** 소유
- ⚠️ REST 규약(`api-design` 스킬)을 적용하지 말 것 — **기존 패턴 유지**가 원칙

## 2. 이벤트 관리 화면 구조

```text
┌──────────────────┬─────────────────────────────────────┐
│                  │ [기본정보] [HTML] [CSS] [JS]        │
│  모바일          │ [RULE] [리소스]                     │
│  미리보기        │                                     │
│  (좌측)          │  ← 탭별 편집 영역 (우측)             │
│                  │                                     │
└──────────────────┴─────────────────────────────────────┘
  하단: [저장]                        상단: [반영(발행)]
```

| 탭 | 역할 | 연결 테이블 |
|----|------|-------------|
| 기본정보 | 이벤트 메타 | `EVENT` |
| HTML / CSS / JS | 마크업 편집 | `EVENT_TMPL_CONTENTS` (`CONTENTS_TYPE`) |
| RULE | 버튼·Rule 등록 | `EVENT_TMPL_BTN` / `EVENT_TMPL_RULE(_META)` |
| 리소스 | 이미지 관리 | `EVENT_TMPL_ASSETS` |

- **저장**(하단) vs **반영(발행)**(상단)이 분리 — 발행 시 `EVENT_TMPL_CONTENTS_HIST` 에 `PROFILE`(PROD/STAGE/DEV)별 이력 적재 → **롤백 근거**

### DOM Page 빌더 탭 (매뉴얼 기준)
`HTML` / `CSS` / `JS` / **`PROC`**
> ⚠️ 빌더 탭에는 **`PROC`** 가 있다. `EVENT_TMPL_CONTENTS_HIST.CONTENTS_TYPE` 이 **VIEW / PROC** 인 것과 대응 — 즉 **화면(VIEW)과 처리(PROC)를 함께 관리**하는 설계.

## 3. 부가 화면
- **이벤트 리소스 관리** + 이미지 업로드 팝업
- **이벤트 모니터링** — 리스트 / 상세 (테스트 데이터 관리, 데이터 조회·추출)
- **테스터 관리** + 테스터 등록 팝업

## 4. 프로모션폼 선택 화면 (2차 신규)
- **카드형 UI** 목록
- 표시 요소: 폼명(`FORM_NM`) · 설명(`FORM_DESC`) · **유형 뱃지**(`FORM_TYPE_NM`) · **미리보기 이미지**(`PREVIEW_IMG_URL`) · 선택 버튼
- 선택 시 `EVENT_TMPL_BRIDGE` 에 `EVENT_SEQ` + `FORM_SEQ` 저장, `PROMOTION_YN` 으로 사용 여부 관리
- 조회 SQL → [34](./34-operational-sql.md#2-프로모션폼-선택-페이지-목록-조회)

## 5. Rule Based 관리 화면 등록 흐름
```text
1. 프로모션폼 내 CTA/Submit 요소 확인
2. class / slotNo 확인
3. Rule Based 관리 화면에서 버튼 선택
4. 쿠폰 / 포인트 / 응모 / 클릭 Rule 선택
5. 버튼 기본정보 입력
6. 실행 기간 설정        (START_DT / END_DT)
7. 테스트 여부 설정      (FLAG_TEST)
8. Rule Meta 입력        (META_JSON)
9. 저장
10. 사용자 클릭 시 class 기반 Rule 실행
```

## 6. 리소스 경로 · S3 규약

**프론트 노출 경로** (`front.happypointcard.com`)
```text
.../upfiles/common/event/EV_EN_/{YYYYMMDD}/{eventSeq}/*.png
```

**이미지 업로드 시 S3 규약**
```text
S3 버킷 : happy-app
S3 경로 : /upfiles/common/event/EV_{YYYYMMDD}_{eventSeq}
```

**프로모션폼 기본 미리보기 이미지**
```text
https://front.happypointcard.com/ha/resources/api/images_renewal/event/
  ├─ default_preview_coupon_issue.png   (쿠폰 발급)
  ├─ default_preview_point_issue.png    (포인트 지급)
  ├─ default_preview_entry_save.png     (응모 적재)
  └─ default_preview_click_save.png     (클릭 적재)
```

> ⚠️ 경로 규약에 **`EV_EN_/{YYYYMMDD}/{eventSeq}`(슬래시 구분)** 와 **`EV_{YYYYMMDD}_{eventSeq}`(언더스코어 구분)** 두 형태가 문서에 함께 나타난다. 실제 업로드/조회 경로는 **운영 소스 확인 필요**.

## 7. 1차 ADMIN 기능 설계 (착수보고)
| 기능 | 내용 |
|------|------|
| **DOM 등록관리** (HTML/JS/CSS) | BO 웹 디자인 컴포넌트, 유형별 기본 템플릿 제공 |
| **Function Binding** | 버튼 등 요소에 기능 마크업 → 신뢰성 향상 (→ 2차 class 바인딩으로 구체화) |
| **Message Binding** | 발급/기발급 등 상황별 메시지 설정 (→ 2차 `META_JSON.msg`) |
| **템플릿 제공** | 단순 버튼 / 퀴즈 입력 / 출석체크(스탬프형) |
| **모니터링** | 테스트 데이터 관리, 데이터 조회·추출 |
| **통합관리** | 리소스 / 테스터 / 템플릿 관리 |

## 참고
- [상위 허브](../ARCHIVE-event-template.md) · [번들 인덱스](./00-INDEX.md)
- [ha_admin INDEX](../../../ha_admin/INDEX.md)
- [21-class-binding-spec.md](./21-class-binding-spec.md) · [30-ddl-event-tmpl.md](./30-ddl-event-tmpl.md)
