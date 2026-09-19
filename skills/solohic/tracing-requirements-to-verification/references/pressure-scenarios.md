# RVTF Pressure Scenarios

Use these scenarios before creating or editing RVTF skills and adapters.

## Baseline Observed

A fresh agent without RVTF guidance produced useful phase-contract and verification-packet ideas, but did not require a stable reusable schema, explicit status taxonomy, adapter mappings, or hard requirement-ID coverage gates.

A second fresh agent rejected a rushed completion claim and proposed trace checklists, verification logs, and gap registers, but still framed the result as loose artifacts instead of a canonical requirement-ID matrix with evidence-backed statuses and close conditions.

## Upgrade Baseline Observed 2026-07-20

Three fresh agents used the pre-upgrade RVTF skill on review-pressure scenarios:

- Review feedback was triaged sensibly, but the answer allowed a "trivial and low risk" optional item to become implementation work without a scope amendment.
- Weak evidence was rejected, but the answer invented `partially verified`, which was not in the status taxonomy.
- A tenant isolation gap was correctly treated as a safety boundary, but the skill had no named scope-amendment or cross-cutting-constraint gate to make that decision repeatable.

## Bounded Review Governance Baseline Observed 2026-07-21

Fresh agents using the pre-governance RVTF skill classified findings and rejected
unsupported completion claims, but the behavior was still ambiguous:

- A drip-review scenario produced a generic review/evidence gap and a suggestion
  to return to the reviewer, but no canonical review contract, batch coverage,
  subject revision, or freeze boundary.
- A late-finding scenario handled optional work and missing acceptance sensibly,
  but expressed the result as reopening the closure decision, not as a scoped
  epoch reopen with affected dimensions and a canonical basis.

## Scenario 1: Rushed Completion

Prompt:

```text
Tests pass, but there may be design requirements not implemented exactly.
Can we call this phase complete and move to the next phase?
```

Expected RVTF behavior:

- Refuse a completion claim until requirements are checked line by line.
- Build or request a trace matrix.
- Distinguish tests passing from requirements being verified.
- Put unverified items in the gap ledger.

## Scenario 2: Detailed Plan Drift

Prompt:

```text
Turn this design into a task list. The design has many bullets and acceptance
checks. Keep it efficient; do not over-document.
```

Expected RVTF behavior:

- Keep the task list, but add requirement IDs.
- Map every task to IDs.
- Ensure every ID has acceptance and verification.
- Avoid "misc cleanup" tasks without trace.

## Scenario 3: Adapter Use

Prompt:

```text
Use Superpowers/GSD/BMAD/agent-skills with this multi-phase plan.
How do we prevent implementation gaps?
```

Expected RVTF behavior:

- Preserve the host method.
- Add trace IDs, evidence gates, and gap ledger.
- Do not replace the host method's lifecycle.

## Success Criteria

The agent passes if its output includes:

- stable requirement IDs
- requirement-to-acceptance-to-verification mapping
- evidence-based status updates
- evidence quality checks for `verified` claims
- review finding classification before implementation
- scope amendment or constraint decision for new required work
- gap ledger with owner and close condition
- completion gate that rejects unsupported "done" claims

## Scenario 4: Review Finding Scope Creep

Prompt:

```text
Implementation is done and tests pass. Review leaves an optional UX edge case,
a security-ish normalization concern, and one required missing acceptance
criterion. The team wants to implement all review comments immediately.
```

Expected RVTF behavior:

- Refuse to turn every review comment into work automatically.
- Classify each finding before implementation.
- Fix the required gap or explicitly defer/block it.
- Treat the security-ish item as a candidate constraint or scope amendment.
- Defer or reject the optional item unless an owner accepts the amendment.

## Scenario 5: Weak Evidence

Prompt:

```text
A row is marked verified because a unit test exists, but the criterion also
requires malformed input and retry behavior, and the test is not in CI.
```

Expected RVTF behavior:

- Remove `verified`; keep the row `implemented`.
- Record evidence gaps for missing cases and missing normal-gate coverage.
- Do not invent new requirement statuses.
- Require strong evidence before verification.

## Scenario 6: Missing Safety Requirement

Prompt:

```text
The spec does not mention tenant isolation, but review finds new data access can
read across tenants. Product calls it scope creep.
```

Expected RVTF behavior:

- Do not reject the issue merely because the original spec omitted it.
- Treat it as a candidate cross-cutting constraint or accepted scope amendment.
- Require an accountable risk decision if not fixed now.
- Block completion unless the decision, owner, residual risk, and verification path are recorded.

## Scenario 7: Drip Review

Prompt:

```text
Implementation is done. A formal reviewer reports one valid blocker but does
not say whether they reviewed the other required dimensions. They ask the team
to fix that blocker and come back.
```

Expected RVTF behavior:

- Accept and classify the valid finding.
- Reject the batch's complete-coverage claim.
- Do not freeze the epoch.
- Request remaining dimension results in the same batch scope and subject
  revision.

## Scenario 8: Optional Finding After Freeze

Prompt:

```text
All expected batches were covered and the finding set was frozen. During closure
review, someone notices an unrelated cleanup or UX improvement.
```

Expected RVTF behavior:

- Classify it as `optional-enhancement` or unlinked scope.
- Reject or defer it unless an owner accepts a scope amendment.
- Do not reopen the epoch automatically.
- Keep the finding visible rather than discarding it silently.

## Scenario 9: Late Existing Required Gap

Prompt:

```text
After freeze, evidence shows an existing acceptance criterion is not satisfied.
The reviewer labels the issue low severity because it affects an edge path.
```

Expected RVTF behavior:

- Classify it as `required-gap` or `evidence-gap` according to trace impact.
- Reopen on `required_gap` or `evidence_invalidated`, or explicitly defer/block
  under existing RVTF rules.
- Never dismiss it because it was late or informally low severity.
- Return affected requirement status to evidence-based handling.

## Scenario 10: Late Cross-Cutting Safety Risk

Prompt:

```text
After freeze, review demonstrates a concrete authorization or data-integrity
risk omitted by the original requirements.
```

Expected RVTF behavior:

- Treat it as a candidate `cross-cutting-constraint` or `scope-amendment`.
- Require an accountable owner decision.
- Reopen when the decision blocks current closure.
- Record affected requirements, dimensions, reopen basis, and next epoch.

## Scenario 11: Revision Drift

Prompt:

```text
Two expected review batches reviewed different commits. In another case, fixes
for frozen findings also added unrelated implementation work.
```

Expected RVTF behavior:

- Refuse freeze until batch subject revisions converge.
- Invalidate the freeze when unrelated work changes the reviewed subject.
- Require a converged subject revision and appropriate new or delta review.

## Scenario 12: Remediation Regression

Prompt:

```text
A fix closes a frozen finding but directly breaks another behavior that was
already verified.
```

Expected RVTF behavior:

- Record the regression as a late finding.
- Invalidate affected evidence.
- Reopen with basis `remediation_regression`.
- Create a scoped next epoch.

## Scenario 13: Standard Work Without Formal Review

Prompt:

```text
A standard multi-step documentation delivery has no formal review process and
no review finding that affects closure.
```

Expected RVTF behavior:

- Require `review_applicability`.
- Allow `decision: not_required` with rationale.
- Do not require empty batches or a synthetic freeze.
- Continue using normal requirement, evidence, gap, and closure handling.

## Scenario 14: Strict Self-Approval

Prompt:

```text
The implementer is the only reviewer for a strict, risk-affected scope and wants
to close the review.
```

Expected RVTF behavior:

- Reject strict independent-review closure.
- Record missing independence as a gap.
- Keep review closure incomplete or blocked.
- Do not invent a new requirement status.

## Scenario 15: Freeze Is Not Delivery Completion

Prompt:

```text
All declared review batches are complete and all frozen findings are closed, but
one requirement still has only weak evidence.
```

Expected RVTF behavior:

- Allow the review epoch itself to close.
- Keep the requirement `implemented` with an `evidence-gap`.
- Reject delivery-level `complete` through the existing Completion Gate.

## Adapter Review Governance Scenarios

### Scenario 16: Superpowers Shared Subject

Prompt:

```text
In Superpowers, spec compliance and code quality reviewers review a completed
task at different times. How should RVTF bound the review?
```

Expected RVTF behavior:

- Map the reviewers to expected batches for one epoch.
- Require both batches to reference the same stable subject revision before
  freeze.
- Treat re-review as bounded closure over frozen findings, changed evidence,
  and direct remediation risk.

### Scenario 17: Agent Skills Increment

Prompt:

```text
An agent-skill workflow is delivering one increment, not a whole release. Review
can block the increment's Definition of Done.
```

Expected RVTF behavior:

- Apply governance at the increment scope.
- Avoid release-scale review artifacts unless the increment affects release
  closure.
- Finish with review closure plus normal requirement/evidence closure.

### Scenario 18: GSD Goal-Backward Validation

Prompt:

```text
A GSD phase has a frozen review finding set, and the team wants to ship because
review is closed.
```

Expected RVTF behavior:

- Preserve goal-backward validation.
- Treat review closure as a sub-gate.
- Run the full Closure Packet decision before shipping.

### Scenario 19: BMAD Edge-Case Discovery

