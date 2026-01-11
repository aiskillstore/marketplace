#!/bin/bash
# doc-search.sh
# Search for content in documentation without reading entire files
# Usage: doc-search.sh <pattern> [directory]

set -e

PATTERN="$1"
DIR="${2:-docs}"

if [ -z "$PATTERN" ]; then
    echo "Usage: doc-search.sh <pattern> [directory]"
    echo "Example: doc-search.sh 'slash command' docs/screens/home"
    exit 1
fi

# Search with context showing
grep -rn --include="*.md" -C 2 "$PATTERN" "$DIR" 2>/dev/null || {
    echo "No matches found for: $PATTERN"
    exit 0
}
