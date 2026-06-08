#!/usr/bin/env python3
"""collect.py — parallel earnings-data collector for the longbridge-earnings skill.

Usage:
    python3 collect.py <SYMBOL> [--full]      # macOS / Linux
    python  collect.py <SYMBOL> [--full]      # Windows

Fetches all CLI data sources needed for an earnings summary card in ONE
parallel round (instead of ~10 sequential calls), trims the JSON, and prints
a compact digest (~3-4K tokens) to stdout. Raw responses are kept in the
output directory for the full-report path to reuse.

    lite  (default): snapshot, income statement (8Q), consensus, forecast-eps,
                     quote, calc-index, institution-rating, segments, news, kline
    --full extras  : balance sheet, cash flow, filing list, industry valuation,
                     peer compare, rating history

Pure standard library — no jq, no shell, works on Windows / macOS / Linux.
"""

import json
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

TIMEOUT = 60  # seconds per CLI call

# ── CLI plumbing ─────────────────────────────────────────────────────


def die(msg, code):
    print(msg, file=sys.stderr)
    sys.exit(code)


def fetch(out_dir, name, args):
    """Run one CLI call; save raw JSON to <name>.json or error to <name>.err."""
    try:
        proc = subprocess.run(
            ["longbridge", *args, "--format", "json"],
            capture_output=True, text=True, encoding="utf-8", timeout=TIMEOUT,
        )
        ok = proc.returncode == 0 and proc.stdout.strip()
    except (subprocess.TimeoutExpired, OSError) as e:
        (out_dir / f"{name}.err").write_text(str(e), encoding="utf-8")
        return
    if ok:
        (out_dir / f"{name}.json").write_text(proc.stdout, encoding="utf-8")
    else:
        err = (proc.stderr or proc.stdout or "empty response").strip()
        (out_dir / f"{name}.err").write_text(err, encoding="utf-8")


# ── Trimming helpers (jq replacements) ───────────────────────────────

_NUM_RE = re.compile(r"^-?[0-9]+\.[0-9]+$")


def slim(node):
    """Cut numeric-string precision: big numbers -> integers, ratios -> 2dp."""
    if isinstance(node, dict):
        return {k: slim(v) for k, v in node.items()}
    if isinstance(node, list):
        return [slim(v) for v in node]
    if isinstance(node, str) and _NUM_RE.match(node):
        n = float(node)
        if abs(n) > 1_000_000:
            return str(round(n))
        r = round(n * 100) / 100
        return str(int(r)) if r == int(r) else str(r)
    return node


def drop_empty(node):
    """Recursively drop "" / null object values (snapshot noise)."""
    if isinstance(node, dict):
        return {k: drop_empty(v) for k, v in node.items() if v not in ("", None)}
    if isinstance(node, list):
        return [drop_empty(v) for v in node]
    return node


def find_objects(node, key):
    """All dicts anywhere in the tree that contain `key` (jq `.. | objects`)."""
    found = []
    if isinstance(node, dict):
        if key in node:
            found.append(node)
        for v in node.values():
            found.extend(find_objects(v, key))
    elif isinstance(node, list):
        for v in node:
            found.extend(find_objects(v, key))
    return found


def pick(obj, *keys):
    return {k: obj.get(k) for k in keys if k in obj}


# ── Per-section trim filters ─────────────────────────────────────────


def trim_statement(data):  # is_qf / bs_qf / cf_qf
    out = []
    for kind in (data.get("list") or {}).values():
        for ind in kind.get("indicators") or []:
            out.append({
                "title": ind.get("title"),
                "accounts": [{
                    "name": a.get("name"), "field": a.get("field"),
                    "values": [pick(v, "period", "value", "yoy")
                               for v in (a.get("values") or [])[:8]],
                } for a in ind.get("accounts") or []],
            })
    return out


def trim_consensus(data):
    return {
        "currency": data.get("currency"),
        "current_period": data.get("current_period"),
        "periods": [{
            **pick(p, "fiscal_year", "fiscal_period", "period_text"),
            "details": [pick(d, "key", "name", "estimate", "actual", "comp")
                        for d in p.get("details") or []],
        } for p in (data.get("list") or [])[:6]],
    }


def trim_forecast_eps(data):
    return [{"mean": i.get("forecast_eps_mean"), "median": i.get("forecast_eps_median"),
             "high": i.get("forecast_eps_highest"), "low": i.get("forecast_eps_lowest")}
            for i in (data.get("items") or [])[-3:]]


def trim_news(data):
    return [pick(o, "id", "title", "published_at")
            for o in find_objects(data, "title")][:10]


def trim_kline(data):
    candles = find_objects(data, "close")
    highs = [float(c["high"]) for c in candles if c.get("high")]
    lows = [float(c["low"]) for c in candles if c.get("low")]
    return {
        "recent": [{"d": str(c.get("timestamp") or c.get("time") or c.get("date"))[:10],
                    "c": c.get("close")} for c in candles[-20:]],
        "high_250d": max(highs) if highs else None,
        "low_250d": min(lows) if lows else None,
    }


