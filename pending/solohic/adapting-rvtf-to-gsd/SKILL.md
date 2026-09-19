---
name: adapting-rvtf-to-gsd
description: Use when applying requirements-to-verification traceability to GSD planning, plan review, phase validation, verification, shipping, convergence, or gap-control workflows.
---

# Adapting RVTF To GSD

**REQUIRED BACKGROUND:** Use `tracing-requirements-to-verification`.

## Host Contract Snapshot

- Host repo/method: GSD Core project/milestone/phase/PLAN execution,
  verification, UAT, and ship lifecycles.
- Branch: `next`.
- Revision: `cf3eb84b3ff1e595a5038d9c96d20a9c3a5e5c16`.

This mapping is pinned to that exact host revision. Re-audit it before use if
GSD planning, Wave, verifier, review, or `.planning` authority changes.

## Principle

GSD is strong at goal convergence. RVTF makes the convergence auditable by turning goals, canonical Acceptance Items, actor Journeys, evidence, and gaps into traceable decisions. GSD retains its phase, goal, plan, verification, and shipping lifecycle.

## Shared RVTF Boundary

Use the required core Skill's schema, gate, and review-governance references for
detailed fields and algorithms; this adapter only maps host boundaries.

- Use `goal`, `milestone`, and `unit` only for containment. Use
  `delivery_groups` with `execution_batch`, `verification_batch`, or
  `review_batch` for execution, verification, and review grouping. A Wave/group
  or child Unit completion never auto-closes a Phase Milestone or parent Goal.
- Effective gates are the union of host-native mandatory gates and RVTF-required
  gates. A reused `evidence_claims[].validity.status: valid` claim never removes
  a fresh/full host gate or claims current tests pass; keep `host_gate_status`
  and `current_test_status_claim` separate.
- Keep self-check, verification, and formal review distinct. Dimensions do not
  imply batch count. Parent coverage remains
  `review_state: pending_at_parent` until actual review. Preserve strict independence
  and required specialist or segregation-of-duties fan-out.
- Review batch subject revisions are immutable. Cross-revision coverage needs
  assessed `review_coverage_carry_forward`; otherwise use delta review or
  controlled reopen.
- The Goal Continuation Contract is declarative: use one host authority and
  record `continuation_mode: durable_host|artifact_only|advisory`, locator,
  remaining scopes, and actual
  `execution_action: continue|stop|await_owner|host_boundary`. RVTF never invokes
  a GSD command/PLAN or overrides user/orchestrator control.
- Resolve the selected planning root through the host Planning Workspace Module.
  `GSD_WORKSTREAM`, a valid session/shared pointer, and the root project may
  identify different planning roots; never merge or vote their state. Treat the
  selected root as `durable_host` only while its workstream ownership and state
  are coherent. GSD's `milestone.lock` in that root is an advisory claim, not a
  mutex: a command may report typed `milestone_conflict` and still mutate
  `STATE.md`. An unresolved conflict is a state-integrity gap. Do not trust
  `Current Position`, advance, or close from it; reconcile the exact Phase
  artifacts and owner, restore one writer, then resume. An incomplete or
  unreadable state-validation scope is likewise an evidence gap, even when a
  sibling boolean or warning looks benign.
- Keep `.planning/state.json` as a versioned, best-effort host display cache. It
  cannot fail its publisher and has no diagnostic channel; `complete`, empty, or
  missing values never override `planning inspect` diagnostics or canonical
  Phase verification. Use `planning inspect` when closure depends on knowing
  whether a required document was absent, unreadable, or unparseable.
- Only canonical `verification.status: passed` closes a GSD Phase. PLAN and
  SUMMARY existence proves implementation progress, not verification. Treat
  `missing`, `unknown`, `human_needed`, `gaps_found`, `stale`, or an
  indeterminate/unreadable verification scope as pending; route human checks
  through UAT and `await_owner`, and resume the full remaining tail-gate chain.
- Any GSD host lifecycle outcome, including `override_closeout`, remains
  `host_status`; RVTF closure is derived independently.

## Host Hierarchy And Grouping

- GSD Project is the host container. Map the current GSD Milestone to an RVTF
  Goal, GSD Phase to Milestone, and GSD PLAN to Unit. PLAN Tasks are internal
  Unit checkpoints, not delivery scopes.
