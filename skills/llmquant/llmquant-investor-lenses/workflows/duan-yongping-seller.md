---
name: Duan Yongping Seller Framework
description: Apply a seller-only, quality-business options framework using sell puts, covered calls, and panic-buy context from LLMQuant Data.
input_data_source: LLMQuant Data
school: value-investing
---

# Duan Yongping Seller Framework

## Purpose

Frame a quality-stock position through three actions: sell put at a willing-buy price, covered call for yield on owned shares, or wait for broad panic before buying stock.

## Input Data Source

Use **LLMQuant Data** for underlying quality, option chains, IV, VIX, and strategy construction.

## Data Needed

Required LLMQuant Data inputs:
- equity market snapshot data and company fundamentals data for price, quality, and balance-sheet sanity.
- option chain data and options strategy construction data for sell-put and covered-call candidates.
- implied-volatility snapshot data for premium attractiveness.
- VIX snapshot data for broad panic context.

## Framework

Only consider:
- Sell put at a price where the investor is genuinely willing to own the stock.
- Covered call against existing shares when the user accepts assignment risk.
- Stock purchase during extreme broad panic if business quality is intact.

Avoid:
- Buying options as lottery tickets.
- Selling puts on businesses the user does not want to own.
- Selling calls when losing the shares would violate the thesis.

## Workflow

1. Confirm whether the user owns shares, has a willing-buy price, or is evaluating panic context.
2. Check business quality and current price.
3. Pull option chain for 25-50 DTE by default unless user specifies.
4. Build sell-put and covered-call panels with yield, cost basis, assignment result, and risk.
5. Use VIX tier to frame patience versus panic opportunity.

## Output Format

1. **Seller Verdict**: sell put, covered call, buy stock on panic, or wait.
2. **Sell Put Panel**: strike, premium, annualized yield, assigned cost basis, delta.
3. **Covered Call Panel**: strike, premium, yield, upside cap, called-away return.
4. **Panic Context**: VIX, tier, action.
5. **Data Used**.

## Guardrails

- Do not present premium as free income; assignment and opportunity cost are real.
- Do not use this framework for low-quality or unprofitable businesses without warning.
- Do not recommend uncovered calls.
