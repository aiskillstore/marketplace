# Valuation Methodologies for Earnings Updates

Reference guide for the three valuation methods used in earnings update reports. All data sourced from longbridge CLI.

---

## 1. Discounted Cash Flow (DCF) Analysis

### Data Sources (longbridge CLI)

- `longbridge filing --help` — list and read filings (10-K) for historical financials (revenue, EBIT, D&A, CapEx, debt, cash)
- `longbridge kline --help` — price history for beta calculation
- `longbridge calc-index --help` — current valuation metrics (P/E, P/B, market cap)
- `longbridge static --help` — EPS TTM, shares outstanding, BPS

### 8-Step DCF Process

#### Step 1: Historical Financial Analysis
- Collect 3-5 years from 10-K via `filing detail`
- Calculate historical FCF = EBIT(1-Tax Rate) + D&A - CapEx - ΔNWC
- Analyze growth rates, margins, capital intensity

#### Step 2: Revenue Projections (5 years)
- **Top-down**: TAM → market share → revenue
- **Bottom-up**: Units × price per unit
- **Hybrid**: Combine multiple drivers
- Use management guidance from latest earnings + filing detail

#### Step 3: Operating Expense Projections
- COGS as % of revenue (from historical margins)
- SG&A: semi-fixed, model with scale effects
- R&D: as % of revenue
- D&A: based on CapEx assumptions
- EBIT = Revenue - COGS - Operating Expenses

#### Step 4: Unlevered Free Cash Flow
```
EBIT
× (1 - Tax Rate)
= NOPAT
+ D&A (non-cash, typically 3-6% of revenue)
- CapEx (maintenance 2-4% + growth 2-5% of revenue)
- Increase in NWC (typically -2% to +2% of revenue delta)
= Unlevered Free Cash Flow
```

#### Step 5: Terminal Value
**Perpetuity Growth Method (preferred):**
```
TV = FCF(final year) × (1 + g) / (WACC - g)
```
- g = 2-3% (must NOT exceed long-term GDP growth)
- Sanity check: TV should be 50-70% of total EV

**Exit Multiple Method (alternative):**
```
TV = EBITDA(final year) × Exit Multiple
```
- Exit multiple from current peer trading comps

#### Step 6: WACC Calculation
```
Cost of Equity = Risk-Free Rate + Beta × Equity Risk Premium
  - Risk-Free Rate: 10Y Treasury yield (~4.2%)
  - Beta: regress daily returns from 250-day kline vs market index (SPX for .US, HSI for .HK)
  - ERP: 5.0-6.0%

Cost of Debt = (Interest Expense ÷ Total Debt) × (1 - Tax Rate)
  - Extract from 10-K via filing detail

WACC = (E/V × Ke) + (D/V × Kd)
  - E = Market Cap (from calc-index → total_market_value)
  - D = Net Debt (from filing detail balance sheet)
  - V = E + D
```

**Typical WACC ranges:**
- Large cap, stable: 7-9%
- Growth companies: 9-12%
- High growth/risk: 12-15%

#### Step 7: Discount to Present Value (Mid-Year Convention)
```
PV = Σ [FCFt / (1 + WACC)^(t-0.5)] + [TV / (1 + WACC)^n]
```

#### Step 8: Enterprise → Equity → Price Per Share
```
Enterprise Value = PV of FCFs + PV of Terminal Value
- Net Debt (Total Debt - Cash, from filing detail)
+ Non-operating Assets (if any)
= Equity Value

Price Per Share = Equity Value / Diluted Shares (from longbridge static → total_shares)
```

### DCF Sensitivity Analysis

Always produce a WACC vs. Terminal Growth table:
```
           Terminal Growth Rate
WACC      2.0%    2.5%    3.0%
8.0%      $XX     $XX     $XX
9.0%      $XX     $XX     $XX
10.0%     $XX     $XX     $XX
```

### Common DCF Pitfalls
1. **Double-counting growth**: Don't project high growth without corresponding CapEx/NWC investment
2. **Unrealistic terminal growth**: Must not exceed long-term GDP growth (2-3%)
3. **Ignoring cyclicality**: Normalize earnings for cyclical businesses
4. **Wrong cash flow**: Use unlevered FCF, not net income
5. **Inconsistent assumptions**: Unlevered FCF must pair with WACC (not cost of equity)

---

## 2. Trading Comparables Analysis

### Data Sources (longbridge CLI)

- `longbridge calc-index --help` — valuation metrics for subject and peers (P/E, P/B, market cap)
- `longbridge static --help` — EPS and shares data for subject and peers

### 6-Step Comps Process

#### Step 1: Select Comparable Companies (5-10)
- Same industry/sector
- Similar business model and revenue streams
- Comparable size (market cap, revenue)
- Similar growth profile and margins

#### Step 2: Gather Financial Data
- Market Cap: `calc-index → total_market_value`
- EPS (TTM): `static → eps_ttm`
- P/E: `calc-index → pe`
- P/B: `calc-index → pb`
- Net Debt: from 10-K/10-Q via `filing detail` (Total Debt - Cash)
- Enterprise Value = Market Cap + Net Debt

#### Step 3: Calculate Multiples
- **EV/Revenue**: For high-growth or unprofitable companies
- **EV/EBITDA**: Most common; capital-intensive businesses
- **P/E (NTM)**: Profitable companies with stable cap structure
- **P/B**: Financial institutions

Calculate LTM (historical) and NTM (forward, preferred) where possible.

