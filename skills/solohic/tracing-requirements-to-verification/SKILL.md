---
name: tracing-requirements-to-verification
description: Use when work has multiple requirements, phases, acceptance criteria, implementation tasks, verification evidence, review findings, review governance, scope changes, delivery gaps, residual risks, or claims of completion that need traceable delivery decisions.
---

# Tracing Requirements To Verification

## Overview

Use Requirements-to-Verification Traceability Framework (RVTF) to keep delivery work anchored from intent to evidence and delivery decision. Requirement Trace proves each criterion; Journey Trace, when applicable, proves that an actor can traverse the required path and reach the expected outcome. Completion means every required Requirement, canonical Acceptance Item, applicable Journey, review finding, and meaningful gap has an explicit evidence-backed decision.

When review can block closure or expand scope, use bounded review governance to
make applicability, coverage, remediation scope, and reopen decisions explicit.
Review governance controls review intake; it never replaces requirement truth or
the final Completion Gate.

## Core Rule

Never let "implemented" mean only "code exists" or "tests pass." Each Requirement must trace through canonical Acceptance Items to implementation work, item evidence, and gap decisions. When acceptance depends on ordered or causally connected observable steps, also require a Journey Trace with path and outcome evidence.

```
No review finding becomes implementation work until it is classified and linked
to a requirement decision.
```

If a finding cannot be linked to an existing requirement, accepted amendment, or existing cross-cutting constraint, it is not automatic scope. Record the decision before doing the work.

## Usage Modes

Choose the lightest mode that controls delivery risk:

| Mode | Use when | Minimum artifact |
| --- | --- | --- |
| `discovery` | Exploring or prototyping without a completion claim. | Assumptions, candidate requirements and Journeys, known unknowns. |
| `lite` | Small bounded change with low risk. | Requirement and Acceptance Item IDs, evidence notes, gap decisions, plus a Journey applicability decision when a path trigger exists. |
| `standard` | Multi-step delivery, phase work, review, or handoff. | Requirement Trace, explicit Journey applicability, Journey Trace when required, review applicability, gap ledger, closure packet. |
| `strict` | Security, privacy, migrations, compatibility, money, production risk, or cross-agent execution. | Standard artifacts plus bounded review governance, independent review evidence, evidence quality, and scope amendment records. |

Do not lower the mode to justify unsupported completion. If review discovers safety, privacy, compliance, data-loss, compatibility, or regression risk, move at least that concern through `strict` handling.

## Workflow

1. Select a usage mode.
2. Build a capability tree for the requested scope.
3. Assign stable requirement IDs to every required behavior, constraint, migration, compatibility promise, documentation change, and non-functional requirement.
4. Mark cross-cutting constraints explicitly when they apply across multiple capabilities.
5. Convert each acceptance criterion into one canonical Acceptance Item nested under exactly one Requirement. Give it a stable delivery-scope ID, source provenance, verification method, status, item evidence, and gap references.
6. Decide Journey applicability. Build a Journey Trace when an actor must traverse ordered or causally connected observable steps to reach an acceptance outcome; otherwise record a justified `not_required` decision when the mode requires it.
7. When Journey Trace applies, define actor, goal, expected outcome, ordered Journey Steps, Acceptance Item references, path evidence, status, and gap references.
8. Map host implementation tasks, stories, phases, or increments to the Requirement, Acceptance Item, Journey, and Journey Step IDs they cover.
9. Decide whether review governance applies. If it does, record a review contract, epoch, batches, freeze, remediation cycles, closure, and controlled reopens as needed.
10. During execution and review, classify every gap or finding before turning it into work.
11. Update Acceptance Item, Requirement, and Journey status from target-specific evidence quality, not from worker reports or parent-task completion.
12. Before completion, produce a closure packet listing Requirement, Acceptance Item, and Journey dispositions; accepted amendments; review closure; residual risk; gaps; and next-phase entry conditions.

## Artifact Chain

