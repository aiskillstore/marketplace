# Hook Events Reference

Complete reference for all Claude Code hook events.

## Hook Input (All Events)

Every hook receives JSON on stdin with these common fields:

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/conversation.jsonl",
  "cwd": "/current/working/directory",
  "permission_mode": "default",
  "hook_event_name": "EventName"
}
```

## Event Details

### PreToolUse

**Triggers**: Before any tool executes

**Additional Input**:
```json
{
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file",
    "content": "..."
  }
}
```

**Output Options**:
```json
{
  "decision": "allow|deny|ask",
  "reason": "Why (shown if deny)",
  "updatedInput": { }
}
```

- `allow`: Proceed without permission prompt
- `deny`: Block with reason shown to user
- `ask`: Show normal permission dialog
- `updatedInput`: Modify tool parameters before execution

---

### PostToolUse

**Triggers**: After tool executes successfully

**Additional Input**:
```json
{
  "tool_name": "Write",
  "tool_input": { },
  "tool_response": {
    "success": true,
    "output": "..."
  }
}
```

**Output Options**:
```json
{
  "decision": "block",
  "reason": "Issue found - Claude should fix",
  "additionalContext": "Details for Claude"
}
```

- `decision: "block"`: Prompts Claude with your reason
- `additionalContext`: Extra info Claude sees

---

### UserPromptSubmit

**Triggers**: When user submits a message

**Additional Input**:
```json
{
  "prompt": "User's message text"
}
```

**Output Options**:
```json
{
  "decision": "block",
  "reason": "Why blocked",
  "additionalContext": "Context added to conversation"
}
```

- `decision: "block"`: Prevents processing, shows reason
- Plain stdout text or `additionalContext`: Injected as context

---

### SessionStart

**Triggers**: When session begins or resumes

**Additional Input**:
```json
{
  "is_resume": false
}
```

**Output Options**:
```json
{
  "additionalContext": "Project context for Claude"
}
```

- Use `CLAUDE_ENV_FILE` to persist environment variables
- `additionalContext`: Shown to Claude at session start

---

### SessionEnd

**Triggers**: When session terminates

**Additional Input**:
```json
{
  "reason": "user_exit|error|timeout"
}
```

**Output**: No decision control. Use for cleanup/logging only.

---

### Stop

**Triggers**: When main agent finishes responding

**Additional Input**:
```json
{
  "stop_reason": "end_turn|tool_use"
}
```

**Output Options**:
```json
{
  "decision": "block",
  "reason": "Continue because..."
}
```

- `decision: "block"`: Agent continues with your reason as context

---

### SubagentStop

**Triggers**: When a subagent finishes

**Additional Input**:
```json
{
  "subagent_type": "task",
  "stop_reason": "end_turn"
}
```

**Output Options**: Same as Stop

---

### PermissionRequest

**Triggers**: When permission dialog would be shown

**Additional Input**:
```json
{
  "tool_name": "Bash",
  "tool_input": { },
  "permission_type": "tool"
}
```

**Output Options**:
```json
{
  "decision": {
    "behavior": "allow|deny"
  },
  "updatedInput": { },
  "message": "Custom message"
}
```

---

### Notification

**Triggers**: When Claude Code sends alerts

**Additional Input**:
```json
{
  "notification_type": "permission|idle|auth",
  "message": "Notification text"
}
```

**Output**: No decision control. Use for routing notifications.

---

### PreCompact

**Triggers**: Before context compaction

**Additional Input**:
```json
{
  "trigger": "auto|manual",
  "token_count": 95000
}
```

**Output Options**:
```json
{
  "decision": "block",
  "reason": "Don't compact yet"
}
```

## Matcher Patterns

Matchers filter which tools trigger hooks:

| Pattern | Matches |
|---------|---------|
| `"Write"` | Exact tool name |
| `"Edit\|Write"` | Multiple tools (regex) |
| `"mcp__memory__.*"` | MCP tools by server |
| `"Notebook.*"` | Tools starting with |
| `"*"` or `""` | All tools |

**Case sensitive**: `"write"` won't match `"Write"`

## Exit Code Reference

| Code | Effect |
|------|--------|
| 0 | Success, continue normally |
| 2 | Blocking error, stop action |
| 1, 3+ | Non-blocking, logged only |

## Security Patterns

### Input Validation

```bash
INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Validate file exists
if [ -z "$FILE" ]; then
  echo "No file path provided" >&2
  exit 2
fi
```

### Path Traversal Prevention

```bash
# Block directory traversal
if [[ "$FILE" == *".."* ]]; then
  echo "Path traversal blocked" >&2
  exit 2
fi

# Ensure within project
if [[ "$FILE" != "$CLAUDE_PROJECT_DIR"* ]]; then
  echo "File outside project" >&2
  exit 2
fi
```

### Safe JSON Output

```bash
# Use jq to ensure valid JSON
jq -n --arg ctx "My context" '{"additionalContext": $ctx}'
```

## Debugging Hooks

### Test Manually

```bash
# Simulate PreToolUse
echo '{"tool_name":"Write","tool_input":{"file_path":"test.txt"}}' | \
  bash .claude/hooks/my-hook.sh
echo "Exit code: $?"
```

### Enable Verbose Mode

Run Claude Code with `--verbose` to see hook output for exit code 0.

### Check Logs

Hook stderr is always shown for exit code 2.
