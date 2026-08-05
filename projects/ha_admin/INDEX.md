---
문서유형: INDEX
프로젝트: ha_admin
작성일: 2026-07-26
최종수정: 2026-08-05
상태: 진행중
요약: 해피포인트 관리자(백오피스) 웹 애플리케이션 (2026-08-05 영구 짝=ha_api 상단 명시)
---

# 📇 ha_admin 문서 인덱스

> 🔗 **영구 짝(pairing)**: 앱 서버 = [`ha_api`](../ha_api/INDEX.md). 이 백오피스가 운영·설정하는 **런타임 = 해피포인트 앱 서버(ha_api)**. **한쪽만 보고 판단 금지** — 도메인/데이터/이벤트 기능은 양쪽을 함께 본다. (이 관계는 `event-template` 태스크와 **독립인 상시 관계**로, 태스크가 완료·아카이브돼도 유지된다.) ⚠️ 본 어드민은 "앱/웹 어드민"이라 웹 계열(`ha_web`/`ha-web-api`) 관리 범위가 추가로 걸릴 수 있음 — 확인 시 함께 점검.

> 📛 폴더/슬러그 = **Bitbucket 저장소명** `ha_admin` (⚠️ 언더스코어). 로컬 폴더는 `ha-admin`(및 `j-ha-admin`).

## 프로젝트 개요
- **저장소명(=KB 슬러그)**: `ha_admin`
- **로컬 폴더**: `ha-admin` (KB 기준 `../../../ha-admin`) — ⚠️ 저장소명과 하이픈/언더스코어 다름. 별도 체크아웃 `j-ha-admin`(브랜치 `develop`)도 존재.
- **설명**: 해피포인트 **관리자(백오피스)** 웹. 운영/컨텐츠/회원 등 관리 기능.
- **스택**: Java 1.8 / Spring MVC + JSP / MyBatis / Oracle(ojdbc8) / **WAR 패키징 (Maven)**
- **remote/브랜치**: `bitbucket.org/sectanine/ha_admin.git` / `ha-admin`=`dev-j`, `j-ha-admin`=`develop`
- **비고**: Maven 중앙에 없는 라이브러리(ojdbc8 등)는 `ext-libs/`에서 `mvn install:install-file`로 로컬 설치 필요(README 참조).

## 문서 목록
| 문서 | 유형 | 상태 | 요약 |
|------|------|------|------|
| ↗ [이벤트 템플릿 프로젝트 (정본: ha_api)](../task/event-template/archive/ARCHIVE-event-template.md) | ARCHIVE(크로스) | **완료** | **이 프로젝트가 서브 참여.** BO 측 담당 = 프로모션폼 선택화면·Rule Based 관리화면·페이지 빌더·테스터 관리. 정본은 `ha_api` 에 있음 |

## 현재 상태 / 핵심 메모
- 신규 등록(2026-07-26). 상세 작업 이력 없음 — 작업 발생 시 이 인덱스에 문서 추가.
- ⚙️ **이벤트 템플릿 프로젝트(완료)의 서브 프로젝트**다. BO(관리자) 측 = **프로모션폼 선택·Rule Based 등록·페이지 빌더**, 앱 런타임 측 = `ha_api`. **한쪽만 보고 판단 금지** → [정본 아카이브](../task/event-template/archive/ARCHIVE-event-template.md)
  - 관련 테이블: `EVENT_TMPL_FORM` · `EVENT_TMPL_BRIDGE` · `EVENT_TMPL_BTN` · `EVENT_TMPL_RULE(_META)` · `EVENT_TMPL_CONTENTS` · `EVENT_TMPL_ASSETS` · `EVENT_TMPL_TESTER` (스키마 `SPCADMIN`)

## 참고 (공통 문서)
- [공유 KB README](../../README.md) · [서버 환경](../../shared/server-env.md)
