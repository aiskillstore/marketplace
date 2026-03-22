#!/usr/bin/env bash
# Launch OpenCode with writable runtime directories.
# Useful when default HOME/XDG paths are readonly in sandboxed environments.

set -euo pipefail

if ! command -v opencode >/dev/null 2>&1; then
  echo "opencode CLI not found. Install via: npm install -g opencode-ai" >&2
  exit 1
fi

SESSION_KEY="$(python3 -c "import hashlib,os; print(hashlib.md5(os.getcwd().encode()).hexdigest()[:8])" 2>/dev/null || echo "default")"
RUNTIME_ROOT="/tmp/jeo-opencode-${SESSION_KEY}"

export XDG_DATA_HOME="${RUNTIME_ROOT}/data"
export XDG_STATE_HOME="${RUNTIME_ROOT}/state"
export XDG_CACHE_HOME="${RUNTIME_ROOT}/cache"

mkdir -p "${XDG_DATA_HOME}" "${XDG_STATE_HOME}" "${XDG_CACHE_HOME}"

exec opencode "$@"
