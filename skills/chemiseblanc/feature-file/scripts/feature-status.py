#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""
Feature status overview with validation and test breakdown.

Usage:
    ./feature-status.py [--format plain|markdown|json] [--validate]
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


def validate_feature(feature: dict) -> list[str]:
    """Validate phase transition rules for a feature. Returns list of errors."""
    errors = []
    phase = feature.get("phase", "Requirements")
    requirements = feature.get("requirements", {})
    decisions = feature.get("decisions")
    test_cases = feature.get("test-cases", {})

    phase_idx = PHASES.index(phase) if phase in PHASES else 0

    # Requirements -> Design: all requirements need descriptions
    if phase_idx >= PHASES.index("Design"):
        for req_id, req in requirements.items():
            desc = req.get("description", "")
            if not desc or not desc.strip():
                errors.append(
                    f"{req_id} missing description (required for Design phase)"
                )

    # Design -> Implementation: need at least one decision or explicit empty list
    if phase_idx >= PHASES.index("Implementation"):
        if decisions is None:
            errors.append(
                "No decisions field (required for Implementation phase, use [] if none needed)"
            )

    # Implementation -> Testing: all requirements must be In-Progress or Complete
    if phase_idx >= PHASES.index("Testing"):
        for req_id, req in requirements.items():
            status = req.get("status", "Not-Started")
            if status == "Not-Started":
                errors.append(
                    f"{req_id} is Not-Started (must be In-Progress or Complete for Testing phase)"
                )

    # Testing -> Complete: all requirements Complete and all tests passing
    if phase_idx >= PHASES.index("Complete"):
        for req_id, req in requirements.items():
            status = req.get("status", "Not-Started")
            if status != "Complete":
                errors.append(
                    f"{req_id} is {status} (must be Complete for Complete phase)"
                )

        for test_id, test in test_cases.items():
            if not test.get("passing", False):
                errors.append(
                    f"{test_id} is failing (all tests must pass for Complete phase)"
                )

    return errors


def get_failing_tests(feature: dict) -> list[dict]:
    """Get list of failing tests with their details."""
    failing = []
    test_cases = feature.get("test-cases", {})
    requirements = feature.get("requirements", {})

    for test_id, test in test_cases.items():
        if not test.get("passing", False):
            # Find which requirements this test covers
            covers = []
            for req_id, req in requirements.items():
                if test_id in req.get("tested-by", []):
                    covers.append(req_id)

            # Get test types
            raw_types = test.get("type")
            if raw_types is None:
                types = None
            elif isinstance(raw_types, str):
                types = [raw_types] if raw_types else None
            elif isinstance(raw_types, list):
                types = raw_types if raw_types else None
            else:
                types = None

            failing.append(
                {
                    "id": test_id,
                    "name": test.get("name", ""),
                    "file": test.get("file", ""),
                    "covers": covers,
                    "type": types,
                }
            )

    return failing


def get_test_stats(feature: dict) -> dict:
    """
    Get test statistics with optional breakdown by type.

    Returns {
        "passing": int,
        "total": int,
        "by_type": {type_name: {"passing": int, "total": int}, ...} | None
    }

    by_type is None if no tests have a type field.
    Types are normalized to lowercase, with "Uncategorized" for tests without types.
    """
    test_cases = feature.get("test-cases", {})

    total = len(test_cases)
    passing = sum(1 for t in test_cases.values() if t.get("passing", False))

    # Check if any test has a type
    any_typed = any("type" in t for t in test_cases.values())

    if not any_typed:
        return {"passing": passing, "total": total, "by_type": None}

    by_type = {}
    for test in test_cases.values():
        test_passing = test.get("passing", False)
        raw_types = test.get("type")

        # Normalize: string -> list, empty/missing -> ["Uncategorized"]
        if raw_types is None:
            types = ["Uncategorized"]
        elif isinstance(raw_types, str):
            types = [raw_types.lower()] if raw_types else ["Uncategorized"]
        elif isinstance(raw_types, list):
            types = (
                [t.lower() for t in raw_types if t] if raw_types else ["Uncategorized"]
            )
            if not types:
                types = ["Uncategorized"]
        else:
            types = ["Uncategorized"]

        for t in types:
            # Normalize "uncategorized" to title case for display
            display_type = "Uncategorized" if t.lower() == "uncategorized" else t
            if display_type not in by_type:
                by_type[display_type] = {"passing": 0, "total": 0}
            by_type[display_type]["total"] += 1
            if test_passing:
                by_type[display_type]["passing"] += 1

    return {"passing": passing, "total": total, "by_type": by_type}


def format_tests_column(stats: dict) -> str:
    """Format the Tests column value with optional type breakdown."""
    base = f"{stats['passing']}/{stats['total']}"

    if stats["by_type"] is None:
        return base

    # Sort alphabetically, "Uncategorized" last
    types = sorted(
        stats["by_type"].keys(), key=lambda t: (t == "Uncategorized", t.lower())
    )
    parts = [
        f"{t}: {stats['by_type'][t]['passing']}/{stats['by_type'][t]['total']}"
        for t in types
    ]

    return f"{base} ({', '.join(parts)})"


def get_progress(feature: dict) -> tuple[int, int]:
    """Get (complete_count, total_count) for requirements."""
    requirements = feature.get("requirements", {})
    total = len(requirements)
    complete = sum(1 for r in requirements.values() if r.get("status") == "Complete")
    return complete, total


