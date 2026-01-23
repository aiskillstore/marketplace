# SKILL.md Template

## YAML Frontmatter

```yaml
---
name: [skill-name]
description: [Action verb] [what it does]. Use when [trigger conditions] or when user mentions [keywords].
---
```

**Frontmatter Rules**:

- `name`: Max 64 chars, lowercase letters/numbers/hyphens only, no reserved words (anthropic, claude)
- `description`: Max 1024 chars, third person voice, includes what AND when to use

## Body Structure

```markdown
**Goal**: [One sentence describing the skill's purpose]

**IMPORTANT**: [Critical constraint or principle - optional]

## Workflow

### Phase 1: [Phase Name]

- [Task 1]
- [Task 2]
- [Task 3]

### Phase 2: [Phase Name]

- [Task 1]
- [Task 2]
- [Task 3]

### Phase 3: [Phase Name]

- [Task 1]
- [Task 2]
- [Task 3]

## Rules

- [Constraint 1]
- [Constraint 2]
- [Constraint 3]

## Acceptance Criteria

- [Criterion 1]
- [Criterion 2]
- [Criterion 3]
```

## Guidelines

### Naming Convention

Use gerund form (verb + -ing):

- `processing-pdfs`
- `analyzing-spreadsheets`
- `managing-databases`

### Description Pattern

```
[Verb]s [objects/actions]. Use when [specific triggers] or when user mentions [keywords].
```

**Examples**:

- "Extracts text from PDF files and fills forms. Use when working with PDFs or when user mentions document extraction."
- "Generates commit messages by analyzing git diffs. Use when user asks for help with commit messages."

### Content Principles

1. **Be concise** - Only add context Claude doesn't already know
2. **One level deep** - Reference files directly from SKILL.md, avoid nested references
3. **Under 500 lines** - Split into separate files if content exceeds this
4. **Consistent terminology** - Use same terms throughout (don't mix "field"/"box"/"element")
5. **No time-sensitive info** - Avoid dates or version-specific content that will become outdated
