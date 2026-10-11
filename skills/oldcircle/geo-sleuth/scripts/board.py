#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Candidate board: every candidate, clue, piece of evidence and exclusion during geolocation is recorded here; ranking and the next step are computed by the script, not from memory.

Rules are written as code, not left to self-discipline:
- There is no "delete candidate" operation. Exclusion has exactly one entry point, `exclude`, and it must be given a computed file (output of geo.py frame, terrain.py and the like);
  the clue itself must be text that was read or a computed result; an inference can only down-weight (likelihood ratio clamped to 1/3–3).
- Exclusion scope must be ≤ evidence scope: for candidates with extent (district/area/road), exclude must state with --covers which stretch the evidence covers;
  coverage under half is rejected. Looking at one point and excluding the whole road (one point standing in for the whole area) is a mistake that recurred twice.
- Discrete candidates are never averaged to a midpoint: the main answer in report is always first place; the rest go to alternatives.
- Population and fame are not evidence: the prior is uniform by default (optionally by area); there is no by-population option.
- Scan order is by "share ÷ pages": scan small districts first, put large districts last with a page cap.
- When discriminating tests can't separate the candidates, next gives a definite next step instead of stalling.

  init       create board.json
  add        add candidates (country/province/city/district/area/point); --from bulk-imports output of poi.py / gazetteer.py / osm.py geom
  children   use gazetteer.py to add every subdivision of an admin area as a candidate ("list the whole category first")
  clue       record a clue: seen / text read / inferred / computed
  evidence   a clue's likelihood ratio for some candidates (>1 supports, <1 opposes)
  exclude    exclude a candidate (needs a computed file)
  scan-bbox  set a candidate's scan extent (built-up area); pages are counted from it
  urban      fill scan-bbox automatically with gazetteer.py urban
  falsify    write the falsification condition before scanning/confirming
  rank       current ranking (score, share, evidence, pages, share/page)
  next       suggested next step
  check      checklist before the conclusion
  report     generate the candidates/alternatives/excluded/unused-clues fields of result.json
  apply      lookup clues (calling code, driving side, territories; plates, area codes… from region packs) add candidates and evidence automatically (uses clues.py)
  move       put a candidate under another candidate (a point under its road) so its supporting evidence counts there
  country    set the country context: apply restricts region-pack lookups to it, next uses its pack's tips
  log        print the ledger

Examples:
  board.py init --photo photo.jpg
  board.py children <municipality or province name>       # all 38 districts become candidates, uniform prior
  board.py add --from pois.json --level area --parent <city>   # fine-level candidates (same-name campuses, OSM walled compounds) all go on the board; don't hand-pick
  board.py clue "bus yellow on top, green below; green rear stripe curves down" --kind livery --status observed --file bus_zoom.png
  board.py evidence --clue K1 --for <district A>:5 --for <district B>:2 --why "compared bus rears one by one across both districts' bus photos" --file livery_sheet.jpg
  board.py apply --kind plate --value <first two plate characters>
  board.py urban <district A> --within <municipality or province name>
  board.py rank
  board.py next
  board.py falsify <district A> --text "give up if the sports field's long axis isn't north-south"
  board.py exclude <district B> --clue K4 --computed frame.json --why "by the view-angle range X should be in frame and ≥40px; it isn't in the image"
  board.py check
  board.py report --merge result.json