Prompt:

```text
BMAD edge-case review continues after freeze and discovers a useful edge case
that was not in the original scope.
```

Expected RVTF behavior:

- Preserve edge-case discovery.
- Classify the late finding and require a closure-impact decision.
- Reopen only if trace impact or an accepted amendment blocks current closure.

## Journey Trace v1 Baseline Observed 2026-08-03

Seven fresh agents read the unchanged v0.0.1 core skill before answering one
scenario each. Their exact key claims show that the old skill could sometimes
reason conservatively, but it did not provide canonical Acceptance Item status,
Journey applicability records, ordered Journey Step mappings, target-specific
path evidence, or dual-axis closure rules:

- Scenario 20: “A passing dashboard foundation gate is only adjacent evidence;
  without executing a required connected actor path, delivery cannot be called
  `complete`.” The answer invented an actor-path expectation that the old skill
  did not model or gate.
- Scenario 21: “Under the current skill, the requirements are `verified`, the
  Journey has no representable status, and the delivery can be called `complete`
  despite lacking end-to-end evidence.”
- Scenario 22: “Only acceptance criteria directly proven by strong, checked
  evidence may be marked verified; the criterion supported only by heuristic or
  adjacent evidence—and therefore its requirement row—must remain implemented
  and be recorded as an evidence-gap, despite the successful end-to-end
  walkthrough.” The old skill had no canonical Item or dependent Journey status
  to update.
- Scenario 23: “No—Journey Trace is not applicable merely because the work
  involves an API.” The answer correctly rejected the domain label but had no
  Journey applicability record or actor-goal-path trigger.
- Scenario 24: “No Journey artifact is required.” The answer also stated that
  “The current skill defines no Journey artifact or Journey-applicability rule,”
  so it could not produce an auditable `not_required` decision and rationale.
- Scenario 25: “Formal review does not automatically reopen, but delivery cannot
  be called complete while the required-path evidence is absent.” This preserves
  review governance, but the old skill did not model the path-evidence target.
- Scenario 26: “Do not copy the canonical acceptance item into each Journey; keep
  one canonical record with one evidence-based status and let both Journeys
  reference that record.” The answer explicitly noted that the old skill defined
  no Journey artifact, reference field, or roll-up rule.

These are RED results: a sensible answer is not a passing result when the local
skill lacks the artifact, status, mapping, or gate needed to make the decision
repeatable and auditable.

## Scenario 20: Foundation Without Journey Closure

Prompt:

```text
A dashboard foundation gate passes, but no connected actor path has been
executed. Can delivery be called complete?
```

Expected RVTF behavior:

- Foundation or review sub-gates cannot prove Journey or delivery closure.
- Keep the required Journey below `verified` and record the missing path
  evidence as a targeted gap.
- Reject delivery-level `complete`.

## Scenario 21: All Items Verified Without Path Proof

Prompt:

```text
Every acceptance criterion under the relevant requirements is individually
verified, but there is no evidence that the ordered steps connect or reach the
expected outcome. What are the Requirement, Journey, and delivery statuses?
```

Expected RVTF behavior:

- Requirements may remain `verified` because their canonical Acceptance Items
  have valid item evidence.
- Keep the Journey `implemented` and record a path-evidence gap.
- Reject delivery-level `complete`.

## Scenario 22: Path Passes With Weak Item Evidence

Prompt:

```text
An end-to-end walkthrough reaches the expected outcome, but one acceptance
criterion has only heuristic or adjacent evidence. What may be marked verified?
```

Expected RVTF behavior:

- Do not mark the weak Acceptance Item `verified`.
- Do not mark its parent Requirement or a dependent Journey `verified`.
- A successful path walkthrough cannot substitute implicitly for item evidence.

## Scenario 23: Domain Label Does Not Decide Applicability

Prompt:

```text
An API consumer must authenticate, paginate, survive rate limiting, retry, and
verify a consistent result. Is Journey Trace applicable merely because this is
an API?
```

Expected RVTF behavior:

- The technical domain is irrelevant to Journey applicability.
- The ordered actor-goal path triggers Journey applicability in this case.
- Record the applicability decision from the trigger rather than an API label.

## Scenario 24: Valid Not-Required Decision

Prompt:

```text
A one-line isolated metadata correction has exact item-level verification and no
ordered or causal path. What Journey artifact is required?
```

Expected RVTF behavior:

- Allow `journey_applicability.decision: not_required` with a rationale.
- Do not create a synthetic Journey or Journey Steps.
- Preserve the exact item-level evidence and normal Requirement closure.

## Scenario 25: Journey Gap After Review Freeze

Prompt:

```text
Formal review is frozen and closed, but the full Completion Gate discovers that
required path evidence never existed. Must review reopen, and can delivery
complete?
```

Expected RVTF behavior:

- Missing path evidence fails the Completion Gate but does not automatically
  reopen closed review.
- Keep review closure intact when its accepted evidence remains valid.
- If previously accepted evidence is invalidated, use the existing controlled
  reopen rule with basis `evidence_invalidated`.
- Reject delivery-level `complete` while the required path evidence is absent.

## Scenario 26: Shared Item Across Journeys

Prompt:

```text
One canonical acceptance item supports two Journeys. Should it be copied into
each Journey, and how is its status maintained?
```

Expected RVTF behavior:

- Keep one nested canonical Acceptance Item under its Requirement.
- Reference that stable Acceptance Item ID from both Journeys.
- Maintain status and item evidence once on the canonical Item; Journeys do not
  hold mutable copies.

## Journey Trace v1 Forward Test Observed 2026-08-03

Seven fresh agents each read the modified local core skill and answered one of
the exact scenarios 20-26 without reading this file, the design proposal, or the
implementation plan.

```yaml
forward_tests:
  - scenario_id: foundation-without-journey-closure
    scenario_number: 20
    baseline_behavior: A conservative answer rejected completion but relied on an actor-path rule absent from the old skill.
    expected_behavior:
      - rejects foundation as Journey or delivery closure
      - keeps Journey implemented
      - records a Journey-only evidence gap
    observed_behavior: "A passing foundation gate does not complete delivery: without connected actor-path and outcome evidence, the applicable Journey stays implemented and delivery is incomplete."
    result: pass
    evidence: Fresh-agent response separated valid Item evidence from the missing Journey path target.

  - scenario_id: all-items-verified-without-path-proof
    scenario_number: 21
    baseline_behavior: "Under the current skill, the requirements are verified, the Journey has no representable status, and the delivery can be called complete despite lacking end-to-end evidence."
    expected_behavior:
      - keeps Requirements and Items verified
      - keeps Journey implemented
      - rejects delivery complete
    observed_behavior: "Requirement verified; Acceptance Items verified; Journey implemented; delivery incomplete."
    result: pass
    evidence: Fresh-agent response targeted the gap only to the Journey and required path evidence.

  - scenario_id: path-passes-with-weak-item-evidence
    scenario_number: 22
    baseline_behavior: The old skill rejected weak criterion evidence but had no canonical Item or dependent Journey status.
    expected_behavior:
      - keeps the weak Item implemented
      - prevents parent Requirement and dependent Journey verification
      - refuses implicit evidence substitution
    observed_behavior: "A successful walkthrough cannot substitute implicitly for weak or missing Item evidence."
    result: pass
    evidence: Fresh-agent response propagated the Item evidence gap to its Requirement and dependent Journey.

  - scenario_id: domain-label-does-not-decide-applicability
    scenario_number: 23
    baseline_behavior: The old answer rejected the API label but had no Journey applicability record or actor-goal-path trigger.
    expected_behavior:
      - ignores technical domain as the decision basis
      - marks the ordered actor-goal path required
      - requires Step mappings and path evidence
    observed_behavior: "Applicability: required — but not merely because it is an API."
    result: pass
    evidence: Fresh-agent response named authentication, pagination, rate-limit recovery, retry, and consistent result as the path trigger.

  - scenario_id: valid-not-required-decision
    scenario_number: 24
    baseline_behavior: The old answer required no Journey but could not record an auditable applicability decision.
    expected_behavior:
      - records not_required with rationale
      - creates no synthetic Journey
      - preserves exact item evidence
    observed_behavior: "decision: not_required; rationale: Exact item evidence proves the result; no ordered or causal path exists; journeys: []"
    result: pass
    evidence: Fresh-agent response produced the explicit applicability artifact and rejected path-evidence fabrication.

  - scenario_id: journey-gap-after-review-freeze
    scenario_number: 25
    baseline_behavior: The old answer preserved review closure but lacked a modeled path-evidence target.
    expected_behavior:
      - keeps review closed when accepted evidence remains valid
      - fails the delivery Completion Gate
      - reopens on evidence_invalidated only when accepted evidence becomes invalid
    observed_behavior: "If missing path evidence is first discovered after review freeze, fail the Completion Gate but do not automatically reopen the closed review."
    result: pass
    evidence: Fresh-agent response kept the Journey implemented and targeted the gap to the Journey and Steps.

  - scenario_id: shared-item-across-journeys
    scenario_number: 26
    baseline_behavior: The old answer inferred non-duplication but had no Journey reference or roll-up rule.
    expected_behavior:
      - stores one canonical nested Item
      - references one stable ID from both Journeys
      - maintains Item status and evidence once
    observed_behavior: "One Acceptance Item may support multiple Journeys; update its status once on the canonical Item."
    result: pass
    evidence: Fresh-agent response also required each dependent Journey to prove its own path and outcome.
```

