---
name: pricing-value-metric
description: Pick the right value metric (price unit) for B2B pricing — per-seat, per-API-call, per-active-record, per-outcome, per-revenue-processed, hybrid. Diagnoses the operator's current metric vs the unit that scales with customer success, identifies gaming + misalignment failure modes, and outputs a recommended metric switch with the metric-shift case study reservoir. Loaded by the main pricing skill when the operator asks about per-seat vs per-X, value metric, price unit, or "should I change how I charge?"
user-invocable: false
allowed-tools: Read
  - Write
license: MIT

---

# Pricing Value Metric — sub-skill

The price-unit engine. The right value metric scales naturally with
customer success — your revenue grows with their growth, automatically,
without re-negotiation.

## Activation

Routed here when operator says:

- "Per-seat vs per-X"
- "Should I change my value metric?"
- "Should I switch to outcome pricing?"
- "Customers are gaming our metric"
- "Our top customer pays the same as our median customer"

## The metric catalog

| Metric | Best for | Failure modes |
|---|---|---|
| **Per-seat** | Tools used continuously by named users (project mgmt, design, CRM) | Login sharing if value-per-seat is low; doesn't scale with usage |
| **Per-API-call** | Programmatic infrastructure (data APIs, search APIs, AI APIs) | Noisy call counts; buyer can't predict bill; rate-limiting tension |
| **Per-active-record** | Data platforms (contacts, customers, deals, leads) | "Active" definition disputes; archived records leak revenue |
| **Per-event / per-transaction** | Notification, payment, messaging | Bill volatility; bursty traffic = bursty bills |
| **Per-MAU / per-MTU** | End-user-facing analytics, CDPs | Passive users inflate; bot-user definition disputes |
| **Per-outcome** | Services + outcome-driven SaaS (closed deals, hired candidates) | Attribution disputes; bounded-liability complexity |
| **Per-revenue-processed** | Embedded fintech, marketplaces | Customer-revenue volatility; pricing-to-bill cadence mismatch |
| **Per-environment / per-workspace** | DevOps, infra | Doesn't scale with team; encourages multi-tenant abuse |
| **Hybrid (base + variable)** | Mixed-mode SaaS (CRM with seats + automation runs) | Two metrics to communicate; pricing page complexity |

## The right-metric rubric

A value metric is RIGHT if it satisfies all 4:

1. **Scales naturally with customer success** — their growth in
   what-they-care-about = their bill grows automatically.
2. **Is easy to count + verify** — no audit disputes, no quarterly
   "what counts as X" debates.
3. **Aligns with how the buyer talks internally** — matches their
   P&L line item or their team's reporting language.
4. **Doesn't create a volume-vs-revenue tension** for their team —
   they don't have to fight you to use you more.

If any fail, the metric leaks margin (or churn).

## The metric-shift case study reservoir

Common shifts and their typical outcomes:

| Shift | Typical outcome | Risk |
|---|---|---|
| Per-seat → per-active-record | 30-100% ACV expansion on top decile, lower churn | Mid-tier customers may shrink at first |
| Per-API-call → per-outcome | 50-200% ACV expansion on top decile | Outcome definition + attribution complexity |
| Per-seat → per-event | Better volume scaling, more predictable | Bursty traffic = bursty bills |
| Flat → consumption | Stronger product-market alignment | Loss of revenue predictability |
| Consumption → flat | Predictable revenue | Caps top-customer expansion |
| Single-metric → hybrid | Captures both seat + usage | Doubles communication complexity |

When recommending a shift, always cite which of the 4 right-metric
criteria is currently failing and which the new metric satisfies.

## Workflow

### 1. Load inputs

From `brand-config.json`:

- `pricing.valueMetric.unit` — current metric
- `pricing.currentTiers` — current tier structure
- `customer.psps[]`

Also gather (ask if not in config):

- Top-10% customer billing vs median (do they pay 5x? 15x? 50x?)
- Documented gaming behaviors (shared logins, single API key for the org, etc.)
- Quarterly revenue volatility (predictable / cyclical / spiky)

### 2. Diagnose current metric

Run the 4-criterion check:

```
Criterion 1 — Scales with success?
  Current: {pass / fail with example}
Criterion 2 — Easy to count + verify?
  Current: {pass / fail}
Criterion 3 — Matches buyer's internal language?
  Current: {pass / fail}
Criterion 4 — No volume-vs-revenue tension?
  Current: {pass / fail}

Failures: {N of 4}
```

### 3. If all 4 pass — recommend HOLD

The metric is right. Don't tune the metric; tune tier prices or
packaging instead. Route to `pricing-contrast-set` or
`pricing-pocket-waterfall`.

### 4. If 1+ fail — diagnose shift candidates

For each failed criterion, identify a candidate metric that addresses it:

- Failed criterion 1 + value scales with usage → consumption metric
- Failed criterion 1 + value scales with outcomes → outcome metric
- Failed criterion 2 + gaming present → metric with cleaner counter
- Failed criterion 3 + buyer talks in dollars-processed → revenue-processed
- Failed criterion 4 + buyer fights to use less → fixed-base + variable cap

### 5. Output the recommendation

```
Value-Metric Diagnosis — {company}
─────────────────────────────────────────────────────────────────

CURRENT METRIC: {unit + price}
4-CRITERION CHECK:
  1. Scales with success: {pass/fail + reason}
  2. Easy to count: {pass/fail}
  3. Matches buyer language: {pass/fail}
  4. No volume-vs-revenue tension: {pass/fail}

TOP CUSTOMER vs MEDIAN: {Nx}
GAMING OBSERVED: {description or "none documented"}

RECOMMENDATION: {HOLD / SHIFT to {new metric}}

IF SHIFT:
  New metric: {unit}
  Reason: {which criteria it satisfies that current fails}
  Predicted top-decile ACV impact: {range from case-study reservoir}
  Risk: {what could go wrong}
  Migration path: {grandfather existing / new logos only / pilot}
  Test design: route to pricing-tribunal (value-metric shifts are
  Strategic-tier under the risk taxonomy — never ship blind)
```

## Self-check

- [ ] 4-criterion check completed for current metric
- [ ] Top-decile vs median ratio captured (or flagged as data gap)
- [ ] Gaming behaviors named specifically (not "we think they game it")
- [ ] Recommendation is HOLD or SHIFT — not "try a few"
- [ ] If SHIFT: case-study reservoir cited for predicted impact range
- [ ] If SHIFT: routed to pricing-tribunal for test design

## Reference

- `../../pricing/references/value-metric-catalog.md` — full metric catalog
- `../../pricing/references/pricing-framework.md` — value-metric in context
- `../pricing-tribunal/SKILL.md` — value-metric shifts are Strategic-tier; must tribunal
