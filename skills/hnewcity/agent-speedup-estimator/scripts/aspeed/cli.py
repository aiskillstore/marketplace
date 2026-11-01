from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from . import __version__
from .adapters import claude_code, codex
from .analyze import AgentAgg, aggregate, category_table, merge
from .estimate import DISK_SPEED, disk_ratio, project_all, validate_sensitivity
from .hardware import detect
from .i18n import CAT, dur, strings
from .report_html import render_html
from .report_md import render_md
from .scores import estimate_from_specs, filter_catalog, find_cpu, load_catalog, load_json, resolve_baseline
from .textio import UnsupportedCompression


def detect_lang() -> str:
    for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        if os.environ.get(var, "").lower().startswith("zh"):
            return "zh"
    if sys.platform == "win32":
        try:
            import ctypes

            if ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0xFF == 0x04:
                return "zh"
        except Exception:
            pass
    return "en"


def parse_args(argv: Optional[List[str]]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="agent_speedup",
        description="Estimate how much faster your coding agents would run on a faster computer, from local Claude Code and Codex transcripts.",
    )
    p.add_argument("--agents", default="claude,codex", help="comma list: claude,codex")
    p.add_argument("--claude-dir", help="folder with Claude Code project transcripts (default ~/.claude/projects)")
    p.add_argument("--codex-dir", help="folder searched recursively for Codex rollout-*.jsonl (default ~/.codex/sessions)")
    p.add_argument("--days", type=float, help="only count activity from the last N days")
    p.add_argument("--target", action="append", default=[], help="CPU name from the score table; repeatable")
    p.add_argument("--custom-target", action="append", nargs=3, default=[], metavar=("NAME", "SINGLE", "MULTI"), help="a CPU not in the table, with its Geekbench 6 scores")
    p.add_argument("--current-cpu", help="override the detected CPU name")
    p.add_argument("--current-gb6", nargs=2, type=int, metavar=("SINGLE", "MULTI"), help="Geekbench 6 scores of this computer, if known; otherwise a table match, stand-in or estimate is used")
    p.add_argument("--current-disk", choices=sorted(DISK_SPEED), help="override the detected disk class")
    p.add_argument("--target-disk", choices=sorted(DISK_SPEED), default="nvme")
    p.add_argument("--cap", type=float, default=300.0, help="seconds of one command treated as hardware-sensitive before the rest counts as waiting")
    p.add_argument("--max-stall", type=float, default=300.0, help="gaps longer than this inside a working turn are stalls, not model time")
    p.add_argument("--max-human", type=float, default=1800.0, help="gaps longer than this between turns are idle, not your reply time")
    p.add_argument("--sensitivity", help="JSON file replacing data/sensitivity.json")
    p.add_argument("--lang", choices=["auto", "en", "zh"], default="auto")
    p.add_argument("--out", default="agent-speedup-report", help="output folder for report.md, report.html, summary.json")
    p.add_argument("--no-html", action="store_true")
    p.add_argument("--json", action="store_true", help="print the JSON result instead of the Markdown summary")
    p.add_argument("--list-cpus", action="store_true")
    p.add_argument("--search", default="", help="search CPU and Mac inventory; also filter default comparisons")
    p.add_argument("--vendor", choices=["Intel", "AMD", "Apple"], default="")
    p.add_argument("--platform", choices=["desktop", "laptop", "workstation", "server", "embedded", "handheld", "apple-silicon"], default="")
    p.add_argument("--generation", default="", help="generation substring, e.g. 'Core 4th', 'Zen 4', 'M2'")
    p.add_argument("--scored-only", action="store_true", help="list only entries with paired Geekbench 6 scores")
    p.add_argument("--target-set", choices=["all", "tiers"], default="all", help="default: all scored CPUs; tiers selects the small curated comparison")
    args = p.parse_args(argv)
    for name in ("days", "cap", "max_stall", "max_human"):
        value = getattr(args, name)
        if value is not None and (not math.isfinite(value) or value < 0 or (name == "days" and value == 0)):
            p.error(f"--{name.replace('_', '-')} must be finite and {'positive' if name == 'days' else 'nonnegative'}")
    if args.current_gb6 and any(v <= 0 for v in args.current_gb6):
        p.error("--current-gb6 scores must be positive integers")
    for name, single, multi in args.custom_target:
        try:
            valid = int(single) > 0 and int(multi) > 0
        except ValueError:
            valid = False
        if not valid:
            p.error("--custom-target scores must be positive integers")
    agents = [a.strip() for a in args.agents.split(",")]
    if any(a not in ("claude", "codex") for a in agents):
        p.error("--agents must be a comma-separated list of claude,codex")
    args.agents = ",".join(dict.fromkeys(agents))
    return args


