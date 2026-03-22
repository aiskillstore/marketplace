#!/bin/bash
# plannotator - Gemini CLI Hook Setup Script
# Adds the ExitPlanMode hook to ~/.gemini/settings.json
# and plannotator instructions to ~/.gemini/GEMINI.md
#
# Usage: ./setup-gemini-hook.sh [--dry-run] [--md-only] [--hook-only]

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GRAY='\033[0;37m'
NC='\033[0m'

DRY_RUN=false
MD_ONLY=false
HOOK_ONLY=false

for arg in "$@"; do
  case $arg in
    --dry-run)  DRY_RUN=true ;;
    --md-only)  MD_ONLY=true ;;
    --hook-only) HOOK_ONLY=true ;;
    -h|--help)
      echo "Usage: $0 [--dry-run] [--md-only] [--hook-only]"
      echo ""
      echo "Configures plannotator for Gemini CLI:"
      echo "  1. Adds ExitPlanMode hook to ~/.gemini/settings.json"
      echo "  2. Adds plannotator instructions to ~/.gemini/GEMINI.md"
      echo ""
      echo "Options:"
      echo "  --dry-run    Show what would change without writing"
      echo "  --md-only    Only update GEMINI.md (skip settings.json hook)"
      echo "  --hook-only  Only update settings.json (skip GEMINI.md)"
      echo "  -h, --help   Show this help"
      exit 0
      ;;
  esac
done

GEMINI_DIR="$HOME/.gemini"
SETTINGS_FILE="$GEMINI_DIR/settings.json"
GEMINI_MD="$GEMINI_DIR/GEMINI.md"

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  plannotator × Gemini CLI Setup            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# ── Check plannotator CLI ─────────────────────────────────
if ! command -v plannotator &>/dev/null; then
  echo -e "${RED}✗ plannotator CLI not found${NC}"
  echo -e "${YELLOW}  Run ./install.sh first${NC}"
  exit 1
fi
echo -e "${GREEN}✓ plannotator CLI is installed${NC}"
echo ""

# ── Check Gemini CLI ──────────────────────────────────────
if ! command -v gemini &>/dev/null; then
  echo -e "${YELLOW}⚠ gemini CLI not found in PATH${NC}"
  echo -e "${GRAY}  Install via: npm install -g @google/gemini-cli${NC}"
  echo -e "${GRAY}  Continuing setup anyway (settings will be ready when gemini is installed)${NC}"
  echo ""
fi

mkdir -p "$GEMINI_DIR"

# ════════════════════════════════════════════════════════════
# PART 1: Hook in ~/.gemini/settings.json
# ════════════════════════════════════════════════════════════
if [ "$MD_ONLY" = false ]; then
  echo -e "${BLUE}━━ Step 1: settings.json hook ━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

  if [ -f "$SETTINGS_FILE" ] && grep -q "plannotator" "$SETTINGS_FILE" 2>/dev/null; then
    echo -e "${YELLOW}⚠ plannotator hook already in ${SETTINGS_FILE}${NC}"
    echo -e "${GRAY}  No changes made.${NC}"
  else
    # Hook JSON (Gemini CLI uses same format as Claude Code)
    HOOK_BLOCK='{
  "hooks": {
    "PermissionRequest": [
      {
        "matcher": "ExitPlanMode",
        "hooks": [
          {
            "type": "command",
            "command": "plannotator",
            "timeout": 1800
          }
        ]
      }
    ]
  }
}'

    echo -e "${BLUE}Hook to be added to ${SETTINGS_FILE}:${NC}"
    echo "$HOOK_BLOCK"
    echo ""

    if [ "$DRY_RUN" = true ]; then
      echo -e "${YELLOW}[DRY RUN] No changes written to settings.json${NC}"
    elif [ ! -f "$SETTINGS_FILE" ]; then
      # Create new settings.json
      cat > "$SETTINGS_FILE" <<'EOF'
{
  "hooks": {
    "PermissionRequest": [
      {
        "matcher": "ExitPlanMode",
        "hooks": [
          {
            "type": "command",
            "command": "plannotator",
            "timeout": 1800
          }
        ]
      }
    ]
  }
}
EOF
      echo -e "${GREEN}✓ Created ${SETTINGS_FILE} with plannotator hook${NC}"
    else
      # Merge into existing settings.json
      BACKUP="${SETTINGS_FILE}.bak.$(date +%Y%m%d%H%M%S)"
      cp "$SETTINGS_FILE" "$BACKUP"
      echo -e "${GRAY}  Backup saved: ${BACKUP}${NC}"

      if command -v python3 &>/dev/null; then
        python3 - "$SETTINGS_FILE" <<'PYEOF'
import json, sys

path = sys.argv[1]
with open(path) as f:
    settings = json.load(f)

new_hook = {
    "matcher": "ExitPlanMode",
    "hooks": [{"type": "command", "command": "plannotator", "timeout": 1800}]
}

