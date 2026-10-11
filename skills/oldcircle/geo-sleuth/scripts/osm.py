#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""OpenStreetMap Overpass queries: find candidate points by "feature combinations" and "linear corridors" instead of searching the whole map.

Suited to photos with "no name, but structure": a power tower next to a high-speed rail bridge, a church at a river bend, a level crossing with four tracks...
Data outside China is very complete; in China, roads, rivers, railways, power lines and large buildings are usable, while small shops and compound interiors are basically missing.
OSM data in China is incomplete: results can only be a source of candidates, not grounds for exclusion.

  find       find features of one kind within an area
  near       find A that has B within N meters (optionally also C)
  crossings  line-to-point: bridges, dams, ferries, level crossings on a river / railway / road (level crossings estimate track count from node count)
  route      bus / rail / ferry route number → sample points along the route, turning "search the whole city" into "search along one line"
  intersect  crossing points of two kinds of linear features (railway × power line ...), optionally requiring a bend beyond the crossing (angle tower, river bend)
  street-scan street view geometry template: bearing looking down a street + "building / no building" on each side → candidate intersections for a whole town
  along      take points at a step along any road / river / line (optionally offset to one side of the road), for satellite thumbnails or street view scans of the roadside
  buildings  list large buildings by footprint area (factories, warehouses, farm sheds), marking how sparse the surroundings are
  coverage   how many features of a kind each candidate admin area has: check OSM coverage before enumerating candidates
  geom       export GeoJSON for any filter (keeps line and polygon geometry) for custom analysis
  raw        run your own Overpass QL ({{bbox}} is replaced with s,w,n,e)

Run queries one after another: public Overpass servers reject parallel requests from one address (every mirror then fails), and a bbox query is often faster than --area for a whole province.

Outputs JSON {name or id: [lat, lon]} (WGS84), which can go straight to tiles.py mark --points to draw on satellite imagery.

Examples (江苏省 = Jiangsu Province, 长江 = Yangtze River):
  osm.py find --bbox 30.24,120.12,30.27,120.17 '["highway"="street_lamp"]'
  osm.py near --area 江苏省 --a '["railway"="rail"]["highspeed"="yes"]["bridge"]' --b '["power"="tower"]' --within 700 --c '["waterway"="river"]' --within-c 100
  osm.py crossings --bbox 31.9,118.4,32.3,119.0 --line '["waterway"="river"]["name"="长江"]' --kind bridge,dam,ferry
  osm.py crossings --bbox <s,w,n,e> --line '["railway"="rail"]' --kind level_crossing
  osm.py route --bbox <s,w,n,e> --kind bus --ref <route number> --step 150 --out route.json
  osm.py intersect --area <full name of province-level admin area> --a '["railway"="rail"]["electrified"="contact_line"]' --b '["power"="line"]' --bend-min 25 --rank-near '["place"~"^(city|town)$"]'
  osm.py street-scan --bbox <town s,w,n,e> --bearing 320:80 --right building --left empty --out cands.json
  osm.py geom '["building"]' --bbox 30.25,120.15,30.26,120.16 --out b.geojson
  osm.py along --bbox <s,w,n,e> --line '["highway"]["ref"="<road number>"]' --step 400 --side north --offset 80 --out pts.json
  osm.py buildings --bbox <s,w,n,e> --min-area 1500 --sort sparse --out big.json
  osm.py coverage --areas <district A>,<district B>,<district C> --filter '["leisure"~"^(pitch|track)$"]'
  osm.py raw query.overpassql --bbox 30.2,120.1,30.3,120.2
