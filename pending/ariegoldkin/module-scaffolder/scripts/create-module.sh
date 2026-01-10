#!/bin/bash

# Module Scaffolder - Create Module Script
# Creates a new feature module with proper structure and boilerplate

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

# Project paths
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
MODULES_DIR="$PROJECT_ROOT/frontend/src/modules"

# Validate arguments
if [ $# -ne 1 ]; then
    echo -e "${RED}Usage: $0 <module-name>${NC}"
    echo "Example: $0 analytics"
    exit 1
fi

MODULE_NAME="$1"

# Validate module name (lowercase with optional hyphens)
if ! [[ "$MODULE_NAME" =~ ^[a-z][a-z0-9-]*$ ]]; then
    echo -e "${RED}Error: Module name must be lowercase with hyphens (e.g., 'analytics' or 'user-profile')${NC}"
    exit 1
fi

MODULE_PATH="$MODULES_DIR/$MODULE_NAME"

# Check if module already exists
if [ -d "$MODULE_PATH" ]; then
    echo -e "${RED}Error: Module '$MODULE_NAME' already exists at $MODULE_PATH${NC}"
    exit 1
fi

echo -e "${GREEN}🚀 Creating module: $MODULE_NAME${NC}"
echo ""

# Create directory structure
echo "Creating directory structure..."
mkdir -p "$MODULE_PATH/components"
mkdir -p "$MODULE_PATH/hooks"
mkdir -p "$MODULE_PATH/utils"

# Convert module-name to PascalCase (e.g., user-profile → UserProfile)
# Using awk for portability across macOS/Linux
MODULE_NAME_PASCAL=$(echo "$MODULE_NAME" | awk -F'-' '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1' OFS='')

# Generate types.ts
echo "Generating types.ts..."
sed -e "s/{{MODULE_NAME}}/$MODULE_NAME/g" \
    -e "s/{{MODULE_NAME_PASCAL}}/$MODULE_NAME_PASCAL/g" \
    "$TEMPLATES_DIR/types.ts.template" > "$MODULE_PATH/types.ts"

# Generate example component (ExampleCard)
COMPONENT_NAME="${MODULE_NAME_PASCAL}Card"
echo "Generating $COMPONENT_NAME.tsx..."
sed -e "s/{{COMPONENT_NAME}}/$COMPONENT_NAME/g" \
    -e "s/{{MODULE_NAME}}/$MODULE_NAME/g" \
    "$TEMPLATES_DIR/component.tsx.template" > "$MODULE_PATH/components/$COMPONENT_NAME.tsx"

# Generate components/index.ts
echo "Generating components/index.ts..."
sed -e "s/{{DIRECTORY_NAME}}/components/g" \
    -e "s/{{EXPORT_NAME}}/$COMPONENT_NAME/g" \
    "$TEMPLATES_DIR/index.ts.template" > "$MODULE_PATH/components/index.ts"

# Generate hooks/index.ts (empty barrel export)
echo "Generating hooks/index.ts..."
echo "// Barrel exports for hooks" > "$MODULE_PATH/hooks/index.ts"
echo "// Export hooks as they are created" >> "$MODULE_PATH/hooks/index.ts"

# Generate utils/index.ts (empty barrel export)
echo "Generating utils/index.ts..."
echo "// Barrel exports for utils" > "$MODULE_PATH/utils/index.ts"
echo "// Export utilities as they are created" >> "$MODULE_PATH/utils/index.ts"

echo ""
echo -e "${GREEN}✅ Module '$MODULE_NAME' created successfully!${NC}"
echo ""
echo "Structure created:"
echo "  $MODULE_PATH/"
echo "  ├── components/"
echo "  │   ├── ${COMPONENT_NAME}.tsx"
echo "  │   └── index.ts"
echo "  ├── hooks/"
echo "  │   └── index.ts"
echo "  ├── utils/"
echo "  │   └── index.ts"
echo "  └── types.ts"
echo ""
echo "Next steps:"
echo "  1. Edit $MODULE_PATH/components/${COMPONENT_NAME}.tsx"
echo "  2. Add hooks in $MODULE_PATH/hooks/"
echo "  3. Add utilities in $MODULE_PATH/utils/"
echo "  4. Run: $SCRIPT_DIR/validate-module.sh $MODULE_NAME"
echo ""