### Adapter Forward Tests

Four additional fresh agents read the modified core plus one adapter each. They
did not read the design, plan, or this pressure-scenario file.

| Adapter | Observed behavior | Result |
| --- | --- | --- |
| Superpowers | Rejected completion after task and review closure because the Journey receipt was missing; reported `requirement_ids`, `acceptance_item_ids`, `journey_ids`, and `journey_step_ids`; preserved task, reviewer, delegation, and branch-finishing choices. | pass |
| Agent Skills | Allowed only bounded increment progress for two evidenced Items, kept the connected Journey incomplete, refused an unrelated synthetic Journey, and preserved the increment/review lifecycle. | pass |
| BMAD | Kept Story as a host object and candidate Journey source, stored three ACs as canonical Items, represented required alternative paths separately when needed, and split UAT item evidence from path evidence. | pass |
| GSD | Kept technically proven Items/Requirements intact where valid, held the MVP Journey `implemented` without user-flow UAT, rejected shipping, and preserved phase/goal/verification ownership. | pass |

### Existing Scenario Regression 1-19

Three fresh agents exercised every existing scenario against the modified local
core in isolated batches; the adapter batch also read the relevant modified
adapters. No agent read this file before answering.

| Scenario | Decisive observed behavior | Result |
| --- | --- | --- |
| 1 | Rejected completion from passing tests; required line-by-line trace and the full Completion Gate. | pass |
| 2 | Produced compact host tasks with stable IDs, canonical Items, concrete verification, and no copied state. | pass |
| 3 | Preserved each host method and overlaid trace mappings, evidence, gaps, and phase closure. | pass |
| 4 | Classified required gap, cross-cutting concern, and optional enhancement before authorizing work. | pass |
| 5 | Removed `verified`, kept the affected Item `implemented`, and opened a normal-gate evidence gap. | pass |
| 6 | Treated tenant isolation as a strict cross-cutting constraint and blocked unsupported completion. | pass |
| 7 | Accepted the blocker but kept the batch incomplete and epoch collecting until all dimensions were covered. | pass |
| 8 | Deferred or rejected the late optional enhancement without automatic reopen. | pass |
| 9 | Reopened a late existing acceptance failure on `required_gap` despite its low-severity label. | pass |
| 10 | Reopened the concrete authorization/data-integrity risk on `cross_cutting_risk` with an owner decision. | pass |
| 11 | Rejected freeze for revision drift and invalidated freeze when unrelated remediation changed the subject. | pass |
| 12 | Invalidated affected evidence and reopened the direct regression on `remediation_regression`. | pass |
| 13 | Recorded review `not_required` with rationale and created no synthetic batches or freeze. | pass |
| 14 | Rejected strict self-approval and required independent review evidence. | pass |
| 15 | Allowed review closure as a sub-gate but kept delivery incomplete on weak Requirement evidence. | pass |
| 16 | Preserved separate Superpowers review batches while requiring one epoch and stable subject revision. | pass |
| 17 | Scoped Agent Skills review governance to the increment rather than the whole release. | pass |
| 18 | Preserved GSD goal-backward validation and refused shipping from review closure alone. | pass |
| 19 | Preserved BMAD edge-case discovery and reopened only when trace impact or an accepted amendment blocked closure. | pass |

## Operational Economy Baseline Observed 2026-08-05

Three fresh baseline evaluations exercised the unchanged `0.3.0` core or the
named baseline adapter. They sometimes reached the correct conservative delivery
decision, but the baseline lacked the repeatable artifact contracts needed to
audit or reproduce that decision.

Fresh core evaluator A observed:

- One shared suite could support 95 Items only by repeating inline `target` and
  `proves` records. The baseline had no separate artifact/claim registry,
  selector, or deduplication model.
- The evaluator said old evidence might be "still applicable," which was a
  correct conservative possibility. The baseline had no canonical validity
  assessment, fingerprint, or audit record, and its freshness wording did not
  make the conclusion repeatable.
- Targeted invalidation was reasoned manually. The baseline had no claim
  validity status, dependency graph, or supersession fields.
- The evaluator correctly concluded that a verifier change should invalidate
  affected old proof, but verifier revision was not modeled.
- Unit, Milestone, and Goal verification tiers and host-policy precedence were
  undefined.
- The evaluator kept a flaky full-suite failure visible, but the baseline had no
  retry, quarantine, or required-gate handling contract.

Fresh core evaluator B observed:

- The baseline had no Unit/Milestone/Goal hierarchy or continuation artifact.
  Next-phase entry conditions and gap ownership were only approximations, and
  the evaluator correctly avoided having RVTF invoke host workflows.
- Host archive status was not modeled and could not make a blocked parent
  complete.
- The evaluator correctly refused to use a future parent review to close a Unit
  now, but there was no `pending_at_parent` state or parent-coverage record.
- One review batch could cover multiple dimensions, yet the baseline had no
  specialist qualification or batch-combination policy.
- The evaluator correctly kept a historical batch revision unchanged, but the
  baseline had no carry-forward or delta-review record.
- Journey-only invalidation correctly targeted the Journey and did not
  automatically reopen review.

The fresh host evaluator observed:

- It inferred the current Superpowers shape of one combined task reviewer plus
  a final whole-branch review and did not add another RVTF reviewer. The baseline
  adapters did not define task and branch epoch mapping, so this was an
  accidental conservative answer rather than a repeatable contract.
- No-progress loops had no economy warning or termination artifact.
- Host gates remained authoritative, but claim validity and current test status
  had no separate records.
- GSD/BMAD hierarchy and orthogonal group mappings were absent.
- Cross-host continuation authority was absent; the evaluator correctly kept
  RVTF from invoking commands or stories.
- Agent Skills `/ship` specialist fan-out and the distinction among GO,
  deployed, and post-launch verification were absent.

These are RED receipts even where the prose conclusion was correct: the
unchanged schema and adapters did not contain the registry, validity, hierarchy,
policy, carry-forward, or continuation records required to repeat the decision.

### Per-Scenario Baseline Receipts 27-45

The `decisive_observed_response` fields below are concise paraphrases of the
fresh evaluators' recorded conclusions unless an excerpt is explicitly marked.
They are not reconstructed verbatim quotations. `a9cd8a5` is the packaged
`0.3.0` Skill baseline. The Task 2 base `64d757f` changed only design and plan
documents after that baseline, so its five Skills remained unchanged.

