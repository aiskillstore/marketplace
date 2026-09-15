---
name: Theme Research
description: Build and monitor thematic equity baskets with tickers, keywords, exposure, valuation, performance, and event signals using LLMQuant Data.
input_data_source: LLMQuant Data
pack: research
---

# Theme Research

## Purpose

Create and maintain a research theme such as AI infrastructure, dividends, EV supply chain, biotech catalysts, energy transition, or regional exposure.

## Input Data Source

Use **LLMQuant Data** for theme storage, tickers, prices, fundamentals, events, ETF holdings, and news/event matches.

## Data Needed

Required LLMQuant Data inputs:
- theme retrieval capability, theme inventory, theme update capability, and theme deletion capability for lifecycle.
- equity market snapshot data and equity price history for current movers and theme performance.
- company fundamentals data for valuation and quality summary.
- equity event radar data and news and event search for keyword and ticker-specific events.
- ETF holdings data when the theme is expressed through ETFs or basket proxies.

## Workflow

1. Determine whether the user wants to create, view, update, delete, or monitor a theme.
2. Normalize tickers and keywords.
3. Pull current data for each ticker and aggregate performance, valuation, and event signals.
4. Flag stale tickers, missing profiles, extreme concentration, and overlapping themes.
5. Present theme-level takeaways before ticker-level detail.

## Output Format

1. **Theme Snapshot**: name, tickers, keywords, last updated.
2. **Top Movers / Laggards**: performance and dates.
3. **Valuation / Quality Summary**: aggregate and outliers.
4. **Event Feed**: matched events and relevance.
5. **Portfolio Actions**: add/remove tickers, create profiles, set alerts.
6. **Data Used**.

## Guardrails

- Do not treat a theme as diversified if one or two names dominate exposure.
- Do not include news/event claims without dates and source metadata.
- If the user supplies vague theme names, propose a ticker/keyword draft and mark it provisional.
