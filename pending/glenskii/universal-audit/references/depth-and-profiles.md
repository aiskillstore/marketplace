# Depth Tiers and Risk Profiles - Selection Guide

Normative definitions live in the spec (Sections 5.2 and 13.0). This file is the
practical selector used in Phase 0.

## Choosing a depth tier

| Signal | Tier |
|---|---|
| Early risk screen, pre-release sanity check, advisory only | **Rapid** |
| Production-readiness decision for a normal-consequence product | **Standard** |
| Regulated data, customer assurance deliverable, high blast radius, acquisition review | **Deep** |

Rules that follow from the tier:

- Rapid selects R controls; Standard selects R+S; Deep selects R+S+D.
- Rapid audits can never issue APPROVED unless every approval gate is independently
  satisfied, and must report coverage against the Standard denominator too.
- Standard requires a separate contradiction pass; Deep requires an independent
  challenger that did not author the findings.
- A time box shrinks coverage, never evidence standards.

## Choosing a risk profile

| Profile | Pick when the product is... | Critical categories |
|---|---|---|
| **P1** Public Consumer | A public website, consumer SaaS, or mobile app | Security/privacy, reliability/ops, UX/product fitness, accessibility |
| **P2** Internal Business | An internal portal or line-of-business tool with controlled users | Security/privacy, architecture/data, quality/correctness, reliability/ops |
| **P3** Data-Sensitive | Handling health, finance, legal, identity, or regulated data | Security/privacy, architecture/data, reliability/recovery, deployment/supply chain |
| **P4** Desktop/Local Utility | A local-first desktop tool or offline utility | Quality/correctness, architecture/data, deployment/supply chain, reliability/recovery |
| **P5** Platform/API | An API, developer platform, or infrastructure service | Security/privacy, reliability/ops, architecture/data, performance/capacity |
| **P6** Model-Assisted | Built around generative models, agents, retrieval, or automated decisions | Security/privacy, quality/correctness, architecture/data, reliability/ops |

Modifiers that raise scrutiny (record them in the manifest): public administration,
children or vulnerable users, safety impact, high transaction value, multi-tenancy,
administrator concentration, irreversible operations, internationalization, contractual
accessibility obligations.

Weight adjustments: a profile may shift any category by at most ±5 percentage points,
totals must stay at 100%, and every adjustment is disclosed with its risk rationale.
Pass adjusted weights to `score.py --weights weights.json`. When in doubt, keep base
weights: profiles already control critical categories and mandatory controls without
touching weights.

## Applicability quick reference

- No web UI → A11Y-* and SEC-WEB/CORS/CSRF/XSS controls are usually NOT APPLICABLE
  (justify each).
- No model features means MOD-* controls are NOT APPLICABLE.
- No mobile target → MOB-*; no desktop target → DESK-*.
- Single-tenant by design → SEC-TENANT-001 and DATA-TENANT-001 may be NA, but ownership
  isolation between users usually still applies.
- NOT APPLICABLE always requires a recorded justification; the scorer rejects NA without one.