Use this chain for every non-trivial delivery unit:

```text
Capability tree
  -> requirement IDs
    -> canonical acceptance items
      -> verification methods
        -> journey applicability and Journey Trace when required
          -> host implementation tasks
            -> item evidence and path evidence
              -> review governance artifacts when applicable
                -> review findings
                  -> gap ledger
                    -> closure decision
```

Read `references/schema.md` when creating or reviewing concrete RVTF artifacts.
Read `references/gates.md` when running design, plan, implementation, review, or completion gates.
Read `references/review-governance.md` when review applicability, review contracts, batches, freeze, remediation review, late findings, or reopen decisions matter.
Read `references/pressure-scenarios.md` when creating or updating this skill, or when forward-testing whether an agent actually follows RVTF.
When a user explicitly asks to inspect a trace visually, read
`references/visualization.md` for the optional local-view workflow. Do not start
it merely because a trace exists or ordinary progress can be explained in
conversation.

## Operational Economy Plane

Use the Operational Economy Plane to organize delivery scope, shared proof,
validity, verification and review cadence, and continuation. It may reduce
duplicate execution, but it never changes Requirement, Acceptance Item,
Journey, review, gap, or closure truth. Host-native lifecycle authority also
remains intact.

Apply this rule at every lifecycle boundary:

```text
effective gates = host-native mandatory gates ∪ RVTF-required gates
```

The stronger freshness, full-suite, or reviewer requirement wins, including
specialist and independence constraints. Economy policy cannot waive a
mandatory host or RVTF gate.
Read `references/schema.md`, `references/gates.md`, and
`references/review-governance.md` for the detailed fields and gate algorithms.

### Delivery Scopes And Groups

Use `goal`, `milestone`, and `unit` as containment-based delivery closure
scopes. Keep `execution_batch`, `verification_batch`, and `review_batch` as
orthogonal groups; a group organizes work but never becomes a closure parent or
proves a member complete.

For every parent with required children, aggregate only from the authoritative,
versioned `required_child_inventory_revision` and
`required_child_scope_refs`. Each child records `required_for_parent` and its
RVTF `disposition`; keep host lifecycle values such as
`done|archived|shipped|override` separately in `host_status`.

- A required `blocked` or incomplete child cannot support parent completion.
- Only child dispositions `complete`, `complete_with_deferred_gaps`,
  `complete_with_residual_risk`, or a recorded accepted scope amendment that
  explicitly removes that child followed by a new authoritative
  `required_child_inventory_revision` may participate in parent closure. Owner
  acceptance without the amendment is insufficient.
- Propagate child deferred-gap or residual-risk truth to the corresponding
  parent disposition; never aggregate it silently to plain `complete`.
- Closing a Unit never implies that its Milestone or Goal is complete.

### Goal Continuation Contract

For a new Operational Economy closure packet declaring
`schema_version: "0.4.0"` whose current scope ends below a known parent, record
a Goal Continuation Contract with
`parent_scope_ref`, `parent_disposition`, `continuation_mode`
(`durable_host|artifact_only|advisory`), `authority_ref`, `resume_locator`,
`remaining_scope_refs`, next entry conditions, and the actual
`execution_action` (`continue|stop|await_owner|host_boundary`). Record
`stop_basis` only when the current execution actually ends through `stop` or an
explicit `host_boundary`; omit it for actions that do not stop at that point.
Legacy `schema_version: "0.3.0"` closure packets remain valid without a
continuation record.

Apply mode-specific authority and locator rules: `durable_host` requires a
resolvable `authority_ref` and `resume_locator`; `artifact_only` locates the
durable continuation artifact and names its responsible authority without
claiming a scheduler; `advisory` names the controlling user or orchestrator and
uses an explicit unknown locator when none exists. New `schema_version: "0.4.0"`
detached or `lite` work with an unknown parent must still record advisory
continuation with
`parent_scope_ref: unknown` and `parent_disposition: unknown`; it must not
invent parent closure. RVTF records continuation and ownership; it never
schedules or invokes the next host workflow, bypasses a host boundary, or
overrides user or orchestrator authority.

