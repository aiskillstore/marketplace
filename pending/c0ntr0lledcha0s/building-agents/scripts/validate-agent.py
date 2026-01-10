#!/usr/bin/env python3
"""
Agent validation script for Claude Code agents.
Validates YAML frontmatter, naming conventions, and schema compliance.
"""

import re
import sys
import yaml
from pathlib import Path

# Ensure UTF-8 output for Unicode characters on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


def validate_agent(file_path: str) -> tuple[bool, list[str]]:
    """
    Validate a Claude Code agent file.

    Returns:
        tuple[bool, list[str]]: (is_valid, list_of_errors)
    """
    errors = []

    try:
        content = Path(file_path).read_text(encoding='utf-8')
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

    if 'description' not in frontmatter:
        errors.append("Missing required field: 'description'")
    else:
        description = frontmatter['description']

        # Validate description length
        if len(description) > 1024:
            errors.append(f"Description too long: {len(description)} characters (max 1024)")

        # Warn if description is too short
        if len(description) < 20:
            errors.append(f"Warning: Description is very short ({len(description)} chars). Consider adding more detail about when to use this agent.")

    # Validate capabilities field (recommended)
    if 'capabilities' not in frontmatter:
        errors.append("Recommendation: Add 'capabilities' field listing specialized tasks this agent can perform (e.g., capabilities: [\"task1\", \"task2\"])")
    else:
        capabilities = frontmatter['capabilities']

        # Validate capabilities is a list
        if not isinstance(capabilities, list):
            errors.append(f"Invalid capabilities field: must be an array (e.g., [\"task1\", \"task2\"])")
        else:
            # Validate each capability is a string
            for i, cap in enumerate(capabilities):
                if not isinstance(cap, str):
                    errors.append(f"Invalid capability at index {i}: must be a string")
                elif len(cap.strip()) == 0:
                    errors.append(f"Invalid capability at index {i}: cannot be empty")
                # Recommend kebab-case format
                elif not re.match(r'^[a-z0-9-]+$', cap):
                    errors.append(f"Recommendation: Capability '{cap}' should use kebab-case (lowercase with hyphens)")

            # Warn if too many capabilities
            if len(capabilities) > 10:
                errors.append(f"Warning: {len(capabilities)} capabilities listed. Consider keeping it focused (3-7 is ideal)")

            # Warn if no capabilities
            if len(capabilities) == 0:
                errors.append("Warning: Capabilities array is empty. Add task descriptions to help Claude understand when to invoke this agent.")

    # Validate optional fields
    if 'tools' in frontmatter:
        tools = frontmatter['tools']
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

            # Warn about Task tool in agents (subagents can't spawn subagents)
            if 'Task' in tool_list:
                errors.append("Warning: Agent has 'Task' tool but subagents cannot spawn other subagents. Consider removing Task or using a skill for orchestration patterns.")

    if 'model' in frontmatter:
        model = frontmatter['model']
        valid_models = ['sonnet', 'opus', 'haiku', 'inherit']
        if model not in valid_models:
            errors.append(f"Invalid model '{model}'. Valid models: {', '.join(valid_models)}")

    # Validate color field (optional but recommended)
    if 'color' in frontmatter:
        color = frontmatter['color']
        # Validate hex color format: #RRGGBB
        if not isinstance(color, str):
            errors.append(f"Invalid color type: must be a string (e.g., \"#3498DB\")")
        elif not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            errors.append(f"Invalid color format '{color}': must be 6-digit hex with # prefix (e.g., \"#3498DB\")")
    else:
        errors.append("Recommendation: Add 'color' field for visual identification in terminal (e.g., color: \"#3498DB\")")

    # Check for body content
    body = content[match.end():]
    if len(body.strip()) < 100:
        errors.append("Warning: Agent body is very short. Consider adding more detailed instructions, examples, and guidelines.")

    # Check for common sections
    if '## Your Capabilities' not in body and '## Capabilities' not in body:
        errors.append("Recommendation: Add a capabilities section to document what the agent can do")

    if '## Your Workflow' not in body and '## Workflow' not in body:
        errors.append("Recommendation: Add a workflow section to document the agent's process")

    return len(errors) == 0, errors


def main():
    if len(sys.argv) < 2:
        print("Usage: validate-agent.py <agent-file.md>")
        sys.exit(1)

    agent_file = sys.argv[1]
    is_valid, errors = validate_agent(agent_file)

    if is_valid:
        print(f"✓ Agent '{agent_file}' is valid!")
        sys.exit(0)
    else:
        print(f"✗ Agent '{agent_file}' has validation issues:\n")
        for error in errors:
            if error.startswith("Warning:") or error.startswith("Recommendation:"):
                print(f"  ⚠️  {error}")
            else:
                print(f"  ❌ {error}")

        # Exit with error only for critical issues (not warnings)
        critical_errors = [e for e in errors if not (e.startswith("Warning:") or e.startswith("Recommendation:"))]
        sys.exit(1 if critical_errors else 0)


if __name__ == '__main__':
    main()
