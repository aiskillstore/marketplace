---
name: Options Hedge Advisor
description: Recommend protective puts, collars, put spreads, or position rules for an existing holding using LLMQuant Data option chains and risk data.
input_data_source: LLMQuant Data
pack: trading
---

# Options Hedge Advisor

## Purpose

Design a practical hedge for an existing position based on cost basis, current price, gain/loss, drawdown, event risk, and hedge budget.

## Input Data Source

Use **LLMQuant Data** for current price, drawdowns, option chains, strategy construction, simulations, Greeks, and IV context.

## Data Needed

Required LLMQuant Data inputs:
- equity market snapshot data and equity price history for current P&L and drawdown.
- option chain data for available put/call hedges.
- options strategy construction data for long put, collar, put spread collar, and covered call structures.
- option position simulation data and option Greeks data for payoff and sensitivities.
- implied-volatility snapshot data for hedge cost context.

## Workflow

1. Parse ticker, share count, cost basis, purpose, horizon, and hedge budget.
2. Classify the situation: falling knife, new entry, gain protection, event hedge, or normal hold.
3. Pull chain and IV data for the target hedge horizon.
4. Build 1-3 hedge candidates and compare cost, protection floor, upside cap, and Greeks.
5. Recommend the least complex hedge that matches the user's stated goal.

## Output Format

1. **Hedge Verdict**: no urgent hedge, protective put, collar, put spread, or reduce position.
2. **Position Context**: current price, cost basis, P&L, drawdown, event risk.
3. **Hedge Candidates**: legs, cost/credit, floor, cap, breakevens.
4. **Scenario Table**: down 10/20%, flat, up 10%, IV shock.
5. **Data Used**.

## Guardrails

- Do not recommend a collar without explaining upside cap.
- Do not size hedge coverage without share count or explicit assumption.
- State hedge cost as dollars and percent of position value.
