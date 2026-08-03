---
문서유형: WORKLOG
프로젝트: sms-agent-replacement
이슈키: --
작성일: 2026-08-03
최종수정: 2026-08-03
작성자: dominic
상태: 진행중
요약: 2026-W32(08-03~08-09) — 배치서버 SMS 발송 에이전트 실사. 벤더=(주)엔디소프트 NDMG 특정, 설치경로 /app/ndsoft 및 설정파일 5종 확인
---

# 🛠️ WORKLOG — 2026-W32 (2026-08-03 ~ 2026-08-09)

## 배경 / 목적
배치서버에 SMS 발송 에이전트가 상주 중이나 **KB에 기록이 전무**했다(`shared/server-env.md`·`spc_batch`·`spc_spring_batch` 어디에도 없음). 교체 검토에 앞서 **현행 구성을 실사**하고 프로젝트를 신설한다.

## 진행 내용

### 1. 벤더 식별 — "엠디소프트"가 아니라 **엔디소프트**
초기 질의는 "SMS 발송 에이전트 회사 중 **엠디**소프트가 있냐"였으나 검색 결과 무관한 업체만 나왔다.
- 실제 검색된 **(주)엠디소프트**(`md-soft.co.kr`)는 **병의원 전자차트(EMR)** 업체 → **무관**
- 서버 프로세스 실사에서 `-Dprocess.id=ndsoft-agnet-sms` 확인 → **엔**디소프트로 확정
- 벤더 연혁의 **"NDMG(NDSOFT Message Gateway)를 ㈜SPC Networks에 구축·운영"** 기록이 jar 접미사 `-spc` 와 일치 → 확정 근거

### 2. 프로세스 실사
`ps -ef` 로 상주 프로세스 확인. PID 110132, PPID=1, 실행 계정 `ec2-user`, **2025년 기동** 이후 무중단, 누적 CPU 2일 13시간.
JVM 옵션: `-Xms64m -Xmx64m -XX:+PrintGCDetails -Dfile.encoding=KSC5601`, 메인 클래스 `ndsoft.message.agent.base.executor.ConsoleExecutor`.

### 3. 설치경로 특정
`-cp` 가 상대경로(`..//lib/...`)라 `/proc/<PID>/cwd` 로 역추적 → cwd `/app/ndsoft/bin`, **설치 루트 `/app/ndsoft`**.
구조는 표준 4단(`bin`/`conf`/`lib`/`logs`).

### 4. 설정파일 확인
`/app/ndsoft/conf` 에 5개 파일 존재: `agent.conf`(메인, 2017-04-05) · `agent.bak`(백업, 2016-12-06) · `jdbc.conf` · `log4j.properties` · `result.properties`.
**`jdbc.conf` 존재 → DB 폴링형 발송 구조가 유력**(배치가 큐 테이블에 적재 → 에이전트가 주기 폴링 → 게이트웨이 전송).

### 5. 프로젝트 신설
`projects/sms-agent-replacement/` 신설 + 루트 README 인덱스 등록 + `shared/server-env.md` 에 배치서버 항목 추가.

## 발생 이슈 & 해결
| 이슈 | 원인 | 해결 |
|------|------|------|
| 벤더 검색 실패 | 사명을 **엠**디소프트로 기억 (실제 **엔**디소프트) | 서버 프로세스의 `process.id`·패키지명(`ndsoft.*`)으로 역추적해 확정 |
| 설치경로 불명 | `-cp` 가 상대경로라 명령행만으로 판단 불가 | `readlink -f /proc/<PID>/cwd` 로 cwd 확인 후 상위 디렉터리 = 설치 루트 |
| KB에 배치서버 기록 없음 | `server-env.md` 가 웹/API 톰캣 위주 | 배치서버(`ip-10-0-70-71`) 항목 신설 |

## 명령/코드 스니펫
```bash
ps -ef | grep -iE 'sms|lms|mms|msg|ppurio|infobank|agent|sender' | grep -v grep
```
```bash
readlink -f /proc/110132/cwd
```
```bash
CWD=$(readlink -f /proc/110132/cwd); ROOT=$(dirname "$CWD"); echo "ROOT = $ROOT"; ls -al "$ROOT"
```
```bash
ls -al /app/ndsoft/conf/
```
> 크리덴셜 마스킹 조회(값은 KB에 기재 금지):
```bash
sed -E 's/((pass|pwd|passwd|secret|key|token)[^=:]*[=:]).*/\1********/I' /app/ndsoft/conf/jdbc.conf
```

