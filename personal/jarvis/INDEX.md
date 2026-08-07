---
문서유형: PERSONAL
프로젝트: jarvis (개인 도구)
관련프로젝트: 전 저장소 공통 — Claude Code · Codex 세션 활동 수집
작성일: 2026-08-06
최종수정: 2026-08-06
작성자: dominic
상태: 운영중
요약: Claude Code·Codex 세션 활동을 실시간으로 보는 로컬 대시보드. 훅(`~/.claude/hooks/jarvis.js`)이 두 하네스 공통으로 수집하고 `dashboard.html` 이 표시한다. `serve.py` 로 로컬 호스팅(기본 127.0.0.1:8708). 수집 데이터(data.js·history.js·hosts.json·turns.json)는 대화 원문을 포함하므로 `.gitignore` 로 커밋에서 제외한다.
---

# Dominic Jarvis

Claude Code · Codex 세션 활동을 한 화면에서 보는 로컬 대시보드.

## 구성

| 파일 | 역할 |
|---|---|
| `dashboard.html` | 대시보드 본체. 외부 리소스 0, 단독 실행 가능 |
| `serve.py` | 로컬 호스팅 (기본 `127.0.0.1:8708`) |
| `data.js` | 활동 스트림 — 훅이 append (**커밋 제외**) |
| `history.js` | 대화 원문 + 작업 맥락 — 훅이 append, 회전 없음 (**커밋 대상**) |
| `hosts.json` · `turns.json` | 세션 호스트 판별 캐시 · 턴 토큰 기준선 (**커밋 제외**) |

## 실행

```bash
python serve.py            # 이 PC 전용
python serve.py --lan      # 같은 Wi-Fi 공개
python serve.py --port 9000
```

`dashboard.html` 을 더블클릭해도 동작한다(`file://`). 서버는 폰·다른 PC 에서 볼 때만 필요하다.

> ⚠️ `--lan` 은 인증이 없다. `history.js` 에 대화 원문이 그대로 들어 있으므로 공용망에서는 쓰지 말 것.

## 데이터를 채우는 쪽

수집은 이 저장소가 아니라 훅이 한다.

```
~/.claude/hooks/jarvis.js      ← Claude Code · Codex 공용
~/.claude/settings.json        ← Claude Code 훅 등록
~/.codex/hooks.json            ← Codex 훅 등록
```

훅이 `UserPromptSubmit` · `PreToolUse` · `PostToolUse` · `Stop` · `SessionStart` · `Notification` 을 받아
`data.js` / `history.js` 에 append 한다. stdout 을 내지 않아 세션 컨텍스트를 오염시키지 않는다.

## `history.js` 레코드 — 작업 추적용

한 줄이 사용자 발화 1건이다. 언제·어디서·무슨 태스크로 한 말인지 함께 남긴다.

| 필드 | 뜻 | 예 |
|---|---|---|
| `ts` | epoch ms (정렬용) | `1786032816719` |
| `d` | 사람이 읽는 시각 | `2026-08-07 01:13:36` |
| `s` | 세션 ID 앞 8자 (화면 표시용) | `63859d39` |
| `sid` | **전체 세션 UUID** — 트랜스크립트 파일명과 동일 | `63859d39-d0c6-4f80-80f8-e2d808ef3d2a` |
| `h` | 호스트 | `IntelliJ IDEA` · `Claude APP` · `Codex` |
| `repo` | 저장소명 (`.git` 위치 기준) | `happypoint-web2` |
| `br` | 브랜치 | `feature/WORK-16613` |
| `task` | 브랜치에서 뽑은 이슈키 | `WORK-16613` |
| `w` | 작업 디렉터리명 | `happypoint-web2` |
| `n` | 요청 원문 (4,000자에서 절단) | — |

- 저장소·브랜치는 **git 명령을 띄우지 않고** `.git/HEAD` 를 직접 읽는다. 프롬프트 제출마다 도는 경로라 프로세스를 안 띄운다.
- 홈 디렉터리처럼 저장소 밖에서 띄운 세션은 `repo`·`br` 를 남기지 않는다(`HEAD` 같은 잡음 방지).
- 대시보드 검색은 본문뿐 아니라 **호스트·저장소·브랜치·태스크·날짜**를 함께 훑는다. `WORK-16613` 로 검색하면 그 태스크의 대화만 남는다.

> ⚠️ 이 파일은 대화 원문을 그대로 담는다. 추적 목적으로 커밋하기로 했으므로(2026-08-07),
> 붙여넣는 내용에 크리덴셜이 섞이지 않도록 주의할 것. 한 번 커밋되면 이력에서 지우기 어렵다.

## 화면

- **📡 실시간 스트림** — 도구 호출·사용자 요청·턴 경계. 0.1초 폴링
- **🎯 Active Session** — 세션별 카드. 호스트(프로젝트) 이름표, 진행 중 표시, 에이전트 칩, 턴 소요·토큰
- **🔥 많이 만진 파일** — 오늘 기준
- **💬 대화 히스토리** — 날짜별·검색

## 세션 이름

`CLAUDE_CODE_ENTRYPOINT` · 실행 경로 · 프로세스 계보로 호스트를 판별하고 `cwd` 로 프로젝트를 붙인다.
`IntelliJ IDEA (happypoint-web2)` · `Claude APP` · `Codex (j-ha-web-api)` 처럼 표시된다.
판별 결과는 `hosts.json` 에 세션당 1회만 캐시한다.
