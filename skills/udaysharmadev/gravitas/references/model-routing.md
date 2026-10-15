# Gravitas -- Model Routing Reference

> WARNING: This document describes a conceptual routing policy.
> The specific model ordering has NOT been benchmarked.
> Do not treat these recommendations as optimal until GravitasBench data confirms them.
> Model names below are dated examples -- check host `/usage` for current offerings.

## The Principle

Spend intelligence where expected error cost exceeds expected inference cost. Route to stronger models (or deeper effort) when the cost of getting it wrong exceeds the cost of a longer, more expensive run.

## Conceptual Routing Policy

simple fix / answer / review
  -> fast inexpensive model + eco

moderate feature / debugging
  -> fast inexpensive model + balanced

high uncertainty / architecture / security
  -> fast model (high effort) OR Pro-class model + deep

parallelizable large project
  -> native Antigravity Teamwork

unresolvable failure after circuit breaker
  -> Antigravity Boost / manual model escalation

## When Native Antigravity Features Are Better

Do not replicate what Antigravity already does well:

| Task type | Use Gravitas | Use Antigravity native |
|-----------|:---:|:---:|
| Reliability enforcement | yes | -- |
| Evidence tracking | yes | -- |
| Requirement coverage | yes | -- |
| Interruption recovery | yes | -- |
| Parallel large project | -- | Teamwork |
| Maximum reasoning depth | -- | Boost |
| Single-session complex task | yes | -- |

Gravitas + Teamwork and Gravitas + Boost are compatible and complementary.

## Available Models in Antigravity (example snapshot, September 2026 -- verify)

- Gemini 3.8 Flash Medium
- Gemini 3.8 Flash High
- Gemini 3.7 Flash Medium
- Gemini 3.1 Pro High
- Claude Sonnet 4.6 Thinking
- Claude Opus 4.6 Thinking

Any of these may serve as baseline, treatment, or reference model in a
matched GravitasBench configuration. No model is the product's identity.

## Quota-Aware Routing

Monitor quota state with /usage before starting a long session.

If premium model quota is low:
1. Switch to a fast inexpensive model + Gravitas (the intended fallback)
2. Gravitas state.json allows continuation from any model switch point
3. The reliability difference should be reduced by Gravitas enforcement

This is Gravitas's core use case: when the premium quota is gone, the fallback with Gravitas should lose less reliability than the bare fallback model.

## GravitasBench Will Measure This

The actual reliability difference between models with and without Gravitas will be quantified in GravitasBench v1. Until that data exists, this document describes a working hypothesis, not a proven routing strategy.