If an iteration changes no implementation, Evidence Claim, review finding,
gap, or disposition, emit a non-blocking operational-economy warning. Select a
new unblocked scope, record why repetition can produce new evidence, or record
the blocker with owner and entry condition; do not auto-launch another
iteration or infer completion from elapsed time or iteration count.

### Evidence Artifacts, Claims, And Validity

Separate the reusable Evidence Artifact from each target-specific Evidence
Claim. One artifact may support many claims, but every claim names its target,
states `proves`, records coverage when applicable, and has independent
validity. An artifact failure invalidates its dependent claims unless the
receipt explicitly partitions and preserves unaffected claims. An Item claim
never implies a Journey path claim. Supported legacy inline evidence remains
valid only when it carries the same target-specific artifact and claim
semantics; do not require a destructive representation migration.

Use `valid|stale|invalidated|unknown` for
`evidence_claims[].validity.status`; these are not trace object statuses. For
cross-revision reuse in `standard` or `strict`, record an auditable assessment
containing the claim, from/to revision, policy, assessor,
target/verifier/dependency/environment/freshness comparison basis, rationale,
and decision. Opaque fingerprints alone are insufficient. A `lite` manual
rationale must identify what was compared for the target criterion or outcome,
verifier, relevant dependency inputs, environment, and freshness. If any
material aspect cannot be assessed, set
`evidence_claims[].validity.status: unknown` and run the targeted gate.

A Git revision change triggers assessment, not global invalidation. Invalidate
or downgrade only affected claims and the trace objects that depend on them;
preserve independent Item, Requirement, and Journey truth.

Keep these three records distinct:

- `evidence_claims[].validity.status`: whether target-specific proof remains reusable;
- `host_gate_status`: whether the effective current-boundary gate ran and met
  its contract;
- `current_test_status_claim`: what may truthfully be said about current tests.

A reusable valid claim never justifies saying current tests pass when the host
freshness contract requires a new run.

### Verification Economy

Select verification by tier while still enforcing effective gates:

| Tier | Purpose |
| --- | --- |
| `worker` | Check the changed target during implementation. |
| `batch` | Check affected shared surfaces before grouped integration or handoff. |
| `milestone` | Run the integration gates required at Milestone closure. |
| `completion` | Audit all required dispositions, evidence validity, reviews, gaps, gates, and continuation for the scope being closed. |

The completion tier is a complete semantic audit, not an unconditional command
to run every test suite. Run a fresh or full suite when host-native or RVTF
policy requires it, and never weaken mandatory fresh/full-suite/review gates.
When a required tier fails, keep that failure visible, isolate and rerun the
minimal failed target, then escalate back to the required tier. Do not loop a
flaky suite until it happens to turn green; record flakiness, quarantine policy,
or a blocker and follow the required escalation path.

### Review Economy

Treat required review dimensions as normative coverage. Reviewer and batch
count are host execution choices, not a count derived from dimensions. Preserve
implementer-independent review for `strict`; strict independence alone does not
force separate batches. Allow a host-permitted independent combined batch when
its expertise and dimension coverage are sufficient. Require separate batches
only when specialist expertise or segregation of duties cannot be satisfied by
the combined batch, or when host-native fan-out mandates them.

Every applicable review contract declares these auditable inputs: review
`cadence` (`unit|batch|milestone|host_native`), `child_scope_policy`,
`covered_child_scope_refs` when the policy is `covered_at_parent`,
`batch_combination_policy`, and `host_native_required_batches`. The Completion
Gate compares those declared inputs with actual parent coverage, batches, and
receipts; declarations alone are not review evidence.

