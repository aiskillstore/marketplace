#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""
Extract known issues across all features.

Usage:
    ./extract-issues.py [--format plain|markdown|json]
"""

import argparse
import json
import sys
from pathlib import Path

import yaml


def load_features(path: Path) -> list[dict]:
    """Load all feature documents from features.yml."""
    if not path.exists():
        print(f"Error: {path} not found", file=sys.stderr)
        sys.exit(1)

    with open(path) as f:
        docs = list(yaml.safe_load_all(f))

    return [doc for doc in docs if doc is not None]


def format_plain(features: list[dict]) -> str:
    """Format output as plain text."""
    lines = []
    found_any = False

    for f in features:
        name = f.get("feature", "Unnamed")
        version = f.get("version", 1)
        phase = f.get("phase", "Unknown")
        issues = f.get("known-issues", [])

        if not issues:
            continue

        found_any = True
        lines.append(f"{name} (v{version}, {phase})")
        for issue in issues:
            if issue:  # Skip empty strings
                lines.append(f"  - {issue}")
        lines.append("")

    if not found_any:
        return "No known issues found."

    return "\n".join(lines).rstrip()


def format_markdown(features: list[dict]) -> str:
    """Format output as markdown."""
    lines = []
    lines.append("# Known Issues")

    found_any = False
    for f in features:
        name = f.get("feature", "Unnamed")
        version = f.get("version", 1)
        phase = f.get("phase", "Unknown")
        issues = f.get("known-issues", [])

        # Filter out empty issues
        issues = [i for i in issues if i]

        if not issues:
            continue

        found_any = True
        lines.append("")
        lines.append(f"## {name} (v{version}, {phase})")
        lines.append("")
        for issue in issues:
            lines.append(f"- {issue}")

    if not found_any:
        lines.append("")
        lines.append("No known issues found.")

    return "\n".join(lines)


def format_json(features: list[dict]) -> str:
    """Format output as JSON."""
    output = {"features": []}

    for f in features:
        name = f.get("feature", "Unnamed")
        version = f.get("version", 1)
        phase = f.get("phase", "Unknown")
        issues = f.get("known-issues", [])

        # Filter out empty issues
        issues = [i for i in issues if i]

        if not issues:
            continue

        output["features"].append(
            {"name": name, "version": version, "phase": phase, "issues": issues}
        )

    return json.dumps(output, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Extract known issues across all features"
    )
    parser.add_argument(
        "--format",
        choices=["plain", "markdown", "json"],
        default="plain",
        help="Output format (default: plain)",
    )
    args = parser.parse_args()

    features = load_features(Path("features.yml"))

    if not features:
        print("No features found in features.yml", file=sys.stderr)
        sys.exit(1)

    if args.format == "plain":
        print(format_plain(features))
    elif args.format == "markdown":
        print(format_markdown(features))
    else:
        print(format_json(features))


if __name__ == "__main__":
    main()
