#!/bin/bash
# Check cyclomatic complexity (max: 15)
# Updated for ESLint v9 flat config compatibility

echo "🔍 Checking code complexity (max: 15)..."
echo

# Navigate to frontend directory (where eslint.config.mjs is located)
cd frontend || { echo "❌ frontend directory not found"; exit 1; }

# Run ESLint with complexity rule only
# Note: --ext and --no-eslintrc are deprecated in ESLint v9
# Flat config auto-detects .ts/.tsx files
# Using default 'stylish' formatter (unix formatter requires separate package)
ESLINT_OUTPUT=$(npx eslint src --rule 'complexity: [error, 15]' 2>&1)
EXIT_CODE=$?

# Filter out npm notices and display output
echo "$ESLINT_OUTPUT" | grep -v "npm notice"

echo
if [ $EXIT_CODE -eq 0 ]; then
  echo "✅ All functions within complexity limit (≤15)"
else
  echo "❌ Complexity violations found"
  echo ""
  echo "💡 Fix: Reduce function complexity"
  echo "   - Extract conditional logic to separate functions"
  echo "   - Use early returns instead of nested ifs"
  echo "   - Replace switch statements with lookup objects"
  echo "   - Split functions with multiple responsibilities"
fi

exit $EXIT_CODE
