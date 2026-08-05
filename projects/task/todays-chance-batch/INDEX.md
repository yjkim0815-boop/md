---
문서유형: INDEX
프로젝트: todays-chance-batch (과업/엄브렐러)
이슈키: --
작성일: 2026-08-05
최종수정: 2026-08-05
작성자: dominic
상태: 진행중(분석)
요약: 오늘의찬스 배치 고도화 — 배치 수집/발송 체계를 재정비하는 과업. 2026-08-05 기상청·미세먼지 수집 배치 전면 장애(외부 API 빈 응답 63,068건, 날씨 적재 0건)를 첫 분석 건으로 착수. 연계 코드 프로젝트는 ha-push-batch(사용자 지정)
---

# 📇 오늘의찬스 배치 고도화 (todays-chance-batch)

> ⚠️ **이 슬러그는 저장소가 아니라 "과업 묶음"이다.** 여러 배치 저장소·서버에 걸쳐 있어 **과업 단위**로 등록한다. (폴더명=저장소명 규칙의 예외 — [sms-agent-replacement](../sms-agent-replacement/INDEX.md) 선례)

## 과업 정의

- **목표**: 오늘의찬스 관련 **배치 수집·적재 체계 고도화**. 외부 API 의존 구간의 **관측 가능성·재시도·한도 관리**를 정비한다.
- **범위**: 이 과업은 **기상청·미세먼지 수집 배치를 포함**한다(2026-08-05 사용자 확정).
- **상태**: 진행중(분석)

### 🔗 연계 프로젝트

| 구분 | 프로젝트 | 비고 |
|---|---|---|
| **연계 코드 프로젝트** | [ha-push-batch](../../ha-push-batch/INDEX.md) | **2026-08-05 사용자 지정.** Java17 / Spring Boot 3.5 / Spring Batch |
| **장애 로그 실제 출처** | [spc_spring_batch](../../spc_spring_batch/INDEX.md) | ⚠️ 아래 주의 참조 |

> 🔴 **주의 — 연계 프로젝트와 장애 출처가 다르다.**
> 2026-08-05 분석한 로그는 **`spc_spring_batch`**(삼성SDS Anyframe Batch · `ip-10-0-70-71:/app/batch`) 산출물이다. 판별 근거: 런처 `com.sds.anyframe.batch.launcher`, 잡 CFG `hp/batch/wthr/gov/GovForecastGrib_CFG.xml`, 경고 `Can not find the Anyframe job appender`.
> **`ha-push-batch` 는 Spring Boot 3.5 기반 출석체크 리마인드 푸시 배치로 기상청 잡을 갖고 있지 않다.**
> 사용자 지정에 따라 과업의 연계 프로젝트는 `ha-push-batch` 로 두되, **현행 장애 대상 소스는 `spc_spring_batch` 임을 혼동하지 않는다.** 고도화가 Anyframe → Spring Boot 이행을 포함하는지는 **미확정**.

## 🚨 지금 막고 있는 것 (2026-08-05 · 원인 확정)

> ✅ **원인 확정: `VilageFcstInfoService_2.0` 활용신청 미등록/만료.**
> 2026-08-05 로컬 PC에서 6개 API를 직접 호출해 확정했다. **서비스키 자체는 유효하다.**

| # | API | 응답 | 판정 |
|---|---|---|---|
| 1 | `VilageFcstInfoService_2.0/getUltraSrtNcst` (초단기실황) | `SERVICE_KEY_IS_NOT_REGISTERED_ERROR` (30) | 🔴 |
| 2 | `VilageFcstInfoService_2.0/getUltraSrtFcst` (초단기예보) | `SERVICE_KEY_IS_NOT_REGISTERED_ERROR` (30) | 🔴 |
| 3 | `VilageFcstInfoService_2.0/getVilageFcst` (동네예보) | `SERVICE_KEY_IS_NOT_REGISTERED_ERROR` (30) | 🔴 |
| 4 | `WthrWrnInfoService/getPwnCd` (기상특보) | `NO_DATA` (03) | ✅ 정상 |
| 5 | `ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty` | 정상 | ✅ |
| 6 | `ArpltnInforInqireSvc/getMinuDustFrcstDspth` | 정상 | ✅ |

