---
name: incident-command-governor
description: Build governed incident command packets. Use when asked to standardize incident review, run severity assessment, or assemble incident communication.
---

# Incident Command Governor

## When To Use

- You need a reusable incident command packet from messy operational inputs.
- You need explicit severity assessment, stakeholder updates, and action ownership.
- You need a governed workflow that can be reviewed, maintained, and audited over time.

## Do Not Use

- The task is only to explain an incident concept.
- The task is only to draft a one-off update.
- The request is still brainstorming and not yet packaging a repeatable incident workflow.

## Workflow

1. Gather the minimum incident inputs:
   - incident summary
   - timeline evidence
   - affected systems and customers
   - severity indicators
   - owners and responders
   - stakeholder audiences
2. Read `references/severity-matrix.md` to assign or confirm severity.
3. Read `references/comms-policy.md` to shape internal and external updates.
4. Read `references/review-policy.md` before finalizing, because this skill is maintained under a monthly review cadence.
5. Use `scripts/build_incident_packet.py` with `input/incident_input_example.json` when deterministic packet assembly is needed.
6. Produce one governed incident packet with:
   - incident summary
   - severity block
   - evidence-backed timeline
   - affected scope
   - owner and action table
   - internal and external comms blocks
   - explicit open risks and review notes
7. Stop and report blockers if severity evidence or ownership data is missing.

## Output Contract

The final answer must include:

- a concise incident summary
- explicit severity and rationale
- a timeline section
- impact scope
- owners and next actions
- stakeholder communication blocks
- governance note for follow-up review

## Validation Checklist

- Severity is justified with evidence, not guessed.
- Owner and next actions are explicit.
- Communications are separated by audience.
- Missing evidence is surfaced as a blocker.
- The packet can be reviewed again without reconstructing context from chat history.

## Reference Map

- Read `references/severity-matrix.md` for severity rules.
- Read `references/comms-policy.md` for communication guidance.
- Read `references/review-policy.md` for review cadence and governed lifecycle expectations.
- Inspect `evals/trigger_cases.json` for routing boundaries.
- Inspect `outputs/incident_packet_example.md` for an example final artifact.
- Inspect `reports/governance_score.json` for the current maturity snapshot.