#### Step 4: Create Comparable Company Table

| Company | Mkt Cap | EV/Revenue | EV/EBITDA | P/E | Rev Growth | EBITDA Margin |
|---------|---------|------------|-----------|-----|------------|---------------|
| Peer A  | $XXB    | X.Xx       | XX.Xx     | XX.Xx | XX%      | XX%           |
| Peer B  | $XXB    | X.Xx       | XX.Xx     | XX.Xx | XX%      | XX%           |
| Peer C  | $XXB    | X.Xx       | XX.Xx     | XX.Xx | XX%      | XX%           |
| **Median** | -    | **X.Xx**   | **XX.Xx** | **XX.Xx** | XX%  | XX%           |

Remove outliers (>2 standard deviations). Use median, not mean.

#### Step 5: Apply Multiples to Subject
```
Implied Price (P/E) = Peer Median P/E × Subject EPS (TTM)
Implied Price (EV/EBITDA) = (Peer Median EV/EBITDA × Subject EBITDA - Net Debt) / Shares
```

#### Step 6: Premium/Discount Adjustment
- **Growth premium**: Higher growth → higher multiple justified
- **Profitability**: Higher margins → higher multiple
- **Size/liquidity**: Larger companies typically trade at premium
- **Market position**: Market leaders → premium
- **Geographic**: Developed vs. emerging markets

---

## 3. Precedent Transactions Analysis

### Data Sources
Longbridge CLI does NOT provide M&A transaction data. Use web search:
- Search: `[industry] M&A transactions [recent years]`
- Sources: press releases, SEC filings (S-4, 8-K, proxy statements)

### 5-Step Process

#### Step 1: Identify Relevant Transactions (5-10)
- Same or similar industry
- Similar size (0.5x to 2x target)
- Recent (last 3-5 years)
- Announced and closed deals

#### Step 2: Gather Transaction Details
- Transaction date, price, and structure
- Target's financials at time of deal
- Strategic rationale and synergies
- Control premium paid

#### Step 3: Calculate Transaction Multiples
```
Transaction EV = Equity Purchase Price + Assumed Debt - Cash Acquired
EV/Revenue (LTM) = Transaction EV / Target's LTM Revenue
EV/EBITDA (LTM) = Transaction EV / Target's LTM EBITDA

Control Premium = (Offer Price - Unaffected Price) / Unaffected Price
Typical range: 20-40%
```

#### Step 4: Create Precedent Transactions Table

| Date | Target | Acquirer | Deal Value | EV/Revenue | EV/EBITDA | Premium |
|------|--------|----------|------------|------------|-----------|---------|
| Q1'26 | CompX | BuyerA | $X.XB | X.Xx | XX.Xx | XX% |
| Q3'25 | CompY | BuyerB | $X.XB | X.Xx | XX.Xx | XX% |
| **Median** | - | - | - | **X.Xx** | **XX.Xx** | **XX%** |

#### Step 5: Apply to Subject
- Precedent multiples typically HIGHER than trading comps (include control premium)
- Weight recent transactions more heavily
- Adjust for market conditions at time of deal vs. current

---

## Valuation Reconciliation

### Dynamic Weighting

Do NOT use fixed weights. Adjust based on context:

| Factor | Higher DCF Weight | Higher Comps Weight | Include Precedent Trans |
|--------|-------------------|--------------------|-----------------------|
| Forecast confidence | High | Low | — |
| Market conditions | Abnormal/dislocated | Normal/stable | — |
| Company maturity | Growth stage | Mature/stable | — |
| M&A likelihood | Low | — | High (industry consolidating) |

**Default ranges:**
- **DCF**: 40-60%
- **Trading Comps**: 25-40%
- **Precedent Transactions**: 0-25% (only include when M&A transactions are relevant and available)

If no precedent transaction data available (common), redistribute weight to DCF and Comps only.

### Bear/Base/Bull Valuation Range

**Always present a valuation range, not a single point estimate.**

Run each method under three scenarios:

| Scenario | DCF Assumptions | Comps Assumptions | Result |
|----------|----------------|-------------------|--------|
| **Bear** | Conservative growth, higher WACC (+50bps), lower terminal growth | Apply 25th percentile peer multiple | Low end |
| **Base** | Most likely growth from updated estimates | Apply median peer multiple | Mid point |
| **Bull** | Optimistic growth, lower WACC (-50bps), higher terminal growth | Apply 75th percentile peer multiple | High end |

**Output format:**
```
VALUATION SUMMARY
─────────────────────────────────────────────────────────
                    Bear Case    Base Case    Bull Case
DCF (XX%)           $XX          $XX          $XX
Trading Comps (XX%) $XX          $XX          $XX
Precedent (XX%)     $XX          $XX          $XX
─────────────────────────────────────────────────────────
Weighted Average     $XX          $XX          $XX

Price Target: $XX (Base Case weighted average)
Current Price: $XX (from longbridge quote)
Implied Upside: +XX%
```

### Sanity Checks

1. **Historical multiples**: Current valuation in line with company's own history?
2. **Peer comparison**: Premium/discount to peers justified?
3. **Implied growth**: What growth rate is the market pricing in? Is it realistic?
4. **Terminal value**: 50-70% of total EV (if >75%, re-examine assumptions)
5. **DCF vs. market**: Implied price within ±30% of current price (if not, explain divergence)
6. **Method agreement**: All methods should directionally agree — major outlier needs explanation