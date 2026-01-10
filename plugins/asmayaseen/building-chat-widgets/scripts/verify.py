#!/usr/bin/env python3
"""Verify building-chat-widgets skill has required references."""
import os
import sys

def main():
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    refs_dir = os.path.join(skill_dir, "references")

    required = ["widget-patterns.md", "server-action-handler.md"]
    missing = [r for r in required if not os.path.isfile(os.path.join(refs_dir, r))]

    if not missing:
        print("✓ building-chat-widgets skill ready")
        sys.exit(0)
    else:
        print(f"✗ Missing: {', '.join(missing)}")
        sys.exit(1)

if __name__ == "__main__":
    main()