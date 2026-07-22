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

## 어노테이션
- 계층: `@RestController`/`@Controller`, `@Service`, `@Repository`
- 트랜잭션: `@Transactional`은 서비스 계층. 읽기전용은 `@Transactional(readOnly=true)`
- 매핑: `@GetMapping/@PostMapping` (구 `@RequestMapping(method=...)` 지양)

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
