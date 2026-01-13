---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: command-optimization
---

---

description: {{COMMAND_DESCRIPTION}}
argument-hint: {{ARGUMENT_HINT}}
allowed-tools: {{ALLOWED_TOOLS}}
---

# {{Command Title}}

{{BRIEF_DESCRIPTION}}: $ARGUMENTS

## Current State

- {{DYNAMIC_CONTEXT_1}}: !`{{SHELL_COMMAND_1}}`
- {{DYNAMIC_CONTEXT_2}}: !`{{SHELL_COMMAND_2}}`

## Task

{{TASK_DESCRIPTION}}

## Workflow

### 1. {{STEP_NAME}}

{{STEP_INSTRUCTIONS}}

```bash
{{EXAMPLE_COMMAND}}
```

### 2. {{STEP_NAME}}

{{STEP_INSTRUCTIONS}}

### 3. {{STEP_NAME}}

{{STEP_INSTRUCTIONS}}

## Output Format

```
{{OUTPUT_TEMPLATE}}
```

## Options

| Flag | Description |
|------|-------------|
| `{{FLAG_1}}` | {{FLAG_1_DESCRIPTION}} |
| `{{FLAG_2}}` | {{FLAG_2_DESCRIPTION}} |

---

## Template Reference

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `description` | Yes | Brief description shown in command list |
| `allowed-tools` | No | Restrict tools available during execution |
| `argument-hint` | No | Usage hint shown in command help |

### Dynamic Context

Use `!` prefix for shell commands that execute when command loads:

```markdown
- Current branch: !`git branch --show-current`
- File count: !`find . -name "*.py" | wc -l`
```

### Arguments

Access command arguments with `$ARGUMENTS` placeholder:

```markdown
Process the following: $ARGUMENTS
```

### Body Structure Requirements

1. **Title** - Clear command name
2. **Current State** - Dynamic context (optional but recommended)
3. **Task** - What the command accomplishes
4. **Workflow** - Step-by-step execution
5. **Output Format** - Expected response structure
6. **Options** - Available flags/modes (if applicable)

### Tool Restrictions

Restrict tools with `allowed-tools` frontmatter:

```yaml
allowed-tools: Read, Grep, Glob
allowed-tools: Bash(git:*), Bash(npm:*)
```

### Quality Checklist

- [ ] Description is concise and action-oriented
- [ ] Dynamic context provides useful state information
- [ ] Workflow steps are clear and numbered
- [ ] Bash commands are shown for reference
- [ ] Output format is well-defined
- [ ] Options/flags documented if applicable
- [ ] No placeholder text remains
