#!/usr/bin/env python3
import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


ROOT = Path(__file__).resolve().parent.parent
SCHEMA_VERSION = "2.0.0"
IR_SCHEMA = ROOT / "skill-ir" / "schema.json"
KEY_REPORTS = [
    "reports/benchmark_methodology.md",
    "reports/intent-context.json",
    "reports/intent-confidence.json",
    "reports/intent-confidence.md",
    "reports/reference-synthesis.json",
    "reports/reference-synthesis.md",
    "reports/output-risk-profile.json",
    "reports/output-risk-profile.md",
    "reports/artifact-design-profile.json",
    "reports/artifact-design-profile.md",
    "reports/prompt-quality-profile.json",
    "reports/prompt-quality-profile.md",
    "reports/system-model.json",
    "reports/system-model.md",
    "reports/iteration-directions.json",
    "reports/iteration-directions.md",
    "reports/skill-overview.json",
    "reports/skill-overview.html",
    "reports/output_quality_scorecard.json",
    "reports/output_quality_scorecard.md",
    "reports/output_execution_runs.json",
    "reports/output_execution_runs.md",
    "reports/output_blind_review_pack.json",
    "reports/output_blind_review_pack.md",
    "reports/output_blind_answer_key.json",
    "reports/output_review_adjudication.json",
    "reports/output_review_adjudication.md",
    "reports/review_annotations.json",
    "reports/review_annotations.md",
    "reports/conformance_matrix.json",
    "reports/conformance_matrix.md",
    "reports/security_trust_report.json",
    "reports/security_trust_report.md",
    "reports/runtime_permission_probes.json",
    "reports/runtime_permission_probes.md",
    "reports/telemetry_hook_recipes.json",
    "reports/telemetry_hook_recipes.md",
    "reports/skill_atlas.json",
    "reports/skill_atlas.html",
    "reports/skill-os-2-review.md",
    "reports/portability_score.json",
    "reports/portability_score.md",
    "reports/governance_score.json",
]


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists() or yaml is None:
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return payload if isinstance(payload, dict) else {}


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    try:
        end_index = lines[1:].index("---") + 1
    except ValueError:
        return {}, text
    frontmatter_text = "\n".join(lines[1:end_index])
    body = "\n".join(lines[end_index + 1 :]).lstrip()
    if yaml is not None:
        payload = yaml.safe_load(frontmatter_text) or {}
        return payload if isinstance(payload, dict) else {}, body
    data: dict[str, Any] = {}
    for line in frontmatter_text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data, body


