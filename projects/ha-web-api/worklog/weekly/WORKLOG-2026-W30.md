---
문서유형: WORKLOG
범위: 프로젝트(ha-web-api)
주기: 주
기간: 2026-W30 (2026-07-20 ~ 07-26)
작성일: 2026-07-22
최종수정: 2026-07-26
작성자: AI(Claude)
상태: 진행중
요약: 스테이징 Tomcat10 커스텀·Scouter 연동 트러블슈팅, Next.js 이관 매핑, 컨벤션 고도화, 계약 API/로그인 연동.
비고: 구 weekly/WEEKLY-2026-W30.md 에서 이관(운영규칙: 프로젝트 작업내역=주단위)
---

# 🛠️ ha-web-api 주간 작업내역 — 2026-W30 (07-20~26)

## 1. 이번 주 한 것 (Done)
- **프레임워크 재정리**: pom 기준 스택 전수(Java21/Spring6.1.14/MyBatis3.5.16).
- **산출물/배포 경로**: `ha-web.war`→`ha-web-api.war`, `/app/docs/ha-web-api`.
- **스테이징 Tomcat 10.1.57 커스텀**: 9.0.68→10.1.57, 포트 dev값 통일(9022/8010/8422), 호스트 stg-www/stg, 스테이징 DB, 프로파일 stage.
- **JDK21 격리**: 기본 java1.8 유지, 톰캣만 setenv.sh로 21.
- **Scouter**: 2.8.1(Java8 전용, 톰캣10 실패)→**2.21.3 교체**. collector 스테이징 10.0.70.114 / 운영 11.7.11.31.
- **편의 알리어스**: start/stop/log-web-api.
- **Next.js 이관 매핑**: URL↔API 엑셀(118행)+WORKLOG.
- **컨벤션 고도화**: java/spring/sql-mybatis 보강.
- **계약 API/로그인(2026-07-26 추가)**: `com.spc.hpc.api.*` 계약 API 확인, `AuthApiResource`(`/api/auth/login|logout|me`) 분석 → 프론트 로그인 BFF 연동 대상 확정.

## 2. 변경/생성 파일 (핵심)
- `D:\100_WORKS\web-tomcat-10.1.57\` — server.xml/ROOT.xml/setenv.sh/startup.sh/scouter(2.21.3)
- `md/shared/server-env.md`, `md/projects/ha-web-api/` 이관매핑·WORKLOG, `md/shared/conventions/*`

## 3. 미결/다음 주 (TODO)
- [ ] 톰캣10 Scouter 2.21.3 실기동 검증(배너/major version 0건)
- [ ] collector ↔ agent 2.21.3 호환 확인
- [ ] Next.js 이관: 계약 인터페이스 파일 생성(응답 DTO 추출)
- [ ] 스테이징 실검증(JSP/DB/본인인증 벤더 jar)
- [ ] 프론트 로그인 세션유지(`/api/auth/me`) 연동 지원

## 4. 결정/합의
- 스테이징 톰캣 포트 = dev 동일값(9022/8010).
- Scouter collector: 스테이징 10.0.70.114 / 운영 11.7.11.31.
- 톰캣10 Scouter는 startup.sh 2줄 주석해제로 on/off(기본 off).
- md는 묻지 말고 수시 현행화.

## 5. 리스크
- Scouter 2.21.3 × collector 서버버전 호환.
- 톰캣10 JDK21에서 벤더 본인인증 jar 동작 미검증.
