---
name: pricing-audit
description: 30-point audit of a B2B pricing program across four dimensions — diagnostic data (8 points), reference frames + copy (8 points), tier architecture (8 points), and operating practice (6 points). Produces a 0-100 score, the top 3 levers, and a 90-day remediation order. Loaded by the main pricing skill when the operator asks to audit or grade their pricing. Based on the JMC 30-Point Pricing Audit framework.
user-invocable: false
allowed-tools: Read Write
  - Grep
license: MIT

---

# Pricing Audit — sub-skill

The deeper audit. Where `pricing-diagnostic` runs 3 surfaces fast,
`pricing-audit` runs 30 checks across 4 dimensions and produces a
prioritized 90-day remediation plan.

## Activation

The main `pricing` skill routes here when the operator says:

- "Audit my pricing program"
- "Grade my pricing 0-100"
- "What's my biggest pricing lever?"
- "Full pricing review"
- "What would Hermann Simon say about my pricing?"

## The 30 checks

### Dimension 1 — Diagnostic Data (8 checks)

| # | Check | Pass criteria |
|---|---|---|
| 1 | WTP discovery recency | Structured WTP method within last 18 months per PSP |
| 2 | WTP method rigor | At least Van Westendorp (n≥20) or Gabor-Granger (n≥30) |
| 3 | PSP segmentation | Distinct WTP distribution per PSP, not single-curve |
| 4 | Close-rate by tier | Close-rate tracked per tier per PSP per quarter |
| 5 | Discount-rate by PSP | Mean + max discount tracked by PSP, monthly |
| 6 | Walk-away tracking | Lost-to-price reasons captured in CRM, weekly |
| 7 | Competitor price tracking | Monthly snapshot of 3-5 direct competitors |
| 8 | Pocket-price calculation | Pocket-price waterfall built + updated quarterly |

### Dimension 2 — Reference Frames + Copy (8 checks)

| # | Check | Pass criteria |
|---|---|---|
| 9 | Reference frame named | Pricing page anchors on inertia, opportunity cost, or replacement cost (NOT competitor) |
| 10 | Inertia value quantified | Specific number on the page (e.g., "you're solving this today with $X/yr of internal time") |
| 11 | Outcome guarantee present | Outcome-tied guarantee with bounded liability + qualification gates |
| 12 | Loss-aversion copy | De-risking language above the gain-of-switching language |
| 13 | No banned anchors | No cost-plus reasoning, no "we're cheaper than X" |
| 14 | One specific outcome per tier | Each tier has 1-2 outcomes the buyer can self-rate against |
| 15 | Tested copy | Pricing copy has been tested in the last 12 months (A/B or qualitative) |
| 16 | Stakeholder-aware copy | Copy speaks to both the user (technical buyer) and the budget holder |

### Dimension 3 — Tier Architecture (8 checks)

| # | Check | Pass criteria |
|---|---|---|
| 17 | Three tiers, no more | Three tiers visible on page (Enterprise gate above ~$30K ACV OK) |
| 18 | Decoy designed correctly | Bottom tier is asymmetrically dominated (same metric, strictly less) |
| 19 | Anchor tier exists | Top tier sets the reference frame; ≥3x the target tier price |
| 20 | Value metric is consistent | Same value metric across all tiers (per-seat or per-call, not mixed) |
| 21 | Feature differentiation is clean | Buyer can grok the differences in <30 seconds (test this on a fresh viewer) |
| 22 | Tier landing distribution healthy | ~5-10% decoy / 70-80% target / 10-25% anchor (per last 90 days) |
| 23 | No "Contact Us" below $30K ACV | Numbers visible for everything under mid-market threshold |
| 24 | Annual vs monthly delta is meaningful | Annual prepay = ≥25% discount tied to commercial value, OR removed |

### Dimension 4 — Operating Practice (6 checks)

| # | Check | Pass criteria |
|---|---|---|
| 25 | Discount policy documented | Tiered approval thresholds (e.g., 0-10% rep, 10-20% manager, 20%+ VP) |
| 26 | Pocket-price waterfall reviewed | Pocket-price waterfall updated + reviewed quarterly |
| 27 | Renewal price increase cadence | Documented annual cadence + 90-day-prior renewal notice |
| 28 | Expansion playbook | Documented expansion-pricing triggers + motion |
| 29 | Quarterly pricing review | Calendar-blocked review with product + sales + finance reps |
| 30 | Failed-test registry | Documented log of pricing tests run + outcomes (especially the failures) |

## Workflow

### 1. Load inputs

From `brand-config.json`:

- `pricing.*` section (all subfields)
- `customer.psps[]`

From the operator's pricing page URL (if provided):

- Use `WebFetch` to grab the live page
- Parse tier structure, copy, value metric

### 2. Run each of 30 checks

For each check, output one of:

- ✅ PASS
- ⚠️ PARTIAL (with what's missing)
- ❌ FAIL (with the specific gap)
- 🔘 NOT APPLICABLE (with the reason)

### 3. Calculate score

Score per dimension:

- Dim 1: PASS count × 12.5 (max 100)
- Dim 2: PASS count × 12.5 (max 100)
- Dim 3: PASS count × 12.5 (max 100)
- Dim 4: PASS count × 16.7 (max 100)

Overall = weighted mean: Dim 1 × 0.25 + Dim 2 × 0.25 + Dim 3 × 0.25 + Dim 4 × 0.25.

### 4. Identify the top 3 levers

Rank failed/partial checks by:

1. **Magnitude** — what's the expected revenue/margin impact?
2. **Reversibility** — how easy to undo if it doesn't work?
3. **Diagnostic depth** — do we know enough to act, or do we need more data first?

Top 3 = highest magnitude × reversibility × diagnostic-depth.

### 5. 90-day remediation order

For each of the top 3 levers, output:

```
Lever 1: {description}
  Why: {magnitude + impact framing}
  Action: {specific sub-skill route — e.g., "Run pricing-pocket-waterfall"}
  Owner: {who}
  Timeline: {week 1-3 / week 4-6 / week 7-12}
  Success metric: {how we'll know it worked}
```

### 6. Output format

```
Pricing Audit — {company}
─────────────────────────────────────────────────────────────────

OVERALL: {score}/100

Dimension 1 — Diagnostic Data: {score}/100
  ✅ {n} pass / ⚠️ {n} partial / ❌ {n} fail
Dimension 2 — Reference Frames + Copy: {score}/100
  ✅ {n} pass / ⚠️ {n} partial / ❌ {n} fail
Dimension 3 — Tier Architecture: {score}/100
  ✅ {n} pass / ⚠️ {n} partial / ❌ {n} fail
Dimension 4 — Operating Practice: {score}/100
  ✅ {n} pass / ⚠️ {n} partial / ❌ {n} fail

─────────────────────────────────────────────────────────────────
TOP 3 LEVERS (90-day remediation):

1. {lever 1}
2. {lever 2}
3. {lever 3}

DETAILED CHECK RESULTS:
[full 30-row table]
```

## Self-check

- [ ] All 30 checks evaluated with rationale (not just scores)
- [ ] Score per dimension + overall calculated
- [ ] Top 3 levers identified with magnitude + reversibility + diagnostic-depth reasoning
- [ ] 90-day order respects sequencing (e.g., WTP discovery before tier rebuild)
- [ ] No fabrication — uncertain checks flagged, not guessed

## References

- `../../pricing/references/pricing-framework.md` — framework underlying each check
- `../pricing-diagnostic/SKILL.md` — the lighter 3-surface diagnostic
- `../pricing-tribunal/SKILL.md` — for material decisions surfaced by the audit
