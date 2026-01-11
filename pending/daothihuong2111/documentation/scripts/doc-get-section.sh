#!/bin/bash
# doc-get-section.sh
# Extract a specific section from markdown file
# Usage: doc-get-section.sh <file> <section-heading>

set -e

FILE="$1"
SECTION="$2"

if [ -z "$FILE" ] || [ -z "$SECTION" ]; then
    echo "Usage: doc-get-section.sh <file> <section-heading>"
    echo "Example: doc-get-section.sh docs/screens/home/README.md 'Features'"
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo "Error: File not found: $FILE"
    exit 1
fi

# Find the section and extract until next same-level heading
awk -v section="$SECTION" '
BEGIN {
    printing = 0
    section_level = 0
}

# Match section heading (case insensitive, flexible spacing)
/^#+/ {
    # Get heading level
    match($0, /^#+/)
    current_level = RLENGTH

    # Get heading text (remove leading # and spaces)
    heading_text = $0
    sub(/^#+ */, "", heading_text)

    # Check if this is our section
    if (tolower(heading_text) == tolower(section)) {
        printing = 1
        section_level = current_level
        print $0
        next
    }

    # Stop if we hit a same or higher level heading after our section
    if (printing && current_level <= section_level) {
        exit
    }
}

# Print lines while in section
printing { print }
' "$FILE"
