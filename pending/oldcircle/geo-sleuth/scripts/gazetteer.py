#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Admin gazetteer: list candidate areas "in full" with extent, area and scan cost. Used by board.py; can also be queried on its own.

  children  list every next-level (or specified-level) admin area of an admin area, with bbox, bbox area, center
  info      an admin area's OSM relation, admin_level, bbox, center
  urban     an admin area's built-up extent (largest contiguous block of OSM residential/commercial/industrial land use), for scan cost and scan_bbox
  cost      how many cells and pages a bbox takes at tiles.py sheet --grid settings

Data comes from OSM Overpass (results cached per query in .geo-cache/osm/). OSM admin lists can have gaps:
children merges them with a region pack's admin table when one knows the parent (regions/<cc>/, e.g. China's three levels) and flags entries missing a bbox.
admin_level differs by country: China province 4 / prefecture 5 / county 6, France region 4 / department 6, US state 4 / county 6. If unsure, omit --level;
the script tries downward from the parent's admin_level and skips levels whose combined extent is under 30% of the parent (China's level 3 is only Hong Kong and Macau).

Examples:
  gazetteer.py children <full province-level name> --out districts.json   # municipality → all districts
  gazetteer.py children <country name> --level 4                          # country → first-level admin divisions
  gazetteer.py info <admin area name>
  gazetteer.py urban <district name> --within <full province-level name>  # built-up bbox + area
  gazetteer.py cost --bbox <s,w,n,e> --zoom 16 --cell 320 --cols 5
