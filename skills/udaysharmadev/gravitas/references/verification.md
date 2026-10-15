# Gravitas -- Verification Reference

## The Hierarchy

Prefer external, deterministic evidence over model self-assessment:
1. Compiler / type checker
2. Unit test runner (actual output)
3. Integration test runner
4. Static analysis (lint, security scan)
5. Deterministic validator
6. Diff inspection
7. Model self-review (supplementary only, lowest weight)

Model self-critique is not verification. It is a weak signal to use when better evidence is unavailable.

## Evidence Requirements by Claim

| Claim | Minimum Required Evidence |
|-------|------------------------|
| Tests pass | Pass count + total + 0 failures from actual run |
| Lint clean | Linter output with 0 warnings |
| Type-safe | tsc/mypy/pyright output clean |
| Build succeeds | Build output last line |
| No regressions | Before count vs after count, both shown |
| Fixed | Before behavior observed, after behavior observed |
| Requirement covered | Evidence entry in ledger linking criterion to proof |

## VERDICT Format

Every verification session ends with exactly one of:
VERDICT: PASS
or
VERDICT: FAIL -- [specific reason]
[failing output]

Never: VERDICT: PASS (with caveats) -- that is a FAIL.
Never: VERDICT: PARTIAL PASS -- that is a FAIL.

## Regression Baseline

Before any change:
1. Run full test suite, record exact count
2. Note existing lint warnings (do not introduce new ones)

After changes:
1. Run full test suite
2. After count >= before count -- not a regression
3. New lint warnings -- must fix before VERDICT: PASS

## Scope-Appropriate Verification

Never run every validator blindly. Discover first, then escalate:

```bash
gravitas validators --root . --changed src/auth/session.ts --depth impact
```

| Depth | Runs | Expands when |
|-------|------|--------------|
| targeted | test validators scoped to changed files | always (baseline) |
| impact | + callers/tests/configs from the repo graph | depth=impact, failure evidence, broad fanout |
| suite | + all project validators | depth=full, failure evidence, release context |
| full | + CI workflows | release context only |

Validators come from `gravitas_verify.discover_validators`: project
config + resolvable binary = catalog entry with provenance. Nothing is
assumed from language. Empty catalog means "say so", not "invent commands".

| Scope | Verification |
|-------|-------------|
| Single function change | Targeted: run tests for that module |
| Multi-file feature | Impact: run all tests for changed modules + callers |
| Shared utility change | Suite: run full test suite |
| Auth/security/schema | Full: complete suite + static analysis |

## Requirement-Evidence States

Each criterion is PENDING, SUPPORTED, PASS, FAIL, BLOCKED, or
UNVERIFIABLE (`gravitas summarize` shows the matrix). Only fresh
Gravitas-owned validator PASS gates completion -- evidence predating the
final mutation is stale and must be re-run. Non-owned evidence
(SUPPORTED) never opens the gate.

## Reproduction-First Debugging

```
symptom -> reproduce -> record failing evidence -> localize -> patch
       -> rerun the SAME reproduction -> regression verification
```

```bash
# 1. Confirm the bug with a reproducer (must FAIL before the fix)
gravitas repro --session-dir <dir> --criterion-id AC-1 --phase before -- ./repro.sh
# 2. Patch, then rerun the same reproducer (must PASS after)
gravitas repro --session-dir <dir> --criterion-id AC-1 --phase after -- ./repro.sh
```

A bug is not confirmed because code "looks suspicious". When reproduction
is impossible, record why instead of fabricating one:

```bash
gravitas repro --session-dir <dir> --criterion-id AC-1 --unreproducible \
  --reason "requires production payment hardware"
```

This stores UNVERIFIABLE, which blocks the finish gate until the contract
is explicitly amended. Confidence is reduced, honestly.

## Adversarial Edge Cases (strict/security work)

For security, auth, algorithms, and stateful behavior, expand seeds into
deterministic boundary variants and execute them through a trusted project
validator; surprises become regression tests:

```bash
gravitas edge-cases --seeds '["5", "", []]'
gravitas validator --session-dir <dir> --validator-id unit --criterion-id AC-1 -- ./run_case.sh
```

Trigger selectively: strict/deep mode, repeated repairs, high
uncertainty. Development tests and hidden benchmark validators stay
separate; self-review never counts as correctness evidence.

## When Self-Review Is Acceptable

Only as supplementary evidence when no test runner is available, the change is purely cosmetic, or the validator cannot run in current environment. State the limitation explicitly:
Note: test runner unavailable in this environment. Diff review only.
VERDICT: CONDITIONAL PASS -- requires human test execution before merge.

## Completion Gating

The Stop hook will not allow task completion until:
- All acceptance criteria have evidence entries in the ledger
- Required validators have been observed to run
- No known failures are unresolved
- The agent's completion claim is consistent with the evidence trace
