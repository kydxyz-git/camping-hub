# CLAUDE.md

공대남자(@kyd_zm) 캠핑 허브 — https://kydz.kr (GitHub Pages, main 브랜치 자동 배포).
과거 이력·상세 배경은 `docs/OPERATIONS_GUIDE.md`(노션 운영가이드 보관본, 일부 폐기). 이 파일과 다르면 **이 파일과 실제 코드가 기준**.

## 아키텍처·데이터 흐름

- 빌드 단계 없는 정적 사이트. `index.html`(인라인 CSS/JS)을 직접 수정하고, 데이터는 런타임에 `data/{config,series,foods,items,camps}.json`을 fetch.
- **데이터 진실소스: admin(`kydz.kr/kydzm/`) → `data/*.json`·이미지가 main에 자동 커밋** (GitHub API).
  - `items.json` 장비(캠핑용품) · `foods.json` 음식(먹거리) · `series.json` 시리즈/EP · `camps.json` 캠핑장
  - `config.json` 사이트 문구·탭명·정렬(`foodsSort`/`itemsSort`)·장비 분류(`itemCats`) · `insights.json` 성과 리포트
  - `stats.json` 통계 Worker가 매시간 커밋 (`chore(stats): hourly sync`) — 손대지 않기
- admin 자동 커밋이 수시로 들어오므로 작업 전 항상 최신 main을 받고, 데이터 JSON은 필요한 필드만 최소 수정.
- 노션은 더 이상 진실소스가 아님. `_cache/sync_data.json`은 과거 노션 page_id 캐시(참고용).

## 페이지 구성

- `index.html` 메인 (`is-pc`/`is-mo` 클래스로 PC·모바일 레이아웃 분기)
- `camp.html` 캠핑장 상세 — 메인 캠핑장 카드에서 `camp.html?id=`로 연결됨 (사용 중)
- `collab.html` 협업 문의 · `preview.html` 모바일 미리보기
- `v2.html`, `v3.html` 폐기된 실험 — 수정 대상 아님
- `conti/`, `kydzm/conti/` 릴스 콘티 · `prompts/` 프롬프트 모음

## admin (kydzm/)

- `index.html` 콘텐츠 CRUD + 통계 대시보드 · `insights.html` 성과 분석 · `deals.html` 딜 보드 · `conti.html` 콘티 보드
- 인증: GitHub PAT를 브라우저 localStorage에만 저장. **토큰·시크릿은 저장소에 절대 커밋 금지.**
- 커밋 메시지: 추가 `sync(admin): …` / 수정 `update(admin): …` / 삭제 `delete(admin): …`
- 콘텐츠 ID `{type}_{hash10}` + `created_at`/`updated_at`. 통계 경로도 ID 기반(`/series/{sid}/{epid}`, `/camps/{id}` …).
- 참고: admin 이미지 업로드는 현재 4:5 센터 크롭 600×750 JPEG(`cropImage4to5`)로 저장됨 → 장비·음식 썸네일 규격과 다르므로, 규격 적용은 수동 교체로 한다.

## 콘텐츠 추가

- 기본은 admin에서 추가/수정.
- 직접 추가할 때: 기존 항목 형식 그대로 (`id`, `created_at`, `updated_at` 포함). 장비 `cat`은 `config.itemCats`의 key.
- 캠핑장 CSV 병합은 `id` 기준. 삭제된 필드(`landscape`/`seasons`/`sites`/`price`)는 되살리지 않기.
- 콘텐츠가 실제로 바뀌면 `python3 tools/update_sitemap.py`.

## 이미지

- **장비·음식 썸네일(`images/products`): 800×800 JPEG, 흰 배경, 여백 7%, 원본 비율 유지(잘림 금지)**
- 이미지 교체 시 **새 파일명**으로 저장하고 해당 JSON의 `thumb`·`updated_at` 갱신 (캐시 무효화). 참조 없어진 이전 파일은 삭제.
- 시리즈(`images/series`)·캠핑장(`images/camps`)은 기존 파일 규격을 따른다.

