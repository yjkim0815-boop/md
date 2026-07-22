---
문서유형: WORKLOG
프로젝트: ha_panel
이슈키: --
작성일: 2026-07-22
최종수정: 2026-07-22
작성자: dominic
상태: 진행중
요약: ha-panel(패널KOK) 코드베이스 분석 — AMP 프레임워크/설문 도메인/배치 맵 정리 + ECC 규칙 기준 진단(인증 암호키 하드코딩·토큰 무결성 부재 = Critical 2건)
---

# 🛠️ WORKLOG — 코드베이스 분석 & 1차 진단 (2026-07-22)

## 배경 / 목적
`ha-panel`은 KB **미등록 프로젝트**였고, [security-review.md](../../shared/security-review.md)의 **"전수 재점검 대상"에 명시적으로 지목**되어 있던 저장소다(ha-web-api·ha-push-batch에서 크리덴셜 평문 커밋이 연속 검출된 뒤 후속 스윕 대상).

- 설문 참여로 **해피포인트가 지급**되는 서비스 → 인증 위·변조 시 **금전적 영향**이 직접 발생한다. 우선순위를 높게 잡았다.
- 자체 SPA 프레임워크(AMP)를 쓰는 유일한 프로젝트라 구조를 KB에 남겨 매 채팅 재탐색 비용을 없앤다.

진단 기준(참조 전용): ECC `rules/java/security.md` · `rules/common/security.md` · `rules/common/coding-style.md`.

## 진행 내용
1. 전수 스캔 — Java 66파일, `WEB-INF/config/spring/*.xml` 5개, MyBatis 매퍼 7개, `web.xml`/`weblogic.xml`/`META-INF/context.xml`, `control/**` JS, git remote/추적파일.
2. 요청 처리 방식(`*.do` + `method=` 분기)·인증 흐름·AMP 모듈 규약·도메인 테이블·배치 크론 정리 → [INDEX.md](./INDEX.md)에 영구 반영.
3. ECC 보안 체크리스트 기준 시크릿 스윕(→ **기존 두 프로젝트와 다른 유형**이 나옴).
4. ECC 코딩 규칙(명시적 에러 처리·죽은 코드·의존성 보안) 기준 코드 리스크 진단.

### 확인된 규모 (2026-07-22 기준)
| 항목 | 수치 |
|------|------|
| Java 파일 / 라인 | 66개 / 약 7,667줄 |
| 화면 JS(`control/`) | 약 9,986줄 |
| 컨트롤러 | 4개 (엔드포인트 `method=` 27개) |
| MyBatis 매퍼 | 7개 — **`${}` 0건** |
| 테스트 | **0건** (테스트 소스 디렉토리 자체가 없음) |
| 빌드 파일 | **없음** (`pom.xml`/`build.gradle` 부재, `.iml`만 존재) |
| git 커밋 | 4개 (이관 스냅샷 수준) |

### 확인된 구성 요점
- **`*.do` + `method=` 파라미터 분기** — REST가 아니라 레거시 Struts 스타일. 신규 엔드포인트 추가 시 이 관례를 따라야 한다(ECC `api-design` 스킬의 REST 규칙을 그대로 적용하면 기존 패턴과 충돌 → ECC "기존 패턴 우선" 원칙에 따라 **현행 관례 유지**).
- **인증 = AES 암호화 토큰/쿠키 단독**. 서버 세션(`HttpSession`)에 인증 상태를 두지 않고, 복호화 결과(`mbrNo`)를 그대로 신뢰한다.
- **DB 접속은 JNDI(`jdbc/panel`)** — ha-web-api·ha-push-batch에서 문제였던 `application*.yml` 평문 크리덴셜 패턴이 **여기엔 없다**. `.properties` 파일도 저장소에 0건.
- **AMP 프레임워크** — `AMP.module = { init: ... }` 규약. 화면 로직 대부분이 `control/**/*.js`에 있고 서버는 JSON + JSP 껍데기만 제공.
- **기초조사 회차별 파일 복제** — `basic-survey-detail-{202301,202401,202501}-{A~F}` 16쌍. 회차 문항 스냅샷 보존 목적이라 단순 통합은 위험.
- **레거시 소켓/FTP 연동** — `schedule/legacy/`에 전문(`PT5110X0`) 기반 소켓 + FTP 업/다운로드. 포인트·HPC 상태 동기화가 이 경로에 의존.

