#!/usr/bin/env python3
"""네이버 블로그 원고 페이지 만들기 (PC에서 실행, 261030)

글 원고(JSON) + 내 PC 사진(MYBOX 폴더 등) → `_blog/{slug}/post.html`
post.html을 브라우저로 열고 '다음 복사' → 네이버 에디터에 Ctrl+V 를 반복하면
글과 사진이 순서대로 들어간다. 사진은 '사진 그대로' 복사되므로 네이버 서버에 올라간다
(홈페이지 kydz.kr 이미지 주소를 붙이면 링크만 걸려서 안 됨).

사용법:
    pip install pillow
    python tools/blog_post.py _blog/봉화별캠핑장.json          # 만들기
    python tools/blog_post.py _blog/봉화별캠핑장.json --serve  # 만들고 브라우저로 열기

원고 JSON 형식은 docs/blog.md 참고. `_blog/`는 .gitignore — 사진·원고는 저장소에 올리지 않는다.
"""
import argparse, base64, html, io, json, os, sys, urllib.request
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError:
    sys.exit('Pillow가 필요해요: pip install pillow')

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / '_blog'
FONT_DIR = OUT / 'fonts'
FONT_URL = 'https://raw.githubusercontent.com/orioncactus/pretendard/main/packages/pretendard/dist/public/static/Pretendard-{}.otf'

# 썸네일 틀 — 블로그 타이틀(남색 밤 사진)과 같은 톤
NAVY, INK, SUB, MUTED, YEL = (16, 22, 38), (245, 242, 235), (170, 176, 190), (120, 128, 145), (255, 232, 115)
PHOTO_LONG = 1600   # 본문 사진 긴 변 (네이버 본문 폭보다 충분히 큼)


def font(weight, size):
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    p = FONT_DIR / f'Pretendard-{weight}.otf'
    if not p.exists():
        print(f'글꼴 내려받는 중: Pretendard-{weight}')
        urllib.request.urlretrieve(FONT_URL.format(weight), p)
    return ImageFont.truetype(str(p), size)


def load(path):
    p = Path(path).expanduser()
    if not p.is_absolute():
        p = (ROOT / p) if (ROOT / p).exists() else p
    if not p.exists():
        sys.exit(f'사진을 찾을 수 없어요: {path}')
    return ImageOps.exif_transpose(Image.open(p)).convert('RGB')


def cover(im, w, h, fy=0.5, fx=0.5):
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = int((im.width - w) * fx), int((im.height - h) * fy)
    return im.crop((x, y, x + w, y + h))


def make_thumb(t):
    """1080×1080: 위 사진 + 아래 남색 띠(이름·한 줄 설명·블로그 이름)."""
    S, PH = 1080, 800
    im = Image.new('RGB', (S, S), NAVY)
    im.paste(cover(load(t['photo']), S, PH, t.get('focus_y', 0.5), t.get('focus_x', 0.5)), (0, 0))
    fade = Image.new('RGBA', (S, 140))
    fd = ImageDraw.Draw(fade)
    for y in range(140):
        a = y / 140
        fd.line([(0, y), (S, y)], fill=NAVY + (int(255 * a * a * (3 - 2 * a)),))
    im.paste(fade, (0, PH - 140), fade)
    d = ImageDraw.Draw(im)
    d.rectangle((72, 836, 80, 950), fill=YEL)
    d.text((104, 826), t['name'], font=font('ExtraBold', 72), fill=INK)
    d.text((106, 920), t.get('sub', ''), font=font('Medium', 34), fill=SUB)
    d.text((S - 72, 1020), '공대남자의 캠핑 기록', font=font('Medium', 24), fill=MUTED, anchor='rs')
    return im


def fit(im):
    s = min(1, PHOTO_LONG / max(im.size))
    return im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS) if s < 1 else im


def jpeg(im, path):
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=90, optimize=True)
    path.write_bytes(buf.getvalue())
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


