#!/usr/bin/env python3
"""검색엔진용 정적 페이지 생성기.

data/*.json 을 읽어 캠핑장·캠핑용품·먹거리마다 내용이 들어 있는 HTML 페이지를 만든다.
  camps/{이름}/index.html · gear/{이름}/index.html · foods/{이름}/index.html
  camps/index.html · gear/index.html · foods/index.html  (목록)
  index.html 의 PRERENDER 블록 (자바스크립트 없이도 보이는 목록)
  sitemap.xml (전체 재생성)

사람이 페이지를 열면 자바스크립트로 실제 사이트 화면으로 바로 이동한다.
  캠핑장 → /camp.html?id=…   용품 → /#items/{id}   먹거리 → /#foods/{id}

GitHub Actions(.github/workflows/build-pages.yml)가 data/ 변경 시 자동 실행한다.
로컬 실행: python3 tools/build_pages.py
"""
import datetime
import html
import json
import os
import re
import shutil
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://kydz.kr'
BRAND = '공대남자의 캠핑이야기'
OG_DEFAULT = SITE + '/images/refs/og-1278df5b.jpg'
KST = datetime.timezone(datetime.timedelta(hours=9))
OUT_DIRS = ['camps', 'gear', 'foods']
MARK_START = '<!-- PRERENDER:START (tools/build_pages.py 자동 생성 — 직접 수정 금지) -->'
MARK_END = '<!-- PRERENDER:END -->'


def load(name):
    with open(os.path.join(ROOT, 'data', name + '.json'), encoding='utf-8') as f:
        return json.load(f)


def pub(rows):
    return [x for x in rows if x.get('published', True) is not False]


def e(s):
    return html.escape(str(s or ''), quote=True)


def slugify(name):
    s = re.sub(r'[\[\]()&+/\\?#%:;,."\'<>|*!~`^{}=@$]', ' ', name)
    s = re.sub(r'\s+', '-', s.strip())
    s = re.sub(r'-+', '-', s).strip('-')
    return s or 'item'


def assign_slugs(rows):
    used, out = set(), {}
    for x in rows:
        s = slugify(x['name'])
        if s in used:
            s = f"{s}-{x['id'][-4:]}"
        used.add(s)
        out[x['id']] = s
    return out


def url_of(section, slug):
    return f"{SITE}/{section}/{quote(slug)}/"


def abs_img(p):
    if not p:
        return ''
    if p.startswith('http'):
        return p
    return SITE + '/' + p.lstrip('./')


def kst_date(iso):
    try:
        d = datetime.datetime.fromisoformat(str(iso).replace('Z', '+00:00'))
        return d.astimezone(KST).strftime('%Y-%m-%d')
    except Exception:
        return datetime.datetime.now(KST).strftime('%Y-%m-%d')


def platform_of(url):
    u = (url or '').lower()
    if 'naver' in u:
        return '네이버'
    if 'camfit' in u:
        return '캠핏'
    if 'thankqcamping' in u or 'camperstory' in u:
        return '땡큐캠핑'
    return '예약 사이트' if u else ''


def clean_ig(url):
    """인스타 링크: /reel/·/tv/ → /p/, 추적 파라미터 제거 (사이트 정규화 규칙과 동일)"""
    m = re.match(r'https?://(www\.)?instagram\.com/(reel|reels|tv|p)/([^/?#]+)', url or '')
    return f'https://www.instagram.com/p/{m.group(3)}/' if m else (url or '')


def josa(word, pair):
    """받침 유무로 조사 선택 (pair: '은는', '이가', '을를', '과와')"""
    ch = (word or ' ')[-1]
    code = ord(ch) - 0xAC00
    has = 0 <= code <= 11171 and code % 28 != 0
    return pair[0] if has else pair[1]


