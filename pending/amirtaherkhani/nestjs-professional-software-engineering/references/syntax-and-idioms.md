# Syntax and Idiom Selection

Choose syntax from evidence in the target repository, not from memory or fashion.

## Evidence ladder

1. Read the nearest project instructions, formatting configuration, compiler settings, dependency manifest, and analogous code.
2. Confirm exact language, runtime, framework, and dependency versions.
3. Inspect installed type declarations, source, generated API contracts, or CLI help when available.
4. Use official documentation that applies to those versions.
5. Run a focused type-check or minimal experiment when overload resolution, inference, generated code, decorators, macros, or runtime semantics remain unclear.

Do not copy syntax from a newer release into an older project. Do not infer feature support from a lockfile entry alone when compiler configuration or runtime targets can disable it.

## Comparison questions

For each candidate form, ask:

- Is it accepted by the actual compiler, formatter, linter, and runtime?
- Does it match nearby code and the team's vocabulary?
- Are types inferred accurately at both declaration and call sites?
- Are effects, errors, allocation, network calls, and state changes visible enough?
- Is the control flow easy to debug and the stack trace useful?
- Does it preserve tree-shaking, serialization, reflection, decorators, or code generation where those matter?
- Is the explicit form clearer for this one use?

Prefer the simplest form that answers these questions well. “Modern” is not a sufficient reason by itself.

## Framework-native syntax

Use the framework's supported composition and lifecycle mechanisms before creating custom wrappers. Confirm names, options, and signatures from installed packages or official docs. A wrapper is justified when it establishes a stable application-owned contract, removes verified repetition, or prevents a recurring misuse—not merely to rename a framework call.

## Examples

Prefer a plain function over a fluent builder when there is one required operation:

```ts
const quote = calculateQuote(input);
```

A builder may help when ordered or optional construction rules are genuinely complex and validation can occur at one boundary:

```ts
const request = PaymentRequest.create(reference)
  .withAmount(amount)
  .withIdempotencyKey(key)
  .build();
```

The builder must not hide that `build()` performs network I/O; creation should remain local and effects should use an explicit verb such as `send()` or `execute()`.

## Verification record

When syntax is a central decision, record the relevant version, repository precedent, official source, focused experiment if used, and why rejected alternatives were less clear or less compatible.
