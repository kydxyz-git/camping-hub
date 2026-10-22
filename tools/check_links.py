"""
쿠팡 링크 점검 — data/items.json · data/foods.json의 쿠팡 링크를 하나씩 따라가서
내 파트너스 코드(AF…)가 붙어 있는지, 상품이 판매 중인지 확인해 data/link_check.json에 기록한다.
링크는 고치지 않는다 (고치는 건 사용자가 파트너스에서 직접 — 사용자 결정 261022).
.github/workflows/link-check.yml이 매주 월요일 + 수동으로 실행. 표준 라이브러리만 사용.

상태
  ok        정상 (내 코드 + 판매 중)
  no_af     파트너스 코드 없음 → 수익 안 잡힘 (쿠팡 앱 '공유' 링크 등)
  other_af  다른 파트너스 코드 (대부분 링크와 코드가 다름)
  soldout   품절·판매 종료 의심 (상품 페이지 문구 기준 — 직접 확인 필요)
  broken    링크 깨짐 (없는 링크·상품으로 안 감)
  unknown   상품 페이지 확인 불가 (쿠팡이 자동 접속을 막음) — 코드 확인은 됨
"""

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "link_check.json")
KST = timezone(timedelta(hours=9))
UA = ("Mozilla/5.0 (Linux; Android 14; SM-S928N) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/130.0.0.0 Mobile Safari/537.36")
SOLDOUT = ["판매가 종료", "판매 종료된", "판매종료", "품절된 상품", "일시품절", "현재 판매하지 않는",
           "상품을 찾을 수 없", "판매중지", "판매 중지", "존재하지 않는 상품"]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def get(url, read=False):
    """(상태 코드, Location, 본문 일부)"""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ko-KR,ko;q=0.9",
                                               "Accept": "text/html,application/xhtml+xml"})
    try:
        r = OPENER.open(req, timeout=20)
        body = r.read(600_000).decode("utf-8", "replace") if read else ""
        return r.status, r.headers.get("Location", ""), body
    except urllib.error.HTTPError as e:
        loc = e.headers.get("Location", "") if e.headers else ""
        return e.code, loc, ""
    except Exception as e:  # 연결 오류
        return 0, "", str(e)


def next_url(body, seen):
    """페이지 본문에서 다음 쿠팡 주소 (상품·파트너스 추적 주소 우선)"""
    text = body.replace("\\/", "/").replace("&amp;", "&")
    cands = re.findall(r"https?://[a-z.]*coupang\.com/[^\"'\s<>\\]+", text)
    cands += [urllib.parse.unquote(u) for u in re.findall(r"https?%3A%2F%2F[a-z.]*coupang\.com[^\"'\s<>&]+", text)]
    cands = [u for u in cands if u not in seen and not re.search(r"\.(js|css|png|jpe?g|gif|svg|ico)(\?|$)", u)]
    for pat in (r"/vp/products/\d+", r"lptag=AF", r"/re/", r"pageKey="):
        for u in cands:
            if re.search(pat, u):
                return u
    return ""


