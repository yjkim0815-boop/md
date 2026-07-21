# 📦 ha-web Spring 프레임워크 고도화 — 영구 아카이브 (WORK-16665)

> **목적**: 이 문서는 해피포인트 홈페이지(ha-web) 프로젝트를 **Spring 5 / Java 8 / Tomcat 9** 에서
> **Spring 6 / Java 21 / Tomcat 10.1 (Jakarta EE)** 로 전면 마이그레이션한 전 과정을 기록한
> **영구 아카이브**입니다.
>
> **대상 독자**: 이 프로젝트에서 새 채팅(새 계정 포함)을 시작하는 Claude Code / 개발자.
> 이 문서 하나만 읽으면 프로젝트 구조, 마이그레이션 내역, 발생한 모든 오류와 해결책,
> 빌드·배포 절차, 서버 환경, git 이력까지 전부 파악할 수 있도록 작성되었습니다.
>
> **작성 시각 기준**: 2026-07-14 ~ 2026-07-16 작업 세션
> **브랜치**: `feature/WORK-16665` (develop 기준)
> **관련 저장소**: `j-ha-web` (원본), `j-ha-web-api` (이관본, Bitbucket `sectanine/ha-web-api.git`)

---

## 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [기술 스택 (마이그레이션 전)](#2-기술-스택-마이그레이션-전)
3. [코드베이스 구조 분석](#3-코드베이스-구조-분석)
4. [XML 설정 파일 상세 분석](#4-xml-설정-파일-상세-분석)
5. [마이그레이션 의사결정 히스토리 (대화 흐름)](#5-마이그레이션-의사결정-히스토리-대화-흐름)
6. [Tomcat 9 → 10.1 이관 상세](#6-tomcat-9--101-이관-상세)
7. [Spring 6 / Jakarta / Java 21 마이그레이션 전체 내역](#7-spring-6--jakarta--java-21-마이그레이션-전체-내역)
8. [전체 버전 변경표](#8-전체-버전-변경표)
9. [빌드 과정에서 발생한 컴파일 오류와 해결](#9-빌드-과정에서-발생한-컴파일-오류와-해결)
10. [런타임(기동) 오류와 해결](#10-런타임기동-오류와-해결)
11. [SiteMesh Jakarta 변환 절차](#11-sitemesh-jakarta-변환-절차)
12. [빌드 / 배포 절차](#12-빌드--배포-절차)
13. [개발 환경 세팅 (Windows)](#13-개발-환경-세팅-windows)
14. [Git 이력 / 사고 및 복구](#14-git-이력--사고-및-복구)
15. [저장소 이관 (j-ha-web → j-ha-web-api)](#15-저장소-이관-j-ha-web--j-ha-web-api)
16. [잔여 검증 항목 (TODO)](#16-잔여-검증-항목-todo)
17. [민감정보 / 보안 주의](#17-민감정보--보안-주의)
18. [새 채팅 시작 시 참고 체크리스트](#18-새-채팅-시작-시-참고-체크리스트)
19. [부록 A: 주요 파일 변경 상세](#부록-a-주요-파일-변경-상세)
20. [부록 B: 용어 및 배경지식](#부록-b-용어-및-배경지식)

---

## 1. 프로젝트 개요

- **프로젝트명**: ha-web (해피포인트 홈페이지)
- **소유**: SPC / 해피포인트카드
- **성격**: 전통적인 **Spring MVC + JSP + MyBatis** 서버사이드 렌더링 웹 애플리케이션 (Spring Boot 아님)
- **패키징**: `war` (외장 Tomcat 배포)
- **주요 도메인**: 회원(가입/인증/탈퇴/휴면), 카드, 포인트, 쿠폰, 이벤트, 제휴(alliance), 매장(store), 설문(survey), 기부(donation), 고객센터, 라이브방송(live), 브랜드회원
- **Maven groupId/artifactId**: `com.spc:ha-web`, version `0.0.1-SNAPSHOT`
- **기본 작업 디렉터리**: `D:\200_DEV\230_WORKSPACE\happypointcard\j-ha-web`
- **git 기본 브랜치**: `master` (PR 대상), 개발은 `develop`
- **git 사용자**: dominic (dominic.kim@spc.co.kr)

### 배포 아키텍처

- 외장 Tomcat에 **압축 해제된 WAR** 형태로 배포 (`unpackWARs="false"`, docBase 지정 방식)
- **PC/모바일 뷰 분리**: `views/pc`, `views/mobile`, `views/brand` (반응형 아님, User-Agent 분기)
- **이중 데이터소스**: ha(Oracle) + cms(MySQL), JNDI + MyBatis 어노테이션 라우팅
- TLS는 앞단(ALB/nginx)에서 종단, Tomcat은 평문 HTTP 커넥터로 수신

---

## 2. 기술 스택 (마이그레이션 전)

| 구성 | 버전 |
|------|------|
| Java | 8 (1.8) |
| Spring Framework | 5.2.5.RELEASE |
| Spring Security | 5.3.1.RELEASE |
| Servlet | 3.1 (javax) |
| JSP/JSTL | JSTL 1.2 (javax) |
| MyBatis | 3.5.4 / mybatis-spring 2.0.4 |
| Oracle JDBC | ojdbc8 12.2.0.1 |
| MySQL | mysql-connector-java 8.0.18 |
| Jackson | 2.9.10.4 |
| Lombok | 1.18.2 |
| AspectJ | 1.8.9 |
| SiteMesh | 3.0.1 |
| Hibernate Validator | 6.1.4 |
| AntiSamy | 1.5.13 |
| problem-spring-web (Zalando) | 0.24.0-RC.0 |
| snakeyaml | 1.26 |
| AWS SDK (kms/core/s3) | 1.11.x |
| Apache HttpClient | 4.5.2 |
| springfox-swagger2 | 2.9.2 |
| spring-mobile-device | 1.1.5.RELEASE |
| spring-cloud | Finchley.SR1 |
| Log4j2 | 2.17.0 (Log4Shell 패치됨) |
| WAS | Apache Tomcat 9.0.68 |

### 본인인증 / 외부 벤더 라이브러리 (ext-libs 로컬 저장소)

pom.xml 의 `<repositories>` 에 `file://${project.basedir}/ext-libs` 가 로컬 파일 저장소로 등록됨.
- `nice.auth:NiceID:1.1`, `nice.auth:IPIN2Client:1.1` (NICE 본인인증)
- `kcb.jni:okname:2.3.2` (KCB 실명확인)
- `thunder.mail:thunder-mail:1.0.0` (메일)
- 이들은 pom 없이 jar만 존재 → 빌드 시 "POM missing" 경고는 **정상**

---

## 3. 코드베이스 구조 분석

```
src/main/java/com/spc/hpc
├── common       (공통 서비스/유틸)
├── dao          (JndiDAO 등)
└── home
    ├── config       (spring, mybatis, converter, error, jsp, properties)
    ├── controller   (pc / mobile / shared / rest / survey)
    ├── filter       (SpcFilter, RedirectFilter, SitemeshFilter, PagingFilter, AntiSamyFilter, HstsFilter, DeviceRedirectFilter[주석])
    ├── interceptor  (SpcInterceptor)
    ├── listener     (SpcServletContextListener)
    ├── restapi      (model, exception)
    ├── security     (Login/Bearer Aspect, SecurityUtils, SessionUser)
    ├── services     (도메인별 service + repository(MyBatis mapper))
    └── util         (WebUtil, JsonUtil, AES128Util, AwsKmsUtil 등)
```

### 규모 실측 (마이그레이션 시점)

- Java 소스 파일: **335개**
- Controller: 28개 (`*Controller.java`) + REST Resource 다수 → Spring 매핑 **181개**
- JSP: **516개**
- `.tag` 파일: 9개 (`WEB-INF/tags/`)
- `.tld`: 1개 (`WEB-INF/tld/unvus.tld`)
- `@Aspect` 클래스: 3개 (BearerAspect, LoginAspect, SpcMultipartAspect)

### MyBatis 매퍼 도메인 구조

`src/main/resources/mybatis/` 하위:
- `default/**` (ha DB 매퍼): alliance, banner, brand, card, common, coupon, customer, donation, emergency, event, external, shared, sleeveqr, sms, store, survey, user
- `cms/**` (cms DB 매퍼)

### javax 사용 실측 (마이그레이션 전 스캔)

- `javax.servlet.*` 계열: 68개 파일 (servlet/http/jsp)
- `javax.inject`: 10개 파일
- `javax.el`: 1개 파일
- `javax.annotation.PostConstruct`: 1건
- **JSE 표준(유지 대상, 변환 금지)**: `javax.crypto`(암호화), `javax.sql`(DataSource), `javax.naming`(JNDI), `javax.net.ssl`(TLS)
- **JSR-305(유지 대상)**: `javax.annotation.Nonnull`, `javax.annotation.Nullable` (findbugs, jakarta 아님!)
- **JDK 제거 API 미사용 확인**: `javax.xml.bind`(JAXB), `sun.misc`, `com.sun.*` → **0건** (마이그레이션 최대 리스크 없음)

---

## 4. XML 설정 파일 상세 분석

### 4.1 `web.xml` (WEB-INF/web.xml)

**필터 체인** (`/*` 순서 적용):
1. `HstsFilter` — HSTS 헤더 (HTTPS 강제)
2. `CharacterEncodingFilter` — UTF-8
3. `SpcFilter` — 공통 커스텀
4. `RedirectFilter` — `*.spc` 대상 URL 변환/리다이렉트
5. `AntiSamyFilter` — XSS 방어 (정책: `xss/antisamy-myspace.xml`)
6. `SitemeshFilter` — 레이아웃 데코레이션
7. `PagingFilter` — 페이징

**기타**:
- 루트 컨텍스트: `classpath:/*/context-*.xml` (context-common, context-datasource)
- 서블릿 컨텍스트: `/WEB-INF/spring/dispatcher-config.xml`
- 세션 쿠키 `secure=true`
- `TRACE`/`OPTIONS` 메서드 차단 (security-constraint)
- 에러페이지: 400/403/404/405 + 기본 → `/error/*.spc`
- JSP 공통 프리루드: 모든 jsp에 `taglibs.jsp` 자동 include, 공백 트리밍
- 리스너: `ContextLoaderListener`, `RequestContextListener`, `SpcServletContextListener`

**마이그레이션 변경**:
- 스키마 `web-app_3_0` (javax) → **Jakarta EE 6.0** (`https://jakarta.ee/xml/ns/jakartaee`, version 6.0)
- DispatcherServlet에 `<multipart-config>` 추가 (max 20MB, threshold 10MB) — 아래 dispatcher 참조

### 4.2 `dispatcher-config.xml`

- `@Controller` 컴포넌트 스캔 (`com.spc.hpc`), AspectJ 오토프록시
- 뷰 리졸버: `/WEB-INF/views/**.jsp`
- 정적 리소스: `/assets/**`, `/robots.txt`
- 인터셉터 4종: `SpcInterceptor`(공통), `MultipartInterceptor`(업로드), `WebContentInterceptor`×2(`/page/**`, `/assets/**` no-store 캐시)
- **마이그레이션 변경**: `CommonsMultipartResolver`(Spring 6에서 제거됨) → `StandardServletMultipartResolver`

### 4.3 `context-common.xml`

- `ProfileAwareYamlFactoryBean` 으로 `config/application.yml` 을 프로파일별 로딩 → `${...}` 플레이스홀더 주입 (Spring Boot 없이 yml 사용하는 커스텀 방식)
  - ⚠️ 이 빈이 Spring 6에서 snakeyaml 2.x(`TagInspector`)를 요구 → 런타임 오류 원인 (10.2절 참조)
- Jackson ObjectMapper: null 미포함, 미지 프로퍼티 무시, Zalando problem 모듈 등록
- 커스텀 컨버터 3종

### 4.4 `context-datasource.xml` (⭐ 이중 데이터소스)

| 구분 | JNDI | MyBatis config | 매퍼 위치 | 마커 어노테이션 |
|------|------|----------------|-----------|----------------|
| 기본(ha) | `jdbc/ha` | mybatis-default.xml | `mybatis/default/**` | `@DefaultMapper` |
| CMS | `jdbc/cms` | mybatis-cms.xml | `mybatis/cms/**` | `@CmsMapper` |

- JNDI 조회 방식(WAS가 커넥션풀 관리), 각각 별도 SqlSessionFactory/TransactionManager
- `MapperScannerConfigurer` 가 같은 패키지(`home.services`)를 스캔하되 **어노테이션으로 어느 DB에 바인딩할지 구분**
- `Log4jdbcProxyDataSource` 로 SQL 로깅
- **핵심**: `type="javax.sql.DataSource"` 는 JSE 표준이라 Jakarta 전환 대상 아님 (그대로 유지)

### 4.5 XSS 정책 파일

`src/main/resources/xss/`: antisamy-default/ckeditor/myspace/unvus/wysiwyg.xml (AntiSamy 정책)

---

## 5. 마이그레이션 의사결정 히스토리 (대화 흐름)

이 절은 사용자의 질문 흐름과 그에 따른 의사결정을 시간순으로 기록한다.
(새 채팅에서 "왜 이렇게 했는지" 배경을 이해하는 데 사용)

1. **"프로젝트 가볍게 분석해줘"** → 스택/구조 파악 (전통 Spring MVC + JSP + MyBatis WAR).
2. **"XML 설정파일 분석해줘"** → web.xml / dispatcher / context-common / context-datasource 분석. 이중 데이터소스 구조 확인.
3. **"Java 21로 올려줘"** → 규모가 커서 **조사만(Plan)** 수행하기로 결정. 걸림돌 스캔:
   - JAXB/sun.misc 미사용 (호재), AspectJ 1.8.9 / Lombok 1.18.2 는 JDK21 불가, spring-mobile/sitemesh 폐기 라이브러리 이슈.
   - 두 경로 제시: **경로 A**(런타임만 21, Spring 5.3 유지, Tomcat 9) vs **경로 B**(Spring 6 + Jakarta 전면).
4. **"스프링6로"** → **경로 B 선택**. 이때 Tomcat도 10.1로 가야 함이 확정 (Servlet 6.0 = jakarta = Tomcat 10.1).
5. **"톰캣은 10.1로 해야해?"** → Yes. Spring 6 = Servlet 6.0 jakarta → Tomcat 10.1 필수 (9는 javax라 불가, 10.0은 EOL).
6. **"개발서버 톰캣 통째로 복사해두면 분석해줄 수 있어?"** → Tomcat 9.0.68 복사받아 분석.
   - **핵심 발견**: JNDI DataSource가 `conf/Catalina/<host>/ROOT.xml` (앱별 context)에 정의됨. 드라이버 jar는 lib에 없음(WAR의 WEB-INF/lib에서 로딩). setenv 없음(프로파일 주입 위치 외부).
7. **"톰캣 10.1.57 다운로드"** → 10.1.57 확정, 리눅스용 tar.gz.
8. **압축/전송 관련 문답** (리눅스에서 풀고 zip으로 윈도우 반입) → 권한/CRLF 이슈 안내.
9. **"설정값 옮겨줘 + 리눅스 jdk 설정도"** → server.xml/ROOT.xml/setenv.sh/error.html 이식 작성.
10. **포트 변경 요청**: 9021→9022, 8421→8422, shutdown 8006→8009→(AJP 충돌 회피)→**8010**.
11. **JDBC 드라이버 필수 여부** → 앱별 context 정의라 WAR의 WEB-INF/lib로 충분(추가 불필요), 정정.
12. **"스프링부트로 바꿀 수 있어?" / "부트에서 왜 jsp 못써?"** → JSP 516개라 war+외장톰캣이 정답. 부트 jar는 Jasper 제약으로 JSP 불가. 부트 전환은 별도 프로젝트로 판단.
13. **"이제 프로젝트 전부 수정해줘"** → 경로 B 전면 마이그레이션 실행. SiteMesh는 **Jakarta 호환 빌드/포크 사용**, spring-mobile은 **소형 UA 파서로 교체** 결정.
14. 빌드 → 컴파일 오류 반복 수정 (9절) → BUILD SUCCESS.
15. 서버 배포 → 기동 오류 반복 수정 (10절): snakeyaml → AWS SDK → SecurityConfig → DispatcherServlet 정상 진입.
16. **파일명 `ha-web.war` 고정 요청** → 모든 프로파일 finalName을 ha-web으로.
17. **app-web 호스트 무시 요청** → ROOT.xml docBase를 빈 폴더로 지정하거나 제거.
18. **"왜 git에 수정내역이 안올라오지?"** → 브랜치 전환/리셋으로 워킹트리 원복됨을 발견. 작업물은 dangling 커밋 `dd`(7f5640c7)에 보존됨을 확인 → 복구.
19. **"feature/WORK-16665 브랜치 생성하고 커밋 (푸시 금지)"** → develop 기준 브랜치 생성 + cherry-pick 커밋.
20. **"j-ha-web-api 저장소로 소스 이관"** → git archive로 이관 + 브랜치 커밋 (푸시 금지).
21. **본 아카이브 작성**.

---

## 6. Tomcat 9 → 10.1 이관 상세

### 6.1 기존 Tomcat 9.0.68 설정 인벤토리 (개발서버)

- **JNDI DataSource** (`conf/Catalina/<host>/ROOT.xml`, 두 호스트 동일):
  - `jdbc/ha` (Oracle), `jdbc/cms` (MySQL) — DBCP 관리, maxTotal=5
- **가상호스트 2개**: `dev-www.happypointcard.com`(ha-web), `dev.happypointcard.com`(app-web)
- **커넥터**: HTTP 9021 (평문). SSL/AJP 전부 주석 (TLS는 앞단 종단)
- **shutdown 포트**: 8006
- **Valve**: `ErrorReportValve`(showReport=false, 커스텀 error.html), `AccessLogValve`(X-Forwarded-For)
- **커스텀 에러페이지**: `error/error.html` (절대경로 하드코딩)
- **docBase**: `/app/docs/ha-web`, `/app/docs/app-web`
- **setenv**: 없음 (프로파일/힙 주입은 외부 스크립트/서비스 추정)
- **드라이버 jar**: Tomcat lib에 없음 → WAR WEB-INF/lib에서 로딩

### 6.2 Tomcat 10.1.57 이식 결과

새 배포본(`/app/server/web-tomcat-10.1.57`)에 아래를 이식/작성:

**`conf/server.xml`** (변경점):
- shutdown 포트: 8005 → **8010**
- HTTP 커넥터: 8080 → **9022** (+`URIEncoding="UTF-8"`), redirectPort → **8422**
- Engine `defaultHost="dev-www.happypointcard.com"`
- 가상호스트 2개 재작성 (`unpackWARs="false" autoDeploy="true"`)
- ErrorReportValve error.html 경로를 **web-tomcat-10.1.57** 로 갱신
- AccessLogValve 패턴 유지 (nwww-access-log / www-access-log)

**`conf/Catalina/dev-www.happypointcard.com/ROOT.xml`** (ha-web):
- docBase `/app/docs/ha-web`, JNDI `jdbc/ha`·`jdbc/cms`
- `type="javax.sql.DataSource"` **그대로** (JSE 표준)

**`conf/Catalina/dev.happypointcard.com/ROOT.xml`** (app-web):
- docBase `/app/docs/app-web` (별개 앱)
- ⚠️ app-web은 아직 javax(Spring 5)라 Tomcat 10.1에서 기동 실패 → 무시하려면 빈 폴더 지정 또는 ROOT.xml 제거

**`error/error.html`**: 기존 커스텀 에러페이지 복사

**`bin/setenv.sh`** (신규):
```sh
export JAVA_HOME=/usr/lib/jvm/java-21-amazon-corretto
export JRE_HOME=$JAVA_HOME
SPRING_PROFILE="-Dspring.profiles.active=dev"
JVM_MEM="-Xms512m -Xmx1024m"
JVM_ETC="-Dfile.encoding=UTF-8 -Duser.timezone=Asia/Seoul -Djava.awt.headless=true"
export CATALINA_OPTS="$CATALINA_OPTS $JVM_MEM $JVM_ETC $SPRING_PROFILE"
```

### 6.3 포트 최종값

| 용도 | 값 |
|------|-----|
| HTTP 웹 (실제 서비스 수신) | **9022** |
| redirectPort (참고값, 미개방) | 8422 |
| shutdown | 8010 |

### 6.4 서버 환경 (개발서버, EC2 Amazon Linux 2023)

- OS: `6.1.161-183.298.amzn2023.x86_64`
- 시스템 기본 java: **1.8** (`openjdk 1.8.0_322`) — 다른 톰캣(admin/api/cms)들이 사용, **건드리면 안 됨**
- JDK 21: `/usr/lib/jvm/java-21-amazon-corretto` (설치만, alternatives 미변경)
- 이 톰캣만 `setenv.sh`의 JAVA_HOME으로 21 격리 사용
- 서버 내 다른 톰캣들: `admin-tomcat-9.0.68`, `api-tomcat-9.0.68`, `cms-tomcat-9.0.68`, `web-tomcat-9.0.68` (기존), `web-tomcat-10.1.57` (신규)
- 배포 경로: `/app/docs/ha-web`, `/app/docs/app-web`

---

## 7. Spring 6 / Jakarta / Java 21 마이그레이션 전체 내역

### 7.1 소스 네임스페이스 치환 (javax → jakarta)

- `javax.servlet` → `jakarta.servlet` (68개 파일)
- `javax.el` → `jakarta.el`
- `javax.inject` → `jakarta.inject`
- `javax.annotation.PostConstruct/PreDestroy` → `jakarta.annotation.*`
- **유지(변환 금지)**: `javax.crypto`, `javax.sql`, `javax.naming`, `javax.net.ssl` (JSE 표준), `javax.annotation.Nonnull/Nullable` (JSR-305)
- **서블릿 요청 속성 키**도 변경: `javax.servlet.error.*`, `javax.servlet.forward.*` 등 → `jakarta.servlet.*` (JSP/Java 내 문자열)

### 7.2 JSP / 태그 / TLD

- taglib URI 전면 교체 (516 JSP + 9 tag):
  - `http://java.sun.com/jsp/jstl/core` → `jakarta.tags.core`
  - `.../functions` → `jakarta.tags.functions`, `/fmt` → `jakarta.tags.fmt`, `/sql` → `jakarta.tags.sql`
- JSP scriptlet 내 `import="javax.servlet..."` → `jakarta.servlet`
- `unvus.tld`: j2ee 2.0 스키마 → **Jakarta EE web-jsptaglibrary 3.0**

### 7.3 코드 레벨 API 변경 (Spring 6 제거/변경 대응)

| 파일 | 변경 |
|------|------|
| `SecurityConfig.java` | `WebSecurityConfigurerAdapter`(제거됨) → `SecurityFilterChain` @Bean. `authorizeRequests().antMatchers` → `authorizeHttpRequests(...requestMatchers...)`. 최종적으로 MvcRequestMatcher 이슈로 `.anyRequest().permitAll()` 만 남김 |
| `SpcInterceptor.java`, `MultipartInterceptor.java` | `HandlerInterceptorAdapter`(제거됨) → `implements HandlerInterceptor` |
| `NetConnectionManager.java` | RestTemplate 요청 팩토리를 **HttpClient 5**(hc.client5) 기반으로. 기존 httpclient4 경로(getHttpClient)는 유지 |
| `JscksonConfig.java` | `org.zalando.problem.ProblemModule` → `org.zalando.problem.jackson.ProblemModule` |
| `WebUtil.java` | spring-mobile `Device/DeviceResolver/LiteDeviceResolver` 제거 → `isMobileUserAgent()` User-Agent 정규식 파서 |
| `RedirectFilter.java` | spring-mobile import 제거 (미사용) |
| `DeviceRedirectFilter.java` | (주석처리 필터지만 컴파일 대상) spring-mobile → WebUtil UA 기반으로 |
| `JsonUtil.java` | raw `TypeReference` → `TypeReference<T>` (Jackson 제네릭 엄격화) |
| `SpcResultSetHandler.java` | MyBatis 3.5.16의 `getMappedColumnNames()`가 `Set` 반환 → `new ArrayList<>(...)` 로 감싸 List 유지 (2곳) |
| `HappyLiveController.java` | 미사용 `net.bytebuddy.utility.RandomString` import 제거 |

### 7.4 라이브러리 교체 결정

- **spring-mobile-device**: 폐기(javax) → 자체 UA 파서로 교체
- **springfox**: Spring 6 미지원 → 제거하고 `io.swagger:swagger-annotations` 만 유지 (어노테이션만 사용, Docket/UI 설정 없어 소스 무변경)
- **commons-fileupload**: Spring 6 표준 멀티파트로 대체하여 제거
- **SiteMesh 3.0.1**: 공식 jakarta 릴리스 없음 → `jakartaee-migration` 툴로 변환한 jar를 `ext-libs`에 `3.0.1-jakarta`로 등록 (11절)
- **spring-cloud**: 미사용 → 제거

---

## 8. 전체 버전 변경표

### 플랫폼 / 런타임
| 구분 | 전 | 후 |
|------|----|----|
| Java (JDK) | 8 | **21** |
| Tomcat | 9.0.68 | **10.1.57** |
| 네임스페이스 | javax.* | **jakarta.*** |
| Servlet API | 3.1 | **6.0** |

### Spring
| 구분 | 전 | 후 |
|------|----|----|
| Spring Framework | 5.2.5 | **6.1.14** |
| Spring Security | 5.3.1 | **6.2.6** |
| spring-mobile-device | 1.1.5 | **제거** |
| spring-cloud | Finchley.SR1 | **제거** |

### 데이터 / 영속성
| 구분 | 전 | 후 |
|------|----|----|
| MyBatis | 3.5.4 | **3.5.16** |
| MyBatis-Spring | 2.0.4 | **3.0.3** |
| Oracle JDBC | ojdbc8 12.2 | **ojdbc11 21.9.0.0** |
| MySQL | mysql-connector-java 8.0.18 | **mysql-connector-j 8.4.0** |

### 주요 라이브러리
| 구분 | 전 | 후 |
|------|----|----|
| Jackson | 2.9.10.4 | **2.17.2** |
| snakeyaml | 1.26 | **2.2** |
| AWS SDK (kms/core/s3, bom) | 1.11.x | **1.12.780** |
| Hibernate Validator | 6.1.4 | **8.0.1** |
| Lombok | 1.18.2 | **1.18.34** |
| AspectJ (rt/weaver) | 1.8.9 | **1.9.22.1** |
| AntiSamy | 1.5.13 | **1.7.7** |
| problem-spring-web | 0.24.0-RC.0 | **0.29.1** |
| jackson-datatype-problem | (전이) | **0.27.1** (명시 추가) |
| Apache HttpClient | 4.5.2 | **4.5.2 유지 + httpclient5 5.3.1 추가** |
| JSTL | 1.2 (javax) | **3.0.1** (jakarta + glassfish 구현) |
| SiteMesh | 3.0.1 (javax) | **3.0.1-jakarta** (자체 변환 jar) |
| commons-fileupload | 1.4 | **제거** |
| springfox-swagger2 | 2.9.2 | **제거** |
| swagger-annotations | (전이) | **1.6.14** |

### 신규 추가 의존성
| 라이브러리 | 버전 | 목적 |
|-----------|------|------|
| jakarta.inject-api | 2.0.1 | javax.inject 대체 |
| jakarta.annotation-api | 2.1.1 | @PostConstruct 등 |
| jakarta.el-api | 5.0.1 | javax.el |
| jakarta.servlet-api | 6.0.0 | provided |
| jakarta.servlet.jsp-api | 3.1.1 | provided |
| org.glassfish.expressly | 5.0.0 | EL 구현체 |
| jsr305 (findbugs) | 3.0.2 | @Nonnull/@Nullable |

### Maven 플러그인
| 플러그인 | 전 | 후 |
|----------|----|----|
| maven-compiler-plugin | 3.8.0 (1.8) | **3.13.0 (21)** |
| aspectj-maven-plugin | com.github.m50d 1.11.1 | **dev.aspectj 1.13.1** |
| maven-war-plugin | 3.2.2 | **3.4.0** |

### 빌드 산출물 파일명
- 모든 프로파일(local/dev/stage/prod) `finalName` = **`ha-web`** → `ha-web.war` (프로파일 무관 동일 파일명. 내부 설정은 프로파일별 상이하므로 빌드 시 `-P` 지정 필수)

---

## 9. 빌드 과정에서 발생한 컴파일 오류와 해결

빌드 명령: `mvn clean package -P dev` (JDK 21)

### 1차 컴파일 오류 (7건)
| 오류 | 파일 | 원인 | 해결 |
|------|------|------|------|
| `package org.zalando.problem.jackson does not exist` / `ProblemModule` | JscksonConfig | problem 0.29의 jackson 모듈 패키지 | import 변경 + `jackson-datatype-problem:0.27.1` 추가 |
| `HandlerInterceptorAdapter` cannot find symbol | SpcInterceptor, MultipartInterceptor | Spring 6에서 제거 | `implements HandlerInterceptor` |
| `package net.bytebuddy.utility does not exist` | HappyLiveController | 미사용 import | import 제거 |

### 2차 컴파일 오류 (4건)
| 오류 | 파일 | 원인 | 해결 |
|------|------|------|------|
| `HttpClient cannot be converted to org.apache.hc.client5...` | NetConnectionManager | Spring 6 `HttpComponentsClientHttpRequestFactory`가 HttpClient5 요구 | httpclient5 추가 + RestTemplate 팩토리 httpclient5로 |
| `Set<String> cannot be converted to List<String>` (2곳) | SpcResultSetHandler | MyBatis 3.5.16 `getMappedColumnNames()` 반환형 변경 | `new ArrayList<>(...)` 래핑 |
| `Object cannot be converted to T` | JsonUtil | raw TypeReference | `TypeReference<T>` |

→ 이후 **BUILD SUCCESS**, `target/ha-web.war` 생성. (남은 경고들은 기존부터 있던 raw type/deprecated 경고로 빌드 무영향)

---

## 10. 런타임(기동) 오류와 해결

배포 후 `catalina.out` 기동 로그에서 한 계층씩 순차 발생. **매번 재빌드 + 서버 폴더 완전 삭제 후 재배포**가 원칙 (덮어쓰기 시 옛 jar 잔존으로 동일 오류 반복).

### 10.1 `NoClassDefFoundError: javax/servlet/ServletContextListener`
- **호스트**: `dev.happypointcard.com` (**app-web**, `/app/docs/app-web`) — **별개의 아직-javax 앱**. ha-web 아님.
- 해결: app-web을 안 쓸 거면 해당 ROOT.xml 제거 또는 docBase를 빈 폴더로 지정.

### 10.2 `NoClassDefFoundError: org/yaml/snakeyaml/inspector/TagInspector`
- **원인**: `ProfileAwareYamlFactoryBean`(Spring `YamlProcessor` 상속)이 snakeyaml **2.x** 요구. pom은 1.26.
- **해결**: snakeyaml 1.26 → **2.2**.

### 10.3 `NoClassDefFoundError: com/fasterxml/jackson/databind/PropertyNamingStrategy$PascalCaseStrategy`
- **원인**: `PascalCaseStrategy`는 Jackson 2.12에서 제거된 내부 클래스. AWS SDK **1.11.x**가 이를 참조하는데 Jackson은 2.17로 상향됨.
- **해결**: AWS SDK 1.11.x → **1.12.780** (bom + kms/core/s3).

### 10.4 `No bean named 'mvcHandlerMappingIntrospector' ... required to use MvcRequestMatcher`
- **원인**: Spring Security 6에서 `requestMatchers("/css/**")` 문자열은 MvcRequestMatcher로 처리 → MVC 컨텍스트(dispatcher)의 introspector 필요. 그러나 SecurityConfig는 루트 컨텍스트에 있어 못 찾음.
- **해결**: 모든 요청 permitAll 설정이므로 세부 매처 제거 → `.anyRequest().permitAll()` 만 남김.

### 10.5 이후
- Root 컨텍스트 정상 → **DispatcherServlet 컨텍스트 초기화**(매핑 181개), AspectJ/Hibernate Validator 8 정상 로드까지 진행. 여기까지 기동 오류 없음.
- ⏭ 남은 실검증: JSP 렌더링/SiteMesh 레이아웃/DB 연결/벤더 jar(NiceID·okname) JDK21 동작 (16절 TODO).

---

## 11. SiteMesh Jakarta 변환 절차

SiteMesh 3.0.1은 javax 기반이며 공식 jakarta 릴리스가 없어, Apache **jakartaee-migration** 툴로 jar를 변환하여 프로젝트 로컬 저장소(`ext-libs`)에 등록한다. **최초 1회만** 수행하면 되고, 변환 jar와 `.pom`은 git에 커밋되어 있어 이후 별도 작업 불필요.

- pom 참조 좌표: `org.sitemesh:sitemesh:3.0.1-jakarta`
- 로컬 저장소 경로: `ext-libs/org/sitemesh/sitemesh/3.0.1-jakarta/` (jar + 수동 작성 .pom)
- 변환 스크립트: `ext-libs/convert-sitemesh-jakarta.sh` (리눅스/맥), `ext-libs/convert-sitemesh-jakarta.ps1` (윈도우)

### Windows 수동 변환 (Maven 없이, JDK만)
```powershell
cd "D:\200_DEV\230_WORKSPACE\happypointcard\j-ha-web"
Invoke-WebRequest "https://repo1.maven.org/maven2/org/sitemesh/sitemesh/3.0.1/sitemesh-3.0.1.jar" -OutFile "$env:TEMP\sitemesh-3.0.1.jar"
Invoke-WebRequest "https://repo1.maven.org/maven2/org/apache/tomcat/jakartaee-migration/1.0.9/jakartaee-migration-1.0.9-shaded.jar" -OutFile "$env:TEMP\jakartaee-migration.jar"
java -jar "$env:TEMP\jakartaee-migration.jar" "$env:TEMP\sitemesh-3.0.1.jar" "ext-libs\org\sitemesh\sitemesh\3.0.1-jakarta\sitemesh-3.0.1-jakarta.jar"
```
`.pom` 은 이미 저장소에 포함(수동 작성). 빌드 시 WAR의 WEB-INF/lib에 자동 번들 → 서버 추가 설치 불필요.

> ⚠️ `mvn`으로 최초 빌드 시 로컬 저장소 캐시 miss가 이전 시도로 캐시돼 있으면 `-U` 옵션으로 강제 갱신. 그래도 안 되면 `~/.m2/repository/org/sitemesh` 삭제 후 재빌드.
> checksum 경고(`no checksums available`)는 로컬 파일 저장소라 **정상**, 무시.

---

## 12. 빌드 / 배포 절차

### 12.1 빌드 (Windows, JDK 21 + Maven 3.9.x)
```powershell
cd "D:\200_DEV\230_WORKSPACE\happypointcard\j-ha-web"
mvn clean package -P dev
# 결과: target\ha-web.war
```
- IntelliJ 사용 시: Maven 도구창 → Profiles에서 `dev` 체크 → Lifecycle clean → package. Runner JRE를 **21**로.
- 프로파일별 산출물 이름은 모두 `ha-web.war` (내부 설정만 상이). 환경에 맞는 `-P` 필수.

### 12.2 배포 (리눅스, Tomcat 10.1.57)
```bash
/app/server/web-tomcat-10.1.57/bin/shutdown.sh
cd /app/docs && rm -rf ha-web && mkdir ha-web && cd ha-web
jar -xf /업로드경로/ha-web.war        # 또는 unzip
ls WEB-INF/lib/ | grep -E "snakeyaml|sitemesh"   # 2.2 / 3.0.1-jakarta 확인
/app/server/web-tomcat-10.1.57/bin/startup.sh
tail -f /app/server/web-tomcat-10.1.57/logs/catalina.out
```
- ⚠️ **반드시 기존 폴더 삭제 후 재압축해제**. 덮어쓰기 금지(옛 jar 잔존).
- 기동 후 확인: `ss -tlnp | grep -E '9022|8010'`, `curl -I http://localhost:9022/page/main/index.spc`

---

## 13. 개발 환경 세팅 (Windows)

- **JDK 21**: `C:\Program Files\Java\jdk-21` (이 PC엔 설치돼 있음). 로컬 기본 java는 25일 수 있음 → 빌드는 21 사용 권장.
- **Maven 3.9.16**: `C:\tools\apache-maven-3.9.16` (수동 zip 설치). winget 설치는 실패한 이력 있음.
- 환경변수 (User 범위, 관리자 불필요):
  - `JAVA_HOME = C:\Program Files\Java\jdk-21`
  - PATH에 `%JAVA_HOME%\bin` (25보다 앞), `C:\tools\apache-maven-3.9.16\bin`
- 확인: 새 PowerShell 창에서 `mvn -v` → `Java version: 21.x` 여야 함.
- IntelliJ JDK/Maven 설정은 **프로젝트별**이라 다른 1.8 프로젝트에 영향 없음.

---

## 14. Git 이력 / 사고 및 복구

### 사고 경위
- 마이그레이션 작업은 **커밋되지 않은 워킹트리 변경** 상태로 진행됨.
- 중간에 브랜치 전환(`qa` ↔ `develop`)과 `qa` 브랜치 `Reset to 03e926d8` 가 발생 → develop 워킹트리가 **원본으로 원복**되어 "수정 내역이 git에 안 보이는" 상황 발생.
- 다행히 작업 전체가 **dangling 커밋 `dd`(7f5640c7, 2026-07-14 17:14)** 에 보존됨 (reflog로 확인).
  - 이 커밋은 최종 상태 전부 포함(Spring6.1.14/Java21, snakeyaml 2.2, AWS 1.12.780, httpclient5, ojdbc11, SecurityConfig anyRequest, sitemesh jar 등).

### 복구
- `develop` 기준 **`feature/WORK-16665`** 브랜치 생성 후 `git cherry-pick --no-commit 7f5640c7` 로 변경 적용 → 커밋.
- 커밋 `17ad2c1f` (110 files changed, 507 insertions, 341 deletions). **푸시는 사용자가 직접**.

### 교훈 (새 채팅에서 반드시 준수)
- 작업 중간중간 커밋하거나 최소한 브랜치 전환 전 stash/commit.
- `git checkout .` / 브랜치 전환 / reset 시 커밋 안 된 변경 유실 주의.
- 유실 의심 시 `git reflog`, `git fsck --lost-found`, dangling commit 확인.

---

## 15. 저장소 이관 (j-ha-web → j-ha-web-api)

- **대상**: `D:\200_DEV\230_WORKSPACE\happypointcard\j-ha-web-api`
- **대상 원격**: `https://bitbucket.org/sectanine/ha-web-api.git` (origin, master, 초기 상태 README만)
- **방법**: 원본에서 `git archive --format=tar HEAD | (cd ../j-ha-web-api && tar -xf -)` 로 tracked 소스만 복사 (`.git`·`target/` 제외).
- 대상에서 `feature/WORK-16665` 브랜치 생성 → `git add -A` → 커밋 `b60d1ea` (2062 files). **푸시는 사용자가 직접**.
- 대상의 기존 `README.md`(Initial commit)는 유지됨.

---

## 16. 잔여 검증 항목 (TODO)

빌드·기동(컨텍스트 초기화)까지는 성공. 아래는 **실제 사용 시나리오 검증 필요** (미완료):

- [ ] JSP 516개 화면 렌더링 (Jasper 런타임 컴파일 — taglib/EL/속성 오류는 페이지 접속 시 드러남)
- [ ] SiteMesh 데코레이션(레이아웃) 정상 동작 (`WEB-INF/layout/*.jsp`)
- [ ] DB 연결 실동작: Oracle `jdbc/ha`, MySQL `jdbc/cms` (SELECT/INSERT, 트랜잭션, 페이징 인터셉터)
- [ ] 본인인증 벤더 모듈 JDK 21 동작: **NiceID / IPIN2Client / KCB okname** (네이티브/구형 API 리스크 최상)
- [ ] 파일 업로드 (`StandardServletMultipartResolver` + multipart-config)
- [ ] AWS S3 / KMS 기능 (SDK 1.12)
- [ ] 이메일 발송 (thunder-mail)
- [ ] 예외 응답 포맷 (problem-spring-web 0.29 / Jackson 직렬화)
- [ ] app-web 호스트 처리 최종 결정 (마이그레이션 or 제거)
- [ ] log4jdbc-remix 0.2.7, 구형 라이브러리들 JDK21 런타임 스모크

---

## 17. 민감정보 / 보안 주의

- **개발서버 DB 접속정보가 평문**으로 존재 (`conf/Catalina/<host>/ROOT.xml`):
  - `jdbc/ha` (Oracle): 계정 `HAMBR_DEV` / dev-hp-oracle RDS
  - `jdbc/cms` (MySQL): 계정 `HPCMS_DEV` / dev-hp-cms RDS
  - ⚠️ Tomcat 설정 폴더를 워크스페이스/저장소에 넣을 때 **비밀번호 노출 위험**. git 커밋 금지, 필요 시 마스킹.
- `application.yml`에 KMS 암호화 값, 다수 외부 API 엔드포인트(happymarket, oilbank, ok-name, adot 등) 존재.
- Jasypt로 설정 일부 암호화 (`SecurityUtils`).
- Tomcat 10.1 + JDK 21: **SecurityManager 제거됨** — `-Djava.security.manager` 관련 옵션 사용 금지.

---

## 18. 새 채팅 시작 시 참고 체크리스트

새 채팅(새 계정 포함)에서 이 프로젝트를 다룰 때:

1. **현재 상태**: 이 프로젝트는 이미 **Spring 6 / Java 21 / Jakarta / Tomcat 10.1** 로 마이그레이션 완료(빌드·기동 성공). 원복하지 말 것.
2. **브랜치**: 작업물은 `feature/WORK-16665` 에 있음 (원본 `j-ha-web`, 이관본 `j-ha-web-api`).
3. **빌드**: `mvn clean package -P dev` (JDK 21 필수). 산출물 `target/ha-web.war`.
4. **SiteMesh**: `ext-libs`의 `sitemesh:3.0.1-jakarta` 커밋본 사용. 없으면 11절대로 재생성.
5. **javax 유지 대상 혼동 금지**: `javax.crypto/sql/naming/net.ssl`(JSE), `javax.annotation.Nonnull/Nullable`(JSR-305)는 jakarta로 바꾸면 안 됨.
6. **배포**: 반드시 서버 폴더 삭제 후 재압축해제 (덮어쓰기 금지).
7. **포트**: HTTP 9022 / shutdown 8010.
8. **app-web(dev.happypointcard.com)**: 별개의 아직-javax 앱. ha-web과 무관, 기동 실패는 예상된 것.
9. **DB 접속정보 평문 주의** (17절).
10. **잔여 검증(16절)** 이 실제 남은 작업. 특히 JSP 화면 / 벤더 본인인증 jar / DB.

---

## 부록 A: 주요 파일 변경 상세

### A.1 SecurityConfig.java (최종)
```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(authorize -> authorize.anyRequest().permitAll())
            .csrf(csrf -> csrf.csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse()));
        return http.build();
    }
    @Bean
    public CsrfTokenRepository csrfTokenRepository() {
        CookieCsrfTokenRepository repository = CookieCsrfTokenRepository.withHttpOnlyFalse();
        repository.setCookieName("XSRF-TOKEN");
        repository.setCookiePath("/");
        return repository;
    }
}
```

### A.2 WebUtil — UA 파서 (spring-mobile 대체)
```java
private static final Pattern MOBILE_UA_PATTERN = Pattern.compile(
    "(?i).*(Mobile|Android|iPhone|iPod|iPad|BlackBerry|Windows Phone|webOS|Opera Mini|IEMobile|Silk).*");

public static String deviceType(HttpServletRequest request) {
    return isMobileUserAgent(request) ? MOBILE : PC;
}
public static boolean isMobileUserAgent(HttpServletRequest request) {
    String ua = request.getHeader("User-Agent");
    return ua != null && MOBILE_UA_PATTERN.matcher(ua).matches();
}
```

### A.3 NetConnectionManager — RestTemplate을 HttpClient5로
- `getRestTemplate(int timeout)` 내부에서 httpclient5 기반 `CloseableHttpClient`(trust-all SSL + 타임아웃)를 만들어 `HttpComponentsClientHttpRequestFactory`에 주입.
- 기존 `getHttpClient()`(httpclient4, SslHttpClientBuilder)는 다른 소비자(HttpsClient/ApiService/SsoService)를 위해 유지.

### A.4 web.xml multipart-config
```xml
<multipart-config>
    <max-file-size>20000000</max-file-size>
    <max-request-size>20000000</max-request-size>
    <file-size-threshold>10000000</file-size-threshold>
</multipart-config>
```

### A.5 dispatcher-config.xml multipartResolver
```xml
<beans:bean id="multipartResolver"
    class="org.springframework.web.multipart.support.StandardServletMultipartResolver" />
```

---

## 부록 B: 용어 및 배경지식

- **Jakarta EE 전환**: Java EE가 Eclipse 재단으로 이관되며 `javax.*` → `jakarta.*` 네임스페이스 변경. Spring 6 / Tomcat 10 세대의 분기점.
- **왜 Tomcat 10.1**: Spring 6 = Servlet 6.0(jakarta). Tomcat 9=Servlet4.0(javax, 불가), 10.0=Servlet5.0(EOL), 10.1=Servlet6.0(권장), 11=Servlet6.1(JDK17+).
- **왜 부트 jar에서 JSP 불가**: Jasper 엔진이 실행형 jar의 중첩 jar 내부 JSP를 리소스로 못 찾음. JSP 유지 시 war + 외장 톰캣이 정답.
- **이중 데이터소스 라우팅**: `@DefaultMapper`(ha) / `@CmsMapper`(cms) 마커로 MapperScannerConfigurer가 구분.
- **ext-libs 로컬 저장소**: pom `<repositories>`의 `file://.../ext-libs` — Maven Central에 없는 벤더 jar를 파일 저장소 레이아웃으로 두고 참조.

---

*본 문서는 ha-web Spring 프레임워크 고도화(WORK-16665) 작업의 영구 아카이브입니다. 프로젝트 진행에 따라 16절 TODO가 해소되면 갱신하십시오.*
