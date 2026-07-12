# Ad Test Design Guide

Detail pack for [ad-test-designer](../SKILL.md). Use the stdlib `experiment.py` helper for deterministic calculations or show the same inputs and formulas manually; do not introduce a hidden notebook/library result.

## Variant matrix template

| Variant | One changed variable | What's held constant | Destination |
|---------|---------------------|----------------------|-------------|
| A (control) | — (baseline) | everything | current LP/URL |
| B | the single test change | all else = control | same or split URL |
| C, D (A/B/n, ≤ 4 total) | a different single change each | all else = control | same |

Rules: one variable per variant; keep a control/holdout; cap A/B/n at 4 variants so traffic isn't split too thin; same audience + budget logic across arms.

### Test structures

- **Creative A/B** — vary one creative element (headline / hook / image). Primary metric usually CTR or CVR.
- **Landing-page A/B / split-URL** — vary one page element (hero, CTA, proof). Primary metric CVR; guardrail bounce.
- **Incrementality (geo / holdout)** — a treated group gets the change, a matched holdout does not. Measures lift over the counterfactual, not just relative variant performance. Needs a clean, comparable holdout (geo split or audience holdout) and a longer window.

## Sample-size lookup (per variant, two-sided α = 0.05, power = 0.80)

Approximate exposures **per variant** to detect a relative lift on a binary metric (CVR/CTR). Interpolate; for A/B/n add ~20–30% headroom for multiple comparisons.

| Baseline rate | 10% lift | 20% lift | 50% lift |
|---------------|----------|----------|----------|
| 1% | ~150k | ~39k | ~6k |
| 3% | ~47k | ~12k | ~2k |
| 5% | ~27k | ~7k | ~1.2k |
| 10% | ~12k | ~3k | ~550 |

**Duration** = (per-variant sample × number of variants) ÷ (traffic/day reaching the test). Floor at one full business cycle (≥ 1–2 weeks) to absorb day-of-week effects. Pre-commit to the sample size; **do not peek and stop early** — early stopping inflates false positives.

**Power note**: power (1−β) is the chance of detecting a true effect of the stated size. The table is built at 0.80; if the user wants 0.90, sizes rise ~30%. State the assumed baseline, minimum detectable effect, α, and power in the design.

## Significance methods

### Two-proportion z-test (CVR / CTR)

For control rate p₁ = x₁/n₁ and variant rate p₂ = x₂/n₂:

1. Pooled rate `p = (x₁ + x₂) / (n₁ + n₂)`.
2. Standard error `SE = sqrt( p·(1−p)·(1/n₁ + 1/n₂) )`.
3. `z = (p₂ − p₁) / SE`.
4. Compare the two-sided p-value with the **precommitted alpha**. `|z| ≥ 1.96` corresponds only to the common `alpha=.05` reference case.

Report p₁, p₂, the relative lift `(p₂−p₁)/p₁`, and the z value with its inputs shown.

### Mann-Whitney U (non-normal continuous metrics)

Use for revenue-per-user, order value, or time-on-page where the distribution is skewed. Compare at the declared alpha and report the effect alongside U; `experiment.py continuous` provides the deterministic stdlib implementation.

### Bootstrap confidence interval (CI on the lift)

Resample each arm with replacement, recompute the statistic, and take the percentiles implied by the declared alpha. Report the interval directly; exclusion of zero is a statistical flag, while clearing a practical-effect boundary is a separate flag.

## Decision ownership

Record the statistical and practical conditions separately:

```
statistically_detected = p < precommitted_alpha
practically_material   = effect clears precommitted practical boundary
```

| Evidence state | Permitted interpretation |
|----------------|--------------------------|
| Statistical + practical flags clear; guardrails hold | Eligible for the named owner to apply the precommitted action rule |
| Statistical flag clears; practical flag does not | Detected but below the declared business-relevance boundary |
| Practical flag clears; statistical flag does not | Directionally large but uncertain; no winner claim |
| Planned sample incomplete or repeated-look policy violated | Incomplete/invalid read; no terminal recommendation |
| Guardrail crosses its precommitted stop rule | Apply the declared stop/escalation rule and name its owner |
| No owner or action rule on file | `decision: UNDECIDED` regardless of the statistical flags |

Never claim that `experiment.py` selected a winner or action. It returns calculated evidence; the calling skill applies only the precommitted rule owned by a named person or process.
