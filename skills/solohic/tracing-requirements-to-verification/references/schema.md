# RVTF Schema

## Schema Version Compatibility Boundary

Use `schema_version: "0.3.0"` for the legacy inline Requirement, Acceptance
Item, Journey, review, gap, and closure representation below. It remains valid
without economy-plane registries, cadence fields, or continuation records.
Artifacts created before versioning may omit `schema_version`; they are treated
as 0.3 only when they contain no 0.4-only section or field. An omitted version
never permits 0.4 content, and an explicit unsupported version is rejected.

Use `schema_version: "0.4.0"` when creating the additive delivery-scope,
evidence-registry, verification-policy, review-cadence, or continuation records
defined later in this reference. Version 0.4 does not move canonical Acceptance
Items out of `requirements[].acceptance[]`, replace Journey path truth, or
reinterpret host status as delivery disposition.

A 0.3 document is rejected when it carries 0.4-only top-level sections:
`delivery_scopes`, `delivery_groups`, `evidence_artifacts`, `evidence_claims`,
`evidence_validity_assessments`, `verification_policy`, `host_gate_receipts`,
`review_impact_assessments`, `review_coverage_carry_forward`, or
`closure_packet`. Legacy 0.3 review dimensions remain a list; 0.4 review
dimensions use the mapping representation shown below.
The same boundary applies to nested 0.4 review-contract fields and batch host
references; adding any such field requires `schema_version: "0.4.0"`.

A 0.4 artifact may be mixed: one target may keep legacy inline evidence while a
different target uses `evidence_ref` and `evidence_claims`. Do not give one
target both mutable inline and registry truth. The target-specific claim is the
compatibility boundary, not the file containing the receipt.

## Requirement ID Style

Use stable IDs that survive task reordering:

```text
<AREA>-<CAPABILITY>-<NUMBER>
```

Examples: `AUTH-SESSION-001`, `CLI-RUN-003`, `DOCS-MIGRATION-002`.

For phase-oriented work, prefix with the phase only when the requirement truly belongs to that phase: `P16-REPLAY-001`.

## Legacy-Compatible 0.3 Inline Trace Matrix