## UI/UX 규칙

- 모바일 우선, PC(≥1024px)는 확장 레이아웃.
- 사진 위 배지는 최대 2개: PICK(노란 별) 좌상단, 판매처/예약처 우하단.
- 예약처 배지: 그래가 `#1a1a1a` / 네이버 `#03C75A` / 캠핏 `#2D8F4C` / 땡큐캠핑 `#FF6B2C` / 기타 `#9e9e9e`
- 판매처 배지: 쿠팡 `#ee2c4d` / 컬리 `#5f0080` / 네이버 `#03C75A` / 알리 `#FF4747` / 테무 `#FF6A00` / 기타. `source`는 저장 시 URL로 항상 재판정.
- 제품 카드는 사진 + 이름 + 배지만 (가격·구매 버튼 없음). 메뉴명은 먹거리/캠핑용품 — "추천" 같은 광고 톤 지양.
- 링크 없는 카드는 `<a href="#">` 대신 `<div>`로 렌더.
- 캠핑장 정렬(`sortCamps`): 그래가 → 이미지 있는 곳 → 방문 횟수↓ → 이름. 별점은 숨김.
- 랜덤 정렬은 7일 이내 신규(`created_at`) 우선 (`sortRecentFirst`).
- 인스타 링크 정규화 유지: `/reel/`·`/tv/` → `/p/`, 추적 파라미터 제거, 인앱 브라우저 → 외부 브라우저, Android는 `intent://`.
- 명당 자리 번호·계곡 포인트 등은 DM 전용 — 사이트에 공개 금지.
- **디스플레이 광고 배너 추가 금지** (협찬 브랜드 인상 관리).

## 통계 (Worker v6 · KST)

- Cloudflare Worker `https://kyd-stats.kydxyz.workers.dev` (KV `KYDZ_STATS`). 소스는 저장소 밖, 사용자가 Cloudflare 대시보드에서 배포.
- 이벤트는 개별 키 `buf:{ts}:{rand}`로 저장 (KV race 회피) — 단일 buffer 키 read-modify-write 금지.
- 엔드포인트: `POST /log`, `GET /stats`, `GET /events?date=`, `GET /health` / SYNC_TOKEN 필요: `/sync`, `/reset`, `/cleanup`, `/migrate-kst`
- **날짜 키는 KST 기준**: admin은 `kstDateStr()`/`kstToday()` 사용, `toISOString().slice(0,10)` 직접 사용 금지. Worker cron은 UTC (KST 0시 = UTC 15시).
- 메인 추적: 카드 페이지뷰는 `pointerdown` capture에서 발송, `sendBeacon` 실패 시 `fetch` keepalive. `isContentPath()`로 방문/콘텐츠 구분해 dedup (방문 30분·24시간, 콘텐츠 5분). 디버그 `?debug=1`.

## 트러블슈팅 핵심

- 반영이 안 보임: Pages 배포 1~5분 + 브라우저 캐시 → 하드 리프레시. 이미지는 새 파일명으로 교체.
- 한글 검색 깨짐: 입력 중 rerender 금지 → 조회 버튼 / Enter(`!e.isComposing`)에서만 검색.
- Android 네이티브 `<select>`는 CSS 제어 불가 → 커스텀 div 드롭다운.
- 검색 중 드래그 정렬은 인덱스가 깨짐 → 검색 중엔 드래그 비활성.
- Worker CORS preflight 회피: `Content-Type: text/plain`.

## 구버전 문서 (적용 금지)

- `tools/SYNC_GUIDE.md`·`tools/*.py`·`_cache/`: 260507 노션 동기화용 구버전. 장비 썸네일 규격에 적용하지 말 것, 노션 토큰 푸시 절차도 폐기됨.
- `docs/OPERATIONS_GUIDE.md`의 "⚠️ 폐기" 섹션(노션 진실소스 동기화, `_build` 복원, 토큰 푸시, v3).

## Git

- 커밋 메시지 형식: `type(scope): 한글 요약`
- **main에 머지하기 전에 변경 요약을 보여주고 확인받기.**
