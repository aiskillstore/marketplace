#!/usr/bin/env bash
# ============================================================================
# install_hook.sh — Register commit_guard.py as a PreToolUse hook
#
# Usage:
#   bash /path/to/skill/scripts/install_hook.sh
#
# This script adds a PreToolUse hook to the current project's
# .claude/settings.local.json that intercepts `git commit` and runs
# business conflict analysis via commit_guard.py.
#
# If .claude/settings.local.json already has content, the hook is merged
# into it (existing settings are preserved).
# ============================================================================
set -euo pipefail

# --- Resolve skill root (directory containing scripts/, references/, SKILL.md) ---
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd -W 2>/dev/null || cd "$(dirname "$0")/.." && pwd)"
COMMIT_GUARD="$SKILL_DIR/scripts/commit_guard.py"

if [ ! -f "$COMMIT_GUARD" ]; then
    echo "❌ Cannot find commit_guard.py at: $COMMIT_GUARD"
    echo "   Run this script from its location inside the skill directory."
    exit 1
fi

# --- Target project (cwd) ---
PROJECT_DIR="$(pwd -W 2>/dev/null || pwd)"
CONFIG_DIR="$PROJECT_DIR/.claude"
CONFIG_FILE="$CONFIG_DIR/settings.local.json"

mkdir -p "$CONFIG_DIR"

# --- Escape path for JSON (Windows path with backslashes → forward slashes) ---
# Python on Windows handles forward slashes in file paths fine.
# Use forward slashes to avoid JSON escape issues with backslashes.
GUARD_PATH="${COMMIT_GUARD//\\//}"
PYTHON_EXE="${PYTHON:-python}"
PYTHON_EXE="${PYTHON_EXE//\\//}"

# --- Write or merge hook config ---
if [ -f "$CONFIG_FILE" ]; then
    # Merge: add PreToolUse hook while preserving existing settings.
    # Pass path via env var to avoid shell-injection risk in inline Python.
    _CONFIG_FILE="$CONFIG_FILE" _PYTHON_EXE="$PYTHON_EXE" _GUARD_PATH="$GUARD_PATH" "$PYTHON_EXE" -c "
import json, os, sys

config_file = os.environ['_CONFIG_FILE']
python_exe = os.environ['_PYTHON_EXE']
guard_path = os.environ['_GUARD_PATH']

with open(config_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

if 'hooks' not in data:
    data['hooks'] = {}
if 'PreToolUse' in data.get('hooks', {}):
    print('ℹ️  PreToolUse hook already registered — skipping.')
    sys.exit(0)

data.setdefault('hooks', {})['PreToolUse'] = {
    'matcher': 'git commit',
    'command': python_exe + ' \"' + guard_path + '\"'
}

with open(config_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
"
else
    # Create new config file
    cat > "$CONFIG_FILE" << EOF
{
  "hooks": {
    "PreToolUse": {
      "matcher": "git commit",
      "command": "${PYTHON_EXE} \"${GUARD_PATH}\""
    }
  }
}
EOF
fi

echo ""
echo "✅ Business conflict analysis hook installed!"
echo "   Config: $CONFIG_FILE"
echo "   Guard:  $COMMIT_GUARD"
echo ""
echo "   Next time you run 'git commit', staged changes will be analyzed."
echo "   If P0 breaking changes are detected, the commit will be blocked"
echo "   and a report will be shown for your decision."
echo ""
echo "   To uninstall, delete the 'PreToolUse' entry from:"
echo "     $CONFIG_FILE"
