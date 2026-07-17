#!/usr/bin/env python3
"""
Validate and package a skill into a distributable zip file.

Usage:
    python package_skill.py <path/to/skill-folder> [output-directory]

Example:
    python package_skill.py .claude/skills/my-skill
    python package_skill.py .claude/skills/my-skill ./dist
"""

import argparse
import os
import re
import sys
import zipfile
from pathlib import Path


class SkillValidator:
    """Validates skill structure and content."""

    def __init__(self, skill_path: Path):
        self.skill_path = skill_path
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate(self) -> bool:
        """Run all validations. Returns True if valid."""
        self._validate_structure()
        self._validate_skill_md()
        self._validate_frontmatter()
        self._validate_resources()

        return len(self.errors) == 0

    def _validate_structure(self):
        """Validate basic directory structure."""
        if not self.skill_path.exists():
            self.errors.append(f"Skill directory does not exist: {self.skill_path}")
            return

        if not self.skill_path.is_dir():
            self.errors.append(f"Path is not a directory: {self.skill_path}")
            return

        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            self.errors.append("Missing required file: SKILL.md")

    def _validate_skill_md(self):
        """Validate SKILL.md content."""
        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            return

        content = skill_md.read_text()

        # Check for TODO placeholders
        if "TODO:" in content:
            self.warnings.append("SKILL.md contains TODO placeholders that should be completed")

        # Check word count (should be under 5000)
        word_count = len(content.split())
        if word_count > 5000:
            self.warnings.append(f"SKILL.md is {word_count} words (recommended: <5000). Consider moving content to references/")

    def _validate_frontmatter(self):
        """Validate YAML frontmatter."""
        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            return

        content = skill_md.read_text()

        # Check for frontmatter
        if not content.startswith("---"):
            self.errors.append("SKILL.md must start with YAML frontmatter (---)")
            return

        # Extract frontmatter
        parts = content.split("---", 2)
        if len(parts) < 3:
            self.errors.append("Invalid YAML frontmatter format in SKILL.md")
            return

        frontmatter = parts[1].strip()

        # Check required fields
        if "name:" not in frontmatter:
            self.errors.append("Missing required 'name' field in frontmatter")

        if "description:" not in frontmatter:
            self.errors.append("Missing required 'description' field in frontmatter")

        # Validate description quality
        desc_match = re.search(r'description:\s*(.+?)(?:\n|$)', frontmatter, re.DOTALL)
        if desc_match:
            description = desc_match.group(1).strip()
            if len(description) < 50:
                self.warnings.append("Description is short. Add more detail about when to use this skill.")
            if "TODO" in description:
                self.errors.append("Description contains TODO placeholder - must be completed")

    def _validate_resources(self):
        """Validate bundled resources."""
        # Check for empty directories
        for subdir in ["scripts", "references", "assets"]:
            dir_path = self.skill_path / subdir
            if dir_path.exists():
                files = list(dir_path.glob("*"))
                # Filter out README files
                actual_files = [f for f in files if f.name != "README.md"]
                if len(actual_files) == 0:
                    self.warnings.append(f"Empty {subdir}/ directory - consider removing if not needed")

        # Check for executable scripts
        scripts_dir = self.skill_path / "scripts"
        if scripts_dir.exists():
            for script in scripts_dir.glob("*.py"):
                if not os.access(script, os.X_OK):
                    self.warnings.append(f"Script {script.name} is not executable (chmod +x)")


def package_skill(skill_path: Path, output_dir: Path) -> Path:
    """Package skill into a zip file."""
    skill_name = skill_path.name
    zip_path = output_dir / f"{skill_name}.zip"

    # Create output directory if needed
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create zip file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in skill_path.rglob("*"):
            if file_path.is_file():
                # Skip hidden files and __pycache__
                if any(part.startswith('.') or part == '__pycache__' for part in file_path.parts):
                    continue

                arcname = file_path.relative_to(skill_path.parent)
                zipf.write(file_path, arcname)
                print(f"  Added: {arcname}")

    return zip_path


def main():
    parser = argparse.ArgumentParser(
        description="Validate and package a skill into a distributable zip file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s .claude/skills/my-skill
    %(prog)s .claude/skills/my-skill ./dist
        """
    )

    parser.add_argument(
        "skill_path",
        help="Path to the skill directory"
    )

    parser.add_argument(
        "output_dir",
        nargs="?",
        default=".",
        help="Output directory for the zip file (default: current directory)"
    )

    args = parser.parse_args()

    skill_path = Path(args.skill_path).resolve()
    output_dir = Path(args.output_dir).resolve()

    print(f"Validating skill: {skill_path.name}")
    print("-" * 50)

    # Validate
    validator = SkillValidator(skill_path)
    is_valid = validator.validate()

    # Print warnings
    for warning in validator.warnings:
        print(f"⚠️  Warning: {warning}")

    # Print errors
    for error in validator.errors:
        print(f"❌ Error: {error}")

    if not is_valid:
        print("\n❌ Validation failed. Fix errors and try again.")
        sys.exit(1)

    if validator.warnings:
        print()

    # Package
    print(f"Packaging skill...")
    zip_path = package_skill(skill_path, output_dir)

    print("-" * 50)
    print(f"✅ Skill packaged successfully: {zip_path}")
    print(f"   Size: {zip_path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
