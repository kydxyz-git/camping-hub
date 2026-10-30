#!/usr/bin/env python3
"""검색엔진용 정적 페이지 생성기.

data/*.json 을 읽어 캠핑장·캠핑용품·먹거리마다 내용이 들어 있는 HTML 페이지를 만든다.
  camps/{이름}/index.html · gear/{이름}/index.html · foods/{이름}/index.html
  camps/index.html · gear/index.html · foods/index.html  (목록)
  index.html 의 PRERENDER 블록 (자바스크립트 없이도 보이는 목록)
  sitemap.xml (전체 재생성)

페이지는 그 자체로 보는 페이지다 (자동 이동 없음 — 261022: 구글이 자바스크립트 이동을 '리디렉션'으로 보고
색인에서 빼서 없앰). 큰 버튼·아래 고정 버튼으로 실제 사이트 화면에 들어간다.
  캠핑장 → /camp.html?id=…   용품 → /?ref=search#items/{id}   먹거리 → /?ref=search#foods/{id}
방문은 통계 Worker에 /search/{camps|gear|foods}/{id} 로 기록 (어디서 왔는지 — 구글·네이버 등 — 와 함께).
캠핑장 페이지는 인스타 게시물의 풀 버전(261030): 훅·릴스·본문·존별 가이드·정보·링크·장비/먹거리 (docs/camp-patch.md).

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
STATS_URL = 'https://kyd-stats.kydxyz.workers.dev/log'
IG = 'https://www.instagram.com/kyd_zm/'
# '공대남자' 검색 시 한 사람으로 묶이도록 모든 정적 페이지에 같은 인물 정보(@id는 메인 index.html과 동일)
PERSON = {'@context': 'https://schema.org', '@type': 'Person', '@id': SITE + '/#person', 'name': '공대남자',
          'alternateName': 'kyd_zm', 'url': SITE + '/',
          'sameAs': [IG, 'https://www.facebook.com/profile.php?id=61588881720150', 'https://naver.me/5ajsIHzm']}
# 배지 색 (CLAUDE.md UI 규칙과 같게)
SELLER_COLOR = {'쿠팡': '#ee2c4d', '컬리': '#5f0080', '네이버': '#03C75A', '알리': '#FF4747', '테무': '#FF6A00'}
BOOK_COLOR = {'그래가 파트너스': '#1a1a1a', '네이버': '#03C75A', '캠핏': '#2D8F4C', '땡큐캠핑': '#FF6B2C'}
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
    if 'graega' in u:
        return '그래가 파트너스'
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
:root{--paper:#FBFBF8;--ink:#15181A;--stone:#6F756E;--line:#E4E4DE;--stamp:#FFE873;--card:#fff}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--paper);color:var(--ink);font-family:'Pretendard Variable','SUIT Variable',-apple-system,system-ui,sans-serif;line-height:1.7;-webkit-font-smoothing:antialiased}
a{color:inherit}
.wrap{max-width:760px;margin:0 auto;padding:20px 16px 110px}
.top{display:flex;justify-content:space-between;align-items:center;font-size:14px;margin-bottom:20px}
.top a{text-decoration:none;font-weight:800}
.top .ig{font-weight:600;color:var(--stone)}
.crumb{color:var(--stone);font-size:13px;margin-bottom:6px}
.crumb a{text-decoration:none}
h1{font-size:28px;line-height:1.3;letter-spacing:-.02em;margin-bottom:10px}
h2{font-size:17px;margin:30px 0 10px;padding-bottom:6px;border-bottom:1px solid var(--line)}
.lead{font-size:16px;margin-bottom:16px}
.hero{position:relative;margin:0 0 16px;border-radius:14px;overflow:hidden;background:#EDEDE7}
.hero img{display:block;width:100%;aspect-ratio:4/3;object-fit:cover}
.hero.sq{background:#fff;border:1px solid var(--line);max-width:420px}
.hero.sq img{aspect-ratio:1/1;object-fit:contain}
.badges{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 12px}
.badge{display:inline-block;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:700;color:#fff;background:#9e9e9e}
.badge.line{background:transparent;color:var(--ink);border:1px solid var(--line);font-weight:600}
.badge.pick{background:var(--stamp);color:var(--ink)}
.go{display:block;text-align:center;margin:8px 0 4px;padding:14px 18px;border-radius:14px;background:var(--ink);color:#fff;text-decoration:none;font-weight:800;font-size:15px}
.sticky{position:fixed;left:0;right:0;bottom:0;padding:10px 16px calc(10px + env(safe-area-inset-bottom));background:linear-gradient(transparent,var(--paper) 30%)}
.sticky a{display:block;max-width:728px;margin:0 auto;text-align:center;padding:14px 18px;border-radius:14px;background:var(--ink);color:#fff;text-decoration:none;font-weight:800;font-size:15px;box-shadow:0 6px 20px rgba(0,0,0,.18)}
dl{display:grid;grid-template-columns:96px 1fr;gap:6px 12px;font-size:15px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
dt{color:var(--stone)}
ul{padding-left:20px}
li{margin:3px 0}
.tags span{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:2px 10px;margin:0 6px 6px 0;font-size:13px;background:var(--card)}
.pics{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin-top:6px}
.pics img{width:100%;aspect-ratio:4/5;object-fit:cover;border-radius:8px;background:#EDEDE7}
.cols{columns:2;column-gap:24px}
.cols li{break-inside:avoid}
.foot{margin-top:44px;padding-top:16px;border-top:1px solid var(--line);font-size:13px;color:var(--stone)}
.foot a{margin-right:12px}
.hook{font-size:19px;font-weight:800;line-height:1.45;letter-spacing:-.01em;margin-bottom:16px}
.story p{font-size:16px;margin:0 0 14px}
.reels{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.reels a{text-decoration:none;display:block}
.reels .th{display:block;aspect-ratio:4/5;border-radius:8px;overflow:hidden;background:#EDEDE7}
.reels .th img{width:100%;height:100%;object-fit:cover;display:block}
.reels b{display:block;font-size:13px;line-height:1.4;margin-top:6px}
.guide{list-style:none;padding:0;display:grid;gap:8px}
.guide li{margin:0;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px}
.guide li.pick{border-color:#E8CF3A;background:#FFFBE3}
.guide b{display:block;font-size:15px}
.layout{display:block;width:100%;height:auto;border-radius:10px;margin-top:10px;border:1px solid var(--line)}
.src{font-size:12px;color:var(--stone);margin-top:6px}
.btns{display:grid;gap:8px}
.btn{display:block;text-align:center;padding:13px 16px;border-radius:12px;background:var(--ink);color:#fff;text-decoration:none;font-weight:800;font-size:15px}
.btn.sub{background:var(--card);color:var(--ink);border:1px solid var(--line);font-weight:700}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.cards a{text-decoration:none;display:block}
.cards .th{position:relative;display:block;aspect-ratio:1/1;border-radius:10px;overflow:hidden;background:#fff;border:1px solid var(--line)}
.cards .th img{width:100%;height:100%;object-fit:contain;display:block}
.cards .th .badge{position:absolute;right:6px;bottom:6px;font-size:10px;padding:2px 7px}
.cards b{display:block;font-size:13px;font-weight:600;line-height:1.4;margin-top:6px}
.dm{margin-top:30px;padding:14px 16px;border-radius:12px;background:var(--card);border:1px solid var(--line);font-size:15px}
@media (min-width:720px){h1{font-size:32px}.go{display:inline-block;padding:13px 28px}.cards{grid-template-columns:repeat(4,1fr)}}
"""


