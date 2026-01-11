#!/usr/bin/env python3
"""
Plugin validation script for Claude Code plugins.
Validates plugin.json schema, directory structure, and component compliance.
"""

import json
import re
import sys
from pathlib import Path
from typing import Tuple, List, Dict, Any

# Ensure UTF-8 output for Unicode characters on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


def validate_plugin(plugin_dir: str) -> Tuple[bool, List[str], List[str]]:
    """
    Validate a Claude Code plugin directory.

    Returns:
        tuple[bool, list[str], list[str]]: (is_valid, errors, warnings)
    """
    errors = []
    warnings = []
    plugin_path = Path(plugin_dir)

    if not plugin_path.is_dir():
        return False, [f"Plugin directory does not exist: {plugin_dir}"], []

    # Check for plugin.json
    plugin_json_path = plugin_path / ".claude-plugin" / "plugin.json"
    if not plugin_json_path.exists():
        errors.append("Missing required file: .claude-plugin/plugin.json")
        return False, errors, warnings

    # Parse plugin.json
    try:
        with open(plugin_json_path, 'r') as f:
            plugin_data = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in plugin.json: {e}")
        return False, errors, warnings
    except Exception as e:
        errors.append(f"Failed to read plugin.json: {e}")
        return False, errors, warnings

    # Validate required fields
    if 'name' not in plugin_data:
        errors.append("Missing required field in plugin.json: 'name'")
    else:
        name = plugin_data['name']

        # Validate name format
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"Invalid plugin name '{name}': must be lowercase letters, numbers, and hyphens only")

        # Validate name length
        if len(name) > 64:
            errors.append(f"Invalid plugin name '{name}': exceeds 64 character limit (length: {len(name)})")

        # Check for underscores
        if '_' in name:
            errors.append(f"Invalid plugin name '{name}': underscores not allowed, use hyphens instead")

        # Check for uppercase
        if name != name.lower():
            errors.append(f"Invalid plugin name '{name}': must be lowercase")

    if 'version' not in plugin_data:
        errors.append("Missing required field in plugin.json: 'version'")
    else:
        version = plugin_data['version']
        # Validate semantic versioning
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            errors.append(f"Invalid version '{version}': must follow semantic versioning (e.g., 1.0.0)")

    if 'description' not in plugin_data:
        errors.append("Missing required field in plugin.json: 'description'")
    else:
        description = plugin_data['description']
        if len(description) < 20:
            warnings.append(f"Description is very short ({len(description)} chars). Consider adding more detail.")
        if len(description) > 1024:
            errors.append(f"Description too long: {len(description)} characters (max 1024)")

    # Validate recommended fields
    if 'author' not in plugin_data:
        warnings.append("Recommendation: Add 'author' field with name, email, and url")
    else:
        author = plugin_data['author']
        if isinstance(author, dict):
            if 'name' not in author:
                warnings.append("Author object missing 'name' field")
            if 'url' not in author and 'email' not in author:
                warnings.append("Author object missing contact information (url or email)")

    if 'license' not in plugin_data:
        warnings.append("Recommendation: Add 'license' field (e.g., 'MIT', 'Apache-2.0')")

    if 'keywords' not in plugin_data:
        warnings.append("Recommendation: Add 'keywords' array for better discoverability")
    else:
        keywords = plugin_data['keywords']
        if not isinstance(keywords, list):
            errors.append("Field 'keywords' must be an array")
        elif len(keywords) < 3:
            warnings.append(f"Only {len(keywords)} keyword(s). Consider adding more for better discoverability.")

    if 'repository' not in plugin_data:
        warnings.append("Recommendation: Add 'repository' URL")

    if 'homepage' not in plugin_data:
        warnings.append("Recommendation: Add 'homepage' URL")

    # Validate component paths
    component_count = 0

    if 'agents' in plugin_data:
        agents = plugin_data['agents']
        if isinstance(agents, str):
            # Single string path - this is WRONG for agents, must be array
            errors.append(f"Field 'agents' must be an array of paths, not a string. Use: [\"./agents/agent.md\"] instead of \"./agents/agent.md\"")
        elif isinstance(agents, list):
            # Array of file paths - check for object format (common mistake)
            for i, agent_item in enumerate(agents):
                if isinstance(agent_item, dict):
                    errors.append(f"Field 'agents[{i}]' is an object but must be a string path. Use \"./agents/file.md\" instead of {{\"name\": ..., \"path\": ...}}")
                elif isinstance(agent_item, str):
                    agent_path = plugin_path / agent_item.lstrip('./')
                    if not agent_path.exists():
                        errors.append(f"Agent file does not exist: {agent_item}")
                    else:
                        component_count += 1
                else:
                    errors.append(f"Field 'agents[{i}]' must be a string path, got {type(agent_item).__name__}")

    if 'skills' in plugin_data:
        skills = plugin_data['skills']
        if isinstance(skills, str):
            # Directory path - allowed for skills
            skills_dir = plugin_path / skills.lstrip('./')
            if not skills_dir.exists():
                errors.append(f"Skills directory does not exist: {skills}")
            elif skills_dir.is_dir():
                skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir()]
                component_count += len(skill_dirs)
                if len(skill_dirs) == 0:
                    warnings.append(f"Skills directory exists but contains no subdirectories: {skills}")
                # Check for SKILL.md in each skill directory
                for skill_dir in skill_dirs:
                    skill_md = skill_dir / "SKILL.md"
                    if not skill_md.exists():
                        errors.append(f"Skill directory missing SKILL.md: {skill_dir.name}")
        elif isinstance(skills, list):
            # Array of directory paths - check for object format (common mistake)
            for i, skill_item in enumerate(skills):
                if isinstance(skill_item, dict):
                    errors.append(f"Field 'skills[{i}]' is an object but must be a string path. Use \"./skills/skill-name\" instead of {{\"name\": ..., \"path\": ...}}")
                elif isinstance(skill_item, str):
                    skill_path = plugin_path / skill_item.lstrip('./')
                    if not skill_path.exists():
                        errors.append(f"Skill directory does not exist: {skill_item}")
                    else:
                        component_count += 1
                        skill_md = skill_path / "SKILL.md"
                        if not skill_md.exists():
                            errors.append(f"Skill directory missing SKILL.md: {skill_item}")
                else:
                    errors.append(f"Field 'skills[{i}]' must be a string path, got {type(skill_item).__name__}")

    if 'commands' in plugin_data:
        commands = plugin_data['commands']
        if isinstance(commands, str):
            # Directory path - allowed for commands
            commands_dir = plugin_path / commands.lstrip('./')
            if not commands_dir.exists():
                errors.append(f"Commands directory does not exist: {commands}")
            elif commands_dir.is_dir():
                # Check for .md files recursively
                command_files = list(commands_dir.rglob("*.md"))
                component_count += len(command_files)
                if len(command_files) == 0:
                    warnings.append(f"Commands directory exists but contains no .md files: {commands}")
        elif isinstance(commands, list):
            # Array of file paths - check for object format (common mistake)
            for i, command_item in enumerate(commands):
                if isinstance(command_item, dict):
                    errors.append(f"Field 'commands[{i}]' is an object but must be a string path. Use \"./commands/cmd.md\" instead of {{\"name\": ..., \"path\": ...}}")
                elif isinstance(command_item, str):
                    command_path = plugin_path / command_item.lstrip('./')
                    if not command_path.exists():
                        errors.append(f"Command file does not exist: {command_item}")
                    else:
                        component_count += 1
                else:
                    errors.append(f"Field 'commands[{i}]' must be a string path, got {type(command_item).__name__}")

    if 'hooks' in plugin_data:
        hooks = plugin_data['hooks']
        if isinstance(hooks, str):
            # Single string path - also allowed for hooks (single hooks.json)
            hook_path = plugin_path / hooks.lstrip('./')
            if not hook_path.exists():
                errors.append(f"Hooks file does not exist: {hooks}")
            else:
                component_count += 1
                # Validate hooks.json
                if hooks.endswith('.json'):
                    try:
                        with open(hook_path, 'r') as f:
                            hook_data = json.load(f)
                        # Basic hooks.json structure validation
                        if 'matchers' not in hook_data and 'hooks' not in hook_data:
                            warnings.append(f"Hooks file missing 'matchers' or 'hooks' field: {hooks}")
                    except json.JSONDecodeError as e:
                        errors.append(f"Invalid JSON in hooks file {hooks}: {e}")
        elif isinstance(hooks, list):
            # Array of file paths - check for object format (common mistake)
            for i, hook_item in enumerate(hooks):
                if isinstance(hook_item, dict):
                    errors.append(f"Field 'hooks[{i}]' is an object but must be a string path. Use \"./hooks/hooks.json\" instead of {{\"name\": ..., \"path\": ...}}")
                elif isinstance(hook_item, str):
                    hook_path = plugin_path / hook_item.lstrip('./')
                    if not hook_path.exists():
                        errors.append(f"Hooks file does not exist: {hook_item}")
                    else:
                        component_count += 1
                        # Validate hooks.json
                        if hook_item.endswith('.json'):
                            try:
                                with open(hook_path, 'r') as f:
                                    hook_data = json.load(f)
                                # Basic hooks.json structure validation
                                if 'matchers' not in hook_data and 'hooks' not in hook_data:
                                    warnings.append(f"Hooks file missing 'matchers' or 'hooks' field: {hook_item}")
                            except json.JSONDecodeError as e:
                                errors.append(f"Invalid JSON in hooks file {hook_item}: {e}")
                else:
                    errors.append(f"Field 'hooks[{i}]' must be a string path, got {type(hook_item).__name__}")
        else:
            errors.append("Field 'hooks' must be a string path or array of paths")

    if component_count == 0:
        warnings.append("Plugin contains no components (agents, skills, commands, or hooks)")

    # Check for README.md
    readme_path = plugin_path / "README.md"
    if not readme_path.exists():
        errors.append("Missing required file: README.md")
    else:
        # Check README.md size
        readme_size = readme_path.stat().st_size
        if readme_size < 200:
            warnings.append(f"README.md is very short ({readme_size} bytes). Consider adding more documentation.")

    # Check for LICENSE file if license is specified
    if 'license' in plugin_data and plugin_data['license']:
        license_path = plugin_path / "LICENSE"
        if not license_path.exists():
            warnings.append("License specified in plugin.json but LICENSE file not found")

    # Security checks
    security_warnings = check_security(plugin_path)
    warnings.extend(security_warnings)

    return len(errors) == 0, errors, warnings


