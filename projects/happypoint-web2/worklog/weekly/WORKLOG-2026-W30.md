---
문서유형: WORKLOG
범위: 프로젝트(happypoint-web2)
주기: 주
기간: 2026-W30 (07-20~07-26)
이슈키: WORK-16611
작성일: 2026-07-26
최종수정: 2026-07-26
작성자: dominic
상태: 진행중
요약: 주간 작업내역 롤업 — 환경분리·PC/모바일 분리·로그인 BFF·배포 정비
---

# 🛠️ happypoint-web2 주간 작업내역 — 2026-W30

> 상세 기록: [WORKLOG-20260726-front-back-integration.md](../../WORKLOG-20260726-front-back-integration.md)

## 이번 주 완료
- 앱 루트 이관 인지(unzipped→루트), 환경 프로필 dev/stg/prod + dotenv-cli 스크립트.
- `db.env` 크리덴셜 외부화(로컬 루트 / 서버 `/app/server/happypoint-web/config/db.env`), `.gitignore`·`.idea` 정리.
- `LEGACY_BASE` 환경별(dev-www/stg-www/www) + 폴백 차단.
- PC/모바일 완전 분리: `middleware.ts` UA rewrite + `globals-pc.css`/`globals-mo.css`(미디어쿼리 제거).
- 로그인 BFF `app/api/login/route.ts` → dev-www `/api/auth/login`, mock 제거.
- `next.config.mjs` `ignoreBuildErrors:true`(저사양 빌드), `lib/search-index.ts` 버그 수정.
- 배포 흐름 정리(robocopy → ha-web-fo → pnpm build → pm2).

## 미해결/이월
- PC 1024px 미만 고정(vw floor 롤백됨) 재검토.
- 로그인 세션 유지 `use-auth.ts` → `/api/auth/me`.
- `returnUrl` `/page/main/index.spc` 라우트 존재 확인.

## 이슈 로그
- PM2 무한재시작(빌드폴더≠cwd) → 해당 폴더서 build 후 restart.
- "Running TypeScript" 저사양 지연 → ignoreBuildErrors.
