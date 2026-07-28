---
문서유형: SHARED
프로젝트: 공통
이슈키: --
작성일: 2026-07-16
최종수정: 2026-07-21
작성자: dominic
상태: 진행중
요약: happypointcard 개발/스테이징 서버(EC2) 및 Tomcat 인스턴스 공통 환경 정보
---

# 🖥️ 공통 서버 환경 (개발)

> ⚠️ 이 문서는 접속정보/구성 정보를 담습니다. **비밀번호·키는 이 문서에 적지 마세요.** (별도 보안 저장소 사용)

## 개발서버 (EC2)
- OS: Amazon Linux 2023 (`6.1.x amzn2023 x86_64`)
- 시스템 기본 JDK: **1.8** (`openjdk 1.8.0_322`) — 기존 톰캣들이 사용, **alternatives 변경 금지**
- JDK 21: `/usr/lib/jvm/java-21-amazon-corretto` (설치만, 특정 톰캣만 setenv로 사용)
- 서버 내 톰캣 인스턴스:
  | 인스턴스 | 용도 | 비고 |
  |----------|------|------|
  | `web-tomcat-9.0.68` | ha-web 구버전 | 마이그레이션 전 |
  | `web-tomcat-10.1.57` | ha-web 신버전(JDK21) | HTTP 9022 / shutdown 8010 |
  | `admin-tomcat-9.0.68` | admin | |
  | `api-tomcat-9.0.68` | api | |
  | `cms-tomcat-9.0.68` | cms | |
- 배포 경로: `/app/docs/<앱명>` (예: `/app/docs/ha-web`, `/app/docs/app-web`)
- 톰캣 홈: `/app/server/<인스턴스>`

## Tomcat 10.1 (ha-web) 요점
- JNDI DataSource는 `conf/Catalina/<host>/ROOT.xml` (앱별 context)에 정의 → 드라이버는 WAR의 WEB-INF/lib로 충분
- 가상호스트: `dev-www.happypointcard.com`(ha-web), `dev.happypointcard.com`(app-web)
- `setenv.sh`에서 JAVA_HOME(21)·프로파일(dev)·힙(512~1024m) 지정
- SecurityManager 제거됨(JDK21/Tomcat10.1) — `-Djava.security.manager` 금지

## DB (개발)
- `jdbc/ha`: Oracle (dev-hp-oracle RDS) — 계정/비번은 서버 ROOT.xml에 존재(평문), **문서화 금지**
- `jdbc/cms`: MySQL (dev-hp-cms RDS)

## 스테이징 (STAGING) — ha-web-api Tomcat 10.1.57
2026-07-21 스테이징 서버 톰캣(기존 9.0.68/JDK8/Spring5)의 설정을 **10.1.57(JDK21/Spring6)** 로 이관. **Scouter APM 연동 포함**.
- **포트(★ 개발서버와 동일값 사용)**: HTTP **9022** / shutdown **8010** / redirect 8422
  - ⚠️ 스테이징 기존 9.0.68 포트(8021/8006/8421)는 **사용 불가** → dev와 동일 포트로 통일(사용자 지정).
