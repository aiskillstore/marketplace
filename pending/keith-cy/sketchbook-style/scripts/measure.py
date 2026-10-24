"""Measure ink drawings like the reference set.
usage: python3 -I measure.py [--json] img1.png [img2 ...]
Each image: threshold (<128 = ink), crop to the drawing's bounding box, scale so the long side is 1024 px.
Reports per image and median:
  stroke  - typical line width in px at 1024 (median 2*d-1 over ridge pixels of the chessboard distance, fills excluded)
  stroke% - the same as % of 1024
  cover   - ink share of the bounding box
  solid   - share of ink lying in solid areas thicker than 24 px (survives 12 erosions, re-grown)
  sparse / dense / ratio - line width where the drawing is calm vs busy. Busyness = density of ink edges in a
            49 px window around each line (ridge) pixel. Line pixels are split into thirds by busyness within
            the image; sparse = mean width (2d-1) of the calmest third, dense = of the busiest third,
            ratio = sparse / dense (1.0 = same weight everywhere; > 1 = thicker lines where it is calm).
Reference numbers: see references/engines.md."""
import sys, json, statistics
import numpy as np
from PIL import Image

def erode(a):
    p = np.pad(a, 1, constant_values=False)
    out = a.copy()
    for dy in (0, 1, 2):
        for dx in (0, 1, 2):
            out &= p[dy:dy + a.shape[0], dx:dx + a.shape[1]]
    return out

def dilate(a):
    p = np.pad(a, 1, constant_values=False)
    out = a.copy()
    for dy in (0, 1, 2):
        for dx in (0, 1, 2):
            out |= p[dy:dy + a.shape[0], dx:dx + a.shape[1]]
    return out

def box_mean(a, r):
    """mean of a over a (2r+1)^2 window, via an integral image"""
    a = a.astype(np.float64)
    c = np.pad(a, ((r + 1, r), (r + 1, r)), mode="edge").cumsum(0).cumsum(1)
    n = 2 * r + 1
    return (c[n:, n:] - c[:-n, n:] - c[n:, :-n] + c[:-n, :-n]) / (n * n)

def measure(path):
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, "white"); bg.alpha_composite(im)
    g = np.asarray(bg.convert("L"))
    r = measure_mask(g < 128)
    if r: r["file"] = path.split("/")[-1]
    return r

def measure_mask(ink):
    """ink: bool array (True = ink) at any scale."""
    ys, xs = np.nonzero(ink)
    if len(xs) == 0: return None
    crop = Image.fromarray(((~ink[ys.min():ys.max() + 1, xs.min():xs.max() + 1]) * 255).astype(np.uint8))
    s = 1024 / max(crop.size)
    crop = crop.resize((max(1, round(crop.width * s)), max(1, round(crop.height * s))), Image.LANCZOS)
    a = np.asarray(crop) < 128
    d = np.zeros(a.shape, np.int16); cur = a.copy(); k = 0
    while cur.any() and k < 60:
        k += 1; d[cur] = k; cur = erode(cur)
    # ridge pixels: d >= every 8-neighbour
    p = np.pad(d, 1)
    ridge = a.copy()
    for dy in (0, 1, 2):
        for dx in (0, 1, 2):
            if dy == 1 and dx == 1: continue
            ridge &= d >= p[dy:dy + a.shape[0], dx:dx + a.shape[1]]
    line = ridge & (d < 12)
    vals = d[line]
    stroke = float(np.median(2 * vals - 1)) if len(vals) else 0.0
    sparse = dense = ratio = 0.0
    if len(vals) >= 30:
        edges = a & ~erode(a)
        busy = box_mean(edges, 24)[line]
        lo, hi = np.quantile(busy, [1 / 3, 2 / 3])
        w = (2 * vals - 1).astype(np.float64)
        if (busy <= lo).any() and (busy >= hi).any():
            sparse = float(w[busy <= lo].mean()); dense = float(w[busy >= hi].mean())
            ratio = sparse / dense if dense else 0.0
    core = d >= 12
    for _ in range(12): core = dilate(core)
    solid = float((core & a).sum() / max(1, a.sum()))
    return {"file": "", "stroke": round(stroke, 1), "stroke%": round(stroke / 10.24, 2),
            "cover": round(float(a.mean()), 3), "solid": round(solid, 3),
            "sparse": round(sparse, 2), "dense": round(dense, 2), "ratio": round(ratio, 2)}

if __name__ != "__main__": pass
else:
  args = [x for x in sys.argv[1:] if x != "--json"]
  rows = [r for r in (measure(f) for f in args) if r]
  if "--json" in sys.argv: print(json.dumps(rows, indent=1))
  else:
      for r in rows: print(f"{r['file'][:40]:40s} stroke {r['stroke']:5.1f}px ({r['stroke%']:.2f}%)  cover {r['cover']:.3f}  solid {r['solid']:.3f}  sparse {r['sparse']:.1f} dense {r['dense']:.1f} ratio {r['ratio']:.2f}")
  med = lambda k: statistics.median(r[k] for r in rows)
  q = lambda k, f: sorted(r[k] for r in rows)[int(f * (len(rows) - 1))]
  print(f"MEDIAN of {len(rows)}: stroke {med('stroke'):.1f}px ({med('stroke%'):.2f}%) [p10 {q('stroke%',.1):.2f}% p90 {q('stroke%',.9):.2f}%]  cover {med('cover'):.3f} [p10 {q('cover',.1):.3f} p90 {q('cover',.9):.3f}]  solid {med('solid'):.3f} [p90 {q('solid',.9):.3f}]  ratio {med('ratio'):.2f} [p10 {q('ratio',.1):.2f} p90 {q('ratio',.9):.2f}] (sparse {med('sparse'):.1f} / dense {med('dense'):.1f})")