# ─── 공통 레이아웃 ────────────────────────────────────────────────────
CSS = """
:root{--paper:#FBFBF8;--ink:#15181A;--stone:#6F756E;--line:#E4E4DE;--stamp:#FFE873}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--paper);color:var(--ink);font-family:'Pretendard Variable','SUIT Variable',-apple-system,system-ui,sans-serif;line-height:1.7;-webkit-font-smoothing:antialiased}
a{color:inherit}
.wrap{max-width:760px;margin:0 auto;padding:28px 20px 72px}
.top{display:flex;justify-content:space-between;align-items:center;font-size:14px;margin-bottom:28px}
.top a{text-decoration:none;font-weight:800}
.crumb{color:var(--stone);font-size:13px;margin-bottom:8px}
.crumb a{text-decoration:none}
h1{font-size:30px;line-height:1.3;letter-spacing:-.02em;margin-bottom:12px}
h2{font-size:18px;margin:32px 0 10px;padding-bottom:6px;border-bottom:1px solid var(--line)}
.lead{font-size:16px;margin-bottom:18px}
.go{display:inline-block;margin:6px 0 4px;padding:11px 18px;border-radius:999px;background:var(--ink);color:#fff;text-decoration:none;font-weight:700;font-size:14px}
dl{display:grid;grid-template-columns:96px 1fr;gap:6px 12px;font-size:15px}
dt{color:var(--stone)}
ul{padding-left:20px}
li{margin:3px 0}
.tags span{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:2px 10px;margin:0 6px 6px 0;font-size:13px}
.pics{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin-top:6px}
.pics img{width:100%;aspect-ratio:4/5;object-fit:cover;border-radius:6px;background:#EDEDE7}
.thumb{width:100%;max-width:360px;aspect-ratio:1/1;object-fit:contain;background:#fff;border:1px solid var(--line);border-radius:8px;margin:8px 0 4px}
.cols{columns:2;column-gap:24px}
.cols li{break-inside:avoid}
.foot{margin-top:48px;padding-top:16px;border-top:1px solid var(--line);font-size:13px;color:var(--stone)}
.foot a{margin-right:12px}
"""