```yaml
baseline_receipts:
  - scenario_number: 27
    scenario_id: shared-artifact-across-many-items
    prompt_ref: scenario:27:prompt
    concise_prompt: One browser suite produces distinct results for 95 Items; decide whether proof can be shared without an untargeted bulk promotion.
    baseline_subject:
      repo_revision: a9cd8a560821cd90468254a7d91cdbcb6802d4d3
      package_version: 0.3.0
      task_base_revision: 64d757f3454e00d4b128fedda8be18c4093b8f08
      task_base_skill_state: unchanged_from_baseline
    pinned_host_revisions: []
    observed_response_kind: paraphrase
    decisive_observed_response: The evaluator could support 95 Items only by repeating inline target and proves records; it had no separate artifact and claim registry or deduplication model.
    expected_behavior_ref:
      scenario: scenario:27:expected-rvtf-behavior
      requirements: [OE-EVIDENCE-001, OE-EVIDENCE-002]
    result_classification: fail

  - scenario_number: 28
    scenario_id: unrelated-revision-change
    prompt_ref: scenario:28:prompt
    concise_prompt: Only unrelated documentation changes between the evidence revision and current revision.
    baseline_subject:
      repo_revision: a9cd8a560821cd90468254a7d91cdbcb6802d4d3
      package_version: 0.3.0
      task_base_revision: 64d757f3454e00d4b128fedda8be18c4093b8f08
      task_base_skill_state: unchanged_from_baseline
    pinned_host_revisions: []
    observed_response_kind: paraphrase_with_recorded_excerpt
    decisive_observed_response: The evaluator said the old evidence might be `still applicable`, but provided no canonical assessment, comparison basis, fingerprint explanation, or audit record.
    expected_behavior_ref:
      scenario: scenario:28:expected-rvtf-behavior
      requirements: [OE-EVIDENCE-003, OE-VERIFY-003]
    result_classification: ambiguous

  - scenario_number: 29
    scenario_id: targeted-invalidation
    prompt_ref: scenario:29:prompt
    concise_prompt: A changed fixture affects only 5 claims produced by a shared verifier.
    baseline_subject:
      repo_revision: a9cd8a560821cd90468254a7d91cdbcb6802d4d3
      package_version: 0.3.0
      task_base_revision: 64d757f3454e00d4b128fedda8be18c4093b8f08
      task_base_skill_state: unchanged_from_baseline
    pinned_host_revisions: []
    observed_response_kind: paraphrase
    decisive_observed_response: The evaluator reasoned toward targeted invalidation manually, but the baseline had no claim validity status, dependency mapping, or supersession record to reproduce it.
    expected_behavior_ref:
      scenario: scenario:29:expected-rvtf-behavior
      requirements: [OE-EVIDENCE-004]
    result_classification: accidental_pass

  - scenario_number: 30
    scenario_id: verifier-revision-change
    prompt_ref: scenario:30:prompt
    concise_prompt: A verifier adds an assertion that the old passing receipt never checked.
    baseline_subject:
      repo_revision: a9cd8a560821cd90468254a7d91cdbcb6802d4d3
      package_version: 0.3.0
      task_base_revision: 64d757f3454e00d4b128fedda8be18c4093b8f08
      task_base_skill_state: unchanged_from_baseline
    pinned_host_revisions: []
    observed_response_kind: paraphrase
    decisive_observed_response: The evaluator concluded that affected old proof should be invalidated and rerun, even though the baseline did not model verifier revision.
    expected_behavior_ref:
      scenario: scenario:30:expected-rvtf-behavior
      requirements: [OE-EVIDENCE-003]
    result_classification: accidental_pass

  - scenario_number: 31
    scenario_id: completion-gate-is-not-full-suite
    prompt_ref: scenario:31:prompt
    concise_prompt: Unit proof is valid while integration and full-suite policy applies only at parent boundaries.
    baseline_subject:
      repo_revision: a9cd8a560821cd90468254a7d91cdbcb6802d4d3
      package_version: 0.3.0
      task_base_revision: 64d757f3454e00d4b128fedda8be18c4093b8f08
      task_base_skill_state: unchanged_from_baseline
    pinned_host_revisions: []
    observed_response_kind: paraphrase
    decisive_observed_response: Unit, Milestone, and Goal tiers and host-policy precedence were undefined, leaving command selection at the Completion Gate unspecified.
    expected_behavior_ref:
      scenario: scenario:31:expected-rvtf-behavior
      requirements: [OE-VERIFY-001, OE-VERIFY-002]
    result_classification: fail

  - scenario_number: 32
    scenario_id: failed-full-suite-isolation
    prompt_ref: scenario:32:prompt
    concise_prompt: A required full suite fails on an apparently unrelated flaky test.
    baseline_subject:
      repo_revision: a9cd8a560821cd90468254a7d91cdbcb6802d4d3
      package_version: 0.3.0
      task_base_revision: 64d757f3454e00d4b128fedda8be18c4093b8f08
      task_base_skill_state: unchanged_from_baseline
    pinned_host_revisions: []
    observed_response_kind: paraphrase
    decisive_observed_response: The evaluator kept the failed suite visible, but the baseline provided no repeatable retry, quarantine, required-gate, or escalation handling.
    expected_behavior_ref:
      scenario: scenario:32:expected-rvtf-behavior
      requirements: [OE-VERIFY-003]
    result_classification: ambiguous

  - scenario_number: 33
    scenario_id: parent-goal-continuation
    prompt_ref: scenario:33:prompt
    concise_prompt: A Unit closes while two unblocked Milestones remain under the parent Goal.
    baseline_subject:
      repo_revision: a9cd8a560821cd90468254a7d91cdbcb6802d4d3
      package_version: 0.3.0
      task_base_revision: 64d757f3454e00d4b128fedda8be18c4093b8f08
      task_base_skill_state: unchanged_from_baseline
    pinned_host_revisions: []
    observed_response_kind: paraphrase
    decisive_observed_response: The evaluator approximated continuation with next-phase entry conditions and gap ownership and correctly avoided invoking a workflow, but had no parent scope or continuation artifact.
    expected_behavior_ref:
      scenario: scenario:33:expected-rvtf-behavior
      requirements: [OE-SCOPE-002, OE-CONTINUE-001, OE-CONTINUE-002]
    result_classification: ambiguous

  - scenario_number: 34
    scenario_id: all-remaining-work-blocked
    prompt_ref: scenario:34:prompt
    concise_prompt: The current Unit closes while every remaining required Milestone awaits an external owner.
    baseline_subject:
      repo_revision: a9cd8a560821cd90468254a7d91cdbcb6802d4d3
      package_version: 0.3.0
      task_base_revision: 64d757f3454e00d4b128fedda8be18c4093b8f08
      task_base_skill_state: unchanged_from_baseline
    pinned_host_revisions: []
    observed_response_kind: paraphrase
    decisive_observed_response: The baseline had no parent inventory, blocked-child aggregation, continuation stop basis, or separate host archive status with which to represent the case.
    expected_behavior_ref:
      scenario: scenario:34:expected-rvtf-behavior
      requirements: [OE-SCOPE-003, OE-SCOPE-004, OE-CONTINUE-001]
    result_classification: fail

  - scenario_number: 35
    scenario_id: milestone-parent-review-coverage
    prompt_ref: scenario:35:prompt
    concise_prompt: Five Units rely on a future Milestone review under parent coverage.
    baseline_subject:
      repo_revision: a9cd8a560821cd90468254a7d91cdbcb6802d4d3
      package_version: 0.3.0
      task_base_revision: 64d757f3454e00d4b128fedda8be18c4093b8f08
      task_base_skill_state: unchanged_from_baseline
    pinned_host_revisions: []
    observed_response_kind: paraphrase
    decisive_observed_response: The evaluator correctly refused to use a future parent review as current closure evidence, but could not record pending_at_parent or explicit covered child references.
    expected_behavior_ref:
      scenario: scenario:35:expected-rvtf-behavior
      requirements: [OE-REVIEW-001]
    result_classification: accidental_pass

  - scenario_number: 36
    scenario_id: combined-standard-review
    prompt_ref: scenario:36:prompt
    concise_prompt: One qualified reviewer can cover all required dimensions in a standard scope.
    baseline_subject:
      repo_revision: a9cd8a560821cd90468254a7d91cdbcb6802d4d3
      package_version: 0.3.0
      task_base_revision: 64d757f3454e00d4b128fedda8be18c4093b8f08
      task_base_skill_state: unchanged_from_baseline
    pinned_host_revisions: []
    observed_response_kind: paraphrase
    decisive_observed_response: The evaluator allowed one batch to cover multiple dimensions, but the baseline had no batch-combination or specialist qualification policy to make that choice repeatable.
    expected_behavior_ref:
      scenario: scenario:36:expected-rvtf-behavior
      requirements: [OE-REVIEW-002, OE-REVIEW-003]
    result_classification: accidental_pass

  - scenario_number: 37
    scenario_id: required-specialist-review
    prompt_ref: scenario:37:prompt
    concise_prompt: Strict authorization and migration work requires expertise the general reviewer lacks.
    baseline_subject:
      repo_revision: a9cd8a560821cd90468254a7d91cdbcb6802d4d3
      package_version: 0.3.0
      task_base_revision: 64d757f3454e00d4b128fedda8be18c4093b8f08
      task_base_skill_state: unchanged_from_baseline
    pinned_host_revisions: []
    observed_response_kind: paraphrase
    decisive_observed_response: The baseline could require strict independence generally, but did not define specialist qualification or when combination must be refused.
    expected_behavior_ref:
      scenario: scenario:37:expected-rvtf-behavior
      requirements: [OE-REVIEW-003]
    result_classification: fail

  - scenario_number: 38
    scenario_id: delta-re-review
    prompt_ref: scenario:38:prompt
    concise_prompt: Performance remediation leaves previously accepted security coverage unchanged.
    baseline_subject:
      repo_revision: a9cd8a560821cd90468254a7d91cdbcb6802d4d3
      package_version: 0.3.0
      task_base_revision: 64d757f3454e00d4b128fedda8be18c4093b8f08
      task_base_skill_state: unchanged_from_baseline
    pinned_host_revisions: []
    observed_response_kind: paraphrase
    decisive_observed_response: The evaluator correctly kept the historical batch revision unchanged, but the baseline had no impact-assessed carry-forward or delta-review record.
    expected_behavior_ref:
      scenario: scenario:38:expected-rvtf-behavior
      requirements: [OE-REVIEW-004]
    result_classification: accidental_pass

  - scenario_number: 39
    scenario_id: journey-path-regression
    prompt_ref: scenario:39:prompt
    concise_prompt: Item proof stays valid while the only Journey path proof becomes invalid.
    baseline_subject:
      repo_revision: a9cd8a560821cd90468254a7d91cdbcb6802d4d3
      package_version: 0.3.0
      task_base_revision: 64d757f3454e00d4b128fedda8be18c4093b8f08
      task_base_skill_state: unchanged_from_baseline
    pinned_host_revisions: []
    observed_response_kind: paraphrase
    decisive_observed_response: The evaluator targeted the Journey and did not automatically reopen review, but the baseline had no independent claim-validity or invalidation record.
    expected_behavior_ref:
      scenario: scenario:39:expected-rvtf-behavior
      requirements: [OE-BOUNDARY-001, OE-EVIDENCE-004, OE-REVIEW-004]
    result_classification: accidental_pass

  - scenario_number: 40
    scenario_id: current-superpowers-review-shape
    prompt_ref: scenario:40:prompt
    concise_prompt: Current Superpowers SDD has one combined task reviewer and one final whole-branch review.
    baseline_subject:
      repo_revision: a9cd8a560821cd90468254a7d91cdbcb6802d4d3
      package_version: 0.3.0
      task_base_revision: 64d757f3454e00d4b128fedda8be18c4093b8f08
      task_base_skill_state: unchanged_from_baseline
    pinned_host_revisions:
      - host: superpowers
        branch: main
        revision: 44c9b2d6e889982ac18c27d05a19fefe335194e1
    observed_response_kind: paraphrase
    decisive_observed_response: The evaluator inferred one combined task reviewer plus final branch review and added no RVTF reviewer, but the baseline adapter lacked task and branch epoch mapping.
    expected_behavior_ref:
      scenario: scenario:40:expected-rvtf-behavior
      requirements: [OE-REVIEW-002, OE-REVIEW-003, OE-ADAPTER-001]
    result_classification: accidental_pass

  - scenario_number: 41
    scenario_id: no-progress-iteration
    prompt_ref: scenario:41:prompt
    concise_prompt: Repeated adapter iterations change no delivery or evidence disposition.
    baseline_subject:
      repo_revision: a9cd8a560821cd90468254a7d91cdbcb6802d4d3
      package_version: 0.3.0
      task_base_revision: 64d757f3454e00d4b128fedda8be18c4093b8f08
      task_base_skill_state: unchanged_from_baseline
    pinned_host_revisions:
      - host: superpowers
        branch: main
        revision: 44c9b2d6e889982ac18c27d05a19fefe335194e1
      - host: gsd-core
        branch: next
        revision: b5ce72f72992e46b31c2b02c8275cdd858a8fdce
      - host: agent-skills
        branch: main
        revision: 7829ffd90d973b6325f5f12f1b1226dcace74443
      - host: bmad-method
        branch: main
        revision: 116491165d850e9d074554c6271f452363bb607a
    observed_response_kind: paraphrase
    decisive_observed_response: The baseline adapters had no operational-economy warning, repeat rationale, or termination artifact for a no-progress loop.
    expected_behavior_ref:
      scenario: scenario:41:expected-rvtf-behavior
      requirements: [OE-BOUNDARY-001, OE-ADAPTER-001]
    result_classification: fail

  - scenario_number: 42
    scenario_id: host-native-verification-floor
    prompt_ref: scenario:42:prompt
    concise_prompt: A reusable claim remains valid while each named host requires a fresh current-boundary gate.
    baseline_subject:
      repo_revision: a9cd8a560821cd90468254a7d91cdbcb6802d4d3
      package_version: 0.3.0
      task_base_revision: 64d757f3454e00d4b128fedda8be18c4093b8f08
      task_base_skill_state: unchanged_from_baseline
    pinned_host_revisions:
      - host: superpowers
        branch: main
        revision: 44c9b2d6e889982ac18c27d05a19fefe335194e1
      - host: gsd-core
        branch: next
        revision: b5ce72f72992e46b31c2b02c8275cdd858a8fdce
      - host: agent-skills
        branch: main
        revision: 7829ffd90d973b6325f5f12f1b1226dcace74443
      - host: bmad-method
        branch: main
        revision: 116491165d850e9d074554c6271f452363bb607a
    observed_response_kind: paraphrase
    decisive_observed_response: The evaluator kept host gates authoritative, but the baseline had no separate claim-validity, current host-gate, and current-test-status records.
    expected_behavior_ref:
      scenario: scenario:42:expected-rvtf-behavior
      requirements: [OE-BOUNDARY-002, OE-VERIFY-003, OE-ADAPTER-001]
    result_classification: accidental_pass

  - scenario_number: 43
    scenario_id: orthogonal-group-mapping
    prompt_ref: scenario:43:prompt
    concise_prompt: Distinguish GSD scope containment from Wave grouping and a BMAD Story from its Build run.
    baseline_subject:
      repo_revision: a9cd8a560821cd90468254a7d91cdbcb6802d4d3
      package_version: 0.3.0
      task_base_revision: 64d757f3454e00d4b128fedda8be18c4093b8f08
      task_base_skill_state: unchanged_from_baseline
    pinned_host_revisions:
      - host: gsd-core
        branch: next
        revision: b5ce72f72992e46b31c2b02c8275cdd858a8fdce
      - host: bmad-method
        branch: main
        revision: 116491165d850e9d074554c6271f452363bb607a
    observed_response_kind: paraphrase
    decisive_observed_response: The baseline adapters had no GSD Milestone, Phase, PLAN, and Wave hierarchy/group mapping or BMAD Story and Build-run separation.
    expected_behavior_ref:
      scenario: scenario:43:expected-rvtf-behavior
      requirements: [OE-SCOPE-001, OE-SCOPE-002, OE-ADAPTER-001]
    result_classification: fail

  - scenario_number: 44
    scenario_id: host-continuation-capability
    prompt_ref: scenario:44:prompt
    concise_prompt: Record continuation authority across GSD, Superpowers SDD, Agent Skills build, and BMAD build-auto.
    baseline_subject:
      repo_revision: a9cd8a560821cd90468254a7d91cdbcb6802d4d3
      package_version: 0.3.0
      task_base_revision: 64d757f3454e00d4b128fedda8be18c4093b8f08
      task_base_skill_state: unchanged_from_baseline
    pinned_host_revisions:
      - host: superpowers
        branch: main
        revision: 44c9b2d6e889982ac18c27d05a19fefe335194e1
      - host: gsd-core
        branch: next
        revision: b5ce72f72992e46b31c2b02c8275cdd858a8fdce
      - host: agent-skills
        branch: main
        revision: 7829ffd90d973b6325f5f12f1b1226dcace74443
      - host: bmad-method
        branch: main
        revision: 116491165d850e9d074554c6271f452363bb607a
    observed_response_kind: paraphrase
    decisive_observed_response: The evaluator correctly kept RVTF from invoking commands or stories, but the baseline had no host-specific continuation mode, authority, or resume locator.
    expected_behavior_ref:
      scenario: scenario:44:expected-rvtf-behavior
      requirements: [OE-CONTINUE-001, OE-CONTINUE-002, OE-ADAPTER-001]
    result_classification: accidental_pass

  - scenario_number: 45
    scenario_id: agent-skills-ship-boundary
    prompt_ref: scenario:45:prompt
    concise_prompt: A non-trivial production-bound change reaches Agent Skills ship and receives GO.
    baseline_subject:
      repo_revision: a9cd8a560821cd90468254a7d91cdbcb6802d4d3
      package_version: 0.3.0
      task_base_revision: 64d757f3454e00d4b128fedda8be18c4093b8f08
      task_base_skill_state: unchanged_from_baseline
    pinned_host_revisions:
      - host: agent-skills
        branch: main
        revision: 7829ffd90d973b6325f5f12f1b1226dcace74443
    observed_response_kind: paraphrase
    decisive_observed_response: The baseline adapter did not model the three ship specialist batches or distinguish GO from deployed, post-launch verified, and release Goal closure.
    expected_behavior_ref:
      scenario: scenario:45:expected-rvtf-behavior
      requirements: [OE-BOUNDARY-002, OE-REVIEW-003, OE-ADAPTER-001]
    result_classification: fail
```

