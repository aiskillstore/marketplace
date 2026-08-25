---
# Decision record — front-matter is machine-readable; keep it accurate.
# Filename:  NNNN-kebab-title.md  (the counter, then a kebab title — no type in the name).
# Identity   = the counter `id` below: permanent, the only thing cross-references use.
# Authoring, promotion, linking, and validation are the decision-records skill's job —
# this template is just the record's shape.
id: "0000"                        # global counter, quoted to keep the zero-pad
title: Short imperative title
type: architecture                # a lowercase slug = the directory this record lives in
status: accepted                  # accepted | deprecated | superseded
date: YYYY-MM-DD
deciders: [trung]
summary: One sentence describing the decision.
tags: []                          # e.g. [access-control, retrieval, orchestrator]
relates_to: []                    # related record IDs, e.g. ["0001", "0003"]
supersedes:                       # ID this replaces, or blank
superseded_by:                    # ID that replaces this, or blank
---

# {id} — {title}

## Context

What forces are at play? What problem or tension prompted this decision? State the constraints as
they actually were at decision time. Don't sanitize.

## Decision

The decision in one or two sentences, active voice ("We will …"). Binding once `accepted` — course
changes only by supersession.

## Rationale

Why this option over the others, given the context above.

## Alternatives considered

| Option | Why not |
| :----- | :------ |
| …      | …       |

## Consequences

**Positive**

- …

**Negative / accepted costs**

- …

**Risks & open questions**

- …

## References

- Threads, specs, external sources, and related records by ID (e.g. `0001`).
