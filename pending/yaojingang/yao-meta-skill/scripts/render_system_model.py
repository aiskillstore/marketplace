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
    frontmatter_text = "\n".join(lines[1:end_index])
    body = "\n".join(lines[end_index + 1 :]).lstrip()
    if yaml is not None:
        payload = yaml.safe_load(frontmatter_text) or {}
        return payload if isinstance(payload, dict) else {}, body
    data = {}
    for line in frontmatter_text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data, body


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def as_list(value) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()]


def compact_unique(items: list[str], limit: int = 6) -> list[str]:
    seen = set()
    result = []
    for item in items:
        normalized = item.strip()
        if not normalized or normalized.lower() in seen:
            continue
        seen.add(normalized.lower())
        result.append(normalized)
        if len(result) >= limit:
            break
    return result


def load_context(skill_dir: Path) -> dict:
    intent = load_json(skill_dir / "reports" / "intent-confidence.json")
    return intent.get("context", {}) if isinstance(intent, dict) else {}


def intent_summary(intent: dict) -> dict:
    if not isinstance(intent, dict):
        return {}
    summary = intent.get("summary")
    return summary if isinstance(summary, dict) else intent


def output_risk_labels(profile: dict) -> list[str]:
    return [
        str(item.get("label", item.get("key", "")))
        for item in profile.get("risk_families", [])
        if item.get("label") or item.get("key")
    ][:5]


def reference_patterns(synthesis: dict) -> list[str]:
    payload = synthesis.get("synthesis", {}) if isinstance(synthesis, dict) else {}
    recommendation = payload.get("recommendation", {}) if isinstance(payload, dict) else {}
    return compact_unique(
        as_list(recommendation.get("borrow_now"))
        + as_list(payload.get("borrow_now"))
        + as_list(recommendation.get("avoid_for_now"))
        + as_list(payload.get("avoid_now")),
        limit=5,
    )


def safe_int(value, default: int = 100) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def build_boundary_map(description: str, context: dict, manifest: dict) -> dict:
    job = context.get("job") or description
    primary_output = context.get("primary_output") or "a reusable skill output"
    real_inputs = as_list(context.get("real_inputs")) or ["user-provided workflow notes, prompts, docs, or examples"]
    exclusions = as_list(context.get("exclusions")) or [
        "one-off adjacent requests that do not match the recurring job",
        "private local material that was not intentionally included",
    ]
    constraints = as_list(context.get("constraints"))
    standards = as_list(context.get("standards"))
    maturity = manifest.get("maturity_tier", "scaffold")
    return {
        "owned_job": str(job),
        "input_boundary": real_inputs,
        "output_boundary": str(primary_output),
        "non_goals": exclusions,
        "constraints": constraints,
        "standards": standards,
        "human_judgment_boundary": [
            "Ask one focused clarification when the real job, output, or exclusion boundary is unclear.",
            "Escalate visible tradeoffs when benchmark patterns conflict with local privacy, naming, or governance constraints.",
            "Do not silently broaden the skill into adjacent jobs just because the examples are nearby.",
        ],
        "maturity_assumption": maturity,
    }


def build_feedback_loops(context: dict, intent: dict, output_profile: dict, synthesis: dict) -> list[dict]:
    confidence = intent_summary(intent).get("score", 0)
    risks = output_risk_labels(output_profile)
    patterns = reference_patterns(synthesis)
    return [
        {
            "name": "Intent boundary loop",
            "signal": f"Intent confidence score is {confidence}/100.",
            "response": "Ask only the highest-leverage clarification before adding package weight.",
            "evidence": "reports/intent-confidence.md and reports/intent-dialogue.md",
        },
        {
            "name": "Reference synthesis loop",
            "signal": "Benchmark patterns are useful only after they are abstracted into borrow and avoid guidance.",
            "response": "Borrow one pattern at a time and keep the rest as reviewer-visible evidence.",
            "evidence": "reports/reference-synthesis.md",
            "current_patterns": patterns,
        },
        {
            "name": "Output quality loop",
            "signal": "Generated output may fail in recurring domain-specific ways.",
            "response": "Apply predicted output-risk families as self-repair checks before final output.",
            "evidence": "reports/output-risk-profile.md",
            "current_risk_families": risks,
        },
        {
            "name": "Reviewer feedback loop",
            "signal": "Human review catches drift that static checks miss.",
            "response": "Capture lightweight feedback and turn repeated findings into gates or references.",
            "evidence": "reports/review-viewer.html and feedback records",
        },
        {
            "name": "Lifecycle loop",
            "signal": "As reuse grows, the skill needs stronger gates, ownership, and regression evidence.",
            "response": "Promote only when the next gate improves reliability more than context cost.",
            "evidence": "manifest.json, reports/iteration-directions.md, and governance checks",
        },
    ]