def page(*, title, desc, canonical, og_image, redirect, body, jsonld=None, og_type='article'):
    ld = ''
    for obj in (jsonld or []):
        ld += '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>\n'
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canonical)}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(canonical)}">
<meta property="og:image" content="{e(og_image)}">
<meta property="og:locale" content="ko_KR">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{e(og_image)}">
<link rel="icon" href="{SITE}/favicon.ico">
<script>location.replace({json.dumps(redirect)});</script>
{ld}<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<div class="top"><a href="{SITE}/">{BRAND}</a><span>@kyd_zm</span></div>
{body}
<div class="foot">
<a href="{SITE}/">홈</a><a href="{SITE}/camps/">다녀온 캠핑장</a><a href="{SITE}/gear/">캠핑용품</a><a href="{SITE}/foods/">먹거리</a>
<p>5년차 부부캠퍼 공대남자가 직접 다녀오고 써 본 것만 기록합니다.</p>
</div>
</div>
</body>
</html>
"""


def breadcrumb(items):
    return {
        '@context': 'https://schema.org', '@type': 'BreadcrumbList',
        'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u}
                            for i, (n, u) in enumerate(items)],
    }


# ─── 캠핑장 ──────────────────────────────────────────────────────────
def camp_page(c, slug, by_region, slugs, eps_by_camp):
    name, region = c['name'], c.get('region') or ''
    visits = int(c.get('visits') or 0)
    addr = c.get('address') or ''
    notes = [n.strip(' -·•') for n in (c.get('notes') or '').split('\n') if n.strip()]
    extras = c.get('extras') or []
    imgs = [x for x in ([c.get('main_img')] + (c.get('imgs') or [])) if x]
    imgs = list(dict.fromkeys(imgs))
    plat = '그래가 파트너스' if c.get('graega') else platform_of(c.get('url'))

    where = addr or (region + ' 지역' if region else '')
    lead = f"{name}{josa(name, '은는')} {where}에 있는 캠핑장입니다." if where else f"{name} 방문 기록입니다."
    if visits > 0:
        lead += f" 공대남자가 직접 {visits}번 다녀온 곳입니다."
    if c.get('pick'):
        lead += ' 공대남자가 추천하는 캠핑장입니다.'

    desc_bits = [f"{name}"]
    if region:
        desc_bits.append(f"{region}")
    if visits:
        desc_bits.append(f"{visits}회 방문")
    if extras:
        desc_bits.append('·'.join(extras[:4]))
    desc = ' | '.join(desc_bits) + '. ' + (notes[0] if notes else '5년차 부부캠퍼가 직접 다녀온 캠핑장 기록.')
    desc = desc[:150]

    rows = []
    if region:
        rows.append(('지역', region))
    if addr:
        rows.append(('주소', addr))
    if c.get('checkin') or c.get('checkout'):
        rows.append(('입실 · 퇴실', f"{c.get('checkin') or '-'} / {c.get('checkout') or '-'}"))
    if visits:
        rows.append(('방문 횟수', f"{visits}회"))
    if plat:
        rows.append(('예약', plat))
    dl = ''.join(f'<dt>{e(k)}</dt><dd>{e(v)}</dd>' for k, v in rows)

    body = [f'<p class="crumb"><a href="{SITE}/camps/">다녀온 캠핑장</a> · {e(region)}</p>',
            f'<h1>{e(name)}</h1>', f'<p class="lead">{e(lead)}</p>',
            f'<a class="go" href="{e(SITE + "/camp.html?id=" + c["id"])}">캠핑장 기록 보기</a>']
    if dl:
        body.append(f'<h2>기본 정보</h2><dl>{dl}</dl>')
    if extras:
        body.append('<h2>특징</h2><p class="tags">' + ''.join(f'<span>{e(t)}</span>' for t in extras) + '</p>')
    if notes:
        body.append('<h2>다녀와서 남긴 메모</h2><ul>' + ''.join(f'<li>{e(n)}</li>' for n in notes) + '</ul>')
    vids = [(v.get('title') or '영상', clean_ig(v.get('url'))) for v in (c.get('videos') or []) if v.get('url')]
    vids += [(t, clean_ig(u)) for t, u in eps_by_camp.get(c['id'], [])]
    vids = list(dict.fromkeys(vids))
    if vids:
        body.append('<h2>관련 영상</h2><ul>' + ''.join(
            f'<li><a href="{e(u)}" rel="nofollow noopener" target="_blank">{e(t)}</a></li>' for t, u in vids) + '</ul>')
    if imgs:
        body.append('<h2>사진</h2><div class="pics">' + ''.join(
            f'<img src="{e(abs_img(p))}" alt="{e(name)} 사진 {i + 1}" loading="lazy">' for i, p in enumerate(imgs[:4])) + '</div>')
    near = [x for x in by_region.get(region, []) if x['id'] != c['id']][:12]
    if near:
        body.append(f'<h2>{e(region)}의 다른 캠핑장</h2><ul class="cols">' + ''.join(
            f'<li><a href="{url_of("camps", slugs[x["id"]])}">{e(x["name"])}</a></li>' for x in near) + '</ul>')

    canonical = url_of('camps', slug)
    ld = {'@context': 'https://schema.org', '@type': 'Campground', 'name': name, 'url': canonical,
          'description': desc}
    if addr:
        ld['address'] = {'@type': 'PostalAddress', 'streetAddress': addr, 'addressRegion': region, 'addressCountry': 'KR'}
    if c.get('lat') and c.get('lng'):
        ld['geo'] = {'@type': 'GeoCoordinates', 'latitude': c['lat'], 'longitude': c['lng']}
    if imgs:
        ld['image'] = [abs_img(p) for p in imgs[:4]]
    return page(title=f"{name} 후기·정보 | {BRAND}", desc=desc, canonical=canonical,
                og_image=abs_img(imgs[0]) if imgs else OG_DEFAULT,
                redirect=f"/camp.html?id={c['id']}", body='\n'.join(body),
                jsonld=[ld, breadcrumb([('홈', SITE + '/'), ('다녀온 캠핑장', SITE + '/camps/'), (name, canonical)])])


# ─── 캠핑용품 · 먹거리 ───────────────────────────────────────────────
def product_page(p, slug, kind, cat_label, siblings, slugs):
    name = p['name']
    is_gear = kind == 'gear'
    section_name = '캠핑용품' if is_gear else '먹거리'
    if is_gear:
        lead = f"공대남자가 캠핑에서 실제로 쓰는 {cat_label} 장비, {name}입니다."
        desc = f"{name} — 5년차 부부캠퍼 공대남자가 실제로 챙겨 다니는 {cat_label} 캠핑용품."
    else:
        lead = f"캠핑 가서 먹어 본 {name}입니다. 다시 살 만했던 것만 기록합니다."
        desc = f"{name} — 5년차 부부캠퍼 공대남자가 캠핑에서 먹어 보고 다시 살 만했던 먹거리."
    if p.get('pick'):
        lead += ' 공대남자 추천 제품입니다.'
    if p.get('desc'):
        desc = (desc + ' ' + p['desc'])[:150]

    rows = [('분류', cat_label)] if cat_label else []
    if p.get('source') and p.get('url'):
        rows.append(('판매처', p['source']))
    dl = ''.join(f'<dt>{e(k)}</dt><dd>{e(v)}</dd>' for k, v in rows)
    target = f"/?ref=search#{'items' if is_gear else 'foods'}/{p['id']}"
    hub = 'gear' if is_gear else 'foods'
    body = [f'<p class="crumb"><a href="{SITE}/{hub}/">{section_name}</a>{(" · " + e(cat_label)) if cat_label else ""}</p>',
            f'<h1>{e(name)}</h1>']
    if p.get('thumb'):
        body.append(f'<img class="thumb" src="{e(abs_img(p["thumb"]))}" alt="{e(name)}">')
    body.append(f'<p class="lead">{e(lead)}</p>')
    if p.get('desc'):
        body.append(f'<p>{e(p["desc"])}</p>')
    body.append(f'<a class="go" href="{e(SITE + target)}">공대남자의 캠핑이야기에서 보기</a>')
    if dl:
        body.append(f'<h2>정보</h2><dl>{dl}</dl>')
    if p.get('video'):
        body.append(f'<h2>관련 영상</h2><p><a href="{e(clean_ig(p["video"]))}" rel="nofollow noopener" target="_blank">인스타그램에서 보기</a></p>')
    sib = [x for x in siblings if x['id'] != p['id']][:12]
    if sib:
        head = f'{cat_label} 다른 용품' if is_gear else '다른 먹거리'
        body.append(f'<h2>{e(head)}</h2><ul class="cols">' + ''.join(
            f'<li><a href="{url_of(hub, slugs[x["id"]])}">{e(x["name"])}</a></li>' for x in sib) + '</ul>')

    canonical = url_of(hub, slug)
    ld = {'@context': 'https://schema.org', '@type': 'Product', 'name': name, 'url': canonical, 'description': desc}
    if p.get('thumb'):
        ld['image'] = abs_img(p['thumb'])
    if cat_label:
        ld['category'] = cat_label
    return page(title=f"{name} | {BRAND}", desc=desc, canonical=canonical,
                og_image=abs_img(p.get('thumb')) or OG_DEFAULT, redirect=target, body='\n'.join(body),
                jsonld=[ld, breadcrumb([('홈', SITE + '/'), (section_name, SITE + f'/{hub}/'), (name, canonical)])])


# ─── 목록 페이지 ─────────────────────────────────────────────────────
def hub_page(*, hub, title, h1, lead, groups, redirect, slugs, extra=lambda x: ''):
    body = [f'<h1>{e(h1)}</h1>', f'<p class="lead">{e(lead)}</p>',
            f'<a class="go" href="{SITE}/{redirect.lstrip("/")}">공대남자의 캠핑이야기에서 보기</a>']
    for label, rows in groups:
        if not rows:
            continue
        body.append(f'<h2>{e(label)}</h2><ul class="cols">' + ''.join(
            f'<li><a href="{url_of(hub, slugs[x["id"]])}">{e(x["name"])}</a>{extra(x)}</li>' for x in rows) + '</ul>')
    canonical = f'{SITE}/{hub}/'
    return page(title=f"{title} | {BRAND}", desc=lead[:150], canonical=canonical, og_image=OG_DEFAULT,
                redirect=redirect, body='\n'.join(body), og_type='website',
                jsonld=[breadcrumb([('홈', SITE + '/'), (h1, canonical)])])


def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def main():
    camps = pub(load('camps'))
    items = pub(load('items'))
    foods = pub(load('foods'))
    series = pub(load('series'))
    cfg = load('config')
    cats = cfg.get('itemCats') or [{'key': 'camp', 'label': '캠핑용품'}]
    cat_label = {c['key']: c['label'] for c in cats}
    keys = [c['key'] for c in cats]

    def cat_of(x):
        k = x.get('cat') or keys[0]
        return k if k in keys else keys[0]

    eps_by_camp = {}
    for s in series:
        for ep in pub(s.get('eps') or []):
            if ep.get('camp_id') and ep.get('url'):
                title = re.sub(r'^EP\.\d+\s*', '', ep.get('title') or '', flags=re.I) or s.get('name')
                eps_by_camp.setdefault(ep['camp_id'], []).append((f"{s.get('name')} · {title}", ep['url']))

    # 정렬: 캠핑장은 방문 많은 순, 나머지는 이름순
    camps.sort(key=lambda c: (-(int(c.get('visits') or 0)), c['name']))
    items.sort(key=lambda x: x['name'])
    foods.sort(key=lambda x: x['name'])
    cs, gs, fs = assign_slugs(camps), assign_slugs(items), assign_slugs(foods)

    # 이전 생성물 정리 후 다시 생성
    for d in OUT_DIRS:
        shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)

    by_region = {}
    for c in camps:
        by_region.setdefault(c.get('region') or '기타', []).append(c)
    for c in camps:
        write(f"camps/{cs[c['id']]}/index.html", camp_page(c, cs[c['id']], by_region, cs, eps_by_camp))
    # camp.html이 주소창을 정적 페이지 주소로 바꿀 때 쓰는 id → 이름 매핑
    write('camps/slugs.json', json.dumps(cs, ensure_ascii=False, separators=(',', ':')) + '\n')

    by_cat = {k: [x for x in items if cat_of(x) == k] for k in keys}
    for x in items:
        write(f"gear/{gs[x['id']]}/index.html",
              product_page(x, gs[x['id']], 'gear', cat_label.get(cat_of(x), ''), by_cat[cat_of(x)], gs))
    for x in foods:
        write(f"foods/{fs[x['id']]}/index.html", product_page(x, fs[x['id']], 'foods', '', foods, fs))

    region_order = ['경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']
    region_order += [r for r in by_region if r not in region_order]
    write('camps/index.html', hub_page(
        hub='camps', title='다녀온 캠핑장 전체 목록', h1='다녀온 캠핑장',
        lead=f'5년차 부부캠퍼 공대남자가 직접 다녀온 캠핑장 {len(camps)}곳의 기록입니다. 지역별로 정리했습니다.',
        groups=[(r, by_region.get(r, [])) for r in region_order], redirect='/#camps', slugs=cs,
        extra=lambda c: f' <small>({int(c.get("visits") or 0)}회)</small>' if c.get('visits') else ''))
    write('gear/index.html', hub_page(
        hub='gear', title='캠핑용품 전체 목록', h1='캠핑용품',
        lead=f'공대남자가 지금 실제로 챙겨 다니는 캠핑용품 {len(items)}개입니다. 분류별로 정리했습니다.',
        groups=[(cat_label[k], by_cat[k]) for k in keys], redirect='/#items', slugs=gs))
    write('foods/index.html', hub_page(
        hub='foods', title='캠핑 먹거리 전체 목록', h1='먹거리',
        lead=f'캠핑 가서 먹어 본 밀키트와 간편식 중 다시 살 만했던 {len(foods)}가지입니다.',
        groups=[('먹거리', foods)], redirect='/#foods', slugs=fs))

    # index.html PRERENDER 블록 (자바스크립트가 돌면 바로 제거됨)
    def links(hub, rows, slugs):
        return ' · '.join(f'<a href="{url_of(hub, slugs[x["id"]])}">{e(x["name"])}</a>' for x in rows)
    pre = (f'{MARK_START}\n<section id="prerender" aria-label="사이트 전체 목록">'
           f'<script>document.getElementById("prerender").remove()</script>'
           f'<h2><a href="{SITE}/camps/">다녀온 캠핑장 {len(camps)}곳</a></h2><p>{links("camps", camps, cs)}</p>'
           f'<h2><a href="{SITE}/gear/">캠핑용품 {len(items)}개</a></h2><p>{links("gear", items, gs)}</p>'
           f'<h2><a href="{SITE}/foods/">먹거리 {len(foods)}가지</a></h2><p>{links("foods", foods, fs)}</p>'
           f'</section>\n{MARK_END}')
    idx_path = os.path.join(ROOT, 'index.html')
    with open(idx_path, encoding='utf-8') as f:
        idx = f.read()
    if MARK_START in idx:
        idx = idx[:idx.index(MARK_START)] + pre + idx[idx.index(MARK_END) + len(MARK_END):]
    else:
        idx = idx.replace('</body>', pre + '\n</body>', 1)
    with open(idx_path, 'w', encoding='utf-8') as f:
        f.write(idx)

    # sitemap.xml
    latest = max([kst_date(x.get('updated_at')) for x in camps + items + foods] or [kst_date(None)])
    urls = [(SITE + '/', latest, '1.0'), (SITE + '/camps/', latest, '0.9'),
            (SITE + '/gear/', latest, '0.8'), (SITE + '/foods/', latest, '0.7')]
    urls += [(url_of('camps', cs[c['id']]), kst_date(c.get('updated_at')), '0.8') for c in camps]
    urls += [(url_of('gear', gs[x['id']]), kst_date(x.get('updated_at')), '0.6') for x in items]
    urls += [(url_of('foods', fs[x['id']]), kst_date(x.get('updated_at')), '0.5') for x in foods]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, mod, pr in urls:
        sm.append(f'  <url><loc>{e(loc)}</loc><lastmod>{mod}</lastmod><priority>{pr}</priority></url>')
    sm.append('</urlset>')
    write('sitemap.xml', '\n'.join(sm) + '\n')
    print(f'camps {len(camps)} · gear {len(items)} · foods {len(foods)} · sitemap {len(urls)} URLs')


if __name__ == '__main__':
    main()
