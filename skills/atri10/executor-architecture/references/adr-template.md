# ADR Template — Decision Record

One per decision that had a live alternative. Path:
`docs/executor/INIT-NNNN-<slug>/architecture/INIT-NNNN-ADR-nn-<slug>.md`

Allocate the ID immediately before writing:
`../../executor/scripts/exec-id INIT-NNNN ADR`

An ADR records a decision taken **with the human in the loop**, during
architecture or design. It is not a ruling: rulings are execution-time
decisions taken without the human while a plan runs, recorded by
`exec-ruling` into that plan's `rulings.md`.

Copy the structure below. Guidance sits in italic lines — replace each one
with content.

## Frontmatter

```yaml
---
id: INIT-0004-ADR-01
initiative: INIT-0004
kind: adr
title: Storage engine for cell state
status: draft                          # draft while writing, active when the gate passes
created_at: 2026-09-01T14:55:52Z       # date -u +%Y-%m-%dT%H:%M:%SZ
updated_at: 2026-09-01T14:55:52Z
supersedes: null                       # a prior ADR in THIS initiative, or null
superseded_by: null
decision: Use per-cell SQLite over a shared Postgres cluster
alternatives_considered: 3
consequences_accepted: No cross-cell transactions; operator must manage N files per node
reversibility: one-way                 # one-way|two-way
informs: [INIT-0004-SPEC-01]
---
```

`decision` is the one-line answer. `consequences_accepted` is the cost you
are choosing, in one line — if it reads as a benefit, it is not the cost.

## Body

---

# Storage engine for cell state

## Context

*What forced a decision, in terms a reader outside the team recognises. Include the constraint or measurement that narrows the field, with its provenance — measured, cited, or inferred. Two paragraphs at most.*

Placement must answer in under 200 ms at p99 with 10k tenants (charter
success criteria). Measured on the load harness (`INIT-0004-RSCH-02`), a
shared cluster added 40–60 ms per placement in network and connection cost
alone, against a 200 ms budget that also has to cover scoring.

Cell state is per-cell by definition: a placement reads candidates within
one region and writes one binding. No query in the design spans cells.

## Options weighed

*Every option that was genuinely viable, each with its cost stated. An option with no cost was not evaluated. Three rows minimum for a one-way door; one alternative is enough for a two-way door.*

| Option | What it buys | What it costs |
|---|---|---|
| Per-cell SQLite (chosen) | No network on the placement path; per-cell isolation is physical | No cross-cell transactions; N files per node to back up; operator learns a new failure mode |
| Shared Postgres cluster | One backup story, familiar ops, cross-cell queries possible | 40–60 ms per placement measured; isolation becomes a query predicate the code must never get wrong |
| Embedded key-value store (LMDB) | Fastest reads measured; single file | No SQL for ad-hoc operator inspection; a scoring change becomes a code change instead of a query change |

*If discovery already compared these, cite the OPTS document by its ID within this initiative rather than repeating the comparison.*

Fuller comparison: `INIT-0004-OPTS-01`.

## Decision

*The choice, stated as a rule someone can apply, not as a preference.*

Cell state lives in one SQLite database per cell, opened by
`sqlite-cell-store`, which is the only component permitted to hold a database
handle. Policy reaches storage exclusively through the `CellStore` port
(`INIT-0004-IFCE-01`).

## Consequences accepted

*Including the ones you dislike. An ADR that lists only consequences you are happy about is an argument, not a record.*

- No cross-cell transaction is available. Any future operation spanning cells
  needs a saga or an explicit two-phase design.
- Backup and restore operate on N files per node, not one endpoint. Runbook
  work lands in the operations documentation.
- Cell migration becomes a file move plus a rebind, which is simpler than a
  row migration but has no partial-progress story.
- Operator ad-hoc inspection works (SQL), which is why LMDB lost.

## What would make this decision wrong

*MANDATORY. Observable, checkable by someone who was not in the room, and paired with the trigger that sends a reader back here. An ADR with no falsifier is an opinion with a template.*

This decision is wrong if any of the following becomes true:

| Falsifier | How it is observed | Trigger to revisit |
|---|---|---|
| A single cell's data exceeds one node's disk | Cell size metric crosses 40 GB | Alert on cell size; reopen this ADR |
| A required operation must be transactional across cells | A spec requirement states it | Spec review — do not work around it silently |
| Placement latency is dominated by scoring, not I/O | Placement benchmark shows I/O under 5 ms of the total | Quarterly benchmark; the latency argument no longer justifies the cost |

## Reversibility

*Match the scrutiny to the door. State what reversal actually costs.*

**One-way.** Reversal means migrating stored data out of N SQLite files into a
cluster, with a dual-write period, and rewriting the isolation guarantee from
physical to logical. Estimated at weeks, not days — which is why three
options were measured rather than argued.

*For a two-way door, this section is one line: "Two-way. Reversal is a new adapter behind the same port, roughly a day." Decide it fast, and revisit it when the falsifier fires.*

## Supersession

*Only present when this ADR replaces another. Restate the original context and name what changed: new evidence, a changed constraint, or the old falsifier firing. Never edit the superseded document's body.*

Supersedes `INIT-0004-ADR-01`, which chose a shared cluster before the load
harness existed. Its falsifier ("wrong if measured per-placement network cost
exceeds 20 ms") fired at 40–60 ms. That reasoning stands as written and is
why this decision is defensible; the old document keeps its body and gains
`superseded_by`.

---

## Quality bar

- `decision` reads as a rule, not a preference.
- Every option has a stated cost; a one-way door has at least three options.
- `consequences_accepted` names something you dislike.
- The falsifier is observable by an outsider and has a revisit trigger.
- `reversibility` matches the scrutiny actually applied — never label a
  one-way door two-way to skip the work.
- Every ID cited belongs to this initiative. Cross-initiative dependencies
  live in the charter's `depends_on`, never here.
- No credentials, tokens, or connection-string values.
