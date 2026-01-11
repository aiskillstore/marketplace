---
name: spawn:agent
description: "Spawn an AI coding agent in a new terminal (Claude, Codex, Gemini, Cursor, OpenCode, Copilot). Defaults to Claude Code if unspecified."
---

# Purpose

Spawn an AI coding agent in a new terminal window. Follow the 'Instructions', execute the 'Workflow', based on the 'Cookbook'.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DEFAULT_AGENT | claude-code | Agent to use when not explicitly specified |
| ENABLED_CLAUDE_CLI | true | Enable Claude Code agent |
| ENABLED_CODEX_CLI | true | Enable OpenAI Codex agent |
| ENABLED_GEMINI_CLI | true | Enable Google Gemini agent |
| ENABLED_CURSOR_CLI | true | Enable Cursor agent |
| ENABLED_OPEN_CODE_CLI | true | Enable OpenCode agent |
| ENABLED_COPILOT_CLI | true | Enable GitHub Copilot agent |
| LOG_TO_FILE | false | Write full terminal output to debug file |
| LOG_AGENT_OUTPUT | true | Write clean agent JSON response to file |
| READ_CAPTURED_OUTPUT | false | Read and display agent output after spawn |
| AGENTIC_CODING_TOOLS | claude-code, codex-cli, gemini-cli, cursor-cli, opencode-cli, copilot-cli | Available agentic tools |

## Instructions

**MANDATORY** - You MUST follow the Workflow steps below in order. Do not skip steps.

### Agent Selection

1. **Explicit request**: If user specifies an agent (e.g., "use gemini", "spawn codex"), use that agent
2. **No agent specified**: Use DEFAULT_AGENT (claude-code)
3. **Check enabled**: Verify the ENABLED_*_CLI flag is true before proceeding

### Reading Cookbooks

- Based on the selected agent, follow the 'Cookbook' section to read the appropriate .md file
- You MUST read and execute the appropriate cookbook file before spawning the agent

## Red Flags - STOP and follow Cookbook

If you're about to:
- Spawn an agent without reading the cookbook first
- Execute a CLI command without running --help
- Skip steps because "this is simple"
- Run a CLI agent with a prompt but without checking INTERACTIVE_MODE requirements

**STOP** -> Read the appropriate cookbook file -> Follow its instructions -> Then proceed

> **Common Mistake**: When spawning agentic CLIs (Claude, Codex, Gemini) with a prompt,
> most require command chaining (e.g., `&& claude --continue`) to stay in interactive
> mode after the prompt completes. Always check the cookbook for the correct pattern.

### Spawn Summary User Prompt

- IF: The user requests spawning an agent with a summary of the conversation
- THEN:
  - Read and REPLACE the <user_prompt_summary> and <agent_response_summary> fields in './prompts/fork-summary-user-prompt.md' with the history of the conversation between you and the user.
  - Include the next users request in the `Next User Request` field.
  - This will be what you pass into the PROMPT field of the agentic coding tool.
  - Spawn the agent with: fork_terminal(command: str, capture=False, log_to_file=False, log_agent_output=True)
- Examples:
    - "Spawn agent use claude code to <xyz> with a summary"
    - "spin up a new terminal with <xyz> with claude code. Include a summary of the conversation."
    - "create a new agent with claude code to <xyz>. Summarize work so far."
    - "spawn agent use gemini to <xyz> with a summary"

## Workflow

**MANDATORY CHECKPOINTS** - Verify each before proceeding:

1. [ ] Understand the user's request
2. [ ] **SELECT AGENT**: Determine which agent (explicit or DEFAULT_AGENT)
3. [ ] READ: './fork_terminal.py' to understand the tooling
4. [ ] Follow the Cookbook (read the appropriate .md file for selected agent)
5. [ ] **CHECKPOINT**: Confirm cookbook instructions were followed (e.g., ran --help)
6. [ ] Execute fork_terminal(command: str, capture=False, log_to_file=False, log_agent_output=True)
7. [ ] IF 'READ_CAPTURED_OUTPUT' is true: Read and display the agent output using read_fork_output()

