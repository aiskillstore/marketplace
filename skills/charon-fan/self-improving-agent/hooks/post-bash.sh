#!/usr/bin/env bash
set -euo pipefail

tool_output="${1:-}"
exit_code="${2:-0}"

echo "[self-improving-agent] PostToolUse: exit=${exit_code}" >&2
if [[ "${SELF_IMPROVING_AGENT_DEBUG:-0}" == "1" && -n "${tool_output}" ]]; then
  printf '[self-improving-agent] Output length: %s bytes\n' "${#tool_output}" >&2
fi
