# Hook Events Reference

Comprehensive documentation for all Claude Code hook events.

## Event Processing Order

```
PreToolUse Hook → Deny Rules → Allow Rules → Ask Rules → Permission Check → [Tool Execution] → PostToolUse Hook
```

## PreToolUse

Fires before a tool is executed. Can block or modify the operation.

**Input Schema:**
```json
{
  "session_id": "abc123",
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file.txt",
    "content": "file contents..."
  }
}
```

**Use Cases:**
- Block dangerous operations
- Validate file paths
- Enforce naming conventions
- Rate limiting

**Example:**
```bash
#!/bin/bash
INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Block writes to protected directories
if [[ "$FILE" == /etc/* ]] || [[ "$FILE" == /usr/* ]]; then
    echo "Cannot write to system directories" >&2
    exit 2
fi
```

## PostToolUse

Fires after a tool completes. Cannot block but can log or notify.

**Input Schema:**
```json
{
  "session_id": "abc123",
  "tool_name": "Bash",
  "tool_input": {
    "command": "npm test"
  },
  "tool_output": {
    "stdout": "...",
    "stderr": "...",
    "exit_code": 0
  }
}
```

**Use Cases:**
- Audit logging
- Metrics collection
- Notifications on completion
- Output transformation

**Example:**
```bash
#!/bin/bash
INPUT=$(cat)
LOG_FILE="$CLAUDE_PROJECT_DIR/.claude/audit.log"
TOOL=$(echo "$INPUT" | jq -r '.tool_name')
TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "$TIME | $TOOL | $(echo "$INPUT" | jq -c '.')" >> "$LOG_FILE"
```

## PermissionRequest

Fires when Claude Code shows a permission dialog.

**Input Schema:**
```json
{
  "session_id": "abc123",
  "tool_name": "Bash",
  "tool_input": {
    "command": "rm -rf node_modules"
  },
  "permission_type": "tool_use"
}
```

**Use Cases:**
- Custom approval workflows
- Slack/Teams notifications
- External approval systems

## Notification

Fires when Claude Code sends a notification.

**Input Schema:**
```json
{
  "session_id": "abc123",
  "notification_type": "task_complete",
  "message": "Build completed successfully"
}
```

**Use Cases:**
- Forward to external services
- Custom notification routing

## UserPromptSubmit

Fires when user submits a prompt. No matcher support.

**Input Schema:**
```json
{
  "session_id": "abc123",
  "prompt": "User's message text"
}
```

**Use Cases:**
- Input logging
- Prompt transformation
- Usage analytics

## Stop

Fires when the main agent finishes. No matcher support.

**Input Schema:**
```json
{
  "session_id": "abc123",
  "reason": "completed",
  "final_message": "Task completed successfully"
}
```

**Use Cases:**
- Session cleanup
- Final logging
- Resource deallocation

## SubagentStop

Fires when a subagent finishes. No matcher support.

**Input Schema:**
```json
{
  "session_id": "abc123",
  "subagent_id": "xyz789",
  "subagent_type": "python-expert",
  "result": "Analysis complete"
}
```

**Use Cases:**
- Subagent performance tracking
- Result aggregation

## PreCompact

Fires before context window compaction. No matcher support.

**Input Schema:**
```json
{
  "session_id": "abc123",
  "current_tokens": 150000,
  "max_tokens": 200000
}
```

**Use Cases:**
- Save context state
- Pre-compaction processing

## SessionStart

Fires when a session begins or resumes. No matcher support.

**Input Schema:**
```json
{
  "session_id": "abc123",
  "is_resume": false,
  "project_dir": "/path/to/project"
}
```

**Use Cases:**
- Project initialization
- Load session state
- Environment setup

**Example:**
```bash
#!/bin/bash
# Load project-specific environment
source "$CLAUDE_PROJECT_DIR/.env.local" 2>/dev/null || true
echo "Session initialized for $(basename "$CLAUDE_PROJECT_DIR")"
```

## SessionEnd

Fires when a session ends. No matcher support.

**Input Schema:**
```json
{
  "session_id": "abc123",
  "duration_ms": 3600000,
  "total_cost_usd": 0.05
}
```

**Use Cases:**
- Session logging
- Cost tracking
- Cleanup tasks

## Exit Code Reference

| Code | Meaning | Effect |
|------|---------|--------|
| 0 | Success | Continue execution |
| 2 | Blocking error | Stop, show stderr to Claude |
| Other | Non-blocking error | Log warning, continue |

## Environment Variables

Available in all hook scripts:

| Variable | Description |
|----------|-------------|
| `CLAUDE_PROJECT_DIR` | Current project directory |
| `CLAUDE_SESSION_ID` | Current session identifier |
| `CLAUDE_TOOL_NAME` | Tool being executed (PreToolUse/PostToolUse only) |