def agent_dict(agg: AgentAgg) -> dict:
    return {
        "sessions": agg.sessions,
        "model_s": round(agg.model_s, 1),
        "tool_s": round(agg.tool_s, 1),
        "human_s": round(agg.human_s, 1),
        "idle_s": round(agg.idle_s, 1),
        "background_s": round(agg.background_s, 1),
        "stalled_s": round(agg.stalled_s, 1),
        "categories": category_table(agg),
        "families": [[k, round(v, 1)] for k, v in agg.families.most_common(10)],
    }


def scan(name: str, args: argparse.Namespace, since: Optional[float]):
    skipped = 0
    packed = 0
    out = []
    if name == "claude":
        root = Path(args.claude_dir) if args.claude_dir else claude_code.default_root()
        for path in claude_code.find_sessions(root):
            try:
                s = claude_code.parse_session(path, since, args.max_stall, args.max_human)
            except OSError:
                skipped += 1
                continue
            if s:
                out.append(s)
    else:
        roots = [Path(args.codex_dir)] if args.codex_dir else codex.default_roots()
        for path in codex.find_sessions(roots):
            try:
                s = codex.parse_session(path, since, args.max_stall, args.max_human)
            except UnsupportedCompression:
                packed += 1
                continue
            except OSError:
                skipped += 1
                continue
            if s:
                out.append(s)
    return out, skipped, packed


def sensitive_expected_s(agg: AgentAgg, sens: dict) -> float:
    cats = sens["categories"]
    fb = cats["other_tool"]
    total = 0.0
    for name, c in agg.cats.items():
        p = cats.get(name, fb)
        total += c.base * (p["cpu"][1] + p["disk"][1])
    return total


def build_targets(args: argparse.Namespace, cpus: List[dict], lang: str):
    custom = strings(lang)["custom"]
    found = []
    for name in args.target:
        cpu = find_cpu(name, cpus)
        if cpu and cpu.get("gb6_single") and cpu.get("gb6_multi"):
            found.append((cpu, "custom", custom))
        else:
            reason = "has no paired Geekbench 6 scores" if cpu else "is unknown or needs a more specific configuration"
            raise ValueError(f"'{name}' {reason}. Use --list-cpus --search to inspect the inventory, or --custom-target NAME SINGLE MULTI with verified Geekbench 6 scores.")
    for name, single, multi in args.custom_target:
        try:
            found.append(({"name": name, "gb6_single": int(single), "gb6_multi": int(multi)}, "custom", custom))
        except ValueError:
            print(f"warning: scores for '{name}' must be whole numbers", file=sys.stderr)
    if found:
        return list({x[0]["name"]: x for x in found}.values()), 0
    if args.target_set == "all":
        selected = filter_catalog(cpus, args.search, args.vendor, args.platform, args.generation, True)
        selected.sort(key=lambda c: (-c["gb6_multi"], c["name"]))
        found = [(c, c.get("platforms", ["cpu"])[0], c.get("generation", custom)) for c in selected]
        if not found:
            raise ValueError("No scored CPUs match these filters. Use --list-cpus to inspect missing-score entries.")
        primary = next((i for i, c in enumerate(selected) if c["name"] == "Intel Core Ultra 7 255H"), 0)
        return found, primary
    tiers = load_json("tiers.json")
    primary = 0
    for t in tiers["tiers"]:
        for cname in t["cpus"]:
            cpu = find_cpu(cname, cpus)
            if cpu and cpu.get("gb6_single") and filter_catalog([cpu], args.search, args.vendor, args.platform, args.generation):
                if t["id"] == tiers.get("primary_tier") and primary == 0 and not any(x[1] == t["id"] for x in found):
                    primary = len(found)
                found.append((cpu, t["id"], t.get("label_" + lang) or t["label"]))
    if not found:
        raise ValueError("No scored CPUs match the selected tiers and filters.")
    return found, primary


