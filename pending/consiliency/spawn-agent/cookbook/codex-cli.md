# Purpose

Create a new Codex CLI agent to execute the command

## Variables

DEFAULT_MODEL: gpt-5.2-codex
HEAVY_MODEL: gpt-5.2-codex
BASE_MODEL: gpt-5.2-codex
FAST_MODEL: gpt-5.2-codex-mini
INTERACTIVE_MODE: true

## Execution Modes

### Native Task Agent (Recommended for automation)
Use Claude Code's native Task agents for non-interactive Codex execution:
- Parallel execution with other providers
- Clean result collection via TaskOutput
- Auto-recovery on auth failures

```bash
# Native agent compatible - use exec with --full-auto
# NOTE: Do NOT specify --model with ChatGPT accounts - let it use the default
codex exec --full-auto "<prompt>"
```

**Important**: With ChatGPT accounts, explicitly specifying `--model` causes errors.
The CLI defaults to `gpt-5.2-codex` when no model is specified. Only use `--model`
if you have a paid OpenAI API account.

### Fork-Terminal (For interactive sessions)
Use fork-terminal when you need:
- Interactive TUI mode
- Browser-based authentication
- Real-time streaming output

## Instructions

### Model Selection
- For the `--model` or `-m` argument, use DEFAULT_MODEL if not specified
- If 'fast' is requested, use FAST_MODEL
- If 'heavy' is requested, use HEAVY_MODEL

### Permission Mode
- Always run with `--dangerously-bypass-approvals-and-sandbox` for full auto mode
- Alternative: use `--full-auto` for sandboxed automatic execution (safer)

### Sandbox Modes
- `read-only` - Read-only access to workspace
- `workspace-write` - Can write to workspace directory
- `danger-full-access` - Full system access (use with caution)

### Interactive Mode Behavior

> **CRITICAL**: Codex CLI exits after completing a prompt by default. Unlike Claude Code,
> Codex does not have a `--continue` flag. To stay interactive, you must launch without
> a prompt OR use the interactive TUI and type your prompt there.

- Never use `exec` subcommand for interactive mode - it's non-interactive by design
- When `INTERACTIVE_MODE: true` (default):
  - **With prompt**: Launch TUI with prompt as argument: `codex "<prompt>"`
  - **Without prompt**: Launch directly in interactive mode: `codex`
- When `INTERACTIVE_MODE: false`:
  - **With prompt**: Use exec subcommand: `codex exec "<prompt>"`
  - **Without prompt**: Launch in interactive mode: `codex`

### Command Construction

**No prompt (always interactive):**
```bash
codex --model <MODEL> --dangerously-bypass-approvals-and-sandbox
```

**With prompt + INTERACTIVE_MODE true (DEFAULT):**
```bash
# Launch TUI with initial prompt - stays interactive after completion
codex --model <MODEL> --dangerously-bypass-approvals-and-sandbox "<prompt>"
```

**With prompt + INTERACTIVE_MODE false (non-interactive execution):**
```bash
# Use exec subcommand for single-task automation
codex exec --model <MODEL> --dangerously-bypass-approvals-and-sandbox "<prompt>"
```

**With prompt + safer sandboxed auto mode:**
```bash
codex --model <MODEL> --full-auto "<prompt>"
```

**REQUIRED STEPS** - Do not skip:

1. **STOP** - Before executing the `codex` command, you MUST first run the command with the --help flag:

   Example:
   ```
   codex --help
   ```

2. Review the help output to understand available options
3. Only THEN proceed to fork the terminal with the full `codex` command

## Key Flags Reference

| Flag | Description |
|------|-------------|
| `-m, --model <MODEL>` | Model to use (gpt-5.2-codex, gpt-5.2-codex-mini) |
| `-s, --sandbox <MODE>` | Sandbox policy (read-only, workspace-write, danger-full-access) |
| `-a, --ask-for-approval <POLICY>` | Approval policy (untrusted, on-failure, on-request, never) |
| `--full-auto` | Sandboxed automatic execution (-a on-failure, --sandbox workspace-write) |
| `--dangerously-bypass-approvals-and-sandbox` | Skip all confirmations, no sandbox (DANGEROUS) |
| `-C, --cd <DIR>` | Set working directory |
| `--search` | Enable web search tool |
| `-i, --image <FILE>` | Attach image(s) to prompt |

## Clean Output Capture

When `LOG_AGENT_OUTPUT` is true (default), use the exec subcommand for non-interactive capture:

```bash
# Non-interactive execution (for capture)
codex exec --model <MODEL> --dangerously-bypass-approvals-and-sandbox "<prompt>"
```

**Note**: The `exec` subcommand runs non-interactively and outputs the result. Check `codex exec --help` for JSON output options if available.

## Red Flags - STOP if you're about to:

- Execute a `codex` command without checking its options first
- Assume you know the `codex` command syntax
- Skip the --help step "because it's simple"
- Use `exec` subcommand when interactive mode is needed

**STOP** -> Run `codex --help` first -> Review output -> Then proceed
