---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: claude-hooks
---

# Hook Configuration Template

Hooks are shell commands that execute in response to Claude Code events.

## Hook Configuration Location

Hooks are configured in `~/.claude/settings.json` under the `hooks` key.

## Hook Events

| Event | Trigger | Use Case |
|-------|---------|----------|
| `PreToolUse` | Before any tool executes | Validation, logging, blocking |
| `PostToolUse` | After tool completes | Cleanup, notifications, post-processing |
| `Notification` | When Claude sends notification | Custom alerts, integrations |
| `Stop` | When Claude stops | Cleanup, final reports |

## Configuration Structure

```json
{
  "hooks": {
    "{{EVENT_NAME}}": [
      {
        "matcher": "{{TOOL_OR_PATTERN}}",
        "hooks": [
          {
            "type": "command",
            "command": "{{SHELL_COMMAND}}"
          }
        ]
      }
    ]
  }
}
```

## Examples

### Pre-Tool Validation Hook

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Executing bash command...'"
          }
        ]
      }
    ]
  }
}
```

### Post-Tool Logging Hook

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'File written: $CLAUDE_FILE_PATH' >> ~/.claude/file_log.txt"
          }
        ]
      }
    ]
  }
}
```

### Notification Hook

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"$CLAUDE_MESSAGE\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

## Environment Variables Available

| Variable | Description | Available In |
|----------|-------------|--------------|
| `$CLAUDE_TOOL_NAME` | Name of tool being executed | PreToolUse, PostToolUse |
| `$CLAUDE_TOOL_INPUT` | JSON input to tool | PreToolUse, PostToolUse |
| `$CLAUDE_TOOL_OUTPUT` | JSON output from tool | PostToolUse |
| `$CLAUDE_FILE_PATH` | Path for file operations | Write, Edit, Read |
| `$CLAUDE_MESSAGE` | Notification message | Notification |

## Matcher Patterns

| Pattern | Matches |
|---------|---------|
| `*` | All tools |
| `Bash` | Bash tool only |
| `Bash(git:*)` | Bash commands starting with git |
| `Write` | Write tool only |
| `mcp__*` | All MCP tools |

## Best Practices

1. **Keep hooks fast** - Long-running hooks block Claude
2. **Use async for slow operations** - Background with `&` if needed
3. **Handle errors gracefully** - Don't let hook failures break workflow
4. **Log sparingly** - Avoid verbose output that clutters context
5. **Test hooks independently** - Verify shell commands work before adding

## Quality Checklist

- [ ] Event type matches intended trigger
- [ ] Matcher pattern is specific enough
- [ ] Command executes quickly (<1s)
- [ ] Error handling prevents cascade failures
- [ ] Environment variables used correctly
- [ ] Hook tested in isolation before deployment
