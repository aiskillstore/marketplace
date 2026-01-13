#!/bin/bash
# PreToolUse Hook: Protect Sensitive Files
# Blocks edits to specified files/patterns
#
# Usage in settings.json:
# {
#   "hooks": {
#     "PreToolUse": [{
#       "matcher": "Write|Edit",
#       "hooks": [{
#         "type": "command",
#         "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/file-protector.sh\""
#       }]
#     }]
#   }
# }

set -euo pipefail

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Skip if no file path (some tools don't have one)
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Security: Block path traversal
if [[ "$FILE_PATH" == *".."* ]]; then
  echo "Blocked: Path traversal attempt detected" >&2
  exit 2
fi

# Define protected patterns (customize these)
PROTECTED_PATTERNS=(
  "*.env"
  "*.env.*"
  "*credentials*"
  "*secret*"
  "*.pem"
  "*.key"
  ".git/*"
  "node_modules/*"
)

# Check against protected patterns
FILENAME=$(basename "$FILE_PATH")
for PATTERN in "${PROTECTED_PATTERNS[@]}"; do
  # shellcheck disable=SC2053
  if [[ "$FILE_PATH" == $PATTERN ]] || [[ "$FILENAME" == $PATTERN ]]; then
    echo "Blocked: Cannot modify protected file matching '$PATTERN'" >&2
    exit 2
  fi
done

# Optional: Require confirmation for specific directories
# SENSITIVE_DIRS=("src/auth" "config")
# for DIR in "${SENSITIVE_DIRS[@]}"; do
#   if [[ "$FILE_PATH" == *"$DIR"* ]]; then
#     # Return "ask" to show permission dialog
#     jq -n '{"decision": "ask"}'
#     exit 0
#   fi
# done

# File is allowed
exit 0
