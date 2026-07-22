---
문서유형: SHARED
프로젝트: 공통(개발자 개인 규칙)
작성일: 2026-07-16
최종수정: 2026-07-22
작성자: dominic
상태: 초안(확인/수정 필요)
요약: 취약점 진단 / 보안 리뷰 기준 — 모든 프로젝트 공통. ECC 보안 규칙(커밋 전 체크리스트·대응 프로토콜·시크릿 스윕) 이식 + Kotlin/buildSrc 스윕·클라이언트(APK) 특수성 + ②-JS/②-ENV 프론트 스윕(주석 내 크리덴셜·번들 인라인 env·소스맵) + **①-B Boot yml 스윕(ENC() 부분 적용 대조)·deny-by-default 판정축** 추가(2026-07-22). 하드코딩 시크릿 **6개 프로젝트 연속** 검출(최초 운영 크리덴셜 = `gcs`)
---

# 🛡️ 취약점 진단 / 보안 리뷰 기준 (초안)

> 모든 프로젝트·모든 채팅에서 코드 리뷰/진단 시 공통 적용하는 개인 기준.

## 기준 프레임
- **OWASP Top 10** 기준으로 점검 *(← 확정/커스터마이즈)*

## ✅ 커밋 전 필수 체크 (ECC 이식)
> 출처: ECC `rules/common/security.md` — "Mandatory Security Checks". **한 항목이라도 미충족이면 커밋 금지.**

- [ ] 하드코딩 시크릿 **0건** (API 키·비밀번호·토큰)
- [ ] 모든 사용자 입력 검증
- [ ] SQL 인젝션 방지 — 파라미터 바인딩(MyBatis `#{}`)
- [ ] XSS 방지 — 출력 이스케이프 / AntiSamy
- [ ] CSRF 보호 활성
- [ ] 인증·인가 검증
- [ ] 엔드포인트 레이트리밋
- [ ] 에러 메시지가 내부 정보를 흘리지 않음

## 🔑 시크릿 관리 원칙 (ECC 이식)
- 소스에 시크릿을 **절대** 하드코딩하지 않는다.
- 환경변수 또는 시크릿 매니저(AWS Secrets Manager / KMS / Jasypt)를 사용한다.
- 필수 시크릿의 존재 여부를 **기동 시점에 검증**하고, 없으면 즉시 실패시킨다.
- **노출됐을 가능성이 있는 시크릿은 무조건 로테이션한다.** 파일에서 지우는 것만으로는 무효화되지 않는다.

### 시크릿 스윕 명령 (값 노출 없이 위치만)
> ⚠️ **세 갈래를 모두 훑어야 한다.** ① 설정 파일 계열(**+ ①-B Boot yml 프로파일**) ② **소스 코드 상수 계열**(주석 포함) ③ **번들 인라인 환경변수 계열**(프론트).
> ⭐ **판정 기준 갱신(2026-07-22, gcs)**: "암호화 수단이 있는가"가 아니라 **"모든 시크릿에 빠짐없이 적용됐는가"** 를 본다. `gcs` 는 같은 파일에서 DB 비밀번호만 Jasypt `ENC()` 이고 AWS·PG 키는 평문이었다 — **부분 적용이 오히려 "조치 완료"로 오인**되게 만든다.
> 근거: `ha-web-api`·`ha-push-batch`는 ①에서, [ha_panel](../projects/ha_panel/WORKLOG-20260722-codebase-analysis.md)은 **①이 완전히 클린한데 ②에서 인증 암호키가 검출**됐고, [gcs_fo](../projects/gcs_fo/WORKLOG-20260722-codebase-analysis.md)는 **②가 "주석 안"이고 ③이 별도 High**였다. 한 갈래만 보면 놓친다.