"""
from __future__ import annotations

import argparse
from _net import PROXY_HELP
import json
import math
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import geo  # noqa: E402
import osm  # noqa: E402
import regions  # noqa: E402

LEVEL_NAMES = {"CN": {4: "province", 5: "prefecture", 6: "county", 7: "township"}, "FR": {4: "region", 6: "department", 8: "commune"},
               "US": {4: "state", 6: "county", 8: "city"}, "*": {2: "country", 4: "first-level admin division", 6: "second-level admin division", 8: "third-level admin division"}}
MIN_COVER = 0.3   # children auto level pick: this level's combined bbox area must be at least this fraction of the parent's bbox


def _cache(args) -> Path:
    return Path(getattr(args, "cache", None) or ".geo-cache/osm")


def _bbox_km2(b: list[float]) -> float:
    s, w, n, e = b
    return abs(n - s) * 110.574 * abs(e - w) * 111.320 * math.cos(math.radians((s + n) / 2))


def _rel_rows(data: dict) -> list[dict]:
    rows = []
    for el in data.get("elements", []):
        if el.get("type") != "relation":
            continue
        t, b = el.get("tags") or {}, el.get("bounds") or {}
        if not b:
            continue
        bbox = [b["minlat"], b["minlon"], b["maxlat"], b["maxlon"]]
        rows.append({"name": t.get("name", str(el["id"])), "name_en": t.get("name:en", ""), "osm_id": el["id"],
                     "admin_level": int(t.get("admin_level") or 0), "bbox": [round(v, 5) for v in bbox],
                     "bbox_km2": round(_bbox_km2(bbox), 1),
                     "center": [round((bbox[0] + bbox[2]) / 2, 5), round((bbox[1] + bbox[3]) / 2, 5)],
                     "population": t.get("population", "")})
    return rows


def find_relation(name: str, proxy: str | None, cache: Path, within: str | None = None,
                  level: int | None = None) -> list[dict]:
    """Find admin relations by name (there can be several with the same name: Chaoyang District in Beijing and in Changchun), with bbox."""
    lv = f'["admin_level"="{level}"]' if level else ""
    if within:
        ql = (f'[out:json][timeout:120];rel["name"="{within}"]["boundary"="administrative"];map_to_area->.p;'
              f'rel(area.p)["name"="{name}"]["boundary"="administrative"]{lv};out tags bb;')
    else:
        ql = f'[out:json][timeout:120];rel["name"="{name}"]["boundary"="administrative"]{lv};out tags bb;'
    rows = _rel_rows(osm.run(ql, proxy, cache))
    rows.sort(key=lambda r: (r["admin_level"], -r["bbox_km2"]))
    return rows


def children(parent: str, proxy: str | None, cache: Path, level: int | None, within: str | None) -> tuple[dict, list[dict]]:
    ps = find_relation(parent, proxy, cache, within)
    if not ps:
        sys.exit(f"OSM has no admin relation named \"{parent}\": try the full name (with or without the suffix 市/省/区), or add --within <parent name>")
    p = ps[0]
    levels = [level] if level else [p["admin_level"] + k for k in (1, 2, 3, 4)]
    first = None
    for lv in levels:
        ql = (f'[out:json][timeout:180];rel({p["osm_id"]});map_to_area->.a;'
              f'rel(area.a)["boundary"="administrative"]["admin_level"="{lv}"];out tags bb;')
        rows = _rel_rows(osm.run(ql, proxy, cache))
        rows = [r for r in rows if r["osm_id"] != p["osm_id"]]
        if len(rows) < 2:
            continue
        rows = sorted(rows, key=lambda r: r["name"])
        if level:
            return p, rows
        # Auto level pick: a level that covers only a small part of the parent isn't the "next level" (China's admin_level 3 is only Hong Kong and Macau; provinces are 4)
        cover = sum(r["bbox_km2"] for r in rows) / max(p["bbox_km2"], 1e-9)
        if cover >= MIN_COVER:
            return p, rows
        print(f"admin_level {lv} has only {len(rows)} ({', '.join(r['name'] for r in rows[:6])}), "
              f"together covering only {cover:.1%} of the parent; not treated as the next level, trying lower", file=sys.stderr)
        first = first or rows
    if first:
        print("None of the lower levels covers the parent; falling back to the first level with ≥2; if that's wrong, give --level", file=sys.stderr)
    return p, first or []


def _local_children(parent: str) -> tuple[list[str], str]:
    """Names of parent's direct children in a region pack's admin table, and the pack code ([] and "" when no pack knows the parent)."""
    pk, kids = regions.admin_children(parent)
    return sorted({k["name"] for k in kids}), (pk["code"] if pk else "")


def urban(name: str, proxy: str | None, cache: Path, within: str | None) -> dict:
    """Built-up area: the largest contiguous block of OSM land-use areas. When land use isn't mapped, fall back to a place=city/town node and estimate a radius from population."""
    rs = find_relation(name, proxy, cache, within)
    if not rs:
        sys.exit(f"OSM has no admin area named \"{name}\": try the full name or add --within")
    r = rs[0]
    ql = (f'[out:json][timeout:180];rel({r["osm_id"]});map_to_area->.a;'
          f'way["landuse"~"^(residential|commercial|retail|industrial)$"](area.a);out bb;')
    els = osm.run(ql, proxy, cache).get("elements", [])
    boxes = [(e["bounds"]["minlat"], e["bounds"]["minlon"], e["bounds"]["maxlat"], e["bounds"]["maxlon"])
             for e in els if e.get("bounds")]
    out = {"name": r["name"], "admin_bbox": r["bbox"], "admin_bbox_km2": r["bbox_km2"], "landuse_polygons": len(boxes)}
    # Admin seat: the place=city/town node with the largest population; prefer the land-use block nearest to it (when OSM is only half mapped, the largest block is often another town)
    ql2 = (f'[out:json][timeout:120];rel({r["osm_id"]});map_to_area->.a;'
           f'node["place"~"^(city|town)$"](area.a);out;')
    nodes = osm.run(ql2, proxy, cache).get("elements", [])
    seat = None
    if nodes:
        def pop(n):
            return int(re.sub(r"\D", "", (n.get("tags") or {}).get("population", "0") or "0") or 0)
        best = max(nodes, key=lambda n: (pop(n), (n.get("tags") or {}).get("place") == "city"))
        seat = {"name": (best.get("tags") or {}).get("name", ""), "ll": (best["lat"], best["lon"]), "population": pop(best)}
        out["seat"] = seat
    if len(boxes) >= 3:
        # Connected blocks on a 2 km grid; take the block with the largest area
        cs = 2 / 110.574
        cell_of = {}
        for i, b in enumerate(boxes):
            cell_of.setdefault((int(((b[0] + b[2]) / 2) / cs), int(((b[1] + b[3]) / 2) / cs)), []).append(i)
        seen, blocks = set(), []
        for c0 in cell_of:
            if c0 in seen:
                continue
            stack, comp = [c0], []
            seen.add(c0)
            while stack:
                c = stack.pop()
                comp.extend(cell_of[c])
                for di in (-1, 0, 1):
                    for dj in (-1, 0, 1):
                        nb = (c[0] + di, c[1] + dj)
                        if nb in cell_of and nb not in seen:
                            seen.add(nb)
                            stack.append(nb)
            blocks.append(comp)
        def block_bbox(comp):
            return [min(boxes[i][0] for i in comp), min(boxes[i][1] for i in comp),
                    max(boxes[i][2] for i in comp), max(boxes[i][3] for i in comp)]

        def block_area(comp):
            return sum(_bbox_km2(list(boxes[i])) for i in comp)

        chosen, how = None, ""
        if seat:
            near = [c for c in blocks if geo.distance(seat["ll"], (((bb := block_bbox(c))[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2)) <= 12000]
            if near:
                chosen, how = max(near, key=block_area), f"contiguous land use nearest the admin seat {seat['name']}"
        if chosen is None:
            chosen, how = max(blocks, key=block_area), "largest contiguous land use (no admin seat node found; may be another town)"
        bb = block_bbox(chosen)
        if seat and not (bb[0] <= seat["ll"][0] <= bb[2] and bb[1] <= seat["ll"][1] <= bb[3]):
            # The block doesn't cover the admin seat: merge in 1.5 km around the seat
            s2, w2 = geo.dest(geo.dest(seat["ll"], 180, 1500), 270, 1500)
            n2, e2 = geo.dest(geo.dest(seat["ll"], 0, 1500), 90, 1500)
            bb = [min(bb[0], s2), min(bb[1], w2), max(bb[2], n2), max(bb[3], e2)]
            how += "; merged in 1.5 km around the admin seat"
        out.update({"urban_bbox": [round(v, 5) for v in bb], "urban_bbox_km2": round(_bbox_km2(bb), 1),
                    "urban_landuse_km2": round(block_area(chosen), 1), "blocks": len(blocks), "source": "landuse", "how": how})
        return out
    if seat:
        pop = seat["population"]
        rad = max(1500.0, min(12000.0, math.sqrt(max(pop, 20000) / 6000 / math.pi) * 1000))  # about 6000 people/km²
        s, w = geo.dest(geo.dest(seat["ll"], 180, rad), 270, rad)
        n, e = geo.dest(geo.dest(seat["ll"], 0, rad), 90, rad)
        out.update({"urban_bbox": [round(s, 5), round(w, 5), round(n, 5), round(e, 5)],
                    "urban_bbox_km2": round(_bbox_km2([s, w, n, e]), 1), "source": "place-node",
                    "place": seat["name"], "population": pop,
                    "note": "OSM has no land use mapped; built-up radius estimated from the place node's population, order of magnitude only"})
        return out
    out["note"] = "OSM has neither land use nor a place node: draw scan_bbox yourself on satellite imagery"
    return out


def cost(bbox: list[float], zoom: int, cell: int, cols: int) -> dict:
    s, w, n, e = bbox
    mpp = 156543.03392 * math.cos(math.radians((s + n) / 2)) / 2 ** zoom
    step = cell * mpp * 0.9
    rows_ = max(1, math.ceil((n - s) * 110574 / step))
    cols_ = max(1, math.ceil((e - w) * 111320 * math.cos(math.radians((s + n) / 2)) / step))
    cells = rows_ * cols_
    return {"bbox": bbox, "km2": round(_bbox_km2(bbox), 1), "zoom": zoom, "cell_px": cell, "cell_m": round(cell * mpp),
            "cells": cells, "pages": math.ceil(cells / (cols * cols)), "per_page": cols * cols}


def _neg_coords(argv: list[str]) -> list[str]:
    return [" " + a if re.match(r"^-\d[\d.]*(,-?[\d.]+)+$", a) else a for a in argv]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--proxy", default=os.environ.get("GEO_PROXY"), help=PROXY_HELP)
    ap.add_argument("--cache", type=Path, default=Path(".geo-cache/osm"))
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(sp):
        sp.add_argument("--proxy", default=argparse.SUPPRESS)
        sp.add_argument("--cache", type=Path, default=argparse.SUPPRESS)

    c = sub.add_parser("children", help="every subordinate admin area of an admin area (with bbox); use when candidates must be listed \"in full\"")
    common(c)
    c.add_argument("name")
    c.add_argument("--level", type=int, help="OSM admin_level; if omitted, try downward from the parent")
    c.add_argument("--within", help="parent admin area name, to disambiguate same names")
    c.add_argument("--out", type=Path, help="write {name: {bbox, bbox_km2, center, ...}}")

    i = sub.add_parser("info")
    common(i)
    i.add_argument("name")
    i.add_argument("--within")
    i.add_argument("--level", type=int)

    u = sub.add_parser("urban", help="built-up extent: scan cost is computed from this, not from the whole admin area")
    common(u)
    u.add_argument("name")
    u.add_argument("--within")
    u.add_argument("--out", type=Path)

    k = sub.add_parser("cost", help="how many pages a bbox takes at tiles.py sheet --grid settings")
    k.add_argument("--bbox", required=True)
    k.add_argument("--zoom", type=int, default=16)
    k.add_argument("--cell", type=int, default=320)
    k.add_argument("--cols", type=int, default=5)

    args = ap.parse_args(_neg_coords(sys.argv[1:]))
    cache = _cache(args)
    if args.cmd == "cost":
        print(json.dumps(cost([float(v) for v in args.bbox.split(",")], args.zoom, args.cell, args.cols), ensure_ascii=False))
        return
    if args.cmd == "info":
        rows = find_relation(args.name, args.proxy, cache, args.within, args.level)
        if not rows:
            sys.exit("Not found; try the full name or add --within")
        for r in rows[:8]:
            print(json.dumps(r, ensure_ascii=False))
        return
    if args.cmd == "urban":
        out = urban(args.name, args.proxy, cache, args.within)
        if args.out:
            args.out.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return
    if args.cmd == "children":
        p, rows = children(args.name, args.proxy, cache, args.level, args.within)
        local, code = _local_children(p["name"])
        names = {r["name"] for r in rows}
        pk = regions.resolve(code) or {}
        missing = [n for n in local if n not in names and not any(regions.strip_suffix(n, pk) == regions.strip_suffix(m, pk) for m in names)]
        out = {r["name"]: {k: r[k] for k in ("osm_id", "admin_level", "bbox", "bbox_km2", "center", "name_en")} for r in rows}
        for n in missing:
            out[n] = {"osm_id": None, "admin_level": None, "bbox": None, "bbox_km2": None, "center": None,
                      "name_en": "", "note": "only in the local admin table, no OSM relation found: fill in the bbox with info/urban, or estimate from the parent's extent for now"}
        lvl = rows[0]["admin_level"] if rows else None
        print(f"{p['name']} (admin_level {p['admin_level']}) children admin_level {lvl}: OSM {len(rows)}"
              + (f", {code} pack's admin table adds {len(missing)} ({', '.join(missing)})" if missing else "")
              + ("; no region pack's admin table has this parent, can't check the list is complete" if not local else ""))
        for name, r in sorted(out.items(), key=lambda kv: -(kv[1]["bbox_km2"] or 0)):
            b = r["bbox"]
            print(f"  {name:<14} {r['bbox_km2'] or '?':>9} km²  {b if b else '(no bbox)'}")
        if args.out:
            args.out.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"-> {args.out}")


if __name__ == "__main__":
    # Chinese Windows outputs GBK by default: it crashes on m², ñ, and Chinese text the agent reads comes out garbled
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    main()
