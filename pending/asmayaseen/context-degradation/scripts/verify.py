#!/usr/bin/env python3
"""Verify skill structure and content."""
import sys
from pathlib import Path

def main():
    skill_dir = Path(__file__).parent.parent
    skill_md = skill_dir / "SKILL.md"
    
    if not skill_md.exists():
        print("✗ SKILL.md not found")
        sys.exit(1)
    
    content = skill_md.read_text()
    
    # Check frontmatter
    if not content.startswith("---"):
        print("✗ Missing YAML frontmatter")
        sys.exit(1)
    
    # Check required sections
    required = ["When to Activate", "Core Concepts", "Guidelines"]
    missing = [s for s in required if s not in content]
    if missing:
        print(f"✗ Missing sections: {', '.join(missing)}")
        sys.exit(1)
    
    print(f"✓ {skill_dir.name} skill validated")
    sys.exit(0)

if __name__ == "__main__":
    main()