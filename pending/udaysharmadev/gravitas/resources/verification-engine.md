# Verification Engine

Proof-based verification. Evidence required. No hope-based testing.
Your job is to disprove success, not assume it.

---

## Verification Philosophy

**Null hypothesis:** The implementation is broken.
**Your job:** Disprove this with evidence.

Reading code and finding it "correct" is reconnaissance, not verification.
Verification requires running. The computer is the ground truth.

---

## Verification by Tier

| Tier | Scope | Time Budget |
|------|-------|------------|
| **0** | Quick sanity: does it compile/run at all? | ~30s |
| **1** | Full chain: lint → type-check → test | ~2 min |
| **2** | Comprehensive: lint → type → test → build → edge cases → adversarial | ~10 min |

---

## Verification Chains (by Language)

### TypeScript
```bash
# Required chain (run in this order)
tsc --noEmit                    # type correctness first
eslint . --max-warnings 0       # zero warnings allowed
vitest run --reporter=verbose   # all tests

# With coverage (Tier 2)
vitest run --coverage --reporter=verbose

# Full output capture
tsc --noEmit 2>&1 && echo "TYPES: PASS" || echo "TYPES: FAIL"
eslint . --max-warnings 0 2>&1 && echo "LINT: PASS" || echo "LINT: FAIL"
vitest run --reporter=verbose 2>&1 | tail -30
```

### Python
```bash
mypy . --strict 2>&1             # type correctness
ruff check . 2>&1                # lint
pytest -v --tb=short 2>&1        # tests
pytest --cov=src --cov-report=term-missing 2>&1  # coverage (Tier 2)
```

### Rust
```bash
cargo check 2>&1                 # syntax + types
cargo clippy -- -D warnings 2>&1 # lint (warnings = errors)
cargo test 2>&1                  # all tests
cargo test -- --nocapture 2>&1   # with output (debugging)
```

### Go
```bash
go vet ./... 2>&1
staticcheck ./... 2>&1           # enhanced lint
go test ./... -v 2>&1
go test ./... -cover 2>&1        # coverage
```

### Java (Maven)
```bash
./mvnw compile 2>&1
./mvnw test 2>&1
./mvnw verify 2>&1               # full chain
```

### C#
```bash
dotnet build --no-restore 2>&1
dotnet test --logger "console;verbosity=detailed" 2>&1
```

### Ruby
```bash
bundle exec rubocop --no-color 2>&1
bundle exec rspec --format documentation 2>&1
```

### PHP
```bash
composer phpstan 2>&1
composer test 2>&1
```

### Swift
```bash
swift build 2>&1
swift test 2>&1
```

---

## Evidence Requirements

| Claim | Required Evidence | Format |
|-------|-----------------|--------|
| "Tests pass" | Pass count ≥ baseline, 0 failures | "47/47 passed, 0 failed" |
| "Lint clean" | Linter output with 0 warnings/errors | "(no output)" or "0 problems" |
| "Type-safe" | Compiler output clean | "(no output)" = clean for tsc |
| "Build succeeds" | Last line of build output | "Build succeeded" |
| "No regressions" | Before + after counts compared | "47→47 pass, 0 new failures" |
| "Fixed" | Before behavior + after behavior, both observed | Test showing fix |
| "Secure" | Security tool output + manual check | "0 high/critical findings" |

### Evidence Format (cite verbatim)

```
Command: vitest run --reporter=verbose
Output:
  ✓ auth › session timeout (12ms)
  ✓ auth › login flow (45ms)
  ✓ auth › logout cleanup (8ms)
  Tests: 47 passed, 47 total, 0 skipped
  Duration: 892ms
```

Never paraphrase test output. Cite it verbatim.

---

## Regression Protocol

### Baseline (before implementation)
```bash
# Run before touching any code
vitest run 2>&1 | tail -5
# Record: X tests, Y pass, Z fail
```

### Post-change comparison
```bash
# Run after implementation
vitest run 2>&1 | tail -5
# Compare: X tests, Y' pass, Z' fail
```

