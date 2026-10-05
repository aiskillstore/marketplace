# IFCE Template — Interface Contract

One per seam crossed by more than one task or plan. Path:
`docs/executor/INIT-NNNN-<slug>/architecture/INIT-NNNN-IFCE-nn-<slug>.md`

Allocate the ID immediately before writing:
`../../executor/scripts/exec-id INIT-NNNN IFCE`

**The failure this document prevents:** two implementers, each seeing only
their own task, build incompatible halves of one seam because the plan
described the interface in prose. Both halves pass their own tests. The
integration is a rewrite and neither implementer was wrong.

Write it so that a reader who never sees the other side of the seam cannot
guess anything. Anything guessable will be guessed differently.

Copy the structure below. Guidance sits in italic lines — replace each one
with content.

## Frontmatter

```yaml
---
id: INIT-0004-IFCE-01
initiative: INIT-0004
kind: interface
title: Cell store and placement error contract
status: draft                       # draft while writing, active when the gate passes
created_at: 2026-09-01T14:55:52Z    # date -u +%Y-%m-%dT%H:%M:%SZ
updated_at: 2026-09-01T14:55:52Z
supersedes: null
superseded_by: null
provides: [CellStore.candidates, CellStore.bind, CellStore.release, MetricsPort.emit]
consumers: [INIT-0004-P01, INIT-0004-P02]
stability: draft                    # draft|stable|frozen
---
```

| `stability` | Meaning | Changing it |
|---|---|---|
| `draft` | Architecture in progress | Edit freely; nothing is built against it |
| `stable` | Gate passed; plans may be written against it | Update every named consumer in the same change |
| `frozen` | A plan is executing against it | Do not edit. Supersede with a new IFCE and record a ruling in the running plan |

`consumers` is filled in as plans are written. An interface with no consumer
list cannot be changed safely, because nobody knows who breaks.

## Body

---

# Cell store and placement error contract

## Scope

*Which components sit on each side. Name them from the ARCH inventory so a reader can find both halves.*

Provider: `sqlite-cell-store` (adapter). Consumer: `placement-service`
(policy). The port itself is owned by policy — the adapter implements it, per
the boundary table in `INIT-0004-ARCH-01`.

## Data types

*Every type crossing the seam, exact. Units, nullability, ranges, encodings. "A timestamp" is four incompatible representations.*

```ts
type CellId = string;        // "r1-c007"; ^[a-z0-9]+-c[0-9]{3}$; never empty
type TenantId = string;      // UUID v4, lowercase, hyphenated
type SizeClass = "small" | "medium" | "large";   // exhaustive; no default

interface Cell {
  id: CellId;
  region: string;            // ISO-3166-1 alpha-2, lowercase
  usedBytes: number;         // integer, >= 0, bytes not MB
  capacityBytes: number;     // integer, > 0
  admitting: boolean;        // false while draining
}

interface Placement {
  tenant: TenantId;
  cell: CellId;
  boundAt: string;           // RFC 3339 UTC, millisecond precision, always "Z"
}
```

*Use the initiative's actual language. The point is exactness, not the notation.*

## Operations

### `candidates(region, sizeClass) -> Cell[]`

```ts
candidates(region: string, sizeClass: SizeClass): Promise<Cell[]>
```

| Parameter | Type | Constraint |
|---|---|---|
| `region` | `string` | ISO-3166-1 alpha-2, lowercase; unknown region is not an error, it returns `[]` |
| `sizeClass` | `SizeClass` | Exhaustive union; an unknown value is a programming error, not a runtime case |

**Returns:** cells in `region` with `admitting === true`, ascending by
`usedBytes`. Empty array when none qualify — **not** an error, and not
`null`. Ordering is part of the contract: the consumer relies on it for
tie-breaking and does not re-sort.

**Errors:**

| Error | When | What the caller must do |
|---|---|---|
| `StoreUnavailable` | Database file unreachable or locked beyond 500 ms | Fail the placement with retry-after; do not fall back to a stale list |
| — | No other error is possible | Any other throw is a defect in the adapter |

**Ordering / lifecycle:** callable only after `open()` has resolved. Read-only
and safe to call concurrently.

### `bind(tenant, cell) -> Placement`

```ts
bind(tenant: TenantId, cell: CellId): Promise<Placement>
```

**Returns:** the persisted placement, with `boundAt` set by the store, not
the caller — the store owns the clock for this field so two nodes cannot
disagree.

**Errors:**

| Error | When | What the caller must do |
|---|---|---|
| `AlreadyBound` | The tenant already has a placement | Read the existing placement and return it; do not retry the bind |
| `CellNotAdmitting` | The cell stopped admitting between `candidates` and `bind` | Re-run `candidates` once, then fail |
| `StoreUnavailable` | As above | Fail with retry-after |

**Idempotency:** not idempotent. A repeated `bind` for the same pair raises
`AlreadyBound` rather than succeeding silently, so a duplicated request is
visible instead of masked.

**Concurrency:** two concurrent `bind` calls for the same tenant — exactly
one succeeds, the other raises `AlreadyBound`. Enforced by a unique
constraint, not by caller discipline.

### `release(tenant) -> void`

```ts
release(tenant: TenantId): Promise<void>
```

**Idempotent.** Releasing an unbound tenant succeeds and does nothing, so
retry after a timeout is always safe.

**Errors:** `StoreUnavailable` only.

## Lifecycle

*What must be initialised before what, and what is guaranteed at each stage. Two correct implementations can still deadlock or double-apply without this section.*

1. `open(config)` resolves before any other call; calls before it raise
   `NotOpen`.
2. Between `open` and `close`, all operations above are available.
3. `close()` waits for in-flight writes, then rejects new calls with
   `NotOpen`. `close()` is idempotent.

## Invariants the provider guarantees

- `usedBytes <= capacityBytes` for every returned cell.
- A tenant has at most one placement at any time.
- `boundAt` never moves backwards for a given tenant.

## Invariants the consumer must uphold

- Never persist a `CellId` obtained anywhere other than `candidates`.
- Never treat an empty `candidates` result as a transport failure.
- Never re-sort the `candidates` result.

## Worked call

*One end-to-end example, so both implementers are reading the same sequence rather than inferring it.*

```ts
const cells = await store.candidates("de", "medium");
if (cells.length === 0) throw new NoCapacity();
try {
  return await store.bind(tenant, cells[0].id);
} catch (e) {
  if (e instanceof AlreadyBound) return await store.placementOf(tenant);
  if (e instanceof CellNotAdmitting) { /* one retry from candidates */ }
  throw e;
}
```

## Change log

*Every change after stability reaches `stable`, so a consumer can tell whether the document changed under them.*

| Date | Change | Consumers updated |
|---|---|---|
| 2026-09-01 | Initial contract | — |

---

## Gap policy

**A task blocked by a missing signature is an architecture gap, not a
planning detail.** When an implementer or planner finds a name, type, error,
or ordering rule missing:

1. Amend this document (or supersede it if `stability: frozen`).
2. Update every named consumer in the same change.
3. Do **not** let the implementer choose — a name invented inside one brief
   is a name its counterpart never sees.

## Quality bar

- Every operation has an exact signature with parameter names in order.
- Every type states units, nullability, and encoding.
- Every error names both the condition and the caller's required response.
- Ordering, idempotency, concurrency, and lifecycle are stated, not implied.
- Empty, absent, and error results are distinguished explicitly.
- `stability` and `consumers` are accurate as of this change.
- Every ID cited belongs to this initiative.
- No credentials, tokens, or real endpoint secrets in examples — use
  `<placeholder>` shapes.
