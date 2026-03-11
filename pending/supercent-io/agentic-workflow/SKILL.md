---
name: agentic-workflow
description: Practical AI agent workflows and productivity techniques. Provides optimized patterns for daily development tasks such as commands, shortcuts, Git integration, MCP usage, and session management.
allowed-tools: Read Write Bash Grep Glob
metadata:
  tags: agentic-workflow, productivity, git, mcp, commands, multi-agent
  platforms: Claude, Gemini, ChatGPT, Codex
  version: 2.0.0
  source: Claude Code Complete Guide - 70 tips (ykdojo + Ado Kukic)
---


# AI Agent Workflow (Workflow & Productivity)

## When to use this skill

- Optimize everyday AI agent work
- Integrate Git/GitHub workflows
- Use MCP servers
- Manage and recover sessions
- Apply productivity techniques

---

## 1. Key commands by agent

### Claude Code commands

| Command | Function | When to use |
|--------|------|----------|
| `/init` | Auto-generate a CLAUDE.md draft | Start a new project |
| `/usage` | Show token usage/reset time | Start of every session |
| `/clear` | Clear conversation history | When context is polluted; start a new task |
| `/context` | Context window X-Ray | When performance degrades |
| `/clone` | Clone the entire conversation | A/B experiments; backups |
| `/mcp` | Manage MCP servers | Enable/disable MCP |
| `!cmd` | Run immediately without Claude processing | Quick status checks |

### Gemini CLI commands

| Command | Function |
|--------|------|
| `gemini` | Start a conversation |
| `@file` | Add file context |
| `-m model` | Select model |

### Codex CLI commands

| Command | Function |
|--------|------|
| `codex` | Start a conversation |
| `codex run` | Run a command |

---

## 2. Keyboard shortcuts (Claude Code)

### Essential shortcuts

| Shortcut | Function | Importance |
|--------|------|--------|
| `Esc Esc` | Cancel the last task immediately | Highest |
| `Ctrl+R` | Search prompt history | High |
| `Shift+Tab` x2 | Toggle plan mode | High |
| `Tab` / `Enter` | Accept prompt suggestion | Medium |
| `Ctrl+B` | Send to background | Medium |
| `Ctrl+G` | Edit in external editor | Low |

### Editor editing shortcuts

| Shortcut | Function |
|--------|------|
| `Ctrl+A` | Move to start of line |
| `Ctrl+E` | Move to end of line |
| `Ctrl+W` | Delete previous word |
| `Ctrl+U` | Delete to start of line |
| `Ctrl+K` | Delete to end of line |

---

## 3. Session management

### Claude Code sessions
```bash
# Continue the last conversation
claude --continue

# Resume a specific session
claude --resume <session-name>

# Name the session during the conversation
/rename stripe-integration
```

### Recommended aliases
```bash
# ~/.zshrc or ~/.bashrc
alias c='claude'
alias cc='claude --continue'
alias cr='claude --resume'
alias g='gemini'
alias cx='codex'
```

---

## 4. Git workflow

### Auto-generate commit messages
```
"Analyze the changes, write an appropriate commit message, then commit"
```

### Auto-generate draft PR
```
"Create a draft PR from the current branch's changes.
Make the title summarize the changes, and list the key changes in the body."
```

### Use Git worktrees
```bash
# Work on multiple branches simultaneously
git worktree add ../myapp-feature-auth feature/auth
git worktree add ../myapp-hotfix hotfix/critical-bug

# Independent AI sessions per worktree
Tab 1: ~/myapp-feature-auth → new feature development
Tab 2: ~/myapp-hotfix → urgent bug fix
Tab 3: ~/myapp (main) → keep main branch
```

### PR review workflow
```
1. "Run gh pr checkout 123 and summarize this PR's changes"
2. "Analyze changes in src/auth/middleware.ts. Check for security issues or performance problems"
3. "Is there a way to make this logic more efficient?"
4. "Apply the improvements you suggested and run tests"
```

---

## 5. Using MCP servers (Multi-Agent)

### Key MCP servers

| MCP server | Function | Use case |
|----------|------|------|
| Playwright | Control web browser | E2E tests |
| Supabase | Database queries | Direct DB access |
| Firecrawl | Web crawling | Data collection |
| Gemini-CLI | Large-scale analysis | 1M+ token analysis |
| Codex-CLI | Run commands | Build, deploy |

### MCP usage examples
```bash
# Gemini: large-scale analysis
> ask-gemini "@src/ Analyze the structure of the entire codebase"

# Codex: run commands
> shell "docker-compose up -d"
> shell "npm test && npm run build"
```

### MCP optimization
```bash
# Disable unused MCP servers
/mcp

# Recommended numbers
# - MCP servers: fewer than 10
# - Active tools: fewer than 80
```

---

## 6. Multi-Agent workflow patterns

### Orchestration pattern
```
[Claude] Plan → [Gemini] Analysis/research → [Claude] Write code → [Codex] Run/test → [Claude] Synthesize results
```

### Practical example: API design + implementation + testing
```
1. [Claude] Design API spec using the skill
2. [Gemini] ask-gemini "@src/ Analyze existing API patterns" - large-scale codebase analysis
3. [Claude] Implement code based on the analysis
4. [Codex] shell "npm test && npm run build" - test and build
5. [Claude] Create final report
```

### TDD workflow
```
"Work using TDD. First write a failing test,
then write code that makes the test pass."

# The AI:
# 1. Write a failing test
# 2. git commit -m "Add failing test for user auth"
# 3. Write minimal code to pass the test
# 4. Run tests → confirm they pass
# 5. git commit -m "Implement user auth to pass test"
```

---

## 7. Container workflow

### Docker container setup
```dockerfile
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
    curl git tmux vim nodejs npm python3 python3-pip
RUN curl -fsSL https://claude.ai/install.sh | sh
WORKDIR /workspace
CMD ["/bin/bash"]
```

### Safe experimentation environment
```bash
# Build and run the container
docker build -t ai-sandbox .
docker run -it --rm \
  -v $(pwd):/workspace \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  ai-sandbox

# Do experimental work inside the container
```

---

## 8. Troubleshooting

### When context is overloaded
```bash
/context  # Check usage
/clear    # Reset context

# Or create HANDOFF.md and start a new session
```

### Cancel a task
```
Esc Esc  # Cancel the last task immediately
```

### When performance degrades
```bash
# Check MCP/tool counts
/mcp

# Disable unnecessary MCP servers
# Reset context
```

---

## Quick Reference Card

```
=== Essential commands ===
/clear      reset context
/context    check usage
/usage      check tokens
/init       generate project description file
!command    run immediately

=== Shortcuts ===
Esc Esc     cancel task
Ctrl+R      search history
Shift+Tab×2 plan mode
Ctrl+B      background

=== CLI flags ===
--continue  continue conversation
--resume    resume session
-p "prompt" headless mode

=== Multi-Agent ===
Claude      plan/code generation
Gemini      large-scale analysis
Codex       run commands

=== Troubleshooting ===
Context overloaded → /clear
Cancel task → Esc Esc
Performance degradation → check /context
```