hooks = settings.setdefault("hooks", {})
perm = hooks.setdefault("PermissionRequest", [])

for h in perm:
    if h.get("matcher") == "ExitPlanMode" and any(
        x.get("command") == "plannotator" for x in h.get("hooks", [])
    ):
        print("Hook already present — no changes made.")
        sys.exit(0)

perm.append(new_hook)

with open(path, "w") as f:
    json.dump(settings, f, indent=2)
    f.write("\n")

print("Hook merged successfully.")
PYEOF
        echo -e "${GREEN}✓ Hook merged into ${SETTINGS_FILE}${NC}"
      else
        echo -e "${RED}✗ python3 not found — cannot merge JSON safely${NC}"
        echo -e "${YELLOW}  Add manually to ${SETTINGS_FILE}:${NC}"
        echo "$HOOK_BLOCK"
        exit 1
      fi
    fi
  fi

  # Also try Gemini CLI's built-in hook migration if available
  if command -v gemini &>/dev/null && gemini hooks --help 2>/dev/null | grep -q migrate; then
    echo ""
    echo -e "${GRAY}  Tip: You can also run 'gemini hooks migrate --from-claude' to auto-migrate Claude Code hooks.${NC}"
  fi
  echo ""
fi

# ════════════════════════════════════════════════════════════
# PART 2: GEMINI.md instructions
# ════════════════════════════════════════════════════════════
if [ "$HOOK_ONLY" = false ]; then
  echo -e "${BLUE}━━ Step 2: GEMINI.md plannotator instructions ━━━━${NC}"
  echo ""

  PLANNOTATOR_MD_BLOCK='
## plannotator — Plan Review

When you have a complete implementation plan, **always submit it for human review** before proceeding:

```bash
# Save markdown plan to file, then send validated JSON payload:
cat > /tmp/plan.md << 'PLAN'
# Your plan markdown...
PLAN

python3 -c "
import json
print(json.dumps({'tool_input': {'plan': open('/tmp/plan.md').read(), 'permission_mode': 'acceptEdits'}}))
" | plannotator > /tmp/plannotator_feedback.txt 2>&1 &
```

**Workflow:**
1. Create your implementation plan in markdown
2. Run the python3 JSON command above (manual mode) OR let ExitPlanMode hook trigger automatically
3. Wait for user approval in the browser UI
4. If approved → proceed with implementation
5. If changes requested → revise and resubmit

**Code review after implementation:**
```bash
plannotator review          # Review all uncommitted changes
plannotator review HEAD~1   # Review specific commit
```

**Plan mode:** Run `gemini --approval-mode plan` to work in read-only planning mode.
plannotator hooks automatically trigger when you exit plan mode.
'

  if [ -f "$GEMINI_MD" ] && grep -q "plannotator" "$GEMINI_MD" 2>/dev/null; then
    echo -e "${YELLOW}⚠ plannotator instructions already in ${GEMINI_MD}${NC}"
    echo -e "${GRAY}  No changes made.${NC}"
  else
    if [ "$DRY_RUN" = true ]; then
      echo -e "${YELLOW}[DRY RUN] Would append to ${GEMINI_MD}:${NC}"
      echo "$PLANNOTATOR_MD_BLOCK"
    else
      # Append plannotator section to GEMINI.md
      if [ ! -f "$GEMINI_MD" ]; then
        cat > "$GEMINI_MD" <<EOF
# Gemini CLI Agent Configuration
EOF
      fi
      printf "\n%s\n" "$PLANNOTATOR_MD_BLOCK" >> "$GEMINI_MD"
      echo -e "${GREEN}✓ plannotator instructions added to ${GEMINI_MD}${NC}"
    fi
  fi
  echo ""
fi

# ════════════════════════════════════════════════════════════
# Summary
# ════════════════════════════════════════════════════════════
echo -e "${GREEN}Gemini CLI setup complete!${NC}"
echo ""
echo -e "${BLUE}How it works:${NC}"
echo -e "  When Gemini exits plan mode (--approval-mode plan),"
echo -e "  plannotator opens automatically in your browser."
echo ""
echo -e "${BLUE}Manual trigger:${NC}"
echo -e "  ${GREEN}cat > /tmp/plan.md << 'PLAN'${NC}"
echo -e "  ${GREEN}# ...your markdown...${NC}"
echo -e "  ${GREEN}PLAN${NC}"
echo -e "  ${GREEN}python3 -c \"import json; print(json.dumps({'tool_input': {'plan': open('/tmp/plan.md').read(), 'permission_mode': 'acceptEdits'}}))\" | plannotator > /tmp/plannotator_feedback.txt 2>&1 &${NC}"
echo -e "  ${GREEN}plannotator review${NC}   (review git diff)"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  ${BLUE}1.${NC} Run ${GREEN}./check-status.sh${NC} to verify configuration"
echo -e "  ${BLUE}2.${NC} Use ${GREEN}gemini --approval-mode plan${NC} to enable plan review"
echo ""
