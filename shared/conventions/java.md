---
문서유형: SHARED
프로젝트: 공통
작성일: 2026-07-16
최종수정: 2026-07-21
상태: 초안(확인/수정 필요)
요약: Java 코드 컨벤션
---

# ☕ Java 코드 컨벤션 (초안)

## 포맷
- 들여쓰기: **기존 파일 스타일을 따른다** (대원칙 #1). 프로젝트 `.editorconfig`가 정본.
  - ⚠️ **`ha-web-api`는 space / 4 유지** (레거시 코드베이스 약 87%가 스페이스4. 탭 재포맷 금지)
- 한 줄 최대 길이: **200자** ✅ 확정
- 중괄호: K&R 스타일 (`if (...) {` 같은 줄)
- 파일 인코딩: UTF-8, 개행: **LF** ✅ 확정
- **한 파일에 public 최상위 타입 1개**
- **멤버 순서**: 상수 → 필드 → 생성자 → public 메서드 → protected → private

## 네이밍
- 클래스: `PascalCase` / 메서드·변수: `camelCase` / 상수: `UPPER_SNAKE_CASE`
- 패키지: 소문자, `com.spc.hpc.<도메인>.<계층>`
- 불리언: `is/has/can` 접두

## 코드 스타일
- 불변(final) 우선, 컬렉션은 인터페이스 타입으로 선언(`List` `Map`)
- Java 8+ 스트림/람다 활용하되 가독성 해치면 for문
- **Java 21 신기능 적극 활용** (이 프로젝트는 JDK21): 신규 DTO/값 타입은 `record`, 지역변수 `var`, `switch` expression(화살표), 텍스트 블록(SQL·JSON), `instanceof` 패턴매칭(캐스팅 생략), 닫힌 계층은 `sealed`
  - ⚠️ 레거시 기존 클래스는 무리하게 record로 갈아엎지 말 것(대원칙 #1). **새로 만드는 것부터** 적용.

## Optional 사용
- 결과가 없을 수 있는 조회(finder)는 `Optional<T>` 반환, null 반환 최소화
- `map()/flatMap()/orElseThrow()` 활용. **`isPresent()` 확인 없이 `get()` 호출 금지**
- ❌ **`Optional`을 필드 타입이나 메서드 파라미터로 쓰지 말 것** (반환용으로만)
```java
return repository.findById(id)
    .map(ResponseDto::from)
    .orElseThrow(() -> new OrderNotFoundException(id));
```

## 예외 처리
- 도메인 오류는 **언체크 예외**(`RuntimeException` 상속 커스텀) 선호, 체크예외 남용 금지
- 예외 메시지에 **컨텍스트 포함**(`"Order not found: id=" + id`)
- 최상위 핸들러 외에는 광범위한 `catch (Exception e)` 지양
- 경계(핸들러)에서 **내부정보 노출 금지**: 스택트레이스·SQL·내부경로를 클라이언트 응답에 넣지 말 것. 서버엔 상세 로깅, 클라이언트엔 일반 메시지 (problem-spring-web으로 매핑)

## 스트림
- 변환에 사용, 파이프라인은 짧게(3~4단계 이내). 가독성 좋으면 메서드 참조(`.map(Order::getTotal)`)
- 스트림 연산 내 **부수효과(side effect) 금지**. 복잡한 로직은 스트림보다 루프

## Lombok
- `@Getter/@Setter/@Builder/@Slf4j` 등 허용
- `@Data`는 엔티티에 지양(연쇄 문제) → 필요한 것만 조합
- 상속 클래스는 `@EqualsAndHashCode(callSuper=...)` 명시

## 로깅
- SLF4J + Log4j2, 파라미터 바인딩 `log.info("x={}", x)` (문자열 연결 금지)
- 예외는 `log.error(msg, e)` 로 스택 포함

## 보안 (Java 공통)
- 하드코딩된 비밀정보(키/토큰/DB비번) 금지 → 환경변수/Jasypt/KMS. `Objects.requireNonNull`로 필수값 검증
- **PII·비밀번호·토큰을 로그에 남기지 말 것**
- 시스템 경계에서 입력 검증(빈값·범위·형식). 파일경로/사용자 문자열은 사용 전 정제
- SQL은 항상 파라미터 바인딩 → [sql-mybatis.md](./sql-mybatis.md)

## 금지/주의
- `System.out.println` 금지(로거 사용)
- 미사용 import/변수 제거

> TODO: 실제 개인 스타일로 확정 (들여쓰기/줄길이/var 사용범위 등).
> 참고 출처: ECC `rules/java/*`(coding-style·patterns·security) 패턴을 이 프로젝트(Java21/Spring6/JSP/MyBatis)에 맞게 이식. ECC는 참조 전용.
