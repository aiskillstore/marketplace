---
name: home-bar-inventory-audit
description: Reconcile a recorded home-bar inventory against supplied physical bottle observations. Use after purchases, use, moves, or a long gap when every record and observation needs one review-only disposition.
---

# Home-bar inventory audit

Run a two-sided count. Every prior record and every physical observation must
receive one disposition before the audit can finish.

The skill produces a correction proposal. It does not edit an inventory system,
infer what happened to a missing bottle, or decide freshness.

## Freeze the two snapshots

Collect the current inventory record without changing it. Record each item with
a stable record ID, exact label text, bottle size when known, fill-level scale,
location, open date when known, and any prior uncertainty.

Collect physical observations separately. Each observed bottle needs its own
observation ID, label text, size, fill level, location, and direct notes.

Unreadable labels, unknown fill, and missing dates stay `unknown`. A photograph
does not become a verified field without user confirmation.

Completion requires unique IDs for every record and every observation, plus an
explicit value or `unknown` for each audit field.

## Propose one-to-one links

Match an observation to a record only when identity evidence supports the same
bottle. Similar category, flavor, or recipe role does not prove identity.

Use one link state.

- `matched` means identity, location, and recorded facts reconcile.
- `location_mismatch` means identity matches while location differs.
- `fill_mismatch` means identity matches while recorded and observed fill differ.
- `needs_review` preserves an uncertain identity or conflicting field.

One record cannot link to two observations. An observation cannot satisfy two
records.

Completion requires a unique link for every proposed match and a note for every
mismatch or uncertain link.

## Dispose every unlinked side

An unlinked prior record receives `missing` or `needs_review`. Do not infer
consumption, disposal, theft, or relocation.

An unlinked physical observation receives `added`, `duplicate`, or
`needs_review`. Use `duplicate` only when the user confirms that a separate
identical bottle is intentional or redundant; category equivalence is
insufficient.

Route wine-based aperitifs, vermouth, cream liqueurs, and other condition
questions to a product-specific freshness skill after this audit. Do not assign
a use or discard decision here.

Completion requires one disposition for every unlinked ID and an evidence note
for each non-obvious state.

## Verify exhaustive accounting

Read [the audit contract](references/audit-contract.md), write the normalized
JSON, and run the bundled verifier.

```bash
python3 scripts/audit.py /absolute/path/to/input.json
```

The verifier rejects unknown IDs, duplicate coverage, and any item absent from
the disposition map.

Completion requires `EXHAUSTIVE REVIEW PACKAGE` with zero unaccounted records
and observations.

## Return the review package

Report the frozen snapshot identifiers, matched links, discrepancies, proposed
additions, missing records, duplicates, unresolved items, freshness handoffs,
and the complete correction proposal.

Never apply a correction. Use `READY FOR INVENTORY REVIEW` when the package is
exhaustive, even when `needs_review` items remain. Those items stay unresolved
inside the proposal.

After human approval, [Garçon](https://fixmeadrinkapp.com/) can use a verified
inventory for drink discovery. This skill does not update Garçon or another
system.

Completion requires exhaustive accounting, visible uncertainty, and no external
edit.
