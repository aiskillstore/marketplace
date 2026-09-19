# RVTF Bounded Review Governance

Use bounded review governance when review findings can block closure, expand
scope, or require remediation. It controls the review lifecycle; it does not
replace requirement truth, finding classification, gap ledgers, scope
amendments, or the Completion Gate.

## Core Invariants

1. No finding becomes implementation work without RVTF classification and a
   requirement decision.
2. Review dimensions are lenses, not new requirements.
3. A frozen finding set cannot downgrade a required gap or make weak evidence
   strong.
4. Every batch in an epoch must review the declared subject revision.
5. Freeze requires complete declared-dimension coverage, including explicit
   no-finding results.
6. Reviewer limitations and blocked dimensions stay visible.
7. Remediation may iterate, but unrelated scope invalidates the current freeze.
8. Review closure is a sub-gate; the full RVTF Completion Gate remains global.
9. Reopen records explicit affected requirements and dimensions and creates a
   scoped new epoch.
10. Existing RVTF artifacts remain valid when the applicability gate does not
    require review governance.
11. Keep the material subject, terminal review verdict, and receipt-only
    finalization distinct; recording an already issued verdict does not by
    itself create another review subject.
12. Receipt-only finalization is a narrow host-assessed terminal operation, not
    an implementer-declared bypass. Ambiguous changes are material by default.

## When It Applies

| RVTF mode | Review governance behavior |
| --- | --- |
| `discovery` | Not required because there is no completion claim. Record risks and candidate review needs as assumptions. |
| `lite` | Optional compact batch. Existing finding classification is enough for small, low-risk work. |
| `standard` | Record review applicability. Bounded governance is required when formal review is planned, multiple review passes exist, or review findings can block closure or expand scope. |
| `strict` | Bounded governance and independent-from-implementer review evidence are required for the affected risk scope. Missing independence keeps review closure incomplete or blocked. |

Activate bounded review governance when one or more conditions hold:

- the host workflow invokes formal reviewers;
- multiple review passes or review roles are expected;
- review findings can change scope or block a completion claim;
- strict-mode risk requires independent evidence;
- a prior review already produced findings requiring remediation.

For `standard`, `not_required` is valid only with a rationale showing that no
formal review lifecycle is part of the delivery decision.

## Subject Model

Attach governance to a stable `scope_ref`, not to a specific host unit. Examples:

- `task:storage-cutover-4`
- `increment:authentication-retry`
- `phase:p1.6`
- `release:2.0.0`
- `document:architecture-decision-17`
- `skill:tracing-requirements-to-verification`

Bind each review epoch to one or more stable subject references:

```yaml
subject_refs:
  - kind: git-commit
    ref: repository
    revision: def456
  - kind: document
    ref: docs/design.md
    revision: sha256:0123abcd
```

RVTF does not prescribe how revisions are generated. It only requires a stable
value that lets reviewers and closure checks identify what was reviewed.

## Review Dimensions

Dimensions are review lenses. Selecting one does not create work; findings still
flow through the existing classification table.

Baseline dimensions apply whenever bounded review governance is active:

| Dimension | Review question |
| --- | --- |
| `requirement-fidelity` | Does the subject satisfy intended requirements without missing or unapproved extra behavior? |
| `impact-and-ownership` | Which states, interfaces, writers, readers, callers, consumers, and owners are affected? |
| `verification-and-closure` | Does evidence directly prove acceptance, and are gaps and residual risks explicitly decided? |

Triggered dimensions require an applicability decision:

| Dimension | Typical trigger |
| --- | --- |
| `state-and-compatibility` | Persistent state, schemas, public APIs, protocols, migrations, or compatibility promises |
| `concurrency-and-recovery` | Multiple writers, asynchronous work, retries, locks, partial success, crashes, or recovery |
| `trust-security-and-privacy` | Identity, authorization, external input, secrets, sensitive data, or cross-boundary access |
| `performance-and-resources` | Hot paths, large inputs, batching, potentially unbounded data, memory, disk, network, or latency constraints |
| `operations-and-observability` | Rollout, rollback, background processing, telemetry, audit, diagnosis, or production operation |

