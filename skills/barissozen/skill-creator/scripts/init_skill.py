#!/usr/bin/env python3
"""
Initialize a new skill with the standard directory structure.

Usage:
    python init_skill.py <skill-name> --path <output-directory>

Example:
    python init_skill.py pdf-editor --path .claude/skills
"""

import argparse
import os
import sys
from pathlib import Path


SKILL_MD_TEMPLATE = '''---
name: {skill_name}
description: TODO: Write a clear description of what this skill does and when it should be used. Be specific about triggers (e.g., "This skill should be used when users want to...").
---

# {skill_title}

TODO: Write 2-3 sentences describing the purpose of this skill.

## When to Use

This skill should be triggered when:
- TODO: Describe trigger condition 1
- TODO: Describe trigger condition 2

## Workflow

### Step 1: TODO

TODO: Describe the first step of the workflow.

### Step 2: TODO

TODO: Describe subsequent steps.

## Bundled Resources

### Scripts

- `scripts/example.py` - TODO: Describe what this script does (or delete if not needed)

### References

- `references/example.md` - TODO: Describe what this reference contains (or delete if not needed)

### Assets

- `assets/` - TODO: Describe assets included (or delete if not needed)
'''

EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""
Example script for {skill_name} skill.

TODO: Replace this with actual functionality or delete if not needed.
"""

import sys


def main():
    """Main entry point."""
    print("Hello from {skill_name} skill!")
    # TODO: Implement actual functionality
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''

EXAMPLE_REFERENCE = '''# {skill_title} Reference

TODO: Add detailed reference documentation here.

This file should contain:
- Detailed schemas or specifications
- API documentation
- Domain knowledge
- Policies or guidelines

Keep SKILL.md lean by moving detailed information here.
'''

EXAMPLE_ASSET_README = '''# Assets

This directory contains files used in the skill's output.

Examples of what to put here:
- Templates (HTML, PPTX, etc.)
- Images and icons
- Boilerplate code
- Fonts
- Sample documents

These files are NOT loaded into context - they're used in output.

TODO: Add assets or delete this directory if not needed.
'''


def create_skill(skill_name: str, output_path: str) -> None:
    """Create a new skill with standard structure."""

    # Validate skill name
    if not skill_name.replace('-', '').replace('_', '').isalnum():
        print(f"Error: Invalid skill name '{skill_name}'. Use only alphanumeric characters, hyphens, and underscores.")
        sys.exit(1)

    # Create skill directory
    skill_dir = Path(output_path) / skill_name

    if skill_dir.exists():
        print(f"Error: Directory already exists: {skill_dir}")
        sys.exit(1)

    # Create directory structure
    directories = [
        skill_dir,
        skill_dir / "scripts",
        skill_dir / "references",
        skill_dir / "assets",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Created: {directory}")

    # Create skill title from name
    skill_title = skill_name.replace('-', ' ').replace('_', ' ').title()

    # Create SKILL.md
    skill_md_path = skill_dir / "SKILL.md"
    skill_md_content = SKILL_MD_TEMPLATE.format(
        skill_name=skill_name,
        skill_title=skill_title,
    )
    skill_md_path.write_text(skill_md_content)
    print(f"Created: {skill_md_path}")

    # Create example script
    script_path = skill_dir / "scripts" / "example.py"
    script_content = EXAMPLE_SCRIPT.format(skill_name=skill_name)
    script_path.write_text(script_content)
    script_path.chmod(0o755)
    print(f"Created: {script_path}")

    # Create example reference
    reference_path = skill_dir / "references" / "example.md"
    reference_content = EXAMPLE_REFERENCE.format(skill_title=skill_title)
    reference_path.write_text(reference_content)
    print(f"Created: {reference_path}")

    # Create assets README
    assets_readme_path = skill_dir / "assets" / "README.md"
    assets_readme_path.write_text(EXAMPLE_ASSET_README)
    print(f"Created: {assets_readme_path}")

    print(f"\n✅ Skill '{skill_name}' created successfully at: {skill_dir}")
    print("\nNext steps:")
    print("1. Edit SKILL.md to add your skill's description and workflow")
    print("2. Add scripts, references, or assets as needed")
    print("3. Delete example files you don't need")
    print(f"4. Package with: python package_skill.py {skill_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new skill with standard directory structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s pdf-editor --path .claude/skills
    %(prog)s my-workflow --path ./skills
        """
    )

    parser.add_argument(
        "skill_name",
        help="Name of the skill (use hyphens for multi-word names)"
    )

    parser.add_argument(
        "--path",
        default=".",
        help="Output directory where skill folder will be created (default: current directory)"
    )

    args = parser.parse_args()

    create_skill(args.skill_name, args.path)


if __name__ == "__main__":
    main()
