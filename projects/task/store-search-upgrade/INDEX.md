---
문서유형: INDEX
프로젝트: store-search-upgrade (과업/엄브렐러)
이슈키: --
작성일: 2026-08-03
최종수정: 2026-08-03
작성자: dominic
상태: 완료(잔여 정리 있음)
요약: 매장검색엔진 고도화 (와이즈넛 -> 엘라스틱서치, 2026-03) — SF-1 라이선스 2026-04-05 만료에 따라 Elasticsearch 8.19로 전환. 만료 7일 전(03-29) ES 기동 완료. SF-1 프로세스는 2026-08 현재까지 잔존
---

# 📇 매장검색엔진 고도화 (와이즈넛 -> 엘라스틱서치)

> ⚠️ **이 슬러그는 저장소가 아니라 "과업 묶음"이다.** 검색 서버 인프라·엔진 전환에 걸친 작업으로, 코드 저장소 단위가 아니라 **과업 단위**로 등록한다. ([homepage-ai-renewal](../../homepage-ai-renewal/INDEX.md) · [sms-agent-replacement](../../task/sms-agent-replacement/INDEX.md) 선례)
>
> 🔕 **자동 주입 제외.** 필요 시 `매장검색엔진 컨텍스트 연결해` 로 수동 연결(12시간).

## 프로젝트 정의
- **명칭**: 매장검색엔진 고도화 (와이즈넛 -> 엘라스틱서치)
- **수행 시기**: **2026년 3월** (ES 기동 완료 2026-03-29)
- **목표**: 매장검색 엔진을 **와이즈넛 SF-1 → Elasticsearch** 로 전환
- **직접 트리거**: **와이즈넛 SF-1 라이선스 2026-04-05 만료**
- **상태**: **완료** — 단, SF-1 프로세스 잔존 등 정리 과제 있음(아래 §4)

## 1. 배경 — 라이선스 만료가 기한이었다

기존 매장검색은 **와이즈넛 SF-1**(상용 검색엔진)이 담당했다. **2026-04-05 라이선스 만료**가 확정돼 있어, 그 이전에 대체 엔진으로 전환하지 못하면 **매장검색 기능이 중단**되는 상황이었다.

- 상용 라이선스 갱신이 아닌 **오픈소스(Elasticsearch) 전환**을 선택
- 만료일이 곧 **하드 데드라인** → 일정 여유가 없는 과업이었다

## 2. 타임라인

| 일자 | 사건 | 근거 |
|---|---|---|
| 2026-02-25 | SF-1 `isc` 프로세스 재기동 | 프로세스 기동시각 (과업 착수 시점과 근접) |
| 2026-03 | **매장검색엔진 고도화 진행** | 사용자 확인 |
| **2026-03-29** | **Elasticsearch 8.19.12 기동** | 프로세스 기동시각 |
| **2026-04-05** | **와이즈넛 SF-1 라이선스 만료** | 사용자 확인 |
| 2026-08-03 | 사후 실사 — SF-1 프로세스 **여전히 상주 중** 확인 | `ps -ef` |

> ✅ **만료 7일 전에 ES 기동 완료.** 데드라인은 지켰다.

## 3. 전환 내용

### Before — 와이즈넛 SF-1
| 항목 | 내용 |
|---|---|
| 설치 경로 | `/app/search/sf-1` |
| 프로세스 | `cmanager`(컬렉션 매니저, 2025년~) · `isc`(Index Search Controller, 2026-02-25~) |
| 구성 | `bin/` · `config/{cmanager.xml, config.xml}` · `license/license.xml` · `log/` · `pid/` |
| 실행 계정 | `ec2-user` |
| 성격 | **상용 라이선스** — 만료 시 사용 불가 |

### After — Elasticsearch
| 항목 | 내용 |
|---|---|
| 버전 | **8.19.12** |
| 설치 | **RPM** (`-Des.distribution.type=rpm`) |
| 경로 | `/usr/share/elasticsearch` · 설정 `/etc/elasticsearch` · 로그 `/var/log/elasticsearch` |
| 실행 계정 | `elasticsearch` (전용 계정) |
| JVM | **`-Xms2g -Xmx2g`** 고정, **G1GC**, `MaxDirectMemorySize=1g` |
| 런타임 | **번들 JDK** (`-Des.java.type=bundled JDK`) — 시스템 JDK 비의존 |
| 부가 | `x-pack-ml` 컨트롤러 동작 중 |
| 성격 | **오픈소스** — 라이선스 만료 리스크 해소 ✅ |

### 서버
**`ip-10-0-75-31`** (검색 전용 서버). ⚠️ 배치서버 `ip-10-0-70-71` 과 **다른 서버**다.
상세: [shared/server-env.md](../../../shared/server-env.md)

## 4. 🟠 잔여 과제 (2026-08-03 실사 기준)

