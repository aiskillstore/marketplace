#!/bin/bash
#
# Claude Code Hook: [Description]
#
# Event: [PreToolUse|PostToolUse|SessionStart|etc]
# Matcher: [Tool name or * for all]
#
# Security: Validates input, quotes variables, prevents path traversal
#

set -euo pipefail

# Error handling
trap 'echo "Error at line $LINENO" >&2; exit 1' ERR

# Check dependencies
command -v jq >/dev/null 2>&1 || {
    echo "jq is required but not installed" >&2
    exit 1
}

# Read input from stdin
INPUT=$(cat)

# Validate JSON
if ! echo "$INPUT" | jq -e '.' > /dev/null 2>&1; then
    echo "Invalid JSON input" >&2
    exit 2
fi

# Parse common fields
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')
SESSION=$(echo "$INPUT" | jq -r '.session_id // empty')

# -------------------------------------------------------------------
# Your hook logic here
# -------------------------------------------------------------------

# Example: Log tool usage
LOG_FILE="${CLAUDE_PROJECT_DIR:-.}/.claude/hook.log"
mkdir -p "$(dirname "$LOG_FILE")"
echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") | $TOOL | $SESSION" >> "$LOG_FILE"

# Example: Block dangerous operations
# if [[ "$TOOL" == "Bash" ]]; then
#     CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
#     if [[ "$CMD" == *"rm -rf /"* ]]; then
#         echo "Blocked dangerous command" >&2
#         exit 2  # Exit 2 = blocking error
#     fi
# fi

# Example: Validate file paths
# if [[ "$TOOL" == "Write" ]]; then
#     FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
#     if [[ "$FILE" == *".."* ]]; then
#         echo "Path traversal blocked" >&2
#         exit 2
#     fi
# fi

# -------------------------------------------------------------------
# Exit codes:
#   0 = Success (continue execution)
#   2 = Blocking error (stderr shown to Claude)
#   Other = Non-blocking error (logged, continues)
# -------------------------------------------------------------------

exit 0

# CONFIGURATION EXAMPLE:
# Add to ~/.claude/settings.json or .claude/settings.local.json:
#
# {
#   "hooks": {
#     "PreToolUse": [{
#       "matcher": "*",
#       "hooks": [{
#         "type": "command",
#         "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/this-script.sh",
#         "timeout": 5000
#       }]
#     }]
#   }
# }
