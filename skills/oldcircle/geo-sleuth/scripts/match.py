#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow", "numpy", "torch", "transformers", "opencv-python-headless", "socksio", "pysocks", "requests"]
# ///
"""Similarity ranking of a photo against a batch of candidate real-scene images (street-view renders, satellite thumbnails, reference images): the machine ranks first, you look only at the top few.

Uses:
- Street-view confirmation: with dozens to hundreds of candidate panorama points, sort by similarity first and open only the top 10 to compare invariant features.
- Satellite thumbnails: compare the top-down views of candidate points with the top-down features visible in the photo (weaker than street view; coarse ranking only).
- Reference library: compare reference images of bus liveries, streetlight styles, etc. with crops of the photo.

  rank    score and rank the candidates, output ranked.json + contact sheet of the top N
  index   save embeddings of a batch of images to disk (reused repeatedly within the same city)

Candidate source, pick one of three:
  --images <dir or glob>                          existing images, file name is the id
  --items <.index.json> --render baidu|gsv      index written by baidu_pano.py sheet/sample or gsv.py sheet, rendered item by item
  --panos panos.json --toward lat,lon | --headings 0,60,…   output of baidu_pano.py scan, rendered by heading (can add --within, --spread)

Scoring:
  global descriptor DINOv2 (facebook/dinov2-small, CLS + patch mean) or CLIP (openai/clip-vit-base-patch32) cosine similarity;
  --refine sift re-ranks the top --refine-top by SIFT + RANSAC inlier count (only inliers ≥ 15 count as geometric consistency).
  Final order: those with inliers by inlier count, the rest by global score. Scores are only for ordering; whether it is the same place still requires you to compare ≥3 invariant features.

On first use the model downloads from HuggingFace and is cached in ~/.cache/huggingface.

Examples:
  match.py rank --query photo.jpg --panos panos.json --toward <lat,lon> --spread 15 --refine sift --top 10 --out ranked.json --sheet ranked.jpg
  match.py rank --query photo.jpg --query-box 200,100,900,700 --items around.index.json --render baidu --spread-headings -30,0,30 --out r.json --sheet r.jpg
  match.py rank --query photo.jpg --images cands/ --method clip --out r.json
  match.py index --images city_panos/ --out city.npz
"""
from __future__ import annotations

import argparse
from _net import PROXY_HELP
from _net import model_proxy_env
import glob
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

MODELS = {"dino": "facebook/dinov2-small", "clip": "openai/clip-vit-base-patch32"}


def _proxy_env(proxy: str | None) -> None:
    model_proxy_env(proxy)


def _device():
    import torch
    return "mps" if torch.backends.mps.is_available() else "cpu"


IMNET = ([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
CLIPN = ([0.48145466, 0.4578275, 0.40821073], [0.26862954, 0.26130258, 0.27577711])


def _tensor(ims: list[Image.Image], norm: tuple, torch):
    """PIL 224×224 → (N,3,224,224) normalized tensor. Does its own preprocessing, no torchvision dependency."""
    mean, std = (np.array(v, dtype=np.float32).reshape(1, 3, 1, 1) for v in norm)
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


class Embedder:
    """Global descriptor. dino: DINOv2 CLS + patch mean; clip: image-tower embedding."""

    def __init__(self, method: str):
        import torch
        from transformers import AutoModel, CLIPModel
        self.method = method
        self.dev = _device()
        t0 = time.time()
        try:
            self.model = (CLIPModel if method == "clip" else AutoModel).from_pretrained(MODELS[method]).to(self.dev).eval()
        except Exception as e:  # noqa: BLE001
            sys.exit(f"failed to load model {MODELS[method]}: {str(e)[:300]}\n"
                     f"check disk space, model availability and `doctor.py --network`.")
        self.torch = torch
        print(f"model {MODELS[method]} ready ({self.dev}, {time.time() - t0:.1f}s)", file=sys.stderr)

    def _views(self, im: Image.Image, multi: bool) -> list[Image.Image]:
        im = im.convert("RGB")
        vs = [im.resize((224, 224), Image.BICUBIC)]
        if multi:
            w, h = im.size
            s = min(w, h)
            vs.append(im.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2)).resize((224, 224), Image.BICUBIC))
            # left and right halves: when the street view and the photo viewpoints are offset, the overlapping half matches better
            vs.append(im.crop((0, 0, int(w * 0.6), h)).resize((224, 224), Image.BICUBIC))
            vs.append(im.crop((int(w * 0.4), 0, w, h)).resize((224, 224), Image.BICUBIC))
        return vs

    def embed(self, ims: list[Image.Image], multi: bool = False, batch: int = 32) -> np.ndarray:
        """Returns (N, V, D): normalized vectors for the V views of each image."""
        views = [self._views(im, multi) for im in ims]
        flat = [v for vs in views for v in vs]
        out = []
        with self.torch.no_grad():
            for i in range(0, len(flat), batch):
                chunk = flat[i:i + batch]
                if self.method == "clip":
                    x = _tensor(chunk, CLIPN, self.torch).to(self.dev)
                    f = _feat(self.model.get_image_features(pixel_values=x))
                else:
                    x = _tensor(chunk, IMNET, self.torch).to(self.dev)
                    h = self.model(pixel_values=x).last_hidden_state
                    f = self.torch.cat([h[:, 0], h[:, 1:].mean(1)], dim=1)
                f = f / f.norm(dim=1, keepdim=True)
                out.append(f.float().cpu().numpy())
        arr = np.concatenate(out, 0)
        nv = len(views[0]) if views else 1
        return arr.reshape(len(ims), nv, -1)


