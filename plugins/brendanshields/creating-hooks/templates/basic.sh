#!/bin/bash
# Basic Hook Template
# Copy and customize for your needs
#
# Usage in settings.json:
# {
#   "hooks": {
#     "EventName": [{
#       "matcher": "ToolPattern",
#       "hooks": [{
#         "type": "command",
#         "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/my-hook.sh\""
#       }]
#     }]
#   }
# }

set -euo pipefail

# Read JSON input from stdin
INPUT=$(cat)

# Extract common fields
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty')
HOOK_EVENT=$(echo "$INPUT" | jq -r '.hook_event_name // empty')

# Extract event-specific fields (customize based on your event)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
# FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
# PROMPT=$(echo "$INPUT" | jq -r '.prompt // empty')

# Your logic here
# Example: Log the event
# echo "$(date -Iseconds) [$HOOK_EVENT] $TOOL_NAME" >> "$CLAUDE_PROJECT_DIR/.claude/hook.log"

# Exit codes:
# 0 = Success (continue normally)
# 2 = Block (stop action, show stderr to user)
# Other = Non-blocking error (logged only)

exit 0