```yaml
schema_version: "0.3.0"
scope:
  id: P1.6
  title: Offline skill optimization
  mode: standard
  sources:
    - docs/design.md
    - docs/acceptance.md

requirements:
  - id: P16-REPLAY-001
    capability: replay isolation
    type: behavior
    source: docs/design.md#replay-isolation
    validity:
      status: accepted
      owner: phase-owner
      rationale: Required for trustworthy offline comparison.
    statement: Baseline, candidate, and test replay use sealed inputs.
    acceptance:
      - id: P16-REPLAY-001-AI-001
        criterion: Baseline, candidate, and test replay load the declared sealed inputs.
        source_ref:
          path: docs/design.md
          anchor: replay-isolation
          revision: sha256:0123abcd
        verification:
          method: automated-test
          command: pnpm test:p1.6 -- replay-isolation
          expected: exits 0 with every replay bound to its declared sealed input
        status: verified
        evidence:
          - artifact: artifacts/replay-sealed-input.json
            subject_revision: def456
            quality: strong
            target: P16-REPLAY-001-AI-001
            proves: All three replay modes use their declared sealed inputs.
            normal_gate: true
        gaps: []
      - id: P16-REPLAY-001-AI-002
        criterion: Replays cannot read mutable live run state.
        source_ref:
          path: docs/acceptance.md
          anchor: live-state-rejection
          revision: sha256:5678ef01
        verification:
          method: automated-test
          command: pnpm test:p1.6 -- replay-live-state-rejection
          expected: exits 0 and fails if live state is read
        status: verified
        evidence:
          - artifact: artifacts/replay-live-state-rejection.json
            subject_revision: def456
            quality: strong
            target: P16-REPLAY-001-AI-002
            proves: The replay runner rejects mutable live state.
            normal_gate: true
        gaps: []
    status: verified
    gaps: []

  - id: P16-TENANT-001
    capability: tenant isolation
    type: cross-cutting-constraint
    applies_to:
      - data access
      - replay storage
    statement: New data access cannot expose records outside the caller tenant.
    acceptance:
      - id: P16-TENANT-001-AI-001
        criterion: Tenant A cannot read tenant B records.
        source_ref:
          path: docs/design.md
          anchor: tenant-isolation
          revision: sha256:0123abcd
        verification:
          method: automated-test
          command: pnpm test:p1.6 -- tenant-isolation
          expected: exits 0
        status: verified
        evidence:
          - artifact: artifacts/tenant-isolation.json
            subject_revision: def456
            quality: strong
            target: P16-TENANT-001-AI-001
            proves: Cross-tenant reads are rejected.
            normal_gate: true
        gaps: []
    status: verified
    gaps: []

  - id: P16-RECOVERY-001
    capability: replay recovery
    type: behavior
    source: docs/design.md#replay-recovery
    validity:
      status: accepted
      owner: phase-owner
      rationale: Recovery is required, but its path proof is intentionally deferred.
    statement: An interrupted replay can resume from sealed state and reach a consistent result.
    acceptance:
      - id: P16-RECOVERY-001-AI-001
        criterion: Resume uses the sealed checkpoint and produces the expected comparison.
        source_ref:
          path: docs/design.md
          anchor: replay-recovery
          revision: sha256:0123abcd
        verification:
          method: end-to-end-test
          command: pnpm test:p1.6 -- replay-recovery
          expected: resumed comparison matches an uninterrupted sealed replay
        status: deferred
        evidence: []
        gaps:
          - GAP-P16-001
    status: deferred
    gaps:
      - GAP-P16-001

journey_applicability:
  scope_ref: phase:P1.6
  decision: required
  rationale: Trustworthy replay acceptance depends on an ordered automation path reaching a consistent comparison result.
  triggers:
    - ordered observable steps
    - path crosses dataset and evaluation boundaries
    - item evidence alone cannot prove the expected outcome

journeys:
  - id: J-P16-REPLAY-001
    name: Produce a trustworthy sealed replay comparison
    actor: evaluation-runner
    goal: Compare baseline, candidate, and test behavior without reading live state.
    expected_outcome: The comparison result is derived only from the declared sealed inputs.
    steps:
      - id: J-P16-REPLAY-001-S1
        observable_outcome: The runner loads the declared sealed inputs for all replay modes.
        acceptance_item_ids:
          - P16-REPLAY-001-AI-001
      - id: J-P16-REPLAY-001-S2
        observable_outcome: The runner rejects any attempt to read mutable live state.
        acceptance_item_ids:
          - P16-REPLAY-001-AI-002
    path_evidence:
      - artifact: artifacts/sealed-replay-journey.json
        subject_revision: def456
        covers_steps:
          - J-P16-REPLAY-001-S1
          - J-P16-REPLAY-001-S2
        proves_order: true
        proves_outcome: true
        quality: strong
        normal_gate: true
    status: verified
    gaps: []
  - id: J-P16-RECOVERY-001
    name: Recover an interrupted sealed replay
    actor: evaluation-runner
    goal: Resume interrupted work without reading mutable live state.
    expected_outcome: The resumed comparison matches an uninterrupted sealed replay.
    steps:
      - id: J-P16-RECOVERY-001-S1
        observable_outcome: The runner resumes from the sealed checkpoint and produces the expected comparison.
        acceptance_item_ids:
          - P16-RECOVERY-001-AI-001
    path_evidence: []
    status: deferred
    gaps:
      - GAP-P16-001

host_trace_mappings:
  - host_kind: task
    host_ref: Task 3
    requirement_ids:
      - P16-REPLAY-001
    acceptance_item_ids:
      - P16-REPLAY-001-AI-001
      - P16-REPLAY-001-AI-002
    journey_ids:
      - J-P16-REPLAY-001
    journey_step_ids:
      - J-P16-REPLAY-001-S1
      - J-P16-REPLAY-001-S2
  - host_kind: task
    host_ref: Task 4
    requirement_ids:
      - P16-TENANT-001
    acceptance_item_ids:
      - P16-TENANT-001-AI-001
    journey_ids: []
    journey_step_ids: []
```

`requirements[].acceptance[]` is the only canonical Acceptance Item store. IDs
remain stable across task or source-bullet reordering; `source_ref` records
provenance and does not generate identity. Journeys reference Item IDs and never
copy Item criterion, status, or evidence. Journey Steps have no separate status.