def track_js(path, title):
    """방문 기록: 바깥(구글·네이버 등)에서 왔으면 어디서 왔는지, 검색어가 주소에 실려 오면 그것도 (네이버 일부)"""
    return ("<script>(function(){try{var r=document.referrer,h='',q='';try{var u=new URL(r);h=u.hostname.toLowerCase();"
            "q=u.searchParams.get('query')||u.searchParams.get('q')||''}catch(e){}"
            "var s=!r?'direct':/kydz\\.kr$/.test(h)?'':/google/.test(h)?'구글':/naver/.test(h)?'네이버':/daum|kakao/.test(h)?'다음/카카오':"
            "/bing/.test(h)?'빙':/instagram|ig\\.me/.test(h)?'인스타그램':/threads/.test(h)?'스레드':h;"
            "var ua=navigator.userAgent||'',d=/iPad|Tablet/i.test(ua)?'tablet':/Mobile|Android|iPhone|iPod|Phone/i.test(ua)?'mobile':'desktop';"
            f"var o={{type:'pageview',path:{json.dumps(path)},title:{json.dumps(title, ensure_ascii=False)},device:d,"
            "lang:String(navigator.language||'').slice(0,2).toLowerCase()};if(s)o.referrer=s;if(q)o.context=('검색어 '+q).slice(0,100);"
            "var b=JSON.stringify(o);if(!(navigator.sendBeacon&&navigator.sendBeacon("
            f"{json.dumps(STATS_URL)},new Blob([b],{{type:'text/plain;charset=UTF-8'}}))))fetch({json.dumps(STATS_URL)},"
            "{method:'POST',body:b,keepalive:true,mode:'cors',credentials:'omit',headers:{'Content-Type':'text/plain;charset=UTF-8'}})}catch(e){}})();</script>")


