# audit

Manual or agent-requested checks on the project knowledge layer. Audit is the safety net for records missed during day-to-day work.

## Checks

- LOG entries that are too long or contain conclusions that belong in topic notes.
- Topic notes without useful frontmatter.
- Missing topic notes for repeated decisions or solved problems.
- Contradictions between topic notes and old LOG entries (topic notes win; flag the stale LOG entry).
- Engineering assets mixed into `cairn/` that should move back to the code tree.
- Broken links or stale pointers in `Cited.md`.
- Graduation candidates that have not been reviewed.
- A deferred-provider project (`graduation.provider: none` in `.cairn/config.yaml`) holding confirmed graduation candidates — surface that connecting a knowledge base is pending (`graduation.md` → Deferred provider). Deferral itself is a valid state, not a defect; flag only when candidates are actually waiting.
- Project topic notes marked `graduation_status: candidate` but not yet graduated or confirmed.
- Project topic notes marked `graduation_status: deferred` or `graduation_status: not_applicable` without enough body context to explain the judgment.
- Knowledge-base notes missing `graduated_from` provenance.
- A new graduation missing a non-empty `graduated_by` list on either the project or knowledge-base side.
- A touched team topic whose safely identifiable substantive human contributors are missing from `contributors`.
- An empty Origin quote heading, or a direct quote without speaker/approved role, date, and context attribution.
- Potentially risky quote content. Flag it only as a prompt for human review; never issue an automatic safety verdict.
- Do not flag untouched legacy notes solely for lacking `contributors` or `graduated_by`: they remain valid and are backfilled only when touched or re-graduated.
- Project topic notes that have graduated but lack the recommended back-pointer (`graduated_to` / `graduated_at`).
- Project topic notes whose `updated` frontmatter date is newer than their `graduated_at` — the corresponding knowledge-base note may now be stale; suggest re-graduation (see `graduation.md` → Re-graduation), don't auto-trigger it.
- Closed or abandoned exploration branches whose valuable `cairn/` knowledge was never salvaged (should trigger a branch closure review, or a LOG / topic / graduation-candidate follow-up).
- Instance drift against the current skill spec: read `skill_spec_date` from `.cairn/config.yaml` and run the Detect step of every `references/upgrade.md` changelog entry newer than it (missing field = run the full changelog). Report drifted items with each entry's fix guidance and safety level; fixing them is the upgrade flow in `upgrade.md`, not audit's job.

## Behavior

Suggest fixes. Do not silently rewrite large bodies of content without user confirmation.

The audit run itself earns one `cairn/LOG.md` entry — a short summary of what was checked and what was found, plus a pointer to the findings, added at the top like any entry. Appending this record is not "rewriting content"; the no-rewrite rule protects existing material, not the log of the audit happening.
