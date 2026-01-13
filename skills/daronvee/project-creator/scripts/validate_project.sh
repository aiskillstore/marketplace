#!/bin/bash
# Validates that a CCGG Business Operations project has all required mechanisms

PROJECT_NAME="$1"

if [ -z "$PROJECT_NAME" ]; then
    echo "Usage: bash validate_project.sh <project-name>"
    exit 1
fi

PROJECT_PATH="Active Projects/_Incubator/$PROJECT_NAME"
INDEX_PATH="Project Memory/Active Projects Index/${PROJECT_NAME}-index.md"

echo "🔍 Validating project: $PROJECT_NAME"
echo ""

ERRORS=0
WARNINGS=0

# Check 1: Project folder exists
if [ ! -d "$PROJECT_PATH" ]; then
    echo "❌ ERROR: Project folder not found: $PROJECT_PATH"
    ((ERRORS++))
else
    echo "✅ Project folder exists"
fi

# Check 2: CLAUDE.md exists
if [ ! -f "$PROJECT_PATH/CLAUDE.md" ]; then
    echo "❌ ERROR: CLAUDE.md not found"
    ((ERRORS++))
else
    echo "✅ CLAUDE.md exists"

    # Check 2a: PARENT SYSTEM INTEGRATION section
    if ! grep -q "## PARENT SYSTEM INTEGRATION" "$PROJECT_PATH/CLAUDE.md"; then
        echo "❌ ERROR: PARENT SYSTEM INTEGRATION section missing in CLAUDE.md"
        ((ERRORS++))
    else
        echo "✅ PARENT SYSTEM INTEGRATION section present"

        # Check sub-sections
        if ! grep -q "### Project Memory Index Sync" "$PROJECT_PATH/CLAUDE.md"; then
            echo "⚠️  WARNING: Project Memory Index Sync sub-section missing"
            ((WARNINGS++))
        fi

        if ! grep -q "### Operations Logging" "$PROJECT_PATH/CLAUDE.md"; then
            echo "⚠️  WARNING: Operations Logging sub-section missing"
            ((WARNINGS++))
        fi

        if ! grep -q "### Strategic Alignment Validation" "$PROJECT_PATH/CLAUDE.md"; then
            echo "⚠️  WARNING: Strategic Alignment Validation sub-section missing"
            ((WARNINGS++))
        fi

        if ! grep -q "### Cross-Project Intelligence" "$PROJECT_PATH/CLAUDE.md"; then
            echo "⚠️  WARNING: Cross-Project Intelligence sub-section missing"
            ((WARNINGS++))
        fi
    fi

    # Check 2b: Template variables replaced
    if grep -q "{{" "$PROJECT_PATH/CLAUDE.md"; then
        echo "⚠️  WARNING: Template variables not replaced ({{ found)"
        ((WARNINGS++))
    fi
fi

# Check 3: README.md exists
if [ ! -f "$PROJECT_PATH/README.md" ]; then
    echo "⚠️  WARNING: README.md not found"
    ((WARNINGS++))
else
    echo "✅ README.md exists"
fi

# Check 4: Active Projects Index exists
if [ ! -f "$INDEX_PATH" ]; then
    echo "❌ ERROR: Active Projects Index not found: $INDEX_PATH"
    ((ERRORS++))
else
    echo "✅ Active Projects Index exists"

    # Check YAML frontmatter
    if ! grep -q "^---$" "$INDEX_PATH"; then
        echo "⚠️  WARNING: YAML frontmatter missing in index"
        ((WARNINGS++))
    fi

    if ! grep -q "strategic_alignment:" "$INDEX_PATH"; then
        echo "⚠️  WARNING: strategic_alignment missing in index"
        ((WARNINGS++))
    fi
fi

# Check 5: Operations log entry
if ! grep -q "$PROJECT_NAME" "operations_log.txt"; then
    echo "⚠️  WARNING: No operations_log.txt entry found for $PROJECT_NAME"
    ((WARNINGS++))
else
    echo "✅ Operations log entry exists"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Validation Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ Project validation PASSED"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "⚠️  Project validation passed with warnings"
    exit 0
else
    echo "❌ Project validation FAILED"
    exit 1
fi
