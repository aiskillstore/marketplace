#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow", "numpy"]
# ///
"""Use elevation data to "look" out from a candidate camera position: synthesize a layered terrain view and skyline to compare ridgelines with the photo.

When there is no street view, only distant mountains (group photos in the mountains, views across a river, aerial shots, a ridgeline outside a window), this replaces Google Earth oblique 3D.
Elevation comes from AWS Terrain Tiles (Terrarium encoding, ~30 m worldwide, no key).

  view     render from one camera position by heading and field of view: shading layered by distance + red skyline + bearing ticks; can be stacked above/below the photo
  profile  output the skyline elevation angle and distance at each bearing (JSON), for numeric comparison
  elev     look up the ground elevation at a point
  scan     along linear infrastructure (railway, road, power line), compute the 360° horizon point by point, keep the points that are "flat nearby + a mountain + the mountain right next to a stretch of flat horizon"
           and cluster them — when the frame shows only one piece of infrastructure and a mountain you can't recognize, use it to cut a whole large region down to a few hundred patches
  ridge    sample the photo's ridgeline: per column, find the sky-to-mountain brightness jump; output a pixel point list + flat-horizon column range + horizon row + focal length (ridge.json)
  fit      score each scan cluster against ridge.json: lay a camera-position grid in each cluster, search heading × focal length × horizon offset,
           skyline RMS + flat-horizon penalty (+ optional: near layer of a two-layer photo, heading perpendicular to a line, how far the linear
           infrastructure is at the frame's left/center/right), sort by score, --sheet draws overlays of the top N

Important: a matching skyline outline only shows that the camera position is near some sight line — moving a few hundred meters forward or back along the sight line barely changes the distant mountain outline.
To pin a point you need a second independent constraint (another near–far object alignment, a road or riverbank on the map). See references/geometry.md.

Examples:
  terrain.py elev --at 35.3606,138.7274
  terrain.py view --at 35.4983,138.7688 --heading 194 --hfov 50 --range 30000 --out fuji.png   # Mt. Fuji from Lake Kawaguchi
  terrain.py view --at <candidate camera position> --height 20 --heading <heading> --hfov 65 --out v.png --photo photo.jpg
  terrain.py profile --at 35.4983,138.7688 --heading 194 --hfov 50 --out prof.json
  terrain.py scan --lines rail_bridges.geojson --bbox 35.1,138.3,36.0,139.2 --out hits.json   # get the lines with osm.py geom first
  terrain.py ridge photo.jpg --x0 760 --x1 1260 --step 20 --flat 0:280 --out ridge.json --png ridge.png
  terrain.py ridge photo.jpg --points "X,Y;X,Y;..." --near "X,Y;X,Y;..." --near-clear X0:X1@ROW --hrow ROW --out ridge.json   # two-layer
  terrain.py fit --hits hits.json --ridge ridge.json --out fit.json --sheet top.jpg            # coarse search: per cluster 2 km / 250 m / z11
  terrain.py fit --at 35.4983,138.7688 --ridge ridge.json --radius 800 --grid 100 --zoom 13 --az-step 0.25 \\
             --line rail.geojson --line-dist 350-750:550-900:800-1700 --out fine.json          # fine search + infrastructure distance constraint
  terrain.py fit --hits hits.json --ridge ridge.json --range 45000 --min-peak 2 --perp-line lines.geojson --out fit.json   # far range + wires overhead

For the fields of ridge.json and fit.json, see each subcommand's --help.
"""
from __future__ import annotations

import argparse
from _net import curl_args, PROXY_HELP
import json
import math
import os
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import geo  # noqa: E402

TILE = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
R_EARTH = 6371008.8
K_REFRACTION = 0.13
F35_RANGE = (13.0, 135.0)          # fit's focal ladder when the photo has no EXIF focal length: 0.5x ultra-wide to ~5x telephoto
F35_RATIO = 1.18                   # step between ladder rungs


FETCH_TRIES = 4
MISSING_HELP = ("fill tiles that still fail after retries as missing (skipped in scan/fit, see-through in view/profile) instead of exiting; "
                "default: any failed tile is an error, because treating it as 0 m silently fakes sea-level terrain")


def _decode(p: Path) -> np.ndarray | None:
    """Decode a cached Terrarium tile; None if it is not a valid 256×256 image (truncated download, HTTP error body)."""
    try:
        with Image.open(p) as im:
            if im.size != (256, 256):
                return None
            a = np.asarray(im.convert("RGB"), dtype=np.float32)
    except Exception:  # noqa: BLE001
        return None
    return a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768


def _fetch(z: int, x: int, y: int, cache: Path, proxy: str | None) -> np.ndarray | None:
    """Elevation of one tile, or None if it could not be downloaded after FETCH_TRIES attempts. Never caches a bad response."""
    p = cache / f"terrarium_{z}_{x}_{y}.png"
    if p.exists():
        a = _decode(p)
        if a is not None:
            return a
        p.unlink(missing_ok=True)                                     # bad file left by an older version: download again
    tmp = p.with_name(f"{p.name}.{os.getpid()}.{threading.get_ident()}.part")
    cmd = ["curl", "-q", "-fsS", "-m", "60", "-o", str(tmp), TILE.format(z=z, x=x, y=y)] + curl_args(proxy)
    for k in range(FETCH_TRIES):
        if k:
            time.sleep(2 ** (k - 1))                                  # 1, 2, 4 s backoff
        r = subprocess.run(cmd, check=False, capture_output=True)
        a = _decode(tmp) if r.returncode == 0 else None
        if a is not None:
            os.replace(tmp, p)
            return a
        tmp.unlink(missing_ok=True)
    return None


def _fetch_all(jobs: list[tuple[int, int]], zoom: int, cache: Path, proxy: str | None, threads: int, progress: bool = False):
    """Yield ((x, y), array or None) for every tile; download failures come back as None."""
    with ThreadPoolExecutor(threads) as ex:
        for i, item in enumerate(zip(jobs, ex.map(lambda t: _fetch(zoom, t[0], t[1], cache, proxy), jobs)), 1):
            if progress and i % 200 == 0:
                print(f"  tiles {i}/{len(jobs)}", file=sys.stderr)
            yield item


def _report_missing(failed: list[tuple[int, int]], total: int, zoom: int, allow_missing: bool) -> None:
    """Fail loudly on missing tiles; with --allow-missing only warn."""
    if not failed:
        return
    eg = ", ".join(f"{zoom}/{x}/{y}" for x, y in failed[:5]) + (" …" if len(failed) > 5 else "")
    msg = f"{len(failed)}/{total} elevation tiles failed to download after {FETCH_TRIES} tries ({eg})"
    if not allow_missing:
        sys.exit(f"{msg}. Good tiles are cached, so just re-run (lower --threads if it keeps failing, "
                 "or check the network with doctor.py --network); --allow-missing proceeds without them")
    print(f"WARNING: {msg}; --allow-missing: continuing without them", file=sys.stderr)


