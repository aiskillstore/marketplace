#!/usr/bin/env python3
"""
Learning Objectives Validator - Check objective statements for measurability

This script validates that learning objectives:
1. Use action verbs from Bloom's taxonomy (measurable)
2. Are specific and testable (not vague)
3. Avoid ambiguous language like "understand" or "know"
4. Align with specified Bloom's level

Usage:
    python validate-objectives.py objectives.yml

Output: JSON with validation results
"""

import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


# Bloom's level action verbs (from blooms-taxonomy-programming.md)
BLOOMS_VERBS = {
    "Remember": {
        "good": ["recall", "recognize", "identify", "define", "list", "memorize", "repeat", "know"],
        "bad": ["understand", "learn", "know", "comprehend"],
    },
    "Understand": {
        "good": [
            "explain",
            "describe",
            "summarize",
            "classify",
            "interpret",
            "infer",
            "rephrase",
            "translate",
            "compare",
        ],
        "bad": ["understand", "know", "learn", "get", "appreciate"],
    },
    "Apply": {
        "good": ["apply", "use", "implement", "solve", "execute", "demonstrate", "employ", "operate", "practice"],
        "bad": ["understand", "learn", "know", "try"],
    },
    "Analyze": {
        "good": [
            "analyze",
            "examine",
            "distinguish",
            "identify",
            "relate",
            "infer",
            "diagram",
            "deconstruct",
            "compare",
        ],
        "bad": ["understand", "learn", "know"],
    },
    "Evaluate": {
        "good": [
            "evaluate",
            "assess",
            "appraise",
            "critique",
            "judge",
            "justify",
            "defend",
            "select",
            "verify",
            "review",
        ],
        "bad": ["understand", "think"],
    },
    "Create": {
        "good": [
            "create",
            "design",
            "build",
            "develop",
            "construct",
            "produce",
            "invent",
            "compose",
            "formulate",
            "generate",
        ],
        "bad": ["understand", "learn"],
    },
}

# Vague language to avoid
VAGUE_WORDS = [
    "understand",
    "know",
    "learn",
    "study",
    "appreciate",
    "get",
    "think about",
    "be familiar",
    "grasp",
    "comprehend",
    "become aware",
    "become acquainted",
]


def extract_first_verb(statement: str) -> str | None:
    """Extract the first action verb from an objective statement."""
    # Pattern: Start of sentence (optional article/prep) + verb
    words = statement.lower().split()
    for i, word in enumerate(words):
        # Remove common prefixes
        clean_word = word.rstrip(",;:")
        if len(clean_word) > 2 and clean_word not in ["the", "a", "an", "to", "in", "with", "using"]:
            return clean_word
    return None


def validate_objective(objective: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate a single objective.

    Returns:
        (is_valid, list_of_errors)
    """
    errors = []

    # Check required fields
    if "statement" not in objective:
        errors.append("Missing 'statement' field")
        return False, errors

    statement = objective["statement"].lower()

    # Check for vague language
    for vague in VAGUE_WORDS:
        if vague in statement:
            errors.append(f"Vague language detected: '{vague}' - use specific action verbs instead")

    # Get Bloom's level for more specific validation
    blooms_level = objective.get("blooms_level", "").strip()

    if blooms_level not in BLOOMS_VERBS:
        errors.append(f"Unknown Bloom's level: {blooms_level}")
    else:
        # Check if statement uses appropriate verbs for the level
        first_verb = extract_first_verb(statement)

        if first_verb:
            level_bad_verbs = BLOOMS_VERBS[blooms_level].get("bad", [])

            # Check if first verb is in the "bad" list for this level
            if any(bad in first_verb for bad in level_bad_verbs):
                errors.append(
                    f"Verb '{first_verb}' is too vague for '{blooms_level}' level. "
                    f"Use one of: {', '.join(BLOOMS_VERBS[blooms_level]['good'])}"
                )

    # Check that statement is not too vague (e.g., not just a topic)
    if len(statement.split()) < 5:
        errors.append("Statement is too brief - should describe what learner will do, not just topic")

    # Check for context or conditions
    if "context:" not in objective or not objective.get("context"):
        errors.append("Missing 'context' - describe the situation or problem")

    # Check for assessment method
    if "assessment_method" not in objective or not objective.get("assessment_method"):
        errors.append("Missing 'assessment_method' - how will this be assessed?")

    # Check for success criteria
    if "success_criteria" not in objective or not objective.get("success_criteria"):
        errors.append("Missing 'success_criteria' - what does success look like?")
    elif isinstance(objective["success_criteria"], list) and len(objective["success_criteria"]) == 0:
        errors.append("success_criteria is empty - add at least one criterion")

    return len(errors) == 0, errors


def validate_objectives_file(data: dict[str, Any]) -> dict[str, Any]:
    """
    Validate an objectives YAML file.

    Returns:
        {
            "valid": bool,
            "summary": {"total": int, "valid": int, "invalid": int},
            "objectives": [
                {"id": str, "statement": str, "valid": bool, "errors": [str]}
            ]
        }
    """
    results = {"valid": True, "summary": {"total": 0, "valid": 0, "invalid": 0}, "objectives": []}

    if "objectives" not in data or not isinstance(data["objectives"], list):
        return {"valid": False, "summary": {"total": 0, "valid": 0, "invalid": 0}, "objectives": []}

    objectives = data["objectives"]
    results["summary"]["total"] = len(objectives)

    for obj in objectives:
        obj_id = obj.get("id", f"#{objectives.index(obj) + 1}")
        obj_statement = obj.get("statement", "(no statement)")
        is_valid, errors = validate_objective(obj)

        results["objectives"].append(
            {"id": obj_id, "statement": obj_statement, "valid": is_valid, "errors": errors}
        )

        if is_valid:
            results["summary"]["valid"] += 1
        else:
            results["summary"]["invalid"] += 1
            results["valid"] = False

    return results


def main() -> None:
    """Parse arguments and validate objectives."""
    if len(sys.argv) < 2:
        print(
            json.dumps(
                {
                    "valid": False,
                    "error": "Usage: python validate-objectives.py <objectives.yml>",
                }
            )
        )
        sys.exit(1)

    objectives_file = sys.argv[1]

    # Check file exists
    if not Path(objectives_file).exists():
        print(json.dumps({"valid": False, "error": f"File not found: {objectives_file}"}))
        sys.exit(1)

    # Load YAML
    if yaml is None:
        print(
            json.dumps(
                {
                    "valid": False,
                    "error": "PyYAML not installed. Install with: pip install pyyaml",
                }
            )
        )
        sys.exit(1)

    try:
        with open(objectives_file, "r") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(json.dumps({"valid": False, "error": f"Failed to parse YAML: {str(e)}"}))
        sys.exit(1)

    # Validate
    results = validate_objectives_file(data)
    print(json.dumps(results, indent=2))

    # Exit with non-zero if validation failed
    sys.exit(0 if results["valid"] else 1)


if __name__ == "__main__":
    main()