def pieces(spec, out):
    """붙여넣을 조각 목록: 이어진 글 블록은 하나로 묶고, 사진은 한 장씩."""
    res, text = [], []

    def flush():
        if text:
            res.append({'k': 'text', 'html': ''.join(h for h, _ in text), 'plain': '\n'.join(p for _, p in text).strip()})
            text.clear()

    n = 0
    if spec.get('thumb'):
        res.append({'k': 'img', 'src': jpeg(make_thumb(spec['thumb']), out / '00_대표.jpg'), 'label': '대표 썸네일'})
    for b in spec['blocks']:
        if 'img' in b:
            flush()
            if str(b['img']).startswith('http'):
                sys.exit(f'사진은 내 PC 파일로 넣어 주세요 (주소를 넣으면 네이버에 링크만 걸려요): {b["img"]}')
            n += 1
            res.append({'k': 'img', 'src': jpeg(fit(load(b['img'])), out / f'{n:02d}.jpg'), 'label': f'사진 {n}'})
        elif 'h' in b:
            text.append((f'<p><b>{html.escape(b["h"])}</b></p><p><br></p>', b['h'] + '\n'))
        elif 'link' in b:
            # 주소는 글자 그대로 붙여야 네이버가 링크 카드(미리보기)를 만든다
            flush()
            t = b.get('text') or b['link']
            plain = t if b['link'] in t else f'{t}\n{b["link"]}'
            res.append({'k': 'link', 'plain': plain, 'html': '<br>'.join(html.escape(l) for l in plain.split('\n')), 'label': '링크 카드'})
        elif 'map' in b:
            t = f'[지도: 에디터 \'장소\' 버튼 → {b["map"]} 검색해서 넣고 이 줄은 지우기]'
            text.append((f'<p>{html.escape(t)}</p><p><br></p>', t + '\n'))
        else:
            lines = b['p'].split('\n')
            text.append((''.join(f'<p>{html.escape(l)}</p>' if l else '<p><br></p>' for l in lines) + '<p><br></p>', b['p'] + '\n'))
    flush()
    return res