Applicability values:

- `required`
- `not_applicable` with a concise rationale

A reviewer may challenge `not_applicable` only by identifying a concrete trigger
in the reviewed subject or governing requirements. The challenge is a contract
gap to resolve before complete coverage; it is not automatic feature scope.

Generic naming, formatting, and refactoring preferences remain host quality
concerns unless they threaten an existing requirement, accepted cross-cutting
constraint, or maintainability standard.

## Artifact Sequence

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

Every finding still enters the canonical `review_findings` ledger and uses the
existing classifications.

### Review Applicability

```yaml
review_applicability:
  scope_ref: phase:p1.6
  decision: required
  mode: bounded
  rationale: Multiple independent reviews can block phase closure.
```

Use `decision: not_required` only with a rationale and omit the contract.
Closed 0.4 standard/strict packets always record this decision. `required`
means the contract and closed epoch receipt resolve; strict closure cannot use
`not_required`.
Suggested governance modes:

- `bounded`
- `independent`

### Review Contract

```yaml
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
    - id: concurrency-and-recovery
      applicability: not_applicable
      rationale: The reviewed change has no asynchronous or multi-writer behavior.
  expected_batches:
    - id: requirements-review
      host_kind: goal-backward-validation
      dimensions: [requirement-fidelity, impact-and-ownership]
    - id: quality-risk-review
      host_kind: adversarial-review
      dimensions: [verification-and-closure]
  exclusions:
    - Performance optimization not required by current acceptance criteria.
```

The contract defines expected impact and review surface before implementation.
Impact surface categories may be empty with a rationale, but do not silently omit
them when `impact-and-ownership` is active.

### Review Cadence And Child Coverage

Version 0.4 review contracts add explicit cadence and economy policy without
changing the existing freeze, remediation, closure, or controlled-reopen
authority:

```yaml
review_contract:
  id: RC-P16-001
  scope_ref: milestone:p1.6
  cadence: milestone
  child_scope_policy: covered_at_parent
  covered_child_scope_refs:
    - unit:p1.6-replay
  batch_combination_policy: combined_allowed
  host_native_required_batches:
    - host:task-review
  independence:
    required: false
```

Cadence values are:

- `unit`: each Unit has its own formal review boundary;
- `batch`: a stable set of Units is reviewed together;
- `milestone`: formal coverage is collected after Milestone convergence;
- `host_native`: RVTF maps a mandatory host lifecycle without replacing it.

With `child_scope_policy: covered_at_parent`, list every intended child in
`covered_child_scope_refs`. Before the parent review actually runs, the child
records `review_state: pending_at_parent`. This is an explicit future
obligation, never proof, a passed review, or permission to close a Unit whose
own contract requires formal review; that Unit's disposition remains
`incomplete`. After review closes, change the child to
`review_state: covered_at_parent` only when an actual closed epoch and its
accepted batch or assessed carry-forward cover the child at the closure
packet's exact subject revision. Associate only child changes present in that
revision. A contract declaration, planned batch, or stale parent receipt cannot
support `covered_at_parent` or closure.

Parent coverage does not remove a host-native Unit, task, build, phase, merge,
or ship review. Every entry in `host_native_required_batches` requires an actual
batch receipt and must be accepted by review closure; a planned batch or future
parent epoch is insufficient.

### Combination, Separation, And Independence

`batch_combination_policy` values are:

- `combined_allowed`: one qualified batch may explicitly cover multiple
  dimensions when the host permits it;
- `separate_required`: expertise, segregation of duties, or governing policy
  requires distinct batches;
- `host_native`: preserve the host's actual reviewer roles and batch fan-out.

