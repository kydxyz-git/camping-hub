# 캠핑 허브 캐시 폴더

새 채팅 세션에서 사용하는 자산 보관 폴더.

## sync_data.json

노션 page_id 캐시. 새 채팅에서 노션 동기화 작업 시작할 때 page_id를 search 없이 바로 사용하기 위한 용도.

**사용 방법**:
```bash
cp _cache/sync_data.json /home/claude/
```

83개 page_id 캐시 (series 11 / camps 64 / foods 6 / items 2 — 시점에 따라 변동)

## 이전 _build/ 폴더 안내

이전에 `_build/camping-hub-v4-draft.html`이 빌드 진실소스였지만 (운영가이드 5장), 빌드 흐름이 `index.html` 직접 수정 방식으로 변경됨에 따라 폴더 자체가 제거됨. 운영가이드 14-15 참조.
