---
문서유형: WORKLOG
프로젝트: gcs
이슈키: --
작성일: 2026-07-22
최종수정: 2026-07-22
작성자: dominic
상태: 진행중
요약: gcs(기프트카드 백엔드) 최초 코드베이스 분석 및 KB 등록 + ECC `rules/java/security.md` 기준 1차 보안 진단 — 🔴 Critical 1 / 🟠 High 2 / 🟡 Medium 3
---

# 🛠️ WORKLOG — gcs 코드베이스 분석 & KB 등록 (2026-07-22)

## 배경 / 목적
- 루트 [README](../../README.md) 및 [gcs_fo INDEX](../gcs_fo/INDEX.md)에서 **`gcs` 등록이 "우선순위 1위"** 로 명시돼 있었다.
- [gcs_fo](../gcs_fo/INDEX.md) 진단 시 *"프론트만 보면 토큰 발급·결제 검증의 **서버 측 판정이 불가능**"* 이라는 한계가 남아 있었다 → 본 등록으로 해소.
- [작업 프로토콜](../../shared/ecc-reference.md#1-작업-프로토콜-중요)에 따라 **ECC를 1차 근거**로 분석했다.

## 진행 내용
1. 저장소 메타 확인 — remote `bitbucket.org/sectanine/gcs.git`, 브랜치 `master`/`develop`/`qa`/`release`, 현재 `develop` 클린.
2. 구조 파악 — `com.spc.gcs` 713파일/57,300줄, 채널 기반(승인·월렛·판매·관리자·공통) 설계 확인 → [INDEX](./INDEX.md)에 정리.
3. **ECC `rules/java/security.md` 기준 시크릿 스윕** (루트 README가 *"신규 프로젝트 진단 시 최우선 항목"* 으로 지정) — Java 소스 / `application-*.yml` 전수.
4. **SQL 인젝션 표면 점검** — `nativeQuery=true` **0건**, `@Query` 4건, 나머지 QueryDSL 타입세이프 API. ✅ 양호.
5. 인증·접근제어 경로 추적 — Spring Security **미사용**, 커스텀 `ApiAuthInterceptor` + `JwtUtil`.
6. 동시성 점검 — `@S9DistributedLock` 10파일 / `@Transactional` 67파일, `WORK-16085` 정리 이력 확인.
7. 테스트·CI 확인 — 테스트 **48파일 존재**, CI 설정 **0건**.

## 🔎 진단 결과

> 🔐 **표기 원칙**: [KB 문서 작성 규칙](../../README.md#-문서-작성-규칙) 및 ECC *"Must Never: 비밀정보 출력"* 에 따라 **실제 값은 기록하지 않고 위치(파일:줄)만** 남긴다.

| # | 심각도 | 항목 | 위치 |
|---|--------|------|------|
| C-1 | 🔴 **Critical** | **운영 AWS IAM 크리덴셜 + PG 연동 apiKey 평문 커밋** | `application-real.yml` (AWS 2쌍, PG apiKey 3곳) · `application-dev.yml` (동일 구조) |
| H-1 | 🟠 High | JWT `secret` · AES 키 평문 + **주석 처리된 평문 DB 비밀번호** | `application-local.yml` |
| H-2 | 🟠 High | **CORS Origin 화이트리스트 + 사내 IP가 Java 소스에 하드코딩** | `interceptor/ApiAuthInterceptor.java` `checkPreFlight()` |
| M-1 | 🟡 Medium | 인증 보호가 **화이트리스트(deny-by-default)가 아닌 "보호 URI 열거"** 방식 | `application-*.yml` `application.jwtSecuredUris` + `JwtSecuredUrisConfig` |
| M-2 | 🟡 Medium | **CI 부재** — 테스트 48개가 자동 실행되지 않음 | 저장소 루트 (`bitbucket-pipelines.yml`·`Jenkinsfile` 없음) |
| M-3 | 🟡 Medium | 저장소 `README.md` 가 **다른 프로젝트 구조를 설명**(`com.spc.happymarket`), 도메인은 "(미정)" | `README.md` |

### C-1. 운영 크리덴셜 평문 커밋 🔴
- **근거 규칙**: ECC `rules/java/security.md` §Secrets Management — *"Never hardcode API keys, tokens, or credentials in source code"*, *"Keep local config files with secrets in `.gitignore`"*.
- **내용**: `application-real.yml`·`application-dev.yml` 에 **AWS `accessKey`/`secretKey`(장기 IAM 키, `AKIA` 접두)** 가 각 2쌍, **PG(결제대행) `apiKey`** 가 3곳 **평문**으로 들어 있고 저장소에 **커밋돼 있다**(`git ls-files` 확인).
- **가중 요인**:
  1. **`real`(운영) 값이다.** dev와 값이 다르므로 운영 전용 크리덴셜이 맞다.
  2. **일관성 붕괴가 명확한 증거**: 같은 파일에서 **DB 비밀번호·MobileOK 키비번은 Jasypt `ENC(...)`** 로 감쌌는데(전 환경 3건씩) AWS·PG만 평문이다. → 암호화 수단이 이미 갖춰져 있는데 **누락**된 것.
  3. yml 주석에 *"25.02.28 KMS 적용 완료"* 표기가 있고 `AwsKmsConfig` 도 존재한다 → **KMS 전환이 일부 필드에만 적용되고 중단**된 정황.
  4. **금전성 서비스**다(카드 충전·승인·환불). PG 키 유출은 곧 금전 손실.
- **주의**: 이미 커밋된 이상 **파일 수정만으로는 해결되지 않는다.** 키 로테이션이 선행돼야 한다(git 히스토리에 잔존).

### H-1. local 프로파일 평문 시크릿 + 주석 처리된 DB 비밀번호 🟠
- `application-local.yml` 에 JWT `secret` 과 AES 256 키가 평문이다. yml 주석은 *"실제 local 환경에서만 사용되는 필드"* 라고 방어하지만,
- **바로 위 줄에 평문 PostgreSQL 비밀번호가 주석 처리된 채 남아 있다**(`ENC()` 줄 아래 `# password: ...`). 주석은 시크릿 스캐너·git 히스토리 관점에서 **평문 노출과 동일**하며, 이 값이 dev DB와 공유되는지 확인이 필요하다.
- 부수: MobileOK 키 경로가 **개발자 개인 절대경로**(`D:/IntelliJProject/...`)로 박혀 있다 → 다른 개발자 로컬 구동 불가.

### H-2. CORS·IP 화이트리스트 소스 하드코딩 🟠
- `ApiAuthInterceptor.checkPreFlight()` 가 허용 Origin 목록(dev 4개 / real 3개)과 **dev 전용 허용 IP 목록(사내 PC 공인 IP 포함)** 을 **Java 코드 상수로** 들고 있다.
- **문제**: ① 도메인·IP 변경 시 **소스 수정 + 재배포**가 필요(설정이어야 할 값이 코드에 있음) ② 사내 네트워크 정보가 저장소에 노출 ③ ECC `rules/common/coding-style.md` 의 **매직값 금지** 위반.
- **조치 방향**: `application-*.yml` 로 외부화(이미 `jwtSecuredUris` 라는 동일 패턴의 선례가 프로젝트 내에 있다 → ECC *"기존 패턴 우선"* 에 부합).

### M-1. 인증 보호 방식이 열거식 🟡
- `jwtSecuredUris` 에 **"보호할 URI"를 나열**하는 구조다. 즉 **기본값이 "인증 없음"** 이다.
- → **신규 엔드포인트를 추가하고 yml 등록을 잊으면 그대로 공개 API가 된다.** 금전 도메인에서 이 실수 비용은 크다.
- **즉시 조치는 어렵다**(구조 변경 = 전 채널 영향). 대신 **PR 체크리스트 항목**으로 고정한다 → 아래 TODO.

### M-2. CI 부재 🟡
- 테스트 **48파일**(Repository·Service·Aspect·Controller 고루 분포)은 **KB 전체에서 가장 좋은 테스트 자산**인데, 이를 돌리는 파이프라인이 없다.
- ECC `tdd-workflow`·`springboot-verification`·`verification-loop` 를 **온전히 적용 가능한 KB 유일 프로젝트**라는 점에서 손실이 크다.

## ✅ 양호 판정 (유지할 것)
| 항목 | 상태 | 비고 |
|------|------|------|
| SQL 인젝션 표면 | ✅ | 네이티브 쿼리 0건, QueryDSL 타입세이프 API 중심 |
| `jpa.hibernate.ddl-auto` | ✅ `validate` (전 환경) | ECC/Boot 모범사례 일치 — **변경 금지** |
| `open-in-view` | ✅ `false` (전 환경) | 지연로딩 누수 방지 |
| 운영 Swagger 노출 | ✅ `real` 에서 `swagger-ui.enabled: false` | |
| 분산락 | ✅ `@S9DistributedLock` + Redisson, `WORK-16085` 로 중복 호출 정리 완료 | |
| 로그 보안 | ✅ `MaskingUtil` · `LogEscapeFilter` 존재 | 마스킹 적용 범위는 추후 점검 |
| 테스트 | ✅ 48파일 | 실행 자동화만 없음(M-2) |

## 📊 KB 횡단 관찰 갱신
- 🔴 **하드코딩 시크릿 = 조직 공통 패턴, 6번째 연속 검출.**
  `ha-web-api` · `ha-push-batch` · `ha_panel` · `thehappy_aos` · `gcs_fo` → **`gcs`**.
  Java / Kotlin / TypeScript 에 이어 **YAML 설정 계층**까지 확장됐고, **운영(real) 크리덴셜**이 나온 건 이번이 처음이다.
- 🎁 **GCS 프론트/백 동일 취약 축**: `gcs_fo` 는 `REACT_APP_API_AUTH_KEY` 번들 인라인(Critical), `gcs` 는 운영 AWS·PG 키 평문 커밋(Critical). **같은 서비스의 양쪽 끝에서 동일 원인**이 나왔다 → GCS는 **시크릿 관리 자체를 서비스 단위 과제**로 다뤄야 한다.

## 명령/코드 스니펫
```bash
# 시크릿 스윕 (ECC rules/java/security.md 기준) — 값 출력 없이 위치만
grep -nE 'accessKey|secretKey|secret:|aes_key|apiKey|password:' src/main/resources/application-*.yml

# SQL 인젝션 표면
grep -rn 'nativeQuery\s*=\s*true' src/main/java | wc -l   # → 0

# 커밋 여부 확인
git ls-files src/main/resources/ | grep yml

# 테스트 실행 (CI가 없으므로 로컬 수동)
./gradlew test
```

## 결과
- `projects/gcs/` 신설 — [INDEX.md](./INDEX.md) + 본 WORKLOG.
- 루트 [README](../../README.md) · [shared/ecc-reference.md](../../shared/ecc-reference.md) 갱신(§4-5 Spring Boot/JPA 매핑 신설).
- **KB 미등록 우선순위 1위 항목 해소.** 잔여 미등록: `ha_admin`, `happypoint-web2`.

## 다음 할 일 (TODO)
- [ ] 🔴 **C-1 대응 (최우선)** — ① AWS IAM 키·PG apiKey **로테이션**(히스토리 잔존이므로 필수) ② 신규 값은 Jasypt `ENC()` 또는 KMS로 전환 ③ 2025-02-28 중단된 **KMS 전환 잔여분 마무리**
- [ ] 🟠 H-1 — `application-local.yml` 주석 처리된 평문 DB 비밀번호 제거 + 해당 계정 dev 공유 여부 확인 / MobileOK `keyPath` 상대경로화
- [ ] 🟠 H-2 — CORS Origin·허용 IP 목록을 `application-*.yml` 로 외부화 (`jwtSecuredUris` 패턴 답습)
- [ ] 🟡 M-1 — **신규 API PR 체크리스트**에 *"`jwtSecuredUris` 등록 여부"* 항목 추가 → [security-review.md](../../shared/security-review.md) 에 반영
- [ ] 🟡 M-2 — `bitbucket-pipelines.yml` 도입해 `./gradlew test` 자동 실행 (KB 내 ECC 검증 스킬 적용 1순위 대상)
- [ ] 🟡 M-3 — 저장소 `README.md` 의 `com.spc.happymarket` 구조 설명 폐기 + 도메인 "(미정)" 갱신
- [ ] [conventions/java.md](../../shared/conventions/java.md)·[spring.md](../../shared/conventions/spring.md) 를 **초안 → 확정**으로 고도화. `gcs` 가 ECC Boot/JPA 예시를 그대로 적용 가능한 첫 대상이므로 **실적용 근거가 이제 생겼다**
- [ ] `service/memberstore` 의 `JdbcTemplate` 벌크 업서트 경로 파라미터 바인딩 확인(유일한 비-QueryDSL 경로)

## 참고 링크
- [gcs INDEX](./INDEX.md)
- [ECC 참조 · 작업 프로토콜](../../shared/ecc-reference.md) — Spring Boot/JPA 매핑 **§4-5**
- [보안 리뷰 기준](../../shared/security-review.md)
- [gcs_fo 진단 기록](../gcs_fo/WORKLOG-20260722-codebase-analysis.md) — 같은 서비스의 프론트 측
- ECC 근거 원문(참조 전용): `../ECC/rules/java/security.md` · `../ECC/rules/common/coding-style.md` · `../ECC/skills/springboot-security/SKILL.md`
