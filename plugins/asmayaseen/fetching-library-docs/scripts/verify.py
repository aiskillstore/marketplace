#!/usr/bin/env python3
"""Verify fetch-docs.sh is executable and dependencies exist."""
import os
import sys

def main():
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fetch_script = os.path.join(skill_dir, "scripts", "fetch-docs.sh")

    if os.path.isfile(fetch_script) and os.access(fetch_script, os.X_OK):
        print("✓ fetch-docs.sh ready")
        sys.exit(0)
    elif os.path.isfile(fetch_script):
        print("✗ fetch-docs.sh not executable. Run: chmod +x scripts/fetch-docs.sh")
        sys.exit(1)
    else:
        print("✗ fetch-docs.sh missing. Check skill installation.")
        sys.exit(1)

if __name__ == "__main__":
    main()