# Purpose

Create a new Claude Code agent to execute the command

## Variables

DEFAULT_MODEL: sonnet
HEAVY_MODEL: opus
BASE_MODEL: sonnet
FAST_MODEL: haiku
INTERACTIVE_MODE: true

## Instructions

### Model Selection
- For the `--model` argument, use DEFAULT_MODEL if not specified
- If 'fast' is requested, use FAST_MODEL
- If 'heavy' is requested, use HEAVY_MODEL

### Permission Mode
- Always run with `--dangerously-skip-permissions`

### Interactive Mode Behavior

> **CRITICAL**: When a prompt is provided and INTERACTIVE_MODE is true, you MUST chain
> two commands with `&&`. The first command executes the prompt, the second keeps
> Claude in interactive mode. Forgetting the `&& claude --continue` part will cause
> Claude to exit after completing the task.

- Never use `-p` (print mode) - we want the UI
- When `INTERACTIVE_MODE: true` (default):
  - **With prompt**: Execute prompt, THEN chain `&& claude --continue` to stay interactive
  - **Without prompt**: Launch directly in interactive mode
- When `INTERACTIVE_MODE: false`:
  - **With prompt**: Execute prompt, exit to bash
  - **Without prompt**: Launch in interactive mode

### Command Construction

**No prompt (always interactive):**
```bash
claude --model <MODEL> --dangerously-skip-permissions
```

**With prompt + INTERACTIVE_MODE true (DEFAULT):**
```bash
# IMPORTANT: Must chain with && to stay interactive after prompt completes
claude --model <MODEL> --dangerously-skip-permissions "<prompt>" && claude --model <MODEL> --dangerously-skip-permissions --continue
```

**With prompt + INTERACTIVE_MODE false:**
```bash
claude --model <MODEL> --dangerously-skip-permissions "<prompt>"
```

**REQUIRED STEPS** - Do not skip:

1. **STOP** - Before executing the `claude` command, you MUST first run the command with the --help flag:

   Example:
   ```
   claude --help
   ```


2. Review the help output to understand available options
3. Only THEN proceed to fork the terminal with the full `claude` command

## Clean Output Capture

When `LOG_AGENT_OUTPUT` is true (default), use print mode with JSON output:

```bash
# One-shot with JSON output (for capture)
claude --model <MODEL> --dangerously-skip-permissions -p --output-format json "<prompt>"
```

The JSON output contains the agent's response without UI elements, ANSI codes, or interactive features.

**Note**: `-p` (print mode) is required for JSON output. This disables the interactive TUI - use this when you need to capture the agent's response for later processing.

## Red Flags - STOP if you're about to:

- Execute a `claude` command without checking its options first
- Assume you know the `claude` command syntax
- Skip the --help step "because it's simple"

**STOP** -> Run `claude --help` first -> Review output -> Then proceed
