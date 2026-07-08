#!/bin/bash

# Module Scaffolder - Add Component Script
# Adds a new component to an existing module

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TEMPLATES_DIR="$SKILL_DIR/templates"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
MODULES_DIR="$PROJECT_ROOT/frontend/src/modules"

# Validate arguments
if [ $# -ne 2 ]; then
    echo -e "${RED}Usage: $0 <module-name> <ComponentName>${NC}"
    echo "Example: $0 analytics AnalyticsChart"
    exit 1
fi

MODULE_NAME="$1"
COMPONENT_NAME="$2"
MODULE_PATH="$MODULES_DIR/$MODULE_NAME"

# Check if module exists
if [ ! -d "$MODULE_PATH" ]; then
    echo -e "${RED}Error: Module '$MODULE_NAME' does not exist${NC}"
    exit 1
fi

# Validate component name (PascalCase)
if ! [[ "$COMPONENT_NAME" =~ ^[A-Z][a-zA-Z0-9]*$ ]]; then
    echo -e "${RED}Error: Component name must be PascalCase (e.g., 'AnalyticsChart')${NC}"
    exit 1
fi

COMPONENT_FILE="$MODULE_PATH/components/$COMPONENT_NAME.tsx"

# Check if component already exists
if [ -f "$COMPONENT_FILE" ]; then
    echo -e "${RED}Error: Component '$COMPONENT_NAME' already exists${NC}"
    exit 1
fi

echo -e "${GREEN}🚀 Adding component: $COMPONENT_NAME to $MODULE_NAME${NC}"
echo ""

# Generate component from template
echo "Generating $COMPONENT_NAME.tsx..."
sed -e "s/{{COMPONENT_NAME}}/$COMPONENT_NAME/g" \
    -e "s/{{MODULE_NAME}}/$MODULE_NAME/g" \
    "$TEMPLATES_DIR/component.tsx.template" > "$COMPONENT_FILE"

# Update components/index.ts barrel export
INDEX_FILE="$MODULE_PATH/components/index.ts"
if [ -f "$INDEX_FILE" ]; then
    echo "Updating components/index.ts..."
    # Check if export already exists
    if grep -q "export \* from \"./$COMPONENT_NAME\"" "$INDEX_FILE"; then
        echo -e "${YELLOW}  ⚠ Export already exists in index.ts${NC}"
    else
        echo "export * from \"./$COMPONENT_NAME\";" >> "$INDEX_FILE"
        echo -e "${GREEN}  ✓ Added export to index.ts${NC}"
    fi
else
    echo "Creating components/index.ts..."
    echo "export * from \"./$COMPONENT_NAME\";" > "$INDEX_FILE"
fi

echo ""
echo -e "${GREEN}✅ Component '$COMPONENT_NAME' added successfully!${NC}"
echo ""
echo "File created:"
echo "  $COMPONENT_FILE"
echo ""
echo "Next steps:"
echo "  1. Edit $COMPONENT_FILE"
echo "  2. Add props to I${COMPONENT_NAME}Props interface"
echo "  3. Implement component logic"
echo ""
