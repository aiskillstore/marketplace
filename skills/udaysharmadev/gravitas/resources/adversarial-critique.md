# Adversarial Critique Protocol

Attack your own plan before executing. Find the failures before the computer does.

---

## Why Adversarial Critique

Models rationalize. Given a plan they wrote, they find reasons it's good.
This resource forces you to do the opposite: assume the plan is broken and
prove it isn't. A plan that survives adversarial critique ships clean code.
A plan that skips it ships bugs.

---

## The 7 Attack Vectors

For every plan, attack it on these 7 dimensions:

### Vector 1 — Wrong File / Wrong Line

```
Attack: "What if the target is not where I think it is?"
Check:
  - Did I grep to confirm the file exists?
  - Did I read the actual line, not rely on Plan's description?
  - Are there multiple files with similar names? (auth.ts vs auth.tsx vs auth/index.ts)
  - Did git log show the file was recently moved?
```

### Vector 2 — Downstream Breakage

```
Attack: "What else depends on what I'm changing?"
Check:
  - Who imports this module? (grep -r "from './auth'" src/)
  - Who calls this function? (grep -rn "functionName(" src/)
  - What tests outside this file assert on this behavior?
  - What API contracts does this expose?
```

### Vector 3 — Test Coverage Gaps

```
Attack: "What scenarios do the tests NOT cover?"
Check:
  - Is there a null input test?
  - Is there an empty string test?
  - Is there a max-value / min-value test?
  - Is there an auth/permissions test?
  - Is there a concurrent access test? (if relevant)
  - Are there integration tests, or only unit tests?
```

### Vector 4 — Config / Environment Mismatch

```
Attack: "What config assumptions might be wrong?"
Check:
  - Does the change work in strict TypeScript mode?
  - Does it work with the current linter rules?
  - Does it work in the CI environment (Node version, Python version)?
  - Are there env vars this depends on that might not be set?
```

### Vector 5 — Concurrency / Race Conditions

```
Attack: "What if two requests hit this simultaneously?"
Check:
  - Is there shared state?
  - Is there a race condition on the session/cache?
  - Does the db operation need a transaction?
  - Is there a retry that could create duplicates?
```

### Vector 6 — Rollback Failure

```
Attack: "What if we need to undo this?"
Check:
  - Is there a rollback path?
  - Does the migration have a down() function?
  - Will reverting the code also revert the data?
  - If this is a feature flag, can we flip it off?
```

### Vector 7 — Security Regression

```
Attack: "Does this introduce or loosen security controls?"
Check:
  - Does this expose a new endpoint without auth?
  - Does this bypass an existing permission check?
  - Does this accept user input without sanitization?
  - Does this log sensitive data?
  - Does this change session/token behavior?
```

---

## Critique Output Format

```markdown
## Adversarial Critique — [plan name]

### Vector 1: Wrong Location
- Risk: LOW — grepped and confirmed auth.ts at src/auth/session.ts:23
- Evidence: `grep -rn "SESSION_TIMEOUT" src/` → one result

### Vector 2: Downstream
- Risk: MEDIUM — 2 middleware files import from session.ts
  - src/middleware/auth.ts:7 — calls validateSession()
  - src/routes/auth.ts:4 — calls createSession()
- Mitigation: run full test suite after, not just session.test.ts

### Vector 3: Test Coverage
- Risk: LOW — 23 tests cover normal cases
- GAP: No test for concurrent session creation
- Mitigation: add one concurrency test before shipping

### Vector 4: Config
- Risk: LOW — TypeScript strict mode on, change is fully typed

### Vector 5: Concurrency
- Risk: LOW — session creation uses DB transaction (line 45)

### Vector 6: Rollback
- Risk: LOW — timeout change is reversible, no data migration

### Vector 7: Security
- Risk: LOW — change only affects timeout value, no auth logic

### Overall Risk: MEDIUM (due to Vector 2)
### Recommendation: proceed with full test suite run
```

---

## Critique Thresholds

| Risk Level | Protocol |
|-----------|---------|
| ALL LOW | Proceed to implementation |
| ANY MEDIUM | Proceed, but run full test suite (not just target tests) |
| ANY HIGH | Stop, revise plan, address risk, re-critique |
| Unmitigated HIGH | Escalate to Tier 2, get user checkpoint |

---

## Common Failure Patterns (Historical)

These are the failures that actually happen. Check for all of them.

### Timeout / Constant Changed in Wrong File
Multiple files often define similar constants. The bug file is rarely the obvious one.
```bash
grep -rn "SESSION_TIMEOUT\|timeout.*=.*[0-9]" src/ --include="*.ts"
```

### Test Assertion Mismatch
Plan says "update function" but the test still asserts on the old value.
```bash
grep -rn "toBe(5000)\|assertEqual.*5000\|expect.*5000" src/
```

### Import Style Breaks Tree Shaking
Changing named export to default export breaks all importers.
```bash
grep -rn "import.*from.*auth" src/ --include="*.ts"
```

### DB Migration Without Transaction
Migration fails halfway, leaves DB in inconsistent state.
Check: does `down()` exist? Is the `up()` in a transaction?

### Auth Middleware Order
Adding middleware in wrong order bypasses auth checks.
Check: middleware registration order in app setup file.

---

## The Pessimist's Checklist

Before finalizing any plan:

```
□ "What if the file isn't where I think it is?"
□ "What if three other files depend on this?"
□ "What if the tests don't cover this case?"
□ "What if CI uses a different config than local?"
□ "What if two users hit this simultaneously?"
□ "What if we need to undo this in production?"
□ "What if this loosens a security check?"
□ "What am I most likely wrong about?"
```

The last question is the most important. Answer it honestly.
