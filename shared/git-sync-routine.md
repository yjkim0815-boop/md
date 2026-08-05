---
문서유형: SHARED
프로젝트: 공통
이슈키: --
작성일: 2026-08-02
최종수정: 2026-08-02
작성자: dominic
상태: 진행중
요약: "비트버켓 페치 받아줘" 트리거 루틴 — 전체 fetch + 안전 조건 충족 저장소만 pull(--ff-only). 판정 기준·실행 절차·App password 폐기 대응(SSH 필수) 포함
---

# 🔄 저장소 동기화 루틴 (Bitbucket)

> **트리거**: 사용자가 **"비트버켓 페치 받아줘"** (또는 "비트버켓 페치", "페치 받아줘") 라고 말하면 이 문서의 절차를 그대로 수행한다.
> 상위: [../README.md](../README.md) · 접근 수단: [atlassian-access.md](./atlassian-access.md)
>
> 🛑 **[강제] 이 루틴은 통합 호출 쿼터를 크게 소모한다.**
> 저장소 12개 전체 fetch = **12회** (1일 통합 50회 중 **24%**). pull 이 붙으면 더 늘어난다.
> **착수 전에 [atlassian-access §3-2 사용 내역](./atlassian-access.md#3-2--호출-사용-내역-매일-갱신)의 잔여 횟수를 먼저 확인**하고, 잔여가 대상 저장소 수보다 적으면 **실행하지 말고 사용자에게 보고**한다.
> 저장소 사이 **3초 대기**는 필수다. 완료 후 사용 내역 표를 즉시 갱신한다.

## 1. 요구사항 (사용자 확정, 2026-08-02)

1. **fetch 는 받을 수 있는 것 전부** 받는다. (fetch 는 워킹트리를 건드리지 않으므로 상태와 무관하게 안전)
2. **pull 은 가능한 것만** 받는다.
3. **수정중 · 스테이징 · (푸시 안 된) 로컬 커밋이 있으면 그냥 둔다.** pull 하다 꼬일 수 있는 것은 손대지 않는다.

## 2. 대상 저장소 — 동적 수집

워크스페이스 루트 하위를 훑어 **`origin` remote 가 `bitbucket.org` 인 저장소만** 대상으로 한다.
**하드코딩하지 않는다** → 새로 클론한 저장소가 자동 포함된다.

- 제외: GitHub(`md`, `ECC`), AWS CodeCommit(`spc_batch`, `spc_spring_batch`)
- 2026-08-02 기준 **12개**: `gcs` `gcs_fo` `ha-admin` `ha-api` `ha-batch` `ha-panel` `ha-web` `happypoint-web2` `j-ha-admin` `j-ha-api` `j-ha-web` `j-ha-web-api`
- ⚠️ `ha-admin`/`j-ha-admin`, `ha-api`/`j-ha-api`, `ha-web`/`j-ha-web` 는 **같은 원격의 중복 체크아웃**이다. 각각 독립 워킹카피이므로 **따로 처리**한다.

## 3. 판정 기준 (정본)

### 3-1. fetch
**전 저장소 무조건 수행.** 꼬인 저장소도 원격 정보는 최신화해 두는 것이 이득이다.

> 🛑 **단, 잔여 쿼터가 대상 저장소 수보다 적으면 "전부"가 아니다.** 이 경우 임의로 일부만 돌리지 말고 **중단하고 사용자에게 보고**한다 — 부분 fetch 는 판정을 왜곡시켜 SKIP/PULL 결정을 틀리게 만든다. 사용자가 대상을 좁혀주거나 +10 을 승인하면 진행한다.

### 3-2. pull — 아래 **하나라도** 걸리면 🟡 SKIP

| # | 조건 | 사유 |
|---|------|------|
| 1 | 수정중 (unstaged) | 사용자 지시 — 꼬임 위험 |
| 2 | 스테이징됨 (staged) | 사용자 지시 — 꼬임 위험 |
| 3 | **로컬 커밋 있음 (ahead > 0)** | 사용자 지시 — 푸시 안 된 커밋 보호 |
| 4 | 충돌 파일 존재 (unmerged) | 꼬임 |
| 5 | rebase / merge / cherry-pick / am / bisect **진행중** | 꼬임 |
| 6 | detached HEAD | 브랜치가 아님 |
| 7 | upstream 없음 | 추적 대상 없음 |
| 8 | diverged (ahead>0 **AND** behind>0) | 꼬임 |

### 3-3. 로컬 브랜치 반영 — 🟢 실행 조건 (전부 충족해야 함)
```
클린(수정·스테이징·충돌 0) AND 진행중작업 없음
AND 브랜치 위 AND upstream 존재
AND ahead == 0 AND behind > 0
```
→ 현재 체크아웃 브랜치는 **`git pull --ff-only`**.

→ 비체크아웃 로컬 브랜치도 같은 조건을 충족하면, `checkout` 없이 SSH refspec으로 fast-forward 반영한다.
```bash
git fetch --no-tags <ssh-url> \
  refs/heads/<upstream-branch>:refs/remotes/origin/<upstream-branch> \
  refs/heads/<upstream-branch>:refs/heads/<local-branch>
```
- 원격 추적 참조와 로컬 브랜치를 **같은 SSH 요청에서 함께** 갱신해, 반영 뒤 `ahead/behind` 판정이 일치하게 한다.
- 대상 브랜치가 다른 worktree에서 체크아웃되어 있으면 제외한다.
- refspec에 `+`를 붙이지 않는다. non-fast-forward 상황은 Git이 거부하도록 둔다.

- **untracked 파일만** 있는 경우는 pull 진행(리포트에 표시). 충돌이 생기면 `--ff-only` 가 자동 차단한다.

### 3-4. 절대 하지 않는 것
`stash` · `checkout` · `reset` · 브랜치 전환 · `--force` · 커밋 · merge 커밋 생성
→ **`--ff-only` 가 안전장치**다. fast-forward 불가 시 **실패하고 아무것도 바뀌지 않는다.**

## 4. 실행 절차

1. **대상 수집** (§2)
2. **순차 SSH fetch** — `git fetch <ssh-url>`
   - ⚠️ **병렬 금지 · 호출 간 최소 1초 간격 유지**. Bitbucket SSH Git 요청은 REST API와 동일하게 초당 1회 이하로 제한한다.
   - `--prune` 은 **기본 미적용**. 필요 시 사용자가 명시적으로 지시.
   - **전 대상의 fetch 완료가 이 단계의 종료 조건이다.** 한 저장소의 fetch가 끝났다고 즉시 해당 저장소 브랜치를 반영하지 않으며, 전체 대상 fetch 성공·실패 결과를 확정한 뒤 다음 단계로 간다.
3. **저장소별 판정** — fetch 후에 `ahead`/`behind` 를 확정한다(fetch 전 수치는 무효).
   ```bash
   git rev-list --left-right --count '@{upstream}...HEAD'   # → "behind<TAB>ahead"
   ```
4. **로컬 브랜치 반영** — 조건 충족분만 현재 브랜치는 `git pull --ff-only`, 비체크아웃 브랜치는 SSH refspec fetch
   - 한 저장소 실패가 전체를 중단시키지 않는다. 다음으로 계속.
5. **결과 표 보고** — 저장소 / 브랜치 / 판정 / 사유 / 변경(`before → after`) + 요약(PULL·SKIP·최신·실패 건수) + SKIP 사유별 안내

## 5. 🔴 전제 — HTTPS 불가, SSH 필수 (2026-08-02 확인)

**Bitbucket 이 App password 를 폐기했다.** 저장된 App password 로 HTTPS git 접근 시 **410 Gone**:
```
remote: CHANGE-3222 - Functionality has been deprecated
remote: App passwords are deprecated and must be replaced with API tokens.
fatal: unable to access 'https://bitbucket.org/...': The requested URL returned error: 410
```

**대응 = SSH 사용.** remote 형식:
```
git@bitbucket.org:sectanine/<repo>.git
```
- HTTPS 를 유지하려면 저장된 자격증명을 **API 토큰 + username=이메일** 로 교체해야 한다(추가 작업).
- 이 KB 는 **SSH 를 정본 경로**로 한다. 상세: [atlassian-access.md §2-1](./atlassian-access.md)

### 사전 점검 (fetch 실패 시 1순위 확인)
```bash
ssh -o BatchMode=yes -T git@bitbucket.org
# 정상: "authenticated via ssh key."
```
```bash
git -C <repo> remote get-url origin
# https:// 로 시작하면 → App password 폐기로 실패한다. SSH 로 전환 필요.
```

## 6. 함정 (실제로 겪은 것)

| # | 함정 | 대응 |
|---|------|------|
| 1 | **`~/.ssh/config` 에 UTF-8 BOM** → `Bad configuration option: \357\273\277#` 로 OpenSSH 가 config 전체를 거부 | PowerShell `Set-Content -Encoding utf8` 은 **BOM 을 넣는다.** `[System.IO.File]::WriteAllText($p,$c,(New-Object System.Text.UTF8Encoding($false)))` 로 작성 |
| 2 | PowerShell 함수 안의 `Write-Output` 이 **반환값에 섞인다** → 상태 로그가 데이터로 잡힘 | 로그는 `Write-Host`, 데이터는 `return` 으로 분리 |
| 3 | fetch 전 `ahead`/`behind` 판정 | **무의미하다.** 반드시 fetch 후 재계산 |
| 4 | 중복 체크아웃(`j-*`)을 같은 저장소로 합쳐 처리 | 워킹카피가 다르므로 **개별 처리** |
| 5 | git remote username 은 `dominic.kim`, **REST API 는 이메일** | 혼동 금지 ([atlassian-access.md §5](./atlassian-access.md)) |

## 7. 판정 결과 예시 (2026-08-02 실측, fetch 실패 전 로컬 상태)

| 저장소 | 브랜치 | 예상 판정 | 사유 |
|---|---|---|---|
| `ha-api` | dev1dev | 🟡 SKIP | 수정중 1건 |
| `happypoint-web2` | dev-j | 🟡 SKIP | 수정중 3건 + untracked 3 |
| `j-ha-admin` | develop | 🟡 SKIP | 수정중 3건 + untracked 1 |
| 나머지 9개 | — | 🟢 fetch 후 behind면 PULL | 클린·브랜치·upstream 정상 |

## 8. 미결 사항

- [ ] remote 12개를 HTTPS → SSH 로 전환 (미실행 — 사용자 승인 대기)
- [ ] 전환 후 이 문서 §7 을 실제 실행 결과로 갱신
- [ ] Windows 자격증명에 남은 **폐기된 App password** 정리 여부 결정
- [ ] macOS 에서도 동일 루틴 검증 (SSH 키·config 이미 존재하는 환경)

## 참고
- [KB 루트 README](../README.md)
- [Atlassian 접근 수단](./atlassian-access.md)

## 9. 실행 이력

### 2026-08-05 Bitbucket fetch + pull

- **대상**: 워크스페이스 루트에서 동적 수집한 Bitbucket `origin` 저장소 **12개** (§2 목록과 일치). GitHub(`md`·`ECC`)·CodeCommit(`spc_batch`·`spc_spring_batch`) 제외.
- **사전 점검**: `ssh -T git@bitbucket.org` → `authenticated via ssh key.` 확인.
- **fetch**: 12개 **전부 성공**. 원격 URL은 **변경하지 않고** HTTPS origin에서 변환한 SSH URL을 `git fetch <ssh-url>` 에 직접 지정했다. 저장소 간 **3초 대기** 준수(병렬 없음).
- **판정** (fetch 후 재계산): PULL 2 · SKIP 3 · 최신 7.

| 저장소 | 브랜치 | ahead | behind | 판정 | 사유 |
|---|---|---:|---:|---|---|
| `j-ha-api` | develop | 0 | 22 | 🟢 **PULL** | |
| `j-ha-web` | develop | 0 | 9 | 🟢 **PULL** | |
| `happypoint-web2` | dev-j | 0 | 0 | 🟡 SKIP | 수정중 1 |
| `j-ha-admin` | develop | 0 | **86** | 🟡 SKIP | 수정중 3 · untracked 1 |
| `j-ha-web-api` | dev-j | 0 | 0 | 🟡 SKIP | 수정중 2 |
| `gcs` `gcs_fo` `ha-admin` `ha-api` `ha-batch` `ha-panel` `ha-web` | — | 0 | 0 | ✅ 최신 | |

- **반영**: `j-ha-api/develop` **22커밋**(`edbc5c502` → `d1d065206`), `j-ha-web/develop` **9커밋**(`9c9b743b` → `601946fa`). 둘 다 `--ff-only`, 반영 후 `behind=0 ahead=0` 확인.
- **안전 조치**: `stash`/`checkout`/`reset`/`--force`/브랜치 전환/원격 URL 변경 **미수행**. SKIP 3건은 손대지 않았다.
- 🔴 **후속**: `j-ha-admin` 이 **behind 86** 으로 가장 뒤처져 있다. 작업 트리 변경 3건을 정리하면 반영 가능하다.
- **쿼터**: SSH 인증 1 + fetch 12 = **13회** 사용.

### 2026-08-03 Bitbucket fetch
- 대상: Bitbucket `origin` 저장소 12개 전체.
- 결과: 12개 모두 HTTPS remote의 Bitbucket App password 폐기(`410 Gone`)로 fetch 실패.
- 안전 조치: 원격 정보가 갱신되지 않아 `pull --ff-only`는 0건 실행. 작업 트리, 스테이징, 브랜치, 커밋은 변경하지 않음.
- 후속: 각 Bitbucket remote를 SSH(`git@bitbucket.org:sectanine/<repo>.git`)로 전환한 뒤 이 루틴을 다시 실행.

### 2026-08-03 Bitbucket SSH fetch 재실행
- 대상: Bitbucket `origin` 저장소 12개 전체. 원격 설정은 변경하지 않고, 각 HTTPS origin에서 변환한 SSH URL을 `git fetch <ssh-url>`에 직접 지정했다.
- 결과: 12개 모두 fetch 성공. 병렬 호출 없이 저장소별 완료 후 최소 1초를 대기했다.
- pull: 0건. 클린 상태인 9개는 모두 `behind=0`으로 최신이었고, `happypoint-web2`는 작업 트리 변경 1건, `j-ha-admin`은 작업 트리 변경 4건, `j-ha-api`는 `ahead=6`으로 안전 조건을 충족하지 않아 그대로 두었다.
- 안전 조치: `pull`/`stash`/`checkout`/`reset`/브랜치 전환/원격 URL 변경은 수행하지 않았다.

### 2026-08-03 로컬 브랜치 fast-forward 반영
- 범위: 로컬 추적 브랜치 70개를 재판정했다. 현재 체크아웃 브랜치뿐 아니라 비체크아웃 로컬 브랜치도 대상에 포함했다.
- 결과: `ha-api` 5개, `ha-web` 3개, `j-ha-api` 5개로 총 13개를 SSH refspec fetch로 fast-forward 반영했다. 모두 성공했고, 요청 간 최소 1초를 지켰다.
- 검증 보완: `ha-api/feature/WORK-15914`는 첫 반영 뒤 원격 추적 참조만 이전 fetch 시점에 머문 것을 확인해, SSH로 `origin/feature/WORK-15914`를 갱신했다. 이후 `behind=0`, `ahead=0` 확인.
- 제외: 작업 트리 변경이 있는 `j-ha-admin` 전체, 로컬 커밋이 앞선 `ha-api/dev2stg`, `ha-api/dev-j`, `j-ha-api/dev1dev`, `j-ha-api/feature/WORK-16655`, upstream이 없는 `happypoint-web2/develop` 등은 변경하지 않았다.
- 안전 조치: `checkout`/`stash`/`reset`/강제 업데이트/원격 URL 변경은 수행하지 않았다. 현재 체크아웃 브랜치는 모두 최신이라 `git pull --ff-only` 실행은 0건이다.

### 2026-08-03 전체 fetch 후 로컬 브랜치 반영 재실행
- fetch 단계: 워크스페이스 전체를 재귀 수집한 Bitbucket 저장소 12개에 SSH fetch를 먼저 모두 완료했다. 전부 성공했고, fetch 완료 전에는 브랜치 반영을 시작하지 않았다.
- 판정 단계: 로컬 추적 브랜치 70개를 fetch 결과 기준으로 재계산했다. 최신 57개, 작업 트리 변경으로 제외 4개, 로컬 커밋/분기 상태로 제외 6개, upstream 없음으로 제외 1개였다.
- 반영 단계: `j-ha-web/develop`(behind 4)과 `j-ha-web/qa`(behind 5)를 SSH refspec fetch로 fast-forward 반영했다. 2건 모두 성공했고, 각 요청 사이 최소 1초를 대기했다.
- 안전 조치: 현재 체크아웃 브랜치에는 반영 대상이 없어 `git pull --ff-only` 0건. `checkout`/`stash`/`reset`/강제 업데이트/원격 URL 변경은 수행하지 않았다.
