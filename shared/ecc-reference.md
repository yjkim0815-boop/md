---
문서유형: SHARED
프로젝트: 공통
이슈키: --
작성일: 2026-07-21
최종수정: 2026-07-21
작성자: dominic
상태: 진행중
요약: ECC(Everything Claude Code) 우승자 컨텍스트 — 정체·작업 프로토콜·해피포인트 백엔드 매핑. 참조 전용(수정 금지)
---

# 🏆 ECC 참조 (Everything Claude Code)

> ⚠️ **경로**: `D:\200_DEV\230_WORKSPACE\happypointcard\ECC` — **엔트로피 해커톤 우승자 컨텍스트**.
> **읽기·참조 전용. 절대 수정 금지.** 컨텍스트 학습 **최우선순위** 소스.

## 1. 작업 프로토콜 (중요)
1. **학습 최우선순위 = ECC.** 새 채팅/작업 시작 시 ECC의 관련 규칙·스킬을 먼저 참조한다.
2. **ECC를 근거로 사용자가 시킨 작업을 수행**한다.
3. 수행 결과·확정 사항을 **`md` 지식 베이스에 업데이트**한다 (공통/프로젝트 지속 고도화).
4. ECC는 참조만, `md`는 갱신 대상. 두 경로를 혼동하지 않는다.

## 2. ECC란
- **정체**: "Everything Claude Code" — 에이전트 하네스 운영체제(플러그인). 단순 config 모음이 아니라 agents/skills/hooks/rules/commands + 메모리·학습·보안 스캔·검증 루프를 갖춘 시스템.
- **버전**: v2.0.0 (로컬 체크아웃 기준 `5deee34c`, 2026-07-20). 원본 `github.com/affaan-m/ECC`.
- **규모**: 약 67 agents / 278 skills / 94 legacy command shims. 다중 하네스(Codex/Claude Code/Cursor/OpenCode/Gemini/Zed/Copilot) 지원.
- **핵심 철학(SOUL)**: Agent-First / Test-Driven / Security-First / Immutability / Plan-Before-Execute.

## 3. ECC 핵심 규칙 요약 (RULES.md · rules/common)
- **Must Always**: 도메인 작업은 전문 에이전트에 위임 · 구현 전 테스트 작성 · 입력 검증/보안 체크 유지 · 불변 업데이트 우선 · 기존 패턴 우선(새로 발명 금지) · 변경은 작고 리뷰 가능하게.
- **Must Never**: 비밀정보/시스템 절대경로 출력 · 미검증 변경 제출 · 보안 훅 우회 · 근거 없는 기능 중복 · 테스트 미확인 코드 배포.
- **coding-style**: KISS/DRY/YAGNI, 작은 파일(200~400줄, 최대 800), 함수 <50줄, 중첩 ≤4, early return, 매직넘버 금지, 명시적 에러 처리(조용한 catch 금지), 경계에서 입력 검증.
- **security(commit 전 필수)**: 하드코딩 비밀정보 0 · 입력 검증 · SQL 인젝션 방지(파라미터 바인딩) · XSS · CSRF · 인증/인가 · 레이트리밋 · 에러 메시지 정보 누출 금지.
- **agents(즉시 위임)**: 복잡 기능→planner, 코드 작성 직후→code-reviewer, 버그/신규→tdd-guide, 아키텍처 결정→architect. 위임 시 **완료 계약**: "백그라운드 대기 중"으로 턴 종료 금지, 위임하면 수집·통합까지 책임.

## 4. 해피포인트 백엔드 ↔ ECC 매핑
> 대상: [j-ha-web-api](../projects/j-ha-web-api/INDEX.md) (Java21/Spring6/Jakarta/MyBatis, WAR + 외장 Tomcat). ⚠️ Spring **MVC + JSP + MyBatis**이며 Boot/JPA 아님 → ECC의 Boot/JPA 예시는 **개념만** 차용.

### 직접 적용 가능한 ECC 스킬 (경로: `ECC/skills/<name>/SKILL.md`)
| ECC 스킬 | 용도 | 해피포인트 적용 시 주의 |
|----------|------|------------------------|
| `java-coding-standards` | Java17+ 네이밍/불변/Optional/스트림/예외/DI | Java21 기능(record/var/switch) OK. 포맷은 프로젝트 정본(space/4) 우선 |
| `springboot-patterns` | 계층구조·REST·검증·예외·페이징·필터·레이트리밋 | Controller→Service→Repository 개념·GlobalExceptionHandler·`OncePerRequestFilter`·생성자주입은 유효. **Spring Data JPA/`@Cacheable` 예시는 미사용**(MyBatis 기반) |
| `springboot-security` | 인증/인가·검증·CSRF·헤더·시크릿·레이트리밋 체크리스트 | 개념 유효. 이 프로젝트는 `SecurityFilterChain`(Security6)·`CookieCsrfTokenRepository` 사용 중. **SQL 인젝션 방지는 MyBatis `#{}` 로 대응** |
| `api-design` | REST URL/페이지네이션/에러응답(RFC7807) | 신규 API 설계 시 |
| `backend-patterns` | API·DB·캐싱 일반 패턴 | 개념 참조 |
| `security-review` / `security-scan` | 보안 리뷰 체크리스트 / AgentShield | [shared/security-review.md](./security-review.md) 확정 시 근거로 활용 |
| `search-first` | 코딩 전 조사 우선 워크플로 | 대규모 변경 전 표준 절차 |
| `tdd-workflow` · `verification-loop` · `eval-harness` | RED-GREEN-리팩터 / 검증 루프 | 실검증 TODO 진행 시 |
| `iterative-retrieval` · `strategic-compact` · `continuous-learning-v2` | 서브에이전트 컨텍스트/압축/학습 | 하네스 운용 |

### 관련 ECC 에이전트 (`ECC/agents/<name>.md`)
- `java-reviewer`, `java-build-resolver`(Maven/Gradle 빌드오류), `planner`, `architect`, `code-reviewer`, `security-reviewer`, `refactor-cleaner`, `doc-updater`, `e2e-runner`.

### 관련 ECC 규칙 (`ECC/rules/`)
- `rules/common/*` (coding-style·security·testing·git-workflow·agents·patterns·performance·hooks) — 언어 무관 공통.
- Java 전용 규칙 팩은 rules 디렉터리에 별도 없음 → Java 지침은 위 **스킬**(java-coding-standards 등)에서 가져온다.

## 5. ECC vs 기존 md conventions 관계
- `md/shared/conventions/*` 는 현재 **"초안"** 상태. ECC의 `java-coding-standards`·`springboot-patterns`·`springboot-security` 가 더 구체적 → **conventions 확정(고도화) 시 ECC를 1차 근거로 사용**.
- 단, **충돌 시 프로젝트 정본이 우선**: 들여쓰기 space/4, 줄길이 200자, LF, MyBatis(`#{}`) 등 [conventions](./conventions/README.md)·[.editorconfig] 규칙은 ECC의 일반 예시보다 우선한다.

## 6. 참고
- [공유 지식 베이스 README](../README.md)
- ECC 가이드 원문: `ECC/the-shortform-guide.md`, `the-longform-guide.md`, `the-security-guide.md` (참조 전용)
- 한국어 문서: `ECC/docs/ko-KR/` (README·skills·rules 번역 존재)