```bash
# ① 설정 파일 계열
grep -rn "AKIA" src/main/resources/ | sed 's/AKIA[A-Z0-9]*/AKIA****REDACTED****/g'
git ls-files src/main/resources/config/          # 설정 파일이 git 추적 대상인지

# ①-B Spring Boot yml 프로파일 계열 — gcs에서 이 형태로 운영(real) 크리덴셜이 검출됨
grep -rnE "(accessKey|secretKey|apiKey|secret|aes_key|password|keyPassword) *:" src/main/resources/application-*.yml \
  | sed -E 's/: *.*/: <REDACTED>/'
# ⭐ 핵심은 "암호화했는가"가 아니라 "빠짐없이 했는가" — ENC() 개수와 시크릿 키 개수를 대조한다
for f in src/main/resources/application-*.yml; do
  echo "$f  ENC()=$(grep -c 'ENC(' $f)  시크릿키=$(grep -cE '(accessKey|secretKey|apiKey|secret|aes_key|password|keyPassword) *:' $f)"
done
# 주석 처리된 평문 시크릿 — ENC() 줄 바로 아래 원본이 남아 있는 패턴이 흔하다
grep -rnE "^\s*#\s*(password|secretKey|apiKey) *:" src/main/resources/application-*.yml | sed -E 's/: *.*/: <REDACTED>/'

# ② 소스 코드 상수 계열 — 암호키/IV/토큰이 Java 상수에 박혀 있는지
grep -rnE "(static +)?(final +)?String +[A-Za-z_]*(KEY|IV|SALT|SECRET|TOKEN|PASSWORD)[A-Za-z_]* *=" \
  --include="*.java" src/ | sed -E 's/=.*/= <REDACTED>/'
# 고엔트로피 리터럴(16자 이상 hex/base64)
grep -rnE '"[A-Za-z0-9+/=]{16,}"' --include="*.java" src/ | sed -E 's/"[A-Za-z0-9+\/=]{16,}"/"<REDACTED>"/'

# ②-K Kotlin 계열 (val/var + 빌드 스크립트) — thehappy_aos에서 이 형태로 검출됨
grep -rnE "va[lr] +[A-Za-z_]*(Key|Iv|Salt|Secret|Token|Password)[A-Za-z_]* *=" \
  --include="*.kt" --include="*.kts" . | sed -E 's/=.*/= <REDACTED>/'
# ⚠️ Android/Gradle 프로젝트는 buildSrc/ 와 *.gradle.kts 도 반드시 포함할 것 (src/ 밖에 있다)
git ls-files 'buildSrc/**' | grep -iE "credential|secret|config"

# ②-JS TypeScript/JavaScript 프론트 계열 — gcs_fo에서 이 형태로 검출됨
# (a) 문자열 리터럴이 대입된 상수만 — `= 뒤 따옴표`를 강제해야 화살표 함수 오탐이 걷힌다
grep -rnE "(const|let|var) +[A-Za-z_]*([Kk]ey|IV|[Ss]alt|[Ss]ecret|[Tt]oken|[Pp]assword|[Cc]redential)[A-Za-z_]* *= *['\"]" src/ | sed -E "s/=.*/= <REDACTED>/"
# (b) 고엔트로피 리터럴 — ⚠️ 주석 안까지 훑을 것. gcs_fo의 실제 검출 유형이 "주석처리된 디버그용 조기 return"이었다
grep -rnE "['\"][A-Za-z0-9+/%=]{40,}['\"]" src/ | sed -E "s/['\"][A-Za-z0-9+\/%=]{40,}['\"]/'<REDACTED>'/"

# ②-ENV 번들 인라인 환경변수 — CRA `REACT_APP_*` / Vite `VITE_*` / Next `NEXT_PUBLIC_*` 는 전부 "공개값"이다
git ls-files | grep -iE "^\.env"        # .env* 가 git 추적 중인가 — ⚠️ .gitignore에 있어도 소급 적용 안 됨(먼저 커밋됐으면 계속 추적)
cut -d= -f1 .env.production 2>/dev/null  # 값 말고 키 이름만 — AUTH/KEY/SECRET 류가 있으면 즉시 판정 대상
grep -rn "GENERATE_SOURCEMAP" .env* 2>/dev/null || echo "⚠️ 운영 소스맵 노출 가능(CRA 기본값=true)"
```
> ⚠️ 진단 결과를 문서화할 때는 **위치·유형·건수만** 남기고 **값은 절대 기재하지 않는다**(KB 공통 규칙).

## 🚨 보안 이슈 발견 시 대응 프로토콜 (ECC 이식)
1. **즉시 중단(STOP)** — 진행 중이던 작업을 계속하지 않는다.
2. 보안 리뷰 관점으로 전환(ECC `agents/security-reviewer.md` · `skills/security-review`).
3. **CRITICAL 먼저 수정**한 뒤 원래 작업 재개.
4. **노출된 시크릿 로테이션** (3번보다 우선일 수 있음 — 이미 커밋된 경우 로테이션이 1순위).
5. **코드베이스 전수 재점검** — 같은 유형이 다른 곳에도 있는지 확인.

