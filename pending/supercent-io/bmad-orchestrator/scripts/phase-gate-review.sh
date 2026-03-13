#!/bin/bash
# BMAD Phase Gate Review
# Submits a phase document to plannotator for review before phase transition.
# On approval, updates bmm-workflow-status.yaml and records Obsidian save path.
#
# Usage:
#   bash scripts/phase-gate-review.sh <doc-file> [title]
#
# Examples:
#   bash scripts/phase-gate-review.sh docs/prd-myapp-2026-02-22.md "PRD Review: myapp"
#   bash scripts/phase-gate-review.sh docs/architecture-myapp-2026-02-22.md

set -e

# ── Args ──────────────────────────────────────────────────────────────────────
DOC_FILE="${1:-}"
TITLE="${2:-}"

if [ -z "$DOC_FILE" ]; then
  echo "Usage: bash scripts/phase-gate-review.sh <doc-file> [title]"
  echo ""
  echo "Examples:"
  echo "  bash scripts/phase-gate-review.sh docs/prd-myapp-2026-02-22.md \"PRD Review: myapp\""
  echo "  bash scripts/phase-gate-review.sh docs/architecture-myapp-2026-02-22.md"
  exit 1
fi

if [ ! -f "$DOC_FILE" ]; then
  echo "Error: Document not found: $DOC_FILE"
  exit 1
fi

# ── Defaults ──────────────────────────────────────────────────────────────────
BASENAME=$(basename "$DOC_FILE" .md)
TITLE="${TITLE:-Phase Review: $BASENAME}"

# Detect project name from config or dirname
PROJECT_NAME="project"
if [ -f "bmad/config.yaml" ]; then
  if command -v yq &>/dev/null; then
    PROJECT_NAME=$(yq eval '.project_name' bmad/config.yaml 2>/dev/null || echo "project")
  else
    PROJECT_NAME=$(grep "project_name:" bmad/config.yaml 2>/dev/null | head -1 | sed 's/.*: *"\?\([^"]*\)"\?/\1/' | tr -d '"' || echo "project")
  fi
fi

# Detect phase from filename
PHASE_TAG="bmad"
if echo "$DOC_FILE" | grep -qi "product-brief\|brainstorm\|research"; then
  PHASE_TAG="bmad,phase-1"
elif echo "$DOC_FILE" | grep -qi "prd\|tech-spec\|ux-design"; then
  PHASE_TAG="bmad,phase-2"
elif echo "$DOC_FILE" | grep -qi "architecture\|solutioning"; then
  PHASE_TAG="bmad,phase-3"
elif echo "$DOC_FILE" | grep -qi "sprint\|story\|dev"; then
  PHASE_TAG="bmad,phase-4"
fi

# ── Colors ────────────────────────────────────────────────────────────────────
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      BMAD Phase Gate Review                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Document:${NC} $DOC_FILE"
echo -e "${BLUE}Title:${NC}    $TITLE"
echo -e "${BLUE}Project:${NC}  $PROJECT_NAME"
echo -e "${BLUE}Tags:${NC}     $PHASE_TAG,$PROJECT_NAME"
echo ""

# ── Check plannotator ─────────────────────────────────────────────────────────
if ! command -v plannotator &>/dev/null; then
  echo -e "${YELLOW}Warning: plannotator CLI not found.${NC}"
  echo "Install: bash scripts/install.sh (from plannotator skill)"
  echo ""
  echo -e "${YELLOW}Manual review fallback:${NC}"
  echo "  Open the document and review manually, then update bmm-workflow-status.yaml"
  echo ""
  echo "  Skipping plannotator gate — proceeding without review."
  exit 0
fi

# ── Submit to plannotator ─────────────────────────────────────────────────────
echo -e "${BLUE}Submitting to plannotator...${NC}"

DOC_CONTENT=$(cat "$DOC_FILE")

