#!/usr/bin/env python3
"""
Skill validation script for Claude Code skills.
Validates SKILL.md format, directory structure, naming conventions, and schema compliance.
"""

import re
import sys
import yaml
from pathlib import Path

# Ensure UTF-8 output for Unicode characters on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


def validate_skill(skill_dir: str) -> tuple[bool, list[str]]:
    """
    Validate a Claude Code skill directory.

    Returns:
        tuple[bool, list[str]]: (is_valid, list_of_errors)
    """
    errors = []
    skill_path = Path(skill_dir)

    # Check if directory exists
    if not skill_path.exists():
        return False, [f"Skill directory does not exist: {skill_dir}"]

    if not skill_path.is_dir():
        return False, [f"Path is not a directory: {skill_dir}"]

    # Check for SKILL.md
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("Missing required file: SKILL.md")
        return False, errors

    # Read SKILL.md
    try:
        content = skill_md.read_text(encoding='utf-8')
    except Exception as e:
        return False, [f"Failed to read SKILL.md: {e}"]

    # Check for YAML frontmatter
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(frontmatter_pattern, content, re.DOTALL)

    if not match:
        errors.append("SKILL.md missing YAML frontmatter (must start with --- and end with ---)")
        return False, errors

    frontmatter_text = match.group(1)

    # Parse YAML
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML syntax in SKILL.md: {e}")
        return False, errors

    # Validate required fields
    if 'name' not in frontmatter:
        errors.append("Missing required field: 'name'")
    else:
        name = frontmatter['name']

        # Validate name format
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"Invalid name '{name}': must be lowercase letters, numbers, and hyphens only")

        # Validate name length
        if len(name) > 64:
            errors.append(f"Invalid name '{name}': exceeds 64 character limit (length: {len(name)})")

        # Check for underscores
        if '_' in name:
            errors.append(f"Invalid name '{name}': underscores not allowed, use hyphens instead")

        # Check for uppercase
        if name != name.lower():
            errors.append(f"Invalid name '{name}': must be lowercase")

        # Check if name matches directory name
        if skill_path.name != name:
            errors.append(f"Warning: Skill name '{name}' does not match directory name '{skill_path.name}'")

        # Recommend gerund form for skills
        if not name.endswith('ing') and not any(word in name for word in ['-ing-', 'analyzing', 'building', 'creating', 'generating', 'processing', 'writing']):
            errors.append(f"Recommendation: Skill names typically use gerund form (verb + -ing): '{name}' → consider 'building-{name}' or '{name}ing'")

    if 'description' not in frontmatter:
        errors.append("Missing required field: 'description'")
    else:
        description = frontmatter['description']

        # Validate description length
        if len(description) > 1024:
            errors.append(f"Description too long: {len(description)} characters (max 1024)")

        # Warn if description is too short
        if len(description) < 30:
            errors.append(f"Warning: Description is very short ({len(description)} chars). For skills, describe WHEN Claude should auto-invoke.")

        # Check for auto-invocation triggers
        trigger_keywords = ['use when', 'when', 'for', 'whenever', 'if']
        if not any(keyword in description.lower() for keyword in trigger_keywords):
            errors.append("Recommendation: Skill description should clearly state WHEN Claude should use it (e.g., 'Use when...')")

    # Validate optional fields
    if 'version' in frontmatter:
        version = frontmatter['version']
        if not re.match(r'^\d+\.\d+\.\d+', str(version)):
            errors.append(f"Warning: Version '{version}' doesn't follow semantic versioning (e.g., 1.0.0)")

    if 'allowed-tools' in frontmatter:
        tools = frontmatter['allowed-tools']
        valid_tools = [
            'Read', 'Write', 'Edit', 'Grep', 'Glob', 'Bash',
            'WebFetch', 'WebSearch', 'NotebookEdit', 'Task',
            'TodoWrite', 'BashOutput', 'KillShell'
        ]

        # Check if using wrong YAML list format instead of comma-separated string
        if isinstance(tools, list):
            errors.append("CRITICAL ERROR: 'allowed-tools' must be a comma-separated string, NOT a YAML list!")
            errors.append("")
            errors.append("   Current format (WRONG):")
            errors.append("   allowed-tools:")
            for tool in tools[:3]:
                errors.append(f"     - {tool}")
            if len(tools) > 3:
                errors.append("     ...")
            errors.append("")
            errors.append(f"   Correct format: allowed-tools: {', '.join(tools)}")
            errors.append("")
        elif isinstance(tools, str):
            tool_list = [t.strip() for t in tools.split(',')]
            for tool in tool_list:
                if tool not in valid_tools:
                    errors.append(f"Warning: Unknown tool '{tool}'. Valid tools: {', '.join(valid_tools)}")

    # Skills do not support the 'model' field - only agents support it
    if 'model' in frontmatter:
        errors.append("Invalid field 'model': Skills do not support model specification. Only agents can specify a model. Remove this field.")

    # Check body content
    body = content[match.end():]
    if len(body.strip()) < 100:
        errors.append("Warning: Skill body is very short. Consider adding detailed instructions and examples.")

    # Check for {baseDir} usage
    if 'scripts' in [p.name for p in skill_path.iterdir()] or \
       'references' in [p.name for p in skill_path.iterdir()] or \
       'assets' in [p.name for p in skill_path.iterdir()]:
        if '{baseDir}' not in body:
            errors.append("Recommendation: Use {baseDir} variable to reference resources in scripts/, references/, or assets/")

    # Check for common sections
    if '## when to use' not in body.lower():
        errors.append("Recommendation: Add a 'When to Use This Skill' section to document auto-invocation triggers")

    if '## capabilities' not in body.lower():
        errors.append("Recommendation: Add a capabilities section to document what the skill can do")

    # Check directory structure
    valid_subdirs = ['scripts', 'references', 'assets']
    for subdir in skill_path.iterdir():
        if subdir.is_dir() and subdir.name not in valid_subdirs and not subdir.name.startswith('.'):
            errors.append(f"Warning: Unexpected subdirectory '{subdir.name}'. Standard subdirs: {', '.join(valid_subdirs)}")

    # Check if scripts are executable
    scripts_dir = skill_path / 'scripts'
    if scripts_dir.exists():
        for script in scripts_dir.iterdir():
            if script.is_file() and script.suffix in ['.sh', '.py']:
                if not script.stat().st_mode & 0o111:
                    errors.append(f"Warning: Script '{script.name}' is not executable. Run: chmod +x {script}")

    return len([e for e in errors if not (e.startswith('Warning:') or e.startswith('Recommendation:'))]) == 0, errors


def main():
    if len(sys.argv) < 2:
        print("Usage: validate-skill.py <skill-directory>")
        sys.exit(1)

    skill_dir = sys.argv[1]
    is_valid, errors = validate_skill(skill_dir)

    if is_valid and not errors:
        print(f"✓ Skill '{skill_dir}' is valid!")
        sys.exit(0)
    else:
        print(f"Validation results for '{skill_dir}':\n")

        critical_errors = []
        warnings = []
        recommendations = []

        for error in errors:
            if error.startswith("Warning:"):
                warnings.append(error)
            elif error.startswith("Recommendation:"):
                recommendations.append(error)
            else:
                critical_errors.append(error)

        if critical_errors:
            print("❌ Critical Errors:")
            for error in critical_errors:
                print(f"   {error}")
            print()

        if warnings:
            print("⚠️  Warnings:")
            for warning in warnings:
                print(f"   {warning}")
            print()

        if recommendations:
            print("💡 Recommendations:")
            for rec in recommendations:
                print(f"   {rec}")
            print()

        sys.exit(1 if critical_errors else 0)


if __name__ == '__main__':
    main()
