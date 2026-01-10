#!/usr/bin/env python3
"""
App Spec Validator

Validates that an app-spec.md file contains all required sections
and follows the expected format.

Usage:
    python validate-app-spec.py path/to/app-spec.md
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple, Optional


class ValidationResult:
    """Result of a single validation check."""

    def __init__(self, passed: bool, message: str, severity: str = "error"):
        self.passed = passed
        self.message = message
        self.severity = severity  # "error" or "warning"


def read_file(path: str) -> str:
    """Read file contents."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def check_section_exists(content: str, section: str) -> ValidationResult:
    """Check if a section header exists."""
    pattern = rf"^##?\s+{re.escape(section)}"
    if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
        return ValidationResult(True, f"Section '{section}' found")
    return ValidationResult(False, f"Missing required section: '{section}'")


def check_subsection_exists(content: str, subsection: str) -> ValidationResult:
    """Check if a subsection header exists."""
    pattern = rf"^###?\s+{re.escape(subsection)}"
    if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
        return ValidationResult(True, f"Subsection '{subsection}' found")
    return ValidationResult(False, f"Missing subsection: '{subsection}'", "warning")


def check_golden_prompts(content: str) -> List[ValidationResult]:
    """Check golden prompt requirements."""
    results = []

    # Check for direct prompts section
    direct_section = re.search(
        r"###?\s+Direct.*?\n(.*?)(?=###|$)", content, re.DOTALL | re.IGNORECASE
    )
    if direct_section:
        # Count numbered items
        direct_prompts = re.findall(r"^\d+\.", direct_section.group(1), re.MULTILINE)
        count = len(direct_prompts)
        if count >= 5:
            results.append(ValidationResult(True, f"Direct prompts: {count} (minimum 5)"))
        else:
            results.append(
                ValidationResult(False, f"Direct prompts: {count} found, need at least 5")
            )
    else:
        results.append(ValidationResult(False, "Missing 'Direct' prompts section"))

    # Check for indirect prompts section
    indirect_section = re.search(
        r"###?\s+Indirect.*?\n(.*?)(?=###|$)", content, re.DOTALL | re.IGNORECASE
    )
    if indirect_section:
        indirect_prompts = re.findall(r"^\d+\.", indirect_section.group(1), re.MULTILINE)
        count = len(indirect_prompts)
        if count >= 5:
            results.append(ValidationResult(True, f"Indirect prompts: {count} (minimum 5)"))
        else:
            results.append(
                ValidationResult(False, f"Indirect prompts: {count} found, need at least 5")
            )
    else:
        results.append(ValidationResult(False, "Missing 'Indirect' prompts section"))

    # Check for negative prompts section
    negative_section = re.search(
        r"###?\s+Negative.*?\n(.*?)(?=###|$)", content, re.DOTALL | re.IGNORECASE
    )
    if negative_section:
        negative_prompts = re.findall(r"^\d+\.", negative_section.group(1), re.MULTILINE)
        count = len(negative_prompts)
        if count >= 3:
            results.append(ValidationResult(True, f"Negative prompts: {count} (minimum 3)"))
        else:
            results.append(
                ValidationResult(False, f"Negative prompts: {count} found, need at least 3")
            )
    else:
        results.append(ValidationResult(False, "Missing 'Negative' prompts section"))

    return results


def check_tools_section(content: str) -> List[ValidationResult]:
    """Check tools section requirements."""
    results = []

    # Find tools section
    tools_section = re.search(
        r"##?\s+Tools.*?\n(.*?)(?=##[^#]|$)", content, re.DOTALL | re.IGNORECASE
    )
    if not tools_section:
        results.append(ValidationResult(False, "Missing 'Tools' section"))
        return results

    tools_content = tools_section.group(1)

    # Count tool definitions (look for ### headers or numbered items)
    tool_headers = re.findall(r"^###\s+\d+\.", tools_content, re.MULTILINE)
    if not tool_headers:
        tool_headers = re.findall(r"^###\s+\w+_\w+", tools_content, re.MULTILINE)

    if len(tool_headers) >= 2:
        results.append(ValidationResult(True, f"Tools defined: {len(tool_headers)}"))
    else:
        results.append(
            ValidationResult(False, f"Only {len(tool_headers)} tools defined, need at least 2")
        )

    # Check for annotations
    if "readOnlyHint" in tools_content or "destructiveHint" in tools_content:
        results.append(ValidationResult(True, "Tool annotations found"))
    else:
        results.append(
            ValidationResult(False, "Missing tool annotations (readOnlyHint, etc.)", "warning")
        )

    return results


