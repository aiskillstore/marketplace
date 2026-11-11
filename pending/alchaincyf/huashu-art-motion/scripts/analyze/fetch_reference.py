#!/usr/bin/env python3
# /// script
# dependencies = ["pillow"]
# ///
"""原作锚定：从维基共享资源按关键词拉公版原作，存本地，并抽主色板、出接触表。

做新风格演示前先跑它：看原作、记签名特征、拿真实色值，不凭印象画「受启发的扁平插画」。

uv run fetch_reference.py --out 参考/ostia "Giotto Lamentation Scrovegni" "Giotto Meeting at the Golden Gate" [--n 1] [--colors 8]

每个查询取前 n 张（默认 1）宽 1600 的缩略图，存为 <out>/<序号>_<标题>.jpg，
同时写 <out>/参考.md（来源 URL、主色 hex）和 <out>/接触表.jpg。
只用公版作品（作者卒年 70 年以上的原作翻拍）；脚本不判断版权，调用者自己确认。
拉完必须看接触表，核对三件事：①是不是这位画家的作品（搜索会混入地图、现代照片、博物馆墙上的翻拍）②是不是三幅不同的作品（脚本只去掉近似图）③哪些是带框的翻拍（色板已取中央 80%，但构图判断仍要自己看）。
"""
import argparse, json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw

UA = {'User-Agent': 'art-motion-research/1.0 (https://github.com/alchaincyf/huashu-art-motion)'}


def get(url, timeout=60, tries=4):
    # 维基共享资源偶尔 SSL EOF：重试几次再报错
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                return r.read()
        except Exception as e:
            if k == tries - 1:
                raise
            time.sleep(1.5 * (k + 1))


def api(**kw):
    return json.loads(get('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode({**kw, 'format': 'json'})))


def search(q, n):
    d = api(action='query', generator='search', gsrsearch=f'{q} filetype:bitmap', gsrnamespace=6, gsrlimit=n + 4,
            prop='imageinfo', iiprop='url|size', iiurlwidth=1600)
    pages = sorted(d.get('query', {}).get('pages', {}).values(), key=lambda p: p.get('index', 0))
    out = []
    for p in pages:
        ii = (p.get('imageinfo') or [{}])[0]
        if ii.get('thumburl') and ii.get('width', 0) >= 900:
            out.append((p['title'].removeprefix('File:'), ii['thumburl'], ii.get('descriptionurl', '')))
        if len(out) >= n:
            break
    return out


def palette(im, k):
    w, h = im.size; im = im.crop((int(w * .1), int(h * .1), int(w * .9), int(h * .9)))   # 去掉画框、墙、页边：只在中央 80% 里抽色
    q = im.convert('RGB').resize((200, 200)).quantize(colors=k, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()[:k * 3]
    cnt = sorted(q.getcolors(), reverse=True)
    return ['#%02x%02x%02x' % tuple(pal[i * 3:i * 3 + 3]) + f' {c / 400:.0f}%' for c, i in cnt]


def ahash(im):
    from PIL import ImageOps
    g = ImageOps.autocontrast(im.convert('L').resize((16, 16)), cutoff=2)       # 先拉对比：调色增强版和原图才会落到同一个哈希附近
    px = list(g.tobytes()); m = sum(px) / 256
    return sum((1 << i) for i, v in enumerate(px) if v > m)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('queries', nargs='+')
    ap.add_argument('--out', required=True)
    ap.add_argument('--n', type=int, default=1)
    ap.add_argument('--colors', type=int, default=8)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    rows, md, seen = [], ['# 原作参考\n'], []
    for q in a.queries:
        hits = search(q, a.n)
        if not hits:
            print(f'!! 没搜到：{q}', file=sys.stderr); continue
        for title, url, page in hits:
            fn = out / (f'{len(rows) + 1:02d}_' + re.sub(r'[^\w]+', '_', title)[:50] + '.jpg')
            fn.write_bytes(get(url, 90))
            im = Image.open(fn)
            hv = ahash(im)
            if any(bin(hv ^ h2).count('1') <= 40 for h2 in seen):                      # 同一幅的另一个翻拍/调色版：丢掉，不凑数
                fn.unlink(); print('dup  ', title, '（与已取的某幅近似，已丢弃）'); continue
            seen.append(hv)
            rows.append((fn, im.copy()))
            md.append(f'- {fn.name}\n  - 来源：{page}\n  - 主色：{"、".join(palette(im, a.colors))}')
            print('ok', fn.name)
    if rows:
        W, H, cols = 640, 400, 3
        sheet = Image.new('RGB', (W * cols, H * ((len(rows) + cols - 1) // cols)), 'white')
        for i, (fn, im) in enumerate(rows):
            t = im.convert('RGB'); t.thumbnail((W, H))
            sheet.paste(t, ((i % cols) * W, (i // cols) * H))
            ImageDraw.Draw(sheet).text(((i % cols) * W + 6, (i // cols) * H + 6), fn.stem[:40], fill=(255, 0, 0))
        sheet.save(out / '接触表.jpg', quality=88)
    (out / '参考.md').write_text('\n'.join(md) + '\n')


main()
