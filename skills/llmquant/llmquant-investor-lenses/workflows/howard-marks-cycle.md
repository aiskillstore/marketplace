---
name: Howard Marks Cycle
description: Estimate market cycle position and offense-versus-defense posture from sentiment, volatility, valuation, and credit data using LLMQuant Data.
input_data_source: LLMQuant Data
school: cycle-risk
---

# Howard Marks Cycle

## Purpose

Replace market forecasting with cycle-position awareness: play offense when fear and value are favorable, defense when optimism and valuation are stretched.

## Input Data Source

Use **LLMQuant Data** for volatility, sentiment, valuation, credit, rates, and macro context.

## Data Needed

Required LLMQuant Data inputs:
- market sentiment snapshot data, VIX snapshot data, and market put/call ratio data for fear/complacency.
- implied-volatility snapshot data for SPY or index-proxy IV rank.
- valuation multiple data for market valuation percentiles.
- macro indicator snapshot data and macro indicator history for credit spreads, rates, liquidity, and financial conditions.

## Cycle Score

Map each component to 0-100:
- 0 means panic, attractive forward risk/reward, offense favored.
- 100 means euphoria, poor forward risk/reward, defense favored.

Posture bands:
- 0-24: hard offense.
- 25-39: offense.
- 40-59: neutral.
- 60-74: defense.
- 75-100: hard defense.

## Workflow

1. Pull sentiment, volatility, valuation, and credit inputs.
2. Normalize each input to a cycle component with historical percentile.
3. Compute weighted cycle score and confidence.
4. Explain disagreements between components.
5. Translate posture into sizing, cash, hedging, and risk appetite.

## Output Format

1. **Cycle Score**: 0-100, posture, confidence.
2. **Component Table**: value, percentile, cycle contribution.
3. **Offense/Defense Plan**: add risk, hold, trim, hedge, or wait.
4. **Contrary Evidence**: what argues against the score.
5. **Data Used**.

## Guardrails

- Do not use cycle score as a market-timing guarantee.
- Do not force offense or defense when components conflict.
- Use percentile windows consistently and report them.
