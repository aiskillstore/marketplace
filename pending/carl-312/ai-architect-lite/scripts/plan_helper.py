"""Minimal plan helper for new developers.

Outputs a tiny plan template with goal, constraints, steps, and validation.
Use stdout by default to avoid extra files; optionally write to a file.

Type Annotations: Fully annotated for Python 3.8+ compatibility using PEP 484/563.
All functions have complete parameter and return type annotations.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a tiny execution plan template")
    parser.add_argument("--goal", help="What you want to achieve")
    parser.add_argument("--constraints", help="Key constraints or guardrails")
    parser.add_argument(
        "--steps",
        help="Comma-separated steps (e.g., 'draft,implement,verify'); leave blank to fill manually",
    )
    parser.add_argument("--validation", help="How to verify (command or checklist)")
    parser.add_argument(
        "--out",
        default="-",
        help="Output path; use '-' (default) to print to stdout.",
    )
    return parser.parse_args()


def build_plan(goal: str | None, constraints: str | None, steps: str | None, validation: str | None) -> str:
    steps_lines = []
    if steps:
        for idx, item in enumerate(steps.split(","), start=1):
            item = item.strip()
            if item:
                steps_lines.append(f"- Step {idx}: {item}")
    if not steps_lines:
        steps_lines = ["- Step 1: (Please fill in)", "- Step 2: (Optional)", "- Step 3: (Optional)"]

    body = [
        "# Mini Plan",
        "## Goal",
        f"- {goal or '(Please fill in)'}",
        "",
        "## Constraints",
        f"- {constraints or '(Optional/Please fill in)'}",
        "",
        "## Steps (<=5)",
        *steps_lines,
        "",
        "## Validation",
        f"- {validation or '(Command/Checklist/Expected result)'}",
        "",
    ]
    return "\n".join(body)


def main() -> None:
    args = parse_args()
    plan_text = build_plan(args.goal, args.constraints, args.steps, args.validation)

    if args.out == "-" or args.out.strip() == "":
        print(plan_text)
    else:
        # Security: Validate output path
        try:
            out_path = Path(args.out).expanduser().resolve(strict=False)
        except (OSError, RuntimeError) as e:
            print(f"Error: Invalid output path - {e}")
            return
        
        # Security: Prevent path traversal - ensure path doesn't contain suspicious patterns
        path_str = str(out_path)
        if ".." in path_str.split(out_path.anchor)[-1]:
            print(f"Error: Path traversal detected in output path")
            return
        
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(plan_text, encoding="utf-8")
        print(f"Wrote plan to {out_path}")


if __name__ == "__main__":
    main()
