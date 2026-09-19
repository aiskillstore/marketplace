# RVTF Gates

## Usage Mode Gate

Before choosing artifact depth:

- Use `discovery` only when there is no completion claim.
- Use `lite` only for small, low-risk changes.
- Use `standard` for phase work, handoffs, or review.
- Use `strict` for security, privacy, data integrity, compatibility, migrations, money, production risk, or cross-agent execution.
- Raise the mode for a risky finding even if the rest of the work stays lighter.

## Journey Applicability Gate

Before planning implementation or claiming closure:

- In `discovery`, record candidate Journeys only; there is no completion claim.
- In `lite`, make a Journey applicability decision whenever an actor-goal path
  has ordered or causally connected observable Steps.
- In `standard` and `strict`, record `journey_applicability.decision` as
  `required` or `not_required` with a rationale.
- Mark Journey Trace `required` when item evidence alone cannot prove the
  outcome, Steps depend on order or state transitions, the path crosses
  boundaries, failure/recovery affects acceptance, or closure must be judged
  backward from an actor goal.
- Do not decide from technical labels. UI, CLI, API, migration, infrastructure,
  human, service, and automation work all use the same triggers.
- Strict risk does not automatically imply Journey applicability.
- Use `not_required` only when exact item-level verification fully proves the
  isolated result and no ordered or causal path exists. Do not invent a
  synthetic Journey.

## Review Governance Applicability Gate

Before review can affect closure or scope:

- In `discovery`, record candidate review needs only as assumptions.
- In `lite`, use bounded review governance only when the risk or host workflow
  justifies it.
- In `standard`, record `review_applicability`; use `not_required` only with a
  rationale showing no formal review lifecycle is part of the delivery decision.
- In `strict`, require bounded governance plus independent-from-implementer
  review evidence for the affected risk scope.
- A closed 0.4 standard/strict packet always records applicability. When it is
  `required`, the contract and closed epoch receipt must resolve; strict closure
  cannot select `not_required`.
- Activate governance when formal reviewers, multiple review passes, blocking
  review findings, strict risk, or prior remediation review are present.

## Requirement Validity Gate

Before trusting a requirement:

- Confirm the requirement still matches the latest source, owner decision, and known constraints.
- Convert contradictions, obsolete assumptions, or infeasible requirements into amend/reject/defer/block decisions.
- Do not use RVTF to prove faithful delivery of a requirement that is no longer valid.

## Design Gate

Before implementation planning:

- Capability tree exists.
- Requirement IDs are stable and complete enough for the phase.
- Each requirement has canonical Acceptance Items nested under
  `requirements[].acceptance[]`.
- Every Acceptance Item has a stable delivery-scope ID, source reference,
  criterion, verification method, initial status, and gap/evidence fields.
- No task or Journey duplicates mutable Acceptance Item status or evidence.
- Journey applicability is recorded at the depth required by the usage mode.
- Every required Journey defines actor, goal, expected outcome, and ordered
  observable Steps; every required Step maps to at least one Acceptance Item ID.
- When a Journey Step asks an actor to judge, choose, confirm, or authorize,
  mapped Acceptance Items define the actor-observable decision basis: public
  alternatives, material differences, relevant constraints or unknowns,
  confirmation or revalidation, and a safe path when information is insufficient.
- Do not treat an action-only outcome such as "actor selected X" or an opaque
  machine identifier as proof that the actor could make the declared decision.
- Cross-cutting constraints are represented as rows or explicit non-goals.
- Requirement validity is checked against sources, assumptions, and owner decisions.
- Assumptions, non-goals, and risk areas are explicit.
- Open questions are either answered or represented as blocked/deferred rows.
- If review governance applies, the review contract identifies baseline
  dimensions, triggered dimensions, impact surface, expected batches, and
  exclusions.

## Review Contract Gate

Before collecting formal review batches:

- Bind the contract to a delivery-scope-neutral `scope_ref`.
- Record impact surface categories: states, interfaces, writers, readers,
  callers, and consumers. Empty categories need rationale when
  `impact-and-ownership` is active.
- Include baseline dimensions: `requirement-fidelity`, `impact-and-ownership`,
  and `verification-and-closure`.
- Mark triggered dimensions as `required` or `not_applicable` with rationale.
- Map expected host review batches to dimensions.
- Do not let dimensions become requirements; findings still require RVTF
  classification and owner decisions.

## Delivery Scope Inventory And Aggregation Gate

Before using child or group progress in a closure decision:

- Classify closure scopes only as `goal`, `milestone`, or `unit`.
- Resolve every `parent_scope_ref`; reject cycles and confirm the reverse parent
  relation agrees with `required_child_scope_refs` and
  `required_for_parent`.
