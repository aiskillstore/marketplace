# Detector catalog

Both scripts emit the same JSON shape: `{findings: [{file, line, test, category,
level, deletable, reason}], summary, plan/fixed}`. `level` is `proven` or
`advisory`; `deletable` is `safe` (removed by `--fix`) or, for advisories that
the script never auto-removes, a hint for the agent's adjudication step:
`aggressive` (usually a deletion once confirmed) or `report-only` (usually
needs a rewrite, not a deletion).

The TS scanner additionally attaches an optional `snippet` field (first 160
chars of the flagged statement) to findings that reference a concrete
statement; the Python scanner does not emit it — consumers must treat it as
optional.

## Categories

| Category | What it catches | Level |
|---|---|---|
| `type-guaranteed` | Assertion re-checks a fact the type checker proves: `expect(typeof f()).toBe('number')`, `toBeDefined()`/`not.toBeNull()` on non-nullable types, `toBeInstanceOf` on nominal classes, `toBeTruthy` on object types, `Array.isArray` on arrays, `expect.any(Ctor)`/`expect.anything()`, `toHaveProperty` on required props; Python: `assert isinstance(x, T)` / `assert x is not None` / `type(x) is T` checked against mypy `reveal_type` | proven / advisory |
| `constant-assert` | Tautologies: `expect(true).toBe(true)`, `assert 1 == 1`, `expect(x).toBe(x)`, `assert x == x` on side-effect-free chains; unittest assert-methods (`assertEqual(1, 1)`, `assertTrue(True)`, `assertEqual(x, x)`) are classified too, always report-only | proven |
| `silent-smoke` | Assertion-free test that cannot even fail by raising: every call it makes is wrapped in a `try`/`except`-`pass` (the handler absorbs any raise), or the body contains no calls at all. Unlike `no-assert` — a legitimate smoke test whose unguarded calls still fail the test on raise — a silent-smoke test has no failure path whatsoever | proven |
| `no-assert` | No assertion anywhere in the test. Per *Rotten Green Tests* (ICSE '19) this is a **smoke test** — legitimate by design (it verifies the code runs without throwing), **not** a rotten test. Surfaced (never a delete candidate) only so a human can spot the rare case where an assertion was clearly intended but forgotten | advisory, report-only |
| `mock-echo` | Test asserts the mock does what it was just stubbed to do: `m.mockReturnValue(5); expect(m()).toBe(5)`, or calls `m()` then asserts `toHaveBeenCalled()` | proven (direct) / advisory (indirect) |
| `duplicate-test` | Body identical to an earlier test. **Same file + same class/describe scope → proven** (auto-deletable). **Different file or scope → advisory** (surfaced only — a shared body can behave differently under a different conftest/fixture set or `beforeEach`, so a human picks which to keep). Comparison is comment/formatting-insensitive but **literal-sensitive** (whitespace *inside* a string/template literal counts), so whitespace-handling tests are not merged. When two identical-bodied tests' names materially diverge, the finding is flagged as a likely copy-paste bug that leaves the named behaviour untested | proven / advisory |
| `dead-assert` | Assertion after an unconditional `return`/`throw`/`raise` — unreachable | proven |
| `missed-fail` | A forced-fail marker (`pytest.fail()` / `fail()` / `raise AssertionError` / `throw new Error`) sitting in dead code after an unconditional `return`/`raise`/`throw` — it can never fire, so the failure it was meant to guard is untested (ICSE '19 "missed fail"). A *reachable* forced-fail behind a live guard — the classic `try: do(); fail() except: pass` "assert it raises" idiom — is deliberately NOT flagged | proven, report-only |
| `missed-skip` | A conditional early `return`/`skip` that precedes real assertions — if the guard fires (`if not feature_available: return` above the asserts), those assertions never run (ICSE '19 "skip"). Guards keyed on a parametrized/fixture argument are excluded | advisory, report-only |
| `swallowed-assert` | Assertion inside `try` with an empty/`pass`/console-only catch — a failure is absorbed | proven, report-only |
| `never-asserts` | Test has assertions but ALL are dead or swallowed → the test cannot fail | proven |
| `conditional-assert` | Assertion gated behind `if` (rotten green test, ICSE '19) — may never execute (e.g. `if (process.platform === 'darwin')` in Linux-only CI). Two shapes are deliberately NOT flagged, being common legit style: loop-nested asserts (`for x in items: if …: assert`), and asserts whose guard is keyed on a parametrized/fixture argument (`if mode: … else: …` — every branch runs across the parametrization). Statically this is a *guess*; with `--coverage` it becomes a fact (see below) | advisory, report-only (proven with coverage) |
| `boundary-tautology` | `expect(x.length).toBeGreaterThanOrEqual(0)` / `assert len(x) >= 0` — a length can never be negative | proven |
| `local-const-echo` | `const expected = 5; expect(expected).toBe(5)` — the test asserts its own arrangement, code under test never involved | proven |
| `floating-async-assert` | `expect(p).resolves/.rejects...` without `await`. Runner-dependent severity: Jest silently never evaluates it (real silent-pass bug); bun:test and modern Vitest fail the test at settle time (style/portability issue). Needs `await` added, so report-only | advisory, report-only |
| `smoke-only` | `expect(fn).not.toThrow()` as an assertion — calling `fn()` directly fails the test on throw anyway; assert on the return value instead | advisory, report-only |
| `self-compare-call` | `expect(f(a)).toEqual(f(a))` / `assert f(a) == f(a)` — equal by construction. Skipped when the test name says stable/deterministic/idempotent (then it's a real determinism check) | advisory, report-only |
| `broad-raises` | `with pytest.raises(Exception):` as the only check — passes on ANY bug that raises | advisory, report-only |
| `skipped-test` | `it.skip` / `xit` / `@pytest.mark.skip` — never runs, can never fail. Advisory because skips sometimes document future work; `skipif` is conditional and untouched | advisory |

## Why proven vs advisory — the escape hatches

A type is only a guarantee when nothing lied to the checker. The scripts
refuse to mark `type-guaranteed` as proven when:

- **the checked value is produced by an inline call** — `assert isinstance(fetch(), dict)`
  / `expect(typeof build()).toBe(...)`. Deleting the assertion would also delete
  that call's execution, which is real smoke coverage. Python skips these
  entirely; TS keeps them advisory. Only assertions on an already-bound name or
  attribute are proven-deletable, because the call that produced the value lives
  on its own line and survives.
- the expression's type involves `any` / `unknown` / type parameters (TS) or
  `Any` / unions (Python) — `JSON.parse`, untyped imports, untyped defs;
- the expression contains `as` casts (except `as const`), `<T>` assertions,
  or non-null `!` (TS), or the file uses `cast(` / `type: ignore` (Python);
- the value comes through element access without `noUncheckedIndexedAccess`,
  or through an **index signature** — the type is a promise, not a check
  (contract tests over JSON-ish APIs live here; they're legit);
- `strictNullChecks` is off — null/undefined facts aren't tracked at all;
- `toBeInstanceOf`: TypeScript is structural, so a declared type `C` can hold
  a shaped non-instance. Only nominal classes (a private/protected/`#` member
  somewhere in the chain) make `instanceof` provable; otherwise advisory.
- Python `type(x) is T` is advisory even when types match: a subclass
  instance satisfies the type but fails the identity check.
- **Annotation laundering**: a
  function annotated `-> dict[str, Any]` whose body just does
  `return http_client.api_get(...)` where `api_get() -> Any`. The type checker
  trusts the signature, but nothing enforces it at runtime — an isinstance
  check on its result is real API-shape regression coverage. The Python
  detector runs mypy with `--warn-return-any` over the source tree and refuses
  to flag assertions on values that flow (directly or through one assignment)
  from a `[no-any-return]` function. This laundering set is then **propagated
  transitively**: a thin wrapper `def f() -> dict: return g()` type-checks clean
  (mypy trusts `g`'s declared return) but re-launders `g`'s `Any`, so `f` is
  folded in via a fixpoint over `return <call>` pass-throughs. The TS detector
  walks the callee's return statements and refuses when an annotated function
  returns an `any`-typed expression or contains a cast in a return.
- Duplicate detection includes decorators in the test's identity — two
  `@pytest.mark.parametrize` tests can share a body but run different cases.
- **Literal-sensitive duplicate key**:
  a naive whitespace-stripped body comparison merges tests that differ only in
  whitespace *inside* a string/template literal — exactly what a template
  whitespace-handling suite looks like (`"{{ name }}"` vs `"{{name}}"`). The TS
  detector builds the duplicate/echo key by tokenizing (`ts.createScanner`) and
  keeping each token's raw text, so literal contents are significant while
  indentation/comments are not. Python already dumps the AST, which preserves
  string-constant values, so it is immune by construction.
- **Closure-mutated locals**: a call-counter
  `count = 0; def cb(): nonlocal count; count += 1; …; assert count == 0`
  is not a `local-const-echo` — the assertion is real behavioural coverage that
  the callback did/didn't run. The Python detector counts assignments across the
  full function subtree (not just the top level) and hard-disqualifies any name
  declared `nonlocal`/`global` in a nested scope. The TS detector only trusts
  `const` bindings to primitive literals, which cannot be closure-mutated.

Known residual edge cases (accepted, documented): property getters with side
effects can defeat `expect(a.b).toBe(a.b)` self-comparison detection; `NaN`
makes `toBe(self)` fail rather than pass — either way the test checks nothing
about the code under test.

## What `--fix` does safely

- **Never drops smoke coverage.** When *every* assertion in a test is redundant,
  the whole test is removed only if nothing executable would remain — the body
  is purely docstrings / `pass` / literal assignments. If the test still calls
  code under test or runs an `import` (a rename/break would fail it), it is left
  intact; the tool refuses to strip a test's last assertion.
- **No dangling locals.** If deleting an assertion orphans a local
  (`resp = Model.model_validate(raw)` used only by the removed assert), the
  assignment is rewritten to a bare `Model.model_validate(raw)` — keeping the
  call (real coverage) while removing the now-unused binding. Pure-literal
  dead assignments are dropped. Orphaned *imports* are left to the project's
  linter (`ruff --fix`), which resolves cross-file usage correctly.

## Single-file mode (`--file <path> [--stdin]`)

Scans exactly one file's content (from disk, or stdin with the path used
for naming) and prints the JSON report to stdout. Syntactic categories
only: no mypy, no tsc Program, no shadow files, no subprocesses — so
`type-guaranteed` can never fire and everything it proves is true by
construction. Built for write-time hooks (`hooks/prevent.py`); `--fix` is
rejected in this mode. Parse failures report a note and zero findings.

## Coverage mode (`--coverage <file>`) — the dynamic half

`conditional-assert` is, on its own, a *static guess*: an assertion behind an
`if` **might** never run. The rotten-green literature (Delplanque ICSE'19, RTj,
Google Test) all resolve this the same way — by **executing** the suite and
seeing which assertions actually fired. Those tools instrument the framework or
VM directly. We can't modify Jest/Vitest/pytest, so we consume the **line
coverage those runners already emit** — which is precisely the coverage-based
alternative Robinson (ESEC/FSE'23) identified but set aside, since he could
instrument Google Test itself and we cannot.

Pass `--coverage` a coverage file and each `conditional-assert` is reconciled
against its line's hit count:

- **ran 0 times** → promoted from advisory to **proven rotten** (fix the guard
  so it fires, or remove it — a genuine bug, per the papers);
- **ran ≥1 time** → a confirmed **false positive**; the finding is dropped;
- **no data for that line** → left as a static advisory, unchanged.

Accepted formats (both ecosystems, one flag): **lcov** (`DA:<line>,<hits>`
records — c8/nyc/jest/`coverage lcov` all emit it), **istanbul**
`coverage-final.json`, and **coverage.py** `coverage json`. The proven tier
(type-guaranteed, tautology, etc.) is untouched by coverage — only the
execution-dependent `conditional-assert` category is refined.

**Coverage must include the test files themselves.** Findings are keyed by
test-file lines, so a coverage config that only measures `src/`
(`--source=src`, `collectCoverageFrom: ['src/**']`) leaves every lookup
empty and the mode confirms nothing. Both scanners emit a
`coverage.warning` when a conditional-assert's test file is absent from
the coverage map — rerun coverage over the whole repo to make it bite.

## False-positive guards (learned from real repos)

- **Custom assertion helpers**: any called function matching
  `/^(expect|assert|verify|check|should)/i` counts as an assertion; the Python
  detector also resolves same-file helpers transitively (a test calling
  `_check_result(...)` whose body asserts is NOT assertion-free).
- **Must-not-raise contract tests** (name/docstring mentions noop / not raise /
  swallow / silent / graceful): reported but never auto-deleted.
- **Enum contract locks** (`expect(ExitCode.OK).toBe(0)`): not flagged — one
  side is a real imported symbol, not a literal.
- **`it.each` / parametrized tables**: skipped entirely.
- **Same-body tests in different describes**: advisory only, never auto-deleted —
  different `beforeEach` context can make identical bodies test different things.

## Grounding

The rotten-green lineage — this tool extends it to TypeScript + Python:

- **Rotten Green Tests** — Delplanque, Ducasse, Polito, Black, Etien, **ICSE 2019**
  (Pharo). Defines the rotten green test and the four categories: *context-dependent*
  (different asserts per branch), *missed fail* (a forced-fail marker that never runs),
  *skip* (an early return/guard that strands later asserts), *fully rotten*.
- **RTj** — Martinez, Etien, Ducasse, Fuhrman, **2019** (arXiv:1912.07322): the same
  detection for **Java/JUnit**, static (Spoon AST) + instrumented execution, and it
  **refactors** rotten tests, not just flags them — the basis for our advisory *rewrite*
  path. 427 rotten tests across 26 GitHub projects.
- **Rotten Green Tests in Google Test** — Robinson, **ESEC/FSE 2023** (C++): detection
  built into the framework (each assertion carries an `executed` flag). Explicitly weighs
  and rejects **coverage-based** detection *because he could instrument the framework*;
  as an external tool we can't, so `--coverage` is exactly that alternative. 183 rotten
  assertions in LLVM/Clang.

Supporting:

- Test smell catalogs / tsDetect, JNose ("Unknown Test" = smoke test, "Duplicate Assert",
  "Conditional Test Logic")
- Pseudo-tested methods — Niedermayr 2016, Descartes ASE 2018 (the mutation-testing ceiling
  this static tool approximates)
- "On the Diffusion of Test Smells in LLM-Generated Unit Tests" (2024) — smells in 38–100% of LLM suites
- TS unsoundness checklist — Effective TypeScript, "Seven Sources of Unsoundness"

## Limitations (be honest in reports)

- Cannot catch weak-but-executing assertions (e.g. `toBeGreaterThan(0)` where the
  contract is an exact count); only mutation testing proves those useless.
- Coverage-subsumption is out of scope. Cross-file and cross-scope duplicates are
  surfaced as advisories only, never auto-deleted.
- Assertions built dynamically (loops over matcher names, `expect[m]()`) are invisible.
- "Deleted nothing" does not mean "suite is sound".
