#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""
Extract requirements that need work (status != Complete).

Usage:
    ./extract-work.py [--format plain|markdown|json] [--phase PHASE] [--status STATUS]
"""

import argparse
import json
import sys
from pathlib import Path

import yaml


PHASES = ["Requirements", "Design", "Implementation", "Testing", "Complete"]
STATUSES = ["Not-Started", "In-Progress", "Needs-Work", "Complete"]


def load_features(path: Path) -> list[dict]:
    """Load all feature documents from features.yml."""
    if not path.exists():
        print(f"Error: {path} not found", file=sys.stderr)
        sys.exit(1)

    with open(path) as f:
        docs = list(yaml.safe_load_all(f))

    return [doc for doc in docs if doc is not None]


def get_incomplete_requirements(
    feature: dict, phase_filter: str | None, status_filter: str | None
) -> list[dict]:
    """Get requirements that are not Complete, with optional filters."""
    requirements = feature.get("requirements", {})
    feature_phase = feature.get("phase", "Requirements")

    # Apply phase filter
    if phase_filter and feature_phase != phase_filter:
        return []

    incomplete = []
    for req_id, req in requirements.items():
        status = req.get("status", "Not-Started")

        # Skip Complete unless explicitly filtered
        if status_filter:
            if status != status_filter:
                continue
        else:
            if status == "Complete":
                continue

        incomplete.append(
            {
                "id": req_id,
                "description": req.get("description", ""),
                "status": status,
                "tested_by": req.get("tested-by", []),
            }
        )

    return incomplete


def format_plain(
    features: list[dict], phase_filter: str | None, status_filter: str | None
) -> str:
    """Format output as plain text."""
    lines = []

    for f in features:
        name = f.get("feature", "Unnamed")
        phase = f.get("phase", "Unknown")
        incomplete = get_incomplete_requirements(f, phase_filter, status_filter)

        if not incomplete:
            continue

        lines.append(f"{name} ({phase})")
        for req in incomplete:
            desc = req["description"]
            if len(desc) > 60:
                desc = desc[:57] + "..."
            lines.append(f"  - {req['id']} [{req['status']}]: {desc}")
        lines.append("")

    if not lines:
        return "No incomplete requirements found."

    return "\n".join(lines).rstrip()


def format_markdown(
    features: list[dict], phase_filter: str | None, status_filter: str | None
) -> str:
    """Format output as markdown."""
    lines = []
    lines.append("# Work Remaining")

    found_any = False
    for f in features:
        name = f.get("feature", "Unnamed")
        phase = f.get("phase", "Unknown")
        incomplete = get_incomplete_requirements(f, phase_filter, status_filter)

        if not incomplete:
            continue

        found_any = True
        lines.append("")
        lines.append(f"## {name} ({phase})")
        lines.append("")
        for req in incomplete:
            status_badge = f"`{req['status']}`"
            lines.append(f"- [ ] **{req['id']}** {status_badge}")
            lines.append(f"  - {req['description']}")
            if req["tested_by"]:
                lines.append(f"  - Tests: {', '.join(req['tested_by'])}")

    if not found_any:
        lines.append("")
        lines.append("No incomplete requirements found.")

    return "\n".join(lines)


def format_json(
    features: list[dict], phase_filter: str | None, status_filter: str | None
) -> str:
    """Format output as JSON."""
    output = {"features": []}

    for f in features:
        name = f.get("feature", "Unnamed")
        phase = f.get("phase", "Unknown")
        incomplete = get_incomplete_requirements(f, phase_filter, status_filter)

        if not incomplete:
            continue

        output["features"].append(
            {"name": name, "phase": phase, "incomplete_requirements": incomplete}
        )

    return json.dumps(output, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Extract requirements needing work")
    parser.add_argument(
        "--format",
        choices=["plain", "markdown", "json"],
        default="plain",
        help="Output format (default: plain)",
    )
    parser.add_argument(
        "--phase", choices=PHASES, default=None, help="Filter to specific phase"
    )
    parser.add_argument(
        "--status",
        choices=STATUSES,
        default=None,
        help="Filter to specific status (default: all except Complete)",
    )
    args = parser.parse_args()

    features = load_features(Path("features.yml"))

    if not features:
        print("No features found in features.yml", file=sys.stderr)
        sys.exit(1)

    if args.format == "plain":
        print(format_plain(features, args.phase, args.status))
    elif args.format == "markdown":
        print(format_markdown(features, args.phase, args.status))
    else:
        print(format_json(features, args.phase, args.status))


if __name__ == "__main__":
    main()
