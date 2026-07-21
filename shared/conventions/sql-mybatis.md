---
문서유형: SHARED
프로젝트: 공통
작성일: 2026-07-16
최종수정: 2026-07-21
상태: 초안(확인/수정 필요)
요약: SQL / MyBatis 컨벤션
---

# 🗄️ SQL / MyBatis 컨벤션 (초안)

## SQL 작성
- 예약어 대문자, 테이블/컬럼은 스키마 규칙 준수
- `SELECT *` 지양 → 필요한 컬럼 명시
- 조인/서브쿼리 가독성 위해 별칭(alias) 명확히
- 인덱스 고려, 대량 조회는 페이징

## MyBatis
- 매퍼 XML은 도메인별 폴더 (`mybatis/default/**`, `mybatis/cms/**`)
- **파라미터는 반드시 `#{}` (PreparedStatement)** — `${}`는 SQL 인젝션 위험이라 **정렬컬럼 등 불가피할 때만** 화이트리스트 검증 후 사용
- resultMap 명시, camelCase 매핑(`mapUnderscoreToCamelCase`)
- 동적쿼리는 `<if>/<choose>/<foreach>` 활용

## 이중 데이터소스 (이 조직 표준)
- ha(Oracle) = `@DefaultMapper`, cms(MySQL) = `@CmsMapper` 마커로 라우팅
- JNDI: `jdbc/ha`, `jdbc/cms`

## 트랜잭션
- 서비스 계층 `@Transactional`. 여러 DAO 묶는 단위로 경계 설정

## `${}` 화이트리스트 (불가피할 때만)
정렬 컬럼/방향처럼 바인딩 불가한 값에 `${}`를 써야 하면 **반드시 서비스단에서 화이트리스트 검증** 후 전달:
```java
// 정렬 컬럼: 허용 목록으로 제한 (사용자 입력 직접 ${} 금지)
private static final Set<String> SORT_COLS = Set.of("reg_dt", "point", "name");
String sortCol = SORT_COLS.contains(req.getSort()) ? req.getSort() : "reg_dt";
String dir = "DESC".equalsIgnoreCase(req.getDir()) ? "DESC" : "ASC";
// 매퍼: ORDER BY ${sortCol} ${dir}   ← 값이 화이트리스트 통과분이라 안전
```
그 외 모든 사용자값은 `#{}`. 문자열 이어붙인 동적 SQL 금지.

## 금지/주의
- 문자열 이어붙인 동적 SQL 금지(인젝션)
- N+1 주의, 반복 쿼리는 배치/조인으로

> TODO: 네이밍(컬럼/매퍼id) 규칙 확정.
> 참고 출처: ECC `rules/java/security.md`(파라미터 바인딩·SQL 인젝션 방지)를 MyBatis 맥락으로 이식. ECC는 참조 전용.
