# Tool Orchestration

Use tools with precision. Batch parallel work. Never retry verbatim. Never guess.

---

## Core Principles

### 1. Parallel by Default

Independent tool calls run in one batch. Sequential is the wrong default.

```
Task: "Fix auth bug"

WRONG (sequential — 3 round-trips):
  turn 1: read src/auth.ts
  turn 2: read src/auth.test.ts
  turn 3: grep SESSION_TIMEOUT src/

RIGHT (parallel — 1 round-trip):
  turn 1: [read src/auth.ts] + [read src/auth.test.ts] + [grep SESSION_TIMEOUT src/]
```

**Rule:** If Call B doesn't need Call A's output, batch them.

---

### 2. Tool Selection Hierarchy

When multiple tools can accomplish the same task, pick the most precise:

```
1. Dedicated tool   → use the purpose-built one (grep > bash > read)
2. Shell / bash     → for complex search, test runners, git commands
3. Read tool        → for targeted single-file reads
4. Write/Edit tool  → for file modifications (always read first)
```

**Examples:**

```
Finding a symbol: grep -rn "functionName" src/   (not: read every file)
Running tests: vitest run                          (not: bash npm test)
Checking file: read src/auth.ts:20-50             (not: read entire file then skim)
```

---

### 3. Never Retry Verbatim

If a tool call fails or is denied, the exact same call will fail again.

```
WRONG: [tool call fails] → retry same call
WRONG: [permission denied] → ask for permission, retry same call
RIGHT: [tool call fails] → diagnose why → adjust → retry adjusted call
RIGHT: [permission denied] → adjust approach (different tool, different path)
```

---

### 4. Confirm Before Destructive Actions

Before any action that's hard to reverse:

```
Hard to reverse: delete, overwrite, migrate, deploy to production
Easy to reverse: read, grep, type-check, lint, run tests
```

For hard-to-reverse:
1. State what you're about to do
2. State what you found at the target (read it first)
3. If different from description → surface, don't proceed
4. If approved → proceed once, no more confirmation loops

---

## Read Tool Patterns

### Targeted read (preferred)
```
Read lines 20–50 of src/auth.ts
→ precise, fast, minimal tokens
```

### Full read (when structure is unknown)
```
Read entire src/auth.ts
→ use when you need to understand full context
→ always read in full for files you're about to edit
```

### Progressive read (for large files)
```
Read lines 1–50    (find the structure)
Read lines 23–45   (target section)
Read lines 100–120 (related section)
```

---

## Search Patterns

### Exact symbol search
```bash
grep -rn "functionName\b" src/ --include="*.ts"
# \b = word boundary — avoids matching functionNameExtra
```

### File pattern search
```bash
find src/ -name "*.test.ts" -type f
find src/ -name "auth*" -type f
```

### Content + context
```bash
grep -rn "SESSION_TIMEOUT" src/ -A 3 -B 3
# -A 3: 3 lines after, -B 3: 3 lines before — see context
```

### Multi-pattern
```bash
grep -rn "SESSION_TIMEOUT\|TIMEOUT\|timeout" src/ --include="*.ts"
```

---

## Shell Tool Best Practices

### Always capture output
```bash
# Run test, capture result
vitest run 2>&1 | tail -20
```

### Check exit codes
```bash
tsc --noEmit && echo "TYPES: CLEAN" || echo "TYPES: FAILED"
eslint . --max-warnings 0 && echo "LINT: CLEAN" || echo "LINT: FAILED"
```

### Use --no-color for parseable output
```bash
vitest run --reporter=verbose --no-color
eslint . --no-color
```

### Limit output for large results
```bash
grep -rn "pattern" src/ | head -50   # cap output
find src/ -name "*.ts" | wc -l       # count, not list
```

---

## Write/Edit Tool Patterns

### Always read before write
```
[read the file] → [verify target content] → [write/edit]
Never write to a file you haven't read in this session
```

### Edit precision
```
Target exact lines/content — not approximate
If the edit tool takes a search-replace:
  Search: exact string including whitespace
  Replace: exact new string
  Test: read the file back to confirm
```

### After write
```
[write file] → [read it back] → [confirm change is correct]
Tool completion ≠ correct result
```

---

## Git Tool Patterns

### Before any change
```bash
git status                           # are there uncommitted changes?
git log --oneline -10 -- [file]      # what changed recently?
git diff HEAD -- [file]              # any uncommitted changes to this file?
```

### After implementation
```bash
git diff                             # review the actual diff before claiming done
git diff --stat                      # files changed, insertions, deletions
```

### Stash for safety
```bash
git stash                            # before risky Tier 2 changes
git stash pop                        # restore if needed
```

---

## Tool Orchestration for GRAVITAS Phases

### Phase: Recon (batch everything)
```
[parallel batch]:
  read src/auth.ts
  + read src/auth.test.ts  
  + grep -rn "SESSION_TIMEOUT" src/
  + git log --oneline -5 -- src/auth.ts
  + read tsconfig.json
```

### Phase: Verify (sequential by necessity)
```
tsc --noEmit        → check output → if FAIL: stop
eslint .            → check output → if FAIL: stop
vitest run          → check output → record counts
→ compare to baseline
→ issue VERDICT
```

### Phase: Report
```
No tool calls needed — synthesize from collected outputs
Lead with verdict, evidence second, details third
```

---

## Common Tool Mistakes

| Mistake | Correct Approach |
|---------|-----------------|
| Sequential reads when parallel possible | Batch all reads |
| Grepping without --include filter | Use --include="*.ts" etc |
| Reading full file when only 20 lines needed | Read targeted range |
| Running tests one at a time | Run full suite: vitest run |
| Forgetting to read back after write | Always confirm write with read |
| Using shell when grep would be faster | grep for search, shell for complex ops |
| Retrying denied call verbatim | Diagnose, adjust, then retry |
