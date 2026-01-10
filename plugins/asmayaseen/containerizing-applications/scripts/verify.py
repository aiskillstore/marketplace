#!/usr/bin/env python3
"""Verify containerizing-applications skill structure."""
import subprocess
import sys
from pathlib import Path


def main():
    skill_dir = Path(__file__).parent.parent
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        print("✗ SKILL.md not found")
        sys.exit(1)

    content = skill_md.read_text()

    # Check required sections
    required = ["Dockerfile Patterns", "docker-compose", "Helm", "Gotchas"]
    missing = [r for r in required if r not in content]

    if missing:
        print(f"✗ Missing sections: {missing}")
        sys.exit(1)

    # Check frontmatter
    if "containerizing-applications" not in content:
        print("✗ Invalid skill name in frontmatter")
        sys.exit(1)

    if "Use when" not in content:
        print("✗ Missing 'Use when' trigger in description")
        sys.exit(1)

    print("✓ containerizing-applications skill ready")
    sys.exit(0)


if __name__ == "__main__":
    main()