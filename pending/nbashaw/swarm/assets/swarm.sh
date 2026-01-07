#!/bin/bash
# Swarm runner - executes headless agents in a loop until completion
# Usage: ./swarm.sh [OPTIONS] PLAN_FILE.md

set -e

# Parse flags
DRY_RUN=false
VERBOSE=false
USE_CODEX=true  # Default to codex

while [[ $# -gt 0 ]]; do
  case $1 in
    -n|--dry-run)
      DRY_RUN=true
      shift
      ;;
    -v|--verbose)
      VERBOSE=true
      shift
      ;;
    --codex)
      USE_CODEX=true
      shift
      ;;
    --claude)
      USE_CODEX=false
      shift
      ;;
    -h|--help)
      echo "Usage: ./swarm.sh [OPTIONS] PLAN_FILE.md"
      echo ""
      echo "Options:"
      echo "  -n, --dry-run    Show what would happen without running agents"
      echo "  -v, --verbose    Print logs, timing, and plan summary"
      echo "  --codex          Use Codex CLI in full-auto mode (default)"
      echo "  --claude         Use Claude CLI instead of Codex"
      echo "  -h, --help       Show this help message"
      echo ""
      echo "Environment variables:"
      echo "  MAX_ITERATIONS   Maximum iterations before stopping (default: 20)"
      exit 0
      ;;
    -*)
      echo "Unknown option: $1"
      echo "Run './swarm.sh --help' for usage"
      exit 1
      ;;
    *)
      PLAN_FILE="$1"
      shift
      ;;
  esac
done

if [ -z "$PLAN_FILE" ]; then
  echo "Usage: ./swarm.sh [OPTIONS] PLAN_FILE.md"
  exit 1
fi

if [ ! -f "$PLAN_FILE" ]; then
  echo "Error: Plan file not found: $PLAN_FILE"
  exit 1
fi

PLAN_NAME=$(basename "$PLAN_FILE" .md | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
DONE_FILE=".context/.done-$PLAN_NAME"
MAX_ITERATIONS=${MAX_ITERATIONS:-20}
N=1

mkdir -p .context

# Function to extract and print Log section
print_log_section() {
  local file="$1"
  awk '/^## Log$/,0' "$file" 2>/dev/null || echo "(No log section found)"
}

# Function to extract and print Goal section
print_goal_section() {
  local file="$1"
  awk '/^## Goal$/,/^## [^G]/' "$file" | sed '$d' 2>/dev/null || echo "(No goal section found)"
}

echo "Starting swarm for: $PLAN_FILE"
echo "Done file: $DONE_FILE"
echo "Max iterations: $MAX_ITERATIONS"
if [ "$USE_CODEX" = true ]; then
  echo "Agent: codex (full-auto mode)"
else
  echo "Agent: claude"
fi
echo ""

if [ "$VERBOSE" = true ]; then
  echo "════════════════════════════════════════"
  echo "  Plan Summary"
  echo "════════════════════════════════════════"
  print_goal_section "$PLAN_FILE"
  echo ""
fi

while [ ! -f "$DONE_FILE" ] && [ $N -le $MAX_ITERATIONS ]; do
  echo "════════════════════════════════════════"
  echo "  Iteration $N"
  echo "════════════════════════════════════════"

  PROMPT="This is iteration $N of the swarm workflow.

Work on the plan at $PLAN_FILE:
1. Read the plan file to understand the goal and current state
2. Check Phase 0 (pre-flight) — if work is already done, skip to Gatekeeper
3. Based on iteration $N:
   - If $((N % 5)) == 0: Adopt Reviewer role (fresh eyes on progress)
   - If all phases complete: Adopt Gatekeeper role
   - Otherwise: Adopt Worker role
4. Execute next uncompleted steps
5. Update checkboxes as you complete them
6. Append your log entry with iteration number, role, and progress
7. If Gatekeeper and GO decision: create done file immediately

Plan file: $(pwd)/$PLAN_FILE
Done file: $DONE_FILE

IMPORTANT: If you are the Gatekeeper and decide GO, you MUST create the done file:
touch $DONE_FILE"

  START_TIME=$(date +%s)

  if [ "$DRY_RUN" = true ]; then
    if [ "$USE_CODEX" = true ]; then
      echo "[DRY-RUN] Would execute: codex exec --full-auto \"$PROMPT\""
    else
      echo "[DRY-RUN] Would execute: claude --dangerously-skip-permissions -p \"$PROMPT\""
    fi
    echo ""
  else
    if [ "$USE_CODEX" = true ]; then
      codex exec --full-auto "$PROMPT"
    else
      claude --dangerously-skip-permissions -p "$PROMPT"
    fi
  fi

  END_TIME=$(date +%s)
  DURATION=$((END_TIME - START_TIME))

  if [ "$VERBOSE" = true ]; then
    echo ""
    echo "────────────────────────────────────────"
    echo "  Iteration $N completed in ${DURATION}s"
    echo "────────────────────────────────────────"
    echo ""
    echo "════════════════════════════════════════"
    echo "  Log Section"
    echo "════════════════════════════════════════"
    print_log_section "$PLAN_FILE"
    echo ""
  fi

  if [ -f "$DONE_FILE" ]; then
    echo ""
    echo "✓ Done file created during iteration $N"
    break
  fi

  N=$((N + 1))
  sleep 2
done

echo ""
echo "════════════════════════════════════════"
if [ -f "$DONE_FILE" ]; then
  echo "✓ Swarm completed after $((N)) iterations"
  echo "  Check the Log section in $PLAN_FILE for details"
else
  echo "✗ Max iterations ($MAX_ITERATIONS) reached without completion"
  echo "  Check the Log section in $PLAN_FILE to see what's blocking"
fi
echo "════════════════════════════════════════"
