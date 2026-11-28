# Build

## New project

Start with [greenfield planning](standards/greenfield.md). Identify the first end-to-end user journey, authoritative state, failure boundaries, and the constraints that actually affect architecture. Choose a small deployable slice with verification. Read the [architecture](standards/architecture.md) and [structure](standards/structure.md) guides when those choices affect delivery.

## Existing project

Trace the normal entry point, ownership, dependencies, and caller contracts. Find and reuse existing services, schemas, helpers, and tests where their semantics fit. For a behavior-preserving change, capture the current observable contract before moving code and use the [refactoring guide](standards/refactoring.md).

## Discover and decide

Convert each consequential feature into a verifiable question. A checkout may need separate searches for retry identity, decimal money, and inventory claims. A music app may need separate decisions for shuffle semantics, durable queue, and a boundary between selection and playback. Ignore concerns the request cannot encounter. A booking feature that confirms immediately may need atomic ownership without needing asynchronous holds.

Use the closest sources for each question. Ask only when a product choice such as equal permutation odds versus artist variety materially changes the result. Use project conventions and stated reversible defaults for routine details.

For example, “let members change their address and use it for their next order” has separate decisions about input validity and when subsequent reads see the new address. Trace the address update and order entry points, then investigate those guarantees separately.

## Implement, verify, and explain

Implement through the real entry point. Keep domain policy in a testable boundary when it has distinct rules or multiple actual callers. A small pure function can be sufficient. Exercise the expected result and an applicable failure, including concurrent calls, retries, old persisted data, or interruption when these can occur.

Explain important decisions with an observable outcome and the specific check. For example, “I made checkout recognize a retry as the same payment. In the test, the payment went through but the reply was lost. Retrying recorded one charge in total.” Keep a measured result separate from a promise about other failure modes.
