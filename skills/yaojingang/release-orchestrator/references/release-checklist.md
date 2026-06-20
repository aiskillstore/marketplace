# Release Checklist

## Required Sections

- release summary
- dependency review
- migration notes
- rollout checklist
- rollback checklist
- stakeholder communication
- final go/no-go decision

## Release Summary Questions

- What changed in this release?
- Which services, schemas, or integrations are affected?
- What is the blast radius if rollout fails?

## Rollout Gate

- Sequencing is clear.
- Ownership is explicit.
- Monitoring signal is defined.
- Rollback trigger is concrete, not vague.

## Packet Failure Modes

- Missing migration notes when data changes exist
- Missing rollback trigger
- "Go" recommendation without acknowledged risk
- Stakeholder message missing audience or send timing