For an isolated change without a path trigger, use the same Requirement and Item
shape and record:

```yaml
journey_applicability:
  scope_ref: change:metadata-correction
  decision: not_required
  rationale: Exact item evidence proves the result; no ordered or causal path exists.
journeys: []
```

## Decision Step Guidance

When an existing Journey Step requires a human actor to judge, choose, confirm,
or authorize, express decision sufficiency through the Step's
`observable_outcome`, its referenced Acceptance Item criteria, and separate
target-specific item and path evidence. This guidance does not add a new Journey
Step type.

```yaml
steps:
  - id: J-CHANGE-001-S2
    observable_outcome: The actor sees public information that distinguishes the available choices, selects one, and sees the current selection revalidated.
    acceptance_item_ids:
      - CHANGE-CHOICE-001-AI-001
```

The referenced Item defines which alternatives, material differences,
constraints, unknowns, and insufficient-information behavior are required by
the domain contract. Keep that actor-facing basis separate from machine
binding: a stable selection token may identify the exact choice, but an opaque
ID or fixture-only lookup does not explain it. Conversely, a readable label
does not replace exact binding and revalidation.

## Gap Ledger

```yaml
gaps:
  - id: GAP-P16-001
    requirement: P16-RECOVERY-001
    acceptance_item: P16-RECOVERY-001-AI-001
    journey: J-P16-RECOVERY-001
    journey_step: J-P16-RECOVERY-001-S1
    type: evidence-gap
    summary: The recovery Item and connected Step lack fresh evidence.
    impact: The Acceptance Item, parent Requirement, and recovery Journey cannot be verified.
    decision: deferred
    owner: next-phase-planning
    close_condition: Record strong item evidence plus path evidence covering the declared Step and outcome.

review_findings:
  - id: RF-P16-001
    source: code-review
    epoch: RE-P16-001
    batch: RB-P16-REQ-001
    dimension: requirement-fidelity
    discovered_after_freeze: false
    summary: Input normalization concern may affect replay identity.
    classification: scope-amendment
    linked_requirement: null
    decision: needs-owner-decision
    rationale: Not in original scope, but may affect correctness.
    blocks_completion: true
    next_step: Decide whether to accept amendment or reject with rationale.

scope_amendments:
  - id: AMEND-P16-001
    source_finding: RF-P16-001
    statement: Normalize replay keys before persistence.
    decision: accepted
    owner: phase-owner
    impacted_requirements:
      - P16-REPLAY-001
    verification:
      method: automated-test
      command: pnpm test:p1.6 -- replay-key-normalization
    blocks_completion: true
```

## Review Governance Artifacts

Use these fields when the review-governance applicability gate requires bounded
or independent review. Omit them when `review_applicability.decision` is
`not_required`.

