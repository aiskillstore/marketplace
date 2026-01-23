# Hooks Architecture Pattern Reference

## Overview

The `.claude/hooks/` folder implements an event-driven architecture for Claude Code automation.

---

## Core Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Claude Code Events                       │
├─────────────────────────────────────────────────────────────┤
│  SessionStart │ PreToolUse │ PostToolUse │ Stop │ etc.      │
└───────┬───────┴─────┬──────┴──────┬──────┴──┬───┴───────────┘
        │             │              │         │
        ▼             ▼              ▼         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Root Event Handlers                        │
│  session_start.py │ pre_tool_use.py │ stop.py │ etc.        │
└───────┬───────────┴────────┬────────┴────┬──────────────────┘
        │                    │             │
        ▼                    ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Specialized Modules                       │
│  plan_mode/ │ security/ │ notification/ │ implement/        │
└───────┬─────┴─────┬─────┴───────┬───────┴───────────────────┘
        │           │             │
        ▼           ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                     Shared Utilities                         │
│        utils/input │ utils/output │ utils/cache │ utils/git │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Shared State (cache.json)                  │
│  { "plan_mode": {...}, "implement": {...}, ... }            │
└─────────────────────────────────────────────────────────────┘
```

---

## Design Patterns

### 1. Dispatcher Pattern

Root-level handlers act as dispatchers that delegate to specialized modules:

```python
# pre_tool_use.py (dispatcher)
from plan_mode import validate_plan

def main():
    validate_plan()  # Delegates to module
```

### 2. Module Encapsulation

Each subdirectory is a self-contained module with:
- `__init__.py` - Public API exports
- Internal implementation files
- Uses shared `utils/` for common operations

```
plan_mode/
├── __init__.py          # Exports: validate_plan, activate_plan_mode, deactivate
├── activate.py          # Internal: activation logic (uses utils/)
├── validate_plan.py     # Internal: validation logic (uses utils/)
└── deactivate.py        # Internal: deactivation logic (uses utils/)
```

### 3. Shared Utilities Pattern

All hooks import from `utils/` for common operations:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import read_stdin_json, set_cache, get_cache, log
```

**Available utilities:**

| Module | Functions | Purpose |
|--------|-----------|---------|
| `utils/input.py` | `read_stdin_json()` | Parse JSON from stdin |
| `utils/output.py` | `log()`, `success_response()`, `block_response()` | Hook output helpers |
| `utils/cache.py` | `get_cache()`, `set_cache()` | Namespaced state persistence |
| `utils/git.py` | `get_git_status()`, `get_modified_files()` | Git operations |

### 4. Namespaced Cache Management

State is persisted in a shared `cache.json` with namespace isolation:

```python
from utils import get_cache, set_cache

# Write with namespace
set_cache("plan_mode", "is_active", True)
set_cache("plan_mode", "session_id", "abc-123")

# Read with namespace
is_active = get_cache("plan_mode", "is_active")
session_id = get_cache("plan_mode", "session_id")
```

**Resulting `cache.json`:**
```json
{
  "plan_mode": {
    "is_active": true,
    "session_id": "abc-123"
  },
  "implement": {
    "current_phase": "explore"
  }
}
```

### 5. Exit Code Conventions

| Exit Code | Meaning |
|-----------|---------|
| 0 | ALLOW - Tool proceeds normally |
| 2 | BLOCK - Tool blocked, message shown to Claude |

```python
from utils import log, block_response

def validate():
    if not valid:
        log("Validation failed")  # stderr
        block_response("Reason")  # exits with code 2
    sys.exit(0)  # allow
```

### 6. Hook Response Format

Hooks communicate via JSON on stdout:

```python
from utils import success_response

# Add context (SessionStart, UserPromptSubmit)
success_response("SessionStart", "Session initialized with ID: abc-123")

# Block with reason (PreToolUse)
response = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "Security Policy Violation"
    }
}
print(json.dumps(response))

# Allow silently
print(json.dumps({"suppressOutput": True}))
```

---

## Event Flow Examples

### Session Start Flow

```
SessionStart Event
    │
    ▼
session_start.py
    │
    ├── read_stdin_json() ─► utils/input.py
    │
    ├── get_milestone() ─► project/status.json
    │
    ├── set_cache("plan_mode", "session_id", id) ─► cache.json
    │
    └── Return additionalContext with session info
```

### Pre-Tool Validation Flow

```
PreToolUse Event
    │
    ▼
pre_tool_use.py
    │
    ├── validate_plan() ─► plan_mode/validate_plan.py
    │                          │
    │                          ├── get_cache("plan_mode", "is_active")
    │                          │
    │                          ├── get_modified_files() ─► utils/git.py
    │                          │
    │                          ├── Check plan file exists
    │                          │
    │                          └── exit(0) or exit(2)
    │
    └── security.py (if configured)
            │
            ├── check_dangerous_path()
            │
            ├── check_dangerous_command()
            │
            ├── log_security_event() ─► .claude/logs/SECURITY.log
            │
            └── Return allow/deny decision
```

### Plan Mode Activation Flow

```
UserPromptSubmit Event (prompt starts with "/plan")
    │
    ▼
user_prompt_submit.py
    │
    ├── activate_plan_mode() ─► plan_mode/activate.py
    │                               │
    │                               ├── read_stdin_json() ─► utils/input.py
    │                               │
    │                               ├── Check prompt.startswith("/plan")
    │                               │
    │                               ├── set_cache("plan_mode", "is_active", True)
    │                               │
    │                               └── Print "Planning Phase" message
    │
    └── exit(0)
```

---

## Best Practices

### 1. Always Use Utils

Import from `utils/` for standard operations:
```python
from utils import read_stdin_json, set_cache, get_cache, log
```

### 2. Namespace Your Cache Keys

Always use your module name as namespace:
```python
set_cache("my_module", "key", value)  # Good
set_cache("key", value)                # Bad - no namespace
```

### 3. Fail-Safe Design

Hooks should never crash Claude Code:
```python
try:
    # Hook logic
except Exception as e:
    log(f"Error: {e}")
    sys.exit(0)  # Allow on error
```

### 4. Minimal Output

Only output when necessary:
```python
# Suppress output for allow decisions
print(json.dumps({"suppressOutput": True}))
```

### 5. Path Independence

Use `sys.path.insert` for utils imports:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import read_stdin_json
```

### 6. Logging Strategy

- User-facing messages: `print()` to stdout
- Debug/error messages: `log()` to stderr
- Security events: Dedicated log files

---

## File Organization

```
.claude/hooks/
├── cache.json               # Shared state with namespaced keys
├── [event]_[action].py      # Root handlers (snake_case)
├── [module]/                # Feature modules
│   ├── __init__.py          # Public exports
│   └── [feature].py         # Implementation (imports from utils/)
└── utils/                   # Shared utilities
    ├── __init__.py          # Module exports
    ├── input.py             # read_stdin_json()
    ├── output.py            # log(), success_response(), block_response()
    ├── cache.py             # get_cache(), set_cache()
    └── git.py               # get_git_status(), get_modified_files()
```
