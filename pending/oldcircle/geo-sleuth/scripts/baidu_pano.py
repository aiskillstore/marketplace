#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow"]
# ///
"""Baidu panoramas (street view in China): find points, scan an area, render by heading, build comparison sheets.

Uses the public endpoints the Baidu Maps web page itself calls; no key needed.
The endpoints are rate-limited: when scanning an area, keep the step at 15 m or more and concurrency at 32 or less.
Baidu street view in China was mostly captured in 2017–2019; when comparing, look at old buildings, new ones may not be there yet.

Examples:
  baidu_pano.py near 22.6047,114.0523                       # nearest panorama point
  baidu_pano.py info 09005700121709201230455178V            # date, position, all points on this road
  baidu_pano.py scan 22.6050,114.0535 --radius 300 --out panos.json
  baidu_pano.py render 09005700121709201230455178V --heading 47 --out v.jpg
  baidu_pano.py sheet --panos panos.json --toward 22.6072,114.0564 --offset -12 --out s.jpg
  baidu_pano.py sheet --ids ID1,ID2 --heading 45 --out s.jpg
  baidu_pano.py sheet --ids ID1 --headings 0,60,120,180,240,300 --out around.jpg   # look around from a single point
  baidu_pano.py sheet --panos panos.json --road <name>路 --spread 60 --toward 22.6072,114.0564 --out s.jpg  # one road only (路 = road), thinned
  baidu_pano.py sample --bbox 22.52,113.90,22.60,114.10 --n 24 --out cityA.jpg     # street-view sample of a candidate city: compare guardrails, streetlights, bus stops
"""
from __future__ import annotations

import argparse
from _net import fetch_bytes, PROXY_HELP
import io
import json
import math
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import geo  # noqa: E402

API = "https://mapsv0.bdimg.com/"


def _get(url: str, timeout: int = 20, proxy: str | None = None) -> bytes:
    return fetch_bytes(url, proxy, timeout)


def near_bdmc(x: float, y: float, proxy: str | None = None) -> dict | None:
    try:
        c = json.loads(_get(f"{API}?qt=qsdata&x={x:.0f}&y={y:.0f}", proxy=proxy)).get("content")
    except Exception:
        return None
    if not c:
        return None
    bx, by = c["x"] / 100, c["y"] / 100
    lat, lon = geo.convert(bx, by, "bdmc", "wgs")
    return {"id": c["id"], "bdmc": [bx, by], "wgs": [lat, lon], "road": c.get("RoadName", "")}


def near(lat: float, lon: float, proxy: str | None = None) -> dict | None:
    return near_bdmc(*geo.convert(lat, lon, "wgs", "bdmc"), proxy=proxy)


def info(pid: str, proxy: str | None = None) -> dict:
    c = json.loads(_get(f"{API}?qt=sdata&sid={pid}", proxy=proxy))["content"][0]
    x, y = c["X"] / 100, c["Y"] / 100
    lat, lon = geo.convert(x, y, "bdmc", "wgs")
    roads = []
    for r in c.get("Roads") or []:
        roads.append([{"id": p["PID"], "wgs": list(geo.convert(p["X"] / 100, p["Y"] / 100, "bdmc", "wgs"))}
                      for p in (r.get("Panos") or [])])        # some points (construction access roads, isolated points) have no road-segment info
    return {"id": pid, "date": c.get("Date"), "wgs": [lat, lon], "bdmc": [x, y],
            "move_dir": c.get("MoveDir"), "roads": roads,
            "timeline": [t.get("ID") for t in (c.get("TimeLine") or [])]}


