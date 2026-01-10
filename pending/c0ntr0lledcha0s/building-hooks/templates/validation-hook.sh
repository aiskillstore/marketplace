#!/bin/bash
#
# Example validation hook for PreToolUse events
# Usage: Called automatically by Claude Code when specified tool is about to be used
#

# Input parameters depend on the event type
# For PreToolUse/PostToolUse:
#   $1 = Tool name (e.g., "Write", "Edit", "Bash")
#   $2 = Tool parameters (JSON or specific values)

TOOL_NAME="$1"
TOOL_PARAM="$2"

# Example: Validate file path for Write/Edit operations
if [[ "$TOOL_NAME" == "Write" ]] || [[ "$TOOL_NAME" == "Edit" ]]; then
    FILE_PATH="$TOOL_PARAM"

    # Define protected directories
    PROTECTED_DIRS=("/etc" "/usr" "/sys" "/boot" "/protected")

    # Check if file is in protected directory
    for protected_dir in "${PROTECTED_DIRS[@]}"; do
        if [[ "$FILE_PATH" == $protected_dir/* ]]; then
            # Block the operation
            echo "{\"decision\": \"block\", \"reason\": \"Cannot modify files in protected directory: $protected_dir\", \"systemMessage\": \"File modification blocked by security policy\"}"
            exit 2
        fi
    done

    # Check file extension restrictions (example)
    if [[ "$FILE_PATH" == *.exe ]] || [[ "$FILE_PATH" == *.dll ]]; then
        echo "{\"decision\": \"block\", \"reason\": \"Cannot write executable files\", \"systemMessage\": \"Executable file creation blocked\"}"
        exit 2
    fi
fi

# Example: Validate Bash commands
if [[ "$TOOL_NAME" == "Bash" ]]; then
    BASH_COMMAND="$TOOL_PARAM"

    # Block dangerous commands
    if echo "$BASH_COMMAND" | grep -qE "rm\s+-rf\s+/|dd\s+if=|mkfs|format|fdisk"; then
        echo "{\"decision\": \"block\", \"reason\": \"Dangerous system command detected\", \"systemMessage\": \"Command blocked for security\"}"
        exit 2
    fi

    # Warn about network operations (but don't block)
    if echo "$BASH_COMMAND" | grep -qE "curl|wget|nc|telnet"; then
        echo "{\"decision\": \"warn\", \"reason\": \"Network operation detected\", \"systemMessage\": \"Warning: Command will access network\"}"
        exit 0
    fi
fi

# Approve the operation
echo "{\"decision\": \"approve\", \"reason\": \"Validation passed\"}"
exit 0