def page(*, title, desc, canonical, og_image, cta, track, body, jsonld=None, og_type='article'):
    """cta: (버튼 글자, 사이트 안 주소) — 본문 안 큰 버튼 + 화면 아래 고정 버튼. track: (통계 경로, 이름)"""
    ld = ''
    for obj in [PERSON] + list(jsonld or []):
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
{ld}<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<div class="top"><a href="{SITE}/">← {BRAND}</a><a class="ig" href="{IG}" rel="noopener" target="_blank">@kyd_zm</a></div>
{body}
<div class="foot">
<a href="{SITE}/">홈</a><a href="{SITE}/camps/">다녀온 캠핑장</a><a href="{SITE}/gear/">캠핑용품</a><a href="{SITE}/foods/">먹거리</a>
<p>5년차 부부캠퍼 공대남자가 직접 다녀오고 써 본 것만 기록합니다.</p>
</div>
</div>
<div class="sticky"><a href="{e(SITE + cta[1])}">{e(cta[0])} →</a></div>
{track_js(*track)}
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
LINK_TYPES = ['reserve', 'discount', 'event', 'homepage', 'naver_blog', 'etc']
LINK_LABEL = {'reserve': '예약하기', 'discount': '할인 받기', 'event': '이벤트', 'homepage': '캠핑장 홈페이지',
              'naver_blog': '네이버 블로그 후기', 'etc': '링크'}


def story_paras(story):
    return [p.strip() for p in re.split(r'\n\s*\n', str(story or '')) if p.strip()]


def camp_links(c, plat):
    """links[] 를 type 순서로. 예약 버튼은 예약처 배지 색. links 에 예약이 없으면 기존 url 로 예약 버튼"""
    out = []
    for l in (c.get('links') or []):
        if not isinstance(l, dict) or not (l.get('url') or '').strip():
            continue
        t = l.get('type') if l.get('type') in LINK_TYPES else 'etc'
        color = ''
        if t == 'reserve':
            p = platform_of(l['url'])
            color = BOOK_COLOR.get(plat if p == '예약 사이트' else p, '')
        out.append((t, (l.get('label') or '').strip() or LINK_LABEL[t], l['url'].strip(), color))
    if c.get('url') and not any(t == 'reserve' for t, *_ in out):
        out.append(('reserve', '예약 페이지 열기', c['url'], BOOK_COLOR.get(plat, '')))
    out.sort(key=lambda x: LINK_TYPES.index(x[0]))
    return out


def product_card(p, hub, slugs):
    img = f'<img src="{e(abs_img(p.get("thumb")))}" alt="" loading="lazy">' if p.get('thumb') else ''
    if p.get('source') and p.get('url'):
        img += f'<span class="badge" style="background:{SELLER_COLOR.get(p["source"], "#9e9e9e")}">{e(p["source"])}</span>'
    return f'<a href="{url_of(hub, slugs[p["id"]])}"><span class="th">{img}</span><b>{e(p["name"])}</b></a>'


