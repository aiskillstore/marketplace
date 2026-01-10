# Supported Documentation Files

Complete list of documentation files this skill scans for, organized by priority and category.

## Glob Pattern

Use this pattern to find all supported files:

```
{AGENTS,CLAUDE,GEMINI,COPILOT,CHATGPT,CODEIUM,CURSOR,WINDSURF,VSCODE,JETBRAINS,WARP,FIG,ZELLIJ,DEVCONTAINER,GITPOD,CODESPACES,AI,ASSISTANT}.md
```

## Files by Category

### Priority 1: Platform-Agnostic

| File | Description |
|------|-------------|
| `AGENTS.md` | Universal AI agent guide - works across all platforms |

### Priority 2: Claude-Specific

| File | Description |
|------|-------------|
| `CLAUDE.md` | Claude Code workflows, commands, and project conventions |

### Priority 3: AI Assistants

| File | Description |
|------|-------------|
| `GEMINI.md` | Google Gemini AI assistant configuration |
| `COPILOT.md` | GitHub Copilot settings and workflows |
| `CHATGPT.md` | ChatGPT/OpenAI integration guide |
| `CODEIUM.md` | Codeium AI completion settings |

### Priority 4: IDEs & Editors

| File | Description |
|------|-------------|
| `CURSOR.md` | Cursor AI-first editor configuration |
| `WINDSURF.md` | Windsurf editor workflows |
| `VSCODE.md` | VS Code workspace settings and extensions |
| `JETBRAINS.md` | IntelliJ, WebStorm, PyCharm configurations |

### Priority 5: Terminal & CLI

| File | Description |
|------|-------------|
| `WARP.md` | Warp terminal AI commands and workflows |
| `FIG.md` | Fig terminal autocomplete scripts |
| `ZELLIJ.md` | Zellij multiplexer layouts |

### Priority 6: Development Environments

| File | Description |
|------|-------------|
| `DEVCONTAINER.md` | VS Code dev container documentation |
| `GITPOD.md` | Gitpod cloud development setup |
| `CODESPACES.md` | GitHub Codespaces configuration |

### Priority 7: Generic/Legacy

| File | Description |
|------|-------------|
| `AI.md` | General AI assistant documentation |
| `ASSISTANT.md` | Generic assistant guide |

## Content Expectations

Each documentation file typically contains:

- **Recommended agents** - Which specialized agents to use
- **Workflows** - Step-by-step processes for common tasks
- **Commands** - CLI commands, scripts, or shortcuts
- **Conventions** - Code style, naming, architecture patterns
- **Project structure** - Directory layout explanations
- **Testing** - How to run and write tests
- **Deployment** - Build and release processes

## Adding New Formats

To support additional documentation formats, add them to the appropriate priority category above and update the glob pattern.
