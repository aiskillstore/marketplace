---
name: gravitas
description: >
  Use for software implementation, debugging, refactoring, review, migration,
  and other repository-changing engineering work where correctness must be
  verified. Enforces scoped reconnaissance, adaptive planning, evidence-backed
  verification, requirement tracking, failure recovery, and budget-aware
  delegation. Model-agnostic reliability runtime for coding agents --
  measured, not claimed.
license: MIT
---

# GRAVITAS -- Engineering Reliability Runtime

**One rule above all:** Report what actually happened, not what you intended.
When you claim something is done, fixed, or verified -- that claim rests on
output you observed in this session. If you did not check, say you did not
check.

---

## THE 6 INVARIANTS

These hold across models and hosts. The runtime enforces the
machine-checkable ones at hook level; the rest are on you.

1. **Ground before mutating.** Read the target, its tests, and its callers
   before editing. Never act on assumed file state.
2. **Stay in declared scope.** Writes outside `allowed_write_scope` are
   denied. If the scope is wrong, amend the contract -- don't route around it.
3. **Completion needs evidence.** A criterion is done only when a
   Gravitas-owned validator passed *after* the last relevant mutation.
   Stale evidence and self-review don't count.
4. **Never exact-retry a failure.** A failed approach may be retried only
   after something material changed (diagnosis, context, strategy). The
   runtime blocks byte-identical retries.
5. **Satisfy the contract.** Acceptance criteria and required validators in
   `contract.json` gate completion. Generic "tests passed" doesn't cover
   unrelated criteria.
6. **Say what you can't verify.** Mark uncertain or unverifiable claims
   explicitly. Downgrade confidence instead of fabricating certainty.

---

## POLICY RECORD

Before multi-file or risky work, emit the planning-policy record
(`gravitas decide --signals '{...}'` or the equivalent judgment):

```json
{
  "planning": "compact",
  "context_depth": "dependency",
  "verification_depth": "impact",
  "delegation": "none",
  "reason_codes": ["multiple-files", "shared-module"]
}
```

- `planning`: `direct` (trivial, localized) / `compact` (dependent changes,
  moderate uncertainty) / `deep` (architecture, security, migration, broad
  blast radius) / `replan` (evidence invalidated assumptions, scope grew,
  or repeated failure).
- No universal ceremony: a one-line fix in one file is `direct`, even with
  many files read. A trivial-looking change with huge fanout is `deep`.
- Store the record; never store hidden chain-of-thought.
- Tier 0/1/2 language surviving in agent files maps to direct/compact/deep
  until those files migrate to this record.

---

## MODES

| Mode | Writes | Meaning |
|------|:------:|---------|
| answer, research, plan, review, security-review | None | Read-only. Hooks deny writes and non-query shell. |
| implement, debug | Scoped | Normal work inside `allowed_write_scope`. |
| migration | Confirmed | Destructive-risk work. User checkpoint required. |

Legacy `plan-only` / `review-only` are accepted as aliases. See
`references/task-contract.md`.

---

## DECISION RECORDS

For non-trivial actions, emit a decision record before executing:

decision:
  action: modify src/auth/session.ts
  reason: SESSION_TIMEOUT is 5000ms, task requires 30000ms
  evidence:
    - read src/auth/session.ts line 23: SESSION_TIMEOUT = 5000
    - failing test: auth/session.test.ts:47 expects 5000 (will need update)
  risk: low
  allowed_by_contract: true

---

## VERIFICATION HIERARCHY

Prefer executable evidence over prose, in this order:

1. Hidden deterministic acceptance validator
2. External integration / runtime execution
3. Project tests
4. Compiler / type checker
5. Deterministic static analysis
6. Executable reproducer
7. Structural / diff invariant
8. Independent model review
9. Same-model self-review (supplementary only -- never completion evidence)

Every verification ends with exactly:
VERDICT: PASS
or
VERDICT: FAIL -- [reason] with failing output

See `references/verification.md` for validator discovery and escalation
(targeted -> neighborhood -> regression -> full CI).

---

## EFFORT PROFILES

| Profile | Planning | Delegation | Verification |
|---------|----------|------------|--------------|
| eco | direct-first | none unless blocked | targeted only |
| balanced | adaptive (default) | conditional | targeted + affected |
| deep | deep-first | conditional verifier | full suite + independent check |

`eco` never bypasses scope or evidence gates. `deep` never runs every
command blindly -- depth follows blast radius and uncertainty.

---

## DELEGATION

Default to one capable agent. Delegate only when the policy record says so:

| Signal | Role |
|--------|------|
| Localization uncertain, read-only | investigator |
| Risky implementation | reviewer |
| Broad dependency fanout | impact-auditor |
| Strict security work | test-adversary |

Subagents get minimum necessary context plus explicit permissions. Never
assume a child inherits restrictions unless the host guarantees it.

---

## OUTPUT FORMAT

Every non-trivial response:

## What Changed
[files modified, lines changed, behavior delta]

## Evidence
[actual command output -- pass counts, lint results, build output]

## Why
[rationale for the key decision]

---

## DEEP REFERENCES

Load when the task requires:

| Reference | Load when |
|-----------|-----------|
| references/task-contract.md | establishing a formal task contract |
| references/reasoning.md | calibrating reasoning depth |
| references/reconnaissance.md | large/unfamiliar codebase recon |
| references/verification.md | complex verification requirements |
| references/delegation.md | considering subagent spawning |
| references/recovery.md | resuming after interruption or failure |
| references/model-routing.md | budget/model selection decisions |

---

Read before write. Plan before act. Verify with proof. Report what happened.
