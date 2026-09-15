# Macro To Portfolio Impact

## Use When

Use this workflow when the user asks how macro changes affect a portfolio, watchlist, ETF set, sector book, or multi-asset allocation.

## LLMQuant Data Needed

Required:
- portfolio holdings, weights, benchmarks, sectors, geographies, factors, and currency exposures.
- macro indicators and cross-asset market data relevant to the portfolio.
- ETF holdings and look-through exposures where ETFs are part of the portfolio.
- rates, FX, credit, commodity, equity index, volatility, and liquidity context.

Freshness:
- Report portfolio as-of date, holdings date, macro observation dates, price dates, and stale-data notices.

Fallback:
- If portfolio holdings are unavailable, ask for positions or analyze a user-provided watchlist as a proxy.

## Workflow

1. Define portfolio scope, benchmark, horizon, and macro shock or regime.
2. Map holdings and ETFs to macro sensitivities: rates, inflation, dollar, oil, credit, growth, and volatility.
3. Compare exposures with current macro dashboard evidence.
4. Identify winners, losers, hedges, and concentration risks.
5. Produce action candidates: monitor, rebalance, hedge, or no change, with evidence thresholds.

## Output Format

1. **Portfolio Macro Read**
2. **Exposure Map**
3. **Scenario Impact**
4. **Hedges / Offsets**
5. **Monitors**
6. **Data Used**

## Guardrails

- Do not calculate portfolio impact without holdings, weights, or a stated proxy.
- Do not treat ETF names as exposures without holdings look-through when available.
- Do not make personalized financial advice claims.
