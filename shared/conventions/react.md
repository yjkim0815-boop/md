---
문서유형: SHARED
프로젝트: 공통
작성일: 2026-07-16
최종수정: 2026-07-16
상태: 초안(확인/수정 필요)
요약: React 컨벤션
---

# ⚛️ React 컨벤션 (초안)

## 컴포넌트
- **함수형 컴포넌트 + Hooks** (클래스형 지양)
- 파일 1개 = 컴포넌트 1개 원칙, 파일명 `PascalCase.jsx/tsx`
- Props 타입 명시(TypeScript 또는 PropTypes)
- 프레젠테이션/컨테이너(로직) 분리 지향

## Hooks
- 규칙 준수: 최상위에서만 호출, 조건문 안 금지
- `useEffect` 의존성 배열 정확히, 클린업 처리
- 커스텀 훅으로 로직 재사용(`useXxx`)

## 상태관리
- 로컬 상태 `useState`, 전역은 팀 표준(Redux/Zustand/Context) *(← 확정 필요)*
- 서버 상태는 React Query 등 고려

## 스타일
- 클래스명/CSS 방식 팀 표준 통일(CSS Module / styled / Tailwind) *(← 확정 필요)*

## 네이밍/구조
- 컴포넌트 `PascalCase`, 훅 `useCamelCase`, 핸들러 `handleXxx`
- 폴더: 기능(도메인) 단위 구성

## 성능/품질
- 불필요 리렌더 방지(`memo`, `useMemo`, `useCallback` — 과용 금지)
- key에 index 지양(안정적 id)
- 접근성(a11y), 에러 바운더리

## 금지/주의
- 직접 DOM 조작 지양(ref 필요한 경우만)
- 시크릿/키 프론트 하드코딩 금지

> TODO: TS 사용여부, 상태관리·스타일 라이브러리, 폴더구조 확정.
