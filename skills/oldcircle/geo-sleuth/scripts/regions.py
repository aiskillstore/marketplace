#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Region packs: country-specific clues, lookup tables and service preferences, kept out of the core.

A pack is a folder regions/<cc>/ (cc = ISO 3166-1 alpha-2, lower case) holding only data and documents:
  region.json   manifest: names, admin levels, lookup tables, preferred services, tips (format: regions/README.md)
  clues.md      clue entries in the shared entry format
  data/*.json   lookup tables in the shared prefix-table format
  tests.json    lookup cases: input → expected matches
Packs never contain code. The core scripts read the manifest; a lookup kind a pack doesn't declare is reported as unsupported, never answered from another country's table.

  list              installed packs: code, name, status, lookups, clue entries
  show <cc>         one pack's card: lookups, services, tips, and a one-line index of its clue entries with line numbers
  lint [cc ...]     check packs against the contract (manifest, sources, entry fields, no code, tests); exit 1 on errors

Extra pack folders (private packs, tests) can be added with GEO_SLEUTH_REGIONS=<dir>[:<dir>...]; a pack there overrides a bundled pack with the same code.

Examples:
  regions.py list
  regions.py show cn
  regions.py lint
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "regions"
BOARD_LEVELS = ["country", "admin1", "admin2", "city", "district", "area", "road", "point"]
MATCH_LEVELS = ["admin1", "admin2", "city", "district"]   # levels a lookup match may name
STATUSES = ("maintained", "community", "stub")
ENTRY_FIELDS = ("Look for", "Points to", "Strength", "Counterexamples", "Sources")
ALLOWED_SUFFIXES = {".json", ".md"}
MERGED = re.compile(r"/|、|;")   # "Ghaziabad / Noida" is two places, not one ("and"/"&" stay legal: Jammu and Kashmir is one)

_CACHE: dict | None = None


# ---------------------------------------------------------------- loading

def _dirs() -> list[Path]:
    extra = [Path(p) for p in os.environ.get("GEO_SLEUTH_REGIONS", "").split(os.pathsep) if p.strip()]
    return [ROOT, *extra]


def packs(reload: bool = False) -> dict[str, dict]:
    """{code: manifest + {"dir": Path}} for every installed pack (folders starting with _ are templates, skipped)."""
    global _CACHE
    if _CACHE is not None and not reload:
        return _CACHE
    out: dict[str, dict] = {}
    for base in _dirs():
        if not base.is_dir():
            continue
        for d in sorted(base.iterdir()):
            f = d / "region.json"
            if d.name.startswith(("_", ".")) or not f.is_file():
                continue
            try:
                m = json.loads(f.read_text(encoding="utf-8"))
            except ValueError:
                continue
            m["dir"] = d
            out[str(m.get("code", d.name)).upper()] = m
    _CACHE = out
    return out


def _fold(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "").strip().lower()
    return re.sub(r"[\s.()\-_'’]", "", s)


def resolve(country: str | None) -> dict | None:
    """Country code / name / alias → pack, or None when no installed pack matches."""
    if not country:
        return None
    key = _fold(country)
    for code, m in packs().items():
        if key == code.lower() or key in {_fold(n) for n in [m.get("name", ""), *m.get("names", [])]}:
            return m
    return None


_TABLES: dict[Path, dict] = {}


def load_table(pack: dict, rel: str) -> dict:
    f = pack["dir"] / rel
    if f not in _TABLES:
        _TABLES[f] = json.loads(f.read_text(encoding="utf-8"))
    return _TABLES[f]


# ---------------------------------------------------------------- prefix-table lookups

def normalize(value: str, spec: dict) -> str:
    v = unicodedata.normalize("NFKC", value or "") if spec.get("fullwidth", True) else (value or "")
    for ch in spec.get("strip", " "):
        v = v.replace(ch, "")
    if spec.get("digits_only"):
        v = re.sub(r"\D", "", v)
    if spec.get("upper", True):
        v = v.upper()
    pre = spec.get("ensure_prefix")
    if pre and v and not v.startswith(pre):
        v = pre + v
    return v


def prefix_lookup(pack: dict, kind: str, value: str) -> dict:
    """Look a value up in one pack's prefix table.
    Returns {"status": ok|no_match|not_applicable|unsupported, "matches": [...], "note", "source", "fetched"}.
    not_applicable = the value doesn't have this table's format (e.g. a Latin plate against a table of Han-character prefixes)."""
    spec = (pack.get("lookups") or {}).get(kind)
    if not spec:
        return {"status": "unsupported", "matches": [], "note": f"{pack['code']} pack has no {kind} table", "source": "", "fetched": ""}
    t = load_table(pack, spec["file"])
    if not isinstance(t, dict) or not isinstance(t.get("entries", {}), dict):
        raise ValueError(f"{spec['file']} must be an object with an 'entries' object")
    meta = t.get("_meta", {})
    src = ", ".join(meta.get("source") or []) if isinstance(meta.get("source"), list) else str(meta.get("source", ""))
    base = {"source": src, "fetched": meta.get("fetched", "")}
    v = normalize(value, meta.get("normalize") or {})
    target = v
    if meta.get("key_pattern"):
        m = re.match(meta["key_pattern"], v)
        if not m:
            return {"status": "not_applicable", "matches": [], "note": "", **base}
        target = m.group(0)
    entries = t.get("entries") or {}
    key = next((target[:n] for n in range(len(target), 0, -1) if target[:n] in entries), None)
    if key is None:
        return {"status": "no_match", "matches": [], "note": meta.get("miss_note", "not in the table"), **base}
    note = ""
    if meta.get("key_pattern") and key != target:
        note = f"only '{key}' matched; '{target[len(key):]}' is not in the table (new series, or table out of date)"
    matches = []
    for e in entries[key]:
        row = {"country": pack.get("name", pack["code"]), "country_code": pack["code"], "key": key}
        row.update(e)
        if note:
            row["note"] = "; ".join(x for x in (note, row.get("note", "")) if x)
        matches.append(row)
    return {"status": "ok", "matches": matches, "note": "", **base}


PACK_ERRORS = (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError, re.error)


def safe_lookup(pack: dict, kind: str, value: str) -> dict:
    """prefix_lookup that turns a broken pack (missing or malformed table) into status "error" instead of an exception."""
    try:
        return prefix_lookup(pack, kind, value)
    except PACK_ERRORS as exc:
        return {"status": "error", "matches": [], "source": "", "fetched": "",
                "note": f"{pack['code']} pack is broken ({type(exc).__name__}: {exc}); run `regions.py lint {pack['code'].lower()}`"}


def lookup(kind: str, value: str, country: str | None = None) -> dict:
    """Prefix lookup across packs. With a country: only that pack (unsupported if it isn't installed or lacks the table).
    Without: every pack that declares the kind; matches from several countries are all returned."""
    if country:
        p = resolve(country)
        if not p:
            have = ", ".join(sorted(packs())) or "none"
            return {"status": "unsupported", "matches": [], "searched": [],
                    "note": f"no region pack for '{country}' (installed: {have}); use global tools, or contribute a pack (regions/README.md)"}
        r = safe_lookup(p, kind, value)
        r["searched"] = [] if r["status"] == "error" else [p["code"]]
        if r["status"] == "unsupported":
            r["note"] += f" (its lookups: {', '.join(p.get('lookups') or {}) or 'none'})"
        return r
    searched, matches, notes, sources, fetched = [], [], [], [], []
    for code, p in packs().items():
        if kind not in (p.get("lookups") or {}):
            continue
        r = safe_lookup(p, kind, value)
        if r["status"] == "not_applicable":
            continue
        if r["status"] == "error":   # one broken pack mustn't take down the other countries' answers
            notes.append(r["note"])
            continue
        searched.append(code)
        matches += r["matches"]
        if r["status"] == "no_match":
            notes.append(f"{code}: {r['note']}")
        if r["source"]:
            sources.append(r["source"])
            fetched.append(f"{code} {r['fetched']}")
    if not searched:
        return {"status": "unsupported", "matches": [], "searched": [],
                "note": "; ".join([f"no installed pack has a {kind} table in this format", *notes]),
                "source": "", "fetched": ""}
    note = "; ".join(notes)
    if len({m["country_code"] for m in matches}) > 1:
        note = "; ".join(x for x in ("matches in several countries: keep each as a hypothesis, or pass --country", note) if x)
    return {"status": "ok" if matches else "no_match", "matches": matches, "searched": searched, "note": note,
            "source": " | ".join(sources), "fetched": ", ".join(fetched)}


# ---------------------------------------------------------------- admin tables

def admin_items(pack: dict) -> list[dict]:
    rel = pack.get("admin_table")
    if not rel or not (pack["dir"] / rel).is_file():
        return []
    try:
        items = load_table(pack, rel).get("items") or []
        if not all(isinstance(it, dict) and "name" in it for it in items):
            raise ValueError(f"{rel}: items must be objects with a name")
        return items
    except PACK_ERRORS:   # broken table: treated as absent here; doctor.py and lint report it
        return []


def level_name(pack: dict, admin_level) -> str:
    return (pack.get("admin_levels") or {}).get(str(admin_level), "district")


def strip_suffix(name: str, pack: dict) -> str:
    """Name without one of the pack's generic suffixes (CN: 市/省/区/县), for matching names across sources."""
    out = name or ""
    for s in pack.get("name_suffixes") or []:
        if out.endswith(s) and len(out) > len(s):
            return out[: -len(s)]
    return out


_INDEX: dict[str, tuple[list[dict], dict]] = {}


def admin_index(pack: dict) -> tuple[list[dict], dict]:
    key = str(pack["dir"])
    if key not in _INDEX:
        items = admin_items(pack)
        by: dict[str, list[dict]] = {}
        for it in items:
            by.setdefault(it["name"], []).append(it)
        _INDEX[key] = (items, by)
    return _INDEX[key]


def admin_chain(pack: dict, item: dict) -> list[str]:
    _, by = admin_index(pack)
    chain, p = [item["name"]], item.get("parent", "")
    while p:
        chain.append(p)
        nxt = by.get(p)
        p = nxt[0].get("parent", "") if nxt else ""
    return list(reversed(chain))


def admin_find(name: str, country: str | None = None) -> list[tuple[dict, dict]]:
    """Exact name first, then a match ignoring the pack's generic suffixes (市/省/区/县 in CN). [(pack, item)]"""
    pk = [resolve(country)] if country else list(packs().values())
    out = []
    for p in pk:
        if not p:
            continue
        items, by = admin_index(p)
        hits = by.get(name) or [it for it in items if strip_suffix(it["name"], p) == strip_suffix(name, p)]
        out += [(p, it) for it in hits]
    return out


def admin_children(name: str, country: str | None = None) -> tuple[dict | None, list[dict]]:
    """Direct children of an admin area in the local tables. (pack, items); (None, []) when no pack knows the parent."""
    hits = admin_find(name, country)
    if not hits:
        return None, []
    p, parent = hits[0]
    kids = [it for it in admin_items(p) if it.get("parent") == parent["name"]]
    return p, kids


def match_from_item(pack: dict, item: dict) -> dict:
    """Admin-table item → match dict with explicit board levels along its chain."""
    _, by = admin_index(pack)
    row = {"country": pack.get("name", pack["code"]), "country_code": pack["code"]}
    for nm in admin_chain(pack, item):
        lv = by[nm][0]["level"] if nm in by else None
        if lv is not None:
            row[level_name(pack, lv)] = nm
    return row


def cid(code: str, match: dict, upto: str | None = None) -> str:
    """Stable candidate id: country code + names along the levels the match states, e.g. CN/广东省/深圳市."""
    parts = [code]
    for lv in MATCH_LEVELS:
        if match.get(lv):
            parts.append(match[lv])
        if lv == upto:
            break
    return "/".join(parts)


# ---------------------------------------------------------------- clue index (for show)

def clue_index(path: Path) -> list[tuple[int, str, str]]:
    """[(line number, '##'/'###', text)] — entries get 'title — points to (strength)'."""
    out: list[tuple[int, str, str]] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, s in enumerate(lines, 1):
        if s.startswith("## "):
            out.append((i, "##", s[3:].strip()))
        elif s.startswith("### "):
            title, points, strength = s[4:].strip(), "", ""
            for t in lines[i: i + 12]:
                if t.startswith("### ") or t.startswith("## "):
                    break
                if t.startswith("- Points to:"):
                    points = t.split(":", 1)[1].strip()
                elif t.startswith("- Strength:"):
                    strength = t.split(":", 1)[1].strip().split(" ")[0].strip(",;")
            short = points if len(points) <= 70 else points[:68].rsplit(" ", 1)[0] + "…"
            out.append((i, "###", f"{title} — {short}" + (f" ({strength})" if strength else "")))
    return out


# ---------------------------------------------------------------- lint

def lint(pack: dict) -> tuple[list[str], list[str]]:
    errs, warns = [], []
    d: Path = pack["dir"]
    code = str(pack.get("code", ""))
    if not re.fullmatch(r"[A-Z]{2}", code):
        errs.append(f"code '{code}' must be an ISO 3166-1 alpha-2 code in upper case")
    if d.name != code.lower():
        errs.append(f"folder name '{d.name}' must be the lower-case code '{code.lower()}'")
    for k in ("name", "names", "status", "docs"):
        if not pack.get(k):
            errs.append(f"region.json: '{k}' is required")
    if pack.get("status") and pack["status"] not in STATUSES:
        errs.append(f"region.json: status must be one of {STATUSES}")
    for f in d.rglob("*"):
        if f.is_file() and f.suffix.lower() not in ALLOWED_SUFFIXES:
            errs.append(f"{f.relative_to(d)}: packs hold data and documents only (.json/.md); code goes into core scripts through a separate PR")
    for rel in pack.get("docs") or []:
        f = d / rel
        if not f.is_file():
            errs.append(f"docs: {rel} not found")
            continue
        _lint_entries(f, rel, errs, warns)
    levels = set((pack.get("admin_levels") or {}).values())
    bad_lv = levels - set(MATCH_LEVELS)
    if bad_lv:
        errs.append(f"admin_levels: {sorted(bad_lv)} are not board levels {MATCH_LEVELS}")
    checks = [lambda: _lint_admin(pack, errs)] if pack.get("admin_table") else []
    checks += [lambda k=k, v=v: _lint_table(pack, k, v, errs, warns) for k, v in (pack.get("lookups") or {}).items()]
    checks.append(lambda: _lint_tests(pack, errs))
    for check in checks:   # a malformed file is an error to report, not a crash
        try:
            check()
        except PACK_ERRORS as exc:
            errs.append(f"malformed data ({type(exc).__name__}: {exc})")
    for svc in ("street_view",):
        v = (pack.get("services") or {}).get(svc)
        if v and not (Path(__file__).parent / v).is_file():
            errs.append(f"services.{svc}: {v} is not a core script")
    return errs, warns


def _lint_entries(f: Path, rel: str, errs: list, warns: list) -> None:
    lines = f.read_text(encoding="utf-8").splitlines()
    if len(lines) > 400:
        warns.append(f"{rel}: {len(lines)} lines; split by topic into several docs (each listed in region.json docs)")
    if not rel.startswith("clues"):
        return
    starts = [i for i, s in enumerate(lines) if s.startswith("### ")]
    for n, i in enumerate(starts):
        end = next((j for j in range(i + 1, len(lines)) if lines[j].startswith(("### ", "## "))), len(lines))
        body = lines[i + 1: end]
        missing = [k for k in ENTRY_FIELDS if not any(s.startswith(f"- {k}:") for s in body)]
        if missing:
            errs.append(f"{rel}:{i + 1} '{lines[i][4:].strip()}' lacks {', '.join(missing)}")


def _lint_table(pack: dict, kind: str, spec: dict, errs: list, warns: list) -> None:
    f = pack["dir"] / spec.get("file", "")
    if not f.is_file():
        errs.append(f"lookups.{kind}: {spec.get('file')} not found")
        return
    try:
        t = json.loads(f.read_text(encoding="utf-8"))
    except ValueError as exc:
        errs.append(f"{spec['file']}: invalid JSON ({exc})")
        return
    if not isinstance(t, dict):
        errs.append(f"{spec['file']}: must be an object with '_meta' and 'entries'")
        return
    meta, entries = t.get("_meta") or {}, t.get("entries")
    for k in ("source", "fetched", "license"):
        if not meta.get(k):
            errs.append(f"{spec['file']}: _meta.{k} is required (where the data comes from, when, under which license)")
    if meta.get("fetched") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(meta["fetched"])):
        errs.append(f"{spec['file']}: _meta.fetched must be YYYY-MM-DD")
    if meta.get("key_pattern"):
        try:
            re.compile(meta["key_pattern"])
        except re.error as exc:
            errs.append(f"{spec['file']}: key_pattern doesn't compile ({exc})")
    if not isinstance(entries, dict) or not entries:
        errs.append(f"{spec['file']}: 'entries' must be a non-empty object of key → [match, ...]")
        return
    if meta.get("count") is not None and meta["count"] != len(entries):
        errs.append(f"{spec['file']}: _meta.count {meta['count']} != {len(entries)} entries")
    if f.stat().st_size > 8 * 1024 * 1024:
        warns.append(f"{spec['file']}: over 8 MB")
    for key, rows in entries.items():
        if not isinstance(rows, list) or not rows:
            errs.append(f"{spec['file']}: '{key}' must map to a non-empty list (several places → several matches, never one merged name)")
            continue
        for r in rows:
            if not isinstance(r, dict) or not any(r.get(lv) for lv in MATCH_LEVELS):
                errs.append(f"{spec['file']}: '{key}' has a match without any of {MATCH_LEVELS}")
                break
            merged = [r[lv] for lv in MATCH_LEVELS if r.get(lv) and MERGED.search(str(r[lv]))]
            if merged:
                errs.append(f"{spec['file']}: '{key}' names {merged}; list each place as its own match")
                break
            extra = [k for k in r if k in BOARD_LEVELS and k not in MATCH_LEVELS]
            if extra:
                errs.append(f"{spec['file']}: '{key}' uses {extra}; a match names admin levels only")
                break


def _lint_admin(pack: dict, errs: list) -> None:
    rel = pack["admin_table"]
    f = pack["dir"] / rel
    if not f.is_file():
        errs.append(f"admin_table: {rel} not found")
        return
    t = json.loads(f.read_text(encoding="utf-8"))
    meta = t.get("_meta") or {}
    for k in ("source", "fetched", "license"):
        if not meta.get(k):
            errs.append(f"{rel}: _meta.{k} is required")
    items = t.get("items") or []
    names = {it.get("name") for it in items}
    lv = {str(it.get("level")) for it in items}
    unknown = lv - set((pack.get("admin_levels") or {}).keys())
    if unknown:
        errs.append(f"{rel}: levels {sorted(unknown)} have no entry in admin_levels")
    orphans = [it["name"] for it in items if it.get("parent") and it["parent"] not in names]
    if orphans:
        errs.append(f"{rel}: {len(orphans)} items name a parent that isn't in the table (e.g. {orphans[:3]})")


def _lint_tests(pack: dict, errs: list) -> None:
    f = pack["dir"] / "tests.json"
    kinds = set(pack.get("lookups") or {})
    if not kinds:
        return
    if not f.is_file():
        errs.append("tests.json is required when the pack has lookups (at least one case per lookup kind)")
        return
    cases = json.loads(f.read_text(encoding="utf-8"))
    seen = set()
    for c in cases:
        seen.add(c.get("kind"))
        r = prefix_lookup(pack, c["kind"], c["value"])
        got = sorted(json.dumps({k: m[k] for k in MATCH_LEVELS if m.get(k)}, ensure_ascii=False, sort_keys=True) for m in r["matches"])
        want = sorted(json.dumps({k: m[k] for k in MATCH_LEVELS if m.get(k)}, ensure_ascii=False, sort_keys=True) for m in c.get("expect", []))
        if got != want:
            errs.append(f"tests.json: {c['kind']} {c['value']} → {got}, expected {want}")
    for k in sorted(kinds - seen):
        errs.append(f"tests.json: no case for lookup kind '{k}'")


# ---------------------------------------------------------------- CLI

def _count_entries(p: dict) -> int:
    n = 0
    for rel in p.get("docs") or []:
        f = p["dir"] / rel
        if f.is_file():
            n += sum(1 for s in f.read_text(encoding="utf-8").splitlines() if s.startswith("### "))
    return n


def cmd_list(_args) -> None:
    ps = packs()
    if not ps:
        print("No region packs installed.")
        return
    for code, p in sorted(ps.items()):
        lk = ", ".join(p.get("lookups") or {}) or "-"
        print(f"{code.lower()}  {p.get('name', '')} [{p.get('status', '?')}]  lookups: {lk}  clue entries: {_count_entries(p)}")
    print("\n`regions.py show <cc>` for one pack's card and clue index. No pack for a country = global tools and references only.")


def cmd_show(args) -> None:
    p = resolve(args.code)
    if not p:
        sys.exit(f"No pack for '{args.code}' (installed: {', '.join(sorted(packs())) or 'none'}). Use global tools; references/clues/global.md has cross-country clues.")
    d: Path = p["dir"]
    rel_dir = d.relative_to(ROOT.parent) if d.is_relative_to(ROOT.parent) else d
    print(f"# {p['code']} {p.get('name', '')} [{p.get('status', '?')}]  ({rel_dir}/)")
    if p.get("admin_levels"):
        names = p.get("level_names") or {}
        print("Admin levels: " + ", ".join(f"{k}={v}" + (f" ({names[v]})" if names.get(v) else "") for k, v in p["admin_levels"].items()))
    for kind, spec in (p.get("lookups") or {}).items():
        t = load_table(p, spec["file"])
        meta = t.get("_meta", {})
        print(f"Lookup {kind}: {len(t.get('entries') or {})} keys, fetched {meta.get('fetched', '?')} → `clues.py lookup {kind} <value> --country {p['code'].lower()}`"
              + (f"  {meta['usage']}" if meta.get("usage") else ""))
    if p.get("admin_table"):
        print(f"Admin table: {len(admin_items(p))} areas (used by `board.py children` and `clues.py lookup admin`)")
    for k, v in (p.get("services") or {}).items():
        print(f"Service {k}: {v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)}")
    for k, v in (p.get("tips") or {}).items():
        print(f"Tip {k}: {v}")
    for rel in p.get("docs") or []:
        f = d / rel
        if not f.is_file():
            continue
        print(f"\n## {rel_dir}/{rel} — read only the entries you need (line numbers below)")
        for ln, kind, text in clue_index(f):
            print(f"  {ln:>4}  {text}" if kind == "###" else f"  {ln:>4}  [{text}]")


def cmd_lint(args) -> None:
    ps = packs()
    codes = [c.upper() for c in args.codes] or sorted(ps)
    bad = 0
    for code in codes:
        if code not in ps:
            print(f"{code}: not installed")
            bad += 1
            continue
        errs, warns = lint(ps[code])
        for w in warns:
            print(f"{code} WARN {w}")
        for e in errs:
            print(f"{code} ERROR {e}")
        bad += bool(errs)
        if not errs:
            print(f"{code}: ok" + (f" ({len(warns)} warnings)" if warns else ""))
    sys.exit(1 if bad else 0)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    s = sub.add_parser("show")
    s.add_argument("code")
    li = sub.add_parser("lint")
    li.add_argument("codes", nargs="*")
    args = ap.parse_args()
    {"list": cmd_list, "show": cmd_show, "lint": cmd_lint}[args.cmd](args)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    main()
