---
문서유형: WORKLOG
프로젝트: sms-agent-replacement
이슈키: --
작성일: 2026-08-03
최종수정: 2026-08-03
작성자: dominic
상태: 진행중
요약: SMS Agent 전환 실행 런북 — 담당자 진행 절차(체크리스트)·필요 소스코드(조사SQL/설정템플릿/스크립트)·D-day 반영 계획서(타임라인·검증·롤백)
---

# 🚀 SMS Agent 전환 실행 런북

> 배경·리스크 분석은 [WORKLOG-20260803 섹타나인 Agent 전환 분석](./WORKLOG-20260803-secta-agent-analysis.md) 참조. 이 문서는 **실행용**이다.
> 🔴 **크리덴셜은 이 문서에 절대 기재하지 않는다.** 값이 필요한 자리는 `<<...>>` 자리표시자로 둔다.

---

# PART 1. 담당자 진행 절차

## 1-1. 체크리스트 (선행조건 순)

| # | 작업 | 선행조건 | 담당 | 상태 |
|---|---|---|---|:---:|
| **A. 벤더 회신 (즉시 · 지연 중)** |
| A1 | 전환 가능 일정 회신 | — | dominic | ☐ |
| A2 | 서버 네트워크 환경 = **내부망** 회신 | — | dominic | ☐ |
| A3 | 모니터링 계정 가입 (**Agent 직연동** 선택) | — | dominic | ☐ |
| A4 | 가입계정 + 네트워크유형 회신 → **Agent ID/PW 발급 요청**(SMS·MMS) | A3 | dominic | ☐ |
| **B. 외부 리드타임 (병행 착수)** |
| B1 | 현행 **발송번호 목록 확정** | — | dominic | ☐ |
| B2 | 발송번호 **통신사 가입증빙원** 발급 신청 | B1 | dominic+유관 | ☐ |
| B3 | **방화벽 신청** — 배치서버 → `10.0.111.252/.253/.254`, SMS `5200` · MMS `8200` | A2 | dominic | ☐ |
| B4 | **Grant(인증) 포트** 별도 확인 → 방화벽 반영 | — | 벤더 문의 | ☐ |
| B5 | **TABLESPACE 확인** | — | 인프라팀 | ☐ |
| **C. 사전 조사 (오늘 바로 가능)** |
| C1 | `TRAN_TYPE` 분포 → **URL(5) 사용 여부** | — | dominic | ☐ |
| C2 | `TRAN_REFKEY` 최대길이 | — | dominic | ☐ |
| C3 | 발송량 피크·대기 적체 패턴 | — | dominic | ☐ |
| C4 | `TRAN_RSLT` 값 분포 → `code.conf` 커버리지 | — | dominic | ☐ |
| C5 | 시퀀스·로그테이블 **실제 명명규칙** 확인 | — | dominic | ☐ |
| C6 | 현행 ARIA 암호화 실사용 여부 | — | 벤더 문의 | ☐ |
| **D. 설치·설정 (계정 수령 후)** |
| D1 | 배포본 업로드 → `/app/secta-agent` | A4 | dominic | ☐ |
| D2 | `setting.sh` 수정 | D1 | dominic | ☐ |
| D3 | `jdbc.conf` 수정 | D1 | dominic | ☐ |
| D4 | `agent.conf` 수정 | A4·B3 | dominic | ☐ |
| D5 | mapper `TABLESPACE` 6곳 치환 | B5 | dominic | ☐ |
| D6 | `code.conf` 검증(벤더본 유지) | C4 | dominic | ☐ |
| **E. 검증 → 전환** |
| E1 | 기동 검증 (현행 정지 상태) | D1~D6 | dominic | ☐ |
| E2 | Dummy 발송 3종 | E1 | dominic | ☐ |
| E3 | **D-day 전환** | E2 | dominic | ☐ |

## 1-2. 벤더 회신 초안 (A1·A2·A4)