def sift_inliers(a: Image.Image, b: Image.Image, max_side: int = 1024) -> tuple[int, int]:
    """Inlier count (and match count) from SIFT + ratio test + RANSAC homography."""
    import cv2

    def prep(im):
        im = im.convert("L")
        s = max_side / max(im.size)
        if s < 1:
            im = im.resize((int(im.width * s), int(im.height * s)), Image.BICUBIC)
        return np.array(im)

    sift = cv2.SIFT_create(nfeatures=3000)
    ka, da = sift.detectAndCompute(prep(a), None)
    kb, db = sift.detectAndCompute(prep(b), None)
    if da is None or db is None or len(ka) < 8 or len(kb) < 8:
        return 0, 0
    m = cv2.BFMatcher().knnMatch(da, db, k=2)
    good = [x[0] for x in m if len(x) == 2 and x[0].distance < 0.75 * x[1].distance]
    if len(good) < 8:
        return 0, len(good)
    pa = np.float32([ka[g.queryIdx].pt for g in good])
    pb = np.float32([kb[g.trainIdx].pt for g in good])
    _, mask = cv2.findHomography(pa, pb, cv2.RANSAC, 6.0)
    return (int(mask.sum()) if mask is not None else 0), len(good)


# ---------------------------------------------------------------- candidate sources

def _items_from_panos(args) -> list[dict]:
    import baidu_pano as bp
    panos = json.loads(Path(args.panos).read_text(encoding="utf-8"))
    if args.within:
        wl, wo, wr = (float(v) for v in args.within.split(","))
        panos = {k: v for k, v in panos.items() if geo.distance((wl, wo), tuple(v["wgs"])) <= wr}
    if args.spread:
        panos = bp.thin(panos, args.spread)
    target = tuple(float(v) for v in args.toward.split(",")) if args.toward else None
    items = []
    for pid, v in panos.items():
        heads = [float(x) for x in args.headings.split(",")] if args.headings else (
            [geo.bearing(tuple(v["wgs"]), target) + args.offset] if target else None)
        if heads is None:
            sys.exit("--panos needs --toward or --headings")
        for hd in heads:
            items.append({"id": pid, "heading": hd % 360, "pitch": args.pitch, "fov": args.fov, "wgs": v["wgs"],
                          "road": v.get("road", ""), "date": v.get("date", "")})
    return items


def _render_items(items: list[dict], engine: str, proxy: str | None, cache: Path) -> list[Image.Image | None]:
    if engine == "gsv":
        import gsv
        def one(it):
            try:
                return gsv.render(it["id"], it["heading"], it.get("pitch", 0), it.get("fov", 90), 640, 480, proxy, cache / "gsv")
            except Exception:  # noqa: BLE001
                return None
    else:
        import baidu_pano as bp
        def one(it):
            try:
                return bp.render(it["id"], it["heading"], it.get("pitch", 10), it.get("fov", 80), cache=cache / "pano", proxy=proxy)
            except Exception:  # noqa: BLE001
                return None
    with ThreadPoolExecutor(12) as ex:
        return list(ex.map(one, items))


