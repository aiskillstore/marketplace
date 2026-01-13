# Hook Security Patterns

Security best practices for Claude Code hook scripts.

## Input Validation

### Always Parse JSON Safely

```bash
#!/bin/bash
set -euo pipefail

INPUT=$(cat)

# Validate JSON structure
if ! echo "$INPUT" | jq -e '.' > /dev/null 2>&1; then
    echo "Invalid JSON input" >&2
    exit 2
fi

TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')
if [[ -z "$TOOL" ]]; then
    echo "Missing tool_name" >&2
    exit 2
fi
```

### Quote All Variables

```bash
# GOOD - Variables are quoted
file_path="$1"
command="$CLAUDE_PROJECT_DIR/scripts/validate.sh"
echo "Processing: $file_path"

# BAD - Unquoted variables allow injection
file_path=$1
command=$CLAUDE_PROJECT_DIR/scripts/validate.sh
```

### Path Traversal Prevention

```bash
#!/bin/bash
INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Check for path traversal
if [[ "$FILE" == *".."* ]]; then
    echo "Path traversal attempt blocked: $FILE" >&2
    exit 2
fi

# Ensure within project directory
REAL_PATH=$(realpath -m "$FILE" 2>/dev/null || echo "$FILE")
if [[ "$REAL_PATH" != "$CLAUDE_PROJECT_DIR"* ]]; then
    echo "Path outside project directory: $FILE" >&2
    exit 2
fi
```

### Command Injection Prevention

```bash
#!/bin/bash
INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Block dangerous commands
DANGEROUS_PATTERNS=(
    "rm -rf /"
    "rm -rf /*"
    "> /dev/sda"
    "mkfs."
    "dd if="
    ":(){:|:&};:"
)

for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if [[ "$CMD" == *"$pattern"* ]]; then
        echo "Blocked dangerous command: $pattern" >&2
        exit 2
    fi
done
```

## Secrets Management

### Never Log Secrets

```bash
#!/bin/bash
INPUT=$(cat)

# DON'T: Log full input (may contain secrets)
# echo "$INPUT" >> /tmp/debug.log

# DO: Log sanitized data
TOOL=$(echo "$INPUT" | jq -r '.tool_name')
echo "$(date) | $TOOL" >> "$CLAUDE_PROJECT_DIR/.claude/audit.log"
```

### Environment Variable Handling

```bash
#!/bin/bash
# Load secrets from secure source
if [[ -f "$HOME/.secrets/claude-hooks" ]]; then
    source "$HOME/.secrets/claude-hooks"
fi

# Never echo secrets
# echo "Using API key: $API_KEY"  # BAD

# Use for operations without exposing
curl -s -H "Authorization: Bearer $API_KEY" "$ENDPOINT" > /dev/null
```

## Rate Limiting

```bash
#!/bin/bash
RATE_FILE="/tmp/claude-hook-rate"
MAX_CALLS=100
WINDOW=60  # seconds

NOW=$(date +%s)
CUTOFF=$((NOW - WINDOW))

# Atomic file operations
{
    flock -x 200

    # Clean old entries and count recent
    if [[ -f "$RATE_FILE" ]]; then
        RECENT=$(awk -v cutoff="$CUTOFF" '$1 > cutoff' "$RATE_FILE" | wc -l)
    else
        RECENT=0
    fi

    if [[ $RECENT -ge $MAX_CALLS ]]; then
        echo "Rate limit exceeded: $RECENT calls in ${WINDOW}s" >&2
        exit 2
    fi

    # Log this call
    echo "$NOW" >> "$RATE_FILE"

    # Cleanup old entries
    awk -v cutoff="$CUTOFF" '$1 > cutoff' "$RATE_FILE" > "${RATE_FILE}.tmp"
    mv "${RATE_FILE}.tmp" "$RATE_FILE"

} 200>"${RATE_FILE}.lock"
```

## Timeout Handling

```bash
#!/bin/bash
# Set script timeout
TIMEOUT=10

# Use timeout for external commands
timeout "$TIMEOUT" some-slow-command || {
    echo "Command timed out after ${TIMEOUT}s" >&2
    exit 2
}
```

## Error Handling

```bash
#!/bin/bash
set -euo pipefail

# Trap errors
trap 'echo "Hook failed at line $LINENO" >&2; exit 1' ERR

# Validate dependencies
command -v jq >/dev/null 2>&1 || {
    echo "jq is required but not installed" >&2
    exit 1
}

# Main logic with explicit error handling
INPUT=$(cat) || {
    echo "Failed to read input" >&2
    exit 1
}
```

## File Permissions

```bash
# Hook scripts should be executable only by owner
chmod 700 hook-script.sh

# Sensitive config should be readable only by owner
chmod 600 ~/.claude/settings.json

# Audit logs should be append-only where possible
chattr +a /var/log/claude-audit.log  # Linux only
```

## Audit Trail Pattern

```bash
#!/bin/bash
INPUT=$(cat)
LOG_DIR="$CLAUDE_PROJECT_DIR/.claude/audit"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
SESSION=$(echo "$INPUT" | jq -r '.session_id // "unknown"')
TOOL=$(echo "$INPUT" | jq -r '.tool_name // "unknown"')
LOG_FILE="$LOG_DIR/${SESSION}.jsonl"

# Append-only logging
{
    echo "{\"timestamp\":\"$TIMESTAMP\",\"tool\":\"$TOOL\",\"input\":$(echo "$INPUT" | jq -c '.tool_input')}"
} >> "$LOG_FILE"
```

## Security Checklist

### Before Deployment

- [ ] All variables quoted
- [ ] Path traversal checks implemented
- [ ] Dangerous command patterns blocked
- [ ] No secrets in logs
- [ ] Proper file permissions set
- [ ] Timeout configured
- [ ] Error handling complete
- [ ] Input JSON validated

### Script Header Template

```bash
#!/bin/bash
#
# Claude Code Hook: [description]
# Security considerations:
#   - Validates all JSON input
#   - Blocks path traversal
#   - Quotes all variables
#   - Logs sanitized data only
#

set -euo pipefail
trap 'echo "Error at line $LINENO" >&2; exit 1' ERR

# Dependencies check
command -v jq >/dev/null 2>&1 || { echo "jq required" >&2; exit 1; }

# Read and validate input
INPUT=$(cat)
if ! echo "$INPUT" | jq -e '.' > /dev/null 2>&1; then
    echo "Invalid JSON" >&2
    exit 2
fi

# Main logic here...
```
