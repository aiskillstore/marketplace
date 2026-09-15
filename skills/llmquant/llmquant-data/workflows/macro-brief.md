---
name: Macro Brief
description: Compose a market-facing macro brief from LLMQuant Data macro indicators, prices, crypto, and research context.
input_data_source: LLMQuant Data
pack: workflows
---

# Macro Brief

## Purpose

Create a concise macro brief that connects data releases, policy pressure, rates, equity context, commodities or crypto, and portfolio implications.

---

## Input Data Source

Use **LLMQuant Data** as the input data source for macro indicators, historical observations, equity prices, crypto snapshots, and research context. State which LLMQuant Data capabilities were used, cite observation dates or price ranges, and do not invent data that was not retrieved.

---

## LLMQuant Data Contract

Required data capabilities:
- macro indicator snapshot data
- macro indicator history

Optional data capabilities:
- equity price history
- crypto market snapshot data
- crypto historical candle data
- paper research search
- wiki knowledge search

Freshness:
- State each macro observation date.
- State market price date ranges.
- Do not treat monthly or quarterly macro data as if it were intraday.

Fallback:
- If an indicator is unsupported, use macro indicator discovery or explain the missing series.
- If market context is unavailable, keep the brief macro-only.

Output:
- Regime call
- Data dashboard
- Market implications
- Risk scenarios
- Data used

---

## Workflow

1. Define the region, horizon, and assets in scope.
2. Pull latest macro snapshots and histories for inflation, labor, rates, curve, growth, and liquidity.
3. Pull market price context for relevant equity indices, ETFs, or crypto if requested.
4. Identify the dominant regime and the main contradiction.
5. Convert the regime into asset implications with caveats.
6. List the next releases that could break the thesis.

---

## Output Format

Use:

1. **One-Line Regime Call**
2. **Dashboard**
3. **What Changed**
4. **Asset Implications**
5. **Risks To The View**
6. **Next Data**
7. **Data Used**

---

## Guardrails

- Do not overfit a macro narrative to one release.
- Do not hide frequency mismatches.
- Do not present policy path as certain.
- Do not use market data outside the retrieved range.
