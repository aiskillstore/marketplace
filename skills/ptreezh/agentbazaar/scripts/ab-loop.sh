#!/usr/bin/env bash
# ============================================================================
# ab-loop.sh — AgentBazaar worker 认领循环（增量，低上下文）
# Discover → claim → execute → submit, driven by agent-runner.js (v2.0 loop).
# Reads DISCOVERY incrementally; never full-polls the repo.
#
# Usage:
#   bash ab-loop.sh --agent <ID> [--interval 30] [--max-rounds 0]
#                   [--llm auto|mock|manual] [--gateway <URL>]
#
# Exit: 0 ok · 1 failed · 2 usage
# ============================================================================
set -euo pipefail

REPO_ROOT="${AGENTBAZAAR_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
cd "$REPO_ROOT"

AGENT_ID=""
INTERVAL=30
MAX_ROUNDS=0
LLM="auto"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent) AGENT_ID="$2"; shift 2 ;;
    --interval) INTERVAL="$2"; shift 2 ;;
    --max-rounds) MAX_ROUNDS="$2"; shift 2 ;;
    --llm) LLM="$2"; shift 2 ;;
    --help|-h)
      sed -n '2,9p' "${BASH_SOURCE[0]}" | grep -E '^# ' | sed 's/^# //'; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

[[ -z "$AGENT_ID" ]] && { echo "missing --agent" >&2; exit 2; }
[[ -f "keys/${AGENT_ID}/private.pem" ]] || { echo "no key — run ab-register.sh --agent $AGENT_ID first" >&2; exit 1; }

node tools/agent-runner.js loop --agent "$AGENT_ID" --interval "$INTERVAL" --max-rounds "$MAX_ROUNDS" --llm "$LLM"
exit $?
