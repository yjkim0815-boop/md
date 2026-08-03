---
문서유형: INDEX
프로젝트: spc_batch
작성일: 2026-07-26
최종수정: 2026-08-03
작성자: dominic
상태: 진행중
요약: SPC 배치 (AWS CodeCommit) — Maven 단일 jar(`hpc_batch`). 배너종료·배포·해피오더동기화·로또·메일발송(Slack/Telegram 알림)·기상청 날씨/미세먼지·매장좌표변환(KATEC→위경도) 스케줄러 모음. 2026-08-03 소스 실사로 실체 확정
---

# 📇 spc_batch 문서 인덱스

> 📛 폴더/슬러그 = 저장소명 `spc_batch` (로컬 폴더 동일). ⚠️ Bitbucket 아닌 **AWS CodeCommit**.

## 프로젝트 개요
- **저장소명(=KB 슬러그)**: `spc_batch`
- **로컬 폴더**: `spc_batch` (KB 기준 `../../../spc_batch`) — 동일 ✅
- **remote/브랜치**: `git-codecommit.ap-northeast-2.amazonaws.com/v1/repos/spc_batch` / `dev`
- **성격**: **독립 실행형 스케줄러 묶음**. Spring Batch 아님 — 각 클래스가 `main` 을 갖는 단발성 잡 형태
- **빌드**: Maven · `groupId=spc` / `artifactId=hpc_batch` / `1.0-SNAPSHOT` / **packaging=jar**
- **실행**: `java -jar xelloss.jar` (readme.txt 기준) ※ 산출물명이 artifactId와 불일치 — **확인 필요**
- **주요 의존**: `javax.mail 1.6.2` · `ojdbc6 12.1.0.2` · `json-simple`

## 활동 이력 (2026-08-03 실사)
| 항목 | 값 |
|---|---|
| 커밋 수 | **319** |
| 최근 커밋 | **2024-08-14** · Dominic.Kim · `[sql] 이벤트 meta 기준쿼리 변경` |
| 소스 규모 | **Java 21개 파일** |

> 📌 **[spc_spring_batch](../spc_spring_batch/INDEX.md) 와 달리 실제로 유지보수된 저장소**다(319 vs 2 커밋). 다만 최근 커밋이 2024-08 로 약 2년 정체.

## 구성 — 기능별 스케줄러

| 패키지 | 클래스 | 기능 |
|---|---|---|
| `com.scp.hpc.banner` | `BannerCloseScheduler` | 배너 종료 처리 |
| `com.scp.hpc.deploy` | `DeployScheduler` | 배포 관련 스케줄 |
| `com.scp.hpc.happyorder` | `HappyOrderSyncRealScheduler` | **해피오더 실시간 동기화** |
| `com.scp.hpc.lotto` | `LottoScheduler` | 로또(이벤트성) |
| `com.scp.hpc.sendMail` | `HappyPointSendMail` · `HappyPointParser` · `HappyPointQuery` · `HappyPointRecevier`(원문 오타) · `HappyPointS3File` · **`SendSlack`** · **`SendTelegram`** | 메일 발송 + **Slack·Telegram 알림** + S3 파일 |
| `com.scp.hpc.weather` | `KmaWeatherInfoApplication` / `~New` / `~NewV2` / `~NewV3` · `KmaWeatherInfo10Application` · `KmaTempBatch` · `KmaDustApplication` | **기상청 날씨·미세먼지 수집** |
| `com.spc.hpc.batch.store.katecTolatlng` | `GeoTransKatecToLatLng` | **매장 좌표 변환 (KATEC → 위경도)** |
| `geotrans` | `GeoPoint` · `GeoTrans` | 좌표계 변환 유틸 |

### ⚠️ 눈에 띄는 점
- **`KmaWeatherInfoApplication` 계열이 5개 버전 공존**(원본/New/NewV2/NewV3/10Application) → 구버전 미정리 의심. 실제 가동본 확인 필요
- **패키지 prefix가 `com.scp` 와 `com.spc` 로 혼재** (`scp` 는 오타로 추정) — 리팩터링 시 주의
- **날씨 수집이 [spc_spring_batch](../spc_spring_batch/INDEX.md) 와 중복**된다(양쪽 다 기상청). **역할 분담 확인 필요**
- `com.spc.hpc.batch.store.*` 는 **매장(store) 좌표** 처리 → **[store-search-upgrade](../task/store-search-upgrade/INDEX.md)(매장검색엔진 고도화)와 연관 가능성**

## ❓ 미확인
- [ ] 배포 위치 — 배치서버 `ip-10-0-70-71` 인지, 별도 서버인지 (`/app/batch` 는 spc_spring_batch 소스로 확인됨)
- [ ] 실행 산출물명 `xelloss.jar` 의 유래·현행 여부
- [ ] 5개 버전 `KmaWeatherInfo*` 중 실가동본
- [ ] `GeoTransKatecToLatLng` 가 매장검색 색인 파이프라인에 관여하는지

## 참고 (공통 문서)
- [공유 KB README](../../README.md)
- [shared/server-env.md](../../shared/server-env.md) — 배치서버 `ip-10-0-70-71`
- [spc_spring_batch](../spc_spring_batch/INDEX.md) — 이름은 비슷하나 **성격이 전혀 다른** 저장소