- Map an execute-phase Wave through `delivery_groups` as an
  `execution_batch`; it groups PLAN Units without becoming their parent.
- Map `worker` to PLAN Task/focused checks and PLAN overall verification;
  `batch` to Wave post-merge build, tests, and hooks; `milestone` to the Phase
  verifier/`VERIFICATION` plus UAT where required; and `completion` to the GSD
  milestone audit/readiness decision. Child claims are inputs, never permission
  to skip the host Phase verifier.

## Host Review And Continuation

- Preserve the pinned split: the plan checker retains its host gate;
  capability-dependent execute-phase code review is advisory, and its failure
  does not block execution at this revision; PR review remains host-directed.
  Only separately declared blocking hooks or contracts may block. Add another
  formal RVTF review only when the actual risk contract requires it.
- Map actual reviewer-lane invocations, not merely declared capabilities, to
  `review_batch` records, and disclose their model/tool trust and limitations.
  `review.parallel_lanes: true` changes scheduling only: join all selected lanes
  before `REVIEWS.md` and consensus, while convergence cycles remain sequential.
  Preserve the shared-adapter caveat when reviewer instances use one CLI; their
  count does not prove provider/tool diversity or strict independence. A failed
  lane's diagnostic stub is limitation evidence, not dimension coverage, and a
  partial consensus cannot fill the missing batch.
  At this revision execute-phase code review remains advisory except for an
  active blocking hook or the documented MVP+TDD escalation. Active security
  and broken-windows ship gates are mandatory host gates: open, missing, or
  unreadable gate evidence blocks shipping. A waiver is an explicit owner
  decision with residual risk, not an inferred pass.
- The pinned `/gsd:ship` workflow treats its configured external-review command
  and `REVISE` verdict as advisory and falls through to manual review, despite
  `workflow.code_review_command` documentation saying non-zero blocks. Record
  that upstream contract drift and follow the executable workflow; do not
  promote the external review to a hard gate unless an actually active blocking
  hook or project contract does so.
- A capability probe that reports `no-input`, `could-not-run`, `skipped`, or no
  parseable result produced no verdict. Do not convert an adjacent boolean or
  exit code into a pass. Evaluate each hook crash through its declared
  `ON_CRASH` policy: `DENY` blocks the effective gate, while `ALLOW` is a
  diagnosed fail-open and still does not prove the probed behavior.
- Preserve the versioned process-exit contract. Under `GSD_EXIT_CONTRACT=v1`, a
  negative data result may still exit zero; v2 uses registered non-zero codes.
  Read the typed payload and selected contract rather than treating exit zero as
  semantic success.
- Preserve negotiated executor isolation as host truth:
  `harness-worktree|orchestrator-worktree|none`. In orchestrator-worktree mode
  GSD owns worktree creation, validation, merge, and git operations; the
  sandboxed executor does not. An unknown capability or base mismatch degrades
  conservatively to sequential execution or fails closed as the host specifies;
  RVTF neither creates a worktree nor upgrades the degraded run to parallel.
- GSD goal-backward verification remains authoritative. Phase closure records
  the unresolved truth of the parent Goal rather than promoting it to complete.
- Derive `durable_host` continuation from the selected root/workstream's
  `STATE`, `ROADMAP`, `PLAN`, `SUMMARY`, `VERIFICATION`, `UAT`, and `HANDOFF`
  under the Planning Workspace Module and orchestrator's single-authority,
  single-writer, and lock rules. RVTF creates no parallel state source; the
  orchestrator, not parallel workers, updates shared continuation.
- `override_closeout` changes only `host_status`. A blocked or incomplete scope
  stays RVTF blocked/incomplete unless accepted deferral or residual-risk rules
  actually close it.
- `/gsd:ship` is an external-action boundary: it pushes the branch and creates
  a PR, and may push a later ship-note commit. Readiness never authorizes RVTF
  to invoke it. A pushed branch or open PR is not merge, deployment, release,
  Phase verification, or Goal closure evidence.

## Mapping

