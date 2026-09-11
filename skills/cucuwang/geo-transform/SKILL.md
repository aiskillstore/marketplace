---
name: geo-transform
description: Use when proposing evidence-bounded readability and structure edits without inventing content, ranking claims, or structured data
---

# GEO Transform — Evidence-Bounded Content Restructuring

Propose focused edits while preserving meaning, voice, provenance, and recoverability.

## Workflow

1. Read one authorized file and run the deterministic scan.
2. Classify each finding as an official requirement, deterministic check, heuristic, or experiment.
3. Show a focused diff before changing the file.
4. Change only what improves readability, factual provenance, or a documented technical requirement.
5. Rerun the same scan and report the reproducible output change separately from any external outcome.

## Allowed transformations

- Split a long paragraph where comprehension improves.
- Repair a genuinely confusing document outline; multiple H1 elements are not automatically wrong.
- Cite or remove unsupported quantitative claims.
- Reduce repetitive wording without changing meaning.
- Propose structured data only when it matches visible content and current documentation.
- Clarify genuine reader questions without auto-generating FAQ schema.

## Boundaries

- Never invent facts, statistics, sources, quotes, authors, dates, or benefits.
- Never describe a score increase as evidence of ranking, indexing, rich results, or citation.
- Never batch-transform files without explicit scope.
- Preserve a reviewable diff and the user's original voice.
