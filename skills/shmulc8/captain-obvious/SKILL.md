---
name: captain-obvious
description: Audit TypeScript and Python tests for assertions that cannot fail or check nothing, and guide test authoring with a contract and regression gate. Use when writing or changing tests to avoid low-value coverage, or cleaning redundant, tautological, duplicated, or AI-generated tests. Cleanup runs bundled deterministic scanners; authoring guidance needs no scan during red-green TDD.
---

# Captain Obvious

Deletes tests that assert what is already guaranteed — by the compiler, by the
mock framework, or by the laws of logic. These tests burn CI time, inflate
coverage confidence, and can never catch a regression. They are the signature
of AI-generated test suites (empirical studies find test smells in 38–100% of
LLM-generated tests).

For cleanup, two deterministic scripts in `scripts/` do the heavy lifting.
Run them, interpret the report, clean up the residue, and verify nothing broke.
**Do not** hand-scan test files or spawn subagents per file — one script
invocation scans the whole project. During test authoring, use the gate below
without running a cleanup scan.

## Authoring gate

Before adding or changing a test, answer four questions:

1. What observable behavior or independent contract does it protect?
2. What plausible regression would make it fail for the intended reason?
3. Is that contract already covered at a stronger boundary? If so, what
   distinct risk does this test cover?
4. Does it require a production export, flag, wrapper, or injection hook used
   only by tests? Can the real entry point be tested instead?

If a new bug regression test can be run safely against the pre-fix baseline,
verify that it fails for the intended reason and passes with the fix. Use
`references/prevention.md` for examples of patterns to avoid. A test need not
contain a direct assertion to be valuable: a deliberate must-not-raise test
can guard a real contract.

## Workflow

### 1. Detect the stack(s)

- TypeScript/JavaScript: `*.test.*` / `*.spec.*` (ts, tsx, mts, cts, js, jsx,
  mjs, cjs) or files under `__tests__`; a `tsconfig.json` enables type checks.
- Python: `test_*.py` / `*_test.py` files (pytest or unittest).
- A repo can have both; run both detectors.

### 2. Safety first

The fix step edits test files in place. Both scripts enforce this themselves:
`--fix` exits 2 unless the target is a git repository with a clean working
tree (untracked files are fine). If it refuses, stash or commit rather than
reaching for `--force` — `--force` removes the only undo path there is
(`git checkout -- <files>`), so use it only when the user has explicitly
accepted that.

Trust boundary: scanning executes the project's own toolchain. mypy loads
`[tool.mypy] plugins` from the repo's config as in-process Python;
`--mypy "uv run mypy"` / `"poetry run mypy"` resolve (and can run) the
repo's dependencies; the TS side loads the repo's own `typescript`
package. Run the scan only on repositories you would be willing to run
`mypy`/`tsc` in yourself.

Note: when installed as a plugin, a write-time PreToolUse hook may also be
active — if a test-file Write/Edit is denied with a "captain-obvious:"
reason during cleanup rewrites, fix the flagged assertions instead of
re-trying the same content (see `references/prevention.md`). Both scanners
also support `--file <path> [--stdin]` for a syntactic-only single-file
scan (JSON to stdout; no mypy/tsc, no side effects).

### 3. Scan (report-only)

```bash
node <skill-dir>/scripts/captain_obvious_ts.mjs --project <repo> --json /tmp/co-ts.json
python3 <skill-dir>/scripts/captain_obvious_py.py --path <repo> --json /tmp/co-py.json
```

- The Python detector shells out to mypy for the type-guaranteed category. Use
  the project's own environment: pass `--mypy "uv run mypy"` for uv projects,
  `--mypy "poetry run mypy"` for poetry, etc. If mypy isn't available it
  degrades gracefully to the syntactic categories.
- Note: the mypy pass briefly writes `_cap_obv_shadow_*` copies next to test
  files (removed when the run ends) — so a "report-only" scan does touch the
  working tree. Pass `--no-types` for a strictly read-only scan; if the tree
  is not writable the scan degrades to syntactic categories and says so.
- The TS detector resolves the project's own `typescript` package; without a
  tsconfig it degrades to syntactic categories.
- **If the project already produces coverage** (or you can cheaply run it),
  pass `--coverage <file>` (lcov / istanbul `coverage-final.json` / coverage.py
  `coverage json`). This is the dynamic half of the ICSE'19 rotten-green
  analysis: a `conditional-assert` whose line never ran is promoted to **proven
  rotten**, and one that did run is dropped as a confirmed false positive. It
  turns the noisiest advisory category into a trustworthy one — use it whenever
  coverage is available.

Show the user the summary table and the findings before deleting anything.

### 3a. Check test value beyond the scanner

The scripts find mechanical patterns; they cannot decide whether a test owns a
useful contract or merely repeats another test. For a focused manual audit,
apply the authoring gate to each review lead or advisory before changing it.

Look especially for expectations copied from the implementation, source-text
greps, fixtures or mocks that manufacture the asserted result, and negative
controls that pass because an unrelated guard rejects the input. These are
**review leads**, not new proven scanner categories. Read the complete test,
the production path, overlapping tests, and relevant history before deciding.
Keep tests that independently lock a public API, protocol, security boundary,
platform behavior, or release artifact, even if they inspect source or run
slowly. A behavior-preserving refactor breaking a test is a reason to examine
it, not sufficient evidence to delete it.

