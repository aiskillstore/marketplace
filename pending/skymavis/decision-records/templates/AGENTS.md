# AGENTS.md — decision records

This file governs how an agent works with the **decision records** under `docs/decisions/`. These
records are **binding** for work in this repo.

The records live here; **how** to author, promote, link, and validate them is owned by the
**decision-records skill** (the `scripts/decisions.py` tool installed from it). The skill is
authoritative — when this file and the skill disagree, the skill wins. If the tool is missing,
install it before changing any record.

## Read order (every task)

1. This file.
1. `docs/decisions/INDEX.md` — the generated registry. Read it first, then load only the records
   whose `type`/`tags` match the task. **Skip `archived/` by default** — consult it only when
   tracing why a decision changed.
1. The specific record(s); their front-matter is authoritative.

## Decision governance — highest priority

1. **Review the relevant accepted records before acting** on anything they cover.
1. **If a request conflicts with an accepted record, STOP and surface it** — do not quietly proceed.
   Only flag real conflicts; stay silent when aligned.
1. **Never rewrite an accepted decision to change course — supersede it** with a new record that
   replaces the old. Refer to records by their counter (e.g. 0001), never by a hand-written path.

## Boundaries

- `accepted/<type>/` and `archived/` — the decision record. **Held firm once accepted**: changing
  course requires supersession, never a rewrite; decider-approved maintenance edits (clarity,
  staleness, cross-record consistency, typography) are allowed. Firm, not frozen.
- `drafts/` — work-in-progress candidates; mutable until promoted. Promotion is a finalizing step
  that needs explicit human sign-off, so never promote on your own initiative.
- Other `docs/*.md` — living docs that may cross-reference records by ID.
- `docs/decisions/INDEX.md` is **generated** — never hand-edit it; regenerate with
  `scripts/decisions.py build`.

## Working style

Be precise. Cross-reference before producing, and verify claims against the source-of-truth record,
not a summary. Keep the active decision set clean: one accepted record per decision, retired ones in
`archived/`.
