# Prevention — never write these patterns

The cheapest dead test is the one never written. Each pair below is a
proven category the write-time hook blocks; write the right-hand form
instead.

| Never write | Write instead |
|---|---|
| `assert True` / `expect(true).toBe(true)` | An assertion on a value the code under test produced |
| `assert x == x` / `expect(x).toBe(x)` | Compare against an independently-stated expected value |
| `assert len(items) >= 0` | Assert the exact expected length or contents |
| `x = 5; assert x == 5` (arrange-assert echo) | Assert on the result of calling real code with `x` |
| `mock.return_value = V; assert f() == V` where `f` just returns the mock | Assert on logic that transforms the value, or drop the test |
| Assertions after `return` / inside `if` that can't fire | Put the assertion on the unconditional path |
| `try: assert ... except: pass` (swallowed assert) | Let the assertion fail; use `pytest.raises` for expected errors |
| Two tests with identical bodies | One test — or make the second actually test its name |
| `pytest.raises(Exception)` as the only check | Raise-type + message/behavior assertions |

Rules of thumb when generating tests:

1. Name the observable behavior or independent contract the test protects.
2. Name a plausible regression that makes it fail for the intended reason. For
   a bug fix, verify the test fails before the fix when a safe baseline exists.
3. Check whether another test already owns that contract at a stronger
   boundary. Add this one only for a distinct risk.
4. Avoid production exports, flags, wrappers, or injection hooks used only by
   tests; exercise the real entry point instead.

Never assert what the type checker already guarantees (`isinstance` on a typed
return, `toBeDefined` on a non-optional field), or directly re-check a value
supplied by the test's own fixture or mock. Keep tests where real production
code must forward, transform, serialize, or reject that value. Source-text
checks can be valuable when they independently protect a public key, path, or
release artifact; do not use them to mirror private implementation details.

## CLAUDE.md snippet (for skill-only installs, no hook)

```markdown
## Test-writing rules (captain-obvious)
- Name the observable contract, the regression that makes it fail, and why
  existing coverage does not already own it. Avoid test-only production seams.
- Never write assertions that hold by construction (assert True,
  expect(x).toBe(x), len >= 0, arrange-echo).
- Never assert what the type checker guarantees (isinstance/toBeDefined
  on typed values); assert behavior instead.
- No duplicate test bodies; no assertions after return or inside
  conditionals that may not fire; no bare pytest.raises(Exception).
```
