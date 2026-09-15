---
name: U.S. Macro Snapshot
description: Build a compact U.S. macro regime read using LLMQuant Data macro indicators.
input_data_source: LLMQuant Data
pack: data
---

# U.S. Macro Snapshot

## Purpose

Create a dated macro regime snapshot across inflation, labor, rates, growth, liquidity, and curve signals. Use this for Fed regime briefs, market context, macro PM setup, or strategy risk framing.

---

## Input Data Source

Use **LLMQuant Data** as the input data source for U.S. macro indicators, observation dates, historical context, and indicator metadata. State which LLMQuant Data capabilities were used, cite observation dates, and do not invent data that was not retrieved.

---

## LLMQuant Data Contract

Required data capabilities:
- macro indicator snapshot data

Optional data capabilities:
- macro indicator history
- macro indicator discovery
- equity price history
- crypto market snapshot data

Freshness:
- Report each indicator's latest observation date.
- Do not compare indicators with different frequencies without noting the mismatch.
- Distinguish data release timing from market pricing.

Fallback:
- If an indicator is unavailable, name it and continue with available indicators.
- If the user asks for an unsupported indicator, use macro indicator discovery to find the nearest supported series.

Output:
- Regime summary
- Indicator table
- Policy and market readthrough
- Watchlist
- Data used

---

## Workflow

1. Clarify region as U.S. unless the user specifies otherwise.
2. Pull snapshots for core inflation, unemployment, nonfarm payrolls, Fed funds, 2Y yield, 10Y yield, 10Y-2Y curve, real GDP, and WTI or financial conditions when relevant.
3. Pull history for indicators where trend matters.
4. Classify regime: disinflation / reflation, easing / tightening, growth acceleration / slowdown, risk-on / risk-off liquidity.
5. Tie every regime claim to dated indicator evidence.

---

## Output Format

Use:

1. **Macro Regime**
2. **Indicator Dashboard**: indicator, latest value, prior value, date, delta, interpretation.
3. **Policy Read**: Fed pressure, curve signal, inflation/labor balance.
4. **Market Readthrough**: equities, rates, USD, commodities, crypto if relevant.
5. **Next Data To Watch**
6. **Data Used**

---

## Guardrails

- Do not call a regime change from one noisy observation.
- Do not mix monthly, quarterly, and daily series without stating date/frequency differences.
- Do not forecast policy as fact.
- Do not use unsupported macro series from memory.
