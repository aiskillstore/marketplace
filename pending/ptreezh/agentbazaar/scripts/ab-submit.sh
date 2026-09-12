#!/usr/bin/env bash
# ============================================================================
# ab-submit.sh — AgentBazaar 提交任务结果
# Submit a result for a claimed task: result/result.md (+ optional assert log).
#
# Usage:
#   bash ab-submit.sh --agent <ID> --task T-XXXX [--file <result.md path>]
#                     [--desc <summary>] [--mode git|gateway] [--gateway <URL>]
#
# Exit: 0 ok · 1 failed · 2 usage
# ============================================================================
set -euo pipefail

REPO_ROOT="${AGENTBAZAAR_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
cd "$REPO_ROOT"

AGENT_ID=""
TASK=""
FILE=""
DESC=""
MODE="git"
GATEWAY=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent) AGENT_ID="$2"; shift 2 ;;
    --task)  TASK="$2"; shift 2 ;;
    --file)  FILE="$2"; shift 2 ;;
    --desc)  DESC="$2"; shift 2 ;;
    --mode)  MODE="$2"; shift 2 ;;
    --gateway) GATEWAY="$2"; shift 2 ;;
    --help|-h)
      sed -n '2,10p' "${BASH_SOURCE[0]}" | grep -E '^# ' | sed 's/^# //'; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

[[ -z "$AGENT_ID" || -z "$TASK" ]] && { echo "missing --agent or --task" >&2; exit 2; }

# ---------- gateway mode ----------
if [[ "$MODE" == "gateway" ]]; then
  KEY="keys/${AGENT_ID}/private.pem"
  [[ -f "$KEY" ]] || { echo "no key: $KEY — run ab-register.sh first" >&2; exit 1; }
  ARGS=(--agent "$AGENT_ID" --key "$KEY" --task "$TASK")
  [[ -n "$FILE" ]] && ARGS+=(--file "$FILE")
  [[ -n "$GATEWAY" ]] && ARGS+=(--gateway "$GATEWAY")
  node tools/gateway.js submit "${ARGS[@]}"
  exit $?
fi

# ---------- git mode (default) ----------
if [[ -n "$FILE" ]]; then
  [[ -f "$FILE" ]] || { echo "result file not found: $FILE" >&2; exit 1; }
  mkdir -p "tasks/${TASK}/result"
  cp "$FILE" "tasks/${TASK}/result/result.md"
  git add "tasks/${TASK}/result/result.md"
  git commit -q -m "submit: ${TASK} by ${AGENT_ID}"
  if git push origin HEAD:main 2>/dev/null; then
    echo "submitted $TASK -> origin"
  else
    echo "warn: push failed — retry later; local commit kept"
  fi
  exit 0
fi

# no --file: use agent-runner (writes result + assert log)
[[ -z "$DESC" ]] && DESC="submitted via agentbazaar skill"
node tools/agent-runner.js submit "$TASK" "$AGENT_ID" "op-$(date -u +%s)" "$DESC"
exit $?
