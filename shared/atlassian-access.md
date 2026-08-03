---
문서유형: SHARED
프로젝트: 공통
이슈키: --
작성일: 2026-08-01
최종수정: 2026-08-02
작성자: dominic
상태: 진행중
요약: Bitbucket·Jira·Confluence 접근 수단 공통 정리 — SSH 키(git) + API 토큰 2종(통합/Bitbucket)의 저장 위치·조회 방법·엔드포인트·기능 범위·함정 (macOS/Windows 양쪽). 2026-08-02 App password 폐기(HTTPS git 410) → SSH 필수 확정, Windows PC 키 등록, MCP 미연결 정정
---

# 🔐 Atlassian 접근 수단 (Bitbucket · Jira · Confluence)

> ⚠️ **이 문서에는 토큰·비밀번호 값을 절대 적지 않는다.** 저장 위치와 꺼내는 방법만 기록한다. 실제 값은 macOS 키체인 / Windows DPAPI 에만 존재한다.
>
> 🚦 **[상시 규칙] API 호출은 초당 1회를 넘기지 않는다.** Bitbucket·Jira·Confluence 전부 해당. Bitbucket SSH Git 요청도 동일하게 최소 1초 간격을 둔다. 상세는 [§3-1 호출 속도 제한](#3-1-호출-속도-제한-상시-규칙).
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

## 3-1. 호출 속도 제한 (상시 규칙)

> 🚦 **Bitbucket · Jira · Confluence API 는 초당 1회를 초과해 호출하지 않는다.**
> 즉 **연속 호출 사이에 최소 1초 간격**을 둔다. 사람이 수동으로 부르든, 에이전트가 스크립트로 부르든 동일하게 적용한다.

### 원칙

1. **최소 간격 1초.** 루프 안에서 호출할 때는 매 반복마다 대기를 넣는다.
2. **페이지네이션이 가장 위험하다.** `next` 를 따라가는 반복문은 순식간에 수십 회를 호출한다. 반드시 대기를 넣는다.
3. **호출 횟수 자체를 줄인다.** 페이지 크기를 키우면(`pagelen=100` / `maxResults=100`) 같은 데이터를 더 적은 호출로 가져온다. 대기보다 이쪽이 우선이다.
4. **필요한 필드만 요청한다.** `fields=` · `?fields=` 로 응답을 줄이면 재조회가 줄어든다.
5. **429(Too Many Requests) 를 받으면 즉시 중단**하고 지수 백오프(1s → 2s → 4s)로 재시도한다. `Retry-After` 헤더가 있으면 그 값을 따른다.
6. **병렬 호출 금지.** 여러 저장소·이슈를 동시에 훑지 않는다. 순차 처리한다.

### 구현 예시

```bash
# bash/zsh — 페이지네이션 루프에 1초 대기
URL="https://api.bitbucket.org/2.0/repositories/sectanine?pagelen=100"
while [ -n "$URL" ]; do
  RESP=$(curl -s -u "$E:$T" "$URL")
  # ... 처리 ...
  URL=$(echo "$RESP" | python3 -c "import json,sys;print(json.load(sys.stdin).get('next',''))")
  sleep 1            # ← 필수
done
```

```powershell
# PowerShell
foreach ($u in $urls) {
  Invoke-RestMethod -Uri $u -Headers $h
  Start-Sleep -Seconds 1           # ← 필수
}
```

### 배경

- 워크스페이스 저장소가 **135개**라 전수 조회 시 페이지네이션이 여러 번 돈다. 무제한으로 돌리면 순간 호출량이 급증한다.
- Atlassian 은 계정·IP 단위로 레이트리밋을 걸며, 초과 시 **일시 차단**될 수 있다. 차단되면 git 작업까지 영향을 받을 수 있으므로 예방이 우선이다.
- 조회는 대부분 급하지 않다. **속도보다 안정성**을 택한다.

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
