---
name: orchestration:native-invoke
description: "Invoke external AI CLIs via native Task agents (Claude, Codex, Gemini, Cursor). Primary mode for multi-provider orchestration with fork-terminal fallback for auth."
type: documentation
---

# Purpose

> **Note**: This is a documentation/guide skill. It provides instructions for invoking
> external AI CLIs using Claude Code's native Task agents. Read this skill to learn
> the patterns, then use the Task tool manually with `subagent_type="general-purpose"`.

Invoke external AI coding CLIs using Claude Code's native Task agents. This is the primary mode for multi-provider orchestration, with fork-terminal as fallback for authentication.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DEFAULT_AGENT | gemini | Agent to use when not explicitly specified |
| ENABLED_CODEX | true | Enable OpenAI Codex via native agent |
| ENABLED_GEMINI | true | Enable Google Gemini via native agent |
| ENABLED_CURSOR | true | Enable Cursor Agent via native agent |
| RUN_IN_BACKGROUND | true | Run agents asynchronously |
| PARALLEL_EXECUTION | true | Launch multiple agents in parallel |
| AUTO_RETRY_ON_AUTH | true | Auto-retry with fork-terminal on auth failure |
| READ_ONLY_MODE | true | Prevent agents from modifying codebase |
| CLEANUP_AGENT_FILES | true | Clean up any files agents write to repo |

## Prerequisites

### CLI Permissions for Subagents

Native Task agents (subagents) require pre-approved permissions to execute CLI commands.
Without these, the Bash tool will be "auto-denied (prompts unavailable)".

**Required in `.claude/settings.json`**:
```json
{
  "permissions": {
    "allow": [
      "Bash(codex:*)",
      "Bash(gemini:*)",
      "Bash(cursor-agent:*)"
    ]
  }
}
```

**Setup**: Run `/ai-dev-kit:setup` to configure permissions automatically.

**Manual**: Add permissions via Claude Code settings or approve when prompted.

**Fallback**: If permissions are denied, use fork-terminal for interactive execution.

## Instructions

**MANDATORY** - You MUST follow the Workflow steps below in order. Do not skip steps.

### Agent Selection

1. **Explicit request**: If user specifies an agent, use that agent
2. **No agent specified**: Use DEFAULT_AGENT
3. **Check enabled**: Verify the ENABLED_* flag is true before proceeding

### Reading Cookbooks

- Based on the selected agent, read the appropriate cookbook from `../spawn/agent/cookbook/`
- You MUST run `--help` on the CLI before constructing the command
- Follow cookbook instructions for non-interactive flags

## Red Flags - STOP and follow Cookbook

If you're about to:
- Launch a native agent without reading the cookbook first
- Execute a CLI command without running --help
- Skip steps because "this is simple"
- Use interactive flags in non-interactive context

**STOP** -> Read the appropriate cookbook file -> Check --help -> Then proceed

> **Critical**: Native agents cannot handle TTY input. Always use non-interactive flags:
> - Codex: `codex exec --full-auto`
> - Cursor: `cursor-agent --force -p`
> - Gemini: Use positional prompt (not `-i`)

## Workflow

**MANDATORY CHECKPOINTS** - Verify each before proceeding:

1. [ ] Understand the user's request
2. [ ] **SELECT AGENT(S)**: Determine which agent(s) to use
3. [ ] READ: Cookbook for each selected agent from `../spawn/agent/cookbook/`
4. [ ] **RUN HELP**: Execute `<cli> --help` to verify available flags
5. [ ] **CONSTRUCT COMMAND**: Build non-interactive command per cookbook
6. [ ] **CHECKPOINT**: Confirm cookbook instructions were followed
7. [ ] Execute via Task tool with `run_in_background: true`
8. [ ] Collect results via TaskOutput
9. [ ] **ON AUTH FAILURE**: Trigger fork-terminal fallback (see Auth Recovery)

## Read-Only vs Write Mode

**Default: READ_ONLY_MODE = true**

When READ_ONLY_MODE is enabled, agents should only analyze and report - not modify files.

### Read-Only Flags by Provider

| Provider | Read-Only Command | Write Mode Command |
|----------|------------------|-------------------|
| **Codex** | `codex exec --sandbox read-only --full-auto` | `codex exec --sandbox workspace-write --full-auto` |
| **Gemini** | `gemini --sandbox --yolo` | `gemini --yolo` |
| **Cursor** | `cursor-agent -p` (no --force) | `cursor-agent --force -p` |

### Prompting for Read-Only

Always include in prompt when READ_ONLY_MODE is true:
```
"Do NOT modify any files. Only analyze and report findings.
If you would normally write to a file, instead return the content in your response."
```

## Worktree Isolation (Recommended for Write Mode)

When agents need write access, use git worktrees for true isolation:

```bash
# Create isolated worktree for agent work
git worktree add /tmp/agent-workspace-<id> -b agent/<provider>-<task>

# Run agent in worktree
cd /tmp/agent-workspace-<id>
<agent-command>

# Review changes
git diff

# If approved, merge back
git checkout main
git merge agent/<provider>-<task>

# Cleanup
git worktree remove /tmp/agent-workspace-<id>
git branch -d agent/<provider>-<task>
```

