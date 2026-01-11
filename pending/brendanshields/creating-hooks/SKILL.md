---
name: creating-hooks
description: |
  Creates Claude Code hooks for automation and workflow customization.
  Guides through hook events, configuration, and script creation.
  Use when user wants to create a hook, automate Claude Code, or asks about hook events.
---

# Creating Hooks

Guides creation of Claude Code hooks for automation and workflow customization.

## Quick Start

1. Choose hook event (when should it trigger?)
2. Configure in settings.json
3. Create hook script
4. Test the hook

## Workflow: Create New Hook

```
Progress:
- [ ] Select hook event
- [ ] Add to settings.json
- [ ] Create hook script
- [ ] Test and validate
```

### Step 1: Select Hook Event

| Event | When It Triggers | Common Use |
|-------|------------------|------------|
| `PreToolUse` | Before tool runs | Block/modify tools |
| `PostToolUse` | After tool succeeds | Validate, log, feedback |
| `UserPromptSubmit` | User sends message | Inject context, validate |
| `SessionStart` | Session begins | Load context, init state |
| `SessionEnd` | Session ends | Cleanup, save state |
| `Stop` | Agent finishes | Decide if should continue |

Full event reference: [reference.md](reference.md)

### Step 2: Configure settings.json

Location priority (highest wins):
1. `.claude/settings.local.json` (local, not committed)
2. `.claude/settings.json` (project)
3. `~/.claude/settings.json` (user)

Basic structure:
```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolPattern",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/my-hook.sh\""
          }
        ]
      }
    ]
  }
}
```

### Step 3: Create Hook Script

Use templates from [templates/](templates/) directory.

Key requirements:
- Read JSON from stdin
- Use exit codes for control (0=success, 2=block)
- Output JSON for decisions

### Step 4: Test

Run hook manually with test input:
```bash
echo '{"tool_name":"Write"}' | bash .claude/hooks/my-hook.sh
```

## Hook Configuration

### Matcher Patterns

```json
"matcher": "Write"           // Exact match
"matcher": "Edit|Write"      // Multiple tools
"matcher": "mcp__.*"         // MCP tools (regex)
"matcher": "*"               // All tools
```

Matchers apply to: `PreToolUse`, `PostToolUse`, `PermissionRequest`

### Timeout

```json
{
  "type": "command",
  "command": "...",
  "timeout": 120
}
```
Default: 60 seconds. Max recommended: 300 seconds.

## Exit Codes

| Code | Meaning | Behavior |
|------|---------|----------|
| 0 | Success | Continue normally |
| 2 | Block | Stop action, show error |
| Other | Non-blocking error | Log only (verbose mode) |

## JSON Output

Return JSON to stdout for decisions:

```json
{
  "decision": "block",
  "reason": "Why blocked",
  "additionalContext": "Info for Claude"
}
```

Decision values by event:
- `PreToolUse`: `allow`, `deny`, `ask`
- `PostToolUse`: `block` (with reason)
- `UserPromptSubmit`: `block` (with reason)
- `Stop`: `block` (requires reason)

## Security Best Practices

1. **Quote all variables**: `"$VAR"` not `$VAR`
2. **Use absolute paths**: `"$CLAUDE_PROJECT_DIR/..."`
3. **Validate inputs**: Check before processing
4. **Block path traversal**: Reject paths with `..`
5. **Set timeouts**: Prevent runaway scripts

## Environment Variables

Available in all hooks:
- `CLAUDE_PROJECT_DIR` - Project root path
- `CLAUDE_CODE_REMOTE` - "true" if web environment

SessionStart only:
- `CLAUDE_ENV_FILE` - Path to persist env vars

## Common Patterns

### Inject Context on Session Start

```bash
#!/bin/bash
# Output context for Claude
echo '{"additionalContext": "Project uses TypeScript"}'
exit 0
```

### Block Dangerous File Edits

```bash
#!/bin/bash
INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
if [[ "$FILE" == *".env"* ]]; then
  echo "Blocking edit to sensitive file" >&2
  exit 2
fi
exit 0
```

### Log All Tool Usage

```bash
#!/bin/bash
INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name')
echo "$(date -Iseconds) $TOOL" >> "$CLAUDE_PROJECT_DIR/.claude/tool.log"
exit 0
```

See [reference.md](reference.md) for complete event details and more examples.
