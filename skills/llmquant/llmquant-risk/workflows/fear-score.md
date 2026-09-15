---
name: Ticker Fear Score
description: Build a per-ticker panic score from VIX, IV rank, RSI, volume anomaly, put/call ratio, and down-day persistence using LLMQuant Data.
input_data_source: LLMQuant Data
pack: trading
---

# Ticker Fear Score

## Purpose

Quantify single-name fear and identify whether a contrarian entry, premium-sale setup, or wait state is supported by multiple signals.

## Input Data Source

Use **LLMQuant Data** for VIX, IV rank, put/call, technicals, volume anomalies, price history, and option flow.

## Data Needed

Required LLMQuant Data inputs:
- options fear-score data for composite score and components when available.
- VIX snapshot data for broad fear.
- implied-volatility snapshot data and options put/call ratio data for ticker option fear.
- equity technical indicator data and equity price history for RSI, down days, volume anomaly, and drawdown.
- options flow summary data for flow confirmation.

## Workflow

1. Pull all component signals and mark missing inputs.
2. Score each component from 0-100 and weight the composite.
3. Classify the result as calm, elevated, signal-ready, or extreme.
4. Explain which components drove the score.
5. Map the score to potential actions: wait, prepare, sell risk-defined premium, or avoid due to event risk.

## Output Format

1. **Fear Score**: 0-100, signal threshold, confidence.
2. **Component Table**: value, score, weight, fallback/missing status.
3. **Interpretation**: panic, normal pullback, or false signal.
4. **Action Bias**: contrarian, premium sale, hedge, or wait.
5. **Data Used**.

## Guardrails

- Do not treat high fear as automatically bullish.
- Do not use neutral fallbacks without labeling them.
- Check earnings and liquidity before any premium-sale implication.
