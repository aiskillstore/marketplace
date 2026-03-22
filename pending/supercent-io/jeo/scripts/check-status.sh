#!/usr/bin/env bash
# JEO Skill — Status Check
# Verifies all JEO components and integrations
# Usage: bash check-status.sh [--resume]

set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; BLUE='\033[0;34m'; BOLD='\033[1m'; NC='\033[0m'
ok()   { echo -e "  ${GREEN}✓${NC} $*"; }
warn() { echo -e "  ${YELLOW}⚠${NC}  $*"; }
err()  { echo -e "  ${RED}✗${NC} $*"; }
info() { echo -e "${BLUE}${BOLD}$*${NC}"; }

RESUME=false
[[ "${1:-}" == "--resume" ]] && RESUME=true

PASS=0; WARN=0; FAIL=0

check() {
  local label="$1"; local cmd="$2"
  if eval "$cmd" >/dev/null 2>&1; then
    ok "$label"; ((PASS++)) || true
  else
    err "$label (not found)"; ((FAIL++)) || true
  fi
}

check_opt() {
  local label="$1"; local cmd="$2"
  if eval "$cmd" >/dev/null 2>&1; then
    ok "$label"; ((PASS++)) || true
  else
    warn "$label (optional — not configured)"; ((WARN++)) || true
  fi
}

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   JEO Skill — Status Check               ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── Prerequisites ─────────────────────────────────────────────────────────────
info "Prerequisites"
check     "node >=18"        "node --version | grep -E 'v(1[89]|[2-9][0-9])'"
check     "npm"              "command -v npm"
check     "git"              "command -v git"
check_opt "bun"              "command -v bun"
check_opt "python3"          "command -v python3"
echo ""

# ── Core Tools ────────────────────────────────────────────────────────────────
info "Core Tools"
check_opt "plannotator CLI"  "command -v plannotator"
check_opt "agent-browser"    "command -v agent-browser || npx agent-browser --version"
check_opt "playwriter"       "command -v playwriter"
echo ""

# ── AI Tool Integrations ──────────────────────────────────────────────────────
info "AI Tool Integrations"

# Claude Code
if [[ -f "${HOME}/.claude/settings.json" ]]; then
  if grep -Eq "claude-plan-gate.py|plannotator" "${HOME}/.claude/settings.json" 2>/dev/null; then
    ok "Claude Code — plannotator hook configured"; ((PASS++)) || true
  else
    warn "Claude Code — plannotator hook not found in settings.json"; ((WARN++)) || true
  fi
  TEAMS_ENABLED=false
  if [[ "${CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS:-}" =~ ^(1|true|True|yes|YES)$ ]]; then
    TEAMS_ENABLED=true
  elif python3 -c "
import json, os, sys
try:
    s = json.load(open(os.path.expanduser('~/.claude/settings.json')))
    val = s.get('env', {}).get('CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS', '')
    sys.exit(0 if str(val) in ('1', 'true', 'True', 'yes') else 1)
except Exception:
    sys.exit(1)
" 2>/dev/null; then
    TEAMS_ENABLED=true
  fi
  if $TEAMS_ENABLED; then
    ok "Claude Code — experimental agent teams enabled"; ((PASS++)) || true
  else
    err "Claude Code — experimental agent teams not enabled (required for JEO team execution)"; ((FAIL++)) || true
  fi
  if grep -q '"agentation"' "${HOME}/.claude/settings.json" 2>/dev/null; then
    ok "Claude Code — agentation MCP configured"; ((PASS++)) || true
  else
    warn "Claude Code — agentation MCP not configured"; ((WARN++)) || true
  fi
  if grep -Eq "claude-agentation-submit-hook.py|localhost:4747/pending" "${HOME}/.claude/settings.json" 2>/dev/null; then
    ok "Claude Code — agentation prompt hook configured"; ((PASS++)) || true
  else
    warn "Claude Code — agentation prompt hook not configured"; ((WARN++)) || true
  fi
  if grep -Eq '\.agent-skills/omg/scripts/(claude-agentation-submit-hook\.py|claude-plan-gate\.py)' "${HOME}/.claude/settings.json" 2>/dev/null; then
    warn "Claude Code — legacy omg hook path detected; rerun ~/.agent-skills/jeo/scripts/setup-claude.sh"; ((WARN++)) || true
  fi
else
  warn "Claude Code — ~/.claude/settings.json not found"; ((WARN++)) || true
