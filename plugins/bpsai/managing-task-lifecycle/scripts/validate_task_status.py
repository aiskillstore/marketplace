#!/usr/bin/env python3
"""Validate task file format and status.

Usage: python validate_task_status.py TASK-XXX.task.md
"""

import sys
import re
from pathlib import Path


def validate_task_file(filepath: str) -> tuple[bool, list[str]]:
    """Validate a task file.

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []
    path = Path(filepath)

    if not path.exists():
        return False, [f"File not found: {filepath}"]

    content = path.read_text()

    # Check frontmatter exists
    if not content.startswith("---"):
        errors.append("Missing YAML frontmatter (must start with ---)")
        return False, errors

    # Extract frontmatter
    parts = content.split("---", 2)
    if len(parts) < 3:
        errors.append("Invalid frontmatter format (missing closing ---)")
        return False, errors

    frontmatter = parts[1]

    # Required fields
    required = ["id", "title", "status"]
    for field in required:
        if f"{field}:" not in frontmatter:
            errors.append(f"Missing required field: {field}")

    # Valid status values
    valid_statuses = ["pending", "in_progress", "blocked", "review", "done"]
    status_match = re.search(r"status:\s*(\w+)", frontmatter)
    if status_match:
        status = status_match.group(1)
        if status not in valid_statuses:
            errors.append(f"Invalid status '{status}'. Must be one of: {valid_statuses}")

    # Check for acceptance criteria section
    body = parts[2] if len(parts) > 2 else ""
    if "## Acceptance Criteria" not in body and "## acceptance criteria" not in body.lower():
        errors.append("Missing '## Acceptance Criteria' section")

    return len(errors) == 0, errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_task_status.py TASK-FILE.task.md")
        print("       python validate_task_status.py TASK-XXX")
        sys.exit(1)

    task_input = sys.argv[1]

    # Handle both full path and task ID
    if task_input.startswith("TASK-") and not task_input.endswith(".md"):
        # Search for task file
        task_dirs = [
            Path(".paircoder/tasks"),
            Path(".paircoder/tasks/archive"),
        ]
        found = None
        for task_dir in task_dirs:
            for f in task_dir.glob(f"{task_input}*.task.md"):
                found = f
                break
        if not found:
            print(f"Error: Could not find task file for {task_input}")
            sys.exit(1)
        filepath = str(found)
    else:
        filepath = task_input

    is_valid, errors = validate_task_file(filepath)

    if is_valid:
        print(f"✓ {filepath} is valid")
        sys.exit(0)
    else:
        print(f"✗ {filepath} has {len(errors)} error(s):")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
