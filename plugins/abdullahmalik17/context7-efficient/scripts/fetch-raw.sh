#!/bin/bash
# Fetch raw documentation from Context7 MCP
# Output: JSON response (stays in shell, doesn't enter Claude context)

set -euo pipefail

LIBRARY_ID="${1:?Error: Library ID required}"
TOPIC="${2:-}"
MODE="${3:-code}"
PAGE="${4:-1}"

# Build parameters JSON
PARAMS=$(cat <<JSON
{
  "context7CompatibleLibraryID": "$LIBRARY_ID",
  "mode": "$MODE",
  "page": $PAGE
JSON
)

# Add topic if provided
if [ -n "$TOPIC" ]; then
  PARAMS=$(cat <<JSON
{
  "context7CompatibleLibraryID": "$LIBRARY_ID",
  "topic": "$TOPIC",
  "mode": "$MODE",
  "page": $PAGE
}
JSON
)
fi

# Call MCP server (response stays in this subprocess!)
python3 "$(dirname "$0")/mcp-client.py" call \
  -s "npx -y @upstash/context7-mcp" \
  -t get-library-docs \
  -p "$PARAMS" 2>/dev/null