def format_plain(
    features: list[dict], all_errors: dict, all_failing: dict, all_test_stats: dict
) -> str:
    """Format output as plain text."""
    lines = []

    # Header
    lines.append(
        "Feature                                   Phase           Progress  Tests"
    )
    lines.append("-" * 78)

    # Feature rows
    for f in features:
        name = f.get("feature", "Unnamed")
        display_name = name[:40]
        phase = f.get("phase", "Unknown")
        complete, total = get_progress(f)
        tests_col = format_tests_column(
            all_test_stats.get(name, {"passing": 0, "total": 0, "by_type": None})
        )

        lines.append(f"{display_name:<42}{phase:<16}{complete}/{total:<10}{tests_col}")

    # Failing tests section
    has_failing = any(all_failing.values())
    if has_failing:
        lines.append("")
        lines.append("Failing Tests:")
        for feature_name, tests in all_failing.items():
            if tests:
                lines.append(f"  {feature_name}:")
                for t in tests:
                    type_str = ""
                    if t.get("type"):
                        type_str = f" [{', '.join(t['type'])}]"
                    lines.append(
                        f"    - {t['id']}{type_str} ({t['file']}::{t['name']})"
                    )
                    if t["covers"]:
                        lines.append(f"      Covers: {', '.join(t['covers'])}")

    # Validation errors section
    has_errors = any(all_errors.values())
    if has_errors:
        lines.append("")
        lines.append("Validation Errors:")
        for feature_name, errors in all_errors.items():
            if errors:
                lines.append(f"  {feature_name}:")
                for e in errors:
                    lines.append(f"    - {e}")

    return "\n".join(lines)


def format_markdown(
    features: list[dict], all_errors: dict, all_failing: dict, all_test_stats: dict
) -> str:
    """Format output as markdown."""
    lines = []

    lines.append("# Feature Status")
    lines.append("")
    lines.append("| Feature | Phase | Progress | Tests |")
    lines.append("|---------|-------|----------|-------|")

    for f in features:
        name = f.get("feature", "Unnamed")
        phase = f.get("phase", "Unknown")
        complete, total = get_progress(f)
        tests_col = format_tests_column(
            all_test_stats.get(name, {"passing": 0, "total": 0, "by_type": None})
        )

        lines.append(f"| {name} | {phase} | {complete}/{total} | {tests_col} |")

    # Failing tests section
    has_failing = any(all_failing.values())
    if has_failing:
        lines.append("")
        lines.append("## Failing Tests")
        for feature_name, tests in all_failing.items():
            if tests:
                lines.append("")
                lines.append(f"### {feature_name}")
                for t in tests:
                    type_str = ""
                    if t.get("type"):
                        type_str = f" [{', '.join(t['type'])}]"
                    lines.append(
                        f"- **{t['id']}**{type_str} (`{t['file']}::{t['name']}`)"
                    )
                    if t["covers"]:
                        lines.append(f"  - Covers: {', '.join(t['covers'])}")

    # Validation errors section
    has_errors = any(all_errors.values())
    if has_errors:
        lines.append("")
        lines.append("## Validation Errors")
        for feature_name, errors in all_errors.items():
            if errors:
                lines.append("")
                lines.append(f"### {feature_name}")
                for e in errors:
                    lines.append(f"- {e}")

    return "\n".join(lines)


def format_json(
    features: list[dict], all_errors: dict, all_failing: dict, all_test_stats: dict
) -> str:
    """Format output as JSON."""
    output = {
        "features": [],
        "failing_tests": all_failing,
        "validation_errors": all_errors,
    }

    for f in features:
        name = f.get("feature", "Unnamed")
        complete, total = get_progress(f)
        stats = all_test_stats.get(name, {"passing": 0, "total": 0, "by_type": None})

        output["features"].append(
            {
                "name": name,
                "phase": f.get("phase", "Unknown"),
                "version": f.get("version", 1),
                "requirements_complete": complete,
                "requirements_total": total,
                "tests_passing": stats["passing"],
                "tests_total": stats["total"],
                "tests_by_type": stats["by_type"],
            }
        )

    return json.dumps(output, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Show feature status overview")
    parser.add_argument(
        "--format",
        choices=["plain", "markdown", "json"],
        default="plain",
        help="Output format (default: plain)",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Exit with code 1 if validation errors exist",
    )
    args = parser.parse_args()

    features = load_features(Path("features.yml"))

    if not features:
        print("No features found in features.yml", file=sys.stderr)
        sys.exit(1)

    # Collect errors, failing tests, and test stats per feature
    all_errors = {}
    all_failing = {}
    all_test_stats = {}

    for f in features:
        name = f.get("feature", "Unnamed")
        all_errors[name] = validate_feature(f)
        all_failing[name] = get_failing_tests(f)
        all_test_stats[name] = get_test_stats(f)

    # Format and output
    if args.format == "plain":
        print(format_plain(features, all_errors, all_failing, all_test_stats))
    elif args.format == "markdown":
        print(format_markdown(features, all_errors, all_failing, all_test_stats))
    else:
        print(format_json(features, all_errors, all_failing, all_test_stats))

    # Exit with error if validation requested and errors found
    if args.validate and any(all_errors.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
