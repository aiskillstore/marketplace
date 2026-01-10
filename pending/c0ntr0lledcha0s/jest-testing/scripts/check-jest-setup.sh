#!/bin/bash
# Jest Project Setup Checker
# Validates that a project has Jest properly configured

set -e

echo "🃏 Jest Setup Checker"
echo "====================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

# Check for package.json
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ package.json not found${NC}"
    exit 1
fi

echo "📦 Checking dependencies..."

# Check for Jest
if grep -q '"jest"' package.json || grep -q '"@jest/core"' package.json; then
    VERSION=$(grep -o '"jest": *"[^"]*"' package.json | sed 's/.*: *"\([^"]*\)".*/\1/' || echo "installed")
    echo -e "${GREEN}✅ Jest installed: $VERSION${NC}"
else
    echo -e "${RED}❌ Jest not found${NC}"
    echo "   Run: npm install -D jest"
    ((ERRORS++))
fi

# Check for TypeScript support
if grep -q '"ts-jest"' package.json; then
    echo -e "${GREEN}✅ ts-jest installed${NC}"
elif grep -q '"@swc/jest"' package.json; then
    echo -e "${GREEN}✅ @swc/jest installed${NC}"
elif grep -q '"babel-jest"' package.json; then
    echo -e "${GREEN}✅ babel-jest installed${NC}"
else
    if grep -q '"typescript"' package.json; then
        echo -e "${YELLOW}⚠ TypeScript found but no Jest transformer${NC}"
        echo "   Run: npm install -D ts-jest"
        ((WARNINGS++))
    fi
fi

# Check for Testing Library
if grep -q '"@testing-library/react"' package.json; then
    echo -e "${GREEN}✅ @testing-library/react installed${NC}"
    
    if grep -q '"@testing-library/jest-dom"' package.json; then
        echo -e "${GREEN}   ✓ jest-dom matchers available${NC}"
    else
        echo -e "${YELLOW}   ⚠ Consider adding @testing-library/jest-dom${NC}"
        ((WARNINGS++))
    fi
    
    if grep -q '"@testing-library/user-event"' package.json; then
        echo -e "${GREEN}   ✓ user-event installed${NC}"
    else
        echo -e "${YELLOW}   ⚠ Consider adding @testing-library/user-event${NC}"
        ((WARNINGS++))
    fi
fi

# Check for MSW
if grep -q '"msw"' package.json; then
    echo -e "${GREEN}✅ MSW installed for network mocking${NC}"
fi

echo ""
echo "⚙️  Checking configuration..."

# Check for Jest config
if [ -f "jest.config.ts" ] || [ -f "jest.config.js" ] || [ -f "jest.config.json" ]; then
    CONFIG_FILE=$(ls jest.config.* 2>/dev/null | head -1)
    echo -e "${GREEN}✅ Config file found: $CONFIG_FILE${NC}"
    
    # Check config contents
    if grep -q "testEnvironment" "$CONFIG_FILE"; then
        echo -e "${GREEN}   ✓ testEnvironment configured${NC}"
    fi
    
    if grep -q "setupFilesAfterEnv" "$CONFIG_FILE"; then
        echo -e "${GREEN}   ✓ Setup files configured${NC}"
    else
        echo -e "${YELLOW}   ⚠ No setupFilesAfterEnv (for jest-dom, MSW, etc.)${NC}"
        ((WARNINGS++))
    fi
    
    if grep -q "coverageThreshold" "$CONFIG_FILE"; then
        echo -e "${GREEN}   ✓ Coverage thresholds set${NC}"
    else
        echo -e "${YELLOW}   ⚠ No coverage thresholds configured${NC}"
        ((WARNINGS++))
    fi
    
    if grep -q "moduleNameMapper" "$CONFIG_FILE"; then
        echo -e "${GREEN}   ✓ Module aliases configured${NC}"
    fi
elif grep -q '"jest"' package.json && grep -A 100 '"jest"' package.json | grep -q '"testEnvironment"'; then
    echo -e "${GREEN}✅ Jest configured in package.json${NC}"
else
    echo -e "${RED}❌ No Jest configuration found${NC}"
    echo "   Create jest.config.ts or add jest section to package.json"
    ((ERRORS++))
fi

# Check for setup file
if [ -f "jest.setup.ts" ] || [ -f "jest.setup.js" ] || [ -f "setupTests.ts" ]; then
    SETUP_FILE=$(ls jest.setup.* setupTests.* 2>/dev/null | head -1)
    echo -e "${GREEN}✅ Setup file found: $SETUP_FILE${NC}"
fi

echo ""
echo "🧪 Checking test files..."

# Count test files
TEST_COUNT=$(find . -name "*.test.ts" -o -name "*.test.tsx" -o -name "*.test.js" -o -name "*.spec.ts" 2>/dev/null | grep -v node_modules | wc -l)

if [ "$TEST_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ Found $TEST_COUNT test file(s)${NC}"
else
    echo -e "${YELLOW}⚠ No test files found${NC}"
    ((WARNINGS++))
fi

# Check __mocks__ directory
if [ -d "__mocks__" ] || find . -name "__mocks__" -type d 2>/dev/null | grep -q .; then
    echo -e "${GREEN}✅ Manual mocks directory found${NC}"
fi

echo ""
echo "📜 Checking npm scripts..."

# Check for test script
if grep -q '"test"' package.json; then
    TEST_SCRIPT=$(grep '"test"' package.json | head -1)
    if echo "$TEST_SCRIPT" | grep -q "jest"; then
        echo -e "${GREEN}✅ Test script uses Jest${NC}"
    fi
    
    if grep -q '"test:watch"' package.json; then
        echo -e "${GREEN}   ✓ Watch mode script available${NC}"
    fi
    
    if grep -q '"test:coverage"' package.json; then
        echo -e "${GREEN}   ✓ Coverage script available${NC}"
    fi
fi

# Check for CI configuration
echo ""
echo "🔄 Checking CI/CD..."

if [ -f ".github/workflows/test.yml" ] || grep -q "jest" .github/workflows/*.yml 2>/dev/null; then
    echo -e "${GREEN}✅ GitHub Actions test workflow found${NC}"
else
    echo -e "${YELLOW}⚠ No CI test configuration found${NC}"
    ((WARNINGS++))
fi

# Summary
echo ""
echo "====================="
echo "📊 Summary"
echo "====================="

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
