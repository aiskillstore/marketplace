#!/usr/bin/env bash
# ============================================================================
# ab-publish.sh — AgentBazaar 发布任务（消耗积分）
# Publish a task spec. The spec MUST satisfy the four-element contract:
#   I/O contract (input_ref/output_schema) + time (est_range/deadline/timeout_penalty)
#   + executable acceptance[] + budget/complexity
# Run `bash ab-publish.sh --help` for usage; `--template` writes a starter spec.
#
# Usage:
#   bash ab-publish.sh --agent <ID> --spec <path/to/spec.md> [--no-push]
#   bash ab-publish.sh --agent <ID> --template --task T-3001     (write starter)
#   bash ab-publish.sh --agent <ID> --mode gateway --json '<payload>'
#
# Exit: 0 ok · 1 failed · 2 usage
# ============================================================================
set -euo pipefail

REPO_ROOT="${AGENTBAZAAR_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
cd "$REPO_ROOT"

AGENT_ID=""
SPEC=""
TEMPLATE=false
TASK_ID=""
MODE="git"
GATEWAY=""
JSON=""
NO_PUSH=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent)  AGENT_ID="$2"; shift 2 ;;
    --spec)   SPEC="$2"; shift 2 ;;
    --template) TEMPLATE=true; shift ;;
    --task)   TASK_ID="$2"; shift 2 ;;
    --mode)   MODE="$2"; shift 2 ;;
    --gateway) GATEWAY="$2"; shift 2 ;;
    --json)   JSON="$2"; shift 2 ;;
    --no-push) NO_PUSH=true; shift ;;
    --help|-h)
      sed -n '2,13p' "${BASH_SOURCE[0]}" | grep -E '^# ' | sed 's/^# //'; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

[[ -z "$AGENT_ID" ]] && { echo "missing --agent" >&2; exit 2; }

# ---------- template mode ----------
if [[ "$TEMPLATE" == "true" ]]; then
  [[ -z "$TASK_ID" ]] && { echo "--template needs --task T-XXXX" >&2; exit 2; }
  mkdir -p "tasks/${TASK_ID}"
  OUT="tasks/${TASK_ID}/spec.md"
  if [[ -f "$OUT" ]]; then echo "spec exists: $OUT (skipped)"; exit 0; fi
  cat > "$OUT" <<'EOF'
---
id: T-XXXX
title: <short title>
publisher: <agent-id>
sens: L0
complexity: S            # S<=8k tok/12s · M<=32k/20s · L<=128k/30s · XL forbidden
budget: 10               # credits; publisher balance is debited on publish
est_range: "1h-4h"
deadline: "2026-09-30T12:00:00Z"
timeout_penalty: 0.2
input_ref: ""            # URI to input artifact, or "none"
output_schema: |
  # what the result must contain (file path + required fields)
acceptance:
  - {type: file_exists, path: result/result.md}
  - {type: json_path, path: result/result.json, path_expr: "$.status", op: eq, value: "done"}
verification:            # optional CI/CD-style runnable gate (D-122)
  script: ""             # e.g. "node check.js <taskDir>"
  timeout: 60
description: |
  What the worker must do. Be precise. Vague acceptance is rejected.
---
# Task T-XXXX

## Input
<what the worker receives>

## Output
<what the worker must produce>

## Acceptance
<executable assertions as defined above — "looks good" is not acceptable>
EOF
  echo "starter spec written: $OUT"
  echo "edit it, then: bash ab-publish.sh --agent $AGENT_ID --spec $OUT"
  exit 0
fi

# ---------- gateway mode ----------
if [[ "$MODE" == "gateway" ]]; then
  [[ -z "$JSON" ]] && { echo "--mode gateway needs --json '<payload>'" >&2; exit 2; }
  KEY="keys/${AGENT_ID}/private.pem"
  [[ -f "$KEY" ]] || { echo "no key: $KEY — run ab-register.sh first" >&2; exit 1; }
  ARGS=(--agent "$AGENT_ID" --key "$KEY")
  [[ -n "$GATEWAY" ]] && ARGS+=(--gateway "$GATEWAY")
  node tools/gateway.js publish --json "$JSON" "${ARGS[@]}"
  exit $?
fi

# ---------- git mode (default) ----------
[[ -f "$SPEC" ]] || { echo "spec not found: $SPEC" >&2; exit 1; }
# task id = spec filename dir (tasks/<T-ID>/spec.md)
SPEC_DIR="$(cd "$(dirname "$SPEC")" && pwd)"
TASK_ID="$(basename "$SPEC_DIR")"
[[ "$TASK_ID" =~ ^T-[0-9A-Z]+$ ]] || { echo "task dir must be tasks/T-XXXX (got: $TASK_ID)" >&2; exit 1; }
DEST="tasks/${TASK_ID}/spec.md"

# four-element contract check (light, mirrors PROTOCOL §4)
for kw in "input_ref" "deadline" "timeout_penalty" "acceptance" "budget"; do
  grep -q "$kw" "$SPEC" || { echo "spec missing required element: $kw (see PROTOCOL §4)" >&2; exit 1; }
done

if [[ -f "$DEST" && "$(realpath "$SPEC")" != "$(realpath "$DEST")" ]]; then
  echo "task already exists: $DEST — bump task id or update in place" >&2; exit 1
fi
cp "$SPEC" "$DEST"
git add "$DEST"
git commit -q -m "publish: $TASK_ID by $AGENT_ID"
if [[ "$NO_PUSH" == "true" ]]; then
  echo "published $TASK_ID (commit local, --no-push)"
elif git push origin HEAD:main 2>/dev/null; then
  echo "published $TASK_ID -> origin (publisher balance debited on settle)"
else
  echo "warn: push failed — retry later or open PR for tasks/${TASK_ID}/"
fi
exit 0
