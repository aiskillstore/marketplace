#!/usr/bin/env python3
"""Verify scaffolding-fastapi-dapr skill has required references."""
import os
import sys

def main():
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    refs_dir = os.path.join(skill_dir, "references")

    required = ["fastapi-patterns.md", "dapr-patterns.md", "sqlmodel-patterns.md"]
    missing = [r for r in required if not os.path.isfile(os.path.join(refs_dir, r))]

    if not missing:
        print("✓ scaffolding-fastapi-dapr skill ready")
        sys.exit(0)
    else:
        print(f"✗ Missing: {', '.join(missing)}")
        sys.exit(1)

if __name__ == "__main__":
    main()