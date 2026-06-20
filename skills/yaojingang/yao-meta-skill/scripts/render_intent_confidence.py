#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


GENERIC_PHRASES = {
    "turn a repeated workflow into a reusable skill",
    "a reusable skill package",
    "describe what the skill does and when to use it",
    "turn rough requests into a compact reusable demo skill",
}

GENERIC_TOKENS = {
    "workflow",
    "skill",
    "package",
    "reusable",
    "repeated",
    "request",
    "requests",
    "task",
    "tasks",
    "work",
    "job",
}

FOLLOW_UP_LIBRARY = {
    "job_specificity": {
        "slot": "job",
        "question": "If you say it plainly, what concrete repeated task should this skill own every time?",
        "why": "A skill needs a real recurring job, not only a generic packaging goal.",
        "list": False,
    },
    "real_inputs": {
        "slot": "real_inputs",
        "question": "What material will people actually hand to this skill in practice?",
        "why": "Real input shape decides whether references, scripts, or examples are needed.",
        "list": True,
    },
    "primary_output": {
        "slot": "primary_output",
        "question": "What finished hand-back should this skill return so the next person can keep moving?",
        "why": "The output is the anchor for package design and review.",
        "list": False,
    },
    "exclusions": {
        "slot": "exclusions",
        "question": "What nearby requests should this skill clearly leave out so the boundary stays clean?",
        "why": "Exclusions are the fastest route to better trigger quality.",
        "list": True,
    },
    "constraints": {
        "slot": "constraints",
        "question": "What constraints matter most here: privacy, naming, compatibility, portability, governance, or speed?",
        "why": "Constraints decide how much structure and validation this skill really needs.",
        "list": True,
    },
    "standards": {
        "slot": "standards",
        "question": "What quality bar matters most here: consistency, auditability, tone, or delivery speed?",
        "why": "Standards explain how to choose the first evaluation gate.",
        "list": True,
    },
}


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


