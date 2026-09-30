# Capacity and ramp math

The bottom-up half of the derivation: how much the team can actually produce, and how new-hire ramp modifies both the team number and the individual quota.

## Ramped Rep Equivalents (RRE)

Nominal headcount overstates capacity whenever part of the team is ramping. Count each rep as their ramp-schedule fraction, not as 1:

```
RRE = Σ over reps of (ramp factor at that rep's tenure-month)
```

On a 0/25/50/75/100% quarterly ramp:

| Tenure       | Ramp factor |
| ------------ | ----------- |
| Month 1      | 0.0         |
| Month 3      | 0.5         |
| Fully ramped | 1.0         |

**Worked example (Dave Kellogg / Kellblog):** 25 nominal reps summed to 17.5 RREs - a 70% effective-to-nominal ratio. A team hiring continuously "loses" roughly 30% of nominal capacity to ramp at any moment. This is why a capacity model on headcount alone systematically overstates the plan.

## Bottom-up capacity formula

```
Sales capacity = RREs × individual quota × average quota attainment
```

(Tomasz Tunguz's formula, with RREs replacing the naive rep count.) Cross-check against the market view: `addressable accounts per territory × historical win rate × average deal size × rep count`. Use your org's own attainment history for the attainment term - not an aspirational 100%.

**Worked example on published B2B SaaS medians** (Bridge Group 2024: median AE quota $800K): a 20-rep team at 16 RREs, $800K quota per ramped rep, 50% historical attainment models to `16 × $800K × 0.5 = $6.4M` - against the `20 × $800K = $16M` a naive plan would book. The gap between those two numbers is the reconciliation conversation.

## Over-assignment: the contested range

Aggregate rep quotas are set above the company commitment so normal miss-rates still land the company number. Published recommendations disagree - treat the range as the finding, never a single figure:

| Source                                                      | Recommendation                                                                  |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------- |
| Dave Kellogg / Kellblog (citing a Zuora CFO Summit dataset) | ~20% typical for enterprise software; observed distribution 0% to 100%+         |
| Drivetrain                                                  | No more than 25%, sized so a team at 80% attainment still makes plan            |
| Withbridges (fractional CFO practice)                       | 15-25% "street quota" above the company target                                  |
| Lative                                                      | 10-20% - flagged by Lative itself as a common but criticized shortcut           |
| RevCast                                                     | An "Attainment Factor" of 75-85% (lower factor = more cushion = more comp cost) |

Working range: **10-25%**. Pick the point from your own attainment history and comp-cost tolerance: more cushion raises the odds of landing the company number and raises comp cost per landed dollar. Over-assignment stacked on top of a nominal-headcount capacity model compounds two overstatements - run RREs first.

## Ramp relief

```
Relieved Quota (period) = Full Quota × Ramp % for that period
Attainment during ramp = Achieved ÷ Relieved Quota
```

There is no universal schedule - sales-cycle length is the primary driver. Documented shapes:

- Canonical quarterly ramp: 0% / 25% / 50% / 75% / 100% across the first four quarters.
- High-velocity (~30-day cycle): 0% / 25% / 50% / 100% by month.
- Mid-market B2B SaaS, 6-month ramp: 30% / 60% / 90% / 100% in quarterly steps.
- Simple variant: first-quarter quota cut ~40%, with a mid-quarter pipeline review.

Ramp-duration benchmarks to sanity-check a proposed schedule:

- SMB: under ~4 months.
- ~$50K+ ACV: around 9 months.
- Enterprise / $200K+ ACV: 9-15 months.

Bridge Group's 2026 AE research (n=158 B2B companies) measured average ramp at 6.2 months - the highest in that series' history - with the average experience bar at hire also rising. Longer cycles and larger deals justify longer, more gradual ramps.

Write the curve and relief rules as explicit policy, applied uniformly - not per-manager discretion. Forecasting, onboarding, and comp payout must all reference the same relieved numbers.

## Draws (boundary note)

Income support during ramp - a recoverable draw (advance repaid from future commission) or a non-recoverable guarantee - is a comp-plan design choice layered beside quota relief, not part of the quota itself. It is the dominant ramp-support mechanism in commission-heavy B2C verticals (solar, auto, insurance), where draw-balance disputes at separation are a known failure. Hand draw design to mbfinotti/sales-skills@sales-comp-design.