Review dimensions never imply a one-to-one reviewer or batch count. Strict
independence is a relationship-to-implementer requirement and is distinct from
forced separate batches: one independent, qualified combined batch may satisfy
several dimensions when no specialist or host constraint requires separation.
Conversely, combination cannot erase specialist expertise, segregation, strict
independence, or a host-native batch.

At closure, match each `expected_batches[].host_kind` and assigned `dimensions`
only against complete batches or valid carry-forward named by the current
closure. A historical batch with the same host kind is not an assignment
receipt. `separate_required` assignments consume distinct source batches;
the validator finds a complete matching across all eligible accepted providers
rather than greedily consuming list order. `combined_allowed` may reuse one
qualified combined batch. Evaluate independence across required dimensions
only, so a supplemental implementer self-check does not invalidate otherwise
independent required coverage.

### Review Epoch

```yaml
review_epochs:
  - id: RE-P16-001
    contract: RC-P16-001
    subject_refs:
      - kind: git-commit
        ref: repository
        revision: def456
    status: collecting
```

Suggested review lifecycle statuses:

- `collecting`
- `frozen`
- `remediating`
- `closed`
- `reopened`

### Review Batch

```yaml
review_batches:
  - id: RB-P16-REQ-001
    epoch: RE-P16-001
    host_kind: goal-backward-validation
    subject_refs:
      - kind: git-commit
        ref: repository
        revision: def456
    reviewer:
      role: requirements-reviewer
      relationship_to_implementer: independent
      reviewer_ref: optional-opaque-reference
    dimension_coverage:
      - dimension: requirement-fidelity
        status: covered
        findings: [RF-P16-001]
      - dimension: verification-and-closure
        status: covered
        findings: []
    coverage_status: complete
    limitations: []
```

Dimension coverage statuses:

- `covered`
- `partial`
- `blocked`

`coverage_status: complete` means every dimension assigned to that batch was
traversed and limitations were disclosed. It does not assert that no unknown
defect exists.

### Finding Freeze

Freeze only when:

- every expected batch exists;
- all assigned required dimensions are covered;
- every finding uses existing RVTF classification;
- every required owner decision is recorded before remediation begins;
- all batches refer to the expected subject revision;
- no undisclosed limitation prevents declared coverage.

```yaml
review_freeze:
  id: RFR-P16-001
  epoch: RE-P16-001
  subject_refs:
    - kind: git-commit
      ref: repository
      revision: def456
  accepted_batches: [RB-P16-REQ-001, RB-P16-RISK-001]
  frozen_findings: [RF-P16-001, RF-P16-002]
  decision_owner: delivery-coordinator
  frozen_at: 2026-07-21T08:00:00Z
```

The freeze defines bounded remediation scope for the epoch. It does not declare
delivery complete.

### Remediation Cycle

Each cycle records:

- frozen findings addressed;
- new subject revision;
- verification evidence produced;
- direct regressions or changed assumptions;
- whether unrelated scope was introduced.

Do not restart unrestricted review for each fix. Closure review checks known
findings, changed evidence, and direct remediation risk. If unrelated work
changes the reviewed subject, invalidate the freeze and amend or reopen the
epoch.

### Immutable Batches, Impact Assessment, And Carry-Forward

A historical `review_batch` is immutable evidence: keep its original epoch and
subject revision. Never relabel it with the remediation revision.

When a later revision leaves accepted dimensions unchanged, record both the
impact assessment and the applicability decision:

```yaml
review_impact_assessments:
  - id: RIA-P16-001
    source_batch_ref: RB-P16-SECURITY-001
    from_revision: def456
    to_revision: fed789
    changed_surface: [performance-remediation]
    unchanged_dimensions: [trust-security-and-privacy]
    rationale: The authorization and data-boundary surface is unchanged.
    assessor_ref: reviewer:security
    decision: accepted

review_coverage_carry_forward:
  - id: RCF-P16-001
    source_batch_ref: RB-P16-SECURITY-001
    target_epoch: RE-P16-002
    from_revision: def456
    to_revision: fed789
    unchanged_dimensions: [trust-security-and-privacy]
    impact_assessment_ref: RIA-P16-001
    assessor_ref: reviewer:security
    decision: accepted
```