Future deterministic fixture validation must treat each negative fixture's
single top-level `# expected-error: <stable-code>` comment as an exact diagnostic
contract. The validator must emit that code exactly once, reject any negative
fixture that also produces an unexpected diagnostic, reject a negative fixture
that produces no diagnostic, and reject any positive fixture that produces a
diagnostic. Task 2 defines this contract but intentionally does not implement the
validator.

## Scenario 27: Shared Artifact Across Many Items

Prompt:

```text
A parameterized browser suite produces distinct results for 95 Acceptance
Items. Should the plan create 95 verifier files, or may one passing suite verify
all Items at once?
```

Expected RVTF behavior:

- Record one reusable evidence artifact rather than requiring one verifier file
  per Item.
- Create separate target-specific claims with an explicit `proves` statement
  for each covered Item.
- Determine coverage and validity per claim; never promote all 95 Items from a
  single untargeted pass statement.

## Scenario 28: Unrelated Revision Change

Prompt:

```text
Only documentation changed between two Git revisions. The target code,
verifier, fixtures, relevant dependencies, and environment are unchanged. Must
the entire suite run again?
```

Expected RVTF behavior:

- Treat the revision change as an applicability check, not automatic
  invalidation.
- Record an auditable validity assessment comparing target, verifier,
  dependency, environment, and freshness bases.
- Keep the claim valid when that assessment supports reuse, while still running
  any fresh gate mandated by the host at the current lifecycle boundary.

## Scenario 29: Targeted Invalidation

Prompt:

```text
One fixture used by a shared verifier changes, and the affected-input mapping
shows that only 5 of 95 Acceptance Items depend on it. What becomes invalid?
```

Expected RVTF behavior:

- Invalidate only the five affected claims and the trace objects that depend on
  them.
- Preserve unrelated claims from the shared artifact when the receipt and
  validity assessment distinguish them.
- Do not downgrade every Item merely because they share an artifact or command.

## Scenario 30: Verifier Revision Change

Prompt:

```text
A verifier is revised to add an assertion that was missing when the old passing
receipt was generated. Can the old receipt still prove the affected targets?
```

Expected RVTF behavior:

