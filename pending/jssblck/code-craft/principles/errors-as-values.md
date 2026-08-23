# Errors are values; gates fail closed

> Handle expected failure through the value channel, with context, and never
> swallow it. A check that cannot answer is a block, not a quiet pass.

## Expected vs unexpected failure

Draw the line clearly:

- **Expected/recoverable** (file missing, bad input, network hiccup, conflict):
  flows through the value channel. Rust `Result`, Go `error` return, TS a
  returned union or a thrown typed error caught at a known seam, Python a
  specific exception. The caller can see it in the signature or contract and
  decide what to do.
- **Bugs/invariants violated** (index out of bounds on data you just built, a
  "this cannot happen" branch): may panic/throw/abort. These are programmer
  errors, not conditions to recover from. Use the language's assert/expect/panic
  with a message that says what invariant broke.

Do not blur them. Crashing on a missing config file is wrong; returning a
recoverable error from a corrupted-internal-state branch is also wrong.

## Add context as it propagates

A bare "file not found" three layers down is useless. Wrap the error with what
you were trying to do as it bubbles up, so the final message reads as a chain:

```
loading profile "alice": reading /etc/app/alice.toml: no such file
```

Every language has the idiom: Rust `.context(...)` / `?` with a context layer,
Go `fmt.Errorf("...: %w", err)`, TS error `cause`, Python `raise ... from err`.
Add a frame of context at each meaningful layer; do not re-wrap mechanically at
every function.

## Never swallow

The empty catch is a silent data-corruption machine:

```
# every one of these is a bug
try: do() except: pass
if let Err(_) = do() {}          # ignored
_ = do()                          # Go: error dropped
do().catch(() => {})              # JS: rejection eaten
```

If you genuinely intend to ignore an error, that is a decision that must be
visible: log it at the right level, comment why it is safe to drop, or convert
it to a default through an explicit path. "Ignored silently" and "handled by
ignoring, on purpose, here is why" must not look the same in the code.

## Fail closed at gates

A gate is any check whose output controls whether something proceeds: an auth
check, a merge gate, a validation step, a feature flag guard, a security filter.

**If a gate cannot produce a valid verdict, the answer is no.** A gate that
errors, times out, or gets malformed data must block, never default to allow. An
advisor (something whose output is informational, not blocking) may fail open,
but say which one you are building. The dangerous bug is the gate that silently
becomes a pass when its backend is down.

```
verdict = run_check(change)        # may error / time out
if verdict is None or verdict.errored:
    return BLOCK                    # fail closed
return verdict.decision
```

## Typed errors at library boundaries

For a library or a module others depend on, give callers a typed error they can
match on (an enum/union of failure modes), not an opaque string or a catch-all.
Reserve opaque/aggregated error types (Rust `anyhow`, a bare `Exception`, a
plain `error`) for application top-levels where the caller just reports and
exits. The deeper and more reused the code, the more its errors should be
inspectable.

## Messages

Lowercase, no trailing period, no "Error:" prefix (the framework adds context).
Describe the condition, not the reaction: "connection refused", not "failed to
connect, exiting." Let the caller decide the reaction.

See the per-language files for the concrete error type, wrapping operator, and
the fail-closed pattern in each.
