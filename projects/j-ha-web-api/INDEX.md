---
문서유형: INDEX
프로젝트: j-ha-web-api
작성일: 2026-07-16
최종수정: 2026-07-16
상태: 진행중
요약: 신규 홈페이지 리뉴얼 Spring API 백엔드 — Java 21 / Spring 6 기반. Spring6/Jakarta/Tomcat10.1 세팅 완료(빌드·기동), 실검증 진행중
---

# 📇 j-ha-web-api 문서 인덱스

## 프로젝트 정체성 (중요)
- **이 프로젝트 = 신규 홈페이지 리뉴얼의 Spring API 백엔드.**
- **Java 21 / Spring 6** 기반. 지금까지 진행한 Spring6/Jakarta/Java21/Tomcat10.1 마이그레이션 작업물이 **실제로 속하는 프로젝트**이다.
- 레거시 기존 홈페이지(Spring MVC)는 별도 프로젝트 **`j-ha-web`** 이며 혼동 금지 → [j-ha-web INDEX](../j-ha-web/INDEX.md)

## 프로젝트 개요
- **워크스페이스 폴더**: `D:\200_DEV\230_WORKSPACE\happypointcard\j-ha-web-api`
- **Bitbucket remote**: `bitbucket.org/sectanine/ha-web-api.git`
- **스택**: Java 21 / Spring 6.1.14 / Spring Security 6.2.6 / Jakarta EE / Tomcat 10.1.57 / MyBatis 3.5.16
- **주요 브랜치**: master 기준 작업 브랜치 `feature/WORK-16665` (코드 이관 커밋 `b60d1ea`, 푸시 전)

## 문서 목록
| 문서 | 유형 | 상태 | 요약 |
|------|------|------|------|
| [ARCHIVE-WORK-16665-spring-upgrade.md](./ARCHIVE-WORK-16665-spring-upgrade.md) | ARCHIVE | 완료(빌드·기동) | Spring6/Java21/Jakarta/Tomcat10.1 전면 세팅·마이그레이션 풀 기록 |
| [WORKLOG-20260721-nextjs-api-migration-map.md](./WORKLOG-20260721-nextjs-api-migration-map.md) | WORKLOG | 진행중 | JSP 페이지→Next.js(happypoint-web2) 이관용 "페이지 URL↔API" 매핑 인벤토리 |

## 현재 상태 / 핵심 메모
- ✅ Java21/Spring6/Jakarta 세팅 완료 → `mvn clean package -P dev` BUILD SUCCESS, Tomcat 10.1.57 기동 성공(컨텍스트 초기화까지).
- ⏭ **실검증 TODO**: JSP 화면 렌더링, SiteMesh 레이아웃, DB(jdbc/ha·jdbc/cms), 본인인증 벤더 jar(NiceID/okname) JDK21 동작 — 아카이브 16절 참조.
- **포트**: HTTP 9022 / shutdown 8010. **빌드 산출물**: `ha-web.war`(전 프로파일 동일명).
- **SiteMesh**: `ext-libs`의 `sitemesh:3.0.1-jakarta` 커밋본 사용.
- **빌드 환경**: JDK 21 + Maven 3.9.x (Windows). IntelliJ Runner JRE 21.

> ⚠️ 아카이브 문서 본문은 작업 당시 `j-ha-web` 폴더에서 진행한 경로가 다수 언급되지만, **작업 결과물의 귀속 프로젝트는 j-ha-web-api** 이다. (경로 표기는 당시 작업 위치 기준)

## 참고 (공통 문서)
- [공유 지식 베이스 README](../../README.md)
- [서버 환경](../../shared/server-env.md)
