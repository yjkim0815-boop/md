---
문서유형: INDEX
프로젝트: ha_api
작성일: 2026-07-22
최종수정: 2026-07-28
작성자: dominic
상태: 진행중
요약: 해피포인트 하이브리드 앱 API 서버 (앱 웹뷰 + REST API). Java8/Spring5.2/JSP(SiteMesh3)/MyBatis WAR — 외장 Tomcat 운영 레거시 모놀리식
---

# 📇 ha_api 문서 인덱스

## 프로젝트 정체성 (중요)
- **이 프로젝트 = 해피포인트 "앱" 백엔드 API 서버** (하이브리드 앱: 앱 내 웹뷰 JSP 페이지 + REST API를 한 서버에서 처리).
- ⚠️ **홈페이지 백엔드(`ha_web` / `ha-web-api`)와 혼동 금지.** 이쪽은 **앱**용이다.
  - `ha_web` = 기존 홈페이지(레거시), `ha-web-api` = 신규 홈페이지 리뉴얼(Java21/Spring6) → [ha-web-api INDEX](../ha-web-api/INDEX.md)
- 정식 스택은 **레거시 Java 8 / Spring 5.2 / Spring MVC + JSP + MyBatis** (WAR + 외장 Tomcat). Boot/JPA 아님.

## 프로젝트 개요
- **워크스페이스 폴더**: `ha-api` (KB 기준 `../../../ha-api`)
- **Bitbucket remote**: `bitbucket.org/sectanine/ha_api.git`
- **주요 브랜치**: `develop`(기본 작업), `master`(기본/PR 대상), `qa`, `release` + 원격 `deploy`, `dev-*`
- **스택**: Java 8 / Spring 5.2.5 / Spring Cloud(Finchley) / Spring Security / Spring MVC + **JSP + SiteMesh 3** / **MyBatis 3.5.4** / WAR 패키징
- **뷰/템플릿**: JSP + SiteMesh3 웹뷰(앱 내 표시). JSP 화면 약 532개.
- **배포**: Docker (`registry.unvus.com`, prefix `spc`) — WAR finalName은 프로파일별 `ha-api` / `ha-api-dev` / `ha-api-stage` / `ha-api-prod`.
- **서버 URL**: DEV `https://dev-napi.happypointcard.com/`, STAGE `https://stg-napi.happypointcard.com/`

## 아키텍처 (com.spc.hpc)
- **`api.controller`**: `page/`(JSP 웹뷰) · `api/` · `rest/`(REST API)로 3분화. 컨트롤러 약 145개.
- **`api.services`**: 도메인별 서비스 **43개** — 앱 기능 전반.
  - 결제/포인트: `happypay` · `point` · `pointstation` · `coupon` · `stamp`
  - 콘텐츠/커머스: `happymarket` · `happylive` · `brand` · `store` · `event` · `banner` · `square`
  - 사용자/인증: `user` · `auth` · `cert` · `agree` · `my` · `employee`
  - 외부연동: `finnq` · `interpark` · `alliance` · `partners` · `external` · `chatbot` · `dynamo`(AWS) · `yapbeacon`
- **`common`**: vo / util / service / interceptor 공통 모듈. `dao` 별도 패키지.
- **규모**: Java 파일 약 649개 · MyBatis Mapper XML 111개.

## DB / 데이터소스 (JNDI)
- `jdbc/ha` — **Oracle** (메인)
- `jdbc/cms` — **MySQL** (CMS)
- `jdbc/ahop` — ahope 계열 (`services/ahope`, `mybatis/ahope`)
- MyBatis mapper 네임스페이스: `mybatis/default` · `mybatis/cms` · `mybatis/ahope` · `mybatis/gis`

## 프로파일 / 포트 (server.port)
| 프로파일 | active | 포트 | 비고 |
|----------|--------|------|------|
| local | dev | 7742 | 로컬 |
| dev | dev | 9200 | 개발 |
| stage / stagep | stage | 9200 | 스테이징 |
| prod | prod | — | 운영 |

