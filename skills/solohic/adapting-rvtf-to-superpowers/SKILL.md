---
name: adapting-rvtf-to-superpowers
description: Use when applying requirements-to-verification traceability to Superpowers workflows, including brainstorming, writing plans, subagent-driven development, review, verification, branch finishing, or skill writing.
---

# Adapting RVTF To Superpowers

**REQUIRED BACKGROUND:** Use `tracing-requirements-to-verification`.

## Host Contract Snapshot

- Host repo/method: Superpowers `writing-plans`, `subagent-driven-development`,
  `executing-plans`, `verification-before-completion`, and
  `finishing-a-development-branch`.
- Branch: `main`.
- Revision: `b36e0829c6d0140e93cfef2ca599b1b07d4a7797`.

This mapping is pinned to that exact host revision. Re-audit it before use if
Superpowers task, review, verification, or branch-finishing behavior changes.

## Principle

Do not replace Superpowers. Add RVTF as the evidence thread running through the existing Superpowers lifecycle. RVTF defines Requirement, canonical Acceptance Item, Journey, evidence, gap, and closure semantics; Superpowers still decides task grouping, implementer/reviewer roles, and whether or how to delegate work.

## Shared RVTF Boundary

Use the required core Skill's schema, gate, and review-governance references for
detailed fields and algorithms; this adapter only maps host boundaries.

- Use `goal`, `milestone`, and `unit` only for containment. Use
  `delivery_groups` with `execution_batch`, `verification_batch`, or
  `review_batch` for execution, verification, and review grouping; group or Unit
  completion never auto-closes a parent Milestone or Goal.
- Effective gates are the union of host-native mandatory gates and RVTF-required
  gates. Reused `evidence_claims[].validity.status: valid` may avoid only gates
  whose freshness policy permits reuse; it never erases a fresh/full host gate
  or supports a current-test claim. Keep `host_gate_status` and
  `current_test_status_claim` separate.
- Keep implementer self-check, verification, and formal review distinct. Review
  dimensions do not imply reviewer or batch count. Parent coverage is future
  work recorded as `review_state: pending_at_parent`, never pre-recorded review
  evidence. Preserve strict independence from the implementer and every required
  specialist or segregation-of-duties fan-out.
- Review batches keep their subject revision immutable. Cross-revision reuse
  requires assessed `review_coverage_carry_forward`; otherwise run the required
  delta review or controlled reopen.
- When Superpowers emits a terminal scoped re-review verdict for a stable
  material subject, map that verdict to RVTF review evidence. A trace update
  that only records the verdict and its explicitly authorized derived
  transitions may use receipt-only finalization after a host-aware diff
  assessment. Do not create another reviewer solely to review that receipt.
- The Goal Continuation Contract is declarative: record one host authority,
  `continuation_mode: durable_host|artifact_only|advisory`, a resolvable or
  explicitly unknown locator as allowed by the mode, remaining scopes, and the
  actual `execution_action: continue|stop|await_owner|host_boundary`. RVTF never
  invokes another command or overrides user/orchestrator control.
- Any Superpowers host lifecycle outcome, including the branch-finishing
  decision, remains `host_status`; derive RVTF closure only from trace truth.
- Keep an SDD `Ruling` as a host execution decision with its reason and cost if
  wrong. Link it to the affected Requirement, finding, gap, or amendment
  decision, but never treat the Ruling itself as accepted scope, correctness
  evidence, review evidence, or closure. A controller may follow the binding
  approved spec for reversible in-worktree conflicts; unrequested scope stays
  rejected/deferred unless an authorized owner accepts an amendment.
- When an approved design contains a human decision Step, require the plan to
  map an actor-facing decision verifier. Keep machine binding through a stable
  token, but treat an opaque ID or fixture-only lookup as protocol evidence
  rather than proof of human judgment.

## Mapping

