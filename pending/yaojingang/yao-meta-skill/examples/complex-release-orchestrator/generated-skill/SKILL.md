---
name: release-orchestrator
description: Coordinate software release preparation, rollout readiness, migration notes, rollback planning, stakeholder communication, and final go/no-go release packets. Use when asked to prepare a release packet, review release readiness, or turn scattered launch notes into one reusable release workflow. Do not use for generic project planning, one-off announcement drafting, or high-level release theory.
---

# Release Orchestrator

## When To Use

- You need one reusable release packet from scattered launch inputs.
- You need to verify migration notes, rollout steps, rollback triggers, and stakeholder messages before release approval.
- You need a go/no-go summary with explicit blockers.

## Do Not Use

- The request is only to explain a release concept.
- The request is only to write a single announcement.
- The request is still brainstorming and not yet packaging a repeatable release workflow.

## Workflow

1. Gather the minimum release inputs:
   - release scope
   - risky changes
   - migrations
   - rollout sequencing
   - rollback triggers
   - communication audiences
2. Read `references/release-checklist.md` and `references/risk-matrix.md` to determine required sections and escalation thresholds.
3. Read `references/migration-template.md` and `references/stakeholder-comms.md` when migrations or communications are present.
4. Use `scripts/build_release_packet.py` with `input/release_input_example.json` as the shape reference when deterministic packet assembly is needed.
5. Produce one release packet with:
   - release summary
   - dependency and migration section
   - rollout steps
   - rollback triggers
   - stakeholder communication plan
   - explicit go/no-go decision
6. If release-critical data is missing, stop and report blockers instead of pretending readiness.

## Output Contract

The final answer must include:

- a concise scope summary
- a risk block with severity
- migration notes or a clear "none required"
- rollout plan
- rollback plan
- stakeholder communication block
- a final decision: `GO`, `GO WITH CONDITIONS`, or `NO-GO`

## Validation Checklist

- Release-critical inputs are either present or explicitly flagged as missing.
- Rollout and rollback are both covered.
- Migration notes are not omitted when schema or data changes exist.
- Stakeholder communication is tailored by audience and timing.
- The final decision is explicit and justified.

## Reference Map

- Read `references/release-checklist.md` for required packet sections.
- Read `references/risk-matrix.md` for decision thresholds.
- Read `references/migration-template.md` for migration note structure.
- Read `references/stakeholder-comms.md` for announcement scaffolds.
- Inspect `evals/trigger_cases.json` for trigger boundaries.
- Inspect `outputs/release_packet_example.md` for an example final artifact.
