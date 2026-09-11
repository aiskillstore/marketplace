# 100,000-row synthetic demo

[简体中文](DEMO.zh-CN.md)

This case shows what `sheet-to-report` produces from a single structured workbook. The data, business context, and findings are synthetic.

## Input

| Item | Demo scope |
| --- | --- |
| Records | 100,000 |
| Period | January 2024 to June 2025 |
| Dimensions | Channel, region, category, and user tier |
| Metrics | Visits, orders, revenue, refunds, and marketing cost |
| Goal | Review growth, efficiency, refund pressure, and the next tests |

The public showcase publishes the finished HTML report, four matched slide comparisons, and both complete 23-slide demo decks. The 5 MB source workbook is not bundled. Use `scripts/generate_sample.py` to create a smaller synthetic workbook for a local workflow test.

## Accepted findings in this demo

1. **Revenue grew while marketing return fell.** The report directs attention to paid-advertising efficiency and treats content-led growth as a hypothesis to verify.
2. **Apparel growth came with refund pressure.** Expansion and after-sales investigation belong in the same decision path.
3. **Customer-tier averages do not prove repeatable lift.** The report keeps the distinction between a descriptive segment difference and a causal result.

## Output tour

**[Open the complete public showcase](https://majichuan.github.io/sheet-to-report/)** · [Read the full HTML report](https://majichuan.github.io/sheet-to-report/report.html)

The HTML report provides a fixed reading path from headline judgments to the operating baseline, chart evidence, actions, and metric definitions. Each major claim links to its evidence and keeps the limitations that affect interpretation.

| Editable standard deck | Optional SlideViber refinement |
| --- | --- |
| ![Standard deck chart page](assets/screenshots/standard-ppt-chart.png) | ![SlideViber-refined chart page](assets/screenshots/slideviber-ppt-chart.png) |

Both slides use the same source values and conclusion. The standard version prioritizes direct editing and presentation structure. The SlideViber version uses a separate composition with a stronger relationship between the judgment, business meaning, and chart. The refinement remains optional and requires a separate SlideViber installation.

[Download the complete editable standard PPTX](https://majichuan.github.io/sheet-to-report/downloads/sheet-to-report-demo-standard.pptx) · [Download the complete SlideViber-refined PPTX](https://majichuan.github.io/sheet-to-report/downloads/sheet-to-report-demo-slideviber.pptx)

## What this demonstrates

- The analysis starts from metric meaning and the business question.
- Conclusions retain their period, denominator, filter, and evidence relationship.
- HTML and both PPT routes share one analysis model, so visual refinement cannot silently change the result.
- Actions name the object to change, the method, the success signal, and the boundary.

This is a product demonstration, not a benchmark or a claim about a real business.
