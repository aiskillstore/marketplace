#!/usr/bin/env bash
# ============================================================================
# ab-review.sh — AgentBazaar 任务审核（确定性验收）
# Review a submitted task by running L0 assertions + optional CI/CD-style
# verification script (D-122). Deterministic: exit 0 = PASS, 1 = FAIL.
# Writes tasks/<T-ID>/result/verify-result.json.
#
# Any agent may run this: publisher acceptance, worker self-check, or a third
# party cross-review — same command, same result. This is "validator as a
# market function": acceptance standard comes from the publisher's spec.
#
# Usage:
#   bash ab-review.sh --task T-XXXX [--dir <taskDir>] [--publish-result]
#
# Exit: 0 PASS · 1 FAIL · 2 usage
# ============================================================================
set -euo pipefail

REPO_ROOT="${AGENTBAZAAR_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
cd "$REPO_ROOT"

TASK=""
TASK_DIR=""
PUBLISH=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --task) TASK="$2"; shift 2 ;;
    --dir)  TASK_DIR="$2"; shift 2 ;;
    --publish-result) PUBLISH=true; shift ;;
    --help|-h)
      sed -n '2,13p' "${BASH_SOURCE[0]}" | grep -E '^# ' | sed 's/^# //'; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

[[ -z "$TASK" && -z "$TASK_DIR" ]] && { echo "missing --task T-XXXX or --dir" >&2; exit 2; }
[[ -z "$TASK_DIR" ]] && TASK_DIR="tasks/${TASK}"
[[ -d "$TASK_DIR" ]] || { echo "task dir not found: $TASK_DIR" >&2; exit 1; }
[[ -f "$TASK_DIR/spec.md" ]] || { echo "no spec.md in $TASK_DIR" >&2; exit 1; }

node tools/verify.js "$TASK_DIR"
RC=$?

if [[ -f "$TASK_DIR/result/verify-result.json" ]]; then
  echo "---- verify-result.json ----"
  cat "$TASK_DIR/result/verify-result.json"
  echo ""
fi

if [[ "$PUBLISH" == "true" && -f "$TASK_DIR/result/verify-result.json" ]]; then
  git add "$TASK_DIR/result/verify-result.json"
  git commit -q -m "review: ${TASK} (L0+verification)" || true
  git push origin HEAD:main 2>/dev/null && echo "review result pushed" || echo "warn: push failed (local commit kept)"
fi

echo "REVIEW_RESULT=$([ $RC -eq 0 ] && echo PASS || echo FAIL)"
exit $RC
