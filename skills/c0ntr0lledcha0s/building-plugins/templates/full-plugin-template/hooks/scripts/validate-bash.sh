#!/bin/bash
# Hook script to validate bash commands before execution
# This runs as a PreToolUse hook for Bash tool calls

# Get the command from environment or stdin
COMMAND="$1"

if [ -z "$COMMAND" ]; then
    echo "✅ Bash command validation passed"
    exit 0
fi

# Check for dangerous patterns
if echo "$COMMAND" | grep -qE "rm\s+-rf\s+/"; then
    echo "❌ BLOCKED: Dangerous command detected (rm -rf /)"
    exit 1
fi

if echo "$COMMAND" | grep -qE ":\(\)\{.*:\|:.*\}"; then
    echo "❌ BLOCKED: Fork bomb detected"
    exit 1
fi

# Add more validation rules as needed

echo "✅ Bash command validation passed"
exit 0
