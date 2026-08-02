---
문서유형: INDEX
프로젝트: happypoint-web2
작성일: 2026-07-26
최종수정: 2026-07-31
상태: 진행중
요약: 해피포인트 신규 홈페이지 리뉴얼 프론트엔드 (Next.js 16 / React 19). 백엔드 짝 = ha-web-api
---

# 📇 happypoint-web2 문서 인덱스

> 📛 폴더/슬러그 = **Bitbucket 저장소명** `happypoint-web2` (로컬 폴더명과 동일).
> 🔗 **상위 프로젝트**: [homepage-ai-renewal(홈페이지 AI 리뉴얼)](../homepage-ai-renewal/INDEX.md) — 백엔드 [`ha-web-api`](../ha-web-api/INDEX.md)와 한 프로젝트.

## 프로젝트 개요
- **저장소명(=KB 슬러그)**: `happypoint-web2`
- **로컬 폴더**: `happypoint-web2` (KB 기준 `../../../happypoint-web2`) — 저장소명과 동일 ✅
- **설명**: 레거시 홈페이지(`ha_web`)를 대체하는 **신규 홈페이지 리뉴얼 프론트엔드**. 데이터는 신규 계약 API 백엔드 [`ha-web-api`](../ha-web-api/INDEX.md)(dev-www)에서 가져오고, 일부는 아직 레거시 HTML 스크래핑.
- **스택**: Next.js 16.2.6 (App Router) / React 19.2.4 / TypeScript 5.7.3 / TailwindCSS v4 / pnpm / shadcn / Pretendard(local) / oracledb 7 / Vitest
- **remote/브랜치**: `bitbucket.org/sectanine/happypoint-web2.git` / 작업 `dev-j`·`feature/WORK-16611`, 배포 `main`
- **앱 본체 경로 주의**: 초기엔 `unzipped/` 하위였으나 머지로 **저장소 루트로 이관됨**. 현재 모든 실행/빌드는 루트에서.

## 아키텍처 핵심
- **⭐ 룰셋(2026-07-31 확정): 1 page ↔ 1 model API.** 모든 `app/(site)/**/page.tsx`는 진입(SSR) 시 **대응 모델 API를 반드시 1회 호출**한다. 데이터 불필요 페이지도 예외 없음 — `lib/model-ping.ts`의 `pingModel("/api/...")`로 fire-and-forget 호출(첫 문장). 백엔드에 대응 API가 없으면 **생성**(동작 없어도 `{code:"00"}` 성공만 반환; POST 전용뿐이면 진입 핑용 GET 엔드포인트 추가). 신규 페이지 추가 시에도 준수. 모델 API=`com.spc.hpc.api.model.*`.
- **⭐ POST→GET RSC 브리지 쿠키 규칙(2026-07-31 확정):** form POST를 GET 렌더링 RSC 페이지로 넘길 때, 목적지 URL의 `/page/` 뒤 세그먼트를 `_`로 연결한 `hpw_` 쿠키명을 쓴다. 예: `/page/join/policy` → `hpw_join_policy`. `lib/post-bridge-cookie.ts`의 `getPostBridgeCookieName()`만 사용하고, 생성 시 대상 URL을 `Path`로 제한한다. 대상 GET 요청에서 RSC가 값을 읽은 직후 미들웨어가 같은 이름·`Path`로 `maxAge: 0`을 내려 **반드시 일회성 파기**한다.
- **데이터 조회 2방식**: (A) 레거시 HTML 스크래핑(`lib/legacy-*.ts` → `LEGACY_BASE`), (B) **신규 계약 API 직접 호출**(`lib/*-api.ts` → `legacyContractGet` → `{LEGACY_BASE}/api/...`). 제휴사 등 신규는 B로 전환 중.
- **Oracle 직접 연결 실험**: `lib/db.ts`(oracledb 풀) + `lib/alliance-corp.ts`(ALLIANCE_CORP 직접 쿼리)도 존재하나, 현재 메인 경로는 **계약 API(ha-web-api)** 방식.
- **PC/모바일 완전 분리**: `middleware.ts`가 UA 판별 → 모바일이면 `/`를 내부적으로 `/mobile`로 rewrite(URL 유지). PC=`app/page.tsx`(HomeDesktop)+`globals-pc.css`, 모바일=`app/mobile/page.tsx`(HomeMobile)+`globals-mo.css`. 두 CSS는 `globals.css` 복사본에서 너비 미디어쿼리 제거(PC=max-width 삭제/min-width 평탄화, MO=반대). 서브페이지는 `globals.css`(반응형 유지).
- **로그인**: `login-form.tsx` → BFF `app/api/login/route.ts` → `{LEGACY_BASE}/api/auth/login`(ha-web-api). JSESSIONID 쿠키를 현재 오리진으로 relay(CORS 회피). (이전 mock `setMockSession` 제거됨.)
- **로그인 판별(전 페이지 SSR)**: 루트 layout `force-dynamic` + `getCurrentUser()` → `GET /api/auth/check`(타임아웃 4s, 미로그인=code 50). 결과를 `AuthProvider` 컨텍스트로 전달. 인증 3종 `/api/auth/{login,logout,check}`.
- **KCB 본인인증(휴대폰·아이핀)**: `join/index/join-auth.tsx` 가 백엔드 JSP 팝업(`/api/page/cert/{phone,ipin}/request.spc`) 열고 `postMessage` 로 결과 수신. 크립토·복호화는 백엔드. authInfo(암호문)는 이후 약관동의→가입폼에서 백엔드가 HttpOnly 쿠키(`MEMBER_AUTH_INFO`)로 복호화·유지(레거시 `BrandMemberController` 방식).
- **본인인증 URL**: 전부 `/api/page/cert/...` (ELB: `/api/*`→백엔드).

