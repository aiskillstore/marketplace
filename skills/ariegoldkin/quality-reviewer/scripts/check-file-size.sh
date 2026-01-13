#!/bin/bash
# Check if files exceed 180 lines (code only, excludes blank lines and comments)

MAX_LINES=180
VIOLATIONS=0
FRONTEND_SRC="frontend/src"

echo "🔍 Checking file sizes (max: $MAX_LINES lines of code)..."
echo

# Check if frontend/src exists
if [ ! -d "$FRONTEND_SRC" ]; then
  echo "❌ Directory $FRONTEND_SRC not found"
  exit 1
fi

# Find all TypeScript files (excluding test files and UI library components)
while IFS= read -r file; do
  # Skip shadcn/ui library components (third-party generated code)
  if [[ "$file" == *"/shared/ui/"* ]]; then
    continue
  fi

  # Count non-blank, non-comment lines (excludes blank lines, //, /*, */, and * inside block comments)
  lines=$(grep -cv "^[[:space:]]*$\|^[[:space:]]*//\|^[[:space:]]*\*\|^[[:space:]]*/\*\|^[[:space:]]*\*/" "$file" 2>/dev/null || echo 0)

  # Handle potential multi-line output from grep
  lines=$(echo "$lines" | head -1)

  if [ "$lines" -gt "$MAX_LINES" ] 2>/dev/null; then
    echo "❌ $file: $lines lines (exceeds $MAX_LINES)"
    VIOLATIONS=$((VIOLATIONS + 1))
  fi
done < <(find "$FRONTEND_SRC" \( -name "*.tsx" -o -name "*.ts" \) ! -name "*.test.ts" ! -name "*.test.tsx" 2>/dev/null)

echo
if [ $VIOLATIONS -gt 0 ]; then
  echo "❌ Found $VIOLATIONS file(s) exceeding $MAX_LINES lines"
  echo ""
  echo "💡 Fix: Break large files into smaller modules"
  echo "   - Extract hooks to separate files"
  echo "   - Move types to types.ts"
  echo "   - Split complex components into sub-components"
  exit 1
else
  echo "✅ All files within size limit ($MAX_LINES lines)"
fi