- 4번 `NO_DATA(03)` 는 **인증 통과 + 특보 없음** 이라는 정상 업무 응답이다. → 키 유효 입증.
- data.go.kr 은 **활용신청 단위로 권한을 관리**한다. 같은 계정 키라도 신청이 없는 서비스는 30번으로 거부된다.
- 🔴 **초기 가설(일일 트래픽 한도 초과)은 오판이었다.** 한도 초과면 `LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR`(22)가 온다. 호출 63,068건은 원인이 아니라 **실패 반복의 결과**다.

### 📋 사용자 확인 필요 — data.go.kr 마이페이지 → 활용신청 현황

> 대상: **`기상청_단기예보 조회서비스`**. 상태만 보지 말고 아래 5개를 확인한다.

| # | 확인 항목 | 문제 신호 |
|---|---|---|
| 1 | **신청 상태** | `반려` · `신청중`(미승인) |
| 2 | **활용기간 만료일** | 오늘 이전 — **가장 유력** |
| 3 | **계정 구분** | `개발계정`이면 통상 **2년 후 자동 만료** |
| 4 | 🔴 **신청 서비스가 `_2.0` 버전인지** | 목록에 아예 없거나 **구버전만 신청**돼 있을 수 있음 |
| 5 | **일일 트래픽 / 잔여** | 이번 건 원인은 아니나 함께 확인 |

> ⚠️ **4번이 특히 의심된다.** 기상청은 구버전 `VilageFcstInfoService` → `VilageFcstInfoService_2.0` 으로 이관했고 **둘은 별개 활용신청**이다. 소스에도 이관 흔적이 남아 있다 — `ConstantsUtil.KMA_URL` 이 구 엔드포인트(`newsky2.kma.go.kr/…SecndSrtpdFrcstInfoService2`)를 가리키고, `KmaForecastGrib/Time/Space` 3개 클래스가 통째로 죽은 코드다.

**결과별 조치**

| 확인 결과 | 조치 | 소요 |
|---|---|---|
| 만료됨 | 연장 신청 | 즉시~1일 |
| 목록에 없음 | 신규 활용신청 (`단기예보 조회서비스` **2.0**) | 자동승인 즉시 / 심의 1~2일 |
| 승인됐는데 거부 | 키 재발급 또는 포털 문의 | — |
| 개발계정 | 운영계정 전환 신청 | 심의 필요 |

> 📌 **계정 소유자도 확인할 것.** 기상특보·미세먼지는 살아 있어 계정 자체는 정상이다. 다만 **퇴사자 명의 계정이면 만료 알림 메일이 아무에게도 가지 않는다.** 이번에 아무도 만료를 몰랐던 이유일 수 있다.

📄 상세: [WORKLOG-20260805-batch-outage.md](./WORKLOG-20260805-batch-outage.md)

## 하루 로그가 설명하는 것 — 문제는 **두 개**였다

| | 문제 | 영향 잡 | 상태 |
|---|---|---|---|
| **A** | 네트워크/응답 지연 (**타임아웃**) | GRIB · TIME · SPACE · **WARN** | 09시경 회복 |
| **B** | **`VilageFcstInfoService_2.0` 활용신청 미등록** | GRIB · TIME · SPACE | 🔴 지속 |

**A의 근거** — 연속 실패 간격이 소스 타임아웃과 정확히 일치했다.

| 잡 | 00~08시 실측 간격 | 소스 타임아웃 |
|---|---:|---:|
| `GovForecastGrib` | 7.0초 | `requestHttpNob(…, 7000, 80)` |
| `GovForecastWarn` | 8.0초 | `requestHttpNob(…, 8000, 80)` |

09시부터 간격이 **0초**로 바뀐 것은 타임아웃이 사라지고 **즉시 인증 거부 응답**이 오기 시작했다는 뜻이다.
→ 그래서 **`GovForecastWarn` 만 14:06에 정상화**됐다(A만 겪음). GRIB·TIME·SPACE는 B가 남아 15:02에도 전량 실패.

