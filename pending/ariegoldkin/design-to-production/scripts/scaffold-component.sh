#!/bin/bash

# Design to Production - Scaffold Component Script
# Creates React component file from template with proper structure

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
TEMPLATES_DIR="$SCRIPT_DIR/../templates"

# Default values
COMPONENT_NAME=""
MODULE_NAME=""
TEMPLATE_TYPE="interactive-card"
PROPS=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --name)
            COMPONENT_NAME="$2"
            shift 2
            ;;
        --module)
            MODULE_NAME="$2"
            shift 2
            ;;
        --template)
            TEMPLATE_TYPE="$2"
            shift 2
            ;;
        --props)
            PROPS="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Validate required arguments
if [ -z "$COMPONENT_NAME" ] || [ -z "$MODULE_NAME" ]; then
    echo -e "${RED}Usage: $0 --name <ComponentName> --module <module-name> [--template <template-type>] [--props <props>]${NC}"
    echo "Example: $0 --name HintsPanel --module practice --template interactive-card --props \"title:string,hints:IHint[]\""
    exit 1
fi

echo -e "${GREEN}🏗️  Scaffolding component...${NC}"
echo ""

# Determine output path
MODULE_PATH="$PROJECT_ROOT/frontend/src/modules/$MODULE_NAME"
COMPONENT_PATH="$MODULE_PATH/components"

# Check if module exists
if [ ! -d "$MODULE_PATH" ]; then
    echo -e "${RED}Error: Module '$MODULE_NAME' does not exist at $MODULE_PATH${NC}"
    echo -e "${YELLOW}Hint: Create module first using module-scaffolder skill${NC}"
    exit 1
fi

# Create components directory if it doesn't exist
mkdir -p "$COMPONENT_PATH"

# Check if template exists
TEMPLATE_FILE="$TEMPLATES_DIR/${TEMPLATE_TYPE}.tsx.template"
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo -e "${RED}Error: Template '$TEMPLATE_TYPE' not found at $TEMPLATE_FILE${NC}"
    exit 1
fi

# Generate component file
OUTPUT_FILE="$COMPONENT_PATH/$COMPONENT_NAME.tsx"

if [ -f "$OUTPUT_FILE" ]; then
    echo -e "${YELLOW}Warning: Component file already exists at $OUTPUT_FILE${NC}"
    read -p "Overwrite? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Replace template variables
sed -e "s/{{COMPONENT_NAME}}/$COMPONENT_NAME/g" \
    -e "s/{{MODULE_NAME}}/$MODULE_NAME/g" \
    "$TEMPLATE_FILE" > "$OUTPUT_FILE"

echo -e "${GREEN}✓ Component scaffolded${NC}"
echo ""
echo "Component: $COMPONENT_NAME"
echo "Module: $MODULE_NAME"
echo "Template: $TEMPLATE_TYPE"
echo "File: $OUTPUT_FILE"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "1. Open $OUTPUT_FILE"
echo "2. Complete TODO items"
echo "3. Run: ./.claude/skills/design-to-production/scripts/validate.sh $OUTPUT_FILE"
