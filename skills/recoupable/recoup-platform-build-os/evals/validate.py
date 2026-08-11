#!/usr/bin/env python3
"""Static build-time checks for a workspace-os-generated workspace.

Report-only (like the doctor it imitates): it scores the *mechanical* subset of rubric.md and prints
a punch list. It never edits the workspace and always exits 0 — evidence, not a gate.

Usage:
    python3 validate.py /path/to/runs/<ts>/<domain>/workspace
    python3 validate.py /path/to/workspace --json   # machine-readable only
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

# Organs every OS must author (matched by folder-name suffix, since they're domain-prefixed).
ORGANS = ["intake", "doctor", "janitor", "learn", "reflect", "skillify"]
CORE_DIRS = ["knowledge", "library", "work", "artifacts", "plugin", "operations"]
PLACEHOLDERS = ["{DOMAIN}", "{PIPELINE}", "{ENTITY}", "{DOMAIN_SLUG}", "{DOMAIN_TITLE}", "{AUTHOR}"]


class Report:
    """Accumulates per-check results so the auto-subtotal is auditable line by line."""

    def __init__(self) -> None:
        self.checks: list[dict] = []

    def add(self, cid: str, got: float, mx: float, status: str, detail: str) -> None:
        self.checks.append(
            {"id": cid, "points": round(got, 2), "max": mx, "status": status, "detail": detail}
        )

    @property
    def subtotal(self) -> float:
        return round(sum(c["points"] for c in self.checks), 2)

    @property
    def maximum(self) -> float:
        return round(sum(c["max"] for c in self.checks), 2)


def read(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return ""


def frontmatter(text: str) -> dict[str, str]:
    """Pull the YAML-ish key: value pairs out of a SKILL.md front-matter block."""
    block = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not block:
        return {}
    fields: dict[str, str] = {}
    for line in block.group(1).splitlines():
        m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if m:
            fields[m.group(1)] = m.group(2).strip()
    return fields


def check_structure(ws: str, r: Report) -> None:
    present = [d for d in CORE_DIRS if os.path.isdir(os.path.join(ws, d))]
    missing = [d for d in CORE_DIRS if d not in present]
    pts = 3 * len(present) / len(CORE_DIRS)
    r.add(
        "core_dirs",
        pts,
        3,
        "PASS" if not missing else "FAIL",
        f"core dirs present {len(present)}/{len(CORE_DIRS)}" + (f"; missing {missing}" if missing else ""),
    )
    pipeline = glob.glob(os.path.join(ws, "*", "_board.md"))
    r.add(
        "pipeline_detected",
        2 if pipeline else 0,
        2,
        "PASS" if pipeline else "WARN",
        f"flowing pipeline (_board.md) at {os.path.basename(os.path.dirname(pipeline[0]))}/" if pipeline
        else "no _board.md found in any top-level folder",
    )


def check_naming(ws: str, r: Report) -> None:
    bad = []
    for entry in sorted(os.listdir(ws)):
        full = os.path.join(ws, entry)
        if entry.startswith(".") or not os.path.isdir(full):
            continue
        if not re.fullmatch(r"[a-z]+", entry):
            bad.append(entry)
    r.add(
        "naming_single_word",
        5 if not bad else max(0, 5 - len(bad)),
        5,
        "PASS" if not bad else "FAIL",
        "all top-level folders are single lowercase words" if not bad else f"non-conforming: {bad}",
    )


def check_brain(ws: str, r: Report) -> None:
    claude = read(os.path.join(ws, "CLAUDE.md"))
    got = 0.0
    notes = []
    if claude:
        got += 2
    else:
        notes.append("CLAUDE.md missing")
    left = [p for p in PLACEHOLDERS if p in claude]
    if claude and not left:
        got += 2
    elif left:
        notes.append(f"unfilled placeholders {left}")
    low = claude.lower()
    contracts = {
        "auto-manage loop": "auto-manage" in low or "auto manage" in low,
        "never-stale": "stale" in low,
        "compound-learning": "compound" in low,
        "filing tree": "filing" in low,
    }
    got += sum(1 for ok in contracts.values() if ok)
    missing_contracts = [k for k, ok in contracts.items() if not ok]
    if missing_contracts:
        notes.append(f"missing contracts {missing_contracts}")
    r.add("brain_claude", got, 8, "PASS" if got == 8 else ("WARN" if got >= 5 else "FAIL"),
          "; ".join(notes) or "CLAUDE.md complete")

    agents = os.path.join(ws, "AGENTS.md")
    if os.path.islink(agents):
        r.add("brain_agents", 4, 4, "PASS", "AGENTS.md is a symlink")
    elif os.path.isfile(agents):
        partial = "claude.md" in read(agents).lower()
        r.add("brain_agents", 2 if partial else 1, 4, "WARN",
              "AGENTS.md references CLAUDE.md (not a symlink)" if partial else "AGENTS.md present but doesn't point to CLAUDE.md")
    else:
        r.add("brain_agents", 0, 4, "FAIL", "AGENTS.md missing")

    dash = read(os.path.join(ws, "artifacts", "dashboard.html"))
    got = 0.0
    if "<html" in dash.lower():
        got += 2
    elif dash:
        notes = ["dashboard exists but isn't HTML"]
    if dash and not any(p in dash for p in PLACEHOLDERS):
        got += 2
    r.add("brain_dashboard", got, 4, "PASS" if got == 4 else ("WARN" if got else "FAIL"),
          "dashboard.html is HTML and customized" if got == 4 else "dashboard missing/placeholder/not-HTML")

    ops = 0
    for f in ("health.md", "improvements.md"):
        if os.path.isfile(os.path.join(ws, "operations", f)):
            ops += 2
    r.add("brain_operations", ops, 4, "PASS" if ops == 4 else "FAIL",
          f"operations seeded {ops//2}/2 files")


def skill_dirs(ws: str) -> list[str]:
    base = os.path.join(ws, "plugin", "skills")
    if not os.path.isdir(base):
        return []
    return [d for d in glob.glob(os.path.join(base, "*")) if os.path.isdir(d)]


def check_skills(ws: str, r: Report) -> None:
    dirs = skill_dirs(ws)
    names = [os.path.basename(d) for d in dirs]
    found = [o for o in ORGANS if any(n.endswith(o) for n in names)]
    organ_score = 8 * len(found) / len(ORGANS)
    domain_skill = any(not any(n.endswith(o) for o in ORGANS) for n in names)
    total = min(10, organ_score + (2 if domain_skill else 0))
    missing = [o for o in ORGANS if o not in found]
    r.add("skills_organs", total, 10, "PASS" if total >= 9 else ("WARN" if total >= 6 else "FAIL"),
          f"organs {len(found)}/6" + (f", missing {missing}" if missing else "") +
          (", +domain skill" if domain_skill else ", NO domain skill"))

    valid, problems = 0, []
    for d in dirs:
        name = os.path.basename(d)
        text = read(os.path.join(d, "SKILL.md"))
        if not text:
            problems.append(f"{name}: no SKILL.md")
            continue
        fm = frontmatter(text)
        ok = True
        if fm.get("name") != name:
            problems.append(f"{name}: frontmatter name != folder")
            ok = False
        if not fm.get("description"):
            problems.append(f"{name}: no description")
            ok = False
        elif "<" in fm["description"] or ">" in fm["description"]:
            problems.append(f"{name}: angle bracket in description")
            ok = False
        valid += ok
    sv = 6 * valid / len(dirs) if dirs else 0
    r.add("skills_valid", sv, 6, "PASS" if dirs and valid == len(dirs) else ("WARN" if valid else "FAIL"),
          f"valid SKILL.md {valid}/{len(dirs)}" + (f"; {problems}" if problems else ""))


def check_manifests(ws: str, r: Report) -> None:
    cpath = os.path.join(ws, "plugin", ".claude-plugin", "plugin.json")
    xpath = os.path.join(ws, "plugin", ".codex-plugin", "plugin.json")
    got, notes = 0.0, []
    claude = codex = None
    try:
        claude = json.loads(read(cpath))
        codex = json.loads(read(xpath))
        got += 2
    except (json.JSONDecodeError, ValueError):
        notes.append("a manifest is missing or invalid JSON")
    if claude and codex:
        cn, xn = claude.get("name", ""), codex.get("name", "")
        if cn and cn == xn and re.fullmatch(r"[a-z0-9-]+", cn):
            got += 2
        else:
            notes.append(f"name parity/kebab fail (claude={cn!r} codex={xn!r})")
        if codex.get("skills") == "./skills/":
            got += 2
        else:
            notes.append(f"codex skills path is {codex.get('skills')!r}, want './skills/'")
    r.add("manifests", got, 6, "PASS" if got == 6 else ("WARN" if got else "FAIL"),
          "; ".join(notes) or f"manifests valid + parity (name={claude.get('name')!r})")


def check_adapter(ws: str, r: Report) -> None:
    adapter = os.path.join(ws, ".agents", "skills")
    if os.path.islink(adapter):
        target = os.path.realpath(adapter)
        ok = target.endswith(os.path.join("plugin", "skills"))
        r.add("adapter", 4 if ok else 3, 4, "PASS" if ok else "WARN",
              f".agents/skills -> {os.readlink(adapter)}")
    elif os.path.isdir(adapter):
        r.add("adapter", 3, 4, "WARN", ".agents/skills is a directory mirror (not a symlink)")
    else:
        r.add("adapter", 0, 4, "FAIL", ".agents/skills adapter missing")


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    json_only = "--json" in sys.argv
    if not args:
        print(__doc__)
        return 0
    ws = os.path.abspath(args[0])
    if not os.path.isdir(ws):
        print(json.dumps({"error": f"not a directory: {ws}"}))
        return 0

    r = Report()
    check_structure(ws, r)
    check_naming(ws, r)
    check_brain(ws, r)
    check_skills(ws, r)
    check_manifests(ws, r)
    check_adapter(ws, r)

    result = {
        "workspace": ws,
        "auto_subtotal": r.subtotal,
        "auto_max": r.maximum,
        "checks": r.checks,
    }
    if json_only:
        print(json.dumps(result, indent=2))
        return 0

    print(f"\nworkspace-os static eval: {ws}")
    print("=" * 72)
    for c in r.checks:
        mark = {"PASS": "✓", "WARN": "~", "FAIL": "✗"}.get(c["status"], "?")
        print(f"  [{mark}] {c['id']:<22} {c['points']:>4}/{c['max']:<3}  {c['detail']}")
    print("=" * 72)
    print(f"  AUTO SUBTOTAL: {r.subtotal}/{r.maximum}  "
          f"(remaining {100 - int(r.maximum)} pts of the /100 build rubric are by inspection)\n")
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
