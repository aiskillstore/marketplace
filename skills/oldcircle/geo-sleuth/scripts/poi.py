#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Place name, residential compound name, housing development name, shop name → coordinate candidates (no API key).

Reverse image search often returns "the photo may be XX花园 (XX Garden)" or "XX大厦 (XX Tower)"; a compound name or hotel name read on a web page must be placed at coordinates before it can be checked.
The same name often exists dozens of times across China; the script lists the same-name points in every region, and other clues in the photo pick among them.

Sources:
  so    360 Maps search: good coverage of residential compounds, housing developments, shops and organizations, with address; raw coordinates are GCJ-02, converted to WGS84
  osm   OpenStreetMap Nominatim: named compounds, parks, roads; coordinates WGS84
  sug   Baidu Maps search suggestions: only "city + district + name", no coordinates; use it to see which districts in China have this name

Examples:
  poi.py "<compound name>" --city <city>                 # all same-name points in the city, outputs {name: [lat, lon]}
  poi.py "<district> <road name> 学校" --city <municipality or prefecture-level city>   # --city only accepts prefecture-level cities; put the district in the keyword (学校 = school)
  poi.py "<compound name>" --city <city> --region cn       # sources from the region pack (CN: 360 Maps + OSM + Baidu suggestions)
  poi.py "<street address or place name>" --region mx     # packs without a poi service: OSM restricted to that country
  poi.py "<compound name>"                                # no city: lists which cities in China have a same-name point
  poi.py "<hotel name>" --city <city> --out pois.json && tiles.py sheet --points pois.json --zoom 18 --out pois_sheet.jpg

