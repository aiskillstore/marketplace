#!/bin/bash
# create-schema.sh
# Creates a new Zod schema file from template

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Usage
if [ "$#" -ne 1 ]; then
    echo -e "${RED}Usage: $0 <entity-name>${NC}"
    echo "Example: $0 hint"
    echo "Example: $0 user"
    exit 1
fi

ENTITY_NAME="$1"
ENTITY_NAME_LOWER=$(echo "$ENTITY_NAME" | tr '[:upper:]' '[:lower:]')
ENTITY_NAME_CAPS=$(echo "$ENTITY_NAME" | awk '{print toupper(substr($0,1,1)) tolower(substr($0,2))}')
CONST_NAME=$(echo "$ENTITY_NAME" | tr '[:lower:]' '[:upper:]')

# Paths
PROJECT_ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
TEMPLATE_FILE="$PROJECT_ROOT/.claude/skills/trpc-scaffolder/templates/schema.ts.template"
OUTPUT_DIR="$PROJECT_ROOT/frontend/src/lib/trpc/schemas"
OUTPUT_FILE="$OUTPUT_DIR/${ENTITY_NAME_LOWER}.schema.ts"

# Check if schema already exists
if [ -f "$OUTPUT_FILE" ]; then
    echo -e "${RED}Error: Schema already exists at $OUTPUT_FILE${NC}"
    exit 1
fi

# Check if template exists
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo -e "${RED}Error: Template not found at $TEMPLATE_FILE${NC}"
    exit 1
fi

# Create output directory if needed
mkdir -p "$OUTPUT_DIR"

# Read template and replace placeholders
echo -e "${YELLOW}Creating schema: ${ENTITY_NAME_LOWER}.schema.ts${NC}"

sed -e "s/{{ENTITY_NAME}}/${ENTITY_NAME_LOWER}/g" \
    -e "s/{{ENTITY_NAME_CAPS}}/${ENTITY_NAME_CAPS}/g" \
    -e "s/{{ENTITY_DESCRIPTION}}/${ENTITY_NAME_LOWER}/g" \
    -e "s/{{CONST_NAME}}/${CONST_NAME}/g" \
    "$TEMPLATE_FILE" > "$OUTPUT_FILE"

echo -e "${GREEN}✅ Schema created: $OUTPUT_FILE${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Edit $OUTPUT_FILE and define your Zod schemas"
echo "2. Replace TODO placeholders with actual field definitions"
echo "3. Import schemas in your router file"
echo "4. Use schemas in .input() and .output() of procedures"
echo ""
echo -e "${GREEN}Example usage in router:${NC}"
echo -e "   ${GREEN}import { create${ENTITY_NAME_CAPS}InputSchema, create${ENTITY_NAME_CAPS}OutputSchema } from \"../schemas/${ENTITY_NAME_LOWER}.schema\";${NC}"
echo ""
echo "Run validation: ./.claude/skills/trpc-scaffolder/scripts/validate-trpc.sh"
