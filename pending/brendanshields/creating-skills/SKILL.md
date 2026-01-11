---
name: creating-skills
description: |
  Creates new Claude Code skills following best practices. Guides through skill structure,
  naming, descriptions, and progressive disclosure. Use when user wants to create a skill,
  build a skill, make a new capability, or asks about skill best practices.
---

# Creating Skills

Guides creation of Claude Code skills using documented best practices.

## Quick Start

For a new skill:
1. Ask user for skill purpose and target users
2. Generate using appropriate template
3. Validate against checklist

For reviewing existing skill:
1. Read SKILL.md and supporting files
2. Check against anti-patterns in [reference.md](reference.md)
3. Report issues with fixes

## Workflow: Create New Skill

```
Progress:
- [ ] Gather requirements (purpose, triggers, complexity)
- [ ] Choose template (basic or advanced)
- [ ] Generate skill structure
- [ ] Customize content
- [ ] Validate against checklist
```

### Step 1: Gather Requirements

Ask user with AskUserQuestion:
- What should this skill do? (purpose)
- When should it activate? (trigger words)
- Simple or complex? (affects structure)

### Step 2: Choose Structure

| Complexity | Structure | When to Use |
|------------|-----------|-------------|
| Basic | Single SKILL.md | Simple workflows, < 200 lines |
| Advanced | SKILL.md + references | Complex domains, multiple workflows |

### Step 3: Generate Skill

Use templates from `templates/` directory:
- [templates/basic.md](templates/basic.md) - Single file skill
- [templates/advanced.md](templates/advanced.md) - Multi-file with references

Create in appropriate location:
- `~/.claude/skills/` - Personal skills
- `.claude/skills/` - Project skills (git-tracked)

### Step 4: Validate

Run through checklist before finishing:

```
Validation Checklist:
- [ ] Name: gerund format (verb-ing), lowercase, hyphens only
- [ ] Name: max 64 characters, no reserved words
- [ ] Description: explains WHAT and WHEN to use
- [ ] Description: third person, max 1024 characters
- [ ] SKILL.md: under 500 lines (ideally under 300)
- [ ] References: one level deep from SKILL.md
- [ ] No time-sensitive info (dates, versions)
- [ ] Consistent terminology throughout
- [ ] Examples: concrete input/output pairs
- [ ] Paths: Unix-style only (forward slashes)
```

## Naming Rules

**Format**: `verb-ing-noun` (gerund form)
- `processing-pdfs`
- `analyzing-spreadsheets`
- `managing-databases`

**Constraints**:
- Max 64 characters
- Lowercase letters, numbers, hyphens only
- No: `anthropic`, `claude`, XML tags

## Description Best Practices

The description determines when Claude activates the skill.

**Include**:
- What the skill does
- When to use it
- Trigger words users might say

**Format**: Third person, active voice

```yaml
# Good
description: |
  Extracts text and tables from PDF files. Use when working with
  PDFs, forms, or document extraction.

# Bad - first person
description: I help you process PDF files
```

## Progressive Disclosure

Keep SKILL.md lean. Move details to reference files:

```
skill-name/
├── SKILL.md          # Overview, workflow (always loaded)
├── reference.md      # Detailed guidelines (loaded when needed)
├── examples.md       # Extended examples
└── templates/        # Reusable templates
```

**Key rule**: References should be one level deep. All reference files link directly from SKILL.md.

See [reference.md](reference.md) for detailed best practices and anti-patterns.

## Frontmatter Schema

```yaml
---
name: skill-name-here
description: |
  What it does and when to use it. Include trigger words.
allowed-tools: Read, Grep  # Optional: restrict available tools
---
```

## Anti-Patterns (Quick Reference)

| Avoid | Do Instead |
|-------|------------|
| Windows paths `scripts\file.py` | Unix paths `scripts/file.py` |
| Too many options | Provide sensible default |
| Assuming tools installed | List required packages |
| Vague descriptions | Specific with trigger words |
| Deeply nested references | One level deep |
| Time-sensitive info | Avoid dates/versions |

Full anti-patterns guide: [reference.md](reference.md)

## Example: Basic Skill

```yaml
---
name: formatting-markdown
description: |
  Formats and lints Markdown files. Use when user mentions
  markdown formatting, MD files, or document styling.
---

# Formatting Markdown

## Workflow

1. Read target file
2. Apply formatting rules
3. Report changes

## Rules

- Headers: ATX style (#)
- Lists: consistent markers
- Code blocks: fenced with language
```
