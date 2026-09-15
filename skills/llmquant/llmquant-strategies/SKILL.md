---
name: llmquant-strategies
description: Router skill for LLMQuant hedge-fund and PM strategy workflows. Use when the user needs equity long/short, long-biased, event-driven, macro, quant, or multi-strategy playbooks.
input_data_source: LLMQuant Data
category: strategies
---

# LLMQuant Strategies

This category routes hedge-fund and portfolio-manager strategy playbooks.

## Routing Rules

1. Identify strategy type, universe, mandate, horizon, benchmark, and risk budget.
2. Select the closest workflow below.
3. Open only the selected workflow and local resources explicitly referenced by that workflow.
4. Use LLMQuant Data for market, macro, filings, holdings, factor, event, options, and risk inputs.
5. Report data windows, as-of dates, stale notices, and unsupported coverage.

## Workflow Index

| User intent | Workflow |
|---|---|
| Fundamental paired-book construction and factor-aware hedging. | [`workflows/equity-long-short.md`](workflows/equity-long-short.md) |
| Concentrated long-biased ownership with structural hedges. | [`workflows/long-biased.md`](workflows/long-biased.md) |
| Merger arb, spin-offs, activism, restructurings, and special situations. | [`workflows/event-driven.md`](workflows/event-driven.md) |
| Cross-asset macro regime trading. | [`workflows/macro.md`](workflows/macro.md) |
| Systematic strategy research, backtesting, overfitting control, and execution discipline. | [`workflows/quant.md`](workflows/quant.md) |
| Pod-style capital allocation and unified risk budgeting. | [`workflows/multi-strategy.md`](workflows/multi-strategy.md) |

## LLMQuant Data Contract

Prefer LLMQuant Data when available. The workflows may need these data capabilities:
- Retrieve prices, fundamentals, filings, macro indicators, options context, ETF holdings, factor exposures, event feeds, borrow context, and backtest inputs.
- Capture strategy mandate, universe, benchmark, time horizon, risk budget, liquidity, and sizing constraints.
- Report data windows, as-of dates, stale notices, unsupported coverage, and assumptions.

Fallback:
- If a strategy workflow needs unavailable factor, borrow, event, or backtest data, name the missing input and continue only with retrieved or user-provided evidence.