class DEM:
    """Elevation mosaic indexed by Web Mercator pixels."""

    def __init__(self, center: tuple[float, float], radius_m: float, zoom: int, cache: Path, proxy: str | None,
                 allow_missing: bool = False):
        cache.mkdir(parents=True, exist_ok=True)
        self.z = zoom
        mpp = geo.meters_per_px(zoom, center[0])
        cx, cy = geo.ll2px(zoom, *center)
        r_px = radius_m / mpp + 256
        self.tx0, self.ty0 = int((cx - r_px) // 256), int((cy - r_px) // 256)
        tx1, ty1 = int((cx + r_px) // 256), int((cy + r_px) // 256)
        nx, ny = tx1 - self.tx0 + 1, ty1 - self.ty0 + 1
        if nx * ny > 400:
            sys.exit(f"Area too large ({nx}x{ny} tiles); reduce --range or lower --zoom")
        self.h = np.full((ny * 256, nx * 256), np.nan, dtype=np.float32)   # missing tiles stay NaN, never 0 m
        jobs = [(x, y) for y in range(self.ty0, ty1 + 1) for x in range(self.tx0, tx1 + 1)]
        failed = []
        for (x, y), arr in _fetch_all(jobs, zoom, cache, proxy, 8):
            if arr is None:
                failed.append((x, y))
                continue
            self.h[(y - self.ty0) * 256:(y - self.ty0 + 1) * 256, (x - self.tx0) * 256:(x - self.tx0 + 1) * 256] = arr
        _report_missing(failed, len(jobs), zoom, allow_missing)

    def sample(self, lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
        n = 256 * 2 ** self.z
        x = (lon + 180) / 360 * n - self.tx0 * 256
        y = (1 - np.arcsinh(np.tan(np.radians(lat))) / np.pi) / 2 * n - self.ty0 * 256
        x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
        fx, fy = x - x0, y - y0
        H, W = self.h.shape
        x0, y0 = np.clip(x0, 0, W - 2), np.clip(y0, 0, H - 2)
        a, b = self.h[y0, x0], self.h[y0, x0 + 1]
        c, d = self.h[y0 + 1, x0], self.h[y0 + 1, x0 + 1]
        return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def _dest_np(lat0: float, lon0: float, brg: np.ndarray, dist: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    la1, lo1 = math.radians(lat0), math.radians(lon0)
    b = np.radians(brg)[:, None]
    d = (dist / R_EARTH)[None, :]
    la2 = np.arcsin(math.sin(la1) * np.cos(d) + math.cos(la1) * np.sin(d) * np.cos(b))
    lo2 = lo1 + np.arctan2(np.sin(b) * np.sin(d) * math.cos(la1), np.cos(d) - math.sin(la1) * np.sin(la2))
    return np.degrees(la2), np.degrees(lo2)


def cast(dem: DEM, at, eye_alt: float, azimuths: np.ndarray, rng: float, near: float = 40.0, n: int = 900, keep_nan: bool = False):
    """Return (elevation angle ° of each sample in each column, sample distance m). n = samples per sight line (view/profile use 900; fit uses --nsamp).
    Samples on missing tiles (--allow-missing) become -90° so they never form a skyline; keep_nan=True leaves them NaN for the caller to detect."""
    dist = near * (rng / near) ** (np.arange(n) / (n - 1))          # dense near, sparse far
    lat, lon = _dest_np(at[0], at[1], azimuths, dist)
    h = dem.sample(lat, lon)
    drop = dist ** 2 / (2 * R_EARTH) * (1 - K_REFRACTION)
    ang = np.degrees(np.arctan2(h - drop[None, :] - eye_alt, dist[None, :]))
    return (ang if keep_nan else np.nan_to_num(ang, nan=-90.0)), dist


def render(ang: np.ndarray, dist: np.ndarray, azimuths: np.ndarray, pitch: float, vfov: float, height: int) -> tuple[Image.Image, np.ndarray, np.ndarray]:
    W = ang.shape[0]
    img = np.zeros((height, W, 3), dtype=np.uint8)
    img[:] = (205, 225, 245)                                         # sky
    top = pitch + vfov / 2

    def row(a):
        return (top - a) / vfov * (height - 1)

    sky_ang = np.full(W, -90.0)
    sky_dist = np.full(W, np.nan)
    runmax = np.maximum.accumulate(ang, axis=1)
    visible = ang >= np.concatenate([np.full((W, 1), -90.0), runmax[:, :-1]], axis=1)
    logd = np.log(dist / dist[0]) / np.log(dist[-1] / dist[0])
    for c in range(W):
        idx = np.nonzero(visible[c])[0]
        prev = row(-90.0)
        # near to far: each visible sample paints this column from "its elevation angle" to "the previous highest point", color from dark to light by distance
        lo_row = height
        for i in idx:
            r = row(ang[c, i])
            if r >= lo_row:
                continue
            shade = int(60 + 150 * logd[i])
            r0 = max(0, int(r))
            img[r0:lo_row, c] = (shade - 25, shade, shade - 35)
            lo_row = r0
        if idx.size:
            j = idx[-1]
            sky_ang[c], sky_dist[c] = ang[c, j], dist[j]
            rr = int(round(row(ang[c, j])))
            if 0 <= rr < height:
                img[max(0, rr - 1):rr + 2, c] = (220, 30, 30)
        _ = prev
    return Image.fromarray(img), sky_ang, sky_dist


def _font(size: int):
    for p in ("/System/Library/Fonts/STHeiti Medium.ttc", "/System/Library/Fonts/Hiragino Sans GB.ttc",
              "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"):
        try:
            return ImageFont.truetype(p, size)
        except Exception:  # noqa: BLE001
            continue
    return ImageFont.load_default()


def annotate(im: Image.Image, azimuths: np.ndarray, pitch: float, vfov: float, title: str) -> Image.Image:
    W, H = im.size
    d = ImageDraw.Draw(im)
    f = _font(16)
    hr = (pitch + vfov / 2) / vfov * (H - 1)
    d.line([(0, hr), (W, hr)], fill=(90, 90, 200), width=1)           # horizontal line at eye height
    names = {0: "N", 45: "NE", 90: "E", 135: "SE", 180: "S", 225: "SW", 270: "W", 315: "NW"}
    span = azimuths[-1] - azimuths[0]
    stepdeg = 5 if span <= 60 else 10 if span <= 150 else 30
    first = math.ceil(azimuths[0] / stepdeg) * stepdeg
    for a in np.arange(first, azimuths[-1] + 1e-6, stepdeg):
        x = (a - azimuths[0]) / span * (W - 1)
        d.line([(x, H - 14), (x, H)], fill="black", width=1)
        lab = f"{a % 360:.0f}°" + (names.get(int(a % 360), ""))
        d.text((x + 3, H - 32), lab, fill="black", font=f)
    d.rectangle([0, 0, W, 24], fill=(0, 0, 0))
    d.text((6, 3), title, fill="yellow", font=f)
    return im



# ---------------------------------------------------------------- scan ----
# Linear infrastructure × terrain filtering. Method in references/corridors.md 4.3.
# Difference from view/profile: this has to cover a province-sized region, far more tiles than the DEM class's 400-tile limit,
# so it builds its own large mosaic filled only with "the tiles actually needed", sampled nearest-neighbor (one z10 cell is ~150 m; interpolation is pointless).


def _tile_xy(lat: float, lon: float, z: int) -> tuple[float, float]:
    n = 2 ** z
    x = (lon + 180) / 360 * n
    y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    return x, y


def _haversine(a: tuple[float, float], b: tuple[float, float]) -> float:
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    d = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R_EARTH * math.asin(math.sqrt(d))


class _Mosaic:
    """A large mosaic stitched from a batch of Terrarium tiles, nearest-neighbor sampling. Tiles that failed to download hold MISSING."""

    MISSING = -32768                                                  # real elevations are clipped to -500…9000, so this never collides

    def __init__(self, need: set[tuple[int, int]], zoom: int, cache: Path, proxy: str | None, threads: int,
                 allow_missing: bool = False):
        cache.mkdir(parents=True, exist_ok=True)
        self.z = zoom
        self.tx0 = min(t[0] for t in need)
        self.ty0 = min(t[1] for t in need)
        nx = max(t[0] for t in need) - self.tx0 + 1
        ny = max(t[1] for t in need) - self.ty0 + 1
        gb = nx * ny * 256 * 256 * 2 / 1e9
        print(f"mosaic {nx}x{ny} tiles, {gb:.2f} GB memory", file=sys.stderr)
        self.h = np.full((ny * 256, nx * 256), self.MISSING, dtype=np.int16)
        jobs = sorted(need)
        failed = []
        for (x, y), arr in _fetch_all(jobs, zoom, cache, proxy, threads, progress=True):
            if arr is None:
                failed.append((x, y))
                continue
            self.h[(y - self.ty0) * 256:(y - self.ty0 + 1) * 256,
                   (x - self.tx0) * 256:(x - self.tx0 + 1) * 256] = np.clip(arr, -500, 9000).astype(np.int16)
        self.n_failed = len(failed)
        _report_missing(failed, len(jobs), zoom, allow_missing)

    def sample(self, lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
        n = 256 * 2 ** self.z
        x = ((lon + 180) / 360 * n - self.tx0 * 256).astype(int)
        y = ((1 - np.arcsinh(np.tan(np.radians(lat))) / np.pi) / 2 * n - self.ty0 * 256).astype(int)
        x = np.clip(x, 0, self.h.shape[1] - 1)
        y = np.clip(y, 0, self.h.shape[0] - 1)
        return self.h[y, x].astype(np.float32)


def _line_points(gj: dict, step: float, skip: list[tuple[str, str]], bbox: tuple[float, float, float, float] | None):
    """Take one point every step meters along each LineString; return [(lat, lon, properties)]."""
    pts = []
    n_line = n_skip = 0
    for f in gj.get("features", []):
        g = f.get("geometry") or {}
        if g.get("type") != "LineString" or len(g.get("coordinates", [])) < 2:
            continue
        tags = f.get("properties", {}) or {}
        n_line += 1
        if any(str(tags.get(k, "")) == v for k, v in skip):
            n_skip += 1
            continue
        c = [(y, x) for x, y in g["coordinates"]]                     # geojson is lon,lat
        if bbox and not (min(p[0] for p in c) <= bbox[2] and max(p[0] for p in c) >= bbox[0]
                         and min(p[1] for p in c) <= bbox[3] and max(p[1] for p in c) >= bbox[1]):
            continue
        got = 0
        acc = 0.0
        for i in range(1, len(c)):
            d = _haversine(c[i - 1], c[i])
            for k in range(int((acc + d) // step)):
                t = (step * (k + 1) - acc) / d if d else 0
                pts.append((c[i - 1][0] + (c[i][0] - c[i - 1][0]) * t,
                            c[i - 1][1] + (c[i][1] - c[i - 1][1]) * t, tags))
                got += 1
            acc = (acc + d) % step
        # lines shorter than step overall, or whose ends nearly coincide (loops), get one midpoint added so the whole line isn't missed
        if got == 0 or _haversine(c[0], c[-1]) < step:
            pts.append((c[len(c) // 2][0], c[len(c) // 2][1], tags))
    if bbox:
        s, w, n, e = bbox
        pts = [p for p in pts if s <= p[0] <= n and w <= p[1] <= e]
    print(f"{n_line} lines ({n_skip} skipped by --skip-tag), {len(pts)} sample points", file=sys.stderr)
    return pts


def _cluster(hits: list[dict], km: float) -> list[dict]:
    """Greedy clustering by max_ang from largest to smallest: the steepest point represents the cluster, points within km join it, and the representative gets n = number of points in the cluster."""
    order = sorted(hits, key=lambda h: -h["max_ang"])
    used = [False] * len(order)
    out = []
    for i, p in enumerate(order):
        if used[i]:
            continue
        n = 0
        for j in range(i, len(order)):
            if not used[j] and _haversine((p["lat"], p["lon"]), (order[j]["lat"], order[j]["lon"])) <= km * 1000:
                used[j] = True
                n += 1
        out.append({**p, "n": n})
    return out


def _cmd_scan(args) -> None:
    az_step = args.az_step
    naz = int(round(360 / az_step))
    if abs(naz * az_step - 360) > 1e-6:
        sys.exit("--az-step must divide 360 evenly")
    if args.step <= 0 or args.near_step <= 0 or args.near_radius < 0:
        sys.exit("--step / --near-step must be greater than 0, --near-radius must not be negative")
    dist = np.array([float(x) for x in args.dist.split(",")], dtype=float)
    near = np.arange(0, args.near_radius + 1e-6, args.near_step, dtype=float)
    skip = []
    for s in (args.skip_tag or ["electrified=no"]):
        if s.lower() in ("none", "-"):
            continue
        if "=" not in s:
            sys.exit(f"--skip-tag must be written as key=value, got {s!r}")
        k, v = s.split("=", 1)
        skip.append((k, v))
    bbox = None
    if args.bbox:
        b = [float(x) for x in args.bbox.split(",")]
        if len(b) != 4:
            sys.exit("--bbox needs 4 numbers: s,w,n,e")
        bbox = (min(b[0], b[2]), min(b[1], b[3]), max(b[0], b[2]), max(b[1], b[3]))

    gj = json.loads(Path(args.lines).read_text(encoding="utf-8"))
    pts = _line_points(gj, args.step, skip, bbox)
    if not pts:
        sys.exit("0 sample points: --bbox encloses nothing, or the geojson has no LineString")

    reach = float(dist.max()) + 500                                   # half a kilometer extra, enough even when a sample point falls on a tile edge
    need: set[tuple[int, int]] = set()
    for lat, lon, _ in pts:
        x, y = _tile_xy(lat, lon, args.zoom)
        r = reach / (40075016.7 * math.cos(math.radians(lat)) / 2 ** args.zoom)
        for tx in range(int(x - r), int(x + r) + 1):
            for ty in range(int(y - r), int(y + r) + 1):
                need.add((tx, ty))
    print(f"need {len(need)} z{args.zoom} tiles", file=sys.stderr)
    if len(need) > args.max_tiles:
        sys.exit(f"{len(need)} tiles > --max-tiles {args.max_tiles}: shrink --bbox, lower --zoom, or run in chunks")
    mos = _Mosaic(need, args.zoom, args.cache, args.proxy, args.threads, args.allow_missing)

    az = np.arange(0, 360, az_step)
    min_low = int(round((args.min_low_deg if args.min_low_deg is not None else args.flat_run) / az_step))
    need_run = int(round(args.flat_run / az_step))
    cap = int(round(args.flat_run_cap / az_step))
    hits = []
    n_missing = 0
    for idx, (lat, lon, tags) in enumerate(pts):
        if idx and idx % 2000 == 0:
            print(f"  scanned {idx}/{len(pts)}, hits {len(hits)}", file=sys.stderr)
        ln, lo = _dest_np(lat, lon, az, near)
        hn = mos.sample(ln, lo)
        if (hn == mos.MISSING).any():
            n_missing += 1
            continue
        if hn.max() - hn.min() > args.near_flat:                      # not flat nearby: a valley or hillside, not the flat ground seen in the frame
            continue
        h0 = float(np.median(hn))
        la, lo = _dest_np(lat, lon, az, dist)
        h = mos.sample(la, lo)
        if (h == mos.MISSING).any():                                  # a hole would read as a deep valley or flat horizon
            n_missing += 1
            continue
        ang = np.degrees(np.arctan2(h - h0 - args.eye, dist[None, :]))  # within a few km earth curvature is <5 m, negligible next to z10 error
        hor = ang.max(axis=1)                                         # horizon elevation angle at each bearing
        rel = (h - h0).max(axis=1)
        mt = hor >= args.min_peak
        low = hor < args.max_low
        if not mt.any() or low.sum() < min_low:
            continue
        best = 0                                                      # how long the flat horizon right next to the mountain is
        for i in range(naz):
            if not mt[i]:
                continue
            for sgn in (-1, 1):
                k = run = 0
                while k < cap:
                    jj = (i + sgn * (k + 1)) % naz
                    if low[jj]:
                        run += 1
                    elif run == 0 and k < 2:                          # allow a 2-cell transition between the mountain foot and flat ground
                        pass
                    else:
                        break
                    k += 1
                best = max(best, run)
        if best < need_run:
            continue
        i = int(np.argmax(hor))
        hits.append({"lat": round(lat, 5), "lon": round(lon, 5), "h0": round(h0), "max_ang": round(float(hor[i]), 1),
                     "az": float(az[i]), "relief": round(float(rel[i])), "flat_run_deg": best * az_step,
                     "name": tags.get("name", ""), "hs": tags.get("highspeed", ""),
                     "elec": tags.get("electrified", ""), "id": tags.get("id", tags.get("@id", ""))})

    clusters = _cluster(hits, args.cluster_km)
    print(f"{len(hits)} hit points → {len(clusters)} clusters", file=sys.stderr)
    if n_missing:
        print(f"WARNING: {n_missing}/{len(pts)} sample points not scanned because they touch missing tiles", file=sys.stderr)
    out = {
        "params": {"lines": str(args.lines), "bbox": list(bbox) if bbox else None, "step_m": args.step,
                   "zoom": args.zoom, "near_flat_m": args.near_flat, "near_radius_m": args.near_radius,
                   "min_peak_deg": args.min_peak, "max_low_deg": args.max_low, "flat_run_deg": args.flat_run,
                   "min_low_deg": args.min_low_deg if args.min_low_deg is not None else args.flat_run,
                   "eye_m": args.eye, "az_step_deg": az_step, "dist_m": dist.tolist(),
                   "skip_tag": [f"{k}={v}" for k, v in skip], "cluster_km": args.cluster_km},
        "n_samples": len(pts), "n_hits": len(hits), "n_clusters": len(clusters),
        "n_failed_tiles": mos.n_failed, "n_samples_missing_dem": n_missing,
        "hits": hits, "clusters": clusters,
    }
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"→ {args.out}", file=sys.stderr)
    if args.clusters_out:
        Path(args.clusters_out).write_text(json.dumps(clusters, ensure_ascii=False, indent=0), encoding="utf-8")
        print(f"→ {args.clusters_out} (cluster list only)", file=sys.stderr)


# ---------------------------------------------------------------- ridge ----
# Photo ridgeline sampling. Method in references/geometry.md 7.4: per column, top to bottom, find the sky→mountain brightness jump.


def _focal_px(photo: Path, w: int, h: int, f0_arg: float | None, f35_default: float):
    """Photo focal length (pixels). Priority: --f0 > EXIF 35mm-equivalent focal length > assumed from --f35.
    The 35mm equivalent converts via the diagonal: f_px = f35 / 43.27 × diagonal pixels; this holds even if the photo was resized.
    Return (f_px, source, f35)."""
    diag = math.hypot(w, h)
    if f0_arg:
        return float(f0_arg), "arg", round(f0_arg * 43.2666 / diag, 1)
    try:
        ifd = Image.open(photo).getexif().get_ifd(0x8769)
        f35 = ifd.get(0xA405)                                          # FocalLengthIn35mmFilm
        if f35 and float(f35) > 0:
            return float(f35) / 43.2666 * diag, "exif", float(f35)
    except Exception:  # noqa: BLE001
        pass
    return f35_default / 43.2666 * diag, "assumed", f35_default


def _parse_pts(spec: str, name: str, W: int, H: int) -> list[list[int]]:
    """Pixel points as "x,y;x,y;..." or a JSON file holding [[x,y],...]."""
    p = Path(spec)
    if p.suffix == ".json" and p.exists():
        raw = json.loads(p.read_text(encoding="utf-8"))
        pts = raw.get("ridge", raw) if isinstance(raw, dict) else raw
    else:
        try:
            pts = [[float(v) for v in part.split(",")] for part in spec.split(";") if part.strip()]
        except ValueError:
            sys.exit(f"{name} must be x,y;x,y;... or a .json file of [[x,y],...], got {spec!r}")
    out = []
    for q in pts:
        if len(q) != 2 or not (0 <= q[0] < W and 0 <= q[1] < H):
            sys.exit(f"{name}: point {q} is not x,y inside the {W}x{H} photo")
        out.append([int(round(q[0])), int(round(q[1]))])
    if len(out) < 3:
        sys.exit(f"{name} needs at least 3 points, got {len(out)}")
    return sorted(out)


def _sky_edge(prof: np.ndarray, ymin: int, ymax: int, k: int, drop: float, hold: int) -> int | None:
    """In one column's brightness profile, top to bottom, find the first row where "the mean of the k rows above exceeds the mean of the k rows below by drop, and the hold rows further down are still dark",
    then take the maximum-gradient row within ±k rows of it. Return the row index of the mountain's first row; None if not found.
    hold is there to skip things only a few pixels tall vertically, such as wires and antennas."""
    n = len(prof)
    cs = np.concatenate([[0.0], np.cumsum(prof, dtype=np.float64)])
    y = np.arange(max(ymin, k), min(ymax, n - k - hold))
    if y.size == 0:
        return None
    above = (cs[y] - cs[y - k]) / k
    below = (cs[y + k] - cs[y]) / k
    held = (cs[y + k + hold] - cs[y + k]) / hold
    ok = (above - below >= drop) & (above - held >= drop)
    if not ok.any():
        return None
    y0 = int(y[np.argmax(ok)])
    yy = np.arange(max(k, y0 - k), min(n - k, y0 + k + 1))
    g = (cs[yy] - cs[yy - k]) / k - (cs[yy + k] - cs[yy]) / k
    return int(yy[np.argmax(g)])


def _cmd_ridge(args) -> None:
    im = Image.open(args.photo).convert("RGB")
    W, H = im.size
    a = np.asarray(im, dtype=np.float32)
    L = a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114
    if args.x1 is None:
        args.x1 = W - 1
    if not (0 <= args.x0 < args.x1 < W):
        sys.exit(f"--x0/--x1 must satisfy 0 ≤ x0 < x1 < width {W}")
    if args.step <= 0:
        sys.exit("--step must be greater than 0")
    ymin = args.ymin if args.ymin is not None else 0
    ymax = args.ymax if args.ymax is not None else H
    f0, f_src, f35 = _focal_px(args.photo, W, H, args.f0, args.f35)

    def edge(x: int) -> int | None:
        x0, x1 = max(0, x - args.halfw), min(W, x + args.halfw + 1)
        return _sky_edge(L[:, x0:x1].mean(axis=1), ymin, ymax, args.k, args.drop, args.hold)

    ridge, missing = [], []
    if args.points:                                                   # hand-picked skyline replaces detection (cloud on the peaks, haze, snow against sky)
        ridge = _parse_pts(args.points, "--points", W, H)
    else:
        for x in range(args.x0, args.x1 + 1, args.step):
            y = edge(x)
            (ridge.append([x, y]) if y is not None else missing.append(x))
    near = _parse_pts(args.near, "--near", W, H) if args.near else []
    near_clear = []
    for spec in args.near_clear or []:
        m = re.match(r"^\s*(\d+):(\d+)@(\d+(?:\.\d+)?)\s*$", spec)
        if not m or not 0 <= int(m[1]) < int(m[2]) < W:
            sys.exit(f"--near-clear must be x0:x1@row with 0 ≤ x0 < x1 < width {W}, got {spec!r}")
        near_clear.append([int(m[1]), int(m[2]), float(m[3])])
    flat = None
    flat_rows: list[int] = []
    flat_pts: list[list[int]] = []                                    # for drawing the check image: flat_rows has only row indices and omits columns with no jump found, so index order can't map back to columns
    if args.flat:
        b = args.flat.split(":")
        if len(b) != 2:
            sys.exit("--flat must be written as x0:x1")
        flat = [int(b[0]), int(b[1])]
        if not (0 <= flat[0] < flat[1] < W):
            sys.exit(f"--flat must satisfy 0 ≤ x0 < x1 < width {W}")
        for x in range(flat[0], flat[1] + 1, args.step):
            y = edge(x)
            if y is not None:
                flat_rows.append(y)
                flat_pts.append([x, y])
    if args.hrow is not None:
        hrow, h_src = float(args.hrow), "arg"
    elif flat_rows:
        hrow, h_src = float(np.median(flat_rows)), "flat"
    else:
        hrow, h_src = H / 2, "center"
    if len(ridge) < 3:
        print(f"warning: only {len(ridge)} ridge points found ({len(missing)} columns missing), fit needs at least 3; adjust --drop/--ymin/--ymax or check --png", file=sys.stderr)
    out = {
        "photo": str(args.photo), "image_size": [W, H], "cx": W / 2,
        "ridge": ridge, "missing_cols": missing, "ridge_source": "points" if args.points else "detected",
        "near": near, "near_clear": near_clear,
        "flat": flat, "flat_rows": flat_rows,
        "hrow": round(hrow, 1), "hrow_source": h_src,
        "f0": round(f0, 1), "f0_source": f_src, "f35_equiv": f35,
        "params": {"x0": args.x0, "x1": args.x1, "step": args.step, "ymin": ymin, "ymax": ymax,
                   "drop": args.drop, "k": args.k, "hold": args.hold, "halfw": args.halfw},
    }
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    src_txt = {"arg": "--f0", "exif": "EXIF 35mm equivalent",
               "assumed": f"no EXIF, assumed {f35} mm equivalent; fit tries {F35_RANGE[0]:g}–{F35_RANGE[1]:g} mm by default"}[f_src]
    h_txt = {"arg": "--hrow", "flat": f"median sky→ground row in the --flat columns ({len(flat_rows)} columns)", "center": "no --flat given, frame midline"}[h_src]
    print(f"{W}x{H}  ridge {len(ridge)} points ({len(missing)} columns missing)  flat-horizon columns {flat}  "
          f"hrow {hrow:.0f} ({h_txt})  f0 {f0:.0f} px ({src_txt}, horizontal FOV {2 * math.degrees(math.atan(W / 2 / f0)):.1f}°)"
          + (f"  near layer {len(near)} points, {len(near_clear)} clear ranges" if near or near_clear else "") + f" → {args.out}")
    if args.png:
        d = ImageDraw.Draw(im)
        d.line([(0, hrow), (W, hrow)], fill=(80, 80, 255), width=1)
        if flat:
            d.line([(flat[0], hrow), (flat[1], hrow)], fill=(0, 200, 255), width=4)
            for x, y in flat_pts:
                d.ellipse([x - 3, y - 3, x + 3, y + 3], outline=(0, 200, 255), width=2)
        for x, y in ridge:
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 220, 0))
        for x in missing:
            d.line([(x, ymin), (x, ymax - 1)], fill=(255, 0, 0), width=1)
        for x, y in near:
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 120, 0))
        for x0, x1, row in near_clear:
            d.line([(x0, row), (x1, row)], fill=(255, 120, 0), width=3)
        d.text((8, 8), f"ridge {len(ridge)} pts  hrow {hrow:.0f} ({h_src})  f0 {f0:.0f}px ({f_src})", fill="yellow", font=_font(20))
        im.save(args.png, quality=90)
        print(f"check image → {args.png} (yellow dots = ridge points, red vertical lines = columns not found, blue line = hrow, cyan line = flat-horizon column range, "
              "orange dots = near-layer points, orange lines = near-clear ranges)")


# ------------------------------------------------------------------ fit ----
# Batch skyline scoring. Method in references/geometry.md 7.4; infrastructure distance constraint in corridors.md 4.3.
# For each candidate camera position compute a full 360° horizon hor(az); convert photo ridge points to (bearing offset, elevation angle) and compare against all headings at once:
#   rms = RMS of the ridge elevation-angle residuals (the residual median serves as horizon offset cc, clamped to ±cc_max)
#   flatpen = mean of max(0, hor - cc - flat_clear) over the flat-horizon columns
#   score = rms + flat_w × flatpen
# With --line, also add: for each heading, the nearest distance dL/dC/dR of infrastructure sample points inside the frame's left/center/right bearing windows,
#   line_pen = meters each falls outside its --line-dist interval / --line-scale (+ penalty 1 for wrong order)
#   total = score + line_w × line_pen; without --line, total = score.
# Two-layer photos (ridge.json has near / near_clear): near(az) = highest angle within D1 m, D1 tried from --near-dist; near points join
#   the far ridge points in the same rms (one cc and roll for both), near_clear columns add nclearpen = mean of max(0, near − row angle).
# --perp-line keeps only headings within --perp-tol of perpendicular to the nearest line (wires crossing the frame almost level).


def _parse_pairs(s: str, name: str, n: int = 3, sep: str = ",", rng: str = ":") -> list[tuple[float, float]]:
    out = []
    for part in s.split(sep):
        b = part.split(rng)
        if len(b) != 2:
            sys.exit(f"{name}: each segment must be written as a{rng}b, got {part!r}")
        out.append((float(b[0]), float(b[1])))
    if len(out) != n:
        sys.exit(f"{name} needs {n} segments, got {len(out)}")
    return out


def _load_centers(args) -> list[dict]:
    if args.at:
        lat, lon = map(float, args.at.split(","))
        return [{"lat": lat, "lon": lon, "name": "", "src_idx": 0}]
    j = json.loads(Path(args.hits).read_text(encoding="utf-8"))
    items = j["clusters"] if isinstance(j, dict) and "clusters" in j else j
    if not isinstance(items, list):
        sys.exit("--hits must be scan output (with a clusters field) or a list of clusters/points")
    centers = []
    for i, c in enumerate(items):
        if "lat" not in c or "lon" not in c:
            sys.exit(f"--hits item {i} has no lat/lon")
        centers.append({**c, "src_idx": c.get("src_idx", i)})
    if args.select:
        want = [int(x) for x in args.select.split(",")]
        bad = [i for i in want if not 0 <= i < len(centers)]
        if bad:
            sys.exit(f"--select indices {bad} out of range 0–{len(centers) - 1}")
        centers = [centers[i] for i in want]
    return centers


def _skyline_xy(hor: np.ndarray, az: np.ndarray, H: float, f: float, cc: float, cx: float, hrow: float, half_w: float,
                roll: float = 0.0):
    """Project the 360° horizon onto photo pixels with the pinhole model fit uses: x = cx + f·tan(bearing offset), y = hrow − f·tan(elevation angle − cc).
    roll = frame roll angle ° (clockwise positive); pass the value fit solved for, otherwise both ends will be off from the photo by a dozen-plus pixels."""
    rel = (az - H + 180) % 360 - 180
    lim = math.degrees(math.atan(half_w / f)) + 1
    m = np.abs(rel) <= lim
    x = cx + f * np.tan(np.radians(rel[m]))
    y = hrow - f * np.tan(np.radians(hor[m] - cc)) + math.tan(math.radians(roll)) * (x - cx)
    o = np.argsort(x)
    return list(zip(x[o].tolist(), y[o].tolist()))


def _fit_sheet(recs: list[dict], ridge: dict, photo: Path | None, out: Path, args, az: np.ndarray, dist_n: int) -> None:
    W, H = ridge["image_size"]
    tw = args.sheet_width
    s = tw / W
    th = int(H * s)
    base = None
    if photo and photo.exists():
        base = Image.open(photo).convert("RGB").resize((tw, th))
    cols = max(1, args.sheet_cols)
    rows = math.ceil(len(recs) / cols)
    sheet = Image.new("RGB", (tw * cols, th * rows), "white")
    font = _font(13)
    for i, r in enumerate(recs):
        tile = base.copy() if base else Image.new("RGB", (tw, th), (120, 120, 120))
        d = ImageDraw.Draw(tile)
        hrow, f, cx = ridge["hrow"], r["f"], ridge.get("cx", W / 2)
        d.line([(0, hrow * s), (tw, hrow * s)], fill=(80, 80, 255), width=1)
        if ridge.get("flat"):
            d.line([(ridge["flat"][0] * s, hrow * s), (ridge["flat"][1] * s, hrow * s)], fill=(0, 200, 255), width=3)
        try:
            dem = DEM(tuple(r["cam"]), args.range + 500, args.zoom, args.cache, args.proxy, args.allow_missing)
            ang, dist_v = cast(dem, tuple(r["cam"]), r["g"] + args.eye, az, args.range, near=args.near, n=dist_n)
            pts = _skyline_xy(ang.max(axis=1), az, r["H"], f, r["cc"], cx, hrow, W / 2, r.get("roll", 0.0))
            d.line([(x * s, y * s) for x, y in pts], fill=(255, 40, 40), width=2)
            if r.get("D1"):
                pts = _skyline_xy(ang[:, dist_v <= r["D1"]].max(axis=1), az, r["H"], f, r["cc"], cx, hrow, W / 2, r.get("roll", 0.0))
                d.line([(x * s, y * s) for x, y in pts], fill=(255, 140, 0), width=2)
        except SystemExit as e:
            d.text((6, th - 20), f"DEM failed: {e}", fill="red", font=font)
        for x, y in ridge["ridge"]:
            d.ellipse([x * s - 2, y * s - 2, x * s + 2, y * s + 2], fill=(255, 220, 0))
        for x, y in ridge.get("near") or []:
            d.ellipse([x * s - 2, y * s - 2, x * s + 2, y * s + 2], fill=(0, 220, 255))
        for x0, x1, row in ridge.get("near_clear") or []:
            d.line([(x0 * s, row * s), (x1 * s, row * s)], fill=(0, 220, 255), width=2)
        line_txt = f"  L/C/R {r['dL']:.0f}/{r['dC']:.0f}/{r['dR']:.0f} pen {r['line_pen']:.2f}" if "line_pen" in r else ""
        txt = (f"#{i + 1} hit{r['hit']} {r['name'] or '-'}  {r['cam'][0]:.5f},{r['cam'][1]:.5f}\n"
               f"H {r['H']:.1f}  f {f:.0f} ({r.get('f35', 0):.0f}mm)  cc {r['cc']:+.2f}  rms {r['rms']:.3f}  flat {r['flatpen']:.3f}{line_txt}\n"
               f"total {r['total']:.3f}")
        d.rectangle([0, 0, tw, 46], fill=(0, 0, 0))
        d.text((4, 2), txt, fill="yellow", font=font)
        sheet.paste(tile, ((i % cols) * tw, (i // cols) * th))
    sheet.save(out, quality=88)
    print(f"overlay → {out} (red line = synthetic skyline, orange line = synthetic near layer, yellow dots = photo ridge points, "
          "cyan dots/lines = photo near points / near-clear rows, blue line = hrow, cyan line on hrow = flat-horizon columns)", file=sys.stderr)


def _cmd_fit(args) -> None:
    if bool(args.hits) == bool(args.at):
        sys.exit("give exactly one of --hits and --at")
    ridge = json.loads(Path(args.ridge).read_text(encoding="utf-8"))
    RX = np.array([p[0] for p in ridge["ridge"]], float)
    RY = np.array([p[1] for p in ridge["ridge"]], float)
    if RX.size < 3:
        sys.exit(f"ridge.json has only {RX.size} ridge points, needs at least 3")
    W, Hh = ridge["image_size"]
    hrow, f0, cx = float(ridge["hrow"]), float(ridge["f0"]), float(ridge.get("cx", W / 2))
    flat = ridge.get("flat")
    FLX = np.arange(flat[0], flat[1] + 1e-6, args.flat_step, dtype=float) if flat else np.zeros(0)
    NX = np.array([p[0] for p in ridge.get("near") or []], float)
    NY = np.array([p[1] for p in ridge.get("near") or []], float)
    ncl = ridge.get("near_clear") or []
    NCX = np.concatenate([np.arange(a, b + 1e-6, args.flat_step) for a, b, _ in ncl]) if ncl else np.zeros(0)
    NCR = np.concatenate([np.full(len(np.arange(a, b + 1e-6, args.flat_step)), r) for a, b, r in ncl]) if ncl else np.zeros(0)
    two = bool(NX.size or NCX.size)
    near_dists = [float(x) for x in args.near_dist.split(",")] if two else [None]
    if two:
        dropped = [d_ for d_ in near_dists if d_ <= args.near]
        near_dists = [d_ for d_ in near_dists if d_ > args.near]
        if not near_dists:
            sys.exit(f"every --near-dist value ({args.near_dist}) is within --near {args.near:g} m, where sight lines start: "
                     "give near distances beyond --near")
        if dropped:
            print(f"note: --near-dist {', '.join(f'{d_:g}' for d_ in dropped)} m dropped, within --near {args.near:g} m", file=sys.stderr)
    diag = math.hypot(W, Hh)
    f35_0 = f0 * 43.2666 / diag
    f_src = ridge.get("f0_source", "assumed")
    if args.focal_scales != "auto" and args.f35_range:
        sys.exit("give --focal-scales or --f35-range, not both")
    if args.focal_scales != "auto":
        fscales = [float(x) for x in args.focal_scales.split(",")]
        focal_how = "--focal-scales"
    elif args.f35_range or f_src == "assumed":
        try:
            lo, hi = (float(x) for x in args.f35_range.split(":")) if args.f35_range else F35_RANGE
        except ValueError:
            sys.exit(f"--f35-range must be lo:hi in mm, got {args.f35_range!r}")
        if not 0 < lo < hi:
            sys.exit("--f35-range needs 0 < lo < hi")
        n = max(2, math.ceil(math.log(hi / lo) / math.log(F35_RATIO)) + 1)
        fscales = [round(lo * (hi / lo) ** (i / (n - 1)) / f35_0, 4) for i in range(n)]
        focal_how = f"{lo:g}–{hi:g} mm equivalent, {n} steps"
    else:
        fscales = [0.9, 1.0, 1.12]
        focal_how = f"focal from {'EXIF' if f_src == 'exif' else '--f0'} × 0.9–1.12"
    px_metric = args.focal_metric == "px" or (args.focal_metric == "auto" and focal_how.endswith("steps"))
    print(f"focal ladder: {focal_how}, compared in {'pixels' if px_metric else 'degrees'} → " + ", ".join(f"{f35_0 * x:.0f}" for x in fscales) + " mm"
          + (f"; two-layer: {NX.size} near points, {NCX.size} near-clear columns, near distance {args.near_dist} m" if two else ""),
          file=sys.stderr)
    if args.grid <= 0 or args.radius < 0 or args.nsamp < 2 or args.near <= 0 or args.range <= args.near:
        sys.exit("need --grid > 0, --radius ≥ 0, --nsamp ≥ 2, 0 < --near < --range")
    az_step = args.az_step
    naz = int(round(360 / az_step))
    if abs(naz * az_step - 360) > 1e-6:
        sys.exit("--az-step must divide 360 evenly")
    if not 0 <= args.roll_max < 15:
        sys.exit("--roll-max must be between 0–15° (0 = don't solve roll, same as the old version)")
    roll_max = math.tan(math.radians(args.roll_max))
    AZ = np.arange(naz) * az_step
    HS = np.arange(naz)

    centers = _load_centers(args)
    if not centers:
        sys.exit("no candidate clusters")

    PS = None                                                         # (n, 4) segments lat1, lon1, lat2, lon2 for the heading constraint
    if args.perp_line:
        segs = []
        for f_ in json.loads(Path(args.perp_line).read_text(encoding="utf-8")).get("features", []):
            g_ = f_.get("geometry") or {}
            parts = [g_["coordinates"]] if g_.get("type") == "LineString" else g_.get("coordinates", []) if g_.get("type") == "MultiLineString" else []
            for c_ in parts:
                segs += [(y1, x1, y2, x2) for (x1, y1, *_), (x2, y2, *_) in zip(c_, c_[1:])]
        if not segs:
            sys.exit(f"--perp-line {args.perp_line}: no LineString in it")
        PS = np.array(segs, float)

    # linear infrastructure sample points (optional)
    LP = None
    if args.line:
        if not args.line_dist:
            sys.exit("--line requires --line-dist L:C:R (three distance intervals, e.g. 350-750:550-900:800-1700)")
        wins = _parse_pairs(args.line_win, "--line-win", 3, ",", ":")
        dwin = _parse_pairs(args.line_dist, "--line-dist", 3, ":", "-")
        scales = [float(x) for x in args.line_scale.split(",")]
        if len(scales) != 3 or min(scales) <= 0:
            sys.exit("--line-scale needs 3 positive numbers, comma-separated")
        skip = []
        for s_ in (args.skip_tag or ["electrified=no"]):
            if s_.lower() in ("none", "-"):
                continue
            if "=" not in s_:
                sys.exit(f"--skip-tag must be written as key=value, got {s_!r}")
            skip.append(tuple(s_.split("=", 1)))
        reach_deg = (args.radius + args.line_reach) / 110540 + 0.01
        lat_c = [c["lat"] for c in centers]
        lon_c = [c["lon"] for c in centers]
        bbox = (min(lat_c) - reach_deg, min(lon_c) - reach_deg * 1.2, max(lat_c) + reach_deg, max(lon_c) + reach_deg * 1.2)
        gj = json.loads(Path(args.line).read_text(encoding="utf-8"))
        pts = _line_points(gj, args.line_sample, skip, bbox)
        LP = np.array([[p[0], p[1]] for p in pts], dtype=float) if pts else np.zeros((0, 2))
        print(f"{len(LP)} infrastructure sample points (every {args.line_sample} m)", file=sys.stderr)

    ring_az = np.arange(0, 360, 45.0)
    ring_d = np.array([0.0, args.cam_flat_radius / 2, args.cam_flat_radius])
    done: set[tuple[int, int]] = set()
    recs: list[dict] = []
    clusters_out: list[dict] = []
    skipped = {"not_flat": 0, "no_peak": 0, "no_line": 0, "dup": 0, "missing_dem": 0, "no_perp_line": 0}
    dem_failed = []
    grid_pts = [(dx, dy) for dy in np.arange(-args.radius, args.radius + 1e-6, args.grid)
                for dx in np.arange(-args.radius, args.radius + 1e-6, args.grid) if dx * dx + dy * dy <= args.radius ** 2]
    if args.radius == 0:
        grid_pts = [(0.0, 0.0)]
    for ci, c in enumerate(centers):
        lat, lon = float(c["lat"]), float(c["lon"])
        name = c.get("name", "")
        try:
            dem = DEM((lat, lon), args.radius + args.range + 500, args.zoom, args.cache, args.proxy, args.allow_missing)
        except SystemExit as e:
            print(f"cluster {c['src_idx']} {name}: DEM failed ({e}), skipped", file=sys.stderr)
            dem_failed.append(c["src_idx"])
            continue
        kx = 111320 * math.cos(math.radians(lat))
        sub = None
        if LP is not None and len(LP):
            m = (np.abs(LP[:, 0] - lat) * 110540 < args.radius + args.line_reach) & (np.abs(LP[:, 1] - lon) * kx < args.radius + args.line_reach)
            sub = LP[m]
        n_c = 0
        best_c = None
        for dx, dy in grid_pts:
            dx, dy = float(dx), float(dy)
            clat = lat + dy / 110540
            clon = lon + dx / kx
            key = (round(clat * 110540 / args.grid), round(clon * kx / args.grid))
            if key in done:
                skipped["dup"] += 1
                continue
            done.add(key)
            rla, rlo = _dest_np(clat, clon, ring_az, ring_d)
            g = dem.sample(rla, rlo)
            if np.isnan(g).any():
                skipped["missing_dem"] += 1
                continue
            if g.max() - g.min() > args.cam_flat:
                skipped["not_flat"] += 1
                continue
            g0 = float(g[:, 0].mean())
            ang, dist_v = cast(dem, (clat, clon), g0 + args.eye, AZ, args.range, near=args.near, n=args.nsamp, keep_nan=True)
            if np.isnan(ang).any():                                   # a missing far tile would drop a ridge out of the skyline; don't rank on it
                skipped["missing_dem"] += 1
                continue
            hor = ang.max(axis=1)
            if hor.max() < args.min_peak:
                skipped["no_peak"] += 1
                continue
            h_ok = None
            line_brg = None
            if PS is not None:
                kxc = math.cos(math.radians(clat))
                # distance to each segment, not its midpoint: a long span's midpoint can be km away while the wire passes overhead
                ay, ax = (PS[:, 0] - clat) * 110540, (PS[:, 1] - clon) * 111320 * kxc
                by, bx = (PS[:, 2] - clat) * 110540, (PS[:, 3] - clon) * 111320 * kxc
                L2 = (bx - ax) ** 2 + (by - ay) ** 2
                t = np.clip(-(ax * (bx - ax) + ay * (by - ay)) / np.where(L2 > 0, L2, 1), 0, 1)
                d2 = (ax + t * (bx - ax)) ** 2 + (ay + t * (by - ay)) ** 2
                i_ = int(np.argmin(d2))
                if d2[i_] > args.perp_reach ** 2:
                    skipped["no_perp_line"] += 1
                    continue
                y1, x1, y2, x2 = PS[i_]
                line_brg = math.degrees(math.atan2((x2 - x1) * kxc, y2 - y1)) % 180
                h_ok = np.abs((AZ - line_brg) % 180 - 90) <= args.perp_tol
            line_pen = None
            dmins = None
            if LP is not None:
                if sub is None or not len(sub):
                    skipped["no_line"] += 1
                    continue
                by = (sub[:, 0] - clat) * 110540
                bx = (sub[:, 1] - clon) * 111320 * math.cos(math.radians(clat))
                bd = np.hypot(bx, by)
                baz = np.degrees(np.arctan2(bx, by)) % 360
                off = (baz[None, :] - AZ[:, None] + 180) % 360 - 180            # (naz, n points)
                far = bd > args.line_min
                dmins = []
                for lo_, hi_ in wins:
                    mm = (off > lo_) & (off < hi_) & far[None, :]
                    dmins.append(np.where(mm, bd[None, :], np.inf).min(axis=1))
                line_pen = np.zeros(naz)
                for dm, (dlo, dhi), sc in zip(dmins, dwin, scales):
                    line_pen += np.maximum(0, dlo - dm) / sc + np.maximum(0, dm - dhi) / sc
                if args.line_order == "asc":
                    line_pen += ((dmins[0] >= dmins[1]) | (dmins[1] >= dmins[2])) * 1.0
                elif args.line_order == "desc":
                    line_pen += ((dmins[0] <= dmins[1]) | (dmins[1] <= dmins[2])) * 1.0
                if not np.isfinite(line_pen).any():
                    skipped["no_line"] += 1
                    continue
            best = None
            def idx(off):
                return (HS[:, None] + np.round(off / az_step).astype(int)[None, :]) % naz
            nhs = {D1: ang[:, dist_v <= D1].max(axis=1) if D1 else None for D1 in near_dists}   # near layer: highest angle within D1 m
            for D1, fs in ((d_, f_) for d_ in near_dists for f_ in fscales):
                nh = nhs[D1]
                f = f0 * fs
                r_off = np.degrees(np.arctan((RX - cx) / f))
                r_el = np.degrees(np.arctan((hrow - RY) / f))
                # solve horizon offset cc (pitch/hrow inaccurate) and roll rr together by least squares: a 1° handheld tilt puts the ridgeline at both ends of the frame
                # off by a dozen-plus pixels; left unsolved, the ground truth gets crowded into the same rms tier as a pile of wrong candidates (one real photo: 11.1 → 6.2 px, only then did the ground truth stand out)
                diff = hor[idx(r_off)] - r_el[None, :]
                if NX.size:                                        # near points share cc and roll with the far ridge
                    n_off = np.degrees(np.arctan((NX - cx) / f))
                    diff = np.concatenate([diff, nh[idx(n_off)] - np.degrees(np.arctan((hrow - NY) / f))[None, :]], axis=1)
                    r_off = np.concatenate([r_off, n_off])
                if roll_max > 0 and (r_off != r_off.mean()).any():
                    oc = r_off - r_off.mean()
                    dmean = diff.mean(axis=1)
                    rr = np.clip(((diff - dmean[:, None]) * oc[None, :]).sum(axis=1) / (oc ** 2).sum(), -roll_max, roll_max)
                    cc = np.clip(dmean - rr * r_off.mean(), -args.cc_max, args.cc_max)
                else:                                              # --roll-max 0: like the old version, subtract only the median
                    rr = np.zeros(naz)
                    cc = np.clip(np.median(diff, axis=1), -args.cc_max, args.cc_max)
                res = diff - cc[:, None] - rr[:, None] * r_off[None, :]
                rms = np.sqrt(np.mean(res ** 2, axis=1))
                rms_near = np.sqrt(np.mean(res[:, RX.size:] ** 2, axis=1)) if NX.size else None
                if FLX.size:
                    fl_off = np.degrees(np.arctan((FLX - cx) / f))
                    pen = np.mean(np.clip(hor[idx(fl_off)] - cc[:, None] - args.flat_clear, 0, None), axis=1)
                else:
                    pen = np.zeros(naz)
                if NCX.size:                                       # near-clear columns: the near layer must stay below the given row
                    c_off = np.degrees(np.arctan((NCX - cx) / f))
                    c_el = np.degrees(np.arctan((hrow - NCR) / f))
                    ncpen = np.mean(np.clip(nh[idx(c_off)] - cc[:, None] - rr[:, None] * c_off[None, :] - c_el[None, :], 0, None), axis=1)
                else:
                    ncpen = np.zeros(naz)
                # across a wide focal ladder, compare in pixels (× fs, i.e. degrees at the base focal): in degrees the same pixel mismatch shrinks as f grows, and on a
                # real photo every candidate ran to the longest rung. Within ×0.9–1.12 degrees stay: there pixels pushed focal short and camera positions farther
                score = (rms + args.flat_w * pen + args.near_clear_w * ncpen) * (fs if px_metric else 1.0)
                total = score + args.line_w * line_pen if line_pen is not None else score
                if h_ok is not None:
                    total = np.where(h_ok, total, np.inf)
                k = int(np.argmin(total))
                if not np.isfinite(total[k]):
                    continue
                if best is None or total[k] < best["total"]:
                    best = {"hit": c["src_idx"], "name": name, "hit_ll": [round(lat, 5), round(lon, 5)],
                            "cam": [round(clat, 5), round(clon, 5)],
                            "d": round(math.hypot(dx, dy)), "brg": round(math.degrees(math.atan2(dx, dy)) % 360),
                            "g": round(g0, 1), "H": round(k * az_step, 2), "fs": fs, "f": round(f, 1), "f35": round(f35_0 * fs, 1),
                            "cc": round(float(cc[k]), 2), "roll": round(math.degrees(math.atan(float(rr[k]))), 2),
                            "rms": round(float(rms[k]), 3),
                            "rms_px": round(float(rms[k]) * f * math.pi / 180, 1), "flatpen": round(float(pen[k]), 3),
                            "score": round(float(score[k]), 3)}
                    if D1:
                        best.update({"D1": D1, "nclearpen": round(float(ncpen[k]), 3)})
                        if rms_near is not None:
                            best["rms_near_px"] = round(float(rms_near[k]) * f * math.pi / 180, 1)
                    if line_brg is not None:
                        best["line_brg"] = round(line_brg, 1)
                    if line_pen is not None:
                        best.update({"dL": round(float(dmins[0][k])), "dC": round(float(dmins[1][k])), "dR": round(float(dmins[2][k])),
                                     "line_pen": round(float(line_pen[k]), 3)})
                    best["total"] = round(float(total[k]), 3)
            if best is None:
                skipped["no_line"] += 1
                continue
            recs.append(best)
            n_c += 1
            if best_c is None or best["total"] < best_c["total"]:
                best_c = best
        clusters_out.append({"hit": c["src_idx"], "name": name, "hit_ll": [round(lat, 5), round(lon, 5)],
                             "n": c.get("n"), "max_ang": c.get("max_ang"), "n_cams": n_c, "best": best_c})
        print(f"cluster {ci + 1}/{len(centers)} hit{c['src_idx']} {name or '-'}: scored {n_c} camera positions"
              + (f", best total {best_c['total']}  H {best_c['H']}  cam {best_c['cam']}" if best_c else ", no camera position passed the filters"), file=sys.stderr)

    recs.sort(key=lambda r: r["total"])
    clusters_out.sort(key=lambda x: x["best"]["total"] if x["best"] else float("inf"))
    for i, x in enumerate(clusters_out):
        x["rank"] = i + 1
    hfov = 2 * math.degrees(math.atan(cx / f0))
    lead = [x["best"] for x in clusters_out if x["best"]] if len(clusters_out) > 1 else recs
    lead = lead[:10]
    focal_edge = None
    if len(fscales) > 1 and lead:
        lo_s, hi_s = min(fscales), max(fscales)
        n_long = sum(r["fs"] == hi_s for r in lead)
        n_short = sum(r["fs"] == lo_s for r in lead)
        top1 = "long" if lead[0]["fs"] == hi_s else "short" if lead[0]["fs"] == lo_s else None
        if top1 or max(n_long, n_short) * 2 >= len(lead):
            focal_edge = {"top1": top1, "long": n_long, "short": n_short, "of": len(lead),
                          "range_f35": [round(f35_0 * lo_s, 1), round(f35_0 * hi_s, 1)]}
    out = {
        "params": {"hits": args.hits, "at": args.at, "select": args.select, "ridge": str(args.ridge),
                   "radius_m": args.radius, "grid_m": args.grid, "zoom": args.zoom, "focal_scales": fscales,
                   "az_step_deg": az_step, "near_m": args.near, "range_m": args.range, "nsamp": args.nsamp, "eye_m": args.eye,
                   "focal": focal_how, "focal_metric": "px" if px_metric else "deg", "f35_ladder": [round(f35_0 * x, 1) for x in fscales],
                   "near_dist_m": near_dists if two else None, "near_clear_w": args.near_clear_w,
                   "perp_line": args.perp_line, "perp_tol_deg": args.perp_tol if args.perp_line else None,
                   "cam_flat_m": args.cam_flat, "cam_flat_radius_m": args.cam_flat_radius, "min_peak_deg": args.min_peak,
                   "cc_max_deg": args.cc_max, "roll_max_deg": args.roll_max, "flat_clear_deg": args.flat_clear, "flat_w": args.flat_w, "flat_step_px": args.flat_step,
                   "line": args.line, "line_dist": args.line_dist, "line_win": args.line_win if args.line else None,
                   "line_scale": args.line_scale if args.line else None, "line_order": args.line_order if args.line else None,
                   "line_w": args.line_w, "line_min_m": args.line_min, "line_sample_m": args.line_sample, "line_reach_m": args.line_reach,
                   "photo": {"f0_px": f0, "hrow": hrow, "cx": cx, "hfov_deg_at_fs1": round(hfov, 1), "n_ridge": int(RX.size), "flat": flat}},
        "n_clusters": len(clusters_out), "n_cams": len(recs), "n_skipped": skipped, "dem_failed_clusters": dem_failed,
        "focal_edge": focal_edge,
        "clusters": clusters_out,
        "cams": recs[:args.keep],
    }
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"clusters {len(clusters_out)}, camera positions {len(recs)}, skipped {skipped} → {args.out}", file=sys.stderr)
    if skipped["missing_dem"]:
        print(f"WARNING: {skipped['missing_dem']} camera positions not scored because their sight lines touch missing tiles", file=sys.stderr)
    for x in clusters_out[:min(args.top, 10)]:
        b = x["best"]
        if b:
            line_txt = f"  L/C/R {b['dL']}/{b['dC']}/{b['dR']} pen {b['line_pen']}" if "line_pen" in b else ""
            near_txt = (f"  D1 {b['D1'] / 1000:g} km near {b.get('rms_near_px', '-')} px clear {b['nclearpen']}" if "D1" in b else "")
            print(f"  {x['rank']:>3}. hit{x['hit']} {x['name'] or '-'}  cam {b['cam']}  H {b['H']}  f {b['f']:.0f} ({b['f35']:.0f} mm)  "
                  f"rms {b['rms']} ({b['rms_px']} px)  flat {b['flatpen']}{near_txt}{line_txt}  total {b['total']}", file=sys.stderr)
    if focal_edge:
        lo_mm, hi_mm = focal_edge["range_f35"]
        side = focal_edge["top1"] or ("long" if focal_edge["long"] >= focal_edge["short"] else "short")
        n_side = focal_edge[side]
        if f_src != "assumed" and args.focal_scales == "auto" and not args.f35_range:
            print(f"WARNING: focal is known ({'EXIF' if f_src == 'exif' else '--f0'}) yet {n_side}/{focal_edge['of']} leading results sit on the {side} end "
                  f"of ×0.9–1.12: it is absorbing another error (hrow, ridge points, crop, wrong place). Check ridge --png before widening.", file=sys.stderr)
        else:
            wider = f"{hi_mm * 0.6:.0f}:{hi_mm * 2:.0f}" if side == "long" else f"{max(8, lo_mm / 2):.0f}:{lo_mm * 1.7:.0f}"
            print(f"WARNING: best focal sits on the {side} end of the ladder ({hi_mm if side == 'long' else lo_mm:.0f} mm) for {n_side}/{focal_edge['of']} "
                  f"leading results{' including #1' if focal_edge['top1'] else ''}. That is a signal, not noise: the photo is probably "
                  f"{'more zoomed in' if side == 'long' else 'wider'} than the ladder. Rerun with --f35-range {wider} before trusting the ranking, "
                  f"heading or focal; only if it runs to the new edge again is the focal absorbing another error (geometry.md 7.4).", file=sys.stderr)
    if args.sheet:
        top = [x["best"] for x in clusters_out if x["best"]][:args.top] if len(clusters_out) > 1 else recs[:args.top]
        if not top:
            print("no camera positions to draw, no overlay", file=sys.stderr)
        else:
            photo = Path(args.photo) if args.photo else None
            if photo is None and ridge.get("photo"):
                # ridge.json records the path exactly as given on the command line, possibly relative: try the current directory first, then the directory of ridge.json
                cands = [Path(ridge["photo"]), Path(args.ridge).parent / ridge["photo"]]
                photo = next((p for p in cands if p.exists()), cands[0])
            if photo is None or not photo.exists():
                print("photo not found (--overlay not given, and the photo path in ridge.json can't be found either); drawing the overlay on a gray background", file=sys.stderr)
                photo = None
            _fit_sheet(top, ridge, photo, Path(args.sheet), args, AZ, args.nsamp)
    if dem_failed:                                                    # output is written, but the ranking is missing these clusters
        sys.exit(f"{len(dem_failed)}/{len(centers)} clusters not scored because their DEM failed "
                 f"(hit {', '.join(map(str, dem_failed))}); re-run to retry them, the ranking above is incomplete")


def _neg_coords(argv: list[str]) -> list[str]:
    """argparse treats negative coordinates like -1.45,-48.5 as option names; prefixing a space makes them plain values (float ignores spaces). Needed for any photo in the southern or western hemisphere.
    fit's --line-win -27:-21,-3:3,18:27 is the same case (a string of numbers separated by commas or colons)."""
    return [" " + a if re.match(r"^-\d[\d.]*([,:]-?[\d.]+)+$", a) else a for a in argv]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--proxy", default=os.environ.get("GEO_PROXY"), help=PROXY_HELP)
    ap.add_argument("--cache", type=Path, default=Path(".geo-cache/dem"))
    sub = ap.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("elev")
    e.add_argument("--at", required=True)
    e.add_argument("--zoom", type=int, default=13)
    e.add_argument("--allow-missing", action="store_true", help=MISSING_HELP)

    def common(sp):
        sp.add_argument("--at", required=True, help="candidate camera position lat,lon (WGS84)")
        g = sp.add_mutually_exclusive_group()
        g.add_argument("--height", type=float, default=1.6, help="height above ground m (for a shot from a building, use floor × 3)")
        g.add_argument("--alt", type=float, help="absolute altitude m (for aerial and mountaintop camera positions)")
        sp.add_argument("--heading", type=float, required=True, help="compass bearing of the frame center")
        sp.add_argument("--hfov", type=float, default=65, help="horizontal field of view; phone main camera about 65 landscape, about 50 portrait")
        sp.add_argument("--range", type=float, default=30000, help="how far to look (m)")
        sp.add_argument("--zoom", type=int, default=12, help="elevation tile zoom level, 12 ≈ 25–30 m per cell")
        sp.add_argument("--width", type=int, default=1400)
        sp.add_argument("--near", type=float, default=40, help="how near to start sampling, m; if spiky false ridgelines appear up close, raise to 150–300")
        sp.add_argument("--out", type=Path, required=True)
        sp.add_argument("--allow-missing", action="store_true", help=MISSING_HELP)

    v = sub.add_parser("view")
    common(v)
    v.add_argument("--pitch", type=float, default=0, help="pitch of the frame center, looking up is positive: a photo whose horizon sits below its middle was shot looking up (positive pitch)")
    v.add_argument("--vfov", type=float, help="vertical field of view; default derived from hfov for a 3:2 frame")
    v.add_argument("--photo", type=Path, help="scale the photo to the same width and place it above the render for comparison")
    v.add_argument("--roll", type=float, default=0, help="frame roll angle (clockwise positive), for downward shots from tall buildings and handheld tilt")
    v.add_argument("--overlay", action="store_true", help="also output a separate image: draw the synthetic skyline (red line) directly on the photo with the same heading/pitch/field of view")

    pr = sub.add_parser("profile")
    common(pr)

    sc = sub.add_parser("scan", formatter_class=argparse.RawDescriptionHelpFormatter, description="""\
Along linear infrastructure, compute the 360° horizon point by point, keep the points that are "flat nearby + a mountain + the mountain right next to a stretch of flat horizon", then cluster them.

Use when: the frame shows only one railway/road/power line and a mountain you can't recognize, with no text at all. First
get the lines with `osm.py geom '<filter>' --bbox <large region> --out lines.geojson`, then run this to cut the large region down to a few hundred patches;
the selected clusters go into `terrain.py fit` for skyline scoring. Method and the reasoning behind the values: references/corridors.md 4.3.

Set thresholds at about half of the photo estimate: one z10 cell is ~150 m, peaks get smoothed away, and the computed elevation angles come out smaller than the real ones.
In a real case, a threshold set at the photo's estimated 6° left not a single point near the ground truth; it only got in after loosening to 4.5° — better too many than a miss; leave the count to the next ranking step.

Output JSON (--out):
  {"params": {...all thresholds used in this run, recorded as is...},
   "n_samples": number of sample points, "n_hits": number of hit points, "n_clusters": number of clusters,
   "hits":     [{"lat","lon","h0": ground elevation at the point m, "max_ang": highest horizon elevation angle °,
                 "az": that bearing °, "relief": max relative height difference at that bearing m, "flat_run_deg": length of flat horizon right next to the mountain °,
                 "name","hs"(highspeed),"elec"(electrified),"id": OSM tags of the line}, ...],
   "clusters": [{...same as above..., "n": number of points in the cluster}, ...]}   # sorted by max_ang from largest to smallest; the cluster representative is the steepest point
--clusters-out writes a separate JSON with only the cluster list (exactly the clusters field).""")
    sc.add_argument("--lines", required=True, help="linear infrastructure GeoJSON (output of osm.py geom); only LineString is read")
    sc.add_argument("--out", required=True, help="output JSON")
    sc.add_argument("--clusters-out", help="also write a separate JSON with only the cluster list")
    sc.add_argument("--bbox", help="only scan sample points inside this range s,w,n,e (for validation and chunked runs; omitted = the whole geojson)")
    sc.add_argument("--step", type=float, default=400, help="take one point every this many meters along the line (default 400; anything in 300–500 works)")
    sc.add_argument("--zoom", type=int, default=10, help="elevation tile zoom level (default 10, one cell ~150 m, enough for mountain outlines)")
    sc.add_argument("--near-flat", type=float, default=40,
                    help="nearby relief limit m: if the height difference within --near-radius of the point exceeds it, the point is not flat and is dropped (default 40; the loosened version used 60)")
    sc.add_argument("--near-radius", type=float, default=1200, help="radius m for judging whether the nearby ground is flat (default 1200)")
    sc.add_argument("--near-step", type=float, default=300, help="nearby sampling interval m (default 300)")
    sc.add_argument("--min-peak", type=float, default=4.5,
                    help="mountain: horizon elevation angle of at least this many degrees (default 4.5, the value after loosening in a real case; the original strict value 6, estimated from that photo, filtered out all of the ground truth)")
    sc.add_argument("--max-low", type=float, default=1.2,
                    help="flat: a horizon elevation angle below this many degrees counts as flat horizon (default 1.2; the loosened version used 1.5)")
    sc.add_argument("--flat-run", type=float, default=20,
                    help="the stretch of flat horizon right next to the mountain must be at least this many degrees (default 20; original strict value 30)")
    sc.add_argument("--min-low-deg", type=float,
                    help="total flat horizon around the full circle of at least this many degrees (default same as --flat-run)")
    sc.add_argument("--flat-run-cap", type=float, default=100, help="count flat-horizon length at most this many degrees to one side (default 100)")
    sc.add_argument("--eye", type=float, default=1.5, help="eye height above ground m (default 1.5)")
    sc.add_argument("--az-step", type=float, default=5, help="bearing step ° (default 5, must divide 360 evenly)")
    sc.add_argument("--dist", default="1500,2000,2500,3000,3500,4000,5000,6000,7000,8000,9000",
                    help="distance steps measured outward along each bearing m, comma-separated (default 1.5–9 km)")
    sc.add_argument("--skip-tag", action="append",
                    help="skip lines carrying this tag, key=value, repeatable (default electrified=no; --skip-tag none means skip none)")
    sc.add_argument("--cluster-km", type=float, default=3.5, help="clustering radius km (default 3.5)")
    sc.add_argument("--threads", type=int, default=8, help="tile download concurrency (default 8; failed tiles are retried with backoff)")
    sc.add_argument("--allow-missing", action="store_true", help=MISSING_HELP)
    sc.add_argument("--max-tiles", type=int, default=4000,
                    help="limit on the number of tiles to download; exits immediately if exceeded (default 4000). Memory is set by the bounding rectangle of these tiles, "
                         "which can be several times the tile count when the line network is sparse; the actual usage is printed before the mosaic is built")

    rg = sub.add_parser("ridge", formatter_class=argparse.RawDescriptionHelpFormatter, description="""\
Photo ridgeline sampling: in --x0..--x1, every --step columns, top to bottom, find the sky→mountain brightness jump (the k rows above are brighter than the k rows below by --drop or more,
and the --hold rows further down are still dark), and take the maximum-gradient row as the ridge pixel. The output is for terrain.py fit.

--flat gives the column range where "the frame shows flat horizon" (the stretch on the left or right with no distant mountains); fit uses it to penalize "a mountain blocking where it should be flat".
Without --hrow, the horizon row is the median of the sky→ground jump rows in the --flat columns; without --flat, it is the frame midline.
Note that this estimate lands on top of things like distant treetops and bridge decks, 10–30 px above the true 0° horizon (on that photo: auto estimate 909,
hand-set 935); fit's horizon offset cc only absorbs ±0.7° (about ±16 px at f≈1300 px), so when there are tall objects in the distance, give --hrow by hand.
Focal length: --f0 > EXIF 35mm-equivalent focal length > assumed from --f35 (default 26 mm, phone main camera), converted to pixels via the diagonal; the source is written to f0_source.
An assumed focal is only the base: fit then searches 13–135 mm equivalent by default, so a zoomed shot is not forced into a main-camera fit.

--points replaces detection with hand-picked skyline points (cloud on the peaks, snow against a pale sky).
Two-layer photos (a lower near range in front of a higher far range, the near range ending mid-frame so the far range's foot shows):
  --near x,y;...        points on the near range's top edge; fit scores them against the highest terrain within a near distance
  --near-clear x0:x1@ROW columns past the near range's end, where nothing near may rise above ROW (the far range's foot / plain)

Output JSON (--out):
  {"photo": photo path (recorded exactly as given on the command line; if fit can't find it, it retries relative to the directory of ridge.json),
   "image_size": [width, height], "cx": center column,
   "ridge": [[x, y], ...],           # ridge pixel points, x column y row (y is the mountain's first row)
   "missing_cols": [x, ...],         # columns where no jump was found
   "ridge_source": "detected"|"points",
   "near": [[x, y], ...], "near_clear": [[x0, x1, row], ...],   # two-layer input, empty when not given
   "flat": [x0, x1] | null, "flat_rows": [jump row of each column in that range],
   "hrow": horizon row, "hrow_source": "arg"|"flat"|"center",
   "f0": focal length px, "f0_source": "arg"|"exif"|"assumed", "f35_equiv": 35mm-equivalent focal length,
   "params": {...parameters used in this run...}}
--png also outputs a check image: yellow dots = ridge points, red vertical lines = columns not found, blue line = hrow, cyan line = flat-horizon column range,
orange dots / lines = near points / near-clear rows. Look at the image before going to fit.""")
    rg.add_argument("photo", type=Path, help="photo")
    rg.add_argument("--x0", type=int, default=0, help="ridge start column (inclusive, default 0)")
    rg.add_argument("--x1", type=int, help="ridge end column (inclusive, default the last column)")
    rg.add_argument("--step", type=int, default=20, help="take one point every this many columns (default 20)")
    rg.add_argument("--flat", help="flat-horizon column range x0:x1 (e.g. 0:280); omit if there is none")
    rg.add_argument("--hrow", type=float, help="row of the horizon; if omitted, estimated from the --flat columns, and failing that, the frame midline")
    rg.add_argument("--f0", type=float, help="focal length px; if given, EXIF is not read")
    rg.add_argument("--f35", type=float, default=26.0, help="assumed 35mm-equivalent focal length mm when there is no EXIF (default 26, phone main camera; 2x telephoto 48–52)")
    rg.add_argument("--ymin", type=int, help="only search below this row (default 0; for clouds in the sky or foreground occlusion)")
    rg.add_argument("--ymax", type=int, help="only search above this row (default the frame bottom)")
    rg.add_argument("--drop", type=float, default=30, help="minimum amount the sky must be brighter than the mountain (0–255 brightness, default 30; in heavy haze lower to 15–20)")
    rg.add_argument("--k", type=int, default=4, help="rows taken above and below each when comparing brightness (default 4)")
    rg.add_argument("--hold", type=int, default=12, help="rows that must stay dark below the jump for it to count as mountain (default 12, used to skip wires and antennas)")
    rg.add_argument("--halfw", type=int, default=1, help="also average this many columns on each side of each column (default 1, i.e. 3 columns)")
    rg.add_argument("--points", help="hand-picked skyline points x,y;x,y;... (or a .json of [[x,y],...]) used instead of detection, "
                    "when cloud, haze or snow against a pale sky breaks the brightness jump; --x0/--x1 are then ignored")
    rg.add_argument("--near", help="two-layer photos: points x,y;x,y;... on the top edge of the NEAR range where it stands in front of a higher far range "
                    "(or a .json of [[x,y],...]); fit then scores the near layer too, see geometry.md 7.4")
    rg.add_argument("--near-clear", action="append",
                    help="two-layer photos: x0:x1@row = in these columns the near layer ends and the far range's foot or plain shows, "
                         "so nothing within the near distance may rise above this row; repeatable")
    rg.add_argument("--out", required=True, help="output ridge.json")
    rg.add_argument("--png", help="check image path")

    ft = sub.add_parser("fit", formatter_class=argparse.RawDescriptionHelpFormatter, description="""\
Batch skyline scoring: in each candidate cluster, lay a camera-position grid (one every --grid meters within --radius), compute the 360° horizon at each camera position,
convert ridge.json's ridge points to (bearing offset, elevation angle), and compare against all headings × --focal-scales at once:
  rms     = RMS of the ridge elevation-angle residuals (the residual median serves as horizon offset cc, clamped to ±--cc-max)
  flatpen = mean of max(0, horizon elevation angle − cc − --flat-clear) over the flat-horizon columns
  score   = rms + --flat-w × flatpen (+ --near-clear-w × nclearpen for two-layer ridge.json)
  rms_px  = rms converted to pixels (rms × f × π/180), for judging whether candidates can be separated (on an f35 ladder the score itself is compared in pixels, --focal-metric): when the top few all come out about as large as
            the error of the ridge sampling itself (a few to a dozen or so pixels), the skyline can't separate them; you need a second constraint
Camera positions first pass two filters: height difference within --cam-flat-radius ≤ --cam-flat (the camera stands on flat ground in the frame),
highest horizon elevation angle ≥ --min-peak (there are mountains to compare).
With --line (GeoJSON from osm.py geom), one more independent constraint is added: for each heading, the nearest distance dL/dC/dR of infrastructure sample points inside the frame's left/center/right bearing windows
(--line-win); distances outside the --line-dist intervals are penalized by meters/--line-scale (--line-order can also penalize the order),
total = score + --line-w × line_pen; headings where any of the three windows has no infrastructure don't count. Without --line, total = score.

Focal: --focal-scales auto (default) tries ×0.9/1/1.12 around an EXIF or --f0 focal, and a 13–135 mm equivalent ladder when ridge.json's focal was
assumed (no EXIF). If the leading results sit on an end of the ladder, fit prints a WARNING and writes focal_edge: rerun with --f35-range widened past
that end before trusting ranking, heading or focal. Running to the new end again means the focal is absorbing another error (bad ridge points, hrow, wrong place).
Two-layer (ridge.json has near / near_clear): the near layer = highest terrain within D1 m, D1 tried from --near-dist; near points share rms, cc and roll
with the far ridge. A far-only fit of a two-layer photo can match the far outline at a wrong heading and focal.
--perp-line keeps headings within --perp-tol of perpendicular to the nearest line (wires crossing the frame almost level).
Distant ranges: --range (default 15 km) must reach the far ridge; for ranges 20–40 km away use --range 45000 and lower --min-peak.

The coarse-search defaults are the ones from the real case: 2 km / 250 m / z11 / 0.5°; for fine search switch to --radius 800 --grid 100 --zoom 13 --az-step 0.25.
The skyline only gives one sight line (moving a few hundred meters forward or back along it doesn't change the outline); always look at the --sheet overlay for the top few, then pin the point with a second constraint.

Two things not to treat as conclusions:
  1. The output H and f have a systematic bias, which comes from hrow in ridge.json. In the same coarse search, hand-set hrow 935 gave H 80.5 / f 1436,
     and the auto-estimated 909 gave H 79.0 / f 1282 — a difference of 1.5° and 12% in focal length (cc can only absorb ±--cc-max). Cluster ranking isn't affected
     (both runs ranked the ground-truth cluster 1st), but before you argue from H/f, get hrow right first (check the blue line on ridge --png).
  2. Fine search (z13) is not guaranteed to be more accurate than coarse search. In tests on the same pipeline, fine search actually ended up farther from the ground truth than coarse search:
     the z13 flat filter (--cam-flat / --cam-flat-radius) filters out the points near the ground truth, and the skyline only gives one sight line anyway.
     In this pipeline, fine search's job is to give geo.py spacing a reliable --center, not to bring the error down by itself.
Method in references/geometry.md 7.4, corridors.md 4.3.

Output JSON (--out):
  {"params": {...all parameters used in this run, including f0/hrow/cx/hfov under photo...},
   "n_clusters", "n_cams": number of camera positions scored, "n_skipped": {"not_flat","no_peak","no_line","dup","missing_dem","no_perp_line"},
   "focal_edge": null | {"top1": "long"|"short"|null, "long", "short", "of": leading results counted, "range_f35": [lo, hi] mm},
   "dem_failed_clusters": hit indices whose elevation tiles failed to download (not scored),
   "clusters": [{"hit": the cluster's index in --hits, "name", "hit_ll": [lat,lon], "n", "max_ang", "n_cams", "rank",
                 "best": <camera record>}, ...],                      # best camera position of each cluster, ascending by total
   "cams":     [<camera record>, ...]}                                 # all camera positions ascending by total, at most --keep entries
  camera record: {"hit","name","hit_ll", "cam": [lat,lon], "d": distance from cluster center m, "brg": bearing cluster center→camera position °,
            "g": ground elevation m, "H": heading °, "fs": focal scale, "f": focal length px, "f35": 35mm-equivalent mm, "cc": horizon offset °, "roll",
            "rms", "rms_px", "flatpen", "score", [two-layer: "D1" m, "rms_near_px", "nclearpen"], [--perp-line: "line_brg"],
            [with --line: "dL","dC","dR" m, "line_pen"], "total"}
--sheet: with multiple clusters, draws the top --top of the per-cluster best camera positions; with a single cluster/--at, draws the top --top camera positions; red line = synthetic skyline, orange line = synthetic near layer, yellow dots = photo ridge points,
cyan dots = photo near points.""")
    src = ft.add_mutually_exclusive_group(required=True)
    src.add_argument("--hits", help="scan output JSON (uses the clusters field) or a cluster-list JSON")
    src.add_argument("--at", help="instead of --hits, give one center lat,lon directly (for fine search)")
    ft.add_argument("--select", help="only run the clusters at these indices in --hits, comma-separated (for validation and chunked runs)")
    ft.add_argument("--ridge", type=Path, required=True, help="output of terrain.py ridge")
    ft.add_argument("--out", required=True, help="output JSON")
    ft.add_argument("--radius", type=float, default=2000, help="camera-position grid radius per cluster m (default 2000; fine search 800)")
    ft.add_argument("--grid", type=float, default=250, help="camera-position grid spacing m (default 250; fine search 100)")
    ft.add_argument("--zoom", type=int, default=11, help="elevation tile zoom level (default 11, one cell ~70 m; fine search 13)")
    ft.add_argument("--focal-scales", default="auto",
                    help="focal length scales of ridge.json's f0, comma-separated. Default auto: EXIF or --f0 focal → 0.9,1,1.12; "
                         "no EXIF → a ladder over --f35-range (13–135 mm equivalent, ~18%% steps), because a guessed main camera "
                         "misses zoomed shots, which are common for distant mountains")
    ft.add_argument("--f35-range", help="lo:hi 35mm-equivalent focal range for the ladder, e.g. 40:270 after the best focal hit the long end; "
                    "overrides auto even with EXIF")
    ft.add_argument("--focal-metric", choices=["auto", "deg", "px"], default="auto",
                    help="unit in which scores are compared across focal lengths: deg (as before) or px (score × focal scale). "
                         "Default auto: px for an f35 ladder, deg for ×0.9–1.12; degrees favour the longest focal on a wide ladder")
    ft.add_argument("--near-dist", default="3000,5000,8000,12000",
                    help="two-layer only: candidate distances m out to which the near layer reaches, comma-separated (default 3000,5000,8000,12000)")
    ft.add_argument("--near-clear-w", type=float, default=1.5, help="two-layer only: weight of nclearpen (default 1.5)")
    ft.add_argument("--perp-line", help="linear infrastructure GeoJSON (osm.py geom); keep only headings near perpendicular to the nearest line, "
                    "for wires crossing the frame almost level overhead")
    ft.add_argument("--perp-tol", type=float, default=35, help="with --perp-line: allowed deviation ° from perpendicular (default 35)")
    ft.add_argument("--perp-reach", type=float, default=1500, help="with --perp-line: camera positions farther than this from any line m are skipped (default 1500)")
    ft.add_argument("--az-step", type=float, default=0.5, help="heading/bearing step ° (default 0.5; fine search 0.25; must divide 360 evenly)")
    ft.add_argument("--near", type=float, default=150, help="how near the sight line starts sampling m (default 150)")
    ft.add_argument("--range", type=float, default=15000, help="how far the sight line looks m (default 15000)")
    ft.add_argument("--nsamp", type=int, default=260, help="samples per sight line, dense near and sparse far (default 260; fine search 400)")
    ft.add_argument("--eye", type=float, default=1.6, help="eye height above ground m (default 1.6)")
    ft.add_argument("--cam-flat", type=float, default=8, help="height difference limit around the camera position m; above it, it isn't a flat-ground camera position (default 8; fine search has used 6)")
    ft.add_argument("--cam-flat-radius", type=float, default=300, help="radius m for judging whether the camera position is flat (default 300; fine search has used 200)")
    ft.add_argument("--min-peak", type=float, default=6, help="minimum highest horizon elevation angle in degrees for a camera position to be scored (default 6)")
    ft.add_argument("--cc-max", type=float, default=0.7, help="limit of horizon offset cc ° (default 0.7, i.e. hrow may be off by a dozen or so pixels)")
    ft.add_argument("--roll-max", type=float, default=1.0,
                    help="roll angle limit ° (default 1.0, the usual range of handheld tilt; 0 = don't solve roll, same as the old version)")
    ft.add_argument("--flat-clear", type=float, default=1.0, help="on the flat-horizon columns, horizon up to this many degrees above cc is not penalized (default 1.0)")
    ft.add_argument("--flat-w", type=float, default=1.5, help="flatpen weight (default 1.5)")
    ft.add_argument("--flat-step", type=float, default=20, help="take one column every this many pixels in the flat-horizon column range (default 20)")
    ft.add_argument("--line", help="linear infrastructure GeoJSON (output of osm.py geom); if given, adds the left/center/right distance constraint")
    ft.add_argument("--line-dist", help="three distance intervals left:center:right m, e.g. 350-750:550-900:800-1700 (required with --line)")
    ft.add_argument("--line-win", default="-27:-21,-3:3,18:27",
                    help="three bearing windows left/center/right, offset angle ° from the frame center (default -27:-21,-3:3,18:27, set for a 53° horizontal field of view; "
                         "writing --line-win=-27:... or putting the value right after both work)")
    ft.add_argument("--line-scale", default="200,200,300", help="penalty scale m of each of the three windows (default 200,200,300: 200 m out of bounds = penalty 1)")
    ft.add_argument("--line-order", choices=["none", "asc", "desc"], default="none",
                    help="order constraint on the three distances: asc = left<center<right (the infrastructure crosses the frame diagonally from near on the left to far on the right), desc the reverse; penalty 1 if not met (default none)")
    ft.add_argument("--line-w", type=float, default=0.3, help="line_pen weight (default 0.3)")
    ft.add_argument("--line-min", type=float, default=150, help="infrastructure points closer to the camera position than this distance don't count (default 150)")
    ft.add_argument("--line-sample", type=float, default=50, help="take one point every this many meters along the infrastructure line (default 50)")
    ft.add_argument("--line-reach", type=float, default=3000, help="only consider infrastructure points within this distance of the camera position m (default 3000)")
    ft.add_argument("--skip-tag", action="append", help="in --line, skip lines carrying this tag, key=value, repeatable (default electrified=no; none means skip none)")
    ft.add_argument("--top", type=int, default=20, help="how many top entries to print in the terminal and draw in --sheet (default 20)")
    ft.add_argument("--keep", type=int, default=5000, help="maximum number of entries written to the cams list (default 5000)")
    ft.add_argument("--sheet", help="overlay sheet jpg of the top --top")
    ft.add_argument("--overlay", "--photo", dest="photo", help="photo for the overlay; if omitted, uses the path recorded in ridge.json")
    ft.add_argument("--sheet-cols", type=int, default=4, help="overlay images per row (default 4)")
    ft.add_argument("--sheet-width", type=int, default=360, help="width of each overlay image px (default 360)")
    ft.add_argument("--allow-missing", action="store_true", help=MISSING_HELP)

    args = ap.parse_args(_neg_coords(sys.argv[1:]))
    if args.cmd == "scan":
        _cmd_scan(args)
        return
    if args.cmd == "ridge":
        _cmd_ridge(args)
        return
    if args.cmd == "fit":
        _cmd_fit(args)
        return
    lat, lon = map(float, args.at.split(","))
    if args.cmd == "elev":
        dem = DEM((lat, lon), 300, args.zoom, args.cache, args.proxy, args.allow_missing)
        h = float(dem.sample(np.array([lat]), np.array([lon]))[0])
        if math.isnan(h):
            sys.exit("no elevation here: the tile under this point failed to download")
        print(f"{h:.0f} m")
        return

    dem = DEM((lat, lon), args.range, args.zoom, args.cache, args.proxy, args.allow_missing)
    ground = float(dem.sample(np.array([lat]), np.array([lon]))[0])
    if math.isnan(ground):
        sys.exit("no elevation at the camera position: the tile under it failed to download")
    eye = args.alt if args.alt is not None else ground + args.height
    az = np.linspace(args.heading - args.hfov / 2, args.heading + args.hfov / 2, args.width)
    if eye < ground + 1:
        print(f"note: eye height {eye:.0f} m is below the ground at this point {ground:.0f} m, so nearby terrain will be taken as the skyline (--alt is wrong, or you should use --height)")
    ang, dist = cast(dem, (lat, lon), eye, az % 360, args.range, near=args.near)

    if args.cmd == "profile":
        runmax = np.max(ang, axis=1)
        far = dist[np.argmax(ang, axis=1)]
        step = max(1, args.width // 180)
        out = [{"azimuth": round(float(az[i] % 360), 2), "skyline_deg": round(float(runmax[i]), 3), "skyline_dist_m": round(float(far[i]))}
               for i in range(0, args.width, step)]
        args.out.write_text(json.dumps({"at": [lat, lon], "eye_alt_m": round(eye, 1), "ground_m": round(ground, 1), "profile": out}, indent=1), encoding="utf-8")
        print(f"ground {ground:.0f} m, eye height {eye:.0f} m → {args.out}")
        return

    vfov = args.vfov or 2 * math.degrees(math.atan(math.tan(math.radians(args.hfov / 2)) * 2 / 3))
    height = int(args.width * vfov / args.hfov)
    im, sky_ang, sky_dist = render(ang, dist, az, args.pitch, vfov, height)
    title = (f"camera {lat:.5f},{lon:.5f}  ground {ground:.0f} m eye {eye:.0f} m  heading {args.heading % 360:.0f}°  "
             f"hfov {args.hfov:.0f}°  farthest skyline {np.nanmax(sky_dist) / 1000:.1f} km")
    im = annotate(im, az, args.pitch, vfov, title)
    if args.roll:
        im = im.rotate(-args.roll, resample=Image.BICUBIC, fillcolor=(255, 255, 255))
    if args.photo and args.overlay:
        ph = Image.open(args.photo).convert("RGB")
        fpx = (ph.width / 2) / math.tan(math.radians(args.hfov / 2))
        cr, sr = math.cos(math.radians(args.roll)), math.sin(math.radians(args.roll))
        pts = []
        for a, e in zip(az, sky_ang):
            if e <= -89:
                continue
            x = fpx * math.tan(math.radians(a - args.heading))
            y = -fpx * math.tan(math.radians(e - args.pitch)) / math.cos(math.radians(a - args.heading))
            pts.append((ph.width / 2 + x * cr - y * sr, ph.height / 2 + x * sr + y * cr))
        ImageDraw.Draw(ph).line(pts, fill=(255, 40, 40), width=max(2, ph.width // 400))
        ov = args.out.with_name(args.out.stem + "_overlay" + args.out.suffix)
        ph.save(ov, quality=90)
        print(f"skyline overlaid on photo -> {ov} (if the red line doesn't match the photo's ridgeline, first adjust --heading/--pitch/--hfov/--roll, then suspect the camera position)")
    if args.photo:
        ph = Image.open(args.photo).convert("RGB")
        ph = ph.resize((args.width, int(ph.height * args.width / ph.width)))
        S = Image.new("RGB", (args.width, ph.height + im.height), "white")
        S.paste(ph, (0, 0))
        S.paste(im, (0, ph.height))
        im = S
    im.save(args.out)
    print(f"ground {ground:.0f} m, eye height {eye:.0f} m, skyline distance {np.nanmin(sky_dist) / 1000:.1f}–{np.nanmax(sky_dist) / 1000:.1f} km → {args.out}")


if __name__ == "__main__":
    # Chinese-locale Windows outputs GBK by default: it crashes on m² or ñ, and any Chinese the agent reads comes out garbled
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    main()
