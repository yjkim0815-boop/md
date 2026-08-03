---
문서유형: SHARED
프로젝트: 공통
이슈키: --
작성일: 2026-07-16
최종수정: 2026-08-03
작성자: dominic
상태: 진행중
요약: happypointcard 개발/스테이징/운영 서버(EC2)·Tomcat 인스턴스 공통 환경 정보 (2026-08-03 배치서버 `ip-10-0-70-71`[NDSoft SMS 에이전트+Anyframe 배치] · 검색서버 `ip-10-0-75-31`[와이즈넛 SF-1 + Elasticsearch 8.19] 등록)
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

## 배치서버 (`ip-10-0-70-71`) — 2026-08-03 신규 등록
웹/API 톰캣 서버와 **별개의 서버**. 한 서버에 **성격이 다른 두 시스템이 공존**하므로 혼동 주의.

| 시스템 | 경로 | 런타임 | 성격 |
|---|---|---|---|
| **SMS 발송 에이전트** | `/app/ndsoft` | Java (힙 64MB 고정, `KSC5601`) | **(주)엔디소프트 NDMG** 벤더 납품 바이너리. 상시 상주 |
| **Anyframe 배치** | `/app/batch` | `/opt/java/java-se-8u43` (JDK8) | 삼성SDS Anyframe. Spring 2.5.6 / spring-batch 1.1.4. 잡 단위 기동 |

- **실행 계정**: 둘 다 `ec2-user`
- **Anyframe 런처**: `com.sds.anyframe.batch.launcher.BatchJobLauncher <잡CFG.xml> BASE_DT=… BASE_TM=… RUN_MODE=PROD`
  - 예: `hp/batch/wthr/gov/GovForecastGrib_CFG.xml`(기상청 예보) — 분 단위 기동 확인
  - DB 드라이버 3종 동시 탑재: `ojdbc8` · `mysql-connector-j 8.0.32` · `sqljdbc4`
  - KB 저장소 [spc_batch](../projects/spc_batch/INDEX.md) / [spc_spring_batch](../projects/spc_spring_batch/INDEX.md) 와의 **동일 여부는 미확인**
- **SMS 에이전트 요약**: 설치 루트 `/app/ndsoft`(`bin`/`conf`/`lib`/`logs`), jar `lib/nd-message-agent-spc.jar`(**2016-12 빌드**), 메인 `ndsoft.message.agent.base.executor.ConsoleExecutor`
  - ⚠️ **`-cp` 가 상대경로(`..//lib/`)** → **반드시 `/app/ndsoft/bin` 에서 기동**. cwd 틀리면 기동 실패
  - ⚠️ **PPID=1 · systemd 미등록** → 프로세스 사망 시 **자동 재기동 없음**
  - ⚠️ `-Dprocess.id=ndsoft-agnet-sms` 의 `agnet` 은 **벤더 원문 오타** — 임의 수정 금지
  - ⚠️ `conf/jdbc.conf`·`conf/agent.conf` 에 **평문 크리덴셜 우려** → 조회 시 마스킹, **문서화 금지**
  - 📄 상세·리스크·교체 검토: **[SMS Agent 전환](../projects/task/sms-agent-replacement/INDEX.md)** (정본)

## 검색 서버 (`ip-10-0-75-31`) — 2026-08-03 신규 등록
⚠️ **배치서버(`ip-10-0-70-71`)와 다른 별도 서버.** 혼동 주의.
**상용 검색엔진(와이즈넛 SF-1)과 Elasticsearch가 같은 서버에 공존**한다.

| 엔진 | 경로 | 계정 | 기동 | 비고 |
|---|---|---|---|---|
| **와이즈넛 SF-1** | `/app/search/sf-1` | `ec2-user` | `cmanager` **2025년** / `isc` **2026-02-25** | 상용. **라이선스 2026-04-05 만료 — 폐기 대상인데 프로세스 잔존** |
| **Elasticsearch 8.19.12** | `/usr/share/elasticsearch` (RPM) | `elasticsearch` | **2026-03-29** | **현행 검색엔진**. 힙 `-Xms2g -Xmx2g`, G1GC, 번들 JDK, x-pack-ml |