"""
from __future__ import annotations

import argparse
from _net import PROXY_HELP
import json
import math
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import regions

HERE = Path(__file__).parent
# uv run writes its own path into the UV env var: call child scripts with it, so uv is found even when it isn't on PATH (e.g. just installed, terminal not reopened)
UV = os.environ.get("UV") or "uv"
LEVELS = ["country", "admin1", "admin2", "city", "district", "area", "road", "point"]
LEVEL_LABEL = {"country": "country", "admin1": "province/state", "admin2": "prefecture/county", "city": "city",
               "district": "district", "area": "area", "road": "road", "point": "point"}
# Candidates with extent: exclusion scope must be <= evidence scope. Looking at one point on a road/area and excluding the whole of it is a mistake that recurred twice
EXTENDED_LEVELS = {"district", "area", "road"}
COVERS_MIN = 0.5  # --covers must cover at least this fraction of the candidate's extent before the whole candidate can be excluded
STATUS = ["observed", "read", "inferred", "computed"]
# Likelihood ratio caps: inferences can only rank; only text read and computed results can move the score a lot
LR_CAP = {"inferred": 3.0, "observed": 5.0, "read": 50.0, "computed": 50.0}
GLOBAL_KINDS = ("calling-code", "driving-side", "territories")   # clues.py tables in data/, not region packs
CHEAP_OPS = [
    ("plate/area-code/calling-code", "plate, area code or calling code readable → `clues.py lookup` + `board.py apply`"),
    ("terrain", "flat vs hill city in the image → `terrain.py view` or z13 satellite imagery per candidate to check terrain; one call rules out a batch"),
    ("livery", "bus/taxi livery → image search for \"<city> <color> bus\" in the local language; read route signs from the results, compare the rear waistline stripe district by district"),
    ("municipal", "guardrails, street lights, bus stops, curb styles → street view of each candidate's built-up area (`gsv.py sheet --points`, or the street-view script the region pack names), one contact sheet per candidate"),
    ("network", "water/road network template → `tiles.py fetch --zoom 13` per candidate, compare river direction and number of bridges"),
    ("phenology", "vegetation + month → weak evidence only, can't exclude on its own"),
]


def _norm(s: str) -> str:
    return re.sub(r"[\s（）()]", "", s or "").rstrip("市省区县自治州自治县自治区特别行政区")


def _clue_kind(kind: str) -> str:
    # Accept the long spelling in new clues and in boards written by older versions.
    return "infra" if kind.strip().lower() in ("infra", "infrastructure") else kind


def _load(p: Path) -> dict:
    if not p.exists():
        sys.exit(f"No {p}: run `board.py init --photo photo.jpg` first")
    return json.loads(p.read_text(encoding="utf-8"))


def _save(p: Path, b: dict) -> None:
    b["updated"] = datetime.now().isoformat(timespec="seconds")
    p.write_text(json.dumps(b, ensure_ascii=False, indent=1), encoding="utf-8")


def _find(b: dict, name: str) -> str:
    if name in b["candidates"]:
        return name
    hits = [k for k in b["candidates"] if _norm(k) == _norm(name)]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        sys.exit(f"No candidate \"{name}\": add it or use children first (existing: {', '.join(list(b['candidates'])[:12])}…)")
    sys.exit(f"\"{name}\" matches several candidates: {hits}; write the full name")


def _log(b: dict, text: str) -> None:
    b.setdefault("log", []).append(f"{datetime.now():%H:%M} {text}")


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    """Run gazetteer.py, clues.py. Child scripts and this one both use UTF-8: Chinese Windows reads and writes GBK by default, and if the two sides differ you get mojibake or crashes."""
    return subprocess.run(cmd, text=True, encoding="utf-8", errors="replace", capture_output=True,
                          env={**os.environ, "PYTHONUTF8": "1"})


def _bbox_km2(bb: list[float]) -> float:
    s, w, n, e = bb
    return abs(n - s) * 110.574 * abs(e - w) * 111.320 * math.cos(math.radians((s + n) / 2))


def _pages(bb: list[float], zoom: int, cell: int, cols: int) -> int:
    s, w, n, e = bb
    mpp = 156543.03392 * math.cos(math.radians((s + n) / 2)) / 2 ** zoom
    step = cell * mpp * 0.9
    r = max(1, math.ceil((n - s) * 110574 / step))
    c = max(1, math.ceil((e - w) * 111320 * math.cos(math.radians((s + n) / 2)) / step))
    return math.ceil(r * c / (cols * cols))


def _inherited(b: dict, name: str, own_clues: set[str]) -> list[dict]:
    """Support flows up, refutation doesn't: a point that matches supports its road, a point that doesn't match says nothing about the rest of the road.
    Per clue the strongest supporting evidence among descendants, for clues the candidate has no evidence of its own."""
    kids: dict[str, list[str]] = {}
    for n, c in b["candidates"].items():
        if c.get("parent") and c.get("status") != "excluded":
            kids.setdefault(c["parent"], []).append(n)
    seen, todo, best = {name}, list(kids.get(name, [])), {}
    while todo:
        n = todo.pop()
        if n in seen:
            continue
        seen.add(n)
        todo += kids.get(n, [])
        for e in b["evidence"]:
            if e["candidate"] == n and e["lr"] > 1 and e["clue"] not in own_clues and e["lr"] > best.get(e["clue"], {}).get("lr", 1):
                best[e["clue"]] = {**e, "via": n}
    return list(best.values())


def _scores(b: dict, level: str, prior_by: str) -> list[dict]:
    rows = []
    for name, c in b["candidates"].items():
        if c["level"] != level:
            continue
        prior = 1.0
        if prior_by == "area" and c.get("bbox"):
            prior = max(_bbox_km2(c["bbox"]), 1.0)
        logit = math.log(prior) + math.log(max(c.get("prior", 1.0), 1e-9))
        ev = [e for e in b["evidence"] if e["candidate"] == name]
        ev += _inherited(b, name, {e["clue"] for e in ev})
        for e in ev:
            logit += math.log(max(e["lr"], 1e-9))
        rows.append({"name": name, "logit": logit, "n_ev": len(ev),
                     "n_verified": sum(1 for e in ev if b["clues"][e["clue"]]["status"] in ("read", "computed")),
                     "excluded": c.get("status") == "excluded", "c": c, "ev": ev})
    open_rows = [r for r in rows if not r["excluded"]]
    if open_rows:
        m = max(r["logit"] for r in open_rows)
        z = sum(math.exp(r["logit"] - m) for r in open_rows)
        for r in open_rows:
            r["share"] = math.exp(r["logit"] - m) / z
    for r in rows:
        r.setdefault("share", 0.0)
    rows.sort(key=lambda r: (r["excluded"], -r["share"]))
    return rows


def _frontier(b: dict) -> str | None:
    """The finest level that still has ≥2 non-excluded candidates; if none, the finest level that has candidates."""
    for lv in reversed(LEVELS):
        if sum(1 for c in b["candidates"].values() if c["level"] == lv and c.get("status") != "excluded") >= 2:
            return lv
    for lv in reversed(LEVELS):
        if any(c["level"] == lv and c.get("status") != "excluded" for c in b["candidates"].values()):
            return lv
    return None


def _cost_of(c: dict, args) -> tuple[int | None, str]:
    bb = c.get("scan_bbox") or c.get("bbox")
    if not bb:
        return None, "no extent"
    pages = _pages(bb, args.zoom, args.cell, args.cols)
    return pages, ("built-up area" if c.get("scan_bbox") else "whole-district bbox")


# ---------------------------------------------------------------- subcommands

def cmd_init(args, p: Path) -> None:
    if p.exists() and not args.force:
        sys.exit(f"{p} already exists (add --force to overwrite)")
    b = {"case": args.case or Path.cwd().name, "photo": args.photo, "created": datetime.now().isoformat(timespec="seconds"),
         "country": _country_code(args.country) if args.country else None,
         "candidates": {}, "clues": {}, "evidence": [], "falsify": {}, "log": []}
    _save(p, b)
    print(f"Created {p}" + (f" (country {b['country']})" if b["country"] else ""))


def _country_code(text: str) -> str:
    pk = regions.resolve(text)
    if not pk:
        print(f"Note: no region pack for '{text}' (installed: {', '.join(sorted(regions.packs())) or 'none'}); "
              f"lookups that need a pack will answer unsupported, global tools still work.")
        return text.upper()
    return pk["code"]


def cmd_country(args, p: Path) -> None:
    b = _load(p)
    if args.code in ("none", "-", ""):
        b["country"] = None
        _log(b, "country cleared")
        _save(p, b)
        print("Country context cleared: lookups search every region pack.")
        return
    b["country"] = _country_code(args.code)
    _log(b, f"country {b['country']}")
    _save(p, b)
    pk = regions.resolve(b["country"])
    print(f"Country context {b['country']}: `apply` restricts region-pack lookups to it; `next` uses its tips."
          + (f" Card: `regions.py show {b['country'].lower()}`." if pk else ""))


def _bbox_around(lat: float, lon: float, r: float) -> list[float]:
    dy, dx = r / 110574, r / (111320 * math.cos(math.radians(lat)))
    return [round(lat - dy, 6), round(lon - dx, 6), round(lat + dy, 6), round(lon + dx, 6)]


def _coords(g) -> list[tuple[float, float]]:
    """All (lon, lat) in a GeoJSON geometry."""
    if isinstance(g, (list, tuple)) and g and isinstance(g[0], (int, float)):
        return [(float(g[0]), float(g[1]))]
    out = []
    for x in g or []:
        out += _coords(x)
    return out


def _read_from(path: Path, radius: float) -> list[tuple[str, dict]]:
    """--from file → [(name, {bbox, center})]. Accepts four forms:
    poi.py/tiles.py {name: [lat, lon]}; gazetteer.py {name: {bbox, center}};
    GeoJSON (osm.py geom, name taken from properties.name); [{name, lat, lon} or {name, bbox}]. Points get an extent from --radius."""
    d = json.loads(path.read_text(encoding="utf-8"))
    rows: list[tuple[str, dict]] = []

    def one(name: str, v) -> None:
        if isinstance(v, (list, tuple)) and len(v) >= 2 and all(isinstance(x, (int, float)) for x in v[:2]):
            lat, lon = float(v[0]), float(v[1])
            rows.append((name, {"center": [lat, lon], "bbox": _bbox_around(lat, lon, radius)}))
        elif isinstance(v, dict):
            bb = v.get("bbox")
            c = v.get("center") or ([v["lat"], v["lon"]] if "lat" in v and "lon" in v else None)
            if bb:
                rows.append((name, {"center": c or [(bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2], "bbox": bb}))
            elif c:
                rows.append((name, {"center": c, "bbox": _bbox_around(float(c[0]), float(c[1]), radius)}))

    if isinstance(d, dict) and d.get("type") == "FeatureCollection":
        for i, f in enumerate(d.get("features", []), 1):
            pr = f.get("properties") or {}
            pts = _coords((f.get("geometry") or {}).get("coordinates"))
            if not pts:
                continue
            lons, lats = [q[0] for q in pts], [q[1] for q in pts]
            name = pr.get("name") or f"{pr.get('@id') or pr.get('id') or f'#{i}'}"
            bb = [min(lats), min(lons), max(lats), max(lons)]
            if len(pts) == 1:
                bb = _bbox_around(lats[0], lons[0], radius)
            rows.append((name, {"center": [round((bb[0] + bb[2]) / 2, 6), round((bb[1] + bb[3]) / 2, 6)],
                                "bbox": [round(v, 6) for v in bb]}))
    elif isinstance(d, dict):
        for name, v in d.items():
            if not str(name).startswith("_"):
                one(str(name), v)
    elif isinstance(d, list):
        for i, v in enumerate(d, 1):
            if isinstance(v, dict):
                one(str(v.get("name") or f"#{i}"), v)
    # Same names (several campuses of one school, several same-name walled areas in OSM) get a sequence number; none are dropped
    seen: dict[str, int] = {}
    out = []
    for name, v in rows:
        seen[name] = seen.get(name, 0) + 1
        out.append((name if seen[name] == 1 else f"{name}#{seen[name]}", v))
    return out


def cmd_add(args, p: Path) -> None:
    b = _load(p)
    if args.level not in LEVELS:
        sys.exit(f"--level must be one of {LEVELS}")
    if not args.names and not args.from_:
        sys.exit("Give candidate names, or --from a file (poi.py --out, gazetteer.py --out, GeoJSON from osm.py geom)")
    if args.from_:
        rows = _read_from(Path(args.from_), args.radius)
        if not rows:
            sys.exit(f"No candidates with coordinates read from {args.from_}")
        n, added = 0, []
        for name, v in rows:
            key = _slot(b, name, args.parent, None, args.level)
            if not key:
                continue
            added.append(key)
            b["candidates"][key] = {"level": args.level, "parent": args.parent, "bbox": v["bbox"], "scan_bbox": None,
                                     "center": v["center"], "prior": args.prior, "status": "open",
                                     "note": args.note or "", "from": str(args.from_)}
            n += 1
        _log(b, f"add --from {args.from_} → +{n} {args.level}")
        _save(p, b)
        hints = [h for k in added for h in [_skip_hint(b, k)] if h]
        if hints:
            print(f"NOTE {hints[0]}" + (f" (and {len(hints) - 1} more)" if len(hints) > 1 else ""))
        print(f"Added {n} {LEVEL_LABEL[args.level]} candidates from {args.from_} ({len(rows)} read; duplicate names skipped). "
              f"Same names under another parent get the parent in the key. All on the board with a uniform prior: record evidence for every one you look at (record --against too when it doesn't match); check lists the ones not looked at.")
    for raw in args.names:
        name = _slot(b, raw, args.parent, None, args.level)
        if not name:
            print(f"Already have {raw}" + (f" under {args.parent}" if args.parent else "") + ", skipping")
            continue
        c = {"level": args.level, "parent": args.parent, "bbox": None, "scan_bbox": None, "prior": args.prior,
             "status": "open", "note": args.note or ""}
        if args.bbox:
            c["bbox"] = [float(v) for v in args.bbox.split(",")]
        b["candidates"][name] = c
        _log(b, f"add {name} ({args.level})")
        hint = _skip_hint(b, name)
        if hint:
            print(f"NOTE {hint}")
    _save(p, b)
    print(f"{len(b['candidates'])} candidates")


def cmd_move(args, p: Path) -> None:
    b = _load(p)
    name = _find(b, args.name)
    parent = _find(b, args.parent)
    if parent == name:
        sys.exit("A candidate can't be its own parent")
    if LEVELS.index(b["candidates"][parent]["level"]) >= LEVELS.index(b["candidates"][name]["level"]):
        sys.exit(f"{parent} ({b['candidates'][parent]['level']}) isn't coarser than {name} ({b['candidates'][name]['level']})")
    old = b["candidates"][name].get("parent")
    b["candidates"][name]["parent"] = parent
    _log(b, f"move {name}: {old} → {parent}")
    _save(p, b)
    print(f"{name} now under {parent} (was {old}); its supporting evidence now counts for {parent} in the {b['candidates'][parent]['level']} ranking")
    hint = _skip_hint(b, name)
    if hint:
        print(f"NOTE {hint}")


def cmd_children(args, p: Path) -> None:
    b = _load(p)
    cmd = [UV, "run", str(HERE / "gazetteer.py"), "children", args.parent, "--out", str(p.parent / ".gz_children.json")]
    if args.level:
        cmd += ["--level", str(args.level)]
    if args.within:
        cmd += ["--within", args.within]
    if args.proxy:
        cmd += ["--proxy", args.proxy]
    r = _run(cmd)
    for line in r.stderr.splitlines():
        if "not treated as the next level" in line or "falling back to the first" in line:
            print(line)
    out = r.stdout.strip(); print(out if len(out) < 1800 else out[:1800].rsplit('\n', 1)[0] + '\n  …')
    if r.returncode != 0:
        sys.exit(f"gazetteer failed: {r.stderr.strip()[-600:]}")
    kids = json.loads((p.parent / ".gz_children.json").read_text(encoding="utf-8"))
    as_level, why = _child_level(b, args, out)
    # Stable ids from a region pack's admin table, so lookups (plates, area codes) land on these same candidates
    pk, local = regions.admin_children(args.parent, b.get("country"))
    by_local = {}
    if pk:
        chain = regions.admin_chain(pk, regions.admin_find(args.parent, pk["code"])[0][1])
        for it in local:
            by_local[_norm(it["name"])] = "/".join([pk["code"], *chain, it["name"]])
    n = 0
    for raw, k in kids.items():
        cid = by_local.get(_norm(raw))
        name = _slot(b, raw, args.parent, cid, as_level)
        if not name:
            continue
        b["candidates"][name] = {"level": as_level, "parent": args.parent, "bbox": k.get("bbox"), "scan_bbox": None,
                                 "prior": 1.0, "status": "open", "note": k.get("note", ""), "osm_id": k.get("osm_id"),
                                 "country": pk["code"] if pk else b.get("country"), "cid": cid}
        n += 1
    _log(b, f"children {args.parent} → +{n} {as_level}")
    _save(p, b)
    print(f"Added {n} candidates (level {as_level}: {why}; uniform prior). Population and fame don't enter the score.")


# Parent's level on the board → level the children are recorded as
NEXT_LEVEL = {"country": "admin1", "admin1": "admin2", "admin2": "district", "city": "district", "district": "area",
              "area": "road", "road": "point"}


def _child_level(b: dict, args, gz_out: str) -> tuple[str, str]:
    """Candidate level for children: use --as-level if given; parent is a country → admin1; parent already on the board → its next level
    (where a province's next level down is directly districts, as with a municipality, record as district); otherwise → district."""
    if args.as_level:
        return args.as_level, "set by --as-level"
    m = re.search(r"admin_level (\d+)\) children admin_level (\d+)", gz_out)
    p_lv, c_lv = (int(m.group(1)), int(m.group(2))) if m else (None, None)
    if p_lv is not None and p_lv <= 2:
        # When jumping straight from a country to a finer level (--level 5/6), don't record as province level
        lv = "admin1" if c_lv is None or c_lv <= 4 else ("admin2" if c_lv == 5 else "district")
        return lv, f"parent is a country, children admin_level {c_lv}"
    hits = [k for k in b["candidates"] if _norm(k) == _norm(args.parent)]
    if len(hits) == 1:
        lv = b["candidates"][hits[0]]["level"]
        nxt = NEXT_LEVEL.get(lv, "district")
        if lv == "admin1" and p_lv is not None and c_lv is not None and c_lv >= p_lv + 2:
            nxt = "district"
        return nxt, f"parent {hits[0]} is {lv} on the candidate board"
    return "district", "default"


def cmd_clue(args, p: Path) -> None:
    b = _load(p)
    kid = f"K{len(b['clues']) + 1}"
    if args.status not in STATUS:
        sys.exit(f"--status must be one of {STATUS}: observed=shape/color seen directly in the image, read=text/numbers read, inferred=inference (building about 8 floors, road going uphill), computed=computed by a script")
    resolves = list(dict.fromkeys(getattr(args, "resolves", None) or []))
    output = args.file or ""
    if resolves:
        if args.status != "computed":
            sys.exit("--resolves requires --status computed: link a result that actually tests the named clues")
        unknown = [k for k in resolves if k not in b["clues"]]
        if unknown:
            sys.exit(f"Unknown clues in --resolves: {', '.join(unknown)}")
        if not output or not Path(output).is_file():
            sys.exit("--resolves requires --file pointing to an existing computed output file")
        output = str(Path(output).resolve())
    kind = _clue_kind(args.kind)
    b["clues"][kid] = {"text": args.text, "kind": kind, "status": args.status, "file": output,
                       "source": args.source or "", "used": False}
    if resolves:
        b["clues"][kid]["resolves"] = resolves
    _log(b, f"clue {kid} [{kind}/{args.status}] {args.text}" + (f"; resolves {', '.join(resolves)}" if resolves else ""))
    _save(p, b)
    cap = LR_CAP[args.status]
    print(f"{kid} recorded. Status {args.status}: likelihood ratio cap {cap:g}" + (", can only rank, can't exclude" if args.status in ("inferred", "observed") else ", usable for exclude (still needs a computed file)"))


def _parse_lr(items: list[str] | None, default: float | None) -> list[tuple[str, float]]:
    out = []
    for it in items or []:
        if ":" in it:
            name, v = it.rsplit(":", 1)
            out.append((name, float(v)))
        elif default is not None:
            out.append((it, default))
        else:
            sys.exit(f"Write it as name:likelihood_ratio, e.g. {it}:5")
    return out


def cmd_evidence(args, p: Path) -> None:
    b = _load(p)
    if args.clue not in b["clues"]:
        sys.exit(f"No clue {args.clue}; run `board.py clue` first")
    cl = b["clues"][args.clue]
    cap = LR_CAP[cl["status"]]
    pairs = _parse_lr(args.for_, 3.0) + [(n, v) for n, v in _parse_lr(args.against, 1 / 3)]
    if not pairs:
        sys.exit("Give at least one --for name:likelihood_ratio or --against name:likelihood_ratio")
    clipped = []
    for name, lr in pairs:
        cname = _find(b, name)
        if lr <= 0:
            sys.exit("A likelihood ratio of 0 means exclusion; use `board.py exclude` (needs a computed file)")
        lr2 = min(max(lr, 1 / cap), cap)
        if abs(lr2 - lr) > 1e-9:
            clipped.append(f"{cname}:{lr:g}→{lr2:g}")
        b["evidence"].append({"id": f"E{len(b['evidence']) + 1}", "clue": args.clue, "candidate": cname, "lr": lr2,
                              "why": args.why or "", "file": args.file or "", "cmd": args.command_ or ""})
    cl["used"] = True
    if args.file and not Path(args.file).exists():
        print(f"Note: {args.file} doesn't exist; evidence files must be real outputs of this session")
    _log(b, f"evidence {args.clue} → {', '.join(f'{n}:{v:g}' for n, v in pairs)}")
    _save(p, b)
    if clipped:
        print(f"Clue {args.clue} is \"{cl['status']}\", likelihood ratio clamped to 1/{cap:g}–{cap:g}: {'; '.join(clipped)}. "
              f"For more weight, first verify the clue as read/computed (read the text, run a script), then record a new clue.")
    print("Recorded." + ("" if args.why else " Suggest adding --why to state the basis."))


def cmd_exclude(args, p: Path) -> None:
    b = _load(p)
    cname = _find(b, args.name)
    if args.clue not in b["clues"]:
        sys.exit(f"No clue {args.clue}")
    cl = b["clues"][args.clue]
    if cl["status"] not in ("read", "computed"):
        sys.exit(f"Clue {args.clue} is \"{cl['status']}\" (inferred/observed): it can't exclude, only `evidence --against {cname}:0.34`. "
                 f"Hard rule 9: exclusion and confirmation use the same standard.")
    if not args.computed or not Path(args.computed).exists():
        sys.exit("Exclusion must attach a computed file (--computed, e.g. geo.py frame output or a terrain.py comparison image), and the file must actually exist")
    c = b["candidates"][cname]
    if c["level"] in EXTENDED_LEVELS:
        if not args.covers:
            sys.exit(
                f"{cname} is a {LEVEL_LABEL[c['level']]}-level candidate (has extent): exclusion needs --covers stating where the evidence actually covers "
                f"('lat,lon' or 'lat,lon:lat,lon'). Hard rule 9: exclusion scope must be ≤ evidence scope — "
                f"looking at one point and excluding the whole thing is one point standing in for the whole area. If you only checked one stretch, use instead: "
                f"board.py evidence --clue {args.clue} --against {cname}:0.34 --file {args.computed}")
        pts = _parse_covers(args.covers)
        if not pts:
            sys.exit("--covers must parse to coordinates: 'lat,lon' (single point) or 'lat,lon:lat,lon' (span)")
        r = _covers_ratio(c, pts)
        if r is not None and r[0] < COVERS_MIN:
            cov_m = _cov_span_m(pts[0], pts[-1]) if len(pts) >= 2 else 0.0
            sys.exit(
                f"--covers covers only about {r[0]:.0%} of {cname} (evidence {cov_m:.0f} m / candidate extent diagonal {r[1]:.0f} m): "
                f"not enough to exclude the whole thing. Add comparison images for the remaining stretches before excluding, or down-weight first: "
                f"board.py evidence --clue {args.clue} --against {cname}:0.34 --file {args.computed}")
    c["status"] = "excluded"
    c["excluded_by"] = {"clue": args.clue, "computed": args.computed, "why": args.why or "",
                        "covers": args.covers or ""}
    cl["used"] = True
    _log(b, f"exclude {cname} by {args.clue} ({args.computed})")
    _save(p, b)
    print(f"Excluded {cname}. Excluded candidates stay in the ledger; check looks back at them.")


def cmd_scan_bbox(args, p: Path) -> None:
    b = _load(p)
    cname = _find(b, args.name)
    b["candidates"][cname]["scan_bbox"] = [float(v) for v in args.bbox.split(",")]
    _log(b, f"scan-bbox {cname} {args.bbox}")
    _save(p, b)
    print("ok")


def cmd_urban(args, p: Path) -> None:
    b = _load(p)
    cname = _find(b, args.name)
    cmd = [UV, "run", str(HERE / "gazetteer.py"), "urban", cname]
    if args.within:
        cmd += ["--within", args.within]
    if args.proxy:
        cmd += ["--proxy", args.proxy]
    r = _run(cmd)
    if r.returncode != 0:
        sys.exit(f"gazetteer urban failed: {r.stderr.strip()[-600:]}")
    d = json.loads(r.stdout[r.stdout.index("{"):])
    if d.get("urban_bbox"):
        b["candidates"][cname]["scan_bbox"] = d["urban_bbox"]
        b["candidates"][cname]["urban_source"] = d.get("source")
        _log(b, f"urban {cname} {d['urban_bbox']} ({d.get('source')})")
        _save(p, b)
        print(f"{cname} built-up area {d['urban_bbox']}, about {d.get('urban_bbox_km2')} km² (source {d.get('source')})"
              + (f"; {d['note']}" if d.get("note") else ""))
    else:
        print(f"{cname}: {d.get('note', 'no built-up area data')}; set it by hand with `board.py scan-bbox`")


def cmd_falsify(args, p: Path) -> None:
    b = _load(p)
    cname = _find(b, args.name)
    b["falsify"].setdefault(cname, []).append(args.text)
    _log(b, f"falsify {cname}: {args.text}")
    _save(p, b)
    print("Falsification condition recorded. If it shows up, give up; don't look for reasons to explain it away.")


def cmd_rank(args, p: Path, quiet: bool = False) -> dict:
    b = _load(p)
    out = {}
    for lv in LEVELS:
        rows = _scores(b, lv, args.prior_by)
        if not rows:
            continue
        out[lv] = rows
        if quiet:
            continue
        print(f"\n[{LEVEL_LABEL[lv]}] {len(rows)} candidates ({sum(1 for r in rows if not r['excluded'])} not excluded)")
        print(f"  {'candidate':<14}{'share':>7}{'evidence':>9}{'verified':>9}{'pages':>6}  {'share/page':>10}  note")
        for r in rows[: args.limit]:
            pages, src = _cost_of(r["c"], args)
            ratio = (r["share"] / pages) if pages else None
            flag = "excluded" if r["excluded"] else ""
            print(f"  {r['name']:<14}{r['share']:>7.1%}{r['n_ev']:>9}{r['n_verified']:>9}{(pages if pages is not None else '?'):>6}"
                  f"  {(f'{ratio:.4f}' if ratio is not None else '?'):>10}  {flag} {src if pages is not None else ''} {r['c'].get('note', '')[:30]}")
        if len(rows) > args.limit:
            print(f"  … {len(rows) - args.limit} more (raise --limit)")
    if not out and not quiet:
        print("No candidates: run `board.py add` or `board.py children` first")
    return out


def _corridor_pending(b: dict) -> list[str]:
    """Infrastructure observations without a computed result explicitly addressing them."""
    infra = [k for k, c in b["clues"].items() if _clue_kind(c["kind"]) == "infra" and c["status"] in ("observed", "read")]
    done = {k for c in b["clues"].values()
            if c["status"] == "computed" and c.get("resolves") and c.get("file") and Path(c["file"]).is_file()
            for k in c.get("resolves", [])}
    return [k for k in infra if k not in done]


def cmd_next(args, p: Path) -> None:
    b = _load(p)
    pend = _corridor_pending(b)
    if pend:
        print(f"→ First: infrastructure clue {', '.join(pend)} has no linked corridor result yet. `osm.py geom '<filter>' --bbox <region> --out lines.geojson` → "
              f"`terrain.py scan --lines lines.geojson` (mountains fill the frame: add `--flat-run 0 --min-low-deg 0`) → `terrain.py fit`; "
              f"two or three kinds of infrastructure: `osm.py near`. Record a result that actually tests the clue with "
              f"`board.py clue '<result>' --kind corridor --status computed --file <output> --resolves <clue-id>` "
              f"(repeat --resolves for each clue tested).")
    lv = _frontier(b)
    if not lv:
        print("No candidates. First do step 2 (lookup clues) or step 4 (coarse location from the environment) and list the candidates in full (board.py children)")
        return
    rows = [r for r in _scores(b, lv, args.prior_by) if not r["excluded"]]
    top = rows[0]
    second = rows[1] if len(rows) > 1 else None
    unused = [k for k, c in b["clues"].items() if not c["used"]]
    print(f"Current frontier: {LEVEL_LABEL[lv]}, {len(rows)} not excluded; first {top['name']} {top['share']:.0%}"
          + (f", second {second['name']} {second['share']:.0%}" if second else ""))
    if unused:
        pending = ", ".join(f"{k}({b['clues'][k]['kind']})" for k in unused)
        print(f"Clues not used yet: {pending} → evidence or apply first")
    separable = (not second) or (top["share"] >= 0.7 and top["share"] / max(second["share"], 1e-9) >= 3)
    if separable and top["n_verified"] == 0 and second:
        print(f"{top['name']} leads but has no verified evidence at all (read/computed); it's built from inferences only: do one cheap verification before scanning.")
    if separable:
        pages, src = _cost_of(top["c"], args)
        print(f"→ Ready to narrow/scan: {top['name']} ({src}, about {pages if pages is not None else '?'} pages).")
        if src == "whole-district bbox":
            print("  First `board.py urban <name>` or `scan-bbox` to shrink the extent to the built-up area; pages drop by an order of magnitude.")
        elif pages is None:
            print(f"  It has no extent yet: `board.py urban {top['name']} --within <parent>` or `board.py scan-bbox {top['name']} --bbox s,w,n,e`, otherwise pages can't be computed.")
        if top["name"] not in b["falsify"]:
            print(f"  Write the falsification condition before scanning: `board.py falsify {top['name']} --text \"…\"`")
        print("  Let the machine rank the scan first: `sat_scan.py grid --bbox <scan_bbox> --preset …`, `osm.py buildings`, `poi.py`; look only at the top 20–30.")
        return
    print("→ Can't separate. Do discriminating tests from cheap to expensive, each on all non-excluded candidates together, not just the leader:")
    kinds_have = {c["kind"] for c in b["clues"].values()}
    pk = _region_of(b, rows)
    tips = (pk or {}).get("tips") or {}
    if pk:
        print(f"  (region pack {pk['code']}: `regions.py show {pk['code'].lower()}` lists its lookups, services and clue index)")
    for kind, tip in [(k, tips.get(k, t)) for k, t in CHEAP_OPS]:
        mark = "(you already have a clue of this kind; record evidence)" if any(k in kinds_have for k in kind.split("/")) else ""
        print(f"  - {kind}: {tip} {mark}")
    print("→ All cheap tests done and still can't separate: don't stop. Scan in \"share ÷ pages\" order, finish the small ones first, set a page cap on the large ones:")
    order = []
    for r in rows:
        pages, src = _cost_of(r["c"], args)
        order.append((r["share"] / pages if pages else 0, r, pages, src))
    order.sort(key=lambda t: -t[0])
    for ratio, r, pages, src in order[:8]:
        print(f"    {r['name']:<14} share {r['share']:.0%}  pages {pages if pages is not None else '?'} ({src})  share/page {ratio:.4f}")
    if any(pages is None for _, _, pages, _ in order):
        print("    Some candidates have no extent: fill it in with `board.py urban` or `scan-bbox`, otherwise they can't be ordered")


def _region_of(b: dict, rows: list[dict]) -> dict | None:
    """The board's country, else the one country all open frontier candidates share."""
    if b.get("country"):
        return regions.resolve(b["country"])
    codes = {r["c"].get("country") for r in rows}
    return regions.resolve(codes.pop()) if len(codes) == 1 and None not in codes else None


def _parse_covers(s: str) -> list[tuple[float, float]]:
    """--covers: 'lat,lon' or 'lat,lon:lat,lon' (the point/span the evidence actually covers). Returns [] if no coordinates parse."""
    pts = []
    for part in str(s).split(":"):
        m = re.findall(r"-?\d+\.\d+|-?\d+", part)
        if len(m) >= 2:
            pts.append((float(m[0]), float(m[1])))
    return pts


def _cov_span_m(a: tuple[float, float], b: tuple[float, float]) -> float:
    kx = 111320.0 * math.cos(math.radians((a[0] + b[0]) / 2))
    return math.hypot((b[1] - a[1]) * kx, (b[0] - a[0]) * 110540.0)


def _covers_ratio(c: dict, pts: list[tuple[float, float]]) -> tuple[float, float] | None:
    """(evidence coverage length / candidate extent diagonal, diagonal in meters). None if the candidate has no bbox (can't compute, only warn)."""
    bb = c.get("bbox") or c.get("scan_bbox")
    if not bb or len(bb) != 4:
        return None
    try:
        sw, ww, nn, ee = (float(v) for v in bb)
    except (TypeError, ValueError):
        return None
    diag = _cov_span_m((sw, ww), (nn, ee))
    if diag <= 1.0:
        return None
    cov = _cov_span_m(pts[0], pts[-1]) if len(pts) >= 2 else 0.0
    return cov / diag, diag


def _unseen(rows: list[dict], lv: str) -> list[str]:
    """Non-excluded candidates at fine levels (area/road/point) without a single piece of evidence. Coarse levels are scanned in share/pages order, where no evidence is normal, so they don't count."""
    if lv not in ("area", "road", "point"):
        return []
    return [r["name"] for r in rows if r["n_ev"] == 0 and not r["excluded"]]


def _center_of(c: dict) -> tuple[float, float] | None:
    if c.get("center"):
        return float(c["center"][0]), float(c["center"][1])
    bb = c.get("bbox")
    return ((bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2) if bb else None


def _inside(c: dict, lat: float, lon: float, pad_m: float = 30) -> bool | None:
    """Is (lat, lon) inside the candidate's bbox (padded)? None when the candidate has no bbox."""
    bb = c.get("bbox")
    if not bb:
        return None
    dy, dx = pad_m / 110574, pad_m / (111320 * math.cos(math.radians(lat)))
    return bb[0] - dy <= lat <= bb[2] + dy and bb[1] - dx <= lon <= bb[3] + dx


def _skipped_level(b: dict, name: str) -> tuple[str, list[str], str | None] | None:
    """A candidate that skips a level its siblings use: a point added under a city that also has road candidates.
    Its evidence then never reaches that level's ranking, which goes on ranking the other roads.
    Returns (skipped level, the siblings at that level, the one whose bbox contains it or None)."""
    c = b["candidates"][name]
    li = LEVELS.index(c["level"])
    for lv in reversed(LEVELS[:li]):
        sibs = [n for n, s in b["candidates"].items() if s["level"] == lv and s.get("parent") == c.get("parent")
                and n != c.get("parent") and s.get("status") != "excluded"]
        if not sibs:
            continue
        at = _center_of(c)
        home = next((n for n in sibs if at and _inside(b["candidates"][n], *at)), None)
        return lv, sibs, home
    return None


def _skip_hint(b: dict, name: str) -> str | None:
    gap = _skipped_level(b, name)
    if not gap:
        return None
    lv, sibs, home = gap
    c = b["candidates"][name]
    where = (f"it lies inside {home} → `board.py move '{name}' --parent '{home}'`" if home else
             f"none of them contains it, so that ranking leaves the answer out → `board.py add <its {lv}> --level {lv} --parent '{c.get('parent')}' --bbox s,w,n,e`, "
             f"then `board.py move '{name}' --parent <it>`")
    return (f"{name} ({c['level']}) sits directly under {c.get('parent')}, which also has {len(sibs)} {lv} candidates; "
            f"its evidence never reaches the {lv} ranking: {where}")


def cmd_check(args, p: Path) -> None:
    b = _load(p)
    ok = True
    print("Pre-conclusion check:")
    for name, c in b["candidates"].items():
        if c.get("status") == "excluded":
            ex = c.get("excluded_by", {})
            if not ex.get("computed") or not Path(ex["computed"]).exists():
                ok = False
                print(f"  FAIL file for excluding {name} doesn't exist: {ex.get('computed')}")
    for name, c in b["candidates"].items():
        if c.get("status") != "excluded" or c["level"] not in EXTENDED_LEVELS:
            continue
        ex = c.get("excluded_by", {})
        pts = _parse_covers(ex.get("covers", ""))
        if not pts:
            ok = False
            print(f"  FAIL excluding {name} ({LEVEL_LABEL[c['level']]} level) has no --covers recorded: no way to judge how much the evidence covered, "
                  f"possibly one point standing in for the whole area → re-run exclude with --covers, or switch to evidence --against to down-weight")
            continue
        r = _covers_ratio(c, pts)
        if r is None:
            print(f"  NOTE evidence for excluding {name} covers {ex['covers']}; the candidate has no bbox, so the coverage ratio can't be computed → "
                  f"state in the conclusion that only this stretch was checked")
        elif r[0] < COVERS_MIN:
            ok = False
            print(f"  FAIL evidence for excluding {name} covers only about {r[0]:.0%} (candidate extent diagonal {r[1]:.0f} m): exclusion scope exceeds evidence scope")
    for name, c in b["candidates"].items():
        if c.get("status") != "excluded" and any(e["candidate"] == name and e["lr"] > 1 for e in b["evidence"]):
            hint = _skip_hint(b, name)
            if hint:
                ok = False
                print(f"  FAIL {hint}")
    lv = _frontier(b)
    if lv:
        rows = [r for r in _scores(b, lv, args.prior_by) if not r["excluded"]]
        top = rows[0]
        if top["n_verified"] == 0:
            ok = False
            print(f"  FAIL main answer {top['name']} has no read/computed evidence, only observations and inferences: you can't claim this level or finer")
        else:
            print(f"  ok   main answer {top['name']}: {top['n_ev']} pieces of evidence, {top['n_verified']} verified")
        weak = [r["name"] for r in rows[1:] if r["share"] >= 0.15]
        if weak:
            print(f"  WARN alternatives with share ≥15% remain: {', '.join(weak)} → write them into alternatives with a discriminating test; no midpoint")
        unseen = _unseen(rows, lv)
        if unseen:
            print(f"  WARN {len(unseen)}/{len(rows)} {LEVEL_LABEL[lv]} candidates have no evidence at all, i.e. were never looked at: "
                  f"{', '.join(unseen[:10])}{' …' if len(unseen) > 10 else ''} → look at each; record evidence --against even when it doesn't match; "
                  f"unseen ones don't count as excluded; state this in the conclusion")
        down = [(e["candidate"], e["clue"]) for e in b["evidence"]
                if e["lr"] < 1 and b["clues"][e["clue"]]["status"] in ("inferred", "observed")
                and b["candidates"][e["candidate"]].get("status") != "excluded"]
        if down:
            names = sorted({n for n, _ in down})
            print(f"  NOTE candidates down-weighted by inference but not excluded: {', '.join(names[:10])} → when no candidate matches, look back at these first")
    for k, c in b["clues"].items():
        if c["status"] in ("read", "computed") and not c.get("file"):
            print(f"  WARN {k} is {c['status']} but has no file: text read needs a zoomed image, computed results need an output file")
    # fine-level answer needs the evidence image the Output section asks for
    fine = [n for n, c in b["candidates"].items() if c["level"] in ("area", "road", "point") and c.get("status") != "excluded"
            and any(e["candidate"] == n and e["lr"] > 1 for e in b["evidence"])]
    if fine:
        ev = Path(args.evidence) if args.evidence else p.parent / "evidence.jpg"
        if not ev.exists():
            ok = False
            print(f"  FAIL evidence image {ev} doesn't exist: supporting evidence reaches area/road/point level ({', '.join(fine[:3])}) → make it with evidence.py "
                  f"(camera + heading wedge on satellite, comparison panels), or pass --evidence <path>")
        else:
            print(f"  ok   evidence image {ev}")
    unused = [k for k, c in b["clues"].items() if not c["used"]]
    if unused:
        print(f"  NOTE unused clues: {', '.join(unused)} → write them into unused_clues")
    for name in [n for n, c in b["candidates"].items() if c.get("status") != "excluded"]:
        if b["falsify"].get(name):
            print(f"  ok   {name} falsification condition: {'; '.join(b['falsify'][name])}")
    print("Result: " + ("pass" if ok else "has FAIL, fix those first"))


def cmd_report(args, p: Path) -> None:
    b = _load(p)
    lv = _frontier(b)
    rep = {"candidate_levels": {}, "main": None, "alternatives": [], "excluded": [], "unused_clues": [],
           "downweighted_not_excluded": [], "falsify": b["falsify"]}
    for l2 in LEVELS:
        rows = _scores(b, l2, args.prior_by)
        if rows:
            rep["candidate_levels"][l2] = [{"name": r["name"], "share": round(r["share"], 3), "evidence": r["n_ev"],
                                            "verified": r["n_verified"], "excluded": r["excluded"]} for r in rows]
    if lv:
        rows = [r for r in _scores(b, lv, args.prior_by) if not r["excluded"]]
        top = rows[0]
        rep["main"] = {"level": lv, "name": top["name"], "share": round(top["share"], 3),
                       "evidence": [{"clue": b["clues"][e["clue"]]["text"], "status": b["clues"][e["clue"]]["status"],
                                     "lr": e["lr"], "why": e["why"], "file": e["file"], **({"via": e["via"]} if e.get("via") else {})}
                                    for e in top["ev"]]}
        for r in rows[1:]:
            if r["share"] >= 0.05:
                rep["alternatives"].append({"name": r["name"], "share": round(r["share"], 3),
                                            "how_to_separate": "run one cheap test on both together (terrain/livery/municipal fixtures/water template), or scan the first 3 pages of each built-up area"})
        rep["unexamined"] = _unseen(rows, lv)
    rep["level_gaps"] = [h for n, c in b["candidates"].items() if c.get("status") != "excluded"
                         and any(e["candidate"] == n and e["lr"] > 1 for e in b["evidence"]) for h in [_skip_hint(b, n)] if h]
    for name, c in b["candidates"].items():
        if c.get("status") == "excluded":
            ex = c.get("excluded_by", {})
            rep["excluded"].append({"name": name, "clue": b["clues"].get(ex.get("clue"), {}).get("text", ""),
                                    "computed": ex.get("computed"), "why": ex.get("why", "")})
    rep["unused_clues"] = [c["text"] for c in b["clues"].values() if not c["used"]]
    rep["downweighted_not_excluded"] = sorted({e["candidate"] for e in b["evidence"] if e["lr"] < 1
                                               and b["clues"][e["clue"]]["status"] in ("inferred", "observed")
                                               and b["candidates"][e["candidate"]].get("status") != "excluded"})
    if args.merge:
        mp = Path(args.merge)
        base = json.loads(mp.read_text(encoding="utf-8")) if mp.exists() else {}
        if rep["main"] and isinstance(base.get("lat"), (int, float)) and isinstance(base.get("lon"), (int, float)):
            inside = _inside(b["candidates"][rep["main"]["name"]], base["lat"], base["lon"], pad_m=max(30, float(base.get("radius_m") or 0)))
            if inside is False:
                rep["main_mismatch"] = (f"result.json lat/lon is outside the board's main answer {rep['main']['name']} ({rep['main']['level']}): "
                                        f"the answer's candidate isn't on that level, or the board ranking disagrees with the conclusion")
        base["board"] = rep
        if rep["alternatives"]:
            base.setdefault("alternatives", [])
            base["alternatives"] = [f"{a['name']} (share {a['share']:.0%}): {a['how_to_separate']}" for a in rep["alternatives"]] + \
                [x for x in base.get("alternatives", []) if not isinstance(x, str) or "(share " not in x]
        base["excluded"] = [f"{x['name']}: {x['why']} ({x['computed']})" for x in rep["excluded"]] or base.get("excluded", [])
        base["unused_clues"] = rep["unused_clues"] or base.get("unused_clues", [])
        mp.write_text(json.dumps(base, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"Merged into {mp} (board field + alternatives/excluded/unused_clues)")
    print(json.dumps(rep, ensure_ascii=False, indent=1)[:4000])
    for w in rep["level_gaps"] + ([rep["main_mismatch"]] if rep.get("main_mismatch") else []):
        print(f"WARN {w}")
    if rep["main"] and rep["alternatives"]:
        print("\nReminder: main answer = first place, alternatives listed separately; no midpoint, no big circle.")


SUB_LEVELS = {"admin2", "city", "district"}   # children may record a prefecture as district; these count as one tier for name matching


def _same_tier(a: str, b: str) -> bool:
    """Levels at which two same-named places could be one place (吉林省 and its 吉林市 share a stem, not a level)."""
    return a == b or (a in SUB_LEVELS and b in SUB_LEVELS)


def _slot(b: dict, name: str, parent: str | None, cid: str | None, level: str) -> str | None:
    """Key for a new candidate, or None when the board already has this place. A same-name place under another parent
    (Gulou District in Nanjing and in Fuzhou) is a different candidate and gets its parent in the key."""
    if name in b["candidates"] and not _same_tier(b["candidates"][name]["level"], level):
        return f"{name} ({level})" if f"{name} ({level})" not in b["candidates"] else None
    same = [k for k in b["candidates"] if _norm(k.split(" (")[0]) == _norm(name) and _same_tier(b["candidates"][k]["level"], level)]
    if not same:
        return name
    for k in same:
        c = b["candidates"][k]
        if cid and c.get("cid"):
            if c["cid"] == cid:
                return None
            continue
        if not parent or not c.get("parent") or _norm(c["parent"]) == _norm(parent):
            return None
    key = f"{name} ({parent})"
    return None if key in b["candidates"] else key


def _same_place(c: dict, name: str, parent: str | None, code: str | None, cid: str | None) -> bool:
    """Is board candidate c the place a lookup names? Same stable id; or same name with no conflicting id, country or parent."""
    if cid and c.get("cid"):
        return c["cid"] == cid
    if code and c.get("country") and c["country"] != code:
        return False
    if parent and c.get("parent") and _norm(c["parent"]) != _norm(parent):
        return False
    return True


def _ensure(b: dict, level: str, name: str, parent: str | None, code: str | None, cid: str | None, why: str) -> str:
    """Candidate key for this place, creating it if needed. Same-name places elsewhere get their parent in the key, e.g. 朝阳区 (长春市)."""
    for k, c in b["candidates"].items():
        if cid and c.get("cid") == cid:
            return k
    for k, c in b["candidates"].items():
        if _norm(k.split(" (")[0]) == _norm(name) and _same_tier(c["level"], level) and _same_place(c, name, parent, code, cid):
            if cid and not c.get("cid"):
                c["cid"] = cid
            if code and not c.get("country"):
                c["country"] = code
            return k
    key = name
    if key in b["candidates"]:
        key = f"{name} ({parent or code})"
    b["candidates"][key] = {"level": level, "parent": parent, "bbox": None, "scan_bbox": None, "prior": 1.0, "status": "open",
                            "note": why, "country": code, "cid": cid}
    return key


def _country_key(b: dict, m: dict) -> str | None:
    """Existing country-level candidate for a region match (by pack code or any of the pack's names), if any."""
    for k, c in b["candidates"].items():
        if c["level"] != "country":
            continue
        if c.get("country") == m["country_code"]:
            return k
        p = regions.resolve(k.split(" (")[0])
        if p and p["code"] == m["country_code"]:
            c["country"] = m["country_code"]
            return k
    return None


def cmd_apply(args, p: Path) -> None:
    b = _load(p)
    cl = HERE / "clues.py"
    country = args.country or b.get("country")
    # The country context only narrows region-pack lookups. Global kinds read --country as an observation target
    # (driving-side --country X = "which side does X drive on"), so passing the context there would overwrite the value.
    is_global = args.kind in GLOBAL_KINDS
    cmd = [UV, "run", str(cl), "lookup", args.kind, args.value, "--json"] + (["--country", country] if country and not is_global else [])
    r = _run(cmd)
    if r.returncode != 0:
        sys.exit(f"clues.py failed: {(r.stderr or r.stdout).strip()[-400:]}")
    try:
        d = json.loads(r.stdout[r.stdout.index("{"):])
    except Exception:  # noqa: BLE001
        sys.exit(f"clues.py output isn't JSON: {r.stdout[:300]}")
    matches = d.get("matches") or []
    kid = args.clue
    if not kid:
        kid = f"K{len(b['clues']) + 1}"
        b["clues"][kid] = {"text": f"{args.kind} {args.value}", "kind": args.kind, "status": "read",
                           "file": args.file or "", "source": d.get("source", ""), "used": False}
    if not matches:
        what = "Lookup not supported" if d.get("status") == "unsupported" else "Lookup returned nothing"
        print(f"{what}: {d.get('note', '')}. Clue {kid} recorded, no evidence added.")
        _save(p, b)
        return
    lr = args.lr
    touched: dict[tuple[str, str], None] = {}
    why = f"lookup {args.kind}={args.value}"

    def hit(lv: str, cname: str) -> None:
        lv = b["candidates"][cname]["level"]   # an existing candidate keeps its level (children may have recorded a prefecture as district)
        if (lv, cname) in touched:   # one piece of evidence per place, however many table rows name it
            return
        touched[(lv, cname)] = None
        b["evidence"].append({"id": f"E{len(b['evidence']) + 1}", "clue": kid, "candidate": cname, "lr": lr,
                              "why": why, "file": args.file or "", "cmd": f"clues.py lookup {args.kind} {args.value}"})

    for m in matches:
        code = m.get("country_code")
        if not code:   # global tables: country level only
            if m.get("country"):
                hit("country", _ensure(b, "country", m["country"], None, None, None, f"from lookup {args.kind}"))
            continue
        ck = _country_key(b, m)
        if ck:   # only when countries are already being compared; a single-country board isn't given a country row
            hit("country", ck)
        parent = None
        for lv in ("admin1", "admin2", "city", "district"):
            name = m.get(lv)
            if not name:
                continue
            hit(lv, _ensure(b, lv, name, parent, code, regions.cid(code, m, upto=lv), f"from lookup {args.kind}"))
            parent = name
    # Finest place each match names: candidates inside it (a district of a pointed-to city) aren't "elsewhere"
    leaves = {_norm(next((m[lv] for lv in ("district", "city", "admin2", "admin1", "country") if m.get(lv)), "")) for m in matches}
    # Other non-excluded candidates at the same level: against, but not excluded (lookups have exceptions too: out-of-town vehicles,
    # headquarters phone numbers). Only candidates the lookup could have pointed to: a country whose pack has no such table
    # (or isn't installed) was never consulted, so "not pointed to" says nothing about it.
    searched = set(d.get("searched") or [])
    ctx = (regions.resolve(country) or {}).get("code") if country else None

    def covered(k: str, c: dict) -> bool:
        if is_global:
            return True
        code = c.get("country")
        if c["level"] == "country":
            # A country row is its own country: the context mustn't stand in for one we can't identify (India with no pack)
            code = code or (regions.resolve(k.split(" (")[0]) or {}).get("code")
            return code in searched
        if code or ctx:
            return (code or ctx) in searched
        # Hand-added candidate of unknown country: covered if a searched pack's admin table knows the name
        return any(pk["code"] in searched for pk, _ in regions.admin_find(k.split(" (")[0]))

    for lv in {lv for lv, _ in touched}:
        for k, c in b["candidates"].items():
            if c["level"] == lv and (lv, k) not in touched and c.get("status") != "excluded" and _norm(c.get("parent") or "") not in leaves \
                    and covered(k, c):
                b["evidence"].append({"id": f"E{len(b['evidence']) + 1}", "clue": kid, "candidate": k, "lr": 1 / lr,
                                      "why": f"lookup {args.kind}={args.value} doesn't point here", "file": "", "cmd": ""})
    b["clues"][kid]["used"] = True
    _log(b, f"apply {args.kind}={args.value} → {[n for _, n in touched]}")
    _save(p, b)
    countries = sorted({m.get("country_code") for m in matches if m.get("country_code")})
    print(f"{kid}: {args.kind}={args.value} → {', '.join(n for _, n in sorted(touched))} (likelihood ratio {lr:g}; others at the same level 1/{lr:g}, not excluded)"
          + (f"\n  Matches in several countries ({', '.join(countries)}): all kept as hypotheses. If the country is known, `board.py country <cc>` and re-apply." if len(countries) > 1 else ""))
    if d.get("note") and len(countries) <= 1:
        print(f"  Note: {d['note'][:300]}")


def cmd_log(args, p: Path) -> None:
    b = _load(p)
    print("\n".join(b.get("log", [])[-args.n:]))
    print(f"\n{len(b['clues'])} clues, {len(b['evidence'])} pieces of evidence, {len(b['candidates'])} candidates")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--board", type=Path, default=Path("board.json"))
    sub = ap.add_subparsers(dest="cmd", required=True)

    def rank_opts(sp):
        sp.add_argument("--prior-by", choices=["none", "area"], default="none", help="prior: uniform (default) or by bbox area. There is no by-population option")
        sp.add_argument("--zoom", type=int, default=16, help="scan pages are computed at this zoom (sports field overview z16, factories z16, buildings z17)")
        sp.add_argument("--cell", type=int, default=320)
        sp.add_argument("--cols", type=int, default=5)

    i = sub.add_parser("init")
    i.add_argument("--photo", required=True)
    i.add_argument("--case")
    i.add_argument("--force", action="store_true")
    i.add_argument("--country", help="country context when it's already known (code or name): region-pack lookups use only that pack")

    co = sub.add_parser("country", help="set the country context (code or name; 'none' clears it)")
    co.add_argument("code")

    a = sub.add_parser("add")
    a.add_argument("names", nargs="*")
    a.add_argument("--from", dest="from_", help="bulk import: JSON from poi.py --out / gazetteer.py --out, or GeoJSON from osm.py geom")
    a.add_argument("--radius", type=float, default=500, help="when --from has only point coordinates, the candidate extent is this many meters around the point (default 500)")
    a.add_argument("--level", required=True, help=f"{'/'.join(LEVELS)}")
    a.add_argument("--parent")
    a.add_argument("--bbox", help="s,w,n,e")
    a.add_argument("--prior", type=float, default=1.0)
    a.add_argument("--note")

    ch = sub.add_parser("children", help="list every subordinate admin area with gazetteer.py and add them as candidates")
    ch.add_argument("parent")
    ch.add_argument("--level", type=int, help="OSM admin_level (automatic if omitted)")
    ch.add_argument("--within")
    ch.add_argument("--as-level", help=f"level to record the candidates as: {'/'.join(LEVELS)}. Automatic if omitted: parent is a country → admin1, "
                                        "parent already on the candidate board → its next level, otherwise district")
    ch.add_argument("--proxy", default=os.environ.get("GEO_PROXY"), help=PROXY_HELP)

    c = sub.add_parser("clue")
    c.add_argument("text")
    c.add_argument("--kind", required=True, help="plate/area-code/text/livery/terrain/sun/infra/vegetation/network/municipal/ip/hint/…; infrastructure is an alias for infra")
    c.add_argument("--status", required=True, help="/".join(STATUS))
    c.add_argument("--file", help="zoomed image, script output")
    c.add_argument("--source", help="where in the image, who said it")
    c.add_argument("--resolves", action="append", metavar="CLUE_ID",
                   help="earlier clue actually tested by this computed result; repeatable, requires --status computed and an existing --file")

    e = sub.add_parser("evidence")
    e.add_argument("--clue", required=True)
    e.add_argument("--for", dest="for_", action="append", help="name:likelihood_ratio (>1), repeatable; name alone defaults to 3")
    e.add_argument("--against", action="append", help="name:likelihood_ratio (<1), repeatable; name alone defaults to 1/3")
    e.add_argument("--why")
    e.add_argument("--file")
    e.add_argument("--command", dest="command_", help="the command that produced this evidence")

    x = sub.add_parser("exclude")
    x.add_argument("name")
    x.add_argument("--clue", required=True)
    x.add_argument("--computed", required=True, help="computed file (must exist)")
    x.add_argument("--covers", help="where the evidence actually covers: 'lat,lon' or 'lat,lon:lat,lon'; required for district/area/road candidates")
    x.add_argument("--why")

    sb = sub.add_parser("scan-bbox")
    sb.add_argument("name")
    sb.add_argument("--bbox", required=True)

    u = sub.add_parser("urban")
    u.add_argument("name")
    u.add_argument("--within")
    u.add_argument("--proxy", default=os.environ.get("GEO_PROXY"), help=PROXY_HELP)

    f = sub.add_parser("falsify")
    f.add_argument("name")
    f.add_argument("--text", required=True)

    r = sub.add_parser("rank")
    rank_opts(r)
    r.add_argument("--limit", type=int, default=15)

    n = sub.add_parser("next")
    rank_opts(n)

    k = sub.add_parser("check")
    rank_opts(k)
    k.add_argument("--evidence", help="evidence image path (default: evidence.jpg next to board.json)")

    rp = sub.add_parser("report")
    rank_opts(rp)
    rp.add_argument("--merge", help="merge into an existing result.json")

    ap_ = sub.add_parser("apply", help="lookup clues add candidates and evidence automatically (clues.py)")
    ap_.add_argument("--kind", required=True, help="calling-code/driving-side/territories, or a region-pack kind (plate, area-code, …: `regions.py list`)")
    ap_.add_argument("--country", help="restrict region-pack lookups to this country (default: the board's country, else every pack)")
    ap_.add_argument("--value", required=True)
    ap_.add_argument("--clue", help="id of an already recorded clue; if omitted, a new read clue is created")
    ap_.add_argument("--file", help="zoomed image the text was read from")
    ap_.add_argument("--lr", type=float, default=20.0)

    mv = sub.add_parser("move", help="put a candidate under another candidate (e.g. a point under its road); evidence stays with it")
    mv.add_argument("name")
    mv.add_argument("--parent", required=True)

    lg = sub.add_parser("log")
    lg.add_argument("-n", type=int, default=40)

    args = ap.parse_args()
    p = args.board
    fn = {"init": cmd_init, "add": cmd_add, "children": cmd_children, "clue": cmd_clue, "evidence": cmd_evidence,
          "exclude": cmd_exclude, "scan-bbox": cmd_scan_bbox, "urban": cmd_urban, "falsify": cmd_falsify,
          "rank": cmd_rank, "next": cmd_next, "check": cmd_check, "report": cmd_report, "apply": cmd_apply, "log": cmd_log,
          "country": cmd_country, "move": cmd_move}
    fn[args.cmd](args, p)


if __name__ == "__main__":
    # Chinese Windows outputs GBK by default: it crashes on m², ñ, and Chinese text the agent reads comes out garbled
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    main()