- In 0.4 standard/strict artifacts, require an explicit boolean
  `required_for_parent` on every non-root scope. Require every actual parent to
  carry both `required_child_inventory_revision` and
  `required_child_scope_refs`, even when that authoritative list is empty.
  Do not extend this lower bound to 0.3 or 0.4 lite artifacts.
- Require a `required_child_inventory_revision` for every authoritative child
  inventory. An empty plan list or completed execution batch is not an
  inventory revision.
- Treat `execution_batch`, `verification_batch`, and `review_batch` groups as
  orthogonal organization. Group completion never closes a member or parent.
- Aggregate a parent only from required children in its current inventory.
  `blocked` and `incomplete` children cannot support a closed parent.
  A plain `complete` parent also cannot hide a required child with qualified
  deferred-gap or residual-risk closure; preserve that qualification at the
  parent.
- Do not invent history for a child that was always optional. When removal from
  required scope is explicitly claimed, require `required_inventory_exclusion`
  to resolve an accepted amendment naming the parent and removed child, and
  require its inventory revision to equal the parent's updated authoritative
  inventory. `required_for_parent: false` alone is not a removal decision.
- Keep `host_status` separate. Host `done`, `archived`, `shipped`, or override
  closeout cannot promote RVTF disposition.

## Plan Gate

Before coding:

- Every host task, story, phase, or increment lists the applicable
  `requirement_ids`, `acceptance_item_ids`, `journey_ids`, and
  `journey_step_ids`. Journey lists may be empty when that host unit does not
  cover an applicable Journey or the scope does not require Journey Trace.
- Every requirement has at least one task, explicit deferral, or rejection.
- Every Acceptance Item has at least one host work mapping, explicit deferral,
  or valid rejection and a concrete verification method.
- Required Journey Steps have host work mappings and planned path/outcome
  evidence; component or foundation checks are not path evidence by default.
- A human decision Step has an actor-facing verifier for the public decision
  basis. Plan machine binding and revalidation separately; a token round-trip
  cannot replace the actor-facing check, and readable output cannot replace
  exact binding.
- Verification commands are concrete enough to run.
- The plan does not add untraced scope.
- Optional enhancements require accepted scope amendments before implementation.

## Implementation Checkpoint

After each implementation slice:

- Update affected Acceptance Item, Requirement, and Journey statuses without
  auto-promoting parents.
- Attach item evidence to canonical Acceptance Item IDs and path evidence to
  Journey IDs and covered Step IDs.
- Check evidence quality before marking `verified`.
- Record deviations in the gap ledger.
- Propagate Item gaps to their parent Requirement and dependent Journeys. Keep a
  Journey-only path gap from falsely downgrading otherwise valid Requirement
  evidence.
- Review requirement coverage before code quality.

## Evidence Quality Gate

Before accepting evidence:

- Every evidence record names or is structurally attached to its target.
- Item evidence proves the exact Acceptance Item criterion, not only adjacent
  behavior.
- Path evidence proves required Step order and connection plus the Journey's
  expected outcome; local component presence is insufficient.
- Array position, fixed ID, internal lookup, or fixture-only knowledge may prove
  protocol flow or machine binding, but cannot by itself prove a human decision
  Step. Human path evidence shows the public information presented, the actor's
  judgment, exact selection or authorization, system confirmation or
  revalidation, and the resulting outcome without undeclared internal knowledge.
- A single artifact may support both axes only when each target and `proves`
  claim is recorded separately.
- Named edge cases and negative cases are covered or logged as gaps.
- Evidence is fresh, reproducible, and tied to a normal gate, or has an explicit manual record.
- Weak item evidence keeps the Item and parent Requirement below `verified` and
  prevents dependent Journeys from being `verified`.
- All Items being `verified` does not verify a Journey when path evidence is
  absent; keep the Journey `implemented` and record an `evidence-gap`.

## Evidence Registry, Reuse, And Invalidation Gate

Before reusing a receipt or invalidating proof:

- Separate reusable `evidence_artifacts` from target-specific
  `evidence_claims`; one artifact may support multiple claims, but every claim
  names one actual Acceptance Item or Journey and its exact proof.
- Accept `evidence_claims[].validity.status: valid` only from a passed artifact.
  `stale`, `invalidated`, and `unknown` cannot support `verified`.
- Keep Item and Journey claims distinct. Every `evidence_ref` resolves to the
  claim for that exact target.
