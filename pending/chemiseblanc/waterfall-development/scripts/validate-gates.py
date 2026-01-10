#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""
Strict gate validation for waterfall workflow.

Usage:
    ./validate-gates.py                                    # All features
    ./validate-gates.py --feature "Name"                   # Specific feature
    ./validate-gates.py --feature "Name" --target Testing  # Check transition

Exit 0: All gates pass
Exit 1: Gate failure
"""

import argparse
import sys
from pathlib import Path

import yaml


PHASES = ["Requirements", "Design", "Implementation", "Testing", "Complete"]


def load_features(path: Path) -> list[dict]:
    """Load all feature documents from features.yml."""
    if not path.exists():
        print(f"Error: {path} not found", file=sys.stderr)
        sys.exit(1)

    with open(path) as f:
        docs = list(yaml.safe_load_all(f))

    return [doc for doc in docs if doc is not None]


def phase_index(phase: str) -> int:
    """Get index of phase, defaulting to 0 if not found."""
    return PHASES.index(phase) if phase in PHASES else 0


def validate_g1(feature: dict) -> list[str]:
    """G1: Feature has ≥1 requirement."""
    errors = []
    requirements = feature.get("requirements", {})
    if not requirements:
        errors.append("G1: no requirements defined")
    return errors


def validate_g2(feature: dict) -> list[str]:
    """G2: All requirements have descriptions."""
    errors = []
    requirements = feature.get("requirements", {})
    for req_id, req in requirements.items():
        desc = req.get("description", "")
        if not desc or not desc.strip():
            errors.append(f"G2: {req_id}: missing description")
    return errors


def validate_g3(feature: dict) -> list[str]:
    """G3: decisions field exists."""
    errors = []
    if "decisions" not in feature:
        errors.append("G3: missing decisions field")
    return errors


def validate_g4(feature: dict) -> list[str]:
    """G4: All requirements In-Progress or Complete."""
    errors = []
    requirements = feature.get("requirements", {})
    for req_id, req in requirements.items():
        status = req.get("status", "Not-Started")
        if status not in ("In-Progress", "Complete"):
            errors.append(f"G4: {req_id}: status is {status}")
    return errors


def validate_g5(feature: dict) -> list[str]:
    """G5: All requirements Complete + tested-by + all tests passing."""
    errors = []
    requirements = feature.get("requirements", {})
    test_cases = feature.get("test-cases", {})

    for req_id, req in requirements.items():
        # Check status is Complete
        status = req.get("status", "Not-Started")
        if status != "Complete":
            errors.append(f"G5: {req_id}: status is {status}, must be Complete")

        # Check tested-by exists and has entries
        tested_by = req.get("tested-by", [])
        if not tested_by:
            errors.append(f"G5: {req_id}: missing tested-by")
        else:
            # Check referenced tests exist
            for test_id in tested_by:
                if test_id not in test_cases:
                    errors.append(
                        f"G5: {req_id}: tested-by references unknown test {test_id}"
                    )

    # Check all tests are passing
    for test_id, test in test_cases.items():
        if not test.get("passing", False):
            errors.append(f"G5: {test_id}: not passing")

    return errors


def validate_feature(feature: dict, target_phase: str | None = None) -> list[str]:
    """Validate gates for a feature up to target phase."""
    errors = []

    current_phase = feature.get("phase", "Requirements")
    check_phase = target_phase if target_phase else current_phase
    check_idx = phase_index(check_phase)

    # G1 + G2: Required for Design and beyond
    if check_idx >= phase_index("Design"):
        errors.extend(validate_g1(feature))
        errors.extend(validate_g2(feature))

    # G3: Required for Implementation and beyond
    if check_idx >= phase_index("Implementation"):
        errors.extend(validate_g3(feature))

    # G4: Required for Testing and beyond
    if check_idx >= phase_index("Testing"):
        errors.extend(validate_g4(feature))

    # G5: Required for Complete
    if check_idx >= phase_index("Complete"):
        errors.extend(validate_g5(feature))

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate waterfall phase gates")
    parser.add_argument(
        "--feature",
        help="Validate specific feature by name",
    )
    parser.add_argument(
        "--target",
        choices=PHASES,
        help="Target phase to validate transition to",
    )
    args = parser.parse_args()

    features = load_features(Path("features.yml"))

    if not features:
        print("No features found in features.yml", file=sys.stderr)
        sys.exit(1)

    # Filter to specific feature if requested
    if args.feature:
        features = [f for f in features if f.get("feature") == args.feature]
        if not features:
            print(f"Feature not found: {args.feature}", file=sys.stderr)
            sys.exit(1)

    # Validate each feature
    all_errors = {}
    for f in features:
        name = f.get("feature", "Unnamed")
        all_errors[name] = validate_feature(f, args.target)

    # Print errors
    has_errors = False
    for feature_name, errors in all_errors.items():
        if errors:
            has_errors = True
            print(f"{feature_name}:")
            for e in errors:
                print(f"  {e}")

    if has_errors:
        sys.exit(1)
    else:
        print("All gates passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
