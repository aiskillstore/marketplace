# Continuity and state records

A **state / continuity record** is the durable, externalized state of a
long-running, multi-session effort: the gate ledger, the decision log, the phase
history that lets any later session resume without re-deriving what already
happened. It is the meta-code layer's answer to holding state silently in a
conversation: the state lives in the artifact, so a fresh session picks it up cold
(see the cold-reader rule in `references/meta-code.md`).

This page is a scanned surface, not rule text. For the wording of any governed
prose rule named below, open its cited `corpus_ref` module.

## When this page applies

- **Predicate:** a multi-session or multi-phase effort needs its progress, gate
  states, decisions, and next action recorded so any actor can resume from the
  record rather than from memory.

## Governing STOW families

- **Action-shaping (band 8).** The record externalizes material changed state
  rather than implying it, and surfaces completed outcomes. Do not repeat the
  full ledger when no material state changed (see
  corpus/action-shaping.md#STOW-ACT-005 and corpus/action-shaping.md#STOW-ACT-007).
- **Accuracy (band 5, always on).** Every gate or phase state cites evidence and
  is a terminal value, not a vague status; the kernel integrity rules forbid an
  unsupported state claim (`SKILL.md` section 3).
- **Terminology (band 6).** Gate and phase IDs are stable across sessions, one
  term per concept, per corpus/words/usage.md#STOW-WRD-011.
- **Literals (band 4).** Commit identifiers and paths are byte-exact.

## Governing schema + template

- **Schema.** `schemas/state.schema.json`. Required fields include `run_id`,
  `updated_ts`, `current` (a `{head, phase, next_action}`), `gates[]` (each a
  `{id, status}` with an `evidence_ref` string), `decisions[]` (each with an
  `id`, a `status`, and optional `supersedes[]` / `superseded_by` links), and a
  `history_append_only` flag; `andons[]` is optional. Status vocabularies are
  closed cores with an `x-` prefix escape for harness-specific states.
- **Template.** `templates/STATE.md`: a valid instance carrying a gate ledger, a
  decision list with supersession links, and a current-state block.

## Validation contract

Validate against the schema:

```
python skills/stow/runtime/validate.py --schema state <file>
```

The load-bearing rules: every `supersedes` / `superseded_by` id resolves to an
existing decision (no dangling supersession); every gate state is in the closed
enum; every decision id is unique; `current.next_action` is present unless every
gate is terminal. **Cold-reader gate:** a new session can determine the current
head, phase, and next action from the record alone.