```yaml
review_applicability:
  scope_ref: phase:p1.6
  decision: required
  mode: bounded
  rationale: Multiple review passes can block phase closure.

review_contract:
  id: RC-P16-001
  scope_ref: phase:p1.6
  impact_surface:
    states: [sealed-replay-input]
    interfaces: [replay-runner]
    writers: [dataset-builder]
    readers: [evaluation-runner]
    callers: [optimization-command]
    consumers: [closure-report]
  dimensions:
    - id: requirement-fidelity
      applicability: required
      requirements: [P16-REPLAY-001]
    - id: impact-and-ownership
      applicability: required
      requirements: [P16-REPLAY-001, P16-TENANT-001]
    - id: verification-and-closure
      applicability: required
      requirements: [P16-REPLAY-001]
    - id: concurrency-and-recovery
      applicability: required
      requirements: [P16-RECOVERY-001]
      rationale: Interrupted replay recovery is part of the delivery scope.
  expected_batches:
    - id: requirements-review
      host_kind: requirement-coverage-review
      dimensions: [requirement-fidelity, impact-and-ownership]
    - id: closure-risk-review
      host_kind: verification-gap-review
      dimensions: [verification-and-closure, concurrency-and-recovery]
  exclusions:
    - Performance optimization is outside current acceptance criteria.

review_epochs:
  - id: RE-P16-001
    contract: RC-P16-001
    subject_refs:
      - kind: git-commit
        ref: repository
        revision: def456
    status: collecting

review_batches:
  - id: RB-P16-REQ-001
    epoch: RE-P16-001
    host_kind: requirement-coverage-review
    subject_refs:
      - kind: git-commit
        ref: repository
        revision: def456
    reviewer:
      role: requirements-reviewer
      relationship_to_implementer: independent
      reviewer_ref: opaque-reference
    dimension_coverage:
      - dimension: requirement-fidelity
        status: covered
        findings: [RF-P16-001]
      - dimension: impact-and-ownership
        status: covered
        findings: []
    coverage_status: complete
    limitations: []

review_freeze:
  id: RFR-P16-001
  epoch: RE-P16-001
  subject_refs:
    - kind: git-commit
      ref: repository
      revision: def456
  accepted_batches: [RB-P16-REQ-001, RB-P16-CLOSE-001]
  frozen_findings: [RF-P16-001]
  decision_owner: delivery-coordinator
  frozen_at: 2026-07-21T08:00:00Z

remediation_cycles:
  - id: RRC-P16-001
    epoch: RE-P16-001
    addresses_findings: [RF-P16-001]
    subject_refs:
      - kind: git-commit
        ref: repository
        revision: fed789
    evidence:
      - artifact: tests/replay-key-normalization.test.ts
        quality: strong
    direct_regressions: []
    unrelated_scope_introduced: false

review_reopens:
  - id: RRO-P16-001
    prior_epoch: RE-P16-001
    basis: evidence_invalidated
    source_finding: RF-P16-009
    affected_requirements: [P16-REPLAY-001]
    affected_dimensions: [verification-and-closure]
    owner_decision: reopen
    next_epoch: RE-P16-002
```

### Review Governance Values

Review lifecycle statuses are separate from requirement statuses:

- `collecting`
- `frozen`
- `remediating`
- `closed`
- `reopened`

Dimension coverage statuses:

- `covered`
- `partial`
- `blocked`

Canonical reopen bases:

- `required_gap`
- `evidence_invalidated`
- `remediation_regression`
- `cross_cutting_risk`
- `accepted_scope_amendment`

For findings produced before freeze, set `epoch`, `batch`, and `dimension`.
For findings discovered after freeze, set `discovered_after_freeze: true`,
identify the affected dimension, keep the existing RVTF `classification`, and
record whether the decision reopens, defers, rejects, blocks, or accepts an
amendment.

## Closure Packet

Version 0.3 keeps the v0.2 flat `verified`, `deferred`, `blocked`, and
`rejected` fields as a derived compatibility summary. The typed Requirement,
Acceptance Item, Journey, and gap sections are additive detail. Generate both
from canonical trace objects and gap decisions; do not update either summary
independently.

```yaml
closure:
  scope: P1.6
  status: complete_with_deferred_gaps
  review_closure:
    epoch: RE-P16-001
    status: closed
    remaining_late_findings: []
  verified:
    - P16-REPLAY-001
    - P16-TENANT-001
  deferred:
    - GAP-P16-001
  blocked: []
  rejected: []
  requirements:
    verified:
      - P16-REPLAY-001
      - P16-TENANT-001
    deferred:
      - P16-RECOVERY-001
    blocked: []
    rejected: []
  acceptance_items:
    verified:
      - P16-REPLAY-001-AI-001
      - P16-REPLAY-001-AI-002
      - P16-TENANT-001-AI-001
    deferred:
      - P16-RECOVERY-001-AI-001
    blocked: []
    rejected: []
  journeys:
    verified:
      - J-P16-REPLAY-001
    deferred:
      - J-P16-RECOVERY-001
    blocked: []
    rejected: []
  gaps:
    deferred:
      - GAP-P16-001
  accepted_amendments:
    - AMEND-P16-001
  verification_runs:
    - command: pnpm test:p1.6
      result: pass
      date: 2026-07-18
  residual_risk:
    - Recovery behavior remains unavailable until its deferred evidence gap closes.
  next_phase_entry:
    - P1.7 owns the replay-recovery evidence gap.
```

## Status Rules

- Requirements, Acceptance Items, and Journeys use `pending`, `implemented`,
  `verified`, `deferred`, `blocked`, and `rejected`.
