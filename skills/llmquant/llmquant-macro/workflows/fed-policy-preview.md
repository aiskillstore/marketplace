# Fed Policy Preview

## Use When

Use this workflow when the user asks for a Fed, FOMC, central-bank, rate-decision, dot-plot, inflation, labor, or policy-path preview.

## LLMQuant Data Needed

Required:
- policy rate history, latest policy setting, meeting calendar, and central-bank communication context.
- inflation, labor, growth, financial conditions, credit, and liquidity indicators.
- yield curve, front-end rates, real rates, dollar, equity, credit, and volatility market pricing.
- consensus or market-implied expectations when available.

Freshness:
- Report macro observation dates, market price dates, meeting date, and whether data is pre- or post-release.

Fallback:
- If meeting-calendar or market-implied expectations are unavailable, frame the preview around macro evidence and list missing inputs.

## Workflow

1. Identify the policy meeting, geography, and decision horizon.
2. Summarize the policy backdrop: inflation, labor, growth, financial conditions, and market stress.
3. Compare incoming data with central-bank reaction function and prior communication.
4. Map likely decision, guidance, and risk cases to rates, FX, equities, credit, and commodities.
5. Create a watchlist of releases and market levels that would change the policy view.

## Output Format

1. **Policy Base Case**
2. **Data Backdrop**
3. **Market Pricing**
4. **Risk Cases**
5. **Asset Implications**
6. **Data Used**

## Guardrails

- Do not invent central-bank quotes or consensus forecasts.
- Do not present a policy forecast as certainty.
- Distinguish decision probability from market reaction.
