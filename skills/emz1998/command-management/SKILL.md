---
name: command-management
description: Use PROACTIVELY this skill when you need to create or update custom commands following best practices
allowed-tools: Read, Write, SlashCommand, TodoWrite, Glob, Grep
---

**Goal**: Create or update custom commands following template standards

**IMPORTANT**: Keep command content high-level and concise. Do not dive into implementation details.

## Workflow

1. Read command docs from `.claude/skills/command-management/references/command-docs.md` and template from `.claude/skills/command-management/templates/command.md`
2. Analyze user requirements and determine command location
3. Create or update the command file
4. Test via `SlashCommand` tool and report results

## Constraints

- DO NOT deviate from template structure (YAML frontmatter + all sections)
- NEVER save commands outside `.claude/commands/` directory
- DO NOT grant excessive tool permissions - apply least-privilege
-

## Acceptance Criteria

- Command saved to correct location with complete YAML frontmatter
- All template sections populated
- Command tested successfully via `SlashCommand`
