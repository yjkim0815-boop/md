---
문서유형: SHARED
프로젝트: 공통
작성일: 2026-07-16
최종수정: 2026-07-21
상태: 초안(확인/수정 필요)
요약: Spring / Spring MVC / Spring Boot 컨벤션
---

# 🌱 Spring 코드 컨벤션 (초안)

## 계층 구조
- `Controller`(웹/REST) → `Service`(트랜잭션·비즈니스) → `Repository/Mapper`(DAO)
- 컨트롤러엔 비즈니스 로직 금지(위임만). **컨트롤러·리포지토리는 얇게, 비즈니스 로직은 서비스에**
- DTO/VM(요청·응답)와 도메인/엔티티 분리. 매핑은 서비스/컨트롤러 경계에서 (신규는 record + `static from()` 팩토리)

## 의존성 주입
- **생성자 주입** 강제(final 필드) — 필드 주입(`@Autowired`/`@Inject` 필드) 지양. 생성자 주입이 테스트 용이·불변 보장
```java
// GOOD — 생성자 주입 (테스트/불변)
public class OrderService {
    private final OrderRepository orderRepository;
    private final PaymentGateway paymentGateway;
    public OrderService(OrderRepository r, PaymentGateway g) { this.orderRepository = r; this.paymentGateway = g; }
}
```
- 순환참조 발생 시 설계 재검토(필드주입으로 우회 금지)

## 명명 규칙 (클래스 접미사)
- **신규 리뉴얼 모델(화면 데이터) 조회 API 는 `~ModelApiResource` 로 명명**하고 **`com.spc.hpc.api.model.<도메인>`** 패키지에 둔다.
  - 예: `com.spc.hpc.api.model.alliance.AllianceModelApiResource`, `…model.event.EventModelApiResource`.
  - JSP ModelAndView(화면 데이터)를 JSON 으로 대체하는 프론트 연결용 조회 컨트롤러가 이에 해당(2026-07 기준 20개).
  - ❌ `~ApiController` 금지. 기존 레거시 REST(`~Resource`)·JSP(`~Controller`)와 이름이 겹치지 않도록 `~ModelApiResource` 로 구분.
- **인증 등 비(非)모델 API** (`com.spc.hpc.api.auth.AuthApiResource` 등)는 `~ApiResource`(모델 아님). 공통 인프라는 `com.spc.hpc.api.common`.
- JSP 화면용 `@Controller`는 기존대로 `~Controller`, 레거시 REST 는 기존대로 `~Resource`.
- 서비스 `~Service`, 매퍼/DAO `~Repository`.

## 어노테이션
- 계층: `@RestController`/`@Controller`, `@Service`, `@Repository`
- 트랜잭션: `@Transactional`은 서비스 계층. 읽기전용은 `@Transactional(readOnly=true)`
- 매핑: `@GetMapping/@PostMapping` (구 `@RequestMapping(method=...)` 지양)

## URL 매핑 규칙 (ApiResource) ⭐
- **클래스 레벨 `@RequestMapping(base)`를 쓰지 않는다.** 각 메서드 매핑에 **full URL**을 직접 명시한다.
  - 이유: 한 화면(엔드포인트)의 실제 URL을 메서드만 보고 바로 알 수 있게(계약/프론트 라우트와 대조 용이).
```java
// ❌ 지양 — 클래스 base + 메서드 조합
@RestController
@RequestMapping("/api/alliance")
public class AllianceApiResource {
    @GetMapping("/corporation")
    public ... listCorp() { ... }
}

// ✅ 권장 — 클래스 base 없음, 메서드에 full URL
@RestController
public class AllianceApiResource {
    @GetMapping("/api/alliance/corporation")
    public ... listCorp() { ... }

    @GetMapping("/api/alliance/card")
    public ... listCard() { ... }
}
```

## API 응답 규격 (ApiResource 공통) ⭐
**★ HTTP 는 항상 200. 성공/실패는 body 의 `code` 로 판별한다** (레거시 JSP-ajax 관용 계승).
- **응답 body 공통**: `{ code, message, detailCode?, detailMessage? }`
  - **`code` = 2자리 대분류**, **`message` = 문구**.
  - **`detailCode` = 4자리 업무 세부코드**(레거시 rpsCd 계열: `0000` 정상, `0011` 휴면 …), **`detailMessage`** = 세부 문구. 없으면 응답에서 생략.

  **★ 응답코드 대역 (해피앱 표준) — HTTP 는 전부 200**
  | code | 의미 | 헬퍼 |
  |------|------|------|
  | `00` | 정상 | (성공 응답) |
  | `01` | 이벤트(Rulebased) | (이벤트 처리코드) |
  | `40` | 인증(로그인/세션/본인인증) | `ApiError.unauthorized()` |
  | `41` | 인증(권한 없음) | `ApiError.forbidden(msg)` |
  | `50` | 정책적 제한 | `ApiError.policy(msg, detailCode, detailMessage)` |
  | `60` | 제휴사 오류 | `ApiError.partner(msg)` |
  | `70` | 외부 시스템 연동 | `ApiError.external(msg)` / `comm(msg)` |
  | `80` | 내부 시스템 연동 | `ApiError.internal(msg)` |
  | `91` | 파라미터 | `ApiError.badRequest(msg)` |
  | `92` | 토큰 | `ApiError.token(msg)` |
  | `93` | 데이터처리 | `ApiError.data(msg, ...)` |
  | `99` | 기타/미구현 | `ApiError.error(msg)` / `notImplemented(msg)` / `ApiExceptionHandler` |

  > 상세: [api-response.md](./api-response.md). code 대역은 detailCode Prefix 와 동일 체계.

  실패 예(전부 HTTP 200):
  ```json
  { "code": "40", "message": "로그인이 필요합니다." }
  { "code": "50", "message": "처리할 수 없습니다.", "detailCode": "5001", "detailMessage": "휴면 회원입니다." }
  { "code": "91", "message": "카드번호가 유효하지 않습니다." }
  ```
