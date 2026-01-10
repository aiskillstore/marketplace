#!/usr/bin/env python3
"""Verify internal-comms skill has required examples."""
import os
import sys

def main():
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    examples_dir = os.path.join(skill_dir, "examples")

    required = ["3p-updates.md", "company-newsletter.md", "faq-answers.md", "general-comms.md"]
    missing = [r for r in required if not os.path.isfile(os.path.join(examples_dir, r))]

    if not missing:
        print("✓ internal-comms skill ready")
        sys.exit(0)
    else:
        print(f"✗ Missing: {', '.join(missing)}")
        sys.exit(1)

if __name__ == "__main__":
    main()