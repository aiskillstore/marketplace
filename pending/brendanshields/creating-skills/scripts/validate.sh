#!/bin/bash
# Validates a skill directory against best practices
# Usage: bash validate.sh /path/to/skill

SKILL_DIR="${1:-.}"
SKILL_FILE="$SKILL_DIR/SKILL.md"
ERRORS=0
WARNINGS=0

echo "Validating skill: $SKILL_DIR"
echo "================================"

# Check SKILL.md exists
if [ ! -f "$SKILL_FILE" ]; then
    echo "ERROR: SKILL.md not found"
    exit 1
fi

# Check frontmatter exists
if ! head -1 "$SKILL_FILE" | grep -q "^---$"; then
    echo "ERROR: Missing frontmatter (must start with ---)"
    ((ERRORS++))
fi

# Check name field
if ! grep -q "^name:" "$SKILL_FILE"; then
    echo "ERROR: Missing 'name' field in frontmatter"
    ((ERRORS++))
else
    NAME=$(grep "^name:" "$SKILL_FILE" | head -1 | sed 's/name: *//')

    # Check gerund format (ends in -ing or contains -ing-)
    if ! echo "$NAME" | grep -qE "ing(-|$)"; then
        echo "WARNING: Name '$NAME' should use gerund format (verb-ing)"
        ((WARNINGS++))
    fi

    # Check lowercase
    if echo "$NAME" | grep -q "[A-Z]"; then
        echo "ERROR: Name must be lowercase"
        ((ERRORS++))
    fi

    # Check length
    if [ ${#NAME} -gt 64 ]; then
        echo "ERROR: Name exceeds 64 characters"
        ((ERRORS++))
    fi

    # Check for reserved words
    if echo "$NAME" | grep -qiE "(anthropic|claude)"; then
        echo "ERROR: Name contains reserved word"
        ((ERRORS++))
    fi
fi

# Check description field
if ! grep -q "^description:" "$SKILL_FILE"; then
    echo "ERROR: Missing 'description' field in frontmatter"
    ((ERRORS++))
fi

# Check line count
LINES=$(wc -l < "$SKILL_FILE" | tr -d ' ')
if [ "$LINES" -gt 500 ]; then
    echo "ERROR: SKILL.md has $LINES lines (max 500)"
    ((ERRORS++))
elif [ "$LINES" -gt 300 ]; then
    echo "WARNING: SKILL.md has $LINES lines (recommend under 300)"
    ((WARNINGS++))
fi

# Check for Windows paths (exclude anti-pattern examples)
if grep -vE 'Avoid|Wrong|Windows paths' "$SKILL_FILE" | grep -qE '\\[a-zA-Z]'; then
    echo "ERROR: Found Windows-style paths (use forward slashes)"
    ((ERRORS++))
fi

# Check for first-person in description (only check actual description, not examples)
# Extract just the first description block (the skill's own description)
FIRST_DESC=$(awk '/^description:/{found=1} found{print; if(/^[a-z]/ && !/^description:/) exit}' "$SKILL_FILE" | head -5)
if echo "$FIRST_DESC" | grep -qiE "\b(I can|I will|I help)\b"; then
    echo "WARNING: Description should use third person, not first person"
    ((WARNINGS++))
fi

echo ""
echo "================================"
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"

if [ $ERRORS -gt 0 ]; then
    echo "FAILED: Fix errors before publishing"
    exit 1
else
    echo "PASSED"
    exit 0
fi
