#!/bin/bash
# Test Quality Metrics Calculator
# Calculates basic test quality metrics for a project

set -e

echo "📊 Test Quality Metrics Calculator"
echo "==================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Initialize counters
TOTAL_TESTS=0
TEST_FILES=0
SOURCE_FILES=0
SOURCE_LINES=0
TEST_LINES=0

echo "🔍 Analyzing codebase..."
echo ""

# Count test files
TEST_FILES=$(find . -name "*.test.ts" -o -name "*.test.tsx" -o -name "*.test.js" -o -name "*.spec.ts" -o -name "*.spec.tsx" 2>/dev/null | grep -v node_modules | wc -l)

# Count source files (excluding tests and node_modules)
SOURCE_FILES=$(find . -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" 2>/dev/null | grep -v node_modules | grep -v ".test." | grep -v ".spec." | grep -v "__tests__" | wc -l)

# Count test lines
if [ "$TEST_FILES" -gt 0 ]; then
    TEST_LINES=$(find . \( -name "*.test.ts" -o -name "*.test.tsx" -o -name "*.test.js" -o -name "*.spec.ts" \) ! -path "*/node_modules/*" -exec cat {} \; 2>/dev/null | wc -l)
fi

# Count source lines
if [ "$SOURCE_FILES" -gt 0 ]; then
    SOURCE_LINES=$(find . \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) ! -path "*/node_modules/*" ! -name "*.test.*" ! -name "*.spec.*" ! -path "*/__tests__/*" -exec cat {} \; 2>/dev/null | wc -l)
fi

# Count individual tests (it/test blocks)
if [ "$TEST_FILES" -gt 0 ]; then
    TOTAL_TESTS=$(find . \( -name "*.test.ts" -o -name "*.test.tsx" -o -name "*.test.js" -o -name "*.spec.ts" \) ! -path "*/node_modules/*" -exec grep -h "^\s*\(it\|test\)(" {} \; 2>/dev/null | wc -l)
fi

# Calculate ratios
if [ "$SOURCE_FILES" -gt 0 ]; then
    TEST_FILE_RATIO=$(echo "scale=2; $TEST_FILES / $SOURCE_FILES" | bc)
else
    TEST_FILE_RATIO="N/A"
fi

if [ "$SOURCE_LINES" -gt 0 ]; then
    TEST_LINE_RATIO=$(echo "scale=2; $TEST_LINES / $SOURCE_LINES" | bc)
else
    TEST_LINE_RATIO="N/A"
fi

# Output results
echo "📈 Test Metrics"
echo "==============="
echo ""
printf "%-25s %s\n" "Test Files:" "$TEST_FILES"
printf "%-25s %s\n" "Source Files:" "$SOURCE_FILES"
printf "%-25s %s\n" "Test File Ratio:" "$TEST_FILE_RATIO"
echo ""
printf "%-25s %s\n" "Test Lines:" "$TEST_LINES"
printf "%-25s %s\n" "Source Lines:" "$SOURCE_LINES"
printf "%-25s %s\n" "Test Line Ratio:" "$TEST_LINE_RATIO"
echo ""
printf "%-25s %s\n" "Total Tests:" "$TOTAL_TESTS"

# Check for describe blocks
DESCRIBE_BLOCKS=$(find . \( -name "*.test.ts" -o -name "*.test.tsx" -o -name "*.test.js" -o -name "*.spec.ts" \) ! -path "*/node_modules/*" -exec grep -h "^\s*describe(" {} \; 2>/dev/null | wc -l)
printf "%-25s %s\n" "Describe Blocks:" "$DESCRIBE_BLOCKS"

echo ""
echo "📊 Quality Indicators"
echo "====================="
echo ""

# Evaluate test file ratio
if [ "$TEST_FILE_RATIO" != "N/A" ]; then
    if (( $(echo "$TEST_FILE_RATIO >= 0.8" | bc -l) )); then
        echo -e "Test File Ratio: ${GREEN}✅ Good ($TEST_FILE_RATIO)${NC}"
    elif (( $(echo "$TEST_FILE_RATIO >= 0.5" | bc -l) )); then
        echo -e "Test File Ratio: ${YELLOW}⚠️ Acceptable ($TEST_FILE_RATIO)${NC}"
    else
        echo -e "Test File Ratio: ${RED}❌ Low ($TEST_FILE_RATIO)${NC}"
    fi
fi

# Check for common patterns
echo ""
echo "🔍 Pattern Analysis"
echo "==================="
echo ""

# Check for beforeEach usage
BEFORE_EACH=$(find . \( -name "*.test.ts" -o -name "*.test.tsx" -o -name "*.test.js" \) ! -path "*/node_modules/*" -exec grep -l "beforeEach" {} \; 2>/dev/null | wc -l)
if [ "$BEFORE_EACH" -gt 0 ]; then
    echo -e "${GREEN}✅ Setup hooks used ($BEFORE_EACH files)${NC}"
else
    echo -e "${YELLOW}⚠️ No beforeEach hooks found${NC}"
fi

# Check for mocking
MOCKS=$(find . \( -name "*.test.ts" -o -name "*.test.tsx" -o -name "*.test.js" \) ! -path "*/node_modules/*" -exec grep -l "jest.mock\|vi.mock" {} \; 2>/dev/null | wc -l)
if [ "$MOCKS" -gt 0 ]; then
    echo -e "${GREEN}✅ Mocking used ($MOCKS files)${NC}"
fi

# Check for async tests
ASYNC_TESTS=$(find . \( -name "*.test.ts" -o -name "*.test.tsx" -o -name "*.test.js" \) ! -path "*/node_modules/*" -exec grep -l "async\|await\|resolves\|rejects" {} \; 2>/dev/null | wc -l)
if [ "$ASYNC_TESTS" -gt 0 ]; then
    echo -e "${GREEN}✅ Async testing used ($ASYNC_TESTS files)${NC}"
fi

# Check for potential issues
echo ""
echo "⚠️ Potential Issues"
echo "==================="
echo ""

# Check for setTimeout in tests (potential flaky test)
TIMEOUTS=$(find . \( -name "*.test.ts" -o -name "*.test.tsx" -o -name "*.test.js" \) ! -path "*/node_modules/*" -exec grep -l "setTimeout" {} \; 2>/dev/null | wc -l)
if [ "$TIMEOUTS" -gt 0 ]; then
    echo -e "${YELLOW}⚠️ setTimeout found in $TIMEOUTS test file(s) - potential flakiness${NC}"
fi

# Check for .only (forgotten focus)
ONLY=$(find . \( -name "*.test.ts" -o -name "*.test.tsx" -o -name "*.test.js" \) ! -path "*/node_modules/*" -exec grep -l "\.only\|fdescribe\|fit" {} \; 2>/dev/null | wc -l)
if [ "$ONLY" -gt 0 ]; then
    echo -e "${RED}❌ .only found in $ONLY file(s) - tests may be skipped${NC}"
fi

# Check for .skip
SKIP=$(find . \( -name "*.test.ts" -o -name "*.test.tsx" -o -name "*.test.js" \) ! -path "*/node_modules/*" -exec grep -l "\.skip\|xdescribe\|xit" {} \; 2>/dev/null | wc -l)
if [ "$SKIP" -gt 0 ]; then
    echo -e "${YELLOW}⚠️ .skip found in $SKIP file(s) - tests being skipped${NC}"
fi

echo ""
echo "==================================="
echo "Analysis complete!"
echo ""
echo "Run 'npm test -- --coverage' for detailed coverage metrics"
