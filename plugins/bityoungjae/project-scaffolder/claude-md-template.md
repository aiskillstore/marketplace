# CLAUDE.md

## Project Overview

{PROJECT_DESCRIPTION}

**Subject**: {SUBJECT}
**Target System**: {TARGET_SYSTEM}
**Total Scope**: {TOTAL_PAGES} pages across {TOTAL_PARTS} parts

---

## Key Documents

| Document | Purpose |
|----------|---------|
| [plan.md](plan.md) | Complete structure with Part/Chapter/Section hierarchy |
| [task.md](task.md) | Progress tracking checklist with session boundaries |
| [persona.md](persona.md) | Writer/Reader personas and code policy |
| [project-context.md](project-context.md) | Target environment and reference URLs |

---

## Key Skills and Commands

### `/write`

Use this command to write the next incomplete document section.

**Workflow**:
1. Find next `[ ]` item in task.md
2. Read corresponding section from plan.md
3. Invoke researcher agent for information gathering
4. Invoke writer agent with context injection (persona.md, project-context.md)
5. Save to `docs/` directory
6. Update task.md checkbox to `[x]`

### `/status`

Check current project progress and next pending tasks.

### `/validate`

Verify project structure and document consistency.

---

## Document Structure

### File Naming Convention

```
docs/{CHAPTER_NUM}-{SECTION_NUM}-{SLUG}.md
```

Example:
```
docs/01-1-introduction.md
docs/03-2-advanced-patterns.md
```

### Frontmatter Template

```yaml
---
title: "{SECTION_TITLE}"
chapter: {CHAPTER_NUM}
section: {SECTION_NUM}
pages: {PAGE_COUNT}
status: draft | review | complete
created: {DATE}
updated: {DATE}
---
```

---

## Writing Persona

**Writer**: {WRITER_DESCRIPTION}

**Reader**: {READER_DESCRIPTION}

### Tone Guidelines

- {TONE_1}
- {TONE_2}
- {TONE_3}

---

## Code Policy

### Preferred Languages

| Priority | Language | Use Case |
|----------|----------|----------|
| 1 | {PREFERRED_1} | {USE_CASE_1} |
| 2 | {PREFERRED_2} | {USE_CASE_2} |

### Forbidden Languages

| Language | Reason |
|----------|--------|
| {FORBIDDEN_1} | {REASON_1} |
| {FORBIDDEN_2} | {REASON_2} |

### Code Style

- {CODE_STYLE_1}
- {CODE_STYLE_2}

---

## Terminology Policy

**Primary Language**: {LANGUAGE}
**Technical Terms**: {TERM_LANGUAGE}

**First Occurrence Rule**:
```
{TERM_FORMAT}
```

---

## Quality Standards

### Content Requirements

- [ ] Meets target page count (within 20%)
- [ ] Code examples are tested and working
- [ ] No prohibited phrases used
- [ ] Terminology policy followed

### Review Checklist

Before marking a section complete:

1. Frontmatter is valid and complete
2. All code blocks have language tags
3. Internal links work correctly
4. Images have alt text (if any)
5. Practice exercises have solutions

---

## Research Priority

When researching topics, prioritize sources in this order:

1. **Official Documentation**: {OFFICIAL_DOCS}
2. **Authoritative Books**: {BOOKS}
3. **Community Resources**: {COMMUNITY}
4. **Blog Posts/Tutorials**: Only if recent ({YEAR}+)

---

## Session Guidelines

Each Claude Code session should:

- Complete 3-5 sections
- Target 20-40 pages of content
- Stay within session boundaries marked in task.md
- Update progress after each section

### Session Workflow

1. Read task.md for current session scope
2. For each section:
   - Read plan.md for details
   - Research if needed
   - Write document
   - Save to docs/
   - Mark task complete
3. Run `/status` at session end

---

## Prohibited Phrases

Avoid these expressions in all content:

- {PROHIBITED_1}
- {PROHIBITED_2}
- {PROHIBITED_3}

---

## Notes

{ADDITIONAL_NOTES}
