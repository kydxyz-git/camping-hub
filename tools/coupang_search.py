"""
쿠팡에서 찾기 — admin 새 장비·먹거리 추가 화면의 '🛒 쿠팡에서 찾기'가 부른다
(.github/workflows/coupang-search.yml, 입력: keyword · req).

쿠팡 파트너스 Open API로 상품을 검색해 후보마다
  상품명 · 가격 · 로켓배송 · 내 파트너스 짧은 링크 · 썸네일 규격(800×800 흰 배경·여백 7%·잘림 없음) JPEG
을 만들어 coupang_search.json 하나에 담는다. 워크플로가 이 파일만 든 `coupang-search` 브랜치로 강제 푸시
(main 기록을 늘리지 않음) → admin이 읽어 폼을 채우고, 저장은 admin의 기존 저장 경로(3-way 병합)로 한다.

환경변수: COUPANG_ACCESS_KEY, COUPANG_SECRET_KEY (저장소 Secrets), KEYWORD, REQ
"""

import base64
import hashlib
import hmac
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

from PIL import Image, ImageChops

API = "https://api-gateway.coupang.com"
PREFIX = "/v2/providers/affiliate_open_api/apis/openapi"
KST = timezone(timedelta(hours=9))
UA = "Mozilla/5.0 (compatible; kydz-admin/1.0)"
LIMIT = 6


def signed(method, path, query=""):
    ak = os.environ.get("COUPANG_ACCESS_KEY", "").strip()
    sk = os.environ.get("COUPANG_SECRET_KEY", "").strip()
    if not ak or not sk:
        raise RuntimeError("COUPANG_ACCESS_KEY / COUPANG_SECRET_KEY가 camping-hub 저장소 Secrets에 없어요.")
    dt = time.strftime("%y%m%dT%H%M%SZ", time.gmtime())
    sig = hmac.new(sk.encode(), (dt + method + path + query).encode(), hashlib.sha256).hexdigest()
    return f"CEA algorithm=HmacSHA256, access-key={ak}, signed-date={dt}, signature={sig}"


def cp(method, path, params=None, body=None):
    path = PREFIX + path
    query = urllib.parse.urlencode(params or {})
    url = API + path + (f"?{query}" if query else "")
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": signed(method, path, query), "Content-Type": "application/json;charset=UTF-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"쿠팡 API 오류 ({e.code}): {e.read().decode('utf-8', 'replace')[:200]}")
    if str(res.get("rCode", "0")) != "0":
        raise RuntimeError(f"쿠팡 API 오류: {res.get('rMessage') or res}")
    return res.get("data")


def download(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def big_image(url):
    """검색 결과 썸네일(230x230 등) 주소에서 크기 부분을 빼 원본을 먼저 시도"""
    tries = [re.sub(r"/thumbnails/remote/\d+x\d+(ex|q\d+)?/", "/", url), re.sub(r"/\d+x\d+ex/", "/492x492ex/", url), url]
    for u in dict.fromkeys(tries):
        try:
            data = download(u)
            Image.open(io.BytesIO(data)).verify()
            return data
        except Exception:
            continue
    raise RuntimeError("이미지 다운로드 실패")


def fit_product_image(data, size=800, margin=0.07, quality=85, info=None):
    """admin fitProductImage와 같은 규칙: 흰 배경 합성 → 연회색 배경은 흰색으로 → 가장자리 여백 정리 → 800×800·여백 7%·비율 유지"""
    im = Image.open(io.BytesIO(data))
    im = im.convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    rgb = bg.convert("RGB")
    w, h = rgb.size
    px = rgb.load()
    corner = [min(px[x, y]) for x, y in ((1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2))]
    lo = min(corner)
    if 228 <= lo < 253 and max(corner) - lo <= 6:
        f = 255 / (lo - 2)
        rgb = rgb.point(lambda v: min(255, int(v * f)))
    box = _ink_box(rgb) or (0, 0, w, h)
    if info is not None:
        # 네 모서리가 흰색(240+)이 아니면 연출 사진(배경 있음) — 홈페이지 스타일과 다름
        px2 = rgb.load()
        info["bg_ok"] = all(min(px2[x, y]) >= 240 for x, y in ((2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3)))
    crop = rgb.crop(box)
    cw, ch = crop.size
    inner = round(size * (1 - margin * 2))
    scale = min(inner / cw, inner / ch)
    dw, dh = max(1, round(cw * scale)), max(1, round(ch * scale))
    crop = crop.resize((dw, dh), Image.LANCZOS)
    out = Image.new("RGB", (size, size), (255, 255, 255))
    out.paste(crop, (round((size - dw) / 2), round((size - dh) / 2)))
    buf = io.BytesIO()
    out.save(buf, "JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def _ink_box(rgb):
    """R·G·B 중 가장 어두운 값이 240 미만인 픽셀(=내용)의 경계 상자"""
    r, g, b = rgb.split()
    darkest = ImageChops.darker(ImageChops.darker(r, g), b)
    return darkest.point(lambda v: 255 if v < 240 else 0).getbbox()


def main():
    keyword = os.environ.get("KEYWORD", "").strip()
    req = os.environ.get("REQ", "").strip()
    out = {"req": req, "keyword": keyword, "at": datetime.now(KST).isoformat(timespec="seconds"), "items": [], "error": ""}
    try:
        if not keyword:
            raise RuntimeError("검색어가 비어 있어요.")
        d = cp("GET", "/products/search", {"keyword": keyword, "limit": LIMIT})
        rows = (d or {}).get("productData", []) if isinstance(d, dict) else (d or [])
        rows = [r for r in rows if r.get("productId")][:LIMIT]
        links = {}
        if rows:
            urls = [f"https://www.coupang.com/vp/products/{r['productId']}" for r in rows]
            for row in cp("POST", "/v1/deeplink", body={"coupangUrls": urls}) or []:
                m = re.search(r"/products/(\d+)", row.get("originalUrl", ""))
                if m and row.get("shortenUrl"):
                    links[m[1]] = row["shortenUrl"]
        for r in rows:
            pid = str(r["productId"])
            if pid not in links:
                continue
            it = {"pid": pid, "name": str(r.get("productName", "")).strip(), "price": r.get("productPrice"),
                  "rocket": bool(r.get("isRocket")), "url": links[pid], "image_url": r.get("productImage", ""),
                  "img": ""}
            try:
                info = {}
                it["img"] = base64.b64encode(fit_product_image(big_image(it["image_url"]), info=info)).decode()
                it["bg_ok"] = info.get("bg_ok", True)
            except Exception as e:
                it["img_error"] = str(e)[:100]
            out["items"].append(it)
        if not out["items"]:
            out["error"] = "검색 결과가 없어요. 검색어를 바꿔 보세요."
    except Exception as e:
        out["error"] = str(e)[:300]
    with open("coupang_search.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print(json.dumps({k: v for k, v in out.items() if k != "items"}, ensure_ascii=False),
          [(i["name"][:30], i["price"], bool(i["img"])) for i in out["items"]])
    return 0


if __name__ == "__main__":
    sys.exit(main())