Before a manual deletion or rewrite, record the test and location, what it can
actually detect, the stronger remaining test (or why none is needed), non-test
callers of any seam to be removed, relevant history, and the focused validation
command. If the evidence is incomplete, keep the test pending investigation.

### 4. Understand the two levels

- **proven** — cannot fail, by construction. The scripts guard the known
  escape hatches (`any`/`unknown`, `as` casts, `!`, index signatures, unchecked
  index access, structural `instanceof`, custom assertion helpers). Those
  marked `deletable: safe` are auto-deleted; proven `report-only` findings
  (swallowed or missed-fail asserts) need a rewrite and `--fix` leaves them.
- **advisory** — almost certainly useless but *not* provable (assertion-free
  tests, structural instanceof, mock-echo variants, index-signature-backed
  checks, rotten-green conditional asserts, unawaited async assertions). The
  script never auto-deletes these, but it records *exactly why* each is
  uncertain, plus a `deletable` hint (`aggressive` = usually a deletion,
  `report-only` = usually needs a rewrite). That reason is a question **you**
  are equipped to answer against the surrounding code — so advisories are
  adjudicated by you (step 6), not dumped on the user.

See `references/detectors.md` for the full category catalog and the reasoning
behind each guard.

### 5. Fix the proven tier (deterministic)

```bash
node <skill-dir>/scripts/captain_obvious_ts.mjs --project <repo> --fix
python3 <skill-dir>/scripts/captain_obvious_py.py --path <repo> --fix
```

Plain `--fix` removes only **proven** findings marked `deletable: safe` — no
judgment required, no LLM. This is the safe deterministic core; run it first.
Proven `report-only` findings stay for you to rewrite in step 6.

### 6. Adjudicate the advisory tier (you decide, then confirm)

Advisories are the cases determinism *can't* settle — and that's your job, not
a report line for the user. Do **not** just forward the list. For each advisory
finding:

1. Read the test and the code it exercises. The finding's `reason` field is a
   pointed question — e.g. *"structural instanceof — a shaped non-instance
   could sneak in"* → check whether anything actually constructs a non-instance
   of that type; *"mock-echo, indirect"* → check whether a real code path runs
   between stub and assert.
   Apply the four value questions above before removing an advisory: identify
   the contract's strongest test owner and check whether this test protects a
   distinct failure mode. For a bug regression, confirm that the test fails on
   the pre-fix behavior for the intended reason when a safe baseline is
   available; a mock that merely produces the expected result is not proof.
2. Decide one of: **delete** (the doubt doesn't hold — it really is useless),
   **keep** (the doubt holds — it's a real check), or **rewrite** (the intent
   is valid but the assertion is broken). Rewrite is the advisory tier's real
   value: fix the unawaited `.rejects` (`await` it), narrow a
   `pytest.raises(Exception)` to the specific type, repair a rotten-green
   `conditional-assert` so it actually runs. Note `no-assert` findings are
   **smoke tests** — legitimate by design (ICSE'19); default to **keep** unless
   the test clearly *meant* to assert something and forgot.
3. **Propose before acting.** Present a compact per-item table — finding,
   verdict, one-line rationale, and the exact edit for rewrites — and apply
   only what the user approves. Never auto-delete or auto-rewrite an advisory.

For a large advisory set, delegate the per-item code reads to a **cheaper, faster
subagent model** (batch the findings; have it return verdict + rationale + proposed
edit per item) and keep the final proposal/synthesis here — don't burn the main
loop reading files one by one. The proven tier is never handed to a subagent;
it's already decided.

### 7. Clean the residue

The scripts delete whole test blocks or individual assertion lines. That can
leave behind: unused imports/variables (`noUnusedLocals` will flag them),
empty `describe()` blocks, empty test classes, orphaned fixtures/mocks. Fix
those by hand — the typechecker output is your worklist.

### 8. Verify

Run the project's typecheck AND full test suite (`tsc --noEmit` + the test
command from package.json / `pytest`). Everything must pass with the same
result as before (minus the deleted tests). If anything regresses,
`git checkout -- <files>` and report what happened instead of pushing through.

### 9. Report

Tell the user: proven tests/assertions removed (per-category counts, lines
saved), the advisory verdicts you applied (deleted / rewritten, with the fix),
and anything you chose to **keep** with the reason the doubt held — that last
group is the tool earning trust, not failing.

## What NOT to flag (the scripts already know, but so should you)

- `toBeDefined()` on `.find()` / `Map.get()` results — the type is `T | undefined`, the check is real.
- Enum/constant contract locks (`expect(ExitCode.OK).toBe(0)`) — they catch renumbering.
- Assertions on values read from files/APIs at test time — real regression tests.
- Tests asserting via custom helpers (`expectAllow(x)`, `self._check(...)`).
- "Must not raise" contract tests for fail-open code paths.

## When not to run the cleanup scanner

- **Mid red-green.** During TDD a test is *supposed* to be failing, and a
  freshly-written test may not have its assertion yet. Use the authoring gate,
  but run the cleanup scanner only once the suite is green.
- **On a branch under review.** Scan (`--json`) is fine; `--fix` is not.
  Rewriting test files while a reviewer or a merge gate is reading the diff
  invalidates what they reviewed.
- **As a coverage or CI-time optimizer.** It deletes tests that cannot fail,
  which is a correctness argument, not a speed one. "CI is slow" is not a
  reason to reach for it — a slow suite full of real tests stays slow.
