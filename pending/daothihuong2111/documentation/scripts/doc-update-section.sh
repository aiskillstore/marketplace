#!/bin/bash
# doc-update-section.sh
# Update a specific section in markdown file
# Usage: doc-update-section.sh <file> <section-heading> <new-content-file>

set -e

FILE="$1"
SECTION="$2"
CONTENT_FILE="$3"

if [ -z "$FILE" ] || [ -z "$SECTION" ] || [ -z "$CONTENT_FILE" ]; then
    echo "Usage: doc-update-section.sh <file> <section-heading> <new-content-file>"
    echo "Example: doc-update-section.sh docs/screens/home/README.md 'Features' new-features.md"
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo "Error: File not found: $FILE"
    exit 1
fi

if [ ! -f "$CONTENT_FILE" ]; then
    echo "Error: Content file not found: $CONTENT_FILE"
    exit 1
fi

TEMP_FILE=$(mktemp)

# Extract everything before section
awk -v section="$SECTION" '
/^#+/ {
    match($0, /^#+/)
    current_level = RLENGTH
    heading_text = $0
    sub(/^#+ */, "", heading_text)

    if (tolower(heading_text) == tolower(section)) {
        section_found = 1
        section_level = current_level
        exit
    }
}
!section_found { print }
' "$FILE" > "$TEMP_FILE"

# Add new content
cat "$CONTENT_FILE" >> "$TEMP_FILE"

# Extract everything after section
awk -v section="$SECTION" '
BEGIN { section_found = 0; after_section = 0 }

/^#+/ {
    if (section_found && !after_section) {
        match($0, /^#+/)
        current_level = RLENGTH
        if (current_level <= section_level) {
            after_section = 1
        }
    }

    if (!section_found) {
        match($0, /^#+/)
        current_level = RLENGTH
        heading_text = $0
        sub(/^#+ */, "", heading_text)

        if (tolower(heading_text) == tolower(section)) {
            section_found = 1
            section_level = current_level
        }
    }
}

after_section { print }
' "$FILE" >> "$TEMP_FILE"

# Replace original file
mv "$TEMP_FILE" "$FILE"

echo "Section '$SECTION' updated in $FILE"
