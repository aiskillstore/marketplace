#!/usr/bin/env bash
# SessionEnd hook - kills indexing processes when Claude Code session ends

set -euo pipefail

PROJECT_ROOT="${PWD}"

# Kill all repo-map processes for this project
PIDS=$(pgrep -f "generate-repo-map.py.*${PROJECT_ROOT}" 2>/dev/null || true)
if [[ -n "${PIDS}" ]]; then
    echo "${PIDS}" | xargs kill 2>/dev/null || true
fi

# Output valid JSON for hook
echo '{"continue": true}'
