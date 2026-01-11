---
name: orchestration
description: "Skills for orchestrating tasks across multiple AI providers and execution environments. Parent skill category containing native-invoke and related delegation patterns."
type: category
---

# Orchestration Skills

This directory contains skills for multi-provider orchestration and task delegation.

## Overview

Orchestration skills enable Claude Code to delegate tasks to external AI providers (OpenAI Codex, Google Gemini, Cursor, OpenCode, Ollama) and coordinate their execution.

## Child Skills

| Skill | Description |
|-------|-------------|
| [native-invoke](./native-invoke/SKILL.md) | Invoke external CLIs via native Task agents |

## Related Skills

- **multi-agent-orchestration** - Higher-level routing and provider selection
- **spawn/agent** - Agent spawning with fork-terminal fallback
- **spawn/terminal** - Terminal forking for interactive CLI sessions
- **model-discovery** - Current model names for each provider

## When to Use

Use orchestration skills when:
- Delegating tasks to specialized providers (Codex for sandboxed, Gemini for large context)
- Running parallel agents across multiple providers
- Implementing fallback chains when primary providers fail
- Need clean result collection from external CLIs

## Quick Reference

```
orchestration/
└── native-invoke/    # Task-based CLI invocation
    └── SKILL.md
    └── cookbook/
        └── provider-routing.md
```

## See Also

- `.claude/ai-dev-kit/dev-tools/orchestration/` - Shell scripts for provider execution
- `.claude/ai-dev-kit/dev-tools/orchestration/config.json` - Provider configuration
- `/ai-dev-kit:delegate` - Command for manual delegation
- `/ai-dev-kit:route` - Command for intelligent routing
