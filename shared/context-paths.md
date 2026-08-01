---
문서유형: SHARED
프로젝트: 공통(지식 베이스 경로)
작성일: 2026-07-30
최종수정: 2026-07-31
작성자: dominic
상태: 진행중
요약: Happy Point Card Codex 컨텍스트 자동참조에 사용하는 Windows 절대 경로.
---

# 컨텍스트 베이스 절대 경로

## Windows 개발 PC

| 구분 | 절대 경로 | 사용 원칙 |
|---|---|---|
| md 지식 베이스 | `D:\200_DEV\230_WORKSPACE\happypointcard\md` | 작업 전 우선 참조하고, 작업 결과와 결정 사항을 적절한 Markdown 문서에 기록한다. |
| ECC 해커톤 컨텍스트 | `D:\200_DEV\230_WORKSPACE\happypointcard\ECC` | 해커톤 우승자 컨텍스트를 참고하는 읽기 전용 자료다. 원본은 수정하지 않는다. |

## 자동참조 순서

1. md 지식 베이스를 먼저 읽어 관련 요지, 결정 사항, 관례, 현재 상태를 파악한다.
2. ECC를 참조하여 해커톤 우승자의 관점을 현재 작업에 적절히 반영한다.
3. 작업으로 새로 생기거나 변경된 지식은 md 지식 베이스에 업데이트한다.

## macOS 개발 PC

| 구분 | 절대 경로 |
|---|---|
| md 지식 베이스 | `/Users/joon/IdeaProjects/md` |
| ECC 해커톤 컨텍스트 | `/Users/joon/IdeaProjects/ECC` |

훅은 `process.platform` 으로 OS 를 판별해 경로를 고르고, 해당 경로가 없으면 반대쪽 OS 경로로 폴백한다. 그래서 **두 PC 에서 같은 파일을 그대로 복사해 쓸 수 있다.**

> 다른 운영체제에서는 이 문서의 역할과 원칙은 유지하되, 각 PC에 존재하는 로컬 절대 경로로 전역 훅 설정을 구성한다.

## 🚨 [상시 규칙] 컨텍스트 자동주입 설정은 Claude · Codex 양쪽 호환으로 수정한다

**md 컨텍스트 자동참조 설정(훅·주입 규칙)을 수정할 때는 반드시 두 하네스 양쪽을 함께 맞춘다.** 한쪽만 고치면 하네스마다 다른 컨텍스트가 주입되어 작업 결과가 갈린다.

| 하네스 | 훅 경로 | 등록 위치 |
|---|---|---|
| **Claude Code** | `~/.claude/hooks/inject-readme.js` | `~/.claude/settings.json` (SessionStart) |
| **Codex** | `~/.codex/hooks/inject-readme.js` | `~/.codex/hooks.json` (SessionStart) |

**두 파일은 byte-for-byte 동일해야 한다.** 수정 후 반드시 복사·대조한다.

```bash
cp ~/.claude/hooks/inject-readme.js ~/.codex/hooks/inject-readme.js
diff -q ~/.claude/hooks/inject-readme.js ~/.codex/hooks/inject-readme.js
```

### 재생성 시 보존해야 할 사용자 설정

훅을 다시 만들거나 덮어쓸 때 **아래 값을 초기화하지 않는다.** 보존하지 않으면 제외하기로 한 프로젝트가 다시 주입된다.

| 상수 | 역할 | 변경 조건 |
|---|---|---|
| `INCLUDED_PROJECTS` | **자동 주입 화이트리스트** | **사용자가 명시적으로 지시할 때만** |
| `MAX_BYTES_PER_FILE` | 파일당 주입 상한 (현재 30000) | 문서가 커져 잘릴 때 |

### 자동 주입 화이트리스트 (2026-08-01 기준 9개)

`homepage-ai-renewal` · `ha_api` · `ha-web-api` · `ha_web` · `ha-push-batch` · `thehappy_ios` · `thehappy_aos` · `happypoint-web2` · `ha_admin`

- **화이트리스트 방식**이다. KB 에 새 프로젝트가 등록되어도 목록에 추가되기 전까지 주입되지 않는다(기본 제외).
- 목록 밖 프로젝트도 KB 에는 존재한다. 사용자가 요청하면 그때 `projects/<slug>/INDEX.md` 를 읽는다.
- 필터는 **README 원본을 수정하지 않는다.** 주입되는 사본에서 표 행만 걸러내므로 KB 허브 인덱스는 14개 그대로 유지된다.

## 적용 기록

- 2026-07-31: Windows 개발 PC에서 `~/.codex/hooks/inject-readme.js`를 SessionStart 훅으로 등록했다. Windows/macOS 경로 상수와 반대 OS 폴백을 사용하며, `md/README.md`와 `md/shared/ecc-reference.md`를 자동 주입한다.
- 2026-08-01: macOS(M1 Max)에 동일 훅을 `~/.claude/hooks/inject-readme.js` 로 구성하고 `~/.claude/settings.json` SessionStart 에 등록했다. 주입 상한을 18000 → **30000** 으로 올려 두 문서가 잘리지 않게 했다.
- 2026-08-01: 자동 주입을 **화이트리스트 방식**으로 전환했다(9개). 양쪽 훅 파일을 byte-for-byte 동기화했고, 파일 상단에 양쪽 호환·설정 보존 경고를 명시했다.