- Journey Steps do not have a formal status.
- `verified` requires target-specific evidence.
- `implemented` is not enough for completion.
- Partial evidence is `implemented` plus one or more `evidence-gap` entries.
- `deferred` requires a reason and close condition.
- `blocked` requires a specific missing input or external state.
- `rejected` requires a scope decision.
- A Requirement can be `verified` only when every active required Acceptance Item
  is `verified`, Requirement-level constraints are verified, and evidence gaps
  are closed.
- A required deferred Item makes its parent Requirement `deferred`; a blocked
  Item makes it `blocked`. Exclude a rejected Item only through a validity or
  scope decision.
- A Journey can be `verified` only when every required Step maps to verified
  Items and strong path evidence proves Step order, connection, and expected
  outcome.
- All Items being `verified` never auto-verifies a Journey.
- A Journey-only path gap keeps the Journey below `verified` and blocks delivery
  completion without downgrading otherwise valid Item or Requirement evidence.
- Review lifecycle and dimension coverage statuses are not requirement statuses.
  Do not use them in the `requirements[].status` field.

## Closure Statuses

- `complete`: all required Requirements and all applicable Journeys are verified,
  with no unresolved blocking findings.
- `complete_with_deferred_gaps`: required deferrals are explicit, owned, and non-blocking.
- `complete_with_residual_risk`: risk remains but is accepted with owner and rationale.
- `incomplete`: required work or evidence is missing.
- `blocked`: external input or state prevents closure.
- `invalid_requirements`: requirements must be corrected before implementation or verification can be trusted.

## Additive 0.4 Delivery Scopes And Groups

Delivery scopes own closure. Groups organize work orthogonally and never create
parent-child closure propagation.

```yaml
schema_version: "0.4.0"

delivery_scopes:
  - scope_ref: goal:example
    scope_kind: goal
    host_kind: release-objective
    host_ref: host-goal:opaque-reference
    required_child_inventory_revision: sha256:goal-inventory-v2
    required_child_scope_refs: [milestone:example]
    disposition: incomplete

  - scope_ref: milestone:example
    scope_kind: milestone
    host_kind: phase
    parent_scope_ref: goal:example
    required_for_parent: true
    required_child_inventory_revision: sha256:milestone-inventory-v3
    required_child_scope_refs: [unit:example, unit:example-next]
    disposition: incomplete

  - scope_ref: unit:example
    scope_kind: unit
    host_kind: task
    parent_scope_ref: milestone:example
    required_for_parent: true
    host_status: done
    disposition: incomplete
    review_state: pending_at_parent

  - scope_ref: unit:example-next
    scope_kind: unit
    host_kind: task
    parent_scope_ref: milestone:example
    required_for_parent: true
    host_status: planned
    disposition: incomplete

delivery_groups:
  - group_ref: execution-group:wave-1
    group_kind: execution_batch
    host_kind: wave
    member_scope_refs: [unit:example]
```

`scope_kind` is exactly `goal`, `milestone`, or `unit`. `group_kind` is exactly
`execution_batch`, `verification_batch`, or `review_batch`. Parent references
must resolve and be acyclic. A parent's authoritative
`required_child_scope_refs` inventory has a revision, agrees with each child's
`required_for_parent`, and is the only path for closure aggregation.

In 0.4 standard and strict artifacts, every non-root scope explicitly records
boolean `required_for_parent`. Every scope that is an actual parent explicitly
records `required_child_inventory_revision` and
`required_child_scope_refs`, including an empty list when it currently has no
required children. This explicit hierarchy floor does not extend to 0.3 or
0.4 lite artifacts.

A closed parent may aggregate only required children with `complete`,
`complete_with_deferred_gaps`, or `complete_with_residual_risk`. Removing a
child requires an accepted scope amendment and an updated inventory; a stale
`required_for_parent: true` is not enough. `host_status` records host lifecycle
truth separately and cannot override a blocked or incomplete RVTF disposition.
A parent declared plain `complete` cannot hide a required child whose current
disposition is `complete_with_deferred_gaps` or
`complete_with_residual_risk`; the parent must preserve the applicable
qualified closure truth.

An ordinary child that was never required may use `required_for_parent: false`
without inventing history. When the artifact explicitly claims that a formerly
required child was removed, record that claim and its accepted amendment:

```yaml
delivery_scopes:
  - scope_ref: unit:removed-example
    scope_kind: unit
    parent_scope_ref: milestone:example
    required_for_parent: false
    required_inventory_exclusion:
      amendment_ref: AMEND-REMOVE-EXAMPLE-001
      inventory_revision: sha256:milestone-inventory-v4
    disposition: incomplete

scope_amendments:
  - id: AMEND-REMOVE-EXAMPLE-001
    decision: accepted
    owner: delivery-owner
    parent_scope_ref: milestone:example
    removed_required_child_scope_refs: [unit:removed-example]
    required_child_inventory_revision: sha256:milestone-inventory-v4
```

The child must be absent from that parent revision's
`required_child_scope_refs`; its exclusion record, amendment parent/child, and
the parent's current `required_child_inventory_revision` must agree. A false or
missing `required_for_parent` value alone neither claims nor proves removal.

## Additive 0.4 Evidence Registry

Artifacts are reusable receipts. Claims are target-specific proof statements.
One passed artifact may support many claims, but every claim independently names
an Acceptance Item or Journey and what the receipt proves.

```yaml
evidence_artifacts:
  - id: EA-EXAMPLE-001
    kind: test-receipt
    locator: artifacts/example.json
    generated_at: 2026-08-05T10:00:00Z
    subject_revision: abc123
    verifier_ref: test:example
    verifier_revision: sha256:verifier-v1
    dependency_fingerprint: sha256:inputs-v1
    environment_fingerprint: python3.13-pyyaml6-linux
    command_signature: python3 tests/example.py
    result: passed

evidence_claims:
  - id: EC-EXAMPLE-ITEM-001
    artifact_ref: EA-EXAMPLE-001
    target_kind: acceptance_item
    target_ref: EXAMPLE-001-AI-001
    proves: The exact Item criterion is satisfied.
    coverage: [item-contract]
    normal_gate: true
    validity:
      status: valid
      assessment_ref: EVA-EXAMPLE-ITEM-001
      checked_against_revision: def456
      invalidation_triggers:
        - target_changed
        - verifier_changed
        - dependency_fingerprint_changed

evidence_validity_assessments:
  - id: EVA-EXAMPLE-ITEM-001
    claim_ref: EC-EXAMPLE-ITEM-001
    from_revision: abc123
    checked_against_revision: def456
    assessed_at: 2026-08-05T11:00:00Z
    assessor_ref: host:affected-graph
    policy_ref: verification-policy:example
    basis:
      target_revision_before: sha256:criterion-v1
      target_revision_after: sha256:criterion-v1
      verifier_revision_before: sha256:verifier-v1
      verifier_revision_after: sha256:verifier-v1
      dependency_fingerprint_before: sha256:inputs-v1
      dependency_fingerprint_after: sha256:inputs-v1
      environment_compatibility: compatible
      freshness: within_policy
      rationale: Only unrelated documentation changed.
    decision: valid
```

The exact claim validity field is `evidence_claims[].validity.status`; allowed
values are `valid`, `stale`, `invalidated`, and `unknown`. They are not
Requirement statuses. A valid claim requires a passed artifact and an actual
target of the declared kind. Item and Journey targets remain separate, and each
inline `evidence_ref` must resolve to a claim for that exact target.

A `verified` Item needs either target-matching inline evidence with
`quality: strong`, `normal_gate: true`, and a non-empty `proves`, or a matching
valid registry claim with those gate/proof properties and a passed artifact. A
`verified` Journey similarly needs one strong inline path or one valid Journey
claim that proves order and outcome and covers every local Step. One target may
not mix inline truth and `evidence_ref`; different targets may choose different
representations.

When `subject_revision` and `checked_against_revision` differ, standard and
strict reuse requires the referenced assessment shown above. It must match the
claim and from/to revisions and explicitly compare the target, verifier,
dependency basis, environment compatibility, and freshness. An opaque
fingerprint alone is never a validity decision. Lite may instead use a concise
`validity.reuse_basis` with `target`, `verifier`, `dependency`, `environment`,
`freshness`, and `rationale`; without those surfaces use `unknown` and rerun.

Invalidate only affected claims and their dependent Items or Journeys. A failed
Journey path claim does not invalidate an unrelated Item claim merely because
both share one artifact.

## Claim Validity, Host Gates, And Current Test Status

