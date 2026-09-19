---
name: adapting-rvtf-to-bmad
description: Use when applying requirements-to-verification traceability to BMAD specs, memlogs, adversarial reviews, edge-case reviews, verification-gap reviews, or preservation checks.
---

# Adapting RVTF To BMAD

**REQUIRED BACKGROUND:** Use `tracing-requirements-to-verification`.

## Host Contract Snapshot

- Host repo/method: BMAD Method Epic/SPEC, Story, Build/build-auto and one-shot,
  review/triage, retrospective, and orchestrator lifecycles.
- Branch: `main`.
- Revision: `6b83751711d34027fe2d0b8d67f6fcde135acb11`.

This mapping is pinned to that exact host revision. Re-audit it before use if
BMAD Story, Build, review/triage, or orchestrator behavior changes.

## Principle

BMAD is strong at spec preservation and gap review. RVTF supplies the canonical Requirement, Acceptance Item, Journey, evidence, gap, and decision records that BMAD reviews preserve and challenge. BMAD keeps its Story, build, review, and memlog lifecycle.

## Shared RVTF Boundary

Use the required core Skill's schema, gate, and review-governance references for
detailed fields and algorithms; this adapter only maps host boundaries.

- Use `goal`, `milestone`, and `unit` only for containment. Use
  `delivery_groups` with `execution_batch`, `verification_batch`, or
  `review_batch` for execution, verification, and review grouping. A Build run,
  group, or Unit completion never auto-closes a parent Epic/release.
- Effective gates are the union of host-native mandatory gates and RVTF-required
  gates. Reused `evidence_claims[].validity.status: valid` never removes a
  fresh/full host gate or claims current tests pass; keep `host_gate_status` and
  `current_test_status_claim` separate.
- Distinguish worker self-check, verification, and formal review. Dimensions do
  not imply reviewer or batch count. Parent coverage remains
  `review_state: pending_at_parent` until an actual receipt exists. Preserve
  strict independence and required specialist or segregation-of-duties fan-out.
- Keep historical review subject revisions immutable. Use assessed
  `review_coverage_carry_forward`, delta review, or controlled reopen instead of
  rebinding a prior batch.
- The Goal Continuation Contract is declarative: use one host authority and
  record `continuation_mode: durable_host|artifact_only|advisory`, locator,
  remaining scopes, and actual
  `execution_action: continue|stop|await_owner|host_boundary`. RVTF never invokes
  another Build, Story, or change scope and never overrides user/orchestrator
  control.
- Any BMAD Build or Story terminal outcome, including `done`, remains
  `host_status`; RVTF closure follows trace truth.
- A free-form one-shot remains a direct Unit. At this revision the host first
  investigates, then may write a minimal `route: in-session` spec before
  implementation when no intent gap, irreversible action, or material footprint
  exists. The frozen block is source preservation, not owner approval; only the
  full dispatch checkpoint supplies that approval. Treat the minimal spec as
  host provenance, not a fabricated Story or accepted scope amendment. Without
  an actual `story_key`, sprint-status synchronization must not update an
  arbitrary Story.
- Treat a BMAD retrospective as an evidence-based assessment of an Epic, not an
  implementation loop. Missing runtime behavior checks narrow the assessed
  scope and remain evidence gaps. Its machine verdict, action items, and retro
  `done` status stay distinct from RVTF closure: unfinished Stories force the
  headless machine verdict to `rejected`; `fix-now` items are proposals until
  an authorized owner routes them; and finishing the retrospective proves only
  that the retrospective ran. It never grants authority to implement, mark an
  Epic complete, push, or publish.

## Host Scope, Gate, And Review Mapping

- Map an Epic or SPEC scope to a Goal or Milestone according to its actual
  closure boundary. For a Story-backed run, map Story to Unit and attach the
  Build execution record to that Unit; Story Acceptance Criteria remain the
  canonical Acceptance Items. For a direct free-form intent or standalone spec
  run, map its single actual change scope to an appropriate Unit without
  fabricating Story ownership. A Build run never becomes a new Build Unit.
- Every Build/build-auto run's review and triage is host-native mandatory and
  cannot be skipped by Epic/Milestone parent coverage or evidence reuse.
- Launch all active review layers before consuming results, then preserve each
  finding's identity while the host verifies its claimed consequence and assigns
  severity. Group only surviving findings by shared root cause. A layer or
  dimension is not automatically a separate review batch; record actual
  invocations and receipts.
- Keep host triage (`intent_gap|bad_spec|patch|defer`) separate from RVTF finding
  classification and disposition. For Build Auto scope decisions, use the
  invocation `verbatim_intent` or an existing `<intent-contract>` as source
  authority; the generated spec, plan, or diff cannot alone prove that a finding
  is out of scope.
- Scope that triage vocabulary to full Build and Build Auto. For
  `route: in-session`, review uses only `patch|HALT|defer` and has no
  `bad_spec` loopback: patch a weak-plan finding only when the one-shot trivial
  fix rule holds; otherwise preserve the host HALT for human direction.
- Preserve the exact repair threshold: `review_loop_iteration > 5` blocks the
  sixth proposed loopback, not the fifth completed iteration. Interactive Build
  halts for the human; Build Auto records a blocked non-convergence result. Do
  not invent the stronger terminal state for the interactive path.
- Map adversarial, edge-case, and verification-gap review to dimensions. Do not
  multiply them into batches unless actual host roles, specialist risk, strict
  independence, or segregation of duties requires fan-out.