"""
from __future__ import annotations

import argparse
from _net import curl_args, PROXY_HELP
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time
from pathlib import Path

# Independent services only: overpass.kumi.systems is the old name of private.coffee (same server), so it can't confirm or replace it
ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]
# overpass-api.de rejects curl's default User-Agent with HTTP 406; public instances ask clients to identify themselves
UA = "geo-sleuth (+https://github.com/Oldcircle/geo-sleuth)"


AREA_SET = re.compile(r"(\((?:area\[[^;]*\];)+\))->\.(\w+);")


def _post(ep: str, ql: str, proxy: str | None, timeout: int) -> tuple[dict | None, str]:
    """(reply, "") or (None, "HTTP 504: <what the server said>")."""
    cmd = ["curl", "-q", "-s", "-m", str(timeout + 30), "-A", UA, "-w", "\n%{http_code}", "--data-urlencode", f"data={ql}", ep]
    cmd += curl_args(proxy)
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    body, _, code = (r.stdout or "").rpartition("\n")
    if r.returncode:
        return None, f"curl exit {r.returncode}"
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        text = " ".join(re.sub(r"<[^>]+>", " ", body).split())
        return None, f"HTTP {code}: {text[:160]}"
    return (data, "") if isinstance(data, dict) else (None, f"HTTP {code}: {str(data)[:160]}")


def _area_empty(data: dict, ql: str) -> bool:
    """An --area query that came back empty (or with a zero area count). Mirrors disagree on these: one answered a whole-province
    power-line query with a clean, empty result while others returned thousands, so an empty answer needs a second mirror."""
    if not AREA_SET.search(ql):
        return False
    els = data.get("elements") or []
    if els and els[0].get("type") == "count":            # coverage / _area_count: the first count is the area count
        return int((els[0].get("tags") or {}).get("total", 0)) == 0
    return not els


def run(ql: str, proxy: str | None, cache: Path, timeout: int = 180, rounds: int = 3) -> dict:
    """Try each mirror in turn; when servers are busy (common for public Overpass), wait a while and retry the whole round. Results are cached per query.
    Error replies are never cached; an empty --area result is cached only when a second mirror agrees."""
    cache.mkdir(parents=True, exist_ok=True)
    key = cache / (hashlib.sha1(ql.encode()).hexdigest()[:16] + ".json")
    if key.exists():
        return json.loads(key.read_text(encoding="utf-8"))
    errs: dict[str, str] = {}
    empty_from = None
    for rnd in range(rounds):
        for ep in ENDPOINTS:
            if ep == empty_from:
                continue
            data, err = _post(ep, ql, proxy, timeout)
            if data is None:
                errs[ep] = err
                continue
            remark = data.get("remark") or ""
            if remark and not data.get("elements"):       # runtime error / timeout / out of memory with nothing returned
                errs[ep] = f"remark: {remark[:160]}"
                continue
            if _area_empty(data, ql) and empty_from is None:
                empty_from, first_empty = ep, data
                continue
            if remark:
                print(f"Overpass remark (results may be incomplete): {remark[:200]}", file=sys.stderr)
            key.write_text(json.dumps(data), encoding="utf-8")
            return data
        if empty_from is not None:
            print(f"Only {empty_from} answered, with an empty --area result; not confirmed by a second mirror, so not cached. "
                  f"Rerun later, or use --bbox, before treating it as \"none\".", file=sys.stderr)
            return first_empty
        last = "; ".join(f"{ep.split('/')[2]} {e}" for ep, e in errs.items())
        if rnd < rounds - 1:
            print(f"No Overpass mirror returned a result, retrying in {15 * (rnd + 1)} s: {last}", file=sys.stderr)
            time.sleep(15 * (rnd + 1))
    sys.exit(f"Overpass query failed on every mirror ({last}). HTTP 504/\"too busy\": retry later, or use --bbox / a smaller area; "
             f"HTTP 400: check the query syntax; curl exit: network or proxy (doctor.py --network)")


def _area_sel(name: str, var: str, loose: bool = False) -> str:
    """Get OSM areas by name and store them in set var.
    Chinese ethnic autonomous regions have bilingual names in OSM ("新疆维吾尔自治区 شىنجاڭ…" (Xinjiang), "西藏自治区 བོད་…" (Tibet), Inner Mongolia with Mongolian script),
    so ["name"="…"] alone silently returns 0 results; that's why name:zh / name:zh-Hans are matched too (indexed, fast).
    loose=True also adds a prefix regex "name + space + other text" as a fallback for bilingual names without name:zh; it scans all area names, which is slow, so use it only when the lookup above finds nothing."""
    q = name.replace("\\", "\\\\").replace('"', '\\"')
    sel = f'area["name"="{q}"];area["name:zh"="{q}"];area["name:zh-Hans"="{q}"];'
    if loose:
        rx = re.sub(r'([.^$*+?()\[\]{}|\\])', r"\\\\\1", name).replace('"', '\\"')
        sel += f'area["name"~"^{rx} "];'
    return f"({sel})->.{var};"


def _area_count(name: str, args, loose: bool = False) -> int:
    """How many areas OSM returns for this name (used after a 0-result query to tell "really none" from "wrong name")."""
    els = run(f"[out:json][timeout:120];{_area_sel(name, 'a', loose)}.a out count;", args.proxy, args.cache).get("elements") or []
    return int(((els[0].get("tags") or {}).get("total", 0)) if els else 0)


def _scope(args) -> tuple[str, str]:
    """Returns (preamble statement, filter suffix)."""
    if args.area:
        return _area_sel(args.area, "searchArea", getattr(args, "area_loose", False)), "(area.searchArea)"
    if args.bbox:
        s, w, n, e = args.bbox
        return "", f"({s},{w},{n},{e})"
    sys.exit("Need --bbox or --area")


def _center(el: dict) -> list[float] | None:
    if el["type"] == "node":
        return [el.get("lat"), el.get("lon")]
    c = el.get("center") or {}
    return [c["lat"], c["lon"]] if "lat" in c else None


def _points(data: dict) -> dict:
    out = {}
    for el in data.get("elements", []):
        ll = _center(el)
        if not ll or ll[0] is None:
            continue
        name = (el.get("tags") or {}).get("name") or f"{el['type']}/{el['id']}"
        if name in out:
            name = f"{name}#{el['id']}"
        out[name] = [round(ll[0], 6), round(ll[1], 6)]
    return out


def _dist(a, b) -> float:
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371008.8 * math.asin(math.sqrt(h))


def _cluster(items: list[tuple[str, list[float], dict]], radius: float) -> list[dict]:
    """Merge results within radius meters into one place (a bridge is often split into several ways; a level crossing has one node per track)."""
    groups: list[dict] = []
    for name, ll, tags in items:
        for g in groups:
            if _dist(g["center"], ll) <= radius:
                g["members"].append((name, ll, tags))
                n = len(g["members"])
                g["center"] = [(g["center"][0] * (n - 1) + ll[0]) / n, (g["center"][1] * (n - 1) + ll[1]) / n]
                break
        else:
            groups.append({"center": list(ll), "members": [(name, ll, tags)]})
    return groups


def _sample(elements: list[dict], step: float) -> list[list[float]]:
    """Take a point every step meters along the lines from out geom."""
    pts = []
    for el in elements:
        geom = el.get("geometry") or []
        acc = 0.0
        for a, b in zip(geom, geom[1:]):
            pa, pb = (a["lat"], a["lon"]), (b["lat"], b["lon"])
            seg = _dist(pa, pb)
            while seg > 0 and acc <= seg:
                t = acc / seg
                pts.append([round(pa[0] + (pb[0] - pa[0]) * t, 6), round(pa[1] + (pb[1] - pa[1]) * t, 6)])
                acc += step
            acc -= seg
    return pts


def cmd_crossings(args) -> dict:
    pre, sc = _scope(args)
    kinds = set(args.kind.split(","))
    buf = f"{args.buffer:.0f}"
    parts = []
    if "bridge" in kinds:
        parts.append(f'way["bridge"]["bridge"!="no"](around.L:{buf}){sc};')
    if "dam" in kinds:
        parts.append(f'nwr["waterway"~"^(dam|weir)$"](around.L:{buf}){sc};')
    if "ferry" in kinds:
        parts.append(f'way["route"="ferry"](around.L:{buf}){sc};')
    if "level_crossing" in kinds:
        parts.append(f'node["railway"~"^(level_crossing|crossing)$"](around.L:{buf}){sc};')
    if not parts:
        sys.exit("--kind only supports bridge,dam,ferry,level_crossing")
    ql = f"[out:json][timeout:180];{pre}way{args.line}{sc}->.L;(" + "".join(parts) + ");out center tags;"
    items = []
    for el in run(ql, args.proxy, args.cache).get("elements", []):
        ll = _center(el)
        if not ll or ll[0] is None:
            continue
        tags = el.get("tags") or {}
        items.append((tags.get("name") or "", ll, tags))
    groups = _cluster(items, 25 if kinds == {"level_crossing"} else 150)
    print(f"{len(groups)} places (merged from {len(items)} OSM features)")
    pts = {}
    for i, g in enumerate(groups, 1):
        tags = [m[2] for m in g["members"]]
        names = sorted({m[0] for m in g["members"] if m[0]})
        if any(t.get("railway") in ("level_crossing", "crossing") for t in tags):
            kind = f"level crossing·~{len(g['members'])} tracks"
        elif any(t.get("waterway") in ("dam", "weir") for t in tags):
            kind = "dam/weir"
        elif any(t.get("route") == "ferry" for t in tags):
            kind = "ferry route"
        else:
            use = {("railway" if t.get("railway") else "road" if t.get("highway") else "other") for t in tags}
            kind = "bridge·" + "/".join(sorted(use))
        label = f"{i:02d} {kind} {', '.join(names)[:40]}".strip()
        pts[label] = [round(g["center"][0], 6), round(g["center"][1], 6)]
    return pts


def cmd_route(args) -> dict:
    pre, sc = _scope(args)
    flt = f'["type"="route"]["route"="{args.kind}"]'
    if args.ref:
        flt += f'["ref"="{args.ref}"]'
    if args.name:
        flt += f'["name"~"{args.name}"]'
    ql = f"[out:json][timeout:180];{pre}relation{flt}{sc}->.R;.R out tags;way(r.R);out geom;"
    data = run(ql, args.proxy, args.cache)
    rels = [e for e in data.get("elements", []) if e["type"] == "relation"]
    ways = [e for e in data.get("elements", []) if e["type"] == "way"]
    for rel in rels:
        t = rel.get("tags") or {}
        print(f"  route {t.get('ref', '')} {t.get('name', '')} {t.get('from', '')}→{t.get('to', '')}")
    pts = _sample(ways, args.step)
    print(f"{len(rels)} route relations, {len(ways)} ways; one point every {args.step:.0f} m along the route, {len(pts)} points total")
    if pts:
        lats, lons = [p[0] for p in pts], [p[1] for p in pts]
        print(f"  route extent bbox: {min(lats):.4f},{min(lons):.4f},{max(lats):.4f},{max(lons):.4f}")
    return {f"R{i}": p for i, p in enumerate(pts)}


def cmd_intersect(args) -> dict:
    """Crossing points of two kinds of linear features (railway × power line, river × road ...), optionally requiring B to bend beyond the crossing (angle tower, river bend)."""
    pre, sc = _scope(args)
    ql = (f"[out:json][timeout:280];{pre}way{args.a}{sc}->.a;way{args.b}(around.a:30){sc}->.b;"
          f".a out geom tags;.b out geom tags;")
    data = run(ql, args.proxy, args.cache, timeout=280)
    A = [e for e in data.get("elements", []) if e.get("geometry") and _match(e, args.a)]
    B = [e for e in data.get("elements", []) if e.get("geometry") and e not in A]
    if not A or not B:
        print(f"A {len(A)} lines, B {len(B)} lines: no crossing points possible (change the area or tags)")
        return {}
    lat0 = A[0]["geometry"][0]["lat"]
    kx, ky = 111320 * math.cos(math.radians(lat0)), 110540

    def pr(g):
        return (g["lon"] * kx, g["lat"] * ky)

    cells: dict[tuple[int, int], list] = {}
    for el in A:
        pts = [pr(g) for g in el["geometry"]]
        for s0, s1 in zip(pts, pts[1:]):
            for c in {(int(s0[0] // 500), int(s0[1] // 500)), (int(s1[0] // 500), int(s1[1] // 500))}:
                cells.setdefault(c, []).append((s0, s1, el))

    def cross(p1, p2, p3, p4):
        d = (p2[0] - p1[0]) * (p4[1] - p3[1]) - (p2[1] - p1[1]) * (p4[0] - p3[0])
        if abs(d) < 1e-9:
            return None
        t = ((p3[0] - p1[0]) * (p4[1] - p3[1]) - (p3[1] - p1[1]) * (p4[0] - p3[0])) / d
        u = ((p3[0] - p1[0]) * (p2[1] - p1[1]) - (p3[1] - p1[1]) * (p2[0] - p1[0])) / d
        if 0 <= t <= 1 and 0 <= u <= 1:
            return (p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1]))
        return None

    def find_bend(el, hit):
        """First bend ≥bend_min in B within bend_within beyond the crossing: returns (distance m, turn angle °) or None."""
        if args.bend_min <= 0:
            return None
        lo, hi = _band(args.bend_within)
        pts = [pr(g) for g in el["geometry"]]
        k = min(range(len(pts)), key=lambda i: math.dist(pts[i], hit))
        for direction in (1, -1):
            d = 0.0
            i = k
            while 0 < i + direction < len(pts) - 1:
                nxt = i + direction
                d += math.dist(pts[i], pts[nxt])
                i = nxt
                if d > hi:
                    break
                if d < lo:
                    continue
                a1 = math.atan2(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
                a2 = math.atan2(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
                turn = abs(math.degrees(a2 - a1))
                turn = min(turn % 360, 360 - turn % 360)
                if turn >= args.bend_min:
                    return round(d), round(turn)
        return None

    hits = []
    for el in B:
        pts = [pr(g) for g in el["geometry"]]
        for s0, s1 in zip(pts, pts[1:]):
            for c in {(int(s0[0] // 500), int(s0[1] // 500)), (int(s1[0] // 500), int(s1[1] // 500))}:
                for a0, a1, ael in cells.get(c, []):
                    x = cross(a0, a1, s0, s1)
                    if not x:
                        continue
                    ta, tb = ael.get("tags") or {}, el.get("tags") or {}
                    lbl = " ".join(filter(None, [ta.get("name", ""), tb.get("name", ""), tb.get("voltage", ""),
                                                 ta.get("electrified", "")]))
                    hits.append((lbl[:40], [x[1] / ky, x[0] / kx], {"bend": find_bend(el, x)}))
    groups = _cluster(hits, args.cluster)
    rows = []
    for g in groups:
        bends = [m[2]["bend"] for m in g["members"] if m[2]["bend"]]
        rows.append({"label": g["members"][0][0], "ll": [round(g["center"][0], 6), round(g["center"][1], 6)],
                     "bend": min(bends) if bends else None})
    if args.ring:
        c_ll, rmin, rmax = args.ring.split(":")
        c = tuple(map(float, c_ll.split(",")))
        before = len(rows)
        rows = [r for r in rows if float(rmin) <= _dist(c, r["ll"]) <= float(rmax)]
        print(f"--ring: {len(rows)}/{before} places kept in the ring {rmin}–{rmax} m from {c_ll}")
    print(f"A {len(A)} lines × B {len(B)} lines → {len(hits)} crossing points, merged into {len(groups)} clusters")
    if args.bend_min > 0:
        with_bend = [r for r in rows if r["bend"]]
        print(f"  of these, {len(with_bend)} have a bend ≥{args.bend_min:g}° in B within {args.bend_within} m beyond the crossing"
              f" (labeled \"bend\"; used only for ranking, see --bend-filter)")
        if args.bend_filter:
            dropped = [r for r in rows if not r["bend"]]
            rows = with_bend
            print(f"  --bend-filter: dropped {len(dropped)} crossing points without a bend. The bend comes from interpreting the photo; "
                  f"if none of the candidates match, look back at this dropped batch first")
            if args.out and dropped:
                dp = args.out.with_name(args.out.stem + "_dropped.json")
                dp.write_text(json.dumps({f"{i:03d} {r['label']}".strip(): r["ll"] for i, r in enumerate(dropped, 1)},
                                         ensure_ascii=False, indent=1), encoding="utf-8")
                print(f"  dropped -> {dp}")
    if args.rank_near:
        rows = _rank_rows(rows, args.rank_near, args)
    elif args.bend_min > 0:
        rows.sort(key=lambda r: r["bend"] is None)
    out = {}
    for i, r in enumerate(rows, 1):
        extra = []
        if r["bend"]:
            extra.append(f"bend {r['bend'][0]}m/{r['bend'][1]}°")
        if r.get("near_m") is not None:
            extra.append(f"{r['near_m'] / 1000:.1f}km from {r['near_name'][:6]}")
        out[f"{i:03d} {r['label']} {' '.join(extra)}".strip()] = r["ll"]
    return out



_SIDES = {"north": (0.0, 1.0), "south": (0.0, -1.0), "east": (1.0, 0.0), "west": (-1.0, 0.0)}


def cmd_along(args) -> dict:
    """Take a point every step meters along any linear feature (road, river, power line filtered by ref / name), optionally shifting all points to one side of the road.
    With --bbox, only points inside the box are kept (Overpass returns the whole length of any road that crosses the box).

    For tiles.py sheet (satellite thumbnails scanning roadside factories, shops, fields) and gsv.py / baidu_pano.py sheet --points (street view scanning storefronts).
    """
    pre, sc = _scope(args)
    data = run(f"[out:json][timeout:180];{pre}way{args.line}{sc};out geom;", args.proxy, args.cache)
    ways = [e for e in data.get("elements", []) if e["type"] == "way" and e.get("geometry")]
    side = _SIDES.get(args.side) if args.side else None
    pts, seen = {}, []
    for w in ways:
        g = [(n["lat"], n["lon"]) for n in w["geometry"]]
        acc = 0.0
        for a, b in zip(g, g[1:]):
            seg = _dist(a, b)
            if seg <= 0:
                continue
            kx = 111320 * math.cos(math.radians(a[0]))
            ux, uy = (b[1] - a[1]) * kx / seg, (b[0] - a[0]) * 110574 / seg  # unit vector (east, north components)
            while acc <= seg:
                t = acc / seg
                lat, lon = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                if side and args.offset:
                    nx, ny = -uy, ux  # left normal
                    if nx * side[0] + ny * side[1] < 0:
                        nx, ny = uy, -ux
                    lat += ny * args.offset / 110574
                    lon += nx * args.offset / kx
                ll = (round(lat, 6), round(lon, 6))
                inside = not args.bbox or (args.bbox[0] <= ll[0] <= args.bbox[2] and args.bbox[1] <= ll[1] <= args.bbox[3])
                if inside and not any(_dist(ll, s) < args.step * 0.5 for s in seen[-200:]):
                    seen.append(ll)
                    name = (w.get("tags") or {}).get("ref") or (w.get("tags") or {}).get("name") or f"w{w['id']}"
                    pts[f"{len(pts):04d} {name}"] = list(ll)
                acc += args.step
            acc -= seg
    print(f"{len(ways)} ways, one point every {args.step:.0f} m, {len(pts)} points total" + (f", offset {args.offset:.0f} m to the {args.side} side" if side else ""))
    if pts:
        lats, lons = [v[0] for v in pts.values()], [v[1] for v in pts.values()]
        print(f"  extent bbox: {min(lats):.4f},{min(lons):.4f},{max(lats):.4f},{max(lons):.4f}")
    return pts


def _ring_area(coords: list[tuple[float, float]]) -> float:
    if len(coords) < 3:
        return 0.0
    lat0 = sum(c[0] for c in coords) / len(coords)
    kx, ky = 111320 * math.cos(math.radians(lat0)), 110574
    xy = [(c[1] * kx, c[0] * ky) for c in coords]
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(xy, xy[1:] + xy[:1]))) / 2


def cmd_buildings(args) -> dict:
    """Find buildings with large footprints (factories, warehouses, farm sheds, mine facilities): filter by footprint area and mark how many other buildings are around.

    In many countries OSM's rural building outlines are traced from satellite imagery, so they have an area even without a name; in China, county and township buildings are often missing, so this can't be grounds for exclusion.
    "Sparse surroundings" is used only for ranking (--sort sparse), not for filtering: a factory site itself is often split into a pile of small sheds.
    """
    pre, sc = _scope(args)
    flt = args.filter or '["building"]'
    data = run(f"[out:json][timeout:240];{pre}way{flt}{sc};out geom;", args.proxy, args.cache)
    rows = []
    for el in data.get("elements", []):
        g = [(n["lat"], n["lon"]) for n in el.get("geometry") or []]
        if len(g) < 4:
            continue
        area = _ring_area(g[:-1] if g[0] == g[-1] else g)
        c = (sum(p[0] for p in g) / len(g), sum(p[1] for p in g) / len(g))
        rows.append({"id": el["id"], "c": c, "area": area, "tags": el.get("tags") or {}})
    big = [r for r in rows if r["area"] >= args.min_area]
    cells: dict[tuple[int, int], list] = {}
    cs = args.within / 111000
    for r in rows:
        cells.setdefault((int(r["c"][0] / cs), int(r["c"][1] / cs)), []).append(r)
    for r in big:
        ci, cj = int(r["c"][0] / cs), int(r["c"][1] / cs)
        r["neighbors"] = sum(1 for di in (-1, 0, 1) for dj in (-1, 0, 1) for o in cells.get((ci + di, cj + dj), [])
                             if o is not r and _dist(r["c"], o["c"]) <= args.within)
    big.sort(key=(lambda r: (r["neighbors"], -r["area"])) if args.sort == "sparse" else (lambda r: -r["area"]))
    print(f"{len(rows)} buildings, {len(big)} with footprint ≥{args.min_area:.0f} m² (sorted by {'sparse surroundings' if args.sort == 'sparse' else 'area'}; nb=number of other buildings within {args.within:.0f} m)")
    pts = {}
    for i, r in enumerate(big, 1):
        t = r["tags"]
        kind = t.get("building", "")
        label = f"{i:03d} {int(r['area'])}m² nb{r['neighbors']} {kind if kind != 'yes' else ''} {t.get('name', '')}"
        pts[" ".join(label.split())] = [round(r["c"][0], 6), round(r["c"][1], 6)]
    return pts


def cmd_coverage(args) -> dict:
    """How many features of a kind each candidate admin area has. Run it before enumerating candidates with OSM: districts with clearly low counts can't be excluded on OSM results and must be scanned separately with a satellite imagery grid."""
    rows = []
    for name in [a for a in args.areas.split(",") if a]:
        for loose in (False, True):                       # bilingual names without name:zh: the second round falls back to the name prefix
            ql = f'[out:json][timeout:120];{_area_sel(name, "a", loose)}.a out count;nwr{args.filter}(area.a);out count;'
            els = run(ql, args.proxy, args.cache).get("elements") or []
            counts = [int((e.get("tags") or {}).get("total", 0)) for e in els]
            if counts and counts[0] > 0:
                break
        rows.append((name, counts[1] if len(counts) > 1 and counts[0] > 0 else -1))
    top = max((n for _, n in rows), default=0)
    print(f"Count of {args.filter} in OSM (compare only admin areas of the same level; a low count may be truly low, or just unmapped):")
    for name, n in rows:
        if n < 0:
            flag = "  ← no admin area with this name in OSM; try another spelling (with or without the \"区/县/市\" suffix)"
        elif n < max(5, top * 0.25):
            flag = "  ← low: OSM results can't exclude this area; scan it with tiles.py sheet --grid instead"
        else:
            flag = ""
        print(f"  {name}: {'?' if n < 0 else n}{flag}")
    return {}


