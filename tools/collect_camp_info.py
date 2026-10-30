#!/usr/bin/env python3
"""캠핑장 정보 수집 (로컬 실행 전용).

그 캠핑장이 실제로 예약받는 플랫폼 페이지에서 입퇴실·매너타임·반려동물·편의시설·운영/예약 안내를 읽어
data/camp_info_raw/{id}.json 에 남긴다. **camps.json 에는 쓰지 않는다** — 사람이 검토해 admin '📥 패치 붙여넣기'로 반영.
고캠핑(한국관광공사) 데이터는 쓰지 않는다.

  땡큐캠핑  m.thankqcamping.com/resv/view.hbb?cseq=  서버 렌더 → requests (사이트 목록·가격은 JS라 무시)
  그래가    graega.short.gy/{n}kydzm → www.graega.com/rooms/{n}  SPA → Playwright 로 렌더한 본문 텍스트
  캠핏      camfit.co.kr/camp/{id}  일반 요청은 막힘 → Playwright 1회, 안 되면 needs_browser (우회·재시도 없음)
  네이버    예약/플레이스/지도/카페 — 시도하지 않고 needs_browser
  그 밖     자체 홈페이지 등 — requests 로 텍스트만

실행:
  pip install -r requirements.txt && python -m playwright install chromium
  python tools/collect_camp_info.py                # 전체
  python tools/collect_camp_info.py --only 알프스   # 이름·id 일부
  python tools/collect_camp_info.py --platform 땡큐캠핑
"""
import argparse
import datetime
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_pages import ROOT, KST, platform_of  # noqa: E402

OUT = os.path.join(ROOT, 'data', 'camp_info_raw')
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/130.0.0.0 Safari/537.36')
FACILITY_WORDS = ['와이파이', '온수', '샤워실', '개수대', '화장실', '매점', '카페', '놀이터', '트램펄린', '방방이', '수영장',
                  '물놀이장', '전기', '산책로', '장작', '분리수거', '세탁', '탈수기', '냉장고', '전자레인지', '캠핑카', '카라반', '트레일러']
# 후기·판매자 정보부터는 개인 글·개인정보라 저장하지 않는다
CUT_MARKERS = ['판매자 정보', '방문후기 (', '\n후기\n고객 평점', '리뷰 더보기']


def plat_key(url):
    u = (url or '').lower()
    if not u:
        return ''
    p = platform_of(u)
    if p == '그래가 파트너스':
        return 'graega'
    if p == '땡큐캠핑':
        return 'thankq'
    if p == '캠핏':
        return 'camfit'
    if p == '네이버':
        return 'naver'
    return 'site'


PLAT_LABEL = {'graega': '그래가', 'thankq': '땡큐캠핑', 'camfit': '캠핏', 'naver': '네이버', 'site': '자체/기타'}


def clean_text(t):
    t = re.sub(r'[ \t\xa0​‍]+', ' ', t or '')
    t = re.sub(r'\n\s*\n+', '\n', t).strip()
    cut = min([i for i in (t.find(m) for m in CUT_MARKERS) if i > 0] or [len(t)])
    t = t[:cut]
    t = re.sub(r'01[016789][-. ]?\d{3,4}[-. ]?\d{4}', '010-****-****', t)       # 휴대폰
    t = re.sub(r'[\w.+-]+@[\w-]+\.[\w.]+', '***@***', t)                         # 메일
    t = re.sub(r'(?<![\d.:-])\d{8,}(?![\d.:-])', '********', t)                  # 와이파이 비밀번호 같은 긴 숫자
    t = re.sub(r'\d{3}-\d{2}-\d{5}', '***-**-*****', t)                             # 사업자번호
    t = re.sub(r'(대표자\s*(?:명)?\s*[:：]?\s*)[^\s|/,]+', r'\1***', t)              # 대표자 이름
    return t


def html_text(raw):
    from bs4 import BeautifulSoup
    s = BeautifulSoup(raw, 'html.parser')
    for tag in s(['script', 'style', 'noscript', 'svg']):
        tag.decompose()
    return s.get_text('\n')


