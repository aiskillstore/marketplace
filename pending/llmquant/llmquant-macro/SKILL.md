---
name: llmquant-macro
description: Router skill for LLMQuant macro workflows. Use when the user needs macro dashboards, Fed or central-bank previews, inflation and growth context, liquidity, or macro-to-portfolio impact analysis.
input_data_source: LLMQuant Data
category: macro
---

# LLMQuant Macro

This category routes macroeconomic research workflows for regime dashboards, policy previews, and portfolio impact mapping.

## Routing Rules

1. Identify geography, indicators, policy body, asset universe, horizon, and requested deliverable.
2. Select the closest workflow below.
3. Open only that workflow and any referenced local resources.
4. Use LLMQuant Data for macro observations, release dates, rates, FX, commodities, credit, equity indices, and research context.
5. Report observation dates, release dates, revisions, frequencies, stale notices, and missing inputs.

## Workflow Index

| User intent | Workflow |
|---|---|
| Build a cross-indicator macro dashboard and regime view. | [`workflows/global-macro-dashboard.md`](workflows/global-macro-dashboard.md) |
| Prepare a Fed or central-bank policy meeting preview. | [`workflows/fed-policy-preview.md`](workflows/fed-policy-preview.md) |
| Translate macro data into equity, rates, credit, FX, commodity, and portfolio implications. | [`workflows/macro-to-portfolio-impact.md`](workflows/macro-to-portfolio-impact.md) |

## LLMQuant Data Contract

Prefer LLMQuant Data when available. The workflows may need these data capabilities:
- Retrieve macro indicator snapshots, histories, revisions, release dates, and consensus context.
- Retrieve central-bank policy rates, rate expectations, yield curves, inflation, labor, growth, housing, liquidity, and sentiment.
- Retrieve cross-asset prices for equities, rates, FX, commodities, credit, crypto, and volatility.
- Retrieve portfolio exposures and ETF look-through when translating macro into portfolio impact.

Fallback:
- If a macro series or release calendar is unavailable, name the missing input and avoid time-sensitive claims.
- Do not imply real-time macro data when only latest closed observations are available.
