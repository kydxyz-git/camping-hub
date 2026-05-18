#!/usr/bin/env python3
"""
sitemap.xml lastmod 일괄 갱신 스크립트

용도: 콘텐츠 동기화 시 sitemap의 모든 lastmod를 오늘 날짜로 갱신
사용: python3 tools/update_sitemap.py
       python3 tools/update_sitemap.py --date 2026-05-17  # 특정 날짜 지정
"""
import re
import sys
import argparse
import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITEMAP_PATH = REPO_ROOT / 'sitemap.xml'


def update_sitemap_lastmod(date_str: str) -> int:
    """sitemap.xml의 모든 <lastmod>를 date_str로 변경. 변경된 개수 반환."""
    if not SITEMAP_PATH.exists():
        print(f'❌ sitemap.xml 없음: {SITEMAP_PATH}')
        sys.exit(1)

    content = SITEMAP_PATH.read_text(encoding='utf-8')
    pattern = re.compile(r'<lastmod>\d{4}-\d{2}-\d{2}</lastmod>')
    matches = pattern.findall(content)
    new_content = pattern.sub(f'<lastmod>{date_str}</lastmod>', content)

    if new_content == content:
        print(f'⏭  변경 없음 (이미 {date_str} 또는 lastmod 미존재)')
        return 0

    SITEMAP_PATH.write_text(new_content, encoding='utf-8')
    print(f'✅ sitemap.xml lastmod {len(matches)}개 → {date_str}')
    return len(matches)


def main():
    parser = argparse.ArgumentParser(description='Update sitemap.xml lastmod')
    parser.add_argument('--date', help='YYYY-MM-DD (기본: 오늘 KST)')
    args = parser.parse_args()

    if args.date:
        date_str = args.date
    else:
        # KST(UTC+9) 기준 오늘
        kst = datetime.timezone(datetime.timedelta(hours=9))
        date_str = datetime.datetime.now(kst).strftime('%Y-%m-%d')

    update_sitemap_lastmod(date_str)


if __name__ == '__main__':
    main()
