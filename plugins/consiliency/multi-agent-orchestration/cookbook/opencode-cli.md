# OpenCode CLI Delegation

Delegate tasks using the OpenCode CLI for provider-agnostic execution.

## When to Use

- Fallback when primary providers are rate-limited
- Provider-agnostic execution with custom models
- Quick headless runs where you want a single CLI interface

## Prerequisites

```bash
which opencode
opencode auth
```

## Delegation Command

```bash
.claude/ai-dev-kit/dev-tools/orchestration/providers/opencode/execute.sh "task" [model]
```

## Model Format

Use `provider/model` format (for example: `anthropic/claude-sonnet-4-5`).

## Output Handling

The wrapper returns JSON with `success`, `output`, `agent`, and `model` fields.
