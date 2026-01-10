---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: skill-creator
---

---

name: {{AGENT_NAME}}
color: {{COLOR}}
description: {{AGENT_DESCRIPTION}}
model: {{MODEL}}
tools: {{TOOLS}}
skills: {{SKILLS}}
---

# Purpose

{{PURPOSE_STATEMENT}}

## Instructions

When invoked, follow these steps:

1. {{STEP_1}}
2. {{STEP_2}}
3. {{STEP_3}}

## Best Practices

- {{BEST_PRACTICE_1}}
- {{BEST_PRACTICE_2}}
- {{BEST_PRACTICE_3}}

## Output Format

{{OUTPUT_FORMAT_DESCRIPTION}}

```
{{OUTPUT_TEMPLATE}}
```

---

## Template Reference

### Required Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique kebab-case identifier (e.g., `code-reviewer`) |
| `description` | Yes | Action-oriented description starting with "Use PROACTIVELY..." or "Specialist for..." |
| `tools` | Yes | Comma-separated list of allowed tools |

### Optional Frontmatter Fields

| Field | Default | Description |
|-------|---------|-------------|
| `model` | sonnet | Model to use: `haiku`, `sonnet`, or `opus` |
| `color` | - | Display color: red, blue, green, yellow, purple, orange, pink, cyan |
| `skills` | - | Comma-separated skill names to load |

### Available Tools

**File Operations:** Read, Write, Edit, MultiEdit, Glob, Grep, LS
**Execution:** Bash, Task, TodoWrite
**Web:** WebFetch, WebSearch
**User Interaction:** AskUserQuestion
**MCP Tools:** mcp__*

### Body Structure Requirements

1. **Purpose Section** - Clear role definition
2. **Instructions Section** - Numbered step-by-step workflow
3. **Best Practices** - Domain-specific guidance
4. **Output Format** - Expected response structure

### Quality Checklist

- [ ] Name is kebab-case and descriptive
- [ ] Description explains WHEN to use the agent
- [ ] Tools list is minimal (only what's needed)
- [ ] Instructions are actionable and numbered
- [ ] Best practices are domain-specific, not generic
- [ ] Output format is clearly defined
- [ ] No placeholder text remains
