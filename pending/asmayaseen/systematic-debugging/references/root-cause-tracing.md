# Root Cause Tracing

## Overview

Bugs often manifest deep in the call stack (git init in wrong directory, file created in wrong location, database opened with wrong path). Your instinct is to fix where the error appears, but that's treating a symptom.

**Core principle:** Trace backward through the call chain until you find the original trigger, then fix at the source.

## When to Use

- Error happens deep in execution (not at entry point)
- Stack trace shows long call chain
- Unclear where invalid data originated
- Need to find which test/code triggers the problem

## The Tracing Process

### 1. Observe the Symptom

```
Error: git init failed in /Users/jesse/project/packages/core
```

### 2. Find Immediate Cause

```python
await exec_file('git', ['init'], cwd=project_dir)
```

### 3. Ask: What Called This?

```
WorktreeManager.create_session_worktree(project_dir, session_id)
  -> called by Session.initialize_workspace()
  -> called by Session.create()
  -> called by test at Project.create()
```

### 4. Keep Tracing Up

What value was passed?
- `project_dir = ''` (empty string!)
- Empty string as `cwd` resolves to `process.cwd()`
- That's the source code directory!

### 5. Find Original Trigger

Where did empty string come from?

```python
context = setup_core_test()  # Returns { temp_dir: '' }
Project.create('name', context.temp_dir)  # Accessed before setup!
```

## Adding Stack Traces

When you can't trace manually, add instrumentation:

```python
import traceback

def git_init(directory: str):
    stack = ''.join(traceback.format_stack())
    print(f"DEBUG git init: dir={directory}, cwd={os.getcwd()}", file=sys.stderr)
    print(f"Stack:\n{stack}", file=sys.stderr)

    subprocess.run(['git', 'init'], cwd=directory)
```

**Critical:** Use `stderr` in tests (stdout may be suppressed)

## Finding Which Test Causes Pollution

If something appears during tests but you don't know which test:

```bash
# Run tests one-by-one, stop at first polluter
for test in $(find . -name "*.test.py"); do
    pytest "$test" -x
    if [ -d ".git" ]; then
        echo "POLLUTER: $test"
        break
    fi
done
```

## Example Resolution

**Bug:** Empty `projectDir` caused `git init` in source code

**Trace chain:**
1. `git init` runs in `process.cwd()` <- empty cwd parameter
2. WorktreeManager called with empty projectDir
3. Session.create() passed empty string
4. Test accessed `context.tempDir` before beforeEach
5. setup_core_test() returns `{ tempDir: '' }` initially

**Root cause:** Top-level variable initialization accessing empty value

**Fix:** Made tempDir a getter that throws if accessed before setup

**Defense-in-depth added:**
- Layer 1: Project.create() validates directory
- Layer 2: WorkspaceManager validates not empty
- Layer 3: NODE_ENV guard refuses git init outside tmpdir
- Layer 4: Stack trace logging before git init

## Key Principle

```
Found immediate cause
        |
        v
Can trace one level up? --no--> DON'T fix just the symptom
        | yes
        v
    Trace backwards
        |
        v
Is this the source? --no--> Keep tracing
        | yes
        v
    Fix at source
        |
        v
Add validation at each layer
        |
        v
    Bug impossible
```

**NEVER fix just where the error appears.** Trace back to find the original trigger.