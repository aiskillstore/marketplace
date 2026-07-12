# Consolidation Pass

Consolidation reconciles non-canonical working notes. It cannot mutate registry truth, accept proposals, or clear event history.

## Procedure

1. Freeze scope and obtain write permission for any proposed changes.
2. Load HOT pointers, their WARM/COLD targets, approved decisions, and relevant registry projection offsets.
3. Group comparable notes by unit, field, window, denominator, source meaning, and authority.
4. Deduplicate exact semantic duplicates while retaining the strongest source pointer.
5. Supersede an older note only when newer evidence is comparable and equal/higher authority; annotate `superseded_by` rather than silently deleting.
6. Preserve genuine conflicts in open loops. For registry-owned truth, submit an authorized proposal with current revision.
7. Distill a conclusion to HOT only when the user explicitly pins it; detail remains in WARM.
8. Archive by age/retention policy and report every changed path.

## Structural Checks

- HOT pointer without a source artifact or accepted registry record;
- broken Markdown links or nonexistent memory paths;
- orphan WARM artifacts that still matter but have no index/reference;
- audit summaries missing framework/profile/version/target/window;
- projections or human views whose offset/revision no longer matches replay;
- unresolved claim or consent references used as if approved.

## Guardrails

- Never edit `memory/events/*.ndjson` or `memory/projections/*.json` manually.
- Never let recency override a higher-authority or differently scoped fact.
- Never overwrite a user-approved decision; surface the conflict.
- Never hard-delete for tidiness. Destructive erasure follows the explicit privacy flow.
- Never copy a score into a new aggregate after stripping its profile/version/context.

The output is a diff summary: deduplicated notes, explicit supersessions, archived artifacts, proposals submitted, unresolved conflicts, broken links, and exact paths/event IDs.
