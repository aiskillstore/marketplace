#!/usr/bin/env python3
# /// script
# dependencies = ["pillow"]
# ///
"""原作并排：左边是 fetch_reference.py 拉的原作（最多 3 幅），右边是我们渲出的静帧，一张图，肉眼对签名。

uv run side_by_side.py --ref 参考/giotto --frame 渲染/38_giotto/t003.00.png --out 对照/38_giotto.jpg [--title "乔托 v2"]

打分前必须出这张图。「一眼认得出是谁的画」这一问，只能拿着原作回答，不能凭记忆。
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def font(size=16):
    for f in ('/System/Library/Fonts/PingFang.ttc', '/System/Library/Fonts/STHeiti Medium.ttc', '/System/Library/Fonts/Hiragino Sans GB.ttc', '/Library/Fonts/Arial Unicode.ttf'):
        try:
            return ImageFont.truetype(f, size)
        except Exception:
            pass
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ref', required=True, help='fetch_reference.py 的输出目录')
    ap.add_argument('--frame', required=True, nargs='+', help='我们渲出的静帧（可多张）')
    ap.add_argument('--out', required=True)
    ap.add_argument('--title', default='')
    a = ap.parse_args()
    refs = sorted(p for p in Path(a.ref).glob('*.jpg') if p.name != '接触表.jpg')[:3]
    H = 480
    tiles = []
    for p in refs:
        im = Image.open(p).convert('RGB'); im = im.resize((int(im.width * H / im.height), H)); tiles.append((im, '原作 ' + p.stem[3:30]))
    ours = []
    for f in a.frame:
        im = Image.open(f).convert('RGB'); im = im.resize((int(im.width * H / im.height), H)); ours.append((im, '我们 ' + Path(f).stem))
    row = tiles + ours
    W = sum(i.width for i, _ in row) + 8 * (len(row) + 1)
    sheet = Image.new('RGB', (W, H + 56), (24, 24, 24)); d = ImageDraw.Draw(sheet); x = 8
    if a.title:
        d.text((8, 4), a.title, fill=(255, 255, 255), font=font(18))
    for im, cap in row:
        sheet.paste(im, (x, 28)); d.text((x, H + 34), cap, fill=(255, 210, 120) if cap.startswith('我们') else (170, 200, 255), font=font(15)); x += im.width + 8
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(a.out, quality=90)
    print('->', a.out)


main()
