#!/usr/bin/env python3
import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

from render_world_class_evidence_ledger import build_ledger


ROOT = Path(__file__).resolve().parent.parent
SCRIPT_INTERFACE = "cli"
SCRIPT_INTERFACE_REASON = "Scans public claim surfaces so world-class completion is not claimed before accepted evidence exists."

FORBIDDEN_WHEN_PENDING = [
    {
        "key": "ready-to-claim-true",
        "pattern": re.compile(r"ready[\s_-]*to[\s_-]*claim[\s_-]*world[\s_-]*class\s*[:=]\s*`?true`?", re.IGNORECASE),
        "reason": "ready_to_claim_world_class cannot be true while ledger evidence is pending.",
    },
    {
        "key": "world-class-ready-true",
        "pattern": re.compile(r"(public\s+)?world[\s_-]*class[\s_-]*ready\s*[:=]\s*`?true`?", re.IGNORECASE),
        "reason": "world-class readiness cannot be claimed before accepted external and human evidence exists.",
    },
    {
        "key": "json-world-class-ready-true",
        "pattern": re.compile(r'"(?:ready_to_claim_world_class|world_class_ready|public_world_class_ready)"\s*:\s*true', re.IGNORECASE),
        "reason": "machine-readable claim fields must remain false until the ledger is ready.",
    },
    {
        "key": "completion-phrase",
        "pattern": re.compile(r"(public\s+)?world[\s_-]*class\s+(?:complete|completed|achieved|certified)", re.IGNORECASE),
        "reason": "completion language is blocked until the world-class ledger is accepted.",
    },
    {
        "key": "zh-completion-phrase",
        "pattern": re.compile(r"世界级(?:已完成|完成|已达成|达成|准备就绪|可声明|认证通过)"),
        "reason": "中文完成态表述必须等到 ledger ready 后才能出现。",
    },
]


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def rel_path(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path.resolve())


def resolve_claim_surface(raw_path: str, skill_dir: Path) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = skill_dir / path
    return path.resolve()


def should_scan_claim_surface(path: Path) -> bool:
    parts = path.parts
    if "release_snapshots" in parts:
        return False
    if path.name in {"world_class_claim_guard.md", "world_class_claim_guard.html"}:
        return False
    if "dist" in parts and "install-simulation" in parts:
        return False
    if "evidence" in parts and "world_class" in parts and "submissions" in parts:
        return False
    return True


def default_claim_surfaces(skill_dir: Path) -> list[Path]:
    paths: list[Path] = []
    for rel in ["README.md", "SKILL.md", "manifest.json"]:
        path = skill_dir / rel
        if path.exists():
            paths.append(path)
    for directory, patterns in [
        (skill_dir / "agents", ["*.yaml", "*.yml", "*.json"]),
        (skill_dir / "docs", ["*.md"]),
        (skill_dir / "evidence" / "world_class", ["*.md", "*.json"]),
        (skill_dir / "dist", ["*.json", "*.md"]),
        (skill_dir / "reports", ["*.md", "*.html", "*.json"]),
        (skill_dir / "registry", ["*.json"]),
        (skill_dir / "security", ["*.md", "*.json"]),
        (skill_dir / "skill-ir", ["*.json"]),
    ]:
        if not directory.exists():
            continue
        for pattern in patterns:
            paths.extend(
                path
                for path in directory.rglob(pattern)
                if path.is_file() and should_scan_claim_surface(path)
            )
    return sorted(set(paths), key=lambda item: rel_path(item, skill_dir))


def line_matches(path: Path, ledger_ready: bool) -> list[dict[str, Any]]:
    if ledger_ready:
        return []
    violations: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return violations
    for lineno, line in enumerate(lines, start=1):
        for rule in FORBIDDEN_WHEN_PENDING:
            if rule["pattern"].search(line):
                violations.append(
                    {
                        "line": lineno,
                        "rule": rule["key"],
                        "reason": rule["reason"],
                        "excerpt": line.strip()[:240],
                    }
                )
    return violations


def escape_markdown_table_cell(value: Any) -> str:
    return str(value).replace("|", "\\|")


