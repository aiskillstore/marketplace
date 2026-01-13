#!/usr/bin/env python3
"""Verify deploying-postgres-k8s skill structure."""
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
    required = ["CloudNativePG", "Cluster", "postgresql.cnpg.io", "storage", "kubectl"]
    missing = [r for r in required if r not in content]

    if missing:
        print(f"✗ Missing sections: {missing}")
        sys.exit(1)

    # Check frontmatter
    if "deploying-postgres-k8s" not in content:
        print("✗ Invalid skill name in frontmatter")
        sys.exit(1)

    if "Use when" not in content:
        print("✗ Missing 'Use when' trigger in description")
        sys.exit(1)

    print("✓ deploying-postgres-k8s skill ready")
    sys.exit(0)


if __name__ == "__main__":
    main()