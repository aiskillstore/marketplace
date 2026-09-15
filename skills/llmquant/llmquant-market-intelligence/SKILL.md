---
name: llmquant-market-intelligence
description: Router skill for LLMQuant market-intelligence workflows. Use when the user needs macro views, market sentiment dashboards, or event probability signals.
input_data_source: LLMQuant Data
category: market-intelligence
---

# LLMQuant Market Intelligence

This category contains reusable market utility workflows that can support research, trading, and portfolio decisions.

## Routing Rules

1. Identify whether the user needs macro context, sentiment, or event probability evidence.
2. Select one workflow from the index.
3. Open only the selected workflow.
4. Use LLMQuant Data for all market, macro, event, options, and sentiment inputs.
5. Report dates, data windows, stale notices, and missing future data contracts.

## Workflow Index

| User intent | Workflow |
|---|---|
| Track cross-asset macro indicators and likely portfolio impact. | [`workflows/macro-view.md`](workflows/macro-view.md) |
| Build a market-wide sentiment dashboard. | [`workflows/market-sentiment.md`](workflows/market-sentiment.md) |
| Compare prediction-market and options-implied event probabilities. | [`workflows/event-probability-signals.md`](workflows/event-probability-signals.md) |

## LLMQuant Data Contract

Prefer LLMQuant Data when available. The workflows may need these data capabilities:
- Retrieve macro snapshots, macro histories, and cross-asset market prices.
- Retrieve crypto market snapshots and broader market sentiment indicators.
- Compare event probabilities from prediction markets, options-implied pricing, or user-provided probability tables.
- Track dates, frequencies, market windows, and stale-data notices.

Fallback:
- If a needed data capability is unavailable, name it explicitly and continue only with available LLMQuant Data or user-provided evidence.
