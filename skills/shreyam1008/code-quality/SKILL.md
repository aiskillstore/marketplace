---
name: code-quality
description: Reviews and simplifies code for maintainability and correctness. Use for a requested code review, refactor, removal of unnecessary abstractions or dependencies, or investigation of tangled logic. Not a default checklist for every small edit.
---

# Code review and simplification

Start from the requested change or observed maintenance problem. Identify the behavior, public contracts, and callers that must survive the refactor. Return a focused patch or findings supported by concrete code paths.

## Choose the change

- Trace one representative input through validation, decisions, and side effects. Name where responsibilities become coupled, state becomes inconsistent, or errors disappear.
- Prefer an existing platform API, standard library, or installed dependency when it meets the actual contract. Compare behavior and maintenance cost before replacing custom code.
- Remove unused branches and indirection after checking callers. Keep an abstraction when it expresses a real boundary, ownership rule, testing seam, or variation; the number of implementations alone is not a reason to delete it.
- Simplify the cause of repeated complexity. Do not compress readable logic into clever expressions or mix unrelated cleanup into a focused fix.
- Preserve security checks, accessibility, error recovery, compatibility, and requested detail. A shorter diff is useful only when the behavior remains correct.

## Review correctness at boundaries

- Parse untrusted data before depending on its shape. Separate parsing from domain decisions and I/O so each failure has a clear owner.
- Check empty, absent, duplicate, reordered, concurrent, and failed inputs relevant to the code. Validate state transitions rather than checking only successful output.
- Make ownership of mutable state explicit. Check whether retries, cancellation, stale asynchronous results, or partial writes can corrupt shared state.
- Preserve public types and failure contracts. Prefer explicit states to contradictory flags; remove casts or suppressions only by establishing the missing invariant.
- Check sensitive paths for authorization before access, contextual output encoding, safe query/command APIs, and secret-free logging. Use a security-specific review when that is the requested scope.

## Simplify with evidence

List the callers or tests that justify removing a branch or dependency. Keep migration requirements visible when a public API changes. Reuse the repository's style and tooling instead of imposing naming, formatting, or folder conventions.

Replace comments that restate the code with explanations of non-obvious constraints. Report the outcome, validation, and remaining tradeoffs at the depth the user needs; this skill does not prescribe a universal response format.

## Verify and report

Run checks appropriate to the changed behavior. For a bug, reproduce the failure before changing it when feasible and verify it no longer occurs. Prefer behavior-level tests that cover meaningful failure paths; do not add tests merely to mirror a refactor's internal shape.

For a review, prioritize actionable findings and name their consequence and location. For an edit, summarize what became simpler, which behavior was preserved, and what was tested. Do not claim correctness from a smaller line count alone.

## References and attribution

- [Google Engineering Practices](https://google.github.io/eng-practices/review/) — code review.
- Simplification guidance incorporates the former `minimalism` skill, inspired by [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) (MIT).
