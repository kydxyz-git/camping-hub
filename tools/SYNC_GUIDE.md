# 캠핑 허브 동기화 표준 절차 (260507 강화 버전)

## 핵심 원칙

**노션 search API는 신뢰할 수 없다.** 키워드 매칭이 단편적이라 신규 ep를 놓칠 수 있다.
따라서 **3중 안전망**으로 검출률을 극대화한다.

## 3중 안전망

### 1. 캐시된 page_id로 직접 fetch (가장 확실)
- 위치: `sync_data._metadata.cached_pages.{category}`
- 동작: 알려진 page_id를 직접 fetch → search 우회
- 용도: 기존 ep의 변경 사항 감지 (제목/URL/썸네일/가격)

### 2. 다중 키워드 검색 (신규 ep 검출)
- 위치: `tools/incremental_sync.py` → `SEARCH_KEYWORDS`
- 동작: 카테고리별로 5\~15개 도메인 키워드를 순차 검색 → 합집합
- 우선순위: 사용자가 "X 시리즈에 추가" 라고 명시하면 그 시리즈 키워드 먼저

### 3. 날짜 필터 (created_date_range)
- 동작: `last_sync` 이후 생성된 페이지만 좁혀서 검색
- 한계: 노션 search는 빈 키워드 안 됨, 'a' 같은 와일드카드 무용지물
- 결국 키워드 다양화가 필수

## 동기화 절차 (체크리스트)

사용자가 "X 동기화해줘" 요청 시:

### Step 1 — 환경 확인 + 컨텍스트 로드
```bash
ls /home/claude/sync_data.json /home/claude/gh-camping-hub  # 환경 확인
# 휘발됐으면: git clone + _build 복원 (메모리 #22)
```

### Step 2 — 캐시 vs 노션 비교 (기존 ep 변경 감지)
1. `sync_data._metadata.cached_pages.{category}` 에서 page_id 리스트 추출
2. 각 page_id를 직접 `Notion:notion-fetch` 호출
3. 노션 properties와 sync_data 비교 → 차이 식별

### Step 3 — 신규 ep 검출 (다중 키워드 검색)
1. `tools/incremental_sync.py`의 `SEARCH_KEYWORDS` 참조
2. 사용자가 시리즈 명시했으면 → 그 키워드 우선 + 다른 키워드도 확인
3. `last_sync` 이후 created로 필터링 (시간 절약)
4. 검색 결과 합집합 계산
5. cached_pages와 차집합 → 신규 ep page_id 식별

### Step 4 — 신규 ep fetch + 처리
1. 새 page_id 직접 fetch → 상세 정보 추출
2. 썸네일 다운로드 → 4:5 센터 크롭 → 600×750 JPEG q80
3. 파일명 규칙 따라 저장:
   - 시리즈: `images/series/{prefix}-ep{NN}.jpg` (prefix: summer/spring-autumn/tips/food/gear)
   - 음식: `images/products/food-{NN}.jpg`
   - 템: `images/products/item-{NN}.jpg`
   - 캠핑장: `images/camps/{page_id_suffix}.jpg` (또는 `-N.jpg`)

### Step 5 — sync_data 갱신
1. 변경된 항목 수정 + 신규 항목 추가
2. **`cached_pages`에 새 page_id 등록 잊지 말기**
3. `last_sync` 갱신
4. `_build/sync_data.json`에도 동일하게 저장

### Step 6 — 빌드 + 검증 + push
```bash
python3 /home/claude/build.py
# JSON 파싱 검증, CSS/JS 변경 반영 확인
cd /home/claude/gh-camping-hub
git add -A && git commit -m "sync: ..." 
# 토큰 fetch from 운영가이드 12-3 → push → remote 원복
```

## 절대 하지 말 것

- ❌ search 결과 0건 떴다고 "변경 없음" 결론 내리기 (다른 키워드로 재시도 必)
- ❌ 캐시된 page_id를 무시하고 search만으로 비교 (search는 보조 수단)
- ❌ 사용자가 "X 추가했어" 라고 말했는데 1\~2개 키워드만 시도하고 포기
- ❌ cached_pages 갱신 빠뜨리기 (다음 동기화 때 그 ep가 또 안 잡힘)

## 향후 확장

- 노션 MCP가 데이터소스 row 전체 조회 API를 지원하면 search 의존 자체를 제거 가능
- 그때까지는 이 3중 안전망이 최선
