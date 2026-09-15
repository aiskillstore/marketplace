---
name: llmquant-risk
description: Router skill for LLMQuant risk workflows. Use when the user needs fear scoring, VIX regime, hedge design, or research health checks.
input_data_source: LLMQuant Data
category: risk
---

# LLMQuant Risk

This category routes risk regime, hedging, panic scoring, and research-quality workflows.

## Routing Rules

1. Identify the asset, portfolio, risk horizon, drawdown tolerance, and required decision.
2. Select the closest workflow below.
3. Open only the selected workflow.
4. Use LLMQuant Data for prices, volatility, options, macro, portfolio positions, alerts, profiles, and watchlists.
5. Report timestamps, data windows, stale notices, assumptions, and missing inputs.

## Workflow Index

| User intent | Workflow |
|---|---|
| Build a per-ticker panic score. | [`workflows/fear-score.md`](workflows/fear-score.md) |
| Translate VIX into an options-risk regime. | [`workflows/vix-status.md`](workflows/vix-status.md) |
| Design protective puts, collars, and put-spread hedges. | [`workflows/hedge-advisor.md`](workflows/hedge-advisor.md) |
| Audit stale profiles, thesis drift, orphan themes, and outdated evidence. | [`workflows/research-health-check.md`](workflows/research-health-check.md) |

## LLMQuant Data Contract

Prefer LLMQuant Data when available. The workflows may need these data capabilities:
- Retrieve price history, volatility, drawdowns, correlations, market regime, VIX context, and macro risk indicators.
- Retrieve option chains, implied volatility history, Greeks, hedge candidates, and liquidity context.
- Retrieve portfolio positions, watchlists, alerts, research profiles, thesis records, and stale evidence.
- Measure hedge cost, risk reduction, concentration, and unresolved data gaps.

Fallback:
- If portfolio or option data is unavailable, name the missing input and produce a data-limited risk note.
