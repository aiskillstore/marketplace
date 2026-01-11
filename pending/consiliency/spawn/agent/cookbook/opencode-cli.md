# Purpose

Create a new OpenCode CLI agent to execute the command

## Variables

DEFAULT_MODEL: anthropic/claude-sonnet-4-5
HEAVY_MODEL: anthropic/claude-opus-4-5
BASE_MODEL: anthropic/claude-sonnet-4-5
FAST_MODEL: anthropic/claude-haiku-4-5
INTERACTIVE_MODE: true

## Instructions

### Model Selection
- OpenCode is provider-agnostic and supports 75+ providers via AI SDK
- Model format: `provider/model` (e.g., `anthropic/claude-sonnet-4-5`, `openai/gpt-5.2`)
- For the `-m, --model` argument, use DEFAULT_MODEL if not specified
- If 'fast' is requested, use FAST_MODEL
- If 'heavy' is requested, use HEAVY_MODEL

### Common Providers & Models
| Provider | Model Examples |
|----------|----------------|
| anthropic | claude-opus-4-5, claude-sonnet-4-5, claude-haiku-4-5 |
| openai | gpt-5.2, gpt-5.2-mini, gpt-5.2-pro |
| google | gemini-3-pro, gemini-3-flash-lite |
| groq | llama-3.3-70b, mixtral-8x7b |
| xai | grok-2, grok-beta |
| deepseek | deepseek-chat, deepseek-reasoner |

### Permission Mode
- OpenCode does not have a global "yolo" mode like other CLIs
- Permissions are configured via `opencode.json` config file
- For automated execution, configure permissions in config or accept prompts

### Interactive Mode Behavior

> **CRITICAL**: OpenCode has two main interfaces:
> - `opencode` or `opencode [project]` - Launches TUI (Terminal UI), always interactive
> - `opencode run [message..]` - Runs headless with a prompt, exits after completion
>
> The TUI is the primary interactive interface. Use `--continue` or `-c` to resume sessions.

- When `INTERACTIVE_MODE: true` (default):
  - **With prompt**: Launch TUI with prompt (TUI stays open)
  - **Without prompt**: Launch TUI directly: `opencode`
- When `INTERACTIVE_MODE: false`:
  - **With prompt**: Use run subcommand: `opencode run "<prompt>"`
  - **Without prompt**: Launch TUI: `opencode`

### Command Construction

**No prompt (always interactive TUI):**
```bash
opencode --model <PROVIDER/MODEL>
```

**With prompt + INTERACTIVE_MODE true (DEFAULT):**
```bash
# Launch TUI with initial prompt - stays interactive
opencode --model <PROVIDER/MODEL> --prompt "<prompt>"
```

**With prompt + INTERACTIVE_MODE false (headless execution):**
```bash
# Run headless, exits after completion
opencode run --model <PROVIDER/MODEL> "<prompt>"
```

**Continue previous session:**
```bash
opencode --model <PROVIDER/MODEL> --continue
```

**Continue specific session:**
```bash
opencode --model <PROVIDER/MODEL> --session <SESSION_ID>
```

**REQUIRED STEPS** - Do not skip:

1. **STOP** - Before executing the `opencode` command, you MUST first run the command with the --help flag:

   Example:
   ```
   opencode --help
   ```

2. Review the help output to understand available options
3. Only THEN proceed to fork the terminal with the full `opencode` command

## Key Flags Reference

| Flag | Description |
|------|-------------|
| `-m, --model <PROVIDER/MODEL>` | Model in format provider/model |
| `-p, --prompt <PROMPT>` | Initial prompt to use |
| `-c, --continue` | Continue the last session |
| `-s, --session <ID>` | Continue specific session by ID |
| `--agent <AGENT>` | Agent to use (Build, Plan, General, Explore) |
| `--port <PORT>` | Port for server mode (default: 0 = random) |
| `--hostname <HOST>` | Hostname for server mode (default: 127.0.0.1) |
| `--print-logs` | Print logs to stderr |
| `--log-level <LEVEL>` | Log level (DEBUG, INFO, WARN, ERROR) |
| `-v, --version` | Show version |
| `-h, --help` | Show help |

## Subcommands Reference

| Subcommand | Description |
|------------|-------------|
| `opencode` | Launch TUI (default) |
| `opencode run [message..]` | Run headless with prompt |
| `opencode serve` | Start headless server |
| `opencode web` | Start web interface |
| `opencode models [provider]` | List available models |
| `opencode stats` | Show token usage and costs |
| `opencode session` | Manage sessions |
| `opencode auth` | Manage credentials |
| `opencode agent` | Manage agents |
| `opencode acp` | Start ACP server |

## Clean Output Capture

When `LOG_AGENT_OUTPUT` is true (default), use the run subcommand for headless capture:

```bash
# Headless execution (for capture)
opencode run --model <PROVIDER/MODEL> "<prompt>"
```

The `run` subcommand executes headlessly and outputs the result. Check `opencode run --help` for JSON output options if available.

**Note**: The `run` subcommand exits after completion - use this when you need to capture the agent's response for later processing.

## Red Flags - STOP if you're about to:

- Execute an `opencode` command without checking its options first
- Assume you know the `opencode` command syntax
- Skip the --help step "because it's simple"
- Use `run` subcommand when interactive TUI is needed
- Forget the `provider/model` format (not just model name)

**STOP** -> Run `opencode --help` first -> Review output -> Then proceed
