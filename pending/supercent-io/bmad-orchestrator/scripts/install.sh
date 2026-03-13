#!/bin/bash
# BMAD Orchestrator — One-Command Setup
# Installs plannotator CLI and configures BMAD + plannotator integration.
#
# Usage:
#   bash scripts/install.sh              # Interactive setup
#   bash scripts/install.sh --skip-plannotator  # BMAD only (no plannotator)
#   bash scripts/install.sh --init-project      # Also initialize BMAD in current project
#   bash scripts/install.sh --dry-run           # Preview what would happen

set -e

# ── Colors ────────────────────────────────────────────────────────────────────
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;37m'
BOLD='\033[1m'
NC='\033[0m'

# ── Flags ─────────────────────────────────────────────────────────────────────
SKIP_PLANNOTATOR=false
INIT_PROJECT=false
DRY_RUN=false

for arg in "$@"; do
  case $arg in
    --skip-plannotator) SKIP_PLANNOTATOR=true ;;
    --init-project)     INIT_PROJECT=true ;;
    --dry-run)          DRY_RUN=true ;;
    -h|--help)
      echo "Usage: bash scripts/install.sh [options]"
      echo ""
      echo "Options:"
      echo "  --skip-plannotator   Set up BMAD only, skip plannotator install"
      echo "  --init-project       Also initialize BMAD in the current project"
      echo "  --dry-run            Preview steps without making changes"
      echo "  -h, --help           Show this help"
      exit 0
      ;;
  esac
done

# ── Header ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BLUE}${BOLD}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}${BOLD}║   BMAD Orchestrator — Setup                      ║${NC}"
echo -e "${BLUE}${BOLD}║   BMAD Method v6 + plannotator integration        ║${NC}"
echo -e "${BLUE}${BOLD}╚══════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$DRY_RUN" = true ]; then
  echo -e "${YELLOW}[DRY RUN] No changes will be made.${NC}"
  echo ""
fi

# ── Step 1: Check plannotator ─────────────────────────────────────────────────
echo -e "${BOLD}Step 1: plannotator CLI${NC}"
echo ""

if [ "$SKIP_PLANNOTATOR" = true ]; then
  echo -e "  ${GRAY}Skipping plannotator (--skip-plannotator)${NC}"
  PLANNOTATOR_OK=false
elif command -v plannotator &>/dev/null; then
  PLANNOTATOR_VERSION=$(plannotator --version 2>/dev/null || echo "installed")
  echo -e "  ${GREEN}✓ plannotator already installed${NC} (${PLANNOTATOR_VERSION})"
  PLANNOTATOR_OK=true
else
  echo -e "  ${YELLOW}plannotator not found. Installing...${NC}"
  echo ""

  if [ "$DRY_RUN" = true ]; then
    echo -e "  ${GRAY}[DRY RUN] Would run: curl -sSfL https://plannotator.ai/install.sh | sh${NC}"
    PLANNOTATOR_OK=false
  else
    # Install plannotator
    if curl -sSfL https://plannotator.ai/install.sh | sh; then
      echo ""
      echo -e "  ${GREEN}✓ plannotator installed${NC}"
      PLANNOTATOR_OK=true

      # Reload PATH so plannotator is found immediately
      export PATH="$HOME/.local/bin:$HOME/bin:$PATH"
    else
      echo ""
      echo -e "  ${RED}✗ plannotator install failed.${NC}"
      echo -e "  ${GRAY}  Manual install: https://plannotator.ai${NC}"
      PLANNOTATOR_OK=false
    fi
  fi
fi

echo ""

# ── Resolve skill directory (used in Steps 2 and 3) ──────────────────────────
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ── Step 2: Set up Claude Code hook ──────────────────────────────────────────
echo -e "${BOLD}Step 2: plannotator Hook (Claude Code)${NC}"
echo ""

HOOK_SCRIPT="${SKILL_DIR}/../plannotator/scripts/setup-hook.sh"

if [ "$PLANNOTATOR_OK" = false ]; then
  echo -e "  ${GRAY}Skipping hook setup (plannotator not installed)${NC}"