- **가상호스트**: `stg-www.happypointcard.com`, `stg.happypointcard.com` — **둘 다 동일 앱**(`/app/docs/ha-web-api`) 바인딩(기존 9.0.68도 둘 다 ha-web).
- **프로파일**: `spring.profiles.active=stage`, Heap **1024/1024**(+NewSize128/Metaspace256), `security.properties`, `DisableExplicitGC`.
- **Scouter**: `scouter/agent.java` (agent 2.8.1 이관). **javaagent는 톰캣9 방식대로 `bin/startup.sh`에 배치**(setenv.sh 아님 — 혼동주의, setenv 쪽 스카우터 줄은 주석 유지=중복 금지). `scouter.conf`: obj_name=`STG_HA_WEB`, collector **스테이징 `10.0.70.114`**(기본포트 6100 UDP·TCP).
  - ⚠️ **Scouter collector 규칙**: **스테이징 = `10.0.70.114`(10.x 대역)**, **운영 = `11.7.11.31`(11.x 대역)**. 스테이징 톰캣은 10.x 사용. (초기 이관본 `10.0.70.55`는 SRE 페이퍼테스트용이라 아무 데도 안 뜸)
  - ⚠️ **현재 setenv.sh에서 주석 처리(비활성)** — JDK21 호환 검증 전 안전 기동용. 검증 후 `SCOUTER_OPTS` 2줄 주석 해제 + `CATALINA_OPTS` 끝에 `$SCOUTER_OPTS` 추가로 활성화.
  - **에이전트 버전**: 톰캣9(Java8)=`scouter.agent 2.8.1`(정상, URL 602개 계측). 톰캣10(Java21)=`major version 65`로 2.8.1 실패 → **2.21.3(JDK17/21 지원)으로 교체 완료**(2026-07-21). 기존 2.8.1은 `scouter.agent.jar.2.8.1.bak`로 백업.
  - ⚠️ **collector 서버 버전 호환 확인 필요**: 에이전트를 2.21.3으로 올렸으므로, 스테이징 collector(`10.0.70.114`, scouter-server) 버전이 너무 낮으면(예: 2.8.x) 세션이 안 맺힐 수 있음. 원칙상 **server 버전 ≥ agent 버전** 권장 → 안 뜨면 collector 서버도 업그레이드 검토.
- **DB(스테이징)**: `jdbc/ha` Oracle `SPCADMIN@happy-app-homepage` RDS(ORCL), `jdbc/cms` MySQL `HPC_APP@hp-cms-rds`(CMS). ⚠️ 계정/비번은 서버 ROOT.xml 평문, **문서화 금지**.
- **로컬 설정 정본**: `D:\100_WORKS\web-tomcat-10.1.57` (스테이징으로 커스텀됨), 원본 대조 `D:\100_WORKS\web-tomcat-9.0.68`.
- ⚠️ **검증 TODO**: Scouter 2.8.1의 JDK21 호환(구버전→기동 실패 가능, 최신 에이전트 교체 검토), NewSize 고정값 G1GC 경고 여부.

## 운영 (PRODUCTION) — ha-web-api Tomcat 10.1.57
2026-07-28 운영 서버 톰캣(기존 **8.5.59/JDK8/Spring MVC**)의 설정을 **10.1.57(JDK21/Spring6)** 로 이관. 스테이징 톰캣10 설정을 기반으로 **운영값만 교체**(구조 동일 → 변경 최소). Scouter 연동 포함.
- **포트(★ 운영 원본 유지)**: HTTP **8021** / shutdown **8006** / redirect 8442. `URIEncoding=UTF-8` 유지. executor(8080)·SSL(8443)·AJP(8009)는 전부 주석(미사용, 운영 동일).
  - 운영 원본(8.5.59)의 활성 커넥터는 8021 하나뿐이었음 → 그대로 계승.
