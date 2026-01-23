# Create New Hook

**Goal**: Create a new Claude Code hook based on user's requirements

## Workflow

- T001: Identify target event (PreToolUse, PostToolUse, Stop, UserPromptSubmit, etc.)
- T002: Create hook script in `.claude/hooks/<hook-name>.py`
- T003: Implement logic with JSON stdin parsing and proper exit codes
- T004: Update `.claude/settings.local.json` to register the hook
- T005: Test with `echo '{}' | python .claude/hooks/<hook-name>.py`
- T006: Report results to main agent

## Constraints

- Prefer Python over shell scripts
- Always parse JSON from stdin with error handling
- Use exit code 0 (success), 2 (block), or other (non-blocking error)
- Never hardcode credentials
- Never create hooks that can infinite loop