### Benefits of Worktree Isolation
- **Full write access**: Agents can make any changes freely
- **Selective merge**: Only merge approved changes
- **No cleanup needed**: Discard worktree to reject changes
- **Parallel agents**: Multiple worktrees for parallel providers
- **Branch history**: Changes are tracked in git

### When to Use Worktrees
| Scenario | Approach |
|----------|----------|
| Analysis/review only | READ_ONLY_MODE + CLI flags |
| Single file edit | Write mode with cleanup |
| Multi-file refactor | Worktree isolation |
| Experimental changes | Worktree (easy to discard) |
| Parallel agent work | Separate worktrees per agent |

## Cleanup Protocol

When CLEANUP_AGENT_FILES is true (default) and NOT using worktrees:

1. **Check for new files** in the working directory
2. **Preserve valuable content** by reading files before deletion
3. **Delete agent-created files** (e.g., `*_REVIEW_OUTPUT.md`, `*_analysis.json`)
4. **Log cleanup actions** for audit trail

```python
# Cleanup pattern
cleanup_patterns = [
    "*_REVIEW_OUTPUT.md",
    "*_analysis.json",
    "*_findings.md",
    "agent_output_*.txt"
]
```

## Cookbook

### Codex (OpenAI)
- IF: User requests Codex/OpenAI and 'ENABLED_CODEX' is true
- THEN: Read `../spawn/agent/cookbook/codex-cli.md`
- Native command pattern (read-only):
```bash
codex exec --sandbox read-only --full-auto --model gpt-5.2-codex "<prompt>"
```
- Native command pattern (write mode):
```bash
codex exec --sandbox workspace-write --full-auto --model gpt-5.2-codex "<prompt>"
```
- Auth failure pattern: "Please log in", "authentication required"
- Login command: `codex login`

### Gemini (Google)
- IF: User requests Gemini/Google and 'ENABLED_GEMINI' is true
- THEN: Read `../spawn/agent/cookbook/gemini-cli.md`
- Native command pattern (read-only):
```bash
gemini --model gemini-3-pro --sandbox --yolo "<prompt>"
```
- Native command pattern (write mode):
```bash
gemini --model gemini-3-pro --yolo "<prompt>"
```
- Auth failure pattern: "Please authenticate", "run `gemini auth`"
- Login command: `gemini auth login`

### Cursor
- IF: User requests Cursor and 'ENABLED_CURSOR' is true
- THEN: Read `../spawn/agent/cookbook/cursor-cli.md`
- Native command pattern (read-only - prompts for approval):
```bash
cursor-agent --model claude-sonnet-4.5 -p "<prompt>"
```
- Native command pattern (write mode - auto-approves):
```bash
cursor-agent --model claude-sonnet-4.5 --force -p "<prompt>"
```
- Auth failure pattern: "Please log in", browser popup needed
- Login command: `cursor-agent login`

## Auth Recovery

When a native agent reports an authentication failure:

1. **Detect**: Check output for auth failure patterns
2. **Fork for login**: Use fork-terminal with login command
3. **Wait**: Monitor for terminal close
4. **Retry**: Re-launch native agent

```python
# Auth recovery flow
def handle_auth_failure(provider: str, original_prompt: str):
    login_commands = {
        "codex": "codex login",
        "gemini": "gemini auth login",
        "cursor": "cursor-agent login"
    }

    # Fork terminal for interactive login
    fork_terminal(login_commands[provider], wait_for_close=True)

    # After terminal closes, retry native invocation
    return invoke_native(provider, original_prompt)
```

## Parallel Invocation

To invoke multiple agents in parallel, use a single message with multiple Task tool calls:

```
# Launch Gemini, Codex, and Cursor in parallel
Task(subagent_type="general-purpose", run_in_background=true, prompt="gemini ...")
Task(subagent_type="general-purpose", run_in_background=true, prompt="codex ...")
Task(subagent_type="general-purpose", run_in_background=true, prompt="cursor ...")
```

Collect results:
```
TaskOutput(task_id="...", block=false)  # Check progress
TaskOutput(task_id="...", block=true)   # Wait for completion
```

## Result Collection

Native agents return results via TaskOutput tool:

| Parameter | Value | Behavior |
|-----------|-------|----------|
| `block=false` | Check status | Non-blocking progress check |
| `block=true` | Wait for completion | Blocks until agent finishes |
| `timeout` | milliseconds | Max wait time before timeout |

### Example Collection Pattern

```
# Check progress (non-blocking)
TaskOutput(task_id="abc123", block=false)

# Wait for completion (blocking)
TaskOutput(task_id="abc123", block=true, timeout=120000)
```

## Comparison: Native vs Fork-Terminal

| Aspect | Native Task Agent | Fork-Terminal |
|--------|-------------------|---------------|
| **Parallel execution** | Excellent | Good |
| **Result collection** | TaskOutput (clean) | File parsing |
| **TTY/Interactive** | NO | YES |
| **Auth handling** | Reports failure | Interactive login |
| **Resume capability** | YES (agent ID) | NO |

**Use Native** when:
- Automating multi-provider tasks
- Parallel execution needed
- Clean result collection required

**Use Fork-Terminal** when:
- Interactive mode needed
- Browser-based auth required
- Real-time streaming output needed