## Cookbook

### Claude Code (Default)
- IF: User requests Claude Code OR no agent explicitly specified
- THEN: Read and execute './cookbook/claude-code.md'
- Examples:
    - "Spawn an agent to <xyz>"
    - "Fork terminal to <xyz>" (no agent specified = claude-code)
    - "Spawn agent use claude code to <xyz>"
    - "spin up a new terminal with claude code"

### Codex CLI
- IF: User requests Codex/OpenAI agent and 'ENABLED_CODEX_CLI' is true
- THEN: Read and execute './cookbook/codex-cli.md'
- Examples:
    - "Spawn agent use codex to <xyz>"
    - "create a new terminal with codex cli to <xyz>"
    - "spawn openai agent to <xyz>"

### Gemini CLI
- IF: User requests Gemini/Google agent and 'ENABLED_GEMINI_CLI' is true
- THEN: Read and execute './cookbook/gemini-cli.md'
- Examples:
    - "Spawn agent use gemini to <xyz>"
    - "create a new terminal with gemini cli to <xyz>"
    - "spawn google agent to <xyz>"

### Cursor CLI
- IF: User requests Cursor agent and 'ENABLED_CURSOR_CLI' is true
- THEN: Read and execute './cookbook/cursor-cli.md'
- Examples:
    - "Spawn agent use cursor cli to <xyz>"
    - "create a new terminal with cursor to <xyz>"
    - "spawn cursor agent to <xyz>"

### OpenCode CLI
- IF: User requests OpenCode agent and 'ENABLED_OPEN_CODE_CLI' is true
- THEN: Read and execute './cookbook/opencode-cli.md'
- Examples:
    - "Spawn agent use opencode cli to <xyz>"
    - "create a new terminal with opencode to <xyz>"
    - "spawn opencode agent to <xyz>"

### Copilot CLI
- IF: User requests Copilot/GitHub agent and 'ENABLED_COPILOT_CLI' is true
- THEN: Read and execute './cookbook/copilot-cli.md'
- Examples:
    - "Spawn agent use copilot cli to <xyz>"
    - "create a new terminal with copilot to <xyz>"
    - "spawn github copilot agent to <xyz>"

## Output Retrieval

The `fork_terminal()` function supports three output controls:

| Parameter | Default | Output File | Description |
|-----------|---------|-------------|-------------|
| `log_agent_output` | `True` | `/tmp/fork-agent-*.json` | Clean agent JSON response |
| `log_to_file` | `False` | `/tmp/fork-debug-*.txt` | Full terminal output (debug) |
| `capture` | `False` | N/A | Block and return content directly |

### Parameter Combinations

| `capture` | `log_agent_output` | `log_to_file` | Behavior |
|-----------|-------------------|---------------|----------|
| `False` | `True` (default) | `False` | Returns agent JSON file path |
| `False` | `False` | `True` | Returns debug file path |
| `False` | `False` | `False` | Returns empty string |
| `True` | `True` | * | Blocks, returns agent JSON content |
| `True` | `False` | `True` | Blocks, returns debug content |

### Retrieving Output Later

When `log_agent_output=True` (default), clean agent output is logged. Use `read_fork_output(file_path)` to retrieve it:

```python
# Spawn without blocking (returns path to JSON output)
file_path = fork_terminal(cmd, log_agent_output=True)
print(f"Agent output will be at: {file_path}")

# Later, read the output when needed
output = read_fork_output(file_path, timeout=60)
```

### Debug Mode

For debugging, enable `log_to_file=True` to capture full terminal output (including stderr):

```python
# Debug mode: capture everything
file_path = fork_terminal(cmd, log_to_file=True, log_agent_output=False)
```