def _rank_rows(rows: list[dict], flt: str, args) -> list[dict]:
    """Rank candidates by "distance to the nearest feature of a kind (town, service area, station ...)", nearest first. Ranks only, never deletes."""
    pre, sc = _scope(args)
    if args.bbox:                                         # towns just outside the bbox edge count too
        s, w, n, e = args.bbox
        sc = f"({s - 0.2},{w - 0.2},{n + 0.2},{e + 0.2})"
    data = run(f"[out:json][timeout:180];{pre}nwr{flt}{sc};out center tags;", args.proxy, args.cache)
    refs = []
    for el in data.get("elements", []):
        ll = _center(el)
        if ll and ll[0] is not None:
            refs.append(((el.get("tags") or {}).get("name", "?"), ll))
    if not refs:
        print(f"--rank-near {flt} found no features; not ranking")
        return rows
    for r in rows:
        name, ll = min(refs, key=lambda t: _dist(r["ll"], t[1]))
        r["near_m"], r["near_name"] = _dist(r["ll"], ll), name
    rows.sort(key=lambda r: r["near_m"])
    print(f"  ranked by distance to the nearest {flt} ({len(refs)} found), nearest first")
    return rows


def _match(el: dict, flt: str) -> bool:
    """Roughly check whether a feature matches A's tag filter (looks only at key=value conditions)."""
    tags = el.get("tags") or {}
    for k, v in re.findall(r'\["([^"]+)"="([^"]+)"\]', flt):
        if tags.get(k) != v:
            return False
    for k in re.findall(r'\["([^"=\]]+)"\]', flt):
        if k not in tags:
            return False
    return True


