#!/usr/bin/env python3
"""
Skill Forge Validation Script
Validates skill structure, metadata, and conventions
Usage: python validate_skill.py <skill-path> [--json]
"""

import argparse
import json
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

def validate_yaml_frontmatter(skill_path: Path) -> Tuple[bool, List[str]]:
    """Validate YAML frontmatter in SKILL.md"""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md not found"]

    with open(skill_md, encoding='utf-8') as f:
        content = f.read()

    # Check for frontmatter
    if not content.startswith("---"):
        errors.append("Missing YAML frontmatter")
        return False, errors

    # Extract frontmatter
    try:
        parts = content.split("---", 2)
        if len(parts) < 3:
            errors.append("Malformed YAML frontmatter")
            return False, errors

        frontmatter = yaml.safe_load(parts[1])

        # Validate required fields
        if "name" not in frontmatter:
            errors.append("Missing 'name' field")
        elif not frontmatter["name"].replace("-", "").replace("_", "").isalnum():
            errors.append("Name should use kebab-case or snake_case")

        if "description" not in frontmatter:
            errors.append("Missing 'description' field")
        else:
            word_count = len(frontmatter["description"].split())
            if word_count < 80 or word_count > 150:
                errors.append(f"Description should be 80-150 words (found {word_count})")

    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML: {e}")

    return len(errors) == 0, errors

def validate_file_structure(skill_path: Path) -> Tuple[bool, List[str]]:
    """Validate directory structure and file organization"""
    errors = []

    # Required files
    if not (skill_path / "SKILL.md").exists():
        errors.append("Missing SKILL.md")

    # Check for GraphViz diagram (recommended but not required)
    dot_files = list(skill_path.glob("*.dot"))
    if not dot_files:
        errors.append("Warning: No GraphViz .dot diagram found (recommended)")

    # Check subdirectories if they should exist
    skill_md_path = skill_path / "SKILL.md"
    if skill_md_path.exists():
        with open(skill_md_path, encoding='utf-8') as f:
            content = f.read()

        if "scripts/" in content:
            if not (skill_path / "scripts").exists():
                errors.append("SKILL.md references scripts/ but directory doesn't exist")

        if "references/" in content:
            if not (skill_path / "references").exists():
                errors.append("SKILL.md references references/ but directory doesn't exist")

        if "assets/" in content:
            if not (skill_path / "assets").exists():
                errors.append("SKILL.md references assets/ but directory doesn't exist")

    return len(errors) == 0, errors

def validate_resource_references(skill_path: Path) -> Tuple[bool, List[str]]:
    """Validate that all referenced resources exist"""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md not found"]

    with open(skill_md, encoding='utf-8') as f:
        content = f.read()

    # Check script references
    import re
    for line in content.split("\n"):
        if "scripts/" in line:
            matches = re.findall(r'scripts/([a-zA-Z0-9_\-\.]+)', line)
            for match in matches:
                script_path = skill_path / "scripts" / match
                if not script_path.exists():
                    errors.append(f"Referenced script not found: scripts/{match}")

        if "references/" in line:
            matches = re.findall(r'references/([a-zA-Z0-9_\-\.]+)', line)
            for match in matches:
                ref_path = skill_path / "references" / match
                if not ref_path.exists():
                    errors.append(f"Referenced reference not found: references/{match}")

        if "assets/" in line:
            matches = re.findall(r'assets/([a-zA-Z0-9_\-\.]+)', line)
            for match in matches:
                asset_path = skill_path / "assets" / match
                if not asset_path.exists():
                    errors.append(f"Referenced asset not found: assets/{match}")

    return len(errors) == 0, errors

def validate_imperative_voice(skill_path: Path) -> Tuple[bool, List[str]]:
    """Check for imperative voice usage (basic heuristic)"""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md not found"]

    with open(skill_md, encoding='utf-8') as f:
        content = f.read()

    # Heuristic: Check for common passive voice patterns
    passive_patterns = [
        "you should",
        "you must",
        "you can",
        "you need to",
        "it is important to",
        "the next step is to"
    ]

    lines_with_issues = []
    for i, line in enumerate(content.split("\n"), 1):
        for pattern in passive_patterns:
            if pattern in line.lower():
                lines_with_issues.append(f"Line {i}: Possible non-imperative voice: '{pattern}'")

    if lines_with_issues:
        errors.extend(lines_with_issues[:5])  # Show first 5
        if len(lines_with_issues) > 5:
            errors.append(f"... and {len(lines_with_issues) - 5} more instances")

    return len(errors) == 0, errors

def main():
    parser = argparse.ArgumentParser(description="Validate Skill Forge skill structure")
    parser.add_argument("skill_path", help="Path to skill directory")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()
    skill_path = Path(args.skill_path)

    if not skill_path.exists():
        print(f"Error: Path not found: {skill_path}", file=sys.stderr)
        return 1

    # Run validations
    results = {
        "frontmatter": validate_yaml_frontmatter(skill_path),
        "structure": validate_file_structure(skill_path),
        "references": validate_resource_references(skill_path),
        "imperative_voice": validate_imperative_voice(skill_path)
    }

    all_passed = all(passed for passed, _ in results.values())

    if args.json:
        output = {
            "passed": all_passed,
            "checks": {
                name: {"passed": passed, "errors": errors}
                for name, (passed, errors) in results.items()
            }
        }
        print(json.dumps(output, indent=2))
    else:
        print("\n" + "="*60)
        print("SKILL FORGE VALIDATION REPORT")
        print("="*60 + "\n")

        for name, (passed, errors) in results.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{name.upper().replace('_', ' ')}: {status}")
            if errors:
                for error in errors:
                    print(f"  • {error}")
            print()

        print("="*60)
        if all_passed:
            print("✓ All validations passed - Skill is ready!")
            return 0
        else:
            print("✗ Some validations failed - Review errors above")
            return 1

if __name__ == "__main__":
    sys.exit(main())
