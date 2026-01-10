#!/usr/bin/env python3
"""Verify building-chatgpt-apps skill is properly configured."""
import os
import sys
from pathlib import Path


def main():
    skill_dir = Path(__file__).parent.parent

    # Check SKILL.md exists
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print("✗ SKILL.md not found. Run: ls -la", skill_dir)
        sys.exit(1)

    # Check references directory
    refs_dir = skill_dir / "references"
    if not refs_dir.exists():
        print("✗ references/ directory not found. Create with reference docs.")
        sys.exit(1)

    # Check required reference files
    required_refs = [
        "widget_patterns.md",
        "response_structure.md",
        "debugging.md",
        "complete_template.md",
    ]
    missing_refs = [r for r in required_refs if not (refs_dir / r).exists()]
    if missing_refs:
        print(f"✗ Missing reference files: {missing_refs}")
        sys.exit(1)

    # Check for key content in SKILL.md
    content = skill_md.read_text()
    required_terms = [
        "window.openai",
        "sendFollowUpMessage",  # Key API for action buttons
        "toolOutput",
        "text/html+skybridge",
        "_meta",
        "structuredContent",
        "FastMCP",
        "Button Interactivity",  # Critical limitation docs
    ]

    missing = [term for term in required_terms if term not in content]
    if missing:
        print(f"✗ SKILL.md missing key terms: {missing}")
        sys.exit(1)

    print("✓ building-chatgpt-apps skill ready (4 refs, all APIs documented)")
    sys.exit(0)


if __name__ == "__main__":
    main()