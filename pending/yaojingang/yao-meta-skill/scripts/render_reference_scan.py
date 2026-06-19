#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


def parse_frontmatter(text: str) -> tuple[dict, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    try:
        end_index = lines[1:].index("---") + 1
    except ValueError:
        return {}, text
    frontmatter = "\n".join(lines[1:end_index])
    body = "\n".join(lines[end_index + 1 :]).lstrip()
    if yaml is not None:
        payload = yaml.safe_load(frontmatter) or {}
        return payload if isinstance(payload, dict) else {}, body
    data = {}
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data, body


def extract_title(body: str, fallback: str) -> str:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def parse_reference(value: str, source: str) -> dict:
    if "::" in value:
        parts = [part.strip() for part in value.split("::")]
        while len(parts) < 4:
            parts.append("")
        name, category, borrow, avoid = parts[:4]
    else:
        name, category, borrow, avoid = value.strip(), "", "", ""
    defaults = {
        "external": (
            "general",
            "Extract the strongest reusable method, structure, or execution pattern.",
            "Do not copy brand language, heavyweight process, or source-specific constraints.",
        ),
        "user": (
            "taste",
            "Learn what quality, tone, workflow shape, or operating standard the user wants to preserve.",
            "Do not copy wording, confidential material, or source-specific implementation details.",
        ),
        "local": (
            "general",
            "Keep the new skill compatible with real local constraints that matter.",
            "Do not inherit private or outdated patterns just because they already exist locally.",
        ),
    }
    default_category, default_borrow, default_avoid = defaults.get(source, defaults["external"])
    return {
        "name": name or "Unnamed reference",
        "category": category or default_category,
        "borrow": borrow or default_borrow,
        "avoid": avoid or default_avoid,
        "source": source,
    }


def infer_scan_focus(skill_dir: Path, description: str) -> list[dict]:
    checks = []
    if (skill_dir / "evals").exists():
        checks.append(
            {
                "label": "Evaluation pattern",
                "reason": "This skill already carries eval assets, so benchmark how top examples define trigger boundaries and quality gates.",
            }
        )
    if (skill_dir / "scripts").exists():
        checks.append(
            {
                "label": "Execution pattern",
                "reason": "There is deterministic logic in scripts, so compare how strong references separate prose from executable steps.",
            }
        )
    if (skill_dir / "agents" / "interface.yaml").exists():
        checks.append(
            {
                "label": "Portability pattern",
                "reason": "The package carries neutral metadata, so scan how good references preserve semantics across targets without forking source.",
            }
        )
    checks.append(
        {
            "label": "Method pattern",
            "reason": f"Use the core job description as the anchor for comparison: {description}",
        }
    )
    return checks[:4]


def split_references(references: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    externals = [item for item in references if item.get("source") == "external"]
    users = [item for item in references if item.get("source") == "user"]
    locals_ = [item for item in references if item.get("source") == "local"]
    return externals, users, locals_


def build_summary(skill_dir: Path, references: list[dict]) -> dict:
    skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(skill_text)
    name = frontmatter.get("name", skill_dir.name)
    description = frontmatter.get("description", "No description found.")
    title = extract_title(body, name.replace("-", " ").title())
    focus = infer_scan_focus(skill_dir, description)
    external_references, user_references, local_constraints = split_references(references)

    borrow_plan = [
        "External benchmark first: let high-quality public references define the upper bound for method, structure, execution, or portability.",
        "User references second: use them to understand taste, standards, and directional preferences without copying source phrasing.",
        "Local fit third: use local assets only to detect naming conflicts, private dependencies, or compatibility constraints.",
        "Borrow patterns, not prose: extract loops, boundaries, metadata, and operator flow without copying source-specific language.",
        "Keep the package light: reject any borrowed pattern that increases context cost faster than it increases reliability.",
    ]

    if external_references:
        borrow_plan.append("Apply only the benchmark patterns that fit the chosen archetype, gates, and context budget.")

    return {
        "skill_name": name,
        "title": title,
        "description": description,
        "scan_focus": focus,
        "external_references": external_references,
        "user_references": user_references,
        "local_constraints": local_constraints,
        "borrow_plan": borrow_plan,
        "priority_rule": "External benchmark objects set the pattern ceiling. User references refine taste and standards. Local files only calibrate fit, risk, and compatibility.",
        "non_goals": [
            "Do not copy source prose or branding into the new skill.",
            "Do not import gates that cost more context than they save.",
            "Do not use benchmark scanning to justify scope creep.",
            "Do not let local historical habits outrank stronger public benchmarks.",
        ],
    }


def render_markdown(summary: dict) -> str:
    lines = [
        "# Reference Scan",
        "",
        f"Skill: `{summary['skill_name']}`",
        "",
        "## Why This Step Exists",
        "",
        "Use a short benchmark pass before authoring the package in depth. External benchmark objects should define the pattern ceiling. Local files are used afterward only to calibrate fit, privacy, naming, and compatibility.",
        "",
        "## Current Skill Anchor",
        "",
        f"- Title: `{summary['title']}`",
        f"- Description: {summary['description']}",
        "",
        "## Scan Focus",
        "",
    ]
    for item in summary["scan_focus"]:
        lines.append(f"- **{item['label']}**: {item['reason']}")

    lines.extend(["", "## Priority Rule", "", f"- {summary['priority_rule']}", ""])

    lines.extend(["## External Benchmark Objects", ""])
    if summary["external_references"]:
        for ref in summary["external_references"]:
            lines.extend(
                [
                    f"### {ref['name']}",
                    f"- Category: `{ref['category']}`",
                    f"- Borrow: {ref['borrow']}",
                    f"- Avoid: {ref['avoid']}",
                    "",
                ]
            )
    else:
        lines.extend(
            [
                "- No explicit external benchmark objects recorded yet.",
                "- Recommended: capture 2 to 5 external references at most.",
                "- Suggested mix: one method reference, one structure reference, one execution or portability reference.",
                "",
            ]
        )

    lines.extend(["## User-Supplied References", ""])
    if summary["user_references"]:
        for ref in summary["user_references"]:
            lines.extend(
                [
                    f"### {ref['name']}",
                    f"- Category: `{ref['category']}`",
                    f"- Learn from: {ref['borrow']}",
                    f"- Do not copy: {ref['avoid']}",
                    "",
                ]
            )
    else:
        lines.extend(
            [
                "- No user-supplied references recorded yet.",
                "- Ask whether the user has a repo, product, page, workflow, or prompt example worth learning from.",
                "- Treat these as pattern references only, not as text to be copied.",
                "",
            ]
        )

    lines.extend(["## Local Fit Check", ""])
    if summary["local_constraints"]:
        for ref in summary["local_constraints"]:
            lines.extend(
                [
                    f"### {ref['name']}",
                    f"- Category: `{ref['category']}`",
                    f"- Keep in mind: {ref['borrow']}",
                    f"- Do not inherit: {ref['avoid']}",
                    "",
                ]
            )
    else:
        lines.extend(
            [
                "- No local constraints recorded yet.",
                "- Use this section for naming collisions, private dependencies, compatibility limits, or existing library conventions.",
                "",
            ]
        )

    lines.extend(["## Borrow Plan", ""])
    for item in summary["borrow_plan"]:
        lines.append(f"- {item}")

    lines.extend(["", "## Non-Goals", ""])
    for item in summary["non_goals"]:
        lines.append(f"- {item}")

    return "\n".join(lines).strip() + "\n"


def render_reference_scan(skill_dir: Path, references: list[dict], output_md: Path | None = None, output_json: Path | None = None) -> dict:
    skill_dir = skill_dir.resolve()
    reports_dir = skill_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_md = output_md or reports_dir / "reference-scan.md"
    output_json = output_json or reports_dir / "reference-scan.json"

    summary = build_summary(skill_dir, references)
    output_md.write_text(render_markdown(summary), encoding="utf-8")
    output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "ok": True,
        "skill_dir": str(skill_dir),
        "artifacts": {
            "markdown": str(output_md),
            "json": str(output_json),
        },
        "summary": summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a benchmark-oriented reference scan for a skill package.")
    parser.add_argument("skill_dir", nargs="?", default=".")
    parser.add_argument("--external-reference", action="append", default=[], help="Format: name::category::borrow::avoid")
    parser.add_argument("--user-reference", action="append", default=[], help="Format: name::category::borrow::avoid")
    parser.add_argument("--local-constraint", action="append", default=[], help="Format: name::category::borrow::avoid")
    parser.add_argument("--reference", action="append", default=[], help="Legacy alias for --external-reference.")
    parser.add_argument("--output-md")
    parser.add_argument("--output-json")
    args = parser.parse_args()

    refs = [parse_reference(item, "external") for item in [*args.external_reference, *args.reference]]
    refs.extend(parse_reference(item, "user") for item in args.user_reference)
    refs.extend(parse_reference(item, "local") for item in args.local_constraint)
    result = render_reference_scan(
        Path(args.skill_dir),
        refs,
        Path(args.output_md).resolve() if args.output_md else None,
        Path(args.output_json).resolve() if args.output_json else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
