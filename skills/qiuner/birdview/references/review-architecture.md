# Review architecture on request

[中文](review-architecture.zh.md)

Use only when Birdview is active and the user asks for architecture evaluation or refactoring opportunities. Start from the verified map in [Stage 1](map-project.md); review the requested scope, not the entire repository by default.

## Inspect responsibilities

Read relevant project terminology and architecture decisions when available; missing glossaries or ADRs do not require creating them. Trace the callers and implementations behind candidate modules. Look for concrete friction:

- One responsibility requires coordinated edits across several modules, or callers must know internal ordering, error handling or configuration details.
- A wrapper adds little behavior while forcing callers through another interface. Ask what happens if it is removed: does complexity disappear or move into its callers? A small adapter can still justify its existence.
- Existing boundaries make important behavior difficult to verify through public interfaces. Describe the behavior at risk, rather than demanding tests for every implementation detail.

Prefer changes that give callers a simpler interface while keeping cohesive behavior together. Module count, file size and diagram neatness alone are not evidence of a problem. Respect existing architecture decisions; suggest revisiting one only with concrete new evidence and state the conflict.

## Present grounded candidates

Return only supported candidates, ordered by expected value. For each, provide:

- Existing module IDs and source paths/symbols, observed friction and its practical impact.
- Proposed responsibility or dependency changes, expected benefit, migration cost and risks, including reasons to retain the current design.
- A behavior-level verification plan and confidence: strong evidence, worth investigating, or speculative. Identify missing evidence; do not present hypotheses as defects.

Use the existing Birdview preview to locate affected modules and explain candidates alongside it. Keep the canonical map factual: do not replace current relationships with proposals, invent activity records or treat the comparison view as a before/after architecture diff. Describe proposed structure in the accompanying explanation; no separate report framework or schema extensions are needed.

Recommend a first candidate only when the evidence supports one; finding no justified refactor is a valid result. Resolve source-answerable questions before asking about material product or design choices, and include a recommendation with its tradeoff. Review alone does not authorize implementation. Once implementation is authorized, follow [Stage 2](show-changes.md) using the current map and declared scope; do not ask again for authorization already given.
