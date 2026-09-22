# Development after activation

[中文](development.zh.md)

Apply only when Birdview is active and the user has authorized coding. Before implementation, follow the displayed-plan confirmation step in [SKILL.md](../SKILL.md); mapping or an initial coding request alone is not plan approval. Preserve the existing map and change workflow; these rules neither enable always-on behavior nor override project instructions.

## Choose the relevant guidance

Read the related implementation, callers and applicable design decisions. Resolve questions from source first; ask only about unresolved choices that materially affect the task. Define the expected observable behavior and a proportionate way to verify it before editing. Combine the sections below when needed, such as bug diagnosis plus UI checks for a broken button. Do not run every section for every task.

### Bug fixes

Establish a reproduction or inspect concrete failure evidence matching the reported symptom. Use the smallest useful test, command, request or UI interaction. For intermittent failures, record reproduction conditions and frequency. If reproduction is unavailable, state what was tried and what evidence is missing; distinguish a tentative fix from a verified one.

Test plausible causes against evidence before choosing a fix. Multiple competing hypotheses help ambiguous failures, but simple bugs need no fixed hypothesis count. Change one relevant variable at a time when investigating. For performance work, measure the affected scenario before and after under comparable conditions.

After fixing, rerun the original scenario. Add a regression test when it can exercise the real failure path and provides durable value; observe it fail before the fix and pass afterward when feasible. Explain missing coverage. Remove temporary instrumentation introduced for this task without deleting others' work.

### Features and behavior changes

Identify observable acceptance behavior and important failure paths. Implement and verify in small behavior-sized steps. Tests should exercise real paths through stable interfaces, rather than mirror private implementation or pass only because internal collaborators are mocked. Use test-first development when requested or useful; do not mandate it for every change or add tests for trivial, reversible edits without meaningful risk.

### Refactoring and architecture changes

Inspect affected callers, compatibility requirements and existing decisions. State the concrete benefit, such as removing duplicated business rules or reducing knowledge required by callers. Preserve behavior unless its change is authorized, and verify the interfaces and paths affected. Do not add speculative abstractions or expand into unrelated cleanup. Ordinary edits do not start an architecture review; use the separate review workflow only when requested under the skill's activation rules.

### UI changes

Inspect the rendered result and affected interaction at relevant viewport sizes. Check loading, empty and error states where affected, plus relevant keyboard operation, focus and accessible labels. Scale checks to the change: a copy edit does not require a full-site audit. When visual or interaction verification is unavailable, state the limitation instead of claiming acceptance.

## Record and finish

Use the existing [change workflow](show-changes.md): put the expected behavior and intended verification in the `planned` reason, actual commands, exit codes and observations in `checks`, and reviews of applicable recorded constraints in `constraintReviews`. Do not invent schema fields or passing results. A manual review supports only the inspected scope, and completing an activity does not establish correctness.

Distinguish checks not run, environment blockers and observed failures. Continue routine checks and justified retries autonomously; ask only for material unresolved choices or required access. After relevant checks pass, broaden testing only for changed scope or remaining risk. Recheck the original request, update the map if responsibilities, ownership or relationships changed, and report the changes, actual verification and remaining limits. These are agent instructions; validators check records, not whether the agent truly followed the process.
