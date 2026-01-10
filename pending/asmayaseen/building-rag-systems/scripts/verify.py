#!/usr/bin/env python3
"""Verify building-rag-systems skill structure."""
import os
import sys

def main():
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    required = [
        "SKILL.md",
        "references/ingestion-patterns.md",
        "references/retrieval-patterns.md",
    ]

    missing = [f for f in required if not os.path.exists(os.path.join(skill_dir, f))]

    if missing:
        print(f"✗ Missing: {', '.join(missing)}")
        sys.exit(1)

    print("✓ building-rag-systems skill ready")
    sys.exit(0)

if __name__ == "__main__":
    main()