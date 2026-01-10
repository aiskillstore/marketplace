#!/usr/bin/env python3
"""
Skill Forge Packaging Script
Creates distributable skill package as .zip file
Usage: python package_skill.py <skill-path> [--output <dir>]
"""

import argparse
import shutil
import sys
import zipfile
from pathlib import Path
from datetime import datetime

def package_skill(skill_path: Path, output_dir: Path = None) -> Path:
    """Package skill into distributable zip file"""

    skill_name = skill_path.name
    output_dir = output_dir or skill_path.parent
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = output_dir / f"{skill_name}-{timestamp}.zip"

    print(f"\n{'='*60}")
    print(f"PACKAGING SKILL: {skill_name}")
    print(f"{'='*60}\n")
    print(f"Source: {skill_path}")
    print(f"Output: {output_file}\n")

    file_count = 0
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob("*"):
            if file_path.is_file():
                # Skip Python cache and system files
                if "__pycache__" in str(file_path) or file_path.name.startswith("."):
                    continue

                arcname = file_path.relative_to(skill_path.parent)
                zf.write(file_path, arcname)
                print(f"  ✓ Added: {arcname}")
                file_count += 1

    print(f"\n{'='*60}")
    print(f"✓ Package created successfully!")
    print(f"  Files: {file_count}")
    print(f"  Size: {output_file.stat().st_size / 1024:.2f} KB")
    print(f"  Location: {output_file}")
    print(f"{'='*60}\n")

    return output_file

def main():
    parser = argparse.ArgumentParser(
        description="Package Skill Forge skill for distribution"
    )
    parser.add_argument("skill_path", help="Path to skill directory")
    parser.add_argument(
        "--output",
        help="Output directory for package (defaults to parent of skill)"
    )

    args = parser.parse_args()
    skill_path = Path(args.skill_path)
    output_dir = Path(args.output) if args.output else None

    if not skill_path.exists():
        print(f"Error: Path not found: {skill_path}", file=sys.stderr)
        return 1

    if not (skill_path / "SKILL.md").exists():
        print(f"Error: Not a valid skill directory (missing SKILL.md)", file=sys.stderr)
        return 1

    try:
        package_skill(skill_path, output_dir)
        print("Installation instructions:")
        print("  1. Copy .zip file to ~/.claude/skills/")
        print("  2. cd ~/.claude/skills && unzip <package-name>.zip")
        print("  3. Restart Claude Code to activate skill\n")
        return 0
    except Exception as e:
        print(f"Error packaging skill: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
