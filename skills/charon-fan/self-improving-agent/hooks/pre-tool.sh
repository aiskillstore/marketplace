#!/usr/bin/env bash
set -euo pipefail

tool_name="${1:-unknown}"
tool_input="${2:-}"

echo "[self-improving-agent] PreToolUse: ${tool_name}" >&2
if [[ "${SELF_IMPROVING_AGENT_DEBUG:-0}" == "1" && -n "${tool_input}" ]]; then
  printf '[self-improving-agent] Input length: %s bytes\n' "${#tool_input}" >&2
fi
