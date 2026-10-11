#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow", "numpy", "torch", "transformers", "socksio", "pysocks", "requests"]
# ///
"""Find a class of target on satellite imagery (running tracks, stadiums, factory buildings, silos, dams, bridges, open-pit mines, solar farms, greenhouses, ports):
split an area into a grid, score each cell with CLIP zero-shot and sort; you look only at the top 20–30 instead of paging through dozens of contact-sheet pages.

  grid     tile a bbox with a grid and score cell by cell → ranked.json + contact sheet of top-N thumbnails + score heatmap
  points   score and rank a given list of candidate points ({name: [lat, lon]} from osm.py buildings / poi.py) point by point
  presets  list the presets and their prompts

The score is an ordering by "how alike", not a verdict: you still have to look at the thumbnails of the top few, then check them against the bearing and shape in the photo.
Cells that are almost a single color (Google placeholder, no imagery) are marked blank and scored 0.
--seeds pois.json: cells near seed points (school, factory POIs) get a bonus; OSM in China maps few running tracks, but 360/Baidu POIs list schools very completely (poi.py).

Examples:
  sat_scan.py grid --bbox <s,w,n,e> --zoom 17 --cell 320 --preset track --top 30 --out ranked.json --sheet top.jpg --heat heat.jpg
  sat_scan.py grid --bbox <s,w,n,e> --preset factory --seeds factories.json --seed-radius 500 --out r.json --sheet r.jpg
  sat_scan.py points --points big_buildings.json --zoom 17 --preset silo --out r.json --sheet r.jpg
  sat_scan.py grid --bbox <s,w,n,e> --query "aerial view of a red running track" --neg "aerial view of houses" --out r.json
"""
from __future__ import annotations

import argparse
from _net import PROXY_HELP
from _net import model_proxy_env
import json
import math
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
import geo  # noqa: E402
import tiles  # noqa: E402

CLIP_ID = "openai/clip-vit-base-patch32"
NEG_COMMON = ["a satellite image of residential buildings and streets", "a satellite image of a road intersection",
              "a satellite image of farmland", "a satellite image of a river", "a satellite image of a parking lot",
              "a satellite image of forest", "a satellite image of a highway", "a satellite image of bare ground"]
PRESETS = {
    "track": (["a satellite image of a school running track", "an aerial view of an athletics track around a football field",
               "an oval red running track seen from above", "a sports ground with a red oval track and green field from above"],
              NEG_COMMON + ["a satellite image of a roundabout", "a satellite image of a swimming pool"]),
    "stadium": (["a satellite image of a large stadium", "an aerial view of a stadium with stands around a field"], NEG_COMMON),
    "factory": (["a satellite image of a large factory building with a long roof", "an aerial view of industrial warehouses",
                 "an aerial view of an industrial plant with big sheds"], NEG_COMMON + ["a satellite image of apartment blocks"]),
    "silo": (["a satellite image of grain silos and a drying tower", "an aerial view of a rice mill with silos",
              "an aerial view of a farm with round silos and long sheds"], NEG_COMMON),
    "dam": (["a satellite image of a dam with a reservoir", "an aerial view of a hydroelectric dam"], NEG_COMMON),
    "bridge": (["a satellite image of a bridge crossing a river", "an aerial view of a long bridge over water"], NEG_COMMON),
    "quarry": (["a satellite image of an open pit mine", "an aerial view of a quarry with terraces"], NEG_COMMON),
    "solar": (["a satellite image of a solar farm with rows of panels"], NEG_COMMON),
    "greenhouse": (["a satellite image of rows of greenhouses", "an aerial view of plastic greenhouses"], NEG_COMMON),
    "port": (["a satellite image of a port with container cranes", "an aerial view of a harbor with ships and piers"], NEG_COMMON),
    "school": (["a satellite image of a school campus with a running track and classroom buildings"], NEG_COMMON),
}


def _proxy_env(proxy: str | None) -> None:
    model_proxy_env(proxy)


