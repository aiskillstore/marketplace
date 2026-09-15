---
name: Watchlist Monitor
description: Manage and summarize a user watchlist with price, IV, earnings, unusual activity, score changes, and priority alerts using LLMQuant Data.
input_data_source: LLMQuant Data
pack: research
---

# Watchlist Monitor

## Purpose

Maintain a practical watchlist dashboard that tells the user what changed, what matters, and which tickers need attention today.

## Input Data Source

Use **LLMQuant Data** for watchlist storage, prices, IV, unusual activity, events, and market context.

## Data Needed

Required LLMQuant Data inputs:
- watchlist retrieval capability, watchlist update capability, and watchlist deletion capability for list management.
- equity market snapshot data for price, day change, volume, and liquidity.
- implied-volatility snapshot data for IV rank, IV percentile, HV, and VRP.
- unusual options activity data for flow alerts.
- equity event calendar data for earnings and corporate events.
- market sentiment snapshot data for regime context.

## Workflow

1. Determine whether the user wants to add, remove, list, or summarize tickers.
2. Mutate the watchlist only when requested.
3. Pull current data for all watchlist tickers.
4. Rank notifications by urgency: event today, unusual activity, IV extreme, price break, score change.
5. Present a dashboard first, then details on requested tickers.

## Output Format

1. **Watchlist Summary**: tickers, market context, highest-priority changes.
2. **Ticker Table**: price, move, IV rank, next event, active alert.
3. **Priority Alerts**: reason, timestamp, suggested next check.
4. **Actions**: analyze, set alert, remove, create profile.
5. **Data Used**.

## Guardrails

- Do not add or remove tickers without explicit user intent.
- Do not treat a watchlist notification as a trade recommendation.
- Flag stale or unavailable option data ticker by ticker.
