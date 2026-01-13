# compound-docs

Capture solved problems as searchable documentation with pattern detection.

## Philosophy

> Each documented solution compounds your team's knowledge. The first time 
> you solve a problem takes research. Document it, and the next occurrence 
> takes minutes. Knowledge compounds.

## Prior Art

This skill is inspired by [Every.to's compound-engineering plugin](https://github.com/EveryInc/compound-engineering-plugin), simplified and generalized for use with any tech stack.

Key differences from the original:
- Removed CORA/Rails-specific terminology and enums
- Simplified categories (developer-experience, deployment, ui, integration, performance, testing)
- Agent-extensible schema - the agent can add new enum values as needed
- Removed severity field
- Interactive CLI setup via `skz add compound-docs`

## Installation

```bash
skz add compound-docs
```

## Usage

The skill auto-triggers when you say things like "that worked" or "it's fixed". You can also manually invoke it with `/compound`.

## Files

- `SKILL.md` - Main skill instructions and workflow
- `schema.yaml` - Frontmatter validation schema (agent-editable)
- `skill.json` - Skill metadata and setup prompts
