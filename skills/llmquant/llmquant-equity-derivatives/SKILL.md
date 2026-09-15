---
name: llmquant-equity-derivatives
description: Router skill for LLMQuant equity derivatives workflows. Use when the user needs single-stock derivative, convertible, warrant, structured payoff, or hybrid security analysis.
input_data_source: LLMQuant Data
category: equity-derivatives
---

# LLMQuant Equity Derivatives

This category routes single-stock derivative and hybrid security workflows. It covers payoff, optionality, dilution, borrow, volatility, and catalyst alignment.

## Routing Rules

1. Identify the underlying ticker, derivative type, maturity, strike/conversion terms, and objective.
2. Select the closest workflow below.
3. Open only that workflow and any relevant local resources.
4. Use LLMQuant Data for underlying prices, option chains, volatility, borrow, corporate actions, convertibles, and warrants.
5. Report contract terms, valuation dates, assumptions, stale notices, and missing inputs.

## Workflow Index

| User intent | Workflow |
|---|---|
| Build a single-stock derivative trade playbook with payoff, Greeks, catalysts, and risk. | [`workflows/single-stock-derivative-playbook.md`](workflows/single-stock-derivative-playbook.md) |
| Analyze convertibles, warrants, or hybrid equity-linked securities. | [`workflows/convertible-and-warrant-lens.md`](workflows/convertible-and-warrant-lens.md) |

## LLMQuant Data Contract

Prefer LLMQuant Data when available. The workflows may need these data capabilities:
- Retrieve underlying equity prices, realized volatility, drawdowns, liquidity, and corporate actions.
- Retrieve option chains, implied volatility history, Greeks, borrow costs, and event calendars.
- Retrieve convertible, warrant, rights, and hybrid-security term sheets, including strike, maturity, conversion, redemption, and anti-dilution terms.
- Retrieve credit context, issuer fundamentals, and filing evidence when relevant.

Fallback:
- If derivative terms are unavailable, state the exact term sheet fields needed and do not estimate them from memory.