PAGE = r'''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>__TITLE__</title>
<style>
:root{--bg:#eef1ec;--paper:#fff;--ink:#1f2420;--muted:#68716a;--line:#d8ddd6;--accent:#03a94f;--done:#e6f4ea}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.7 -apple-system,"Malgun Gothic","Apple SD Gothic Neo",sans-serif}
.bar{position:sticky;top:0;z-index:5;background:var(--paper);border-bottom:1px solid var(--line);padding:10px 16px}
.bar-in{max-width:760px;margin:0 auto;display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.bar b{margin-right:auto}
button{font:inherit;font-size:14px;border:1px solid var(--line);background:#fff;border-radius:8px;padding:7px 12px;cursor:pointer}
#next{background:var(--accent);color:#fff;border-color:var(--accent);font-weight:700;font-size:16px;padding:10px 18px}
#state{font-variant-numeric:tabular-nums;color:var(--muted)}
.wrap{max-width:760px;margin:0 auto;padding:16px}
.guide{background:#fff6d6;color:#6a5300;border-radius:10px;padding:10px 14px;font-size:14px;margin-bottom:14px}
.pc{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin-bottom:10px;cursor:pointer}
.pc.cur{outline:3px solid var(--accent)}.pc.done{background:var(--done);opacity:.7}
.pc .no{font-size:12px;color:var(--muted)}.pc img{display:block;max-width:100%;max-height:320px;border-radius:4px}
.pc .t p{margin:0}
.toast{position:fixed;left:50%;bottom:20px;transform:translateX(-50%);background:#222;color:#fff;padding:9px 16px;border-radius:20px;opacity:0;transition:opacity .2s}
.toast.on{opacity:1}
</style></head><body>
<div class="bar"><div class="bar-in"><b>__TITLE_ESC__</b>
<button id="cpTitle">제목 복사</button><button id="cpTags">태그 복사</button>
<span id="state"></span><button id="next">다음 복사 ▶</button></div></div>
<div class="wrap">
<div class="guide">브라우저와 네이버 에디터를 <b>창 두 개로 나란히</b> 띄우고: <b>다음 복사</b> → 에디터에 <b>Ctrl+V</b> 반복.
잘못 붙였으면 해당 칸을 눌러 그 조각부터 다시 복사. 끝나면 대표 사진 지정·태그·카테고리(__CAT__) 확인 후 발행.</div>
<div id="list"></div></div><div class="toast" id="toast"></div>
<script>
const D = __DATA__;
const $ = id => document.getElementById(id);
let i = 0;
const toast = t => { const e = $('toast'); e.textContent = t; e.classList.add('on'); clearTimeout(toast.t); toast.t = setTimeout(() => e.classList.remove('on'), 1600); };
const list = $('list');
D.pieces.forEach((p, k) => {
  const el = document.createElement('div'); el.className = 'pc'; el.dataset.k = k;
  el.innerHTML = `<div class="no">${k + 1}. ${p.k === 'text' ? '글' : p.label}</div>` + (p.k === 'img' ? `<img src="${p.src}">` : `<div class="t">${p.html}</div>`);
  el.onclick = () => { i = k; copy(); };
  list.appendChild(el);
});
function mark() {
  document.querySelectorAll('.pc').forEach((e, k) => { e.classList.toggle('done', k < i); e.classList.toggle('cur', k === i); });
  const p = D.pieces[i];
  $('state').textContent = i < D.pieces.length ? `${i + 1}/${D.pieces.length} · 다음은 ${{img: '사진', link: '링크'}[p.k] || '글'}` : '다 붙였어요 ✓';
}
async function copy() {
  const p = D.pieces[i]; if (!p) return;
  try {
    if (p.k === 'img') {
      const png = await new Promise(res => { const im = new Image(); im.onload = () => { const c = document.createElement('canvas');
        c.width = im.naturalWidth; c.height = im.naturalHeight; c.getContext('2d').drawImage(im, 0, 0); c.toBlob(res, 'image/png'); }; im.src = p.src; });
      await navigator.clipboard.write([new ClipboardItem({ 'image/png': png })]);
    } else if (p.k === 'link') {
      await navigator.clipboard.writeText(p.plain);
      toast(`${i + 1}번 링크 — Ctrl+V, 카드가 안 생기면 주소 끝에서 Enter`); i++; mark(); return;
    } else {
      await navigator.clipboard.write([new ClipboardItem({ 'text/html': new Blob([p.html], { type: 'text/html' }), 'text/plain': new Blob([p.plain], { type: 'text/plain' }) })]);
    }
    toast(`${i + 1}번 복사 — 에디터에 Ctrl+V`); i++; mark();
  } catch (e) { toast('복사가 막혔어요 — README의 --serve로 열어 주세요'); console.error(e); }
}
$('next').onclick = copy;
const plain = (t, m) => navigator.clipboard.writeText(t).then(() => toast(m), () => toast('복사가 막혔어요'));
$('cpTitle').onclick = () => plain(D.title, '제목 복사');
$('cpTags').onclick = () => plain(D.tags, '태그 복사');
mark();
</script></body></html>'''


def main():
    ap = argparse.ArgumentParser(description='네이버 블로그 원고 페이지 만들기')
    ap.add_argument('spec', help='원고 JSON (docs/blog.md 형식)')
    ap.add_argument('--serve', action='store_true', help='만든 뒤 localhost로 띄워 브라우저 열기')
    a = ap.parse_args()
    spec = json.loads(Path(a.spec).read_text(encoding='utf-8'))
    for k in ('slug', 'title', 'blocks'):
        if k not in spec:
            sys.exit(f'원고 JSON에 "{k}"가 없어요')
    out = OUT / spec['slug']
    out.mkdir(parents=True, exist_ok=True)
    ps = pieces(spec, out)
    data = json.dumps({'title': spec['title'], 'tags': spec.get('tags', ''), 'pieces': ps}, ensure_ascii=False)
    page = (PAGE.replace('__DATA__', data).replace('__TITLE_ESC__', html.escape(spec['title']))
            .replace('__TITLE__', html.escape(spec['slug'] + ' 원고')).replace('__CAT__', html.escape(spec.get('category', '캠핑장 후기'))))
    (out / 'post.html').write_text(page, encoding='utf-8')
    n_img = sum(p['k'] == 'img' for p in ps)
    print(f'완료: {out / "post.html"}  (조각 {len(ps)}개 · 사진 {n_img}장)')
    if a.serve:
        import functools, http.server, threading, webbrowser
        h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(out))
        srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), h)
        url = f'http://127.0.0.1:{srv.server_address[1]}/post.html'
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
        print(f'열기: {url}  (다 붙였으면 Ctrl+C로 종료)')
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
