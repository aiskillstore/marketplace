# Syntactic Sugar and API Ergonomics

Syntactic sugar is a convenience surface over existing semantics. It should reduce friction without creating hidden behavior or a second inconsistent API.

## Decision test

Add sugar only when all of these are true:

1. **Repeated friction:** real call sites contain ceremony, duplication, or a recurring misuse.
2. **Stable semantics:** the underlying operation and failure model are understood and unlikely to fork immediately.
3. **Clear name:** the convenient form communicates intent better than the explicit form.
4. **No hidden material behavior:** I/O, state mutation, authorization, transactions, retries, caching, allocation, and expensive work remain discoverable.
5. **Type safety:** overloads and inference reject invalid combinations rather than accepting ambiguous bags of options.
6. **Escape hatch:** advanced callers retain access to meaningful control when needed.
7. **Compatibility:** the addition does not silently reinterpret existing calls.
8. **Tests and examples:** realistic examples cover normal, edge, and failure behavior.

If only code length improves, keep the explicit form.

## Good shapes

- Named constructors that validate a meaningful invariant.
- Small helpers that preserve a stable underlying operation.
- Defaults for common cases when defaults are safe, documented, and observable.
- Fluent APIs for truly staged construction, with effects behind explicit verbs.
- Framework adapters that keep application code independent of volatile vendor syntax.

## Warning signs

- Boolean arguments whose meaning is unclear at the call site.
- Many overloads that accept overlapping shapes.
- Getters or property access that perform I/O.
- Constructors that start work, reach the network, or register global state.
- Decorators or annotations that silently change authorization, transactions, retries, or persistence.
- DSLs that replace familiar language constructs with project-specific magic.
- Convenience methods that swallow errors, add unbounded retries, or change transaction scope.

## API example

An explicit API:

```ts
await client.execute({
  operation: 'capture',
  paymentId,
  idempotencyKey,
  timeoutMs: 3_000,
});
```

A safe convenience method can preserve the same contract:

```ts
await client.capture(paymentId, {
  idempotencyKey,
  timeoutMs: 3_000,
});
```

The convenience method should delegate to the explicit operation, return the same result type, preserve error and cancellation behavior, and expose options that materially affect correctness. It should not silently invent an idempotency key or retry a payment with an unknown outcome.

## Migration

Prefer additive sugar. If replacing an existing public form:

- inventory consumers;
- document old and new forms;
- provide deprecation or migration guidance;
- keep behavior aligned during the compatibility window;
- test both forms against the same contract.
