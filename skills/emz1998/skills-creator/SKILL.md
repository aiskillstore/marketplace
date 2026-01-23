---
name: skills-creator
description: Creates and maintains Agent Skills with effective triggers and progressive disclosure. Use when user requests to create a skill, generate a SKILL.md, build custom capabilities, or mentions "create skill", "new skill", or "skill configuration".
---

**Goal**: Create well-structured Agent Skills following best practices for discoverability, conciseness, and progressive disclosure.

**IMPORTANT**: Skills configuration should be concise and high-level. Only include context Claude does not already know.

## Workflow

1. Read references: `skills-docs.md` and `best-practices.md` in `.claude/skills/skills-creator/references/`
2. Analyze requirements and determine freedom level
3. Create SKILL.md using template from `.claude/skills/skills-creator/templates/template.md`
4. Add resources(reference files, scripts, etc.) alongside the SKILL.md file only if necessary. Use folder to organize resources.
5. Save to `.claude/skills/[skill-name]/SKILL.md` and report completion

## Rules

- Only add context Claude doesn't already know
- Keep references one level deep from SKILL.md
- Provide one default approach, avoid offering multiple options
- Use forward slashes in file paths (no Windows-style paths)
- Match freedom level to task fragility (high freedom for flexible tasks, low for critical operations)

## Acceptance Criteria

- Skill saved to `.claude/skills/[skill-name]/SKILL.md`
- Name valid (max 64 chars, lowercase letters/numbers/hyphens only)
- Description valid (max 1024 chars, third person, no "I" or "you")
- Description includes what skill does AND when to use it
- SKILL.md body under 500 lines
- Consistent terminology throughout
- No duplicate or conflicting skills exist
- No time-sensitive information included
- Name defined using gerund form (e.g., `processing-pdfs`, `analyzing-data`)