With child policy `covered_at_parent`, record
`review_state: pending_at_parent` before the parent review; never record future
review as existing evidence. A Unit whose
closure contract requires formal review remains incomplete until an actual
receipt covers it. Preserve every historical batch and its subject revision
immutably. Cross-revision reuse requires `review_coverage_carry_forward` with
source batch, from/to revisions, unchanged dimensions, impact assessment,
assessor, and decision; otherwise run a delta batch or controlled reopen.

## Status Taxonomy

Use these statuses consistently for Requirements, Acceptance Items, and Journeys. Journey Steps do not have an independent formal status:

| Status | Meaning |
| --- | --- |
| `pending` | The object exists but implementation has not started. |
| `implemented` | Code or docs exist, but verification evidence is not complete. |
| `verified` | Required evidence exists and was checked. |
| `deferred` | Deliberately postponed with reason, owner, and follow-up trigger. |
| `blocked` | Cannot proceed without external input or state change. |
| `rejected` | Explicitly out of scope or no longer required. |

Do not invent additional statuses such as `partially verified`. Partial proof stays `implemented`; record missing coverage as evidence gaps.

## Review Finding Intake

Classify every review finding before implementation:

| Class | Decision rule |
| --- | --- |
| `required-gap` | Existing requirement or acceptance criterion is missing or partial. Fix now unless explicitly deferred or blocked. |
| `evidence-gap` | Implementation may exist but evidence does not prove the acceptance criterion. Keep status `implemented`; add evidence or record a gap. |
| `cross-cutting-constraint` | Safety, privacy, security, compatibility, data integrity, performance, observability, or regression concern. Do not reject only because the original spec omitted it. |
| `scope-amendment` | Legitimate new requirement not in the original scope. Add an amendment decision before implementation. |
| `optional-enhancement` | Useful but not required. Reject or defer unless an owner accepts it into scope. |
| `quality-defect` | Code quality issue that threatens an existing requirement or maintainability standard. Link it to that constraint or record it as non-blocking review debt. |

For governed review, also record the finding's epoch, batch, dimension, subject
revision, and whether it was discovered after freeze. Late findings can reopen
only through trace impact and owner decision, not severity labels alone.

## Bounded Review Governance

Use bounded review governance when formal reviewers, multiple review passes,
blocking findings, strict risk, or prior remediation review are part of the
delivery decision.

The governance flow is:

```text
Delivery Scope
  -> Review Applicability
    -> Review Contract
      -> Review Epoch
        -> Review Batches
          -> Finding Freeze
            -> Remediation Cycle(s)
              -> Review Closure or Controlled Reopen
```

Baseline dimensions are `requirement-fidelity`, `impact-and-ownership`, and
`verification-and-closure`. Triggered dimensions cover state/compatibility,
concurrency/recovery, trust/security/privacy, performance/resources, and
operations/observability.

Freeze only after every expected batch covers its assigned dimensions on the
same subject revision and every finding has RVTF classification plus required
owner decisions. Freeze bounds remediation scope; it is not delivery completion.

Closure review checks frozen findings, changed evidence, and direct remediation
risk. Reopen only for `required_gap`, `evidence_invalidated`,
`remediation_regression`, `cross_cutting_risk`, or
`accepted_scope_amendment`, with affected requirements, dimensions, owner
decision, and next epoch recorded.

When a terminal review verdict has already assessed a stable material subject,
distinguish that verdict from the update that records it. A receipt-only
finalization may attach the verdict and derive only its explicitly authorized
finding, gap, review, and closure transitions. When a host-aware diff assessment
confirms that no material delivery truth changed, that terminal update does not
create a new review obligation. Any ambiguous change, or any change to
requirements, acceptance, Journeys, evidence truth, review scope, risk, host
gates, implementation, packages, or release facts, is material and returns to
impact assessment plus delta review or controlled reopen. A self-declared
receipt-only label is never proof.

## Requirement Validity

Check whether requirements are still valid when new information appears. Invalid, obsolete, contradictory, or infeasible requirements need a source, owner, rationale, and decision: amend, reject, defer, or block. RVTF tracks delivery fidelity; it does not prove the original requirement was correct.