def check_security(plugin_path: Path) -> List[str]:
    """Check for common security issues."""
    warnings = []

    # Check for common secret files
    secret_files = ['.env', 'credentials.json', 'secrets.json', '.env.local']
    for secret_file in secret_files:
        if (plugin_path / secret_file).exists():
            warnings.append(f"Security: Found potential secrets file '{secret_file}'. Ensure it's in .gitignore")

    # Check for executable scripts with dangerous patterns
    for script_file in plugin_path.rglob("*.sh"):
        if script_file.is_file():
            try:
                content = script_file.read_text()
                # Check for dangerous patterns
                if re.search(r'rm\s+-rf\s+/', content):
                    warnings.append(f"Security: Dangerous pattern 'rm -rf /' in {script_file.relative_to(plugin_path)}")
                if re.search(r'eval\s+', content):
                    warnings.append(f"Security: Potentially dangerous 'eval' in {script_file.relative_to(plugin_path)}")
            except Exception:
                pass

    return warnings


def print_validation_results(plugin_name: str, is_valid: bool, errors: List[str], warnings: List[str]):
    """Print validation results in a nice format."""
    print(f"\n{'✅' if is_valid else '❌'} PLUGIN VALIDATION: {plugin_name}")
    print("━" * 50)

    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for error in errors:
            print(f"   • {error}")

    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"   • {warning}")

    if not errors and not warnings:
        print("\n✅ All validations passed! Plugin is ready.")
    elif not errors:
        print(f"\n✅ Validation passed with {len(warnings)} warning(s)")

    print("━" * 50)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate-plugin.py <plugin-directory>")
        print("\nExample:")
        print("  python3 validate-plugin.py ./my-plugin/")
        sys.exit(1)

    plugin_dir = sys.argv[1]
    plugin_name = Path(plugin_dir).name

    is_valid, errors, warnings = validate_plugin(plugin_dir)
    print_validation_results(plugin_name, is_valid, errors, warnings)

    # Exit codes
    if errors:
        sys.exit(1)  # Critical errors
    elif warnings:
        sys.exit(2)  # Warnings only
    else:
        sys.exit(0)  # All good


if __name__ == "__main__":
    main()
