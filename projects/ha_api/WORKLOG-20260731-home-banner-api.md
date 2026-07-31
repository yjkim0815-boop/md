---
문서유형: WORKLOG
프로젝트: ha_api
이슈키: --
작성일: 2026-07-31
최종수정: 2026-07-31
작성자: dominic
상태: 진행중
요약: 홈페이지 메인 배너 영역(HA_11101)을 제공하는 일반 REST API를 추가했다.
---

# 🛠️ WORKLOG — 홈페이지 메인 배너 API (2026-07-31)

## 배경 / 목적
신규 홈페이지 프론트가 기존 `NormalBannerRepository.listNormalBannerInfo` 쿼리로 메인 배너 목록을 조회할 수 있도록, 모델 API와 분리된 홈페이지 전용 REST API를 추가한다.

## 진행 내용
1. `POST /api/home/banner-list` 엔드포인트를 `controller/rest/home/HomeBannerResource`에 추가했다.
2. `NormalBannerService.listHomepageMainBannerInfo()`가 쿼리 파라미터를 서버에서 구성하도록 추가했다.
3. `areaCode`는 `HA_11101`로 고정해 다른 배너 영역을 요청으로 조회할 수 없게 했다.
4. 웹 디바이스 코드는 `PlatformType.WEB.getCode()`인 `W`로 설정해 `W` 및 `ALL` 배너를 조회한다.
5. 로그인 사용자 기준의 타겟, 등급, 임직원, 세그먼트 조건 및 S3 이미지 URL 조합은 기존 배너 서비스 규칙을 재사용한다.

## API 계약
- Method/URL: `POST /api/home/banner-list`
- Request body: 없음
- Response: `{ "code": "00", "message": "성공", "result": [ ...banner ] }`
- 빈 배너 목록도 정상 응답(`code: "00"`, 빈 배열)으로 처리한다.

## 검증
- 정적 점검: 컨트롤러 → 서비스 → 기존 `NormalBannerRepository.listNormalBannerInfo` 호출 및 MyBatis 파라미터(`areaCode`, `deviceType`, `imgUrl`, 사용자 조건) 연결 확인.
- `mvn -DskipTests compile`: 소스 컴파일 단계 전 `target/classes/attach.yml` 접근 거부로 실패. 기존 빌드 출력 경로 권한 문제이며 신규 소스 컴파일 결과는 미확인.

## 다음 할 일 (TODO)
- [ ] 소유자 권한의 로컬 터미널에서 `mvn -DskipTests compile` 재실행.
- [ ] 개발 DB에서 `HA_11101`의 `W` 또는 `ALL` 배너 노출 데이터와 이미지/링크 값을 확인.
- [ ] 홈페이지 프론트에서 API 연동 및 응답 렌더링.

## 참고 링크
- [ha_api INDEX](./INDEX.md)
- [공통 ECC 참조](../../shared/ecc-reference.md)
