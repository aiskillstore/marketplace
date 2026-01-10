#!/usr/bin/env python3
"""
Hooks validation script for Claude Code hooks configuration.
Validates JSON syntax, event names, matchers, and hook structure.
"""

import json
import sys
import re
from pathlib import Path

# Ensure UTF-8 output for Unicode characters on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


def validate_hooks(file_path: str) -> tuple[bool, list[str]]:
    """
    Validate a Claude Code hooks configuration file.

    Returns:
        tuple[bool, list[str]]: (is_valid, list_of_errors)
    """
    errors = []
    path = Path(file_path)

    if not path.exists():
        return False, [f"File does not exist: {file_path}"]

    # Read file
    try:
        content = path.read_text(encoding='utf-8')
    except Exception as e:
        return False, [f"Failed to read file: {e}"]

    # Parse JSON
    try:
        config = json.loads(content)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON syntax: {e}"]

    # Check top-level structure
    if 'hooks' not in config:
        errors.append("Missing top-level 'hooks' field")
        return False, errors

    hooks = config['hooks']
    if not isinstance(hooks, dict):
        errors.append("'hooks' field must be an object")
        return False, errors

    # Valid event names
    valid_events = [
        'PreToolUse',
        'PostToolUse',
        'UserPromptSubmit',
        'Stop',
        'SessionStart',
        'SessionEnd',
        'Notification',
        'SubagentStop',
        'PreCompact'
    ]

    # Events that require matchers
    tool_events = ['PreToolUse', 'PostToolUse']

    # Events that should NOT have matchers
    lifecycle_events = [
        'UserPromptSubmit',
        'Stop',
        'SessionStart',
        'SessionEnd',
        'Notification',
        'SubagentStop',
        'PreCompact'
    ]

    # Validate each event
    for event_name, event_hooks in hooks.items():
        # Check event name
        if event_name not in valid_events:
            errors.append(f"Invalid event name '{event_name}'. Valid events: {', '.join(valid_events)}")
            continue

        # Check event hooks is a list
        if not isinstance(event_hooks, list):
            errors.append(f"Event '{event_name}' must contain a list of hook configurations")
            continue

        # Validate each hook configuration
        for i, hook_config in enumerate(event_hooks):
            hook_num = i + 1

            # Check for matcher field
            if event_name in tool_events:
                if 'matcher' not in hook_config:
                    errors.append(f"Event '{event_name}' hook #{hook_num}: Missing required 'matcher' field")
                else:
                    matcher = hook_config['matcher']
                    # Validate matcher pattern
                    if matcher == '':
                        errors.append(f"Event '{event_name}' hook #{hook_num}: Empty matcher (use '*' for all tools)")

                    # Try to compile as regex
                    try:
                        re.compile(matcher)
                    except re.error as e:
                        errors.append(f"Event '{event_name}' hook #{hook_num}: Invalid regex in matcher '{matcher}': {e}")

            elif event_name in lifecycle_events:
                if 'matcher' in hook_config and hook_config['matcher']:
                    errors.append(f"Event '{event_name}' hook #{hook_num}: Should not have 'matcher' field (lifecycle events don't use matchers)")

            # Check hooks array
            if 'hooks' not in hook_config:
                errors.append(f"Event '{event_name}' hook #{hook_num}: Missing 'hooks' array")
                continue

            if not isinstance(hook_config['hooks'], list):
                errors.append(f"Event '{event_name}' hook #{hook_num}: 'hooks' must be an array")
                continue

            # Validate individual hooks
            for j, hook in enumerate(hook_config['hooks']):
                hook_item_num = j + 1

                if 'type' not in hook:
                    errors.append(f"Event '{event_name}' hook #{hook_num}, item #{hook_item_num}: Missing 'type' field")
                    continue

                hook_type = hook['type']

                if hook_type == 'command':
                    if 'command' not in hook:
                        errors.append(f"Event '{event_name}' hook #{hook_num}, item #{hook_item_num}: Missing 'command' field for command type")
                    else:
                        command = hook['command']
                        # Check if command looks valid
                        if not command.strip():
                            errors.append(f"Event '{event_name}' hook #{hook_num}, item #{hook_item_num}: Empty command")

                        # Check if script file exists (if it looks like a file path)
                        if command.startswith('bash ') or command.startswith('sh '):
                            script_path = command.split()[1] if len(command.split()) > 1 else None
                            if script_path and script_path.startswith('/'):
                                script_file = Path(script_path)
                                if not script_file.exists():
                                    errors.append(f"Warning: Script file does not exist: {script_path}")
                                elif not script_file.stat().st_mode & 0o111:
                                    errors.append(f"Warning: Script file is not executable: {script_path}")

                elif hook_type == 'prompt':
                    if 'prompt' not in hook:
                        errors.append(f"Event '{event_name}' hook #{hook_num}, item #{hook_item_num}: Missing 'prompt' field for prompt type")
                    else:
                        prompt = hook['prompt']
                        if not prompt.strip():
                            errors.append(f"Event '{event_name}' hook #{hook_num}, item #{hook_item_num}: Empty prompt")

                else:
                    errors.append(f"Event '{event_name}' hook #{hook_num}, item #{hook_item_num}: Invalid type '{hook_type}'. Valid types: 'command', 'prompt'")

    # Check for common mistakes
    if not hooks:
        errors.append("Warning: No hooks defined (hooks object is empty)")

    return len([e for e in errors if not e.startswith('Warning:')]) == 0, errors


def main():
    if len(sys.argv) < 2:
        print("Usage: validate-hooks.py <hooks.json>")
        sys.exit(1)

    hooks_file = sys.argv[1]
    is_valid, errors = validate_hooks(hooks_file)

    if is_valid and not errors:
        print(f"✓ Hooks configuration '{hooks_file}' is valid!")
        sys.exit(0)
    else:
        print(f"Validation results for '{hooks_file}':\n")

        critical_errors = []
        warnings = []

        for error in errors:
            if error.startswith("Warning:"):
                warnings.append(error)
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

        sys.exit(1 if critical_errors else 0)


if __name__ == '__main__':
    main()
