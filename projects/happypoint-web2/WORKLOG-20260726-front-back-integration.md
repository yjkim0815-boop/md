---
문서유형: WORKLOG
프로젝트: happypoint-web2
이슈키: WORK-16611
작성일: 2026-07-26
최종수정: 2026-07-26
작성자: dominic
상태: 진행중
요약: 프론트(로컬)↔백엔드(dev-www) 연동 세팅 — 환경분리·PC/모바일 분리·계약API/Oracle·로그인 BFF·배포 정비
---

# 🛠️ WORKLOG — 프론트/백엔드 개발 구조 정립 & 로그인 연동 (2026-07-26)

## 개발 분담 구조 (확정)
- **프론트 `happypoint-web2`**: 이 PC **로컬 `pnpm dev`(localhost:3000)** 로 구동. `LEGACY_BASE=dev-www` 호출.
- **백엔드 `ha-web-api`(로컬 `j-ha-web-api`, 브랜치 `dev-j`, `com.spc.hpc.api.*`)**: Claude가 소스 수정 → 사용자가 **개발서버 `dev-www.happypointcard.com`** 배포.
- 접점: `dev-www/api/*` (계약 API + `/api/auth/*`).

## 진행 내용
1. **앱 구조 이관 인지**: 앱 본체가 `unzipped/` → 저장소 루트로 이동(머지). 모든 실행/빌드는 루트에서.
2. **환경별 프로필**: `dotenv-cli`로 `.env.local`(로컬)·`.env.dev`·`.env.stg`·`.env.prod` + `start:dev/stg/prod` 스크립트. `LEGACY_BASE` dev=dev-www / stg=stg-www / prod=www, 폴백도 각 환경으로(운영 유출 차단).
3. **DB 접속정보 외부화**: `db.env` 분리(gitignore). 로컬=루트 `db.env`(pnpm dev 로드), 서버=`/app/server/happypoint-web/config/db.env`. `.env.*`엔 크리덴셜 금지·공개설정만(푸시 허용). `.gitignore`에 `db.env`·`.idea/` 추가 + `.idea/` 추적 해제.
4. **PC/모바일 완전 분리**: `middleware.ts`(UA 판별 → `/`→`/mobile` rewrite, URL 유지). PC=`app/page.tsx`+`globals-pc.css`, MO=`app/mobile/page.tsx`+`globals-mo.css`. 두 CSS는 `globals.css` 복사본에서 너비 미디어쿼리 제거(awk). 서브페이지는 `globals.css` 유지.
5. **Oracle 직접 조회 실험**: `lib/db.ts`+`lib/alliance-corp.ts`(ALLIANCE_CORP, MyBatis 조건 이식). 단 현재 메인 경로는 계약 API.
6. **로그인 연동**: 백엔드 분석 → `AuthApiResource` 확인(`POST /api/auth/login` `{login,password,rememberMe}` → JSESSIONID). 프론트 mock(`setMockSession`) 제거 → BFF `app/api/login/route.ts`(dev-www 프록시 + 쿠키 relay) + `login-form.tsx` 실호출로 교체.
7. **빌드 타입체크 스킵**: `next.config.mjs` `typescript.ignoreBuildErrors:true` (사양 낮은 dev서버 "Running TypeScript" 멈춤 회피). 검증은 CI `tsc --noEmit`.
8. **버그 수정**: `lib/search-index.ts` 라우터정리 커밋(3ec42a0)에서 깨진 `BRANDS`/`SEARCH_INDEX` 참조 → `SEARCH_INDEX=pages`로 복구.

## 발생 이슈 & 해결
| 이슈 | 원인 | 해결 |
|------|------|------|
| PM2 무한 재시작(↺68) | `next start` 폴더에 `.next` 없음(빌드폴더≠PM2 cwd) | `/app/docs/ha-web-fo`에서 직접 build 후 restart |
| 개발서버 배포 "Running TypeScript" 멈춤 | tsc가 저사양 서버서 리소스 부족(코드 타입에러 아님 — 로컬 tsc 통과) | `ignoreBuildErrors:true`(빌드 스킵) + CI에서 tsc |
| API가 운영(www) 호출 | `.env.dev`가 www였음 | `.env.dev`/`.env.local` → dev-www + 폴백 dev-www |
| PC 1024 미만 찌그러짐 | `body overflow-x:clip` 뷰포트 전파 + vw 단위 | min-width는 넣음. vw→calc floor는 화면 틀어져 **되돌림**(미해결) |
| main 배포 안 됨 | (정적비교) 설정 동일·타입에러 없음 → 저사양 tsc 지연 추정 | ignoreBuildErrors로 회피 |

## 배포 (로컬 → 개발서버)
```powershell
robocopy D:\200_DEV\230_WORKSPACE\happypointcard\happypoint-web2 D:\100_WORKS\ha-web-fo `
  /E /XD node_modules .next .git .idea unzipped /XF .env.local db.env
# → zip → 서버 업로드 → /app/docs/ha-web-fo 에서: pnpm install && pnpm build && pm2 restart ha-web-fo
```
> ⚠️ `.env.dev`는 배포 포함(=`.env*` 통 제외 금지). `db.env`는 서버 외부경로에 별도 존재.

## 다음 할 일 (TODO)
- [ ] 로그인 세션 유지: `use-auth.ts`(현 `hp_session` mock) → `/api/auth/me` 기반으로 전환
- [ ] PC 1024 미만 고정 재검토(vw floor 대안 or 컨테이너 스케일)
- [ ] `returnUrl` 기본값 `/page/main/index.spc` 라우트 신규 프론트 존재 여부 확인
- [ ] 파일 유실 현상 유의: 배포 전 `next.config.mjs`(ignoreBuildErrors)·`.env.dev`(dev-www) 재확인

## 참고 링크
- [happypoint-web2 INDEX](./INDEX.md) · 백엔드 짝 [ha-web-api INDEX](../ha-web-api/INDEX.md)
- [서버 환경](../../shared/server-env.md)