| # | 항목 | 내용 |
|---|---|---|
| 1 | 🟠 **SF-1 프로세스 잔존** | 라이선스 만료 **4개월 경과(2026-08-03)** 후에도 `cmanager`·`isc` 가 계속 상주 중. 메모리·CPU 점유(누적 CPU: cmanager 20분 / isc 6시간 22분) |
| 2 | 🟡 **정리 범위 미확정** | 프로세스 정지 · `/app/search/sf-1` 보존/삭제 · 색인 데이터 백업 여부 |
| 3 | 🟡 **ES 운영 체계 미확인** | systemd 등록 여부, 스냅샷/백업, 모니터링, x-pack 보안 설정 |
| 4 | 🟡 **색인 배치 이관 확인** | 매장 데이터 색인 잡이 ES 기준으로 전환됐는지 (구 SF-1 색인 잡 잔존 여부) |
| 5 | 🟡 **애플리케이션 연동 확인** | 홈페이지 검색이 ES를 바라보는지 |

> ⚠️ **SF-1을 먼저 죽이지 말 것.** 라이선스가 만료됐어도 프로세스가 살아있다는 건 ① 단순 미정리 ② 일부 기능이 아직 참조 중 둘 중 하나다. **어떤 애플리케이션도 SF-1 포트를 호출하지 않는지 확인한 뒤** 정지한다.

## 5. 애플리케이션 연동 (확인 필요)

홈페이지 리뉴얼 쪽에 검색 관련 흔적이 있어 **연결 관계를 확인해야 한다**.
- 프론트 [happypoint-web2](../../happypoint-web2/INDEX.md) — `page/search` (실사용 검색 결과 페이지, `header-search`·`mobile-header`·`site-nav`·`SearchAction` 참조)
- 백엔드 [ha-web-api](../../ha-web-api/INDEX.md) — `GET /api/search` (**2026-W31 시점 빈 모델 스텁**)
- 레거시 [ha-web-api WORKLOG](../../ha-web-api/WORKLOG-20260721-nextjs-api-migration-map.md) — `GET /page/store/search.spc` → `GET /api/store/search?brandCode&metro&city` (**매장검색**)

> ❓ **핵심 질문**: 이 과업의 "매장검색"이 위 `store/search` 경로와 같은 것인지, 별도 시스템인지. 같다면 **홈페이지 리뉴얼과 직접 연결된 과업**이 된다.

## 6. 🔻 SF-1 정지 절차 (2026-08-03 착수)

> 🔴 **원복 커맨드 (정지 전 반드시 보존).** systemd 미등록이라 **한번 죽으면 자동 재기동되지 않는다.** 아래는 2026-08-03 실사 시점의 실제 기동 커맨드 원문이다.
> ```bash
> /app/search/sf-1/bin/cmanager -home /app/search/sf-1 -conf ../config/cmanager.xml -pid /app/search/sf-1/pid/cmanager.pid -log /app/search/sf-1/log/cmanager
> ```
> ```bash
> /app/search/sf-1/bin/isc -conf /app/search/sf-1/config/config.xml -license /app/search/sf-1/license/license.xml -log /app/search/sf-1/log/isc -pid /app/search/sf-1/pid/isc.pid
> ```
> ⚠️ `cmanager` 는 `-conf ../config/...` **상대경로** → 반드시 `/app/search/sf-1/bin` 에서 실행.
> ⚠️ 라이선스가 이미 만료(2026-04-05)라 **재기동해도 정상 동작하지 않을 수 있다.** 원복은 "프로세스 복구"까지만 보장된다.

### STEP 1 — 참조자 확인 (필수, 생략 금지)
아직 SF-1을 호출하는 애플리케이션이 없는지 확인한다. **ESTABLISHED 세션이 하나라도 있으면 정지 보류.**
- 리스닝 포트 확인 → 해당 포트의 연결 상대 확인 → 로그의 최근 질의 유입 여부 확인

### STEP 2 — 백업
설정·라이선스·기동 커맨드를 보존한다(색인 데이터는 용량 확인 후 판단).

### STEP 3 — 정지
1. `bin/` 에 벤더 제공 stop 스크립트가 있으면 **그것을 우선 사용**
2. 없으면 **SIGTERM(`kill`)** — `kill -9` 는 최후수단
3. 정지 순서: **`isc` 먼저 → `cmanager` 나중** (검색 처리 주체를 먼저 내림)

### STEP 4 — 재기동 방지
`cron`/`@reboot`/기타 감시 스크립트에 SF-1 기동이 걸려 있지 않은지 확인.

### STEP 5 — 관찰 (권장 1~2주)
**경로(`/app/search/sf-1`)는 즉시 삭제하지 않는다.** 프로세스만 내리고 관찰 후 삭제 판단.

### 진행 기록
| 일자 | 단계 | 결과 |
|---|---|---|
| 2026-08-03 | 정지 절차 수립 · 원복 커맨드 보존 | ✅ |
| | STEP 1 참조자 확인 | ⏳ |
| | STEP 3 정지 | ⏳ |

## 7. 확인 명령어 (잔여 조사)

```bash
sudo ss -tnlp | grep -E 'isc|cmanager'
```
```bash
curl -s localhost:9200/_cat/indices?v
```
```bash
systemctl is-enabled elasticsearch; systemctl status elasticsearch --no-pager | head -5
```
```bash
ls -alt /app/search/sf-1/log/ | head; du -sh /app/search/sf-1
```

## 참고 (공통 문서)
- [공유 KB README](../../../README.md)
- [shared/server-env.md](../../../shared/server-env.md) — 검색 서버 `ip-10-0-75-31` 항목
- 관련 과업: [sms-agent-replacement](../../task/sms-agent-replacement/INDEX.md) — **동일 패턴**(레거시 상용 솔루션 교체)
