#!/usr/bin/env python3
"""Check if a task is ready for completion.

Usage: python check_completion.py TASK-XXX
"""

import subprocess
import sys
import re
from pathlib import Path


def run_command(cmd: list[str]) -> tuple[bool, str]:
    """Run a command and return (success, output)."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def check_tests() -> tuple[bool, str]:
    """Check if tests pass."""
    success, output = run_command(["pytest", "-v", "--tb=short"])
    if success:
        return True, "All tests pass"
    return False, "Tests failing"


def check_linting() -> tuple[bool, str]:
    """Check if linting passes."""
    success, output = run_command(["ruff", "check", "."])
    if success:
        return True, "Linting passes"
    return False, "Linting errors found"


def check_task_file(task_id: str) -> tuple[bool, str]:
    """Check if task file exists and has required fields."""
    task_dirs = [
        Path(".paircoder/tasks"),
    ]
    found = None
    for task_dir in task_dirs:
        for f in task_dir.glob(f"{task_id}*.task.md"):
            found = f
            break

    if not found:
        return False, f"Task file not found for {task_id}"

    content = found.read_text()

    # Check status is not already done
    if re.search(r"status:\s*done", content):
        return True, "Task already marked done"

    # Check acceptance criteria exist
    if "## Acceptance Criteria" not in content:
        return False, "Missing acceptance criteria section"

    return True, f"Task file found: {found}"


def check_uncommitted_changes() -> tuple[bool, str]:
    """Check for uncommitted changes."""
    success, output = run_command(["git", "status", "--porcelain"])
    if success and output.strip():
        return False, "Uncommitted changes exist"
    return True, "Working directory clean"


def main():
    if len(sys.argv) < 2:
        print("Usage: python check_completion.py TASK-XXX")
        sys.exit(1)

    task_id = sys.argv[1]

    print(f"Completion checklist for {task_id}")
    print("=" * 40)

    checks = [
        ("Task file", lambda: check_task_file(task_id)),
        ("Tests", check_tests),
        ("Linting", check_linting),
        ("Git status", check_uncommitted_changes),
    ]

    all_passed = True
    for name, check_fn in checks:
        passed, message = check_fn()
        status = "✓" if passed else "✗"
        print(f"{status} {name}: {message}")
        if not passed:
            all_passed = False

    print("=" * 40)
    if all_passed:
        print("✓ Ready for completion!")
        print("\nNext steps:")
        print(f"  1. bpsai-pair ttask done TRELLO-XX --summary '...' --list 'Deployed/Done'")
        print(f"  2. bpsai-pair task update {task_id} --status done")
        sys.exit(0)
    else:
        print("✗ Not ready - fix issues above first")
        sys.exit(1)


if __name__ == "__main__":
    main()
