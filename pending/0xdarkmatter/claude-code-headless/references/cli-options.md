# CLI Options Reference

Complete reference for Claude Code CLI flags.

## Core Options

### Input/Output

| Flag | Short | Description |
|------|-------|-------------|
| `--print` | `-p` | Non-interactive mode (required for headless) |
| `--output-format` | | Output format: text, json, stream-json |
| `--verbose` | `-v` | Enable verbose/debug logging |
| `--quiet` | `-q` | Suppress non-essential output |

### Session Management

| Flag | Short | Description |
|------|-------|-------------|
| `--resume` | `-r` | Resume conversation by session ID |
| `--continue` | `-c` | Continue most recent conversation |
| `--session-id` | | Specify session ID for new session |

### Prompt Configuration

| Flag | Description |
|------|-------------|
| `--append-system-prompt` | Append text to system prompt |
| `--prepend-system-prompt` | Prepend text to system prompt |
| `--system-prompt` | Replace entire system prompt |

### Tool Control

| Flag | Description |
|------|-------------|
| `--allowedTools` | Comma-separated list of allowed tools |
| `--disallowedTools` | Comma-separated list of denied tools |
| `--mcp-config` | Path to MCP server configuration JSON |

### Permission Control

| Flag | Description |
|------|-------------|
| `--permission-mode` | Permission handling mode |

Permission modes:
- `default` - Ask for permission (blocks in headless)
- `acceptEdits` - Auto-accept file modifications
- `bypassPermissions` - Skip all permission prompts

### Model Selection

| Flag | Description |
|------|-------------|
| `--model` | Model to use: sonnet, opus, haiku |

## Usage Examples

### Basic Headless

```bash
# Simple query
claude -p "What is 2+2?"

# With file context
cat file.py | claude -p "Explain this code"

# From file
claude -p "$(cat prompt.txt)"
```

### Tool Restrictions

```bash
# Read-only mode
claude -p "Analyze codebase" \
  --allowedTools "Read,Grep,Glob,WebFetch,WebSearch" \
  --disallowedTools "Write,Edit,Bash,Task"

# Specific tools only
claude -p "Search for bugs" \
  --allowedTools "Read,Grep"
```

### Session Continuation

```bash
# Start session, capture ID
result=$(claude -p "Start analysis" --output-format json)
session_id=$(echo "$result" | jq -r '.session_id')

# Continue with context
claude -r "$session_id" "What did you find?"

# Continue most recent
claude -c "Add more details"
```

### System Prompt Modification

```bash
# Add context
claude -p "Review code" \
  --append-system-prompt "Focus on security vulnerabilities. Output findings as markdown."

# Full replacement
claude -p "Hello" \
  --system-prompt "You are a helpful assistant that only speaks in haiku."
```

### MCP Integration

```bash
# Use MCP servers from config
claude -p "Query the database" \
  --mcp-config ./mcp-servers.json

# With specific tools
claude -p "Fetch from GitHub" \
  --mcp-config ./mcp-servers.json \
  --allowedTools "mcp__github__*"
```

### Debugging

```bash
# Verbose output
claude -p "Debug this" --verbose

# Debug mode (shows internal operations)
claude --debug -p "Analyze"
```

## Input Methods

### Stdin Piping

```bash
# Pipe file content
cat error.log | claude -p "Explain these errors"

# Pipe command output
git diff | claude -p "Review this diff"

# Heredoc
claude -p "$(cat <<EOF
Analyze this data:
- Item 1
- Item 2
EOF
)"
```

### File Input

```bash
# Read prompt from file
claude -p "$(cat prompt.md)"

# With context files
claude -p "Review: $(cat src/main.ts)"
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | API key for Claude |
| `CLAUDE_PROJECT_DIR` | Override project directory |
| `NO_COLOR` | Disable colored output |

## Flag Combinations

### CI/CD Pipeline

```bash
claude -p "Run tests and report" \
  --permission-mode acceptEdits \
  --output-format json \
  --allowedTools "Bash,Read,Write"
```

### Security Audit

```bash
claude -p "Security review" \
  --allowedTools "Read,Grep,WebSearch" \
  --disallowedTools "Write,Edit,Bash" \
  --append-system-prompt "Report vulnerabilities in JSON format"
```

### Documentation Generation

```bash
claude -p "Generate API docs" \
  --permission-mode acceptEdits \
  --allowedTools "Read,Write,Glob" \
  --output-format json
```
