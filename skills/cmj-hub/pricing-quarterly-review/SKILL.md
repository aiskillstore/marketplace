---
name: pricing-quarterly-review
description: The quarterly pricing review cadence — the operating practice that prevents pricing drift. Produces a quarterly review agenda, the data pull list (close-rate, discount-rate, pocket-price waterfall, tier-landing distribution, WTP refresh status), and the verdict format (hold / iterate / escalate to tribunal). Loaded by the main pricing skill when the operator asks about quarterly review, ops cadence, or "what should I check on pricing this quarter."
user-invocable: false
allowed-tools: Read
  - Write
license: MIT

---

# Pricing Quarterly Review — sub-skill

The operating practice. Pricing that doesn't get reviewed gets
eroded. The quarterly review IS the compounding moat.

## Activation

Routed here when operator says:

- "Quarterly pricing review"
- "What should we check this quarter on pricing"
- "Pricing ops cadence"
- "Schedule the pricing review"
- "First quarterly review on pricing"

## The cadence

Quarterly, NOT annually. Annual pricing review = annual pricing drift.

| Quarter | Focus |
|---|---|
| Q1 | Annual price + tier review; budget-cycle alignment |
| Q2 | Discount discipline + pocket-price waterfall refresh |
| Q3 | Tier landing distribution + decoy / anchor health |
| Q4 | WTP refresh for one PSP per year (rotating); annual renewal price-increase preview |

This is a *rolling* cadence — each quarter has a focus, but the
core data pull happens every time.

## The core data pull (every quarter)

| Metric | Source | What to check |
|---|---|---|
| New-logo ACV | CRM | Trend vs last 4 quarters; PSP-segmented |
| Close-rate by tier | CRM | Healthy: target tier ~75%, decoy ~5-10%, anchor 10-25% |
| Mean discount % | CRM | Trend vs last 4 quarters; PSP-segmented |
| Discount-policy compliance | CRM | % of deals discounted within policy vs outside |
| Walk-away rate | CRM | Lost-to-price as % of opportunities — and the verbatim quotes |
| Pocket-price waterfall | Billing system + CRM | Recompute via `pricing-pocket-waterfall` skill |
| Tier landing distribution | Billing system | Compare to target distribution |
| Renewal churn | Billing system | Especially mid-renewal price changes; expansion vs contraction |
| Top-decile vs median ACV ratio | Billing system | Healthy: 5-15x for healthy value-metric; <3x = misaligned metric |
| Competitor prices | Manual or scraping | Snapshot for the file (not for decision-making — see banned patterns) |

## The review agenda (90 minutes)

### Minutes 0-15 — Data check-in

Walk through the 10 metrics above. State of each: trend up / down / flat. Surface anomalies.

### Minutes 15-30 — Discount-discipline review (Q2 deep-dive)

Per the pocket-price waterfall — which leak step is largest this
quarter? Is the discount policy working? Any individual reps drifting?

### Minutes 30-45 — Tier landing + decoy health (Q3 deep-dive)

Is the target tier still ~75% of new logos? Is the decoy still doing
its job (T2 obviously better)? Is the anchor tier still credible
(≥3x target, real buyers)?

### Minutes 45-60 — WTP signal review (Q4 deep-dive)

What did this quarter's walk-aways say verbatim? Any PSP-specific
patterns? Is it time for a structured WTP refresh?

### Minutes 60-75 — Decisions

Three verdict categories:

1. **HOLD** — Pricing is healthy. Schedule next quarterly. No action this quarter.
2. **ITERATE** — Surface a specific tuning (a specific discount policy
   change, tier-card copy refresh, feature shift). Routine-tier; no
   tribunal required.
3. **ESCALATE TO TRIBUNAL** — Material or Strategic change needed.
   Route to `pricing-tribunal` for hypothesis + test design.

### Minutes 75-90 — Calendar + ownership

- Calendar next quarterly review (90 days out)
- Calendar 30-day check-ins on any ITERATE actions
- Calendar tribunal kick-off if applicable
- Document the verdict + reasoning in `pricing.review.log[]`

## Attendees (REQUIRED)

| Role | Why |
|---|---|
| Pricing owner (often CEO, COO, VP Product) | Final accountability for pricing |
| Sales leader | Discount discipline + buyer feedback |
| Finance / RevOps | Pocket-price + waterfall numbers |
| Product leader | Packaging + tier feature decisions |

Don't run a pricing review without all four. Single-perspective
reviews produce single-perspective decisions.

## The review log

Every quarter's review goes in `brand-config.json` under
`pricing.review.log[]`:

```json
{
  "date": "2026-04-15",
  "quarter": "Q2 2026",
  "focus": "Discount discipline + pocket-price waterfall refresh",
  "metrics_snapshot": { ... },
  "verdict": "ITERATE",
  "actions": [
    "Tighten ramp discount policy: rep authority 0-15% (was 0-20%)",
    "Add reason-code requirement to all >10% discounts"
  ],
  "next_review": "2026-07-15",
  "attendees": ["..."]
}
```

The log is the compounding moat. The first review is harder than
the fifth. The fifth is harder than the twentieth.

## Workflow

### 1. Pre-review data pull

Run `pricing-pocket-waterfall` + grab CRM exports for the 10 metrics.

### 2. Generate the agenda

Output the 6-section agenda with the operator's actual metrics
populated. Highlight anomalies (any metric ≥1 SD from the trailing
4-quarter mean).

### 3. After the meeting

Capture the verdict + actions + next-review-date. Update
`brand-config.json` review log.

### 4. Schedule

- Calendar next quarterly
- Calendar any 30-day check-ins on ITERATE actions
- Calendar tribunal kick-off if ESCALATE

## Self-check

- [ ] Agenda covers all 6 sections
- [ ] Data pull is complete or data gaps flagged
- [ ] Attendees include all 4 roles
- [ ] Verdict is HOLD / ITERATE / ESCALATE (no "let's revisit next quarter" vagueness)
- [ ] Actions are specific (not "improve pricing")
- [ ] Next review calendared

## Reference

- `../../pricing/references/pricing-framework.md` — operating-practice section
- `../pricing-pocket-waterfall/SKILL.md` — the waterfall refresh
- `../pricing-tribunal/SKILL.md` — for ESCALATE decisions
- `../pricing-renewal-discipline/SKILL.md` — for renewal price changes