def check(url):
    chain, cur = [url], url
    status, body = 0, ""
    first_body = ""
    for _ in range(8):
        is_product = re.search(r"coupang\.com/vp/products/\d+", cur)
        status, loc, body = get(cur, read=True)
        if status in (301, 302, 303, 307, 308) and loc:
            cur = urllib.parse.urljoin(cur, loc)
            chain.append(cur)
            continue
        if status == 200 and not is_product:
            # 짧은 링크는 HTTP 넘김이 아니라 페이지 안(자바스크립트·meta)에서 다음 주소로 넘김 → 본문에서 찾기
            first_body = first_body or body
            nxt = next_url(body, chain)
            if nxt:
                cur = nxt
                chain.append(cur)
                continue
        break
    joined = " ".join(urllib.parse.unquote(u) for u in chain)
    af = (re.search(r"lptag=(AF\d+)", joined) or re.search(r"\b(AF\d{5,})\b", joined) or [None, ""])[1]
    pid = (re.search(r"/vp/products/(\d+)", joined) or re.search(r"pageKey=(\d+)", joined) or [None, ""])[1]
    final = chain[-1]

    if not pid:
        if status == 200:
            # 페이지는 열리는데 상품 주소를 못 찾음 → 점검 방식 문제일 수 있어 '확인 불가'로
            return {"status": "unknown", "af": af, "product_id": "", "detail": "넘어가는 주소를 못 찾음 (확인 불가)",
                    "_body": first_body[:3000]}
        detail = f"상품으로 안 감 (마지막 주소 {final[:80]}, 응답 {status or '연결 오류'})"
        return {"status": "broken", "af": af, "product_id": "", "detail": detail}
    if status == 200 and body:
        hit = next((w for w in SOLDOUT if w in body), "")
        if hit:
            return {"status": "soldout", "af": af, "product_id": pid, "detail": f"상품 페이지에 '{hit}' 문구"}
        return {"status": "ok", "af": af, "product_id": pid, "detail": ""}
    if status == 404:
        return {"status": "broken", "af": af, "product_id": pid, "detail": "상품 페이지 404 (삭제된 상품)"}
    return {"status": "unknown", "af": af, "product_id": pid,
            "detail": f"상품 페이지 확인 불가 (응답 {status or '연결 오류'})"}


def main():
    rows = []
    for kind in ("items", "foods"):
        with open(os.path.join(ROOT, "data", f"{kind}.json"), encoding="utf-8") as f:
            for it in json.load(f):
                url = (it.get("url") or "").strip()
                if "coupang" in url and it.get("id"):
                    rows.append((kind, it))
    results, sample = {}, ""
    for n, (kind, it) in enumerate(rows, 1):
        r = check(it["url"].strip())
        body = r.pop("_body", "")
        if body and not sample:
            sample = body
        results[it["id"]] = {"type": kind, "name": it.get("name", ""), "url": it["url"].strip(), **r}
        print(f"[{n}/{len(rows)}] {r['status']:8} {it.get('name', '')} {r['af']} {r['detail']}")
        time.sleep(1.5)

    # 내 코드 = 가장 많이 쓰인 코드. 코드 없는 링크·다른 코드 링크를 따로 표시
    main_af = (Counter(r["af"] for r in results.values() if r["af"]).most_common(1) or [("", 0)])[0][0]
    for r in results.values():
        if r["status"] in ("broken",):
            continue
        if not r["af"]:
            r["status"], r["detail"] = "no_af", "파트너스 코드 없음 — 파트너스에서 만든 링크가 아님 (수익 안 잡힘)" + (f" · {r['detail']}" if r["detail"] else "")
        elif main_af and r["af"] != main_af:
            r["status"], r["detail"] = "other_af", f"다른 파트너스 코드 {r['af']} (대부분은 {main_af})" + (f" · {r['detail']}" if r["detail"] else "")

    out = {"checked_at": datetime.now(KST).isoformat(timespec="seconds"), "main_af": main_af,
           "counts": dict(Counter(r["status"] for r in results.values())), "results": results}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps(out["counts"], ensure_ascii=False), "main_af", main_af)

    # 액션 화면 요약
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        bad = [r for r in results.values() if r["status"] not in ("ok", "unknown")]
        with open(summary, "a", encoding="utf-8") as f:
            f.write(f"## 쿠팡 링크 점검 — 문제 {len(bad)}개 / {len(results)}개\n\n")
            for r in bad:
                f.write(f"- **{r['name']}** ({r['type']}) — {r['detail']}\n")
            if sample:  # 점검 방식 손볼 때 참고용 (짧은 링크 페이지 앞부분)
                f.write("\n<details><summary>짧은 링크 페이지 예시</summary>\n\n```html\n" + sample.replace("```", "") + "\n```\n</details>\n")


if __name__ == "__main__":
    main()
