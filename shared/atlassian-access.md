---
문서유형: SHARED
프로젝트: 공통
이슈키: --
작성일: 2026-08-01
최종수정: 2026-08-04
작성자: dominic
상태: 진행중
요약: Bitbucket·Jira·Confluence 접근 수단 공통 정리 — SSH 키(git) + API 토큰 2종(통합/Bitbucket)의 저장 위치·조회 방법·엔드포인트·기능 범위·함정 (macOS/Windows 양쪽). 2026-08-02 App password 폐기(HTTPS git 410) → SSH 필수 확정, Windows PC 키 등록, MCP 미연결 정정. **2026-08-04 호출 제한 강화 — 3초/회 · 1일 통합 50회(SSH+API 4종 공유 쿼터) · 소진 시 중단·보고·당일 +20 승인제** + 사용 내역 표 신설
---

# 🔐 Atlassian 접근 수단 (Bitbucket · Jira · Confluence)

> ⚠️ **이 문서에는 토큰·비밀번호 값을 절대 적지 않는다.** 저장 위치와 꺼내는 방법만 기록한다. 실제 값은 macOS 키체인 / Windows DPAPI 에만 존재한다.
>
> 🛑 **[강제 규칙] API 호출은 `3초에 1회` · `1일 통합 50회` 를 넘기지 않는다.** (2026-08-05 30회→50회 상향)
> **Bitbucket SSH · Bitbucket API · Confluence API · Jira API 4종이 하나의 쿼터를 공유**한다(MCP 도구 호출 포함). SSH fetch 를 20회 썼다면 Jira·Confluence 는 남은 30회만 쓸 수 있다.
> **50회 소진 시 작업을 중단하고 사용자에게 보고**한다. 사용자가 "20회 추가"를 승인하면 **당일에 한해** 연장되며 다음 날 50회로 초기화된다.
> 상세·사용 내역: [§3-1 호출 제한](#3-1--호출-제한-강제-규칙--2026-08-04-강화) · [§3-2 사용 내역](#3-2--호출-사용-내역-매일-갱신)
>
> 상위: [../README.md](../README.md)

## 1. 계정·사이트 정보

| 항목 | 값 |
|---|---|
| Atlassian 계정 | `dominic.kim@spc.co.kr` |
| Bitbucket 워크스페이스 | `sectanine` (저장소 **135개**) |
| Atlassian 사이트 | `https://secta9ine.atlassian.net` |
| **cloudId** | `89ca5ed0-2672-496f-a295-17520dc2d02f` |

## 2. 인증 수단 3종

| 수단 | 용도 | 만료 |
|---|---|---|
| **SSH 키** | git clone / fetch / push | 없음 |
| **통합 API 토큰** | Jira + Confluence REST API | 있음 |
| **Bitbucket API 토큰** | Bitbucket REST API | 있음 |

> API 토큰은 **앱당 1개**만 만들 수 있다(발급 화면에서 앱을 단수 선택). 그래서 Jira+Confluence 통합 1개, Bitbucket 1개로 나뉜다. 스코프는 한 토큰당 **50개 제한**이 있다.

### 2-1. SSH 키 (git 전용)

> 🔴 **git HTTPS 는 더 이상 쓸 수 없다 (2026-08-02 확인).** Bitbucket 이 **App password 를 폐기**해서, 저장된 App password 로 HTTPS fetch 시 **410 Gone** 이 떨어진다.
> ```
> remote: CHANGE-3222 - Functionality has been deprecated
> remote: App passwords are deprecated and must be replaced with API tokens.
> fatal: ... The requested URL returned error: 410
> ```
> → **git 접근은 SSH 가 정본 경로**다. (HTTPS 를 굳이 쓰려면 자격증명을 **API 토큰 + username=이메일** 로 교체해야 한다.)

**등록 위치**: `https://bitbucket.org/account/settings/ssh-keys/` (Bitbucket > Personal settings > SSH keys)

**등록된 키 (계정 기준, 2026-08-02 API 조회)**

| Label | 등록일 | 비고 |
|---|---|---|
| `A2485.Dominic` | 2026-08-01 | |
| `git.dominic` | 2026-07-18 | |
| (Windows `JOON-DEV`) | 2026-08-02 | 지문 `SHA256:kH2wWFAbZfdNGlas/NzYoor6T3jlIuGF+jbNKOEZb74` |

**PC별 키 (경로는 공통 `~/.ssh/id_ed25519_bitbucket`)**

| PC | 지문 | 상태 |
|---|---|---|
| macOS | `SHA256:G6E25gsjNiMkrg+9rzEkSZeGx4jiJOGXzxEWJuNB4XA` | 기존 |
| Windows `JOON-DEV` | `SHA256:kH2wWFAbZfdNGlas/NzYoor6T3jlIuGF+jbNKOEZb74` | **2026-08-02 생성·등록·인증 확인**(패스프레이즈 없음) |

`~/.ssh/config` 에 `bitbucket.org` 호스트를 등록한다. macOS 는 키체인 연동(`UseKeychain yes`), **Windows 는 `UseKeychain` 을 넣으면 안 된다**(OpenSSH for Windows 미지원 옵션). 공통으로 `IdentitiesOnly yes` 를 둔다.
**사내망에서 22번 포트가 막히면** `HostName altssh.bitbucket.org` / `Port 443` 으로 전환한다(config 에 주석으로 준비되어 있음).

> ⚠️ **Windows 에서 config 작성 시 BOM 금지.** PowerShell `Set-Content -Encoding utf8` 은 BOM 을 넣어 `Bad configuration option: \357\273\277#` 로 **config 전체가 거부**된다. `[System.IO.File]::WriteAllText($p,$c,(New-Object System.Text.UTF8Encoding($false)))` 로 작성한다.

remote 는 SSH 형식을 쓴다: `git@bitbucket.org:sectanine/<repo>.git`

> 🚦 Bitbucket SSH Git 요청(`fetch`/`pull`/`push` 포함)은 저장소 간·연속 요청 사이에 **최소 1초** 간격을 둔다. 병렬 요청은 금지한다.

> ⚠️ **이 PC(Windows `JOON-DEV`)의 remote 12개는 아직 HTTPS** (`https://dominic.kim@bitbucket.org/...`) → **fetch 불가 상태.** SSH 전환이 선행 과제다. 동기화 절차는 [git-sync-routine.md](./git-sync-routine.md) 참조.

### 2-2. 토큰 저장 위치 (OS 병기)

| | macOS (키체인) | Windows (DPAPI 파일) |
|---|---|---|
| 통합 키 | service `atlassian-api` | `%USERPROFILE%\.atlassian\api.cred` |
| Bitbucket 키 | service `atlassian-bitbucket` | `%USERPROFILE%\.atlassian\bitbucket.cred` |
| 공통 account | `dominic.kim@spc.co.kr` | 동일 |

Bitbucket 토큰은 `git credential` 에도 등록해 둔다(호스트 `bitbucket.org`, username = **이메일**).

**꺼내는 방법**

```bash
# macOS
security find-generic-password -a dominic.kim@spc.co.kr -s atlassian-api -w
```

```powershell
# Windows
[System.Net.NetworkCredential]::new('',(Get-Content "$env:USERPROFILE\.atlassian\api.cred"|ConvertTo-SecureString)).Password
```

## 3. API 엔드포인트

**스코프 토큰은 사이트 도메인이 아니라 `api.atlassian.com/ex/` 를 쓴다.** `secta9ine.atlassian.net` 으로 직접 호출하면 인증이 통과하지 않는다.

| 대상 | Base URL |
|---|---|
| Jira | `https://api.atlassian.com/ex/jira/{cloudId}/rest/api/3/` |
| Jira Agile(보드·스프린트) | `https://api.atlassian.com/ex/jira/{cloudId}/rest/agile/1.0/` |
| Confluence | `https://api.atlassian.com/ex/confluence/{cloudId}/wiki/api/v2/` |
| Bitbucket | `https://api.bitbucket.org/2.0/` |

인증은 **Basic (이메일:토큰)**. 사용자명은 Bitbucket 아이디(`dominic.kim`)가 아니라 **이메일**이어야 한다.

## 3-1. 🚦 호출 제한 (강제 규칙 · 2026-08-04 강화)

> 🛑 **이 규칙은 강하게 적용한다. 예외 없이 지킨다.**
> 사용자가 "빨리 해줘"라고 해도, 작업이 중간에 끊겨도, **한도를 넘겨서 호출하지 않는다.** 한도에 걸리면 **중단하고 사용자에게 보고**한다.

### 적용 대상 (4종 · 하나의 통합 쿼터)

| # | 대상 | 예시 |
|---|---|---|
| 1 | **Bitbucket SSH** | `git fetch` · `git pull` · `git clone` · `git ls-remote` (저장소 1개당 1회) |
| 2 | **Bitbucket API** | `api.bitbucket.org/2.0/*` |
| 3 | **Confluence API** | REST 직접 호출 · **Atlassian MCP `*Confluence*` 도구** |
| 4 | **Jira API** | REST 직접 호출 · **Atlassian MCP `*Jira*` 도구** |

> ⚠️ **MCP 도구 호출도 1회로 센다.** `searchJiraIssuesUsingJql`·`getConfluencePage` 등은 내부적으로 REST 를 부르므로 직접 호출과 동일하다.

### 규칙 3가지

| # | 규칙 | 값 |
|---|---|---|
| **R1** | **최소 호출 간격** | **3초에 1회** — 연속 호출 사이 3초 이상 대기. 종류가 달라도 동일(Bitbucket 직후 Jira 도 3초) |
| **R2** | **1일 통합 상한** | **50회** — 위 4종을 **합산**. 저장소별·서비스별 개별 한도가 아니다 |
| **R3** | **소진 시 처리** | 50회 도달 → **즉시 중단 + 사용자에게 보고**. 임의로 더 호출하지 않는다 |

> 📌 **기본 한도 30회 → 50회 상향 (2026-08-05 사용자 확정).**
> 저장소 12개 전체 fetch(12회)와 워크로그 주차 수집(주당 6~10회)을 같은 날 돌리면 30회로는 부족하다는 것이 실측으로 확인됐다. 2026-08-05 하루에 워크로그 수집만으로 **48회**를 썼다.

**R2 는 공유 풀이다.** 예를 들어 Bitbucket SSH 로 fetch/pull 을 **20회** 썼다면, 그날 **Jira + Confluence 는 남은 30회**만 쓸 수 있다.

```
[통합 50회]
 ├ Bitbucket SSH   20회 사용  ──┐
 └ 잔여 30회 ────────────────── ├─ Jira · Confluence · Bitbucket API 가 나눠 씀
                                ┘
```

### 소진 시 절차

1. 50회에 도달하면 **진행 중인 작업을 멈춘다.**
2. 사용자에게 아래 형식으로 보고한다.
   ```
   🛑 오늘 API 호출 한도 50회를 모두 소진했습니다.
      내역: Bitbucket SSH 20 · Jira 8 · Confluence 2
      남은 작업: <무엇을 하려던 중이었는지>
      추가 승인을 주시면 이어서 진행합니다.
   ```
3. 사용자가 **"20회 추가해줘"** 라고 하면 → **당일에 한해 +20회**. 한도는 70회가 된다.
4. **추가분은 이월되지 않는다.** 다음 날 0시에 다시 **50회로 초기화**된다.

5. 추가는 **사용자가 명시적으로 말할 때만** 적용한다. 에이전트가 먼저 "추가할까요?"로 유도하지 않는다 — 보고만 하고 기다린다.
6. **잔여는 암산하지 말고 기록으로 검산한다.**

> ⚠️ **오보고 사례 (2026-08-05).** 워크로그 수집 회차 하나(6회)를 빠뜨리고 "42/50 · 잔여 8" 로 보고했으나 실제는 **48/50 · 잔여 2** 였다. 사용자가 되물어 발견했다. `manifest.json` 의 `runs[].calls.total` 처럼 **실제 기록을 합산**해 보고한다.

### 한도를 아끼는 법 (호출 전에 먼저 검토)

1. **페이지 크기를 키운다** — `maxResults=100` · `pagelen=100`. 1회로 100건이면 3회 나눠 받을 이유가 없다.
2. **필요한 필드만** — `fields=` 로 응답을 줄여 재조회를 막는다.
3. **저장한 결과를 재사용한다** — MCP 응답이 크면 파일로 저장되므로, **같은 데이터를 다시 부르지 말고 그 파일을 Python/jq 로 다시 판다.**
4. **페이지네이션은 최후 수단** — `next` 루프는 한도를 순식간에 태운다. 돌리기 전에 "정말 전건이 필요한가"를 먼저 묻는다.
5. **병렬 호출 금지** — R1(3초 간격)과 양립할 수 없다. 무조건 순차.
6. **429 를 받으면 즉시 중단** — 지수 백오프(3s → 6s → 12s). `Retry-After` 가 있으면 그 값을 따른다. **재시도도 1회로 센다.**

### 구현 예시

```bash
# bash/zsh — 3초 간격
for u in "${urls[@]}"; do
  curl -s -u "$E:$T" "$u"
  sleep 3            # ← 필수 (1초 아님)
done
```

```powershell
# PowerShell
foreach ($u in $urls) {
  Invoke-RestMethod -Uri $u -Headers $h
  Start-Sleep -Seconds 3           # ← 필수
}
```

### 배경

- 워크스페이스 저장소가 **135개**라 전수 fetch 는 그 자체로 한도를 훨씬 넘는다. **전수 조회는 기본적으로 금지**이며, 필요한 저장소만 지정해 돈다.
- Atlassian 은 계정·IP 단위로 레이트리밋을 걸며, 초과 시 **일시 차단**된다. 차단되면 **git 작업까지 막혀** 개발이 멈춘다.
- 조회는 대부분 급하지 않다. **속도보다 안정성**을 택한다. — [work-tendency](../personal/work-tendency.md) 무장애 지향과 동일한 판단.

## 3-2. 📊 호출 사용 내역 (매일 갱신)

> 🔄 **호출할 때마다 즉시 이 표를 갱신한다.** 날짜가 바뀌면 새 행을 만들고 이전 행은 아래 이력으로 내린다.

### 오늘 (2026-08-07)

| 대상 | 사용 | 비고 |
|---|---:|---|
| Bitbucket SSH | 0 | |
| Bitbucket API | 0 | |
| Jira API | **11** | 팀 워크로그 W26 `2026-06-22` — PowerShell 예외 1회(서버 도달 불명 포함) + REST 일자별 search 6회 + 오버플로 4회 |
| Confluence API | 0 | |
| **합계** | **11 / 50** | 잔여 **39회** |

### 이전 오늘 (2026-08-05)

| 대상 | 사용 | 비고 |
|---|---:|---|
| Bitbucket SSH | 0 | |
| Bitbucket API | 0 | |
| Jira API | **5** | 팀 워크로그 9회차 `2026-05-25` — REST search 3(3분할) + 오버플로 2 |
| Confluence API | 0 | |
| **합계** | **5 / 30** | 잔여 **25회** |

### 이력 — 2026-08-04

| 대상 | 사용 | 비고 |
|---|---:|---|
| Bitbucket SSH | 0 | |
| Bitbucket API | 0 | |
| Jira API | **35** | 팀 워크로그 1~8회차(타임아웃 2회 포함) + 로스터 조회 1 |
| Confluence API | **3** | 이벤트 템플릿 설명회 초안 검토 (읽기 3회) |
| **합계** | **44 / 50** | 잔여 **6회** · 🟢 **사용자 승인 +20 (2026-08-04 당일 한정)** |

**내역 (2026-08-04)**

| # | 대상 | 호출 | 용도 |
|---:|---|---|---|
| 1~3 | Jira MCP | `searchJiraIssuesUsingJql` ×3 | 팀 워크로그 1회차 — 주차 3개 (`2026-08-03`·`2026-07-27`·`2026-07-20`) |
| 4~10 | Jira REST | `/issue/{key}/worklog` ×7 | 오버플로 이슈 전량 (425건) |
| 11~12 | Confluence MCP | `getConfluencePage` ×2 | 설명회 초안 검토 + 수정 후 재검토 |
| 13 | Jira MCP | `searchJiraIssuesUsingJql` ×1 | 팀 워크로그 2회차 — `2026-07-13` |
| 14~16 | Jira REST | `/issue/{key}/worklog` ×3 | 신규·변경 오버플로만 (9개 중 6개 캐시 적중) |
| 17 | Confluence MCP | `getConfluencePage` ×1 | 설명회 초안 3차 검토 (변경 없음 확인) |
| 18 | Jira MCP | `searchJiraIssuesUsingJql` ×1 | 팀 워크로그 3회차 — `2026-07-06` (**오버플로 0회**) |
| 19 | Jira MCP | `searchJiraIssuesUsingJql` ×1 | 팀 워크로그 4회차 — `2026-06-29` |
| 20~23 | Jira REST | `/issue/{key}/worklog` ×4 | 분기 경계 신규 버킷 3개 (`WORK-12211` 은 1,138건이라 **페이지네이션 2회**) |

> ✅ **로스터 9명(accountId·이메일)은 캐시에서 추출해 호출 0회.** `lookupJiraAccountId` 9회를 절약했다. → [personal/team-worklog/roster.json](../personal/team-worklog/roster.json)

> ℹ️ **규칙 제정(2026-08-04) 이전 호출은 소급하지 않는다.** 이 규칙이 생기기 전 이벤트 템플릿 자산 분석(Confluence 4건 + Jira 81건 + 워크로그 조회)에서 상당량을 이미 호출했으나, 그 시점에는 한도가 없었으므로 카운트에서 제외한다. **제정 시점부터 0 으로 시작한다.**

### 이력

| 날짜 | 합계 | 추가 승인 | 비고 |
|---|---:|---:|---|
| _(없음)_ | | | |

## 4. 기능 범위 (2026-08-01 실측)

### 통합 키 — Jira

| 기능 | 결과 |
|---|---|
| 내 계정 · 프로젝트 목록 · 필드 목록 | ✅ 200 |
| 이슈 검색(JQL) · 이슈 생성메타 · 사용자 검색 | ✅ 200 |
| **첨부파일** | ✅ 200 |
| **보드 / 스프린트 (Agile API)** | ✅ 200 |
| 워크플로 관리(관리자 API) | ❌ **403** |

### 통합 키 — Confluence

| 기능 | 결과 |
|---|---|
| 스페이스 · 페이지 · 검색(CQL) · 댓글 · 사용자 | ✅ 200 |
| **첨부파일** | ✅ 200 |

### Bitbucket 키

| 기능 | 결과 |
|---|---|
| 저장소 목록 · 워크스페이스 · 브랜치 | ✅ 200 |
| **PR 목록 · 파이프라인** | ✅ 200 |

## 5. 함정 (실제로 막혔던 것)

1. **사용자명은 이메일.** Bitbucket 아이디로 쓰면 `API token must be used with an atlassian registered email` 401.
2. **스코프 없는 토큰은 무용지물.** 발급 시 *"Create API token"* 이 아니라 ***"Create API token with scopes"*** 를 눌러야 한다. 전자로 만들면 `API Token provided has no Bitbucket scopes` 401.
3. **토큰은 스코프 밖에서 동작하지 않는다.** Bitbucket 스코프 토큰으로 Jira 를 호출하면 `Unauthorized; scope does not match` 401.
4. **무제한 JQL 금지.** `order by created DESC` 처럼 조건이 없으면 400 (`무제한 JQL 쿼리는 여기에서 허용되지 않습니다`). `created >= -30d`·`project = WORK` 등 **검색 제한을 반드시 붙인다.** 권한 문제가 아니다.
5. **구 검색 엔드포인트 폐기.** `/rest/api/3/search` 는 **410 Gone**. `/rest/api/3/search/jql` 을 쓴다. 오래된 예제 코드가 여기서 막힌다.
6. **`accessible-resources` 로 스코프 조회 불가.** 그 엔드포인트는 OAuth 3LO 전용이라 API 토큰으로는 401. 스코프 확인은 **실제 엔드포인트를 호출해 보는 방식**으로 한다.

## 6. MCP 와의 관계

> ⚠️ **정정(2026-08-02, Windows `JOON-DEV`)**: 이 PC의 Claude Code 세션에는 **Atlassian MCP 가 로드되어 있지 않다**(MCP 레지스트리 검색 결과 0건). 따라서 이 환경에서는 **Jira·Confluence 도 API 토큰 경로만 사용 가능**하며, 아래 "MCP 권장" 표가 적용되지 않는다. MCP 연결 여부는 **PC·세션마다 확인**할 것.

Claude Code 에는 Atlassian MCP 가 OAuth 로 연결되어 있어 **Jira·Confluence 는 토큰 없이도** 조회·생성·수정이 된다. 단 MCP 로는 **첨부파일·스프린트·대량처리·삭제·Bitbucket 이 불가**하고, 백그라운드(cron) 실행에서는 인증이 없을 수 있다.

| 용도 | 권장 수단 |
|---|---|
| 대화 중 이슈·페이지 조회/작성 | **MCP** |
| 첨부파일·스프린트·대량처리·자동화 스크립트 | **API 토큰** |
| Bitbucket 전반 | **API 토큰** (MCP 미지원) |

## 7. 저장소 클론 시 주의

저장소명과 로컬 폴더명이 다르다. 반드시 [../README.md](../README.md) 의 매핑표를 따라 폴더명을 지정해 클론한다. 그러지 않으면 KB 문서의 `../` 상대경로가 전부 깨진다.

```bash
git clone git@bitbucket.org:sectanine/thehappy_ios.git ha-ios
```

## 8. 미결 사항

- [ ] 커밋 이메일이 개인 메일(`yjkim0815@naver.com`)로 남아 있다 → `~/IdeaProjects/` 하위에서만 회사 메일을 쓰도록 `includeIf` 조건부 설정 필요
- [ ] 워크플로 관리 API(403)가 필요해지면 스코프 재발급 검토
- [ ] 토큰 만료일 확인·갱신 주기 미정