def camp_page(c, slug, by_region, slugs, eps_by_camp, products):
    name, region = c['name'], c.get('region') or ''
    visits = int(c.get('visits') or 0)
    addr = c.get('address') or ''
    info = c.get('info') if isinstance(c.get('info'), dict) else {}
    checkin = info.get('checkin') or c.get('checkin') or ''
    checkout = info.get('checkout') or c.get('checkout') or ''
    facilities = [f for f in (info.get('facilities') or []) if f]
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
    if checkin or checkout:
        rows.append(('입실 · 퇴실', f"{checkin or '-'} / {checkout or '-'}"))
    for k, label in (('manner', '매너타임'), ('pets', '반려동물'), ('max_people', '최대 인원')):
        if str(info.get(k) or '').strip():
            rows.append((label, str(info[k]).strip()))
    if facilities:
        rows.append(('편의시설', ' · '.join(facilities)))
    for k, label in (('season', '운영'), ('notice', '안내')):
        if str(info.get(k) or '').strip():
            rows.append((label, str(info[k]).strip()))
    if visits:
        rows.append(('방문 횟수', f"{visits}회"))
    if plat:
        rows.append(('예약', plat))
    dl = ''.join(f'<dt>{e(k)}</dt><dd>{e(v)}</dd>' for k, v in rows)
    src = info.get('source') if isinstance(info.get('source'), dict) else {}
    src_line = ''
    if src.get('platform') or src.get('checked_at'):
        src_line = '출처: ' + ' · '.join(x for x in (src.get('platform'), (src.get('checked_at') or '') + ' 확인' if src.get('checked_at') else '') if x)
    links = camp_links(c, plat)

    badges = []
    if c.get('pick'):
        badges.append('<span class="badge pick">★ PICK</span>')
    if region:
        badges.append(f'<span class="badge line">{e(region)}</span>')
    if visits:
        badges.append(f'<span class="badge line">{visits}회 방문</span>')
    if plat:
        badges.append(f'<span class="badge" style="background:{BOOK_COLOR.get(plat, "#9e9e9e")}">{e(plat)}</span>')
    hook = (c.get('hook') or '').strip()
    paras = story_paras(c.get('story'))
    if paras:
        desc = re.sub(r'\s+', ' ', paras[0])[:120]

    # 1) 히어로 + 제목 + 배지 + 훅
    body = [f'<p class="crumb"><a href="{SITE}/camps/">다녀온 캠핑장</a> · {e(region)}</p>']
    if imgs:
        body.append(f'<div class="hero"><img src="{e(abs_img(imgs[0]))}" alt="{e(name)}"></div>')
    body += [f'<h1>{e(name)}</h1>', f'<div class="badges">{"".join(badges)}</div>' if badges else '',
             f'<p class="hook">{e(hook)}</p>' if hook else f'<p class="lead">{e(lead)}</p>']

    # 2) 릴스 — 썸네일 카드 + 인스타 링크 (외부 embed 스크립트 없음)
    vids = [(v.get('title') or '영상', clean_ig(v.get('url')), v.get('thumb') or (imgs[0] if imgs else ''))
            for v in (c.get('videos') or []) if isinstance(v, dict) and v.get('url')]
    vids += [(t, clean_ig(u), th or (imgs[0] if imgs else '')) for t, u, th in eps_by_camp.get(c['id'], [])]
    seen, reels = set(), []
    for t, u, th in vids:
        if u not in seen:
            seen.add(u)
            reels.append((t, u, th))
    if reels:
        body.append('<h2>릴스</h2><div class="reels">' + ''.join(
            f'<a href="{e(u)}" rel="nofollow noopener" target="_blank"><span class="th">'
            + (f'<img src="{e(abs_img(th))}" alt="" loading="lazy">' if th else '')
            + f'</span><b>{e(t)}</b></a>' for t, u, th in reels) + '</div>')

    # 3) 본문 (빈 줄 = 단락, 마크다운 처리 없음)
    if paras:
        body.append('<h2>다녀온 이야기</h2><div class="story">' + ''.join(
            '<p>' + '<br>'.join(e(l) for l in p.split('\n')) + '</p>' for p in paras) + '</div>')

    # 4) 존별 가이드 + 배치도 (pick 먼저)
    guide = [g for g in (c.get('guide') or []) if isinstance(g, dict) and (g.get('zone') or g.get('text'))]
    guide.sort(key=lambda g: not g.get('pick'))
    layouts = [p for p in (c.get('layout_imgs') or []) if p]
    if guide or layouts:
        h = '<h2>존별 가이드</h2>'
        if guide:
            h += '<ul class="guide">' + ''.join(
                f'<li{" class=pick" if g.get("pick") else ""}><b>{"★ " if g.get("pick") else ""}{e(g.get("zone"))}</b>'
                f'{e(g.get("text"))}</li>' for g in guide) + '</ul>'
        h += ''.join(f'<img class="layout" src="{e(abs_img(p))}" alt="{e(name)} 배치도" loading="lazy">' for p in layouts)
        body.append(h)

    # 5) 정보
    if dl or extras:
        h = '<h2>정보</h2>'
        if dl:
            h += f'<dl>{dl}</dl>'
        if src_line:
            h += f'<p class="src">{e(src_line)}</p>'
        if extras:
            h += '<p class="tags" style="margin-top:12px">' + ''.join(f'<span>{e(t)}</span>' for t in extras) + '</p>'
        body.append(h)

    # 6) 링크 · 이때 쓴 장비 · 먹은 것
    if links:
        body.append('<h2>예약·링크</h2><div class="btns">' + ''.join(
            f'<a class="btn{"" if t in ("reserve", "discount", "event") else " sub"}" href="{e(u)}" rel="nofollow noopener" target="_blank"'
            + (f' style="background:{color}"' if color else '') + f'>{e(lb)} →</a>' for t, lb, u, color in links) + '</div>')
    for head, ids, rows, hub in (('이때 쓴 장비', c.get('gear'), products['items'], 'gear'),
                                 ('이때 먹은 것', c.get('foods'), products['foods'], 'foods')):
        cards = [rows[i] for i in (ids or []) if i in rows]
        if cards:
            body.append(f'<h2>{head}</h2><div class="cards">' + ''.join(product_card(p, hub, products['slugs'][hub]) for p in cards) + '</div>')

    # 7) 메모
    if notes:
        body.append('<h2>다녀와서 남긴 메모</h2><ul>' + ''.join(f'<li>{e(n)}</li>' for n in notes) + '</ul>')
    # 8) 사진 전체
    if len(imgs) > 1:
        body.append('<h2>사진</h2><div class="pics">' + ''.join(
            f'<img src="{e(abs_img(p))}" alt="{e(name)} 사진 {i + 2}" loading="lazy">' for i, p in enumerate(imgs[1:])) + '</div>')
    # 9) 같은 지역
    near = [x for x in by_region.get(region, []) if x['id'] != c['id']][:12]
    if near:
        body.append(f'<h2>{e(region)}의 다른 캠핑장</h2><ul class="cols">' + ''.join(
            f'<li><a href="{url_of("camps", slugs[x["id"]])}">{e(x["name"])}</a></li>' for x in near) + '</ul>')
    # 10) DM 안내 (가이드가 없을 때만)
    if c.get('dm') and not guide:
        kw = (c.get('dm_keyword') or '').strip()
        msg = f"더 자세한 추천 자리·배치도는 인스타 DM '{kw}'" if kw else '더 자세한 추천 자리·배치도는 인스타 DM으로 물어봐 주세요'
        body.append(f'<p class="dm"><a href="{IG}" rel="noopener" target="_blank">{e(msg)} →</a></p>')

    canonical = url_of('camps', slug)
    ld = {'@context': 'https://schema.org', '@type': 'Campground', 'name': name, 'url': canonical,
          'description': desc}
    if addr:
        ld['address'] = {'@type': 'PostalAddress', 'streetAddress': addr, 'addressRegion': region, 'addressCountry': 'KR'}
    if c.get('lat') and c.get('lng'):
        ld['geo'] = {'@type': 'GeoCoordinates', 'latitude': c['lat'], 'longitude': c['lng']}
    if imgs:
        ld['image'] = [abs_img(p) for p in imgs[:4]]
    if checkin:
        ld['checkinTime'] = checkin
    if checkout:
        ld['checkoutTime'] = checkout
    if info.get('pets'):
        ld['petsAllowed'] = str(info['pets']).strip() != '불가'
    if facilities:
        ld['amenityFeature'] = [{'@type': 'LocationFeatureSpecification', 'name': f, 'value': True} for f in facilities]
    same = list(dict.fromkeys(u for t, _, u, _ in links if t in ('reserve', 'homepage')))
    if same:
        ld['sameAs'] = same
    if reels:
        ld['video'] = [{'@type': 'VideoObject', 'name': t, 'url': u} for t, u, _ in reels]
    title = f"{name} — {hook} | {BRAND}" if hook else f"{name} 후기·정보 | {BRAND}"
    return page(title=title, desc=desc, canonical=canonical,
                og_image=abs_img(imgs[0]) if imgs else OG_DEFAULT,
                cta=('공대남자 홈페이지로', '/#camps'), track=(f"/search/camps/{c['id']}", name),
                body='\n'.join(b for b in body if b),
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
    badges = []
    if p.get('pick'):
        badges.append('<span class="badge pick">★ PICK</span>')
    if cat_label:
        badges.append(f'<span class="badge line">{e(cat_label)}</span>')
    if p.get('source') and p.get('url'):
        badges.append(f'<span class="badge" style="background:{SELLER_COLOR.get(p["source"], "#9e9e9e")}">{e(p["source"])}</span>')
    body = [f'<p class="crumb"><a href="{SITE}/{hub}/">{section_name}</a>{(" · " + e(cat_label)) if cat_label else ""}</p>']
    if p.get('thumb'):
        body.append(f'<div class="hero sq"><img src="{e(abs_img(p["thumb"]))}" alt="{e(name)}"></div>')
    body.append(f'<h1>{e(name)}</h1>')
    if badges:
        body.append(f'<div class="badges">{"".join(badges)}</div>')
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
                og_image=abs_img(p.get('thumb')) or OG_DEFAULT, cta=('공대남자의 캠핑이야기에서 보기', target),
                track=(f"/search/{hub}/{p['id']}", name), body='\n'.join(body),
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
                cta=('공대남자의 캠핑이야기에서 보기', redirect), track=(f"/search/{hub}", h1),
                body='\n'.join(body), og_type='website',
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
                eps_by_camp.setdefault(ep['camp_id'], []).append((f"{s.get('name')} · {title}", ep['url'], ep.get('thumb') or ''))

    # 정렬: 캠핑장은 방문 많은 순, 나머지는 이름순
    camps.sort(key=lambda c: (-(int(c.get('visits') or 0)), c['name']))
    items.sort(key=lambda x: x['name'])
    foods.sort(key=lambda x: x['name'])
    cs, gs, fs = assign_slugs(camps), assign_slugs(items), assign_slugs(foods)
    # 캠핑장 페이지의 '이때 쓴 장비·먹은 것' 카드용
    products = {'items': {x['id']: x for x in items}, 'foods': {x['id']: x for x in foods},
                'slugs': {'gear': gs, 'foods': fs}}

    # 이전 생성물 정리 후 다시 생성
    for d in OUT_DIRS:
        shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)

    by_region = {}
    for c in camps:
        by_region.setdefault(c.get('region') or '기타', []).append(c)
    for c in camps:
        write(f"camps/{cs[c['id']]}/index.html", camp_page(c, cs[c['id']], by_region, cs, eps_by_camp, products))
    # camp.html이 주소창을 정적 페이지 주소로 바꿀 때 쓰는 id → 이름 매핑 (장비·먹거리는 camp.html 카드 링크용)
    write('camps/slugs.json', json.dumps(cs, ensure_ascii=False, separators=(',', ':')) + '\n')
    write('gear/slugs.json', json.dumps(gs, ensure_ascii=False, separators=(',', ':')) + '\n')
    write('foods/slugs.json', json.dumps(fs, ensure_ascii=False, separators=(',', ':')) + '\n')

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
