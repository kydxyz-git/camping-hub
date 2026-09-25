# CLAUDE.md

이 저장소에서 작업할 때 따르는 규칙.

## 데이터 진실소스

- 관리자 페이지 `kydz.kr/kydzm/` 에서 수정하면 `data/*.json` 으로 자동 커밋된다.
  - `data/items.json` — 장비
  - `data/foods.json` — 음식
  - `data/series.json` — 시리즈
  - `data/insights.json` — 성과 리포트

## 이미지

- 장비·음식 썸네일(`images/products`): 800x800 JPEG, 흰 배경, 여백 7%, 원본 비율 유지(잘림 금지)
- 이미지 교체 시 새 파일명으로 저장하고 해당 JSON의 `thumb`·`updated_at` 을 갱신한다 (캐시 무효화)

## 구버전 문서

- `tools/SYNC_GUIDE.md` 는 260507 노션 동기화용 구버전이다.
  - 장비 썸네일 규격에 적용하지 말 것
  - 노션 토큰 푸시 절차도 폐기됨

## 금지 사항

- 디스플레이 광고 배너 추가 금지 (협찬 브랜드 인상 관리)

## Git

- 커밋 메시지 형식: `type(scope): 한글 요약`
- main에 머지하기 전에 변경 요약을 보여주고 확인받기
