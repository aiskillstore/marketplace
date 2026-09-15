# Convertible And Warrant Lens

## Use When

Use this workflow when the user asks about convertible bonds, warrants, rights, PIPE warrants, SPAC warrants, or other equity-linked hybrid securities.

## LLMQuant Data Needed

Required or future:
- convertible security term data: coupon, maturity, conversion price, conversion ratio, call/put provisions, and rank.
- warrant term data: strike, expiry, exercise style, redemption triggers, and anti-dilution clauses.
- equity price history: underlying price, volatility, liquidity, and drawdowns.
- corporate action data: splits, dividends, mergers, tender offers, and redemptions.
- credit spread and issuer credit context: issuer credit spread, bond price, and default-risk proxy.
- implied-volatility history: implied volatility context for embedded optionality.

Optional:
- SEC filing section retrieval
- company fundamentals data

Freshness:
- Report term sheet date, filing date, quote date, and underlying price timestamp.

Fallback:
- If the term sheet is unavailable, state the missing contract terms and do not value the instrument.

## Workflow

1. Identify security type, issuer, ticker/CUSIP, term sheet fields, and user objective.
2. Pull terms, underlying price, volatility, credit, corporate action, and filing evidence.
3. Decompose the instrument into bond value, option value, dilution, call risk, and liquidity.
4. Run upside/downside scenarios around conversion or exercise thresholds.
5. Explain whether the instrument behaves more like credit, equity, or optionality.

## Output Format

1. **Instrument Summary**
2. **Terms That Matter**
3. **Valuation Drivers**
4. **Scenario Table**
5. **Key Risks**
6. **Data Used**

## Guardrails

- Do not infer conversion, warrant, or redemption terms from memory.
- Do not treat warrants or convertibles as equivalent to common stock.
- Clearly flag dilution, call, liquidity, and credit risks.