## 외부 라이브러리 (ext-libs, 수동 install)
Maven 중앙에 없어 `ext-libs/`에 두고 `mvn install:install-file` 수행 (README 참조):
- `okname-2.2.3.jar` (KCB 실명인증), `thunder-mail-1.0.0.jar`, `ojdbc8-12.2.0.1.jar`(Oracle)

## 문서 목록
| 문서 | 유형 | 상태 | 요약 |
|------|------|------|------|
| [WORKLOG-20260731-home-banner-api.md](./WORKLOG-20260731-home-banner-api.md) | WORKLOG | 진행중 | 홈페이지 메인 배너(`HA_11101`) 조회 일반 REST API `POST /api/home/banner-list` 추가 |
| [archive/ARCHIVE-event-template.md](../task/event-template/archive/ARCHIVE-event-template.md) | ARCHIVE | **완료** | **이벤트 템플릿 프로젝트**(크로스 정본) — 1차(2025) Rule Based 고도화 + 2차(2026 상반기) 프로모션폼·클래스 바인딩 컴포넌트. 서브=`ha_admin` |
| [WORKLOG-20260724-attendance-check-revamp.md](./WORKLOG-20260724-attendance-check-revamp.md) | WORKLOG | 진행중 | 출석체크 개편 기획 — 월 만근 추첨(1만P×10) → 주 7일 완주 전원 5P 실시간 + 추첨 1만P×3명 |
| [MEETING-20260724-attendance-revamp.md](./MEETING-20260724-attendance-revamp.md) | MEETING | 진행중 | 개편 회의록 — 일 00시 트래픽(NetFUNNEL)·확률공개 법무검토·토요일 사전선정(순수 3회)·실시간랜덤/선착순 지양 |

## 현재 상태 / 핵심 메모
- 2026-07-22 최초 등록. 코드 **가벼운 구조 파악** 완료(스택·도메인·DB·프로파일).
- ✅ 2026-07-28 **이벤트 템플릿 프로젝트 완료 아카이브 등록** — 1차(2025, `HA25H101`/`HA25H204`) Rule Based 고도화 + 2차(2026 상반기, `HA26H197`) 프로모션폼·클래스 바인딩. ⚠️ **`ha_admin` 과 크로스 프로젝트**(정본은 이쪽) → [아카이브](../task/event-template/archive/ARCHIVE-event-template.md)
  - 미해결 리스크: **class prefix 혼재**(`ha-btn-` vs `ha-rule-btn-`) → 코드 수정 전 운영 소스 확인 필수.
- 2026-07-24 **출석체크 개편 기획 기록**(문서화만, 코드 변경 없음) → 관련 도메인 `services/stamp` + `services/point`/`pointstation`. 기획 확정(Open Questions) 대기. [WORKLOG](./WORKLOG-20260724-attendance-check-revamp.md)
- 대형 레거시 모놀리식: Spring XML 설정(`context-*.xml`, `dispatcher-config.xml`) + JSP + MyBatis, **Java 8 고정**.
- 특정 기능 작업 시 `services/<도메인>` + 대응 `mybatis/**/<도메인>` mapper를 **짝으로** 확인.
- ⚠️ 앱(this) vs 홈페이지(`ha_web*`) 프로젝트 구분 주의.

## ECC 적용 메모 (참조: [ecc-reference.md](../../shared/ecc-reference.md))
- Spring **MVC + JSP + MyBatis**이며 Boot/JPA 아님 → ECC의 Boot/JPA 예시는 **개념만** 차용.
- 유효: `java-coding-standards`(단 Java **8** — record/var/switch식 등 Java17+ 문법은 불가), `springboot-patterns`(계층·예외·필터 개념), `springboot-security`(체크리스트), `security-review`.
- SQL 인젝션 방지는 MyBatis `#{}` 파라미터 바인딩으로 대응.

## 참고 (공통 문서)
- [공유 지식 베이스 README](../../README.md)
- [ECC 참조](../../shared/ecc-reference.md) · [서버 환경](../../shared/server-env.md) · [코드 컨벤션](../../shared/conventions/README.md)
</content>
</invoke>
