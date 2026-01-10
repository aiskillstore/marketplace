# Hook Configuration Patterns

Advanced configuration for Claude Code hooks.

## Configuration Locations

| File | Scope | Priority |
|------|-------|----------|
| `~/.claude/settings.json` | Global (all projects) | Lower |
| `.claude/settings.local.json` | Project-specific | Higher |

Project settings are additive to global settings.

## Full Configuration Schema

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolPattern",
        "hooks": [
          {
            "type": "command",
            "command": "path/to/script.sh",
            "timeout": 5000
          }
        ]
      }
    ]
  }
}
```

## Multiple Hooks Per Event

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          { "type": "command", "command": "validate-write.sh" }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "validate-bash.sh" }
        ]
      },
      {
        "matcher": "*",
        "hooks": [
          { "type": "command", "command": "log-all-tools.sh" }
        ]
      }
    ]
  }
}
```

## Matcher Patterns

### Simple Matchers

```json
{"matcher": "Write"}      // Exact tool name
{"matcher": "Bash"}       // Bash commands
{"matcher": "Read"}       // File reads
```

### Wildcard Matchers

```json
{"matcher": "*"}          // All tools
{"matcher": ""}           // All tools (empty = wildcard)
{"matcher": "mcp__*"}     // All MCP tools
```

### MCP Tool Matchers

```json
{"matcher": "mcp__filesystem__*"}     // All filesystem MCP tools
{"matcher": "mcp__github__create_*"}  // GitHub create operations
```

## Chaining Multiple Commands

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          { "type": "command", "command": "lint-check.sh", "timeout": 3000 },
          { "type": "command", "command": "security-scan.sh", "timeout": 10000 }
        ]
      }
    ]
  }
}
```

Hooks execute sequentially. If any hook exits with code 2, execution stops.

## Timeout Configuration

```json
{
  "type": "command",
  "command": "slow-check.sh",
  "timeout": 30000  // 30 seconds (milliseconds)
}
```

Default timeout: 5000ms (5 seconds)

## Path Variables

Use `$CLAUDE_PROJECT_DIR` for portable paths:

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/validate.sh"
      }]
    }]
  }
}
```

## Conditional Hooks

Handle conditions in the script, not configuration:

```bash
#!/bin/bash
INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name')

# Only process Write and Edit
case "$TOOL" in
  Write|Edit)
    # Validation logic
    ;;
  *)
    exit 0  # Skip other tools
    ;;
esac
```

## Environment-Specific Hooks

### Development vs Production

```bash
#!/bin/bash
if [[ "${CLAUDE_ENV:-development}" == "production" ]]; then
    # Stricter validation
    strict_validate.sh
else
    # Lenient for development
    exit 0
fi
```

### Per-Project Override

Project `.claude/settings.local.json` can add project-specific hooks:

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/scripts/project-validate.sh"
      }]
    }]
  }
}
```

## Common Configuration Patterns

### Audit Logging

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/audit-log.sh"
      }]
    }]
  }
}
```

### Block Dangerous Commands

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/block-dangerous.sh",
        "timeout": 1000
      }]
    }]
  }
}
```

### Session Initialization

```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/init-session.sh"
      }]
    }]
  }
}
```

## Debugging Configuration

1. **Check JSON validity:**
   ```bash
   jq '.' ~/.claude/settings.json
   ```

2. **Test hook script:**
   ```bash
   echo '{"tool_name":"Bash","tool_input":{}}' | ./hook.sh
   echo $?  # Check exit code
   ```

3. **Enable debug mode:**
   ```bash
   claude --debug
   ```

4. **List registered hooks:**
   ```
   /hooks
   ```