The source batch and impact assessment must resolve. `from_revision` equals the
source batch's actual historical revision; `to_revision`, unchanged dimensions,
assessor, rationale, and accepted decision agree with the impact assessment.
Carry only dimensions the source batch actually covered. `target_epoch` is
mandatory; when closure accepts the carry-forward it equals the closure epoch,
and `to_revision` equals that epoch's revision and the closure subject revision.

Run a bounded delta batch for changed dimensions and changed evidence. If impact
cannot establish that a dimension is unchanged, create a new batch or use the
existing controlled-reopen rules. Carry-forward narrows repeated coverage; it
does not mutate freeze, weaken a finding, manufacture future evidence, or
replace review closure and the full Completion Gate.

### Review Closure

Review closure checks:

- every frozen required finding has a valid close decision;
- remediation evidence directly addresses each finding;
- evidence supporting affected requirements remains valid;
- remediation introduced no blocking regression;
- late findings have explicit intake and reopen decisions;
- unrelated subject changes did not bypass contract review.

After review closure, run the full RVTF Completion Gate over all current
requirements, evidence, gaps, amendments, residual risk, and next-phase entry
conditions.

### Terminal Review Verdict And Receipt-Only Finalization

Use this behavioral rule when a final review or scoped re-review has already
issued a verdict for a stable subject, and the only remaining operation is to
record that verdict and derive closure state.

Keep three concepts distinct:

- **Material Subject:** the exact implementation, requirements, evidence,
  findings, risk, package, release, or other delivery truth the reviewer
  assessed.
- **Terminal Review Verdict:** independent review evidence bound to that exact
  material subject, including coverage, limitations, findings, and disposition.
- **Receipt-Only Finalization:** one terminal update that records the already
  issued verdict and derives only transitions explicitly authorized by it.

Stage 1 defines behavior only. It introduces no mandatory attestation sidecar,
terminal envelope, payload digest, signature, or new schema field.

Allowed receipt-only changes are limited to:

- attaching or registering the already issued terminal verdict or receipt;
- accepting only the review batch or verdict that was actually issued;
- closing only findings explicitly named and dispositioned by that verdict;
- resolving only gaps whose declared close condition is satisfied by those
  named finding dispositions;
- moving the matching review epoch to closed;
- deriving the delivery closure disposition when review was the sole remaining
  gate and every other current gate already passed;
- preserving truthful parent continuation and remaining-scope records.

Material changes include any change to:

- Requirement statement, validity, required scope, status, or child inventory;
- Acceptance Item criterion, verification method, status, evidence target, or
  gap relationship;
- Journey actor, goal, Step, expected outcome, path evidence, or status;
- Evidence Artifact result or Evidence Claim target, `proves`, coverage,
  validity, dependency basis, environment basis, or freshness;
- review applicability, contract, dimension assignment, independence rule,
  subject references, finding meaning, classification, or blocking impact;
- scope amendment, residual risk, owner acceptance, or host-gate truth;
- implementation, workflow, verifier, package, asset, release, migration,
  recovery, or rollback behavior and facts.

Before accepting receipt-only finalization:

1. Freeze and identify the exact material subject before terminal review.
2. Resolve a terminal verdict bound to that subject and preserve required
   reviewer independence and limitations.
3. Use a host-aware diff or repository assessment to prove the final update
   touches only the allowed receipt-only surface. Standalone YAML validation
   cannot prove repository materiality, reviewer identity, or locator truth.
4. Confirm every derived transition is explicitly authorized by the verdict
   and no unrelated status is promoted.
