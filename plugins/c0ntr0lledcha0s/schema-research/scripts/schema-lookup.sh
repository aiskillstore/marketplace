#!/bin/bash
# Schema.org Quick Lookup Script
# Opens Schema.org page for a class or property in the browser

usage() {
    echo "Usage: $0 <ClassName|propertyName>"
    echo ""
    echo "Examples:"
    echo "  $0 Person"
    echo "  $0 Recipe"
    echo "  $0 birthDate"
    echo "  $0 worksFor"
    exit 1
}

if [ $# -eq 0 ]; then
    usage
fi

TERM=$1
URL="https://schema.org/$TERM"

echo "Opening Schema.org page for: $TERM"
echo "URL: $URL"

# Open in default browser (cross-platform)
if command -v xdg-open &> /dev/null; then
    # Linux
    xdg-open "$URL"
elif command -v open &> /dev/null; then
    # macOS
    open "$URL"
elif command -v start &> /dev/null; then
    # Windows (Git Bash)
    start "$URL"
else
    echo "Could not detect browser opener. Please visit manually:"
    echo "$URL"
fi