## Canonical Acceptance Items

An Acceptance Item is an independently verifiable criterion nested under `requirements[].acceptance[]`. It is the canonical criterion record, not a copy made for a task or Journey.

- Each Acceptance Item belongs to exactly one Requirement and has a globally unique, stable ID within the delivery scope.
- Keep source provenance separate from identity. A moved bullet does not get a new ID merely because its locator changed.
- Record criterion, source reference, verification method, status, target-specific item evidence, and gap references on the Item.
- Journeys and Journey Steps reference Acceptance Item IDs. Never copy Item criterion, status, or evidence into a Journey.
- One Acceptance Item may support multiple Journeys; update its status once on the canonical Item.

Requirement status must obey the child Items:

| Active required Acceptance Item state | Parent Requirement constraint |
| --- | --- |
| Any `pending` or `implemented` Item | Requirement cannot be `verified`. |
| Any `deferred` Item | Requirement is `deferred` unless an accepted scope decision removes the Item from the required set. |
| Any `blocked` Item | Requirement is `blocked`. |
| Any `rejected` Item | Exclude it only with a recorded validity or scope decision. |
| All Items `verified` | Requirement may be `verified` only if Requirement-level constraints and evidence gaps are also closed. |

Do not derive percentages or a `partial` status. Preserve progress on the child Items while applying the parent constraint.

## Journey Applicability And Trace

Build a Journey Trace when acceptance depends on an actor reaching an outcome through ordered or causally connected observable steps. The actor may be a user, operator, developer, API consumer, external system, service, or automation. Applicability depends on the path, not on labels such as UI, CLI, API, migration, or infrastructure.

Common triggers are:

- item evidence alone cannot prove the overall outcome;
- steps have order, state-transition, or causal dependencies;
- the path crosses Requirements, components, systems, or responsibility boundaries;
- failure, recovery, rollback, or an alternative path affects acceptance;
- end-to-end closure must be judged backward from an actor goal.

In `discovery`, record candidate Journeys only. In `lite`, make an applicability decision when a trigger exists. In `standard` and `strict`, record `journey_applicability.decision` as `required` or `not_required` with rationale. Strict risk alone does not make a Journey required. When exact item-level verification fully proves an isolated change and no ordered or causal path exists, record `not_required`; do not create a synthetic Journey.

An Actor Journey records a stable ID, name, actor, goal, expected outcome, ordered Journey Steps, path evidence, status, and gaps. Each required Journey Step describes an actor-observable behavior or result and references at least one canonical Acceptance Item ID. A source-code edit is an implementation task, not a Journey Step. Scenario remains a way to describe preconditions or alternate/failure/recovery context; it is not a separate v1 trace object.

When a Journey decision Step requires an actor to judge, choose, confirm, or
authorize, its referenced Acceptance Items must define the actor-observable
decision basis needed to act from the public surface. Keep that basis separate
from exact machine binding: a stable selection token may bind the choice, but
an opaque ID, array position, internal lookup, or fixture-only fact cannot by
itself prove that a human actor could make the decision. Include material
differences, relevant constraints or unknowns, result confirmation or
revalidation, and a safe `hold` or evidence-seeking path when the declared
decision cannot yet be made. The adopting domain decides which concrete facts
are material.

Journey verification requires all of the following:

1. Every required Step maps to at least one Acceptance Item.
2. Every referenced required Acceptance Item is `verified`.
3. Strong, fresh, applicable path evidence proves the declared Step order and connection.
4. Path evidence proves the expected outcome, not merely that local components exist.
5. Required failure or recovery paths are explicitly represented.
6. No unresolved Journey or Journey Step gap remains.

All Acceptance Items being `verified` does not imply that a Journey is `verified`. Without adequate path evidence, keep the Journey `implemented`, record an evidence gap, and reject delivery completion.

## Evidence Quality