## 🔴 왜 로그로 원인을 알 수 없었나 — `requestHttpNob`

```java
// SocketHandller.requestHttpNob — 기상청 4개 잡이 사용
catch (IOException e) { retVal = ""; }        // 예외를 삼킨다 (Nob = No Bubble)
if (responseCode == 200) { retVal = 본문 }    // else 없음 → 비200 응답 폐기

// 호출부 (GovForecastWarn.java L80 등)
if (rpsVal == null || "".equals(rpsVal.trim())) LOGGER.error("["+txId+"]NO-RPS="+rpsVal);
```

**타임아웃(A)과 인증거부(B)가 로그에 똑같이 `NO-RPS=` 로 찍힌다.** 브라우저로 한 번에 보이는 오류를 배치는 하루 **63,068번 버렸다.**

대조 — 미세먼지 잡은 `requestHttp`(예외를 던짐)를 써서 로그에 `SocketTimeoutException` 이 그대로 남았다. **API 차이가 아니라 코드 선택의 차이다.**

## 도출된 개선 항목

| # | 항목 | 근거 | 우선순위 |
|---|---|---|---|
| 1 | **활용신청 복구** | 원인 확정 — 위 §확인 필요 참조 | 🔴 즉시 |
| 2 | **`requestHttpNob` 폐기** — 예외 전파 + 비200 상태코드·본문 로깅 | 원인 추적 불가의 직접 원인 | 🔴 최우선 |
| 3 | **연속 실패 시 중단** (Circuit Breaker) | 전량 실패 중에도 10분 간격 재실행, 63,068건 낭비 | 🟡 |
| 4 | **적재 0건 알림** | 대상 828건 → 반영 0건이 26회 반복돼도 무알림 | 🟡 |
| 5 | HTTP → HTTPS 전환 | 전 잡이 `http://` 포트 80 평문 전송 | 🟡 |
| 6 | `EasySSLProtocolSocketFactory` 제거 | 인증서 검증 무력화 유틸. 현재 죽은 코드지만 HTTPS 전환 시 위험 | 🟡 |
| 7 | **서비스키 하드코딩 제거** | 98자 운영키가 `ConstantsUtil` 8개 상수 + 각 잡에 인라인. **DEV=PROD 동일** | 🟡 |
| 8 | `KmaForecast*` 죽은 코드 3종 정리 | 셸이 `Gov*` 를 호출. `kma_wthr_del.sh` 만 `KmaForecastDel` 사용 | ⚪ |
| 9 | Anyframe appender 경고 정리 | `anyframeAppender`·`stepAppender` 미탐지 157회 | ⚪ 무해 |

## 참고 — 서비스키 실측 (2026-08-05)

- **98자**, `16utFQyosA…lQsg%3D%3D`. **URL 인코딩된 상태**(`%2F`·`%2B`·`%3D`)로 저장돼 있고 그대로 전송해야 한다.
- ⚠️ `.class` 문자열 덤프에서 앞에 `b` 가 붙어 보이는 것은 **CONSTANT_Utf8 길이 바이트 `0x62`(=98)** 이다. 키의 일부가 아니다.
- `ConstantsUtil` 의 `KMA/GOV/AIR/AIRv2` × `DEV/PROD` **8개 상수 + 6개 잡 인라인 = 20곳이 SHA256 동일**. data.go.kr 은 계정당 인증키 1개이므로 기상청·에어코리아가 같은 키를 쓰는 것 자체는 정상이나, **DEV/PROD 미분리는 결함**이다.

## 이력

| 날짜 | 내용 |
|---|---|
| 2026-08-05 | 과업 개설. 로그 분석(63,068건 실패·적재 0건) → 소스 확보 → **CFR 0.152 로 25개 클래스 디컴파일** → 로컬 직접 호출로 **원인 확정(활용신청 미등록)**. 개선 항목 9건 도출. 사용자 확인 대기 중 |