# Submit via plannotator CLI (opens browser UI)
echo "$DOC_CONTENT" | plannotator submit \
  --title "$TITLE" \
  --stdin 2>/dev/null || {
    # Fallback: use python3 to pipe content
    python3 -c "
import sys, subprocess
content = open('$DOC_FILE').read()
proc = subprocess.run(
    ['plannotator', 'submit', '--title', '$TITLE', '--stdin'],
    input=content.encode(),
    capture_output=True
)
sys.exit(proc.returncode)
" 2>/dev/null || {
    echo -e "${YELLOW}Could not auto-submit. Open plannotator manually:${NC}"
    echo "  plannotator"
    echo "  Then paste the content of: $DOC_FILE"
    exit 0
  }
}

# ── Update workflow status ─────────────────────────────────────────────────────
STATUS_FILE="docs/bmm-workflow-status.yaml"
WORKFLOW_NAME="$BASENAME"

# Extract workflow name by matching filename against bmm-workflow-status.yaml
# Handles hyphenated names like product-brief, tech-spec, ux-design
find_workflow_name() {
  local doc_basename
  doc_basename=$(basename "$DOC_FILE" .md)
  local status_yaml="$STATUS_FILE"

  if [ ! -f "$status_yaml" ]; then
    echo ""
    return
  fi

  if command -v yq &>/dev/null; then
    # yq: find the name whose entry matches any leading segment of the filename
    yq eval '.workflow_status[].name' "$status_yaml" 2>/dev/null | while IFS= read -r name; do
      if [[ "$doc_basename" == "$name"* ]]; then
        echo "$name"
        return
      fi
    done | head -1
  else
    # python3 fallback: parse YAML names with grep/sed, no external modules needed
    python3 - <<PYEOF 2>/dev/null
import os, re
status_yaml = "$status_yaml"
doc_basename = "$doc_basename"
try:
    with open(status_yaml) as f:
        content = f.read()
    names = re.findall(r"""^\s*-\s+name:\s*["']?([^"'\n]+)["']?""", content, re.MULTILINE)
    for name in names:
        name = name.strip()
        if doc_basename.startswith(name):
            print(name)
            break
except Exception:
    pass
PYEOF
  fi
}

WORKFLOW_NAME=$(find_workflow_name)

# Fallback: strip trailing date/project suffix (e.g., product-brief-myapp-2026 -> product-brief)
if [[ -z "$WORKFLOW_NAME" ]]; then
  WORKFLOW_NAME=$(echo "$BASENAME" | sed 's/-[0-9]\{4\}[^-]*$//' | sed 's/-[a-zA-Z0-9]*$//')
fi

# Final fallback: original single-field cut
if [[ -z "$WORKFLOW_NAME" ]]; then
  WORKFLOW_NAME=$(echo "$BASENAME" | cut -d'-' -f1)
fi

if [ -f "$STATUS_FILE" ]; then
  echo ""
  echo -e "${GREEN}Updating workflow status...${NC}"
  
  TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  
  # Update last_updated timestamp
  if command -v yq &>/dev/null; then
    yq eval ".last_updated = \"$TIMESTAMP\"" -i "$STATUS_FILE" 2>/dev/null || true
    yq eval "(.workflow_status[] | select(.name == \"$WORKFLOW_NAME\") | .plannotator_review) = \"approved\"" \
      -i "$STATUS_FILE" 2>/dev/null || true
    yq eval "(.workflow_status[] | select(.name == \"$WORKFLOW_NAME\") | .reviewed_at) = \"$TIMESTAMP\"" \
      -i "$STATUS_FILE" 2>/dev/null || true
  else
    echo -e "${YELLOW}Note: Install yq for automatic status update${NC}"
    echo "  brew install yq"
    echo ""
    echo "  Manually update $STATUS_FILE:"
    echo "    plannotator_review: \"approved\""
    echo "    reviewed_at: \"$TIMESTAMP\""
  fi
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Phase gate review submitted.${NC}"
echo ""
echo "Next steps:"
echo "  1. Review and annotate in the plannotator UI"
echo "  2. Click Approve (saves to your enabled destination: Obsidian or Bear)"
echo "  3. Proceed to next BMAD phase"
echo ""