## 필수 점검 항목
1. **인젝션**: SQL(`${}` 지양, `#{}` 사용), OS 커맨드, LDAP
2. **XSS**: 사용자 입력 출력 이스케이프(AntiSamy/`c:out`), innerHTML 직접삽입 금지
3. **인증/인가**: 세션/토큰 검증, 권한 체크 우회 여부, 민감기능 접근통제
4. **CSRF**: 상태변경 요청 토큰 검증(CookieCsrfTokenRepository 등)
5. **민감정보 노출**: 비밀번호/키 하드코딩·로그·응답 노출 금지, 암호화(Jasypt/KMS)
6. **암호화**: 안전한 알고리즘/키관리, 평문 저장 금지
7. **접근제어(IDOR)**: 리소스 소유자 검증
8. **설정 오류**: 디렉터리 리스팅, 상세 에러 노출(showReport=false), 불필요 메서드(TRACE/OPTIONS) 차단
9. **취약 의존성**: 알려진 CVE 라이브러리 업데이트(Log4Shell 등)
10. **파일 업로드**: 확장자/용량/경로 검증, 실행권한

## 리뷰 산출물 형식
- **심각도**: Critical / High / Medium / Low
- **항목**: 위치(파일:라인) → 문제 → 재현/영향 → 권고 조치
- 오탐 줄이기: 실제 악용 시나리오가 성립하는지 검증 후 보고

## 개인 스타일 (예시 — 확정 필요)
- 리뷰는 **근거(코드/시나리오)와 함께** 제시, 추측성 지적 지양
- 수정안은 최소 침습 우선, 대규모 변경은 사전 협의

> TODO: 심각도 기준, 보고 포맷, 필수/제외 항목을 개인 기준으로 확정.

## 적용 이력 (진단 기록)
| 일자 | 프로젝트 | 결과 |
|------|----------|------|
| 2026-07-22 | [ha-web-api](../projects/ha-web-api/WORKLOG-20260722-codebase-analysis.md) | 🔴 Critical 1건 — `config/application*.yml` 크리덴셜 평문 커밋(AWS 3세트 + 벤더 API 키). 조치 미착수 |
| 2026-07-22 | [ha-push-batch](../projects/ha-push-batch/WORKLOG-20260722-codebase-analysis.md) | 🔴 Critical 2건 — ① `config/*.yml` 5개 전부 크리덴셜 평문 커밋(**운영 Oracle 관리자 계정 + 운영 푸시 API 키** + Slack 웹훅 + 텔레그램 봇 토큰) ② stage 프로파일이 **운영 DB를 2분 주기로 전체 DELETE**. 그 외 High 2 / Medium 3. 조치 미착수 |
| 2026-07-22 | [ha_panel](../projects/ha_panel/WORKLOG-20260722-codebase-analysis.md) | 🔴 Critical 2건 — ① **인증 토큰 AES 키/IV가 소스 상수에 하드코딩 + 커밋**(`SessionUtils`·`AES256Utils`) → **임의 회원 사칭 → 포인트 적립 가능** ② 토큰에 **무결성(MAC)·만료·nonce 전무** + URL 쿼리로 전달 → 유출 시 영구 유효. 그 외 High 2(토큰 평문 로깅·인증 실패 침묵) / Medium 2 / Low 2. ✅ 설정 파일·DB 크리덴셜은 **클린**(JNDI). 조치 미착수 |