def iso(ts: Optional[float]) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d") if ts else ""


def build_notes(r: dict, lang: str) -> List[str]:
    S = strings(lang)
    allv = r["agents"]["all"]
    notes = [S["model_note"], S["e2e_note"], S["prior_note"], S["arch_note"], S["approval_note"]]
    if r["baseline"]["source"] in ("proxy", "estimated"):
        notes.append(S["proxy_note"].format(note=r["baseline"]["note"]))
        notes.append(S["widen_note"].format(p=round((r["baseline"]["uncertainty"] - 1.0) * 100)))
    if r["settings"]["compressed_unread"]:
        notes.append(S["skipped_note"].format(n=r["settings"]["compressed_unread"]))
    working = allv["model_s"] + allv["tool_s"]
    if working < 3600:
        notes.append(S["little_data"].format(t=dur(working)))
    excess = sum(c["excess_seconds"] for c in allv["categories"])
    if allv["tool_s"] and excess / allv["tool_s"] > 0.05:
        notes.append(S["excess_note"].format(t=dur(excess)))
    other = next((c["seconds"] for c in allv["categories"] if c["category"] == "other_tool"), 0.0)
    if allv["tool_s"] and other / allv["tool_s"] > 0.15:
        notes.append(S["other_note"].format(p=100.0 * other / allv["tool_s"]))
    return notes


