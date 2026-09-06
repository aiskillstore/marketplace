# Cross-harness interchange

A **cross-harness interchange envelope** is a packaged file format intended for
an artifact passed to another agent runtime, CI bot, or human tool. It is a
self-describing wrapper: what kind of artifact it
carries, which schema and version validate it, its content type, an integrity
hash, and the payload inline or by reference. This page also governs the
**machine-readable event stream** (the append-only, line-oriented log of what
happened during a run) because the stream is the interchange format for runtime
history and reuses the existing JSONL contract.

The schema, template, and standalone checks establish file-level portability
only. No second live harness has been exercised, so live interchange behavior,
state continuity, and lossless transfer remain unverified.

This page is a scanned surface, not rule text. For the wording of any governed
prose rule named below, open its cited `corpus_ref` module.

## When this page applies

- **Predicate:** an artifact must cross a harness boundary and be validated by a
  receiver with no shared memory, or a run emits an event log that a monitor,
  replayer, or auditor consumes.

## Governing STOW families

- **Serialization (band 3).** The envelope and the event stream are structured
  data that must parse and validate; the event stream reuses the JSONL contract
  in `references/format-jsonl.md` (`validate.py --format jsonl`), where each
  non-empty line is one independently parseable object.
- **Contract (band 2).** The envelope declares the payload's contract, so a
  receiver knows which schema to run without asking.
- **Literals (band 4).** The integrity hash and the payload bytes are protected
  literals (see corpus/words/usage.md#STOW-WRD-014 and corpus/punctuation.md#STOW-PCT-006).
- **Terminology and versioning (band 6).** The schema id and version name a
  shipped contract exactly.

## Governing schema + template

- **Schema.** `schemas/output-contract.schema.json`. Required fields include
  `stow_version`, `artifact_type` (from the meta-code catalog), `content_type`,
  `schema_id`, `schema_version`, a `region_map[]`, and exactly one of `payload`
  or `payload_ref`. `integrity` (`{algo: "sha256", value}`) is optional but
  recommended; when present beside an inline payload, the hash must match.
- **Template.** `templates/event-stream.jsonl`: a valid JSONL instance of one
  phase: each line an event `{ts, actor, type, ...}` with a monotonic timestamp
  and a `type` from the closed core vocabulary of `schemas/event.schema.json`:
  `phase_start`, `tool_call`, `gate_pass`, `gate_fail`, `andon_raise`,
  `andon_resolve`, `decision`, `note`, `phase_done`. A harness-specific type
  uses the `x-` prefix escape; evolution is additive-only within
  `schema_version` 1.

## Validation contract

Validate the envelope against its schema, and an event stream per line:

```
python skills/stow/runtime/validate.py --schema output-contract <envelope>
python skills/stow/runtime/validate.py --schema event <event-stream>.jsonl
```

The load-bearing rules: when `integrity` is present, `sha256(payload_bytes) ==
integrity.value`; `artifact_type` is in the catalog; `schema_id` resolves to a
shipped schema, and if non-null the payload validates against it; for an event
stream, every line parses, there is no wrapping array, timestamps are monotonic
non-decreasing, and each `type` is core vocabulary or `x-` prefixed. Line
failures are reported as `line N: <reason>`. A receiver that implements the
same packaged schema can perform the same closed check without repository-local
state; that conditional file contract is not evidence of a live second harness.

## Lifecycle-ownership boundary

The executing harness owns the audit and execution lifecycle: what a gate
means, when an escalation is raised, how phases advance, when work is done.
STOW owns the representation: terminology, structure, serialization, the
schemas above, and the interchange envelope. The artifact classes map onto any
harness's lifecycle without STOW defining one: HANDOFF carries a control
transfer, PLAN carries the phase/task DAG, AUDIT carries findings with
terminal dispositions, RUNBOOK carries an executable step list, STATE carries
the durable gate/decision ledger, the task packet carries one dispatched unit
of work, and the event stream carries the append-only trace. The `x-` status
and event-type escapes exist so a harness's own lifecycle states travel intact;
STOW validates their shape and never their semantics.
