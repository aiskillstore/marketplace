# Spec Template

Copy the skeleton, fill it, delete nothing. A section with no content
says so in one line ("No open questions.") — a deleted section reads as an
oversight.

Path: `<initiative>/specs/INIT-NNNN-SPEC-nn-<topic-slug>.md`

Worked examples below use `INIT-0004` (cell placement) so the shape is
visible. Replace them; never ship them.

## Skeleton

````markdown
---
id: INIT-0004-SPEC-01
initiative: INIT-0004
kind: spec
title: Cell placement
status: draft
created_at: <UTC from an executed command>
updated_at: <same>
supersedes: null
superseded_by: null
implements: [INIT-0004-ARCH-01, INIT-0004-DSGN-01]
decisions: [INIT-0004-ADR-01, INIT-0004-ADR-02]
verification: INIT-0004-VRFY-01
plans: []
global_constraints: 3
---

# Cell placement — specification

## Scope

<One paragraph. What this spec governs, stated so a reader knows in ten
seconds whether their question is answered here. Name the components
involved by the names the architecture uses.>

## Global constraints

Every requirement below implicitly includes this section. Values are
copied verbatim from their source — never paraphrased.

| ID | Constraint | Source |
|---|---|---|
| C01 | Node `>= 20.11.0`; the build fails on lower | INIT-0004-ADR-01 |
| C02 | No new runtime dependency outside `@platform/*` | charter constraints |
| C03 | Cell identifiers match `^cell-[0-9]{1,4}$` | INIT-0004-IFCE-01 |

## Requirements

### R01 — Placement is deterministic for a fixed cell set

**Requirement:** Given the same tenant ID and the same set of available
cells, `placeCell` returns the same cell on every call.

**Observable:** Two calls with identical input return equal cell IDs.

**Source:** INIT-0004-ADR-01 (hash-based placement)

**Verified by:** V01

### R02 — Unknown cell is rejected with 422

**Requirement:** A placement request naming a cell absent from the
available set is rejected with HTTP 422 and a body whose `error` field is
`unknown_cell`. No placement is recorded.

**Observable:** Response status and `error` field; the placement table
gains no row.

**Source:** INIT-0004-IFCE-01 · `placeCell` error cases

**Verified by:** V02, V03

<One block per requirement. Numbered R01…Rnn, sequential, never
renumbered once any plan cites them. One requirement per number — an
"and" in the requirement sentence is a second requirement hiding.>

## Interfaces

Referenced by ID. Signatures live in the interface document; restating
them here creates a second source of truth that drifts.

| Interface | Symbols this spec relies on | Requirements |
|---|---|---|
| INIT-0004-IFCE-01 | `placeCell` | R01, R02, R03 |
| INIT-0004-IFCE-01 | `evictCell` | R14 (operator-invoked only; OOS-02 excludes automation) |

## Coverage

Output of self-review check 5. Every symbol in every referenced interface
document's `provides:` list is either specified or explicitly out of
scope; every ADR whose `informs:` names this spec is reflected.

| Source | Item | Specified as | Or out of scope because |
|---|---|---|---|
| INIT-0004-IFCE-01 | `placeCell` | R01, R02, R03 | — |
| INIT-0004-IFCE-01 | `evictCell` | R14 | Automated invocation excluded — OOS-02 |
| INIT-0004-ADR-01 | Hash-based placement | R01 | — |
| INIT-0004-ADR-02 | Tenant isolation boundary | R09 | — |

## Out of scope

Itemized. One line each, each naming the thing a helpful implementer
might otherwise build.

| ID | Not built | Note |
|---|---|---|
| OOS-01 | Multi-region placement | Single region only; see charter non-goals |
| OOS-02 | Automated eviction | `evictCell` stays operator-invoked |
| OOS-03 | Placement rebalancing on cell addition | Deliberate; a later initiative |

## Open questions

| ID | Question | Owner | Blocking |
|---|---|---|---|
| Q1 | Does a tenant keep its cell across a plan upgrade? | <human> | yes |
| Q2 | Retention for placement audit rows | <human> | no |

A blocking question is answered before the phase gate passes. A
non-blocking one is answered before the requirement that depends on it is
planned — name that requirement here.

## Impact on existing plans

<Only present when this spec supersedes another. One row per plan whose
`spec:` named the superseded document.>

| Plan | Status | Action |
|---|---|---|
| INIT-0004-P01 | executing | Task 4 re-argued: R05 threshold changed |
| INIT-0004-P02 | not started | Unaffected; cites R01–R03 only |
````

## Requirement block rules

| Field | Rule |
|---|---|
| Heading | `### R<nn> — <short name>`; the name is a handle, the requirement is the sentence |
| Requirement | Present indicative of the finished system. Exact values, exact strings, exact status codes |
| Observable | What a person or a command sees from outside. If you cannot write this line, the requirement is not testable |
| Source | The `ADR`, `IFCE`, `DSGN`, or charter line it derives from — this initiative's IDs only |
| Verified by | The VRFY criterion IDs (`V<nn>`). Filled in when the VRFY document is written |

Optional per requirement, when they carry real content:

- **Failure behaviour** — what happens on the sad path, if the
  requirement's main sentence covers only the happy one.
- **Boundary** — the exact limit and what happens at, below, and above it.
  "Up to 4096 cells" needs the behaviour at 4096 and at 4097.

## What a good requirement looks like

| Bad | Why it fails | Good |
|---|---|---|
| The router handles invalid input gracefully | Unobservable, ambiguous | R02 above |
| Placement should be fast | No threshold | Placement returns within 50ms at p99 for 10k tenants |
| Add appropriate logging | Placeholder | Each placement emits one `placement.assigned` log line carrying tenant ID and cell ID |
| Validate the request and store the placement | Two requirements in one | Split into R04 (validation) and R05 (persistence) |
| Behaves like the existing shard router | "Similar to X" | State the behaviour; the implementer has not read the shard router |

## Before writing the file

1. `id` matches the filename's ID segment.
2. `initiative` matches the containing folder's ID.
3. Every referenced ID begins with this initiative's ID — a
   cross-initiative citation is forbidden; move the dependency to the
   charter's `depends_on`.
4. `global_constraints` equals the number of `C<nn>` rows.
5. `created_at` / `updated_at` came from an executed command.
6. If superseding: the old document's `superseded_by` points back here.
