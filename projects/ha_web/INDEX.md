---
문서유형: INDEX
프로젝트: ha_web
작성일: 2026-07-16
최종수정: 2026-07-21
상태: 유지(레거시)
요약: 기존 홈페이지 (레거시 Spring MVC). 소스 원복 예정. 신규 리뉴얼 백엔드는 ha-web-api 참조
---

# 📇 ha_web 문서 인덱스

## 프로젝트 정체성 (중요)
- **이 프로젝트 = 기존 홈페이지 (레거시 Spring MVC).**
- ⚠️ 이 워크스페이스 폴더에서 Spring6/Java21 마이그레이션을 **실험적으로 진행했으나, 소스는 나중에 원복(revert) 예정**이다. 즉 이 프로젝트의 정식 상태는 **레거시 Spring 5 / Java 8 / Spring MVC** 이다.
- 신규 홈페이지 리뉴얼의 **Spring API 백엔드(Java21/Spring6)** 는 별도 프로젝트 **`ha-web-api`** 이다 → [ha-web-api INDEX](../ha-web-api/INDEX.md)
- **Spring6/Java21 마이그레이션 기록은 `ha-web-api` 아카이브를 참조**할 것. (이 폴더에 두지 않음)

## 프로젝트 개요
- **워크스페이스 폴더**: `ha_web` (KB 기준 `../../../ha_web`)
- **Bitbucket remote**: `bitbucket.org/sectanine/ha_web.git`
- **정식 스택**: Java 8 / Spring 5.2.5 / Spring MVC + JSP + MyBatis / Tomcat 9 (레거시)
- **설명**: 해피포인트 기존 홈페이지

## 문서 목록
| 문서 | 유형 | 상태 | 요약 |
|------|------|------|------|
| (없음) | | | 필요 시 추가 |

## 현재 상태 / 핵심 메모
- 레거시 유지 프로젝트. 소스 **원복 예정**.
- Spring6/Java21 관련 작업물·기록은 여기가 아니라 **`ha-web-api`** 에 있음.

## 참고 (공통 문서)
- [공유 지식 베이스 README](../../README.md)
- [ha-web-api (신규 리뉴얼 백엔드)](../ha-web-api/INDEX.md)
