# Reconcile Duplicates And Merge Safely

Primary tools:
- `review_affinity`
- `inspect_affinity_item`
- `merge_contacts`

Goal:
- Collapse true duplicates without losing lineage, identities, participants, or relationship truth.

When to use:
- Duplicate-candidate review surfaces indicate a likely duplicate.
- A harness or operator has strong evidence that two contacts are the same real entity.

When not to use:
- The match is still speculative and unresolved.
- The real need is just better identities or labels rather than an actual merge.

Step-by-step sequence:
1. Start with `review_affinity` on the duplicate-candidate view.
2. Inspect both candidate contacts before merging.
3. Confirm the winner explicitly rather than letting recency or convenience decide by accident.
4. Use `merge_contacts` only when the identity and history picture is clear.
5. Inspect the surviving contact after the merge to confirm the merged state looks right.
6. Review merge history when you need lineage confirmation later.

Validation checks:
- The surviving contact now contains the expected identities and visible history.
- The loser is no longer treated as a live normal contact.
- The merge reason is still understandable when reviewed later.

Pitfalls:
- Do not merge on a weak fuzzy-name match alone.
- Do not skip inspection of both sides before merging.
- Do not assume merges are easy to conceptually undo just because the system preserves lineage.

Tips and tricks:
- Prefer a winner that already carries the stronger routing identity and richer history unless another reason dominates.
- If the system is uncertain, clarify first instead of forcing a merge.
- Review merge history after sensitive merges to confirm the lineage chain is clean.

Tool calls to prefer:
- `review_affinity` for duplicate-candidate discovery and merge-history review
- `inspect_affinity_item` for both candidate contacts
- `merge_contacts` only after confirmation

Related skills:
- `identify-and-locate-contacts`
- `import-history-without-faking-evidence`