## 발생 이슈 & 해결
| 이슈 | 원인 | 해결 |
|------|------|------|
| 🔴 인증 암호키/IV 하드코딩 커밋 | `SessionUtils`/`AES256Utils`에 상수로 직접 기재 | **미해결 — TODO(로테이션 + 외부화)** |
| 🔴 토큰 무결성·만료 부재 | AES-CBC 암호문만으로 인증, MAC/exp/nonce 없음 | **미해결 — 설계 변경 필요** |
| 🟠 토큰 평문 로깅 | `ulog.info("panelIntro :: "+toknAuth)` | **미해결 — TODO(즉시 제거 가능)** |
| 🟠 인증 실패 침묵 | `SessionUtils` 빈 `catch` 4개 | **미해결 — TODO** |

---

### 🔴 Critical-1: 인증 토큰 암호화 키/IV 하드코딩 + 저장소 커밋
> ⚠️ KB 규칙에 따라 **값은 기재하지 않는다**. 위치·유형만 기록.

- **위치**:
  | 위치 | 유형 |
  |------|------|
  | `src/main/java/hp/panel/common/util/SessionUtils.java:14` | 인증 토큰/쿠키용 **AES 키** (`public static final`) |
  | `src/main/java/hp/panel/common/util/SessionUtils.java:15` | 동일 용도 **IV** (`public static final`) |
  | `src/main/java/hp/panel/common/util/AES256Utils.java:13` | 별도 AES-256 **키** (`mbrNo` 암호화용, `BaseSrvyMgCtl.java:845`에서 사용) — IV는 **키의 앞 16바이트를 그대로 사용**(`:14`) |
- **영향(악용 시나리오)**:
  1. 저장소 접근자(또는 WAR 디컴파일러)가 키/IV를 획득한다.
  2. 임의의 `mbrNo` 로 `mbrNo$$<타인 회원번호>|||mbrNm$$...` 평문을 만들어 동일 방식으로 암호화한다.
  3. `GET /panel.do?method=auth&token=<위조 토큰>` 호출 → 서버가 복호화에 성공하므로 **그대로 해당 회원으로 인증**되고 `PANEL_AUTH` 쿠키가 발급된다.
  4. 타인 명의로 설문 참여·프로필 조회/수정·**포인트 적립**·참여이력 열람이 가능하다. 회원번호는 순차성이 있어 대량 시도도 어렵지 않다.
- **판정 근거**: ECC `rules/java/security.md` — "Secrets Management: Never hardcode API keys, tokens, or credentials in source code" / "Never implement custom auth crypto — use established libraries".
- **가중 요소**: `AES256Utils`는 **IV를 키에서 파생**시킨다(`key.substring(0,16)`). IV가 키에 종속돼 고정이므로 동일 평문이 항상 동일 암호문이 된다 → 사전 대입·패턴 분석에 취약.
- **ECC 대응 프로토콜**: STOP → **키 로테이션 최우선**(커밋된 이상 코드 수정만으로 무효화되지 않음. 단, 로테이션 시 **기존 발급 쿠키가 전부 무효화**되므로 앱 배포와 동기화 필요) → 환경변수/시크릿 매니저 이관 → 전수 재점검.

### 🔴 Critical-2: 인증 토큰에 무결성·만료·재사용 방지가 전혀 없음
- **위치**: `SessionUtils.getToknAuth()` / `getCookieAuth()` / `setCookieUser()`
- **내용**: 토큰은 `mbrNo$$...|||mbrNm$$...` 를 AES-CBC로 암호화한 **암호문 단독**이다.
  - **MAC/서명 없음** → 암호문 위조·변조 탐지 수단이 없다. 복호화가 "성공한 것처럼 보이면" 곧 인증이다.
  - **만료(exp) 없음** → 쿠키에는 `Max-Age=86400`이 붙지만, **URL로 넘어오는 `token` 파라미터 자체에는 시간 정보가 없다**. 한 번 유출된 토큰은 **영구 유효한 베어러 자격증명**이 된다.
  - **nonce/1회용 없음** → 재사용(replay) 차단 불가.