- Require a verified Item's inline record or registry claim to be strong,
  target-specific, normal-gate proof backed by a pass. Require one verified
  Journey path record or claim to cover every local Step plus order and outcome.
  Reject inline/registry mixing for the same target, while allowing different
  targets to use different representations.
- When the artifact and checked revision differ, compare target, verifier,
  relevant dependency basis, environment compatibility, and freshness. In
  standard/strict, record the assessor, policy, rationale, before/after values,
  and decision in a validity assessment. An opaque fingerprint is not enough.
- Lite reuse still names all comparison surfaces in its rationale; otherwise
  set the claim to `unknown` and run the applicable targeted gate.
- Invalidate only affected claims and dependent trace objects. Do not downgrade
  every target that shares the artifact, and do not let a Journey-only path
  invalidation downgrade still-valid Item evidence.

## Effective Gate And Verification Tier Gate

Before selecting commands for a boundary:

- Define the `worker`, `batch`, `milestone`, and `completion` tiers for a new
  standard/strict verification policy.
- Require that policy and a non-empty host-native gate floor for every closed
  0.4 standard/strict packet; omission or an empty list is not an economy choice.
- Select the smallest sufficient tier for the current scope and trigger;
  Milestone integration and Goal full-suite commands do not run early merely
  because the semantic audit is named Completion Gate.
- Compute effective gates as the union of applicable RVTF-required gates and
  host-native mandatory gates. Economy and reuse may never subtract the host
  floor.
- A valid old claim may skip only a gate whose freshness policy permits reuse.
  Current-tree, task-completion, phase, build, merge, ship, and host-declared
  full-suite gates still require their matching fresh receipts.
- Keep claim validity, `host_gate_status`, and `current_test_status_claim`
  separate. Only a matching passed receipt at the current revision and
  lifecycle boundary supports the latter two facts, and the current-test receipt
  must be the one referenced by the satisfied effective closure gate. Treat
  `freshness` as a host-defined policy value and require exact policy/receipt
  equality rather than an RVTF-owned token list.
- Enforce a non-empty metadata floor before matching: the required policy gate
  has gate, boundary, and freshness; the satisfied closure entry has gate,
  receipt, satisfied status, and revision; and its passed receipt has matching
  gate, boundary, freshness, revision, execution time, and command signature.
  Missing metadata on both sides is invalid, not a match.
- Keep a failed required gate visible. Isolate its first real failure, use the
  applicable retry/quarantine/escalation policy, and never rerun indefinitely
  for an accidental pass.

## Review Finding Intake Gate

Before implementing review feedback:

- Classify each finding: `required-gap`, `evidence-gap`, `cross-cutting-constraint`, `scope-amendment`, `optional-enhancement`, or `quality-defect`.
- Link it to an existing requirement, accepted amendment, or cross-cutting constraint.
- For governed review, record epoch, batch, dimension, subject revision, and
  whether the finding was discovered after freeze.
- Record optional or unlinked findings as deferred/rejected unless an owner accepts them into scope.
- Treat safety, privacy, compliance, data-loss, compatibility, and regression findings as candidate constraints, not disposable extras.

## Review Batch And Freeze Gate

Before freezing a review finding set:

- Every expected batch exists.
- Each batch reviewed the epoch's declared subject revision.
- Every assigned required dimension is `covered`, including dimensions with no
  findings.
- Reviewer limitations are disclosed; `partial` or `blocked` dimensions prevent
  complete coverage.
- Every finding has an RVTF classification and required owner decision.
- Batches with different subject revisions do not freeze until revisions
  converge.
- A reviewer who reports one blocker but omits remaining dimensions has produced
  a valid finding but an incomplete batch.

Freeze defines bounded remediation scope only. It is not delivery completion.

## Review Cadence And Parent Coverage Gate

Before relying on review coverage:

- Set cadence to `unit`, `batch`, `milestone`, or `host_native`; dimension count
  does not determine reviewer or batch count.
- With `child_scope_policy: covered_at_parent`, list exact
  `covered_child_scope_refs`. Until the parent review actually runs, record
  `review_state: pending_at_parent`, never completed review evidence.
- If a Unit's closure contract requires that formal parent review, keep the Unit
  incomplete while coverage is pending. Unit self-checks remain useful but are
  not the missing formal receipt.
- After parent review, change the child to `covered_at_parent` only when an
  actual closed epoch and accepted batch or assessed carry-forward cover that
  child at the closure packet's exact subject revision. A declared contract or
  stale parent receipt is not coverage.
- Preserve every `host_native_required_batches` entry. Parent coverage cannot
  replace mandatory per-task, per-build, per-phase, or pre-merge review.
