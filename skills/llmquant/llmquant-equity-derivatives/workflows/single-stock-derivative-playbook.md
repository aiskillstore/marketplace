# Single-Stock Derivative Playbook

## Use When

Use this workflow when the user wants to design or evaluate a listed option, structured payoff, hedge, or asymmetric single-stock derivative trade around one underlying equity.

## LLMQuant Data Needed

Required or future:
- equity price history: underlying returns, realized volatility, drawdowns, and technical context.
- option chain data: expirations, strikes, bid/ask, volume, open interest, and IV.
- option Greeks data: delta, gamma, theta, vega, rho, and scenario Greeks.
- implied-volatility history: IV rank, IV percentile, term structure, and skew.
- corporate event data: earnings, investor days, regulatory decisions, and deal events.
- borrow cost and short availability data: hard-to-borrow, short rebate, and availability where relevant.

Optional:
- SEC filing section retrieval
- ticker-level 13F holder data
- company fundamentals data

Freshness:
- Report option quote timestamp, underlying price timestamp, event dates, and IV history window.

Fallback:
- If option chain or Greek data is unavailable, state the missing LLMQuant Data input and do not recommend a contract.

## Workflow

1. Define market view, time horizon, risk budget, max loss, and catalyst path.
2. Pull underlying price, volatility, option chain, Greeks, event, and borrow data.
3. Compare candidate payoffs: outright option, vertical, calendar, diagonal, collar, put spread, or ratio structure.
4. Stress test price, volatility, time decay, and event outcomes.
5. Select the cleanest structure or explain why no derivative is justified.

## Output Format

1. **Derivative View**
2. **Best-Fit Structure**
3. **Payoff And Greeks**
4. **Scenario Table**
5. **Risks**
6. **Data Used**

## Guardrails

- Do not fabricate option quotes, Greeks, or borrow rates.
- Do not ignore bid/ask spread and liquidity.
- Do not present a derivative as suitable for a specific person without knowing mandate and constraints.
