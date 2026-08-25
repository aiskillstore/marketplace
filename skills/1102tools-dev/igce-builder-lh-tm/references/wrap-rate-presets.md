# Burden Multiplier Reference

Use multipliers as transparent estimating assumptions. A burden multiplier represents wages, fringe, overhead, G&A, and profit in the fixed hourly labor rate. It is not evidence that a particular contractor has those costs.

## Baseline scenarios

| Environment | Low | Mid | High | Use |
|---|---:|---:|---:|---|
| Commercial professional services or GSA MAS | 1.8x | 2.0x | 2.2x | Default when the user accepts a generic scenario |
| Services-centric multi-agency IDIQ | 1.9x | 2.1x | 2.3x | Directional prior only |
| Agency-specific or cleared-services IDIQ | 2.0x | 2.2x | 2.4x | Use only when the requirement supports added cost |
| DOE management and operations environment | 2.2x | 2.4x | 2.6x | Directional prior only |

Do not automatically apply a clearance, SCIF, or OCONUS increment. The skill's data sources do not measure those premiums. If the requirement includes one, identify the unsupported factor and ask the user for a multiplier, approved rate, or other basis.

## Selection order

Use the strongest available basis:

1. User-supplied fixed hourly rates.
2. Contract-, vehicle-, or solicitation-specific rates.
3. CO-supplied FPRA, FPRR, audited, or bilateral rates.
4. A user-confirmed scenario from the table.
5. The 1.8x, 2.0x, 2.2x generic baseline with explicit disclosure.

If an audited or approved multiplier controls, use it as the point estimate. Do not force it into the table or bookend it by plus or minus 0.2. A sensitivity display may be added only when requested and must say that the approved rate remains authoritative.

## Custom multiplier

When the user supplies a custom multiplier, use it as the primary estimate. Ask whether low and high scenarios are required. If the user accepts a sensitivity convention, plus or minus 0.2 may be used, bounded at zero, and must be labeled sensitivity rather than evidence.

## Dimensional rules

```text
direct hourly rate = aged annual wage / 2,080
burdened hourly rate = direct hourly rate * burden multiplier
period labor = burdened hourly rate * productive hours * FTE * months / 12
```

- Use 2,080 only to convert an annual wage to an hourly direct rate.
- Use the user-supplied or assumption-cell productive hours to price annual labor.
- Apply burden only to labor.
- Do not apply burden to travel, materials, computer usage, licenses, or other direct costs.
- Keep the hourly rate and labor-category ceiling hours visible so the NTE labor amount can be reproduced.

## CALC+ comparison

Compare each burdened hourly labor rate with a level-matched CALC+ pool. Show the underlying direct hourly rate and multiplier so a reviewer can bridge the arithmetic. When the difference from P50 exceeds 15%, inspect seniority, SOC, geography, title-pool composition, and multiplier basis before writing the neutral note.
