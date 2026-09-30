# Validation checks

Two gates a quota plan must pass before it ships:

- The sanity ratios.
- The attainment-distribution model.

All benchmark figures below are B2B SaaS - no equivalent published rep-level series exists for B2C (its trade data measures market transactions, not rep performance), so validate a B2C plan against the org's own historicals.

## Sanity ratios

| Ratio             | Band                                                   | Segment variation                                     |
| ----------------- | ------------------------------------------------------ | ----------------------------------------------------- |
| Quota:OTE         | 4x-6x, ~5x steady state                                | ~3x SMB/early-stage; 7x-10x+ enterprise/multi-product |
| Pipeline coverage | 3x-5x                                                  | SMB 2x-3x; mid-market 3x-4x; enterprise 4x-7x         |
| Commission rate   | ~10% new business, ~5% renewal                         | -                                                     |
| Comp cost of sale | ~20% of new ARR at 5x quota:OTE (~31¢/$1 fully loaded) | -                                                     |

Measured medians: Bridge Group found quota:OTE at 4.2x in 2024 ($800K quota / $190K OTE) and 4.6x in 2026 ($960K / $200K).

**The linkage (Insight Partners' 5x-rule mechanics):** at a 50/50 base-variable split, a 5x quota:OTE ratio implies roughly a 10% commission rate on new business, and required pipeline coverage follows from win rate as `coverage ≈ 1 ÷ win rate`. Quota:OTE, pay mix, and commission rate are one system - fix two and the third is determined.

A quota that pushes quota:OTE out of band therefore breaks the comp plan too: flag it to mbfinotti/sales-skills@sales-comp-design rather than patching the quota alone. Building the coverage model in full is mbfinotti/sales-skills@sales-pipeline-coverage-modeling's job.

Caveat: per-segment granularity beyond the headline multiples is frequently vendor content marketing. Cross-check any specific segment figure against a second independent source before relying on it.

## Attainment distribution: target shape vs. current reality

**Classic target:** a bell curve.

- 60-70% of reps at or slightly above quota.
- 15-20% outperforming.
- 10-15% short.

This shape is what keeps a comp plan cost-effective and a team motivated.

**Current reality - re-baseline before grading against the classic figure.** Attainment structurally collapsed after 2022:

| Source                                                    | Metric                    | Value                                                                                 |
| --------------------------------------------------------- | ------------------------- | ------------------------------------------------------------------------------------- |
| Bridge Group (biennial; n=172 in 2024, n=158 in 2026)     | AEs hitting annual quota  | 74% (2012) → 66% (2022) → 51% (2024) → 48% (2026)                                     |
| RepVue Cloud Sales Index (~47-57K rep ratings, quarterly) | Average attainment        | ~43-44% through 2025                                                                  |
| Salesforce State of Sales (multi-industry survey)         | Reps hitting annual quota | 28% individually - its lowest in six years                                            |
| ICONIQ State of GTM (150+ B2B software cos.)              | _Ramped_ AEs at quota     | 58% (2025) → 62% (2026) - the outlier moving up; narrower, more forgiving denominator |
| WorldatWork / BSC                                         | Best-practice target      | 60% at annual quota (guidance, not measurement)                                       |

The shape changed too: instead of a bell, 2024-2026 data shows a barbell - the top ~20% of reps clearing 120%+ while the bottom third sits under ~40%, with a shrinking middle. Bridge Group's 2026 edition confirms the shift: fewer companies in the 50-90% attainment range, more in the 0-30% zone.

**How to use it:** model the proposed quota's expected distribution from rep-level history. A modeled barbell is the signature of a top-down target with no capacity validation behind it. Grade the model against the re-baselined reality (a well-run team lands roughly in the 60-75% top-quartile band, not the folk 100%-for-everyone), and state in the plan which baseline you graded against.

## Re-baselining triggers (during the cycle)

- **Under ~40% of reps at quota** - the named threshold at which the quota process and comp plan need re-derivation, not coaching.
- **Team attainment under ~45%** - top-quartile rep attrition steepens sharply around this level; a quota failure becomes a retention failure.
- **Underperformance spreading to historically strong reps and territories** - the signal that the target/capacity model is wrong rather than execution being weak. Chronic bottom performers missing is a management question; everyone missing is a planning question.

## Sourcing rules

- Triangulate at least three independent series before setting anything - published sources diverge by more than 15% on attainment.
- Weight by methodology: Bridge Group (transparent biennial sample) and RepVue (largest rep-reported sample, self-selected) over vendor-published segment breakdowns; survey-of-opinion data (Salesforce) is directional only.
- Drop a source that has skipped two publication cycles.