- **Host**: `www.happypointcard.com` **1개**(스테이징은 stg-www/stg 2개였음), `appBase=webapps unpackWARs=true autoDeploy=true`, AccessLog prefix `www-access`, Engine `defaultHost=www.happypointcard.com`.
- **JDK21 설치(2026-07-28)**: 운영서버(`ip-10-0-70-57`)에 `java-21-amazon-corretto-devel` 설치 → **Corretto 21.0.11 LTS** @ `/usr/lib/jvm/java-21-amazon-corretto`. **시스템 기본 java = 1.8.0_265 유지**(alternatives 미변경, 다른 톰캣 admin/api/cms 보호). 이 톰캣만 setenv `JAVA_HOME`으로 21 격리. ※ 이 서버 java 는 alternatives 미관리(PATH 기반)라 설치해도 기본 안 바뀜(확인 완료).
- **JVM(setenv.sh)**: 힙 **`-Xms1536m -Xmx1536m`**(운영과 동일) + `-XX:MaxMetaspaceSize=256m`. **NewSize/MaxNewSize 고정은 제거(B안)** — JDK8 튜닝값이라 JDK21 기본 G1GC 자동조정에 맡김(힙 총량은 동일 1536m). 프로파일 **`-Dspring.profiles.active=prod`**. 인코딩/타임존(UTF-8/Asia-Seoul)·headless 유지.
- **Scouter**: `bin/startup.sh`에서 활성화(톰캣9 방식, setenv 쪽은 주석 유지=중복 금지). 에이전트 **2.21.3**(JDK21 호환, 운영 원본 2.8.1 아님). `scouter.conf`: obj_name=**`WEB`**, collector **운영 `11.7.11.31`**(UDP·TCP 6100), 운영 풀옵션 이식(X-Forwarded-For·http헤더/쿼리 프로파일·정적확장자·health.jsp discard).
- **세션 영속**: context.xml `<Manager>`는 스테이징도 주석(비활성)이라 운영(`pathname=""`)과 동일 → **변경 불필요**.
- **DB(운영)**: 톰캣 설정에 DB 없음 → 앱(WAR)이 `spring.profiles.active=prod`로 운영 DB 분기. 계정/비번 **문서화 금지**.
- **로컬 설정 정본**: `D:\100_WORKS\web-tomcat-10.1.57`(2026-07-28 운영값으로 전환), 운영 원본 대조 `D:\100_WORKS\web-tomcat-8.5.59`.
- ⚠️ **확인 필요(배포 전)**: ① 운영 nginx/L4가 8021로 라우팅하는지 ② 운영 collector(`11.7.11.31`) scouter-server 버전이 agent 2.21.3과 호환되는지(server≥agent) ③ JDK21 기동 로그에서 GC 경고 없는지.

## 리버스 프록시 라우팅 (리뉴얼: 프론트+백엔드 한 도메인 분기)
앞단(nginx/ALB)이 경로로 분기:
```
https://<도메인>/
  ├─ /api/**  → Tomcat 9022 (Spring, ha-web-api)
  └─ 그 외     → Next 3000 (pm2, ha-web-fo)
```
- **개발: `https://dev.happypointcard.com/`** — `/api/**`=9022 톰캣 / 그 외=3000 Next(pm2).
- same-origin이라 로그인 세션쿠키(JSESSIONID)·`/api` 호출 그대로 동작(CORS 불필요).
- Next `next.config`의 `/api` 프록시 rewrite는 **로컬 개발(nginx 없음)용 폴백**. 배포 환경에선 nginx가 `/api`를 톰캣으로 보냄.

## 편의 알리어스 (ha-web-api Tomcat 10.1.57) — dev·staging 공통
서버 `~/.bashrc`에 등록. dev·스테이징 모두 톰캣 경로가 동일(`/app/server/web-tomcat-10.1.57`)해서 정의도 동일하다.
```bash
alias start-web-api='/app/server/web-tomcat-10.1.57/bin/startup.sh'
alias stop-web-api='/app/server/web-tomcat-10.1.57/bin/shutdown.sh'
alias log-web-api='tail -f /app/server/web-tomcat-10.1.57/logs/catalina.out'
```
- 등록 후 `source ~/.bashrc`, 확인 `type start-web-api stop-web-api log-web-api`.
- ※ `start-web-api`는 **순수 기동**(startup.sh)만 함. WAR 재배포(shutdown→압축해제→기동→로그)는 별도 `web-api-deploy.sh` 사용.

## 배포 원칙
- WAR 재배포 시 **기존 폴더 삭제 후 재압축해제** (덮어쓰기 금지 — 옛 jar 잔존)
- TLS는 앞단(ALB/nginx) 종단, 톰캣은 평문 HTTP 수신