def section(text, start, ends):
    i = text.find(start)
    if i < 0:
        return ''
    j = min([k for k in (text.find(e, i + len(start)) for e in ends) if k > 0] or [len(text)])
    return text[i:j]


def first(pattern, text, flags=0):
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else ''


def hhmm(s):
    """'오후 11:00' → '23:00'"""
    m = re.match(r'(오[전후])?\s*(\d{1,2}):(\d{2})', s.strip())
    h = int(m.group(2)) % 12 + (12 if m.group(1) == '오후' else 0) if m.group(1) else int(m.group(2))
    return f'{h:02d}:{m.group(3)}'


def extract(text, plat):
    """본문 텍스트에서 정보 블록 후보를 뽑는다 (사람이 검토하는 초안)."""
    t = text
    x = {'checkin': '', 'checkout': '', 'manner': '', 'pets': '', 'facilities': [], 'season': '', 'notice': ''}
    x['checkin'] = first(r'(?:입실|체크인)\s*(?:시간)?\s*[:：]?\s*(\d{1,2}:\d{2})', t)
    x['checkout'] = first(r'(?:퇴실|체크아웃)\s*(?:시간)?\s*[:：]?\s*(\d{1,2}:\d{2})', t)
    ms = first(r'매너\s*타임\s*(?:시작)?\s*[:：]?\s*(\d{1,2}:\d{2})', t)
    me = first(r'매너\s*타임[\s\S]{0,30}?종료\s*[:：]?\s*(\d{1,2}:\d{2})', t)
    if not ms:
        m = re.search(r'매너\s*타임\s*[:：]?\s*((?:오[전후]\s*)?\d{1,2}:\d{2})\s*[~\-]\s*((?:오[전후]\s*)?\d{1,2}:\d{2})', t)
        if m:
            ms, me = hhmm(m.group(1)), hhmm(m.group(2))
    if ms:
        x['manner'] = f'{ms}~{me}' if me else ms
    pet = [l.strip() for l in t.split('\n') if re.search(r'반려|애견|펫\b|반려견', l) and len(l.strip()) <= 60]
    if pet:
        x['pets'] = ' / '.join(dict.fromkeys(pet))[:120]
    fac_src = t
    if plat == 'thankq':
        fac_src = section(t, '시설/환경\n전체보기', ['예약안내']) or t
    elif plat == 'graega':
        fac_src = section(t, '', ['진행중인 이벤트', '공지사항']) or t
        fac_src += '\n' + section(t, '편의', ['예약 취소', '취소∙변경', '위치 및 주변'])
    x['facilities'] = [w for w in FACILITY_WORDS if w in fac_src]
    x['season'] = first(r'(?:운영\s*기간|운영\s*시즌|동계\s*(?:휴장|미운영)[^\n]*)\s*[:：]?\s*([^\n]{2,40})', t)
    notes = []
    if plat == 'thankq':
        cyc = first(r'오픈주기\s*\n\s*([^\n]+(?:\n\s*\([^\n]+\))?)', t)
        if cyc:
            notes.append('예약 오픈 ' + re.sub(r'\s+', ' ', cyc))
        until = first(r'예약가능\s*\n\s*([^\n]+까지)', t)
        if until:
            notes.append('예약 가능 ' + until)
    elif plat == 'graega':
        nxt = first(r'다음 오픈일\s*\n\s*([^\n]+)', t)
        if nxt:
            notes.append('예약 오픈 ' + nxt)
        for l in section(t, '공지사항', ['캠핑장 배치도', '멤버십']).split('\n')[1:6]:
            if l.strip():
                notes.append(l.strip())
    x['notice'] = ' · '.join(notes)[:300]
    return x


def fetch_requests(url):
    import requests
    r = requests.get(url, headers={'User-Agent': UA, 'Accept-Language': 'ko-KR,ko;q=0.9'}, timeout=25)
    raw = r.content
    enc = r.encoding if (r.encoding and r.encoding.lower() != 'iso-8859-1') else None
    if not enc:
        m = re.search(rb'charset=["\']?([\w-]+)', raw[:3000], re.I)
        enc = m.group(1).decode() if m else 'utf-8'
    return r.status_code, r.url, raw.decode(enc, 'replace')


_browser = None


