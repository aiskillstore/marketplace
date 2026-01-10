#!/usr/bin/env python3
"""
Validates that a CCGG Business Operations project has all required mechanisms

Usage:
    python validate_project.py <project-name>

Examples:
    python validate_project.py ccgg-offers-pricing
    python validate_project.py magnetic-content-os
"""

import sys
from pathlib import Path


def validate_project(project_name):
    """
    Validate a CCGG Business Operations project has all required mechanisms.

    Args:
        project_name: Name of the project to validate

    Returns:
        (errors, warnings) tuple with counts
    """
    project_path = Path("Active Projects/_Incubator") / project_name
    index_path = Path("Project Memory/Active Projects Index") / f"{project_name}-index.md"

    print(f"[VALIDATING] project: {project_name}")
    print()

    errors = 0
    warnings = 0

    # Check 1: Project folder exists
    if not project_path.exists():
        print(f"[ERROR] Project folder not found: {project_path}")
        errors += 1
    else:
        print("[OK] Project folder exists")

    # Check 2: CLAUDE.md exists
    claude_md = project_path / "CLAUDE.md"
    if not claude_md.exists():
        print("[ERROR] CLAUDE.md not found")
        errors += 1
    else:
        print("[OK] CLAUDE.md exists")

        # Read CLAUDE.md content
        content = claude_md.read_text(encoding='utf-8')

        # Check 2a: PARENT SYSTEM INTEGRATION section
        if "## PARENT SYSTEM INTEGRATION" not in content:
            print("[ERROR] PARENT SYSTEM INTEGRATION section missing in CLAUDE.md")
            errors += 1
        else:
            print("[OK] PARENT SYSTEM INTEGRATION section present")

            # Check sub-sections
            if "### Project Memory Index Sync" not in content:
                print("[WARNING] Project Memory Index Sync sub-section missing")
                warnings += 1

            if "### Operations Logging" not in content:
                print("[WARNING] Operations Logging sub-section missing")
                warnings += 1

            if "### Strategic Alignment Validation" not in content:
                print("[WARNING] Strategic Alignment Validation sub-section missing")
                warnings += 1

            if "### Cross-Project Intelligence" not in content:
                print("[WARNING] Cross-Project Intelligence sub-section missing")
                warnings += 1

        # Check 2b: Template variables replaced
        if "{{" in content:
            print("[WARNING] Template variables not replaced ({{ found)")
            warnings += 1

    # Check 3: README.md exists
    readme = project_path / "README.md"
    if not readme.exists():
        print("[WARNING] README.md not found")
        warnings += 1
    else:
        print("[OK] README.md exists")

    # Check 4: Active Projects Index exists
    if not index_path.exists():
        print(f"[ERROR] Active Projects Index not found: {index_path}")
        errors += 1
    else:
        print("[OK] Active Projects Index exists")

        # Read index content
        index_content = index_path.read_text(encoding='utf-8')

        # Check YAML frontmatter
        if not index_content.startswith("---"):
            print("[WARNING] YAML frontmatter missing in index")
            warnings += 1

        if "strategic_alignment:" not in index_content:
            print("[WARNING] strategic_alignment missing in index")
            warnings += 1

    # Check 5: Operations log entry
    ops_log = Path("operations_log.txt")
    if ops_log.exists():
        ops_content = ops_log.read_text(encoding='utf-8')
        if project_name not in ops_content:
            print(f"[WARNING] No operations_log.txt entry found for {project_name}")
            warnings += 1
        else:
            print("[OK] Operations log entry exists")
    else:
        print("[WARNING] operations_log.txt not found")
        warnings += 1

    # Summary
    print()
    print("=" * 40)
    print("Validation Summary")
    print("=" * 40)
    print(f"Errors: {errors}")
    print(f"Warnings: {warnings}")
    print()

    if errors == 0 and warnings == 0:
        print("[OK] Project validation PASSED")
        return 0
    elif errors == 0:
        print("[WARNING] Project validation passed with warnings")
        return 0
    else:
        print("[ERROR] Project validation FAILED")
        return 1


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_project.py <project-name>")
        print()
        print("Examples:")
        print("  python validate_project.py ccgg-offers-pricing")
        print("  python validate_project.py magnetic-content-os")
        sys.exit(1)

    project_name = sys.argv[1]
    exit_code = validate_project(project_name)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