def build_drift_watch(manifest: dict, output_profile: dict) -> list[dict]:
    maturity = manifest.get("maturity_tier", "scaffold")
    risk_labels = output_risk_labels(output_profile)
    return [
        {
            "name": "Trigger drift",
            "watch_signal": "Users start invoking the skill for adjacent one-off or explanation-only requests.",
            "countermeasure": "Add near-neighbor exclusions and route evals before expanding workflow steps.",
            "cadence": "per trigger or description change",
        },
        {
            "name": "Output drift",
            "watch_signal": "Outputs remain valid but become generic, cluttered, or weakly aligned with the user's domain.",
            "countermeasure": "Refresh output-risk and artifact-design profiles, then add one self-repair check.",
            "cadence": "after the first 3-5 real uses",
            "risk_families": risk_labels,
        },
        {
            "name": "Reference drift",
            "watch_signal": "Borrowed benchmark patterns no longer fit the local job or add ceremony without payoff.",
            "countermeasure": "Re-run reference synthesis and keep only patterns that improve the current boundary.",
            "cadence": "per material benchmark or product assumption change",
        },
        {
            "name": "Governance drift",
            "watch_signal": "Skill usage becomes team-critical while ownership, review cadence, or rollback evidence stays informal.",
            "countermeasure": "Promote maturity tier and add reviewer-visible lifecycle evidence.",
            "cadence": "monthly" if maturity in {"production", "governed", "library"} else "when reuse becomes real",
        },
    ]


def build_failure_map(output_profile: dict, prompt_profile: dict) -> list[dict]:
    risks = output_risk_labels(output_profile)
    prompt_matrix = prompt_profile.get("quality_matrix", []) if isinstance(prompt_profile, dict) else []
    weak_prompt_axes = [
        str(item.get("label", "Prompt quality"))
        for item in prompt_matrix
        if isinstance(item, dict) and safe_int(item.get("score"), 100) < 80
    ][:3]
    return [
        {
            "family": "Boundary failure",
            "symptom": "The skill handles nearby requests that were never part of the recurring job.",
            "repair": "Narrow the description and add explicit non-goals before adding more execution steps.",
        },
        {
            "family": "Feedback gap",
            "symptom": "The skill has rules but no signal telling authors which rule should change after use.",
            "repair": "Turn repeated reviewer feedback into one eval, one reference note, or one self-repair check.",
        },
        {
            "family": "Output degradation",
            "symptom": "The result is structurally correct but generic, cluttered, or weakly matched to the user's domain.",
            "repair": "Use output-risk families as pre-final checks.",
            "current_risk_families": risks,
        },
        {
            "family": "Prompt-behavior mismatch",
            "symptom": "The role, task, and format are copied from a prompt instead of becoming stable skill behavior.",
            "repair": "Convert reusable role/task/format assumptions into workflow, reports, or references.",
            "watch_axes": weak_prompt_axes,
        },
    ]


