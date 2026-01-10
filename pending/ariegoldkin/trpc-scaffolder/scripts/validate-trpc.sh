#!/bin/bash
# validate-trpc.sh
# Validates tRPC setup: router registration, schema existence, type exports

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Paths
PROJECT_ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
ROUTERS_DIR="$PROJECT_ROOT/frontend/src/lib/trpc/routers"
SCHEMAS_DIR="$PROJECT_ROOT/frontend/src/lib/trpc/schemas"
APP_ROUTER="$ROUTERS_DIR/_app.ts"

echo -e "${BLUE}🔍 Validating tRPC Setup...${NC}"
echo ""

# Check 1: _app.ts exists
echo -e "${YELLOW}[1/4] Checking _app.ts exists...${NC}"
if [ ! -f "$APP_ROUTER" ]; then
    echo -e "${RED}❌ Error: _app.ts not found at $APP_ROUTER${NC}"
    exit 1
fi
echo -e "${GREEN}✅ _app.ts found${NC}"
echo ""

# Check 2: Find all router files (except _app.ts)
echo -e "${YELLOW}[2/4] Finding router files...${NC}"
ROUTER_FILES=$(find "$ROUTERS_DIR" -name "*.ts" ! -name "_app.ts" -type f 2>/dev/null || true)

if [ -z "$ROUTER_FILES" ]; then
    echo -e "${YELLOW}⚠️  No router files found (besides _app.ts)${NC}"
    echo ""
else
    echo -e "${GREEN}Found routers:${NC}"
    echo "$ROUTER_FILES" | while read -r file; do
        basename "$file"
    done
    echo ""
fi

# Check 3: Verify routers are registered in _app.ts
echo -e "${YELLOW}[3/4] Checking router registration in _app.ts...${NC}"
UNREGISTERED=0

if [ -n "$ROUTER_FILES" ]; then
    echo "$ROUTER_FILES" | while read -r router_file; do
        router_name=$(basename "$router_file" .ts)

        # Check if imported
        if ! grep -q "import.*${router_name}Router.*from.*\\./${router_name}" "$APP_ROUTER"; then
            echo -e "${RED}❌ Router '${router_name}' not imported in _app.ts${NC}"
            UNREGISTERED=1
        fi

        # Check if registered in appRouter
        if ! grep -q "${router_name}:.*${router_name}Router" "$APP_ROUTER"; then
            echo -e "${RED}❌ Router '${router_name}' not registered in appRouter${NC}"
            UNREGISTERED=1
        fi
    done

    if [ "$UNREGISTERED" -eq 0 ]; then
        echo -e "${GREEN}✅ All routers properly registered${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No routers to check${NC}"
fi
echo ""

# Check 4: Verify schema files exist and export types
echo -e "${YELLOW}[4/4] Checking schema files...${NC}"
SCHEMA_FILES=$(find "$SCHEMAS_DIR" -name "*.schema.ts" -type f 2>/dev/null || true)

if [ -z "$SCHEMA_FILES" ]; then
    echo -e "${YELLOW}⚠️  No schema files found${NC}"
    echo ""
else
    echo -e "${GREEN}Found schemas:${NC}"
    MISSING_EXPORTS=0

    echo "$SCHEMA_FILES" | while read -r schema_file; do
        schema_name=$(basename "$schema_file")
        echo "  - $schema_name"

        # Check if schema exports types
        if ! grep -q "export type" "$schema_file"; then
            echo -e "${RED}    ❌ Missing type exports (should use: export type X = z.infer<...>)${NC}"
            MISSING_EXPORTS=1
        fi
    done

    if [ "$MISSING_EXPORTS" -eq 0 ]; then
        echo -e "${GREEN}✅ All schemas export types${NC}"
    fi
fi
echo ""

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ tRPC validation complete${NC}"
echo ""
echo -e "${YELLOW}Reminder:${NC}"
echo "- All routers must be registered in _app.ts"
echo "- All schemas should export inferred types"
echo "- Router procedures should use .input() and .output()"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "- Run: npm run type-check"
echo "- Test endpoints in your frontend"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
