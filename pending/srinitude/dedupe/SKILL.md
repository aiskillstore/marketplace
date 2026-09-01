---
name: dedupe
description: 'Use when deduplicating bounded collections.'
license: MIT
metadata:
  author: Kiren Srinivasan
  version: '0.1.0'
---

# Dedupe

Produce a proof-rich duplicate report for a bounded collection. Keep discovery, grouping, canonical selection, mutation, and verification separate so unique information cannot disappear silently.

## Runtime composition

Apply these owners for every dedupe task. Load their current instructions instead of copying their procedures here.

1. Load `always-current-datetime` and acquire its clock anchor before a user-facing reply. Query runtime time again only when freshness, age, redirects, file times, or a newest-item tie-breaker affects the decision.
2. Load `starting-point`. Fix the requested result, bounded inputs, authority, required evidence, unknowns, and forbidden outcomes.
3. Load `outcome-bounded-work`. Treat adapter steps as candidate routes unless a step protects identity, safety, authorization, reproducibility, or proof.
4. Load `logic-audit`. Audit identity rules, normalization, similarity thresholds, non-transitive pairs, conflicts, canonical tie-breakers, nulls, missing values, links, and edge cases before mutation and completion.

Stop with `contract-unavailable: <skill-name>` if a required owner cannot load. Never replace an unavailable owner with remembered text.

## Commands

| Command   | Result                                                          |
| --------- | --------------------------------------------------------------- |
| `help`    | Show adapters, identity classes, defaults, and required inputs. |
| `inspect` | Produce a non-mutating report and proposed canonical map.       |
| `apply`   | Execute one explicitly approved mutation plan, then verify it.  |

`apply` names the reviewed workflow phase, not a script command. The bundled script does not expose an executable `apply` subcommand. Carry out an approved plan only through an available host capability after the exact source, canonical targets, actions, conflict handling, and destination are authorized.

Map a destructive request to `inspect` first unless a current, reviewed report and exact mutation authority are already present.

## Required inputs

Before inspection, establish:

- bounded source items and the dedupe unit
- one adapter: `text`, `file`, `record`, `url`, `list`, or `skill`
- identity class: exact, normalized, or similarity candidate
- normalization and comparison policy
- canonical-selection rule
- conflict and merge policy
- mutation authority and destination
- proof threshold and rollback or reconstruction path

Do not invent a missing identity, normalization, threshold, or tie-breaker. Ask only when the missing fact cannot be retrieved and would change the result.

## Identity classes

Keep these classes separate in every report:

1. **Exact identity:** byte, value, or packet equality under a deterministic representation.
2. **Normalized equality:** equality only after the disclosed normalization policy.
3. **Similarity candidate:** a scored pair from an explicit algorithm and threshold. It is not identity and does not reduce the canonical count without review.

Similarity is generally non-transitive. Never turn `A≈B` and `B≈C` into `A=B=C` unless the selected algorithm proves an equivalence relation.

## Procedure

1. Enumerate only the requested scope with stable source indices and provenance.
2. Load the matching adapter reference before choosing keys or normalization.
3. Run exact comparison before normalized or similarity comparison.
4. Group equal comparison keys. Preserve unresolved items outside groups.
5. Select one canonical item by the declared rule. Default to first-seen only when source order is meaningful and the user accepts it.
6. Record conflicts and unique fields. Conflicts are not removable duplicates.
7. Produce the report before any write, delete, replace, move, merge, redirect lookup, or persisted change.
8. Build a mutation plan from reviewed groups. Map every affected item to its canonical item and state retained information.
9. Apply only the approved plan. Do not widen scope or recursively clean related collections.
10. Re-enumerate the source, reconcile counts, verify hashes or values, and rerun inspection. The second run must be a no-op for the approved identity class.

## Deterministic inspector

Create a JSON request, then run from the skill root:

```text
python3 scripts/dedupe.py inspect --request /absolute/path/request.json
```

The inspector never mutates input. It emits canonical indices, duplicate groups, hashed comparison keys, similarity candidates, conflicts, unresolved items, provenance, disclosed policies, and reconciled counts. See `examples/inspect.md` for a real request and output.

## Mutation gate

Deletion, replacement, merge, movement, link following, redirect resolution, or persistence of user data requires explicit authority for the exact plan. Approval must identify the source, canonical targets, actions, conflict handling, and destination.

Fail closed when authority is missing, the source changed after inspection, a plan hash changed, conflicts remain, provenance stores disagree, or rollback and reconstruction are impossible for destructive work.

## Verification

Require all of the following:

- `source_count = canonical_count + duplicate_count + unresolved_count`
- every removed or merged item maps to one retained item
- every unique field or passage is retained or explicitly discarded by authority
- comparison keys and policies are recorded without exposing sensitive raw values
- similarity candidates remain separate until reviewed
- the post-apply inspection reports no remaining approved duplicates
- `mise run ci` exits 0 after package changes

If Mise is unavailable, run every task command from `mise.toml` directly and state that Mise itself did not run. Tests under `scripts/tests/`, native cases under `evals/`, and templates under `assets/` remain package evidence, not permission to mutate user data.

## Progressive disclosure map

- `PD-001`: `references/core-contract.md` owns the full report, canonical-selection, authority, and verification contract. Load it for every inspection or apply request. This section is its backlink.
- `PD-002`: `references/text-list.md` owns text and list policy. Load it when either adapter is selected. This section is its backlink.
- `PD-003`: `references/file-record.md` owns file and record policy. Load it when either adapter is selected. This section is its backlink.
- `PD-004`: `references/url-skill.md` owns URL and skill policy. Load it when either adapter is selected. This section is its backlink.
- `PD-005`: `references/report-mutation.md` owns request and report fields, approval shape, apply checks, and degraded verification. Load it before producing a report or mutation plan. This section is its backlink.
- `references/decisions.md` records why these boundaries exist. Read it before changing this skill.
- `examples/` holds one worked case per command plus the common failure path. Load the matching example when output shape is unclear.

## Done

The task is done only when the requested bounded outcome passes, every retained task and adapter decision is evidenced, all authorized changes verify, unresolved items are visible, and the final logic audit finds no unsupported identity, threshold, tie-breaker, or completion claim.