def build_leverage_points(intent: dict, manifest: dict, output_profile: dict, synthesis: dict) -> list[dict]:
    confidence = intent_summary(intent).get("score", 0)
    maturity = manifest.get("maturity_tier", "scaffold")
    risks = output_risk_labels(output_profile)
    patterns = reference_patterns(synthesis)
    points = []
    if confidence < 80:
        points.append(
            {
                "rank": 1,
                "point": "Clarify the real job boundary",
                "why": "Intent uncertainty creates downstream trigger, output, and governance errors.",
                "move": "Ask one focused question and update intent context before adding assets.",
            }
        )
    points.append(
        {
            "rank": 2,
            "point": "Tune the frontmatter description",
            "why": "The description is the highest-leverage routing surface.",
            "move": "Name the recurring job, expected input, output, and strongest non-goal in compact language.",
        }
    )
    if risks:
        points.append(
            {
                "rank": 3,
                "point": "Install output self-repair checks",
                "why": f"The likely failure families are: {', '.join(risks[:3])}.",
                "move": "Add only the checks that prevent recurring output mistakes.",
            }
        )
    if patterns:
        points.append(
            {
                "rank": 4,
                "point": "Borrow one pattern, not a whole product",
                "why": "External references improve quality when reduced to structure, not copied as surface style.",
                "move": f"Start from: {patterns[0]}",
            }
        )
    if maturity in {"production", "governed", "library"}:
        points.append(
            {
                "rank": 5,
                "point": "Close the lifecycle loop",
                "why": "Team-reused skills need visible ownership, review cadence, and regression evidence.",
                "move": "Keep manifest, review viewer, and iteration directions aligned after each material change.",
            }
        )
    return points[:5]


def stability_score(intent: dict, manifest: dict, output_profile: dict, synthesis: dict) -> tuple[int, str]:
    confidence = intent_summary(intent).get("score", 0)
    maturity = manifest.get("maturity_tier", "scaffold")
    score = 55
    score += min(20, int(confidence / 5))
    score += 8 if output_profile.get("risk_families") else 0
    score += 8 if reference_patterns(synthesis) else 0
    score += 9 if maturity in {"production", "governed", "library"} else 4
    score = max(0, min(100, score))
    if score >= 90:
        band = "system-ready"
    elif score >= 75:
        band = "stable-first-pass"
    elif score >= 60:
        band = "needs-boundary-tuning"
    else:
        band = "fragile"
    return score, band


def build_system_model(skill_dir: Path) -> dict:
    skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    frontmatter, _body = parse_frontmatter(skill_text)
    manifest = load_json(skill_dir / "manifest.json")
    intent = load_json(skill_dir / "reports" / "intent-confidence.json")
    context = load_context(skill_dir)
    synthesis = load_json(skill_dir / "reports" / "reference-synthesis.json")
    output_profile = load_json(skill_dir / "reports" / "output-risk-profile.json")
    prompt_profile = load_json(skill_dir / "reports" / "prompt-quality-profile.json")
    description = str(frontmatter.get("description", ""))
    score, band = stability_score(intent, manifest, output_profile, synthesis)
    return {
        "skill_name": frontmatter.get("name", skill_dir.name),
        "description": description,
        "systems_doctrine": "Structure drives behavior: improve the boundary, feedback loops, drift watch, and leverage points before adding weight.",
        "stability": {
            "score": score,
            "band": band,
        },
        "boundary_map": build_boundary_map(description, context, manifest),
        "feedback_loops": build_feedback_loops(context, intent, output_profile, synthesis),
        "drift_watch": build_drift_watch(manifest, output_profile),
        "failure_pattern_map": build_failure_map(output_profile, prompt_profile),
        "leverage_points": build_leverage_points(intent, manifest, output_profile, synthesis),
        "reviewer_rule": "Reviewer should ask whether the skill's structure will keep producing the desired behavior after repeated real use.",
    }