def main(argv: Optional[List[str]] = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    args = parse_args(argv)
    catalog = load_catalog()
    cpus = catalog["cpus"]
    if args.list_cpus:
        selected = filter_catalog(cpus, args.search, args.vendor, args.platform, args.generation, args.scored_only)
        if args.json:
            print(json.dumps({**catalog, "cpus": selected}, ensure_ascii=False, indent=2))
        else:
            for c in selected:
                score = f"GB6 {c['gb6_single']} / {c['gb6_multi']}" if c.get("gb6_single") else c["score_status"]
                print(f"{c['name']} | {c['generation']} | {', '.join(c['platforms'])} | {score}")
            print(f"\n{len(selected)} entries; {sum(bool(c.get('gb6_single')) for c in selected)} with paired Geekbench 6 reference scores.")
        return 0

    lang = detect_lang() if args.lang == "auto" else args.lang
    try:
        targets_in, primary = build_targets(args, cpus, lang)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    try:
        if args.sensitivity:
            with open(args.sensitivity, encoding="utf-8") as fh:
                sens = json.load(fh)
        else:
            sens = load_json("sensitivity.json")
        validate_sensitivity(sens)
    except (OSError, ValueError) as exc:
        print(f"Invalid sensitivity configuration: {exc}", file=sys.stderr)
        return 2
    agents = [a.strip() for a in args.agents.split(",") if a.strip() in ("claude", "codex")]
    since = time.time() - args.days * 86400 if args.days else None

    scanned: Dict[str, list] = {}
    skipped = 0
    packed = 0
    for name in agents:
        sessions, bad, packed_n = scan(name, args, since)
        skipped += bad
        packed += packed_n
        if sessions:
            scanned[name] = sessions
    if not scanned:
        if packed:
            print(f"{packed} compressed Codex sessions need Python 3.14+ or 'pip install zstandard' to be read.", file=sys.stderr)
        print("No Claude Code or Codex transcripts with timing data were found. Use --claude-dir / --codex-dir to point at them.", file=sys.stderr)
        return 2

    aggs = {name: aggregate(name, ss, args.cap) for name, ss in scanned.items()}
    total = merge(list(aggs.values()))

    hw = detect()
    if args.current_cpu:
        hw.cpu_name = args.current_cpu
    if args.current_disk:
        hw.disk_class = args.current_disk

    unc = 1.0
    if args.current_gb6:
        base = {"name": hw.cpu_name or "Current CPU", "gb6_single": args.current_gb6[0], "gb6_multi": args.current_gb6[1]}
        base_note, source = "measured by the user", "manual"
    else:
        found, source, base_note, unc = resolve_baseline(hw.cpu_name, lang)
        if found:
            base = {"name": found["name"], "gb6_single": found["gb6_single"], "gb6_multi": found["gb6_multi"]}
            if source == "proxy":
                base["name"] = strings(lang)["scored_as"].format(cpu=hw.cpu_name, proxy=found["name"])
                base["proxy"] = found["name"]
        else:
            est, base_note, unc = estimate_from_specs(hw.threads, lang)
            source = "estimated"
            base = {"name": strings(lang)["est_as"].format(cpu=hw.cpu_name or "?"), **est}

    s_disk = disk_ratio(hw.disk_class, args.target_disk)
    targets = []
    for cpu, tier_id, tier_label in targets_in:
        targets.append(
            {
                "name": cpu["name"],
                "id": cpu.get("id", cpu["name"]),
                "vendor": cpu.get("vendor", "Custom"),
                "generation": cpu.get("generation", "Custom"),
                "platforms": cpu.get("platforms", []),
                "source_url": cpu.get("source_url", ""),
                "score_status": cpu.get("score_status", "user-provided"),
                "score_note": cpu.get("score_note", ""),
                "benchmark": "Geekbench 6",
                "tier_id": tier_id,
                "tier": tier_label,
                "gb6_single": cpu["gb6_single"],
                "gb6_multi": cpu["gb6_multi"],
                "cpu_x_single": round(cpu["gb6_single"] / base["gb6_single"], 3),
                "cpu_x_multi": round(cpu["gb6_multi"] / base["gb6_multi"], 3),
                "scenarios": project_all(total, base, cpu, s_disk, sens, unc),
            }
        )

    r = {
        "version": __version__,
        "lang": lang,
        "period": {"first": iso(total.first_ts), "last": iso(total.last_ts), "days": round(((total.last_ts or 0) - (total.first_ts or 0)) / 86400, 1)},
        "hardware": hw.as_dict(),
        "baseline": {**base, "note": base_note, "source": source, "uncertainty": unc},
        "disk": {"current": hw.disk_class, "target": args.target_disk, "ratio": round(s_disk, 3)},
        "settings": {"cap_s": args.cap, "max_stall_s": args.max_stall, "max_human_s": args.max_human, "skipped_files": skipped, "compressed_unread": packed},
        "agents": {**{k: agent_dict(v) for k, v in aggs.items()}, "all": agent_dict(total)},
        "sensitive_expected_s": round(sensitive_expected_s(total, sens), 1),
        "targets": targets,
        "catalog": catalog,
        "primary": primary,
        "cat_names": CAT.get(lang, CAT["en"]),
    }
    r["notes"] = build_notes(r, lang)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    md = render_md(r, lang)
    (out / "report.md").write_text(md, encoding="utf-8")
    (out / "summary.json").write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "cpu-catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    written = [out / "report.md", out / "summary.json", out / "cpu-catalog.json"]
    if not args.no_html:
        (out / "report.html").write_text(render_html(r, lang), encoding="utf-8")
        written.append(out / "report.html")

    print(json.dumps(r, ensure_ascii=False, indent=2) if args.json else md)
    for w in written:
        print(f"wrote {w.resolve()}", file=sys.stderr)
    return 0
