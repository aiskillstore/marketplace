#!/bin/bash
# Playwright Project Setup Checker
# Validates that a project has Playwright properly configured

set -e

echo "🎭 Playwright Setup Checker"
echo "=========================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# Check for package.json
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ package.json not found${NC}"
    echo "   Run 'npm init' to create one"
    exit 1
fi

echo "📦 Checking dependencies..."

# Check for Playwright installation
if grep -q '"@playwright/test"' package.json; then
    VERSION=$(grep '"@playwright/test"' package.json | sed 's/.*: *"\([^"]*\)".*/\1/')
    echo -e "${GREEN}✅ @playwright/test installed: $VERSION${NC}"
else
    echo -e "${RED}❌ @playwright/test not found in package.json${NC}"
    echo "   Run: npm install -D @playwright/test"
    ((ERRORS++))
fi

# Check for Playwright config
echo ""
echo "⚙️  Checking configuration..."

if [ -f "playwright.config.ts" ] || [ -f "playwright.config.js" ]; then
    CONFIG_FILE=$(ls playwright.config.* 2>/dev/null | head -1)
    echo -e "${GREEN}✅ Config file found: $CONFIG_FILE${NC}"
    
    # Check for common config issues
    if grep -q "baseURL" "$CONFIG_FILE"; then
        echo -e "${GREEN}   ✓ baseURL configured${NC}"
    else
        echo -e "${YELLOW}   ⚠ baseURL not set (tests will need full URLs)${NC}"
        ((WARNINGS++))
    fi
    
    if grep -q "trace" "$CONFIG_FILE"; then
        echo -e "${GREEN}   ✓ Trace capture configured${NC}"
    else
        echo -e "${YELLOW}   ⚠ Trace not configured (add trace: 'on-first-retry')${NC}"
        ((WARNINGS++))
    fi
    
    if grep -q "screenshot" "$CONFIG_FILE"; then
        echo -e "${GREEN}   ✓ Screenshots configured${NC}"
    fi
    
    if grep -q "webServer" "$CONFIG_FILE"; then
        echo -e "${GREEN}   ✓ WebServer configured (auto-starts dev server)${NC}"
    else
        echo -e "${YELLOW}   ⚠ webServer not configured (manual server start needed)${NC}"
        ((WARNINGS++))
    fi
else
    echo -e "${RED}❌ playwright.config.ts/js not found${NC}"
    echo "   Run: npx playwright init"
    ((ERRORS++))
fi

# Check for test files
echo ""
echo "🧪 Checking test files..."

TEST_COUNT=$(find . -name "*.spec.ts" -o -name "*.spec.js" -o -name "*.test.ts" 2>/dev/null | grep -v node_modules | wc -l)

if [ "$TEST_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ Found $TEST_COUNT test file(s)${NC}"
    
    # Check for Page Objects
    PO_COUNT=$(find . -name "*.page.ts" -o -name "*.page.js" 2>/dev/null | grep -v node_modules | wc -l)
    if [ "$PO_COUNT" -gt 0 ]; then
        echo -e "${GREEN}   ✓ Found $PO_COUNT page object(s)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ No test files found (*.spec.ts, *.spec.js)${NC}"
    ((WARNINGS++))
fi

# Check for browsers
echo ""
echo "🌐 Checking browsers..."

if npx playwright --version > /dev/null 2>&1; then
    # Check if browsers are installed
    if [ -d "$HOME/.cache/ms-playwright" ] || [ -d "/ms-playwright" ]; then
        echo -e "${GREEN}✅ Playwright browsers installed${NC}"
    else
        echo -e "${YELLOW}⚠ Browsers may not be installed${NC}"
        echo "   Run: npx playwright install"
        ((WARNINGS++))
    fi
else
    echo -e "${RED}❌ Playwright CLI not available${NC}"
    ((ERRORS++))
fi

# Check for TypeScript
echo ""
echo "📝 Checking TypeScript..."

if [ -f "tsconfig.json" ]; then
    echo -e "${GREEN}✅ tsconfig.json found${NC}"
else
    echo -e "${YELLOW}⚠ tsconfig.json not found (may need for TS tests)${NC}"
    ((WARNINGS++))
fi

# Check for ESLint
if [ -f ".eslintrc.js" ] || [ -f ".eslintrc.json" ] || grep -q '"eslint"' package.json 2>/dev/null; then
    echo -e "${GREEN}✅ ESLint configured${NC}"
fi

# Check for test scripts
echo ""
echo "📜 Checking npm scripts..."

if grep -q '"test"' package.json; then
    TEST_SCRIPT=$(grep '"test"' package.json | head -1)
    if echo "$TEST_SCRIPT" | grep -q "playwright"; then
        echo -e "${GREEN}✅ Test script uses Playwright${NC}"
    else
        echo -e "${YELLOW}⚠ Test script doesn't reference Playwright${NC}"
        ((WARNINGS++))
    fi
fi

# Check for CI config
echo ""
echo "🔄 Checking CI/CD..."

if [ -f ".github/workflows/playwright.yml" ] || [ -f ".github/workflows/test.yml" ]; then
    echo -e "${GREEN}✅ GitHub Actions workflow found${NC}"
elif [ -f ".gitlab-ci.yml" ]; then
    echo -e "${GREEN}✅ GitLab CI config found${NC}"
else
    echo -e "${YELLOW}⚠ No CI configuration found${NC}"
    ((WARNINGS++))
fi

# Summary
echo ""
echo "=========================="
echo "📊 Summary"
echo "=========================="

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warning(s) found${NC}"
    exit 0
else
    echo -e "${RED}❌ $ERRORS error(s), $WARNINGS warning(s)${NC}"
    exit 1
fi
