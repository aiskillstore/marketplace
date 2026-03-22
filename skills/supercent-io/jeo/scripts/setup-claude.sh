#!/usr/bin/env bash
# JEO Skill — Claude Code Plugin & Hook Setup
# Configures: omc plugin, plannotator hook, agentation MCP, jeo workflow in ~/.claude/settings.json
# Usage: bash setup-claude.sh [--dry-run]

set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; RED='\033[0;31m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✓${NC} $*"; }
warn() { echo -e "${YELLOW}⚠${NC}  $*"; }
err()  { echo -e "${RED}✗${NC} $*"; }
info() { echo -e "${BLUE}→${NC} $*"; }

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

JEO_SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_SETTINGS="${HOME}/.claude/settings.json"

echo ""
echo "JEO — Claude Code Setup"
echo "========================"

# ── 1. Check Claude Code ──────────────────────────────────────────────────────
if ! command -v claude >/dev/null 2>&1; then
  warn "claude CLI not found. Install Claude Code first."
  echo ""
  echo "Plugin installation (run inside Claude Code session):"
  echo "  /plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode"
  echo "  /plugin install oh-my-claudecode"
  echo "  /omc:omc-setup"
  echo ""
  echo "plannotator plugin:"
  echo "  /plugin marketplace add backnotprop/plannotator"
  echo "  /plugin install plannotator@plannotator"
else
  ok "claude CLI found"
fi

# ── 2. Configure ~/.claude/settings.json ─────────────────────────────────────
info "Configuring ~/.claude/settings.json..."

mkdir -p "$(dirname "$CLAUDE_SETTINGS")"

if [[ -f "$CLAUDE_SETTINGS" ]]; then
  if ! $DRY_RUN; then
    cp "$CLAUDE_SETTINGS" "${CLAUDE_SETTINGS}.jeo.bak"
    ok "Backup created: ${CLAUDE_SETTINGS}.jeo.bak"
  fi
fi

if $DRY_RUN; then
  echo -e "${YELLOW}[DRY-RUN]${NC} Would sync plannotator hook, agent teams, agentation MCP, and UserPromptSubmit hook in $CLAUDE_SETTINGS"
else
  JEO_SKILL_DIR="$JEO_SKILL_DIR" python3 - <<'PYEOF'
import json
import os

settings_path = os.path.expanduser("~/.claude/settings.json")
jeo_skill_dir = os.environ["JEO_SKILL_DIR"]
plan_gate_cmd = f'python3 "{jeo_skill_dir}/scripts/claude-plan-gate.py"'
stop_continuation_cmd = f'python3 "{jeo_skill_dir}/scripts/claude-stop-continuation.py"'
agentation_cmd = f'python3 "{jeo_skill_dir}/scripts/claude-agentation-submit-hook.py"'

try:
    with open(settings_path) as f:
        settings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}

changed = False
messages = []

hooks = settings.setdefault("hooks", {})
perm_req = hooks.setdefault("PermissionRequest", [])
plannotator_entry = next((entry for entry in perm_req if entry.get("matcher") == "ExitPlanMode"), None)
if plannotator_entry is None:
    plannotator_entry = {"matcher": "ExitPlanMode", "hooks": []}
    perm_req.append(plannotator_entry)
    changed = True

plan_hooks = plannotator_entry.setdefault("hooks", [])
# Remove ALL plannotator-related hooks so raw "plannotator" and claude-plan-gate.py
# can never coexist — having both causes plannotator to open twice on ExitPlanMode.
stale = [
    h for h in plan_hooks
    if h.get("command", "").startswith("plannotator")
    or "claude-plan-gate.py" in h.get("command", "")
]
for h in stale:
    plan_hooks.remove(h)
# Insert the single correct entry
plan_hooks.insert(0, {"type": "command", "command": plan_gate_cmd, "timeout": 1800})
changed = True
if stale:
    messages.append(f"✓ JEO plan gate wrapper synced ({len(stale)} stale entr{'y' if len(stale) == 1 else 'ies'} removed — dedup fix)")
else:
    messages.append("✓ JEO plan gate wrapper added to ExitPlanMode")

env = settings.setdefault("env", {})
if env.get("CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS") != "1":
    env["CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS"] = "1"
    changed = True
    messages.append("✓ Experimental agent teams enabled")
else:
    messages.append("✓ Experimental agent teams already enabled")

mcp_servers = settings.setdefault("mcpServers", {})
if "agentation" not in mcp_servers:
    mcp_servers["agentation"] = {
        "command": "npx",
        "args": ["-y", "agentation-mcp", "server"],
    }
    changed = True
    messages.append("✓ agentation MCP server registered")