def parse_sections(body: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {"_preamble": []}
    current = "_preamble"
    for line in body.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
            continue
        sections.setdefault(current, []).append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def extract_list_items(text: str, limit: int = 12) -> list[str]:
    items = []
    for line in text.splitlines():
        stripped = line.strip()
        match = re.match(r"^(?:[-*]|\d+\.)\s+(.*)$", stripped)
        if match:
            item = match.group(1).strip()
            if item:
                items.append(item)
        if len(items) >= limit:
            break
    return items


def compact_unique(items: list[str], limit: int = 12) -> list[str]:
    seen = set()
    output = []
    for item in items:
        value = str(item).strip()
        key = value.lower()
        if not value or key in seen:
            continue
        seen.add(key)
        output.append(value)
        if len(output) >= limit:
            break
    return output


def trigger_samples(skill_dir: Path, key: str, limit: int = 8) -> list[str]:
    payload = load_json(skill_dir / "evals" / "trigger_cases.json")
    values = payload.get(key, [])
    samples = []
    if isinstance(values, list):
        for item in values:
            if isinstance(item, dict):
                samples.append(str(item.get("text", "")).strip())
            else:
                samples.append(str(item).strip())
    return compact_unique(samples, limit=limit)


def report_list(skill_dir: Path) -> list[str]:
    return [rel for rel in KEY_REPORTS if (skill_dir / rel).exists()]


def file_list(skill_dir: Path, folder: str, suffixes: set[str] | None = None, limit: int | None = None) -> list[str]:
    target = skill_dir / folder
    if not target.exists():
        return []
    paths = []
    for path in sorted(target.rglob("*")):
        if not path.is_file():
            continue
        if suffixes is not None and path.suffix not in suffixes:
            continue
        paths.append(str(path.relative_to(skill_dir)))
        if limit is not None and len(paths) >= limit:
            break
    return paths


def workflow_steps(sections: dict[str, str]) -> list[str]:
    for key in ("Compact Workflow", "Workflow", "How It Works", "Runbook", "Quick Start"):
        items = extract_list_items(sections.get(key, ""), limit=10)
        if items:
            return items
    return ["Understand the request.", "Execute the main task.", "Validate the result."]


def decision_points(sections: dict[str, str], system_model: dict[str, Any]) -> list[str]:
    points = []
    for key in ("Router Rules", "Modes", "Output Contract"):
        points.extend(extract_list_items(sections.get(key, ""), limit=6))
    boundary = system_model.get("boundary_map", {}) if isinstance(system_model, dict) else {}
    points.extend(boundary.get("human_judgment_boundary", []) if isinstance(boundary, dict) else [])
    return compact_unique(points, limit=10)


def failure_modes(skill_dir: Path, output_risk: dict[str, Any], system_model: dict[str, Any]) -> list[str]:
    modes = []
    modes.extend(output_risk.get("top_risks", [])[:6])
    drift = system_model.get("drift_watch", []) if isinstance(system_model, dict) else []
    for item in drift:
        if isinstance(item, dict):
            modes.append(str(item.get("watch_signal", "") or item.get("risk", "")))
    failure_cases = skill_dir / "evals" / "failure-cases.md"
    if failure_cases.exists():
        modes.extend(extract_list_items(failure_cases.read_text(encoding="utf-8"), limit=4))
    return compact_unique(modes, limit=10)


def risk_level_from_count(count: int) -> str:
    if count >= 5:
        return "high"
    if count >= 2:
        return "medium"
    return "low"


def build_skill_ir(skill_dir: Path) -> dict[str, Any]:
    skill_dir = skill_dir.resolve()
    skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(skill_text)
    sections = parse_sections(body)
    manifest = load_json(skill_dir / "manifest.json")
    interface_data = load_yaml(skill_dir / "agents" / "interface.yaml")
    intent_context = load_json(skill_dir / "reports" / "intent-context.json")
    output_risk = load_json(skill_dir / "reports" / "output-risk-profile.json")
    system_model = load_json(skill_dir / "reports" / "system-model.json")

    name = str(frontmatter.get("name") or manifest.get("name") or skill_dir.name)
    description = str(frontmatter.get("description") or intent_context.get("description") or "")
    title = str(interface_data.get("interface", {}).get("display_name") or name.replace("-", " ").title())
    job = str(intent_context.get("job") or system_model.get("boundary_map", {}).get("owned_job") or description)
    exclusions = intent_context.get("exclusions", [])
    if not exclusions:
        exclusions = system_model.get("boundary_map", {}).get("non_goals", [])

    scripts = file_list(skill_dir, "scripts", suffixes={".py", ".sh", ".js", ".ts"})
    references = file_list(skill_dir, "references", suffixes={".md", ".txt", ".json", ".yaml", ".yml"})
    assets = file_list(skill_dir, "assets") + file_list(skill_dir, "templates")
    trigger_eval_files = file_list(skill_dir, "evals", suffixes={".json", ".jsonl", ".md"})
    output_eval_files = file_list(skill_dir, "evals/output", suffixes={".json", ".jsonl", ".md"})

    target_platforms = manifest.get("target_platforms") or interface_data.get("compatibility", {}).get("adapter_targets", [])
    maturity = str(manifest.get("maturity_tier") or manifest.get("skill_archetype") or "scaffold")
    trust_boundary = "external" if maturity == "governed" else "team" if maturity in {"production", "library"} else "personal"
    output_risk_count = len(output_risk.get("risk_families", []))
    execution_risk = "medium" if scripts else "low"

    return {
        "schema_version": SCHEMA_VERSION,
        "name": name,
        "title": title,
        "job_to_be_done": job,
        "trigger_surface": {
            "description": description,
            "should_trigger": trigger_samples(skill_dir, "should_trigger") or [description],
            "should_not_trigger": compact_unique([*trigger_samples(skill_dir, "should_not_trigger"), *map(str, exclusions)], 10),
            "edge_cases": trigger_samples(skill_dir, "near_neighbor"),
        },
        "workflow": {
            "steps": workflow_steps(sections),
            "decision_points": decision_points(sections, system_model),
            "failure_modes": failure_modes(skill_dir, output_risk, system_model),
        },
        "resources": {
            "references": references,
            "scripts": scripts,
            "assets": assets,
            "reports": report_list(skill_dir),
        },
        "eval_plan": {
            "trigger": trigger_eval_files,
            "output": output_eval_files,
            "adversarial": file_list(skill_dir, "evals/adversarial", suffixes={".json", ".jsonl", ".md"}),
            "baseline": "without_skill",
        },
        "risk": {
            "output_risk": risk_level_from_count(output_risk_count),
            "execution_risk": execution_risk,
            "trust_boundary": trust_boundary,
        },
        "governance": {
            "owner": str(manifest.get("owner", "")),
            "maturity": maturity if maturity in {"scaffold", "production", "library", "governed"} else "scaffold",
            "review_cadence": str(manifest.get("review_cadence", "")),
            "review_due": str(manifest.get("review_due", "")),
        },
        "targets": [str(item) for item in target_platforms],
        "source_files": compact_unique(
            [
                "SKILL.md",
                "manifest.json" if (skill_dir / "manifest.json").exists() else "",
                "agents/interface.yaml" if (skill_dir / "agents" / "interface.yaml").exists() else "",
                "reports/intent-context.json" if (skill_dir / "reports" / "intent-context.json").exists() else "",
                "reports/output-risk-profile.json" if (skill_dir / "reports" / "output-risk-profile.json").exists() else "",
                "reports/system-model.json" if (skill_dir / "reports" / "system-model.json").exists() else "",
            ],
            limit=20,
        ),
    }


def validate_ir(payload: dict[str, Any]) -> list[str]:
    failures = []
    for key in ("schema_version", "name", "job_to_be_done", "trigger_surface", "workflow", "resources", "eval_plan", "risk", "governance"):
        if key not in payload:
            failures.append(f"Missing required field: {key}")
    if payload.get("schema_version") != SCHEMA_VERSION:
        failures.append(f"schema_version must be {SCHEMA_VERSION}")
    if not payload.get("trigger_surface", {}).get("description"):
        failures.append("trigger_surface.description is required")
    if not payload.get("trigger_surface", {}).get("should_trigger"):
        failures.append("trigger_surface.should_trigger needs at least one sample")
    if not payload.get("workflow", {}).get("steps"):
        failures.append("workflow.steps needs at least one step")
    if payload.get("risk", {}).get("output_risk") not in {"low", "medium", "high"}:
        failures.append("risk.output_risk must be low, medium, or high")
    if payload.get("governance", {}).get("maturity") not in {"scaffold", "production", "library", "governed"}:
        failures.append("governance.maturity is invalid")
    return failures


def default_output_path(skill_dir: Path, payload: dict[str, Any]) -> Path:
    if skill_dir.resolve() == ROOT.resolve():
        return ROOT / "skill-ir" / "examples" / f"{payload['name']}.json"
    return skill_dir / "reports" / "skill-ir.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a platform-neutral Skill IR document from a skill package.")
    parser.add_argument("skill_dir", nargs="?", default=".")
    parser.add_argument("--output-json")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    payload = build_skill_ir(skill_dir)
    failures = validate_ir(payload)
    output_json = Path(args.output_json).resolve() if args.output_json else default_output_path(skill_dir, payload)
    if not args.validate_only:
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result = {
        "ok": not failures,
        "schema": str(IR_SCHEMA),
        "skill_dir": str(skill_dir),
        "artifacts": {"json": str(output_json)},
        "summary": {
            "name": payload.get("name"),
            "maturity": payload.get("governance", {}).get("maturity"),
            "target_count": len(payload.get("targets", [])),
            "trigger_samples": len(payload.get("trigger_surface", {}).get("should_trigger", [])),
            "resource_count": sum(len(payload.get("resources", {}).get(key, [])) for key in ("references", "scripts", "assets", "reports")),
        },
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["ok"] else 2)


if __name__ == "__main__":
    main()
