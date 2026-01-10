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

name: {{SKILL_NAME}}
description: {{SKILL_DESCRIPTION}}
---

# {{Skill Title}}

{{BRIEF_OVERVIEW}}

## When to Use This Skill

- {{USE_CASE_1}}
- {{USE_CASE_2}}
- {{USE_CASE_3}}

## What This Skill Does

1. {{CAPABILITY_1}}
2. {{CAPABILITY_2}}
3. {{CAPABILITY_3}}

## Core Principles

### Principle 1: {{PRINCIPLE_NAME}}

{{PRINCIPLE_EXPLANATION}}

### Principle 2: {{PRINCIPLE_NAME}}

{{PRINCIPLE_EXPLANATION}}

## Workflow

### Step 1: {{STEP_NAME}}

{{STEP_INSTRUCTIONS}}

### Step 2: {{STEP_NAME}}

{{STEP_INSTRUCTIONS}}

## Best Practices

- {{BEST_PRACTICE_1}}
- {{BEST_PRACTICE_2}}

## Anti-Patterns

- {{ANTI_PATTERN_1}}
- {{ANTI_PATTERN_2}}

## Examples

### Example 1: {{EXAMPLE_NAME}}

**Scenario:** {{SCENARIO_DESCRIPTION}}

**Approach:**

```
{{EXAMPLE_APPROACH}}
```

## Reference Files

This skill includes reference files in `references/`:

- `{{REFERENCE_FILE}}.md`: {{REFERENCE_DESCRIPTION}}

---

## Template Reference

### Required Structure

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description)
│   └── Markdown body
└── Bundled Resources (optional)
    ├── scripts/       - Executable code
    ├── references/    - Documentation
    └── assets/        - Output files
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique kebab-case identifier |
| `description` | Yes | Third-person description: "This skill should be used when..." |

### Body Structure Requirements

1. **When to Use** - Clear trigger conditions
2. **What This Skill Does** - Capabilities list
3. **Core Principles** - Domain frameworks (non-obvious knowledge)
4. **Workflow** - Step-by-step process
5. **Best Practices** - Do's
6. **Anti-Patterns** - Don'ts
7. **Examples** - Concrete usage scenarios

### Progressive Disclosure Design

| Level | Content | Size Guidance |
|-------|---------|---------------|
| Metadata | name + description | ~100 words |
| SKILL.md body | Core workflow | <5k words |
| References | Detailed knowledge | Unlimited |

### Quality Checklist

- [ ] Description uses third-person ("This skill should be used when...")
- [ ] Knowledge is non-obvious (not inherent to Claude)
- [ ] Workflow is actionable with clear steps
- [ ] Examples are concrete and domain-specific
- [ ] Anti-patterns help avoid common mistakes
- [ ] Large content moved to references/ (keeps SKILL.md lean)
- [ ] No placeholder text remains
