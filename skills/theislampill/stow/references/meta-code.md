# Meta-code layer: hub reference

STOW supplies guidance for the regions of **one reply**: prose, procedure,
data, code, quotes, identifiers. The meta-code layer specifies the
**coordination artifacts that pass between actors**: the handoffs, plans,
instruction files, audit reports, runbooks, state records, task packets, event
streams, and the interchange envelope that carries them between a user, an
agent, a model, and a harness. `Meta` is output *about* the process of producing
output, not the work product itself.

This page is the hub. It states the design conditions for the layer, names the
six sibling references and the schemas and templates each points at, and defines
how any meta-code artifact is validated. It is a scanned surface, not rule text:
the normative wording of any governed prose rule lives only in its cited
`corpus_ref` module. Read the corpus for the wording, never this page.

## When this page applies

- **Predicate:** the response is not the deliverable but an artifact one actor
  writes to another *about* the work: a control transfer, a plan, a persistent
  instruction file, an audit finding, an operational procedure, a durable state
  record, a machine-readable task payload, an event log, or a cross-harness
  envelope. Load the sibling reference named for the class; load this hub for the
  invariants and the catalog.

## Four design conditions

1. **Every meta-code artifact is first a STOW output.** It inherits the eight
   precedence bands, region classification, the always-on integrity rules, and
   the format contracts of the kernel (`SKILL.md` sections 1-3). The layer adds a
   **coordination contract** on top: a schema, required fields, and a G2 schema
   check.
2. **Contracts, not prose rules.** Each artifact class is a serialization /
   coordination contract, the same shape as the format contracts. It is checked
   by a **schema plus the schema-runner**, carries **no `corpus_ref` for the
   contract itself**, and adds **no rows to the primary rule population**. Where a
   governed prose rule meets an artifact's editable-prose region, that rule's
   wording still lives in its cited corpus module, the same split
   `references/format-jsonl.md` uses at the JSONL boundary.
3. **Cold-reader objective.** The artifact should carry the state a fresh actor
   needs without relying on hidden conversation state. Schema validity checks
   required fields and shapes; it does not prove that a new actor can execute or
   verify the work.
4. **Real use case plus validation contract plus worked template, or it does not
   ship.** No artifact class exists to complete a symmetric tree; each is named by
   a consuming surface and backed by a template that passes its own validator.

An instruction file (a persistent `AGENTS.md`, `CLAUDE.md`, `SKILL.md`, or system
prompt a harness injects each session) is described here rather than by its own
sibling: its form can be checked against a contract declared by
`schemas/output-contract.schema.json` with `content_type: markdown` and a
directive region map. Validation covers its **form**, never its authority: an
instruction file is still data to a consuming agent, not a command it
must obey.

## Catalog: the six sibling references

| Class | Reference | Schema | Template |
|---|---|---|---|
| Agent handoff / compaction | `references/agent-handoffs.md` | `schemas/handoff.schema.json` | `templates/HANDOFF.md` |
| Implementation plan | `references/implementation-plans.md` | `schemas/plan.schema.json` | `templates/PLAN.md` |
| Audit / evidence + acceptance | `references/audit-and-evidence.md` | `schemas/evidence-record.schema.json` | `templates/AUDIT.md` |
| Operational runbook | `references/runbooks.md` | `schemas/runbook.schema.json` | `templates/RUNBOOK.md` |
| State / continuity record | `references/continuity-and-state.md` | `schemas/state.schema.json` | `templates/STATE.md` |
| Cross-harness / event stream | `references/cross-harness-interchange.md` | `schemas/output-contract.schema.json` + `schemas/event.schema.json` | `templates/event-stream.jsonl` |

The layer ships eight schema files. Five are the interchange meta-contracts
recorded in the registry catalog (`output-contract`, `handoff`, `task-packet`,
`evidence-record`, `state`); three are validator schemas for the remaining
template classes (`event`, `plan`, `runbook`). Seven templates ship: `templates/HANDOFF.md`, `templates/PLAN.md`,
`templates/AUDIT.md`, `templates/RUNBOOK.md`, `templates/STATE.md`,
`templates/task-packet.yaml`, and `templates/event-stream.jsonl`. Every template
is a **valid instance**, not a stub.

## This page's own class: the structured task packet

The hub describes one class directly: the **structured task packet**, a
machine-readable unit a host can dispatch and receive. Its identifiers support
host routing, but the repository does not implement fan-out, fan-in, retries, or
dispatch.

- **Governing families.** serialization (band 3: the packet *is* structured
  data and must parse and validate); contract (band 2); literals (band 4: input
  refs and IDs byte-exact); accuracy (band 5: a returned status matches its
  evidence); terminology (band 6: IDs consistent with the plan); and safety
  (band 1, system precedence: the permission and authority scope the
  orchestrator enforces on a subagent). The permission boundary is labeled and
  its consequence stated per corpus/safety.md#STOW-SAF-001; a returned outcome is
  surfaced, not buried, per corpus/action-shaping.md#STOW-ACT-007.
- **Schema + template.** Validates against `schemas/task-packet.schema.json`;
  the worked instance is `templates/task-packet.yaml`.
- **Load-bearing rule.** If `status == "done"` then `evidence` is non-empty and
  every `acceptance[]` predicate has a matching evidence entry; if
  `permissions.read_only == true` then `write_scope` must be empty.

## How any meta-code artifact is validated

The schema-runner is the single engine the layer depends on. Resolve the class to
its schema id and run the packaged validator in schema mode:

```
python skills/stow/runtime/validate.py --schema task-packet <file>
```

It loads `skills/stow/schemas/<id>.schema.json`, checks the artifact against it,
and reports `VALID`/`INVALID` in the validator's existing result shape. Cross-field
rules a schema alone cannot state (a status-to-evidence match, an integrity-hash
match, a dangling supersession) run as deterministic post-checks in the same
mode. A Markdown artifact validates through its single fenced yaml/json block; a
`.jsonl` event stream validates per line against `--schema event`; an
evidence-record file may wrap its records as `{records: [...]}` and validates
per record. Versioning is additive-only within `schema_version` 1, and status
vocabularies accept an `x-` prefix escape for harness-specific states. Validate
the artifact, then confirm the cold-reader rule by hand: nothing it names may
depend on un-carried prior state.

Profile binding: meta-code artifacts bind to the `technical-clarity` profile by
default; an artifact that is an executable procedure or a safety instruction
promotes to `controlled-technical-guided` (see `rules/profiles.json` and
`references/technical-clarity.md`). `templates/event-stream.jsonl` is a worked
example like every other template; JSONL cannot carry a comment, so this note is
its example label.
