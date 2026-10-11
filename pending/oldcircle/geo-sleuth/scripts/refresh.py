#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Maintainer tool: re-fetch the bundled lookup tables from their sources and rewrite them in the shared formats.

Global tables go to data/; the China pack's tables go to regions/cn/data/ in the prefix-table and admin-table formats (regions/README.md).
Lookups never call this; they read the JSON only. Contributed packs ship their data with `_meta.source` and don't need a parser here.

  refresh.py [table|all]       tables: calling_codes driving_side territories cn/admin cn/plates cn/area_codes
  refresh.py all --from-dir D  parse already-downloaded source files instead of fetching (names in LOCAL_NAMES)

cn/plates and cn/area_codes resolve place names against cn/admin, so refresh cn/admin first (all does).
"""
from __future__ import annotations

import argparse
from _net import curl_args, PROXY_HELP
import html as H
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
CN = HERE.parent / "regions" / "cn" / "data"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

SOURCES = {
    "calling_codes": ["https://en.wikipedia.org/wiki/List_of_telephone_country_codes"],
    "driving_side": ["https://en.wikipedia.org/wiki/Left-_and_right-hand_traffic"],
    "territories": ["https://en.wikipedia.org/wiki/List_of_dependent_territories"],
    "cn/admin": ["https://raw.githubusercontent.com/modood/Administrative-divisions-of-China/master/dist/pca-code.json"],
    "cn/plates": ["https://zh.wikipedia.org/zh-cn/中华人民共和国民用机动车号牌"],
    "cn/area_codes": ["https://zh.wikipedia.org/zh-cn/中国大陆固定电话号码"],
}
LOCAL_NAMES = {"cn/plates": "plates_zh.html", "cn/area_codes": "areacodes2_zh.html", "calling_codes": "calling_en.html",
               "driving_side": "driving_en.html", "territories": "dependent_en.html", "cn/admin": "pca-code.json"}
LICENSE = {"cn/admin": "WTFPL (modood/Administrative-divisions-of-China)"}
WIKI_LICENSE = "Derived from Wikipedia, CC BY-SA 4.0"

# Letter splits inside municipalities: source is common knowledge of the former prefecture divisions; the Wikipedia page only goes down to “重庆市” (Chongqing). Marked unverified; verify before use.
MUNICIPAL_LETTER_NOTES = {
    "渝": {"A": "main urban districts", "B": "main urban districts", "C": "永川、江津、合川、璧山、铜梁、大足、荣昌、潼南 (former 永川 prefecture)", "D": "main urban districts (added later)",
          "F": "万州、开州、梁平、忠县、云阳、奉节、巫山、巫溪、城口 (former 万县 prefecture)", "G": "涪陵、南川、垫江、丰都、武隆 (former 涪陵 prefecture)",
          "H": "黔江、石柱、秀山、酉阳、彭水 (former 黔江 prefecture)"},
}

# Wikipedia's “List of dependent territories” leaves out overseas territories integrated into the home country (French overseas departments, Spain's Canaries, US Hawaii…), but they are exactly the intersection that “IP country × hinted continent” is looking for, so they are added here.
# Sources: Wikipedia Overseas France / Outermost regions of the EU / per-country articles; region/subregion follow the UN geoscheme.
INTEGRAL_OVERSEAS = [
    {"name": "French Guiana", "sovereign": "France", "region": "Americas", "subregion": "South America", "status": "Overseas department and region (integral part of France, EU)"},
    {"name": "Guadeloupe", "sovereign": "France", "region": "Americas", "subregion": "Caribbean", "status": "Overseas department and region"},
    {"name": "Martinique", "sovereign": "France", "region": "Americas", "subregion": "Caribbean", "status": "Overseas department and region"},
    {"name": "Réunion", "sovereign": "France", "region": "Africa", "subregion": "Eastern Africa", "status": "Overseas department and region"},
    {"name": "Mayotte", "sovereign": "France", "region": "Africa", "subregion": "Eastern Africa", "status": "Overseas department and region"},
    {"name": "Saint Martin", "sovereign": "France", "region": "Americas", "subregion": "Caribbean", "status": "Overseas collectivity"},
    {"name": "Saint Barthélemy", "sovereign": "France", "region": "Americas", "subregion": "Caribbean", "status": "Overseas collectivity"},
    {"name": "Saint Pierre and Miquelon", "sovereign": "France", "region": "Americas", "subregion": "Northern America", "status": "Overseas collectivity"},
    {"name": "French Polynesia", "sovereign": "France", "region": "Oceania", "subregion": "Polynesia", "status": "Overseas collectivity"},
    {"name": "New Caledonia", "sovereign": "France", "region": "Oceania", "subregion": "Melanesia", "status": "Sui generis collectivity"},
    {"name": "Wallis and Futuna", "sovereign": "France", "region": "Oceania", "subregion": "Polynesia", "status": "Overseas collectivity"},
    {"name": "Canary Islands", "sovereign": "Spain", "region": "Africa", "subregion": "Northern Africa (Atlantic)", "status": "Autonomous community (integral part of Spain)"},
    {"name": "Ceuta", "sovereign": "Spain", "region": "Africa", "subregion": "Northern Africa", "status": "Autonomous city (integral part of Spain)"},
    {"name": "Melilla", "sovereign": "Spain", "region": "Africa", "subregion": "Northern Africa", "status": "Autonomous city (integral part of Spain)"},
    {"name": "Azores", "sovereign": "Portugal", "region": "Europe", "subregion": "Southern Europe (Atlantic)", "status": "Autonomous region (integral part of Portugal)"},
    {"name": "Madeira", "sovereign": "Portugal", "region": "Europe", "subregion": "Southern Europe (Atlantic, off Africa)", "status": "Autonomous region (integral part of Portugal)"},
    {"name": "Hawaii", "sovereign": "United States", "region": "Oceania", "subregion": "Polynesia", "status": "State (integral part of the US)"},
    {"name": "Alaska", "sovereign": "United States", "region": "Americas", "subregion": "Northern America", "status": "State (integral part of the US)"},
    {"name": "Bonaire", "sovereign": "Netherlands", "region": "Americas", "subregion": "Caribbean", "status": "Special municipality (integral part of the Netherlands)"},
    {"name": "Sint Eustatius", "sovereign": "Netherlands", "region": "Americas", "subregion": "Caribbean", "status": "Special municipality"},
    {"name": "Saba", "sovereign": "Netherlands", "region": "Americas", "subregion": "Caribbean", "status": "Special municipality"},
    {"name": "Svalbard", "sovereign": "Norway", "region": "Europe", "subregion": "Northern Europe (Arctic)", "status": "Unincorporated area (integral part of Norway)"},
    {"name": "Easter Island", "sovereign": "Chile", "region": "Oceania", "subregion": "Polynesia", "status": "Special territory (integral part of Chile)"},
    {"name": "Galápagos Islands", "sovereign": "Ecuador", "region": "Americas", "subregion": "South America (Pacific)", "status": "Province (integral part of Ecuador)"},
    {"name": "Andaman and Nicobar Islands", "sovereign": "India", "region": "Asia", "subregion": "Southern Asia (Bay of Bengal)", "status": "Union territory (integral part of India)"},
    {"name": "Kaliningrad Oblast", "sovereign": "Russia", "region": "Europe", "subregion": "Eastern Europe (exclave on the Baltic)", "status": "Oblast (integral part of Russia)"},
    {"name": "Okinawa", "sovereign": "Japan", "region": "Asia", "subregion": "Eastern Asia", "status": "Prefecture (integral part of Japan)"},
]

# ---------------------------------------------------------------- HTML table parsing (handles rowspan/colspan)

def _clean(c: str) -> str:
    c = re.sub(r"<sup[^>]*>.*?</sup>", "", c, flags=re.S)
    c = re.sub(r"<br\s*/?>", " | ", c)
    c = H.unescape(re.sub(r"<[^>]+>", "", c))
    c = re.sub(r"\[[^\]]*\]", "", c)
    return re.sub(r"\s+", " ", c).strip()


def _tables(html: str) -> list[list[list[str]]]:
    out = []
    for t in re.findall(r"<table[^>]*>(.*?)</table>", html, re.S):
        rows, pending = [], {}
        for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", t, re.S):
            cells = re.findall(r"<t([dh])([^>]*)>(.*?)</t[dh]>", tr, re.S)
            row, col, k = [], 0, 0
            while k < len(cells) or col in pending:
                if col in pending:
                    text, left = pending[col]
                    row.append(text)
                    if left <= 1:
                        del pending[col]
                    else:
                        pending[col] = (text, left - 1)
                    col += 1
                    continue
                _, attrs, body = cells[k]
                k += 1
                text = _clean(body)
                rs = re.search(r'rowspan="?(\d+)', attrs)
                cs = re.search(r'colspan="?(\d+)', attrs)
                n = int(cs.group(1)) if cs else 1
                for _ in range(n):
                    row.append(text)
                    if rs and int(rs.group(1)) > 1:
                        pending[col] = (text, int(rs.group(1)) - 1)
                    col += 1
            rows.append(row)
        out.append(rows)
    return out


def _sections_h3(html: str) -> list[tuple[str, str]]:
    parts = re.split(r"<h3[^>]*>", html)
    secs = []
    for part in parts[1:]:
        if "</h3>" not in part:
            continue
        title, body = part.split("</h3>", 1)
        secs.append((_clean(title), body.split("<h2", 1)[0]))
    return secs


# ---------------------------------------------------------------- per-table parsers

def parse_cn_plates(html: str) -> dict:
    out = {}
    for title, body in _sections_h3(html):
        m = re.match(r"^(.+?)（(.)）$", title)
        if not m:
            continue
        prov, abbr = m.group(1), m.group(2)
        letters = {}
        for li in re.findall(r"<li[^>]*>(.*?)</li>", body, re.S):
            text = _clean(li)
            text = re.split(r"[。；;]", text)[0]
            text = re.sub(r"^(参见：.*?)(?=[A-Z](?:[/、，,]|\s))", "", text)
            text = re.sub(r"^(汽车|小型汽车|大型汽车)\s*", "", text)
            if "摩托车" in text or "拖拉机" in text:
                continue
            mm = re.match(r"^([A-Z](?:\s*[/、，,–\-~～至]\s*[A-Z])*)\s*[：:]?\s*(.+)$", text)
            if not mm:
                continue
            place = mm.group(2).strip()
            spec = mm.group(1)
            Ls: list[str] = []
            for seg in re.split(r"[/、，,]", spec):
                seg = seg.strip()
                r = re.match(r"^([A-Z])\s*[–\-~～至]\s*([A-Z])$", seg)
                if r:
                    Ls += [chr(c) for c in range(ord(r.group(1)), ord(r.group(2)) + 1) if chr(c) not in "IO"]
                elif seg:
                    Ls.append(seg)
            for L in Ls:
                letters[L] = place
        if letters:
            out[abbr] = {"province": prov, "letters": letters}
    for abbr, notes in MUNICIPAL_LETTER_NOTES.items():
        if abbr in out:
            out[abbr]["letter_notes_unverified"] = notes
    return out


def parse_cn_area_codes(html: str) -> dict:
    out = {}
    for t in _tables(html):
        if not t or not t[0] or t[0][0] != "区号":
            continue
        for row in t[1:]:
            if len(row) < 3 or not re.match(r"^\d{2,4}$", row[0]):
                continue
            code = "0" + row[0]
            entry = {"admin1": row[1], "admin2": [x.strip() for x in row[2].split("|") if x.strip()],
                     "digits": row[3] if len(row) > 3 else "", "note": row[4] if len(row) > 4 else ""}
            # "/" in the digits column marks a retired code; the note alone isn't enough (023's note tells the history of 811 being retired)
            if entry["digits"] == "/":
                entry["deprecated"] = True
            out[code] = entry
    return out


def parse_calling_codes(html: str) -> dict:
    out = {}
    for t in _tables(html):
        if len(t) < 50 or not t[0] or t[0][0] != "Serving":
            continue
        for row in t[1:]:
            if len(row) < 2 or not re.match(r"^\d", row[1]):
                continue
            country = row[0]
            m = re.match(r"^(\d+)\s*(?:\(([^)]*)\))?", row[1])
            if not m:
                continue
            code = m.group(1)
            subs = [s.strip() for s in (m.group(2) or "").split(",") if s.strip()]
            keys = [f"{code}-{s}" for s in subs] or [code]
            for k in keys:
                out.setdefault(k, []).append({"country": country, "utc": row[2] if len(row) > 2 else ""})
    return out


DRIVING_SUPPLEMENT = {  # regions without their own row in the Wikipedia table (source: each region's article, common knowledge)
    "Hong Kong": ("left", "kept from British rule, opposite to the mainland"), "Macau": ("left", "kept from Portuguese rule, opposite to the mainland"), "Taiwan": ("right", ""),
    "French Guiana": ("right", "French overseas department"), "Guadeloupe": ("right", "French overseas department"), "Martinique": ("right", "French overseas department"),
    "Réunion": ("right", "French overseas department"), "Mayotte": ("right", "French overseas department"), "New Caledonia": ("right", "French territory"), "French Polynesia": ("right", "French territory"),
    "Puerto Rico": ("right", "US territory"), "Guam": ("right", "US territory"), "U.S. Virgin Islands": ("left", "US territory, a rare left-hand one"),
    "American Samoa": ("right", "US territory"), "Northern Mariana Islands": ("right", "US territory"),
    "Greenland": ("right", "Denmark"), "Faroe Islands": ("right", "Denmark"), "Aruba": ("right", "Netherlands"), "Curaçao": ("right", "Netherlands"), "Sint Maarten": ("right", "Netherlands"),
    "Gibraltar": ("right", "British territory, a rare right-hand one"), "Bermuda": ("left", "British territory"), "Cayman Islands": ("left", "British territory"),
    "British Virgin Islands": ("left", "British territory"), "Anguilla": ("left", "British territory"), "Montserrat": ("left", "British territory"),
    "Turks and Caicos Islands": ("left", "British territory"), "Falkland Islands": ("left", "British territory"), "Saint Helena": ("left", "British territory"),
    "Isle of Man": ("left", "British Crown Dependency"), "Jersey": ("left", "British Crown Dependency"), "Guernsey": ("left", "British Crown Dependency"),
    "Cook Islands": ("left", "New Zealand associated state"), "Niue": ("left", "New Zealand associated state"), "Tokelau": ("left", "New Zealand territory"),
    "Canary Islands": ("right", "Spain"), "Azores": ("right", "Portugal"), "Madeira": ("right", "Portugal"), "Svalbard": ("right", "Norway"),
}


def parse_driving_side(html: str) -> dict:
    """The table's "Country" header spans two columns: sovereign state, then a sub-unit for states listed in parts
    (China → Mainland / Hong Kong / Macau). Keying every row by the first column let the last sub-row overwrite the
    country (China came out as LHT with Macau's note), so sub-rows are resolved explicitly."""
    out: dict = {}
    groups: dict[str, list[tuple[str, dict]]] = {}
    for t in _tables(html):
        if len(t) < 100 or not t[0] or t[0][0] != "Country":
            continue
        for row in t[1:]:
            if len(row) < 2:
                continue
            idx = next((i for i, c in enumerate(row) if re.match(r"^(LHT|RHT)", c.upper())), None)
            if idx is None:
                continue
            e = {"side": "left" if row[idx].upper().startswith("LHT") else "right",
                 "switched": row[idx + 1] if len(row) > idx + 1 else "", "note": row[idx + 2] if len(row) > idx + 2 else ""}
            if idx >= 2 and row[1] != row[0]:
                groups.setdefault(re.sub(r" and overseas territories$", "", row[0]), []).append((row[1], e))
            else:
                out[row[0]] = e
    for parent, subs in groups.items():
        main = [e for sub, e in subs if sub == "Mainland" or sub.endswith(" proper") or sub.startswith("Contiguous")]
        if main:
            out[parent] = main[0]
        elif len({e["side"] for _, e in subs}) == 1:
            # Listed by province/state, all the same side (Canada): the country takes that side, provinces aren't countries
            out[parent] = dict(subs[0][1], note="; ".join(f"{sub}: {e['note']}" for sub, e in subs if e["note"]))
            continue
        for sub, e in subs:
            if e in main:
                continue
            out[sub] = dict(e, part_of=parent, note="; ".join(x for x in (f"part of {parent}", e["note"]) if x))
    for k, (side, note) in DRIVING_SUPPLEMENT.items():
        if k not in out:
            out[k] = {"side": side, "switched": "", "note": note, "curated": True}
    return out


def parse_territories(html: str) -> dict:
    items = []
    for t in _tables(html):
        if not t or not t[0] or t[0][0] != "Name" or "Sovereign state" not in t[0]:
            continue
        hi = {h: i for i, h in enumerate(t[0])}
        for row in t[1:]:
            if len(row) < len(t[0]) - 1:
                continue
            items.append({"name": row[hi["Name"]], "sovereign": row[hi["Sovereign state"]], "region": row[hi["UN region"]],
                          "subregion": row[hi["UN subregion"]], "status": row[hi.get("Legal status", len(row) - 1)],
                          "population": row[hi.get("Population (2016)", 1)], "area_km2": row[hi.get("Area (km)", 2)]})
    names = {it["name"].lower() for it in items}
    for it in INTEGRAL_OVERSEAS:
        if it["name"].lower() not in names:
            items.append(dict(it, population="", area_km2="", curated=True))
    by_sov: dict = {}
    for it in items:
        by_sov.setdefault(it["sovereign"], []).append(it)
    return {"by_sovereign": by_sov, "count": len(items),
            "note": "Wikipedia's “List of dependent territories” excludes overseas territories integrated into the home country, such as French overseas departments; INTEGRAL_OVERSEAS adds them (curated=true)"}


def parse_cn_admin(raw: str) -> dict:
    nodes = json.loads(raw)
    items = []

    def walk(ns, parent, level):
        for n in ns:
            name, code = n.get("name", ""), n.get("code", "")
            ch = n.get("children") or []
            if level == 2 and name in ("市辖区", "县", "省直辖县级行政区划", "自治区直辖县级行政区划", "市"):
                walk(ch, parent, 3)      # dummy level for municipalities / province-administered units: attach children directly to the province
                continue
            items.append({"name": name, "code": code, "level": level, "parent": parent})
            walk(ch, name, level + 1)

    walk(nodes, "", 1)
    return {"items": items}



# ---------------------------------------------------------------- China pack: raw tables → shared formats

CN_ADMIN_LEVELS = {1: "admin1", 2: "admin2", 3: "district"}   # must match regions/cn/region.json admin_levels


class _CNAdmin:
    def __init__(self, items: list[dict]):
        self.items = items
        self.by: dict[str, list[dict]] = {}
        for it in items:
            self.by.setdefault(it["name"], []).append(it)

    def chain(self, it: dict) -> list[dict]:
        out, cur = [it], it
        while cur.get("parent"):
            nxt = self.by.get(cur["parent"])
            if not nxt:
                break
            cur = nxt[0]
            out.append(cur)
        return list(reversed(out))

    def under(self, prov: str, name: str) -> dict | None:
        """The one item called name (or name without its 市/区/县 suffix) inside province prov."""
        cands = self.by.get(name) or [it for n, its in self.by.items() if n.rstrip("市区县") == name.rstrip("市区县") for it in its]
        cands = [it for it in cands if prov in [c["name"] for c in self.chain(it)]]
        return cands[0] if len(cands) == 1 else None

    def match(self, it: dict) -> dict:
        return {CN_ADMIN_LEVELS[c["level"]]: c["name"] for c in self.chain(it)}


def _cn_places(adm: _CNAdmin, prov: str, place: str) -> list[dict]:
    """Free-text place from a Wikipedia table cell → matches. Unresolvable text (vehicle classes, "直辖市全境", historic areas)
    stays at province level with the text as the note, instead of becoming a fake place."""
    place = place.strip()
    if place == prov or place.rstrip("市") == prov.rstrip("市"):
        return [{"admin1": prov}]
    m = re.match(r"^(.+?)（(.+)）$", place)
    head, inner = (m.group(1), m.group(2)) if m else (place, "")
    it = adm.under(prov, head)
    if not it:
        return [{"admin1": prov, "note": place}]
    if inner:
        subs = [x.strip() for x in re.split(r"[、，,]", inner) if x.strip()]
        kids = [adm.under(prov, x) for x in subs]
        if subs and all(kids) and not re.search(r"不含|部分|地级|地区", inner):
            return [adm.match(k) for k in kids]
        return [dict(adm.match(it), note=inner)]
    return [adm.match(it)]


def cn_plates_table(raw: dict, adm: _CNAdmin) -> dict:
    entries: dict[str, list[dict]] = {}
    for abbr, v in raw.items():
        prov = v["province"]
        entries[abbr] = [{"admin1": prov, "note": "province abbreviation only"}]
        unv = v.get("letter_notes_unverified") or {}
        for letter, place in v["letters"].items():
            rows = []
            for p in re.split(r"[、，,/]", place):
                if not p.strip():
                    continue
                for r in _cn_places(adm, prov, p):
                    if set(r) <= {"admin1", "note"} and not r.get("note") and letter in unv:
                        r.update(note=f"whole municipality; district split from common knowledge: {unv[letter]}", unverified=True)
                    elif set(r) <= {"admin1", "note"} and not r.get("note"):
                        r["note"] = "whole municipality" if prov.endswith("市") else "whole province"
                    rows.append(r)
            entries[abbr + letter] = _dedup(rows)
    return entries


def cn_area_codes_table(raw: dict, adm: _CNAdmin) -> dict:
    entries: dict[str, list[dict]] = {}
    for code, e in raw.items():
        note = ("deprecated; " if e.get("deprecated") else "") + (e.get("note") or "")
        rows = []
        for a in e["admin2"] or [e["admin1"]]:
            for r in _cn_places(adm, e["admin1"], a):
                r["note"] = "; ".join(x for x in (r.get("note", ""), note) if x)
                if e.get("digits"):
                    r["digits"] = e["digits"]
                rows.append(r)
        entries[code] = _dedup(rows)
    return entries


def _dedup(rows: list[dict]) -> list[dict]:
    """One match per place: rows naming the same place (several vehicle classes under one letter) merge, notes joined."""
    out: dict[str, dict] = {}
    for r in rows:
        k = json.dumps({lv: r[lv] for lv in ("admin1", "admin2", "district") if r.get(lv)}, ensure_ascii=False, sort_keys=True)
        if k not in out:
            out[k] = dict(r)
            continue
        notes = [x for x in out[k].get("note", "").split("; ") if x]
        notes += [x for x in r.get("note", "").split("; ") if x and x not in notes]
        out[k]["note"] = "; ".join(notes)
    return list(out.values())


PLATE_META = {"kind": "plate", "normalize": {"strip": " ·-", "upper": True},
              "key_pattern": "^[\\u4e00-\\u9fff][A-Z]?",
              "usage": "first Han character (province) + issuing letter, e.g. <abbr><letter>; the rest of the plate is ignored",
              "note": "Municipality letter splits come from common knowledge, marked unverified; Hong Kong/Macau/Taiwan, military and police plates are not in the table.",
              "miss_note": "province abbreviation not in the table"}
AREA_META = {"kind": "area-code", "normalize": {"digits_only": True, "ensure_prefix": "0"},
             "usage": "landline area code; accepts 0817, 0817-1234567, (0817) 123. 010/02X are 3 digits, the rest 4",
             "miss_note": "not a mainland China landline area code (mobile number, 400/800, foreign number)"}


# ---------------------------------------------------------------- fetch / write

def _fetch(url: str, proxy: str | None) -> str:
    cmd = ["curl", "-q", "-s", "-m", "90", "-A", UA, "-L"]
    cmd += curl_args(proxy)
    r = subprocess.run(cmd + [url], capture_output=True)
    if r.returncode != 0 or len(r.stdout) < 1000:
        sys.exit(f"fetch failed: {url} (check service availability with doctor.py --network)")
    return r.stdout.decode("utf-8", "replace")


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{path.relative_to(HERE.parent)}: {payload['_meta'].get('count')} entries ({path.stat().st_size // 1024} KB)")


def refresh(name: str, raw: str) -> None:
    today = date.today().isoformat()
    meta = {"source": SOURCES[name], "fetched": today, "license": LICENSE.get(name, WIKI_LICENSE)}
    if name in ("calling_codes", "driving_side", "territories"):
        data = {"calling_codes": parse_calling_codes, "driving_side": parse_driving_side, "territories": parse_territories}[name](raw)
        _write(DATA / f"{name}.json", {"_meta": dict(meta, count=data.get("count") or len(data)), **data})
    elif name == "cn/admin":
        data = parse_cn_admin(raw)
        _write(CN / "admin.json", {"_meta": dict(meta, count=len(data["items"])), **data})
    else:
        adm = _CNAdmin(json.loads((CN / "admin.json").read_text(encoding="utf-8"))["items"])
        if name == "cn/plates":
            entries, extra = cn_plates_table(parse_cn_plates(raw), adm), PLATE_META
        else:
            entries, extra = cn_area_codes_table(parse_cn_area_codes(raw), adm), AREA_META
        _write(CN / f"{name.split('/')[1]}.json", {"_meta": dict(extra, **meta, count=len(entries)), "entries": entries})


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("table", nargs="?", default="all", help=f"all or one of {', '.join(SOURCES)}")
    ap.add_argument("--proxy", default=os.environ.get("GEO_PROXY"), help=PROXY_HELP)
    ap.add_argument("--from-dir", type=Path, help="directory of already-downloaded source files (for development)")
    args = ap.parse_args()
    names = list(SOURCES) if args.table == "all" else [args.table]
    for name in names:
        if name not in SOURCES:
            sys.exit(f"unknown table {name}; one of {', '.join(SOURCES)}")
        raw = (args.from_dir / LOCAL_NAMES[name]).read_text(encoding="utf-8", errors="replace") if args.from_dir else _fetch(SOURCES[name][0], args.proxy)
        refresh(name, raw)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    main()
