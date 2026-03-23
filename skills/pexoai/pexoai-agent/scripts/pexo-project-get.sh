#!/usr/bin/env bash
# If invoked with sh, re-exec with bash (this script uses bash-only syntax).
[ -n "${BASH_VERSION:-}" ] || exec bash "$0" "$@"

usage() {
  cat <<'EOF'
Usage:
  pexo-project-get.sh <project_id> [--full-history]
  pexo-project-get.sh -h | --help

Description:
  Fetch project state and derive nextAction for agent-side orchestration.

Options:
  --full-history   Return simplified full message history instead of nextAction view

Returns:
  Default mode:
    Project JSON with nextAction, nextActionHint, and recentMessages when action is needed
  --full-history:
    Project JSON with recentMessages for the full simplified history

Common errors:
  401  Invalid API key or auth failure
  404  Project not found
  500  Backend/internal failure
EOF
}

# Get project details with next-action recommendation.
# Returns a clean project JSON with:
#
#   nextAction      — WAIT | RESPOND | DELIVER | FAILED | RECONNECT
#   nextActionHint  — plain-language instruction for what to do next
#   recentMessages  — simplified last conversation round (when nextAction is RESPOND / DELIVER / FAILED / RECONNECT)
#
# Raw status fields (status / executionStatus / serviceStatus) and meaningless
# progress values (executionProgress / stepProgress) are stripped from output.
# Callers should only use nextAction to decide what to do.
#
# ── All (executionStatus × serviceStatus) combinations in practice ───────────
# executionStatus: IDLE (DB default / no progress yet), RUNNING, FAILED, INTERRUPTED.
#                  COMPLETED is not used in production (Agent does not send "finished").
# serviceStatus:   IDLE (default or after ProcessExecution exits), PROCESSING (during ProcessExecution).
#
#  | executionStatus | serviceStatus | Scenario | nextAction |
#  |-----------------|---------------|----------|------------|
#  | IDLE            | IDLE          | New project, or no active run; no message sent yet or previous run ended. | WAIT |
#  | IDLE            | PROCESSING    | ProcessExecution just started, no progress event from Agent yet (brief). | WAIT |
#  | RUNNING         | IDLE          | Run was reported RUNNING but worklet already exited (e.g. stream closed). Reconnect by sending a new message. | RECONNECT |
#  | RUNNING         | PROCESSING    | Normal: Agent is producing, worklet is handling the stream. | WAIT |
#  | INTERRUPTED     | IDLE          | Pexo waiting for input; no active ProcessExecution (user must send message or reconnect). | RESPOND |
#  | INTERRUPTED     | PROCESSING    | Pexo waiting for input; ProcessExecution still open (stream waiting for reply). | RESPOND |
#  | FAILED          | IDLE          | Run failed, worklet has exited. | FAILED |
#  | FAILED          | PROCESSING    | Run failed, worklet defer not run yet (brief). | FAILED |
#
# nextAction mapping:
#   FAILED    — executionStatus=FAILED
#   DELIVER   — executionStatus=COMPLETED AND serviceStatus≠PROCESSING (COMPLETED not used in practice)
#   RESPOND   — executionStatus=INTERRUPTED
#   RECONNECT — executionStatus=RUNNING AND serviceStatus=IDLE (should re-initiate conversation via pexo-chat.sh)
#   WAIT      — all other combinations
#
# recentMessages format (simplified, actionable-only):
#   USER      → {role, text}
#   message   → {role, event:"message",       text}
#   final_video    → {role, event:"final_video",   assetId}
#   preview_video  → {role, event:"preview_video", assetIds:[...]}
#   document  → {role, event:"document", documentType, documentName}
#   (planning / progress / thinking / meta / voice etc. are omitted)
#
# Usage: pexo-project-get.sh <project_id> [--full-history]
source "$(dirname "$0")/_common.sh"

case "${1:-}" in
  -h|--help)
    usage
    exit 0
    ;;
esac

