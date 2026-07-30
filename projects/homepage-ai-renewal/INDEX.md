---
문서유형: INDEX
프로젝트: homepage-ai-renewal (상위/엄브렐러)
작성일: 2026-07-29
최종수정: 2026-07-29
작성자: dominic
상태: 진행중
요약: 해피포인트 홈페이지 AI 리뉴얼 — 프론트(happypoint-web2)·백엔드(ha-web-api)를 하나로 묶는 상위 프로젝트. 완료까지 지속 현행화·디벨롭.
---

# 📇 홈페이지 AI 리뉴얼 (homepage-ai-renewal) — 상위 프로젝트 인덱스

> ⚠️ **이 슬러그는 Bitbucket 저장소가 아니라 "상위 묶음(엄브렐러)"이다.** 실제 코드는 아래 두 저장소에 있으며, 이 문서는 둘을 **하나의 프로젝트로 연결·총괄**한다. (폴더명=저장소명 규칙의 예외 — 통합 관점 문서)

## 프로젝트 정의
- **목표**: 레거시 홈페이지([`ha_web`](../ha_web/INDEX.md))를 대체하는 **신규 홈페이지 리뉴얼**. 프론트+백엔드를 한 몸으로 개발.
- **범위**: 프론트엔드 + 계약 API 백엔드 + 로컬/개발/스테이징/운영 환경 + 배포/인프라(ELB·nginx·PM2·Tomcat) 연동.
- **상태**: 진행중 (완료 시점까지 이 INDEX + 하위 worklog를 **지속 현행화·디벨롭**).

## 🔗 구성 (프론트 ↔ 백엔드 연결)
| 축 | 저장소(KB 슬러그) | 스택 | 배포처 | 문서 |
|---|---|---|---|---|
| **프론트엔드** | [`happypoint-web2`](../happypoint-web2/INDEX.md) | Next.js 16 / React 19 / TS / TailwindCSS v4 / pnpm | dev/stg/prod (PM2 `ha-web-fo`, 포트 3000) | [INDEX](../happypoint-web2/INDEX.md) · [W31 worklog](../happypoint-web2/worklog/weekly/WORKLOG-2026-W31.md) |
| **백엔드** | [`ha-web-api`](../ha-web-api/INDEX.md) | Java21 / Spring6 / Jakarta / MyBatis / Tomcat10.1 (WAR) | `dev.happypointcard.com` 등 | [INDEX](../ha-web-api/INDEX.md) · [W31 worklog](../ha-web-api/worklog/weekly/WORKLOG-2026-W31.md) |
| (대체 대상) | [`ha_web`](../ha_web/INDEX.md) | Java8 / Spring5.2 / JSP | — | 레거시 홈페이지 |

- **로컬 체크아웃**: 프론트 `happypoint-web2`, 백엔드 `j-ha-web-api`(브랜치 `dev-j`).
- **연동 규약**: 브라우저/SSR → `{도메인}/api/*` → (ELB) → 백엔드. `com.spc.hpc.api.*` 응답은 `ApiResponseWrapper`로 `{code,message,data}` 엔벨로프 자동 래핑(HTTP 항상 200, `00`=성공/로그인·`50`=미로그인).

## 아키텍처 통합 관점 (프론트↔백엔드 접점)
- **인증**: 프론트 로그인폼 → `POST /api/auth/login`(백엔드). 전 페이지 SSR `GET /api/auth/check`로 로그인여부 판별 → `AuthProvider` 컨텍스트. 인증 3종 `/api/auth/{login,logout,check}`.
- **로컬 로그인**: **프론트 BFF 프록시**(`app/api/auth/[...path]/route.ts`)가 `/api/auth/*`를 `LEGACY_BASE`로 서버-투-서버 중계 + 쿠키 `Domain/Secure` 제거. → 백엔드 CORS/CSRF 커스터마이징 불필요(회사IP CORS 방식은 폐기·원복).
- **본인인증(KCB 휴대폰·아이핀)**: 프론트가 백엔드 JSP 팝업(`/api/page/cert/...`) 열고 `postMessage`로 결과 수신. 복호화는 100% 백엔드(`MEMBER_AUTH_INFO` HttpOnly 쿠키).
- **데이터**: (A) 신규 계약 API 직접 호출 (B) 레거시 HTML 스크래핑 — A로 전환 중.
- **도메인**: dev = `dev.happypointcard.com` (구 `dev-www` 폐기, 2026-07-29).

## 마일스톤 / 현재 초점
- [진행] 로그인/세션·본인인증 연동 안정화, 로컬 개발 로그인(BFF 프록시) 확정.
- [검토] 로그인 남용 방지(nonce+CAPTCHA+rate limit) — 설계 단계.
- [대기] 신규 계약 API join-policy/join-view(authInfo) 연동, ELB `/api` strip 여부 확정.

## 통합 TODO (하위 worklog와 동기화)
- [ ] `AuthProvider` 최종 노출 필드 범위 확정(로그인여부 최소화 vs GA용 mbrNo)
- [ ] 로그인 보안(nonce/CAPTCHA/rate limit) 구현 여부 결정
- [ ] 약관동의 → 가입폼 authInfo(HttpOnly 쿠키) 연동
- [ ] ELB `/api` strip 검증 → cert 컨트롤러 매핑 확정
- [ ] `/api/auth/*` 프록시 화이트리스트·로깅 운영 전 점검

## 운영 규칙 (이 상위 프로젝트)
- **현행화**: 확정/변경 사항 발생 시 이 INDEX + 해당 하위(`happypoint-web2`/`ha-web-api`) 주간 worklog를 **즉시 갱신**. 완료까지 지속.
- **커밋/푸시**: md 커밋·푸시는 **사용자가 직접** (Claude는 파일 편집만).
- **읽기 순서**: 전역 성향(6M) → 전역 작업동향(3M) → 하위 프로젝트 성향(3M) → 하위 작업내역(3M).

## 참고
- [KB 루트 README](../../README.md) · [서버 환경](../../shared/server-env.md) · [API 응답 표준](../../shared/conventions/api-response.md)
