---
name: decision-doc-sync
description: "Trigger: architecture change, new convention, UI/UX standard, quality gate change, ADR. Keep existing project docs in sync with structural decisions."
license: Apache-2.0
metadata:
  author: purrfold
  version: "1.0"
---

# Decision Documentation Sync

## Activation Contract

Load this skill when a change introduces or changes a structural decision: architecture, UI/UX standards, scripts or quality gates, or a cross-cutting convention.

## Hard Rules

1. Check which documents exist before editing; update only documents that exist, and create one only when a rule below requires it.
2. Keep each fact in one document and link to it from others instead of duplicating it.
3. Record the decision itself, not the change history.
4. Never leave a document contradicting the code after the change.

## Decision Gates

| Change type | Document |
| --- | --- |
| Architecture, folder structure, scripts | `README.md` |
| Visual or UX standard, tokens, component usage | `DESIGN.md` |
| Agent workflow, commands, operational guidance | `AGENTS.md` |
| Durable decision with alternatives and consequences | new record in `docs/adr/` |

## Execution Steps

1. Check which of `README.md`, `DESIGN.md`, `AGENTS.md`, and `docs/adr/` exist.
2. Classify the change with the table above; one change may hit several rows.
3. Update each affected document that exists.
4. For an ADR, follow the existing numbering and format in `docs/adr/`; see [references/doc-map.md](references/doc-map.md).
5. Reread the edited sections against the code.

## Output Contract

List every document updated, created, or deliberately skipped, with a one-line reason each.

## References

- [references/doc-map.md](references/doc-map.md) — ADR format and edge cases.