if [[ $# -lt 1 ]]; then
  usage >&2
  exit 2
fi

pid="$1"
shift

full_history=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --full-history) full_history=true; shift ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Error: unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

# jq filter: simplify a raw messages array into actionable-only entries.
# ASSISTANT events not listed here (planning, progress, thinking, meta, voice…) are dropped.
_SIMPLIFY_MSGS='[.[] |
  if (.role | ascii_downcase) == "user" then
    {role: "USER", text: (.content.native_inputs.text // null)}
  else
    (.content.event // "") as $evt |
    (.content.data  // {}) as $d  |
    if      $evt == "message"       then {role: "ASSISTANT", event: "message",       text:          ($d.message          // null)}
    elif    $evt == "final_video"   then {role: "ASSISTANT", event: "final_video",   assetId:       ($d.final_video_id   // null)}
    elif    $evt == "preview_video" then {role: "ASSISTANT", event: "preview_video", assetIds:      ($d.preview_video_ids // [])}
    elif    $evt == "document"      then {role: "ASSISTANT", event: "document",      documentType:  ($d.type // null), documentName: ($d.name // null)}
    else empty
    end
  end
]'

_raw=$(pexo_get "/api/biz/projects/${pid}")

# Read status fields needed for nextAction logic before stripping them
exec_status=$(echo "$_raw" | jq -r '.executionStatus // ""')
svc_status=$(echo  "$_raw" | jq -r '.serviceStatus  // ""')

# Strip raw status fields and meaningless progress values from the output project object
project=$(echo "$_raw" | jq 'del(.status, .executionStatus, .serviceStatus, .executionProgress, .stepProgress)')

# ── Full history mode (bypass nextAction logic) ───────────────────────────────
if [[ "$full_history" == "true" ]]; then
  history=$(pexo_get "/api/biz/projects/${pid}/history?page=1&page_size=200&sort_order=ASC")
  raw_msgs=$(echo "$history" | jq 'if type == "array" then . else (.messages // []) end' 2>/dev/null || echo '[]')
  messages=$(echo "$raw_msgs" | jq "$_SIMPLIFY_MSGS" 2>/dev/null || echo '[]')
  echo "$project" | jq --argjson msgs "$messages" '. + {recentMessages: $msgs}'
  exit 0
fi

# ── Determine nextAction from status fields ──────────────────────────────────
if [[ "$exec_status" == "FAILED" ]]; then
  next_action="FAILED"
  hint="Production failed. Read recentMessages for error details. Send a new message via pexo-chat.sh to retry with a modified brief."
elif [[ "$exec_status" == "COMPLETED" && "$svc_status" != "PROCESSING" ]]; then
  next_action="DELIVER"
  hint="Production complete. Find assetId in recentMessages[event=final_video], fetch it with pexo-asset-get.sh."
elif [[ "$exec_status" == "INTERRUPTED" ]]; then
  next_action="RESPOND"
  hint="Pexo is waiting for your input. Read recentMessages to understand what is needed, then call pexo-chat.sh to respond."
elif [[ "$exec_status" == "RUNNING" && "$svc_status" == "IDLE" ]]; then
  next_action="RECONNECT"
  hint="Connection may have been lost. Re-initiate the conversation by sending a new message via pexo-chat.sh."
else
  # IDLE+IDLE, IDLE+PROCESSING, RUNNING+PROCESSING
  next_action="WAIT"
  hint="Production is in progress. Poll again in 60 seconds."
fi

# ── Fetch and simplify recentMessages when caller must act ───────────────────
if [[ "$next_action" == "RESPOND" || "$next_action" == "DELIVER" || "$next_action" == "FAILED" || "$next_action" == "RECONNECT" ]]; then
  # Paginate DESC (newest first) until we find a page with a user message,
  # then take from that user message to the top and reverse to chronological order.
  page=1
  page_size=50
  accumulated='[]'
  recent_raw='[]'
  while true; do
    resp=$(pexo_get "/api/biz/projects/${pid}/history?page=${page}&page_size=${page_size}&sort_order=DESC")
    new_msgs=$(echo "$resp" | jq 'if type == "array" then . else (.messages // []) end' 2>/dev/null || echo '[]')
    has_more=$(echo "$resp" | jq '.hasMore // false' 2>/dev/null)
    accumulated=$(jq -n --argjson a "$accumulated" --argjson b "$new_msgs" '$a + $b' 2>/dev/null || echo '[]')
    user_count=$(echo "$accumulated" | jq '[.[] | select((.role | ascii_downcase) == "user")] | length' 2>/dev/null || echo 0)
    if [[ "${user_count:-0}" -gt 0 ]]; then
      recent_raw=$(echo "$accumulated" | jq '
        . as $all |
        [range(length)] | map(select(($all[.].role | ascii_downcase) == "user")) |
        if length > 0 then (first as $idx | $all[0:($idx+1)] | reverse)
        else []
        end
      ' 2>/dev/null || echo '[]')
      break
    fi
    if [[ "$has_more" != "true" ]]; then
      break
    fi
    page=$((page + 1))
  done

  recent=$(echo "$recent_raw" | jq "$_SIMPLIFY_MSGS" 2>/dev/null || echo '[]')

  echo "$project" | jq \
    --arg  na   "$next_action" \
    --arg  hint "$hint"        \
    --argjson msgs "$recent"   \
    '. + {nextAction: $na, nextActionHint: $hint, recentMessages: $msgs}'
else
  echo "$project" | jq \
    --arg na   "$next_action" \
    --arg hint "$hint"        \
    '. + {nextAction: $na, nextActionHint: $hint}'
fi