Claim reuse does not establish that current host tests or reviews ran. Preserve
three separate facts:

- claim applicability in `evidence_claims[].validity.status`;
- required current-boundary execution in `closure_packet.host_gate_status`;
- the fresh receipt's `current_test_status_claim`.

```yaml
host_gate_receipts:
  - id: HGR-CURRENT-TREE-001
    gate_ref: host:test-current-tree
    lifecycle_boundary: task_completion
    subject_revision: def456
    executed_at: 2026-08-05T11:30:00Z
    command_signature: python3 tests/example.py --current-tree
    freshness: current_tree
    status: passed
    current_test_status_claim: passed
```

A closure may mark a required host gate `satisfied` only through a matching
fresh receipt, gate reference, lifecycle boundary, freshness, and subject
revision. A valid older claim cannot manufacture a current test-status claim.
`current_test_status_claim: passed` is valid only when that exact receipt is
referenced by the closure's satisfied effective host gate at the current
revision; unused, historical, failed, wrong-boundary, and stale receipts do not
prove current tests. `freshness` is a host-policy value, not an RVTF enum: the
receipt must exactly match the effective required gate's declared value (for
example, `pre_merge_current`).

This match has a non-empty metadata floor. Each required policy gate names
`gate_ref`, `lifecycle_boundary`, and `freshness`; each satisfied closure entry
names `gate_ref`, `receipt_ref`, `status: satisfied`, and `subject_revision`;
and the referenced receipt names matching gate, boundary, freshness, revision,
`executed_at`, and `command_signature`, with `status: passed`. A passed
`current_test_status_claim` is valid only across this complete chain. Two
missing values never count as equal metadata.

## Additive 0.4 Verification Policy

```yaml
verification_policy:
  id: verification-policy:example
  scope_ref: milestone:example
  host_native_required_gates:
    - gate_ref: host:test-current-tree
      lifecycle_boundary: task_completion
      freshness: current_tree
  tiers:
    worker:
      trigger: affected_unit_change
      command_refs: [test:targeted]
    batch:
      trigger: batch_ready_or_shared_dependency_change
      command_refs: [test:affected]
    milestone:
      trigger: milestone_closure
      command_refs: [test:integration]
    completion:
      trigger: goal_closure
      command_refs: [trace:completion-audit, test:repository-full]
  reuse_policy: reuse_valid_claims_then_run_missing_gates
```

The four tiers are `worker`, `batch`, `milestone`, and `completion`. Their
effective gate set is always the union of applicable RVTF commands and
`host_native_required_gates`; reuse cannot erase the host floor. Completion is
a semantic audit, not an instruction to run every repository suite at every
Unit. A host-declared fresh or full gate remains mandatory at its boundary.
Every closed 0.4 standard/strict packet requires this policy, non-empty command
references in all four tiers, and at least one
`host_native_required_gates` entry. Clearing or omitting the host floor cannot
make an otherwise closed packet valid.

## Additive 0.4 Review Cadence And Carry-Forward

```yaml
review_contract:
  id: RC-EXAMPLE-001
  scope_ref: milestone:example
  cadence: milestone
  child_scope_policy: covered_at_parent
  covered_child_scope_refs: [unit:example]
  batch_combination_policy: combined_allowed
  host_native_required_batches: [host:task-review]
  independence:
    required: false
  dimensions:
    baseline:
      - requirement-fidelity
      - impact-and-ownership
      - verification-and-closure
    triggered: []
  expected_batches: []

review_impact_assessments:
  - id: RIA-EXAMPLE-001
    source_batch_ref: RB-EXAMPLE-001
    from_revision: abc123
    to_revision: def456
    changed_surface: [documentation-only]
    unchanged_dimensions: [trust-security-and-privacy]
    rationale: The reviewed security surface is unchanged.
    assessor_ref: reviewer:security
    decision: accepted

review_coverage_carry_forward:
  - id: RCF-EXAMPLE-001
    source_batch_ref: RB-EXAMPLE-001
    target_epoch: RE-EXAMPLE-002
    from_revision: abc123
    to_revision: def456
    unchanged_dimensions: [trust-security-and-privacy]
    impact_assessment_ref: RIA-EXAMPLE-001
    assessor_ref: reviewer:security
    decision: accepted
```

