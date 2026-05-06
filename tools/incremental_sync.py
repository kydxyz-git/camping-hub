"""
캠핑 허브 차분 동기화 핵심 로직 (260507~)

작동 원리:
1. sync_data._metadata.cached_pages에 모든 알려진 page_id 캐시되어 있음
2. 캐시된 ID는 Notion search 우회 → 직접 fetch로 변경 감지 (확실함)
3. 신규 ep는 search 의존이 불가피하지만, 카테고리별 다중 키워드 + 날짜 필터로 검출률 극대화

이 모듈은 직접 실행되지 않고 sync.py에서 import해서 사용됨.
"""

# ============================================================
# 카테고리별 신규 ep 검색 키워드 (도메인 다양화)
# ============================================================
# 사용자가 "X 시리즈에 추가했어"라고 명시하면 해당 카테고리 키워드를 모두 시도.
# 노션 search는 의미적 매칭이라 단일 키워드로는 놓칠 수 있음.

SEARCH_KEYWORDS = {
    # 인스타 시리즈 — 시리즈명별로 도메인 키워드
    "series_summer": [
        "여름", "계곡", "물놀이", "수영", "더위", "장마", "에어컨"
    ],
    "series_spring_autumn": [
        "봄", "가을", "철쭉", "단풍", "벚꽃", "단풍", "만추"
    ],
    "series_tips": [
        "꿀팁", "노하우", "방법", "텐트", "타프", "장비", "수납",
        "철수", "설치", "팁", "추천", "주의"
    ],
    "series_food": [
        "음식", "요리", "레시피", "캠핑밥", "구이", "찌개", "튀김",
        "라면", "바베큐", "야끼토리", "고기", "해산물"
    ],
    "series_gear": [
        "장비", "DJI", "오즈모", "포켓", "카메라", "악세사리",
        "테이블", "의자", "랜턴", "텐트", "침낭", "쿠커",
        "버너", "릴렉세이션", "도쿄크래프트"
    ],
    
    # 추천 음식 — 식재료/브랜드 다양화
    "foods": [
        "음식", "요리", "캠핑", "추천", "할인", "배송", "쿠팡",
        "컬리", "네이버", "야키토리", "꼬치", "고추", "튀김",
        "떡볶이", "만두", "짬뽕", "두릅"
    ],
    
    # 추천 템 — 캠핑 장비 카테고리
    "items": [
        "캠핑", "장비", "추천", "할인", "쿠팡", "네이버", "컬리",
        "텐트", "의자", "테이블", "랜턴", "화로", "박스", "가방",
        "악세사리", "포켓", "DJI", "오즈모", "카메라", "브라켓"
    ],
    
    # 캠핑장 — 지역명 + 환경
    "camps": [
        "캠핑장", "오토캠핑", "글램핑", "계곡", "바다", "숲",
        "경남", "경북", "강원", "전남", "전북", "충남", "충북",
        "경기", "산", "호수", "해변", "캠프", "야영장"
    ],
}


def find_new_pages_by_keywords(notion_search_fn, data_source_url, keyword_list, 
                                last_sync_date=None, page_size=25):
    """
    신규 ep 검출용 다중 키워드 검색.
    
    Args:
        notion_search_fn: Notion:notion-search 호출 함수 (Claude tool 래퍼)
        data_source_url: collection://... 형식
        keyword_list: 시도할 키워드 리스트
        last_sync_date: ISO 날짜 (이 이후 생성된 페이지만 필터)
        page_size: 회당 결과 수
    
    Returns:
        dict: {page_id: {title, timestamp}} 합집합
    """
    found = {}
    for kw in keyword_list:
        filters = {}
        if last_sync_date:
            filters["created_date_range"] = {"start_date": last_sync_date[:10]}
        
        result = notion_search_fn(
            query=kw,
            data_source_url=data_source_url,
            filters=filters,
            page_size=page_size,
            max_highlight_length=0
        )
        for r in result.get('results', []):
            pid = r['id']
            if pid not in found:
                found[pid] = {
                    "title": r['title'],
                    "timestamp": r.get('timestamp', '')
                }
    return found


def detect_changes(cached_page_ids, notion_results):
    """
    캐시 vs 노션 검색 결과 비교.
    
    Returns:
        new_ids: 노션엔 있고 캐시엔 없음 (신규 ep)
        deleted_ids: 캐시엔 있고 노션 검색에 없음 (삭제 가능성)
    """
    cached_set = set(cached_page_ids)
    notion_set = set(notion_results.keys())
    return {
        "new": notion_set - cached_set,
        "deleted_candidates": cached_set - notion_set
    }


# ============================================================
# 카테고리 → 데이터소스 URL 매핑
# ============================================================
DATA_SOURCES = {
    "series": "collection://d867d959-4c1b-487c-b7e0-ae7d82987520",
    "camps":  "collection://b5638d30-2613-4f25-aa76-88b3f65cf9e8",
    "foods":  "collection://fba27f16-acf1-46ff-ae39-17828322229c",
    "items":  "collection://2e74ca8b-8cdf-45ea-b78c-0b885a2b1ee6",
}


def get_keywords_for_category(category, hint_subseries=None):
    """
    카테고리별 검색 키워드 가져오기.
    
    series 카테고리는 hint_subseries로 하위 시리즈 키워드 우선 적용 가능.
    예: hint_subseries="장비소개" → series_gear 키워드 + 일반 series 키워드 모두
    """
    if category == "series":
        keywords = []
        # 모든 시리즈 키워드 통합
        for k in ["series_summer", "series_spring_autumn", "series_tips", 
                  "series_food", "series_gear"]:
            keywords.extend(SEARCH_KEYWORDS[k])
        # hint가 있으면 해당 시리즈 키워드를 앞에 둠 (우선순위)
        if hint_subseries:
            hint_map = {
                "여름에 가기 좋은 캠핑장": "series_summer",
                "봄·가을에 가기 좋은 캠핑장": "series_spring_autumn",
                "캠핑꿀팁": "series_tips",
                "또 해먹고 싶은 캠핑 음식": "series_food",
                "장비소개": "series_gear",
            }
            hint_key = hint_map.get(hint_subseries)
            if hint_key:
                priority = SEARCH_KEYWORDS[hint_key]
                # priority를 앞에 + 중복 제거
                seen = set()
                ordered = []
                for k in priority + keywords:
                    if k not in seen:
                        seen.add(k)
                        ordered.append(k)
                return ordered
        # 중복 제거
        return list(dict.fromkeys(keywords))
    return SEARCH_KEYWORDS.get(category, [])


def report(category, cached_count, found_count, new_ids, deleted_candidates):
    """진단 결과 리포트"""
    lines = []
    lines.append(f"=== {category} 차분 동기화 진단 ===")
    lines.append(f"  캐시된 page_id: {cached_count}개")
    lines.append(f"  노션 검색 발견: {found_count}개")
    if new_ids:
        lines.append(f"  ⚠️  신규 ep 발견: {len(new_ids)}개")
        for pid in new_ids:
            lines.append(f"     + {pid}")
    else:
        lines.append(f"  ✓ 신규 ep 없음")
    if deleted_candidates:
        lines.append(f"  ⚠️  삭제 후보 (검색에 안 잡힘): {len(deleted_candidates)}개")
        lines.append(f"     (검색 누락일 수도 있으니 fetch로 확인 필요)")
    return "\n".join(lines)
