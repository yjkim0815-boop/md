---
문서유형: WORKLOG
프로젝트: etc (미분류)
이슈키: --
작성일: 2026-08-03
최종수정: 2026-08-04
작성자: dominic
상태: 완료
요약: KB 구조 개편 — projects/task 신설·태스크 3건 이관, etc 인박스 신설, Confluence 작성 규격 신설, 일정 관리 체계 도입, 프로젝트 목록 표시 규칙 확정
---

# 🛠️ WORKLOG — KB 구조 개편 (2026-08-03 ~ 08-04)

## 배경 / 목적
특정 프로젝트·태스크에 귀속되지 않는 **KB 자체의 구조·운영 규칙 개편**. 하루 동안 여러 건이 연쇄적으로 확정되어 한 문서로 묶는다.

> 📥 이 문서는 **`projects/etc/` 인박스 규칙의 첫 적용 사례**다. 귀속처가 없어 여기에 기록하며, 필요 시 나중에 배정한다.

## 진행 내용

### 1. 용어·표시 규칙 확정
- **저장소 = "프로젝트" / 과업 = "태스크"** 로 사용자 대면 표기 고정
- **"프로젝트 목록" 6열 표** 확정: `No | 이름 | 설명 | 상태 | 컨텍스트 자동주입 | 구분`
- **태스크를 표 상단**, 프로젝트를 아래 배치
- **표시명 고정값 테이블** — 슬러그별 한글 표시명을 못박아 매번 달라지지 않게 함
- **목록 제외 대상**: `spc_batch` · `spc_spring_batch` · `etc`
- ⚠️ 규칙이 README 두 곳(§컨텍스트 활성화 정책 / §프로젝트 목록 하단)에 중복 존재 → **정본 1곳 + 요약·링크**로 정리

### 2. `projects/task/` 신설 + 태스크 3건 이관
| 태스크 | 이관 | 파일 |
|---|---|---|
| `sms-agent-replacement` | `projects/` → `projects/task/` | 3 |
| `store-search-upgrade` | 〃 | 1 |
| `event-template` | `projects/ha_api/archive/` → `projects/task/event-template/` | **17** |

- 전부 **`git mv`** 로 이동해 파일 이력 보존
- 상대경로 링크 전수 조정 — 특히 `event-template` 허브의 `../INDEX.md`(구 `ha_api` 자기 참조)는 단순 깊이 +1로는 해결되지 않아 **경로별 개별 치환** 필요했음
- `event-template` 은 태스크 진입점 `INDEX.md` 를 신규 작성(정본은 아카이브 유지)
- **`homepage-ai-renewal` 은 이관 보류** — 사용자 지시(작업 진행 후)

### 3. 태스크 폴더 관리 규칙 확정
- 위치: **`projects/task/<슬러그>/`**, 슬러그는 과업명 kebab-case → **폴더명=저장소명 규칙의 명시적 예외**
- **작업로그 위치 규칙**: 대상 저장소가 **있으면** 각 프로젝트 폴더에 / **없으면** 태스크 폴더 안에

### 4. `projects/etc/` 미분류 인박스 신설
- 귀속처가 불명확한 작업 이력을 **등록 시점에 고민 없이** 넣는 대기실
- 트리거 **"etc 내역 보여줘"** → 대기 목록 제시 → 사용자 지정 시 `git mv` + 링크 갱신 + 대상 INDEX 등록 + 배정 이력 기록

### 5. `shared/confluence-authoring.md` 신설
Confluence 문서 작성 규격 정본. `atlassian-access.md`(접근 수단)와 역할 분리.
- 문서 골격 12절 (**요약·가능 범위·제약은 생략 금지**)
- 톤 규칙 6종 — 실측>추정 · 과잉약속 금지 · 독자 언어 · 지표 선별 · **반발 선제대응** · 제약은 시점과 함께
- Confluence HTML+ 규약 · **ADF 중첩 제약** · 불투명 ID 생성 금지
- 자리표시자/초안 원칙 — **모르는 값은 지어내지 않고 비워두고 보고**, 초안 임의 발행 금지, 이미지 업로드 불가
- 트리거 **"컨플 작성해줘"**