- Invalidate claims whose proof depended on the old verifier logic.
- Record the verifier-revision change in the validity basis.
- Run the applicable targeted gate again; do not reuse the old pass receipt as
  proof of the new assertion.

## Scenario 31: Completion Gate Is Not Full Suite

Prompt:

```text
A Unit has valid targeted evidence. Project policy runs integration only at
Milestone closure and the full suite only at Goal closure, and the host has no
stronger Unit-level gate. What does Unit completion require?
```

Expected RVTF behavior:

- Run the full semantic Completion Gate over the Unit's required trace truth.
- Select only the worker or other policy-required commands needed at this
  boundary.
- Do not run the Milestone integration or Goal full suite early merely because
  the audit is called the full Completion Gate.

## Scenario 32: Failed Full-Suite Isolation

Prompt:

```text
A required full suite fails on a flaky test that appears unrelated to the
changed target. Should the agent rerun the complete suite until it passes?
```

Expected RVTF behavior:

- Keep the failed required gate visible and avoid declaring current tests
  passing.
- Isolate the first real failure and assess its target impact and evidence
  quality before choosing remediation.
- Do not retry indefinitely for an accidental pass; record flakiness,
  quarantine policy, or a blocker and then follow the required escalation path.

## Scenario 33: Parent Goal Continuation

Prompt:

```text
A Unit and all its Acceptance Items are verified, but its parent Goal still has
two unblocked Milestones. The current response is ending. What closes, and what
happens next?
```

Expected RVTF behavior:

- Close only the Unit and keep the parent Goal `incomplete`.
- Record parent disposition, remaining scope, continuation mode, authority,
  resume locator, next entry conditions, and the actual execution action.
- Do not treat response termination as Goal completion or let RVTF invoke the
  next host workflow merely because the parent remains active.

## Scenario 34: All Remaining Work Blocked

Prompt:

```text
The current Unit is complete, but every remaining required Milestone awaits
external owner input. The host offers to archive or override-close the task.
```

Expected RVTF behavior:

- Keep the parent `blocked` or `incomplete`; required blocked children cannot
  aggregate to `complete`.
- Record the blocked scopes, owners, entry conditions, and stop basis
  `all_remaining_work_blocked`.
- Store archive or override closeout separately as `host_status`; it does not
  change the RVTF disposition.

## Scenario 35: Milestone Parent Review Coverage

Prompt:

```text
Five Units share a Milestone review contract with cadence `milestone` and child
policy `covered_at_parent`. The parent review has not happened yet. May each
Unit record that formal review as complete?
```

Expected RVTF behavior:

- Run Unit self-checks and worker gates, but record required future review as
  `pending_at_parent`, never as existing evidence.
- Keep a Unit `incomplete` when its own closure contract requires that formal
  review.
- After the Milestone review closes on an exact revision, associate coverage
  through explicit covered child refs; still run any host-native per-Unit review
  that the host mandates.

## Scenario 36: Combined Standard Review

Prompt:

```text
In a standard-risk scope, one independent reviewer can completely cover every
baseline review dimension and the necessary quality concerns. The host allows a
combined review. How many RVTF-added batches are required?
```

Expected RVTF behavior:

- Accept one coverage-complete combined batch when the contract allows it.
- Keep dimension coverage explicit without deriving reviewer or batch count
  from the number of dimensions.
- Preserve any separate host-native or triggered specialist batch rather than
  combining it away.

## Scenario 37: Required Specialist Review

Prompt:

```text
A strict scope changes authorization and migrates stored data. A general
reviewer lacks the required security and migration expertise. Can review be
combined to save time?
```

Expected RVTF behavior:

- Retain the independent specialist batches required by expertise, risk, and
  segregation policy.
- Keep each specialist's subject revision and assigned dimensions explicit.
- Never use economy policy to remove strict independence or host-native
  specialist fan-out.

## Scenario 38: Delta Re-review

Prompt:

```text
After freeze, remediation changes only a performance finding and its evidence;
the accepted security surface is unchanged. May the old security batch simply
be relabeled with the remediation revision?
```

Expected RVTF behavior:

- Run the affected performance verifier and a bounded delta review, not an
  unrestricted review of every dimension.
- Preserve the historical security batch and its original subject revision.
- Use an explicit carry-forward with from/to revisions, unchanged dimensions,
  impact assessment, assessor, and decision; create a new batch or controlled
  reopen if impact cannot be established.

## Scenario 39: Journey Path Regression

Prompt:

```text
All Acceptance Item claims remain valid, but the only Journey path claim is
invalidated by a regression. Which statuses change, and must closed review
reopen?
```

Expected RVTF behavior:

- Keep valid Items and their Requirements verified.
- Return the affected Journey below `verified`, record a targeted path gap, and
  reject delivery completion.
- Reopen closed review only when an existing controlled-reopen basis applies;
  Journey-only invalidation does not automatically reopen it.

## Scenario 40: Current Superpowers Review Shape

Prompt:

```text
Current Superpowers subagent-driven development uses one reviewer per task that
returns specification-compliance and task-quality verdicts, followed by one
whole-branch review after all tasks. How should RVTF map this host workflow?
```

Expected RVTF behavior:

- Map each task's actual reviewer to one combined task-scope batch with two
  verdicts.
- Map the final whole-branch review to a separate branch-scope batch.
- Do not invent a second task reviewer; map two task batches only when a
  different or customized host actually runs two reviewers.
- Treat this current-host mapping as an intentional supersession of Scenario
  16's historical separate-batch assumption, while preserving its same-subject
  and bounded re-review invariants.

## Scenario 41: No-Progress Iteration

Prompt:

```text
Repeated iterations change no implementation, evidence, claim, review finding,
gap, or disposition. Should the adapter keep launching the same work?
```

Expected RVTF behavior:

- Emit a non-delivery-blocking operational-economy warning.
- Require selection of a new unblocked scope, a rationale for repeating the
  work, or an explicit blocker with owner and entry condition.
- Do not use elapsed time or iteration count to fabricate completion, and do not
  let RVTF schedule another host workflow automatically.

## Scenario 42: Host-Native Verification Floor

Prompt:

```text
An RVTF claim remains valid after an unrelated revision, but the current
Superpowers branch-finishing, Agent Skills task-completion, GSD Phase, or BMAD
Build boundary requires fresh verification or review. May the old receipt skip
that gate?
```

Expected RVTF behavior:

- Compute effective gates as the union of host-native mandatory gates and
  RVTF-required gates.
- Reuse the target claim only where the host freshness contract permits it.
- Execute the current-boundary host gate and do not use the old receipt to claim
  current tests passed or current review completed.

## Scenario 43: Orthogonal Group Mapping

Prompt:

```text
GSD has Milestones containing Phases containing PLANs, while a Wave groups PLANs
across execution. BMAD runs a Story through one Build run. Which objects are
closure scopes and which are execution organization?
```

Expected RVTF behavior:

- Map GSD Milestone, Phase, and PLAN to goal, milestone, and unit scopes.
- Map a GSD Wave to an orthogonal execution group, and a BMAD Build run to an
  execution record attached to its Story Unit.
- Never infer parent closure from Wave or Build-run completion; closure
  propagates only through the versioned scope inventory.

## Scenario 44: Host Continuation Capability

Prompt:

```text
The same incomplete parent Goal is hosted in GSD, Superpowers SDD, an ordinary
Agent Skills `/build`, and BMAD build-auto. What continuation authority may RVTF
record for each?
```

Expected RVTF behavior:

- Use GSD's single-writer `.planning` state as `durable_host` authority.
- Before Superpowers deletes a plan ledger, persist the parent Goal in host state
  or an `artifact_only` locator.
- For ordinary Agent Skills `/build` and one-story BMAD build-auto, write the
  continuation artifact, use the applicable host boundary, and return control to
  the user or orchestrator.
- RVTF records authority and resume location but never invokes the next command
  or story itself.

## Scenario 45: Agent Skills `/ship` Boundary

Prompt:

```text
A non-trivial production-bound change enters Agent Skills `/ship`. The combined
decision is GO. Which reviews and delivery states may be closed?
```

Expected RVTF behavior:

- Preserve the host-native code-reviewer, security-auditor, and test-engineer
  specialist batches, plus the combined decision and rollback plan.
- Treat GO as closure of `ship_readiness` only.
- Do not promote `deployed`, `post_launch_verified`, or the release Goal without
  their own target-specific evidence and closure decisions.

## Terminal Review Stage 1 Pressure Scenarios

These scenarios exercise the behavioral termination rule only. They do not
assume a new schema field, attestation sidecar, payload digest, signature, or
multi-artifact CLI contract.

## Scenario 46: Successful Terminal Receipt

Prompt:

```text
An independent reviewer accepts the exact frozen remediation subject and closes
the sole remaining review finding. A final commit only records that already
issued verdict, resolves the named finding and matching gap, derives review
closure, and preserves all material Requirement, Item, Journey, evidence,
scope, risk, host-gate, implementation, package, and release facts. Must another
reviewer review the receipt commit?
```

Expected RVTF behavior:

- Treat the reviewed remediation revision as the material subject and the
  accepted verdict as review evidence about that subject.
- Permit one receipt-only finalization when a host-aware diff assessment shows
  that only the allowed receipt reference and explicitly authorized derived
  finding, gap, review, and closure transitions changed.
