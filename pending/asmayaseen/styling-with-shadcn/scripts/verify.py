#!/usr/bin/env python3
"""Verify styling-with-shadcn skill has required references."""
import os
import sys

def main():
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    refs_dir = os.path.join(skill_dir, "references")

    if os.path.isdir(refs_dir) and os.path.isfile(os.path.join(refs_dir, "component-examples.md")):
        print("✓ styling-with-shadcn skill ready")
        sys.exit(0)
    else:
        print("✗ Missing references/component-examples.md")
        sys.exit(1)

if __name__ == "__main__":
    main()