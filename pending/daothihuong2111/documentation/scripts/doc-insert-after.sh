#!/bin/bash
# doc-insert-after.sh
# Insert content after a specific section in markdown file
# Usage: doc-insert-after.sh <file> <section-heading> <new-content-file>

set -e

FILE="$1"
SECTION="$2"
CONTENT_FILE="$3"

if [ -z "$FILE" ] || [ -z "$SECTION" ] || [ -z "$CONTENT_FILE" ]; then
    echo "Usage: doc-insert-after.sh <file> <section-heading> <new-content-file>"
    echo "Example: doc-insert-after.sh docs/screens/home/README.md 'Features' new-section.md"
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

# Process file
awk -v section="$SECTION" -v content_file="$CONTENT_FILE" '
BEGIN {
    in_section = 0
    section_level = 0
    section_found = 0
}

/^#+/ {
    match($0, /^#+/)
    current_level = RLENGTH
    heading_text = $0
    sub(/^#+ */, "", heading_text)

    # Found target section
    if (tolower(heading_text) == tolower(section)) {
        in_section = 1
        section_level = current_level
        section_found = 1
    }

    # End of target section - insert content here
    if (in_section && section_found && current_level <= section_level) {
        # Insert new content
        while ((getline line < content_file) > 0) {
            print line
        }
        close(content_file)
        print ""  # Add blank line
        in_section = 0
        section_found = 0
    }
}

{ print }

END {
    # If section was last, insert at end
    if (section_found && in_section) {
        while ((getline line < content_file) > 0) {
            print line
        }
        close(content_file)
    }
}
' "$FILE" > "$TEMP_FILE"

# Replace original file
mv "$TEMP_FILE" "$FILE"

echo "Content inserted after section '$SECTION' in $FILE"