- **추가 노출 경로**: 토큰이 **URL 쿼리 파라미터**로 전달된다 → 웹서버 access log·프록시 로그·Referer 헤더·앱 웹뷰 히스토리에 남는다. (ECC `rules/common/security.md` — 자격증명을 URL에 싣지 않는다)
- **권고 방향**: 표준 라이브러리 기반 서명 토큰(JWT/JWS 등 `exp`+`jti` 포함)으로 전환하거나, 최소 조치로 **① 토큰에 발급시각 포함 후 유효시간 검증 ② HMAC 부가 ③ 토큰 전달을 URL이 아닌 헤더/POST 바디로 이동**.

### 🟠 High-3: 인증 토큰 원문을 평문 로깅
- **위치**: `BaseSrvyMgCtl.java:86` — `ulog.info("panelIntro :: "+toknAuth);`
- **내용**: 인증 진입점에서 **토큰 전체를 그대로 로그에 남긴다.** Critical-2(만료 없음)와 결합하면 **로그 파일 열람 권한 = 전 회원 사칭 권한**이 된다.
- **판정 근거**: ECC `rules/java/security.md` — "Clear sensitive data from logs — never log passwords, tokens, or PII".
- **권고**: 해당 라인 제거 또는 마스킹(앞 4자리 + 길이). **조치 난이도가 가장 낮으므로 우선 처리 대상.**

### 🟠 High-4: 인증 실패가 조용히 삼켜짐 (빈 catch)
- **위치**: `SessionUtils.java` — `setCookieUser`(:43) · `getCookieAuth`(:66) · `getMbrAuth`(:84) 의 `catch(Exception e) {}` **본문 완전 공백**, `getToknAuth`(:113)는 `e.printStackTrace()`만.
  - 저장소 전체 빈 `catch` 블록 **5개** (나머지 1개는 `common/socket/HttpManager.java`).
- **내용**: 복호화 실패(=위조/손상 토큰)가 예외로 전파되지 않고 **빈 `HashMap` 반환**으로 끝난다. 호출부는 "인증 실패"와 "정보 없음"을 구분할 수 없다.
- **영향**:
  - 위조 시도가 **로그에 아무 흔적도 남기지 않는다** → 침해 탐지 불가.
  - 인증 실패 시 흐름이 중단되지 않고 계속 진행되어, 호출부의 null/빈값 처리 누락이 그대로 인가 우회로 이어질 수 있다(각 호출부 개별 검증 필요 — 이번 스캔 범위 밖).
  - `e.printStackTrace()`는 로깅 체계(log4j MDC) 밖으로 새며 스택트레이스를 표준출력에 노출한다.
- **판정 근거**: ECC `rules/common/coding-style.md` — "명시적 에러 처리(조용한 catch 금지)".

### 🟠 Medium-5: 빌드 파일 부재 → 재현 빌드·의존성 CVE 스캔 불가
- **내용**: `pom.xml`·`build.gradle`이 **없다**. IntelliJ `hp.panel.iml`/`ha-panel.iml` 과 `out/artifacts/KOK_war_exploded` 산출물만 존재하며, `WEB-INF/lib`도 저장소에 없다.
- **영향**:
  - **의존성 목록이 저장소에 존재하지 않는다** → ECC `rules/java/security.md`의 "Dependency Security(OWASP Dependency-Check/Snyk, CVE 추적)"를 **원천적으로 수행할 수 없다**. Spring 4.1 스키마·log4j 1.x·jQuery 3.1.0 등 노후 버전 흔적이 있어 실제 위험도는 낮지 않다.
  - CI/재현 빌드 불가, 개발자 로컬 환경에 빌드가 종속된다.
- **권고**: Maven `pom.xml` 도입(실 배포 WAR의 `WEB-INF/lib` 목록에서 역산) → 그 후 CVE 스캔을 1회 수행.

### 🟠 Medium-6: 빌드 산출물 git 추적 → 설정 드리프트
- **내용**:
  | 경로 | 추적 파일 수 |
  |------|--------------|
  | `out/artifacts/KOK_war_exploded/**` | **538** |
  | `src/main/webapp/WEB-INF/classes/**` (spring/sql 설정 사본) | 13 |
  - `.gitignore`에 `target/`·`dist/`는 있으나 **`out/`이 빠져 있다**. `WEB-INF/jsp.zip`(소스 압축본)도 추적 중.
