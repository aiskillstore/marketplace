---
name: hooks-management
description: Use PROACTIVELY when you need to create, update, configure, or validate Claude hooks for various events and integrations
---

**Goal**: Create, update or troubleshoot Claude Code hook scripts

## Workflow

### Phase 1: Exploration & Analysis

- T001: Read hook docs from `.claude/skills/hooks-management/references/hooks.md`
- T002: Analyze the request and identify if the task is to create, update or troubleshoot a hook.
- T003: Choose the appropriate task to perform based on the request in `.claude/skills/hooks-management/tasks/`
- T004: Check existing hooks in `.claude/hooks/` and settings configuration in `.claude/settings.local.json`
- T005: Perform the task
- T006: Test the hook execution and edge cases using `echo` (see Testing Strategy)
- T007: Review security and performance
- T008: Update `.claude/skills/hooks-management/references/hooks-status.md` to reflect changes
- T009: Update `.claude/skills/hooks-management/references/architecture-pattern.md` if architectural changes were made (new modules, utils, patterns)
- T010: Provide comprehensive report to main agent

## Implementation Strategy

- For new hooks: Create script file in `.claude/hooks/` following naming convention
- If the task is to troubleshoot, follow the troubleshooting task in `.claude/skills/hooks-management/tasks/troubleshooting.md`
- If the task is to update, follow the update task in `.claude/skills/hooks-management/tasks/update-hook.md`
- If the task is to create, follow the create task in `.claude/skills/hooks-management/tasks/create-new-hook.md`
- Prefer Python over shell scripts if possible.
- Implement idempotent operations where possible

## Testing Strategy

Use `echo` to pipe test input directly to hook scripts without creating test files:

```bash
# Test with sample JSON input
echo '{"session_id": "test-123", "tool": "Read", "result": "sample output"}' | python .claude/hooks/your-hook.py

# Test with minimal input
echo '{}' | python .claude/hooks/your-hook.py

# Test error handling with malformed input
echo 'invalid json' | python .claude/hooks/your-hook.py

# Test with specific event data
echo '{"event": "stop", "reason": "user_request"}' | python .claude/hooks/your-hook.py
```

**Testing Checklist:**

- [ ] Hook accepts valid JSON input via stdin
- [ ] Hook handles empty input gracefully
- [ ] Hook handles malformed input without crashing
- [ ] Hook returns appropriate exit codes (0 for success, non-zero for errors)
- [ ] Hook output is valid JSON when required by the event type

## Constraints

- **Must** update `.claude/settings.local.json` to link hooks
- **Must** test hooks after generation without creating test files
- **Never** create hooks that modify critical system files
- **Never** implement hooks with hardcoded credentials
- **Never** write hooks that can cause infinite loops
- **Never** bypass security validations or access controls
- **Never** create hooks without proper error handling
- **Never** create test files when testing hooks
- **Never** write complicated hooks with complex logic. Keep it simple and straightforward.

## Success Criteria

- Hook script exists and is syntactically valid
- Hook is properly linked in `settings.local.json`
- Hook executes successfully on target event
- Error handling covers common failure scenarios
- No security vulnerabilities detected
- `hooks-status.md` reference updated to reflect current hook state
- `architecture-pattern.md` updated if architectural changes were made
- Comprehensive report provided to main agent upon completion
- Code is readable and concise.
