# Documentation File Patterns

Complete list of documentation files to scan for project-level AI assistant guidance.

## Priority 1: Platform-Agnostic

| File | Purpose |
|------|---------|
| `AGENTS.md` | AI-agnostic project guidance (highest priority) |
| `AI.md` | General AI assistant instructions |
| `ASSISTANT.md` | Generic assistant documentation |

## Priority 2: Claude-Specific

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Claude Code specific instructions |
| `.claude/CLAUDE.md` | Claude in config directory |
| `claude.md` | Lowercase variant |

## Priority 3: Other AI Assistants

| File | Purpose |
|------|---------|
| `GEMINI.md` | Google Gemini instructions |
| `COPILOT.md` | GitHub Copilot instructions |
| `CHATGPT.md` | ChatGPT/OpenAI instructions |
| `CODEIUM.md` | Codeium assistant instructions |

## Priority 4: IDE-Specific

| File | Purpose |
|------|---------|
| `CURSOR.md` | Cursor IDE instructions |
| `WINDSURF.md` | Windsurf IDE instructions |
| `VSCODE.md` | VS Code with AI extensions |
| `JETBRAINS.md` | JetBrains AI Assistant |

## Priority 5: Terminal/CLI Tools

| File | Purpose |
|------|---------|
| `WARP.md` | Warp terminal AI instructions |
| `FIG.md` | Fig/Amazon Q instructions |
| `ZELLIJ.md` | Zellij terminal multiplexer |

## Priority 6: Cloud Development Environments

| File | Purpose |
|------|---------|
| `DEVCONTAINER.md` | VS Code Dev Containers |
| `GITPOD.md` | Gitpod workspaces |
| `CODESPACES.md` | GitHub Codespaces |

## Glob Patterns for Scanning

```bash
# Root level (most common)
*.md          # All markdown in root

# Standard patterns
AGENTS.md
CLAUDE.md
AI.md
ASSISTANT.md

# Case variations
[Aa][Gg][Ee][Nn][Tt][Ss].md
[Cc][Ll][Aa][Uu][Dd][Ee].md

# Hidden directories
.claude/*.md
.cursor/*.md
.github/*.md

# Documentation directories
docs/AGENTS.md
docs/AI.md
.docs/*.md
```

## Full Pattern List

```
# Platform-agnostic
AGENTS.md
AI.md
ASSISTANT.md

# Claude
CLAUDE.md
.claude/CLAUDE.md
.claude/README.md

# Other AI
GEMINI.md
COPILOT.md
CHATGPT.md
OPENAI.md
CODEIUM.md

# IDEs
CURSOR.md
.cursor/RULES.md
WINDSURF.md
VSCODE.md
JETBRAINS.md

# Terminals
WARP.md
FIG.md
ZELLIJ.md

# Dev environments
DEVCONTAINER.md
.devcontainer/README.md
GITPOD.md
.gitpod.md
CODESPACES.md
.codespaces/README.md

# Other documentation that may help
CONTRIBUTING.md
DEVELOPMENT.md
ARCHITECTURE.md
CONVENTIONS.md
STYLE.md
```

## File Content Expectations

### AGENTS.md Structure

```markdown
# Project Name - Agent Guidelines

## Overview
Brief project description

## Recommended Agents
Which agents work best for this project

## Key Workflows
Common development tasks

## Conventions
Code style and patterns

## Commands
Quick reference commands
```

### CLAUDE.md Structure

```markdown
# Claude Code Instructions

## Project Context
What this project does

## Key Patterns
Important code patterns

## Tools and Workflows
Available commands

## Constraints
What to avoid
```

## Scanning Best Practices

1. **Check root first** - Most docs are in project root
2. **Respect case variations** - Some use lowercase
3. **Check hidden directories** - `.claude/`, `.cursor/`
4. **Read completely** - Don't truncate important docs
5. **Preserve intent** - When consolidating, keep original meaning
6. **Note platform specifics** - Mark IDE/tool-specific instructions