Cadence is `unit`, `batch`, `milestone`, or `host_native`. Child coverage is
explicit; before the parent batch actually runs, record
`review_state: pending_at_parent`, never future evidence. Batch combination is
`combined_allowed`, `separate_required`, or `host_native`. Combination does not
remove strict independence, specialist expertise, segregation requirements, or
`host_native_required_batches`.

For a closed 0.4 standard/strict packet, `review_applicability` is mandatory.
`decision: required` requires a matching `review_contract` plus a closed,
resolving epoch receipt. Contract `expected_batches[].host_kind` and
`expected_batches[].dimensions` match only complete batches or valid
carry-forward explicitly accepted by the current closure; historical or
unaccepted batches do not satisfy the assignment. `separate_required` consumes
distinct accepted source batches, while `combined_allowed` may reuse one
qualified combined batch. Distinct assignment is a complete matching across all
eligible accepted providers, independent of provider or assignment order.
Independence is evaluated per required dimension, so a supplemental self-check
does not poison independently covered required work.

A scope in `review_state: pending_at_parent` remains `incomplete` when formal
parent review is part of its closure contract. Change the state to
`covered_at_parent` only after a closed epoch and its accepted batch or assessed
carry-forward cover the child at the closure packet's exact `subject_revision`.
`covered_at_parent` without that current-revision receipt is not closure proof.

Historical batches keep their original epoch and subject revision forever.
Carry-forward is a new assessment linking from/to revisions; it agrees with an
accepted impact assessment and carries only dimensions actually covered by the
source batch. Changed dimensions receive a bounded delta batch. If unchanged
impact cannot be established, create that batch or use controlled reopen.
Every carry-forward names `target_epoch`; an accepted carry-forward targets the
closure epoch, and `to_revision` equals both that epoch's revision and
`closure_packet.subject_revision`.

## Additive 0.4 Closure Continuation

New 0.4 non-Goal closure packets include continuation. Version 0.3 `closure`
records remain legacy-compatible without it.

```yaml
closure_packet:
  scope_ref: unit:example
  subject_revision: def456
  disposition: complete
  host_gate_status:
    - gate_ref: host:test-current-tree
      receipt_ref: HGR-CURRENT-TREE-001
      status: satisfied
      subject_revision: def456
  continuation:
    parent_scope_ref: milestone:example
    parent_disposition: incomplete
    continuation_mode: artifact_only
    authority_ref: rvtf:goal-example
    resume_locator: docs/delivery/example.yaml
    remaining_scope_refs: [unit:example-next]
    next_entry_conditions:
      - Begin the next unblocked Unit after owner selection.
    execution_action: stop
    stop_basis: host_command_completed
```

`continuation_mode` is `durable_host`, `artifact_only`, or `advisory`.
`durable_host` and `artifact_only` require an authority and locator; advisory
identifies the user or external orchestrator that retains control.
`execution_action` is `continue`, `stop`, `await_owner`, or `host_boundary`.
Use `stop_basis` only, and always, for an actual `stop` or `host_boundary`.
Continuation records truth and resumption capability; RVTF is not a scheduler
and never invokes the next workflow merely because the parent remains active.
`goal_complete` requires a known closed parent or Goal and no remaining scope
references. `all_remaining_work_blocked` requires a non-empty list of resolved
blocked scopes and a blocked or incomplete parent. `owner_requested_stop`,
`host_runtime_boundary`, and `host_command_completed` record why execution
paused; they do not change the recorded parent disposition.

## Minimum Additive Fields By Mode

| Mode | Minimum 0.4 economy detail |
| --- | --- |
| `discovery` | Candidate hierarchy and reuse assumptions only; no closure claim. |
| `lite` | Known parent reference where available; advisory continuation is allowed; cross-revision reuse names all comparison surfaces in a concise rationale. |
| `standard` | Scope hierarchy and requiredness, orthogonal groups when used, four-tier verification policy with host floor, review cadence, assessment-backed cross-revision validity, and continuation authority. |
| `strict` | Standard fields plus explicit verifier/dependency/environment basis, independent review for affected risk, specialist or separate batches when required, and assessed carry-forward. |

These additions never relax canonical Requirement, Acceptance Item, Journey,
review finding, gap, freeze, remediation, controlled-reopen, or Closure Packet
truth.
