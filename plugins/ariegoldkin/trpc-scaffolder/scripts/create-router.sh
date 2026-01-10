#!/bin/bash
# create-router.sh
# Creates a new tRPC router file from template

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Usage
if [ "$#" -ne 1 ]; then
    echo -e "${RED}Usage: $0 <router-name>${NC}"
    echo "Example: $0 user"
    exit 1
fi

ROUTER_NAME="$1"
ROUTER_NAME_LOWER=$(echo "$ROUTER_NAME" | tr '[:upper:]' '[:lower:]')
ROUTER_NAME_CAPS=$(echo "$ROUTER_NAME" | awk '{print toupper(substr($0,1,1)) tolower(substr($0,2))}')

# Paths
PROJECT_ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
TEMPLATE_FILE="$PROJECT_ROOT/.claude/skills/trpc-scaffolder/templates/router.ts.template"
OUTPUT_DIR="$PROJECT_ROOT/frontend/src/lib/trpc/routers"
OUTPUT_FILE="$OUTPUT_DIR/${ROUTER_NAME_LOWER}.ts"

# Check if router already exists
if [ -f "$OUTPUT_FILE" ]; then
    echo -e "${RED}Error: Router already exists at $OUTPUT_FILE${NC}"
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
echo -e "${YELLOW}Creating router: ${ROUTER_NAME_LOWER}${NC}"

sed -e "s/{{ROUTER_NAME}}/${ROUTER_NAME_LOWER}/g" \
    -e "s/{{ROUTER_NAME_CAPS}}/${ROUTER_NAME_CAPS}/g" \
    -e "s/{{ROUTER_DESCRIPTION}}/${ROUTER_NAME_LOWER}/g" \
    -e "s/{{ENTITY_NAME}}/${ROUTER_NAME_LOWER}/g" \
    "$TEMPLATE_FILE" > "$OUTPUT_FILE"

echo -e "${GREEN}✅ Router created: $OUTPUT_FILE${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Edit $OUTPUT_FILE and add your procedures"
echo "2. Create schemas in frontend/src/lib/trpc/schemas/"
echo "3. Register router in frontend/src/lib/trpc/routers/_app.ts:"
echo -e "   ${GREEN}import { ${ROUTER_NAME_LOWER}Router } from \"./${ROUTER_NAME_LOWER}\";${NC}"
echo -e "   ${GREEN}export const appRouter = router({ ..., ${ROUTER_NAME_LOWER}: ${ROUTER_NAME_LOWER}Router });${NC}"
echo ""
echo "Run validation: ./.claude/skills/trpc-scaffolder/scripts/validate-trpc.sh"