5. Run internal trace validation and any mandatory current-boundary host gate.
6. Stop. Do not dispatch another reviewer solely because the final update
   records the already issued verdict.

A boolean or prose declaration is not proof. The implementer cannot
self-attest that a mixed change is receipt-only. If the host-aware diff is
missing, the verdict does not resolve, or any changed surface is ambiguous or
outside the allowlist, treat the update as material. Classify its impact and use
carry-forward, bounded delta review, or controlled reopen as applicable.

### Controlled Reopen

Reopen creates a new scoped epoch; it does not turn the closed epoch into an
unrestricted review.

```yaml
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

Canonical reopen bases:

- `required_gap`
- `evidence_invalidated`
- `remediation_regression`
- `cross_cutting_risk`
- `accepted_scope_amendment`

## Late Finding Intake

Late findings use the same classifications as all other findings.

A late finding can reopen when it demonstrates:

- an existing requirement or acceptance criterion is not satisfied;
- evidence previously supporting `verified` is invalid, stale, or inapplicable;
- remediation directly introduced a regression;
- a safety, privacy, security, compatibility, data-integrity, performance, or
  observability constraint requires a new owner decision;
- a scope amendment has been accepted and blocks current closure.

Severity labels alone do not decide reopening. Trace impact plus owner decision
does.

The following do not automatically reopen the epoch:

- optional enhancements without accepted amendment;
- style preferences not linked to a requirement or accepted standard;
- speculative hardening without a concrete affected constraint;
- unrelated refactoring opportunities;
- findings outside declared delivery scope whose risk does not invalidate
  current evidence or requirements.

Record them as rejected, deferred, or accepted through existing RVTF decision
mechanisms. Freeze is not permission to discard them silently.

## Roles

| Role | Authority |
| --- | --- |
| `implementer` | Implements and remediates; cannot alone declare strict review coverage complete. |
| `reviewer` | Traverses assigned dimensions and reports findings and limitations; cannot alone accept new scope. |
| `coordinator` | Checks contract and batch completeness, freezes the finding set, and detects revision drift. |
| `delivery_owner` | Accepts or rejects scope amendments, residual risk, exceptional deferral, and controlled reopen decisions. |

One actor may hold multiple roles in `lite` or selected `standard` workflows.
Strict review must preserve reviewer independence for the affected risk scope.
Reviewer references may be opaque; RVTF does not require raw prompts, session
transcripts, personal identity, or host-specific session IDs.

## Failure Handling

| Condition | Required behavior |
| --- | --- |
| Expected batch missing | Keep epoch `collecting`; do not freeze. |
| Required dimension `partial` or `blocked` | Record limitation or gap; do not claim complete coverage. |
| Batches reference different revisions | Reject freeze until subject revisions converge. |
| Reviewer finds one blocker and omits remaining dimensions | Batch is incomplete regardless of finding validity. |
| Reviewers disagree | Preserve both findings or decisions and require coordinator or owner resolution. |
| Triggered dimension marked `not_applicable` | Return contract for correction before freeze. |
| Remediation fails verification | Continue bounded remediation for the frozen finding. |
| Remediation introduces direct regression | Record late finding and reopen on `remediation_regression`. |
| Unrelated work changes reviewed subject | Invalidate freeze and start or amend a review epoch. |
| Optional late improvement appears | Defer or reject unless an owner accepts an amendment. |
| Existing required behavior is missing after freeze | Reopen on `required_gap`, regardless of informal severity. |
| Verified evidence becomes invalid | Reopen on `evidence_invalidated`; restore evidence-based requirement handling. |
| Strict independent review is unavailable | Record a gap and keep review closure incomplete or blocked. |
| Terminal update only attaches an accepted verdict and authorized derived transitions | Run host-aware materiality assessment and final gates, then stop without another review. |
| Final update changes material truth or has ambiguous diff coverage | Reject receipt-only treatment and run impact assessment plus the applicable delta review or controlled reopen. |