def trim_filings(data):
    out = []
    for o in find_objects(data, "title") + find_objects(data, "name"):
        out.append({"id": o.get("id"), "title": o.get("title") or o.get("name"),
                    "date": o.get("published_at") or o.get("date") or o.get("filed_at")})
    return out[:10]


def trim_compare(data):
    return [pick(p, "name", "counter_id", "price_close", "market_value", "pe", "pb",
                 "ps", "roe", "roa", "net_margin", "div_yld", "eps", "sales", "net_income")
            for p in data.get("list") or []]


# ── Digest output ────────────────────────────────────────────────────


def section(out_dir, title, name, trim=None):
    print(f"===== {title} =====")
    raw = out_dir / f"{name}.json"
    err = out_dir / f"{name}.err"
    if raw.exists():
        try:
            data = json.loads(raw.read_text(encoding="utf-8"))
            trimmed = slim(trim(data) if trim else data)
            print(json.dumps(trimmed, ensure_ascii=False, separators=(",", ":")))
        except (ValueError, KeyError, TypeError) as e:
            print(f"N/A (trim failed: {e}; raw: {raw})")
    elif err.exists():
        msg = err.read_text(encoding="utf-8")[:200].replace("\n", " ")
        print(f"N/A ({msg})")
    else:
        print("N/A (no data)")


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows cp936 etc.

    args = sys.argv[1:]
    full = "--full" in args
    args = [a for a in args if a != "--full"]
    if len(args) != 1:
        die("usage: collect.py <SYMBOL> [--full]", 2)
    symbol = args[0].strip()

    if not shutil.which("longbridge"):
        die("ERROR: longbridge CLI not found. See SKILL.md 'Fallbacks'.", 3)

    # HK symbols: leading zeros can cause empty results (09988.HK -> 9988.HK).
    if symbol.upper().endswith(".HK"):
        symbol = symbol.lstrip("0") if symbol.rstrip(".HKhk").strip("0") else symbol

    out_dir = Path(tempfile.gettempdir()) / f"lb_earnings_{symbol.lower().replace('.', '_')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    jobs = {
        "snapshot":     ["financial-report", "snapshot", symbol],
        "is_qf":        ["financial-report", symbol, "--kind", "IS", "--report", "qf"],
        "consensus":    ["consensus", symbol],
        "forecast_eps": ["forecast-eps", symbol],
        "quote":        ["quote", symbol],
        "calc_index":   ["calc-index", symbol],
        "rating":       ["institution-rating", symbol],
        "segments":     ["business-segments", symbol],
        "news":         ["news", symbol, "--count", "10"],
        "kline":        ["kline", symbol, "--period", "day", "--count", "250"],
    }
    if full:
        jobs.update({
            "bs_qf":      ["financial-report", symbol, "--kind", "BS", "--report", "qf"],
            "cf_qf":      ["financial-report", symbol, "--kind", "CF", "--report", "qf"],
            "filings":    ["filing", symbol, "--count", "10"],
            "ind_val":    ["industry-valuation", "dist", symbol],
            "compare":    ["compare", symbol],
            "rating_his": ["institution-rating", symbol, "--history"],
        })

    with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
        for name, cli_args in jobs.items():
            pool.submit(fetch, out_dir, name, cli_args)

    # Quarterly statement may be empty for semi-annual reporters: retry saf.
    is_file = out_dir / "is_qf.json"
    try:
        empty = not trim_statement(json.loads(is_file.read_text(encoding="utf-8")))
    except (OSError, ValueError):
        empty = True
    if empty:
        fetch(out_dir, "is_qf", ["financial-report", symbol, "--kind", "IS", "--report", "saf"])

    print(f"SYMBOL: {symbol}")
    print(f"COLLECTED_AT: {datetime.now(timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M %Z')}")
    print(f"RAW_DIR: {out_dir}  (full statements/filings live here — reuse, do not re-fetch)")

    section(out_dir, "SNAPSHOT (latest period)", "snapshot", drop_empty)
    section(out_dir, "INCOME_STATEMENT (last 8 quarters)", "is_qf", trim_statement)
    section(out_dir, "CONSENSUS (estimate vs actual, recent periods)", "consensus", trim_consensus)
    section(out_dir, "FORECAST_EPS (annual consensus range, latest 3 windows)", "forecast_eps", trim_forecast_eps)
    section(out_dir, "QUOTE", "quote")
    section(out_dir, "CALC_INDEX (PE/PB/mktcap)", "calc_index")
    section(out_dir, "INSTITUTION_RATING", "rating")
    section(out_dir, "SEGMENTS (revenue breakdown)", "segments")
    section(out_dir, "NEWS (latest 10 headlines)", "news", trim_news)
    section(out_dir, "KLINE (20 recent closes + 250d range)", "kline", trim_kline)

    if full:
        section(out_dir, "FILINGS (latest 10)", "filings", trim_filings)
        section(out_dir, "INDUSTRY_VALUATION (percentile dist)", "ind_val")
        section(out_dir, "PEER_COMPARE", "compare", trim_compare)
        print("===== FULL-MODE RAW FILES =====")
        print(f"BS/CF statements, rating history: {out_dir}" + "/{bs_qf,cf_qf,rating_his}.json")


if __name__ == "__main__":
    main()
