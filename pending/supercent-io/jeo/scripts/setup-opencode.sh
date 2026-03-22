#!/usr/bin/env bash
# JEO Skill — OpenCode Plugin Registration
# Configures: opencode.json plugin entry + agentation MCP + slash commands
# Usage: bash setup-opencode.sh [--dry-run]

set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; RED='\033[0;31m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✓${NC} $*"; }
warn() { echo -e "${YELLOW}⚠${NC}  $*"; }
info() { echo -e "${BLUE}→${NC} $*"; }

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

# Resolve opencode.json priority:
# 1) cwd (project-level config), then
# 2) ~/.config/opencode/opencode.json, then
# 3) legacy ~/.opencode.json
OPENCODE_JSON=""
for candidate in "./opencode.json" "${HOME}/.config/opencode/opencode.json" "${HOME}/opencode.json"; do
  [[ -f "$candidate" ]] && OPENCODE_JSON="$candidate" && break
done

echo ""
echo "JEO — OpenCode Plugin Setup"
echo "==========================="

# ── 1. Check OpenCode ────────────────────────────────────────────────────────
if ! command -v opencode >/dev/null 2>&1; then
  warn "opencode CLI not found. Install via: npm install -g opencode-ai"
fi

# Optional runtime check: OpenCode writes SQLite/cache/state under XDG dirs.
# If HOME-backed defaults are not writable, suggest tmp-based launcher.
if command -v opencode >/dev/null 2>&1; then
  OPENCODE_DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/opencode"
  if ! (mkdir -p "$OPENCODE_DATA_DIR" 2>/dev/null && [[ -w "$OPENCODE_DATA_DIR" ]]); then
    warn "OpenCode data dir is not writable: $OPENCODE_DATA_DIR"
    warn "Use: bash $(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/run-opencode-safe.sh"
  fi
fi

# ── 2. Configure opencode.json ────────────────────────────────────────────────
info "Configuring opencode.json..."

if [[ -z "$OPENCODE_JSON" ]]; then
  OPENCODE_JSON="${HOME}/.config/opencode/opencode.json"
  warn "No opencode.json found — will create at $OPENCODE_JSON"
fi

if $DRY_RUN; then
  echo -e "${YELLOW}[DRY-RUN]${NC} Would configure $OPENCODE_JSON with JEO plugin"
else
  # Backup
  mkdir -p "$(dirname "$OPENCODE_JSON")"
  [[ -f "$OPENCODE_JSON" ]] && cp "$OPENCODE_JSON" "${OPENCODE_JSON}.jeo.bak"

  OPENCODE_JSON_PATH="$OPENCODE_JSON" python3 - <<'PYEOF'
import json, os

config_path = os.environ["OPENCODE_JSON_PATH"]
try:
    with open(config_path) as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    config = {}

# Set schema (normalize old escaped key if present)
legacy_schema_key = "\\$schema"
if legacy_schema_key in config:
    if "$schema" not in config:
        config["$schema"] = config[legacy_schema_key]
    config.pop(legacy_schema_key)
config.setdefault("$schema", "https://opencode.ai/config.json")

# Add plugins
plugins = config.setdefault("plugin", [])

# Add plannotator if not present
if "@plannotator/opencode@latest" not in plugins:
    plugins.append("@plannotator/opencode@latest")
    print("✓ plannotator plugin added")

# Add omx if not present
if "@oh-my-opencode/opencode@latest" not in plugins:
    plugins.append("@oh-my-opencode/opencode@latest")
    print("\u2713 omx (oh-my-opencode) plugin added")

# Add agentation MCP if not present
mcp_config = config.setdefault("mcp", {})
if "agentation" not in mcp_config:
    mcp_config["agentation"] = {
        "type": "local",
        "command": ["npx", "-y", "agentation-mcp", "server"]
    }
    print("\u2713 agentation MCP added to opencode.json")
else:
    print("\u2713 agentation MCP already present")

# Migrate legacy instructions to valid type (OpenCode expects array)
legacy_instructions = config.get("instructions")
if isinstance(legacy_instructions, str):
    text = legacy_instructions.strip()
    config["instructions"] = [text] if text else []
elif legacy_instructions is not None and not isinstance(legacy_instructions, list):
    config["instructions"] = [str(legacy_instructions)]

# Register JEO slash commands in OpenCode's "command" table
commands = config.setdefault("command", {})
jeo_commands = {
    "jeo-plan": {
        "description": "JEO planning workflow (ralph + plannotator)",
        "template": (
            "Write plan.md, then run mandatory PLAN gate: "
            "bash .agent-skills/jeo/scripts/plannotator-plan-loop.sh plan.md /tmp/plannotator_feedback.txt 3. "
            "If plannotator is missing, the PLAN gate auto-installs it first. "
            "This waits for approve/feedback, restarts dead sessions up to 3 times, "
            "and asks whether to stop PLAN after repeated failures."
        ),
    },
    "jeo-exec": {
        "description": "JEO execute workflow (team/bmad)",
        "template": (
            "Execute approved plan using team agents if available; otherwise use BMAD workflow phases."
        ),
    },
    "jeo-annotate": {
        "description": "Process agentation annotations (VERIFY_UI loop)",
        "template": (
            "Run agentation watch loop: acknowledge, implement fix, resolve, and repeat until pending count is 0."
        ),
    },
    "jeo-verify": {
        "description": "Verify browser behavior with agent-browser",
        "template": "Run agent-browser snapshot and verify the UI/flow for the current task.",
    },
    "jeo-cleanup": {
        "description": "Cleanup worktrees after JEO completion",
        "template": "Run: bash .agent-skills/jeo/scripts/worktree-cleanup.sh",
    },
}

added = 0
for name, spec in jeo_commands.items():
    if name not in commands:
        commands[name] = spec
        added += 1

if added:
    print(f"\u2713 Added {added} JEO command(s) to opencode.json")
else:
    print("\u2713 JEO commands already present")

with open(config_path, "w") as f:
    json.dump(config, f, indent=2)
print(f"✓ opencode.json saved: {config_path}")
PYEOF

  ok "OpenCode configuration updated"
fi

echo ""
echo "OpenCode slash commands after setup:"
echo "  /jeo-plan      ← Start planning workflow"
echo "  /jeo-exec      \u2190 Execute task"
echo "  /jeo-annotate  \u2190 agentation watch loop (VERIFY_UI); /jeo-agentui is deprecated alias"
echo "  /jeo-verify    \u2190 Verify UI with agent-browser"
echo "  /jeo-cleanup   ← Clean worktrees"
echo "  /plannotator-review ← Code review UI"
echo ""
echo "If OpenCode shows 'readonly database', run:"
echo "  bash $(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/run-opencode-safe.sh"
echo ""
echo "  Restart OpenCode to activate plugins."
echo ""
ok "OpenCode setup complete"
echo ""
