# Advanced Skill Template

Use this template for complex skills requiring multiple files.

## Directory Structure

```
{skill-name}/
├── SKILL.md           # Overview and navigation (under 300 lines)
├── reference.md       # Detailed guidelines
├── examples.md        # Extended examples (optional)
├── scripts/           # Automation scripts (optional)
│   └── validate.sh
└── templates/         # Reusable templates (optional)
    └── output.md
```

## SKILL.md Template

```yaml
---
name: {skill-name}
description: |
  {What it does}. {Additional context}.
  Use when {trigger conditions}.
---

# {Skill Title}

{One sentence overview}

## Quick Start

For {common task}:
1. {Step 1}
2. {Step 2}
3. {Step 3}

For {other task}:
See [reference.md](reference.md)

## Workflow: {Primary Workflow}

```
Progress:
- [ ] {Phase 1}
- [ ] {Phase 2}
- [ ] {Phase 3}
- [ ] {Validation}
```

### {Phase 1}

{Core instructions - keep brief}

### {Phase 2}

{Core instructions}

For advanced options, see [reference.md](reference.md#phase-2-details)

### {Phase 3}

{Core instructions}

## Quick Reference

| {Concept} | {Description} |
|-----------|---------------|
| {item} | {brief explanation} |

## Common Patterns

### Pattern: {Name}

{Brief description with example}

See [examples.md](examples.md) for more patterns.

## Validation

Run checklist before completing:

```
Validation:
- [ ] {Check 1}
- [ ] {Check 2}
- [ ] {Check 3}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| {problem} | {fix} |

Full troubleshooting: [reference.md](reference.md#troubleshooting)
```

## reference.md Template

```markdown
# {Skill Name} Reference

Detailed guidelines for {skill purpose}.

## {Topic 1}

### {Subtopic}

{Detailed explanation}

### {Subtopic}

{Detailed explanation with examples}

## {Topic 2}

{More detailed content}

## Phase 2 Details

{Advanced options referenced from SKILL.md}

## Troubleshooting

### {Issue 1}

**Symptoms**: {what user sees}

**Cause**: {why it happens}

**Solution**: {how to fix}

### {Issue 2}

{Similar structure}
```

## examples.md Template

```markdown
# {Skill Name} Examples

Extended examples for common scenarios.

## Example 1: {Scenario}

### Context

{Setup and requirements}

### Input

{What user provides}

### Process

1. {Step taken}
2. {Step taken}

### Output

{Result produced}

## Example 2: {Scenario}

{Similar structure}
```

## Key Principles

1. **SKILL.md stays lean**: Overview, navigation, quick reference only
2. **One level deep**: All references link directly from SKILL.md
3. **Progressive disclosure**: Load details only when needed
4. **Consistent structure**: Same patterns across all files
