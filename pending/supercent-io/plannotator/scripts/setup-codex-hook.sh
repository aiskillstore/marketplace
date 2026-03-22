#!/bin/bash
# plannotator - Codex CLI Setup Script
# Configures plannotator for Codex CLI by:
#   1. Adding developer_instructions to ~/.codex/config.toml
#   2. Creating a plannotator prompt at ~/.codex/prompts/plannotator.md
#
# Usage: ./setup-codex-hook.sh [--dry-run]

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
      echo "Configures plannotator for Codex CLI:"
      echo "  1. Adds plannotator instructions to ~/.codex/config.toml developer_instructions"
      echo "  2. Creates ~/.codex/prompts/plannotator.md for agent role"
      echo ""
      echo "Options:"
      echo "  --dry-run   Show what would change without writing"
      echo "  -h, --help  Show this help"
      exit 0
      ;;
  esac
done

CODEX_DIR="$HOME/.codex"
CODEX_CONFIG="$CODEX_DIR/config.toml"
CODEX_PROMPTS="$CODEX_DIR/prompts"
PLANNOTATOR_PROMPT="$CODEX_PROMPTS/plannotator.md"

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  plannotator × Codex CLI Setup             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

if ! command -v plannotator &>/dev/null; then
  echo -e "${RED}✗ plannotator CLI not found${NC}"
  echo -e "${YELLOW}  Run ./install.sh first${NC}"
  exit 1
fi
echo -e "${GREEN}✓ plannotator CLI is installed${NC}"
echo ""

if ! command -v codex &>/dev/null; then
  echo -e "${YELLOW}⚠ codex CLI not found in PATH${NC}"
  echo -e "${GRAY}  Install via: npm install -g @openai/codex${NC}"
  echo -e "${GRAY}  Continuing setup anyway...${NC}"
  echo ""
fi

mkdir -p "$CODEX_DIR" "$CODEX_PROMPTS"

# ════════════════════════════════════════════════════════════
# PART 1: developer_instructions in config.toml
# ════════════════════════════════════════════════════════════
echo -e "${BLUE}━━ Step 1: config.toml developer_instructions ━━━━${NC}"
echo ""

PLANNOTATOR_INSTRUCTION='Before implementing any plan, write the plan markdown to /tmp/plan.md and run: `python3 -c "import json; print(json.dumps({\"tool_input\": {\"plan\": open(\"/tmp/plan.md\").read(), \"permission_mode\": \"acceptEdits\"}}))" | plannotator > /tmp/pn_out.txt 2>&1 & sleep 5; cat /tmp/pn_out.txt`. Wait for user approval in plannotator UI. After coding, run `plannotator review` to open code review.'

if [ -f "$CODEX_CONFIG" ] && grep -q "plannotator" "$CODEX_CONFIG" 2>/dev/null; then
  echo -e "${YELLOW}⚠ plannotator already referenced in ${CODEX_CONFIG}${NC}"
  echo -e "${GRAY}  No changes made to config.toml.${NC}"
else
  if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}[DRY RUN] Would add to developer_instructions in ${CODEX_CONFIG}:${NC}"
    echo "  $PLANNOTATOR_INSTRUCTION"
  else
    if [ ! -f "$CODEX_CONFIG" ]; then
      cat > "$CODEX_CONFIG" <<EOF
developer_instructions = "${PLANNOTATOR_INSTRUCTION}"
EOF
      echo -e "${GREEN}✓ Created ${CODEX_CONFIG} with plannotator instructions${NC}"
    else
      BACKUP="${CODEX_CONFIG}.bak.$(date +%Y%m%d%H%M%S)"
      cp "$CODEX_CONFIG" "$BACKUP"
      echo -e "${GRAY}  Backup saved: ${BACKUP}${NC}"

      if grep -q "^developer_instructions" "$CODEX_CONFIG"; then
        if command -v python3 &>/dev/null; then
          python3 - "$CODEX_CONFIG" "$PLANNOTATOR_INSTRUCTION" <<'PYEOF'
import sys, re

path = sys.argv[1]
addition = sys.argv[2]

with open(path) as f:
    content = f.read()

pattern = r'^(developer_instructions\s*=\s*")(.+?)(")'
match = re.search(pattern, content, re.MULTILINE)

if match:
    current = match.group(2)
    if "plannotator" not in current:
        new_val = current + " " + addition
        content = content[:match.start()] + f'developer_instructions = "{new_val}"' + content[match.end():]
        with open(path, "w") as f:
            f.write(content)
        print("Appended to developer_instructions.")
    else:
        print("plannotator already in developer_instructions — no change.")