def _load_candidates(args) -> tuple[list[dict], list[Image.Image]]:
    cache = Path(args.cache)
    if args.images:
        p = Path(args.images)
        files = sorted(p.glob("*.jp*g")) + sorted(p.glob("*.png")) if p.is_dir() else [Path(x) for x in sorted(glob.glob(args.images))]
        if not files:
            sys.exit(f"--images has no images: {args.images}")
        items = [{"id": f.stem, "file": str(f)} for f in files]
        return items, [Image.open(f) for f in files]
    if args.items:
        items = json.loads(Path(args.items).read_text(encoding="utf-8"))
        if args.spread_headings:
            ds = [float(x) for x in args.spread_headings.split(",")]
            items = [dict(it, heading=(it["heading"] + d) % 360) for it in items for d in ds]
    elif args.panos:
        items = _items_from_panos(args)
    else:
        sys.exit("candidate source: pick one of --images / --items / --panos")
    if len(items) > args.max_candidates:
        if args.toward and all(it.get("wgs") for it in items):
            tgt = tuple(float(v) for v in args.toward.split(","))
            items.sort(key=lambda it: geo.distance(tuple(it["wgs"]), tgt))
            how = "nearest to the --toward target first"
        else:
            how = "in list order"
        print(f"{len(items)} candidates, more than --max-candidates {args.max_candidates}; taking {args.max_candidates} {how} (narrow first with --within/--spread)", file=sys.stderr)
        items = items[: args.max_candidates]
    engine = args.render or ("gsv" if items and str(items[0].get("id", "")).startswith(("CAoS", "CIHM")) or len(str(items[0].get("id", ""))) == 22 else "baidu")
    ims = _render_items(items, engine, args.proxy, cache)
    ok_items, ok_ims = [], []
    for it, im in zip(items, ims):
        if im is not None:
            ok_items.append(it)
            ok_ims.append(im)
    if not ok_ims:
        sys.exit("not a single candidate rendered: check panorama ids, coverage and service availability with doctor.py --network")
    if len(ok_ims) < len(items):
        print(f"{len(items) - len(ok_ims)} failed to render, skipped", file=sys.stderr)
    return ok_items, ok_ims


