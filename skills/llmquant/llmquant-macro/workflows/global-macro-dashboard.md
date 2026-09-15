# Global Macro Dashboard

## Use When

Use this workflow when the user asks for the current macro regime, a dashboard of key indicators, or a cross-asset macro brief.

## LLMQuant Data Needed

Required:
- macro indicator snapshots and histories for growth, inflation, labor, liquidity, housing, consumption, and sentiment.
- policy rates, yield curves, real-rate context, and market-implied rate expectations when available.
- equity index, sector, commodity, FX, credit, volatility, and crypto market prices.
- release dates, observation dates, and revision information.

Freshness:
- Report latest observation date by series, market price date, release calendar date, and stale-data notices.

Fallback:
- If cross-asset prices or rate expectations are unavailable, produce an indicator-only dashboard and list missing market inputs.

## Workflow

1. Define geography, horizon, investor lens, and asset universe.
2. Pull indicators across growth, inflation, labor, liquidity, and financial conditions.
3. Score each block as accelerating, decelerating, tight, loose, risk-on, or risk-off.
4. Compare the macro regime with market pricing and asset leadership.
5. Summarize the base case, alternate regimes, and indicators that would change the view.

## Output Format

1. **Macro Regime**
2. **Indicator Dashboard**
3. **Cross-Asset Confirmation**
4. **Regime Risks**
5. **Next Releases**
6. **Data Used**

## Guardrails

- Do not mix monthly, weekly, and daily data without naming frequency differences.
- Do not overstate precision from stale or revised macro series.
- Separate nowcast evidence from forecast interpretation.