| 2026-07-22 | [gcs_fo](../projects/gcs_fo/WORKLOG-20260722-codebase-analysis.md) | 🔴 Critical 1건 — **앱 인증 크리덴셜(`hpcAut`) 실값이 `axios.config.ts:17` 주석처리된 조기 `return` 에 하드코딩 + 커밋** → 재사용 시 해당 회원의 GCS 토큰 발급 → **잔액·이용내역·환불 접근**. 🟠 High 2건 — ① `REACT_APP_API_AUTH_KEY` **번들 인라인 + `.env*` 4종 git 추적**(`.gitignore` 등재에도 불구, 선(先)커밋이라 무효) ② **운영 소스맵 노출**(`GENERATE_SOURCEMAP` 미설정). 그 외 Medium 3(테스트·CI 0건 / `any`·`@ts-ignore` 76건 / CSP 부재). ✅ `dangerouslySetInnerHTML`·`target="_blank"`·localStorage 토큰저장은 **클린**. 조치 미착수 |
| 2026-07-22 | [gcs](../projects/gcs/WORKLOG-20260722-codebase-analysis.md) | 🔴 Critical 1건 — **운영(real) AWS IAM 키 2쌍 + PG apiKey 3곳이 `application-real.yml`/`application-dev.yml` 에 평문 커밋**. ⭐ 같은 파일에서 **DB 비밀번호·MobileOK 키비번만 Jasypt `ENC()`** 로 감싼 **부분 적용** 상태(주석에 *"25.02.28 KMS 적용 완료"* 표기 + `AwsKmsConfig` 존재 → **전환 중단 정황**). 🟠 High 2건 — ① `application-local.yml` JWT `secret`·AES 키 평문 + **주석 처리된 평문 DB 비밀번호** ② **CORS 허용 Origin·사내 IP 목록이 `ApiAuthInterceptor` Java 소스에 하드코딩**. 그 외 Medium 3(인증 보호가 `jwtSecuredUris` **열거식=기본 공개** / CI 0건으로 테스트 48개 미실행 / 저장소 README가 타 프로젝트 구조 설명). ✅ **네이티브 쿼리 0건**(QueryDSL) · `ddl-auto: validate` · `open-in-view: false` · 운영 Swagger 차단은 **클린**. 조치 미착수 |
| 2026-07-22 | [thehappy_aos](../projects/thehappy_aos/INDEX.md) | 🔴 Critical 1건 — **AES 키/IV·로그인 salt가 `buildSrc/.../Credentials.kt` 상수에 하드코딩 + git 추적**. 🔴 High 1건 — **release 빌드 `isMinifyEnabled=false`**(ProGuard 룰 지정돼 있으나 미적용) → 디컴파일로 키 회수 용이. 그 외 🟠 `usesCleartextTraffic="true"`(+`networkSecurityConfig` 부재) · JS 브릿지 `@JavascriptInterface` **133개** 노출면. ⚠️ **1차 구조 분석 중 검출 — 전수 진단 미수행**. 조치 미착수 |

