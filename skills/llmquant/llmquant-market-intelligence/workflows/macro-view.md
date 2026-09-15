---
name: Macro View
description: Track cross-asset macro indicators and explain their likely impact on a user's watchlist or portfolio using LLMQuant Data.
input_data_source: LLMQuant Data
pack: research
---

# Macro View

## Purpose

Create a monitored macro dashboard for indicators such as VIX, Treasury yields, dollar index, gold, oil, bitcoin, credit spreads, inflation, labor, and liquidity.

## Input Data Source

Use **LLMQuant Data** for all macro observations, cross-asset prices, crypto snapshots, profile holdings, and impact analysis.

## Data Needed

Required LLMQuant Data inputs:
- cross-asset macro snapshot data for VIX, DXY, gold, oil, yields, credit, and major risk assets.
- macro indicator snapshot data and macro indicator history for FRED-backed macro series.
- equity price history and crypto market snapshot data for asset-market context.
- research profile inventory when the user wants portfolio or watchlist impact.

## Workflow

1. Identify requested indicators or load the user's tracked macro list.
2. Pull latest values, previous values, historical percentile, and observation dates.
3. Classify each indicator as easing/tightening, risk-on/risk-off, inflationary/disinflationary, or growth supportive/negative.
4. Connect macro moves to the user's tickers or themes when profile data exists.
5. Separate observed data from portfolio interpretation.

## Output Format

1. **Macro Dashboard**: indicator, latest value, change, percentile, date.
2. **Regime Read**: liquidity, rates, inflation, growth, risk sentiment.
3. **Portfolio Impact**: affected holdings, direction, confidence.
4. **Next Data to Watch**.
5. **Data Used**.

## Guardrails

- Do not mix daily market indicators with monthly macro releases without date labels.
- Do not call a regime change from one indicator alone.
- If portfolio holdings are unavailable, provide general asset implications only.
