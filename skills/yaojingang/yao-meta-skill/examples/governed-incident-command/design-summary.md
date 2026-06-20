# Design Summary

This example is intentionally governed rather than merely complex.

## Scope

The skill exists to assemble reusable incident command packets from messy operational artifacts.

It does not exist for:

- generic debugging help
- one-off status message drafting
- incident theory or training-only explanations

## Boundary Decisions

- Severity policy moved to `references/severity-matrix.md`
- stakeholder messaging moved to `references/comms-policy.md`
- monthly review expectations moved to `references/review-policy.md`
- deterministic output shaping moved to `scripts/build_incident_packet.py`
- a governed `manifest.json` is required because this skill is intended to be reviewed and maintained

## Why This Is A Governed Example

- explicit owner
- monthly review cadence
- active lifecycle state
- governed maturity tier
- reports and evidence files
- trigger evals plus sample output artifact
