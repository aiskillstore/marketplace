#!/bin/bash

# Design to Production - Validate Component Script
# Validates component against DevPrep AI quality standards

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
    echo -e "${RED}Usage: $0 <component-path>${NC}"
    echo "Example: $0 modules/practice/components/HintsPanel.tsx"
    exit 1
fi

COMPONENT_PATH="$1"

# Check if file exists
if [ ! -f "$PROJECT_ROOT/frontend/src/$COMPONENT_PATH" ] && [ ! -f "$COMPONENT_PATH" ]; then
    echo -e "${RED}Error: Component file not found${NC}"
    exit 1
fi

# Normalize path
if [ -f "$PROJECT_ROOT/frontend/src/$COMPONENT_PATH" ]; then
    FULL_PATH="$PROJECT_ROOT/frontend/src/$COMPONENT_PATH"
else
    FULL_PATH="$COMPONENT_PATH"
fi

echo -e "${GREEN}🔍 Validating component...${NC}"
echo ""

ERRORS=0
WARNINGS=0

# Check file size (≤180 lines)
LINES=$(wc -l < "$FULL_PATH")
if [ "$LINES" -gt 180 ]; then
    echo -e "${RED}✗ File size: $LINES lines (exceeds 180)${NC}"
    ((ERRORS++))
else
    echo -e "${GREEN}✓ File size: $LINES lines${NC}"
fi

# Check interface naming (I prefix)
INTERFACE_COUNT=$(grep -h '^interface [A-Z]' "$FULL_PATH" | grep -v '^interface I' | wc -l || echo "0")
INTERFACE_COUNT=$(echo "$INTERFACE_COUNT" | tr -d ' \n')
if [ "$INTERFACE_COUNT" -gt 0 ]; then
    echo -e "${RED}✗ Found interface(s) without 'I' prefix${NC}"
    ((ERRORS++))
else
    echo -e "${GREEN}✓ Interface naming (I prefix)${NC}"
fi

# Check for 'any' types
ANY_COUNT=$(grep ': any' "$FULL_PATH" | wc -l || echo "0")
ANY_COUNT=$(echo "$ANY_COUNT" | tr -d ' \n')
if [ "$ANY_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}⚠ Found $ANY_COUNT usage(s) of 'any' type${NC}"
    ((WARNINGS++))
else
    echo -e "${GREEN}✓ No 'any' types${NC}"
fi

# Check glassmorphism class usage
VALID_CLASSES="glass-card|glass-card-static|glass-header|btn-glass|btn-primary-glass|neon-glow|neon-glow-purple|neon-glow-pink|neon-glow-cyan|neon-glow-green|neon-glow-red|gradient-text|text-glow|icon-glow|fade-in|slide-up|pulse-glow"
INVALID_GLASS=$(grep -o 'className="[^"]*glass[^"]*"' "$FULL_PATH" | grep -Ev "($VALID_CLASSES)" || echo "")
if [ -n "$INVALID_GLASS" ]; then
    echo -e "${YELLOW}⚠ Potentially invalid glassmorphism classes:${NC}"
    echo "$INVALID_GLASS" | sed 's/^/  /'
    ((WARNINGS++))
else
    echo -e "${GREEN}✓ Glassmorphism classes valid${NC}"
fi

# Check import patterns
RELATIVE_IMPORTS=$(grep "from ['\"]\\.\\./" "$FULL_PATH" | wc -l || echo "0")
RELATIVE_IMPORTS=$(echo "$RELATIVE_IMPORTS" | tr -d ' \n')
if [ "$RELATIVE_IMPORTS" -gt 3 ]; then
    echo -e "${YELLOW}⚠ Found $RELATIVE_IMPORTS relative imports (consider using @shared, @modules, @lib)${NC}"
    ((WARNINGS++))
else
    echo -e "${GREEN}✓ Import patterns${NC}"
fi

# Summary
echo ""
echo "======================================"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ Validation PASSED${NC}"
    echo "Component meets all DevPrep AI standards!"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Validation PASSED with warnings${NC}"
    echo "Found $WARNINGS warning(s) - review recommended"
else
    echo -e "${RED}❌ Validation FAILED${NC}"
    echo "Found $ERRORS error(s) and $WARNINGS warning(s)"
    exit 1
fi
echo "======================================"