def render_markdown(model: dict) -> str:
    boundary = model["boundary_map"]
    lines = [
        "# System Model",
        "",
        f"Skill: `{model['skill_name']}`",
        "",
        f"- Stability score: `{model['stability']['score']}/100`",
        f"- Stability band: `{model['stability']['band']}`",
        f"- Doctrine: {model['systems_doctrine']}",
        "",
        "## System Boundary Map",
        "",
        f"- Owned job: {boundary['owned_job']}",
        f"- Output boundary: {boundary['output_boundary']}",
        f"- Maturity assumption: `{boundary['maturity_assumption']}`",
        "- Input boundary:",
    ]
    lines.extend(f"  - {item}" for item in boundary["input_boundary"])
    lines.append("- Non-goals:")
    lines.extend(f"  - {item}" for item in boundary["non_goals"])
    if boundary["constraints"]:
        lines.append("- Constraints:")
        lines.extend(f"  - {item}" for item in boundary["constraints"])
    if boundary["standards"]:
        lines.append("- Standards:")
        lines.extend(f"  - {item}" for item in boundary["standards"])
    lines.append("- Human judgment boundary:")
    lines.extend(f"  - {item}" for item in boundary["human_judgment_boundary"])

    lines.extend(["", "## Feedback Loops", ""])
    for loop in model["feedback_loops"]:
        lines.extend(
            [
                f"### {loop['name']}",
                "",
                f"- Signal: {loop['signal']}",
                f"- Response: {loop['response']}",
                f"- Evidence: {loop['evidence']}",
            ]
        )
        if loop.get("current_patterns"):
            lines.append("- Current patterns:")
            lines.extend(f"  - {item}" for item in loop["current_patterns"])
        if loop.get("current_risk_families"):
            lines.append("- Current risk families:")
            lines.extend(f"  - {item}" for item in loop["current_risk_families"])
        lines.append("")

    lines.extend(["## Delay And Drift Watch", ""])
    for item in model["drift_watch"]:
        lines.extend(
            [
                f"### {item['name']}",
                "",
                f"- Watch signal: {item['watch_signal']}",
                f"- Countermeasure: {item['countermeasure']}",
                f"- Cadence: {item['cadence']}",
            ]
        )
        if item.get("risk_families"):
            lines.append("- Risk families:")
            lines.extend(f"  - {risk}" for risk in item["risk_families"])
        lines.append("")

    lines.extend(["## Failure Pattern Map", ""])
    for item in model["failure_pattern_map"]:
        lines.extend(
            [
                f"### {item['family']}",
                "",
                f"- Symptom: {item['symptom']}",
                f"- Repair: {item['repair']}",
            ]
        )
        for key in ("current_risk_families", "watch_axes"):
            if item.get(key):
                label = key.replace("_", " ").title()
                lines.append(f"- {label}:")
                lines.extend(f"  - {value}" for value in item[key])
        lines.append("")

    lines.extend(["## Highest Leverage Moves", ""])
    for point in model["leverage_points"]:
        lines.extend(
            [
                f"### {point['rank']}. {point['point']}",
                "",
                f"- Why: {point['why']}",
                f"- Move: {point['move']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Reviewer Use",
            "",
            f"- {model['reviewer_rule']}",
            "- Prefer changing the system boundary, feedback loop, or leverage point before adding more prose.",
            "- If a problem repeats, convert it into a named failure pattern and one regression check.",
            "",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def render_system_model(skill_dir: Path, output_md: Path | None = None, output_json: Path | None = None) -> dict:
    skill_dir = skill_dir.resolve()
    reports_dir = skill_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_md = output_md or reports_dir / "system-model.md"
    output_json = output_json or reports_dir / "system-model.json"
    model = build_system_model(skill_dir)
    output_md.write_text(render_markdown(model), encoding="utf-8")
    output_json.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "ok": True,
        "skill_dir": str(skill_dir),
        "artifacts": {
            "markdown": str(output_md),
            "json": str(output_json),
        },
        "summary": {
            "skill_name": model["skill_name"],
            "stability": model["stability"],
            "leverage_points": model["leverage_points"][:3],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a systems-thinking model for a skill package.")
    parser.add_argument("skill_dir", nargs="?", default=".")
    parser.add_argument("--output-md")
    parser.add_argument("--output-json")
    args = parser.parse_args()
    result = render_system_model(
        Path(args.skill_dir),
        Path(args.output_md).resolve() if args.output_md else None,
        Path(args.output_json).resolve() if args.output_json else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
