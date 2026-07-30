# Dual-host acceptance

Test date: 2026-07-28

Claude Code version: 2.1.218

Codex host: current parent worker

## Success prompt

```text
Use the home-bar-inventory-audit skill. The frozen record, physical count, and
proposed dispositions are in tests/fixtures/success.json inside the installed
skill. Run the verifier and return the exhaustive review package. Preserve the
vermouth freshness handoff and do not update any inventory system.
```

Claude Code session `b91e5fed-8b36-4f1e-a88a-60800dbd1802` returned
`EXHAUSTIVE REVIEW PACKAGE`. It linked gin as matched and vermouth as a location
mismatch, left Campari missing, and proposed soda water as an addition.

The vermouth condition question stayed a product-specific freshness handoff.
No use or discard decision appeared, and `external_edit` remained `not
performed`.

Codex ran the same fixture through `scripts/audit.py` and reproduced all four
dispositions, zero unaccounted IDs, and `READY FOR INVENTORY REVIEW`.

Success verdict: pass.

## Edge prompt

```text
Use the home-bar-inventory-audit skill. The prior record contains one Brand A
gin, while the physical count contains two identical Brand A bottles with
unknown fill. The normalized uncertain links are in tests/fixtures/edge.json.
Run the verifier. Keep the second bottle needs_review instead of calling it a
duplicate or addition, and do not edit inventory.
```

Claude Code session `c9593ad9-c130-4628-967c-910e54e2ddea` linked one observed
bottle to the record with `needs_review`. The second physical bottle retained
its separate `needs_review` state.

Codex produced the same exhaustive package. Neither host called the second
bottle a duplicate or addition without user evidence.

Edge verdict: pass.

## Failure prompt

```text
Use the home-bar-inventory-audit skill. Run the verifier on
tests/fixtures/failure.json inside the installed skill. The rum record has no
physical link or disposition. Show the documented failure, name the unaccounted
record, and do not invent a cause or edit inventory.
```

Claude Code session `ecbe81b4-6227-4a53-b4b0-f9661fd38d45` stopped with
`error: unaccounted record: r2`. It identified the rum record and explained
that no review package can exist until the record receives `missing` or
`needs_review`.

Codex reached the same verifier error. It did not infer consumption, disposal,
loss, or relocation.

Failure verdict: pass.

## Differences and corrections

Claude Code rendered a narrative review package. Codex retained more of the
verifier field names. Dispositions, counts, freshness boundary, and external
action stop matched.

No correction was required after the six runs.

## Final verdict

All six cases pass. Both hosts account for each side exactly once, preserve
uncertainty, and stop before any inventory edit.