def check_value_proposition(content: str) -> List[ValidationResult]:
    """Check value proposition section."""
    results = []

    # Look for Know/Do/Show mentions
    has_know = bool(re.search(r"\bKnow\b", content, re.IGNORECASE))
    has_do = bool(re.search(r"\bDo\b", content))
    has_show = bool(re.search(r"\bShow\b", content, re.IGNORECASE))

    if has_know and has_do and has_show:
        results.append(ValidationResult(True, "Know/Do/Show framework addressed"))
    else:
        missing = []
        if not has_know:
            missing.append("Know")
        if not has_do:
            missing.append("Do")
        if not has_show:
            missing.append("Show")
        results.append(
            ValidationResult(
                False, f"Missing value pillars: {', '.join(missing)}", "warning"
            )
        )

    return results


def validate_app_spec(path: str) -> Tuple[List[ValidationResult], bool]:
    """Run all validations on the app-spec.md file."""
    results: List[ValidationResult] = []

    # Read file
    try:
        content = read_file(path)
    except FileNotFoundError:
        results.append(ValidationResult(False, f"File not found: {path}"))
        return results, False
    except Exception as e:
        results.append(ValidationResult(False, f"Error reading file: {e}"))
        return results, False

    results.append(ValidationResult(True, f"File loaded: {path}"))

    # Required sections
    required_sections = [
        "Product Context",
        "Value Proposition",
        "Golden Prompts",
    ]

    for section in required_sections:
        results.append(check_section_exists(content, section))

    # Optional but recommended sections
    recommended_sections = ["Tools", "Widget", "Authentication"]
    for section in recommended_sections:
        result = check_section_exists(content, section)
        if not result.passed:
            result.severity = "warning"
            result.message = f"Recommended section missing: '{section}'"
        results.append(result)

    # Detailed checks
    results.extend(check_value_proposition(content))
    results.extend(check_golden_prompts(content))
    results.extend(check_tools_section(content))

    # Calculate overall pass/fail
    errors = [r for r in results if not r.passed and r.severity == "error"]
    passed = len(errors) == 0

    return results, passed


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python validate-app-spec.py <path-to-app-spec.md>")
        sys.exit(1)

    path = sys.argv[1]
    results, passed = validate_app_spec(path)

    print("\n" + "=" * 60)
    print("APP SPEC VALIDATION RESULTS")
    print("=" * 60 + "\n")

    # Group by status
    errors = [r for r in results if not r.passed and r.severity == "error"]
    warnings = [r for r in results if not r.passed and r.severity == "warning"]
    successes = [r for r in results if r.passed]

    # Print successes
    if successes:
        print("PASSED:")
        for r in successes:
            print(f"  ✓ {r.message}")
        print()

    # Print warnings
    if warnings:
        print("WARNINGS:")
        for r in warnings:
            print(f"  ⚠ {r.message}")
        print()

    # Print errors
    if errors:
        print("ERRORS:")
        for r in errors:
            print(f"  ✗ {r.message}")
        print()

    # Summary
    print("=" * 60)
    print(f"Summary: {len(successes)} passed, {len(warnings)} warnings, {len(errors)} errors")

    if passed:
        print("\n✓ App spec is valid!")
        sys.exit(0)
    else:
        print("\n✗ App spec has errors. Please fix and re-validate.")
        sys.exit(1)


if __name__ == "__main__":
    main()