def cell_image(lat: float, lon: float, zoom: int, size: int, source: str, proxy: str | None, cache: Path) -> Image.Image:
    """Stitch a size×size satellite image centered on (lat, lon) (reuses the tile cache)."""
    gx, gy = geo.ll2px(zoom, lat, lon)
    x0, y0 = gx - size / 2, gy - size / 2
    tile = Image.new("RGB", (size, size), "gray")
    for tx in range(int(x0 // 256), int((x0 + size) // 256) + 1):
        for ty in range(int(y0 // 256), int((y0 + size) // 256) + 1):
            p = cache / f"{source}_{zoom}_{tx}_{ty}.jpg"
            if tiles._get(tiles.SOURCES[source].format(x=tx, y=ty, z=zoom), p, proxy):
                try:
                    tile.paste(Image.open(p), (int(tx * 256 - x0), int(ty * 256 - y0)))
                except Exception:  # noqa: BLE001
                    pass
    return tile


def prefetch(points: dict, zoom: int, size: int, source: str, proxy: str | None, cache: Path) -> None:
    need = set()
    for lat, lon in points.values():
        gx, gy = geo.ll2px(zoom, lat, lon)
        x0, y0 = gx - size / 2, gy - size / 2
        for tx in range(int(x0 // 256), int((x0 + size) // 256) + 1):
            for ty in range(int(y0 // 256), int((y0 + size) // 256) + 1):
                need.add((tx, ty))
    cache.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(16) as ex:
        list(ex.map(lambda t: tiles._get(tiles.SOURCES[source].format(x=t[0], y=t[1], z=zoom), cache / f"{source}_{zoom}_{t[0]}_{t[1]}.jpg", proxy), need))


CLIPN = ([0.48145466, 0.4578275, 0.40821073], [0.26862954, 0.26130258, 0.27577711])


def _tensor(ims: list[Image.Image], torch):
    mean, std = (np.array(v, dtype=np.float32).reshape(1, 3, 1, 1) for v in CLIPN)
    arr = np.stack([np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0 for im in ims]).transpose(0, 3, 1, 2)
    return torch.from_numpy((arr - mean) / std)


def _feat(out):
    """In transformers 5, get_*_features returns BaseModelOutputWithPooling with the projected vector in pooler_output; older versions return the tensor directly."""
    if hasattr(out, "shape"):
        return out
    for k in ("pooler_output", "text_embeds", "image_embeds"):
        v = getattr(out, k, None)
        if v is not None and hasattr(v, "shape"):
            return v
    return out[0]


class Scorer:
    def __init__(self, pos: list[str], neg: list[str]):
        import torch
        from transformers import CLIPModel, CLIPTokenizer
        self.dev = "mps" if torch.backends.mps.is_available() else "cpu"
        t0 = time.time()
        try:
            tok = CLIPTokenizer.from_pretrained(CLIP_ID)
            self.model = CLIPModel.from_pretrained(CLIP_ID).to(self.dev).eval()
        except Exception as e:  # noqa: BLE001
            sys.exit(f"failed to load CLIP: {str(e)[:300]}\ncheck disk space, model availability and `doctor.py --network`.")
        self.torch = torch
        with torch.no_grad():
            t = tok(pos + neg, return_tensors="pt", padding=True).to(self.dev)
            tf = _feat(self.model.get_text_features(**t))
            self.text = (tf / tf.norm(dim=1, keepdim=True)).float()
        self.npos = len(pos)
        print(f"CLIP ready ({self.dev}, {time.time() - t0:.1f}s), {len(pos)} positive prompts, {len(neg)} negative prompts", file=sys.stderr)

    def score(self, ims: list[Image.Image], multi_scale: bool, batch: int = 48) -> np.ndarray:
        """Score per image = sum of positive-prompt probabilities (softmax over all prompts, logit scale 100); multi_scale also looks at 2×2 sub-blocks and takes the max."""
        views_per = 5 if multi_scale else 1
        flat = []
        for im in ims:
            im = im.convert("RGB")
            flat.append(im.resize((224, 224), Image.BICUBIC))
            if multi_scale:
                w, h = im.size
                for (a, b) in ((0, 0), (w // 2, 0), (0, h // 2), (w // 2, h // 2)):
                    flat.append(im.crop((a, b, a + w // 2, b + h // 2)).resize((224, 224), Image.BICUBIC))
        probs = []
        with self.torch.no_grad():
            for i in range(0, len(flat), batch):
                x = _tensor(flat[i:i + batch], self.torch).to(self.dev)
                f = _feat(self.model.get_image_features(pixel_values=x))
                f = f / f.norm(dim=1, keepdim=True)
                logits = 100.0 * f.float() @ self.text.T
                p = logits.softmax(dim=1)[:, : self.npos].sum(dim=1)
                probs.append(p.cpu().numpy())
        arr = np.concatenate(probs).reshape(len(ims), views_per)
        return arr.max(axis=1)


def _blank(im: Image.Image) -> bool:
    a = np.asarray(im.convert("L").resize((64, 64)), dtype=np.float32)
    return float(a.std()) < 6.0


def _sheet(rows: list[dict], ims: list[Image.Image], out: Path, cols: int, size: int) -> list[Path]:
    from baidu_pano import _font
    f = _font(14)
    per = cols * cols
    pages = []
    for pi in range(0, len(rows), per):
        chunk = rows[pi:pi + per]
        S = Image.new("RGB", (cols * size, ((len(chunk) + cols - 1) // cols) * size), "black")
        d = ImageDraw.Draw(S)
        for k, r in enumerate(chunk):
            cx, cy = (k % cols) * size, (k // cols) * size
            S.paste(ims[r["_i"]].resize((size, size)), (cx, cy))
            c = size / 2
            d.line([cx + c - 10, cy + c, cx + c + 10, cy + c], fill="red", width=2)
            d.line([cx + c, cy + c - 10, cx + c, cy + c + 10], fill="red", width=2)
            d.rectangle([cx, cy, cx + size, cy + 20], fill="black")
            d.text((cx + 4, cy + 3), f"#{r['rank']} {r['score']:.2f} {r['lat']:.5f},{r['lon']:.5f}" + (" seed" if r.get("seed_near") else ""), fill="yellow", font=f)
        o = out if pi == 0 else out.with_name(f"{out.stem}_{pi // per + 1}{out.suffix}")
        S.save(o, quality=88)
        pages.append(o)
    return pages


def _heat(rows: list[dict], names: list[str], out: Path) -> None:
    """Lay the cells out as a matrix by cell name rXXcYY, mapping score to color."""
    rc = {}
    for r in rows:
        m = re.match(r"r(\d+)c(\d+)", r["cell"])
        if m:
            rc[(int(m.group(1)), int(m.group(2)))] = r["score"]
    if not rc:
        return
    R = max(k[0] for k in rc) + 1
    C = max(k[1] for k in rc) + 1
    px = 24
    S = Image.new("RGB", (C * px, R * px), "black")
    d = ImageDraw.Draw(S)
    mx = max(rc.values()) or 1
    for (i, j), s in rc.items():
        v = s / mx
        d.rectangle([j * px, i * px, (j + 1) * px - 1, (i + 1) * px - 1], fill=(int(255 * v), int(120 * v), int(255 * (1 - v)) // 3))
    S.save(out)


def run(points: dict, args) -> None:
    _proxy_env(args.proxy)
    cache = Path(args.cache)
    if args.preset:
        pos, neg = PRESETS[args.preset]
    else:
        pos, neg = [], list(NEG_COMMON)
    pos = list(pos) + list(args.query or [])
    neg = list(neg) + list(args.neg or [])
    if not pos:
        sys.exit("give --preset or --query")
    t0 = time.time()
    prefetch(points, args.zoom, args.size, args.source, args.proxy, cache)
    names = list(points)
    with ThreadPoolExecutor(8) as ex:
        ims = list(ex.map(lambda n: cell_image(points[n][0], points[n][1], args.zoom, args.size, args.source, args.proxy, cache), names))
    t1 = time.time()
    sc = Scorer(pos, neg)
    scores = sc.score(ims, args.multi_scale)
    t2 = time.time()
    seeds = json.loads(Path(args.seeds).read_text(encoding="utf-8")) if args.seeds else {}
    rows = []
    for i, n in enumerate(names):
        lat, lon = points[n]
        blank = _blank(ims[i])
        s = 0.0 if blank else float(scores[i])
        near = None
        if seeds:
            for sn, sl in seeds.items():
                if geo.distance((lat, lon), (sl[0], sl[1])) <= args.seed_radius:
                    near = sn
                    s += args.seed_bonus
                    break
        rows.append({"cell": n, "lat": lat, "lon": lon, "score": round(s, 4), "blank": blank, "seed_near": near, "_i": i})
    rows.sort(key=lambda r: -r["score"])
    for k, r in enumerate(rows):
        r["rank"] = k + 1
    print(f"{len(names)} cells; fetch {t1 - t0:.1f}s, scoring {t2 - t1:.1f}s; blank cells {sum(1 for r in rows if r['blank'])}")
    print(f"{'#':>3} {'score':>6}  cell/name          lat,lon")
    for r in rows[: min(args.top, 20)]:
        print(f"{r['rank']:>3} {r['score']:>6.3f}  {str(r['cell'])[:18]:<18} {r['lat']:.5f},{r['lon']:.5f}" + (f"  near {r['seed_near']}" if r["seed_near"] else ""))
    if args.out:
        Path(args.out).write_text(json.dumps([{k: v for k, v in r.items() if k != "_i"} for r in rows], ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"-> {args.out}")
        pts = {f"#{r['rank']} {r['score']:.2f}": [r["lat"], r["lon"]] for r in rows[: args.top]}
        Path(args.out).with_suffix(".top.json").write_text(json.dumps(pts, ensure_ascii=False, indent=1), encoding="utf-8")
    if args.sheet:
        for p in _sheet(rows[: args.top], ims, Path(args.sheet), args.cols, args.size):
            print(f"-> {p}")
    if getattr(args, "heat", None):
        _heat(rows, names, Path(args.heat))
        print(f"-> {args.heat} (rows north to south, columns west to east; brighter = more alike)")


def _neg_coords(argv: list[str]) -> list[str]:
    return [" " + a if re.match(r"^-\d[\d.]*(,-?[\d.]+)+$", a) else a for a in argv]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(sp):
        sp.add_argument("--preset", choices=list(PRESETS))
        sp.add_argument("--query", action="append", help="custom positive prompt (English), repeatable")
        sp.add_argument("--neg", action="append", help="custom negative prompt, repeatable")
        sp.add_argument("--zoom", type=int, default=17)
        sp.add_argument("--size", "--cell", dest="size", type=int, default=320, help="pixels per cell")
        sp.add_argument("--multi-scale", action="store_true", help="also look at 2×2 sub-blocks of each cell and take the max (for small targets)")
        sp.add_argument("--seeds", help="{name:[lat,lon]} seed points; nearby cells get a bonus")
        sp.add_argument("--seed-radius", type=float, default=400)
        sp.add_argument("--seed-bonus", type=float, default=0.15)
        sp.add_argument("--top", type=int, default=30)
        sp.add_argument("--cols", type=int, default=5)
        sp.add_argument("--out")
        sp.add_argument("--sheet")
        sp.add_argument("--source", choices=list(tiles.SOURCES), default="google")
        sp.add_argument("--proxy", default=os.environ.get("GEO_PROXY"), help=PROXY_HELP)
        sp.add_argument("--cache", type=Path, default=Path(".geo-cache/tiles"))

    g = sub.add_parser("grid")
    g.add_argument("--bbox", required=True, help="s,w,n,e")
    g.add_argument("--step", type=float, help="cell spacing in meters; default is 90%% of the width each cell covers")
    g.add_argument("--heat", help="score heatmap output")
    common(g)

    p = sub.add_parser("points")
    p.add_argument("--points", required=True, help="{name: [lat, lon]}")
    common(p)

    sub.add_parser("presets")

    args = ap.parse_args(_neg_coords(sys.argv[1:]))
    if args.cmd == "presets":
        for k, (pos, neg) in PRESETS.items():
            print(f"{k}:\n  + " + "\n  + ".join(pos) + f"\n  - {len(neg)} negative prompts")
        return
    if args.cmd == "grid":
        pts = tiles.grid_points(args.bbox, args.zoom, args.size, args.step)
        print(f"grid: {len(pts)} cells (r rows north to south, c columns west to east)")
    else:
        pts = json.loads(Path(args.points).read_text(encoding="utf-8"))
    run(pts, args)


if __name__ == "__main__":
    # Chinese-locale Windows writes GBK by default: m², ñ make it crash, and the Chinese the agent reads comes out garbled
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    main()
