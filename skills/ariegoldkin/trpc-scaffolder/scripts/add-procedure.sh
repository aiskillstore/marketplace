#!/bin/bash
# add-procedure.sh
# Adds a procedure to an existing tRPC router

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Usage
if [ "$#" -lt 2 ]; then
    echo -e "${RED}Usage: $0 <router-name> <procedure-name> [query|mutation]${NC}"
    echo "Example: $0 ai getHints query"
    echo "Example: $0 user createUser mutation"
    exit 1
fi

ROUTER_NAME="$1"
PROCEDURE_NAME="$2"
PROCEDURE_TYPE="${3:-mutation}"  # Default to mutation

ROUTER_NAME_LOWER=$(echo "$ROUTER_NAME" | tr '[:upper:]' '[:lower:]')
PROCEDURE_NAME_CAPS=$(echo "$PROCEDURE_NAME" | awk '{print toupper(substr($0,1,1)) tolower(substr($0,2))}')

# Validate procedure type
if [[ "$PROCEDURE_TYPE" != "query" && "$PROCEDURE_TYPE" != "mutation" ]]; then
    echo -e "${RED}Error: Procedure type must be 'query' or 'mutation'${NC}"
    exit 1
fi

# Paths
PROJECT_ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
TEMPLATE_FILE="$PROJECT_ROOT/.claude/skills/trpc-scaffolder/templates/procedure.snippet"
ROUTER_FILE="$PROJECT_ROOT/frontend/src/lib/trpc/routers/${ROUTER_NAME_LOWER}.ts"

# Check if router exists
if [ ! -f "$ROUTER_FILE" ]; then
    echo -e "${RED}Error: Router not found at $ROUTER_FILE${NC}"
    echo "Create router first: ./.claude/skills/trpc-scaffolder/scripts/create-router.sh $ROUTER_NAME"
    exit 1
fi

# Check if template exists
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo -e "${RED}Error: Template not found at $TEMPLATE_FILE${NC}"
    exit 1
fi

# Read template and replace placeholders
PROCEDURE_CODE=$(sed -e "s/{{PROCEDURE_NAME}}/${PROCEDURE_NAME}/g" \
    -e "s/{{PROCEDURE_NAME_CAPS}}/${PROCEDURE_NAME_CAPS}/g" \
    -e "s/{{PROCEDURE_TYPE}}/${PROCEDURE_TYPE}/g" \
    -e "s/{{PROCEDURE_DESCRIPTION}}/TODO: Add description/g" \
    -e "s/{{INPUT_FIELDS}}/TODO: List input fields/g" \
    -e "s/{{OUTPUT_FIELDS}}/TODO: List output fields/g" \
    "$TEMPLATE_FILE")

echo -e "${YELLOW}Adding procedure '${PROCEDURE_NAME}' to ${ROUTER_NAME_LOWER} router...${NC}"
echo ""
echo -e "${YELLOW}Procedure code to add:${NC}"
echo "$PROCEDURE_CODE"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Add this procedure to $ROUTER_FILE inside the router({ ... }) object"
echo "2. Create schemas for ${PROCEDURE_NAME}InputSchema and ${PROCEDURE_NAME}OutputSchema"
echo "3. Import schemas at the top of the router file"
echo "4. Implement the business logic in the procedure"
echo ""
echo -e "${GREEN}💡 Tip: Don't forget the trailing comma after the procedure!${NC}"
