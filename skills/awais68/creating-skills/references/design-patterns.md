# Skill Design Patterns

## Progressive Disclosure

| Layer | Content | Budget | When Loaded |
|-------|---------|--------|-------------|
| Metadata | name + description | ~100 tokens | Always |
| Instructions | SKILL.md body | <5000 tokens | When activated |
| Resources | scripts/, references/ | As needed | On demand |

## Workflow Patterns

### Pattern 1: High-level guide with references
```markdown
## Quick Start
[80% case]

## Advanced
See [REFERENCE.md](references/REFERENCE.md)
```

### Pattern 2: Validation loop
```
Run → Validate → Fix → Repeat → Proceed
```

### Pattern 3: Failure escalation
```
If verify.py fails twice:
1. STOP automation
2. Surface diagnostic command
3. Request human intervention
```

## MCP Output Discipline

**Rule**: MCP responses must NEVER enter context verbatim.

```python
# BAD
print(mcp_response)  # 900+ tokens

# GOOD
filtered = extract_relevant(mcp_response)
print(filtered)  # <200 tokens
```

## Frontmatter Template

```yaml
---
name: gerund-form-name
description: |
  What it does in one sentence.
  Use when [specific trigger condition].
  NOT when [exclusion if collision possible].
---
```
