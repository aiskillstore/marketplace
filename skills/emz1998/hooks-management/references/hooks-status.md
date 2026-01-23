# Hooks Status Reference

## Overview

Current status of all Claude Code hooks in `.claude/hooks/`.

---

## Root-Level Event Handlers

| File | Event | Status | Description |
|------|-------|--------|-------------|
| `session_start.py` | SessionStart | Implemented | Initializes session ID, loads milestone from `project/status.json` |
| `session_end.py` | SessionEnd | Empty | Not implemented |
| `pre_tool_use.py` | PreToolUse | Implemented | Validates plan mode via `validate_plan()` |
| `post_tool_use.py` | PostToolUse | Empty | Not implemented |
| `user_prompt_submit.py` | UserPromptSubmit | Implemented | Activates plan mode when `/plan` command detected |
| `stop.py` | Stop | Implemented | Validates plan completion before stopping |
| `subagent_stop.py` | SubagentStop | Empty | Not implemented |
| `permission_request.py` | PermissionRequest | Implemented | Switches to plan mode on permission requests |
| `pre_compact.py` | PreCompact | Empty | Not implemented |
| `notification.py` | Various | Empty | Not implemented |

---

## Module Status

### plan_mode/ - Plan Mode State Management

| File | Status | Purpose |
|------|--------|---------|
| `__init__.py` | Implemented | Exports module functions |
| `activate.py` | Implemented | Activates plan mode on `/plan` command (uses `utils/`) |
| `validate_plan.py` | Implemented | Validates plan file exists with >100 lines (uses `utils/`) |
| `deactivate.py` | Implemented | Deactivates plan mode (uses `utils/`) |

**Note:** Cache management moved to shared `utils/cache.py` with namespaced keys (`plan_mode.*`).

### security/ - Security Validation

| File | Status | Purpose |
|------|--------|---------|
| `security.py` | Implemented | Risk scoring, command/path blocking, security logging |

**Features:**
- Risk levels: low (1), medium (5), high (10), critical (20)
- Blocks: `rm -rf /`, `dd`, `mkfs`, fork bombs
- Protects: `/etc/passwd`, `/boot/`, SSH keys
- Logs to: `.claude/logs/SECURITY.log`
- Auto-rotation at 1000 entries

### notification/ - Push Notifications

| File | Status | Purpose |
|------|--------|---------|
| `notify-ntfy.py` | Implemented | ntfy.sh push notifications |

**Features:**
- Sends notifications on Stop/SubagentStop events
- Tracks: files edited, files created, commands run, agents launched
- Stores activity in `session_activity.json`
- Tracks UserPromptSubmit for context

### implement/ - TDD Workflow Enforcement

| File | Status | Purpose |
|------|--------|---------|
| `implement.py` | Implemented | Phase-based workflow enforcement |
| `phase_guard.py` | Implemented | Additional phase validation |
| `phase-completion-check.py` | Implemented | Checks phase completion |
| `prompt.py` | Implemented | Phase-specific prompts |
| `stop_reset.py` | Implemented | Resets workflow on stop |
| `state.json` | Data | Current workflow state |
| `prompts/` | Templates | Phase prompt templates |

**Workflow Phases:**
1. explore
2. research
3. research_review
4. plan
5. plan_consult
6. failing_test
7. passing_test
8. refactor
9. code_review
10. commit

### change_log/ - Change Tracking

| File | Status | Purpose |
|------|--------|---------|
| `change-log.py` | Implemented | Tracks file changes (12KB) |

### compact/ - Compaction

| File | Status | Purpose |
|------|--------|---------|
| `compact-instructions.py` | Implemented | Pre-compact instructions |

### hooks_test/ - Testing

| File | Status | Purpose |
|------|--------|---------|
| `test-hooks.py` | Implemented | Hook testing utilities |

### utils/ - Shared Utilities

| File | Status | Purpose |
|------|--------|---------|
| `__init__.py` | Implemented | Module exports for all utilities |
| `input.py` | Implemented | `read_stdin_json()` - Parse JSON from stdin |
| `output.py` | Implemented | `log()`, `success_response()`, `block_response()` - Hook output helpers |
| `cache.py` | Implemented | `get_cache()`, `set_cache()` - Shared cache with namespaced keys |
| `git.py` | Implemented | `get_git_status()`, `get_modified_files()` - Git operations |

**Shared Cache:** `cache.json` stores all hook state with namespace isolation (e.g., `plan_mode.is_active`).

---

## Summary

| Category | Implemented | Empty/Placeholder |
|----------|-------------|-------------------|
| Root handlers | 5 | 5 |
| plan_mode | 4 | 0 |
| security | 1 | 0 |
| notification | 1 | 0 |
| implement | 6 | 0 |
| change_log | 1 | 0 |
| compact | 1 | 0 |
| hooks_test | 1 | 0 |
| utils | 5 | 0 |
| **Total** | **25** | **5** |
