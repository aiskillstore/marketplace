#!/usr/bin/env python3
"""Verify skill tracker installation."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

# Path constants
PROJECT_ROOT = Path.cwd()
HOOKS_DIR = PROJECT_ROOT / ".claude" / "hooks"
LOGS_DIR = PROJECT_ROOT / ".claude" / "activity-logs"
SETTINGS_FILE = PROJECT_ROOT / ".claude" / "settings.json"

REQUIRED_SCRIPTS = [
    "track-prompt.sh",
    "track-skill-start.sh",
    "track-skill-end.sh",
    "analyze-skills.py",
]

REQUIRED_HOOKS = ["UserPromptSubmit", "PreToolUse", "PostToolUse"]


def check_directories() -> bool:
    """T018: Verify hooks and activity-logs directories exist."""
    errors = []

    if not HOOKS_DIR.exists():
        errors.append(f"Missing: {HOOKS_DIR}")
    if not LOGS_DIR.exists():
        errors.append(f"Missing: {LOGS_DIR}")

    if errors:
        print("Directories:")
        for e in errors:
            print(f"  {e}")
        return False

    print("Directories: OK")
    return True


def check_hook_scripts() -> bool:
    """T019: Verify all scripts exist and are executable."""
    errors = []

    for script in REQUIRED_SCRIPTS:
        path = HOOKS_DIR / script
        if not path.exists():
            errors.append(f"Missing: {path}")
        elif not path.stat().st_mode & 0o111:
            errors.append(f"Not executable: {path}")

    if errors:
        print("Hook scripts:")
        for e in errors:
            print(f"  {e}")
        return False

    print("Hook scripts: OK")
    return True


def check_jq() -> bool:
    """T020: Verify jq command is available."""
    if shutil.which("jq") is None:
        print("jq: NOT FOUND")
        print("  Install with: brew install jq (macOS) or apt install jq (Linux)")
        return False

    print("jq: OK")
    return True


def check_settings() -> bool:
    """T021: Verify settings.json has hook configurations."""
    if not SETTINGS_FILE.exists():
        print(f"Settings: Missing {SETTINGS_FILE}")
        return False

    try:
        with open(SETTINGS_FILE) as f:
            settings = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Settings: Invalid JSON - {e}")
        return False

    hooks = settings.get("hooks", {})
    missing = [h for h in REQUIRED_HOOKS if h not in hooks]

    if missing:
        print("Settings: Missing hooks")
        for h in missing:
            print(f"  - {h}")
        return False

    print("Settings: OK")
    return True


def main():
    """T022: Run all checks and exit with appropriate code."""
    print("=" * 50)
    print("SKILL TRACKER VERIFICATION")
    print("=" * 50)
    print()

    checks = [
        check_directories(),
        check_hook_scripts(),
        check_jq(),
        check_settings(),
    ]

    print()

    if all(checks):
        print("All checks passed")
        sys.exit(0)
    else:
        print("Some checks failed. Run setup.py to fix:")
        print("  python .claude/skills/installing-skill-tracker/scripts/setup.py")
        sys.exit(1)


if __name__ == "__main__":
    main()