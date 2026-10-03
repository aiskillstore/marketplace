---
name: pricing-contrast-set
description: Design the three-tier contrast-set architecture — decoy / target / anchor. Applies asymmetric dominance (Ariely) so the decoy makes the target obviously better, the anchor sets the high reference frame, and ~75% of buyers land on the target tier. Loaded by the main pricing skill when the operator asks to design tiers, redesign the pricing page, or apply the decoy effect. Outputs tier definitions, feature differentiation, value-metric scaling per tier, and the predicted landing distribution.
user-invocable: false
allowed-tools: Read
  - Write
license: MIT

---

# Pricing Contrast-Set — sub-skill

The three-tier architecture engine. The structure that outperforms
two-tier and four-tier in 80%+ of B2B SaaS / services tests.

## Activation

Routed here when operator says:

- "Design my pricing tiers"
- "Redesign my pricing page"
- "Apply the decoy effect"
- "Should I add a tier / remove a tier?"
- "Three-tier pricing"

## The architecture

```
Tier 1 (Decoy)         Tier 2 (Target)       Tier 3 (Anchor)
═══════════════        ═══════════════       ═══════════════
Job: Make T2 look      Job: Where 70-85%     Job: Set the high
obviously better.      of buyers should      reference frame.
                       land.

Same value metric      Same value metric     Same value metric
as T2, strictly less.  but at the dominant   at a strict premium.
                       feature set.

Pricing: 25-35% of     Pricing: target ACV   Pricing: ≥3x T2,
T2 price.                                    sometimes 5-10x.
```

## Design rules

### 1. Same value metric across all tiers

If T2 is per-seat, T1 and T3 must be per-seat. Don't mix
per-seat with per-API-call across tiers — the buyer can't grok the
comparison in <30 seconds.

### 2. Decoy is asymmetrically dominated

T1 has strictly less of the same value-metric quantity (fewer seats /
fewer calls / fewer records). And/or strictly fewer features from
the same feature set. The buyer should recognize T1 < T2 instantly.

Bad decoy example: T1 has 5 seats + integration A; T2 has 10 seats
+ integration B. (Different integration breaks the symmetry.)

Good decoy example: T1 has 5 seats + integrations A; T2 has 25 seats
+ integrations A + B. (T2 has everything T1 has, plus more.)

### 3. Anchor tier sets the high frame

T3 is priced ≥3x T2. It sets the reference frame so T2 reads as
"reasonable" not "expensive." T3 should be a real product (one the
top 10% of customers actually buy), not a fictional max tier.

If you can't articulate a real T3 buyer, you don't have a true
anchor — you have an inflated decoy on the upper end.

### 4. Feature differentiation is grokable in <30 seconds

Test it. Show the page to someone who's never seen it. Ask: "Which
tier would you pick if you ran a 50-person team?" If they need
>30 seconds, the differentiation is muddy.

Clean differentiation:

- Quantity (seats, calls, records, GB)
- One or two binary features per tier (e.g., "SSO," "Audit log")
- One or two service levels (e.g., "Standard support," "Priority,"
  "Named CSM")

Avoid:

- Long feature checklists (>6 lines per tier)
- "Up to" qualifiers everywhere (creates fuzz)
- Mid-tier features that exist nowhere else (creates parsing tax)

### 5. Value-metric scales continuously but with decreasing per-unit price

| Tier | Volume | Per-unit cost | Total |
|---|---|---|---|
| T1 (Decoy) | 5 seats | $20/seat | $100 |
| T2 (Target) | 25 seats | $12/seat | $300 |
| T3 (Anchor) | 100 seats | $8/seat | $800 |

Decreasing per-unit price across tiers reads as "even better deal
IF you need more" — natural quantity discount, no artificial cliff.

### 6. No "Enterprise — call us" below $30K ACV

Below that threshold, "contact us" adds friction without lift.
Below mid-market, buyers need a number to feel safe. Above ~$30K
ACV, a real enterprise tier (with custom procurement) is fine.

### 7. Annual prepay is meaningful or absent

Annual prepay should:

- Be ≥25% off monthly equivalent (so the buyer's CFO sees the math), AND
- Be tied to commercial value (churn-lock, cash flow, multi-year SLA)

Otherwise: don't offer it. ~16% off reads as "we want your cash"
without giving a real concession.

## Workflow

### 1. Load inputs

From `brand-config.json`:

- `pricing.currentTiers` — present state
- `pricing.valueMetric.unit` — the metric across tiers
- `customer.psps[]` — who's buying which tier today
- Last 90 days of tier landing distribution (if tracked)

### 2. Diagnose current tier health

Run the tier landing check:

| Current distribution | State |
|---|---|
| ~5-10% T1 / 70-80% T2 / 10-25% T3 | Healthy three-tier |
| ≥20% T1 | Decoy is working as a real product → not a decoy → broken |
| <50% T2 | Differentiation muddy, or T2 is over/underpriced |
| <5% T3 | Anchor not credible; can probably price T3 higher |
| Two tiers only | Add a decoy or anchor based on diagnostic surface |
| Four+ tiers | Eliminate the redundant tier; pick the weakest |

### 3. Design the new tier set

For each tier, output:

```
Tier {name}: ${price}/{cadence}
  Value-metric: {unit + volume}
  Features: 
    - {feature 1}
    - {feature 2}
    - {feature 3 — max 6 features}
  Target buyer: {PSP description}
  Buyer count (predicted % landing): {N}%
```

### 4. Self-check before output

- [ ] Three tiers, no more (unless real Enterprise tier above $30K ACV)
- [ ] Same value metric across tiers
- [ ] Decoy is asymmetrically dominated
- [ ] Anchor is ≥3x target and has a real buyer
- [ ] Predicted landing distribution is ~75% on target
- [ ] Per-unit cost decreases across tiers
- [ ] Feature differentiation is <30 seconds to grok (validate this)
- [ ] No "contact us" below $30K ACV
- [ ] Annual prepay either ≥25% or absent

### 5. Generate the pricing-page tier cards

Output ready-to-ship copy:

```
[Tier 1 card]
[Tier 2 card — visually emphasized with "Most Popular" or similar]
[Tier 3 card]
```

With the anchor block from `pricing-reference-frames` above the cards.

### 6. Schedule the A/B test

Don't ship a new tier set blind. Route to `pricing-tribunal` for the
hypothesis + test design. Tier rebuilds are Material-tier changes
under the tribunal taxonomy.

## Output format

```
Three-Tier Contrast Set — {company}
─────────────────────────────────────────────────────────────────

Tier 1 — Decoy: ${price}
  {value-metric quantity}
  Features: {short list}
  Designed to make T2 obvious. Predicted landing: ~5-10%.

Tier 2 — Target: ${price}    ★ Most Popular
  {value-metric quantity}
  Features: {short list}
  Where 70-85% of buyers should land.

Tier 3 — Anchor: ${price}
  {value-metric quantity}
  Features: {full list}
  Sets the high reference frame. Predicted landing: 10-25%.

PREDICTED TIER LANDING: {distribution}
ANCHOR (above tier cards): {use output from pricing-reference-frames}
A/B TEST RECOMMENDED: yes (route to pricing-tribunal)
```

## References

- `../../pricing/references/pricing-framework.md` — full contrast-set framework
- `../../pricing/references/decoy-effect-patterns.md` — asymmetric dominance patterns
- `../pricing-reference-frames/SKILL.md` — anchor copy ABOVE the cards
- `../pricing-tribunal/SKILL.md` — for ship-it test design
