#!/bin/bash
# Check naming conventions (interfaces must have 'I' prefix)

echo "🔍 Checking naming conventions..."
echo

VIOLATIONS=0
FRONTEND_SRC="frontend/src"

if [ ! -d "$FRONTEND_SRC" ]; then
  echo "❌ Directory $FRONTEND_SRC not found"
  exit 1
fi

# Check for interfaces without 'I' prefix
while IFS= read -r file; do
  # Find interface declarations without 'I' prefix
  # Match patterns like: "interface Foo" or "export interface Foo"
  if grep -Eq "^[[:space:]]*(export[[:space:]]+)?interface[[:space:]]+[a-z][A-Za-z]*" "$file"; then
    echo "❌ $file: Interface without 'I' prefix"
    grep -En "^[[:space:]]*(export[[:space:]]+)?interface[[:space:]]+[a-z][A-Za-z]*" "$file" | head -3
    VIOLATIONS=$((VIOLATIONS + 1))
  fi
done < <(find "$FRONTEND_SRC" \( -name "*.tsx" -o -name "*.ts" \) 2>/dev/null)

echo
if [ $VIOLATIONS -gt 0 ]; then
  echo "❌ Found $VIOLATIONS naming violation(s)"
  echo ""
  echo "💡 Naming Conventions:"
  echo "   Interfaces: IUserProfile, IButtonProps, IQuestionData"
  echo "   Types:      QuestionType, Difficulty, SeniorityLevel"
  echo "   Functions:  camelCase (getUserProfile, validateEmail)"
  echo "   Components: PascalCase (Button, PracticeWizard)"
  echo "   Files:      PascalCase.tsx (components), camelCase.ts (utils)"
  exit 1
else
  echo "✅ Naming conventions followed"
fi
