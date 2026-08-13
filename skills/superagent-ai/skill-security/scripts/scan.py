#!/usr/bin/env python3
"""
skill-security scanner — Stage 1 (deterministic) engine.

Runs regex patterns, Python AST analysis, taint tracking, shell/JS heuristics,
frontmatter/contract checks, supply-chain analysis, and YARA matching over a
skill directory, single file, or zip. Emits findings + a 0-100 risk score.

This is the *mechanical* half. The agent that invoked the skill reads the
output and performs Stage 2: semantic judgment and the frontmatter<->behavior
contract check. See ../SKILL.md.

Usage:
    python3 scan.py <path-to-skill-dir | SKILL.md | skill.zip> [--format json|markdown|terminal|sarif] [--min-confidence 0.0]
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # robust import from any cwd

import analyzers as az  # noqa: E402
from yara_lite import YaraEngine  # noqa: E402

RULES_DIR = Path(__file__).resolve().parent.parent / "rules"

SEV_POINTS = {"CRITICAL": 50, "HIGH": 25, "MEDIUM": 10, "LOW": 5}
RISK_BANDS = [(81, "CRITICAL", "DO NOT INSTALL"), (51, "HIGH", "DO NOT INSTALL"),
              (21, "MEDIUM", "REVIEW MANUALLY"), (0, "LOW", "LIKELY SAFE")]

_YARA_SEVERITY_TO_RULE = {
    "malware": ("YR1", "Malware signature match", "CRITICAL"),
    "webshell": ("YR2", "Webshell signature match", "CRITICAL"),
    "cryptominer": ("YR3", "Cryptominer signature match", "HIGH"),
    "hacktool": ("YR4", "Hacktool / exploit signature match", "HIGH"),
}


def _resolve_target(target: str) -> tuple[Path, tempfile.TemporaryDirectory | None]:
    p = Path(target)
    tmp = None
    if p.suffix.lower() in (".zip", ".skill") and p.is_file():
        tmp = tempfile.TemporaryDirectory()
        with zipfile.ZipFile(p) as zf:
            zf.extractall(tmp.name)
        extracted = Path(tmp.name)
        # if the zip contains a single top-level dir, descend into it
        entries = [e for e in extracted.iterdir()]
        if len(entries) == 1 and entries[0].is_dir():
            return entries[0], tmp
        return extracted, tmp
    return p, None


def run_scan(target: str, min_confidence: float = 0.0) -> dict:
    root, tmp = _resolve_target(target)
    try:
        scan_in = az.discover(root)
        engine = YaraEngine(RULES_DIR)
        findings: list[az.Finding] = []
        components: list[az.Component] = []
        skill_name = root.name
        has_exec = False

        for fp in scan_in.files:
            rel = str(fp.relative_to(scan_in.root)) if fp != scan_in.root else fp.name
            kind, executable = az.classify(fp)
            content = az.read_text(fp)
            if not content:
                continue
            n_lines = content.count("\n") + 1
            components.append(az.Component(rel, kind, n_lines, executable))
            if executable:
                has_exec = True
            if fp.name == "SKILL.md" and content.startswith("---"):
                skill_name = az.parse_frontmatter(content)[0].get("name", skill_name)

            # regex patterns (all text + code files)
            findings += az.scan_patterns(rel, kind, content)
            # frontmatter / contract / unicode (manifest + markdown)
            if kind in ("skill_manifest", "markdown"):
                findings += az.scan_frontmatter(rel, content)
            # python deep analysis
            if kind == "python":
                findings += az.scan_python_ast(rel, content)
                findings += az.scan_taint(rel, content)
            # shell / js heuristics
            if kind in ("shell", "javascript"):
                findings += az.scan_shell_js(rel, content)
            # dependency manifests
            if fp.name in ("requirements.txt", "requirements.in", "package.json"):
                findings += az.scan_dependencies(rel, fp.name, content)
            # YARA over everything textual
            for hit in engine.scan_text(content):
                cat = hit.meta.get("category", "")
                rid = hit.meta.get("rule_id")
                sev = hit.meta.get("severity", "HIGH")
                conf = float(hit.meta.get("confidence", "0.7") or 0.7)
                if rid is None:
                    base = cat.split("_")[0] if cat else ""
                    rid, _t, _s = _YARA_SEVERITY_TO_RULE.get(cat, ("YR5", "Skill-threat signature", sev))
                    title = f"YARA: {hit.rule}"
                else:
                    title = f"YARA: {hit.rule}"
                clean_cat = cat.replace("_", " ").title() if cat else "YARA Match"
                findings.append(az.Finding(
                    rid, title, clean_cat, sev, conf,
                    rel, 1, ", ".join(hit.matched_strings[:6]),
                    hit.meta.get("description", "")))

        # filter by confidence, then dedupe
        findings = [f for f in findings if f.confidence >= min_confidence]
        findings = _dedupe(findings)
        findings.sort(key=lambda f: (-az.SEVERITY_ORDER.get(f.severity, 0), -f.confidence, f.file, f.line))

        score, band, recommendation = _score(findings, has_exec)
        return {
            "skill": skill_name,
            "source": str(target),
            "yara_backend": engine.backend,
            "risk": {"score": score, "severity": band, "recommendation": recommendation},
            "has_executable_scripts": has_exec,
            "components": [c.__dict__ for c in components],
            "findings": [f.dict() for f in findings],
            "summary": _summary(findings),
        }
    finally:
        if tmp is not None:
            tmp.cleanup()


def _dedupe(findings: list[az.Finding]) -> list[az.Finding]:
    seen = set()
    out = []
    for f in findings:
        key = (f.rule_id, f.file, f.line, f.title)
        if key not in seen:
            seen.add(key)
            out.append(f)
    return out


def _score(findings: list[az.Finding], has_exec: bool) -> tuple[int, str, str]:
    score = 0
    for f in findings:
        # weight by confidence so low-confidence noise doesn't dominate
        score += SEV_POINTS.get(f.severity.upper(), 0) * (0.5 + 0.5 * f.confidence)
    if has_exec:
        score *= 1.3
    score = int(min(100, max(0, round(score))))
    for threshold, band, rec in RISK_BANDS:
        if score >= threshold:
            return score, band, rec
    return score, "LOW", "LIKELY SAFE"


def _summary(findings: list[az.Finding]) -> dict:
    by_sev: dict[str, int] = {}
    by_cat: dict[str, int] = {}
    for f in findings:
        by_sev[f.severity] = by_sev.get(f.severity, 0) + 1
        by_cat[f.category] = by_cat.get(f.category, 0) + 1
    return {"total": len(findings), "by_severity": by_sev, "by_category": by_cat}


# --------------------------------------------------------------------------- #
# output formats
# --------------------------------------------------------------------------- #
def fmt_json(result: dict) -> str:
    return json.dumps(result, indent=2)


def fmt_markdown(result: dict) -> str:
    r = result["risk"]
    lines = [
        f"# skill-security report: {result['skill']}",
        "",
        f"- **Score:** {r['score']}/100 ({r['severity']})",
        f"- **Recommendation:** {r['recommendation']}",
        f"- **Executable scripts:** {'yes' if result['has_executable_scripts'] else 'no'}",
        f"- **Findings:** {result['summary']['total']}  (YARA backend: {result['yara_backend']})",
        "",
        "## Findings",
        "",
    ]
    if not result["findings"]:
        lines.append("_No deterministic findings. Still review the SKILL.md body for intent._")
    else:
        lines.append("| Severity | Rule | Title | File:Line | Conf | Evidence |")
        lines.append("|---|---|---|---|---|---|")
        for f in result["findings"]:
            ev = f["evidence"].replace("|", "\\|")[:80]
            lines.append(f"| {f['severity']} | {f['rule_id']} | {f['title']} | `{f['file']}:{f['line']}` | {f['confidence']:.2f} | `{ev}` |")
    return "\n".join(lines)


def fmt_terminal(result: dict) -> str:
    r = result["risk"]
    out = [
        "═" * 64,
        f" skill-security  ·  {result['skill']}",
        "═" * 64,
        f" score          {r['score']}/100",
        f" severity       {r['severity']}",
        f" recommendation {r['recommendation']}",
        f" yara backend   {result['yara_backend']}",
        f" findings       {result['summary']['total']}",
        "─" * 64,
    ]
    for f in result["findings"]:
        out.append(f" [{f['severity']:8}] {f['rule_id']:5} {f['title']}")
        out.append(f"            {f['file']}:{f['line']}  (conf {f['confidence']:.2f})")
        if f["evidence"]:
            out.append(f"            > {f['evidence'][:90]}")
    out.append("═" * 64)
    return "\n".join(out)


def fmt_sarif(result: dict) -> str:
    level = {"CRITICAL": "error", "HIGH": "error", "MEDIUM": "warning", "LOW": "note"}
    rules_seen = {}
    sarif_results = []
    for f in result["findings"]:
        rules_seen[f["rule_id"]] = f["title"]
        sarif_results.append({
            "ruleId": f["rule_id"],
            "level": level.get(f["severity"], "warning"),
            "message": {"text": f"{f['title']} (confidence {f['confidence']:.2f})"},
            "locations": [{"physicalLocation": {
                "artifactLocation": {"uri": f["file"]},
                "region": {"startLine": max(1, f["line"])},
            }}],
        })
    return json.dumps({
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {
                "name": "skill-security",
                "rules": [{"id": rid, "name": name} for rid, name in rules_seen.items()],
            }},
            "results": sarif_results,
        }],
    }, indent=2)


FORMATTERS = {"json": fmt_json, "markdown": fmt_markdown, "terminal": fmt_terminal, "sarif": fmt_sarif}


def main() -> int:
    ap = argparse.ArgumentParser(description="Deterministic security scanner for AI agent skills.")
    ap.add_argument("target", help="path to skill dir, SKILL.md, or .zip/.skill")
    ap.add_argument("-f", "--format", choices=list(FORMATTERS), default="terminal")
    ap.add_argument("--min-confidence", type=float, default=0.0)
    ap.add_argument("-o", "--output", help="write to file instead of stdout")
    args = ap.parse_args()

    if not Path(args.target).exists():
        print(f"error: target not found: {args.target}", file=sys.stderr)
        return 2

    result = run_scan(args.target, min_confidence=args.min_confidence)
    text = FORMATTERS[args.format](result)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"wrote {args.format} report to {args.output}", file=sys.stderr)
    else:
        print(text)
    # exit code reflects risk for CI use
    return 1 if result["risk"]["severity"] in ("HIGH", "CRITICAL") else 0


if __name__ == "__main__":
    raise SystemExit(main())
