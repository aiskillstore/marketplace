# GRAVITAS Prompt Template

3-layer prompt assembly for optimal Gemini performance.
Every GRAVITAS task follows this structure.

---

## The 3-Layer System

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: System (static, load once, cacheable)          │
│  SKILL.md + references loaded only when needed           │
│  → Core protocol, 5 rules, tier classification           │
├─────────────────────────────────────────────────────────┤
│  Layer 2: Task (per-invocation, specific)                │
│  Goal, files, constraints, output format                 │
│  → What to do, where, and how to report it              │
├─────────────────────────────────────────────────────────┤
│  Layer 3: Context (delta for session/subagents)          │
│  Memory, prior findings, session failures               │
│  → What was learned, what failed, current state         │
└─────────────────────────────────────────────────────────┘
```

---

## Layer 1: System Prompt (SKILL.md)

Load once. Cacheable. Contains the full GRAVITAS protocol.

**Contents:**
- 5 Non-negotiable rules
- Tier classification (0/1/2)
- Adaptive reasoning and budget profiles
- Compact recovery state
- Conditional delegation
- Writing protocol
- Output format
- Verification chains

**When to load:** At session start. Once per session.
**When NOT to reload:** Every message (unnecessary, wastes tokens).

---

## Layer 2: Task Prompt

Constructed fresh for each task. Maximum specificity.

### Template

```markdown
## Goal
[One sentence: exactly what to accomplish]

## Files (scope)
- Target: [exact path or "find with grep pattern"]
- Related: [files that need reading or may be affected]
- Tests: [test file path]

## Constraints
- [what NOT to do — specific]
- [what to keep unchanged]
- [scope limit: "only touch files in src/auth/"]

## Context (from recon or prior work)
- [key finding from reconnaissance]
- [specific line numbers if known]
- [recent git changes if relevant]

## Output Format
[exact format — with an example when non-obvious]

## Tier
[0 / 1 / 2] — [brief justification]
```

### Example: Bug Fix Task

```markdown
## Goal
Fix SESSION_TIMEOUT: change from 5_000ms to 30_000ms.
Users are being logged out after 5 seconds.

## Files
- Target: src/auth/session.ts (timeout constant is at line 23)
- Test: src/auth/session.test.ts (assertion at line 47 needs update)
- Config: tsconfig.json (strict mode — types must be correct)

## Constraints
- Only touch these 2 files
- Don't refactor session module (out of scope)
- Don't change other timeout values (there are 3 others — leave them)
- Conventional commit format: "fix: increase session timeout to 30s"

## Context
- Recon found: SESSION_TIMEOUT = 5_000 at session.ts:23
- Test at session.test.ts:47 asserts toBe(5000) — must update
- 2 middleware files import session.ts — they'll need full suite run
- Last change to auth.ts: 6 weeks ago (unrelated)

## Output Format
## What Changed
[files, lines, behavior]

## Evidence
[verbatim vitest output]

VERDICT: PASS

## Tier
1 — moderate, 2 files, clear scope, low risk
```

---

## Layer 3: Context Delta (for resumption and optional subagents)

Minimal context injected at spawn time or after context compression.

### For a conditional subagent

```markdown
## Session Context — [agent name]

### Memory
- SESSION_TIMEOUT at src/auth/session.ts:23 (confirmed via grep)
- Test at session.test.ts:47 (asserts old value — needs update)

### Session Failures
- Tried editing config.ts — wrong file, SESSION_TIMEOUT not there
  → Do NOT touch config.ts

### Current Task State
- Explore: complete (findings above)
- Plan: complete (change lines 23 and 47)
- General: in progress (your job)
- Verify: pending

### Baseline
47/47 tests pass before this change
```

### For Long Sessions (after context compression)

```markdown
## Session Summary — [timestamp]

### What we've established
- Bug: SESSION_TIMEOUT is 5_000 but should be 30_000
- Location: src/auth/session.ts:23
- Test impact: session.test.ts:47 asserts old value
- Scope confirmed: only 2 files need changing

### Session failures
- config.ts was a dead end — do not retry

### Status
General agent implementing now. Verify pending.
```

---

## Assembling the Full Prompt

### Tier 0 (trivial)
```
[Layer 1: SKILL.md — already loaded]
[Layer 2: task only — 3-5 lines]
```

### Tier 1 (standard)
```
[Layer 1: SKILL.md]
[Layer 2: full task template]
[Layer 3: memory + session failures if any]
```

### Tier 2 (high-stakes)
```
[Layer 1: SKILL.md]
[Layer 1+: adversarial-critique.md]
[Layer 2: full task template with Tier 2 extensions]
[Layer 3: full context delta]
[User checkpoint before execution]
```

---

## Subagent Prompt Construction

When spawning a specialized agent, give them a complete Layer 2 + Layer 3:

### Explore Dispatch
```markdown
## Task for Explore
**Goal:** Map [specific area] to answer: [question]
**Scope:** [directory or file pattern]
**Read:** [specific files if known]
**Return:**
  - File map: [file] → [what it contains + key lines]
  - Dependency graph: who imports what
  - Risk flags: ⚠️ anything unexpected
  - Git context: last 5 changes to affected files
Do NOT edit anything.
```

### Verify Dispatch
```markdown
## Task for Verify
**Goal:** Verify the [feature/fix] is correct.
**Scope:** [test files, source files]
**Baseline:** [N] tests passing before change
**Run:**
  tsc --noEmit && eslint . && vitest run
**Edge cases to check:** [list specific cases]
**Return:** VERDICT: PASS or VERDICT: FAIL with full output
```

---

## Quick Templates by Task Type

### Bug Fix
```
Goal: Fix [symptom] — [suspected cause]
Files: [target] + [test]
Constraint: Stay in these files
Output: What Changed + Evidence + VERDICT
Tier: 1
```

### Feature Addition
```
Goal: Add [feature] to [module]
Files: [implementation files] + [test files]
Constraint: [scope limits]
Output: Full ## sections + VERDICT
Tier: 1 or 2 depending on auth/security involvement
```

### Refactor
```
Goal: Refactor [what] to [why]
Files: [all affected files — be exhaustive]
Constraint: No behavior changes, tests must pass unchanged
Output: What Changed + Evidence (before/after pass counts) + VERDICT
Tier: 2 if production module, 1 otherwise
```

### Security Fix
```
Goal: Fix [vulnerability] in [location]
Files: [target] + [tests] + [related modules]
Constraint: Don't introduce new endpoints. Don't change auth logic except the fix.
Output: Threat model + Fix + Security tests + VERDICT
Tier: 2 always
```
