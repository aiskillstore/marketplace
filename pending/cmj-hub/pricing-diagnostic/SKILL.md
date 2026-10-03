---
name: pricing-diagnostic
description: The three-surface pricing diagnostic — willingness-to-pay distribution, value-metric alignment, and packaging-vs-pricing diagnosis. Loaded by the main pricing skill when the operator asks "should I raise prices", "where am I leaving money on the table", or "diagnose my pricing." Outputs a diagnostic report with surface-level scores (0-100 per surface), top 3 leaks, and a triage decision (price-tune / package-rebuild / metric-shift / hold).
user-invocable: false
allowed-tools: Read Write
  - Grep
license: MIT

---

# Pricing Diagnostic — sub-skill

The core diagnostic engine. Before any pricing change, this
sub-skill runs three surfaces in order and outputs a triage
decision.

## Activation

The main `pricing` skill routes here when the operator says:

- "Should I raise my prices?"
- "Where am I leaving money on the table?"
- "Diagnose my pricing"
- "Audit my pricing"
- "Run a pricing review"

## Workflow

### 1. Load inputs

Required (from `brand-config.json`):

- `pricing.currentTiers` — present prices + cadence
- `pricing.valueMetric` — current unit
- `customer.psps` — Pain Signal Profile(s)
- `pricing.discountPolicy` — documented thresholds or "discretion"

Optional but improves diagnosis:

- `pricing.wtpResearch` — WTP discovery data if available
- `pricing.pocketWaterfall` — discount waterfall if built
- `pricing.referenceAnchor` — current reference frame

If `pricing.*` is empty, route to `pricing-onboarding` first.

### 2. Surface 1 — Willingness-to-pay (WTP) distribution

Diagnostic questions per PSP:

1. **Do you have structured WTP data?** (Van Westendorp / Gabor-Granger /
   conjoint within last 18 months — Yes/No)
2. **If yes, what's the P10/P50/P90 of WTP per PSP?**
3. **If no, what's the close-rate at current price per PSP?**
4. **Are you discounting >15% on any PSP segment to close?**
   (Indicates current price is above WTP P50 for that segment)
5. **Are you walking away from buyers who say "too expensive" without
   counter-offer?** (Indicates current price is at or above WTP P90)

Score this surface 0-100:

| Score | State |
|---|---|
| 0-30 | No WTP data, high discount rate, no PSP differentiation. Highest-leverage area. |
| 31-60 | Some WTP signal, some discounting, partial PSP differentiation. Real leverage. |
| 61-85 | WTP data <18 months old per PSP, discounting within policy, PSP-aware pricing. Some room. |
| 86-100 | Recent structured WTP per PSP, quarterly refresh, tested by segment. Low-leverage. |

Output: WTP score + top 2 specific gaps + recommended action.

### 3. Surface 2 — Value-metric alignment

Diagnostic questions:

1. **What scales with your customer's success?** (Volume of what they do = volume of value created)
2. **Does your current value metric (per-seat / per-call / etc.) scale with that?** Y/N
3. **Are customers gaming the metric?** (Sharing logins to avoid per-seat; routing through a single API key to avoid per-call; etc.)
4. **What's your top-decile customer paying — and does it reflect their value created?**
5. **Are you charging customers who used to be small but are now huge at their old rate?**

Score this surface 0-100:

| Score | State |
|---|---|
| 0-30 | Metric doesn't track customer growth. Gaming is happening. Top customers pay <2x median despite using >10x. |
| 31-60 | Metric tracks growth weakly. Some gaming. Top customers pay 3-5x median. |
| 61-85 | Metric tracks growth well. No documented gaming. Top customers pay 5-15x median. |
| 86-100 | Metric naturally scales with success. Customer expansion is automatic. Top customers pay >15x median. |

Output: Value-metric score + the alignment failure mode (if any) + recommended action.

### 4. Surface 3 — Packaging-vs-pricing diagnosis

Diagnostic questions:

1. **Can the buyer grok your tier differentiation in <30 seconds?** (Test this — show the pricing page to someone who's never seen it.)
2. **Is your bottom tier so feature-poor it loses sales** (vs being a real decoy that helps the target conversation)?
3. **Is your top tier so feature-rich it caps natural expansion?**
4. **Are the WRONG features bundled together?** (e.g., advanced reporting in the highest tier when most teams need it earlier)
5. **What % of buyers land on each tier?** (Healthy: ~5-10% decoy / 70-80% target / 10-25% anchor)

Score this surface 0-100:

| Score | State |
|---|---|
| 0-30 | Pricing page is confusing. Bottom tier is broken. Tier landing % is skewed (e.g., 60% on decoy). |
| 31-60 | Page is OK, tier feature-set has obvious issues, landing distribution is off. |
| 61-85 | Clear page, reasonable tier diff, landing distribution close to healthy. |
| 86-100 | Tested page, clean differentiation, landing distribution within target. |

Output: Packaging score + the packaging issue (if any) + recommended action.

### 5. Triage decision

Cross-reference the three scores:

| WTP | Value-metric | Packaging | Triage decision |
|---|---|---|---|
| Low | Low | Low | **Diagnostic discipline** — pause new pricing work; do WTP discovery first. (~6 weeks) |
| Low | High | High | **WTP discovery** — your prices may be too low; investigate before raising. (~4 weeks) |
| High | Low | High | **Metric shift** — wrong unit is the issue; piloted with new logos first. (~8 weeks) |
| High | High | Low | **Packaging rebuild** — pricing page rebuild, NOT a price change. (~3 weeks) |
| Mixed | Mixed | Mixed | **Audit + tribunal** — escalate to `pricing-audit` then `pricing-tribunal` |
| All High | | | **Hold + quarterly review** — pricing is healthy; schedule the next review |

### 6. Output format

```
Pricing Diagnostic — {company}
─────────────────────────────────────────────────────────────────

Surface 1 — Willingness-to-pay distribution: {score}/100
  Top gaps:
    - {gap 1}
    - {gap 2}
  Recommended: {action}

Surface 2 — Value-metric alignment: {score}/100
  Failure mode: {none / per-seat misalignment / metric gaming / etc.}
  Top customer paying: ${X}/mo vs median ${Y}/mo ({Z}x multiple)
  Recommended: {action}

Surface 3 — Packaging-vs-pricing: {score}/100
  Tier landing %: {bottom}% / {middle}% / {top}%
  Packaging issue: {none / feature misbundle / decoy broken / etc.}
  Recommended: {action}

─────────────────────────────────────────────────────────────────
TRIAGE: {triage decision}
NEXT SUB-SKILL: {sub-skill route}
TIMELINE: {duration}
─────────────────────────────────────────────────────────────────
```

## Self-check

Before delivering the report:

- [ ] All 3 surfaces scored with rationale
- [ ] Top 2-3 gaps named per surface (not just scores)
- [ ] Triage decision matches the surface-score matrix
- [ ] Next sub-skill named explicitly
- [ ] Timeline given (no "consult a pricing expert" hand-waving)
- [ ] No fabrication of WTP numbers or close-rate data the operator didn't provide

## References

- `../../pricing/references/pricing-framework.md` — the three surfaces deep
- `../../pricing/references/value-metric-catalog.md` — value-metric patterns
- `../../pricing/references/decoy-effect-patterns.md` — packaging diagnostics
- `../pricing-audit/SKILL.md` — the 30-point audit (next step for high-stakes diagnoses)
- `../pricing-tribunal/SKILL.md` — for material change decisions
