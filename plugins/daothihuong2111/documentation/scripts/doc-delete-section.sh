#!/bin/bash
# doc-delete-section.sh
# Delete a specific section from markdown file
# Usage: doc-delete-section.sh <file> <section-heading>

set -e

FILE="$1"
SECTION="$2"

if [ -z "$FILE" ] || [ -z "$SECTION" ]; then
    echo "Usage: doc-delete-section.sh <file> <section-heading>"
    echo "Example: doc-delete-section.sh docs/screens/home/README.md 'Old Feature'"
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo "Error: File not found: $FILE"
    exit 1
fi

TEMP_FILE=$(mktemp)

# Keep everything except the target section
awk -v section="$SECTION" '
BEGIN {
    in_section = 0
    section_level = 0
}

/^#+/ {
    match($0, /^#+/)
    current_level = RLENGTH
    heading_text = $0
    sub(/^#+ */, "", heading_text)

    # Entering target section
    if (tolower(heading_text) == tolower(section)) {
        in_section = 1
        section_level = current_level
        next
    }

    # Exiting target section
    if (in_section && current_level <= section_level) {
        in_section = 0
    }
}

# Print lines not in target section
!in_section { print }
' "$FILE" > "$TEMP_FILE"

# Replace original file
mv "$TEMP_FILE" "$FILE"

echo "Section '$SECTION' deleted from $FILE"
