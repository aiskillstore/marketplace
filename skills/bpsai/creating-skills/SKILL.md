---
name: creating-skills
description: Use when creating new skills, documenting workflows, or standardizing processes into reusable skill definitions.
---

# Creating Skills

## When to Create a Skill

Create a skill when:
- A workflow is repeated across multiple sessions
- Complex multi-step processes need documentation
- Team needs standardized approach to a task
- Errors occur that a documented procedure would prevent

## Skill Directory Structure

```
.claude/skills/{skill-name}/
├── SKILL.md          # Required: Main skill document
├── reference/        # Optional: Supporting documents
└── scripts/          # Optional: Automation scripts
```

## SKILL.md Template

```markdown
---
name: skill-name
description: Third-person description of what the skill does. Under 1024 chars.
---

# Skill Title

## When to Use

Describe trigger conditions.

## Steps

1. First step
2. Second step
3. Third step

## Commands

```bash
command1
command2
```

## Examples

Show usage examples.
```

## Frontmatter Rules

**Required fields (only these two allowed):**

| Field | Rules |
|-------|-------|
| `name` | Lowercase, hyphenated, gerund form (e.g., `creating-skills`) |
| `description` | Under 1024 chars, 3rd-person voice, no "you" |

**Not allowed:** Any other fields (version, author, tags, etc.)

## Naming Conventions

| Rule | Good | Bad |
|------|------|-----|
| Lowercase | `reviewing-code` | `Reviewing-Code` |
| Hyphens, not underscores | `creating-skills` | `creating_skills` |
| Gerund form (-ing) | `implementing-with-tdd` | `implement-tdd` |
| Match directory name | `name: foo` in `foo/` | `name: bar` in `foo/` |

### Gerund Suggestions

| Instead of | Use |
|------------|-----|
| `code-review` | `reviewing-code` |
| `plan` | `planning` |
| `implement` | `implementing` |
| `design` | `designing` |
| `finish` | `finishing` |

## Description Guidelines

**Good (3rd person):**
> Manages task lifecycle transitions and coordinates Trello sync.

**Bad (2nd person):**
> Use when you need to manage task lifecycle.

## File Size Limits

- SKILL.md: **Under 500 lines**
- Description: **Under 1024 characters**

## Validation Checklist

Before finalizing a skill:

- [ ] Frontmatter has only `name` and `description`
- [ ] Name is lowercase-hyphenated gerund
- [ ] Name matches directory name
- [ ] Description under 1024 characters
- [ ] Description uses 3rd-person voice
- [ ] SKILL.md under 500 lines
- [ ] No "Claude already knows this" content
- [ ] Includes actionable steps or commands

## CLI Commands

```bash
# List all skills
bpsai-pair skill list

# Validate all skills
bpsai-pair skill validate

# Validate specific skill
bpsai-pair skill validate creating-skills

# Auto-fix simple issues
bpsai-pair skill validate --fix
```

## Common Validation Errors

| Error | Fix |
|-------|-----|
| Extra frontmatter fields | Remove all fields except name/description |
| Name mismatch | Make frontmatter name match directory name |
| Description too long | Shorten to under 1024 characters |
| File too long | Split into SKILL.md + reference docs |

## Creating a New Skill

1. **Create directory**: `mkdir -p .claude/skills/{skill-name}`
2. **Create SKILL.md** with template above
3. **Add content**: Steps, commands, examples
4. **Validate**: `bpsai-pair skill validate {skill-name}`
5. **Fix issues**: Address any errors or warnings
6. **Test**: Verify skill works in practice

## Anti-patterns to Avoid

- **Generic knowledge**: Don't document things Claude already knows
- **Excessive length**: Keep focused, link to reference docs
- **2nd person voice**: Use "Performs X" not "Use when you need X"
- **Extra metadata**: No version, author, tags in frontmatter
- **Underscores**: Use hyphens for multi-word names
