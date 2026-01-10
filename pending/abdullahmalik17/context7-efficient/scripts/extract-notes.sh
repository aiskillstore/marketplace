#!/bin/bash
# Extract important notes and warnings using grep
# Filters for key informational content

set -euo pipefail

MAX_NOTES="${1:-3}"

# Use grep to find lines with important keywords
grep -iE '(important|note:|warning:|caution:|tip:|remember:|must|should not|deprecated|breaking change)' | \
  head -n "$MAX_NOTES" | \
  sed 's/^/- /' || echo "- No important notes found"
