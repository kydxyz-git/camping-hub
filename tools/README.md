# 캠핑 허브 동기화 도구

이 폴더는 **노션 ↔ 캠핑 허브 사이트 동기화**를 안정적으로 수행하기 위한 도구 모음입니다.

## ⚠️ 새 채팅에서 동기화 작업 시 반드시 확인

### 1. `SYNC_GUIDE.md` (필독)
동기화 표준 절차서. 노션 search API의 한계와 그 우회 전략(3중 안전망)이 정리되어 있음.
**"X 동기화해줘" 요청을 받으면 무조건 이 파일부터 읽기.**

### 2. `incremental_sync.py`
- `SEARCH_KEYWORDS`: 카테고리별 신규 ep 검색 키워드 (5\~15개씩)
- `find_new_pages_by_keywords()`: 다중 키워드 합집합 검색
- `detect_changes()`: 캐시 vs 노션 비교

### 3. `refresh_cache.py`
- `sync_data._metadata.cached_pages` 자동 재계산
- **매 동기화 마지막 단계에서 반드시 호출**

## sync_data.json 스키마 변경 (260507)

새로 추가된 `_metadata.cached_pages`:
```json
{
  "_metadata": {
    "last_sync": "...",
    "cached_pages": {
      "series": [{"page_id": "...", "title": "...", "series_name": "..."}, ...],
      "camps":  [{"page_id": "...", "name": "..."}, ...],
      "foods":  [{"page_id": "...", "name": "..."}, ...],
      "items":  [{"page_id": "...", "name": "..."}, ...]
    },
    "cached_pages_updated": "..."
  }
}
```

이 캐시 덕분에 매번 노션 search에 전적으로 의존하지 않고, 알려진 page_id를 직접 fetch해서 변경 사항을 감지할 수 있음.

## 핵심 교훈

### 노션 search API의 한계
- 의미적 매칭이라 키워드가 정확히 안 맞으면 결과 누락
- 빈 키워드/와일드카드 안 됨
- 단일 키워드로 신규 ep 검출 시도하면 약 50% 누락 가능
- → **다중 키워드 + 캐시 우선이 답**
