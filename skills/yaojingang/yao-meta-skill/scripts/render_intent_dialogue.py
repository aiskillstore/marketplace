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


def classify_focus(description: str) -> str:
    lowered = description.lower()
    if any(token in lowered for token in ["review", "audit", "incident", "risk", "govern"]):
        return "quality-and-boundary"
    if any(token in lowered for token in ["export", "package", "adapter", "client", "portable"]):
        return "portability-and-contract"
    if any(token in lowered for token in ["workflow", "coordinate", "orchestrate", "process"]):
        return "execution-and-assets"
    return "trigger-and-output"


def build_questions(focus: str) -> list[dict]:
    base = [
        {
            "question": "If this skill worked beautifully, what recurring job would it reliably handle for the user every time?",
            "why": "This reveals the real job-to-be-done and gives the package a humane center instead of a guessed prompt shape.",
        },
        {
            "question": "When someone reaches for this skill in the real world, what materials will they actually hand to it?",
            "why": "Input shape decides whether references, scripts, or templates are needed.",
        },
        {
            "question": "What finished output should it hand back so the user can immediately keep moving?",
            "why": "Outputs should drive the package structure before extra guidance is added.",
        },
        {
            "question": "Which nearby requests should this skill politely refuse so the boundary stays clean?",
            "why": "The exclusion list is the fastest route to better trigger quality.",
        },
        {
            "question": "What matters most here: speed, consistency, auditability, portability, governance, or tone/style fit?",
            "why": "Constraints decide how much structure, packaging, and review the skill actually needs.",
        },
        {
            "question": "Do you already have any references you want this skill to learn from, such as a repo, product, page, workflow, or prompt example?",
            "why": "A good reference can raise the quality bar quickly, but the skill should only borrow patterns and standards, never copy wording or confidential material.",
        },
    ]
    if focus == "quality-and-boundary":
        base.append(
            {
                "question": "What failure would make this skill untrustworthy in practice?",
                "why": "The answer usually reveals the first evaluation gate worth adding.",
            }
        )
    elif focus == "portability-and-contract":
        base.append(
            {
                "question": "Which environments or clients must be able to consume this skill?",
                "why": "This sets the minimum metadata and degradation strategy.",
            }
        )
    else:
        base.append(
            {
                "question": "What repeated manual step should become a deterministic asset first?",
                "why": "This usually reveals whether a script or reference should be created next.",
            }
        )
    return base


def build_opening_styles() -> list[dict]:
    return [
        {
            "label": "温柔陪伴型",
            "best_when": "用户想法还散、还在试探，或者需要先被接住。",
            "message": "我们先不急着把它说成一个很完整的 skill。你就像跟我聊天一样，先说说你最想让它以后稳稳接住哪类重复工作；如果它做得很理想，最后应该交回你一个什么结果。",
        },
        {
            "label": "专业教练型",
            "best_when": "用户目标比较明确，希望被高效带着走。",
            "message": "我们先把这件事讲清楚，再决定 skill 怎么设计。你先告诉我三件事：它要接住的重复任务是什么，别人通常会给它什么材料，最后你希望它交付什么结果。",
        },
        {
            "label": "共创伙伴型",
            "best_when": "用户已经有一些想法，希望一起打磨，不想被填表。",
            "message": "我们把这次当成一次共创。你先给我一个粗糙版本就行，我先帮你看它真正的核心任务是什么，再一起决定边界、结构和接下来最值的一步。",
        },
    ]


def build_summary(skill_dir: Path) -> dict:
    skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(skill_text)
    name = frontmatter.get("name", skill_dir.name)
    description = frontmatter.get("description", "No description found.")
    title = extract_title(body, name.replace("-", " ").title())
    focus = classify_focus(description)
    questions = build_questions(focus)
    opening_styles = build_opening_styles()
    output = {
        "capability_sentence": f"{title} should turn a recurring request into a reliable reusable output without widening the boundary unnecessarily.",
        "required_capture": [
            "recurring job",
            "real inputs",
            "required outputs",
            "exclusions",
            "constraints",
            "reference preferences",
            "first evaluation target",
        ],
        "recommended_first_gate": "trigger and boundary" if focus != "portability-and-contract" else "portability and contract",
    }
    return {
        "skill_name": name,
        "title": title,
        "description": description,
        "focus": focus,
        "opening_frame": "Let's start from the real work, the result you care about, and the standards that matter here. We can make the structure clearer after that.",
        "reference_note": "If you already have examples you admire, bring them in. We will learn the pattern, not copy the source.",
        "conversation_path": [
            "Start with the user's own words, not package vocabulary.",
            "Reflect the job, output, and non-goals back in one clean sentence.",
            "Only then offer a tiny scaffold if it would help the user move faster.",
        ],
        "opening_styles": opening_styles,
        "optional_scaffold": [
            "The repeated job it should reliably handle",
            "The real inputs people will hand to it",
            "The useful output it should hand back",
            "What it should clearly refuse",
        ],
        "questions": questions,
        "output": output,
    }


def render_markdown(summary: dict) -> str:
    lines = [
        "# Intent Dialogue",
        "",
        f"Skill: `{summary['skill_name']}`",
        "",
        "## Opening Frame",
        "",
        summary["opening_frame"],
        "",
        "## Opening Tone Options",
        "",
    ]
    for item in summary["opening_styles"]:
        lines.extend(
            [
                f"### {item['label']}",
                "",
                f"- Best when: {item['best_when']}",
                f"- Example: {item['message']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Conversation Path",
            "",
        ]
    )
    for idx, item in enumerate(summary["conversation_path"], start=1):
        lines.append(f"{idx}. {item}")
    lines.extend(
        [
            "",
            "## Why Start Here",
            "",
            "Use this short dialogue before deep authoring. The goal is to learn the real job, output, exclusions, and constraints so the first package is small but accurate.",
            "",
            "## Current Anchor",
            "",
            f"- Title: `{summary['title']}`",
            f"- Description: {summary['description']}",
            f"- Focus: `{summary['focus']}`",
            f"- Reference note: {summary['reference_note']}",
            "",
            "## Questions To Ask",
            "",
        ]
    )
    for idx, item in enumerate(summary["questions"], start=1):
        lines.extend(
            [
                f"{idx}. {item['question']}",
                f"   Why: {item['why']}",
            ]
        )
    lines.extend(
        [
            "",
            "## Capture Before Drafting",
            "",
            f"- Capability sentence: {summary['output']['capability_sentence']}",
            f"- Recommended first gate: `{summary['output']['recommended_first_gate']}`",
            "- Tiny optional scaffold:",
        ]
    )
    for item in summary["optional_scaffold"]:
        lines.append(f"  - {item}")
    for item in summary["output"]["required_capture"]:
        lines.append(f"- Capture: `{item}`")
    return "\n".join(lines).strip() + "\n"


def render_intent_dialogue(skill_dir: Path, output_md: Path | None = None, output_json: Path | None = None) -> dict:
    skill_dir = skill_dir.resolve()
    reports_dir = skill_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_md = output_md or reports_dir / "intent-dialogue.md"
    output_json = output_json or reports_dir / "intent-dialogue.json"

    summary = build_summary(skill_dir)
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
    parser = argparse.ArgumentParser(description="Render an intent dialogue guide for a skill package.")
    parser.add_argument("skill_dir", nargs="?", default=".")
    parser.add_argument("--output-md")
    parser.add_argument("--output-json")
    args = parser.parse_args()
    result = render_intent_dialogue(
        Path(args.skill_dir),
        output_md=Path(args.output_md).resolve() if args.output_md else None,
        output_json=Path(args.output_json).resolve() if args.output_json else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
