# Skill Creation Quick Reference

## Directory Structure

```
skill-name/
├── SKILL.md              # Required - Main skill definition
├── scripts/              # Optional - Executable code
│   └── *.py, *.sh
├── references/           # Optional - Documentation for context
│   └── *.md
└── assets/               # Optional - Files for output
    └── templates, images, etc.
```

## SKILL.md Template

```markdown
---
name: my-skill
description: Clear description of what this skill does. This skill should be used when users want to [specific trigger conditions].
---

# My Skill

Brief purpose description (2-3 sentences).

## When to Use

- Trigger condition 1
- Trigger condition 2

## Workflow

Step-by-step instructions...

## Bundled Resources

Reference any scripts, references, or assets here.
```

## Frontmatter Rules

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | Use hyphens for multi-word names |
| `description` | Yes | 50+ chars, specific about triggers |

## Resource Guidelines

### scripts/
- For repetitive code or deterministic operations
- Make executable: `chmod +x script.py`
- Can run without loading into context

### references/
- For detailed documentation Claude should reference
- Keeps SKILL.md lean (<5k words)
- Include grep patterns for large files

### assets/
- For files used in output (not read into context)
- Templates, images, boilerplate code

## Commands

```bash
# Initialize new skill
python .claude/skills/skill-creator/scripts/init_skill.py <name> --path <dir>

# Package skill
python .claude/skills/skill-creator/scripts/package_skill.py <skill-dir>
```

## Best Practices Checklist

- [ ] Description is specific about when to trigger
- [ ] SKILL.md under 5000 words
- [ ] No TODO placeholders remain
- [ ] Detailed content moved to references/
- [ ] Scripts are executable
- [ ] Unused directories removed
- [ ] No information duplication