- Preserve the host verification-gap evidence rule: tests must execute and
  observe deterministic changed behavior. Reject demands to test static source
  wording or brittle LLM output; they are not verification gaps merely because
  no such test exists.
- When Story acceptance includes a human decision Step, put an actor-facing
  decision verifier in the owning Build/UAT scope. Keep machine binding through
  a stable token, but treat an opaque ID or fixture-only lookup as protocol
  evidence rather than proof of human judgment.
- One Build/build-auto invocation handles one Story-backed run or one direct
  change scope. Story or Unit closure never closes an Epic/release; the
  orchestrator owns backlog order, next Story/change-scope selection, and
  blocked routing.
- A folder+ID blocked Story is not a resumable locator: dispatching the same ID
  halts as `story already blocked`. Preserve the blocked Story and required-child
  impact until the external orchestrator/owner supplies an explicit recovery
  decision; RVTF does not delete the file or manufacture a known-good spec.
- `followup_review_recommended: true` is advisory output, not a gate, backlog,
  resume permission, or review obligation. Host `deferred` findings are also not
  a backlog; the orchestrator decides whether to create separately authorized
  work, while RVTF preserves their classification and current-scope disposition.
- Derive continuation from the Build spec terminal status, deferred findings,
  and one orchestrator authority/reference. At the command boundary it is
  normally `artifact_only` or `advisory` with `execution_action: stop` or
  `host_boundary`; return control rather than scheduling the next Story or
  change scope.
- BMAD `done` changes `host_status` only and never promotes a parent RVTF scope
  to complete.

## Mapping

| BMAD area | RVTF addition |
| --- | --- |
| Spec kernel | Store capability tree, Requirement IDs, canonical Acceptance Items, Journey applicability, required Journeys and Steps, verification methods, validity decisions, constraints, non-goals, and review contract when formal review can affect closure. |
| Story | Treat a Story as a candidate Journey source, not an automatic Journey. Map Story acceptance criteria to canonical Acceptance Items and decide Journey applicability from the actual actor-goal path. |
| Build one-shot | Map the actual free-form change to one direct Unit. Preserve the pre-implementation `route: in-session` minimal spec as unapproved host provenance; if implementation reveals an intent gap, irreversible action, or footprint growth, preserve the host escalation to full dispatch planning. Do not attach sprint Story status without a resolved `story_key`. |
| Build/build-auto Tasks & Acceptance | For Story-backed work, attach the Build execution record to its Story Unit. For direct intent or a standalone spec, attach it to the one appropriate Unit representing the actual change scope; never invent a Story. Map that Unit to Requirement, Acceptance Item, Journey, and Journey Step IDs. Use the I/O & Edge-Case Matrix to expose Item criteria and required alternative or recovery Steps without copying Item state. |
| UAT and edge-case execution | Record target-specific item evidence and, when the executed flow proves ordered Steps and expected outcome, explicit path evidence with covered Journey Step IDs. |
| Append-only memlog | Record Item, Requirement, and Journey status changes; item/path evidence; Journey applicability; review lifecycle; finding classifications; amendment decisions; and gaps as append-only events. |
| Review verification gap | Classify each gap against requirement ID, evidence quality, adoption, regression, verification method, or scope amendment. |
| Adversarial review | Attack unsupported `verified` claims, untraced extra scope, optional review findings that became work without approval, and incomplete review-batch coverage. |
| Edge-case hunter | Create missing acceptance criteria, candidate constraints, scope amendments, or gap entries for uncovered edge cases; late discoveries still need controlled closure-impact decisions. |
| Preservation validation | Check that later plans preserve canonical Item IDs/status, Journey/Step mappings, item/path evidence, gap targets, Requirement decisions, amendments, and review epoch decisions. |
| Evidence-based retrospective | Inventory the Epic's declared criteria, Stories, revisions, verification, review, and runtime behavior evidence. Record missing inputs as narrowed assessment or gaps; map the machine acceptance verdict to `host_status`; keep proposed remediation/action items pending owner disposition; and derive Epic closure only through the RVTF Completion Gate. |

## BMAD Review Add-On

Use this prompt in BMAD reviews:

```text
Review the RVTF trace matrix and gap ledger. Find Requirements or Acceptance
Items without evidence, evidence that does not prove its declared Item or
Journey target, Journeys whose ordered Steps or expected outcome are unproven,
untraced scope, review findings that were implemented without classification,
lost deferred gaps, status changes not supported by the memlog, review batches
that omit assigned dimensions, and remediation changes outside the frozen
finding set.
```

## Completion Rule

BMAD can challenge whether the Story or direct change scope stayed intact. RVTF defines the rows and evidence BMAD should challenge.

Attach this mapping to the relevant Story or build task while preserving BMAD's
own grouping:

```yaml
requirement_ids: []
acceptance_item_ids: []
journey_ids: []
journey_step_ids: []
```

Story completion does not auto-verify its Acceptance Items or any candidate
Journey. UAT can support both evidence axes only when its records separately name
the Item criterion and the covered Step order/outcome claims.

When BMAD discovers a new edge case, do not treat it as automatic work. Record whether it is a required gap, candidate cross-cutting constraint, accepted amendment, optional enhancement, or rejected extra.

Freeze does not suppress edge-case discovery. It controls whether a late edge
case reopens current delivery, becomes an amendment, is deferred, or is rejected
outside the current closure decision.