```text
안녕하세요, SPC 모바일개발팀 김영준입니다.
2차 문자 서비스 전환 관련 회신드립니다.

1. 전환 가능 일정 : <<YYYY-MM-DD>> (희망) / <<YYYY-MM-DD>> (예비)
   - 대상 업무 : 해피포인트 배치서버 SMS 발송 에이전트 (현행 NDSoft)
2. 서버 네트워크 환경 : 내부망 (사내 IDC)
3. 모니터링 계정 : <<가입계정>>  (연동방식: Agent 직연동)
4. Agent 네트워크 유형 : 내부
5. Agent 계정 발급 요청 : SMS용 / MMS(LMS 포함)용 각 1건

[문의사항]
① Grant(인증) 서버의 접속 주소·포트를 확인 부탁드립니다.
   - 안내주신 5200(SMS)/8200(MMS)은 발송(Relay) 포트로 이해했습니다.
   - 배포본 conf 기본값은 agent.grant.port=5100 으로 되어 있어 확인이 필요합니다.
② 이중화 권고 방식 — L4 VIP(10.0.111.252) 단일 사용 vs 개별 노드(.253/.254) 멀티 host 중
   권장 구성을 알려주시면 반영하겠습니다.
③ 현행 Agent는 전문 암호화로 ARIA를 내장하고 있습니다. 신규는 AES/LEA 인데,
   기존 연동에서 암호화를 사용 중이었는지 확인 부탁드립니다.
④ 배포본 conf 기본값 중 아래가 매뉴얼 권장범위와 달라 확인 요청드립니다.
   - agent.sms.timeout.hour=5 (매뉴얼 24~100)
   - agent.sms.fetch.count=600 (매뉴얼 기본 200)
   - MMS 이미지 500KB/합계 1500KB (매뉴얼 300/1024)
⑤ mapper(oracle-secta-legacy.xml) 관련
   - fetchMessages 가 TRAN_TYPE 4/6 만 조회합니다. URL 전송(5)은 미지원이 맞는지요.
   - createTranTable 의 TRAN_REFKEY 는 VARCHAR2(40), createLogTable 은 VARCHAR2(20) 로
     길이가 달라 로그 이관 시 ORA-12899 우려가 있습니다. 확인 부탁드립니다.

감사합니다.
```

---

# PART 2. 필요한 소스코드

## 2-1. 사전 조사 SQL (C1~C5)

### C1. `TRAN_TYPE` 분포 — 🔴 URL(5) 사용 여부 판정
```sql
-- 현재 전송 테이블
SELECT TRAN_TYPE, COUNT(*) AS CNT, MIN(TRAN_DATE) AS FIRST_DT, MAX(TRAN_DATE) AS LAST_DT
FROM EM_TRAN
GROUP BY TRAN_TYPE
ORDER BY TRAN_TYPE;
```
```sql
-- 최근 3개월 로그 테이블 (월별 테이블명은 C5 결과로 치환)
SELECT TRAN_TYPE, COUNT(*) AS CNT
FROM EM_LOG_<<YYYYMM>>
GROUP BY TRAN_TYPE
ORDER BY TRAN_TYPE;
```
> **판정**: `TRAN_TYPE=5` 가 **1건이라도 있으면** 전환 후 영구 적체 → 벤더에 mapper 수정 요청 필수.

### C2. `TRAN_REFKEY` 길이 — 🔴 ORA-12899 판정
```sql
SELECT COUNT(*)                          AS TOTAL_CNT,
       COUNT(TRAN_REFKEY)                AS USED_CNT,
       MAX(LENGTH(TRAN_REFKEY))          AS MAX_LEN,
       SUM(CASE WHEN LENGTH(TRAN_REFKEY) > 20 THEN 1 ELSE 0 END) AS OVER_20
FROM EM_TRAN;
```
> **판정**: `OVER_20 > 0` 이면 로그 이관 실패 발생 → DDL 정정 필요.

### C3. 발송량·적체 패턴 — 🔴 `fetch.hour` 산정 근거
```sql
-- 시간대별 발송량 (최근 7일)
SELECT TO_CHAR(TRAN_DATE,'YYYY-MM-DD HH24') AS HH, COUNT(*) AS CNT
FROM EM_TRAN
WHERE TRAN_DATE >= SYSDATE - 7
GROUP BY TO_CHAR(TRAN_DATE,'YYYY-MM-DD HH24')
ORDER BY CNT DESC
FETCH FIRST 20 ROWS ONLY;
```
```sql
-- 현재 대기건(1)·전송중(2) 적체 및 최장 대기시간
SELECT TRAN_STATUS,
       COUNT(*) AS CNT,
       ROUND(MAX(SYSDATE - TRAN_DATE) * 24, 2) AS MAX_WAIT_HOUR
FROM EM_TRAN
WHERE TRAN_STATUS IN ('1','2')
GROUP BY TRAN_STATUS;
```
> **판정**: `MAX_WAIT_HOUR > 1` 이력이 있으면 `agent.sms.fetch.hour=1` 은 **위험** → 4 이상으로 상향.

