#!/usr/bin/env python3
"""캠핑장 패치 JSON을 data/camps.json 에 적용 (Code 세션용 — admin '📥 패치 붙여넣기'와 같은 규칙).

  python tools/apply_camp_patch.py patch.json            # 객체 하나 또는 [객체, …]
  python tools/apply_camp_patch.py patch.json --merge guide,links   # 배열 필드 병합 (기본은 대체)
  python tools/apply_camp_patch.py patch.json --dry-run  # 바뀌는 필드만 출력

규칙: id → name 으로 대상 찾기 · 값 null 은 필드 삭제 · "visits": "+1" 은 증가 · info 는 항목별 덮어쓰기 ·
배열(guide links gear foods imgs extras …)은 기본 대체. 모르는 필드는 경고만 하고 저장. updated_at 갱신.
camps.json 은 admin 과 같은 형식(indent 2)으로 쓰고, 다른 캠핑장은 건드리지 않는다.
"""
import argparse
import datetime
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMPS = os.path.join(ROOT, 'data', 'camps.json')
KNOWN = {'name', 'region', 'extras', 'graega', 'url', 'imgs', 'main_img', 'img_pos', 'rating', 'visits', 'published',
         'checkin', 'checkout', 'address', 'notes', 'pick', 'videos', 'dm', 'dm_keyword', 'lat', 'lng',
         'hook', 'story', 'guide', 'layout_imgs', 'info', 'links', 'gear', 'foods', 'visit_log'}
LINK_TYPES = {'reserve', 'discount', 'event', 'homepage', 'naver_blog', 'etc'}


def merge_key(field, x):
    if field == 'guide':
        return json.dumps(x.get('zone'), ensure_ascii=False)
    if field == 'links':
        return json.dumps([x.get('type'), x.get('url')], ensure_ascii=False)
    return json.dumps(x, ensure_ascii=False, sort_keys=True)


def apply(camp, patch, merge):
    c = json.loads(json.dumps(camp, ensure_ascii=False))
    for k, v in patch.items():
        if v is None:
            c.pop(k, None)
        elif k == 'visits' and isinstance(v, str) and v.startswith('+'):
            c['visits'] = int(c.get('visits') or 0) + int(v[1:])
        elif k == 'info' and isinstance(c.get('info'), dict):
            info = dict(c['info'])
            for ik, iv in v.items():
                if iv is None:
                    info.pop(ik, None)
                else:
                    info[ik] = iv
            c['info'] = info
        elif k in merge and isinstance(c.get(k), list):
            arr = list(c[k])
            idx = {merge_key(k, x): i for i, x in enumerate(arr)}
            for x in v:
                key = merge_key(k, x)
                if key in idx:
                    arr[idx[key]] = x
                else:
                    arr.append(x)
            c[k] = arr
        else:
            c[k] = v
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('patch')
    ap.add_argument('--merge', default='', help='병합할 배열 필드 (콤마)')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    with open(args.patch, encoding='utf-8') as f:
        patches = json.load(f)
    patches = patches if isinstance(patches, list) else [patches]
    with open(CAMPS, encoding='utf-8') as f:
        camps = json.load(f)
    merge = {x.strip() for x in args.merge.split(',') if x.strip()}
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    names = []
    for p in patches:
        p = dict(p)
        cid, name = p.pop('id', None), p.get('name')
        idx = next((i for i, c in enumerate(camps) if (cid and c['id'] == cid) or (not cid and c['name'] == name)), -1)
        if idx < 0:
            sys.exit(f'✖ 대상 없음: {cid or name}')
        for k in ('created_at', 'updated_at'):
            p.pop(k, None)
        for k in p:
            if k not in KNOWN:
                print(f'⚠ 모르는 필드 {k} — 그대로 저장')
        for k in ('guide', 'links', 'gear', 'foods', 'imgs', 'extras', 'layout_imgs', 'videos', 'visit_log'):
            if p.get(k) is not None and not isinstance(p[k], list):
                sys.exit(f'✖ {k} 는 배열이어야 함')
        for l in p.get('links') or []:
            if not l.get('url'):
                sys.exit('✖ links 에 url 없는 항목')
            if l.get('type') not in LINK_TYPES:
                print(f"⚠ links type {l.get('type')} → etc 로 표시")
        old = camps[idx]
        new = apply(old, p, merge)
        changed = [k for k in p if old.get(k) != new.get(k)]
        print(f"{old['name']} ({old['id']}): {', '.join(changed) or '변경 없음'}")
        if changed:
            new['updated_at'] = now
            camps[idx] = new
            names.append(old['name'])
    if args.dry_run or not names:
        return
    with open(CAMPS, 'w', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(camps, ensure_ascii=False, indent=2) + '\n')
    print('적용:', ', '.join(names))


if __name__ == '__main__':
    main()
