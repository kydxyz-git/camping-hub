# 캠핑 허브 빌드 자산 (Deprecated)

⚠️ **이 폴더는 더 이상 빌드에 사용되지 않습니다.** (260521+)

## 현재 빌드 흐름

`index.html`이 런타임에 `data/*.json` 파일을 fetch로 로드합니다:
- `data/config.json` — 사이트 텍스트
- `data/series.json` — 인스타 시리즈
- `data/foods.json` — 추천 음식
- `data/items.json` — 추천 템
- `data/camps.json` — 캠핑장 카탈로그

동기화 시 변경되는 것은 `data/*.json`만이며, `index.html`은 직접 수정합니다.
`_build/camping-hub-v4-draft.html`은 옛 lambda re.sub 빌드 흐름의 잔존물로,
다음 빌드에 영향을 주지 않습니다.

## 보존 이유

- 과거 채팅 메모리 + 운영가이드 5장/12-2/13-3이 `_build/`를 참조
- 즉시 삭제 시 새 채팅 세션에서 컨텍스트 혼란 가능
- 보존하되 deprecated 명시

## 새 채팅 시작 시 복원 절차 (참고)

`sync_data.json`만 복원하면 됨:
```bash
cd /home/claude
git clone https://github.com/kydxyz-git/camping-hub.git gh-camping-hub
cp gh-camping-hub/_build/sync_data.json /home/claude/  # 노션 page_id 캐시 용도
```
