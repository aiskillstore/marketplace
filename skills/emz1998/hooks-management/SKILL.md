---
name: hooks-management
description: Use PROACTIVELY when you need to create, update, configure, or validate Claude hooks for various events and integrations
---

**Goal**: Create, update or troubleshoot Claude Code hook scripts

## Workflow

- Read hook documentation from `.claude/skills/hooks-management/references/hooks.md`
- Read hook input patterns from `.claude/skills/hooks-management/references/input-patterns.md`
- Review existing hooks in `.claude/hooks/` and settings in `.claude/settings.local.json`
- Create or update the hook script following the input patterns
- Troubleshoot the hook script if needed
- Verify hook execution using `echo` to pipe JSON input
- Review for security and performance issues
- Provide report to main agent

## Rules

- **NEVER** hardcode credentials or modify critical system files
- **NEVER** write hooks that can cause infinite loops
- **NEVER** bypass security validations
- **DO NOT** use multiline comments in hook scripts. Only use single line comments.
- **MUST** include proper error handling
- **MUST** prefer readability over performance
- **MUST** prefer Python over shell scripts
- **MUST** write semantic and idiomatic code

## Acceptance Criteria

- Hook executes successfully on target event
- Hook handles invalid/malformed input gracefully
- No security vulnerabilities
- Hook follows dispatcher pattern (for new hook logic)
