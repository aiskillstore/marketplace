#!/bin/bash

# Module Scaffolder - Validate Module Script
# Validates that a module follows DevPrep AI architecture and quality standards

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
MODULES_DIR="$PROJECT_ROOT/frontend/src/modules"

# Validate arguments
if [ $# -ne 1 ]; then
    echo -e "${RED}Usage: $0 <module-name>${NC}"
    echo "Example: $0 analytics"
    exit 1
fi

MODULE_NAME="$1"
MODULE_PATH="$MODULES_DIR/$MODULE_NAME"

# Check if module exists
if [ ! -d "$MODULE_PATH" ]; then
    echo -e "${RED}Error: Module '$MODULE_NAME' does not exist at $MODULE_PATH${NC}"
    exit 1
fi

echo -e "${GREEN}🔍 Validating module: $MODULE_NAME${NC}"
echo ""

ERRORS=0
WARNINGS=0

# Check directory structure
echo "Checking directory structure..."
if [ ! -d "$MODULE_PATH/components" ]; then
    echo -e "${RED}  ✗ Missing components/ directory${NC}"
    ((ERRORS++))
else
    echo -e "${GREEN}  ✓ components/ directory exists${NC}"
fi

if [ ! -d "$MODULE_PATH/hooks" ]; then
    echo -e "${YELLOW}  ⚠ Missing hooks/ directory (optional but recommended)${NC}"
    ((WARNINGS++))
else
    echo -e "${GREEN}  ✓ hooks/ directory exists${NC}"
fi

if [ ! -d "$MODULE_PATH/utils" ]; then
    echo -e "${YELLOW}  ⚠ Missing utils/ directory (optional but recommended)${NC}"
    ((WARNINGS++))
else
    echo -e "${GREEN}  ✓ utils/ directory exists${NC}"
fi

# Check for barrel exports
echo ""
echo "Checking barrel exports..."
if [ -f "$MODULE_PATH/components/index.ts" ]; then
    echo -e "${GREEN}  ✓ components/index.ts exists${NC}"
else
    echo -e "${RED}  ✗ Missing components/index.ts${NC}"
    ((ERRORS++))
fi

# Check file size limits (180 lines)
echo ""
echo "Checking file size limits (max 180 lines)..."
while IFS= read -r -d '' file; do
    lines=$(wc -l < "$file")
    if [ "$lines" -gt 180 ]; then
        echo -e "${RED}  ✗ $file: $lines lines (exceeds 180)${NC}"
        ((ERRORS++))
    fi
done < <(find "$MODULE_PATH" -type f \( -name "*.ts" -o -name "*.tsx" \) -print0)

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}  ✓ All files within 180-line limit${NC}"
fi

# Check for proper TypeScript naming (I prefix for interfaces)
echo ""
echo "Checking naming conventions..."
INTERFACE_COUNT=$(grep -rh "^interface [A-Z]" "$MODULE_PATH" --include="*.ts" --include="*.tsx" | grep -v "^interface I" | wc -l || true)
if [ "$INTERFACE_COUNT" -gt 0 ]; then
    echo -e "${RED}  ✗ Found $INTERFACE_COUNT interface(s) without 'I' prefix${NC}"
    grep -r "^interface [A-Z]" "$MODULE_PATH" --include="*.ts" --include="*.tsx" | grep -v "interface I" | sed 's/^/    /'
    ((ERRORS++))
else
    echo -e "${GREEN}  ✓ All interfaces use 'I' prefix${NC}"
fi

# Check for 'any' types
echo ""
echo "Checking for 'any' types..."
ANY_COUNT=$(grep -r ": any" "$MODULE_PATH" --include="*.ts" --include="*.tsx" | wc -l || true)
if [ "$ANY_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}  ⚠ Found $ANY_COUNT usage(s) of 'any' type${NC}"
    ((WARNINGS++))
else
    echo -e "${GREEN}  ✓ No 'any' types found${NC}"
fi

# Check for proper imports (path aliases)
echo ""
echo "Checking import patterns..."
RELATIVE_IMPORTS=$(grep -r "from ['\"]\.\./" "$MODULE_PATH" --include="*.ts" --include="*.tsx" | wc -l || true)
if [ "$RELATIVE_IMPORTS" -gt 5 ]; then
    echo -e "${YELLOW}  ⚠ Found $RELATIVE_IMPORTS relative imports (consider using path aliases @modules, @shared, @lib)${NC}"
    ((WARNINGS++))
else
    echo -e "${GREEN}  ✓ Import patterns look good${NC}"
fi

# Summary
echo ""
echo "======================================"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ Module validation PASSED${NC}"
    echo "Module '$MODULE_NAME' follows all DevPrep AI standards!"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Module validation PASSED with warnings${NC}"
    echo "Found $WARNINGS warning(s) - review recommended"
else
    echo -e "${RED}❌ Module validation FAILED${NC}"
    echo "Found $ERRORS error(s) and $WARNINGS warning(s)"
    exit 1
fi
echo "======================================"
echo ""