### C4. `TRAN_RSLT` 분포 — 🔴 `code.conf` 커버리지
```sql
SELECT TRAN_RSLT, COUNT(*) AS CNT,
       ROUND(RATIO_TO_REPORT(COUNT(*)) OVER () * 100, 2) AS PCT
FROM EM_LOG_<<YYYYMM>>
GROUP BY TRAN_RSLT
ORDER BY CNT DESC;
```
> **판정**: 현행에 나타나는 Legacy 1바이트 코드가 신규 `code.conf` 우변에 **모두 존재**하는지 대조. 없으면 `*=d` 로 뭉개진다.

### C5. 스키마 실물 확인 (시퀀스·테이블·TABLESPACE)
```sql
SELECT TABLE_NAME, TABLESPACE_NAME, NUM_ROWS
FROM USER_TABLES
WHERE TABLE_NAME LIKE 'EM\_%' ESCAPE '\'
ORDER BY TABLE_NAME;
```
```sql
SELECT SEQUENCE_NAME, LAST_NUMBER FROM USER_SEQUENCES WHERE SEQUENCE_NAME LIKE 'EM%';
```
```sql
SELECT COLUMN_NAME, DATA_TYPE, DATA_LENGTH, NULLABLE
FROM USER_TAB_COLUMNS
WHERE TABLE_NAME = 'EM_TRAN'
ORDER BY COLUMN_ID;
```
> **확보 항목**: ① mapper 치환용 **TABLESPACE명** ② Dummy INSERT용 **시퀀스명**(`EM_TRAN_PR` vs `EM_TRAN_SEQ` — 매뉴얼 내 표기 불일치) ③ 로그테이블 **실제 명명규칙**(`EM_LOG_YYYYMM` 여부)

## 2-2. 설정 파일 작성 (D2~D6)

### D2. `bin_linux/setting.sh`
```sh
APP_HOME="/app/secta-agent"        # 배포본 기본값 /home/webdev/secta-agent 에서 변경
JAVA_HOME="/usr"                   # `which java` 결과에서 /bin/java 를 뺀 경로
XMS="128M"
XMX="256M"
APP_PROFILE="production"           # 배포본 기본값 development 에서 변경
```
> `JAVA_HOME` 확인:
```bash
which java && readlink -f $(which java)
```

### D3. `conf/jdbc.conf`
```properties
# 현행 /app/ndsoft/conf/jdbc.conf 의 접속 대상과 동일하게 설정 (값은 서버에서 직접 복사)
jdbc.driver=oracle.jdbc.OracleDriver
jdbc.url=jdbc:oracle:thin:@<<HOST>>:1521:<<SID>>
jdbc.username=<<USER>>
jdbc.password=<<PASSWORD>>
mybatis.mapper.location=conf/mapper/oracle-secta-legacy.xml
```
> 🟠 **배포본 기본값은 `net.sf.log4jdbc.sql.jdbcapi.DriverSpy` + `jdbc:log4jdbc:oracle:...`** (SQL 로깅 래퍼)다. **운영에는 성능 부담**이므로 위처럼 순수 드라이버 사용 권장(벤더 확인 후 확정).

### D4. `conf/agent.conf` — 변경 대상 키만
```properties
# ── Grant 인증 (B3/B4 확정 후) ──
agent.grant.url=http://10.0.111.252
agent.grant.port=<<GRANT_PORT>>          # 배포본 5100 / 메일 안내 5200 — 벤더 확인 필요
agent.grant.auth.path=v2.1/auth

# ── 계정 (A4 수령 후) ──
agent.sms.api.id=<<SMS_ID>>
agent.sms.api.pw=<<SMS_PW>>
agent.mms.api.id=<<MMS_ID>>
agent.mms.api.pw=<<MMS_PW>>

# ── 테이블 (현행과 동일) ──
agent.sms.table.name.tran=EM_TRAN
agent.sms.table.name.log=EM_LOG
agent.mms.table.name.tran=EM_TRAN
agent.mms.table.name.log=EM_LOG
agent.table.log.type=2                   # 월별 = 현행 spc.manage.history.table=month 와 동등
agent.table.log.year=4

# ── 주기 (현행 대비) ──
agent.fetch.delay=1                      # 현행 1000ms 와 동등 ✅
agent.complete.delay=10                  # 현행 60초 → 10초. 부하 관찰 대상 🟠
agent.sms.fetch.hour=<<C3 결과로 결정>>    # 배포본 1 / 현행 무제한 / 매뉴얼 기본 4  🔴
agent.sms.fetch.count=<<C3 결과로 결정>>   # 배포본 600 / 매뉴얼 기본 200

# ── MMS 이미지 (현행 경로 승계) ──
agent.contents.path=<<현행 이미지 경로>>

# ── 서비스 ──
agent.use.sms=true
agent.use.lms=true
agent.use.mms=true
agent.use.kko=false
agent.use.kkf=false
agent.use.rcs=false

# ⚠️ 아래 라인은 break.use=false 여도 절대 삭제 금지 (없으면 기동 실패)
agent.break.use=false
agent.break.hours=0,1,2,3,4,5
agent.break.type=0
```

