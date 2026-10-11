#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pillow"]
# ///
"""Image processing before looking at and searching with a photo.

  zoom      crop a region, upscale and sharpen: read small text, count tracks, check plate background color
  edges     one upscaled image for each of the four edges and four corners — ropes in corners, a boat bow at the bottom, small road signs are the easiest to miss
  variants  variants for reverse image search: tight crop / horizontal flip / enhanced grayscale / color-cast removal / upscale; optional perspective rectification
  grid      cut into N×M tiles, for "search only a part" in reverse image search
  piers     take a brightness profile along a few rows below the bridge deck and find the pixel columns of the bridge piers (for back-solving the camera position)

Coordinates are always original-image pixels x0,y0,x1,y1 (top-left, bottom-right). Check the original image size first with `exif.py` or PIL.

Examples:
  imgprep.py zoom photo.jpg --box 820,40,1080,300 --scale 4 --out sign.png
  imgprep.py edges photo.jpg --out-dir edges/
  imgprep.py variants photo.jpg --box 300,120,900,760 --prefix left --out-dir v/     # → v/left_crop.jpg left_flip.jpg …
  imgprep.py variants photo.jpg --persp 312,140,880,95,905,770,290,720 --out-dir v/   # rectify four corners (top-left top-right bottom-right bottom-left)
  imgprep.py grid photo.jpg --rows 2 --cols 3 --out-dir tiles/
  imgprep.py piers photo.jpg --rows 926:940 --out cols.json --sheet piers.jpg

piers output JSON:
  {"image": path, "size": [W, H], "rows": [r0, r1], "cols": [x0, x1],
   "polarity": "bright" | "dark",            # whether piers are brighter or darker than their surroundings
   "params": {"min_gap": 20, "min_prominence": 12, "baseline": 61},
   "count": number of peaks,
   "piers": [{"col": 38, "prominence": 100.5, "dev": 92.4, "level": 183.2}, ...]}
  col is the pixel column (integer, original-image coordinates), prominence is the peak's topographic prominence (the main basis for judging real vs. false),
  dev is the height after baseline removal, level is the column's raw mean brightness over the rows range. piers are sorted by col ascending.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps, ImageStat


def _box(s: str) -> tuple[int, int, int, int]:
    x0, y0, x1, y1 = (int(float(v)) for v in s.split(","))
    return min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)


def zoom(im: Image.Image, box, scale: float) -> Image.Image:
    c = im.crop(box)
    c = c.resize((max(1, int(c.width * scale)), max(1, int(c.height * scale))), Image.LANCZOS)
    return c.filter(ImageFilter.UnsharpMask(radius=2, percent=120, threshold=2))


def gray_world(im: Image.Image) -> Image.Image:
    """Gray-world white balance: use when an old photo has a yellow or purple cast."""
    r, g, b = ImageStat.Stat(im.convert("RGB")).mean
    avg = (r + g + b) / 3
    chans = [ch.point(lambda v, k=avg / max(m, 1): max(0, min(255, int(v * k))))
             for ch, m in zip(im.convert("RGB").split(), (r, g, b))]
    return ImageOps.autocontrast(Image.merge("RGB", chans), cutoff=1)


def perspective(im: Image.Image, quad: list[float]) -> Image.Image:
    """Four corners (top-left top-right bottom-right bottom-left) → rectangle. Output width and height take the larger of each pair of opposite side lengths."""
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = (quad[i:i + 2] for i in range(0, 8, 2))
    w = int(max(((x1 - x0) ** 2 + (y1 - y0) ** 2) ** .5, ((x2 - x3) ** 2 + (y2 - y3) ** 2) ** .5))
    h = int(max(((x3 - x0) ** 2 + (y3 - y0) ** 2) ** .5, ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** .5))
    # PIL's QUAD transform: the output rectangle's four corners come, in order, from the source's top-left, bottom-left, bottom-right, top-right
    return im.transform((w, h), Image.QUAD, (x0, y0, x3, y3, x2, y2, x1, y1), Image.BICUBIC)


def _range(s: str) -> tuple[int, int]:
    """Parse "a:b" (a inclusive, b exclusive)."""
    a, b = s.split(":")
    a, b = int(float(a)), int(float(b))
    return (a, b) if a <= b else (b, a)


def _baseline(p, w: int):
    """Sliding median baseline: flattens slowly varying brightness such as the bridge body, sky and ground, leaving only thin vertical strips."""
    import numpy as np
    h = w // 2
    pad = np.pad(p, (h, h), mode="edge")
    return np.array([float(np.median(pad[i:i + w])) for i in range(len(p))])


def _prominence(d, i: int) -> float:
    """Topographic prominence of local maximum i: peak height minus the higher of the two valley floors it descends to on the left and right."""
    h = d[i]
    lo = h
    j = i
    while j > 0 and d[j - 1] <= h:
        j -= 1
        lo = min(lo, d[j])
    left = lo
    lo = h
    j = i
    while j < len(d) - 1 and d[j + 1] <= h:
        j += 1
        lo = min(lo, d[j])
    return float(h - max(left, lo))


def _peaks(d, min_gap: int, min_prominence: float) -> list[tuple[int, float]]:
    """Find peaks in d: prominence must first pass the threshold, then, from highest to lowest prominence, greedily keep those ≥ min_gap apart."""
    cand = [i for i in range(1, len(d) - 1) if d[i] >= d[i - 1] and d[i] > d[i + 1]]
    res = [(i, _prominence(d, i)) for i in cand]
    res = [(i, pr) for i, pr in res if pr >= min_prominence]
    res.sort(key=lambda t: -t[1])
    keep: list[tuple[int, float]] = []
    for i, pr in res:
        if all(abs(i - j) >= min_gap for j, _ in keep):
            keep.append((i, pr))
    keep.sort()
    return keep


def piers(im: Image.Image, rows: tuple[int, int], cols: tuple[int, int] | None,
          min_gap: int, min_prominence: float, baseline_win: int, polarity: str) -> dict:
    """Take each column's mean brightness over the rows below the bridge deck → subtract the sliding median baseline → find peaks = bridge pier pixel columns.

    In the shadow of a shaded bridge body, piers are usually brighter than their surroundings (polarity=bright); against the light or on overcast days it can be the reverse (dark);
    auto computes both and takes the one with the larger total prominence.
    """
    import numpy as np
    W, H = im.size
    r0, r1 = max(0, rows[0]), min(H, rows[1])
    if r1 - r0 < 1:
        raise SystemExit(f"--rows {rows[0]}:{rows[1]} selects no rows in a {W}x{H} image")
    x0, x1 = (0, W) if cols is None else (max(0, cols[0]), min(W, cols[1]))
    a = np.asarray(im.convert("L"), dtype=float)
    p = a[r0:r1, x0:x1].mean(axis=0)
    base = _baseline(p, max(3, baseline_win | 1))
    dev = p - base
    opts = {"bright": _peaks(dev, min_gap, min_prominence),
            "dark": _peaks(-dev, min_gap, min_prominence)} if polarity == "auto" \
        else {polarity: _peaks(dev if polarity == "bright" else -dev, min_gap, min_prominence)}
    pol = max(opts, key=lambda k: sum(pr for _, pr in opts[k]))
    sign = 1.0 if pol == "bright" else -1.0
    found = [{"col": int(i + x0), "prominence": round(pr, 2),
              "dev": round(float(dev[i]) * sign, 2), "level": round(float(p[i]), 2)}
             for i, pr in opts[pol]]
    return {"size": [W, H], "rows": [r0, r1], "cols": [x0, x1], "polarity": pol,
            "params": {"min_gap": min_gap, "min_prominence": min_prominence, "baseline": baseline_win},
            "count": len(found), "piers": found}


def piers_sheet(im: Image.Image, r: dict, out: Path) -> None:
    """Draw the sampled row band and each pier column (numbered) on the original image, so a person can check at a glance for extra or missing ones."""
    from PIL import ImageDraw
    sheet = im.copy()
    d = ImageDraw.Draw(sheet)
    r0, r1 = r["rows"]
    x0, x1 = r["cols"]
    d.rectangle([x0, r0, x1 - 1, r1 - 1], outline=(0, 200, 255), width=1)
    for n, pier in enumerate(r["piers"]):
        x = pier["col"]
        d.line([(x, max(0, r0 - 60)), (x, min(sheet.height, r1 + 60))], fill=(255, 0, 0), width=1)
        d.text((x + 2, max(0, r0 - 72)), str(n), fill=(255, 255, 0))
    sheet.save(out, quality=92)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    z = sub.add_parser("zoom")
    z.add_argument("image", type=Path)
    z.add_argument("--box", type=_box, required=True)
    z.add_argument("--scale", type=float, default=3)
    z.add_argument("--out", type=Path, required=True)

    e = sub.add_parser("edges")
    e.add_argument("image", type=Path)
    e.add_argument("--frac", type=float, default=0.18, help="edge strip as a fraction of the whole image, default 0.18")
    e.add_argument("--out-dir", type=Path, required=True)

    v = sub.add_parser("variants")
    v.add_argument("image", type=Path)
    v.add_argument("--box", type=_box, help="search only this region (removes sky and background)")
    v.add_argument("--persp", help="8 numbers: the four corners top-left top-right bottom-right bottom-left, rectified to a front view")
    v.add_argument("--prefix", help="output file name prefix; default is original name + crop box, so variants of different boxes don't overwrite each other")
    v.add_argument("--out-dir", type=Path, required=True)

    g = sub.add_parser("grid")
    g.add_argument("image", type=Path)
    g.add_argument("--rows", type=int, default=2)
    g.add_argument("--cols", type=int, default=2)
    g.add_argument("--overlap", type=float, default=0.15)
    g.add_argument("--out-dir", type=Path, required=True)

    pr = sub.add_parser("piers", help="find bridge pier pixel columns from the brightness profile of a few rows below the bridge deck",
                        formatter_class=argparse.RawDescriptionHelpFormatter, description="""\
