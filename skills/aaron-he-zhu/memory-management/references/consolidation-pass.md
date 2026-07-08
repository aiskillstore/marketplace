# Consolidation Pass (Reflection)

The consolidation pass is `memory-management`'s **content-reconciliation** mode — the reflection step
that keeps long-running memory from degrading into stale, contradictory, duplicated noise. The step-5
hygiene checks look at **size and age**; this pass reconciles **meaning**. Run it on the `consolidate`
argument, on an explicit "reconcile/merge memory" request, or on the monthly archive cadence.

> Why it exists: append-and-age memory accumulates near-duplicates and equal-weight contradictions.
> Without reconciliation a reader can surface a stale fact over the current one (the "record still
> says Postgres six weeks after the MySQL migration" failure). This pass is the observable,
> file-based equivalent of the reflection/consolidation step in the agent-memory literature — done by
> the agent over markdown, with no reference-frequency counting and no external store.

## The four levers

| Lever | Action | Rule |
|-------|--------|------|
| **Deduplicate** | Merge entries stating the same fact in different words | Keep clearest phrasing + newest `last_updated`; one row per fact |
| **Resolve conflicts** | Reconcile two entries that disagree (same entity + field) | Recency-wins: mark older `superseded_by: [date]`; ambiguity → `open-loops.md`, never auto-pick |
| **Distill** | Collapse several related WARM findings into one durable conclusion | Promote the ≤3-line conclusion to HOT; detail stays in WARM |
| **Prune** | Remove what no longer earns its place | Demote/archive by the 30/90-day `last_updated` clock; drop superseded lines past 90 days |

## Procedure

1. Load `memory/hot-cache.md`, the relevant `candidates.md` ledgers, and any WARM files in scope.
2. Group entries by subject (entity, keyword, competitor, offer, veto, campaign).
3. Within each group, apply the levers **in order**: dedupe → resolve conflicts (supersede) → distill → prune.
4. Keep hot-cache within the 80-line / 25KB limit; if trimming is needed, **demote — do not delete**.
5. Report the diff: what was merged, what was superseded (with dates), what was distilled/promoted,
   what was archived — and any conflicts parked in `memory/open-loops.md`.

## Guardrails (Decision Gates)

- **Never overwrite** a user-approved `memory/decisions.md` entry or a registry canonical record —
  surface the conflict; supersede only via the owner/registry `candidates.md` flow.
- **Never hard-delete** to save space — demotion/archival is reversible; hard-delete is for GDPR
  erasure only (see [SKILL.md §GDPR](../SKILL.md)).
- **Never auto-resolve genuine ambiguity** — park it in `memory/open-loops.md` for the user.

## Worked example

Hot cache before (two sessions appended the same competitor's DA at different times, a third restated it):

```
- Competitor acme.com — DA 42 (measured 2026-04-02)
- Competitor acme.com — DA 51 (measured 2026-06-30)
- Rival acme.com domain authority is 51
```

After a consolidation pass — dedupe the third line into the second, supersede the stale first line:

```
- Competitor acme.com — DA 51 (measured 2026-06-30)
- Competitor acme.com — DA 42 (measured 2026-04-02) superseded_by: 2026-06-30
```

The live value is now unambiguous, the prior value is retained (not deleted), and the duplicate is gone.
The superseded line ages out on the normal 90-day clock.

## Cadence

- **On request** — `consolidate` / "reconcile memory".
- **Monthly** — as part of the archive routine (see [Update Triggers & Integration](update-triggers-integration.md) → Archive Management → Monthly).
- **Before a milestone** — a report, a launch T-0, or a quarter close, so downstream reads start clean.
