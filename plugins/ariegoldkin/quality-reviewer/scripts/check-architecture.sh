#!/bin/bash
# Verify files are in correct 6-folder structure

echo "🔍 Checking architecture compliance (6-folder structure)..."
echo

VIOLATIONS=0
FRONTEND_SRC="frontend/src"

if [ ! -d "$FRONTEND_SRC" ]; then
  echo "❌ Directory $FRONTEND_SRC not found"
  exit 1
fi

# Valid top-level directories in 6-folder structure
VALID_DIRS=("app" "modules" "shared" "lib" "store" "styles" "types")

# Check for files directly in src/ (should be in folders)
shopt -s nullglob
for file in "$FRONTEND_SRC"/*.ts "$FRONTEND_SRC"/*.tsx; do
  if [ -f "$file" ]; then
    echo "❌ $(basename "$file"): File directly in src/ (should use 6-folder structure)"
    VIOLATIONS=$((VIOLATIONS + 1))
  fi
done
shopt -u nullglob

# Check for invalid top-level directories
for dir in "$FRONTEND_SRC"/*/; do
  if [ -d "$dir" ]; then
    dirname=$(basename "$dir")

    # Check if directory is in valid list
    valid=0
    for valid_dir in "${VALID_DIRS[@]}"; do
      if [ "$dirname" = "$valid_dir" ]; then
        valid=1
        break
      fi
    done

    if [ $valid -eq 0 ]; then
      echo "❌ Invalid top-level directory: $dirname"
      echo "   Valid: ${VALID_DIRS[*]}"
      VIOLATIONS=$((VIOLATIONS + 1))
    fi
  fi
done

echo
if [ $VIOLATIONS -gt 0 ]; then
  echo "❌ Found $VIOLATIONS architecture violation(s)"
  echo ""
  echo "💡 6-Folder Structure:"
  echo "   app/     - Routes only (Next.js App Router)"
  echo "   modules/ - Feature logic (practice, assessment, results, profile, questions, home)"
  echo "   shared/  - Cross-cutting (ui, components, hooks, utils)"
  echo "   lib/     - External integrations (trpc, claude)"
  echo "   store/   - Zustand state management"
  echo "   styles/  - Design system (globals.css, glassmorphism.css)"
  exit 1
else
  echo "✅ Architecture follows 6-folder structure"
fi
