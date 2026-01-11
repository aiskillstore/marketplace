#!/bin/bash
# doc-find-duplicates.sh
# Find duplicate content across documentation files
# Usage: doc-find-duplicates.sh [directory]

set -e

DIR="${1:-docs}"

if [ ! -d "$DIR" ]; then
    echo "Error: Directory not found: $DIR"
    exit 1
fi

echo "Searching for duplicate content in $DIR..."
echo ""

# Find all H2 headings and check for duplicates
echo "=== Duplicate Section Headings ==="
grep -rh "^## " "$DIR" --include="*.md" 2>/dev/null | sort | uniq -d || echo "(none)"

echo ""
echo "=== Files with Similar Content (>80% match) ==="

# Create temp directory
TEMP_DIR=$(mktemp -d)

# Get all markdown files
find "$DIR" -name "*.md" -type f > "$TEMP_DIR/files.txt"

# Check each pair of files
while IFS= read -r file1; do
    while IFS= read -r file2; do
        if [ "$file1" \< "$file2" ]; then
            # Count common lines
            comm -12 <(sort "$file1") <(sort "$file2") > "$TEMP_DIR/common.txt"
            common_lines=$(wc -l < "$TEMP_DIR/common.txt")
            file1_lines=$(wc -l < "$file1")

            # Calculate similarity percentage
            if [ "$file1_lines" -gt 0 ]; then
                similarity=$((common_lines * 100 / file1_lines))

                if [ "$similarity" -gt 80 ]; then
                    echo "$file1 <-> $file2: ${similarity}% similar"
                fi
            fi
        fi
    done < "$TEMP_DIR/files.txt"
done < "$TEMP_DIR/files.txt"

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "=== Duplicate Code Blocks ==="
# Extract code blocks and find duplicates
grep -rh "^\`\`\`" -A 10 "$DIR" --include="*.md" 2>/dev/null | grep -v "^\`\`\`" | sort | uniq -d | head -5 || echo "(none)"
