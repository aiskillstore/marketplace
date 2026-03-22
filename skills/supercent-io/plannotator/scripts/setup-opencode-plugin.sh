#!/bin/bash
# plannotator - OpenCode Plugin Registration Script
# Registers @plannotator/opencode@latest plugin in opencode.json
# and copies slash commands to ~/.config/opencode/command/
#
# Usage: ./setup-opencode-plugin.sh [--dry-run] [--project-dir DIR]

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GRAY='\033[0;37m'
NC='\033[0m'

DRY_RUN=false
PROJECT_DIR="${PWD}"

for arg in "$@"; do
  case $arg in
    --dry-run) DRY_RUN=true ;;
    --project-dir=*) PROJECT_DIR="${arg#*=}" ;;
    --project-dir)   PROJECT_DIR="" ;;
    -h|--help)
      echo "Usage: $0 [--dry-run] [--project-dir DIR]"
      echo ""
      echo "Registers plannotator OpenCode plugin:"
      echo "  1. Adds @plannotator/opencode@latest to opencode.json"
      echo "  2. Copies slash commands to ~/.config/opencode/command/"
      echo ""
      echo "Options:"
      echo "  --project-dir DIR  Target project dir (default: current dir)"
      echo "  --dry-run          Show what would change without writing"
      echo "  -h, --help         Show this help"
      exit 0
      ;;
  esac
done

OPENCODE_JSON="${PROJECT_DIR}/opencode.json"
OPENCODE_COMMAND_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/opencode/command"
PLUGIN_NAME="@plannotator/opencode@latest"

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  plannotator × OpenCode Plugin Setup       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GRAY}Project dir: ${PROJECT_DIR}${NC}"
echo ""

if ! command -v plannotator &>/dev/null; then
  echo -e "${RED}✗ plannotator CLI not found${NC}"
  echo -e "${YELLOW}  Run ./install.sh first${NC}"
  exit 1
fi
echo -e "${GREEN}✓ plannotator CLI is installed${NC}"
echo ""

# ════════════════════════════════════════════════════════════
# PART 1: opencode.json plugin registration
# ════════════════════════════════════════════════════════════
echo -e "${BLUE}━━ Step 1: opencode.json plugin registration ━━━━━${NC}"
echo ""

if [ -f "$OPENCODE_JSON" ] && grep -q "plannotator" "$OPENCODE_JSON" 2>/dev/null; then
  echo -e "${YELLOW}⚠ plannotator already in ${OPENCODE_JSON}${NC}"
  echo -e "${GRAY}  No changes needed.${NC}"
elif [ "$DRY_RUN" = true ]; then
  echo -e "${YELLOW}[DRY RUN] Would add '${PLUGIN_NAME}' to ${OPENCODE_JSON}${NC}"
else
  if [ ! -f "$OPENCODE_JSON" ]; then
    cat > "$OPENCODE_JSON" <<EOF
{
  "\$schema": "https://opencode.ai/config.json",
  "plugin": ["${PLUGIN_NAME}"]
}
EOF
    echo -e "${GREEN}✓ Created ${OPENCODE_JSON} with plannotator plugin${NC}"
  else
    BACKUP="${OPENCODE_JSON}.bak.$(date +%Y%m%d%H%M%S)"
    cp "$OPENCODE_JSON" "$BACKUP"
    echo -e "${GRAY}  Backup saved: ${BACKUP}${NC}"

    if command -v python3 &>/dev/null; then
      python3 - "$OPENCODE_JSON" "$PLUGIN_NAME" <<'PYEOF'
import json, sys

path = sys.argv[1]
plugin = sys.argv[2]

with open(path) as f:
    config = json.load(f)

plugins = config.setdefault("plugin", [])

if any("plannotator" in p for p in plugins):
    print("plannotator plugin already present — no change.")
    sys.exit(0)

plugins.append(plugin)

with open(path, "w") as f:
    json.dump(config, f, indent=2)
    f.write("\n")

print("Plugin registered.")
PYEOF
      echo -e "${GREEN}✓ Added plannotator plugin to ${OPENCODE_JSON}${NC}"
    else
      echo -e "${RED}✗ python3 not found — add manually to ${OPENCODE_JSON}:${NC}"
      echo '  "plugin": ["'"${PLUGIN_NAME}"'"]'
      exit 1
    fi
  fi
fi
echo ""

# ════════════════════════════════════════════════════════════
# PART 2: Slash commands for OpenCode
# ════════════════════════════════════════════════════════════
echo -e "${BLUE}━━ Step 2: OpenCode slash commands ━━━━━━━━━━━━━━━${NC}"
echo ""

REVIEW_CMD="${OPENCODE_COMMAND_DIR}/plannotator-review.md"
ANNOTATE_CMD="${OPENCODE_COMMAND_DIR}/plannotator-annotate.md"

REVIEW_CMD_CONTENT='---
description: Open interactive code review for current changes
---

Open the plannotator code review UI for current git diff.

!`plannotator review`

Address the code review feedback above.'

ANNOTATE_CMD_CONTENT='---
description: Open interactive annotation UI for a markdown file
---

!`plannotator annotate "$ARGUMENTS"`

Address the annotation feedback above.'

if [ "$DRY_RUN" = true ]; then
  echo -e "${YELLOW}[DRY RUN] Would create:${NC}"
  echo -e "  ${REVIEW_CMD}"
  echo -e "  ${ANNOTATE_CMD}"
else
  mkdir -p "$OPENCODE_COMMAND_DIR"

  if [ ! -f "$REVIEW_CMD" ]; then
    printf '%s\n' "$REVIEW_CMD_CONTENT" > "$REVIEW_CMD"
    echo -e "${GREEN}✓ Created /plannotator-review command${NC}"
  else
    echo -e "${GRAY}  /plannotator-review already exists — skipped${NC}"
  fi

  if [ ! -f "$ANNOTATE_CMD" ]; then
    printf '%s\n' "$ANNOTATE_CMD_CONTENT" > "$ANNOTATE_CMD"
    echo -e "${GREEN}✓ Created /plannotator-annotate command${NC}"
  else
    echo -e "${GRAY}  /plannotator-annotate already exists — skipped${NC}"
  fi
fi
echo ""

echo -e "${GREEN}OpenCode plugin setup complete!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  ${BLUE}1.${NC} ${YELLOW}Restart OpenCode${NC} for the plugin to take effect"
echo -e "  ${BLUE}2.${NC} Add to ${GREEN}opencode.json${NC} if not auto-detected:"
echo ""
echo -e '    {  "'
echo -e '      "$schema": "https://opencode.ai/config.json",'
echo -e "      \"plugin\": [\"${PLUGIN_NAME}\"]"
echo -e '    }'
echo ""
echo -e "  ${BLUE}3.${NC} Available slash commands after restart:"
echo -e "    ${GREEN}/plannotator-review${NC}         — code review"
echo -e "    ${GREEN}/plannotator-annotate file.md${NC} — annotate markdown"
echo ""
echo -e "  ${BLUE}4.${NC} The ${GREEN}submit_plan${NC} tool is automatically available to the agent"
echo ""
