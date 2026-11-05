# Measurement and benchmark use

## Poptin 2026 reference

Source: [Poptin's public report](https://www.poptin.com/blog/popup-conversion-rate-benchmarks-2026/), published October 8, 2026; checked November 4, 2026.

January–September 2026 retained sample: 5,885 popups, 3,897 accounts, 138,664,470 recorded views.

| Objective | Median | 75th percentile | 90th percentile | Popups |
|---|---:|---:|---:|---:|
| Form submissions | 1.30% | 2.67% | 5.29% | 2,305 |
| Tracked button clicks | 2.95% | 6.00% | 12.40% | 3,580 |

Each popup contributes equally to percentiles; pooled rates weight exposure. Eligibility required 1,000 views and 14 exposure days. The lowest objective-specific decile was excluded before these summaries. This is a selected vendor cohort, not an all-site average. Views/events can repeat and do not establish valid contacts, consent, or revenue. Design snapshots may differ from historical designs; unavailable designs and unadjusted bots can bias results. Comparisons are descriptive, not causal. Embedded forms are outside scope. Historical timing, targeting, frequency, industry, and lead-quality benchmarks are not established here.

Gamified submission median: 6.80%, only 31 popups from 27 accounts. It is exploratory, not a predicted lift. Do not infer that a format switch causes improvement. Percentile thresholds are not averages of top performers or guarantees.

## Analysis contract

For user-supplied results, record:
- Objective and event definition, including bot/deduplication rules.
- Event count and eligible denominator, date range, timezone, and attribution window.
- Whether exposure means displays, sessions, or unique people; do not silently change units.
- Audience, device, campaign eligibility, variants, and changes during the period.
- Integration receipts and downstream quality where available.

A zero denominator yields an undefined rate, not 0%. Flag events above exposures and investigate rather than clipping. Report counts alongside percentages. Distinguish percentage-point change from relative lift: moving from 2% to 3% is +1 percentage point and +50% relative. A relative lift from a zero baseline is undefined.

## Experiment decision

Choose a randomization unit that matches the business question and repeated visits. Check assignment persistence, exposure logging, exclusions, sample-ratio mismatch, contamination, and concurrent tests. Use a suitable statistical method with predeclared assumptions; don't apply independent-user formulas to repeated popup impressions without qualification. Account for multiple variants or outcomes when drawing conclusions.

To calculate sample size, first obtain baseline rate, smallest worthwhile effect (absolute or relative), chosen power, significance level, allocation, and independent analysis unit. State the method and assumptions, then convert the required eligible units into a duration using actual traffic. If these inputs are missing, ask for them or label illustrative assumptions; do not manufacture a universal minimum.

Track qualified leads per eligible visitor and, for coupons, contribution margin or incremental revenue per eligible visitor where feasible. A popup-free holdout can answer whether the intervention helps overall outcomes; a format A/B test alone cannot establish that.

Guardrails may include page conversion, checkout completion, dismissal, complaints, unsubscribe, lead rejection, and site performance. Decide thresholds with the user. A deadline can end collection without producing a winner. Report inconclusive outcomes honestly and preserve the control if business evidence is insufficient.

## Academy experiment loop

The [public popup experiment guide](https://www.poptin.com/academy/guides/build-a-reliable-popup-experiment-loop-that-improves-conversions-over-time/), checked 2026-11-04, motivates a repeatable learning record: hypothesis, audience, trigger, changed variable, dates, result, and next action. Keep the control available. If eligibility or measurement changes mid-test, document it and reassess comparability rather than pooling incompatible periods. Diagnose the bottleneck: weak delivery suggests rule/trigger issues; strong clicks with weak submissions suggests form or next-step friction. Use the statistical safeguards above before interpreting a winner.