fi

# Codex CLI
if [[ -f "${HOME}/.codex/config.toml" ]]; then
  if python3 - <<'PYEOF' >/dev/null 2>&1
import pathlib, re
p = pathlib.Path.home() / '.codex' / 'config.toml'
text = p.read_text(encoding='utf-8')
m1 = re.search(r'(?ms)^developer_instructions\s*=\s*"""\n?(.*?)\n?"""\s*$', text)
if m1 and 'Keyword: jeo | Platforms: Codex, Claude, Gemini, OpenCode' in m1.group(1):
    raise SystemExit(0)
m2 = re.search(r'(?m)^developer_instructions\s*=\s*"(.*)"\s*$', text)
if m2 and 'Keyword: jeo | Platforms: Codex, Claude, Gemini, OpenCode' in bytes(m2.group(1), 'utf-8').decode('unicode_escape'):
    raise SystemExit(0)
raise SystemExit(1)
PYEOF
  then
    ok "Codex CLI — JEO developer_instructions configured"; ((PASS++)) || true
  else
    warn "Codex CLI — JEO developer_instructions missing/invalid in config.toml"; ((WARN++)) || true
  fi
  if [[ -f "${HOME}/.codex/prompts/jeo.md" ]]; then
    ok "Codex CLI — /prompts:jeo available"; ((PASS++)) || true
  else
    warn "Codex CLI — /prompts:jeo not found"; ((WARN++)) || true
  fi
  if grep -q "jeo-notify.py" "${HOME}/.codex/config.toml" 2>/dev/null; then
    ok "Codex CLI — notify hook configured"; ((PASS++)) || true
  else
    warn "Codex CLI — notify hook missing"; ((WARN++)) || true
  fi
  if grep -q 'agent-turn-complete' "${HOME}/.codex/config.toml" 2>/dev/null; then
    ok "Codex CLI — tui notifications include agent-turn-complete"; ((PASS++)) || true
  else
    warn "Codex CLI — tui notifications missing agent-turn-complete"; ((WARN++)) || true
  fi
else
  warn "Codex CLI — ~/.codex/config.toml not found"; ((WARN++)) || true
fi

# Gemini CLI
if [[ -f "${HOME}/.gemini/settings.json" ]]; then
  if grep -q "plannotator" "${HOME}/.gemini/settings.json" 2>/dev/null; then
    ok "Gemini CLI — plannotator hook configured"; ((PASS++)) || true
  else
    warn "Gemini CLI — plannotator hook not found"; ((WARN++)) || true
  fi
else
  warn "Gemini CLI — ~/.gemini/settings.json not found"; ((WARN++)) || true
fi
if [[ -f "${HOME}/.gemini/GEMINI.md" ]]; then
  if grep -q "JEO Orchestration" "${HOME}/.gemini/GEMINI.md" 2>/dev/null; then
    ok "Gemini CLI — JEO instructions in GEMINI.md"; ((PASS++)) || true
  else
    warn "Gemini CLI — JEO not in GEMINI.md"; ((WARN++)) || true
  fi
fi

# OpenCode
for candidate in "./opencode.json" "${HOME}/opencode.json" "${HOME}/.config/opencode/opencode.json"; do
  if [[ -f "$candidate" ]]; then
    if grep -q "plannotator" "$candidate" 2>/dev/null; then
      ok "OpenCode — plannotator plugin configured ($candidate)"; ((PASS++)) || true
    else
      warn "OpenCode — plannotator not in $candidate"; ((WARN++)) || true
    fi
    break
  fi
done
echo ""