elif [ ! -f "$HOOK_SCRIPT" ]; then
  echo -e "  ${YELLOW}plannotator skill not found at expected path.${NC}"
  echo -e "  ${GRAY}  Install plannotator skill first:${NC}"
  echo -e "  ${GRAY}  npx skills add https://github.com/supercent-io/skills-template --skill plannotator${NC}"
  echo ""
  echo -e "  ${GRAY}  Then run hook setup manually:${NC}"
  echo -e "  ${GRAY}  bash .agent-skills/plannotator/scripts/setup-hook.sh${NC}"
else
  if [ "$DRY_RUN" = true ]; then
    echo -e "  ${GRAY}[DRY RUN] Would run: bash $HOOK_SCRIPT${NC}"
  else
    echo -e "  ${BLUE}Configuring Claude Code ExitPlanMode hook...${NC}"
    bash "$HOOK_SCRIPT" && echo -e "  ${GREEN}✓ Hook configured${NC}" || \
      echo -e "  ${YELLOW}⚠ Hook setup skipped (may already be configured)${NC}"
  fi
fi

echo ""

# ── Step 3: Verify BMAD scripts are executable ────────────────────────────────
echo -e "${BOLD}Step 3: BMAD Scripts${NC}"
echo ""

SCRIPTS=(
  "scripts/install.sh"
  "scripts/init-project.sh"
  "scripts/check-status.sh"
  "scripts/phase-gate-review.sh"
  "scripts/validate-config.sh"
)

for script in "${SCRIPTS[@]}"; do
  SCRIPT_PATH="${SKILL_DIR}/${script}"
  if [ -f "$SCRIPT_PATH" ]; then
    if [ "$DRY_RUN" = false ]; then
      chmod +x "$SCRIPT_PATH"
    fi
    echo -e "  ${GREEN}✓${NC} ${script}"
  else
    echo -e "  ${GRAY}-${NC} ${script} ${GRAY}(not found)${NC}"
  fi
done

echo ""

# ── Step 4: Optional project initialization ───────────────────────────────────
if [ "$INIT_PROJECT" = true ]; then
  echo -e "${BOLD}Step 4: Initialize BMAD in Current Project${NC}"
  echo ""

  INIT_SCRIPT="${SKILL_DIR}/scripts/init-project.sh"
  if [ -f "$INIT_SCRIPT" ]; then
    if [ "$DRY_RUN" = true ]; then
      echo -e "  ${GRAY}[DRY RUN] Would run: bash $INIT_SCRIPT${NC}"
    else
      bash "$INIT_SCRIPT"
    fi
  else
    echo -e "  ${RED}✗ init-project.sh not found${NC}"
  fi
  echo ""
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo -e "${GREEN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}${BOLD}  Setup complete!${NC}"
echo ""

echo -e "${BOLD}What's configured:${NC}"
if [ "$PLANNOTATOR_OK" = true ]; then
  echo -e "  ${GREEN}✓${NC} plannotator CLI — visual plan review"
  echo -e "  ${GREEN}✓${NC} Claude Code hook — auto-review on ExitPlanMode"
fi
echo -e "  ${GREEN}✓${NC} BMAD scripts — workflow orchestration"
echo ""

echo -e "${BOLD}Next steps:${NC}"
echo ""

if [ "$INIT_PROJECT" = false ]; then
  echo -e "  ${BLUE}1. Initialize BMAD in your project:${NC}"
  echo -e "     ${YELLOW}/workflow-init${NC}   ← run this in your AI session"
  echo ""
fi

echo -e "  ${BLUE}$([ "$INIT_PROJECT" = true ] && echo 1 || echo 2). Start your first phase:${NC}"
echo -e "     ${YELLOW}/workflow-status${NC}  ← see what's recommended next"
echo ""

echo -e "  ${BLUE}$([ "$INIT_PROJECT" = true ] && echo 2 || echo 3). Review each phase document before advancing:${NC}"
echo -e "     ${GRAY}bash scripts/phase-gate-review.sh docs/prd-*.md${NC}"
echo ""

if [ "$PLANNOTATOR_OK" = true ]; then
  echo -e "  ${BLUE}$([ "$INIT_PROJECT" = true ] && echo 3 || echo 4). Restart Claude Code${NC} so the hook takes effect."
  echo ""
fi

echo -e "${GRAY}Full guide: cat .agent-skills/bmad-orchestrator/SETUP.md${NC}"
echo ""
