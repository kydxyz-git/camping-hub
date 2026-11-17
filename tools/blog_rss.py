#!/usr/bin/env python3
"""네이버 블로그 RSS(blog.naver.com/kydz) → data/blog_posts.json (올린 글 달력용, 261117)
글 제목·날짜·주소·카테고리만 (공개 정보). 지난 기록은 지우지 않고 합친다 — RSS는 최근 글만 나와서."""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html import unescape

BLOG_ID = "kydz"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "blog_posts.json")
KST = timezone(timedelta(hours=9))


def tag(item, name):
    m = re.search(rf"<{name}>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</{name}>", item, re.S)
    return unescape(m[1].strip()) if m else ""


def main():
    req = urllib.request.Request(f"https://rss.blog.naver.com/{BLOG_ID}.xml", headers={"User-Agent": "Mozilla/5.0 (kydz blog calendar)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        xml = r.read().decode("utf-8", "replace")
    found = []
    for it in re.findall(r"<item>(.*?)</item>", xml, re.S):
        link = re.sub(r"\?.*$", "", tag(it, "link"))
        try:
            at = parsedate_to_datetime(tag(it, "pubDate")).astimezone(KST).isoformat(timespec="minutes")
        except (TypeError, ValueError):
            continue
        no = (re.search(r"/(\d+)$", link) or [None, ""])[1]
        found.append({"id": no or link, "at": at, "title": tag(it, "title"), "category": tag(it, "category"), "url": link})
    try:
        old = json.load(open(OUT, encoding="utf-8")).get("posts", [])
    except (OSError, ValueError):
        old = []
    by = {p["id"]: p for p in old}
    for p in found:
        by[p["id"]] = p
    posts = sorted(by.values(), key=lambda p: p["at"], reverse=True)
    same = [p["id"] for p in posts] == [p["id"] for p in old] and all(by[p["id"]] == p for p in old)
    # 새 글이 없어도 확인 시각(checked_at)은 남김 — 오늘 돌았는지 예비 실행이 이걸로 판단 (261118)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"blog": BLOG_ID, "checked_at": datetime.now(KST).isoformat(timespec="minutes"), "posts": posts}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(("바뀐 것 없음 — 확인 시각만" if same else f"블로그 글 {len(posts)}개") + f" (RSS {len(found)}개)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
