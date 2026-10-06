# DSGN Template — Component Design

One per component whose internals are not obvious from the ARCH plus its
IFCE. Path:
`docs/executor/INIT-NNNN-<slug>/design/INIT-NNNN-DSGN-nn-<slug>.md`

Allocate the ID immediately before writing:
`../../executor/scripts/exec-id INIT-NNNN DSGN`

A design covers **one** component's insides. Its public surface is not
restated here — it points at the interface document. If this design describes
two components, split it; if it restates the IFCE, delete the restatement,
because two copies of a signature drift.

Copy the structure below. Guidance sits in italic lines — replace each one
with content.

## Frontmatter

```yaml
---
id: INIT-0004-DSGN-01
initiative: INIT-0004
kind: design
title: Placement service internals
status: draft                       # draft while writing, active when the gate passes
created_at: 2026-09-01T14:55:52Z    # date -u +%Y-%m-%dT%H:%M:%SZ
updated_at: 2026-09-01T14:55:52Z
supersedes: null
superseded_by: null
component: placement-service
implements: [INIT-0004-ARCH-01]
interfaces: [INIT-0004-IFCE-01]
---
```

## Body

---

# Placement service internals

## 1. Responsibility

*One line, matching the ARCH inventory exactly. If they disagree, one is wrong — fix it here and in the ARCH in the same change.*

Chooses the cell a tenant belongs to and records the binding.

## 2. What this component does not do

*Explicit non-responsibilities. This is where scope creep is cheapest to stop, and where an implementer learns which neighbour to call.*

- Does not decide whether a request is admissible — `admission-control` does.
- Does not open a database handle — only `sqlite-cell-store` does.
- Does not format responses or map errors to status codes — `http-edge` does.

## 3. Public surface

*Point, do not copy.*

Consumed: `CellStore`, `MetricsPort` — see `INIT-0004-IFCE-01`.
Exposed: `place(request) -> Placement` — see `INIT-0004-IFCE-01`.

## 4. State

*Every piece of state the component holds, who may mutate it, and how long it lives. State with no named owner is state two code paths will fight over.*

| State | Type | Lifetime | Mutated by | Rule |
|---|---|---|---|---|
| `rules` | `PlacementRules` | process | never after construction | Immutable; a rules change is a restart |
| `scoreCache` | `Map<CellId, number>` | one `place()` call | `score()` only | Never outlives the call; no cross-request caching, because a stale score binds a full cell |
| none | — | — | — | The component holds no connection, no session, no clock |

**Concurrency:** `place()` is re-entrant and holds no shared mutable state
between calls. Two concurrent placements for the same tenant are resolved by
the store's unique constraint (`INIT-0004-IFCE-01`), not here.

## 5. Algorithms

*Step by step, with the ordering and the complexity. If the order of two steps matters, say why — that "why" is what stops a later refactor from swapping them.*

### `place(request)`

1. `candidates = store.candidates(request.region, request.sizeClass)`.
2. If empty → raise `NoCapacity`. (Checked before scoring so the empty case
   costs no work.)
3. Score each candidate: `score = freeBytes / capacityBytes`, tie-break by
   the store's returned order — which is ascending `usedBytes`, and is part
   of the contract, so we do not re-sort.
4. `store.bind(request.tenant, best.id)`.
5. On `AlreadyBound` → return the existing placement (idempotent from the
   caller's view). On `CellNotAdmitting` → retry from step 1 exactly once,
   then raise.
6. Emit `placement.bound` with cell and duration via `MetricsPort`.

**Complexity:** O(n) in candidate count, n bounded by cells per region
(currently ≤ 64). No sort — the store returns ordered.

## 6. Edge cases

*The cases a reasonable implementer would get wrong, each with the required behaviour. This table is the design's highest-value section for whoever writes the tests.*

| Case | Required behaviour |
|---|---|
| No candidates | `NoCapacity`, no metric emitted, no store write |
| Exactly one candidate at 100% capacity | Still rejected — capacity check is in scoring, not only in the store |
| `AlreadyBound` | Return the existing placement; do not re-bind, do not raise |
| `CellNotAdmitting` twice in a row | Raise after the single retry; do not loop |
| Metrics emit fails | Placement still succeeds; the error is swallowed and counted |
| Tie between two identical scores | Lower `usedBytes` wins, i.e. store order |

## 7. Error handling

*Which errors this component raises, which it translates, and which it lets through untouched. Silent translation is how a caller loses the ability to react.*

| Origin | Handling |
|---|---|
| `StoreUnavailable` | Propagate unchanged — the edge maps it to 503 |
| `AlreadyBound` | Absorbed; converted into a successful return |
| `CellNotAdmitting` | Absorbed once, then propagated |
| Metrics errors | Absorbed and counted; never affect the result |

## 8. Testing seams

*What is injected, what fakes exist, and what must be exercised for real. Core behaviour must be testable without the real framework, database, network, vendor, or clock — that requirement is what a seam is for.*

| Seam | Injected as | Fake | Tested for real where |
|---|---|---|---|
| `CellStore` | constructor parameter | `InMemoryCellStore` — enforces the same unique constraint | Adapter test against a real SQLite file |
| `MetricsPort` | constructor parameter | `RecordingMetrics` | Not tested for real; emission is fire-and-forget |
| Clock | not needed — the store owns `boundAt` | — | — |

Tests target the behaviour in section 6, not the call sequence in section 5 —
asserting that `candidates` was called once tests the plumbing, and passes
after the logic breaks.

## 9. File structure

*Decomposition, decided once here with the whole component in view.*

| Path | Responsibility | Changes when |
|---|---|---|
| `core/placement/place.ts` | The `place()` use case | The placement flow changes |
| `core/placement/score.ts` | Scoring and tie-breaking | The scoring rule changes |
| `core/placement/errors.ts` | `NoCapacity` and the absorbed-error policy | The error contract changes |
| `core/ports/cell-store.ts` | The `CellStore` port declaration | `INIT-0004-IFCE-01` changes |
| `test/placement/place.test.ts` | Section 6 edge cases | Behaviour changes |

Rules this table follows:

- **One clear responsibility per file**, with a well-defined interface.
- **Files that change together live together. Split by responsibility, not
  by technical layer** — a layer-sliced tree makes one conceptual change edit
  five directories.
- **Prefer smaller, focused files over large ones that do too much.** Agents
  reason best about code they can hold in context at once, and edits are more
  reliable when files are focused.
- **In an existing codebase, follow the established patterns.** If the
  codebase uses large files, do not unilaterally restructure. If a file this
  work must modify has grown unwieldy, propose the split here — with its
  boundary named — so planning can task it deliberately rather than an
  implementer improvising it mid-task.

## 10. Open questions

*What this design does not settle, so the spec does not assume it did.*

- Whether eviction belongs here or in a separate component. Deferred; the
  `CellStore` port leaves room for either.

---

## Quality bar

- The responsibility line matches the ARCH inventory word for word.
- The non-responsibilities name the neighbour that owns each excluded concern.
- Every state row has an owner, a lifetime, and a mutation rule.
- Every algorithm step whose order matters says why.
- The edge-case table is specific enough to become test names directly.
- Every seam names its fake, and nothing that must be real is faked.
- The file table gives every file one responsibility and a "changes when".
- Every ID cited belongs to this initiative.
- No credentials, tokens, or connection-string values.