### D5. mapper TABLESPACE 치환 (6곳)
```bash
grep -n 'TABLESPACE' /app/secta-agent/conf/mapper/oracle-secta-legacy.xml
```
```bash
cp /app/secta-agent/conf/mapper/oracle-secta-legacy.xml{,.bak} && sed -i 's/TABLESPACE TS_SMS_WEB/TABLESPACE <<실제TS명>>/g' /app/secta-agent/conf/mapper/oracle-secta-legacy.xml && grep -c 'TABLESPACE <<실제TS명>>' /app/secta-agent/conf/mapper/oracle-secta-legacy.xml
```
> 결과가 **6** 이어야 정상.

## 2-3. 설치 스크립트 (D1)

```bash
sudo mkdir -p /app/secta-agent && sudo chown -R ec2-user:ec2-user /app/secta-agent && cd /app/secta-agent && unzip -o ~/secta-agent-oracle.zip && chmod +x bin_linux/*.sh && ls -al
```

## 2-4. 검증 명령 (E1~E2)

### E1. 기동 검증
```bash
cd /app/secta-agent/bin_linux && ./checkVersion.sh
```
```bash
cd /app/secta-agent/bin_linux && ./runner.sh start && sleep 5 && ./runner.sh status
```
```bash
tail -100 /app/secta-agent/logs/secta-agent.log | grep -iE 'error|fail|exception|connect'
```
> ✅ **정상 기준**: `ERROR`/`FAIL` 없음 + **`Connection` 로그 존재**(중계 서버 연결 성공).

```bash
sudo ss -tnp | grep -E '10\.0\.111\.(252|253|254)'
```
> 방화벽·연결 확인. ESTABLISHED 세션이 보여야 한다.

### E2. Dummy 발송 (⚠️ **현행 정지 상태에서**, 수신번호는 반드시 테스트 번호)

**SMS**
```sql
INSERT INTO EM_TRAN (TRAN_PR, TRAN_PHONE, TRAN_CALLBACK, TRAN_STATUS, TRAN_DATE, TRAN_MSG, TRAN_TYPE)
VALUES (<<시퀀스명>>.NEXTVAL, '<<테스트번호>>', '<<발신번호>>', '1', SYSDATE, '[TEST] SMS 전환 검증', 4);
COMMIT;
```

**LMS**
```sql
INSERT INTO EM_TRAN_MMS (MMS_SEQ, FILE_CNT, MMS_BODY, MMS_SUBJECT)
VALUES (EM_TRAN_MMS_SEQ.NEXTVAL, 0, '[TEST] LMS 본문 전환 검증', 'LMS 테스트');
INSERT INTO EM_TRAN (TRAN_PR, TRAN_PHONE, TRAN_CALLBACK, TRAN_STATUS, TRAN_DATE, TRAN_MSG, TRAN_TYPE, TRAN_ETC4)
VALUES (<<시퀀스명>>.NEXTVAL, '<<테스트번호>>', '<<발신번호>>', '1', SYSDATE, '[TEST] LMS', 6, EM_TRAN_MMS_SEQ.CURRVAL);
COMMIT;
```

**MMS** (이미지 경로는 `agent.contents.path` 기준 실재 파일)
```sql
INSERT INTO EM_TRAN_MMS (MMS_SEQ, FILE_CNT, MMS_BODY, MMS_SUBJECT, FILE_TYPE1, FILE_NAME1, SERVICE_DEP1)
VALUES (EM_TRAN_MMS_SEQ.NEXTVAL, 1, '[TEST] MMS 본문', 'MMS 테스트', 'IMG', '<<이미지 절대경로>>', 'ALL');
INSERT INTO EM_TRAN (TRAN_PR, TRAN_PHONE, TRAN_CALLBACK, TRAN_STATUS, TRAN_DATE, TRAN_MSG, TRAN_TYPE, TRAN_ETC4)
VALUES (<<시퀀스명>>.NEXTVAL, '<<테스트번호>>', '<<발신번호>>', '1', SYSDATE, '[TEST] MMS', 6, EM_TRAN_MMS_SEQ.CURRVAL);
COMMIT;
```