### Regression check
```
Pass count: Y' >= Y?  → ✅ no regression
Pass count: Y' < Y?   → ❌ REGRESSION — [Y-Y'] tests newly failing
New warnings: M' > M? → ❌ NEW LINT ISSUES — [list them]
```

---

## Edge Case Matrix

For every changed function, verify these inputs:

| Input | Why | Typical Expected |
|-------|-----|-----------------|
| Normal valid input | Happy path | Success |
| Empty string `""` | Boundary | Error or default |
| `null` | Null safety | Error with message |
| `undefined` | JS/TS gotcha | Error with message |
| `0` | Zero boundary | Depends on domain |
| Negative number `-1` | Range check | Error or clamp |
| `MAX_SAFE_INTEGER` | Overflow | Depends |
| Very long string | Memory / truncation | Depends |
| Special chars `<>&"'` | XSS / injection | Escaped or rejected |
| Malformed JSON `{bad}` | Parse safety | Error |

Create tests for any missing from this matrix.

---

## Security Verification (when auth/input/db changed)

```bash
# SQL injection patterns
grep -rn "query.*\$\{" src/ --include="*.ts"           # template literals in SQL
grep -rn "execute.*+.*req\." src/ --include="*.ts"     # string concat in queries

# XSS patterns
grep -rn "innerHTML\|outerHTML\|document.write" src/ --include="*.ts"
grep -rn "dangerouslySetInnerHTML" src/ --include="*.tsx"

# Hardcoded secrets
grep -rn "password\s*=\s*['\"]" src/ --include="*.ts"
grep -rn "api_key\s*=\s*['\"]" src/ --include="*.ts"
grep -rn "secret\s*=\s*['\"]" src/ --include="*.ts"

# Auth bypass
grep -rn "skipAuth\|bypassAuth\|noAuth" src/ --include="*.ts"
```

---

## VERDICT Protocol

### Issuing VERDICT: PASS

Requirements (ALL must be met):
- [ ] All tests pass (pass count ≥ baseline)
- [ ] Zero new lint warnings (in strict mode)
- [ ] Type-check clean
- [ ] No security regressions
- [ ] Edge case matrix covered (or explicitly waived with reason)

```
VERDICT: PASS

Tests:    47/47 (baseline: 47/47 — no regression)
Lint:     clean (0 warnings)
Types:    clean (tsc --noEmit: no output)
Coverage: 87% on changed files (was 85%)
Security: no new issues found
```

### Issuing VERDICT: FAIL

Issue FAIL if ANY of the above is not met.

```
VERDICT: FAIL

Failing tests (2):
  ✗ auth › session validation (14ms)
    AssertionError: expected 30000 to be 5000
    at src/auth/session.test.ts:47:24

  ✗ middleware › auth check (8ms)
    TypeError: SESSION_TIMEOUT is not defined
    at src/middleware/auth.ts:23:5

Root cause: Test assertion not updated, and middleware import missing.
Required fix:
  1. Update src/auth/session.test.ts:47 — change toBe(5000) to toBe(30000)
  2. Add import { SESSION_TIMEOUT } to src/middleware/auth.ts
```

### VERDICT must be the last thing in your verification report

Gate automation on this string: `VERDICT: PASS` or `VERDICT: FAIL`.

---

## Verification Failure Protocol

When verification fails:

1. **Stop** — don't patch and re-run hoping it'll work
2. **Read error carefully** — diagnose root cause, not symptom
3. **Fix root cause** — not the test (unless test is genuinely wrong)
4. **Re-run full chain** — not just the failing test
5. **Log to SESSION_FAILURES.md** if the approach itself was wrong
6. **Report honestly** — VERDICT: FAIL with specific reason

### Root Cause vs Symptom

```
Symptom:  Test fails with "SESSION_TIMEOUT is not defined"
Wrong fix: Add SESSION_TIMEOUT = 30000 to the test file
Root cause: Middleware doesn't import SESSION_TIMEOUT from session.ts
Right fix:  Add the import to middleware/auth.ts
```

Always fix the cause. Never patch the symptom.
