# Fair-share allocation

Territories are rarely equal in opportunity, so a flat per-rep quota on patch-based territories is structurally unfair. Fair-share allocation is the dominant documented correction.

## The formula

```
Rep Quota = Company Target × (Rep's Territory Potential ÷ Total Market Potential)
```

Territory potential is a scored estimate combining:

- Addressable market inside the territory.
- Account density.
- Existing penetration and whitespace.
- Competitive intensity.
- Travel burden.

The account-level criteria behind such a score belong to mbfinotti/sales-skills@sales-account-segmentation and mbfinotti/sales-skills@sales-account-tiering - this file covers only the quota-indexing step.

## Worked example - $20M target, 5 reps

| Rep | Territory potential | Share | Fair-share quota |
| --- | ------------------- | ----- | ---------------- |
| A   | $15M                | 30%   | $6.0M            |
| B   | $12M                | 24%   | $4.8M            |
| C   | $10M                | 20%   | $4.0M            |
| D   | $8M                 | 16%   | $3.2M            |
| E   | $5M                 | 10%   | $2.0M            |

**Negative example - the same book split flat:** $4M each. Rep E must now capture 80% of a $5M territory while rep A needs 27% of a $15M one. E's number is structurally unattainable and A's is a layup - the flat quota measured territory luck, not execution, before anyone made a call.

## Modified fair share

Alexander Group's trademarked **Modified Fair Share** applies the same proportional math starting from each territory's _historical results_ instead of a scored potential. It is the efficiency default in the SKILL.md menu because the input already exists in the CRM - no scoring model to build.

It inherits history's blind spots: a territory that underperformed because of a weak prior rep scores as low-potential, and a redrawn territory has no history at all. When history is unrepresentative, move up to potential-based fair share.

## Territory index variant

Some orgs convert scores into an index (baseline 100; a 120 territory carries 1.2× the base quota) and multiply. The proportional-share math is the well-documented core; the index-multiplier mechanics are a firm-by-firm convention, not a published standard - treat any specific index formula as house style.

## Governance for mid-cycle changes

Cichelli's guidance (_Compensating the Sales Force_, the Alexander Group reference text): keep mid-year account and territory changes to a minimum, and route named-account carve-outs and any mid-year reassignment through a formal process, never ad hoc manager adjustment. Every unmanaged move silently rewrites someone's quota.

## The trade-off to disclose

Territory weighting makes performance harder to read: attainment now blends execution skill with the accuracy of the scoring model. Without a credible, periodically refreshed model, weighting produces disproportionate quotas just as easily as fair ones - the inputs matter as much as the act of weighting. Disclose this in the plan, and state the model's refresh date next to the allocation table.