Baidu Maps web place search requires a CAPTCHA, so the script doesn't use it; the Tencent and Amap APIs require a key, so it doesn't use them either.
"""
from __future__ import annotations

import argparse
from _net import curl_args, PROXY_HELP
import json
import os
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import geo  # noqa: E402
import regions  # noqa: E402

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def _curl(url: str, proxy: str | None = None, ua: str = UA, timeout: int = 25) -> str:
    cmd = ["curl", "-q", "-sS", "-m", str(timeout), "-A", ua, url]
    cmd += curl_args(proxy)
    # Pages are UTF-8. Without encoding=, Chinese Windows decodes as GBK, and stdout is None when decoding fails
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(f"Request failed (curl exit code {r.returncode}): {r.stderr.strip()[:200]}", file=sys.stderr)
    return r.stdout


def search_so(kw: str, city: str | None, n: int, proxy: str | None = None) -> tuple[list[dict], list[dict]]:
    q = {"keyword": kw, "batch": 1, "number": n, "ext": 1, "sid": 1000}
    if city:
        q["cityname"] = city
    raw = _curl("https://restapi.map.so.com/newapi?" + urllib.parse.urlencode(q), proxy=proxy)
    try:
        d = json.loads(raw)
    except json.JSONDecodeError:
        print(f"360 Maps did not return JSON: {raw[:120]}", file=sys.stderr)
        return [], []
    rows = []
    for p in d.get("poi") or []:
        if not p.get("x") or not p.get("y"):
            continue
        lat, lon = geo.gcj2wgs(float(p["y"]), float(p["x"]))
        rows.append({"src": "so", "name": p.get("name", ""), "city": p.get("city", ""), "area": p.get("area", ""),
                     "address": p.get("address", ""), "type": p.get("cat_new_name") or p.get("type", ""),
                     "wgs": [round(lat, 6), round(lon, 6)]})
    cities = [{"city": c.get("name"), "province": c.get("province"), "count": c.get("resultnum")}
              for c in d.get("citysuggestion") or []]
    return rows, cities


def search_osm(kw: str, city: str | None, n: int, proxy: str | None, country: str) -> list[dict]:
    q = {"q": f"{kw} {city}" if city else kw, "format": "jsonv2", "limit": n, "accept-language": "en"}
    if country:
        q["countrycodes"] = country
    raw = _curl("https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(q), proxy=proxy,
                ua="geo-sleuth/1.0 (photo geolocation research)")
    try:
        d = json.loads(raw)
    except json.JSONDecodeError:
        print(f"Nominatim did not return JSON (check service availability with doctor.py --network): {raw[:120]}", file=sys.stderr)
        return []
    return [{"src": "osm", "name": p.get("name") or p.get("display_name", "").split(",")[0],
             "city": "", "area": "", "address": p.get("display_name", ""), "type": f"{p.get('category')}/{p.get('type')}",
             "wgs": [round(float(p["lat"]), 6), round(float(p["lon"]), 6)]} for p in d]


def search_sug(kw: str, proxy: str | None = None) -> list[dict]:
    raw = _curl("https://map.baidu.com/su?" + urllib.parse.urlencode({"wd": kw, "cid": 1, "type": 0, "newmap": 1, "ie": "utf-8"}), proxy=proxy)
    try:
        d = json.loads(raw)
    except json.JSONDecodeError:
        return []
    out = []
    for s in d.get("s") or []:
        parts = s.split("$")
        if len(parts) >= 4:
            out.append({"src": "sug", "city": parts[0], "area": parts[1], "name": parts[3]})
    return out



def _neg_coords(argv: list[str]) -> list[str]:
    """argparse treats negative coordinates like -1.45,-48.5 as option names; a leading space makes them plain values (float ignores the space). Every southern- or western-hemisphere case needs this."""
    return [" " + a if re.match(r"^-\d[\d.]*(,-?[\d.]+)+$", a) else a for a in argv]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("keyword", help="place name, residential compound name, housing development name, or shop name")
    ap.add_argument("--city", help="city name, e.g. <name>市 or <name> (omit to search the whole country)")
    ap.add_argument("--region", help="region pack (code or name): sources and Nominatim country come from its services.poi")
    ap.add_argument("--sources", help="any of so,osm,sug, comma-separated (default: the region pack's; without one, so,osm,sug for Han-script keywords, else osm)")
    ap.add_argument("--limit", type=int, default=10, help="max results per source")
    ap.add_argument("--country", help="Nominatim country code (default: the region pack's; without one, no restriction)")
    ap.add_argument("--proxy", default=os.environ.get("GEO_PROXY"), help=PROXY_HELP)
    ap.add_argument("--out", type=Path, help="write {name: [lat, lon]} (WGS84) for tiles.py mark / sheet")
    args = ap.parse_args(_neg_coords(sys.argv[1:]))
    svc = {}
    if args.region:
        pk = regions.resolve(args.region)
        if pk:
            svc = (pk.get("services") or {}).get("poi") or {"sources": "osm", "country": pk["code"].lower()}
        elif re.fullmatch(r"[A-Za-z]{2}", args.region.strip()):
            # No pack for this country: still restrict Nominatim to it rather than searching the whole world
            svc = {"sources": "osm", "country": args.region.strip().lower()}
            print(f"No region pack for '{args.region}': OSM only, restricted to countrycodes={svc['country']}", file=sys.stderr)
        else:
            sys.exit(f"No region pack for '{args.region}' (installed: {', '.join(sorted(regions.packs()))}): "
                     f"pass its ISO 3166-1 alpha-2 code (e.g. --region in) so the search stays inside that country")
    han = re.search(r"[\u4e00-\u9fff]", args.keyword)
    args.sources = args.sources or svc.get("sources") or ("so,osm,sug" if han and not args.region else "osm")
    args.country = args.country if args.country is not None else svc.get("country", "")

    src = set(args.sources.split(","))
    rows: list[dict] = []
    if "so" in src:
        so_rows, cities = search_so(args.keyword, args.city, args.limit, args.proxy)
        if args.city and so_rows and not any(args.city in (r["city"] + r["area"] + r["address"]) for r in so_rows):
            print(f"Note: none of the 360 Maps results is in \"{args.city}\" — it doesn't recognize this city name and silently switched to another city. "
                  f"Pass a prefecture-level city or municipality to --city (e.g. 重庆 (Chongqing)), and put the district name in the keyword (e.g. \"<district> <name>\")")
        rows += so_rows
        if cities and not args.city:
            print("360 Maps: cities in China with same-name results (result count)")
            print("  " + ", ".join(f"{c['city']}({c['count']})" for c in cities[:30]))
    if "osm" in src:
        rows += search_osm(args.keyword, args.city, args.limit, args.proxy, args.country)
    if "sug" in src:
        sug = search_sug(args.keyword, args.proxy)
        if sug:
            print("Baidu suggestions (no coordinates; only shows which districts have this name):")
            print("  " + "; ".join(f"{s['city']}{s['area']} {s['name']}" for s in sug[:15]))

    # Deduplicate when two sources return the same place (within 150 m and one name contains the other)
    uniq: list[dict] = []
    for r in rows:
        if any(geo.distance(r["wgs"], u["wgs"]) < 150 and (r["name"] in u["name"] or u["name"] in r["name"]) for u in uniq):
            continue
        uniq.append(r)
    print(f"\n{len(uniq)} candidates with coordinates (WGS84):")
    pts = {}
    for i, r in enumerate(uniq, 1):
        label = f"{i:02d} {r['name']} {r['area']}".strip()
        pts[label] = r["wgs"]
        print(f"  {label}  {r['wgs'][0]},{r['wgs'][1]}  [{r['src']}] {r['type']}  {r['address'][:60]}")
    if not uniq:
        print("  None. Try another spelling (drop the \"小区/花园\" (compound/garden) suffix, add the district name), or use revimg.py --query to search the web for an address")
    if args.out:
        args.out.write_text(json.dumps(pts, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"-> {args.out}")
    if len(uniq) >= 2:
        # Several campuses of one school or several branches of a chain all show up here; the first one is not necessarily the right one
        print(f"\nAll {len(uniq)} places must be candidates; don't take only the first one: "
              + (f"`board.py add --from {args.out} --level area --parent <parent>` puts them all on the candidate board" if args.out
                 else "add --out pois.json, then `board.py add --from pois.json --level area` puts them all on the candidate board"))


if __name__ == "__main__":
    # Chinese Windows outputs GBK by default: it crashes on m² or ñ, and the Chinese the agent reads is garbled
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    main()
