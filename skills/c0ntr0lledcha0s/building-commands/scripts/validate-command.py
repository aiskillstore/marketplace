#!/usr/bin/env python3
"""
Command validation script for Claude Code slash commands.
Validates YAML frontmatter, naming conventions, and schema compliance.
"""

import re
import sys
import yaml
from pathlib import Path

# Ensure UTF-8 output for Unicode characters on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


def validate_command(file_path: str) -> tuple[bool, list[str]]:
    """
    Validate a Claude Code slash command file.

    Returns:
        tuple[bool, list[str]]: (is_valid, list_of_errors)
    """
    errors = []
    path = Path(file_path)

    if not path.exists():
        return False, [f"File does not exist: {file_path}"]

    # Get command name from filename
    command_name = path.stem

    # Validate filename
    if not re.match(r'^[a-z0-9-]+$', command_name):
        errors.append(f"Invalid filename '{command_name}.md': must be lowercase letters, numbers, and hyphens only")

    if '_' in command_name:
        errors.append(f"Invalid filename '{command_name}.md': underscores not allowed, use hyphens instead")

    # Check if name is action-oriented (starts with verb)
    common_verbs = [
        'add', 'build', 'check', 'clean', 'commit', 'create', 'delete', 'deploy',
        'generate', 'get', 'install', 'list', 'make', 'push', 'remove', 'review',
        'run', 'search', 'show', 'test', 'update', 'validate'
    ]
    if not any(command_name.startswith(verb) for verb in common_verbs):
        errors.append(f"Recommendation: Command names are typically action-oriented (start with a verb): '{command_name}' → consider 'run-{command_name}', 'create-{command_name}', etc.")

    # Read file
    try:
        content = path.read_text(encoding='utf-8')
    except Exception as e:
        return False, [f"Failed to read file: {e}"]

    # Check for YAML frontmatter
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(frontmatter_pattern, content, re.DOTALL)

    if not match:
        errors.append("Missing YAML frontmatter (must start with --- and end with ---)")
        return False, errors

    frontmatter_text = match.group(1)

    # Parse YAML
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML syntax: {e}")
        return False, errors

    # Check for recommended fields
    if 'description' not in frontmatter:
        errors.append("Recommendation: Add 'description' field to help users understand what the command does")
    else:
        description = frontmatter['description']
        if len(description) < 10:
            errors.append(f"Warning: Description is very short ({len(description)} chars)")

    # Validate optional fields
    if 'allowed-tools' in frontmatter:
        tools = frontmatter['allowed-tools']
        valid_tools = [
            'Read', 'Write', 'Edit', 'Grep', 'Glob', 'Bash',
            'WebFetch', 'WebSearch', 'NotebookEdit', 'Task',
            'TodoWrite', 'BashOutput', 'KillShell'
        ]

        if isinstance(tools, str):
            tool_list = [t.strip() for t in tools.split(',')]
            for tool in tool_list:
                if tool not in valid_tools:
                    errors.append(f"Warning: Unknown tool '{tool}'. Valid tools: {', '.join(valid_tools)}")

    # Validate model field - commands support version aliases and full IDs, not short aliases
    if 'model' in frontmatter:
        model_value = frontmatter['model']

        # Check if it's a SHORT alias (these DON'T work in commands)
        if model_value in ['haiku', 'sonnet', 'opus', 'inherit']:
            # Map short aliases to version aliases
            version_alias_map = {
                'haiku': 'claude-haiku-4-5',
                'sonnet': 'claude-sonnet-4-5',
                'opus': 'claude-opus-4-5'
            }
            suggested_version = version_alias_map.get(model_value, 'claude-sonnet-4-5')

            errors.append(
                f"CRITICAL ERROR: Commands cannot use short aliases. "
                f"Found: 'model: {model_value}'\n\n"
                f"   📝 Quick Fix Options:\n\n"
                f"   Option 1 (Recommended): Remove the model field entirely\n"
                f"     sed -i '/^model:/d' {file_path}\n\n"
                f"   Option 2: Use version alias instead\n"
                f"     sed -i 's/model: {model_value}/model: {suggested_version}/' {file_path}\n\n"
                f"   ℹ️  Why? Commands execute in conversation context and must use explicit\n"
                f"      version aliases. Only agents can use short aliases like '{model_value}'.\n\n"
                f"   📚 See: agent-builder/skills/building-commands/templates/ for examples"
            )
        # Check if it looks like a valid model ID (basic format check)
        elif not model_value.startswith('claude-'):
            errors.append(
                f"Warning: Model '{model_value}' doesn't match expected format 'claude-*'. "
                f"Ensure this is a valid Anthropic model ID (e.g., 'claude-haiku-4-5' or 'claude-haiku-4-5-20251001')."
            )

    if 'argument-hint' in frontmatter:
        arg_hint = frontmatter['argument-hint']

        # Handle both list and string types (YAML parsing can produce either)
        if isinstance(arg_hint, list):
            arg_hint = ' '.join(str(item) for item in arg_hint)
        elif not isinstance(arg_hint, str):
            arg_hint = str(arg_hint)

        if not arg_hint.startswith('['):
            errors.append(f"Warning: argument-hint typically uses brackets: '{arg_hint}' → '[{arg_hint}]'")

    # Check body content
    body = content[match.end():]

    # Check for argument usage
    uses_positional = bool(re.search(r'\$\d+', body))
    uses_all_args = '$ARGUMENTS' in body

    if uses_positional or uses_all_args:
        if 'argument-hint' not in frontmatter:
            errors.append("Recommendation: Add 'argument-hint' field since the command uses arguments ($1, $2, or $ARGUMENTS)")

        # Document the arguments in body
        if uses_positional and '## Arguments' not in body:
            errors.append("Recommendation: Add an '## Arguments' section to document what each positional argument does")

    # Check for workflow documentation
    if '## Workflow' not in body and '## Steps' not in body:
        errors.append("Recommendation: Add a workflow section to document the command's execution steps")

    # Check for examples
    if '## Example' not in body and '## Usage' not in body:
        errors.append("Recommendation: Add usage examples showing how to invoke the command")

    # Security checks
    if 'Bash' in frontmatter.get('allowed-tools', ''):
        # Check for dangerous patterns
        dangerous_patterns = [
            (r'\$\w+\s*(?:&&|\||;|`)', "Potential command injection risk with unsanitized arguments"),
            (r'rm\s+-rf\s+\$', "Dangerous rm -rf with variable - add validation"),
            (r'eval\s+\$', "Using eval with arguments is dangerous"),
        ]

        for pattern, warning in dangerous_patterns:
            if re.search(pattern, body):
                # Note: This often matches markdown backticks around $ARGUMENTS, not actual injection
                # Treat as recommendation rather than critical error since these are templates for Claude
                errors.append(f"Recommendation: {warning} (review if $variables are used in actual bash blocks)")

    return len([e for e in errors if not (e.startswith('Warning:') or e.startswith('Recommendation:'))]) == 0, errors


def main():
    if len(sys.argv) < 2:
        print("Usage: validate-command.py <command-file.md>")
        sys.exit(1)

    command_file = sys.argv[1]
    is_valid, errors = validate_command(command_file)

    if is_valid and not errors:
        print(f"✓ Command '{command_file}' is valid!")
        sys.exit(0)
    else:
        print(f"Validation results for '{command_file}':\n")

        critical_errors = []
        warnings = []
        recommendations = []

        for error in errors:
            if error.startswith("Security Warning:"):
                critical_errors.append(error)
            elif error.startswith("Warning:"):
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
