# Risk-Adaptive Shaping

“厚积” does not mean maximizing documentation. It means reducing the uncertainties that are expensive to discover late.

> **Shape according to the cost of being wrong.**

Use two dimensions:

1. **Reversibility** — how easy is it to undo the decision?
2. **Failure consequence** — how damaging is a wrong decision?

## Decision matrix

| | Low consequence | High consequence |
|---|---|---|
| **Easy to reverse** | Move fast; test directly | Run a focused experiment before broad rollout |
| **Hard to reverse** | Deliberately shape the decision | Deep validation, rehearsal, and explicit ownership review |

## Low-risk examples

- wording and layout tweaks;
- internal tools;
- reversible feature-flagged experiments;
- local implementation choices with no public contract.

These should not be slowed by heavyweight governance.

## High-risk examples

- public APIs and plugin contracts;
- authentication and permission models;
- billing and entitlement rules;
- core database schemas;
- irreversible migrations;
- security boundaries;
- data retention or destructive operations.

## Evidence tools

Choose only the tools that reduce a material uncertainty:

- disposable Spike;
- PoC;
- prototype;
- ADR;
- benchmark;
- usability test;
- load test;
- migration rehearsal;
- security review;
- rollback rehearsal.

## AI capability shaping

When AI behavior is a key uncertainty, test with realistic inputs and capture:

- task success criteria;
- known failure modes;
- structured-output stability;
- hallucination or unsupported-answer behavior;
- latency distribution;
- token/inference cost;
- sensitivity to context size and noisy input;
- deterministic, rules-based, or non-AI alternatives.

A successful demo is evidence that a capability can work under tested conditions. It is not evidence that the architecture, economics, or ownership model are ready for production.

Use [Risk Review](../templates/risk-review.md) to record the decision.