def _sheet(rows: list[dict], ims: dict, out: Path, cols: int = 3, tw: int = 480, th: int = 360) -> None:
    from baidu_pano import _font
    n = len(rows)
    S = Image.new("RGB", (cols * tw, max(1, (n + cols - 1) // cols) * th), "black")
    d = ImageDraw.Draw(S)
    f = _font(16)
    for i, r in enumerate(rows):
        x, y = (i % cols) * tw, (i // cols) * th
        S.paste(ims[r["id_key"]].convert("RGB").resize((tw, th)), (x, y))
        t = f"#{r['rank']} inliers {r['inliers'] if r['inliers'] is not None else '-'} global {r['score_global']:.3f} …{str(r['id'])[-9:]}"
        if r.get("heading") is not None:
            t += f" h{r['heading']:.0f}"
        d.rectangle([x, y, x + tw, y + 22], fill="black")
        d.text((x + 4, y + 2), t, fill="yellow", font=f)
    S.save(out, quality=88)


def cmd_rank(args) -> None:
    _proxy_env(args.proxy)
    q = Image.open(args.query)
    if args.query_box:
        x0, y0, x1, y1 = (int(float(v)) for v in args.query_box.split(","))
        q = q.crop((x0, y0, x1, y1))
    items, ims = _load_candidates(args)
    t0 = time.time()
    methods = ["dino", "clip"] if args.method == "both" else [args.method]
    sims = np.zeros(len(ims))
    for m in methods:
        emb = Embedder(m)
        qf = emb.embed([q], multi=True)[0]              # (V, D)
        cf = emb.embed(ims, multi=False)[:, 0]          # (N, D)
        s = (cf @ qf.T).max(axis=1)                     # each candidate takes its max similarity over the query's views
        sims += s / len(methods)
    order = np.argsort(-sims)
    rows = []
    for rk, i in enumerate(order):
        it = items[i]
        rows.append({"rank": rk + 1, "id": it.get("id"), "id_key": i, "file": it.get("file"), "score_global": round(float(sims[i]), 4),
                     "inliers": None, "matches": None, "heading": it.get("heading"), "wgs": it.get("wgs"),
                     "road": it.get("road", ""), "date": it.get("date", ""), "label": it.get("label", "")})
    t1 = time.time()
    if args.refine != "none":
        top = rows[: args.refine_top]
        def one(r):
            return sift_inliers(q, ims[r["id_key"]])
        with ThreadPoolExecutor(4) as ex:
            for r, (inl, mt) in zip(top, ex.map(one, top)):
                r["inliers"], r["matches"] = inl, mt
        rows.sort(key=lambda r: (-(r["inliers"] or 0) if (r["inliers"] or 0) >= args.min_inliers else 0, -r["score_global"]))
        for k, r in enumerate(rows):
            r["rank"] = k + 1
    t2 = time.time()
    out_rows = rows[: args.top]
    print(f"{len(ims)} candidates; global scoring {t1 - t0:.1f}s, refinement {t2 - t1:.1f}s")
    print(f"{'#':>3} {'inliers':>7} {'global':>7}  id / heading / position")
    for r in out_rows:
        pos = f"{r['wgs'][0]:.5f},{r['wgs'][1]:.5f}" if r.get("wgs") else (r.get("file") or "")
        print(f"{r['rank']:>3} {(r['inliers'] if r['inliers'] is not None else '-'):>7} {r['score_global']:>7.3f}  …{str(r['id'])[-10:]}"
              f" h{r['heading']:.0f} {pos} {r.get('road', '')}" if r.get("heading") is not None else
              f"{r['rank']:>3} {(r['inliers'] if r['inliers'] is not None else '-'):>7} {r['score_global']:>7.3f}  {r['id']} {pos}")
    strong = [r for r in out_rows if (r["inliers"] or 0) >= args.min_inliers]
    if args.refine != "none":
        print(f"{len(strong)} with inliers ≥{args.min_inliers}" + (": open these first and compare invariant features" if strong else ": this does not mean none of them is right — with a season change, an old capture, or the photo taken on the sidewalk while the street view is from the middle of the road, the ground truth also often has only single-digit inliers. First open the top 10 in --sheet and compare invariant features; if none match, change heading (--spread-headings) or widen the area"))
    if args.out:
        Path(args.out).write_text(json.dumps([{k: v for k, v in r.items() if k != "id_key"} for r in rows], ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"-> {args.out} (all {len(rows)} rows)")
    if args.sheet:
        _sheet(out_rows, {r["id_key"]: ims[r["id_key"]] for r in out_rows}, Path(args.sheet))
        print(f"-> {args.sheet}")


def cmd_index(args) -> None:
    _proxy_env(args.proxy)
    p = Path(args.images)
    files = sorted(p.glob("*.jp*g")) + sorted(p.glob("*.png")) if p.is_dir() else [Path(x) for x in sorted(glob.glob(args.images))]
    emb = Embedder(args.method)
    feats = emb.embed([Image.open(f) for f in files], multi=False)[:, 0]
    np.savez(args.out, ids=np.array([f.stem for f in files]), files=np.array([str(f) for f in files]), feats=feats, method=args.method)
    print(f"{len(files)} images -> {args.out}")


def _neg_coords(argv: list[str]) -> list[str]:
    return [" " + a if re.match(r"^-\d[\d.]*(,-?[\d.]+)+$", a) else a for a in argv]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--proxy", default=os.environ.get("GEO_PROXY"), help=PROXY_HELP)
    ap.add_argument("--cache", type=Path, default=Path(".geo-cache"))
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("rank")
    r.add_argument("--query", required=True)
    r.add_argument("--query-box", help="x0,y0,x1,y1: compare only this region")
    r.add_argument("--images")
    r.add_argument("--items", help=".index.json from baidu_pano.py / gsv.py")
    r.add_argument("--render", choices=["baidu", "gsv"], help="which engine renders --items; if omitted, guessed from the id format")
    r.add_argument("--spread-headings", help="extra heading offsets for each --items entry, e.g. -30,0,30")
    r.add_argument("--panos", help="output of baidu_pano.py scan")
    r.add_argument("--toward", help="lat,lon")
    r.add_argument("--headings")
    r.add_argument("--offset", type=float, default=0)
    r.add_argument("--within", help="lat,lon,radius in meters")
    r.add_argument("--spread", type=float, help="thinning spacing in meters")
    r.add_argument("--pitch", type=float, default=10)
    r.add_argument("--fov", type=float, default=80)
    r.add_argument("--max-candidates", type=int, default=400)
    r.add_argument("--method", choices=["dino", "clip", "both"], default="dino")
    r.add_argument("--refine", choices=["none", "sift"], default="sift")
    r.add_argument("--refine-top", type=int, default=30)
    r.add_argument("--min-inliers", type=int, default=15)
    r.add_argument("--top", type=int, default=10)
    r.add_argument("--out")
    r.add_argument("--sheet")
    r.add_argument("--proxy", default=argparse.SUPPRESS)
    r.add_argument("--cache", type=Path, default=argparse.SUPPRESS)

    i = sub.add_parser("index")
    i.add_argument("--images", required=True)
    i.add_argument("--method", choices=["dino", "clip"], default="dino")
    i.add_argument("--out", required=True)
    i.add_argument("--proxy", default=argparse.SUPPRESS)

    args = ap.parse_args(_neg_coords(sys.argv[1:]))
    if args.cmd == "rank":
        cmd_rank(args)
    else:
        cmd_index(args)


if __name__ == "__main__":
    # Chinese-locale Windows writes GBK by default: m², ñ make it crash, and the Chinese the agent reads comes out garbled
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    main()
