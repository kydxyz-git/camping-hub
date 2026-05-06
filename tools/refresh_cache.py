"""
sync_data.json의 _metadata.cached_pages를 자동으로 재계산.

매 동기화 직후 호출하여 cached_pages가 항상 최신 상태가 되도록 보장.
신규 ep 추가 후 이 함수를 호출 안 하면 다음 동기화 때 그 ep를 다시 신규로 잘못 인식할 수 있음.

사용법:
    from refresh_cache import refresh_cached_pages
    refresh_cached_pages('/home/claude/sync_data.json')
"""

import json
from datetime import datetime, timezone


def refresh_cached_pages(sync_data_path):
    """sync_data.json의 cached_pages를 현재 데이터 기반으로 재계산"""
    with open(sync_data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cached = {
        "series": [],
        "camps": [],
        "foods": [],
        "items": []
    }
    
    for s in data.get('series', []):
        for ep in s.get('eps', []):
            if ep.get('page_id'):
                cached['series'].append({
                    "page_id": ep['page_id'],
                    "title": ep.get('title', ''),
                    "series_name": s.get('name', '')
                })
    
    for c in data.get('camps', []):
        if c.get('page_id'):
            cached['camps'].append({
                "page_id": c['page_id'],
                "name": c.get('name', '')
            })
    
    for f in data.get('foods', []):
        if f.get('page_id'):
            cached['foods'].append({
                "page_id": f['page_id'],
                "name": f.get('name', '')[:30]
            })
    
    for i in data.get('items', []):
        if i.get('page_id'):
            cached['items'].append({
                "page_id": i['page_id'],
                "name": i.get('name', '')[:30]
            })
    
    if '_metadata' not in data:
        data['_metadata'] = {}
    data['_metadata']['cached_pages'] = cached
    data['_metadata']['cached_pages_updated'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    with open(sync_data_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return {
        "series": len(cached['series']),
        "camps": len(cached['camps']),
        "foods": len(cached['foods']),
        "items": len(cached['items']),
        "total": sum(len(v) for v in cached.values())
    }


if __name__ == '__main__':
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/sync_data.json'
    result = refresh_cached_pages(path)
    print(f"✓ cached_pages 갱신됨: {path}")
    for k, v in result.items():
        if k != 'total':
            print(f"  {k}: {v}개")
    print(f"  합계: {result['total']}개")
