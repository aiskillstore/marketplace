---
name: Event Probability Signals
description: Compare prediction-market probabilities with options-implied and macro-implied probabilities to identify event mispricing using LLMQuant Data.
input_data_source: LLMQuant Data
pack: research
---

# Event Probability Signals

## Purpose

Identify mismatches between event probabilities implied by prediction markets, options markets, macro data, and related asset prices.

## Input Data Source

Use **LLMQuant Data** for prediction market events, market prices, options-implied probabilities, macro observations, and asset context.

## Data Needed

Required LLMQuant Data inputs:
- prediction-market event data and prediction-market price data for event definitions, odds, liquidity, and close dates.
- options-implied event probability data and option chain data for option-derived event probabilities and skew.
- macro indicator snapshot data and macro indicator history for macro events such as Fed, inflation, labor, or recession.
- equity price history for related tickers and ETFs.

## Workflow

1. Define the event, event date, settlement criteria, and relevant assets.
2. Pull prediction-market odds, liquidity, and update time.
3. Pull options-implied probability for the same event window.
4. Compare probability spread, liquidity, timing, and basis risk.
5. Suggest possible expressions only when the mapping from event to instrument is defensible.

## Output Format

1. **Probability Gap**: event odds, options-implied odds, spread, confidence.
2. **Event Contract**: settlement criteria, deadline, liquidity, source timestamp.
3. **Market Mapping**: affected tickers/options/macros and basis risk.
4. **Possible Expressions**: options, ETFs, or no trade.
5. **Data Used**.

## Guardrails

- Do not call an arbitrage unless settlement, liquidity, fees, and basis risk are addressed.
- Do not compare probabilities for mismatched event windows.
- If event criteria are ambiguous, lead with that caveat.
