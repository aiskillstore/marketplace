#!/usr/bin/env python3
"""
Skill Packager - Package and install Claude Code skills

Usage:
    # Create zip file (for Claude.ai/Desktop/API distribution)
    python scripts/package_skill.py my-skill --package

    # Install to personal skills (Claude Code)
    python scripts/package_skill.py my-skill --install personal

    # Install to project skills (Claude Code)
    python scripts/package_skill.py my-skill --install project

    # Package with custom output location
    python scripts/package_skill.py my-skill --package --output ./dist
"""

import sys
import zipfile
import shutil
import argparse
from pathlib import Path
from quick_validate import validate_skill


def get_personal_skills_dir():
    """Get personal skills directory path (~/.claude/skills/)"""
    home = Path.home()
    return home / ".claude" / "skills"


def get_project_skills_dir():
    """Get project skills directory path (.claude/skills/ in current directory)"""
    return Path.cwd() / ".claude" / "skills"


def install_skill(skill_path, install_type):
    """
    Install skill to Claude Code skills directory.

    Args:
        skill_path: Path to the skill folder
        install_type: 'personal' or 'project'

    Returns:
        True if successful, False otherwise
    """
    skill_path = Path(skill_path).resolve()
    skill_name = skill_path.name

    # Determine target directory
    if install_type == 'personal':
        target_dir = get_personal_skills_dir()
        location_desc = f"personal skills (~/.claude/skills/)"
    elif install_type == 'project':
        target_dir = get_project_skills_dir()
        location_desc = f"project skills (.claude/skills/)"
    else:
        print(f"[ERROR] Error: Invalid install type '{install_type}'. Use 'personal' or 'project'.")
        return False

    target_path = target_dir / skill_name

    # Create target directory if it doesn't exist
    target_dir.mkdir(parents=True, exist_ok=True)

    # Check if skill already exists
    if target_path.exists():
        print(f"[WARNING]  Skill '{skill_name}' already exists in {location_desc}")
        response = input("   Overwrite? [y/N]: ").strip().lower()
        if response != 'y':
            print("   Installation cancelled.")
            return False
        print(f"   Removing existing skill...")
        shutil.rmtree(target_path)

    # Copy skill to target location
    try:
        print(f" Installing '{skill_name}' to {location_desc}...")
        shutil.copytree(skill_path, target_path)
        print(f"[OK] Successfully installed to: {target_path}")

        # Print verification instructions
        print("\n Verification:")
        if install_type == 'personal':
            print(f"   Check: ls ~/.claude/skills/{skill_name}/SKILL.md")
        else:
            print(f"   Check: ls .claude/skills/{skill_name}/SKILL.md")
            print(f"   Commit: git add .claude/skills/{skill_name}/")
            print(f"           git commit -m \"Add {skill_name} skill\"")

        print(f"   Test: Ask Claude 'What skills are available?'")

        return True

    except Exception as e:
        print(f"[ERROR] Error installing skill: {e}")
        return False


def package_skill(skill_path, output_dir=None):
    """
    Package a skill folder into a zip file for distribution.

    Args:
        skill_path: Path to the skill folder
        output_dir: Optional output directory for the zip file (defaults to current directory)

    Returns:
        Path to the created zip file, or None if error
    """
    skill_path = Path(skill_path).resolve()

    # Determine output location
    skill_name = skill_path.name
    if output_dir:
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path.cwd()

    zip_filename = output_path / f"{skill_name}.zip"

    # Create the zip file
    try:
        print(f"📦 Creating zip package...")
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the skill directory
            for file_path in skill_path.rglob('*'):
                if file_path.is_file():
                    # Calculate the relative path within the zip
                    arcname = file_path.relative_to(skill_path.parent)
                    zipf.write(file_path, arcname)
                    print(f"  Added: {arcname}")

        print(f"\n[OK] Successfully packaged skill to: {zip_filename}")

        # Print distribution instructions
        print("\n Distribution:")
        print(f"   Claude.ai/Desktop: Upload {zip_filename} via Settings > Features")
        print(f"   Claude API: Upload via /v1/skills endpoint")
        print(f"   Share: Send {zip_filename} to team members")

        return zip_filename

    except Exception as e:
        print(f"[ERROR] Error creating zip file: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Package and install Claude Code skills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Install to personal skills (available across all projects)
  python scripts/package_skill.py my-skill --install personal

  # Install to project skills (shared with team via git)
  python scripts/package_skill.py my-skill --install project

  # Create zip for Claude.ai/Desktop/API distribution
  python scripts/package_skill.py my-skill --package

  # Package with custom output location
  python scripts/package_skill.py my-skill --package --output ./dist
        """
    )

    parser.add_argument('skill_path', help='Path to the skill folder')

    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        '--install',
        choices=['personal', 'project'],
        help='Install skill to Claude Code (personal or project skills directory)'
    )
    action_group.add_argument(
        '--package',
        action='store_true',
        help='Create zip package for distribution (Claude.ai/Desktop/API)'
    )

    parser.add_argument(
        '--output',
        help='Output directory for zip file (only with --package)',
        default=None
    )

    args = parser.parse_args()

    # Validate skill folder exists
    skill_path = Path(args.skill_path).resolve()

    if not skill_path.exists():
        print(f"[ERROR] Error: Skill folder not found: {skill_path}")
        sys.exit(1)

    if not skill_path.is_dir():
        print(f"[ERROR] Error: Path is not a directory: {skill_path}")
        sys.exit(1)

    # Validate SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"[ERROR] Error: SKILL.md not found in {skill_path}")
        sys.exit(1)

    # Run validation before proceeding
    print(f"🔍 Validating skill: {skill_path.name}")
    valid, message = validate_skill(skill_path)
    if not valid:
        print(f"[ERROR] Validation failed: {message}")
        print("   Please fix validation errors before proceeding.")
        sys.exit(1)
    print(f"[OK] {message}\n")

    # Execute requested action
    if args.install:
        success = install_skill(skill_path, args.install)
        sys.exit(0 if success else 1)

    elif args.package:
        if args.output and args.install:
            print("[WARNING]  Warning: --output is only used with --package")

        result = package_skill(skill_path, args.output)
        sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