> 🔁 **반복 패턴 경고**: 서로 다른 두 프로젝트에서 **동일 유형(`src/main/resources/config/application*.yml` 평문 크리덴셜 + git 추적)** 이 연속 검출됐다.
> ECC 대응 프로토콜 5단계 "코드베이스 전수 재점검"에 따라 **아직 진단하지 않은 프로젝트(`ha-api`, `ha-admin`, `happypoint-web2` …)도 같은 스윕을 우선 수행**할 것. 조직 차원의 설정 외부화 표준이 없다는 신호로 본다.
>
> 🆕 **패턴 확장(2026-07-22, ha_panel)**: 시크릿 노출은 **설정 파일 계열만이 아니다.** `ha-panel`은 설정 계열이 완전히 클린(JNDI + 외부 프로퍼티)인데 **소스 코드 상수(`static final String`)에 인증 암호키가 박혀** 있었다.
> → 남은 프로젝트 스윕 시 **위 "시크릿 스윕 명령"의 ①②를 모두 실행**할 것. ①만 돌리면 이 유형은 100% 놓친다.
>
> 📌 **영향도 판정 참고**: 3건 모두 "저장소 접근 = 운영 권한 획득"으로 귀결됐다. 특히 `ha-panel`은 **포인트(금전성 자산)가 걸려 있어** 단순 정보 노출이 아닌 **직접적 금전 손실 시나리오**다. 심각도 산정 시 서비스의 자산 성격을 반영한다.
>
> 🆕 **패턴 확장 2(2026-07-22, thehappy_aos)**: 하드코딩 시크릿이 **4개 연속 프로젝트**에서 검출됐고, 이번엔 **서버가 아닌 네이티브 클라이언트**다. 두 가지가 새롭다.
> 1. **위치가 `src/` 밖이다** — `buildSrc/`(Gradle 빌드 로직)에 있었다. 기존 스윕 명령은 `src/` 기준이라 **경로만 믿으면 놓친다**. → 위 `②-K` 및 `buildSrc` 스윕 추가.
> 2. **클라이언트는 "커밋 안 하면 안전"이 성립하지 않는다** — 앱 바이너리는 이용자에게 배포되므로, 시크릿을 외부 주입으로 바꿔도 **APK 디컴파일로 회수 가능**하다. 따라서 클라이언트에서는 *(a)* 난독화(R8) 활성화가 **보조 방어선으로 필수**이고, *(b)* **애초에 클라이언트가 보유하면 안 되는 비밀인지**를 먼저 판정해야 한다(서버 이관 검토).
> → 남은 클라이언트 프로젝트([thehappy_ios](../projects/thehappy_ios/INDEX.md)) 도 **동일 스윕 + 난독화 설정 점검**을 수행할 것. 앱 2종은 설계가 1:1 대응하므로 **같은 유형이 존재할 개연성이 높다**.
>
> 🆕 **패턴 확장 3(2026-07-22, [gcs_fo](../projects/gcs_fo/WORKLOG-20260722-codebase-analysis.md))**: **5개 연속** 검출. 이번엔 **웹 프론트엔드(TypeScript)** 이며, 세 가지가 새롭다.
> 1. **주석 안에 있었다** — 디버깅용 조기 `return '<크리덴셜>'` 을 주석 처리해 남긴 형태다. **빌드 산출물에서는 사라지지만 git 히스토리에는 영구히 남는다.** → 스윕 시 *"주석은 안전"* 이라는 전제를 버릴 것. 위 `②-JS (b)` 는 주석까지 훑도록 설계돼 있다.
> 2. **`.gitignore` 는 알리바이가 되지 않는다** — `.env*` 4개가 `.gitignore` 에 **전부 등재돼 있는데도 4개 모두 추적 중**이었다. 무시 규칙은 **이미 추적 중인 파일에 소급 적용되지 않는다**. → `.gitignore` 확인이 아니라 **`git ls-files` 로 확인**할 것.
> 3. **프론트 환경변수는 "비밀"이 될 수 없다** — CRA `REACT_APP_*`(Vite `VITE_*`, Next `NEXT_PUBLIC_*` 동일)는 빌드 시 번들에 **문자열로 인라인**된다. `thehappy_aos`의 *"클라이언트 시크릿은 배포로 회수 가능"* 과 **같은 구조이며, 웹은 디컴파일조차 필요 없다**(+ 소스맵이 켜져 있으면 원본 코드까지 노출).
> → 판정 순서를 고정한다: **(a) 이 비밀을 클라이언트가 애초에 보유해야 하는가**(아니면 BFF/릴레이 서버로 이관) → (b) 불가피하면 권한 최소화 + 서버 측 검증(오리진·레이트리밋) → (c) 소스맵 차단은 **보조 방어선으로 필수**.
> → 남은 프론트 프로젝트(`happypoint-web2`, `ha-admin` 등) 진단 시 **`②-JS` + `②-ENV` 를 반드시 포함**할 것.
>
> 🆕 **패턴 확장 4(2026-07-22, [gcs](../projects/gcs/WORKLOG-20260722-codebase-analysis.md))**: **6개 연속** 검출. 이번엔 **부분 적용(partial remediation)** 이라는 새 유형이다.
> 1. **"암호화했다"가 안전을 뜻하지 않는다** — `gcs` 는 Jasypt `ENC()` 를 **이미 쓰고 있는데도** 같은 파일의 AWS·PG 키만 평문이었다. 도구 도입 여부만 확인하면 **"조치 완료"로 오판**한다. → 위 `①-B` 의 **ENC() 개수 ↔ 시크릿 키 개수 대조**를 표준 절차로 삼는다.
> 2. **중단된 마이그레이션은 흔적을 남긴다** — 주석의 *"KMS 적용 완료"* 표기와 실제 상태가 어긋났다. **설정 주석의 "완료" 문구를 근거로 삼지 말 것**, 값 자체를 본다.
> 3. **처음으로 "운영(real) 크리덴셜"이 나왔다** — 지금까지는 dev/공용 위주였다. **`real` 프로파일을 별도 항목으로 분리해 우선 확인**한다.
> 4. **파일 수정만으로 끝나지 않는다** — 이미 커밋된 이상 git 히스토리에 잔존하므로 **키 로테이션이 선행**돼야 한다(패턴 확장 3의 `.gitignore` 알리바이 문제와 같은 성격).
>
> 🆕 **신규 판정축: 인증 보호가 deny-by-default 인가** — `gcs` 는 `jwtSecuredUris` 에 **보호할 URI를 열거**한다(기본값=인증 없음). 시크릿과 무관한 축이지만 **금전 도메인에서 신규 엔드포인트 등록 누락이 곧 공개 API**가 되므로, 앞으로 진단 시 **"보호 방식이 화이트리스트인가 블랙리스트인가"** 를 필수 확인 항목에 넣는다.

## 참고
- [ECC 참조 · 프로토콜](./ecc-reference.md) — ECC는 **읽기 전용**. 좋은 패턴만 이곳(md)으로 이식한다.
- ECC 원문(참조 전용): `../../ECC/rules/common/security.md`, `../../ECC/skills/security-review/SKILL.md`, `../../ECC/the-security-guide.md`
