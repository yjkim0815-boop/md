---
문서유형: SHARED
프로젝트: 공통(개발자 개인 규칙)
작성일: 2026-07-16
최종수정: 2026-07-21
작성자: dominic
상태: 초안(확인/수정 필요)
요약: 기술별 코드 컨벤션 인덱스 — 모든 프로젝트/모든 채팅 공통 적용
---

# 🧩 코드 컨벤션 (공통)

> 이 폴더의 규칙은 **특정 프로젝트가 아니라 개발자 개인(dominic)에게 종속된 공통 규칙**이다.
> `happypointcard` 하위 **모든 프로젝트·모든 채팅에서 공통 적용**한다.
>
> ⚠️ 각 문서는 현재 **초안(일반 모범기준)** 이다. 실제 개인 스타일에 맞게 검토·수정한 뒤 상태를 `확정`으로 바꿀 것.
>
> 🔒 **컨벤션 변경 규칙(중요)**: 컨벤션은 **임의로 수정하지 않는다.** 수정이 필요하다고 판단되면 **먼저 사용자에게 확인(제안)**한 뒤 승인 시에만 변경한다.
> **특히 API 응답코드([api-response.md](./api-response.md))의 `code`·`detailCode` 대역/체계**를 바꾸는 것(대역 추가·remap·삭제)은 **반드시 사용자 확인 후**.
> **예외(확인 불필요)**: 개별 API 응답에 **detailCode/detailMessage 를 명시적으로 담아야 하는 경우**(레거시 rpsCd 등 그대로 전달)는 **자동으로 추가**해도 된다. → 대역/체계 변경 = 확인 대상 / 개별 응답에 detail 값 채우기 = 자동 OK.

## 사용법 (새 채팅에서)
- 대화 시작 시: "`md/shared/conventions/` 규칙 반영해서 작업해줘" 한 줄로 전 기술 공통 적용.
- 특정 기술만: "`md/shared/conventions/spring.md` 기준으로" 처럼 지정.

## 기술별 문서
| 문서 | 대상 |
|------|------|
| [java.md](./java.md) | Java 공통 |
| [spring.md](./spring.md) | Spring / Spring MVC / Spring Boot |
| [sql-mybatis.md](./sql-mybatis.md) | SQL / MyBatis |
| [javascript.md](./javascript.md) | JavaScript (공통) |
| [react.md](./react.md) | React |
| [html-css.md](./html-css.md) | HTML / CSS |
| [api-response.md](./api-response.md) | **API 응답 표준** (전 프로젝트 공통: 엔벨로프·code 대역·detailCode) |

## 관련 공통 문서
- [보안/취약점 진단 기준](../security-review.md)
- [서버 환경](../server-env.md)

## 고도화 출처 (참조 전용)
- `java.md`/`spring.md`/`sql-mybatis.md`는 **ECC**(`../../../ECC`, 워크스페이스 루트 하위의 해커톤 우승자 컨텍스트)의 `rules/java/*`·`rules/common/*` 패턴을 이 프로젝트(Java21/Spring6/JSP/MyBatis)에 맞게 이식해 보강했다(2026-07-21).
- ⚠️ **ECC는 읽기 전용**. 좋은 패턴은 여기(md)로 이식해 발전시키고 ECC 원본은 수정하지 않는다.

## 공통 포맷 규칙 (전 언어)
- **들여쓰기: 기존 파일의 스타일을 따른다 (대원칙 #1).** 프로젝트마다 기준이 다를 수 있으므로 각 프로젝트 `.editorconfig`를 정본으로 삼는다.
  - ⚠️ **`ha-web-api`(레거시 홈페이지) 기준**: 코드베이스가 **스페이스 4칸**으로 지배적(실측 약 87%). → 이 프로젝트는 **space / 4** 유지. 탭으로 재포맷 금지(수백 파일 diff 폭발 + 대원칙 #1 위반).
  - 신규 프로젝트에서 탭을 선호하면 해당 프로젝트 `.editorconfig`에 명시하고 처음부터 일관 적용.
- **한 줄 최대 길이: 200자** ✅ 확정
- **개행문자: LF (`\n`)** ✅ 확정 — 단, 윈도우 전용 `.bat`만 CRLF 예외
- `.editorconfig` / `.gitattributes` 로 강제 권장 (space/4 예시):
  ```
  # .editorconfig
  [*]
  indent_style = space
  indent_size = 4
  end_of_line = lf
  charset = utf-8
  trim_trailing_whitespace = true
  insert_final_newline = true
  [*.bat]
  end_of_line = crlf
  ```
  ```
  # .gitattributes
  * text=auto eol=lf
  *.bat text eol=crlf
  ```

## 공통 대원칙 (모든 언어)
1. **일관성 > 개인 취향**: 기존 파일의 스타일을 따른다(주변 코드와 동일하게).
2. 이름은 의도가 드러나게. 축약 남발 금지.
3. 매직넘버/하드코딩 지양 → 상수/설정으로.
4. 주석은 "왜"를 남긴다("무엇"은 코드로).
5. 커밋은 작게, 메시지에 이슈키(WORK-XXXXX) 포함.
6. 死코드/미사용 import 제거.
