# Core deduplication contract

Owner: `dedupe`. Load for every `inspect` command or `apply` request. Backlink: `SKILL.md` PD-001.

## Outcome frame

Use `starting-point` to record:

- intended canonical collection or report
- bounded source and stable item unit
- user authority and destination
- required proof
- unknowns that could change identity or mutation
- forbidden loss, writes, recursion, or disclosure

Use `outcome-bounded-work` to drop recipe steps that protect no invariant. Never drop identity, scope, authority, conflict, provenance, rollback, or verification gates.

## Pipeline

1. **Preflight:** Fix scope, adapter, identity class, policy, canonical rule, and proof.
2. **Enumerate:** Assign stable indices and source provenance without changing input.
3. **Extract:** Produce exact and, when requested, normalized comparison keys.
4. **Compare:** Group equal keys. Produce pairwise scores for similarity requests.
5. **Select:** Apply the declared canonical rule within each group.
6. **Resolve:** Preserve conflicts and unique information in a merge ledger.
7. **Report:** Emit counts, maps, policies, evidence, and unresolved items.
8. **Plan:** Turn reviewed groups into explicit actions with a plan digest.
9. **Authorize:** Require authority for the exact plan and destination.
10. **Apply:** Execute only listed actions with one writer.
11. **Verify:** Re-enumerate, reconcile, compare evidence, and rerun.

## Identity classes

### Exact identity

Use an unambiguous representation:

- text or scalar value with type preserved
- file byte hash
- record canonical JSON or declared key tuple
- literal URL value
- ordered list member representation
- skill packet hash including relative paths and bytes

A digest proves equality only for the bytes or representation hashed. It does not prove ownership, authority, freshness, meaning, or safe deletion.

### Normalized equality

Record every transformation in order. Common transformations include Unicode normalization, case folding, whitespace handling, selected record fields, URL component rules, and text decoding.

Do not hide lossy transformations. Punctuation removal, diacritic removal, stemming, redirect resolution, format conversion, field omission, and timestamp truncation require explicit policy.

### Similarity candidate

Name the algorithm, version or implementation, input representation, threshold, score direction, and pair. Keep candidates separate from equality groups.

Treat similarity as pairwise unless the algorithm supplies a proven grouping rule. Do not infer transitivity.

## Canonical selection

Declare one deterministic selector and its tie-breakers. Supported policies include:

- first or last in meaningful source order
- authoritative source
- highest completeness score with disclosed fields
- newest or oldest by a named timestamp
- preferred path, domain, owner, or version
- explicit user selection

Use `always-current-datetime` when a newest, oldest, freshness, or age decision depends on runtime time. Record the anchor and timezone. Do not use file modification time or skill version as authority without a declared rule.

## Conflict policy

A matching identity key can coexist with conflicting non-key content. Record:

- conflicting field or passage
- values and their provenance
- canonical value rule, if approved
- values retained elsewhere
- unresolved status

Never erase conflict evidence to make a group look clean. Missing and null are distinct unless the schema says otherwise.

## Logic audit

Use `logic-audit` at these gates:

- after identity and normalization are proposed
- before a similarity threshold is accepted
- after canonical tie-breakers are selected
- before mutation authority is used
- after verification, before claiming completion

Audit assumptions, unsupported equivalences, threshold sensitivity, non-transitive chains, stale inputs, split provenance, count equations, empty inputs, malformed items, link behavior, and rollback claims.

## Count proof

For inspection:

```text
source_count = canonical_count + duplicate_count + unresolved_count
```

Here `duplicate_count` counts non-canonical members in strict equality groups. Similarity candidates do not affect this equation.

For apply, also reconcile:

```text
planned_actions = applied_actions + skipped_actions + failed_actions
```

Every applied action must reference a report group, canonical item, approval scope, and post-action proof.

## Forbidden outcomes

- silent deletion or overwrite
- invented identity or merge rules
- treating similarity as identity
- expanding into unrelated paths, repositories, records, URLs, lists, or skills
- network redirect lookup without network authority
- exposing raw sensitive comparison values when a digest or index suffices
- trusting stale reports after source drift
- claiming completion with unresolved conflicts or failed verification