> 📌 **공존 사유 확정(2026-08-03)**: **[매장검색엔진 고도화 (와이즈넛 -> 엘라스틱서치)](../projects/task/store-search-upgrade/INDEX.md)** 과업으로 SF-1 라이선스 만료(2026-04-05) 전에 ES로 전환했다. 현행은 **ES**, SF-1은 **미정리 잔존**이다. ⚠️ SF-1 정지 전 참조하는 앱이 없는지 먼저 확인할 것.

### 와이즈넛 SF-1 구성
```
/app/search/sf-1/
├─ bin/      cmanager(컬렉션 매니저) · isc(Index Search Controller)
├─ config/   cmanager.xml · config.xml
├─ license/  license.xml      ← 상용 라이선스(만료일 확인 필요)
├─ log/      cmanager · isc
└─ pid/      cmanager.pid · isc.pid
```
- 기동 인자: `cmanager -home /app/search/sf-1 -conf ../config/cmanager.xml -pid ... -log ...`
- `isc -conf config/config.xml -license license/license.xml -log ... -pid ...`
- 누적 CPU: `cmanager` 약 20분 / **`isc` 약 6시간 22분** → 실부하는 `isc`
- ⚠️ **PPID=1 · systemd 미등록** → 사망 시 자동 재기동 없음 (NDSoft SMS 에이전트와 동일 패턴)
- ⚠️ `isc`만 2026-02-25 재기동 — **사유 미확인**

### ❓ 미확인 (조사중)
- [x] ~~SF-1 ↔ ES 관계~~ → **해소**: 매장검색엔진 고도화 (와이즈넛 -> 엘라스틱서치) 전환. 현행=ES, SF-1=잔존
- [x] ~~SF-1 라이선스 만료일~~ → **2026-04-05 만료**
- [ ] **SF-1 정리** — 참조 앱 없음 확인 후 프로세스 정지·경로 보존/삭제 결정
- [ ] SF-1 컬렉션 구성·서비스 포트 (정리 전 참조 여부 판단용)
- [ ] ES 인덱스 실사용 여부(`_cat/indices`), 보안(x-pack) 설정
- [ ] 홈페이지 검색(`page/search` · 백엔드 `/api/search` 스텁)이 어느 엔진에 연결되는지
      → [happypoint-web2](../projects/happypoint-web2/INDEX.md) · [ha-web-api](../projects/ha-web-api/INDEX.md)
- [ ] 색인 배치 위치(이 서버 cron인지 배치서버인지)

## ELB/리버스 프록시 라우팅 (리뉴얼: 프론트+백엔드 한 도메인 분기)
**3도메인**: 개발 `dev.happypointcard.com` · 스테이징 `stg.happypointcard.com` · 운영 `www.happypointcard.com`.
앞단(ELB)이 **경로 prefix로 분기**(3도메인 공통):
```
https://<도메인>/
  ├─ /api/*  → 신규 Spring 백엔드 (ha-web-api)
  └─ 그 외    → Next.js 프론트 서버 (ha-web-fo)
```
- **서버 토폴로지**: 운영 = **프론트 2대 + 백엔드 Spring 2대**. 개발/스테이징 = **1대에 프론트·백엔드 공존(포트 분리)**.
  - 개발 예: `/api/*`=9022 톰캣 / 그 외=3000 Next(pm2).
- **마이그레이션 원칙(중요)**: `/page`로 시작·`.spc`로 끝나는 **모든 레거시 Spring MVC 화면 = 전부 Next로 이관**. URL 동일, **맨 뒤 `.spc`만 제거**한 경로가 신규 라우트(예: `/page/brand/member/join-auth.spc`→`/page/brand/member/join-auth`). `.spc` 화면은 ELB상 프론트가 받으므로, 미들웨어에서 진입 URL은 `.spc` 제거 후 **같은 오리진 rewrite**로 Next에서 연다(레거시 백엔드 절대경로 리다이렉트 금지).
- same-origin이라 로그인 세션쿠키(JSESSIONID)·`/api` 호출 그대로 동작(CORS 불필요).
- Next `next.config`의 `/api` 프록시 rewrite는 **로컬 개발(ELB 없음)용 폴백**. 배포 환경에선 ELB가 `/api/*`를 백엔드로 보냄.

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
