# CLAUDE.md Template

Copy and customize this template for each plan wiki.

```markdown
# [Plan Name] - Claude Instructions

## Plan Structure

This is an Obsidian-compatible modular plan.

\`\`\`
plan-name/
├── README.md           # Index - start here
├── CLAUDE.md           # This file - rules for Claude
├── changelog.md        # Amendment history
├── deferred.md         # Preserved deferred work
├── phases/             # High-level phase overviews
├── tasks/              # Individual task specifications
├── reference/          # Supporting documentation
└── research/           # Oracle/Delphi research outputs
\`\`\`

## Rules

### 1. Progressive Disclosure

**DO:** Read only the files you need for the current task.
**DON'T:** Load the entire plan into context.

\`\`\`
User asks about X → Read tasks/X.md
User asks about Phase N → Read phases/0N-name.md
User asks for overview → Read README.md only
\`\`\`

### 2. Open Task Tracking

Tasks are tracked with Obsidian comment checkboxes:

\`\`\`markdown
%% [ ] this is an open question/task %%
%% [x] this was completed → see [[research/result]] %%
\`\`\`

**Finding open tasks:**
\`\`\`bash
grep -r '%% \[ \]' path/to/plan/
\`\`\`

**When completing a task:**
1. Mark \`[x]\` in the comment
2. Add arrow \`→\` with link to result
3. Add entry to changelog.md

### 3. Research Workflow

When a \`%% [ ]\` comment needs research:

1. **Simple question:** Use single oracle
2. **Complex/uncertain:** Use Delphi (3 parallel oracles + synthesis)

**Research outputs go to:** \`research/\` directory

**Link format after research:**
\`\`\`markdown
%% [x] question → Delphi complete: [[research/topic-delphi]] %%
> **Research:** See [[research/topic]] for details
\`\`\`

### 4. Changelog Protocol

**Every change to the plan must be logged in changelog.md.**

Format:
\`\`\`markdown
## YYYY-MM-DD

### Added
- [[path/to/file]] - Description

### Changed
- [[path/to/file]] - What changed and why

### Research
- [[research/topic]] - Summary of findings
\`\`\`

### 5. Version Preservation

Before major amendments:
1. Copy current file to \`{filename}.v{n}.md\`
2. Continue editing main file
3. Reference old version in changelog

### 6. Wiki-Link Format

Use Obsidian wiki-links for all internal references:

\`\`\`markdown
[[tasks/1.1-project-structure]]           # Same directory
[[../research/topic]]                     # Relative path
[[tasks/4.1-name|Display Name]]           # With display text
\`\`\`

### 7. Key Decisions Made

| Decision | Research | Recommendation |
|----------|----------|----------------|
| [Topic] | [[research/topic]] | **Choice** - reason |

### 8. Deferred Work

Deferred items are preserved in [[deferred]] for future implementation.
Do not delete deferred content - it may be needed later.

### 9. Task File Structure

Each task file should have:

\`\`\`markdown
# Task X.Y: Title

**Phase:** N - Phase Name
**Commit:** \`type(scope): description\`

%% [x] or [ ] any open questions %%

> **Research:** See [[../research/topic]] if applicable

## Overview (if needed)
## Files
## Steps
## Success Criteria
\`\`\`

### 10. When Adding New Tasks

1. Create file in \`tasks/\` with format \`{phase}.{task}-{slug}.md\`
2. Add to phase file's task table
3. Add to README.md task index
4. Add changelog entry
```