def normalized_list(value: list[str] | str | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        parts = [item.strip() for item in value.split(",")]
        return [item for item in parts if item]
    return [str(item).strip() for item in value if str(item).strip()]


def tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", text.lower())


def is_generic(text: str) -> bool:
    compact = " ".join(text.lower().split())
    if not compact:
        return True
    if compact in GENERIC_PHRASES:
        return True
    tokens = tokenize(compact)
    if len(tokens) <= 3:
        return True
    content_tokens = [token for token in tokens if token not in GENERIC_TOKENS]
    return len(content_tokens) < 2


def build_context_from_skill(skill_dir: Path) -> dict[str, Any]:
    skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    frontmatter, _ = parse_frontmatter(skill_text)
    payload = load_json(skill_dir / "reports" / "intent-context.json")
    if payload:
        return payload
    return {
        "job": frontmatter.get("description", ""),
        "real_inputs": [],
        "primary_output": "",
        "description": frontmatter.get("description", ""),
        "exclusions": [],
        "constraints": [],
        "standards": [],
        "correction": "",
        "user_references": [],
    }


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def assess_intent_confidence(context: dict[str, Any]) -> dict[str, Any]:
    job = str(context.get("job", "")).strip()
    primary_output = str(context.get("primary_output", "")).strip()
    description = str(context.get("description", "")).strip()
    real_inputs = normalized_list(context.get("real_inputs"))
    exclusions = normalized_list(context.get("exclusions"))
    constraints = normalized_list(context.get("constraints"))
    standards = normalized_list(context.get("standards"))
    user_references = normalized_list(context.get("user_references"))
    correction = str(context.get("correction", "")).strip()

    score = 0
    strengths = []
    gaps = []

    def add_gap(key: str, label: str, reason: str, severity: str = "high") -> None:
        gaps.append({"key": key, "label": label, "reason": reason, "severity": severity})

    if job and not is_generic(job):
        score += 25
        strengths.append("The recurring job is concrete enough to anchor the package.")
    elif job:
        score += 10
        add_gap(
            "job_specificity",
            "Recurring job is still generic",
            "The current job statement sounds more like a packaging goal than a concrete repeated task.",
        )
    else:
        add_gap("job_specificity", "Recurring job is missing", "The package has no clear job-to-be-done anchor yet.")

    if real_inputs:
        score += 15
        strengths.append("Real input shape is explicit.")
    else:
        add_gap("real_inputs", "Real inputs are missing", "Without real inputs, it is hard to choose assets, scripts, or examples.")

    if primary_output and not is_generic(primary_output):
        score += 20
        strengths.append("The hand-back output is concrete.")
    elif primary_output:
        score += 8
        add_gap(
            "primary_output",
            "Primary output is still generic",
            "The current output does not yet say what a useful finished deliverable looks like.",
        )
    else:
        add_gap("primary_output", "Primary output is missing", "The package does not yet know what it must hand back.")

    if exclusions:
        score += 15
        strengths.append("Boundary exclusions are already explicit.")
    else:
        add_gap("exclusions", "Near-neighbor exclusions are missing", "The route may blur into nearby requests without an exclusion list.")

    if constraints:
        score += 10
        strengths.append("Operational constraints are visible.")
    else:
        add_gap("constraints", "Constraints are missing", "The package does not yet know which tradeoffs matter most.")

    if standards:
        score += 5
        strengths.append("Quality standards are visible.")
    else:
        add_gap("standards", "Quality bar is implied, not explicit", "The first evaluation target is still underspecified.", "medium")

    if correction:
        score += 5
        strengths.append("A correction loop already tightened the first reading.")

    if user_references:
        score += 5
        strengths.append("Reference preferences are already available.")

    if description and not is_generic(description):
        score += 5

    score = min(score, 100)
    if score >= 85:
        band = "high"
    elif score >= 70:
        band = "medium"
    else:
        band = "low"

    gate_passed = score >= 70 and not any(
        gap["key"] in {"job_specificity", "real_inputs", "primary_output"} and gap["severity"] == "high"
        for gap in gaps
    )
    follow_up_questions = [
        {
            **FOLLOW_UP_LIBRARY[gap["key"]],
            "label": gap["label"],
            "severity": gap["severity"],
        }
        for gap in gaps
        if gap["key"] in FOLLOW_UP_LIBRARY
    ][:3]

    anchor_sentence = " ".join(
        item
        for item in [
            job or "Unclear recurring job.",
            f"Primary output: {primary_output}." if primary_output else "",
            f"Exclusions: {', '.join(exclusions)}." if exclusions else "",
        ]
        if item
    ).strip()

    return {
        "score": score,
        "band": band,
        "gate_passed": gate_passed,
        "strengths": strengths[:5],
        "gaps": gaps,
        "follow_up_questions": follow_up_questions,
        "anchor_sentence": anchor_sentence,
        "recommended_action": (
            "Intent is clear enough to package the first routeable version."
            if gate_passed
            else "Pause before deep authoring and close the highest-leverage gaps first."
        ),
        "context": {
            "job": job,
            "real_inputs": real_inputs,
            "primary_output": primary_output,
            "description": description,
            "exclusions": exclusions,
            "constraints": constraints,
            "standards": standards,
            "correction": correction,
            "user_references": user_references,
        },
    }


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Intent Confidence",
        "",
        f"- Confidence score: `{summary['score']}/100`",
        f"- Confidence band: `{summary['band']}`",
        f"- Gate passed: `{summary['gate_passed']}`",
        f"- Recommended action: {summary['recommended_action']}",
        "",
        "## Current Reading",
        "",
        summary["anchor_sentence"] or "No clear anchor sentence yet.",
        "",
        "## Strong Signals",
        "",
    ]
    if summary["strengths"]:
        for item in summary["strengths"]:
            lines.append(f"- {item}")
    else:
        lines.append("- No strong signals yet.")

    lines.extend(["", "## Gaps To Close", ""])
    if summary["gaps"]:
        for gap in summary["gaps"]:
            lines.append(f"- **{gap['label']}** (`{gap['severity']}`): {gap['reason']}")
    else:
        lines.append("- No major intent gaps detected.")

    lines.extend(["", "## Follow-Up Questions", ""])
    if summary["follow_up_questions"]:
        for item in summary["follow_up_questions"]:
            lines.append(f"- **{item['question']}**")
            lines.append(f"  - Why: {item['why']}")
    else:
        lines.append("- No extra follow-up questions required before the first package.")
    return "\n".join(lines).strip() + "\n"


def render_intent_confidence(
    skill_dir: Path,
    context: dict[str, Any] | None = None,
    output_md: Path | None = None,
    output_json: Path | None = None,
    context_json: Path | None = None,
) -> dict[str, Any]:
    skill_dir = skill_dir.resolve()
    reports_dir = skill_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_md = output_md or reports_dir / "intent-confidence.md"
    output_json = output_json or reports_dir / "intent-confidence.json"
    context_json = context_json or reports_dir / "intent-context.json"

    context_payload = context or build_context_from_skill(skill_dir)
    summary = assess_intent_confidence(context_payload)
    output_md.write_text(render_markdown(summary), encoding="utf-8")
    output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    context_json.write_text(json.dumps(summary["context"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "skill_dir": str(skill_dir),
        "artifacts": {
            "markdown": str(output_md),
            "json": str(output_json),
            "context_json": str(context_json),
        },
        "summary": summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Render an intent confidence report for a skill package.")
    parser.add_argument("skill_dir", nargs="?", default=".")
    parser.add_argument("--context-json")
    parser.add_argument("--output-md")
    parser.add_argument("--output-json")
    args = parser.parse_args()

    context = None
    if args.context_json:
        context = load_json(Path(args.context_json).resolve())

    result = render_intent_confidence(
        Path(args.skill_dir),
        context=context,
        output_md=Path(args.output_md).resolve() if args.output_md else None,
        output_json=Path(args.output_json).resolve() if args.output_json else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