- Use `combined_allowed` only when one qualified batch can cover the declared
  dimensions. Use `separate_required` for expertise, segregation, or policy,
  and `host_native` for the host's actual fan-out.
- Match every expected host kind and assigned dimension only against complete
  batches or valid carry-forward accepted by the current closure. Historical,
  stale, supplemental, or unaccepted batches do not fill an assignment;
  `separate_required` assignments require a complete distinct-provider matching
  and cannot depend on provider-list order.
- Treat strict implementer independence as a coverage property, not a command
  to create one batch per dimension. Combination never removes a required
  specialist or independent batch. A supplemental self-check does not poison
  independently accepted coverage of all required dimensions.

## Remediation Review Gate

During remediation review:

- Check frozen findings, changed evidence, and direct remediation risk.
- Do not restart unrestricted review for each fix.
- Record the new subject revision and evidence for each remediation cycle.
- If remediation fails verification, continue bounded remediation for the frozen
  finding.
- If unrelated work changes the subject, invalidate the freeze and amend or
  reopen the epoch.
- If remediation introduces a direct regression, record a late finding and
  reopen on `remediation_regression`.

## Terminal Review Finalization Gate

After a terminal review or scoped re-review issues its verdict, decide whether
the update that records it is material or receipt-only before scheduling any
further reviewer.

- Bind the terminal verdict to the exact material subject it assessed, with its
  coverage, limitations, findings, disposition, and required independence.
- Accept receipt-only finalization only when a host-aware materiality assessment
  proves that the final diff attaches that verdict and changes only explicitly
  authorized derived finding, gap, review, closure, and continuation fields.
- Confirm no Requirement, Acceptance Item, Journey, evidence truth, review
  contract, finding meaning, amendment, residual risk, host gate,
  implementation, package, workflow, release, recovery, or rollback fact
  changed.
- Keep standalone validation separate: it can check internal trace consistency,
  but it cannot prove the repository diff, reviewer identity, independence,
  external locator, or materiality boundary.
- Run the internal trace validator and every mandatory current-boundary host
  gate after the terminal update.
- Do not schedule another review solely because the finalization commit records
  an already issued review verdict.
- Reject a self-declared receipt-only flag as evidence. Treat missing diff
  assessment, unresolved verdicts, and ambiguous or out-of-allowlist changes as
  material, then use impact assessment, delta review, or controlled reopen.

## Review Carry-Forward And Delta Gate

When remediation changes the review subject revision:

- Never edit or relabel the historical batch's epoch or subject revision.
- Carry unchanged coverage through a new `review_coverage_carry_forward` that
  resolves the source batch and target epoch and records exact from/to
  revisions, unchanged dimensions, assessor, and accepted impact assessment.
- For closure use, require `target_epoch` to equal the closure epoch and
  `to_revision` to equal both the epoch and closure subject revision.
- Require the impact assessment and carry-forward to agree on source, from/to,
  dimensions, assessor, rationale, and decision.
- Carry only dimensions the source batch actually covered.
- Run a bounded delta batch for changed dimensions. If unchanged impact cannot
  be established, create a new batch or use the existing controlled-reopen
  rules; do not silently rebind old evidence.

## Controlled Reopen Gate

For findings discovered after freeze:

- Reopen only when trace impact shows `required_gap`,
  `evidence_invalidated`, `remediation_regression`, `cross_cutting_risk`, or
  `accepted_scope_amendment`.
- Record affected requirements, affected dimensions, source finding, basis,
  owner decision, and next epoch.
- Do not reopen automatically for optional enhancements, style preferences,
  speculative hardening, unrelated refactoring, or out-of-scope findings that do
  not invalidate current evidence or requirements.
- Never dismiss an existing required gap only because it was discovered late or
  labeled low severity.

## Scope Amendment Gate

Before expanding scope:

- Record source finding, rationale, impacted requirements, owner decision, and verification.
- Do not implement an unapproved amendment except to stop an active safety or production incident.
- If an amendment blocks completion, reflect that in the closure packet.

## Continuation Gate

Before ending a new 0.4 non-Goal closure:

- Record the actual parent reference and disposition, remaining scope refs,
  next entry conditions, continuation mode, authority, locator, and execution
  action.
- Use `durable_host` only for authoritative persistent host state;
  `artifact_only` for a durable RVTF artifact without scheduling authority; and
  `advisory` when the user or external orchestrator retains the decision.
- Use `continue`, `stop`, `await_owner`, or `host_boundary` as the action. Add a
  canonical `stop_basis` only, and always, for an actual stop or host boundary.
- Keep blocked remaining work and its owner/entry conditions explicit. A host
  runtime boundary does not change parent disposition.