| Superpowers skill | RVTF addition |
| --- | --- |
| `superpowers:brainstorming` | Map a throwaway spike to `discovery` without a delivery closure claim. For a bounded path, keep the approved in-chat design as source provenance and use the lightest applicable RVTF artifact without inventing a host spec or plan file. For an architectural path, choose RVTF mode; define canonical Acceptance Items; decide Journey applicability from actor-goal-path triggers; when required, define actor, goal, expected outcome, and observable Steps. Also record requirement validity, constraints, assumptions, non-goals, and review applicability. |
| `superpowers:writing-plans` | Treat a plan/branch closure boundary as a Milestone and each independently closable task as a Unit. If the host groups tasks for execution, represent that orthogonally in `delivery_groups`. At the plan/branch Milestone or execution group, declare the four trace-ID mappings, verification policy, review cadence, planned item/path evidence, and approved amendments without changing host task boundaries. |
| `superpowers:subagent-driven-development` | Each independently closable task remains a Unit. When small same-shape tasks share one implementer dispatch, record that dispatch as an `execution_batch` and the actual combined task review as one `review_batch` with per-Unit coverage; neither group closes its members. The pinned host shape has one combined task reviewer returning specification-compliance and task-quality verdicts, followed after all tasks by one whole-branch review batch. Do not create an extra task reviewer from RVTF. The implementer self-check is not formal review. Record host Rulings with trace impact, and have the implementer report advanced trace IDs, evidence, findings, and gaps without mutating copied Item state. |
| `superpowers:executing-plans` | Keep host tasks as Units, but do not invent a per-task reviewer. Add an upper review only when an actual RVTF risk contract requires it. |
| `superpowers:requesting-code-review` | Map each actual host reviewer invocation to its actual batch over one stable subject revision; record both verdict/dimension coverage and limitations without deriving batch count from dimensions. |
| `superpowers:receiving-code-review` | Classify each comment before implementation; freeze only after expected batches are complete and subject revisions match. |
| `superpowers:verification-before-completion` | Check claim validity first, run any missing RVTF tier, then preserve the host's current-message fresh-verification contract. Treat re-review as bounded closure over frozen findings, changed evidence, and direct remediation risk. Map the terminal scoped re-review verdict to its material subject; if the final trace diff is receipt-only, run final validation and stop without a synthetic review round. The Completion Gate remains a semantic trace audit. |
| `superpowers:finishing-a-development-branch` | At the plan/branch Milestone, preserve the mandatory full suite on the integration tree plus review closure, a closure packet, amendment decisions, and explicit treatment of required gaps. A reusable claim cannot skip this host gate. If the host breaker is reached with residual findings, require owner adjudication, deferral, block, residual-risk acceptance, or controlled reopen rather than automatically repeating review. Preserve a worktree whose removal is refused because it has modified or untracked files; the owner must choose commit, move, or unrecoverable deletion before cleanup, and RVTF never converts branch closure into cleanup authority. |
| `superpowers:writing-skills` | Treat RVTF changes as process TDD: pressure scenario first, skill change second, forward-test third. |

## Prompt Additions

For every planned task, add the host mapping without changing Superpowers task
boundaries:

```yaml
requirement_ids: []
acceptance_item_ids: []
journey_ids: []
journey_step_ids: []
```

Between SDD tasks, record `execution_action: continue`; Unit closure is not a
pause. Closing the plan/branch Milestone still enters the host
`finishing-a-development-branch` lifecycle even when a higher Goal remains
incomplete. Before deleting a plan-scoped SDD ledger, persist that higher Goal's
continuation either in authoritative host Goal state (`durable_host`) or at a
resolvable durable RVTF artifact locator (`artifact_only`). Superpowers remains
the only workflow authority; RVTF adds no scheduler.

For implementer subagents, add:

```text
Track RVTF coverage. Report which Requirement, Acceptance Item, Journey, and
Journey Step IDs advanced; which item or path evidence was added; and which
gaps, review findings, or scope amendments need a decision. Do not infer a
verified parent or Journey from task completion.
```

For every SDD controller Ruling, add the affected trace reference and state
whether it preserves existing scope, rejects/defers an unaccepted proposal, or
records an owner-authorized amendment. Include every Ruling in the host's final
Ruling summary; never let it disappear with the SDD workspace.

For spec reviewers, add:

```text
Review Requirement and Acceptance Item IDs line by line. Do not approve based
only on task text, worker report, or passing tests. Every required Item needs
target-specific evidence or a gap decision. For each applicable Journey, check
Step-to-Item mapping plus path order, connection, and expected-outcome evidence.
Classify each review finding before recommending implementation.
If bounded review governance applies, report the review epoch subject revision,
assigned dimensions covered, dimensions with no findings, and limitations.
```

## Completion Rule

In Superpowers, "all tasks complete" and "review closed" are not the final
condition. The final condition is: all required Acceptance Items aggregate
consistently to their Requirements; every applicable Journey has valid path and
outcome evidence; all remaining objects have explicit dispositions; and any
governed review epoch is closed or has a controlled reopen, deferral, block, or
residual-risk decision.

## Review Feedback Rule

When using Superpowers review skills, no review finding becomes work until it is linked to an existing requirement, accepted scope amendment, or cross-cutting constraint. Optional improvements stay deferred or rejected unless an owner changes the scope.

Do not let remediation review become a fresh unrestricted review loop. After
freeze, review only frozen findings, changed evidence, and direct remediation
risk unless a late finding justifies controlled reopen through RVTF trace impact.

After the terminal scoped re-review, bind its verdict to the exact material
subject. If a host-aware diff assessment confirms that the only subsequent
change records that verdict and authorized derived closure transitions, use
receipt-only finalization and stop. Do not create another reviewer or restart
the host review loop solely because the ledger now contains the verdict. A
mixed or ambiguous diff remains material and follows normal impact,
delta-review, or controlled-reopen handling.
