# Audit

Begin with read-only inspection. Match the depth to the user's scope. Start from entry points and trace real call paths, state changes, and failure handling. A broad audit should identify which surfaces were inspected.

Translate the observed symptom into a testable condition. For repeated feed items, inspect ordering, page boundaries, and insertions between requests before choosing a record. State the triggering case in the user's language.

For a broad audit, split reachable surfaces by data ownership, public contracts, and failure paths. Search separately for concrete issues that have evidence. Use [architecture](standards/architecture.md), [structure](standards/structure.md), or [testing](standards/testing.md) for cross-cutting findings. A general code smell becomes actionable when the reviewer can show where it changes behavior, costs, or maintenance.

For each actionable finding, record the severity, file and line, observed behavior, a concrete triggering condition, the user-visible effect, and the smallest plausible correction. Link a decision record when it explains the issue. Distinguish verified behavior from an inference that requires more evidence. For example, if adding an item between page loads reproduced a duplicate, lead with the duplicate and its trigger, then identify the offset boundary and how to check the correction.

Prioritize incorrect results, data loss, and broken user flows before speculative scale or style concerns. Existing project conventions and verified product constraints may justify the current choice.

Provide findings before changes for an audit-only request. When the user asks for an in-scope fix or refactor, retain the behaviors callers rely on, make the authorized edits, and verify the normal entry point and the triggering case.

For behavior-preserving changes, use [safe refactoring](standards/refactoring.md). Capture an observable baseline before edits. Report limitations per surface when the reproduction, migration, or integration check could not be run.
