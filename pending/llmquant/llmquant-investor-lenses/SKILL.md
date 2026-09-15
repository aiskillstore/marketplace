---
name: llmquant-investor-lenses
description: Router skill for LLMQuant investor-lens workflows. Use when the user wants an investor-style reasoning overlay grounded in LLMQuant Data evidence.
input_data_source: LLMQuant Data
category: investor-lenses
---

# LLMQuant Investor Lenses

This category routes investor-style reasoning overlays. The named workflows are analytical lenses, not claims of endorsement or replication. All external evidence must come from LLMQuant Data.

## Routing Rules

1. Identify the requested investor lens, ticker/asset, horizon, and decision type.
2. Select the closest workflow below.
3. Open only that workflow and any local resources explicitly referenced by that workflow.
4. Use LLMQuant Data for filings, prices, fundamentals, ownership, macro, and valuation evidence.
5. Separate evidence from interpretation and avoid unsupported persona claims.

## Workflow Index

| User intent | Workflow |
|---|---|
| Long-term owner lens: moat, circle of competence, and margin of safety. | [`workflows/warren-buffett.md`](workflows/warren-buffett.md) |
| Quantitative value and margin-of-safety discipline. | [`workflows/ben-graham.md`](workflows/ben-graham.md) |
| Multi-model quality investor with inversion discipline. | [`workflows/charlie-munger.md`](workflows/charlie-munger.md) |
| Dhandho, cloning, and low-risk doubles. | [`workflows/mohnish-pabrai.md`](workflows/mohnish-pabrai.md) |
| Emerging-market compounder and ROE-first selection. | [`workflows/rakesh-jhunjhunwala.md`](workflows/rakesh-jhunjhunwala.md) |
| GARP, ten-baggers, and simple explainable businesses. | [`workflows/peter-lynch.md`](workflows/peter-lynch.md) |
| Qualitative growth and scuttlebutt-style research. | [`workflows/phil-fisher.md`](workflows/phil-fisher.md) |
| Disruptive innovation, Wright's Law, and exponential TAM. | [`workflows/cathie-wood.md`](workflows/cathie-wood.md) |
| Macro liquidity regime and asymmetric sizing. | [`workflows/stanley-druckenmiller.md`](workflows/stanley-druckenmiller.md) |
| Concentrated activist value and catalyst unlocks. | [`workflows/bill-ackman.md`](workflows/bill-ackman.md) |
| Contrarian deep value and filing-first downside work. | [`workflows/michael-burry.md`](workflows/michael-burry.md) |
| Tail-risk, barbell, convexity, and antifragile thinking. | [`workflows/nassim-taleb.md`](workflows/nassim-taleb.md) |
| Story-plus-numbers valuation discipline. | [`workflows/aswath-damodaran.md`](workflows/aswath-damodaran.md) |
| Mechanical Buffett-style business, moat, management, and valuation scorecard. | [`workflows/warren-buffett-scorecard.md`](workflows/warren-buffett-scorecard.md) |
| Seller-only quality-business options framework. | [`workflows/duan-yongping-seller.md`](workflows/duan-yongping-seller.md) |
| Cycle-position offense/defense signal. | [`workflows/howard-marks-cycle.md`](workflows/howard-marks-cycle.md) |
| Rare panic-buy gate for liquid quality exposure. | [`workflows/david-tepper-panic-signal.md`](workflows/david-tepper-panic-signal.md) |

## LLMQuant Data Contract

Prefer LLMQuant Data when available. The workflows may need these data capabilities:
- Retrieve filings, fundamentals, valuation inputs, market prices, 13F ownership, macro indicators, options context, credit context, and sentiment evidence.
- Support investor-lens analysis with dated evidence rather than persona-style assertions.
- Preserve the distinction between retrieved facts, user-provided assumptions, and the selected investor framework.

Fallback:
- If a lens needs unavailable data, name the missing input and continue only with retrieved or user-provided evidence.
- Do not invent quotes, holdings, valuation inputs, or biographical claims.
