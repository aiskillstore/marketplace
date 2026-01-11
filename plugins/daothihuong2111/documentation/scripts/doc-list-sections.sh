#!/bin/bash
# doc-list-sections.sh
# List all sections (headings) in a markdown file
# Usage: doc-list-sections.sh <file>

set -e

FILE="$1"

if [ -z "$FILE" ]; then
    echo "Usage: doc-list-sections.sh <file>"
    echo "Example: doc-list-sections.sh docs/screens/home/README.md"
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo "Error: File not found: $FILE"
    exit 1
fi

# Extract all markdown headings with line numbers
grep -n "^#" "$FILE" | while IFS=: read -r line_num heading; do
    # Count heading level
    level=$(echo "$heading" | grep -o "^#*" | wc -c)
    level=$((level - 1))

    # Get heading text
    text=$(echo "$heading" | sed 's/^#* *//')

    # Indent based on level
    indent=$(printf '%*s' $((level * 2)) '')

    echo "${indent}${text} (line ${line_num})"
done