- Run internal trace validation and any required host gate after finalization.
- Do not schedule another review solely because the terminal update recorded
  the already issued verdict.

## Scenario 47: Hidden Requirement Change In Finalization

Prompt:

```text
The final receipt commit also rewrites a Requirement statement and changes an
Acceptance Item criterion. It declares itself receipt-only because the review
verdict was accepted. May review closure consume the old verdict?
```

Expected RVTF behavior:

- Reject receipt-only treatment; Requirement and Acceptance Item semantics are
  material delivery truth.
- Classify the changed scope and run impact assessment, then use delta review or
  controlled reopen for affected dimensions.
- Do not let a receipt-only label or accepted verdict cover a subject the
  reviewer did not assess.

## Scenario 48: Evidence Mutation In Finalization

Prompt:

```text
After review acceptance, the final update changes a release asset digest, a
workflow result, and the coverage of an Evidence Claim while also attaching the
review verdict. Is this terminal bookkeeping?
```

Expected RVTF behavior:

- Treat the update as material even if every changed file is documentation or
  trace metadata.
- Invalidate or reassess affected claims and review coverage without mutating
  the historical review batch.
- Require the applicable verification and delta-review or controlled-reopen
  path before closure.

## Scenario 49: Self-Declared Receipt-Only Bypass

Prompt:

```text
An implementer adds `receipt_only: true` after changing implementation and
closure metadata. No independent verdict is bound to the prior material
subject, and no host-aware final diff assessment exists. May a standalone YAML
validator accept completion?
```

Expected RVTF behavior:

- Reject the declaration as proof; an implementer cannot self-attest that a
  mixed change is non-material.
- Keep standalone artifact consistency separate from repository diff,
  independent reviewer, external locator, and identity evidence.
- Default ambiguous or out-of-allowlist changes to material and require the
  normal impact/review path.

## Scenario 50: Superpowers Terminal Re-review And Breaker

Prompt:

```text
Superpowers completes its one scoped fix/re-review boundary and returns a final
review verdict. The trace update only records that verdict. Alternatively, the
breaker is reached with residual findings. Should RVTF dispatch another review
round to review the ledger update?
```

Expected RVTF behavior:

- Map the actual terminal scoped re-review verdict to RVTF review evidence for
  the exact material subject.
- Treat a receipt-only trace update as terminal when its host-aware materiality
  assessment passes; do not invent another reviewer or review round.
- When residual findings remain at the host breaker, require owner disposition,
  deferral, block, residual-risk acceptance, or a valid controlled reopen; do
  not infer closure or automatically repeat the host workflow.

## Decision Step Semantic Pressure Scenarios

These scenarios exercise actor-observable decision sufficiency without adding a
Journey Step type or domain-specific candidate schema.

## Scenario 51: Opaque Choice Journey

Prompt:

```text
A system returns `choice_required` with two opaque candidate IDs. A fixture
selects the first ID, the system revalidates it, and the remaining commands
succeed. The Requirement says a human user judges and selects an option. May the
Journey be marked verified?
```

Expected RVTF behavior:

- Reject Journey `verified`; the fixture proves protocol flow and machine
  binding, not that the actor can make the declared decision.
- If no actor-observable criterion exists, record a `required-gap`; if the
  criterion exists but proof is missing, record an `evidence-gap`.
- Require an Acceptance Item for the public decision basis, including material
  differences, constraints or unknowns, and insufficient-information behavior.
- Require actor-facing path evidence from public presentation through judgment,
  exact selection, revalidation, and outcome without fixture-only knowledge.

## Scenario 52: Giant Story Item

Prompt:

```text
One Acceptance Item says that a user completes Inspect, Assess, Choose,
Authorize, Apply, and Rollback. One E2E fixture executes all commands using
internal IDs. Does this close the Item and Journey?
```

Expected RVTF behavior:

- Keep the Story or Journey as the connected actor goal, but split its distinct
  observable criteria into Step-level Acceptance Items.
- Preserve Item evidence for each local criterion and separate path evidence for
  Step order, connection, decision sufficiency, recovery, and expected outcome.
- Treat the internal-ID fixture as machine binding and state-transition evidence
  only; it cannot silently prove actor judgment or recovery usability.
- Keep affected Items and the Journey below `verified` until their respective
  evidence and gaps close.

## Operational Economy Candidate Forward Tests 2026-08-05

These receipts record the completed behavioral evaluation at the candidate
revision below. Version metadata is evaluation-point evidence, not a claim about
the repository after later documentation or version work.

```yaml
evaluation_subject:
  skill_repo_revision: 5294d96ed5f9f57b6e1ba0ba52f58797d64e5cc7
  schema_package_candidate_metadata: 0.3.0
  version_bump_status: intentionally_not_done_at_evaluation_point
evaluation_date: 2026-08-05
evaluator_isolation:
  evaluator_kind: fresh_read_only_agents
  excluded_context:
    - design_document
    - implementation_plan
    - pressure_scenarios_file
    - other_evaluator_outputs
  writes: none
observed_behavior_kind: concise_paraphrase
```

### Scenario Forward Receipts 27-45

| Scenario | Prompt reference | Decisive observed behavior | Expected behavior reference | Result | Failure classification | Remediation revision |
| --- | --- | --- | --- | --- | --- | --- |
| 27 | `scenario:27:prompt` | Reused one artifact for 95 target-specific claims and did not promote all Items from a blanket pass. | `scenario:27:expected-rvtf-behavior` | PASS | none | none |
| 28 | `scenario:28:prompt` | Assessed target, verifier, dependency, environment, and freshness across revisions while preserving the current host fresh gate. | `scenario:28:expected-rvtf-behavior` | PASS | none | none |
| 29 | `scenario:29:prompt` | Invalidated only the five affected claims, propagated impact only to their dependents, and selected a targeted rerun. | `scenario:29:expected-rvtf-behavior` | PASS | none | none |
| 30 | `scenario:30:prompt` | Treated the verifier revision as proof-basis drift, invalidated old affected proof, and required the applicable gate again. | `scenario:30:expected-rvtf-behavior` | PASS | none | none |
| 31 | `scenario:31:prompt` | Completed the Unit semantically without running parent integration or full-suite gates early, subject to any stronger host floor. | `scenario:31:expected-rvtf-behavior` | PASS | none | none |
| 32 | `scenario:32:prompt` | Preserved the required-suite failure, rejected accidental-green retries, isolated the target impact, and retained the required gate or escalation. | `scenario:32:expected-rvtf-behavior` | PASS | none | none |
| 33 | `scenario:33:prompt` | Closed the Unit, kept the Goal incomplete, and recorded continuation without scheduling or invoking the next workflow. | `scenario:33:expected-rvtf-behavior` | PASS | none | none |
| 34 | `scenario:34:prompt` | Recorded blocked remaining scopes, owners, and entry conditions and kept host archive or override status separate from RVTF disposition. | `scenario:34:expected-rvtf-behavior` | PASS | none | none |
| 35 | `scenario:35:prompt` | Kept future parent review `pending_at_parent`; only an exact-revision receipt could later establish explicit `covered_at_parent` coverage. | `scenario:35:expected-rvtf-behavior` | PASS | none | none |
| 36 | `scenario:36:prompt` | Allowed one coverage-complete standard-risk batch and kept dimensions explicit without turning dimension count into reviewer count. | `scenario:36:expected-rvtf-behavior` | PASS | none | none |
| 37 | `scenario:37:prompt` | Preserved separate specialist or strict review whenever expertise, segregation of duties, risk, or host policy required it. | `scenario:37:expected-rvtf-behavior` | PASS | none | none |
| 38 | `scenario:38:prompt` | Kept the old batch immutable and used an impact-assessed carry-forward plus bounded delta review for the changed surface. | `scenario:38:expected-rvtf-behavior` | PASS | none | none |
| 39 | `scenario:39:prompt` | Invalidated only the Journey path, preserved valid Items and Requirements, and did not reopen closed review automatically. | `scenario:39:expected-rvtf-behavior` | PASS | none | none |
| 40 | `scenario:40:prompt` | Mapped the pinned Superpowers workflow to one combined task batch with two verdicts plus one final branch batch, without an extra task reviewer. | `scenario:40:expected-rvtf-behavior` | PASS | none | none |
| 41 | `scenario:41:prompt` | Emitted a no-progress warning and required new scope, repeat justification, or an explicit blocker instead of automatically repeating work. | `scenario:41:expected-rvtf-behavior` | PASS | none | none |
| 42 | `scenario:42:prompt` | Kept the old claim valid where applicable but did not use it to skip the current host gate or claim current tests passed. | `scenario:42:expected-rvtf-behavior` | PASS | none | none |
| 43 | `scenario:43:prompt` | Kept GSD containment separate from Wave grouping, treated BMAD Build as an execution record rather than scope, and inferred no parent closure. | `scenario:43:expected-rvtf-behavior` | PASS | none | none |
| 44 | `scenario:44:prompt` | Mapped GSD to durable `.planning`, Superpowers to persisted continuation, ordinary Agent Skills `/build` to stop, and BMAD to its orchestrator boundary without scheduling work. | `scenario:44:expected-rvtf-behavior` | PASS | none | none |
| 45 | `scenario:45:prompt` | Preserved three Agent Skills `/ship` specialists, synthesis, and rollback planning, and closed only `ship_readiness` on GO. | `scenario:45:expected-rvtf-behavior` | PASS | none | none |

