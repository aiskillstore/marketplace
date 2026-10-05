# Implementation and Verification

Scale the workflow to risk while always preserving evidence.

## Change sizing

For a small local change:

1. Inspect the implementation, callers, tests, and configuration.
2. Make the narrowest coherent edit.
3. Run focused tests and the nearest static checks.

For a public API, persistence, authentication, concurrency, deployment, migration, or cross-module change:

1. Map consumers and compatibility constraints.
2. State failure, rollback, and migration behavior.
3. Add contract, integration, or end-to-end coverage as appropriate.
4. Run broader checks and a realistic smoke test when practical.

## Test selection

| Risk | Minimum useful evidence |
| --- | --- |
| Pure deterministic logic | Unit tests with boundaries and invalid input |
| Public API or library | Contract tests, types/compilation, realistic usage examples |
| Adapter or persistence | Integration test against realistic semantics |
| Authorization or sensitive data | Allowed and denied cases, ownership checks, non-disclosure |
| Concurrency or retries | Duplicate, timeout, cancellation, ordering, and cleanup cases |
| Migration or deployment | Compatibility sequence, dry run or staging evidence, success and rollback signals |

Tests should validate observable behavior. Avoid coupling them to private methods or incidental object structure.

## Verification order

Run fast, focused checks first so failures are attributable. Then expand according to blast radius:

1. Targeted tests.
2. Type checking or compilation.
3. Lint and formatting verification.
4. Related package or module tests.
5. Full build or suite when justified.
6. Runtime or integration smoke checks.

Use project-provided commands. Check scripts before running them and avoid fixing, snapshot-updating, migration, deployment, or destructive options unless they are in scope.

## Failure handling

When a check fails:

- determine whether the change caused it;
- fix in-scope regressions;
- do not rewrite unrelated failing areas;
- report pre-existing or environment-blocked failures precisely;
- never disable a meaningful check to obtain a green result.

## Completion evidence

The final report should identify executed commands, outcomes, anything not run, and why. “Looks correct” is not verification.