def fetch_browser(url):
    """Playwright 렌더 1회 (재시도 없음)."""
    global _browser
    from playwright.sync_api import sync_playwright
    if _browser is None:
        pw = sync_playwright().start()
        _browser = pw.chromium.launch()
    ctx = _browser.new_context(user_agent=UA, locale='ko-KR')
    try:
        pg = ctx.new_page()
        resp = pg.goto(url, wait_until='networkidle', timeout=45000)
        pg.wait_for_timeout(2500)
        return (resp.status if resp else 0), pg.url, pg.inner_text('body')
    finally:
        ctx.close()


def collect(c, url):
    plat = plat_key(url)
    rec = {'platform': PLAT_LABEL.get(plat, ''), 'url': url, 'final_url': '', 'status': 'fail',
           'fetched_at': datetime.datetime.now(KST).isoformat(timespec='seconds'), 'text': '', 'extracted': {}}
    if plat == 'naver':
        rec['status'] = 'needs_browser'
        rec['reason'] = '네이버 예약/플레이스/지도/카페는 시도하지 않음'
        return rec
    try:
        if plat in ('graega', 'camfit'):
            code, final, text = fetch_browser(url)
        else:
            code, final, raw = fetch_requests(url)
            text = html_text(raw)
        rec['final_url'] = final
        rec['http_status'] = code
        text = clean_text(text)
        blocked = code >= 400 or len(text) < 200 or re.search(r'client.?side exception|Access Denied|captcha', text, re.I)
        if blocked:
            rec['status'] = 'needs_browser' if plat == 'camfit' else 'fail'
            rec['reason'] = f'HTTP {code}, 본문 {len(text)}자'
            rec['text'] = text[:2000]
            return rec
        rec['text'] = text
        rec['extracted'] = extract(text, plat)
        rec['status'] = 'ok'
    except Exception as ex:  # noqa: BLE001 — 한 곳 실패는 기록만 하고 넘어간다
        rec['status'] = 'needs_browser' if plat == 'camfit' else 'fail'
        rec['reason'] = f'{type(ex).__name__}: {str(ex)[:200]}'
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', help='이름 또는 id 일부')
    ap.add_argument('--platform', help='그래가 / 땡큐캠핑 / 캠핏 / 네이버 / 자체/기타')
    args = ap.parse_args()
    with open(os.path.join(ROOT, 'data', 'camps.json'), encoding='utf-8') as f:
        camps = [c for c in json.load(f) if c.get('published', True) is not False]
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for c in camps:
        if args.only and args.only not in c['name'] and args.only not in c['id']:
            continue
        urls = [c.get('url') or ''] + [l.get('url') or '' for l in (c.get('links') or []) if l.get('type') in ('reserve', 'homepage')]
        urls = [u.strip() for u in dict.fromkeys(urls) if u and u.strip()]
        if not urls:
            rows.append((c['name'], '-', 'no_url', 0))
            continue
        if args.platform and PLAT_LABEL.get(plat_key(urls[0])) != args.platform:
            continue
        rec = None
        for u in urls:  # 예약 url 먼저, 안 되면 links 의 다음 url
            rec = collect(c, u)
            if rec['status'] == 'ok':
                break
            time.sleep(1)
        rec = {'id': c['id'], 'name': c['name'], **rec}
        with open(os.path.join(OUT, c['id'] + '.json'), 'w', encoding='utf-8') as f:
            json.dump(rec, f, ensure_ascii=False, indent=1)
            f.write('\n')
        n = sum(1 for v in rec['extracted'].values() if v)
        rows.append((c['name'], rec['platform'], rec['status'], n))
        print(f"{rec['status']:<13} {rec['platform']:<6} {n}  {c['name']}", flush=True)
        time.sleep(1)
    if _browser is not None:
        _browser.close()

    print('\n| 캠핑장 | 플랫폼 | 상태 | 추출 필드 수 |\n|---|---|---|---|')
    for r in rows:
        print(f'| {r[0]} | {r[1]} | {r[2]} | {r[3]} |')
    nb = [r[0] for r in rows if r[2] == 'needs_browser']
    if nb:
        print('\nneeds_browser: ' + ', '.join(nb))


if __name__ == '__main__':
    main()
