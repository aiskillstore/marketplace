# Update Hook

**Goal**: Update existing Claude Code hook based on user's requirements

## Workflow

- T001: Read existing hook from `.claude/hooks/<hook-name>.py`
- T002: Review current settings in `.claude/settings.local.json`
- T003: Apply requested changes while preserving working logic
- T004: Update `.claude/settings.local.json` if event/matcher changed
- T005: Test with `echo '{}' | python .claude/hooks/<hook-name>.py`
- T006: Run `/hooks` to verify registration
- T007: Report results to main agent

## Constraints

- Preserve existing functionality unless explicitly asked to remove
- Keep JSON stdin parsing and error handling intact
- Never break existing hook integrations
- Test after every change