def cmd_geom(args) -> dict:
    """Any filter → GeoJSON (keeps geometry for lines, polygons and points), for custom analysis or overlays."""
    pre, sc = _scope(args)
    data = run(f"[out:json][timeout:180];{pre}nwr{args.filter}{sc};out geom tags;", args.proxy, args.cache)
    feats = []
    for el in data.get("elements", []):
        tags = el.get("tags") or {}
        if el["type"] == "node":
            geom = {"type": "Point", "coordinates": [el["lon"], el["lat"]]}
        elif el.get("geometry"):
            coords = [[g["lon"], g["lat"]] for g in el["geometry"]]
            closed = len(coords) > 3 and coords[0] == coords[-1]
            geom = {"type": "Polygon", "coordinates": [coords]} if closed and ("building" in tags or "area" in tags) \
                else {"type": "LineString", "coordinates": coords}
        else:
            continue
        feats.append({"type": "Feature", "id": f"{el['type']}/{el['id']}", "properties": tags, "geometry": geom})
    gj = {"type": "FeatureCollection", "features": feats}
    out = args.out or Path("osm_geom.geojson")
    out.write_text(json.dumps(gj, ensure_ascii=False), encoding="utf-8")
    if not feats and args.area and not getattr(args, "area_loose", False) and _area_count(args.area, args) == 0:
        if _area_count(args.area, args, loose=True) > 0:
            print(f"\"{args.area}\" has a bilingual name in OSM and no name:zh; retrying by name prefix", file=sys.stderr)
            args.area_loose = True
            return cmd_geom(args)
        print(f"Note: no area named \"{args.area}\" found in OSM; 0 results doesn't mean there is nothing here; try another spelling or use --bbox", file=sys.stderr)
    print(f"{len(feats)} features -> {out}")
    args.out = None
    return {}