Evidence is strong only when it proves its declared target, covers named edge cases, is fresh or still applicable, and is part of the normal verification gate or has an explicit manual record. Weak evidence cannot support `verified`.

- **Item evidence** proves one Acceptance Item criterion.
- **Path evidence** proves Journey Step order, connection, and the expected outcome.

The same artifact may support both targets only when each target and `proves` claim is recorded separately. A local assertion can be strong Item evidence yet weak Journey evidence. A successful walkthrough cannot substitute implicitly for weak or missing Item evidence.

## Gap Ledger

Every gap needs:

- affected Requirement ID or capability, plus Acceptance Item, Journey, and Journey Step IDs when applicable
- observed gap
- impact
- decision: fix now, defer, block, reject, or split
- owner or next responsible workflow
- verification needed to close it

Do not hide gaps in prose summaries. If it matters, put it in the ledger.

Propagate gaps only to affected trace objects:

```text
Item evidence gap
  -> Acceptance Item cannot be verified
    -> parent Requirement cannot be verified
      -> dependent Journeys cannot be verified
```

```text
Journey-only path gap
  -> Journey cannot be verified
    -> delivery cannot be complete
```

A Journey-only path gap does not downgrade otherwise valid Requirement or Item evidence. If missing path evidence is first discovered after review freeze, fail the Completion Gate but do not automatically reopen the closed review. Reopen through the existing `evidence_invalidated` basis only when previously accepted evidence is later invalidated and trace impact warrants a controlled reopen.

## Scope Amendment

Use a scope amendment when review or implementation discovers necessary work not present in the original requirements. Record source, rationale, impacted requirements, owner decision, expected verification, and whether it blocks completion. Unapproved amendments are not implementation tasks.

## Completion Gate

Before claiming a phase, feature, plan, or task is complete:

1. Re-read the latest requirements and plan.
2. Check the authoritative required-child inventory revision, child scope refs,
   `required_for_parent`, and dispositions. Reject group completion,
   `host_status`, blocked/incomplete children, or silent deferred/residual
   aggregation as parent closure.
3. Check every Requirement and canonical Acceptance Item ID line by line.
4. Enforce Item-to-Requirement aggregation constraints; do not auto-promote a parent from partial child evidence.
5. Confirm every `verified` target has target-specific proof. For registry
   evidence, resolve its Evidence Claim and check the artifact and
   `evidence_claims[].validity.status`; apply the same semantics to supported
   legacy inline evidence.
6. Check the recorded Journey applicability decision and rationale.
7. For every applicable Journey, check Step-to-Item mappings, referenced Item status, independent path claims, expected outcome, and Journey/Step gaps.
8. Check review findings and scope amendments are classified.
9. If bounded review governance applies, audit the contract's `cadence`,
   `child_scope_policy`, `covered_child_scope_refs`,
   `batch_combination_policy`, and `host_native_required_batches` against actual
   required batch coverage, valid parent coverage or cross-revision
   carry-forward, and review closure or a controlled reopen, deferral, block, or
   residual-risk decision. Review closure remains a sub-gate.
10. Compute effective gates, confirm required `host_gate_status`, and keep any
    `current_test_status_claim` within the host freshness contract.
11. For every new Operational Economy non-Goal closure packet declaring
    `schema_version: "0.4.0"`, validate continuation: the true known parent
    disposition, or
    `continuation_mode: advisory` with `parent_disposition: unknown` for
    detached/`lite` unknown-parent work; mode-appropriate authority and locator,
    including resolvability for `durable_host`; `remaining_scope_refs` and
    `next_entry_conditions`; the actual `execution_action`; and `stop_basis`
    presence only for an actual stop or ending `host_boundary`, with absence
    otherwise. Preserve legacy `schema_version: "0.3.0"` closure packets without
    continuation and never infer scheduling authority.
