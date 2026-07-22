---
문서유형: WORKLOG
프로젝트: ha-web-api
이슈키: --
작성일: 2026-07-22
최종수정: 2026-07-22
작성자: dominic
상태: 진행중
요약: ha-web-api 코드베이스 전수 구조 파악 — 패키지/레이어 맵, 외부 연동 인벤토리, ECC 보안규칙 기준 리스크 1차 진단(하드코딩 크리덴셜 Critical)
---

# 🛠️ WORKLOG — 코드베이스 구조 분석 & 보안 1차 진단 (2026-07-22)

## 배경 / 목적
Spring6/Java21 마이그레이션(WORK-16665) 이후 이 프로젝트의 **실검증**과 **Next.js 이관 매핑**을 이어가려면
코드베이스의 레이어 구조·외부 연동 인벤토리가 KB에 남아 있어야 한다. 매 채팅마다 재탐색하는 비용을 없애는 것이 목적.
진단 기준은 ECC `rules/common/security.md` · `skills/security-review/SKILL.md`(참조 전용).

## 진행 내용
1. 프로젝트 전수 스캔 — 소스 파일 수, 패키지 트리, 빌드 설정(`pom.xml`), `web.xml` 필터 체인, `context-datasource.xml` 확인.
2. 레이어/패키지 맵 정리 → [INDEX.md](./INDEX.md) "코드베이스 구조"에 반영.
3. 외부 연동(벤더 API) 인벤토리 정리 → 동일하게 INDEX 반영.
4. ECC 보안 체크리스트 기준 1차 스윕 — 하드코딩 크리덴셜 탐지.

### 확인된 규모 (2026-07-22 기준)
| 항목 | 수치 |
|------|------|
| `src` 전체 파일 | 약 2,048 |
| Java 클래스 | 335 |
| JSP | 516 |
| 서비스 도메인 패키지 | 22 |
| 테스트 | **0** (`src/test` 자체가 없음) |

### 확인된 구성 요점
- **Spring Boot 아님**: 순수 WAR + `web.xml` + `classpath:/*/context-*.xml`(XML 빈 설정) + `@Configuration` 혼용.
- **DataSource는 JNDI 2개**: `jdbc/ha`(Oracle) · `jdbc/cms`(MySQL). 각각 별도 SqlSessionFactory·TransactionManager.
  MyBatis 매퍼 스캔은 `com.spc.hpc.home.services` 하위를 `@DefaultMapper`/CMS 어노테이션으로 구분.
  → 서버 환경 상세는 [server-env.md](../../shared/server-env.md).
- **로깅 DataSource 래핑**: `log4jdbc-remix`(`Log4jdbcProxyDataSource`) + 커스텀 `RemoveEmptyLineFormatter`.
- **인증 방식**: `@Login` / `@Bearer` 커스텀 어노테이션 + AspectJ(`LoginAspect`, `BearerAspect`)로 인터셉트. 세션은 `SessionUser`.
- **필터 체인**(web.xml 순서): `hstsFilter` → `encodingFilter`(UTF-8) → `spcFilter` → `redirectFilter` → `sitemesh` → `pagingFilter` → `antiSamyFilter`(정책 `xss/antisamy-myspace.xml`).
  `deviceRedirectFilter`는 주석 처리된 상태.
- **세션 쿠키**: `<secure>true</secure>` 적용됨.

## 발생 이슈 & 해결
| 이슈 | 원인 | 해결 |
|------|------|------|
| 🔴 **하드코딩 크리덴셜이 git에 커밋됨** | `config/application*.yml`에 AWS 키/벤더 API 키가 평문. Jasypt 의존성은 있으나 미사용 | **미해결 — 아래 TODO 참조** |

### 🔴 Critical: 크리덴셜 평문 커밋
> ⚠️ KB 규칙에 따라 **값은 기재하지 않는다**. 위치·유형·건수만 기록.

- **위치**: `src/main/resources/config/application.yml`(기준 파일), `application-dev.yml`, `application-local.yml` — 셋 다 **git 추적 중**.
- **유형**: AWS Access Key/Secret 쌍 3세트(S3 · DynamoDB · KMS), SPC 전문 인증키, 제휴사 API 키(인터파크·제휴·SKT 에이닷), 카카오/네이버지도 키, Amplitude 키, KMS 암호문.
- **영향**: `application.yml`은 프로파일 공통 기준 파일 → `prod`/`stage`도 이 값을 상속. 저장소 접근 = 운영 AWS 자격증명 획득.
- **판정 근거**: ECC `rules/common/security.md` "Mandatory Security Checks — No hardcoded secrets" 위반. ECC 프로토콜상 **STOP → fix → rotate → 전수 재점검** 대상.

## 명령/코드 스니펫
```bash
# 크리덴셜 탐지 (값 출력 없이 위치만)
grep -rn "AKIA" src/main/resources/config/ | sed 's/AKIA[A-Z0-9]*/AKIA****REDACTED****/g'
git ls-files src/main/resources/config/
```

## 결과
- 코드베이스 구조 맵·외부 연동 인벤토리를 [INDEX.md](./INDEX.md)에 영구 반영 완료.
- 보안 1차 진단 결과 Critical 1건 식별. 조치는 미착수(사용자 판단 필요).

## 다음 할 일 (TODO)
- [ ] **(Critical) 노출된 AWS 키 3세트 로테이션** — 저장소 접근 이력이 있는 이상 파일만 지워도 유효한 키는 살아있음. 로테이션이 1순위.
- [ ] 크리덴셜을 환경변수 / AWS Secrets Manager / 기존 KMS 경로로 이관, yml에는 placeholder만 남기기.
- [ ] git history 정리(`filter-repo` 등) 여부 판단 — 팀 저장소이므로 사전 협의 필요.
- [ ] 벤더 API 키(인터파크·SKT 등)도 동일 처리 대상인지 담당자 확인.
- [ ] 테스트 0건 — 실검증 TODO와 묶어 최소 스모크 테스트라도 도입 검토(ECC `tdd-workflow`).
- [ ] AWS SDK v1 → v2 이관 검토(v1은 유지보수 종료 단계).
- [ ] Log4j2가 BOM 무시하고 `2.17.0` 고정 — 상위 버전 CVE 확인 후 갱신 검토.

## 참고 링크
- [ha-web-api INDEX](./INDEX.md)
- [Spring6 마이그레이션 아카이브](./ARCHIVE-WORK-16665-spring-upgrade.md)
- [Next.js API 매핑 워크로그](./WORKLOG-20260721-nextjs-api-migration-map.md)
- [공통 보안 리뷰 기준](../../shared/security-review.md)
- [ECC 참조](../../shared/ecc-reference.md)
