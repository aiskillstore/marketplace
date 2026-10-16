# Context Management

Large context windows are precision instruments, not dump bins.
Attention degrades in the middle. Structure matters.

---

## The Attention Curve

In a long context, current Pro-class models give highest attention to:
- The start of the context (task, instructions, constraints)
- The end of the context (output format, examples, final instruction)
- Lowest attention: the middle (large code dumps, long docs)

```
Attention level:
HIGH  ████████████████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒████████████████████
      [start: task,     ] [middle: content     ] [end: format, examples]
      instructions         dumps, docs            VERDICT requirements
```

**Implication:** Put critical instructions at start AND end.
Critical output format requirements go at the end.

---

## Context Budgeting

Know roughly how many tokens you're working with:

| Content | Approx Tokens |
|---------|--------------|
| 1 line of code | ~10 |
| 100-line file | ~1,000 |
| 1,000-line file | ~10,000 |
| Full codebase (medium) | ~100,000 |
| Full codebase (large) | ~500,000–1M |

**Budget allocation for a 200K task:**

```
System/skill instructions:  ~5K   (2.5%)
Task description:           ~1K   (0.5%)
Recon context:              ~50K  (25%)
Implementation + tests:     ~100K (50%)
Verification output:        ~10K  (5%)
Working space:              ~34K  (17%)
```

---

## When to Use Large Context

**Do use large context for:**

- Full codebase review (need to see everything to find the issue)
- Multi-file refactoring (need all files to ensure consistency)
- Cross-file dependency tracing (can't grep your way to understanding)
- Document analysis (the document is the context)

**Don't use large context for:**

- Single-file fixes (grepping line numbers is sufficient)
- Questions about one function (targeted read is better)
- Tasks where progressive disclosure is more natural

---

## Context Structure (by Task Size)

### Small task (single file, < 50K tokens)
```
[task description]
[target file content]
[constraints]
[output format]
```

### Medium task (2-5 files, 50K–200K tokens)
```
[task + goal]
[constraints]
[file 1 — most important]
[file 2 — supporting]
[file 3 — tests]
[output format + example]   ← end: high attention
```

### Large task (full codebase, 200K–1M tokens)
```
[task + goal]               ← start: high attention
[critical constraints]      ← start: high attention
--- large context dump ---
[files by relevance, most important last before output]
--- end ---
[output format + examples]  ← end: high attention
[VERDICT requirements]      ← end: high attention
```

---

## Progressive Disclosure Strategy

Don't load the whole codebase when you can find what you need.

### Step 1 — Search First
```bash
grep -rn "SESSION_TIMEOUT" src/ --include="*.ts"
# → finds src/auth/session.ts:23
# You now need 1 file, not the whole src/
```

### Step 2 — Load Targeted Context
```
read src/auth/session.ts (142 lines)
read src/auth/session.test.ts (65 lines)
# Total: ~2K tokens, not 200K
```

### Step 3 — Expand Only If Needed
```
# If the fix has unexpected downstream effects:
grep -rn "from.*session" src/ --include="*.ts"
# → 2 more files to read
# Still: ~5K tokens total
```

---

## Long Session Management

When a session grows long:

### Recognize context pressure
Signs that context is getting crowded:
- You're unsure what state a file is in (was it edited?)
- You're repeating recon you already did
- You're uncertain about decisions made earlier

### Response: verify, don't rely on memory
```
WRONG: "Earlier I established that SESSION_TIMEOUT is at line 23..."
RIGHT: [grep SESSION_TIMEOUT src/] → confirm current state
```

### Cross-session continuity
For multi-day tasks, use memory protocol:
- Save task status to GRAVITAS_TASK_STATUS.md
- Save non-obvious findings to GRAVITAS_MEMORY.md
- Next session: read memory first, then recon to verify it's current

---

## Subagent Context Isolation

When spawning subagents, be deliberate about what context to pass:

### Pass to subagent:
- The specific task
- Relevant findings (not raw file dumps)
- Constraints
- Output format

### Don't pass:
- Your full conversation history
- Raw file content (subagent can read it themselves)
- Intermediate work the subagent doesn't need

### Result from subagent:
- Receive conclusions, not file dumps
- The subagent's work stays in their context, not yours
- You keep: VERDICT, key findings, specific changes made

---

## Token-Efficient Patterns

### Read excerpts, not whole files
```
GOOD: read src/auth.ts lines 20-50    → ~300 tokens
BAD:  read src/auth.ts (full 2000 lines) → ~20,000 tokens
```

### Summarize large outputs
```
$ grep -rn "SESSION_TIMEOUT" src/
  # 47 matches across 23 files

→ Don't paste all 47 matches
→ Summarize: "SESSION_TIMEOUT appears in 23 files. Key ones: [3 most relevant]"
```

### Use line references
```
GOOD: "The issue is at src/auth.ts:23 (SESSION_TIMEOUT = 5_000)"
BAD:  [paste entire auth.ts to show line 23]
```

---

## Context Hygiene Rules

- Don't load context you won't use
- Don't paste full files when line references suffice
- Don't accumulate tool output in chat without summarizing
- Don't repeat prior context — reference it by location
- Do read back to verify after edits (small targeted read, not full file)
- Do structure context with task first, content middle, format last