Take the brightness profile along the --rows rows, subtract the sliding median baseline, and find peaks with prominence ≥ --min-prominence; the pixel columns of the peaks are the pier columns.
For sample rows, pick the rows below the bridge deck where the piers are exposed and the background (sky, distant view, water) is continuous; when the deck is tilted in the frame, widen the row band to cover both ends.

Output JSON (--out):
  {"image": path, "size": [W, H], "rows": [r0, r1], "cols": [x0, x1],   # cols is the column search range, not the structure columns
   "polarity": "bright" | "dark",            # whether piers are brighter or darker than their surroundings
   "params": {"min_gap": 20, "min_prominence": 12, "baseline": 61},
   "count": number of peaks,
   "piers": [{"col": 38, "prominence": 100.5, "dev": 92.4, "level": 183.2}, ...]}
  col is the pixel column (integer, original-image coordinates), prominence is the peak's prominence (the main basis for judging real vs. false),
  dev is the height after baseline removal, level is the column's raw mean brightness over the rows range. piers are sorted by col ascending.

This JSON can go straight to geo.py spacing --cols @cols.json, but **check --sheet first**:
drop non-pier peaks (bright foreground spots, railings, trees); structure segments broken by foreground occlusion must be separated with ';' when you hand-write the --cols string.""")
    pr.add_argument("image", type=Path)
    pr.add_argument("--rows", type=_range, required=True,
                    help='sample rows, "r0:r1" (r0 inclusive, r1 exclusive). Take the rows below the bridge deck where the piers are exposed; '
                         'look with zoom first; when the deck is tilted, widen the row band to cover both ends')
    pr.add_argument("--cols", type=_range, help='search only within this column range, "x0:x1"; default full width')
    pr.add_argument("--min-gap", type=int, default=20, help="minimum spacing in pixels between two pier columns, default 20")
    pr.add_argument("--min-prominence", type=float, default=12,
                    help="peak prominence threshold (0-255 gray level), default 12; lower gives extra false peaks, higher misses dense piers at the far end")
    pr.add_argument("--baseline", type=int, default=61,
                    help="window width of the sliding median baseline, default 61 px; larger than the pier spacing, smaller than the scale of brightness changes along the bridge body")
    pr.add_argument("--polarity", choices=["auto", "bright", "dark"], default="auto",
                    help="whether piers are brighter or darker than their surroundings, default auto (tries both, takes the one with the larger total prominence)")
    pr.add_argument("--out", type=Path, required=True, help="output JSON, structure at the top of --help")
    pr.add_argument("--sheet", type=Path, help="draw the row band and each column (numbered) on the original image, for a person to check")

    args = ap.parse_args()
    im = ImageOps.exif_transpose(Image.open(args.image)).convert("RGB")
    W, H = im.size

    if args.cmd == "zoom":
        zoom(im, args.box, args.scale).save(args.out)
        print(args.out)
        return

    if args.cmd == "piers":
        r = piers(im, args.rows, args.cols, args.min_gap, args.min_prominence, args.baseline, args.polarity)
        r = {"image": str(args.image), **r}
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(r, ensure_ascii=False), encoding="utf-8")
        print(f"rows {r['rows'][0]}:{r['rows'][1]}  cols {r['cols'][0]}:{r['cols'][1]}  "
              f"polarity {r['polarity']}  found {r['count']} columns")
        for n, pier in enumerate(r["piers"]):
            print(f"  {n:>2}  col {pier['col']:>5}  prominence {pier['prominence']:>6.1f}  brightness {pier['level']:>6.1f}")
        print("list: " + ",".join(str(p["col"]) for p in r["piers"]))
        print("Before feeding geo.py spacing, check --sheet: drop non-pier peaks (bright foreground spots, railings, trees); "
              "separate structure segments broken by foreground occlusion with ';', e.g. --cols '38,133,218;745,788,829'")
        print(args.out)
        if args.sheet:
            args.sheet.parent.mkdir(parents=True, exist_ok=True)
            piers_sheet(im, r, args.sheet)
            print(args.sheet)
        return

    args.out_dir.mkdir(parents=True, exist_ok=True)
    stem = args.image.stem
    if args.cmd == "variants":
        stem = args.prefix or (f"{stem}_{'-'.join(map(str, args.box))}" if args.box else stem)
    outs = []
    if args.cmd == "edges":
        fw, fh = int(W * args.frac), int(H * args.frac)
        regions = {"top": (0, 0, W, fh), "bottom": (0, H - fh, W, H), "left": (0, 0, fw, H), "right": (W - fw, 0, W, H),
                   "corner_tl": (0, 0, 2 * fw, 2 * fh), "corner_tr": (W - 2 * fw, 0, W, 2 * fh),
                   "corner_bl": (0, H - 2 * fh, 2 * fw, H), "corner_br": (W - 2 * fw, H - 2 * fh, W, H)}
        for name, box in regions.items():
            scale = max(1.0, 1600 / max(box[2] - box[0], box[3] - box[1]))
            p = args.out_dir / f"{stem}_{name}.jpg"
            zoom(im, box, scale).save(p, quality=92)
            outs.append(p)
    elif args.cmd == "variants":
        base = im
        if args.persp:
            base = perspective(im, [float(x) for x in args.persp.split(",")])
            p = args.out_dir / f"{stem}_persp.jpg"
            base.save(p, quality=95)
            outs.append(p)
        if args.box:
            base = base.crop(args.box)
            p = args.out_dir / f"{stem}_crop.jpg"
            base.save(p, quality=95)
            outs.append(p)
        for name, img in (("flip", ImageOps.mirror(base)),
                          ("gray", ImageOps.autocontrast(ImageOps.grayscale(base), cutoff=1)),
                          ("wb", gray_world(base))):
            p = args.out_dir / f"{stem}_{name}.jpg"
            img.save(p, quality=95)
            outs.append(p)
        if max(base.size) < 800:
            k = 1024 / max(base.size)
            p = args.out_dir / f"{stem}_up.jpg"
            base.resize((int(base.width * k), int(base.height * k)), Image.LANCZOS).save(p, quality=95)
            outs.append(p)
    elif args.cmd == "grid":
        tw, th = W / args.cols, H / args.rows
        ox, oy = tw * args.overlap, th * args.overlap
        for r in range(args.rows):
            for c in range(args.cols):
                box = (int(max(0, c * tw - ox)), int(max(0, r * th - oy)), int(min(W, (c + 1) * tw + ox)), int(min(H, (r + 1) * th + oy)))
                p = args.out_dir / f"{stem}_r{r}c{c}.jpg"
                im.crop(box).save(p, quality=92)
                outs.append(p)
    for p in outs:
        print(p)


if __name__ == "__main__":
    # Chinese-locale Windows outputs GBK by default: it crashes on m² or ñ, and any Chinese the agent reads comes out garbled
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    main()
