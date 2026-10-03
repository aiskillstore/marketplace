---
name: pricing-renewal-discipline
description: Renewals + expansion as continuous pricing surgery. Designs the renewal-pricing motion (90-day-prior notice, value-anchored escalation rationale, grandfather policy), the expansion-pricing triggers (usage thresholds, role-change, outcome-attainment), and the contraction-policy guardrails (when a customer wants to downgrade — keep them vs lose them). Loaded by the main pricing skill when the operator asks about renewals, expansion pricing, or "how do I raise prices on existing customers."
user-invocable: false
allowed-tools: Read
  - Write
license: MIT

---

# Pricing Renewal Discipline — sub-skill

Renewals + expansion are where most pricing leaks. New-logo pricing
gets attention; existing-customer pricing drifts.

## Activation

Routed here when operator says:

- "How do I raise prices on existing customers?"
- "Renewal pricing"
- "Expansion pricing"
- "Customer wants to downgrade — should I let them?"
- "How do I get my install base on new pricing?"

## The renewal motion (5 rules)

### Rule 1 — 90-day-prior notice

Every price change at renewal gets communicated to the customer at
least 90 days before the renewal date. In writing. With the reason.

Anything less than 90 days reads as bad faith — buyer feels trapped.
Surprise price increases at renewal are the #1 driver of "customer
hates us" reviews on G2 / Capterra.

### Rule 2 — Anchor the increase on delivered value, not CPI

Banned: "Annual CPI adjustment of 8%."
Good: "Since you signed last year, we shipped {feature 1}, {feature 2},
{feature 3}. The new price reflects expanded value. New list is $X;
your renewal price is $Y."

If you didn't deliver more — don't raise.

### Rule 3 — Grandfather existing customers OR ramp slowly

Two acceptable options when new-logo list goes up:

**Grandfather indefinitely.** Existing customers stay on old pricing.
Best for trust. Worst for unit-economics.

**Ramp slowly.** 5-15% per renewal cycle over 12-24 months with
90-day prior notice each time. Best balance.

**NEVER**: Bulk-raise existing customers to new list. Mass-churn event.

### Rule 4 — Bottom decile gets the smallest increase (or none)

15% on a $99/mo customer is ~$15. 15% on a $999/mo customer is ~$150.
Same percentage, different felt-cost. Bottom decile is the highest
churn-risk; let them expand into a higher tier naturally instead.

### Rule 5 — Top decile gets a custom motion

Don't bulk-process the top 10% (by ACV) through the same renewal
email flow as the median. Custom AE / CS conversation. References.
Budget. Pricing power.

## The expansion motion

Expansion-pricing triggers — when to surface an upgrade conversation:

| Trigger | What it means | Move |
|---|---|---|
| Usage threshold crossed | ≥80% of tier limit | Surface upgrade 30 days before they cap |
| Role-change trigger | New buyer (champion left/arrived) | Reset relationship + pricing conversation |
| Outcome attainment | Customer hit the outcome the product enables | Expand the use case, not just seats |
| Adjacent-team interest | Different team in same org wants in | Treat as new logo for that team |
| Renewal date | The natural pricing-conversation moment | Use it |
| Customer-initiated upsell | They asked for more | Easy win; close fast |

For each trigger:

1. Anchor on value already delivered (specific receipts)
2. Frame expansion as MORE of the same value
3. Inertia frame (what they lose if they don't expand)
4. Specific upgrade path with effective price

## The contraction motion

When a customer wants to downgrade — 5 diagnostic questions:

1. **Is the use case still active?** If they stopped using, downgrade
   is a churn-precursor — fight to save the use case, not the tier.
2. **Did their team shrink?** If headcount dropped, downgrade is
   appropriate; expansion comes back later.
3. **Did the budget shrink (independent of value delivered)?**
   Negotiate non-price commercial concessions first.
4. **Did the value delivered drop?** Fix the value problem — don't
   paper over with a discount.
5. **Are they planning to leave?** Pre-churn signal. Escalate to CS.

Downgrade response options:

| State | Response |
|---|---|
| Use case shrank | Allow downgrade; mark as expansion candidate later |
| Budget shrank | Extended payment terms before discount; preserve list |
| Value problem | Fix the value; don't discount as substitute |
| Pre-churn signal | Engage CS leadership; consider win-back terms |
| Just shopping | Don't reflexively match; defend value frame |

**Never auto-process downgrades.** Self-serve downgrades destroy
the conversation that diagnoses why.

## Workflow

### 1. Load inputs

From `brand-config.json`:

- `pricing.currentTiers`
- `pricing.renewal.cadence`
- `pricing.renewal.priorNoticeDays` (target: ≥90)
- `pricing.expansion.triggers[]`

From CRM:

- Customers <60 days from renewal (URGENT — past notice window)
- Customers 60-180 days from renewal
- Customers crossing expansion thresholds this quarter
- Customers who initiated downgrade requests

### 2. Generate the renewal motion plan

For URGENT customers (past 90-day window):

```
URGENT — past 90-day notice window
  Customer: {name}
  Renewal date: {date}
  Days until renewal: {N}
  Current price: ${Y}
  Action: Extend current price for 1 quarter + send the proper-notice
  email for the NEXT cycle
```

For 60-180 day customers:

```
Customer: {name}
Renewal: {date} ({N} days)
Current price: ${Y}
Recommended new price: ${Z}
Increase rationale (deliver verbatim):
  - {value delivered #1}
  - {value delivered #2}
  - {value delivered #3}
Notice template: {paragraph}
```

### 3. Generate the expansion motion plan

For each customer crossing a trigger:

```
Customer: {name}
Trigger: {description}
Suggested expansion: {upgrade tier / add module}
Effective price impact: ${delta}
Talking points: {3 anchored on value delivered}
```

### 4. Generate the contraction-response playbook

For each downgrade-request customer: run the 5 questions + recommend
a response from the table.

## Self-check

- [ ] Every renewal flagged with days-to-renewal
- [ ] No renewal change without 90-day prior notice
- [ ] Increase rationale anchored on delivered value, not CPI
- [ ] Bottom decile not getting full % increase
- [ ] Top decile getting custom motion (not bulk flow)
- [ ] Expansion triggers tracked + acted on within 30 days
- [ ] Downgrade requests get diagnostic, not auto-process

## Reference

- `../../pricing/references/pricing-framework.md` — operating practice
- `../pricing-quarterly-review/SKILL.md` — where renewal performance gets reviewed
- `../pricing-tribunal/SKILL.md` — for cross-base renewal policy changes
