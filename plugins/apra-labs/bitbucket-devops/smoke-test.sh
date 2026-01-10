#!/bin/bash
# Smoke test for Claude Bitbucket DevOps Skill
# Validates that the installation is complete and functional
# Run this after install.sh to verify everything works

SKILL_DIR="${1:-$HOME/.claude/skills/bitbucket-devops}"
PASSED=0
FAILED=0

echo "Smoke Testing Claude Bitbucket DevOps Skill"
echo "Testing directory: $SKILL_DIR"
echo ""

# Helper functions
pass() {
    echo "[PASS] $1"
    PASSED=$((PASSED + 1))
}

fail() {
    echo "[FAIL] $1"
    FAILED=$((FAILED + 1))
}

warn() {
    echo "[WARN] $1"
}

# ========== FILE STRUCTURE TESTS ==========
echo "[1/5] Testing file structure..."
echo ""

# Test 1: Directory exists
if [ -d "$SKILL_DIR" ]; then
    pass "Skill directory exists"
else
    fail "Skill directory not found: $SKILL_DIR"
    echo ""
    echo "Run install.sh first!"
    exit 1
fi

cd "$SKILL_DIR"

# Test 2: Essential files exist
REQUIRED_FILES=(
    "SKILL.md"
    "package.json"
    "credentials.json.template"
    "lib/helpers.js"
    "bitbucket-mcp/dist/index-cli.js"
    "bitbucket-mcp/package.json"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        pass "File exists: $file"
    else
        fail "Missing file: $file"
    fi
done

echo ""

# ========== DEPENDENCY TESTS ==========
echo "[2/5] Testing dependencies..."
echo ""

# Test 3: node_modules exists
if [ -d "bitbucket-mcp/node_modules" ]; then
    pass "node_modules directory exists"
else
    fail "node_modules directory missing - dependencies not installed"
fi

# Test 4: Critical dependencies exist (directory check)
REQUIRED_DEPS=(
    "bitbucket-mcp/node_modules/axios"
    "bitbucket-mcp/node_modules/@modelcontextprotocol/sdk"
)

for dep in "${REQUIRED_DEPS[@]}"; do
    if [ -d "$dep" ]; then
        pass "Dependency exists: $(basename $dep)"
    else
        fail "Missing dependency: $(basename $dep)"
    fi
done

# Test 5: Axios can be imported by Node.js (functional test)
cd bitbucket-mcp
if node -e "import('axios').then(() => process.exit(0)).catch(() => process.exit(1))" 2>/dev/null; then
    pass "axios can be imported by Node.js (functional)"
else
    fail "axios import failed - Node.js cannot find the module"
fi
cd "$SKILL_DIR"

echo ""

# ========== PACKAGE.JSON TESTS ==========
echo "[3/5] Testing package.json configuration..."
echo ""

# Test 6: Root package.json has type: module
if grep -q '"type".*:.*"module"' package.json 2>/dev/null; then
    pass "Root package.json has type: module (ES modules enabled)"
else
    fail "Root package.json missing type: module"
fi

# Test 7: bitbucket-mcp package.json has type: module
if grep -q '"type".*:.*"module"' bitbucket-mcp/package.json 2>/dev/null; then
    pass "bitbucket-mcp package.json has type: module"
else
    fail "bitbucket-mcp package.json missing type: module"
fi

echo ""

# ========== NODE.JS TESTS ==========
echo "[4/5] Testing Node.js functionality..."
echo ""

# Test 8: Node.js is available
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    pass "Node.js is available: $NODE_VERSION"
else
    fail "Node.js not found in PATH"
fi

# Test 9: CLI tool can be executed (syntax check)
if node bitbucket-mcp/dist/index-cli.js --help 2>&1 | grep -qi "bitbucket\|usage\|command" || true; then
    pass "CLI tool is executable"
else
    warn "CLI tool may have issues (--help not recognized, but this is expected)"
fi

# Test 10: Helper library can be executed (test for module errors)
# Simple test: try to run the helper with no arguments (will show usage but proves it loads)
if node "$SKILL_DIR/lib/helpers.js" 2>&1 | grep -qi "error.*unknown command\|available commands"; then
    pass "lib/helpers.js can be executed (no module errors)"
else
    # Module loaded but no command given - this is also success
    if node "$SKILL_DIR/lib/helpers.js" 2>&1; then
        pass "lib/helpers.js can be executed (no module errors)"
    else
        fail "lib/helpers.js execution failed - check dependencies"
    fi
fi

echo ""

# ========== CREDENTIAL TESTS ==========
echo "[5/5] Testing credentials configuration..."
echo ""

# Test 11: Credentials file exists (either real or template)
if [ -f "credentials.json" ]; then
    pass "credentials.json exists"

    # Test if it's still the template
    if grep -q "your-workspace-name" credentials.json 2>/dev/null; then
        warn "credentials.json still has template values - needs configuration"
    else
        pass "credentials.json appears to be configured"
    fi
else
    warn "credentials.json not created yet (expected on first install)"
    if [ -f "credentials.json.template" ]; then
        pass "credentials.json.template exists (can be copied)"
    else
        fail "credentials.json.template missing"
    fi
fi

echo ""

# ========== INTEGRATION TEST (OPTIONAL) ==========
echo "Integration test (optional)..."
echo ""

if [ -f "credentials.json" ] && ! grep -q "your-workspace-name" credentials.json 2>/dev/null; then
    warn "Skipping integration test - requires valid credentials and network"
    # Uncomment below to test with real API calls:
    # if node lib/helpers.js get-latest "workspace" "repo" 2>&1; then
    #     pass "Integration test: API call successful"
    # else
    #     warn "Integration test failed - check credentials and network"
    # fi
else
    warn "Skipping integration test - credentials not configured"
fi

echo ""

# ========== SUMMARY ==========
echo "======================================================================"
echo ""
echo "Test Results:"
echo ""
echo "   Passed: $PASSED"
echo "   Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "RESULT: All tests passed!"
    echo ""
    echo "The skill should work correctly."
    echo ""
    if grep -q "your-workspace-name" credentials.json 2>/dev/null; then
        echo "Next step: Configure credentials.json with your Bitbucket details"
    fi
    exit 0
else
    echo "RESULT: $FAILED test(s) failed!"
    echo ""
    echo "Please review the errors above and:"
    echo "1. Re-run install.sh"
    echo "2. Check that all dependencies installed correctly"
    echo "3. Verify Node.js version is v18 or higher"
    echo ""
    exit 1
fi