## 결과
- ✅ 벤더·제품 확정: **(주)엔디소프트 / NDMG**
- ✅ 설치경로·설정경로·로그경로 확정
- ✅ 리스크 8건 도출 (바이너리 EOL, JDK8/KSC5601, 힙 64MB, 무감시 상주, cwd 의존 기동, 평문 크리덴셜, 로그 미정리, 미상 변경이력)
- ✅ KB 신설: [INDEX](../../INDEX.md) · README 등록 · server-env 배치서버 항목
- ⏳ 발송 방식(폴링 vs 소켓)·큐 테이블·게이트웨이 엔드포인트는 **미확인**

## 다음 할 일 (TODO)
- [ ] `agent.conf`·`jdbc.conf` 마스킹 조회 → **발송 큐 테이블·폴링 주기·게이트웨이 엔드포인트** 확정
- [ ] `diff /app/ndsoft/conf/agent.bak /app/ndsoft/conf/agent.conf` → 2017년 변경분 파악
- [ ] `ss -tnp | grep 110132` → 소켓 연결 유무로 발송 방식 최종 판정
- [ ] `/app/ndsoft/bin/*.sh` 확인 → 기동/재기동 절차 문서화 (장애 대응 필수)
- [ ] 2026-04-10(conf)·2026-04-21(bin) 변경 이력 추적
- [ ] 로그 용량·디스크 여유 점검 (`du -sh /app/ndsoft/logs`, `df -h /app`)
- [ ] 발송 요청 주체 확인 — `/app/batch` 잡인지 타 앱인지
- [ ] 벤더 지원 계약 유효 여부 확인 (042-610-3800)
- [ ] 실사 완료 후 **대체안 검토** 착수 (자체 구현 vs 상용 중계사 전환)

---

## [2026-08-03 추가] 신규 에이전트 자료 입수 → 전수 분석

교체 대상이 **섹타나인(SECTA9INE) Agent v2.0.1 Legacy호환** 으로 확정됐다. 배포본·벤더 매뉴얼(24p)·내부 설치가이드(10슬라이드)를 전수 분석.

### 확정
- **DB 스키마 동일**(`EM_TRAN`/`EM_TRAN_MMS`/`EM_LOG`) → **발송 요청 코드 수정 불필요**
- **Java 8 호환**(class major 52) → 서버 JDK 교체 불필요
- 기동 방식 개선: `runner.sh {start|stop|status}` + `checkVersion.sh`
- Jasypt 내장 → **크리덴셜 암호화 가능성** 확보

### 최우선 리스크 4건
1. 🔴 **결과코드 체계 상이** — `3001`/`3002`/`3004`/`3005` 가 현행과 **의미가 다름**. 현행 `result.properties` 이식 금지
2. 🔴 **`fetch.hour=1`** — 현행 무제한 → 1시간 초과 대기건 자동 실패
3. 🔴 **`TRAN_TYPE=5`(URL) 미조회** — 사용 중이면 영구 적체
4. 🔴 **로그테이블 `TRAN_REFKEY` 20 vs 40** — 이관 시 `ORA-12899`

### 보안
🔴 현행 `jdbc.conf` 의 접속 대상이 **SPC 홈페이지 운영 Oracle RDS(관리자 계정)** 이며 **평문**이다. 개인 PC 백업 폴더에도 그대로 존재. 파일 권한·백업본 정리·Jasypt 암호화·전환 후 비밀번호 교체 검토 필요.

📄 **정본**: [WORKLOG-20260803 섹타나인 Agent 전환 분석](../../WORKLOG-20260803-secta-agent-analysis.md)

### 추가 TODO
- [ ] **전환 일정·사전준비 요구사항 메일 원문 확보** (폴더명에는 있으나 본문 파일 없음)
- [ ] **1차 전환 범위** 확인 — 선례 파악
- [ ] Phase 1 사전 조사 SQL 실행 (TRAN_TYPE 분포·REFKEY 길이·시퀀스명·결과코드 분포)

## 참고 링크
- [프로젝트 INDEX](../../INDEX.md)
- [섹타나인 Agent 전환 분석](../../WORKLOG-20260803-secta-agent-analysis.md)
- [shared/server-env.md](../../../../shared/server-env.md)
- [shared/security-review.md](../../../../shared/security-review.md)
