#!/bin/bash

# Design to Production - Extract Structure Script
# Parses HTML prototype and outputs JSON structure for component analysis

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"

# Validate arguments
if [ $# -ne 1 ]; then
    echo -e "${RED}Usage: $0 <html-file-path>${NC}"
    echo "Example: $0 .superdesign/design_iterations/glassmorphism_hints_panel_1.html"
    exit 1
fi

HTML_FILE="$1"

# Check if file exists
if [ ! -f "$PROJECT_ROOT/$HTML_FILE" ]; then
    echo -e "${RED}Error: HTML file not found at $PROJECT_ROOT/$HTML_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}🔍 Analyzing HTML prototype...${NC}"
echo ""

# Extract component name from filename
FILENAME=$(basename "$HTML_FILE" .html)
COMPONENT_NAME=$(echo "$FILENAME" | sed 's/glassmorphism_//' | sed 's/_/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1' OFS='')

# Extract glassmorphism classes
GLASS_CLASSES=$(grep -oh 'class="[^"]*' "$PROJECT_ROOT/$HTML_FILE" | sed 's/class="//' | tr ' ' '\n' | grep -E '^(glass-|btn-|neon-|gradient-|text-glow|icon-glow|fade-in|pulse-glow)' | sort -u || echo "none")

# Extract interactive elements
BUTTONS=$(grep -c '<button' "$PROJECT_ROOT/$HTML_FILE" || echo "0")
INPUTS=$(grep -c '<input' "$PROJECT_ROOT/$HTML_FILE" || echo "0")
SELECTS=$(grep -c '<select' "$PROJECT_ROOT/$HTML_FILE" || echo "0")
FORMS=$(grep -c '<form' "$PROJECT_ROOT/$HTML_FILE" || echo "0")

# Detect layout patterns
LAYOUT_PATTERN="unknown"
if grep -q 'display: grid\|grid-template' "$PROJECT_ROOT/$HTML_FILE"; then
    LAYOUT_PATTERN="grid"
elif grep -q 'display: flex\|flex-direction' "$PROJECT_ROOT/$HTML_FILE"; then
    LAYOUT_PATTERN="flex"
elif grep -q 'flex flex-col\|space-y-' "$PROJECT_ROOT/$HTML_FILE"; then
    LAYOUT_PATTERN="vertical-stack"
fi

# Output JSON structure
OUTPUT_FILE="$PROJECT_ROOT/.claude/skills/design-to-production/${COMPONENT_NAME}-structure.json"

cat > "$OUTPUT_FILE" <<EOF
{
  "componentName": "$COMPONENT_NAME",
  "sourceFile": "$HTML_FILE",
  "glassmorphismClasses": [
$(echo "$GLASS_CLASSES" | sed 's/^/    "/' | sed 's/$/",/' | sed '$ s/,$//')
  ],
  "interactiveElements": {
    "buttons": $BUTTONS,
    "inputs": $INPUTS,
    "selects": $SELECTS,
    "forms": $FORMS
  },
  "layoutPattern": "$LAYOUT_PATTERN",
  "suggestedTemplate": "$([ "$BUTTONS" -gt 0 ] && echo "interactive-card" || echo "display-card")"
}
EOF

echo -e "${GREEN}✓ Structure extracted${NC}"
echo ""
echo "Component: $COMPONENT_NAME"
echo "Glassmorphism classes: $(echo "$GLASS_CLASSES" | wc -l | tr -d ' ')"
echo "Interactive elements: $BUTTONS buttons, $INPUTS inputs, $SELECTS selects"
echo "Layout pattern: $LAYOUT_PATTERN"
echo "Suggested template: $([ "$BUTTONS" -gt 0 ] && echo "interactive-card" || echo "display-card")"
echo ""
echo -e "${GREEN}Output saved to: $OUTPUT_FILE${NC}"