else:
    messages.append("✓ agentation MCP already registered")

user_prompt = hooks.setdefault("UserPromptSubmit", [])

# Migrate old-format entries (flat {"type":"command",...}) to new matcher format
migrated = False
new_user_prompt = []
for entry in user_prompt:
    if "matcher" in entry and "hooks" in entry:
        new_user_prompt.append(entry)
    elif entry.get("type") == "command":
        # Old format → wrap in new matcher format
        new_user_prompt.append({"matcher": "*", "hooks": [entry]})
        migrated = True
    else:
        new_user_prompt.append(entry)
if migrated:
    hooks["UserPromptSubmit"] = new_user_prompt
    user_prompt = new_user_prompt
    changed = True
    messages.append("✓ UserPromptSubmit hooks migrated to new matcher format")

agentation_entry = next(
    (
        entry for entry in user_prompt
        if isinstance(entry, dict)
        and any(
            "claude-agentation-submit-hook.py" in h.get("command", "")
            or h.get("command", "").startswith("curl -sf --connect-timeout 1 http://localhost:4747")
            for h in entry.get("hooks", [])
        )
    ),
    None,
)
if agentation_entry is None:
    user_prompt.append({
        "matcher": "*",
        "hooks": [{"type": "command", "command": agentation_cmd, "timeout": 300}],
    })
    changed = True
    messages.append("✓ agentation submit-gate hook added")
else:
    hook_list = agentation_entry.setdefault("hooks", [])
    target_hook = next(
        (
            h for h in hook_list
            if "claude-agentation-submit-hook.py" in h.get("command", "")
            or h.get("command", "").startswith("curl -sf --connect-timeout 1 http://localhost:4747")
        ),
        None,
    )
    if target_hook is None:
        hook_list.append({"type": "command", "command": agentation_cmd, "timeout": 300})
        changed = True
    else:
        if target_hook.get("command") != agentation_cmd:
            target_hook["command"] = agentation_cmd
            changed = True
        if target_hook.get("timeout") != 300:
            target_hook["timeout"] = 300
            changed = True
    messages.append("✓ agentation submit-gate hook synced")

# ── Stop hook: auto-continue after plannotator approval ──────────────────────
# Registers claude-stop-continuation.py as a Stop hook so JEO automatically
# proceeds to EXECUTE after plannotator approves the plan, without waiting
# for user input.
stop_hooks = hooks.setdefault("Stop", [])
# Find or create the default (no-matcher) Stop entry
stop_entry = next(
    (e for e in stop_hooks if "matcher" not in e or e.get("matcher") in ("", None, "*")),
    None,
)
if stop_entry is None:
    stop_entry = {"hooks": []}
    stop_hooks.append(stop_entry)
    changed = True

stop_hook_list = stop_entry.setdefault("hooks", [])
# Remove stale JEO stop continuation hooks, then insert correct one
jeo_stop_stale = [
    h for h in stop_hook_list
    if "claude-stop-continuation.py" in h.get("command", "")
]
for h in jeo_stop_stale:
    stop_hook_list.remove(h)
stop_hook_list.insert(0, {"type": "command", "command": stop_continuation_cmd, "timeout": 10})
changed = True
if jeo_stop_stale:
    messages.append(f"✓ JEO stop-continuation hook synced ({len(jeo_stop_stale)} stale removed)")
else:
    messages.append("✓ JEO stop-continuation hook added (auto-continue after plannotator)")

if changed or not os.path.exists(settings_path):
    os.makedirs(os.path.dirname(settings_path), exist_ok=True)
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)

for message in messages:
    print(message)
PYEOF
  ok "Claude Code settings synced"
fi

# ── 3. Instructions ───────────────────────────────────────────────────────────
echo ""
echo "Manual plugin installation (run inside Claude Code):"
echo ""
echo "  # Install oh-my-claudecode (omc)"
echo "  /plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode"
echo "  /plugin install oh-my-claudecode"
echo "  /omc:omc-setup"
echo ""
echo "  # Install plannotator"
echo "  /plugin marketplace add backnotprop/plannotator"
echo "  /plugin install plannotator@plannotator"
echo ""
echo "  # Then restart Claude Code"
echo ""
ok "Claude Code setup complete"
echo "  IMPORTANT: Restart Claude Code to activate all hooks and plugins"
echo "  JEO requires /omc:team execution in Claude Code. Verify CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 after restart."
echo ""
