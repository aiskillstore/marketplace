---
name: VIX Status
description: Translate current VIX level, percentile, term structure, and history into an options-risk regime using LLMQuant Data.
input_data_source: LLMQuant Data
pack: trading
---

# VIX Status

## Purpose

Turn the market's volatility level into a practical regime read for sizing, hedging, buying protection, or selling premium.

## Input Data Source

Use **LLMQuant Data** for VIX level, history, percentile, term structure, and sentiment context.

## Data Needed

Required LLMQuant Data inputs:
- VIX snapshot data for current VIX, timestamp, change, and percentile.
- VIX history for 1-year and multi-year distribution.
- market volatility term-structure data for contango/backwardation and front/back spread.
- market sentiment snapshot data for breadth and risk regime confirmation.

## Workflow

1. Pull current VIX and history.
2. Classify tier: calm, normal, premium sweet spot, caution, extreme fear.
3. Check term structure for stress confirmation.
4. Map tier to options posture: buy protection, normal sizing, active premium sale, reduced size, or avoid short vol.
5. Include historical distribution by tier.

## Output Format

1. **VIX Tier**: level, label, percentile, timestamp.
2. **Term Structure**: contango/backwardation and implication.
3. **Strategy Posture**: premium selling, hedging, size adjustment.
4. **History Context**: share of past year in each tier.
5. **Data Used**.

## Guardrails

- Do not recommend short volatility in extreme fear without risk caps.
- Do not use VIX alone for single-name option decisions.
- Report whether VIX data is intraday or close-based.