**상태 추적**
```sql
SELECT TRAN_PR, TRAN_TYPE, TRAN_STATUS, TRAN_RSLT, TRAN_NET, TRAN_DATE, TRAN_RSLTDATE
FROM EM_TRAN
WHERE TRAN_MSG LIKE '[TEST]%'
ORDER BY TRAN_PR DESC;
```
```sql
SELECT TRAN_PR, TRAN_STATUS, TRAN_RSLT, TRAN_REPORTDATE
FROM EM_LOG_<<YYYYMM>>
WHERE TRAN_MSG LIKE '[TEST]%'
ORDER BY TRAN_PR DESC;
```
> ✅ **합격 기준**
> ① `TRAN_STATUS` **1 → 3 → 4** 전이 ② 완료건이 `EM_LOG_YYYYMM` 으로 이관 ③ `TRAN_RSLT` 가 **Legacy 1바이트 코드**(`0`=성공)로 저장 ④ **실제 단말 수신 확인**
> ❌ **불합격**: `TRAN_STATUS=5`(DB 처리 실패) 발생 → 즉시 중단, 로그 확보 후 벤더 문의

---

# PART 3. D-day 반영 계획서

## 3-1. 전제 조건 (전부 ☑ 되어야 착수)

| # | 조건 |
|---|---|
| 1 | Agent ID/PW **수령 완료** (SMS·MMS) |
| 2 | 방화벽 **오픈 완료** 및 연결 확인 |
| 3 | 발송번호 **가입증빙원 등록 완료** |
| 4 | 사전 조사 C1~C5 **완료**, 리스크 #1~#4 **판정 완료** |
| 5 | 설정 D2~D6 **작성 완료** |
| 6 | E1·E2 **검증 통과** |
| 7 | **롤백 절차 확인** 및 현행 백업 완료 |

## 3-2. 타임라인

| 시각 | 단계 | 작업 |
|---|---|---|
| **T-1일** | 사전 | 현행 `/app/ndsoft` **전체 백업**, 대기건 추이 확인, 관계자 공지 |
| **T-30분** | 준비 | 발송량 적은 시간대 진입 확인, 모니터링 화면 대기 |
| **T-10분** | 스냅샷 | 전환 직전 대기건 수 기록 |
| **T+0** | **정지** | 현행 에이전트 중지 |
| T+2분 | 확인 | 프로세스 종료 확인, 잔여 대기건 확인 |
| T+5분 | **기동** | 신규 에이전트 시작 |
| T+7분 | 연결 | 로그 `Connection` + 소켓 ESTABLISHED 확인 |
| T+10분 | **실발송 검증** | Dummy 1건 + 실제 트래픽 처리 관찰 |
| T+30분 | 안정 | 상태 전이·결과코드 분포 확인 |
| T+2시간 | 1차 판정 | 정상이면 종료, 이상 시 롤백 |
| **T+1일** | 후속 | `d` 코드 비율·자동실패·DB부하 리뷰 |

## 3-3. 실행 절차

### ① 사전 백업 (T-1일)
```bash
sudo tar czf /home/ec2-user/ndsoft-backup-$(date +%Y%m%d).tar.gz -C /app --exclude='ndsoft/logs/*' ndsoft && sudo chown ec2-user:ec2-user /home/ec2-user/ndsoft-backup-*.tar.gz && ls -lh /home/ec2-user/ndsoft-backup-*.tar.gz
```

### ② 전환 직전 스냅샷 (T-10분)
```sql
SELECT TRAN_STATUS, COUNT(*) AS CNT, MIN(TRAN_DATE) AS OLDEST
FROM EM_TRAN GROUP BY TRAN_STATUS ORDER BY TRAN_STATUS;
```
> `TRAN_STATUS=1,2` 건수를 기록. **2(전송진행)가 많으면 잦아들 때까지 대기.**

