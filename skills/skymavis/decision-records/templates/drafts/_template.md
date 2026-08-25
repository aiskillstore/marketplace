---
# Draft — a decision candidate (WIP). Same shape as a decision record, so promotion is
# mechanical; it just carries a 4-letter ID and status: draft, and lives in drafts/.
# Filename:  AAAA-kebab-title.md  (AAAA = the 4 UPPERCASE letters of `id` below).
# Promotion, linking, and validation are the decision-records skill's job.
id: ABCD                          # REQUIRED: 4 UPPERCASE letters, a mnemonic of the topic
title: Short imperative title
type: architecture                # a lowercase slug = the directory it lands in on promotion
status: draft                     # draft | under-review
date: YYYY-MM-DD
deciders: [trung]
summary: One sentence describing the decision.
tags: []                          # e.g. [access-control, retrieval, orchestrator]
relates_to: []                    # related record IDs — counters and/or draft IDs
supersedes:                       # a decision this replaces, or blank
superseded_by:                    # ID that replaces this, or blank
---

# {id} — {title}

## Context

What forces are at play? What problem or tension prompts this decision? State the constraints as
they actually are. Don't sanitize.

## Decision

The proposed decision in one or two sentences, active voice ("We will …"). Binding once promoted and
`accepted` — course changes only by supersession.

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

- Threads, specs, external sources, and related records by ID (e.g. `0001`, `TIER`).
