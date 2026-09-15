---
name: Warren Buffett Scorecard
description: Apply a Buffett-style business, moat, management, and valuation scorecard using LLMQuant Data.
input_data_source: LLMQuant Data
school: value-investing
---

# Warren Buffett Scorecard

## Purpose

Score whether a business is understandable, durable, well-managed, and available at a sensible price relative to long-term alternatives.

## Input Data Source

Use **LLMQuant Data** for company data, filings, valuation history, and rate context. Do not use anecdotes or reputation as substitutes for evidence.

## Data Needed

Required LLMQuant Data inputs:
- equity market snapshot data for size, sector, market, liquidity, and price.
- company fundamentals data for margins, ROE, ROIC, debt, FCF, dividends, buybacks, and growth.
- valuation multiple data and historical valuation data for current and historical valuation.
- SEC filing discovery and SEC filing section retrieval for business description, risks, MD&A, and capital allocation.
- macro indicator snapshot data for 10-year Treasury yield or relevant discount-rate proxy.

## Scorecard

Score 0-100:
- Business/circle of competence: simplicity, predictability, cyclicality, regulatory exposure.
- Moat: pricing power, margins, returns on capital, scale, brand, switching cost.
- Management: capital allocation, dilution, buybacks, dividends, leverage discipline.
- Valuation: FCF yield versus rates, multiples, historical band, margin of safety.

Verdict:
- 75-100: Holdable at the right price.
- 55-74: Watchlist; quality or valuation gap remains.
- Below 55: Avoid for Buffett-style ownership.

## Workflow

1. Pull facts first: fundamentals, filings, valuation, rates.
2. Score each lens and show evidence.
3. Penalize complexity, leverage, poor FCF conversion, and valuation without margin of safety.
4. Provide a hold/buy/watch/avoid verdict only after the scorecard.

## Output Format

1. **Verdict**: holdable, watchable, or avoid.
2. **Scorecard Table**: business, moat, management, valuation.
3. **Evidence**: filings and metrics supporting each score.
4. **Price Discipline**: fair-value range or required margin of safety.
5. **Data Used**.

## Guardrails

- Do not imply Buffett would buy the stock; state "Buffett-style scorecard."
- Do not overrule weak valuation with a good story.
- Do not score moat from brand claims alone.
