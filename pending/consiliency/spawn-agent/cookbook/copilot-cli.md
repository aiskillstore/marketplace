# Purpose

Create a new GitHub Copilot CLI agent to execute the command

## Variables

DEFAULT_MODEL: claude-sonnet-4.5
HEAVY_MODEL: claude-sonnet-4.5
BASE_MODEL: claude-sonnet-4.5
FAST_MODEL: claude-sonnet-4.5
INTERACTIVE_MODE: true

## Instructions

### Model Selection
- Default model is Claude Sonnet 4.5 (configurable via `/model` command in session)
- Model selection is done within the session using `/model` command
- No command-line flag for model selection at launch

### Permission Mode
- Use `--allow-all-tools` for automatic approval of all tool usage
- Alternative: `--allow-tool NAME` to allow specific tools
- Block tools with: `--deny-tool NAME`

### Tool Approval Modes
- Default: Prompt for approval on each tool use
- Session approval: "Yes, approve for session" grants tool for rest of session
- `--allow-all-tools`: Permit unrestricted tool usage (equivalent to yolo mode)

### Interactive Mode Behavior

> **CRITICAL**: Copilot CLI has two modes:
> - Interactive mode: `copilot` - Launches conversational session
> - Programmatic mode: `copilot -p "prompt"` - Single prompt execution
>
> Use `--continue` to resume the most recent session or `--resume` for session selection.

- When `INTERACTIVE_MODE: true` (default):
  - **With prompt**: Use prompt flag with continue: `copilot -p "<prompt>" --continue`
  - **Without prompt**: Launch directly: `copilot`
- When `INTERACTIVE_MODE: false`:
  - **With prompt**: Single execution: `copilot -p "<prompt>"`
  - **Without prompt**: Launch in interactive mode: `copilot`

### Command Construction

**No prompt (always interactive):**
```bash
copilot --allow-all-tools
```

**With prompt + INTERACTIVE_MODE true (DEFAULT):**
```bash
# Execute prompt and continue in interactive mode
copilot --allow-all-tools -p "<prompt>" --continue
```

**With prompt + INTERACTIVE_MODE false (single execution):**
```bash
# Execute prompt and exit
copilot --allow-all-tools -p "<prompt>"
```

**Resume previous session:**
```bash
copilot --allow-all-tools --resume
```

**With custom agent:**
```bash
copilot --allow-all-tools --agent=<agent-name> -p "<prompt>"
```

**REQUIRED STEPS** - Do not skip:

1. **STOP** - Before executing the `copilot` command, you MUST first run the command with the help flag:

   Example:
   ```
   copilot help
   ```

2. Review the help output to understand available options
3. Only THEN proceed to fork the terminal with the full `copilot` command

## Key Flags Reference

| Flag | Description |
|------|-------------|
| `-p "prompt"` | Single prompt execution (programmatic mode) |
| `--continue` | Resume most recently closed session |
| `--resume` | Return to previous interactive sessions (selection menu) |
| `--allow-all-tools` | Permit unrestricted tool usage |
| `--allow-tool NAME` | Grant permission for specific tool |
| `--deny-tool NAME` | Block designated tool |
| `--agent=NAME` | Specify custom agent |

## In-Session Commands Reference

| Command | Description |
|---------|-------------|
| `/login` | Authenticate with GitHub account |
| `/model` | Change AI model |
| `/ai-dev-kit:delegate` | Hand off to Copilot coding agent on GitHub |
| `/add-dir /path` | Add trusted directory |
| `/cwd /path` | Change working directory |
| `/mcp add` | Add MCP server |
| `/usage` | View token usage metrics |
| `/feedback` | Submit feedback |
| `!command` | Execute shell command directly |
| `?` | Display command options |

## Help Subcommands

| Command | Description |
|---------|-------------|
| `copilot help` | Terminal command reference |
| `copilot help config` | Configuration settings |
| `copilot help environment` | Environment variable reference |
| `copilot help logging` | Logging levels |
| `copilot help permissions` | Tool use permissions |

## File Context

Include files in prompts using `@` syntax:
- `@src/app.js` - Include single file
- Tab completion supported for matching paths

## Clean Output Capture

When `LOG_AGENT_OUTPUT` is true (default), use programmatic mode for capture:

```bash
# Programmatic mode (for capture)
copilot --allow-all-tools -p "<prompt>"
```

The `-p` flag runs in programmatic mode and outputs the result without interactive elements.

**Note**: Programmatic mode exits after completion - use this when you need to capture the agent's response for later processing.

## Red Flags - STOP if you're about to:

- Execute a `copilot` command without checking its options first
- Assume you know the `copilot` command syntax
- Skip the help step "because it's simple"
- Use `-p` without `--continue` when interactive mode is needed
- Forget that model selection is done via `/model` in-session, not CLI flag

**STOP** -> Run `copilot help` first -> Review output -> Then proceed
