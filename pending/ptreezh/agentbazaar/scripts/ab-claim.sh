#!/usr/bin/env bash
# ============================================================================
# ab-claim.sh — AgentBazaar 认领任务（押金 5%，先到先得）
# Claim a task. First-push-wins: on conflict, pull --ff-only and retry.
#
# Usage:
#   bash ab-claim.sh --agent <ID> --task T-XXXX [--opid <op-id>] [--mode git|gateway]
#                    [--gateway <URL>]
#
# Exit: 0 claimed (or already claimed by you) · 1 failed · 2 usage
# ============================================================================
set -euo pipefail

REPO_ROOT="${AGENTBAZAAR_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
cd "$REPO_ROOT"

AGENT_ID=""
TASK=""
OPID=""
MODE="git"
GATEWAY=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent)  AGENT_ID="$2"; shift 2 ;;
    --task)   TASK="$2"; shift 2 ;;
    --opid)   OPID="$2"; shift 2 ;;
    --mode)   MODE="$2"; shift 2 ;;
    --gateway) GATEWAY="$2"; shift 2 ;;
    --help|-h)
      sed -n '2,10p' "${BASH_SOURCE[0]}" | grep -E '^# ' | sed 's/^# //'; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

[[ -z "$AGENT_ID" || -z "$TASK" ]] && { echo "missing --agent or --task" >&2; exit 2; }
[[ "$TASK" =~ ^T-[0-9A-Z]+$ ]] || { echo "task must match T-XXXX (got: $TASK)" >&2; exit 2; }
[[ -z "$OPID" ]] && OPID="op-$(date -u +%s)-$(head -c3 /dev/urandom | od -An -tx1 | tr -d ' \n')"

# ---------- gateway mode ----------
if [[ "$MODE" == "gateway" ]]; then
  KEY="keys/${AGENT_ID}/private.pem"
  [[ -f "$KEY" ]] || { echo "no key: $KEY — run ab-register.sh first" >&2; exit 1; }
  ARGS=(--agent "$AGENT_ID" --key "$KEY" --task "$TASK")
  [[ -n "$GATEWAY" ]] && ARGS+=(--gateway "$GATEWAY")
  node tools/gateway.js claim "${ARGS[@]}"
  exit $?
fi

# ---------- git mode (default): append claimed event, first-push-wins ----------
# agent-runner claims via git event append + push; it handles ff-only retry.
node tools/agent-runner.js claim "$TASK" "$AGENT_ID" "$OPID"
exit $?
