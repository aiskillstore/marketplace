---
name: adapting-rvtf-to-openspec
description: Use when applying RVTF traceability to an OpenSpec Change or OpenSpec lifecycle decision.
---

# Adapting RVTF To OpenSpec

**REQUIRED BACKGROUND:** Use tracing-requirements-to-verification.

Add an evidence-backed RVTF audit projection to one OpenSpec Change without
replacing OpenSpec's authored specifications, artifact graph, or lifecycle.

## Host Contract Snapshot

- Upstream: <https://github.com/Fission-AI/OpenSpec>
- Evaluated ref: `refs/tags/v1.9.0`
- Evaluated revision: `2826b8889e5223a9a8095d4428b60b56597e1020`
- Host authorities: `openspec status --change <name> --json` for the selected
  root, schema, artifact graph, and readiness; `openspec instructions apply
  --change <name> --json` for context files, tasks, progress, and apply state.

This adapter is compatible only with that exact contract. Re-audit it when the
tracked ref, host semantics, adapter, RVTF core, or supported scope changes.

## Principle And Authority

OpenSpec owns the authored behavioral contract and its planning/lifecycle
state. RVTF owns stable trace identity, target-specific evidence claims,
Journey path truth, gaps, review state, and evidence-backed closure. Repository,
user, CI, or the selected execution host retains authority for merge, release,
deployment, and other external actions.

Host progress is input to the trace, never proof by itself. RVTF is a
declarative audit layer: it does not invoke, select, or schedule the next host
action.

## Supported V1 Surface

Proceed only when all are true:

- one repo-local OpenSpec root is selected;
- one named active or archived Change is in scope;
- the Change uses the built-in `spec-driven` schema; and
- execution uses OpenSpec standalone or exactly one split-host authority.

Store, custom schema, cross-root or cross-repository planning, bulk archive, and
a native OpenSpec integration pack are unsupported in v1. Report the
unsupported capability and stop the formal RVTF workflow. Do not reinterpret a
custom artifact graph as `spec-driven` and do not silently fall back from a
Store to a repo-local root.

`explore` and `onboard` remain discovery/learning. `propose`, `new`, `continue`,
and `ff` create planning artifacts. None creates implementation evidence or
RVTF closure.

## Change-Local Sidecar

Use exactly:

```text
openspec/changes/<change-name>/rvtf.yaml
```

Create and validate this sidecar before implementation for `lite`, `standard`,
or `strict` work. It moves with an archived Change; stable ID values do not
depend on its path.

OpenSpec remains authored truth. For every projected Requirement and Acceptance
Item, record its stable ID, snapshot text, source path relative to the sidecar,
heading lineage or anchor, and the complete source file's SHA-256 digest in
`source_ref.revision`.

On a digest mismatch, reject the old projection as closure input, reread the
source, record the affected gap, reconcile whether each stable ID survives a
rename or instead needs split/merge/replacement/amendment treatment, update
affected mappings and evidence validity, then rerun the relevant gates. Preserve
unaffected evidence only through an explicit validity assessment.

Before the first implementation action require planning apply-readiness,
`rvtf.yaml`, Requirement/Item records, Journey applicability, task mappings,
`rvtf validate`, and the applicable RVTF Design and Plan Gates.

## Artifact And Scenario Mapping

- Map every required OpenSpec Requirement to one stable RVTF Requirement. A
  title rename preserves the stable ID when semantic identity continues.
- Give every required OpenSpec Scenario disposition: map it to one or more
  canonical Acceptance Items; combine it with named Scenarios for one Item;
  use it as named precondition, alternative, failure, or recovery context; or
  reject it through a recorded validity/scope decision. Never ignore it.
- A Scenario is not automatically a Journey. Decide Journey applicability from
  an actor, goal, and observable multi-step path whose order, connection,
  boundary, recovery, or outcome needs evidence. Journeys reference canonical
  Item IDs rather than copying Item state. Record a rationale when not required.
- When a Scenario or Requirement yields a human decision Step, map an
  actor-facing decision verifier to its Acceptance Item and owning task. Keep
  machine binding through a stable token, but treat an opaque ID or fixture-only
  lookup as protocol evidence rather than proof of human judgment.
- One evidence artifact may support several targets only through separate
  target-specific claims. Item criterion evidence and Journey path/outcome
  evidence remain independent.

