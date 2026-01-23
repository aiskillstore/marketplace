# Troubleshooting Hook Tasks

**Goal**: Troubleshoot Claude Code hook with issue

## Workflow

- T001: Re-read the hook specifications from `.claude/skills/hooks-management/references/hooks.md` if not yet done
- T002: Run `/hooks` to verify hook is registered
- T003: Read hook script from `.claude/hooks/<hook-name>`
- T004: Check hook registration in `.claude/settings.local.json`
- T005: Test with `echo '{}' | python .claude/hooks/<hook-name>`
- T006: Test with malformed input `echo 'invalid' | python .claude/hooks/<hook-name>`
- T007: Verify exit codes (0=success, 2=block, other=non-blocking error)
- T008: Run `claude --debug` to see hook execution details
- T009: Apply fix and retest
- T010: Report diagnosis and resolution to main agent

## Common Issues

- Hook not registered in `.claude/settings.local.json`
- Script not executable (`chmod +x` needed)
- Quotes not escaped in JSON (use `\"` inside strings)
- Wrong matcher (case-sensitive, check exact tool name)
- Command not found (use full paths or `$CLAUDE_PROJECT_DIR`)
- Invalid JSON parsing in stdin
- Missing error handling for edge cases
- Timeout exceeded (default 60 seconds)

## Exit Code Reference

| Code  | Meaning            | Behavior                                  |
| ----- | ------------------ | ----------------------------------------- |
| 0     | Success            | stdout shown in verbose mode, JSON parsed |
| 2     | Block              | stderr shown to Claude, tool call blocked |
| Other | Non-blocking error | stderr shown in verbose mode, continues   |
