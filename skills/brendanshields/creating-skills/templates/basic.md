# Basic Skill Template

Use this template for simple skills under 200 lines.

## Template

```yaml
---
name: {skill-name}
description: |
  {What it does}. Use when {trigger conditions}.
---

# {Skill Title}

{One sentence overview}

## Workflow

```
Progress:
- [ ] Step 1: {action}
- [ ] Step 2: {action}
- [ ] Step 3: {action}
```

### Step 1: {Action Name}

{Instructions for step 1}

### Step 2: {Action Name}

{Instructions for step 2}

### Step 3: {Action Name}

{Instructions for step 3}

## Examples

### Example 1: {Scenario}

Input:
{example input}

Output:
{example output}

## Quick Reference

| Term | Meaning |
|------|---------|
| {term} | {definition} |
```

## Placeholders

Replace these placeholders:

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{skill-name}` | Gerund format name | `formatting-markdown` |
| `{What it does}` | Core functionality | `Formats Markdown files` |
| `{trigger conditions}` | When to activate | `user mentions MD formatting` |
| `{Skill Title}` | Human-readable title | `Formatting Markdown` |
| `{action}` | Workflow step | `Read target file` |

## Example: Completed Basic Skill

```yaml
---
name: validating-json
description: |
  Validates JSON files against schemas. Use when user mentions
  JSON validation, schema checking, or data structure verification.
---

# Validating JSON

Validates JSON data against JSON Schema definitions.

## Workflow

```
Progress:
- [ ] Load JSON file
- [ ] Load or infer schema
- [ ] Validate and report
```

### Step 1: Load JSON

Read the target JSON file. Handle parse errors gracefully.

### Step 2: Load Schema

If schema provided, use it. Otherwise, infer from data structure.

### Step 3: Validate

Run validation, collect all errors, report with line numbers.

## Examples

### Example: Valid JSON

Input: `{"name": "test", "count": 5}`
Schema: `{"type": "object", "required": ["name"]}`
Output: Valid

### Example: Invalid JSON

Input: `{"count": "five"}`
Schema: `{"properties": {"count": {"type": "number"}}}`
Output: Error at $.count: expected number, got string
```