## 환경변수 / 시크릿
- `.env.local`(로컬 dev)·`.env.dev`·`.env.stg`·`.env.prod`: **공개 설정만**(크리덴셜 없음, 푸시 허용). `LEGACY_BASE`: dev=`dev-www`, stg=`stg-www`, prod=`www`.happypointcard.com.
- **DB 접속정보는 `db.env`로 분리**(gitignore). 로컬=프로젝트 루트 `db.env`(pnpm dev가 로드), 서버=`/app/server/happypoint-web/config/db.env`(start:* 스크립트가 dotenv-cli로 로드).
- 이미지: `LEGACY_S3_URL`(happy-app S3), `FRONT_BASE`(front.happypointcard.com — `/upfiles` 경로용).

## 빌드 / 배포
- **개발서버 배포**: 로컬에서 robocopy로 스테이징 복사 → zip → 서버 업로드 → 서버에서 `pnpm install && pnpm build && pm2 restart ha-web-fo`.
  - robocopy: `... /XD node_modules .next .git .idea unzipped /XF .env.local db.env` (⚠️ `.env.dev`는 올려야 하므로 `.env*` 통 제외 금지).
  - 서버 앱 경로 `/app/docs/ha-web-fo`, PM2 프로세스명 `ha-web-fo`, 포트 3000.
- **빌드 타입체크 스킵**: `next.config.mjs`에 `typescript.ignoreBuildErrors: true` — 사양 낮은 dev 서버에서 "Running TypeScript" 멈춤 회피. 타입검증은 CI(`bitbucket-pipelines.yml`/`.github/ci.yml`)의 `tsc --noEmit`가 담당.

## 문서 목록
| 문서 | 유형 | 상태 | 요약 |
|------|------|------|------|
| [worklog/weekly/WORKLOG-2026-W31.md](./worklog/weekly/WORKLOG-2026-W31.md) | WORKLOG | 진행중 | KCB 본인인증(휴대폰·아이핀) 연동·SSR 로그인 판별·서버 파일 로그·/api 라우팅 통일 |
| [worklog/weekly/WORKLOG-2026-W30.md](./worklog/weekly/WORKLOG-2026-W30.md) | WORKLOG | 진행중 | 환경분리·PC/모바일 분리·로그인 BFF·배포 정비 |
| [WORKLOG-20260726-front-back-integration.md](./WORKLOG-20260726-front-back-integration.md) | WORKLOG | 진행중 | (상세) 프론트↔백엔드 연동 세팅 초기 기록 |

## 개발 분담 (2026-07-26 확정)
- **프론트**: 이 PC 로컬 `pnpm dev`(localhost:3000). **Claude가 소스 수정** → 사용자 로컬 확인.
- **백엔드(ha-web-api / j-ha-web-api dev-j)**: **Claude가 소스 수정** → 사용자가 **dev-www.happypointcard.com** 배포.

## 현재 상태 / 핵심 메모
- PC/모바일 분리·globals-pc/mo·middleware 적용됨. PC 1024px 미만 고정(min-width)은 `overflow-x:clip` 전파/vw 이슈로 시행착오 중(=vw floor 방식은 되돌림). 서브페이지는 라우터 정리로 `/page/*` 하위 이관됨.
- 로그인 BFF 구현 완료 → dev-www `/api/auth/login` 실호출. 세션 유지(마이페이지 등)는 `use-auth.ts`가 아직 `hp_session` 기반이라 `/api/auth/me` 연동 필요(다음 단계).
- ⚠️ 이 세션 중 일부 파일이 편집기 린터/유실로 되돌아가는 현상 있었음 — 배포 전 `next.config.mjs`(ignoreBuildErrors)·`.env.dev`(dev-www) 값 재확인 권장.

## 참고 (공통 문서)
- [공유 KB README](../../README.md) · [서버 환경](../../shared/server-env.md)
- 백엔드 짝: [ha-web-api](../ha-web-api/INDEX.md) / 레거시: [ha_web](../ha_web/INDEX.md)
