# Correctness and API lens

Trigger: implementation logic, public/internal contracts, parsing, CLI behavior, libraries, or schema/API changes.

## Attack questions

What invariants must hold before and after every operation? Which states are impossible, and where is that enforced? Enumerate empty/absent/null/zero/false separately where semantics differ. Test minimum, maximum, just-inside, just-outside, duplicate, malformed, and unexpected-type inputs. Inspect overflow, truncation, units, precision, locale, Unicode normalization, time zones, and date boundaries when relevant.

Trace early returns, exception paths, cleanup, partial results, and cancellation. Check what callers observe after failure, including persistence and side effects. Inspect ownership/lifetime and resource cleanup. A successful local calculation can still violate the consumer's contract.

For APIs, examine validation order, status/error shape, pagination stability, cursor scope, sorting ties, filtering, idempotency semantics, quotas, request size, version negotiation, backwards compatibility, and unauthorized resource existence leaks. For a CLI, inspect exit codes, stdout versus stderr, quoting boundaries, broken pipes, paths with spaces, and incomplete output handling. Do not execute untrusted constructed shell strings.

## Evidence to collect

A compact input partition table, expected result from the contract, actual result or exact source path, and the affected caller. For stateful behavior, include the complete transition sequence rather than just the last request. Add a contract test at the public boundary plus a focused test at the invariant owner when useful.

## Edge cases that are easy to miss

An empty successful response versus missing data; default values that overwrite explicit false/zero; order-dependent validation; two valid encodings of one identifier; pagination after concurrent insertion; errors masked by a `finally` return; a generator consumed twice; floating-point equality in monetary paths; cache keys that omit tenant/version/locale; aliasing when mutable defaults or references are shared.

These are prompts to investigate only where applicable, not findings on their own. Do not recommend new behavior contrary to an established contract without flagging the product decision.

## Repair re-attack

Test the original failure, another member of the same equivalence class, and unaffected normal behavior. Recheck every direct consumer of a changed return/error/schema contract. Confirm the fix did not replace an explicit failure with silent corruption or make formerly bounded inputs unbounded.
