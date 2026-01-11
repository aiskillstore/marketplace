#!/usr/bin/env python3
"""Validate project planning documents for completeness and consistency.

This script checks:
1. Required files exist
2. Documents have required sections
3. No placeholder text remains
4. Cross-references are valid
5. Documents meet length guidelines
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def count_words(text: str) -> int:
    """Count words in text, excluding code blocks."""
    # Remove code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`[^`]+`", "", text)
    return len(text.split())


def check_placeholders(content: str, filepath: Path) -> list[str]:
    """Check for remaining placeholder text."""
    issues = []
    placeholders = [
        r"\[TODO\]",
        r"\[TBD\]",
        r"\[PLACEHOLDER\]",
        r"\[Project Name\]",
        r"\[Date\]",
        r"\[Name\]",
        r"\[Description\]",
        r"\[YYYY-MM-DD\]",
    ]

    for pattern in placeholders:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            issues.append(
                f"{filepath}: Found placeholder '{matches[0]}' ({len(matches)} occurrences)"
            )

    return issues


def check_required_sections(
    content: str, filepath: Path, required: list[str]
) -> list[str]:
    """Check that required sections exist."""
    issues = []
    for section in required:
        # Check for section as H2 or H3
        pattern = rf"^##\s*{re.escape(section)}|^###\s*{re.escape(section)}"
        if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            issues.append(f"{filepath}: Missing required section '{section}'")
    return issues


def check_tldr(content: str, filepath: Path) -> list[str]:
    """Check for TL;DR section."""
    if not re.search(r"##\s*TL;DR|^TL;DR", content, re.MULTILINE | re.IGNORECASE):
        return [f"{filepath}: Missing TL;DR section"]
    return []


def check_cross_references(content: str, filepath: Path, docs_dir: Path) -> list[str]:
    """Check that cross-references point to existing files."""
    issues = []
    # Find markdown links to local files
    links = re.findall(r"\[([^\]]+)\]\(\.?/?([^)]+\.md)\)", content)

    for link_text, link_path in links:
        # Skip external links
        if link_path.startswith("http"):
            continue

        # Resolve relative to docs/planning/
        link_path = link_path.removeprefix("./")

        target = docs_dir / link_path
        if not target.exists():
            issues.append(
                f"{filepath}: Broken link to '{link_path}' (text: '{link_text}')"
            )

    return issues


def validate_pvs(content: str, filepath: Path) -> list[str]:
    """Validate Project Vision & Scope document."""
    issues = []

    # Check length (target 500-800, max 1000)
    word_count = count_words(content)
    if word_count > 1000:
        issues.append(f"{filepath}: Too long ({word_count} words, max 1000)")

    # Required sections
    required = ["Problem", "Solution", "Scope", "Constraints"]
    issues.extend(check_required_sections(content, filepath, required))

    # TL;DR
    issues.extend(check_tldr(content, filepath))

    # Placeholders
    issues.extend(check_placeholders(content, filepath))

    return issues


def validate_tech_spec(content: str, filepath: Path) -> list[str]:
    """Validate Technical Specification document."""
    issues = []

    # Check length (target 1000-1500, max 2000)
    word_count = count_words(content)
    if word_count > 2000:
        issues.append(f"{filepath}: Too long ({word_count} words, max 2000)")

    # Required sections
    required = ["Technology Stack", "Architecture", "Data Model"]
    issues.extend(check_required_sections(content, filepath, required))

    # TL;DR
    issues.extend(check_tldr(content, filepath))

    # Placeholders
    issues.extend(check_placeholders(content, filepath))

    return issues


def validate_roadmap(content: str, filepath: Path) -> list[str]:
    """Validate Development Roadmap document."""
    issues = []

    # Check length (target 800-1200, max 1500)
    word_count = count_words(content)
    if word_count > 1500:
        issues.append(f"{filepath}: Too long ({word_count} words, max 1500)")

    # Required sections
    required = ["Timeline", "Phase", "Milestone"]
    issues.extend(check_required_sections(content, filepath, required))

    # TL;DR
    issues.extend(check_tldr(content, filepath))

    # Placeholders
    issues.extend(check_placeholders(content, filepath))

    return issues


def validate_adr(content: str, filepath: Path) -> list[str]:
    """Validate Architecture Decision Record."""
    issues = []

    # Check length (target 300-600, max 800)
    word_count = count_words(content)
    if word_count > 800:
        issues.append(f"{filepath}: Too long ({word_count} words, max 800)")

    # Required sections
    required = ["Context", "Decision", "Consequences"]
    issues.extend(check_required_sections(content, filepath, required))

    # Check for status
    if not re.search(
        r"Status.*:.*\b(Proposed|Accepted|Deprecated|Superseded)\b",
        content,
        re.IGNORECASE,
    ):
        issues.append(f"{filepath}: Missing or invalid Status field")

    # TL;DR
    issues.extend(check_tldr(content, filepath))

    # Placeholders
    issues.extend(check_placeholders(content, filepath))

    return issues


def main() -> int:
    """Run validation on planning documents."""
    # Find docs/planning directory
    project_root = Path.cwd()
    docs_dir = project_root / "docs" / "planning"

    if not docs_dir.exists():
        print("ERROR: docs/planning/ directory not found")
        return 1

    all_issues: list[str] = []
    files_checked = 0

    # Check required files exist
    required_files = [
        ("project-vision.md", validate_pvs),
        ("tech-spec.md", validate_tech_spec),
        ("roadmap.md", validate_roadmap),
    ]

    for filename, validator in required_files:
        filepath = docs_dir / filename
        if not filepath.exists():
            all_issues.append(f"Missing required file: {filepath}")
            continue

        content = filepath.read_text()
        files_checked += 1

        # Check if still placeholder
        if "Awaiting Generation" in content:
            all_issues.append(
                f"{filepath}: Document not yet generated (still placeholder)"
            )
            continue

        # Run document-specific validation
        all_issues.extend(validator(content, filepath))

        # Check cross-references
        all_issues.extend(check_cross_references(content, filepath, docs_dir))

    # Check ADR directory
    adr_dir = docs_dir / "adr"
    if not adr_dir.exists():
        all_issues.append("Missing ADR directory: docs/planning/adr/")
    else:
        adr_files = list(adr_dir.glob("adr-*.md"))
        if not adr_files:
            all_issues.append("No ADR files found in docs/planning/adr/")
        else:
            for adr_file in adr_files:
                content = adr_file.read_text()
                files_checked += 1

                if "Awaiting Generation" in content:
                    continue

                all_issues.extend(validate_adr(content, adr_file))
                all_issues.extend(check_cross_references(content, adr_file, docs_dir))

    # Report results
    print(f"\n{'=' * 60}")
    print("Project Planning Documents Validation Report")
    print(f"{'=' * 60}\n")
    print(f"Files checked: {files_checked}")

    if all_issues:
        print(f"Issues found: {len(all_issues)}\n")
        for issue in all_issues:
            print(f"  - {issue}")
        print(f"\n{'=' * 60}")
        return 1
    print("Status: All documents valid")
    print(f"\n{'=' * 60}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