# ── JEO State ─────────────────────────────────────────────────────────────────
info "JEO State"
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
STATE_FILE="$GIT_ROOT/.omc/state/jeo-state.json"
PHASE="unknown"
if [[ -f "$STATE_FILE" ]]; then
  ok "State file found: $STATE_FILE"
  if command -v python3 >/dev/null 2>&1; then
    PHASE=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('phase','unknown'))" 2>/dev/null || echo "unknown")
    TASK=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('task','(none)'))" 2>/dev/null || echo "(none)")
    RETRY=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('retry_count',0))" 2>/dev/null || echo "0")
    LAST_ERR=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); e=d.get('last_error'); print(e if e else '(none)')" 2>/dev/null || echo "(none)")
    PLAN_GATE=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('plan_gate_status','(none)'))" 2>/dev/null || echo "(none)")
    PLAN_HASH=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('last_reviewed_plan_hash') or '(none)')" 2>/dev/null || echo "(none)")
    SUBMIT_GATE=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('agentation',{}).get('submit_gate_status','(none)'))" 2>/dev/null || echo "(none)")
    echo "     Current phase: $PHASE"
    echo "     Task: $TASK"
    echo "     Plan gate: $PLAN_GATE"
    [[ "$PLAN_HASH" != "(none)" ]] && echo "     Last reviewed hash: ${PLAN_HASH:0:12}..."
    echo "     Agentation submit gate: $SUBMIT_GATE"
    [[ "$RETRY" -gt 0 ]] && echo "     Retry count: $RETRY"
    [[ "$LAST_ERR" != "(none)" ]] && echo -e "     ${RED}Last error: $LAST_ERR${NC}"
  fi
  if $RESUME; then
    echo ""
    echo "  Resume instructions:"
    echo "  The JEO workflow was in phase: $PHASE"
    echo "  Check .omc/plans/jeo-plan.md for the approved plan"
  fi
else
  warn "No active JEO state (no workflow in progress)"
  if $RESUME && command -v python3 >/dev/null 2>&1; then
    info "Initializing fresh JEO state file for new session..."
    mkdir -p "$GIT_ROOT/.omc/state" "$GIT_ROOT/.omc/plans"
    GIT_ROOT="$GIT_ROOT" python3 - <<'PYEOF'
import json, datetime, os, uuid
now = datetime.datetime.utcnow().isoformat() + "Z"
git_root = os.environ["GIT_ROOT"]
state = {
    "mode": "jeo",
    "phase": "plan",
    "session_id": str(uuid.uuid4()),
    "task": "resumed session",
    "plan_approved": False,
    "plan_gate_status": "pending",
    "plan_current_hash": None,
    "last_reviewed_plan_hash": None,
    "last_reviewed_plan_at": None,
    "plan_review_method": None,
    "checkpoint": None,
    "last_error": None,
    "retry_count": 0,
    "team_available": False,
    "agentation": {
        "active": False,
        "session_id": None,
        "keyword_used": None,
        "submit_gate_status": "idle",
        "submit_signal": None,
        "submit_received_at": None,
        "submitted_annotation_count": 0,
        "started_at": None,
        "timeout_seconds": 120,
        "annotations": {"total": 0, "pending": 0, "acknowledged": 0, "resolved": 0, "dismissed": 0},
        "completed_at": None,
        "exit_reason": None
    },
    "created_at": now,
    "updated_at": now
}
os.makedirs(os.path.join(git_root, ".omc", "state"), exist_ok=True)
os.makedirs(os.path.join(git_root, ".omc", "plans"), exist_ok=True)
state_path = os.path.join(git_root, ".omc", "state", "jeo-state.json")
with open(state_path, "w") as f:
    json.dump(state, f, indent=2)
print(f"✓ Fresh JEO state initialized at {state_path} (phase: plan)")
PYEOF
  elif [[ -z "${1:-}" ]]; then
    echo "     Tip: Run with --resume to initialize state for a new session"
  fi
fi

# Worktrees
WORKTREE_COUNT=$(git worktree list 2>/dev/null | wc -l | tr -d ' ') || WORKTREE_COUNT=0
if [[ "$WORKTREE_COUNT" -gt 1 ]]; then
  warn "Active worktrees: $WORKTREE_COUNT (run worktree-cleanup.sh when done)"
else
  ok "No extra worktrees active"
fi
echo ""

# ── Summary ────────────────────────────────────────────────────────────────────
echo "══════════════════════════════════════════"
echo -e "  ${GREEN}✓${NC} Passed: $PASS  ${YELLOW}⚠${NC}  Warnings: $WARN  ${RED}✗${NC} Failed: $FAIL"
echo "══════════════════════════════════════════"
echo ""

if [[ $FAIL -gt 0 ]]; then
  echo "Fix failures by running: bash scripts/install.sh --all"
elif [[ $WARN -gt 0 ]]; then
  echo "Run platform setup scripts to resolve warnings:"
  echo "  bash scripts/setup-claude.sh"
  echo "  bash scripts/setup-codex.sh"
  echo "  bash scripts/setup-gemini.sh"
  echo "  bash scripts/setup-opencode.sh"
else
  echo -e "${GREEN}All checks passed! JEO is fully configured.${NC}"
fi
echo ""
