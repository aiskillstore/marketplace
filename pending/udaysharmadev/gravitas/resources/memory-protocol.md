# Memory Protocol

Persistent context across sessions. Don't repeat mistakes. Don't re-discover
what you already learned.

---

## Two Memory Layers

### Layer 1 — Session Memory (in-session, ephemeral)

Created at task start. Lost when session ends.

**File:** `SESSION_FAILURES.md` in the project root or working dir.

```markdown
## Session Failures — 2026-09-08

- **auth timeout**: Tried changing SESSION_TIMEOUT in config.ts:15. Wrong file.
  Actual location is src/auth/session.ts:23. Do not retry config.ts.

- **test runner**: Tried `npm test`. Returns error. Use `vitest run` directly.
  See package.json scripts for the right command.
```

**When to write:**
- Every failed approach, immediately after failure
- Every wrong file path discovered
- Every command that doesn't work as expected
- Every assumption that turned out false

**When to read:**
- Before retrying any approach
- Before touching a file that might have been searched before
- At task start if the file exists from previous work

---

### Layer 2 — Project Memory (cross-session, persistent)

Stored in `GRAVITAS_MEMORY.md` at project root, or `.gravitas/memory/` directory.

**Format:**

```markdown
---
type: user | feedback | project | reference
name: short-kebab-slug
description: one-line summary (used to decide relevance at recall time)
created: 2026-09-08
updated: 2026-09-08
---

[The fact. Concrete. Actionable. Not vague.]

**Why:** [Why this matters]
**How to apply:** [When to use this memory]
**Related:** [[other-memory-slug]]
```

---

## Memory Types

### `user` — Who is the user

```markdown
---
type: user
name: user-preferences
description: Developer preferences and working style
---

Prefers explicit error messages over silent failures.
Uses conventional commit format (feat/fix/chore/docs).
Wants terminal commands shown to verify changes.
Works in TypeScript with strict mode on.

**Why:** Shapes how to write commit messages and code.
**How to apply:** Always show the verify command. Use conventional commits.
```

### `feedback` — What the user has corrected

```markdown
---
type: feedback
name: test-runner-preference
description: Use vitest run not npm test for this project
---

User corrected me: `npm test` runs lint before tests and is slow. For fast
iteration, use `vitest run` directly. Only use `npm test` for CI checks.

**Why:** Saves time, matches user's workflow.
**How to apply:** Any time I'd run tests, use `vitest run` not `npm test`.
```

### `project` — Ongoing context not in code

```markdown
---
type: project
name: auth-rewrite-context
description: Auth module is being rewritten — old and new systems co-exist
---

The auth module is mid-migration. `/src/auth/` is the new system.
`/src/auth_legacy/` is the old system still in production for 20% of users.
Do not touch legacy auth unless explicitly asked. Migration completes 2026-10-01.

**Why:** Prevents accidentally breaking legacy auth.
**How to apply:** Any auth task — check which system is in scope first.
**Related:** [[migration-timeline]]
```

### `reference` — External resources

```markdown
---
type: reference
name: stripe-webhook-docs
description: Stripe webhook signature verification docs
---

https://stripe.com/docs/webhooks/signatures
Used in src/webhooks/stripe.ts. Check here before any Stripe webhook changes.

**Why:** The implementation must match the Stripe spec exactly.
**How to apply:** Load before any Stripe webhook work.
```

---

## Memory Index — GRAVITAS_MEMORY.md

The index file. One line per memory. Loaded into context each session.
Never put full memory content here.

```markdown
# GRAVITAS Memory Index

## User
- [user-preferences](memory/user-preferences.md) — dev preferences, commit style, verify commands

## Feedback
- [test-runner-preference](memory/test-runner-preference.md) — vitest run, not npm test
- [import-style](memory/import-style.md) — named exports only, never default

## Project
- [auth-rewrite-context](memory/auth-rewrite-context.md) — legacy and new auth co-exist
- [db-schema](memory/db-schema.md) — schema location and migration approach

## Reference
- [stripe-webhook-docs](memory/stripe-webhook-docs.md) — webhook signature verification
```

---

## Memory Lifecycle

### Before saving

1. Search for existing memory that already covers it
2. Update rather than duplicate
3. Delete memories that turned out to be wrong

### Don't save

- Things in git history (git log is the memory)
- Things derivable from code (the code is the memory)
- Things only relevant to the current conversation
- What the user said verbatim (extract the useful fact instead)

### When to save

- Non-obvious things about the project
- User corrections and preferences
- Failed approaches and why they failed
- External resources needed repeatedly
- Architecture decisions not in code comments

---

## Recall Protocol

At session start, if `GRAVITAS_MEMORY.md` exists:
1. Read the index
2. Load memories relevant to today's task
3. Verify any memories that reference files (the file may have moved)
4. Note memories that seem outdated — flag for update

**Don't blindly follow stale memories.** If a memory says "function X is at
line 23" — verify it. Lines change. Verify before recommending.

---

## Cross-Session Continuity Pattern

When continuing a multi-session task:

```markdown
## Task Status — [task name]

### Completed
- [x] Step 1: Auth recon — findings in memory/auth-rewrite-context.md
- [x] Step 2: Plan — approved by user 2026-09-07

### In Progress
- [ ] Step 3: Implementation — started src/auth/session.ts, not done

### Blocked
- Step 4: Verify — can't run tests until step 3 done

### Session Failures (this session)
- Tried editing config.ts for timeout. Wrong file. Actual: src/auth/session.ts:23
```

Save this as `GRAVITAS_TASK_STATUS.md` for multi-day tasks.