def _band(s: str) -> tuple[float, float]:
    a, b = s.split(":")
    return float(a), float(b)


def cmd_street_scan(args) -> dict:
    """Street view geometry template: camera standing at an intersection (or on a road), looking down a street, with a "building / no building" pattern on each side → candidate points across the whole town."""
    if not args.bbox:
        sys.exit("street-scan only supports --bbox (the extent of one town, sides no longer than ~15 km)")
    s, w, n, e = args.bbox
    if (n - s) > 0.2 or (e - w) > 0.25:
        print("Tip: the area is large and the query may time out; running it town by town in several passes is more reliable", file=sys.stderr)
    excl = "footway|path|cycleway|steps|track|pedestrian|bridleway|corridor|platform|proposed|construction|elevator"
    ql = (f'[out:json][timeout:280];way["highway"]["highway"!~"^({excl})$"]({s},{w},{n},{e});out body geom;'
          f'way["building"]({s},{w},{n},{e});out body geom;')
    data = run(ql, args.proxy, args.cache, timeout=280)
    lat0, lon0 = (s + n) / 2, (w + e) / 2
    kx, ky = 111320 * math.cos(math.radians(lat0)), 110540

    def P(g):
        return ((g["lon"] - lon0) * kx, (g["lat"] - lat0) * ky)

    types = set(args.types.split(","))
    ways = [el for el in data.get("elements", []) if el["type"] == "way" and el.get("geometry")]
    hw = [el for el in ways if "highway" in (el.get("tags") or {})]
    bl = [el for el in ways if "building" in (el.get("tags") or {})]
    node_ways: dict[int, set] = {}
    for wy in hw:
        for nd in wy["nodes"]:
            node_ways.setdefault(nd, set()).add(wy["id"])
    grid: dict[tuple[int, int], list] = {}
    area: dict[int, float] = {}
    for b in bl:
        pts = [P(g) for g in b["geometry"]]
        area[b["id"]] = abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:]))) / 2 if len(pts) > 2 else 0
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            k = max(1, int(math.hypot(x2 - x1, y2 - y1) / 2))
            for i in range(k + 1):
                x, y = x1 + (x2 - x1) * i / k, y1 + (y2 - y1) * i / k
                grid.setdefault((int(x // 50), int(y // 50)), []).append((x, y, b["id"]))
    b_lo, b_hi = _band(args.bearing)
    near_lo, near_hi = _band(args.band)
    clr_lo, clr_hi = _band(args.clear)
    ah_lo, ah_hi = _band(args.ahead)
    reach = int(max(ah_hi, near_hi, clr_hi) // 50) + 2

    def bearing_ok(brg):
        return (b_lo <= brg <= b_hi) if b_lo <= b_hi else (brg >= b_lo or brg <= b_hi)

    def along(pts, dist):
        acc = 0.0
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            L = math.hypot(x2 - x1, y2 - y1)
            if L > 0 and acc + L >= dist:
                f = (dist - acc) / L
                return (x1 + (x2 - x1) * f, y1 + (y2 - y1) * f)
            acc += L
        return None

    def side_ok(J, ux, uy, want, sign):
        if want == "any":
            return True
        nx, ny = uy * sign, -ux * sign            # sign=+1 right side, -1 left side
        cx, cy = int(J[0] // 50), int(J[1] // 50)
        hits = set()
        blocked = False
        for gx in range(cx - reach, cx + reach + 1):
            for gy in range(cy - reach, cy + reach + 1):
                for x, y, bid in grid.get((gx, gy), []):
                    t = (x - J[0]) * ux + (y - J[1]) * uy
                    lat_d = (x - J[0]) * nx + (y - J[1]) * ny
                    if ah_lo <= t <= ah_hi:
                        if near_lo <= lat_d <= near_hi and area.get(bid, 0) >= args.min_area:
                            hits.add(bid)
                        if clr_lo <= lat_d <= clr_hi:
                            blocked = True
        return bool(hits) if want == "building" else not blocked

    cands = {}
    for wy in hw:
        if wy["tags"]["highway"] not in types:
            continue
        g = [P(x) for x in wy["geometry"]]
        starts = []
        for end in (0, -1):
            if args.anywhere or len(node_ways.get(wy["nodes"][end], ())) >= 2:
                starts.append((g if end == 0 else g[::-1], "s" if end == 0 else "e", 0.0))
        if args.anywhere:
            total = sum(math.hypot(x2 - x1, y2 - y1) for (x1, y1), (x2, y2) in zip(g, g[1:]))
            d = args.every
            while d < total - args.look:
                starts.append((g, f"m{int(d)}", d))
                d += args.every
        for pts, tag, off in starts:
            J = along(pts, off) if off else pts[0]
            p_far, p_mid = along(pts, off + args.look), along(pts, off + args.look / 2)
            if not J or not p_far or not p_mid:
                continue
            ux, uy = p_far[0] - J[0], p_far[1] - J[1]
            L = math.hypot(ux, uy)
            ux, uy = ux / L, uy / L
            brg = math.degrees(math.atan2(ux, uy)) % 360
            if not bearing_ok(brg):
                continue
            b_mid = math.degrees(math.atan2(p_mid[0] - J[0], p_mid[1] - J[1])) % 360
            if abs((b_mid - brg + 180) % 360 - 180) > 15:                    # the first half must be straight enough
                continue
            if side_ok(J, ux, uy, args.right, +1) and side_ok(J, ux, uy, args.left, -1):
                name = (wy.get("tags") or {}).get("name", "")
                key = f"{len(cands) + 1:03d} {name[:20]} heading {brg:.0f}° way{wy['id']}{tag}".strip()
                cands[key] = [round(J[1] / ky + lat0, 6), round(J[0] / kx + lon0, 6)]
    print(f"{len(hw)} roads, {len(bl)} buildings → {len(cands)} candidates (point = camera position at the intersection / on the road)")
    return cands



def _neg_coords(argv: list[str]) -> list[str]:
    """argparse treats negative coordinates like -1.45,-48.5 as option names; a leading space makes them plain values (float ignores the space). Every southern- or western-hemisphere case needs this."""
    return [" " + a if re.match(r"^-\d[\d.]*(,-?[\d.]+)+$", a) else a for a in argv]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--proxy", default=os.environ.get("GEO_PROXY"), help=PROXY_HELP)
    ap.add_argument("--cache", type=Path, default=Path(".geo-cache/osm"))
    sub = ap.add_subparsers(dest="cmd", required=True)

    def scope(sp):
        sp.add_argument("--proxy", default=argparse.SUPPRESS, help="can also go after the subcommand")
        sp.add_argument("--cache", type=Path, default=argparse.SUPPRESS)
        sp.add_argument("--bbox", type=lambda s: tuple(map(float, s.split(","))), help="south,west,north,east")
        sp.add_argument("--area", help='OSM admin area name, e.g. "Bayern", "江苏省" (Jiangsu Province), "深圳市" (Shenzhen)')
        sp.add_argument("--out", type=Path, help="write {name:[lat,lon]}")
        sp.add_argument("--limit", type=int, default=30, help="max rows printed to the terminal")

    f = sub.add_parser("find")
    f.add_argument("filter", help='Overpass tag filter, e.g. \'["amenity"="fuel"]\'')
    scope(f)

    n = sub.add_parser("near")
    n.add_argument("--a", required=True, help="the main feature to find")
    n.add_argument("--b", required=True, help="feature that must be near the main feature")
    n.add_argument("--within", type=float, default=200, help="max distance from A to B (meters)")
    n.add_argument("--c", help="optional: a third required feature")
    n.add_argument("--within-c", type=float, default=200)
    n.add_argument("--report", type=Path, help="write the actual B/C distances and key tags for each A (JSON), for ranking")
    n.add_argument("--rank-near", help='rank by distance to the nearest feature of a kind, e.g. \'["place"~"^(city|town)$"]\' (ranks only, never deletes)')
    scope(n)

    c = sub.add_parser("crossings")
    c.add_argument("--line", required=True, help='linear feature tags, e.g. \'["waterway"="river"]["name"="长江"]\' (Yangtze), \'["railway"="rail"]\'')
    c.add_argument("--kind", default="bridge,dam,ferry", help="bridge,dam,ferry,level_crossing, comma-separated")
    c.add_argument("--buffer", type=float, default=40, help="how many meters from the linear feature still counts as on the line")
    scope(c)

    ro = sub.add_parser("route")
    ro.add_argument("--kind", default="bus", help="bus / trolleybus / tram / subway / train / light_rail / ferry")
    ro.add_argument("--ref", help="route number, e.g. 79")
    ro.add_argument("--name", help="regex fragment of the route name")
    ro.add_argument("--step", type=float, default=200, help="take a point every this many meters along the route")
    scope(ro)

    r = sub.add_parser("raw")
    r.add_argument("file", type=Path, help="Overpass QL file")
    scope(r)

    it = sub.add_parser("intersect")
    it.add_argument("--a", required=True, help='first kind of line, e.g. \'["railway"="rail"]["electrified"="contact_line"]\'')
    it.add_argument("--b", required=True, help='second kind of line, e.g. \'["power"="line"]\'')
    it.add_argument("--bend-min", type=float, default=0,
                    help="mark crossing points where B bends ≥ this many degrees beyond the crossing (angle tower / river bend) and rank them first; 0 = ignore bends. By default only marks, never deletes")
    it.add_argument("--bend-within", default="100:1000", help="distance range of the bend from the crossing, m")
    it.add_argument("--bend-filter", action="store_true",
                    help="actually delete crossing points without a bend (deleted ones go to <out>_dropped.json). Use only when the bend is a fact you confirmed with your own eyes in the photo")
    it.add_argument("--rank-near", help='rank by distance to the nearest feature of a kind, e.g. \'["place"~"^(city|town)$"]\', \'["highway"="services"]\'')
    it.add_argument("--ring", help="lat,lon:min_m:max_m — keep only crossing points in this distance ring around a point (e.g. a distance range computed from a landmark's pixel size)")
    it.add_argument("--cluster", type=float, default=100, help="crossing points within this many meters merge into one place")
    scope(it)

    cv = sub.add_parser("coverage", help="how many features of a kind each candidate admin area has: check OSM coverage before enumerating; blank areas can't be grounds for exclusion")
    cv.add_argument("--areas", required=True, help='comma-separated OSM admin area names, e.g. "<name>区,<name>县"')
    cv.add_argument("--filter", required=True, help='feature filter, e.g. \'["leisure"~"^(pitch|track)$"]\', \'["building"]\'')
    cv.add_argument("--proxy", default=argparse.SUPPRESS)
    cv.add_argument("--cache", type=Path, default=argparse.SUPPRESS)

    al = sub.add_parser("along", help="take points at a step along a road / river / power line (optionally offset to one side), for satellite thumbnails or street view scans of the roadside")
    al.add_argument("--line", required=True, help='linear feature filter, e.g. \'["highway"]["ref"="<road number>"]\', \'["highway"]["name"~"<road name fragment>"]\'')
    al.add_argument("--step", type=float, default=150, help="take a point every this many meters; ≤150 for finding storefronts in street view, 300–500 is fine for satellite thumbnails")
    al.add_argument("--side", choices=list(_SIDES), help="which side of the road to offset to (by compass direction)")
    al.add_argument("--offset", type=float, default=0, help="offset in meters; when looking at factories on one side of the road, use the building-to-road distance")
    scope(al)

    bu = sub.add_parser("buildings", help="find large buildings by footprint area (factories, warehouses, farm sheds), marking how sparse the surroundings are")
    bu.add_argument("--min-area", type=float, default=1000, help="minimum footprint m²")
    bu.add_argument("--within", type=float, default=200, help="radius for counting surrounding buildings, m")
    bu.add_argument("--sort", choices=["area", "sparse"], default="area", help="sparse: fewer surrounding buildings first (isolated rural factories); ranks only, never deletes")
    bu.add_argument("--filter", help='building filter, default \'["building"]\', e.g. \'["building"~"industrial|warehouse|farm_auxiliary"]\'')
    scope(bu)

    gm = sub.add_parser("geom")
    gm.add_argument("filter", help='tag filter, e.g. \'["building"]\', \'["highway"]\'')
    scope(gm)

    ss = sub.add_parser("street-scan")
    ss.add_argument("--bearing", required=True, help="bearing range of the street the camera looks down, e.g. 320:80 (may cross north)")
    ss.add_argument("--right", choices=["building", "empty", "any"], default="any", help="right side of the street")
    ss.add_argument("--left", choices=["building", "empty", "any"], default="any", help="left side of the street")
    ss.add_argument("--band", default="4:22", help="'building' test band: lateral distance from the street centerline, m")
    ss.add_argument("--clear", default="3:10", help="'empty' test band: no building may be in this lateral range, m")
    ss.add_argument("--ahead", default="0:40", help="how far ahead along the street to look, m")
    ss.add_argument("--min-area", type=float, default=150, help="minimum footprint m² required for 'building'")
    ss.add_argument("--look", type=float, default=60, help="how many meters ahead are used to compute the street bearing")
    ss.add_argument("--types", default="residential,unclassified,living_street,tertiary,secondary,service")
    ss.add_argument("--anywhere", action="store_true", help="the camera isn't necessarily at an intersection: try every --every meters along the street")
    ss.add_argument("--every", type=float, default=30)
    scope(ss)

    args = ap.parse_args(_neg_coords(sys.argv[1:]))
    if args.cmd == "crossings":
        pts = cmd_crossings(args)
    elif args.cmd == "route":
        pts = cmd_route(args)
    elif args.cmd == "intersect":
        pts = cmd_intersect(args)
    elif args.cmd == "geom":
        pts = cmd_geom(args)
    elif args.cmd == "coverage":
        cmd_coverage(args)
        return
    elif args.cmd == "along":
        pts = cmd_along(args)
    elif args.cmd == "buildings":
        pts = cmd_buildings(args)
    elif args.cmd == "street-scan":
        pts = cmd_street_scan(args)
    else:
        if args.cmd == "raw":
            ql = args.file.read_text(encoding="utf-8")
            if args.bbox:
                ql = ql.replace("{{bbox}}", ",".join(map(str, args.bbox)))
        else:
            pre, sc = _scope(args)
            if args.cmd == "find":
                ql = f"[out:json][timeout:180];{pre}nwr{args.filter}{sc};out center tags;"
            else:
                ql = f"[out:json][timeout:180];{pre}nwr{args.b}{sc}->.b;nwr{args.a}(around.b:{args.within:.0f}){sc}->.a;"
                if args.c:
                    ql += f"nwr{args.c}{sc}->.c;nwr.a(around.c:{args.within_c:.0f})->.a;"
                ql += ".a out center tags;"
        pts = _points(run(ql, args.proxy, args.cache))
        print(f"{len(pts)} results")
        if not pts:
            print("  0 doesn't mean none: OSM may not have mapped this area at all (common for counties and townships in China), so it can't be grounds for exclusion; compare first with osm.py coverage, or use tiles.py sheet --grid instead")
        if args.cmd == "near" and args.rank_near and pts:
            rows = _rank_rows([{"label": k, "ll": v, "bend": None} for k, v in pts.items()], args.rank_near, args)
            pts = {f"{r['label']} {r['near_m'] / 1000:.1f}km from {r['near_name'][:6]}" if r.get("near_m") is not None
                   else r["label"]: r["ll"] for r in rows}
        if args.cmd == "near" and args.report and pts:
            pre2, sc2 = _scope(args)
            rep = {}
            a_ids = f"nwr{args.b}{sc2}->.b;nwr{args.a}(around.b:{args.within:.0f}){sc2}->.a;"
            if args.c:
                a_ids += f"nwr{args.c}{sc2}->.c;nwr.a(around.c:{args.within_c:.0f})->.a;"
            q2 = (f"[out:json][timeout:200];{pre2}{a_ids}.a out center tags;"
                  f"nwr{args.b}(around.a:{args.within:.0f}){sc2};out geom tags;")
            if args.c:
                q2 += f"nwr{args.c}(around.a:{args.within_c:.0f}){sc2};out geom tags;"
            d2 = run(q2, args.proxy, args.cache)
            others = [e for e in d2.get("elements", []) if e.get("geometry") or e["type"] == "node"]
            for name, ll in pts.items():
                near_list = []
                for el in others:
                    geom = el.get("geometry") or ([{"lat": el["lat"], "lon": el["lon"]}] if el["type"] == "node" else [])
                    if not geom:
                        continue
                    dmin = min(_dist(ll, (g["lat"], g["lon"])) for g in geom)
                    t = el.get("tags") or {}
                    keep = {k2: v for k2, v in t.items() if k2 in
                            ("name", "voltage", "electrified", "highspeed", "railway", "power", "waterway", "highway", "tracks")}
                    near_list.append({"dist_m": round(dmin), "tags": keep})
                near_list.sort(key=lambda x: x["dist_m"])
                rep[name] = {"ll": ll, "nearest": near_list[:4]}
            args.report.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"report -> {args.report}")
    for k, (name, ll) in enumerate(pts.items()):
        if k >= args.limit:
            print("  …")
            break
        print(f"  {name}  {ll[0]},{ll[1]}")
    if args.out:
        args.out.write_text(json.dumps(pts, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"-> {args.out}")


if __name__ == "__main__":
    # Chinese Windows outputs GBK by default: it crashes on m² or ñ, and the Chinese the agent reads is garbled
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    main()
