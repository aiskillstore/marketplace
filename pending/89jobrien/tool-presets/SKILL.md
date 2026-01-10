---
name: tool-presets
description: Standardized tool set definitions for Claude Code agents ensuring consistent tool access across similar agent types
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: skill
---

# Tool Presets Skill

Standardized tool set definitions for Claude Code agents. Use these presets to ensure consistent tool access across similar agent types.

## Available Presets

| Preset | Tools | Best For |
|--------|-------|----------|
| `dev-tools` | Read, Write, Edit, Bash | Development/coding agents |
| `file-ops` | Read, Write, Edit, Grep, Glob | File manipulation agents |
| `analysis` | Read, Grep, Glob, Bash | Code analysis agents |
| `research` | Read, Write, WebSearch, WebFetch | Research agents |
| `orchestration` | Read, Write, Edit, Task, TodoWrite | Coordinator agents |
| `full-stack` | All tools | Comprehensive agents |

## Usage

Reference a preset in your agent's frontmatter:

```yaml
---
name: my-agent
description: Agent description
tools: Read, Write, Edit, Bash  # Use dev-tools preset pattern
skills: tool-presets
---
```

## Preset Selection Guide

### When to use `dev-tools`

- Writing or modifying code
- Running build/test commands
- General development tasks

### When to use `file-ops`

- Searching codebases
- Refactoring across files
- Code analysis without execution

### When to use `analysis`

- Read-only code review
- Pattern detection
- Static analysis

### When to use `research`

- Documentation lookup
- External API research
- Web-based information gathering

### When to use `orchestration`

- Multi-agent coordination
- Complex task breakdown
- Workflow management

### When to use `full-stack`

- Comprehensive agents needing all capabilities
- Meta agents that delegate to others

## Reference Files

For detailed tool lists per preset, see:

- `dev-tools.md` - Development tools preset
- `file-ops.md` - File operations preset
- `analysis.md` - Code analysis preset
- `research.md` - Research tools preset
- `orchestration.md` - Multi-agent orchestration preset
