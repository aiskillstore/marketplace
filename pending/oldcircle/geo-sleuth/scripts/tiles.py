#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow"]
# ///
"""Download satellite tiles, stitch them into one large image (mosaic), and mark points on it.

A .json with the same name is written next to the mosaic (zoom level, top-left tile index, center point);
evidence.py and the mark subcommand use it to convert lat/lon to image pixels.

Google satellite imagery is the default (WGS84, the same coordinate system as GPS, no offset correction needed in China).

Examples:
  tiles.py fetch 22.6050,114.0540 --zoom 18 --radius 4 --out area.jpg
  tiles.py mark area.jpg --points panos.json --out area_panos.jpg --label
  tiles.py mark area.jpg --points cands.json --geojson power.geojson --geojson rail.geojson \
           --sector 22.6045,114.0520,265,40,3000 --out area_lines.jpg       # overlay line features + camera-position view sector
  tiles.py sheet --points cands.json --zoom 18 --out cands_sheet.jpg     # one centered thumbnail per candidate point, numbered
  tiles.py px2ll area.jpg --px 812,440 --px 300,95                      # mosaic pixels → lat/lon (for a cropped image add --crop x0,y0 --scale s)
  tiles.py sheet --grid <s,w,n,e> --zoom 17 --size 320 --cols 5 --out town.jpg   # tile a whole urban area with a grid and look cell by cell (find running tracks, factory buildings)
"""
from __future__ import annotations

import argparse
from _net import curl_args, PROXY_HELP
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
import geo  # noqa: E402

SOURCES = {
    "google": "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
    "esri": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
}


def _get(url: str, path: Path, proxy: str | None) -> bool:
    if path.exists() and path.stat().st_size > 1000:
        return True
    cmd = ["curl", "-q", "-s", "-m", "60", "-o", str(path), url]
    cmd += curl_args(proxy)
    subprocess.run(cmd, check=False)
    return path.exists() and path.stat().st_size > 1000


