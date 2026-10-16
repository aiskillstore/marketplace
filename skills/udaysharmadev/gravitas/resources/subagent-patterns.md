# Subagent Patterns

When to spawn, how to spawn, how to communicate, how to synthesize.
Coordination patterns for investigator, reviewer, and implementer roles.

---

## Core Decision: Spawn or Act Directly?

```
Should I spawn a subagent?

Is the task a single-step lookup?
  → NO. Act directly. Subagent overhead isn't worth it.

Is the task complex enough to benefit from specialization?
  → YES. Use specialized agents.

Do I have independent work streams I could parallelize?
  → YES. Spawn in parallel.

Would the results dump fill my context window unnecessarily?
  → YES. Delegate to keep conclusion, not file dumps.
```

---

## When to Spawn

| Scenario | Action |
|----------|--------|
| Single file lookup | Act directly |
| Find a symbol in known file | Act directly (grep) |
| Unknown codebase — need to map | Spawn Explore |
| Multi-file refactor | Spawn Plan → General → Verify |
| Independent feature areas | Spawn parallel General agents |
| Complex architecture decision | Spawn Plan with adversarial mode |
| Full verification pass | Spawn Verify |
| Security review | Spawn Verify with security mode |

---

## Spawn Patterns

### Pattern 1: Sequential Pipeline

Use when each agent needs the previous agent's output.

```
Explore → Plan → General → Verify
```

```
# Step 1
explore_result = spawn(Explore, task="Map auth module", scope="src/auth/")

# Step 2 (needs explore_result)
plan_result = spawn(Plan, task="Plan timeout fix", context=explore_result)

# Step 3 (needs plan_result)
impl_result = spawn(General, task="Implement", plan=plan_result)

# Step 4 (needs impl_result)
verdict = spawn(Verify, task="Verify auth tests", scope="src/auth/")
```

### Pattern 2: Parallel Fan-Out

Use when work streams are independent.

```
         ┌→ General (feature A) → Verify A ┐
Explore  →│                                  → Synthesize
         └→ General (feature B) → Verify B ┘
```

```
# Step 1
explore_result = spawn(Explore, task="Map full codebase")

# Step 2 (parallel — A and B are independent)
[plan_A, plan_B] = spawn_parallel([
  Plan(task="Plan feature A"),
  Plan(task="Plan feature B"),
])

# Step 3 (parallel — A and B are independent)
[impl_A, impl_B] = spawn_parallel([
  General(task="Implement A", plan=plan_A),
  General(task="Implement B", plan=plan_B),
])

# Step 4 (parallel)
[verdict_A, verdict_B] = spawn_parallel([
  Verify(task="Verify A"),
  Verify(task="Verify B"),
])
```

### Pattern 3: Fork (for large context separation)

Use when you want to keep a subtask's file dumps out of your context.

```
# Your context stays clean — fork handles the dump
fork_result = spawn(fork, task="Find all usages of deprecated API")
# fork returns: summary of findings, not raw file content
```

---

## Dispatching an Agent

Every dispatch message must include:

```markdown
## Task for [AgentType]
**Task:** [One precise sentence]
**Scope:** [Specific files, directories, or "find with grep"]
**Constraints:** [What NOT to do]
**Context:** [Relevant findings from prior agents]
**Return:** [Exactly what to send back]
```

### Example Dispatch: Explore

```markdown
## Task for Explore
**Task:** Map the authentication module to understand session timeout handling.
**Scope:** src/auth/ and any files that import from it
**Constraints:** Read-only. Don't edit anything.
**Return:**
  - File map with key line numbers
  - Dependency graph (imports/exports)
  - Recent git changes to the auth module
  - Any risk flags (⚠️)
```

### Example Dispatch: General

```markdown
## Task for General
**Task:** Update SESSION_TIMEOUT from 5_000 to 30_000ms.
**Scope:** src/auth/session.ts and src/auth/session.test.ts
**Plan:**
  1. src/auth/session.ts:23 — change constant value
  2. src/auth/session.test.ts:47 — update assertion to toBe(30_000)
**Constraints:**
  - Stay in these two files only
  - Do not refactor unrelated code
  - Read both files before editing
**Return:** VERDICT: PASS or VERDICT: FAIL with test output
```

### Example Dispatch: Verify

```markdown
## Task for Verify
**Task:** Verify the session timeout fix is correct.
**Scope:** src/auth/
**Baseline:** 47/47 tests passing before change
**Required:**
  - Run: tsc --noEmit && eslint . && vitest run
  - Compare to baseline
  - Check edge cases: null session, expired session, concurrent sessions
**Return:** VERDICT: PASS or VERDICT: FAIL with full output
```

---

## Receiving Agent Results

When an agent reports back:

1. **Read the VERDICT first** — is it PASS or FAIL?
2. **If FAIL** → diagnose from the output, dispatch General for fix
3. **Don't relay raw file dumps** — synthesize findings
4. **Resolve conflicts** — if two agents disagree, reason through it explicitly

### Synthesis Pattern

```
Explore found: SESSION_TIMEOUT at src/auth/session.ts:23
Plan says: change to 30_000, also update test at line 47
General reports: changed both files, VERDICT: PASS, 47/47 tests
Verify confirms: VERDICT: PASS, 47/47 tests, lint clean

→ Final synthesis:
  "Fixed SESSION_TIMEOUT from 5_000 to 30_000. Updated test assertion.
   47/47 tests pass. Lint clean. VERDICT: PASS."
```

---

## Agent Communication Rules

- Never fabricate an agent's results — wait for actual output
- Never mark task complete before Verify issues VERDICT: PASS
- If a spawned agent is stuck, don't re-ask the same question — adjust
- Relay conclusions, not file dumps, to the user
- Maximum fix cycles: 3. After 3 FAIL verdicts, escalate to user

---

## Anti-Patterns

| Anti-Pattern | Why Wrong | Fix |
|-------------|-----------|-----|
| Spawn for single-file lookup | Overhead > benefit | Act directly |
| Sequential when parallel possible | Wastes time | Batch independent spawns |
| Relay raw file dump to user | Clutters context | Synthesize findings |
| Spawn without precise task | Agent does wrong thing | Write exact task + scope |
| Mark done before VERDICT: PASS | Ships bugs | Always verify before claiming done |
| Re-spawn same agent on same task | Retry loop | Change the task or the approach |
