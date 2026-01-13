#!/usr/bin/env python3
"""Verify a skill follows constitution requirements."""
import os
import re
import sys

def main():
    # Check if a skill path was provided, otherwise check self
    skill_path = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skill_md = os.path.join(skill_path, "SKILL.md")

    if not os.path.isfile(skill_md):
        print(f"✗ SKILL.md not found at {skill_path}")
        sys.exit(1)

    with open(skill_md, 'r') as f:
        content = f.read()

    # Extract YAML frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        print("✗ Missing YAML frontmatter. Add --- delimiters.")
        sys.exit(1)

    frontmatter = match.group(1)

    # Extract name using regex
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    if not name_match:
        print("✗ Missing 'name' in frontmatter")
        sys.exit(1)
    name = name_match.group(1).strip()

    # Extract description (handles multi-line YAML with | or >)
    desc_match = re.search(r'^description:\s*[\|>]?\s*\n?(.*)', frontmatter, re.MULTILINE | re.DOTALL)
    if not desc_match:
        print("✗ Missing 'description' in frontmatter")
        sys.exit(1)
    desc = desc_match.group(1).strip()

    # Check gerund naming
    if not re.match(r'^[a-z][a-z0-9-]*$', name):
        print(f"✗ Invalid name format: {name}")
        sys.exit(1)

    # Check for "Use when" trigger
    if 'use when' not in desc.lower():
        print("✗ Description missing 'Use when' trigger")
        sys.exit(1)

    # Check verify.py exists
    verify_path = os.path.join(skill_path, "scripts", "verify.py")
    if not os.path.isfile(verify_path):
        print("✗ scripts/verify.py missing")
        sys.exit(1)

    print(f"✓ {name} valid")
    sys.exit(0)

if __name__ == "__main__":
    main()