- **영향**: **`WEB-INF/config/spring/*.xml`을 고쳐도 실제 클래스패스에 올라가는 건 `WEB-INF/classes/spring/*.xml`** 이다. 두 사본이 갈라지면 "고쳤는데 반영이 안 되는" 디버깅 지옥이 발생한다. 지금은 내용이 동일하나 구조적으로 시한폭탄.
- **권고**: `.gitignore`에 `out/` 추가 + `WEB-INF/classes/` 추적 해제(빌드 시 `config/`에서 복사되도록 일원화).

### 🟡 Low-7: URL 파라미터가 로드할 JS 모듈 경로를 결정
- **위치**: `WEB-INF/jsp/main/base.jsp:110,120` — `var am = AMP._GET("am") == "" ? AMP.extv.defaultModule : AMP._GET("am"); AMP.run(am);`
- **내용**: 쿼리스트링 `am` 값이 그대로 AMP 모듈 경로가 되어 `control/<am>.html` + `.js` 를 로드한다.
- **평가**: 로드 경로가 **동일 출처 `control/` 접두 + 확장자 고정**이라 외부 스크립트 주입은 성립하지 않는다 → **XSS로는 오탐**. 다만 `../` 상대경로로 의도치 않은 내부 파일 로드/에러 유발은 가능하므로 **화이트리스트 검증 권고** 수준.
- ✅ 참고: 서버 측 `<%=am%>` 출력들은 전부 **JSP 내 하드코딩 리터럴**이며 요청 파라미터가 아니다 → 반사형 XSS 아님(오탐 배제).

### 🟡 Low-8: 코드/설정 위생
- **인증 쿠키 `HttpOnly` 누락**: `SessionUtils.java:39`에서 `Set-Cookie` 헤더를 **문자열로 직접 조립**하는데 `Secure; SameSite=strict`만 있고 **`HttpOnly`가 없다**. `web.xml`의 `<cookie-config><http-only>`는 **JSESSIONID에만 적용**되어 이 쿠키는 보호되지 않는다 → XSS 발생 시 인증 쿠키가 JS로 탈취 가능. **한 단어 추가로 해결되므로 우선 처리 권장.**
- **죽은 코드**: `WebFilter.addSameSiteAttribute()`는 정의만 되고 **호출되지 않는다**. `SessionUtils.getToknAuth()`의 User-Agent 기반 키 파생 로직은 주석 처리된 채 고정 키로 대체돼 있다(원래 의도했던 보강이 비활성).
- **테스트 0건**: ECC SOUL 원칙 Test-Driven 기준 미달. 최소한 `SessionUtils` 암복호화 라운드트립 테스트부터 필요.
- **미사용 엔드포인트**: `BaseSrvyMgCtl` `method=test`(:489) — 운영 노출 여부 확인 필요.
- **중복 `@ExceptionHandler(Exception.class)`**: `BaseSrvyMgCtl:55,64`에 **동일 예외 타입 핸들러가 2개** 선언되어 있다(각각 400/404 지정). Spring은 동일 타입 중복 매핑 시 기동 실패 또는 임의 선택이 되므로 **의도대로 동작하지 않는다.**
- **Java 8 / Spring 4.1 스키마** — 프레임워크 노후. 업그레이드 시 [ha-web-api의 Spring 업그레이드 아카이브](../ha-web-api/ARCHIVE-WORK-16665-spring-upgrade.md)가 선례가 된다.

## 명령/코드 스니펫
```bash
# 하드코딩 암호키 위치만 확인 (값 노출 없이)
grep -rn "static.*String \(key\|iv\|ENC_KEY\|ENC_IV\)" src/main/java/hp/panel/common/util/ | sed -E 's/=.*/= <REDACTED>/'

# SQL 인젝션 스윕 — ${} 사용 0건 확인
grep -rn '\${' src/main/webapp/WEB-INF/config/sql/ | wc -l

# 빈 catch 블록 수 (5건)
find src/main/java -name "*.java" | xargs perl -0777 -ne 'my $c=()=/catch\s*\([^)]*\)\s*\{\s*\}/g; $t+=$c; END{print "$t\n"}'

# 추적 중인 빌드 산출물
git ls-files out | wc -l                       # 538
git ls-files src/main/webapp/WEB-INF/classes | wc -l   # 13
```