else:
    with open(path, "a") as f:
        f.write(f'\ndeveloper_instructions = "{addition}"\n')
    print("Added developer_instructions line.")
PYEOF
        else
          echo "developer_instructions = \"${PLANNOTATOR_INSTRUCTION}\"" >> "$CODEX_CONFIG"
        fi
        echo -e "${GREEN}✓ Updated developer_instructions in ${CODEX_CONFIG}${NC}"
      else
        printf '\ndeveloper_instructions = "%s"\n' "$PLANNOTATOR_INSTRUCTION" >> "$CODEX_CONFIG"
        echo -e "${GREEN}✓ Added developer_instructions to ${CODEX_CONFIG}${NC}"
      fi
    fi
  fi
fi
echo ""

# ════════════════════════════════════════════════════════════
# PART 2: plannotator prompt file
# ════════════════════════════════════════════════════════════
echo -e "${BLUE}━━ Step 2: plannotator prompt file ━━━━━━━━━━━━━━━${NC}"
echo ""

PROMPT_CONTENT='# plannotator — Plan Review Agent

Use this prompt to do a plan review session with plannotator before implementation.

## How to Use

```bash
# In Codex, invoke with:
/prompts:plannotator "Review my plan for [feature]"
```

## Workflow

1. Create your implementation plan in markdown format
2. Pipe it to plannotator for human review:
   ```bash
   cat > /tmp/plan.md << '"'"'PLAN
   # Implementation Plan: [Feature Name]

   ## Steps
   1. ...
   2. ...
   PLAN

   python3 -c "import json; print(json.dumps({\"tool_input\": {\"plan\": open(\"/tmp/plan.md\").read(), \"permission_mode\": \"acceptEdits\"}}))" | plannotator > /tmp/plannotator_feedback.txt 2>&1 &
   ```
3. User reviews and annotates in browser UI
4. If approved → proceed with implementation
5. If changes requested → revise plan and resubmit

## After Coding

```bash
# Review all uncommitted changes
plannotator review

# Review a specific commit
plannotator review HEAD~1

# Review branch diff
plannotator review main...HEAD
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `PLANNOTATOR_REMOTE` | Set to `1` for remote/SSH mode |
| `PLANNOTATOR_PORT` | Fixed port (default: random) |
| `PLANNOTATOR_BROWSER` | Custom browser path |

## Obsidian Integration

Approved plans auto-save to Obsidian when enabled in plannotator UI settings.
Install Obsidian: https://obsidian.md/download
'

if [ -f "$PLANNOTATOR_PROMPT" ]; then
  echo -e "${YELLOW}⚠ ${PLANNOTATOR_PROMPT} already exists${NC}"
  echo -e "${GRAY}  Skipping (delete file to recreate).${NC}"
elif [ "$DRY_RUN" = true ]; then
  echo -e "${YELLOW}[DRY RUN] Would create ${PLANNOTATOR_PROMPT}${NC}"
else
  printf '%s\n' "$PROMPT_CONTENT" > "$PLANNOTATOR_PROMPT"
  echo -e "${GREEN}✓ Created ${PLANNOTATOR_PROMPT}${NC}"
fi
echo ""

echo -e "${GREEN}Codex CLI setup complete!${NC}"
echo ""
echo -e "${BLUE}How to use plannotator in Codex:${NC}"
echo ""
echo -e "  ${BLUE}Plan review:${NC}"
echo -e "    ${GREEN}cat > /tmp/plan.md << 'PLAN'${NC}"
echo -e "    ${GREEN}# ...your markdown...${NC}"
echo -e "    ${GREEN}PLAN${NC}"
echo -e "    ${GREEN}python3 -c \"import json; print(json.dumps({\\\"tool_input\\\": {\\\"plan\\\": open(\\\"/tmp/plan.md\\\").read(), \\\"permission_mode\\\": \\\"acceptEdits\\\"}}))\" | plannotator > /tmp/plannotator_feedback.txt 2>&1 &${NC}"
echo ""
echo -e "  ${BLUE}Code review after coding:${NC}"
echo -e "    ${GREEN}plannotator review${NC}"
echo ""
echo -e "  ${BLUE}Use plannotator agent prompt:${NC}"
echo -e "    ${GREEN}/prompts:plannotator${NC}  (inside Codex interactive session)"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  ${BLUE}1.${NC} Run ${GREEN}./check-status.sh${NC} to verify configuration"
echo -e "  ${BLUE}2.${NC} Start a Codex session and use plannotator review"
echo ""