12. State the actual closure status: `complete`, `complete_with_deferred_gaps`, `complete_with_residual_risk`, `incomplete`, `blocked`, or `invalid_requirements`.
13. Call delivery `complete` only when every required Requirement and every applicable Journey is `verified`; if required gaps remain, reject `complete`.

## Common Failures

| Failure | Correction |
| --- | --- |
| Plan has tasks but no requirement IDs | Add IDs before implementation starts. |
| Tests pass but requirements are unchecked | Build the trace matrix and inspect each row. |
| Review only checks code quality | Run a requirement coverage review first. |
| Review finding turns into work automatically | Classify it and link it to an existing requirement, accepted amendment, or constraint first. |
| Reviewer reports one blocker and omits other dimensions | Accept the finding, mark the batch incomplete, and do not freeze. |
| Re-review restarts open-ended review after every fix | Bound it to frozen findings, changed evidence, and direct remediation risk. |
| Freeze treated as completion | Close review if valid, then still run the full Completion Gate. |
| Foundation or component gate treated as Journey completion | Require target-specific path evidence for the ordered Steps and expected outcome. |
| Acceptance Item copied into each Journey | Keep one canonical nested Item and reference its stable ID. |
| All Acceptance Items `verified`, so Journey auto-verifies | Keep Journey `implemented` until strong path and outcome evidence passes its own gate. |
| Technical domain label decides Journey applicability | Apply actor-goal-path triggers regardless of UI, API, migration, infrastructure, or actor type. |
| Isolated change gets a synthetic Journey | Record a justified `not_required` decision when item evidence fully proves the result and no path exists. |
| Missing path evidence after review freeze automatically reopens review | Fail delivery closure; reopen only when accepted evidence is invalidated under controlled-reopen rules. |
| Late optional finding blocks closure | Defer/reject unless an owner accepts an amendment. |
| Weak evidence marked `verified` | Keep the row `implemented` and record evidence gaps. |
| Owner or verifier counts presented as completion evidence | Use target-specific evidence and object dispositions; counts are diagnostic only. |
| Deferred work is mentioned informally | Move it into the gap ledger with owner and close condition. |
| Next phase starts with hidden leftovers | Convert leftovers into next-phase entry criteria or explicit exclusions. |
| Execution, verification, or review group completion closes a parent | Aggregate only through the versioned required-child scope inventory. |
| Host `done`, `archived`, `shipped`, or `override` becomes RVTF `complete` | Keep host lifecycle in `host_status`; derive RVTF disposition from trace truth. |
| One passing artifact blanket-verifies many targets | Create independent target-specific Evidence Claims with `proves`, coverage, and validity. |
| Opaque fingerprint proves cross-revision validity | Record the auditable comparison basis, rationale, assessor, policy, and decision. |
| Old valid claim is reported as current tests passing | Run the fresh effective host gate before making a current-test claim. |
| Completion Gate always runs the full suite | Run the complete semantic audit plus only the suites required by effective gates at this boundary. |
| Review dimensions become reviewer or batch count | Preserve normative coverage; let host, expertise, independence, and policy determine execution shape. |
| Future parent review is used as Unit evidence | Record `review_state: pending_at_parent`; keep formally reviewed closure incomplete until the receipt exists. |
| Historical batch is rewritten onto a new revision | Keep it immutable and use assessed carry-forward, a delta batch, or controlled reopen. |
| Recording an accepted review verdict recursively triggers another review | Separate the reviewed material subject from receipt-only finalization; do not re-review a terminal update solely because it records the verdict. |
| A mixed material change declares itself receipt-only | Reject the declaration, default ambiguity to material, and require host-aware impact assessment plus the applicable review path. |
| Unit closure becomes Goal completion | Close only the Unit and aggregate the authoritative remaining child inventory. |
| Continuation record acts as a scheduler | Record authority, locator, and actual action, then leave invocation to the user, orchestrator, or host. |
| No-progress iteration repeats automatically | Warn, select new unblocked scope, justify evidence-producing repetition, or record a blocker. |
