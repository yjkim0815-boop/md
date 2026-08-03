---
문서유형: INDEX
프로젝트: spc_spring_batch
작성일: 2026-07-26
최종수정: 2026-08-03
작성자: dominic
상태: 진행중(형상 정합 확인 필요)
요약: 삼성SDS **Anyframe Batch** 기반 배치 — **배치서버 `ip-10-0-70-71`의 `/app/batch` 가동 소스로 확정**(2026-08-03). 기상청 예보·미세먼지 수집 잡. ⚠️ 로컬 저장소가 운영 대비 stale(커밋 2개, 2019년 이후 정지)
---

# 📇 spc_spring_batch 문서 인덱스

> 📛 폴더/슬러그 = 저장소명 `spc_spring_batch` (로컬 폴더 동일). ⚠️ Bitbucket 아닌 **AWS CodeCommit**.
> ⚠️ **이름과 달리 Spring Batch 가 아니라 삼성SDS `Anyframe Batch` 다.**

## 프로젝트 개요
- **저장소명(=KB 슬러그)**: `spc_spring_batch`
- **로컬 폴더**: `spc_spring_batch` (KB 기준 `../../../spc_spring_batch`) — 동일 ✅
- **remote/브랜치**: `git-codecommit.ap-northeast-2.amazonaws.com/v1/repos/spc_spring_batch` / `dev`
- **프레임워크**: **삼성SDS Anyframe Batch 1.0.0** (`anyframe-batch-runtime-1.0.0.jar` · `anyframe-batch-agent-interfaces-1.0.0.jar`)
- **런처**: `com.sds.anyframe.batch.launcher.BatchJobLauncher <잡CFG.xml> BASE_DT= BASE_TM= RUN_MODE= …`
- **빌드**: Maven/Gradle 파일 **없음** — `lib/` 에 jar 직접 동봉 + `bin/` 컴파일 산출물 커밋 방식

## 🔗 배포처 확정 (2026-08-03)
**배치서버 `ip-10-0-70-71` 의 `/app/batch` 가 이 저장소의 가동본이다.**

근거 — 서버 `ps -ef` 의 classpath와 이 저장소 `lib/` 목록이 일치:
`anyframe-batch-runtime-1.0.0` · `anyframe-batch-agent-interfaces-1.0.0` · `AutomailAPI.jar` · `hessian-3.2.0` · `jasypt-1.7` · `hsqldb` · `json-simple-1.1.1` · `commons-*` · `dom4j-1.6.1` · `cglib-nodep-2.2` · `apache-log4j-extras-1.2.17` · `sapjco3`(`libsapjco3.so`)

> 📌 서버에서 실제로 도는 잡 예: `hp/batch/wthr/gov/GovForecastGrib_CFG.xml` (기상청 예보, 분 단위 기동)
> 관련: [shared/server-env.md](../../shared/server-env.md) 배치서버 항목 · [sms-agent-replacement](../task/sms-agent-replacement/INDEX.md)(같은 서버의 SMS 에이전트)

## 🔴 형상 정합 문제 (최우선 확인)

| 항목 | 값 |
|---|---|
| 커밋 수 | **2개** |
| 최근 커밋 | **2019-01-30** · Boheon Kim · `프로젝트 등록` |

- 🔴 **저장소가 2019년 "프로젝트 등록" 이후 사실상 정지 상태**인데, 운영 서버에서는 지금도 가동 중이다.
- 🔴 **서버 가동 잡 `hp/batch/wthr/gov/GovForecastGrib_CFG.xml` 의 `gov` 패키지가 로컬 저장소에 없다.** 로컬에는 `hp/batch/wthr/kma` 만 존재.
  → **운영 반영분이 형상관리에 들어오지 않았을 가능성**이 높다. 서버 소스와 저장소 대조가 필요하다.

## 구성 — 잡 구조
Anyframe 규약상 **잡 1개 = `<Job>.java` + `<Job>_CFG.xml`(잡 정의) + `<Job>_SQL.xml`(쿼리)** 3종 세트.

| 패키지 | 잡 | 기능 |
|---|---|---|
| `hp.batch.wthr.kma` | `KmaForecastGrib` · `KmaForecastTime` · `KmaForecastSpace` · `KmaForecastDel` | **기상청(KMA) 예보 수집·정리** |
| `hp.batch.dust.air` | `AirForecastBrgh` · `AirForecastNext` | **미세먼지 예보 수집** |
| `hp.batch.noml.frot` | `HsFrontView` | 프론트 노출 데이터 |
| `hp.batch.common` | `ComnUtil` · `ConstantsUtil` · `DateUtil` · `StringsUtil` · `EncodeUtil` · `SocketHandller`(원문 오타) · `EasySSLProtocolSocketFactory` · `EasyX509TrustManager` | 공통 유틸 (SSL 우회 포함) |
| `hp.batch.dvo` | `ParamDvo` | 파라미터 DVO |

### 설정 (`config/`)
```
config/
├─ batch.properties · log4j.xml
├─ common/   batchjobrun.sh · batchjobkill.sh · common.env
└─ spring/batch/  batch-application-context.xml · data-source-context.xml
                  jdbc.properties · transform-3.0.xsl
```
> ⚠️ `jdbc.properties` 에 DB 접속정보 존재 가능 → **값은 KB에 기재 금지**. `jasypt-1.7` 동봉이라 암호화 적용 여부 확인 가치 있음.

### ⚠️ 눈에 띄는 점
- `EasySSLProtocolSocketFactory` · `EasyX509TrustManager` = **TLS 인증서 검증 우회** 유틸. 외부 API(기상청 등) 연동용으로 보이나 **보안 검토 대상**
- **기상청 수집이 [spc_batch](../spc_batch/INDEX.md) 와 중복**된다 — 양쪽 역할 분담 확인 필요
- `libsapjco3.so` (SAP Java Connector) 동봉 → **SAP 연동 잡 존재 가능성**

## ❓ 미확인
- [ ] 🔴 **서버 `/app/batch` 소스 ↔ 저장소 대조** — `wthr/gov` 등 미커밋분 파악
- [ ] 운영 반영 절차(배포 방식) — 형상관리 없이 서버 직접 수정인지
- [ ] `spc_batch` 와의 기상청 수집 역할 분담
- [ ] SAP 연동 잡 실재 여부
- [ ] `jdbc.properties` 크리덴셜 암호화 여부

## 참고 (공통 문서)
- [공유 KB README](../../README.md)
- [shared/server-env.md](../../shared/server-env.md) — 배치서버 `ip-10-0-70-71`
- [shared/security-review.md](../../shared/security-review.md) — TLS 우회·크리덴셜 검토 기준
- [spc_batch](../spc_batch/INDEX.md) — 이름은 비슷하나 **성격이 전혀 다른** 저장소