| GSD concern | RVTF addition |
| --- | --- |
| Plan completeness is not goal achievement | Require evidence for each Requirement and canonical Acceptance Item before completion. |
| Task completion is not goal achievement | Close tasks only as implementation progress; update Items and Requirements from item evidence and Journeys from referenced Items plus path evidence. |
| Existence is not integration | Add integration Acceptance Items and, when an actor-goal path exists, Journey Steps with ordered path/outcome verification. |
| MVP user flow | Map the user flow to an Actor Journey and its observable Steps when path triggers apply; map GSD user-story acceptance to canonical Acceptance Items. |
| Human decision Step | Put an actor-facing decision verifier in the owning PLAN/Phase validation scope. Keep machine binding through a stable token, but treat an opaque ID or fixture-only lookup as protocol evidence rather than proof of human judgment. |
| Non-MVP phase | Keep phase/goal as the host axis and decide Journey applicability from general path triggers rather than forcing a user flow. |
| Phase plan | Map each plan/task to `requirement_ids`, `acceptance_item_ids`, `journey_ids`, and `journey_step_ids`. |
| Review findings can inflate scope | Classify findings and require accepted amendments before new work. |
| Multiple phase reviews can drip new blockers | Declare review applicability, contract expected batches, and freeze only after covered dimensions share one subject revision. |
| Evidence can be weak | Check evidence quality before marking rows verified. |
| Cross-agent plan convergence | Compare plans by requirement-ID coverage, not by similar task wording. |
| Cross-cutting constraints | Track safety, privacy, compatibility, migration, and regression constraints as rows. |
| Goal-backward verification | Align the phase goal with Journey `expected_outcome`, walk backward through path evidence and Steps to canonical Items, then inspect item evidence; review freeze never replaces this walk. |
| Phase verification | Report Item evidence gaps separately from Journey path gaps, propagate each only to affected objects, and reject dual-axis closure when either required axis is open. |
| Concurrent `.planning` mutation | Preserve typed `milestone_conflict` as a state-integrity gap, distrust the clobbered single-slot position, reconcile per-Phase artifacts and ownership, then restore single-writer continuation. |
| Workstream and state projection | Resolve the selected planning root through `GSD_WORKSTREAM`/Planning Workspace Module; treat `state.json` as best-effort display state and `planning inspect` as the diagnostic surface without replacing canonical verification. |
| Phase status routing | Require canonical `passed`; preserve `missing`, `unknown`, `human_needed`, `gaps_found`, stale, and unreadable/indeterminate states as distinct pending reasons. |
| Reviewer lanes and consensus | Record actual lane receipts, join parallel lanes before synthesis, preserve shared-adapter and failed-lane limitations, and reject partial consensus as missing coverage. |
| Runtime isolation and exits | Preserve negotiated isolation, GSD git authority, safe sequential degradation, declared hook crash policy, and versioned payload/exit semantics. |
| Capability gates | Separate advisory review output from active blocking hooks; include security and broken-windows gates in the effective host gate set and record explicit waivers as residual-risk decisions. |
| Shipping | Require review closure when applicable, a closure packet, and gap-ledger decisions; treat push/PR creation as an explicit host/user action and never as merge, deployment, release, or Goal closure. |

## GSD Gate Add-On

When running a GSD validation or ship review, ask:

```text
Which Requirement and Acceptance Item IDs prove the goal is achieved?
Which Items only have implementation but no target-specific evidence?
When Journey Trace applies, which Journey and Step IDs represent the MVP or
system flow, and what path evidence proves order and expected outcome?
Which verified Items or Journeys rely on weak or out-of-gate evidence?
Which review findings are required gaps, amendments, optional extras, or constraints?
If formal review applies, which review epoch, subject revision, dimensions, and
batches prove the declared review surface was traversed?
Which gaps are being carried forward, and where are they owned?
What extra work was done without a requirement?
```

## Completion Rule

GSD may decide whether a phase is fit to move forward. RVTF supplies the evidence basis for that decision.

Use `discovery` mode for goal exploration, but switch to `standard` or `strict` before a completion or ship decision.

If bounded review governance applies, a closed review epoch is only a sub-gate.
Run the full goal-backward Closure Packet decision before shipping or advancing
the phase. The packet must enforce Item-to-Requirement aggregation and list
Journey path gaps separately from Item evidence gaps.
