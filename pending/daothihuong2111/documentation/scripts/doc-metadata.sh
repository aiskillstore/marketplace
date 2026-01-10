#!/bin/bash
# doc-metadata.sh
# Get metadata about a documentation file
# Usage: doc-metadata.sh <file>

set -e

FILE="$1"

if [ -z "$FILE" ]; then
    echo "Usage: doc-metadata.sh <file>"
    echo "Example: doc-metadata.sh docs/screens/home/README.md"
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo "Error: File not found: $FILE"
    exit 1
fi

# Get metadata
LINES=$(wc -l < "$FILE")
SECTIONS=$(grep -c "^##" "$FILE" 2>/dev/null || echo 0)
H2_COUNT=$(grep -c "^## " "$FILE" 2>/dev/null || echo 0)
H3_COUNT=$(grep -c "^### " "$FILE" 2>/dev/null || echo 0)
CODE_BLOCKS=$(grep -c "^\`\`\`" "$FILE" 2>/dev/null || echo 0)
CODE_BLOCKS=$((CODE_BLOCKS / 2))  # Divide by 2 (opening + closing)
LINKS=$(grep -o "\[.*\](.*)" "$FILE" 2>/dev/null | wc -l)
LAST_MODIFIED=$(stat -c %y "$FILE" 2>/dev/null | cut -d' ' -f1)

# Calculate size status
if [ "$LINES" -gt 500 ]; then
    SIZE_STATUS=" TOO LARGE (>500 lines)"
elif [ "$LINES" -gt 450 ]; then
    SIZE_STATUS="⚠️  APPROACHING LIMIT (>450 lines)"
elif [ "$LINES" -gt 400 ]; then
    SIZE_STATUS="⚡ LARGE (>400 lines)"
else
    SIZE_STATUS="✅ OK (<400 lines)"
fi

# Output metadata
echo "File: $FILE"
echo "----------------------------------------"
echo "Lines: $LINES"
echo "Size Status: $SIZE_STATUS"
echo "H2 Sections: $H2_COUNT"
echo "H3 Subsections: $H3_COUNT"
echo "Code Blocks: $CODE_BLOCKS"
echo "Links: $LINKS"
echo "Last Modified: $LAST_MODIFIED"
echo ""
echo "Top-level sections:"
grep "^## " "$FILE" 2>/dev/null | sed 's/^## /  - /' || echo "  (none)"
