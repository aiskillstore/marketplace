#!/usr/bin/env python3
"""Verify building-mcp-servers skill has required references."""
import os
import sys

def main():
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    refs_dir = os.path.join(skill_dir, "references")

    required_refs = [
        "mcp_best_practices.md",
        "python_mcp_server.md",
        "node_mcp_server.md"
    ]

    missing = [r for r in required_refs if not os.path.isfile(os.path.join(refs_dir, r))]

    if not missing:
        print("✓ building-mcp-servers skill ready")
        sys.exit(0)
    else:
        print(f"✗ Missing: {', '.join(missing)}")
        sys.exit(1)

if __name__ == "__main__":
    main()