- **프론트 판별**: HTTP는 항상 200이므로 **`body.code === "00"` 이면 성공, 아니면 실패**(error.tsx). (HTTP status로 분기하지 않음)
- **성공 응답 형태(확정: 래핑)**: `{ "code":"00", "message":"성공", "detailCode":"0000", "detailMessage":"성공", "result": { …화면데이터… } }`
  - 컨트롤러는 데이터만 반환하면 되고, **`ApiResponseWrapper`(ResponseBodyAdvice)가 자동으로 `result`로 감싼다**(없으면 빈 객체 `{}`). 실패(`ApiFailBody`)는 통과(실패도 `result:{}` 포함).
  ```json
  { "code":"00", "message":"성공", "detailCode":"0000", "detailMessage":"성공", "result": { "corpList":[ ... ], "category":"life" } }
  ```
- **내부정보 노출 금지**: 예외 스택/SQL/경로는 서버 로그만. 클라이언트엔 일반 메시지(`ApiExceptionHandler` → `code=99`, HTTP 200).
- 인증 가드: 로그인 필요 화면은 메서드 첫머리에서 `SecurityUtils.getCurrentUser()==null → ApiError.unauthorized()`.

### ⭐ 기존 비즈니스 로직·응답코드 보존 (최우선 원칙)
- 신규 `/api`는 **기존 소스의 비즈니스 로직·분기·응답코드(rpsCd/rpsDtlCd/SUCCESS_CODE 등)를 그대로 재사용**한다. 로직을 새로 짜거나 코드값을 임의 remap하지 않는다.
- 기존 전문(H0 등) 응답의 **`rpsCd`/`rpsDtlCd`/메시지는 원형 그대로 전달**한다(예: `detailCode`=rpsCd, `detailMessage`=원본 메시지, 또는 result에 그대로 포함). 프론트가 기존과 동일한 신호를 받도록 한다.
- 분기 조건(예: 로그인 `SUCCESS_CODE`=1 통과 후 `rpsCd` 88=휴면 / 44+2728=비번재설정)도 **기존 `checkauth.jsp` 등과 동일하게** 유지.
- 즉 대분류 `code`(00/50/80/99)는 엔벨로프 표준으로 씌우되, **원본 코드/메시지/로직은 손대지 않고 보존**한다.

## REST API
- URL: 소문자·하이픈, 명사 위주(`/api/user/point`)
- 응답 포맷 일관(공통 Response 래퍼 / problem-spring-web). 이 프로젝트는 `restapi/model/RestResponse*` + `ResponseBuilder` 사용
- 상태코드 의미 준수(200/201/400/401/403/404/500)
- **경계에서 안전한 에러 메시지**: 내부 예외를 그대로 노출하지 말고 일반 메시지로 매핑. 상세는 서버 로깅.
```java
try {
    return orderService.findById(id);
} catch (OrderNotFoundException ex) {
    log.warn("Order not found: id={}", id);      // 서버엔 상세
    return ResponseBuilder.error("Resource not found");   // 클라이언트엔 일반 메시지
} catch (Exception ex) {
    log.error("Unexpected error id={}", id, ex);
    return ResponseBuilder.error("Internal server error"); // ex.getMessage() 노출 금지
}
```

## 설정
- 프로파일: local/dev/stage/prod. 환경별 값은 yml/프로파일로
- 비밀값은 코드/커밋에 금지 → Jasypt/KMS/환경변수

## Spring 6 / Jakarta 주의 (이 조직 표준)
- 네임스페이스 `jakarta.*` (javax 아님). 단 `javax.crypto/sql/naming/net.ssl`은 JSE라 유지
- Security 6: `SecurityFilterChain` @Bean 방식(어댑터 없음), `requestMatchers`
- 인터셉터: `HandlerInterceptor` 직접 구현(Adapter 제거됨)
- 멀티파트: `StandardServletMultipartResolver`
- 자세한 마이그레이션 이력: [ha-web-api 아카이브](../../projects/ha-web-api/ARCHIVE-WORK-16665-spring-upgrade.md)

## 테스트
- 서비스 단위테스트 우선, 컨트롤러는 MockMvc/슬라이스 테스트

> TODO: 팀/개인 규칙으로 확정 (응답 래퍼 포맷, 패키지 구조 등).
> 참고 출처: ECC `rules/java/patterns.md`(생성자 주입·서비스 계층·응답 엔벨로프), `rules/java/security.md`(경계 에러 메시지)를 이 프로젝트 구조에 맞게 이식. ECC는 참조 전용.
