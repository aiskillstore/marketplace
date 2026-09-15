---
name: David Tepper Panic Signal
description: Detect rare panic-buy conditions using VIX, per-ticker fear, quality filters, and liquidity context from LLMQuant Data.
input_data_source: LLMQuant Data
school: macro-momentum
---

# David Tepper Panic Signal

## Purpose

Identify whether current conditions resemble a high-conviction panic-buy setup for quality, liquid large-cap exposure.

## Input Data Source

Use **LLMQuant Data** for VIX, ticker fear, quality filters, market sentiment, and price history.

## Data Needed

Required LLMQuant Data inputs:
- VIX snapshot data for broad panic level and percentile.
- options fear-score data for per-ticker panic.
- equity market snapshot data and company fundamentals data for size, profitability, liquidity, and quality.
- market sentiment snapshot data for breadth and risk regime confirmation.
- equity price history for drawdown and rebound context.

## Signal Gates

All gates should pass for an armed signal:
- VIX is extreme by absolute level and percentile.
- Ticker or index fear score is extreme.
- The target is liquid, large-cap, profitable, and not structurally impaired.
- Market breadth and liquidity are consistent with panic rather than isolated fraud or solvency risk.

Levels:
- Armed: all gates pass.
- Watch: broad fear or ticker fear is close.
- Near: stress is elevated but incomplete.
- Cold: patience state.

## Workflow

1. Default to SPY/QQQ/DIA or user-specified liquid target.
2. Pull VIX, fear, quality, sentiment, and drawdown data.
3. Evaluate each signal gate.
4. If armed, recommend staged exposure rather than all-in timing.
5. If not armed, explain what is missing.

## Output Format

1. **Signal Level**: armed, watch, near, or cold.
2. **Gate Table**: VIX, fear score, quality, sentiment, liquidity.
3. **Action Plan**: stage, wait, hedge, or avoid.
4. **Failure Modes**: why panic may be justified.
5. **Data Used**.

## Guardrails

- Do not apply panic-buy logic to low-quality or illiquid names.
- Do not call every selloff a panic signal.
- Separate "cheap because fear" from "cheap because fundamentals broke."
