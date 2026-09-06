# Agent handoffs

An **agent handoff** transfers control across a boundary where no shared memory
survives: an orchestrator finishes a bounded phase and hands a fresh subagent or
session the work, or a conversation is compacted for a later pickup. The receiver
must reconstruct the goal, what is done, what is not, the constraints, the single
next action, the artifacts, and the open risks with **no access to the prior
transcript**. That reconstruction requirement is the cold-reader rule of the
meta-code layer (see `references/meta-code.md`) in its sharpest form.

This page is a scanned surface, not rule text. For the wording of any governed
prose rule named below, open its cited `corpus_ref` module.

## When this page applies

- **Predicate:** control passes to an actor that will not see this conversation:
  a phase-to-phase transfer, a fan-out to a subagent, or a compaction that a
  future session resumes from.

## Governing STOW families

- **Action-shaping (band 8).** The handoff opens with the result and carries
  exactly one concrete next action, restates progress so the receiver holds no
  state implicitly, and surfaces completed outcomes rather than burying them:
  see corpus/action-shaping.md#STOW-ACT-001,
  corpus/action-shaping.md#STOW-ACT-005, and
  corpus/action-shaping.md#STOW-ACT-007. The functional response-frame rule in
  `STOW-ACT-001` also excludes a preamble or synthetic sign-off.
- **Accuracy and integrity (band 5, always on).** Every `done` claim carries an
  evidence reference; a status with no evidence is fabricated specificity and is
  forbidden by the kernel integrity rules (`SKILL.md` section 3).
- **Literals (band 4).** Repository paths and commit identifiers pass through
  byte-exact.
- **Terminology (band 6).** Task and phase IDs are reused verbatim from the plan
  the handoff points at, one term per concept, per
  corpus/words/usage.md#STOW-WRD-011.

## Governing schema + template

- **Schema.** `schemas/handoff.schema.json`. Required fields include
  `handoff_id`, `from_actor`, `to_actor`, `created_ts`, `goal`, `plan_ref`,
  `done[]` (each a `{claim, evidence_ref}`), `not_done[]`, `constraints[]`,
  `next_action` (a single string), `artifacts[]`, `open_risks[]`, and
  `acceptance_for_next`.
- **Template.** `templates/HANDOFF.md`: a valid instance with those fields as
  headings and inline field hints.

## Validation contract

Validate against the schema:

```
python skills/stow/runtime/validate.py --schema handoff <file>
```

The load-bearing rules, checked as deterministic post-checks in the same mode:
`next_action` is exactly one non-empty imperative; every `done[].evidence_ref`
resolves; every task ID used under `done`/`not_done` exists in the referenced
plan; no artifact path dangles. **Cold-reader gate:** no field references
conversation state the handoff does not itself carry. Confirm this by hand after
the schema passes.