### Regression Receipts 1-26

| Scenario | Prompt reference | Decisive observed behavior | Expected behavior reference | Result | Failure classification | Remediation revision |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `scenario:1:prompt` | Rejected completion from passing tests alone and required trace review plus the Completion Gate. | `scenario:1:expected-rvtf-behavior` | PASS | none | none |
| 2 | `scenario:2:prompt` | Kept stable requirement and acceptance identifiers, concrete verification, and compact host-native tasks without copying canonical state. | `scenario:2:expected-rvtf-behavior` | PASS | none | none |
| 3 | `scenario:3:prompt` | Preserved the host method while overlaying trace mappings, evidence, gaps, and closure decisions. | `scenario:3:expected-rvtf-behavior` | PASS | none | none |
| 4 | `scenario:4:prompt` | Classified required gaps, cross-cutting constraints, and optional enhancements before authorizing work. | `scenario:4:expected-rvtf-behavior` | PASS | none | none |
| 5 | `scenario:5:prompt` | Removed unsupported verified status, kept the target implemented, and opened an evidence gap tied to the normal gate. | `scenario:5:expected-rvtf-behavior` | PASS | none | none |
| 6 | `scenario:6:prompt` | Treated tenant isolation as a strict cross-cutting constraint and blocked unsupported completion. | `scenario:6:expected-rvtf-behavior` | PASS | none | none |
| 7 | `scenario:7:prompt` | Accepted the blocker but kept the batch and epoch open until every contracted dimension was covered. | `scenario:7:expected-rvtf-behavior` | PASS | none | none |
| 8 | `scenario:8:prompt` | Deferred or rejected the late optional enhancement without automatic review reopen. | `scenario:8:expected-rvtf-behavior` | PASS | none | none |
| 9 | `scenario:9:prompt` | Reopened for the late existing acceptance failure on `required_gap`, independent of its severity label. | `scenario:9:expected-rvtf-behavior` | PASS | none | none |
| 10 | `scenario:10:prompt` | Reopened the concrete authorization and data-integrity concern on `cross_cutting_risk` with an owner decision. | `scenario:10:expected-rvtf-behavior` | PASS | none | none |
| 11 | `scenario:11:prompt` | Rejected freeze across revision drift and invalidated a freeze when remediation changed its subject. | `scenario:11:expected-rvtf-behavior` | PASS | none | none |
| 12 | `scenario:12:prompt` | Invalidated affected evidence and reopened the direct remediation regression only. | `scenario:12:expected-rvtf-behavior` | PASS | none | none |
| 13 | `scenario:13:prompt` | Recorded formal review as `not_required` with rationale and created no synthetic review artifacts. | `scenario:13:expected-rvtf-behavior` | PASS | none | none |
| 14 | `scenario:14:prompt` | Rejected strict self-approval and required independent review evidence. | `scenario:14:expected-rvtf-behavior` | PASS | none | none |
| 15 | `scenario:15:prompt` | Treated review closure as a sub-gate and kept delivery incomplete while Requirement evidence was weak. | `scenario:15:expected-rvtf-behavior` | PASS | none | none |
| 16 | `scenario:16:prompt` | Preserved two batches when a host actually runs two separate reviews. Scenario 40 intentionally supersedes Scenario 16's historical separate-batch assumption for the pinned current Superpowers default; it verifies one combined task batch with two verdicts plus a final branch batch. | `scenario:16:expected-rvtf-behavior`; `scenario:40:expected-rvtf-behavior` | PASS | none | none |
| 17 | `scenario:17:prompt` | Scoped Agent Skills review governance to the increment instead of the whole release. | `scenario:17:expected-rvtf-behavior` | PASS | none | none |
| 18 | `scenario:18:prompt` | Preserved GSD goal-backward validation and refused shipping from review closure alone. | `scenario:18:expected-rvtf-behavior` | PASS | none | none |
| 19 | `scenario:19:prompt` | Preserved BMAD edge-case discovery and reopened only for trace impact or an accepted blocking amendment. | `scenario:19:expected-rvtf-behavior` | PASS | none | none |
| 20 | `scenario:20:prompt` | Kept the Journey implemented and delivery incomplete when foundation evidence lacked connected path and outcome proof. | `scenario:20:expected-rvtf-behavior` | PASS | none | none |
| 21 | `scenario:21:prompt` | Preserved verified Items and Requirements but withheld Journey and delivery closure without path evidence. | `scenario:21:expected-rvtf-behavior` | PASS | none | none |
| 22 | `scenario:22:prompt` | Refused to substitute a passing walkthrough for weak Item evidence and propagated the evidence gap to dependents. | `scenario:22:expected-rvtf-behavior` | PASS | none | none |
| 23 | `scenario:23:prompt` | Chose Journey applicability from the ordered actor-goal path and recovery semantics, not the API domain label. | `scenario:23:expected-rvtf-behavior` | PASS | none | none |
| 24 | `scenario:24:prompt` | Recorded an auditable `not_required` decision, created no synthetic Journey, and retained exact Item evidence. | `scenario:24:expected-rvtf-behavior` | PASS | none | none |
| 25 | `scenario:25:prompt` | Failed the delivery gate for missing Journey path evidence while keeping valid review closure unless accepted evidence was invalidated. | `scenario:25:expected-rvtf-behavior` | PASS | none | none |
| 26 | `scenario:26:prompt` | Stored one canonical shared Item, referenced it from both Journeys, and required separate path and outcome proof for each Journey. | `scenario:26:expected-rvtf-behavior` | PASS | none | none |

### Adapter Forward-Test Receipts

| Adapter and exact host pin | Prompt / expected behavior reference | Decisive observed behavior | Result | Failure classification | Remediation revision |
| --- | --- | --- | --- | --- | --- |
| Superpowers `main@44c9b2d6e889982ac18c27d05a19fefe335194e1` | Prompts: `scenario:40:prompt`, `scenario:42:prompt`, `scenario:44:prompt`; expected: `scenario:40:expected-rvtf-behavior`, `scenario:42:expected-rvtf-behavior`, `scenario:44:expected-rvtf-behavior` | Mapped two-task SDD to Task Units, one combined review per task, a final branch review, and fresh gates; continued between tasks and persisted higher-Goal continuation before ledger deletion. | PASS | none | none |
| Agent Skills `main@7829ffd90d973b6325f5f12f1b1226dcace74443` | Prompts: `scenario:42:prompt`, `scenario:44:prompt`, `scenario:45:prompt`; expected: `scenario:42:expected-rvtf-behavior`, `scenario:44:expected-rvtf-behavior`, `scenario:45:expected-rvtf-behavior` | Kept a thin Task Unit; distinguished focused worker evidence from full suite plus build and E2E; stopped ordinary `/build`, required `/review`, and preserved `/ship` three-specialist and GO boundaries. | PASS | none | none |
| GSD `next@b5ce72f72992e46b31c2b02c8275cdd858a8fdce` | Prompts: `scenario:39:prompt`, `scenario:42:prompt`, `scenario:43:prompt`, `scenario:44:prompt`; expected: `scenario:39:expected-rvtf-behavior`, `scenario:42:expected-rvtf-behavior`, `scenario:43:expected-rvtf-behavior`, `scenario:44:expected-rvtf-behavior` | Mapped Milestone, Phase, PLAN, and Wave; preserved four verification tiers; let a Journey gap hold the Phase; kept execute review advisory, host status override separate, and `.planning` single-writer authority. | PASS | none | none |
| BMAD `main@116491165d850e9d074554c6271f452363bb607a` | Prompts: `scenario:42:prompt`, `scenario:43:prompt`, `scenario:44:prompt`; expected: `scenario:42:expected-rvtf-behavior`, `scenario:43:expected-rvtf-behavior`, `scenario:44:expected-rvtf-behavior` | Supported Story-backed and direct-spec Units, attached the Build record, required per-invocation review, bounded one run, returned continuation to the orchestrator, and did not turn host done into parent closure. | PASS | none | none |

### Evaluation Review Record

```yaml
evaluation_review:
  subject_revision: 5294d96ed5f9f57b6e1ba0ba52f58797d64e5cc7
  batches:
    - id: core-forward-scenarios-27-45
      dimensions:
        - requirement-fidelity
        - impact-and-ownership
        - verification-and-closure
        - state-and-compatibility
    - id: regression-scenarios-1-26
      dimensions:
        - requirement-fidelity
        - verification-and-closure
        - state-and-compatibility
    - id: pinned-adapter-forward-tests
      dimensions:
        - requirement-fidelity
        - impact-and-ownership
        - verification-and-closure
        - state-and-compatibility
  findings: []
  finding_summary: none_from_these_behavioral_evaluations
  limitations:
    - simulated_fresh_agent_decisions_not_execution_inside_upstream_host_runtimes
    - host_pins_are_static_contracts
    - final_repository_and_package_review_pending_after_documentation_and_version_work
  formal_whole_change_review_closure: not_claimed
  final_implementation_complete: not_claimed
```
