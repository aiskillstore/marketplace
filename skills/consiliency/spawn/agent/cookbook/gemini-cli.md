# Purpose

Create a new Gemini CLI agent to execute the command

## Variables

DEFAULT_MODEL: gemini-3-pro
HEAVY_MODEL: gemini-3-deep-think
BASE_MODEL: gemini-3-pro
FAST_MODEL: gemini-3-flash-lite
MODEL_ROUTING: auto
INTERACTIVE_MODE: true

## Execution Modes

### Native Task Agent (Recommended for automation)
Use Claude Code's native Task agents for non-interactive Gemini execution:
- Parallel execution with other providers
- Clean result collection via TaskOutput
- Auto-recovery on auth failures

```bash
# Native agent compatible - one-shot with model selection
gemini --model <MODEL> --yolo "<prompt>"
```

Gemini CLI works well with native agents because:
- One-shot mode (positional prompt) exits cleanly after completion
- No special flags needed for non-interactive execution
- `--yolo` auto-approves all actions

### Fork-Terminal (For interactive sessions)
Use fork-terminal when you need:
- Interactive session that stays open (`-i` flag)
- Session resume capability
- Real-time streaming output

## Instructions

### Model Selection
- Gemini CLI uses auto-routing by default (simple prompts → Flash, complex → Pro)
- For the `--model` or `-m` argument, use DEFAULT_MODEL if not specified
- If 'fast' is requested, use FAST_MODEL (gemini-3-flash-lite)
- If 'heavy' is requested, use HEAVY_MODEL (gemini-3-deep-think)
- For stable production use: gemini-3-pro or gemini-3-flash-lite
- Use `/model` command in session to switch to Pro routing for most capable model

### Permission Mode
- Always run with `--yolo` or `-y` for automatic approval of all actions
- Alternative: use `--approval-mode yolo` for the same effect
- For auto-approve edits only: `--approval-mode auto_edit`

### Approval Modes
- `default` - Prompt for approval on each action
- `auto_edit` - Auto-approve edit tools only
- `yolo` - Auto-approve all tools (equivalent to `-y`)

### Interactive Mode Behavior

> **CRITICAL**: Gemini CLI has two distinct behaviors:
> - Positional prompt (no flag): One-shot mode, exits after completion
> - `-i/--prompt-interactive`: Executes prompt AND stays in interactive mode
>
> Use `-i` flag to stay interactive after prompt completion.

- When `INTERACTIVE_MODE: true` (default):
  - **With prompt**: Use `-i` flag: `gemini -i "<prompt>"`
  - **Without prompt**: Launch directly: `gemini`
- When `INTERACTIVE_MODE: false`:
  - **With prompt**: Use positional argument: `gemini "<prompt>"`
  - **Without prompt**: Launch in interactive mode: `gemini`

### Command Construction

**No prompt (always interactive):**
```bash
gemini --model <MODEL> --yolo
```

**With prompt + INTERACTIVE_MODE true (DEFAULT):**
```bash
# Use -i to stay interactive after prompt completes
gemini --model <MODEL> --yolo -i "<prompt>"
```

**With prompt + INTERACTIVE_MODE false (one-shot execution):**
```bash
# Positional prompt - exits after completion
gemini --model <MODEL> --yolo "<prompt>"
```

**Resume previous session:**
```bash
gemini --model <MODEL> --yolo --resume latest
```

**REQUIRED STEPS** - Do not skip:

1. **STOP** - Before executing the `gemini` command, you MUST first run the command with the --help flag:

   Example:
   ```
   gemini --help
   ```

2. Review the help output to understand available options
3. Only THEN proceed to fork the terminal with the full `gemini` command

## Key Flags Reference

| Flag | Description |
|------|-------------|
| `-m, --model <MODEL>` | Model to use (gemini-3-pro, gemini-3-deep-think, gemini-3-flash-lite) |
| `-y, --yolo` | Auto-approve all actions (YOLO mode) |
| `--approval-mode <MODE>` | Set approval mode (default, auto_edit, yolo) |
| `-i, --prompt-interactive <PROMPT>` | Execute prompt and stay interactive |
| `-s, --sandbox` | Run in sandbox mode |
| `-r, --resume <SESSION>` | Resume previous session (use "latest" or index) |
| `--list-sessions` | List available sessions |
| `-e, --extensions <LIST>` | Specify extensions to use |
| `-l, --list-extensions` | List available extensions |
| `--allowed-tools <LIST>` | Tools allowed without confirmation |
| `--include-directories <DIRS>` | Additional workspace directories |
| `-o, --output-format <FORMAT>` | Output format (text, json, stream-json) |
| `-d, --debug` | Enable debug mode |

## Clean Output Capture

When `LOG_AGENT_OUTPUT` is true (default), append `-o json` to get clean JSON output:

```bash
# One-shot with JSON output (for capture)
gemini --model <MODEL> --yolo -o json "<prompt>"
```

The JSON output contains the agent's response without startup noise, debug messages, or ANSI codes.

**Note**: `-o json` produces one-shot output (no interactive mode). Use this when you need to capture the agent's response for later processing.

## Red Flags - STOP if you're about to:

- Execute a `gemini` command without checking its options first
- Assume you know the `gemini` command syntax
- Skip the --help step "because it's simple"
- Use positional prompt when interactive mode is needed (use `-i` instead)
- Confuse `-p` (deprecated) with `-i` (correct for interactive)

**STOP** -> Run `gemini --help` first -> Review output -> Then proceed