## 결과
- `ha_panel` KB 신규 등록 — [INDEX.md](./INDEX.md)에 AMP 프레임워크 규약·엔드포인트 맵·인증 흐름·도메인 테이블·배치 크론 영구 반영.
- ECC 기준 1차 진단: **Critical 2 / High 2 / Medium 2 / Low 2**. 조치는 전부 미착수(사용자 판단 필요).
- **✅ 클린 판정 항목**(오탐 배제 완료): SQL 인젝션(`${}` 0건) · DB 크리덴셜 미커밋(JNDI) · API 프로퍼티 미커밋 · 서버측 JSP 반사형 XSS · `web.xml`의 위험 메서드(PUT/DELETE/TRACE/OPTIONS) 차단.
- 공통 문서 갱신: [README.md](../../README.md) 프로젝트 표 등록, [security-review.md](../../shared/security-review.md) 적용 이력 + **시크릿 유형 확장**, [ecc-reference.md](../../shared/ecc-reference.md) 적용 강도 표에 행 추가.

### 🔁 KB 차원의 발견 — 시크릿 패턴이 두 갈래다
기존 KB는 크리덴셜 리스크를 **"`config/application*.yml` 평문 커밋"** 유형으로만 기록해 왔다. `ha-panel`은 **설정 파일 계열은 완전히 클린**(JNDI + 외부 프로퍼티)인데, 대신 **소스 코드 상수에 암호키가 박혀 있는** 다른 유형이 나왔다.
→ 앞으로 미진단 프로젝트(`ha-api`·`ha-admin`·`gcs`) 스윕 시 **설정 파일만 보면 놓친다. `static final String` 상수 스윕을 반드시 병행**할 것. → [security-review.md](../../shared/security-review.md) 시크릿 스윕 절에 반영함.

## 다음 할 일 (TODO)
- [ ] **(Critical) 인증 암호키/IV 로테이션 + 외부화** — `SessionUtils.ENC_KEY/ENC_IV`, `AES256Utils.key`. ⚠️ 로테이션 시 **기존 발급 쿠키 전부 무효화** → 앱 배포/전환 시점 조율 필요. 저장소 접근 이력이 있는 이상 **코드 수정만으로는 무효화되지 않는다.**
- [ ] **(Critical) 인증 토큰 설계 변경** — 서명(HMAC/JWS) + 만료(`exp`) + 재사용 방지(`jti`) 추가, 토큰 전달을 URL 쿼리에서 헤더/바디로 이동.
- [ ] **(High) `BaseSrvyMgCtl.java:86` 토큰 평문 로깅 제거** — 가장 손쉬운 즉시 조치.
- [ ] **(High) `SessionUtils` 빈 catch 4개 처리** — 복호화 실패를 `PanelBizException`으로 승격 + 실패 로그 기록(탐지 가능하게).
- [ ] **(Medium) `HttpOnly` 추가** — `SessionUtils.java:39` `Set-Cookie` 문자열에 한 단어 추가.
- [ ] **(Medium) `pom.xml` 도입** 후 의존성 CVE 스캔 1회 수행 (log4j 1.x·Spring 4.x·jQuery 3.1.0 확인).
- [ ] **(Medium) `.gitignore`에 `out/` 추가 + `WEB-INF/classes/` 추적 해제** — 설정 드리프트 차단.
- [ ] **(Low) `method=test` 엔드포인트 운영 노출 여부 확인**, 중복 `@ExceptionHandler` 정리, 죽은 코드(`addSameSiteAttribute`) 제거.
- [ ] **배포/운영 환경 확인** — 이 서비스가 **어느 WebLogic 인스턴스에 어떻게 배포되는지 미확인**. 확인 후 [server-env.md](../../shared/server-env.md)에 추가(현 문서는 Tomcat 기준만 존재).
- [ ] 인증 실패(빈 Map) 시 **각 컨트롤러 호출부가 실제로 흐름을 차단하는지** 개별 검증 — 이번 스캔 범위 밖. 인가 우회 가능성 확인 필요.

## 참고 링크
- [ha_panel INDEX](./INDEX.md)
- [ECC 참조 · 작업 프로토콜](../../shared/ecc-reference.md)
- [보안 진단 기준](../../shared/security-review.md)
- 동일 시기 진단: [ha-push-batch](../ha-push-batch/WORKLOG-20260722-codebase-analysis.md) · [ha-web-api](../ha-web-api/WORKLOG-20260722-codebase-analysis.md)
- ECC 원문(참조 전용): `../../../ECC/rules/java/security.md`, `../../../ECC/rules/common/security.md`, `../../../ECC/rules/common/coding-style.md`
