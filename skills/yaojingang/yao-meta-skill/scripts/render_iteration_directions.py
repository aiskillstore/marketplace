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


def load_manifest(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def extract_sections(body: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current = "_preamble"
    sections[current] = []
    for line in body.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
            continue
        sections[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def section_text(sections: dict[str, str], *names: str) -> str:
    lowered = {key.lower(): value for key, value in sections.items()}
    for name in names:
        if name.lower() in lowered:
            return lowered[name.lower()]
    return ""


def has_any_files(path: Path) -> bool:
    return path.exists() and any(path.iterdir())


def direction(priority: int, title: str, why: str, actions: list[str], unlocks: str) -> dict:
    return {
        "priority": priority,
        "title": title,
        "why": why,
        "actions": actions,
        "unlocks": unlocks,
        "do_now": "",
        "wait_on": "",
    }


def build_directions(skill_dir: Path) -> tuple[dict, list[dict]]:
    skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(skill_text)
    sections = extract_sections(body)
    manifest = load_manifest(skill_dir / "manifest.json")
    benchmark = load_json(skill_dir / "reports" / "github-benchmark-scan.json")
    description = frontmatter.get("description", "")
    maturity = manifest.get("maturity_tier", "scaffold")

    candidates: list[dict] = []
    if "Do not use" not in body and "exclusion" not in body.lower():
        candidates.append(
            direction(
                1,
                "Tighten trigger and exclusions",
                "The package needs clearer near-neighbor exclusions before it grows.",
                [
                    "Add 3 to 5 should-trigger and should-not-trigger examples.",
                    "Refine the frontmatter description to name the recurring job and non-goals.",
                    "Run a first trigger evaluation pass before expanding the package.",
                ],
                "Cleaner routing and fewer accidental activations.",
            )
        )
    if not has_any_files(skill_dir / "references") or not has_any_files(skill_dir / "scripts"):
        candidates.append(
            direction(
                2,
                "Add the first execution asset",
                "The package is still mostly prose. Add one asset that removes repeated manual work.",
                [
                    "Move stable procedural guidance into references if users will need it repeatedly.",
                    "Create one deterministic helper script if a repeated step can be executed instead of described.",
                    "Keep the main SKILL.md compact and route-oriented.",
                ],
                "Stronger execution quality without bloating the entrypoint.",
            )
        )
    if benchmark.get("repositories"):
        top_repo = benchmark["repositories"][0]
        candidates.append(
            direction(
                2,
                "Borrow one proven pattern on purpose",
                "You already have public benchmark objects. The next gain is to choose one pattern intentionally instead of absorbing everything loosely.",
                [
                    f"Read the strongest pattern from {top_repo.get('full_name', 'the top benchmark repo')}.",
                    "Decide whether to borrow method, structure, execution, or portability, but only one of them first.",
                    "Record what you will not borrow so the package stays light.",
                ],
                "A cleaner package shape with less accidental over-design.",
            )
        )
    if maturity == "scaffold":
        candidates.append(
            direction(
                3,
                "Promote from scaffold to production-ready",
                "The first version exists; the next gain usually comes from adding the smallest useful gates.",
                [
                    "Decide whether this skill is personal, team-reused, or library-grade.",
                    "Add only the gates that match that risk level.",
                    "Record lifecycle metadata and review cadence once reuse becomes real.",
                ],
                "A clearer path from exploratory package to maintained asset.",
            )
        )
    workflow_section = section_text(sections, "Workflow", "Compact Workflow", "How To Use")
    if workflow_section and len(workflow_section) < 120:
        candidates.append(
            direction(
                4,
                "Deepen operator guidance",
                "The workflow is still thin and may not be repeatable by another operator.",
                [
                    "Split the job into distinct phases or checkpoints.",
                    "Add success conditions and failure boundaries for each phase.",
                    "Link outputs to the step that produces them.",
                ],
                "Better repeatability and easier human review.",
            )
        )
    if "portable" in description.lower() or "package" in description.lower():
        candidates.append(
            direction(
                5,
                "Harden portability semantics",
                "The skill already signals reuse across environments, so contract clarity matters early.",
                [
                    "Confirm activation mode, execution context, and trust assumptions.",
                    "Add or review degradation strategy for non-native targets.",
                    "Package the skill once to verify adapter expectations.",
                ],
                "Safer cross-environment reuse with less target drift.",
            )
        )

    if len(candidates) < 3:
        candidates.append(
            direction(
                len(candidates) + 10,
                "Create an iteration evidence loop",
                "The package should show what changed and why after the first draft.",
                [
                    "Generate the HTML skill report and keep it aligned with the package.",
                    "Record reference scan choices and non-goals.",
                    "Capture the next iteration choice explicitly before adding more files.",
                ],
                "A clearer path for the next author or reviewer.",
            )
        )

    chosen = sorted(candidates, key=lambda item: item["priority"])[:3]
    for index, item in enumerate(chosen, start=1):
        item["do_now"] = (
            "Do this first."
            if index == 1
            else "Do this after the first move lands cleanly."
        )
        item["wait_on"] = (
            "Wait to add broader structure until this move clearly improves reliability."
            if index == 1
            else "Wait until the package has evidence that this extra structure is justified."
        )
    summary = {
        "skill_name": frontmatter.get("name", skill_dir.name),
        "description": description,
        "maturity_tier": maturity,
        "selection_rule": "Pick the three smallest next steps that increase reliability more than they increase context cost.",
        "recommended_now": chosen[0]["title"] if chosen else "",
        "recommended_now_why": chosen[0]["why"] if chosen else "",
        "defer_for_now": chosen[-1]["title"] if chosen else "",
    }
    return summary, chosen


def render_markdown(summary: dict, directions: list[dict]) -> str:
    lines = [
        "# Iteration Directions",
        "",
        f"Skill: `{summary['skill_name']}`",
        "",
        f"- Maturity tier: `{summary['maturity_tier']}`",
        f"- Selection rule: {summary['selection_rule']}",
        f"- Start here: `{summary['recommended_now']}`",
        f"- Why first: {summary['recommended_now_why']}",
        f"- Defer for now: `{summary['defer_for_now']}`",
        "",
        "## Top 3 Next Moves",
        "",
    ]
    for item in directions:
        lines.extend(
            [
                f"### {item['priority']}. {item['title']}",
                "",
                f"- Why now: {item['why']}",
                f"- Timing: {item['do_now']}",
                "- Recommended actions:",
            ]
        )
        for action in item["actions"]:
            lines.append(f"  - {action}")
            lines.append(f"- Unlocks: {item['unlocks']}")
            lines.append(f"- Wait on: {item['wait_on']}")
            lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_iteration_directions(skill_dir: Path, output_md: Path | None = None, output_json: Path | None = None) -> dict:
    skill_dir = skill_dir.resolve()
    reports_dir = skill_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_md = output_md or reports_dir / "iteration-directions.md"
    output_json = output_json or reports_dir / "iteration-directions.json"

    summary, directions = build_directions(skill_dir)
    payload = {"summary": summary, "directions": directions}
    output_md.write_text(render_markdown(summary, directions), encoding="utf-8")
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "ok": True,
        "skill_dir": str(skill_dir),
        "artifacts": {
            "markdown": str(output_md),
            "json": str(output_json),
        },
        **payload,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the top three next iteration directions for a skill package.")
    parser.add_argument("skill_dir", nargs="?", default=".")
    parser.add_argument("--output-md")
    parser.add_argument("--output-json")
    args = parser.parse_args()
    result = render_iteration_directions(
        Path(args.skill_dir),
        output_md=Path(args.output_md).resolve() if args.output_md else None,
        output_json=Path(args.output_json).resolve() if args.output_json else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