def fetch(center: tuple[float, float], zoom: int, radius: int, out: Path, source: str,
          proxy: str | None, cache: Path) -> dict:
    cache.mkdir(parents=True, exist_ok=True)
    gx, gy = geo.ll2px(zoom, *center)
    cx, cy = int(gx // 256), int(gy // 256)
    xs = range(cx - radius, cx + radius + 1)
    ys = range(cy - radius, cy + radius + 1)
    jobs = [(x, y) for x in xs for y in ys]

    def job(t):
        x, y = t
        p = cache / f"{source}_{zoom}_{x}_{y}.jpg"
        ok = _get(SOURCES[source].format(x=x, y=y, z=zoom), p, proxy)
        return t, p, ok

    img = Image.new("RGB", (256 * len(xs), 256 * len(ys)), "black")
    failed = 0
    with ThreadPoolExecutor(16) as ex:
        for (x, y), p, ok in ex.map(job, jobs):
            if not ok:
                failed += 1
                continue
            try:
                img.paste(Image.open(p), ((x - xs[0]) * 256, (y - ys[0]) * 256))
            except Exception:
                failed += 1
    img.save(out, quality=90)
    meta = {"zoom": zoom, "origin_tile": [xs[0], ys[0]], "center": list(center), "source": source,
            "size": list(img.size), "m_per_px": geo.meters_per_px(zoom, center[0]), "failed_tiles": failed}
    out.with_suffix(".json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


class Mosaic:
    """lat/lon ↔ mosaic pixels."""

    def __init__(self, image: Path):
        self.meta = json.loads(Path(image).with_suffix(".json").read_text(encoding="utf-8"))
        self.z = self.meta["zoom"]
        self.ox, self.oy = self.meta["origin_tile"]

    def to_px(self, lat: float, lon: float) -> tuple[float, float]:
        x, y = geo.ll2px(self.z, lat, lon)
        return x - self.ox * 256, y - self.oy * 256

    def to_ll(self, x: float, y: float) -> tuple[float, float]:
        return geo.px2ll(self.z, x + self.ox * 256, y + self.oy * 256)


PALETTE = ["yellow", "cyan", "magenta", "lime", "orange", "white", "red", "deepskyblue"]


LINE_COLORS = ["orange", "deepskyblue", "magenta", "lime", "white", "red"]


def _draw_geojson(d: ImageDraw.ImageDraw, m: "Mosaic", gj: dict, color: str) -> int:
    """Draw GeoJSON lines, polygons and points on the mosaic (line width 3, polygons as outlines only). Returns how many features were drawn."""
    n = 0
    for ft in gj.get("features", []):
        g = ft.get("geometry") or {}
        t, cs = g.get("type"), g.get("coordinates")
        if not cs:
            continue
        lines = {"LineString": [cs], "MultiLineString": cs, "Polygon": cs,
                 "MultiPolygon": [ring for poly in cs for ring in poly]}.get(t)
        if lines is not None:
            for ln in lines:
                xy = [m.to_px(c[1], c[0]) for c in ln]
                if len(xy) >= 2:
                    d.line(xy, fill=color, width=3)
            n += 1
        elif t == "Point":
            x, y = m.to_px(cs[1], cs[0])
            d.rectangle([x - 3, y - 3, x + 3, y + 3], outline=color, width=2)
            n += 1
    return n


def _draw_sector(d: ImageDraw.ImageDraw, m: "Mosaic", spec: str) -> None:
    """lat,lon,heading,horizontal FOV,radius m → camera-position view sector."""
    lat, lon, hd, fov, rng = map(float, spec.split(","))
    pts = [m.to_px(lat, lon)]
    steps = max(4, int(fov // 3))
    for k in range(steps + 1):
        a = hd - fov / 2 + fov * k / steps
        pts.append(m.to_px(*geo.dest((lat, lon), a, rng)))
    d.line(pts + [pts[0]], fill="yellow", width=3)
    mid = m.to_px(*geo.dest((lat, lon), hd, rng))
    d.line([pts[0], mid], fill="yellow", width=1)
    x, y = pts[0]
    d.ellipse([x - 7, y - 7, x + 7, y + 7], fill="red", outline="yellow", width=2)


def mark(image: Path, points: dict, out: Path, label: bool, geojsons: list[Path] | None = None,
         sectors: list[str] | None = None) -> None:
    """points: {name: [lat, lon]} (wgs). Colored by the name prefix before the first space; with --label, writes the first 12 characters of the name."""
    m = Mosaic(image)
    img = Image.open(image).convert("RGB")
    d = ImageDraw.Draw(img)
    for i, gp in enumerate(geojsons or []):
        n = _draw_geojson(d, m, json.loads(Path(gp).read_text(encoding="utf-8")), LINE_COLORS[i % len(LINE_COLORS)])
        print(f"{gp}: {n} features, color {LINE_COLORS[i % len(LINE_COLORS)]}")
    for sp in sectors or []:
        _draw_sector(d, m, sp)
    groups: dict[str, str] = {}
    for name, ll in points.items():
        lat, lon = ll[0], ll[1]
        prefix = str(name).split(" ")[0].rstrip("0123456789") or "_"
        color = groups.setdefault(prefix, PALETTE[len(groups) % len(PALETTE)])
        x, y = m.to_px(lat, lon)
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=color, outline="black")
        if label:
            d.text((x + 7, y - 6), str(name)[:12], fill=color)
    img.save(out, quality=90)


def grid_points(bbox: str, zoom: int, size: int, step: float | None) -> dict:
    """Tile s,w,n,e into grid points; default spacing = 90% of the width each cell covers."""
    import math

    s, w, n, e = (float(v) for v in bbox.split(","))
    mpp = 156543.03392 * math.cos(math.radians((s + n) / 2)) / 2 ** zoom
    step = step or size * mpp * 0.9
    dlat, dlon = step / 110574, step / (111320 * math.cos(math.radians((s + n) / 2)))
    pts, r, lat = {}, 0, n - dlat / 2
    while lat > s:
        c, lon = 0, w + dlon / 2
        while lon < e:
            pts[f"r{r:02d}c{c:02d}"] = [round(lat, 6), round(lon, 6)]
            c, lon = c + 1, lon + dlon
        r, lat = r + 1, lat - dlat
    return pts


def sheet(points: dict, zoom: int, size: int, cols: int, out: Path, source: str, proxy: str | None, cache: Path) -> list[Path]:
    """One size×size satellite thumbnail centered on each candidate point, with number and name, laid out on one page (more pages automatically when there are too many)."""
    cache.mkdir(parents=True, exist_ok=True)
    items = list(points.items())
    per = cols * cols
    pages = []
    for pi in range(0, len(items), per):
        chunk = items[pi:pi + per]
        rows = (len(chunk) + cols - 1) // cols
        S = Image.new("RGB", (cols * size, rows * size), "black")
        dr = ImageDraw.Draw(S)
        for k, (name, ll) in enumerate(chunk):
            gx, gy = geo.ll2px(zoom, ll[0], ll[1])
            x0, y0 = gx - size / 2, gy - size / 2
            tile = Image.new("RGB", (size, size), "gray")
            for tx in range(int(x0 // 256), int((x0 + size) // 256) + 1):
                for ty in range(int(y0 // 256), int((y0 + size) // 256) + 1):
                    p = cache / f"{source}_{zoom}_{tx}_{ty}.jpg"
                    if _get(SOURCES[source].format(x=tx, y=ty, z=zoom), p, proxy):
                        try:
                            tile.paste(Image.open(p), (int(tx * 256 - x0), int(ty * 256 - y0)))
                        except Exception:  # noqa: BLE001
                            pass
            cx, cy = (k % cols) * size, (k // cols) * size
            S.paste(tile, (cx, cy))
            c = size / 2
            dr.line([cx + c - 12, cy + c, cx + c + 12, cy + c], fill="red", width=2)
            dr.line([cx + c, cy + c - 12, cx + c, cy + c + 12], fill="red", width=2)
            dr.rectangle([cx, cy, cx + size, cy + 20], fill="black")
            dr.text((cx + 4, cy + 3), f"#{pi + k + 1} {str(name)[:28]}", fill="yellow")
        o = out if pi == 0 else out.with_name(f"{out.stem}_{pi // per + 1}{out.suffix}")
        S.save(o, quality=88)
        pages.append(o)
    return pages



def _neg_coords(argv: list[str]) -> list[str]:
    """argparse treats negative coordinates like -1.45,-48.5 as option names; prefixing a space makes them plain values (float ignores the space). Needed for every puzzle in the southern or western hemisphere."""
    return [" " + a if re.match(r"^-\d[\d.]*(,-?[\d.]+)+$", a) else a for a in argv]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("fetch")
    f.add_argument("center", help="lat,lon (wgs)")
    f.add_argument("--zoom", type=int, default=18, help="17≈1.1m/px for an area, 19≈0.28m/px for a single building")
    f.add_argument("--radius", type=int, default=4, help="rings of tiles around the center tile, 4 → 9x9 tiles")
    f.add_argument("--out", type=Path, required=True)
    f.add_argument("--source", choices=list(SOURCES), default="google")
    f.add_argument("--proxy", default=os.environ.get("GEO_PROXY"), help=PROXY_HELP)
    f.add_argument("--cache", type=Path, default=Path(".geo-cache/tiles"))

    mk = sub.add_parser("mark")
    mk.add_argument("image", type=Path)
    mk.add_argument("--points", type=Path, help="JSON: {name: [lat, lon]}")
    mk.add_argument("--out", type=Path, required=True)
    mk.add_argument("--label", action="store_true")
    mk.add_argument("--geojson", type=Path, action="append", help="overlay GeoJSON (output of osm.py geom), repeatable, one color per file")
    mk.add_argument("--sector", action="append", help="camera-position view sector lat,lon,heading,horizontal FOV,radius m, repeatable")

    sh = sub.add_parser("sheet", help="centered satellite thumbnail for each candidate point, laid out as a numbered comparison page")
    shg = sh.add_mutually_exclusive_group(required=True)
    shg.add_argument("--points", type=Path, help="JSON {name: [lat, lon]}")
    shg.add_argument("--grid", help="s,w,n,e: cover an area with a grid and render cell by cell (cell name r<row>c<col>: r00 northernmost, c00 westernmost; center coordinates written to <out>.cells.json)")
    sh.add_argument("--step", type=float, help="--grid cell spacing (meters); default leaves 10%% overlap of the area each cell covers")
    sh.add_argument("--zoom", type=int, default=18)
    sh.add_argument("--size", type=int, default=320, help="pixels per cell")
    sh.add_argument("--cols", type=int, default=4, help="cols×cols cells per page")
    sh.add_argument("--out", type=Path, required=True)
    sh.add_argument("--source", choices=list(SOURCES), default="google")
    sh.add_argument("--proxy", default=os.environ.get("GEO_PROXY"), help=PROXY_HELP)
    sh.add_argument("--cache", type=Path, default=Path(".geo-cache/tiles"))

    pl = sub.add_parser("px2ll", help="pixels on a mosaic (or a cropped/scaled copy of it) → lat/lon")
    pl.add_argument("image", type=Path, help="mosaic from tiles.py fetch (needs the same-name .json next to it)")
    pl.add_argument("--px", action="append", required=True, help="x,y, repeatable; if you measured on a cropped/scaled image, pair with --crop/--scale")
    pl.add_argument("--crop", default="0,0", help="top-left x0,y0, in the original mosaic, of the image you measured pixels on")
    pl.add_argument("--scale", type=float, default=1.0, help="scale of that image relative to the original mosaic (0.5 for half size)")
    pl.add_argument("--out", type=Path, help="write {p1: [lat, lon], ...}")

    args = ap.parse_args(_neg_coords(sys.argv[1:]))
    if args.cmd == "px2ll":
        m = Mosaic(args.image)
        x0, y0 = (float(v) for v in args.crop.split(","))
        pts = {}
        for i, s in enumerate(args.px, 1):
            x, y = (float(v) for v in s.split(","))
            lat, lon = m.to_ll(x0 + x / args.scale, y0 + y / args.scale)
            pts[f"p{i}"] = [round(lat, 6), round(lon, 6)]
            print(f"p{i}  ({x:.0f},{y:.0f}) → {lat:.6f},{lon:.6f}")
        if args.out:
            args.out.write_text(json.dumps(pts, indent=1), encoding="utf-8")
            print(f"-> {args.out}")
        return
    if args.cmd == "sheet":
        pts = json.loads(args.points.read_text(encoding="utf-8")) if args.points else grid_points(args.grid, args.zoom, args.size, args.step)
        if args.grid:
            args.out.with_suffix(".cells.json").write_text(json.dumps(pts, indent=1), encoding="utf-8")
            print(f"grid: {len(pts)} cells (cell name r<row>c<col>, rows north to south, columns west to east; cell center coordinates -> {args.out.with_suffix('.cells.json')})")
        for p in sheet(pts, args.zoom, args.size, args.cols, args.out, args.source, args.proxy, args.cache):
            print(p)
        return
    if args.cmd == "fetch":
        lat, lon = map(float, args.center.split(","))
        meta = fetch((lat, lon), args.zoom, args.radius, args.out, args.source, args.proxy, args.cache)
        print(json.dumps(meta))
    elif args.cmd == "mark":
        if not (args.points or args.geojson or args.sector):
            ap.error("mark needs at least one of --points, --geojson, --sector")
        mark(args.image, json.loads(args.points.read_text(encoding="utf-8")) if args.points else {}, args.out, args.label,
             args.geojson, args.sector)
        print(args.out)


if __name__ == "__main__":
    # Chinese-locale Windows writes GBK by default: m², ñ make it crash, and the Chinese the agent reads comes out garbled
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    main()
