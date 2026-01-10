#!/usr/bin/env python3
"""Verify systematic-debugging skill structure."""
import os
import sys

def main():
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    required = [
        "SKILL.md",
        "references/root-cause-tracing.md",
    ]

    missing = [f for f in required if not os.path.exists(os.path.join(skill_dir, f))]

    if missing:
        print(f"X Missing: {', '.join(missing)}")
        sys.exit(1)

    # Check SKILL.md has key sections
    skill_path = os.path.join(skill_dir, "SKILL.md")
    with open(skill_path, 'r') as f:
        content = f.read()

    required_sections = ["Phase 1:", "Phase 2:", "Phase 3:", "Phase 4:", "Iron Law"]
    missing_sections = [s for s in required_sections if s not in content]

    if missing_sections:
        print(f"X Missing sections: {', '.join(missing_sections)}")
        sys.exit(1)

    print("OK systematic-debugging skill ready")
    sys.exit(0)

if __name__ == "__main__":
    main()