Every required OpenSpec task carries all applicable mappings, including empty
Journey lists when Journey Trace is not required:

```yaml
requirement_ids: []
acceptance_item_ids: []
journey_ids: []
journey_step_ids: []
```

Task checkbox state changes task progress only. `skip_specs: true` means there
is no OpenSpec spec-level behavioral delta; it does not prove RVTF has no
Requirements. Inventory relevant refactor, documentation, migration,
compatibility, operational, non-functional, and accepted amendment constraints.

For detailed Scenario disposition pressure cases, read
`references/pressure-scenarios.md`.

## Standalone And Split-Host Rules

Record one execution lifecycle authority.

- In `standalone`, OpenSpec tasks and apply state own execution progress.
- In `split-host`, OpenSpec owns authored artifacts while one selected method
  and its RVTF adapter own task, review, branch/phase, and continuation state.
  OpenSpec tasks may remain mapped planning checkpoints but cannot override the
  selected host.

Represent the choice with exactly one `host_trace_mappings` entry whose
`host_kind` is `execution-authority` and whose `host_ref` resolves to the
OpenSpec Change or selected host object. Stop on missing or dual authority.

Effective gates are the union of OpenSpec mandatory gates, selected-host
mandatory gates, and RVTF-required gates. Reuse cannot subtract a mandatory
gate or fabricate current-test status.

## Planning, Apply, Verify, Sync, And Archive Mapping

| OpenSpec state/action | RVTF treatment |
| --- | --- |
| Planning artifact done | Planning readiness only; no target status promotion. |
| `apply` or checked task progress | May advance mapped work to `implemented`; does not produce `verified`. |
| `/opsx:verify` | Optional candidate evidence and finding input, not a core profile gate or closure decision. |
| `sync` | Updates authored current specs; does not produce `verified`. Reconcile affected source bindings. |
| `archive` | Records `host_status: archived` and moves history; does not produce `verified` or alter the prior RVTF disposition. |

Any `/opsx:verify` result needs exact targets, non-empty `proves`, subject and
verifier revisions, coverage, quality, freshness, and normal-gate assessment.
An all-clear report cannot blanket-verify an Item or Journey.

## Formal Completion Preflight

Run in this order:

1. Confirm source Change, repo-local root, and built-in schema remain supported.
2. Recompute every source-file SHA-256 digest and reconcile mismatches.
3. Run `openspec validate <name> --strict --json` successfully.
4. Run every selected implementation-host mandatory gate.
5. Audit target-specific evidence claims and validity.
6. Audit Acceptance Item and Requirement aggregation.
7. Audit Journey applicability, Steps, path evidence, and expected outcome.
8. Audit findings, gaps, amendments, review closure, and residual risks.
9. Produce the Closure Packet with actual host status and disposition.
10. Run `rvtf validate openspec/changes/<name>/rvtf.yaml` successfully.

The CLI must resolve on `PATH`; `rvtf --version` must succeed and support the
sidecar schema. Exit `1` is a semantic validation failure. Exit `2` is an
operational failure. A missing CLI or either nonzero exit is an unsatisfied
gate; manual reading is not a validator pass.

## Failure Handling

| Condition | Required decision |
| --- | --- |
| Source digest mismatch | Reject the projection for closure, assess impact, and reconcile. |
| OpenSpec strict validation fails | Preserve the host failure and reject closure. |
| Unsupported Store/schema/root/bulk/native-integration surface | Name the capability and stop without guessing. |
| Tasks done but target evidence missing | Preserve task progress; keep affected targets `implemented`. |
| Journey path proof missing | Keep the Journey `implemented` without downgrading valid Item evidence. |
| CLI missing or operationally broken | Record the gate gap and owner; do not substitute manual inspection. |
| Execution authority ambiguous | Stop until one authority is selected. |
| Early archive | Preserve `archived` host state and the prior RVTF disposition. |
| New untraced work | Classify and map it or obtain an amendment before implementation. |

## Completion Rule

OpenSpec readiness, task progress, verify output, sync, and archive remain
distinct from RVTF closure. Claim `complete` only after every required
Requirement, canonical Acceptance Item, applicable Journey, host gate, source
binding, review decision, gap disposition, Closure Packet field, and final CLI
validation supports it. Otherwise state the strongest supported status, exact
gap, owner, and close condition.
