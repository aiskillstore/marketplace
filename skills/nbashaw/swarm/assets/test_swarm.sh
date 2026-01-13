#!/bin/bash
# Test script for swarm.sh
# Tests all flags and basic functionality

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SWARM_SH="$SCRIPT_DIR/swarm.sh"
TEST_PLAN="/tmp/test_plan_$$.md"
TESTS_PASSED=0
TESTS_FAILED=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create a minimal test plan
cat > "$TEST_PLAN" <<'EOF'
# Test Plan

## Goal
Test plan for testing swarm.sh

## Log
No logs yet
EOF

cleanup() {
  rm -f "$TEST_PLAN"
  rm -f .context/.done-test_plan_*
}

trap cleanup EXIT

pass() {
  echo -e "${GREEN}✓${NC} $1"
  TESTS_PASSED=$((TESTS_PASSED + 1))
}

fail() {
  echo -e "${RED}✗${NC} $1"
  TESTS_FAILED=$((TESTS_FAILED + 1))
}

echo "════════════════════════════════════════"
echo "  Testing swarm.sh"
echo "════════════════════════════════════════"
echo ""

# Test 1: --help flag
echo "Test 1: --help flag prints usage and exits 0"
if OUTPUT=$("$SWARM_SH" --help 2>&1); then
  if echo "$OUTPUT" | grep -q "Usage:" && echo "$OUTPUT" | grep -q "\-\-codex" && echo "$OUTPUT" | grep -q "\-\-claude"; then
    pass "Test 1: --help works and shows --codex/--claude flags"
  else
    fail "Test 1: --help doesn't show usage or flags"
  fi
else
  fail "Test 1: --help exited with error"
fi
echo ""

# Test 2: --dry-run flag (defaults to codex)
echo "Test 2: --dry-run doesn't call agent and defaults to codex"
OUTPUT=$("$SWARM_SH" --dry-run "$TEST_PLAN" 2>&1 | head -20)
if echo "$OUTPUT" | grep -q "\[DRY-RUN\]"; then
  if echo "$OUTPUT" | grep -q "codex exec --full-auto"; then
    pass "Test 2: --dry-run shows [DRY-RUN] with codex command"
  else
    fail "Test 2: --dry-run doesn't default to codex"
  fi
else
  fail "Test 2: --dry-run doesn't show [DRY-RUN] message"
fi
echo ""

# Test 2b: --claude flag
echo "Test 2b: --claude flag uses claude CLI"
OUTPUT=$("$SWARM_SH" --dry-run --claude "$TEST_PLAN" 2>&1 | head -20)
if echo "$OUTPUT" | grep -q "claude --dangerously-skip-permissions"; then
  pass "Test 2b: --claude uses claude CLI"
else
  fail "Test 2b: --claude doesn't use claude CLI"
fi
echo ""

# Test 2c: --codex flag (explicit)
echo "Test 2c: --codex flag uses codex CLI"
OUTPUT=$("$SWARM_SH" --dry-run --codex "$TEST_PLAN" 2>&1 | head -20)
if echo "$OUTPUT" | grep -q "codex exec --full-auto"; then
  pass "Test 2c: --codex uses codex CLI"
else
  fail "Test 2c: --codex doesn't use codex CLI"
fi
echo ""

# Test 3: --verbose with --dry-run
echo "Test 3: --verbose shows plan summary and timing"
OUTPUT=$("$SWARM_SH" --verbose --dry-run "$TEST_PLAN" 2>&1 | head -40)
if echo "$OUTPUT" | grep -q "Plan Summary"; then
  if echo "$OUTPUT" | grep -q "completed in"; then
    pass "Test 3: --verbose shows plan summary and timing"
  else
    fail "Test 3: --verbose doesn't show timing"
  fi
else
  fail "Test 3: --verbose doesn't show plan summary"
fi
echo ""

# Test 4: Missing plan file error
echo "Test 4: Missing plan file shows error"
if OUTPUT=$("$SWARM_SH" /nonexistent/file.md 2>&1); then
  fail "Test 4: Should have failed for missing file"
else
  if echo "$OUTPUT" | grep -q "Error.*not found"; then
    pass "Test 4: Shows error for missing file"
  else
    fail "Test 4: Wrong error message for missing file"
  fi
fi
echo ""

# Test 5: Run shellcheck if available
echo "Test 5: Run shellcheck"
if command -v shellcheck &> /dev/null; then
  if shellcheck "$SWARM_SH"; then
    pass "Test 5: shellcheck reports no errors"
  else
    fail "Test 5: shellcheck found errors"
  fi
else
  echo -e "${YELLOW}⊘${NC} Test 5: shellcheck not installed (skipped)"
fi
echo ""

# Summary
echo "════════════════════════════════════════"
echo "  Test Summary"
echo "════════════════════════════════════════"
echo -e "${GREEN}Passed:${NC} $TESTS_PASSED"
if [ $TESTS_FAILED -gt 0 ]; then
  echo -e "${RED}Failed:${NC} $TESTS_FAILED"
  exit 1
else
  echo -e "${GREEN}All tests passed!${NC}"
  exit 0
fi
