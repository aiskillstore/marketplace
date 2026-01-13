#!/usr/bin/env bash
# Bisection script to find which test creates unwanted files/state
# 
# Requirements: bash, find, npm with `npm test <file>` support
#
# Usage: ./find-polluter.sh <file_or_dir_to_check> <test_directory>
# Example: ./find-polluter.sh '.git' './src'

set -e

if [ $# -ne 2 ]; then
  echo "Usage: $0 <file_to_check> <test_directory>"
  echo "Example: $0 '.git' './src'"
  exit 1
fi

POLLUTION_CHECK="$1"
TEST_DIR="$2"

echo "🔍 Searching for test that creates: $POLLUTION_CHECK"
echo "Test directory: $TEST_DIR"
echo ""

# Get list of test files
TEST_FILES=$(find "$TEST_DIR" -name '*.test.ts' -o -name '*.test.js' -o -name '*.spec.ts' -o -name '*.spec.js' | sort)

# Check if any test files found
if [ -z "$TEST_FILES" ]; then
  echo "❌ No test files found in: $TEST_DIR"
  echo "   Looking for: *.test.ts, *.test.js, *.spec.ts, *.spec.js"
  exit 1
fi

TOTAL=$(echo "$TEST_FILES" | grep -c . || echo 0)

echo "Found $TOTAL test files"
echo ""

COUNT=0
for TEST_FILE in $TEST_FILES; do
  COUNT=$((COUNT + 1))

  # Skip if pollution already exists
  if [ -e "$POLLUTION_CHECK" ]; then
    echo "⚠️  Pollution already exists before test $COUNT/$TOTAL"
    echo "   Skipping: $TEST_FILE"
    continue
  fi

  echo "[$COUNT/$TOTAL] Testing: $TEST_FILE"

  # Run the test
  npm test "$TEST_FILE" > /dev/null 2>&1 || true

  # Check if pollution appeared
  if [ -e "$POLLUTION_CHECK" ]; then
    echo ""
    echo "🎯 FOUND POLLUTER!"
    echo "   Test: $TEST_FILE"
    echo "   Created: $POLLUTION_CHECK"
    echo ""
    echo "Pollution details:"
    ls -la "$POLLUTION_CHECK"
    echo ""
    echo "To investigate:"
    echo "  npm test $TEST_FILE    # Run just this test"
    echo "  cat $TEST_FILE         # Review test code"
    exit 1
  fi
done

echo ""
echo "✅ No polluter found - all tests clean!"
exit 0
