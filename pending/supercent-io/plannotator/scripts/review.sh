#!/bin/bash
# plannotator - Code Review (Diff Review) Script
# Opens a visual diff review of current git changes in the plannotator UI.
#
# Usage:
#   ./review.sh              # Review all uncommitted changes
#   ./review.sh HEAD~1       # Review last commit
#   ./review.sh main...HEAD  # Review changes from main to HEAD

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GRAY='\033[0;37m'
NC='\033[0m'

DIFF_REF="${1:-}"

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    plannotator Code Review                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check CLI
if ! command -v plannotator &>/dev/null; then
  echo -e "${RED}✗ plannotator CLI not found${NC}"
  echo -e "${YELLOW}  Run ./install.sh first${NC}"
  exit 1
fi

# Check git repo
if ! git rev-parse --git-dir &>/dev/null 2>&1; then
  echo -e "${RED}✗ Not inside a git repository${NC}"
  exit 1
fi

# Show diff summary
echo -e "${BLUE}Repository:${NC} $(git rev-parse --show-toplevel 2>/dev/null)"
echo -e "${BLUE}Branch:${NC} $(git branch --show-current 2>/dev/null)"
echo ""

if [ -n "$DIFF_REF" ]; then
  echo -e "${BLUE}Diff target:${NC} ${DIFF_REF}"
  STAT=$(git diff --stat "$DIFF_REF" 2>/dev/null || git diff --stat "${DIFF_REF}..HEAD" 2>/dev/null)
else
  echo -e "${BLUE}Diff target:${NC} uncommitted changes (staged + unstaged)"
  STAT=$(git diff --stat HEAD 2>/dev/null)
  if [ -z "$STAT" ]; then
    STAT=$(git diff --stat 2>/dev/null)
  fi
fi

if [ -z "$STAT" ]; then
  echo -e "${YELLOW}⚠ No changes found to review${NC}"
  echo ""
  echo -e "${GRAY}Tips:${NC}"
  echo -e "  • Make some changes and run again"
  echo -e "  • Review a specific commit: ./review.sh HEAD~1"
  echo -e "  • Review branch diff: ./review.sh main...HEAD"
  exit 0
fi

echo ""
echo -e "${BLUE}Changes to review:${NC}"
echo "$STAT" | sed 's/^/  /'
echo ""

# Launch plannotator review
echo -e "${BLUE}Opening plannotator diff review UI...${NC}"
echo ""

if [ -n "$DIFF_REF" ]; then
  plannotator review "$DIFF_REF"
else
  plannotator review
fi

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
  echo -e "${GREEN}Review session complete${NC}"
else
  echo -e "${YELLOW}Review exited with code ${EXIT_CODE}${NC}"
  echo ""
  echo -e "${GRAY}If the browser didn't open, check:${NC}"
  echo -e "  • Is PLANNOTATOR_REMOTE=1 set? Access at http://localhost:${PLANNOTATOR_PORT:-19432}"
  echo -e "  • Run ${GREEN}./check-status.sh${NC} to diagnose"
fi

echo ""