def build_guard(skill_dir: Path, generated_at: str, claim_surfaces: list[Path] | None = None) -> dict[str, Any]:
    ledger = build_ledger(skill_dir, generated_at)
    ledger_ready = ledger.get("summary", {}).get("ready_to_claim_world_class") is True
    surfaces = claim_surfaces or default_claim_surfaces(skill_dir)
    scanned = []
    violations = []
    for path in surfaces:
        matches = line_matches(path, ledger_ready)
        rel = rel_path(path, skill_dir)
        scanned.append({"path": rel, "violation_count": len(matches)})
        for match in matches:
            violations.append({"path": rel, **match})
    ok = len(violations) == 0
    json_surface_count = sum(1 for item in scanned if item["path"].endswith(".json"))
    metadata_surface_count = sum(
        1 for item in scanned if item["path"].endswith((".json", ".yaml", ".yml"))
    )
    package_surface_count = sum(
        1
        for item in scanned
        if item["path"] == "manifest.json"
        or item["path"].startswith(("agents/", "dist/", "security/"))
    )
    return {
        "schema_version": "1.0",
        "ok": ok,
        "generated_at": generated_at,
        "skill_dir": rel_path(skill_dir, ROOT),
        "summary": {
            "ledger_ready_to_claim_world_class": ledger_ready,
            "ledger_pending_count": ledger.get("summary", {}).get("pending_count", 0),
            "claim_surface_count": len(scanned),
            "json_claim_surface_count": json_surface_count,
            "metadata_claim_surface_count": metadata_surface_count,
            "package_claim_surface_count": package_surface_count,
            "violation_count": len(violations),
            "overclaim_guard_active": True,
            "decision": (
                "claim-ready"
                if ledger_ready and ok
                else ("claim-blocked-overclaim" if violations else "claim-guard-pass-evidence-pending")
            ),
        },
        "rules": [
            {"key": item["key"], "reason": item["reason"], "pattern": item["pattern"].pattern}
            for item in FORBIDDEN_WHEN_PENDING
        ],
        "scanned_surfaces": scanned,
        "violations": violations,
        "source_ledger": {
            "json": "reports/world_class_evidence_ledger.json",
            "markdown": "reports/world_class_evidence_ledger.md",
        },
        "artifacts": {
            "json": "reports/world_class_claim_guard.json",
            "markdown": "reports/world_class_claim_guard.md",
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# World-Class Claim Guard",
        "",
        f"Generated at: `{report['generated_at']}`",
        "",
        "## Summary",
        "",
        f"- decision: `{summary['decision']}`",
        f"- ledger ready to claim world-class: `{str(summary['ledger_ready_to_claim_world_class']).lower()}`",
        f"- ledger pending evidence: `{summary['ledger_pending_count']}`",
        f"- claim surfaces scanned: `{summary['claim_surface_count']}`",
        f"- JSON claim surfaces scanned: `{summary['json_claim_surface_count']}`",
        f"- metadata claim surfaces scanned: `{summary['metadata_claim_surface_count']}`",
        f"- package/runtime claim surfaces scanned: `{summary['package_claim_surface_count']}`",
        f"- violations: `{summary['violation_count']}`",
        f"- overclaim guard active: `{str(summary['overclaim_guard_active']).lower()}`",
        "",
        "This guard scans public claim surfaces, machine-readable reports, and package/runtime metadata for completion language that would contradict the world-class evidence ledger. It allows evidence planning and pending-state language, but blocks completion claims until the ledger is ready.",
        "",
        "## Violations",
        "",
        "| Path | Line | Rule | Excerpt |",
        "| --- | ---: | --- | --- |",
    ]
    if report["violations"]:
        for item in report["violations"]:
            excerpt = str(item["excerpt"]).replace("|", "\\|")
            lines.append(f"| `{item['path']}` | {item['line']} | `{item['rule']}` | {excerpt} |")
    else:
        lines.append("| `none` | 0 | `none` | none |")
    lines.extend(
        [
            "",
            "## Rules",
            "",
            "| Rule | Reason |",
            "| --- | --- |",
        ]
    )
    for rule in report["rules"]:
        reason = escape_markdown_table_cell(rule["reason"])
        lines.append(f"| `{rule['key']}` | {reason} |")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Guard public world-class completion claims against the evidence ledger.")
    parser.add_argument("skill_dir", nargs="?", default=".")
    parser.add_argument("--claim-surface", action="append", default=[])
    parser.add_argument("--output-json", default="reports/world_class_claim_guard.json")
    parser.add_argument("--output-md", default="reports/world_class_claim_guard.md")
    parser.add_argument("--generated-at", default=date.today().isoformat())
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    claim_surfaces = [resolve_claim_surface(item, skill_dir) for item in args.claim_surface] if args.claim_surface else None
    report = build_guard(skill_dir, args.generated_at, claim_surfaces)
    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    if not output_json.is_absolute():
        output_json = skill_dir / output_json
    if not output_md.is_absolute():
        output_md = skill_dir / output_md
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["ok"] else 2)


if __name__ == "__main__":
    main()
