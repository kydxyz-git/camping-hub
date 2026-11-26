"""폰용 작은 사진 만들기 (사용자 261126 '사진 용량은 줄이되 PC 버전 모바일 버전 따로').

images/{series,camps,products}/파일 → images/m/{같은 폴더}/같은 이름.jpg
- 폰 카드에서 사진이 보이는 폭이 약 120px(화면 배율 2.6배면 약 320px)이라 가로 320px로 줄임.
- JPEG 품질 72·점진적(progressive). 투명 PNG는 흰 바탕에 합성.
- 작은 판이 없을 때만 만듦(사진은 바꿀 때 새 이름). 원본이 지워졌으면 작은 판도 지움.
- PC는 원본 그대로 씀. 원본은 건드리지 않음.
GitHub Actions(build-pages.yml)가 사진·데이터가 바뀔 때마다 돌린다.
"""
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLDERS = ["series", "camps", "products"]
WIDTH = 320
QUALITY = 72
EXT = (".jpg", ".jpeg", ".png", ".webp")


def make(src, dst):
    im = Image.open(src)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[-1])
        im = bg
    else:
        im = im.convert("RGB")
    if im.width > WIDTH:
        im = im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im.save(dst, "JPEG", quality=QUALITY, optimize=True, progressive=True)


def main():
    made = removed = 0
    before = after = 0
    for f in FOLDERS:
        src_dir = os.path.join(ROOT, "images", f)
        dst_dir = os.path.join(ROOT, "images", "m", f)
        names = set()
        for n in sorted(os.listdir(src_dir)) if os.path.isdir(src_dir) else []:
            if not n.lower().endswith(EXT):
                continue
            base = os.path.splitext(n)[0] + ".jpg"
            names.add(base)
            src, dst = os.path.join(src_dir, n), os.path.join(dst_dir, base)
            if os.path.exists(dst):   # 사진을 바꾸면 새 파일 이름으로 저장하는 규칙이라 '없을 때만' 만들면 됨 (Actions 체크아웃은 파일 시각이 다 같아서 시각 비교 안 씀)
                continue
            try:
                make(src, dst)
                made += 1
                before += os.path.getsize(src)
                after += os.path.getsize(dst)
            except Exception as e:  # 깨진 파일 하나가 전체를 멈추지 않게
                print(f"::warning::{f}/{n} 작은 판 못 만듦: {e}")
        if os.path.isdir(dst_dir):
            for n in os.listdir(dst_dir):
                if n not in names:
                    os.remove(os.path.join(dst_dir, n))
                    removed += 1
    print(f"폰용 사진 새로 {made}장 (원본 {before // 1024}KB → {after // 1024}KB), 지운 것 {removed}장")
    return 0


if __name__ == "__main__":
    sys.exit(main())
