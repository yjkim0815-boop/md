---
문서유형: SHARED
프로젝트: 공통
이슈키: --
작성일: 2026-08-01
최종수정: 2026-08-01
작성자: dominic
상태: 진행중
요약: Bitbucket·Jira·Confluence 접근 수단 공통 정리 — SSH 키(git) + API 토큰 2종(통합/Bitbucket)의 저장 위치·조회 방법·엔드포인트·기능 범위·함정 (macOS/Windows 양쪽)
---

# 🔐 Atlassian 접근 수단 (Bitbucket · Jira · Confluence)

> ⚠️ **이 문서에는 토큰·비밀번호 값을 절대 적지 않는다.** 저장 위치와 꺼내는 방법만 기록한다. 실제 값은 macOS 키체인 / Windows DPAPI 에만 존재한다.
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

```
경로   ~/.ssh/id_ed25519_bitbucket
지문   SHA256:G6E25gsjNiMkrg+9rzEkSZeGx4jiJOGXzxEWJuNB4XA
등록   Bitbucket > Personal settings > SSH keys
```

`~/.ssh/config` 에 `bitbucket.org` 호스트를 등록해 키체인 연동(`UseKeychain yes`)한다. **사내망에서 22번 포트가 막히면** `HostName altssh.bitbucket.org` / `Port 443` 으로 전환한다(config 에 주석으로 준비되어 있음).

remote 는 SSH 형식을 쓴다: `git@bitbucket.org:sectanine/<repo>.git`

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