### 6. 일정 관리 체계 도입
- 정본 **`personal/schedule.md`** + README 상시 규칙
- **날짜 2축**: `등록일`(추가한 날) / `기준일`(발생·요청일) → **"요청 후 N일"(외부 압박) / "등록 후 N일"(내부 지연)**
- ⚠️ **경과일수는 문서에 저장하지 않고 표시 시점 계산** — 박아두면 다음 날 틀림
- **프로젝트/태스크별 그룹핑** + `📥 미정` 그룹
- 알림: 🔴 지연·🟠 임박은 **매 세션 최상단**, 사용자가 해제할 때까지 지속
- 초기 등록 8건(S-001 ~ S-008)

### 7. 부수 정리
- **서버 2대 KB 등록**: 배치서버 `ip-10-0-70-71`(NDSoft SMS 에이전트 + Anyframe 배치) · 검색서버 `ip-10-0-75-31`(와이즈넛 SF-1 + Elasticsearch 8.19)
- **`spc_batch` · `spc_spring_batch` 실체 규명** — "상세 확인 필요" 껍데기를 실제 분석으로 대체. `spc_spring_batch` 가 `/app/batch` 가동 소스임을 lib 목록 일치로 확정, **형상관리 누락(`wthr/gov` 미커밋)** 발견
- **깨진 상대링크 2건 수정** — `ha-web-api` ↔ `happypoint-web2` 주간 워크로그 상호참조. `worklog/weekly/` 구조 변경 시 미반영된 사전 결함
- `personal/tendency/monthly/TENDENCY-2026-08.md` 신규 작성

## 발생 이슈 & 해결
| 이슈 | 원인 | 해결 |
|---|---|---|
| `event-template` 허브의 `../INDEX.md` 링크 | 이동 전에는 `ha_api/INDEX.md` 를 가리켰으나 이동 후 의미가 완전히 바뀜 | 깊이 +1 일괄 치환이 아니라 **경로별 개별 매핑** |
| 번들 16개의 `../ARCHIVE-event-template.md` | 형제 참조라 깊이 변경 대상이 아님 | 3단계 이상 경로만 선별 치환 |
| README 목록 규칙 중복 | 서로 다른 시점에 두 하네스가 각각 추가 | 정본 1곳 지정 + 나머지는 요약·링크 |
| 링크 검증 필요 | 대규모 이동으로 깨짐 위험 | 전수 검증 스크립트 반복 실행 → **최종 깨짐 0건** |

## 결과
- **md 파일 86개 → 링크 603건 전수 유효(깨짐 0)**
- 태스크 4건 · 프로젝트 11건 · 제외 2건 체계 확립
- 신규 공통 문서 2건(`confluence-authoring.md` · `schedule.md`), 신규 인박스 1건(`etc/`)
- 규칙은 전부 **README에 반영** → Claude Code · Codex 양쪽 자동 적용

## 다음 할 일 (TODO)
- [ ] `homepage-ai-renewal` → `projects/task/` 이관 (사용자 판단 대기)
- [ ] 컨텍스트 주입 열 규칙 정합성 — README 정본 절과 하단 요약 블록의 표기가 한때 상이했음. 재발 여부 관찰
- [ ] Codex `additionalContextLimit: 12000` vs 실제 주입량(41KB) 초과 여부 확인 — 규칙 뒷부분이 잘릴 가능성

## 참고 링크
- [KB 루트 README](../../README.md)
- [shared/confluence-authoring.md](../../shared/confluence-authoring.md)
- [personal/schedule.md](../../personal/schedule.md)
- [etc 인박스 INDEX](./INDEX.md)
