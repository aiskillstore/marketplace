---
name: command-management
description: Use PROACTIVELY this skill when you need to create or update custom commands following best practices
allowed-tools: Read, Write, SlashCommand, TodoWrite, Glob, Grep
---

**Goal**: Create or update a custom command following best practices and template standards

## Tasks

- T001: Read the Anthropic documentation on how to create custom commands from `@.claude/skills/command-management/references/command-docs.md`
- T001: Read the command template from `.claude/skills/command-management/templates/command.md`
- T002: Analyze instructions/requirements from the user to understand the command's purpose and scope
- T003: Determine the appropriate command folder location
- T004: Create or update the command file in the determined location
- T005: Test the command using the `SlashCommand` tool
- T006: Report the results to the user

## Constraints

- NEVER omit any of the 6 template sections (Context, Tasks, Constraints, Examples, References, Output Format)
- NEVER omit required YAML frontmatter fields (name, description, allowed-tools, argument-hint, model)
- NEVER save command files outside `.claude/commands/` directory
- NEVER grant more tool permissions than absolutely necessary
- NEVER use 'all' tool access unless the command truly requires unrestricted access
- NEVER use 'opus' model unless the command requires complex reasoning
- DO NOT create tasks without sequential IDs (T001, T002, T003, etc.)
- DO NOT create non-atomic tasks - each task must describe one clear operation
- DO NOT skip the testing phase via `SlashCommand` tool
- DO NOT omit usage examples with actual parameter values

## Success Criteria

- [ ] Command file saved to correct location (`.claude/commands/` or appropriate subfolder)
- [ ] YAML frontmatter includes all required fields (name, description, allowed-tools, argument-hint, model)
- [ ] All 6 template sections present and populated
- [ ] Tool permissions follow least-privilege principle
- [ ] Tasks organized with sequential IDs (T001, T002, etc.)
- [ ] At least one concrete usage example included
- [ ] Command tested successfully via `SlashCommand` tool