- Accept `goal_complete` only with a known closed parent or Goal and no
  remaining scopes. Accept `all_remaining_work_blocked` only with a non-empty
  set of resolved blocked scopes and a blocked or incomplete parent.
  Owner-requested, runtime-boundary, and command-completed stops explain the
  pause but do not promote or otherwise rewrite parent disposition.
- Record continuation capability only. RVTF never schedules the next command,
  workflow, story, reviewer, or session automatically.

## Operational Economy Warning Gate

Economy warnings never change delivery truth or skip a required gate. Warn when
the same command or review coverage is repeated on unchanged inputs, verifier
fan-out grows without target need, or an iteration changes no implementation,
evidence claim, finding, gap, or disposition.

On no progress, select a new unblocked scope, record a concrete rationale for
the repeat, or create an explicit blocker with owner and entry condition. Do not
use elapsed time, iteration count, token pressure, or response termination to
fabricate closure, and do not launch another host workflow merely to stay busy.

## Completion Gate

Before saying complete:

- Treat this as a full semantic audit of the current scope, not an unconditional
  instruction to run every repository suite. Run the verification-policy tier
  selected for this boundary plus every mandatory fresh/full host gate.
- Re-read the latest requirements, plan, and gap ledger.
- Verify every active required Acceptance Item has a valid disposition and every
  `verified` Item has fresh, target-specific evidence.
- Enforce status consistency: all active required Items must be `verified`
  before their Requirement can be `verified`; deferred, blocked, and rejected
  Items require the corresponding parent decision.
- Confirm the Journey applicability decision and rationale.
- For every applicable Journey, verify Step-to-Item mappings, referenced Item
  status, strong path evidence, expected outcome proof, recovery coverage, and
  Journey/Step gaps before allowing `verified`.
- Confirm review findings and scope amendments have decisions.
- If review governance is required, confirm the epoch is closed or has a
  controlled reopen, deferral, block, or residual-risk decision.
- If receipt-only finalization was used, confirm the terminal verdict resolved,
  the host-aware materiality assessment covered the final diff, only authorized
  derived transitions changed, and final trace plus host gates passed.
- Treat review closure as a sub-gate: missing path evidence discovered after
  freeze fails delivery closure but does not automatically reopen review. Use
  `evidence_invalidated` only when previously accepted evidence became invalid.
- Confirm all remaining Requirements, Acceptance Items, and Journeys are
  `deferred`, `blocked`, or `rejected` with owner and rationale where required.
- Produce a closure packet with separate Requirement, Acceptance Item, Journey,
  gap, review, amendment, verification-run, and residual-risk dispositions.
- For delivery hierarchies, run the inventory/aggregation gate and preserve
  incomplete or blocked parent truth after a child closes.
- For a new non-Goal 0.4 closure, validate its continuation contract without
  treating continuation as scheduler authority.
- Call delivery `complete` only when every required Requirement and every
  applicable Journey is `verified`.
- Do not start the next phase until leftover work becomes next-phase scope, entry criteria, or explicit exclusion.

## Reviewer Prompt Add-On

Add this block to spec or delivery reviews:

```text
Check the RVTF trace matrix. For each requirement ID:
- Is the requirement represented by implementation work?
- Does every canonical Acceptance Item have a stable ID and source reference?
- Is each Acceptance Item satisfied by target-specific evidence, not by claims?
- Are extra behaviors traced to an approved requirement?
- Are missing or partial behaviors recorded in the gap ledger?

For Journey applicability and each required Journey:
- Does the decision follow actor-goal-path triggers rather than a technical label?
- Does every required Step reference canonical Acceptance Item IDs without copying state?
- Does path evidence prove Step order, connection, and expected outcome?
- Are Item gaps and Journey-only path gaps propagated to the correct targets?

For each review finding:
- Is it classified before implementation?
- Is it linked to an existing requirement, accepted amendment, or constraint?
- Does it represent weak evidence, missing required behavior, optional scope, or a new safety constraint?

For governed review:
- Which review contract, epoch, subject revision, and dimensions were reviewed?
- Did every expected batch cover its assigned dimensions or disclose limitations?
- Are no-finding dimensions recorded as covered rather than omitted?
- Are late findings classified with a reopen, defer, reject, block, or amendment decision?
- Did a terminal receipt avoid recursive review only after a host-aware
  materiality assessment proved that no material truth changed?

Report missing Requirements or Acceptance Items, weak item or path evidence,
unverified implemented work, invalid Journey applicability, untraced extra
scope, unapproved amendments, and gaps without owner or close condition.
```
