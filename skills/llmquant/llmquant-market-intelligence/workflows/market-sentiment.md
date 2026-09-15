---
name: Market Sentiment
description: Build a market-wide sentiment dashboard with VIX, put/call, breadth, fear/greed, sector rotation, and regime classification using LLMQuant Data.
input_data_source: LLMQuant Data
pack: research
---

# Market Sentiment

## Purpose

Classify the current market as risk-on, risk-off, complacent, stressed, or neutral using multiple sentiment and participation indicators.

## Input Data Source

Use **LLMQuant Data** for sentiment indicators, market index history, sector performance, and observation dates.

## Data Needed

Required LLMQuant Data inputs:
- market sentiment snapshot data for composite sentiment.
- VIX snapshot data for level, percentile, and term structure if available.
- market put/call ratio data for equity and index positioning.
- market breadth snapshot data for advance/decline, new highs/lows, and participation.
- sector rotation snapshot data for sector leadership and cycle mapping.
- equity price history for SPY, QQQ, IWM, DIA, or requested index proxies.

## Workflow

1. Pull current market sentiment components and historical context.
2. Classify each component as fear, greed, neutral, or conflicting.
3. Aggregate into a regime call with confidence.
4. Explain implications for equity beta, options premium, hedging, and position sizing.
5. Show disagreements between indicators instead of hiding them.

## Output Format

1. **Regime Call**: risk-on, risk-off, neutral, or mixed; confidence.
2. **Indicator Table**: reading, percentile, interpretation, date.
3. **Sector Rotation**: leaders, laggards, cycle implication.
4. **Trading Implications**: premium selling, hedging, beta, cash.
5. **Data Used**.

## Guardrails

- Do not infer sentiment from price action alone when breadth or positioning is missing.
- Do not treat put/call spikes as directional without context.
- Report the lookback period for all percentile claims.