### ③ 현행 정지 (T+0)
```bash
cd /app/ndsoft/bin && sh runner-unix.sh stop
```
```bash
ps -ef | grep -- '-Dprocess.id=ndsoft-agnet-sms' | grep -v grep || echo "현행 정지 완료"
```
> ⚠️ **`kill -9` 금지.** 스크립트는 SIGTERM 을 보낸다. 안 죽으면 30초 대기 후 재시도.

### ④ 신규 기동 (T+5분)
```bash
cd /app/secta-agent/bin_linux && ./runner.sh start && sleep 5 && ./runner.sh status
```

### ⑤ 연결 확인 (T+7분)
```bash
tail -50 /app/secta-agent/logs/secta-agent.log && echo "=== 소켓 ===" && sudo ss -tnp | grep -E '10\.0\.111\.(252|253|254)'
```

### ⑥ 처리 관찰 (T+10분~)
```sql
SELECT TRAN_STATUS, COUNT(*) AS CNT FROM EM_TRAN GROUP BY TRAN_STATUS ORDER BY TRAN_STATUS;
```
```sql
SELECT TRAN_RSLT, COUNT(*) AS CNT FROM EM_LOG_<<YYYYMM>>
WHERE TRAN_REPORTDATE >= SYSDATE - 1/24 GROUP BY TRAN_RSLT ORDER BY CNT DESC;
```
> 🔴 **주시 지표**: ① `TRAN_STATUS=1` 이 **줄어드는지**(안 줄면 fetch 실패) ② `TRAN_STATUS=5` **발생 여부** ③ `TRAN_RSLT='d'` **비율 급증 여부**(코드 매핑 누락 신호)

## 3-4. 🔴 롤백

### 판단 기준 (하나라도 해당 시 즉시 롤백)
| # | 조건 |
|---|---|
| 1 | 기동 후 5분 내 **중계서버 연결 실패** |
| 2 | `TRAN_STATUS=1` 이 **줄지 않음** (fetch 미동작) |
| 3 | `TRAN_STATUS=5`(DB 처리 실패) **발생** |
| 4 | 실제 **단말 미수신** |
| 5 | `TRAN_RSLT='d'` 비율이 전환 전 대비 **비정상 급증** |
| 6 | 대량 **자동 실패** 발생 (`fetch.hour` 초과 추정) |

### 롤백 절차
```bash
cd /app/secta-agent/bin_linux && ./runner.sh stop && sleep 3 && ./runner.sh status
```
```bash
cd /app/ndsoft/bin && sh runner-unix.sh start && sleep 3 && ps -ef | grep -- '-Dprocess.id=ndsoft-agnet-sms' | grep -v grep
```
> ⚠️ **`/app/ndsoft` 는 절대 삭제하지 않는다.** 전환 후 최소 **2주 관찰** 뒤 정리 판단.
> ⚠️ 롤백 시 신규가 이미 `EM_LOG_YYYYMM` 으로 이관한 건은 되돌아오지 않는다 → **중복 발송 여부 확인** 필요.

## 3-5. 전환 후 체크 (T+1일)

| # | 항목 | 방법 |
|---|---|---|
| 1 | `d`(기타) 코드 비율 | 전환 전후 `TRAN_RSLT` 분포 비교 |
| 2 | 자동 실패 발생 | `fetch.hour` 초과로 실패 처리된 건 추적 |
| 3 | DB 부하 | `complete.delay` 10초의 이관 부하 측정 |
| 4 | 로그 증가율 | `du -sh /app/secta-agent/logs` |
| 5 | 프로세스 생존 | `./runner.sh status` (systemd 미등록 상태) |

## 3-6. 잔여 개선 과제 (전환 완료 후)
- [ ] **systemd 등록** — 현행·신규 모두 미등록(무감시). 사망 시 자동 재기동 없음
- [ ] **로그 보관 기간 정책**(logback) 설정
- [ ] **Jasypt 크리덴셜 암호화** 적용
- [ ] **전문 암호화 level 상향** 검토 (수신번호·본문)
- [ ] 구 `/app/ndsoft` 정리 (2주 관찰 후)
- [ ] DB 계정 **비밀번호 교체** 검토

---

## 참고 링크
- [프로젝트 INDEX](./INDEX.md)
- [섹타나인 Agent 전환 분석 (정본)](./WORKLOG-20260803-secta-agent-analysis.md)
- [WORKLOG-2026-W32](./worklog/weekly/WORKLOG-2026-W32.md)
- [shared/server-env.md](../../../shared/server-env.md)
