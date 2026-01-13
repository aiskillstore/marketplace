# Purpose

Create a new Cursor Agent CLI to execute the command

## Variables

DEFAULT_MODEL: claude-sonnet-4.5
HEAVY_MODEL: claude-opus-4.5
BASE_MODEL: claude-sonnet-4.5
FAST_MODEL: gpt-5.2
INTERACTIVE_MODE: true

## Execution Modes

### Native Task Agent (Recommended for automation)
Use Claude Code's native Task agents for non-interactive Cursor execution:
- Parallel execution with other providers
- Clean result collection via TaskOutput
- Auto-recovery on auth failures

```bash
# Native agent compatible - use print mode with force
cursor-agent --model <MODEL> --force -p "<prompt>"
```

### Fork-Terminal (For interactive sessions)
Use fork-terminal when you need:
- Interactive TUI mode
- Browser-based authentication
- Real-time streaming output

## Instructions

### Model Selection
- For the `--model` or `-m` argument, use DEFAULT_MODEL if not specified
- If 'fast' is requested, use FAST_MODEL (gpt-5.2)
- If 'heavy' or 'thinking' is requested, use HEAVY_MODEL (claude-opus-4.5)
- Available models: gpt-5.2, claude-sonnet-4.5, claude-opus-4.5, gemini-3-pro

### Permission Mode
- Use `--force` or `-f` to force allow commands unless explicitly denied
- This is the closest equivalent to "yolo mode" for Cursor Agent CLI
- Without `--force`, CLI will ask to approve (Y) or reject (N) each command

### Interactive Mode Behavior

> **CRITICAL**: Cursor Agent CLI has two modes:
> - Interactive mode: `cursor-agent` or `cursor-agent "prompt"` - TUI chat interface
> - Non-interactive mode: `cursor-agent -p "prompt"` - Prints response to console, for scripts/CI
>
> Use `--resume` to continue previous sessions.

- When `INTERACTIVE_MODE: true` (default):
  - **With prompt**: Launch TUI with prompt: `cursor-agent "<prompt>"`
  - **Without prompt**: Launch TUI directly: `cursor-agent`
- When `INTERACTIVE_MODE: false`:
  - **With prompt**: Use print mode: `cursor-agent -p "<prompt>"`
  - **Without prompt**: Launch TUI: `cursor-agent`

### Command Construction

**No prompt (always interactive TUI):**
```bash
cursor-agent --model <MODEL> --force
```

**With prompt + INTERACTIVE_MODE true (DEFAULT):**
```bash
# Launch TUI with initial prompt - stays interactive
cursor-agent --model <MODEL> --force "<prompt>"
```

**With prompt + INTERACTIVE_MODE false (non-interactive/scripting):**
```bash
# Print mode for scripts and CI/CD
cursor-agent --model <MODEL> --force -p "<prompt>"
```

**With specific output format (non-interactive):**
```bash
# JSON output for parsing
cursor-agent --model <MODEL> --force -p "<prompt>" --output-format json

# Plain text output
cursor-agent --model <MODEL> --force -p "<prompt>" --output-format text

# Streaming JSON (default)
cursor-agent --model <MODEL> --force -p "<prompt>" --output-format stream-json
```

**Resume previous session:**
```bash
cursor-agent --model <MODEL> --force --resume
```

**Resume specific session:**
```bash
cursor-agent --model <MODEL> --force --resume <chatId>
```

**Fullscreen mode:**
```bash
cursor-agent --model <MODEL> --force --fullscreen "<prompt>"
```

**REQUIRED STEPS** - Do not skip:

1. **STOP** - Before executing the `cursor-agent` command, you MUST first run the command with the --help flag:

   Example:
   ```
   cursor-agent --help
   ```

2. Review the help output to understand available options
3. Only THEN proceed to fork the terminal with the full `cursor-agent` command

## Key Flags Reference

| Flag | Description |
|------|-------------|
| `-m, --model <MODEL>` | Model to use (gpt-5.2, claude-sonnet-4.5, claude-opus-4.5, gemini-3-pro) |
| `-f, --force` | Force allow commands unless explicitly denied |
| `-p, --print` | Non-interactive mode, print responses to console |
| `--output-format <FORMAT>` | Output format: text, json, stream-json (default) |
| `--resume [chatId]` | Resume a chat session (latest or specific ID) |
| `--fullscreen` | Enable fullscreen mode |
| `-a, --api-key <KEY>` | API key (or use CURSOR_API_KEY env var) |
| `-v, --version` | Output version number |
| `-h, --help` | Display help |

## Subcommands Reference

| Subcommand | Description |
|------------|-------------|
| `cursor-agent` | Start interactive TUI (default) |
| `cursor-agent login` | Authenticate with Cursor |
| `cursor-agent logout` | Sign out and clear authentication |
| `cursor-agent status` | Check authentication status |
| `cursor-agent update` | Update to latest version (alias: upgrade) |
| `cursor-agent ls` | List chat sessions |
| `cursor-agent resume` | Resume latest chat session |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `CURSOR_API_KEY` | API key for authentication |

## Notes

- Cursor Agent CLI is in beta - security safeguards are still evolving
- Can read, modify, delete files and execute approved shell commands
- Supports MCP (Model Context Protocol) - auto-detects mcp.json config
- Works alongside other IDEs (Neovim, JetBrains, etc.)

## Clean Output Capture

When `LOG_AGENT_OUTPUT` is true (default), use print mode with JSON output:

```bash
# Non-interactive with JSON output (for capture)
cursor-agent --model <MODEL> --force -p "<prompt>" --output-format json
```

The JSON output contains the agent's response without TUI elements or ANSI codes.

**Note**: `-p` (print mode) is required for JSON output. This disables the interactive TUI - use this when you need to capture the agent's response for later processing.

## Red Flags - STOP if you're about to:

- Execute a `cursor-agent` command without checking its options first
- Assume you know the `cursor-agent` command syntax
- Skip the --help step "because it's simple"
- Use `-p` (print mode) when interactive TUI is needed
- Confuse `cursor` (IDE launcher) with `cursor-agent` (agentic CLI)

**STOP** -> Run `cursor-agent --help` first -> Review output -> Then proceed
