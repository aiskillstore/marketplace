#!/bin/bash
# plannotator - Claude Code Hook Setup Script
# Adds the ExitPlanMode hook to ~/.claude/settings.json
# Use this as an alternative to the Claude Code plugin install.
#
# Usage: ./setup-hook.sh [--dry-run]

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GRAY='\033[0;37m'
NC='\033[0m'

DRY_RUN=false
for arg in "$@"; do
  case $arg in
    --dry-run) DRY_RUN=true ;;
    -h|--help)
      echo "Usage: $0 [--dry-run]"
      echo ""
      echo "Adds the plannotator hook to ~/.claude/settings.json"
      echo ""
      echo "Options:"
      echo "  --dry-run   Show what would be changed without writing"
      echo "  -h, --help  Show this help"
      exit 0
      ;;
  esac
done

SETTINGS_FILE="$HOME/.claude/settings.json"
SETTINGS_DIR="$HOME/.claude"

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    plannotator Hook Setup                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check plannotator is installed
if ! command -v plannotator &>/dev/null; then
  echo -e "${RED}✗ plannotator CLI not found${NC}"
  echo -e "${YELLOW}  Run ./install.sh first${NC}"
  exit 1
fi

echo -e "${GREEN}✓ plannotator CLI is installed${NC}"
echo ""

# Check if already configured
if [ -f "$SETTINGS_FILE" ] && grep -q "plannotator" "$SETTINGS_FILE" 2>/dev/null; then
  echo -e "${YELLOW}⚠ plannotator hook already exists in ${SETTINGS_FILE}${NC}"
  echo ""
  echo -e "Current hook configuration:"
  grep -A3 -B1 "plannotator" "$SETTINGS_FILE" 2>/dev/null | head -20
  echo ""
  echo -e "${GRAY}No changes made. Remove manually if you want to reconfigure.${NC}"
  exit 0
fi

# The hook JSON to inject
HOOK_JSON='{
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
}'

echo -e "${BLUE}Hook to be added:${NC}"
echo "$HOOK_JSON"
echo ""

if [ "$DRY_RUN" = true ]; then
  echo -e "${YELLOW}[DRY RUN] No changes written.${NC}"
  echo -e "Target file: ${SETTINGS_FILE}"
  exit 0
fi

# Ensure ~/.claude directory exists
mkdir -p "$SETTINGS_DIR"

if [ ! -f "$SETTINGS_FILE" ]; then
  # Create new settings.json with hook
  echo -e "${BLUE}Creating new settings file: ${SETTINGS_FILE}${NC}"
  cat > "$SETTINGS_FILE" <<EOF
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
  echo -e "${BLUE}Merging hook into existing: ${SETTINGS_FILE}${NC}"
  echo ""

  # Back up existing settings
  BACKUP="${SETTINGS_FILE}.bak.$(date +%Y%m%d%H%M%S)"
  cp "$SETTINGS_FILE" "$BACKUP"
  echo -e "${GRAY}  Backup saved: ${BACKUP}${NC}"

  # Use Python (available on macOS/Linux) to merge JSON safely
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

# Don't add if already present
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

    echo -e "${GREEN}✓ Hook added to ${SETTINGS_FILE}${NC}"

  else
    echo -e "${RED}✗ python3 not found — cannot merge JSON safely${NC}"
    echo -e "${YELLOW}  Add this manually to ${SETTINGS_FILE}:${NC}"
    echo ""
    echo '  "hooks": {'
    echo '    "PermissionRequest": ['
    echo '      {'
    echo '        "matcher": "ExitPlanMode",'
    echo '        "hooks": [{"type": "command", "command": "plannotator", "timeout": 1800}]'
    echo '      }'
    echo '    ]'
    echo '  }'
    exit 1
  fi
fi

echo ""
echo -e "${GREEN}Hook setup complete!${NC}"
echo ""
echo -e "${BLUE}How it works:${NC}"
echo -e "  When Claude Code finishes planning (Shift+Tab×2 in plan mode),"
echo -e "  plannotator opens automatically in your browser."
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  ${BLUE}1.${NC} Restart Claude Code for hooks to take effect"
echo -e "  ${BLUE}2.${NC} Run ${GREEN}./check-status.sh${NC} to verify configuration"
echo ""