def scan(lat: float, lon: float, radius_m: float, step_m: float, workers: int = 24, proxy: str | None = None) -> dict:
    """Query the nearest panorama point at each point of a square grid; deduplicate and return {id: {...}}."""
    pts = []
    n = int(radius_m // step_m)
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            p = geo.dest(geo.dest((lat, lon), 0, i * step_m), 90, j * step_m)
            pts.append(p)
    found: dict = {}
    with ThreadPoolExecutor(workers) as ex:
        for r in ex.map(lambda p: near(*p, proxy=proxy), pts):
            if r:
                found[r["id"]] = r
    return found


def thin(panos: dict, spread_m: float) -> dict:
    """Thin by minimum spacing: of points closer than spread_m, keep only the first."""
    kept: dict = {}
    for k, v in panos.items():
        if all(geo.distance(tuple(v["wgs"]), tuple(u["wgs"])) >= spread_m for u in kept.values()):
            kept[k] = v
    return kept


def sample(bbox: tuple[float, float, float, float], n: int, spread_m: float, seed: int,
           skip: list[str], named_only: bool = True, workers: int = 16, proxy: str | None = None) -> list[dict]:
    """Scatter random points in the area to find panoramas, deduplicate, thin by spacing, take n; the heading is the capture car's direction of travel (along the road)."""
    import random
    rnd = random.Random(seed)
    s, w, nn, e = bbox
    found: dict = {}
    tries = 0
    while len(found) < n and tries < n * 8:
        batch = [(rnd.uniform(s, nn), rnd.uniform(w, e)) for _ in range(n * 2)]
        tries += len(batch)
        with ThreadPoolExecutor(workers) as ex:
            for r in ex.map(lambda p: near(*p, proxy=proxy), batch):
                if not r or r["id"] in found or any(k in (r.get("road") or "") for k in skip):
                    continue
                if named_only and not r.get("road"):        # points without a road name are mostly internal roads of residential compounds and campuses, with no municipal fixtures in view
                    continue
                if not (s <= r["wgs"][0] <= nn and w <= r["wgs"][1] <= e):
                    continue
                if all(geo.distance(tuple(r["wgs"]), tuple(u["wgs"])) >= spread_m for u in found.values()):
                    found[r["id"]] = r
                if len(found) >= n:
                    break
    items = []
    with ThreadPoolExecutor(8) as ex:
        infos = list(ex.map(lambda pid: info(pid, proxy=proxy), list(found)[:n]))
    for inf in infos:
        v = found[inf["id"]]
        items.append({"id": inf["id"], "heading": (inf.get("move_dir") or 0) % 360, "pitch": 0, "fov": 60,
                      "date": inf.get("date"), "wgs": v["wgs"], "road": v.get("road", ""),
                      "label": f"{(v.get('road') or '')[:10]} {str(inf.get('date') or '')[:6]}"})
    return items


def render(pid: str, heading: float, pitch: float = 10, fov: float = 80,
           w: int = 1024, h: int = 768, cache: Path | None = None, proxy: str | None = None) -> Image.Image:
    """Render a perspective view at a compass heading. heading 0 = north, positive pitch = looking up, fov is the vertical field of view. Max width 1024."""
    w = min(w, 1024)
    key = f"{pid}_{heading:.0f}_{pitch:.0f}_{fov:.0f}_{w}x{h}.jpg"
    if cache:
        cache.mkdir(parents=True, exist_ok=True)
        if (cache / key).exists():
            return Image.open(cache / key)
    url = (f"{API}?qt=pr3d&fovy={fov:.0f}&quality=80&panoid={pid}&heading={heading:.1f}"
           f"&pitch={pitch:.1f}&width={w}&height={h}")
    try:
        data = _get(url, 40, proxy)
    except Exception:
        return Image.new("RGB", (w, h), "gray")
    if cache:
        (cache / key).write_bytes(data)
    return Image.open(io.BytesIO(data))


def _font(size: int):
    for p in ("/System/Library/Fonts/STHeiti Medium.ttc", "/System/Library/Fonts/Hiragino Sans GB.ttc",
              "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"):
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def sheet(items: list[dict], out: Path, cols: int = 3, tw: int = 480, th: int = 360,
          cache: Path | None = None, proxy: str | None = None) -> None:
    """items: [{id, heading, pitch?, fov?, label?}] → numbered contact sheet."""
    def one(it):
        return render(it["id"], it["heading"], it.get("pitch", 10), it.get("fov", 80), cache=cache, proxy=proxy)

    with ThreadPoolExecutor(12) as ex:
        ims = list(ex.map(one, items))
    rows = (len(items) + cols - 1) // cols
    S = Image.new("RGB", (cols * tw, rows * th), "black")
    d = ImageDraw.Draw(S)
    f = _font(16)
    for i, (it, im) in enumerate(zip(items, ims)):
        x, y = (i % cols) * tw, (i // cols) * th
        S.paste(im.convert("RGB").resize((tw, th)), (x, y))
        text = it.get("label") or f"{i}: …{it['id'][-9:]} h{it['heading']:.0f}"
        d.rectangle([x, y, x + tw, y + 22], fill="black")
        d.text((x + 4, y + 2), text, fill="yellow", font=f)
    S.save(out, quality=88)



def _neg_coords(argv: list[str]) -> list[str]:
    """argparse treats negative coordinates like -1.45,-48.5 as option names; prefixing a space makes them plain values (float ignores the space). Needed for every puzzle in the southern or western hemisphere."""
    return [" " + a if re.match(r"^-\d[\d.]*(,-?[\d.]+)+$", a) else a for a in argv]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--proxy", help=PROXY_HELP)
    ap.add_argument("--cache", type=Path, default=Path(".geo-cache/pano"))
    sub = ap.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("near")
    n.add_argument("latlon")

    i = sub.add_parser("info")
    i.add_argument("id")

    s = sub.add_parser("scan")
    s.add_argument("center")
    s.add_argument("--radius", type=float, default=250)
    s.add_argument("--step", type=float, default=20)
    s.add_argument("--out", type=Path, required=True)

    r = sub.add_parser("render")
    r.add_argument("id")
    r.add_argument("--heading", type=float, required=True)
    r.add_argument("--pitch", type=float, default=10)
    r.add_argument("--fov", type=float, default=80)
    r.add_argument("--out", type=Path, required=True)

    sh = sub.add_parser("sheet")
    g = sh.add_mutually_exclusive_group(required=True)
    g.add_argument("--ids", help="comma-separated panoids")
    g.add_argument("--panos", type=Path, help="JSON output of scan")
    g.add_argument("--spec", type=Path, help="JSON list [{id, heading, pitch, fov, label}]")
    sh.add_argument("--heading", type=float, help="one heading for all")
    sh.add_argument("--headings", help="render these headings at every point, comma-separated, e.g. 0,60,120,180,240,300 (look around from a single point)")
    sh.add_argument("--toward", help="lat,lon: each point faces this target")
    sh.add_argument("--offset", type=float, default=0, help="angle added on top of the toward bearing")
    sh.add_argument("--pitch", type=float, default=10)
    sh.add_argument("--fov", type=float, default=80)
    sh.add_argument("--within", help="lat,lon,radius in meters: only points inside this circle")
    sh.add_argument("--road", help="only points whose road name contains these characters (the road field in scan output); comma-separated for several")
    sh.add_argument("--spread", type=float, help="thinning: minimum meters between neighboring points")
    sh.add_argument("--limit", type=int, default=12, help="max cells per contact sheet; extra cells go to more pages automatically")
    sh.add_argument("--out", type=Path, required=True)

    sp = sub.add_parser("sample", help="random street-view sample contact sheet of a candidate city/area: compare the styles of municipal fixtures such as guardrails, streetlights, bus stops, curbs")
    sp.add_argument("--bbox", required=True, help="south,west,north,east (urban area)")
    sp.add_argument("--n", type=int, default=24, help="how many points to sample")
    sp.add_argument("--spread", type=float, default=300, help="minimum spacing between two points, m")
    sp.add_argument("--seed", type=int, default=1)
    sp.add_argument("--skip", default="隧道,高速,高架,匝道,立交", help="skip points whose road name contains these characters, comma-separated (default: tunnel, expressway, elevated road, ramp, interchange)")
    sp.add_argument("--heading-offset", type=float, default=0, help="extra degrees to turn from the along-road direction (90 = look at the roadside)")
    sp.add_argument("--include-unnamed", action="store_true", help="also take points without a road name (internal roads of residential compounds, campuses); skipped by default")
    sp.add_argument("--out", type=Path, required=True)

    for parser in (n, i, s, r, sh, sp):
        parser.add_argument("--proxy", default=argparse.SUPPRESS, help=PROXY_HELP)
    args = ap.parse_args(_neg_coords(sys.argv[1:]))
    if args.cmd == "sample":
        bb = tuple(map(float, args.bbox.split(",")))
        items = sample(bb, args.n, args.spread, args.seed, [k for k in args.skip.split(",") if k],
                       named_only=not args.include_unnamed, proxy=args.proxy)
        for it in items:
            it["heading"] = (it["heading"] + args.heading_offset) % 360
        if not items:
            sys.exit("no panorama points found in the area (area too small, or no Baidu street view here)")
        pages = [items[k:k + 12] for k in range(0, len(items), 12)]
        for pi, page in enumerate(pages):
            out = args.out if pi == 0 else args.out.with_name(f"{args.out.stem}_{pi + 1}{args.out.suffix}")
            sheet(page, out, cache=args.cache, proxy=args.proxy)
            print(out)
        idx = args.out.with_suffix(".index.json")
        idx.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
        dates = sorted(str(i.get("date") or "")[:4] for i in items)
        print(f"{len(items)} points, capture years {dates[0]}–{dates[-1]}; index -> {idx}")
        return
    if args.cmd == "near":
        print(json.dumps(near(*map(float, args.latlon.split(",")), proxy=args.proxy), ensure_ascii=False))
    elif args.cmd == "info":
        print(json.dumps(info(args.id, proxy=args.proxy), ensure_ascii=False, indent=1))
    elif args.cmd == "scan":
        lat, lon = map(float, args.center.split(","))
        res = scan(lat, lon, args.radius, args.step, proxy=args.proxy)
        args.out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{len(res)} panos -> {args.out}")
    elif args.cmd == "render":
        render(args.id, args.heading, args.pitch, args.fov, cache=args.cache, proxy=args.proxy).save(args.out)
        print(args.out)
    elif args.cmd == "sheet":
        if args.spec:
            items = json.loads(args.spec.read_text(encoding="utf-8"))
        else:
            if args.ids:
                need_pos = bool(args.within or args.toward)
                panos = {p: (info(p, proxy=args.proxy) if need_pos else None) for p in args.ids.split(",")}
            else:
                panos = json.loads(args.panos.read_text(encoding="utf-8"))
            if args.within:
                wl, wo, wr = map(float, args.within.split(","))
                panos = {k: v for k, v in panos.items() if geo.distance((wl, wo), v["wgs"]) <= wr}
            if args.road:
                keys = [k for k in args.road.split(",") if k]
                panos = {k: v for k, v in panos.items() if any(x in ((v or {}).get("road") or "") for x in keys)}
                print(f"{len(panos)} points after --road filter")
            if args.spread:
                panos = thin(panos, args.spread)
                print(f"{len(panos)} points after --spread thinning")
            target = tuple(map(float, args.toward.split(","))) if args.toward else None
            items = []
            for pid, v in panos.items():
                if args.headings:
                    for hd in (float(x) for x in args.headings.split(",")):
                        items.append({"id": pid, "heading": hd % 360, "pitch": args.pitch, "fov": args.fov})
                    continue
                if target:
                    hd = geo.bearing(tuple(v["wgs"]), target) + args.offset
                elif args.heading is not None:
                    hd = args.heading
                else:
                    ap.error("need --heading, --headings or --toward")
                items.append({"id": pid, "heading": hd % 360, "pitch": args.pitch, "fov": args.fov})
        pages = [items[k:k + args.limit] for k in range(0, len(items), args.limit)] or [[]]
        for pi, page in enumerate(pages):
            # page 1 is written to --out itself, later pages get _2, _3…, to avoid "the file given by --out doesn't exist"
            out = args.out if pi == 0 else args.out.with_name(f"{args.out.stem}_{pi + 1}{args.out.suffix}")
            sheet(page, out, cache=args.cache, proxy=args.proxy)
            print(out)
        if len(pages) > 1:
            print(f"{len(pages)} pages: {args.out.name} plus {args.out.stem}_2 … _{len(pages)}, {args.limit} cells per page")
        if len(pages) > 1 or args.spec is None:
            idx = args.out.with_suffix(".index.json")
            idx.write_text(json.dumps(items, indent=1), encoding="utf-8")
            print(f"index -> {idx}")


if __name__ == "__main__":
    # Chinese-locale Windows writes GBK by default: m², ñ make it crash, and the Chinese the agent reads comes out garbled
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    main()
