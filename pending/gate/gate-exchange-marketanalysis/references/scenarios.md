# gate-exchange-marketanalysis — Scenarios & MCP Call Specs

This document defines the **MCP call order, parameters, required fields, and output format** for each scenario. Implementations must call Gate MCP in the order specified under each Case and produce reports according to the templates below.

**MCP tool names (Gate MCP):** Spot market data use `get_spot_order_book`, `get_spot_candlesticks`, `get_spot_tickers`, `get_spot_trades`. Futures market data use `get_futures_contract`, `get_futures_order_book`, `get_futures_candlesticks`, `get_futures_tickers`, `get_futures_trades`. Futures funding/liquidation/premium use `get_futures_funding_rate`, `list_futures_liq_orders`, `get_futures_premium_index`. Call these exact tool names when invoking Gate MCP.

| Case | Scenario | Core MCP Call Order |
|------|----------|---------------------|
| 1 | Liquidity analysis | get_spot_order_book → get_spot_candlesticks → get_spot_tickers (use futures APIs when user says perpetual/contract) |
| 2 | Momentum (buy vs sell) | get_spot_trades → get_spot_tickers → get_spot_candlesticks → get_spot_order_book → get_futures_funding_rate (futures APIs when contract) |
| 3 | Liquidation monitoring | list_futures_liq_orders → get_futures_candlesticks → get_futures_tickers |
| 4 | Funding rate arbitrage | get_futures_tickers → get_futures_funding_rate → get_spot_tickers → get_spot_order_book |
| 5 | Basis (spot vs futures) | get_spot_tickers(spot) → get_futures_tickers → get_futures_premium_index |
| 6 | Manipulation risk | Spot: get_spot_order_book → get_spot_tickers → get_spot_trades. When user says perpetual/contract: get_futures_order_book → get_futures_tickers → get_futures_trades |
| 7 | Order book explainer | get_spot_order_book(limit=10) → get_spot_tickers |
| 8 | Slippage simulation | Spot: get_spot_order_book → get_spot_tickers. Futures: get_futures_contract → get_futures_order_book → get_futures_tickers |
| 9 | K-line breakout / support–resistance | get_spot_candlesticks → get_spot_tickers (spot); get_futures_candlesticks → get_futures_tickers (futures) |
| 10 | Liquidity + weekend vs weekday | get_spot_order_book → get_spot_candlesticks → get_spot_tickers (spot); get_futures_contract → get_futures_order_book → get_futures_candlesticks → get_futures_tickers (futures) |

---

## Case 1: Liquidity Analysis

### MCP Call Spec (document-aligned)

For liquidity analysis, **call Gate MCP in this order** and extract the listed fields; output must follow the Report Template below.

| Step | MCP Tool | Parameters | Required Fields |
|------|----------|------------|----------------|
| 1 | `get_spot_order_book` (spot) | `currency_pair={BASE}_USDT`, `limit=20` | Number of ask/bid levels; top 10 bid/ask depth totals; bid1/ask1 (for spread and slippage) |
| 2 | `get_spot_candlesticks` (spot) | `currency_pair={BASE}_USDT`, `interval=1d`, `limit=30` | Last 30 days volume (for 30d avg); latest candle for 24h volume reference |
| 3 | `get_spot_tickers` (spot) | `currency_pair={BASE}_USDT` | `last`; `quoteVolume` 24h (USDT); `changePercentage` 24h; `high24h`/`low24h` |
| 4 (optional) | `get_spot_trades` (spot) | `currency_pair={BASE}_USDT`, `limit=100` | Recent trade size distribution for "recent flow" and participation |

**Calculation & judgment** (aligned with SKILL):

- **API choice**: Use futures APIs (e.g. get_futures_order_book) when user says "perpetual" or "contract"; otherwise spot.
- **Slippage** = `2×(ask1−bid1)/(bid1+ask1)×100%`; if > 0.5% → flag "high slippage risk".
- **Depth**: asks/bids depth < 10 levels → flag "low liquidity".
- **24h volume** < 30-day volume average → flag "cold pair".
- **Liquidity rating**: Combine above into 1–5 ⭐.

**Output**: Must include a "Core metrics" table (order book depth, 24h volume, 30d avg volume, bid-ask spread, slippage + status), "Assessment" (liquidity rating x/5 ⭐), and short "Recommendation".

---

### Scenario 1.1: Spot liquidity query

**Context**: User wants to know ETH spot trading conditions.

**Prompt examples**:
- "How is ETH liquidity?"

**Expected behavior**:
1. Call in order per **MCP Call Spec**: `get_spot_order_book` → `get_spot_candlesticks` → `get_spot_tickers` (optional `get_spot_trades`).
2. From order book: level count, top 10 depth, bid1/ask1.
3. From candlesticks: 30d avg volume, 24h volume.
4. From tickers: last, 24h quote volume, change.
5. Compute slippage; apply document logic for status and rating.
6. Output core metrics table + assessment + recommendation per Report Template.

**Output**:
```markdown
## ETH Liquidity Analysis

### Core metrics

| Metric | Value | Status |
|--------|-------|--------|
| Order book depth | 20 levels | OK |
| 24h volume | $485M | Active |
| 30d avg volume | $320M | - |
| Bid-ask spread | 0.02% | Excellent |
| Slippage risk | 0.03% | Very low |

### Assessment

**Liquidity rating**: 5/5 ⭐

ETH liquidity is excellent, suitable for large size.
```

---

### Scenario 1.2: Futures liquidity query

**Context**: User asks about perpetual/contract depth.

**Prompt examples**:
- "How is BTC perpetual depth?"

**Expected behavior**:
1. Detect "perpetual/contract" and use **futures** MCP: `get_futures_order_book` (`settle=usdt`, `contract=BTC_USDT`, `limit=20`) → optional `get_futures_tickers`, `get_futures_candlesticks`(1d, 30).
2. Extract level count, top 10 depth, bid1/ask1; compute slippage.
3. Output core metrics table + liquidity rating per liquidity criteria.

**Output**:
```markdown
## BTC_USDT Perpetual — Liquidity Analysis

| Metric | Value | Status |
|--------|-------|--------|
| Order book depth | 50 levels | Excellent |
| Slippage risk | 0.01% | Very low |

Liquidity rating: 5/5 ⭐
```

---

### Scenario 1.3: Low-liquidity / cold pair warning

**Context**: User queries a low-cap or illiquid pair.

**Prompt examples**:
- "How is XYZ liquidity?"

**Expected behavior**:
1. Still follow **Case 1 MCP Call Spec**: `get_spot_order_book` → `get_spot_candlesticks` → `get_spot_tickers`.
2. If depth < 10 levels, or 24h volume < 30d avg, or slippage > 0.5%, mark 🔴 in core metrics and output risk note + low liquidity rating.

**Output**:
```markdown
## XYZ Liquidity Analysis

### Risk notice

| Metric | Value | Status |
|--------|-------|--------|
| Order book depth | 5 levels | Insufficient depth |
| 24h volume | $15K | Cold pair |
| Slippage risk | 2.3% | High |

**Liquidity rating**: 1/5 ⭐

⚠️ This pair has poor liquidity; large orders will incur significant slippage.
```

---

## Case 2: Momentum (buy vs sell)

### MCP Call Spec (document-aligned)

**Trigger**: "Is BTC more long or short in 24h, and is it sustainable?" For momentum analysis, **call in this order**; use futures APIs when user asks about contract.

| Step | MCP Tool | Parameters | Required Fields |
|------|----------|------------|----------------|
| 1 | `get_spot_trades` (spot) / `get_futures_trades` (futures) | `currency_pair` or `contract`+`settle`, `limit=1000` | Buy/sell volume; buy share = buy_volume / total_volume |
| 2 | `get_spot_tickers` (spot) / `get_futures_tickers` (futures) | Same pair | 24h volume, 24h change |
| 3 | `get_spot_candlesticks` (spot) / `get_futures_candlesticks` (futures) | `interval=1d`, `limit=30` | 30-day average volume |
| 4 | `get_spot_order_book` (spot) / `get_futures_order_book` (futures) | `limit=20` | Top 10 bid/ask depth for long/short balance |
| 5 | `get_futures_funding_rate` or equivalent | When contract | Funding rate; positive → long bias, negative → short bias |

**Calculation & judgment** (aligned with SKILL):

- **Buy share > 70%** → "buy-side strong"; sell share > 70% → "sell-side strong".
- **24h volume > 30d avg** → "active".
- **Funding rate** sign + **order book top 10** balance → overall bias and sustainability.

**Output**: Must include "Buy/sell forces" table, momentum direction, sustainability, and short analysis.

---

### Scenario 2.1: Basic momentum query

**Context**: User wants to judge short-term long vs short strength.

**Prompt examples**:
- "Is BTC more long or short in 24h, and is it sustainable?"

**Expected behavior**:
1. Call per **MCP Call Spec**: `get_spot_trades`/`get_futures_trades` → `get_spot_tickers`/`get_futures_tickers` → `get_spot_candlesticks`/`get_futures_candlesticks` → `get_spot_order_book`/`get_futures_order_book` → `get_futures_funding_rate` (futures when contract).
2. From trades: buy/sell volume, buy share; tickers: 24h volume and change; candlesticks: 30d avg; order book: top 10 long/short depth; funding rate for bias.
3. Apply logic (buy > 70% → buy-side strong; 24h > 30d avg → active; funding + book → direction and sustainability).
4. Output buy/sell table + direction + analysis per Report Template.

**Output**:
```markdown
## BTC Momentum Analysis

### Buy/sell forces

| Metric | Value |
|--------|-------|
| Buy share | 65% |
| Sell share | 35% |
| 24h volume | $2.1B |
| 30d avg volume | $1.8B |
| Activity | Active |

### Conclusion

**Momentum direction**: Buy-side slightly ahead

Buy share 65% but below 70% "strong" threshold; currently long-leaning but not one-sided. Volume above 30d avg; activity is rising.
```

---

### Scenario 2.2: One-sided strong buy

**Context**: User asks whether buy side is strong.

**Prompt examples**:
- "Is ETH buy side strong?"

**Expected behavior**:
1. Call per **MCP Call Spec**: `get_spot_trades`(ETH_USDT) → `get_spot_tickers` → `get_spot_candlesticks`.
2. Compute buy/sell share; if buy > 70% mark as buy-side strong.
3. Output buy/sell table + direction (buy-side strong).

**Output**:
```markdown
## ETH Momentum Analysis

### Buy/sell forces

| Metric | Value |
|--------|-------|
| Buy share | 78% |
| Sell share | 22% |

### Conclusion

**Momentum direction**: Buy-side strong

Buy share 78%, well above 70% threshold; clear long-dominated tape. With volume expansion, trend may extend.
```

---

### Scenario 2.3: Futures momentum query

**Context**: User explicitly asks about contract momentum.

**Prompt examples**:
- "BTC contract momentum"

**Expected behavior**:
1. Detect "contract" and use **futures** MCP: `get_futures_trades` (`settle=usdt`, `contract=BTC_USDT`) → `get_futures_tickers` → `get_futures_candlesticks`.
2. Extract buy/sell share, 24h volume, 30d avg per MCP Call Spec; same output structure, data from futures.

---

## Case 3: Liquidation Monitoring

### MCP Call Spec (document-aligned)

**Trigger**: "Recent liquidations?", "Which coins liquidated most?" For liquidation monitoring, **call in this order** (futures only).

| Step | MCP Tool | Parameters | Required Fields |
|------|----------|------------|----------------|
| 1 | `list_futures_liq_orders` | `settle=usdt`, time range (last 1h; optional 24h for daily baseline) | Liq volume by contract; long (size>0) / short (size<0); 1h total liq |
| 2 | `get_futures_candlesticks` | `settle=usdt`, `contract`, `interval=5m`, `limit=12` | Price during liq window, current price, recovery |
| 3 | `get_futures_tickers` | `settle=usdt` (or specific contract) | Current price, 24h change |

**Calculation & judgment** (aligned with SKILL):

- **1h liq > 3× daily avg** → flag "anomaly".
- **One-sided liq > 80%** (long or short) → flag "long squeeze" or "short squeeze".
- **Price recovered** (vs wick low/high) → flag "wick / spike".

**Output**: Must include "Market overview" table, "Anomaly contracts" table, and wick analysis when relevant (low, current price, recovery).

---

### Scenario 3.1: Market-wide liquidation overview

**Context**: User wants a market-wide liquidation view.

**Prompt examples**:
- "Recent liquidations?"

**Expected behavior**:
1. Call per **MCP Call Spec**: `list_futures_liq_orders` → `get_futures_candlesticks` → `get_futures_tickers`.
2. Aggregate liq by contract; long/short share; if daily baseline available, compute 1h vs daily multiple.
3. Apply logic: 1h liq > 3× daily → anomaly; one-sided > 80% → long/short squeeze; price recovered → wick.
4. Output market overview table + anomaly contracts table.

**Output**:
```markdown
## Liquidation Monitoring

**Time**: 2026-03-05 15:30

### Market overview

| Metric | Value |
|--------|-------|
| 1h total liq | $45M |
| Long liq | $38M (84%) |
| Short liq | $7M (16%) |

### Anomaly contracts

| Contract | Liq volume | Multiple | Type |
|----------|------------|----------|------|
| ETH_USDT | $18M | 4.2x | Long squeeze |
| SOL_USDT | $8M | 3.5x | Long squeeze |

Long liq 84%; current move is squeezing long leverage.
```

---

### Scenario 3.2: Wick / spike detection

**Context**: User suspects a wick/spike (e.g. BTC).

**Prompt examples**:
- "Did BTC just wick?"

**Expected behavior**:
1. Call per **MCP Call Spec**: `list_futures_liq_orders`(1h, optional filter contract=BTC_USDT) → `get_futures_candlesticks`(BTC_USDT, 5m, 12) → `get_futures_tickers`.
2. From liq: long/short share; from candlesticks: low, current price; recovery = (current − low) / (pre-spike high − low) or similar.
3. If long-dominated liq and recovery > 80%, output wick analysis (liq table + low/current/recovery + wick conclusion).

**Output**:
```markdown
## BTC Wick Analysis

### Liquidation data

| Metric | Value |
|--------|-------|
| 1h liq | $25M |
| Long liq | $23M (92%) |
| Low | $62,100 |
| Current | $63,800 |
| Recovery | 85% |

### Conclusion

**Type**: Wick / spike

- Long-dominated liq (92%)
- Price recovered 85%
- Typical short wick squeezing long leverage
```

---

## Case 4: Funding Rate Arbitrage Scan

### MCP Call Spec (document-aligned)

**Trigger**: "Any arbitrage opportunities?", "Which coins have extreme funding?" For arbitrage scan, **call in this order**.

| Step | MCP Tool | Parameters | Required Fields |
|------|----------|------------|----------------|
| 1 | `get_futures_tickers` | `settle=usdt` | All contracts' funding_rate, 24h volume |
| 2 | `get_futures_funding_rate` or equivalent | For candidates / full market | Rate details |
| 3 | `get_spot_tickers` (spot) | Per candidate `currency_pair={BASE}_USDT` | Spot last; spot–futures spread |
| 4 | `get_spot_order_book` (spot) | For top candidates `currency_pair`, `limit=20` | Top 10 depth; exclude if depth too thin |

**Calculation & judgment** (aligned with SKILL):

- **|rate| > 0.05% and 24h vol > $10M** → candidate.
- **Spot–futures spread > 0.2%** → bonus.
- **Book depth too thin** → exclude.

**Output**: Must include "Arbitrage opportunities" table, strategy note (long basis / short basis), and risk disclaimer.

---

### Scenario 4.1: Market-wide arbitrage scan

**Context**: User wants to find funding arbitrage opportunities.

**Prompt examples**:
- "Any arbitrage opportunities?"

**Expected behavior**:
1. Call per **MCP Call Spec**: `get_futures_tickers` → `get_futures_funding_rate` → `get_spot_tickers`(candidates) → `get_spot_order_book`(top candidates).
2. Logic: |rate|>0.05% and 24h vol>$10M → candidate; spot–futures spread>0.2% → bonus; thin depth → exclude.
3. Output arbitrage table + strategy + risk note.

**Output**:
```markdown
## Funding Rate Arbitrage Scan

**Time**: 2026-03-05 15:30

### Top 5 opportunities

| Contract | Rate | Ann. | Basis | Depth | Strategy |
|----------|------|------|-------|-------|----------|
| DOGE_USDT | +0.15% | 164% | +0.3% | OK | Long basis |
| PEPE_USDT | +0.12% | 131% | +0.2% | Fair | Long basis |
| WIF_USDT | -0.10% | 109% | -0.1% | OK | Short basis |

### Strategy

**Long basis**: Short futures + long spot  
**Short basis**: Long futures + short spot (borrow)

⚠️ Risk: Actual PnL must account for fees and execution.
```

---

### Scenario 4.2: Extreme funding query

**Context**: User wants coins with extreme funding rates.

**Prompt examples**:
- "Which coins have extreme funding?"

**Expected behavior**:
1. Call `get_futures_tickers`(settle=usdt); filter |funding_rate| > 0.001 (0.1%).
2. Sort by |rate|; label severity (e.g. extreme positive, high negative).
3. Output "Extreme funding" table (contract, rate, status).

**Output**:
```markdown
## Extreme Funding

| Contract | Rate | Status |
|----------|------|--------|
| DOGE_USDT | +0.18% | Extreme positive |
| SHIB_USDT | +0.15% | High positive |
| WIF_USDT | -0.12% | High negative |

Positive rate > 0.1% means high cost to long; may signal short-term pullback risk.
```

---

## Case 5: Basis (Spot vs Futures) Monitoring

### MCP Call Spec (document-aligned)

**Trigger**: "What is the basis?", "Spot–futures spread." For basis monitoring, **call in this order**.

| Step | MCP Tool | Parameters | Required Fields |
|------|----------|------------|----------------|
| 1 | `get_spot_tickers` (spot) | `currency_pair={BASE}_USDT` | Spot `last` |
| 2 | `get_futures_tickers` | `settle=usdt`, optional `contract={BASE}_USDT` | Futures price, mark_price, index_price |
| 3 | `get_futures_premium_index` or equivalent | `settle=usdt`, `contract={BASE}_USDT` | premium_index; if history available, for mean and deviation |

**Calculation & judgment** (aligned with SKILL):

- **Current basis vs historical mean** (deviation).
- **Basis widening / narrowing** (widening → sentiment heating; narrowing → mean reversion).

**Output**: Must include "Basis data" table, current vs historical mean, widening/narrowing conclusion, and short recommendation.

---

### Scenario 5.1: Single-coin basis query

**Context**: User asks for BTC spot–futures spread.

**Prompt examples**:
- "What is BTC basis?"

**Expected behavior**:
1. Call per **MCP Call Spec**: `get_spot_tickers`(BTC_USDT) → `get_futures_tickers`(usdt, BTC_USDT) → optional `get_futures_premium_index`.
2. Compute basis, basis rate; if premium history available, historical mean.
3. Output basis table + analysis + recommendation per Report Template.

**Output**:
```markdown
## BTC Spot–Futures Basis

### Basis data

| Metric | Value |
|--------|-------|
| Spot | $63,500 |
| Futures | $63,700 |
| Basis | +$200 |
| Basis rate | +0.31% |
| Historical mean | +0.15% |

### Analysis

Current basis rate 0.31%, above historical mean 0.15%; **elevated positive basis**. Possible reasons: strong bullish sentiment; suitable for long-basis arbitrage.
```

---

### Scenario 5.2: Negative basis warning

**Context**: User queries ETH basis.

**Prompt examples**:
- "ETH spot–futures spread"

**Expected behavior**:
1. Call per **MCP Call Spec**: `get_spot_tickers`(ETH_USDT) → `get_futures_tickers`(usdt, ETH_USDT) → optional `get_futures_premium_index`(settle=usdt, contract=ETH_USDT).
2. Compute basis and basis rate; if premium index available, use for context; if negative, output basis table + ⚠️ negative basis warning (bearish / short crowding).

**Output**:
```markdown
## ETH Spot–Futures Basis

### Basis data

| Metric | Value |
|--------|-------|
| Spot | $3,200 |
| Futures | $3,185 |
| Basis | -$15 |
| Basis rate | -0.47% |

### Notice

Currently **negative basis** (futures below spot), which often indicates:
- Bearish sentiment
- Or short crowding
```

---

## Case 6: Manipulation Risk Analysis (Is the coin easy to manipulate?)

### MCP Call Spec (document-aligned)

**Trigger**: "How is this coin’s depth vs volume?" / "Is it easy to manipulate?"

**API choice**: When user mentions **perpetual, contract, futures**, use **futures** tools; otherwise use **spot** tools.

| Step | MCP Tool (spot) | MCP Tool (futures, when user says perpetual/contract) | Parameters | Required Fields |
|------|-----------------|--------------------------------------------------------|------------|----------------|
| 1 | `get_spot_order_book` | `get_futures_order_book` | Spot: `currency_pair={BASE}_USDT`. Futures: `settle=usdt`, `contract={BASE}_USDT`. `limit=20` | Top 10 bid depth sum, top 10 ask depth sum |
| 2 | `get_spot_tickers` | `get_futures_tickers` | Same pair / contract + settle | 24h quote volume (quoteVolume) |
| 3 | `get_spot_trades` | `get_futures_trades` or equivalent | Same pair; `limit=500` (or 24h window) | Trade size distribution; consecutive same-direction large orders |

**Calculation & judgment** (aligned with SKILL):

- **Top 10 depth total / 24h volume < 0.5%** → "thin depth".
- **24h trades have consecutive same-direction large orders** → "possible manipulation".

**Output**: Must include "Depth analysis" table (top 10 depth, 24h volume, depth ratio, assessment), "Large order" summary, and "Manipulation risk" conclusion.

---

### Scenario 6.1: Manipulation risk query

**Context**: User is concerned about small-cap coin manipulation.

**Prompt examples**:
- "Is PEPE easy to manipulate?"

**Expected behavior**:
1. Call per **MCP Call Spec**: `get_spot_order_book`(PEPE_USDT) → `get_spot_tickers` → `get_spot_trades`(limit=500).
2. Compute depth ratio; from trades identify large and consecutive same-side.
3. Output depth table + large order summary + risk conclusion per Report Template.

**Output**:
```markdown
## PEPE Manipulation Risk

### Depth analysis

| Metric | Value | Assessment |
|--------|-------|------------|
| Top 10 depth | $850K | - |
| 24h volume | $320M | - |
| Depth ratio | 0.27% | Thin |

### Large orders

In last 500 trades:
- 3 consecutive large buys (15% of sample)
- Max single: $125K

### Risk conclusion

**Manipulation risk**: High

- Depth ratio < 0.5% implies small size can move price
- Consecutive same-side large orders suggest possible manipulation
```

---

### Scenario 6.2: Healthy pair (low risk)

**Context**: User queries a major pair (e.g. BTC).

**Prompt examples**:
- "How is BTC depth vs volume?"

**Expected behavior**:
1. Call per **MCP Call Spec**: `get_spot_order_book`(BTC_USDT) → `get_spot_tickers` → optional `get_spot_trades`.
2. Compute depth ratio; if > 2% assess as good depth, low manipulation risk.
3. Output depth table + risk conclusion (low).

**Output**:
```markdown
## BTC Manipulation Risk

### Depth analysis

| Metric | Value | Assessment |
|--------|-------|------------|
| Top 10 depth | $85M | - |
| 24h volume | $2.1B | - |
| Depth ratio | 4.0% | Good |

### Risk conclusion

**Manipulation risk**: Low

BTC has ample depth; large size would be needed to move price; manipulation risk is low.
```

---

### Scenario 6.3: Futures manipulation risk (perpetual/contract)

**Context**: User asks about manipulation for a **perpetual/contract** (e.g. "BTC contract easy to manipulate?").

**Prompt examples**:
- "Is BTC contract easy to manipulate?"
- "How is ETH perpetual depth vs volume?"

**Expected behavior**:
1. Detect "perpetual" or "contract" and use **futures** MCP: `get_futures_contract`(settle=usdt, contract=BTC_USDT) → `get_futures_order_book`(settle=usdt, contract=BTC_USDT, limit=20) → `get_futures_tickers` → `get_futures_trades` (or equivalent, limit=500).
2. Use `quanto_multiplier` from contract to convert order book size to notional; extract top 10 depth total and 24h volume; from futures trades detect consecutive same-direction large orders.
3. Apply same judgment: depth ratio < 0.5% → thin; consecutive same-side large → possible manipulation.
4. Output depth analysis table + large order summary + manipulation risk conclusion (same structure as 6.1/6.2, data from futures).

**Output**: Same structure as Scenario 6.1 or 6.2; data source is futures contract, order book, tickers, and trades.

---

## Case 7: Order Book Explainer

### MCP Call Spec (document-aligned)

**Trigger**: "Explain the order book", "What is the order book?", "How to read the book?" For order book explainer, **call in this order**.

| Step | MCP Tool | Parameters | Required Fields |
|------|----------|------------|----------------|
| 1 | `get_spot_order_book` (spot) / `get_futures_order_book` (futures) | `currency_pair` or `contract`+`settle`, `limit=10` | bids/asks sample (price and size per level) |
| 2 | `get_spot_tickers` (spot) / `get_futures_tickers` (futures) | Same pair | `last` for spread explanation |

**Interpretation** (aligned with SKILL):

- Show sample bids/asks (levels and sizes).
- Explain **spread** (bid–ask) using ticker last.
- Fast moves + deep depth → good liquidity.

**Output**: Must include order book tutorial, live order book example, key metrics (best bid, best ask, spread), and short takeaways.

---

### Scenario 7.1: Beginner explainer

**Context**: User is new and needs a tutorial.

**Prompt examples**:
- "Explain the order book"

**Expected behavior**:
1. Call per **MCP Call Spec**: `get_spot_order_book` (e.g. BTC_USDT, limit=10) → `get_spot_tickers`.
2. Fill order book table and key metrics with live data; add tutorial text (Bids/Asks/Spread, what spread means).
3. Output tutorial + live example + takeaways.

**Output**:
```markdown
## Order Book Explained

### What is the order book

The order book is the exchange’s "list of orders":

- **Asks**: Sell orders, sorted by price low to high
- **Bids**: Buy orders, sorted by price high to low
- **Spread**: Gap between best ask and best bid

### Live example (BTC)

**Asks** ↑
| Price | Size | Cumulative |
|-------|------|------------|
| 63,550 | 2.5 | 7.8 |
| 63,530 | 1.8 | 5.3 |
| 63,510 | 3.5 | 3.5 | ← Best ask

------- Last: 63,505 -------

**Bids** ↓
| Price | Size | Cumulative |
|-------|------|------------|
| 63,500 | 4.2 | 4.2 | ← Best bid
| 63,480 | 2.1 | 6.3 |
| 63,460 | 3.0 | 9.3 |

### Takeaways

- **Spread** = 63,510 − 63,500 = $10 (0.016%)
- Tighter spread → better liquidity
- Deeper book → less impact from large orders
```

---

### Scenario 7.2: Specific pair order book

**Context**: User wants to see a specific pair’s book (e.g. ETH).

**Prompt examples**:
- "Show ETH order book"

**Expected behavior**:
1. Call per **MCP Call Spec**: `get_spot_order_book`(ETH_USDT, limit=10) → `get_spot_tickers`(ETH_USDT).
2. Output ETH live table (asks/bids, price, size, cumulative) + last + spread and short comment (e.g. liquidity, support).

**Output**:
```markdown
## ETH Order Book

**Asks**
| Price | Size | Cumulative |
|-------|------|------------|
| 3,205 | 45 | 120 |
| 3,203 | 32 | 75 |
| 3,201 | 43 | 43 | ← Best ask

--- Last: 3,200 ---

**Bids**
| Price | Size | Cumulative |
|-------|------|------------|
| 3,200 | 55 | 55 | ← Best bid
| 3,198 | 28 | 83 |
| 3,196 | 40 | 123 |

Spread: $1 (0.03%) — liquidity good. Bid depth heavier than asks; support below is stronger.
```

---

## Case 8: Slippage Simulation

### MCP Call Spec (document-aligned)

**Trigger**: "slippage simulation", "market buy $X slippage", "how much slippage if I market buy $10K?", e.g. "ADA_USDT slippage simulation: if I market buy $10K, how much slippage?"

**Required inputs** (both must be provided; do not use defaults):

- **Currency pair** (e.g. `ETH_USDT`, `ADA_USDT`, `BTC_USDT`): identifies which order book and ticker to use. **If the user does not specify a pair**, prompt them to provide one (e.g. "Please specify a pair, e.g. ETH_USDT, ADA_USDT.").
- **Quote amount** (e.g. $10,000 USDT): the notional to simulate for the market buy. **If the user does not specify an amount**, prompt them to provide one (e.g. "Please specify the quote amount, e.g. $10K USDT."). **Do not assume a default** (e.g. do not default to $10K).

**API choice**: When user mentions **perpetual, contract, futures**, use **futures** tools; otherwise use **spot** tools.

| Step | MCP Tool (spot) | MCP Tool (futures, when user says perpetual/contract) | Parameters | Required Fields |
|------|-----------------|--------------------------------------------------------|------------|----------------|
| 1 | `get_spot_order_book` | `get_futures_contract` | Spot: `currency_pair={BASE}_USDT`, `limit=50`. Futures: `settle=usdt`, `contract={BASE}_USDT` | Spot: asks (price, size), bid1/ask1. Futures: `quanto_multiplier` (contract size) for ladder notional |
| 2 | — | `get_futures_order_book` | Futures: `settle=usdt`, `contract={BASE}_USDT`, `limit=50` | Asks (price, size) for ladder walk; bid1/ask1 |
| 3 | `get_spot_tickers` | `get_futures_tickers` | Same pair / contract + settle | `last`, `lowestAsk` (or use ask1 from order book) |

**Calculation & judgment** (aligned with SKILL):

- **Order book + latest price**: Use current order book and ticker last / best ask.
- **Simulate market buy for quote amount Q (e.g. $10K USDT)**: Walk the **ask** ladder from best ask upward; at each level fill `amount_i` at `price_i` until cumulative quote volume `sum(price_i × amount_i)` ≥ Q (last level may be partially filled so total cost ≈ Q).
- **Outputs**: Total base filled, volume spent, **volume-weighted average execution price** = total_cost / total_base.
- **Slippage = deviation from best ask**:
  - **Price deviation**: `avg_price − ask1` (points in price).
  - **Relative deviation**: `(avg_price − ask1) / ask1 × 100%`; optionally in bps: `× 10000`.

**Output**: Must include "Simulation inputs" (pair, quote amount, ask1), "Fill summary" (total base, avg price), "Slippage" (vs ask1: points and %), and short "Conclusion".

---

### Scenario 8.1: Spot slippage simulation (e.g. ADA_USDT market buy $10K)

**Context**: User wants to know how much slippage to expect for a market buy of a given USDT amount on spot.

**Prompt examples**:
- "ADA_USDT slippage simulation: if I market buy $10K, how much slippage?"
- "How much slippage for a $10K market buy in ETH?"

**Expected behavior**:
1. **Require pair and amount**: If the user did not specify a **currency pair** (e.g. ADA_USDT, ETH_USDT), prompt them to provide one; do not run the simulation or assume a default pair. If the user did not specify a **quote amount** (e.g. $10,000 USDT), prompt them to provide one; do not assume a default (e.g. do not default to $10K).
2. Parse pair (e.g. ADA_USDT, ETH_USDT) and quote amount (e.g. $10,000 USDT) from the user.
3. Call per **MCP Call Spec**: `get_spot_order_book`(pair, limit=50) → `get_spot_tickers`(pair).
4. Walk ask ladder until cumulative quote ≥ quote amount; compute total base filled, total cost, volume-weighted avg price.
5. ask1 = first ask price from order book (or ticker lowestAsk). Slippage = avg_price − ask1 (points) and (avg_price − ask1)/ask1 × 100 (%).
6. Output simulation inputs table + fill summary + slippage vs ask1 + conclusion.

**Output**:
```markdown
## ADA_USDT Slippage Simulation (Spot Market Buy)

### Simulation inputs

| Item | Value |
|------|--------|
| Pair | ADA_USDT (spot) |
| Quote amount | $10,000 USDT |
| Best ask | 0.xxxx USDT |

### Fill summary

| Metric | Value |
|--------|--------|
| Total base filled | x,xxx ADA |
| Total cost | ~$10,000 USDT |
| Volume-weighted avg price | 0.xxxx USDT |

### Slippage vs best ask

| Metric | Value |
|--------|--------|
| Price deviation (points) | +0.xxxx USDT |
| Relative deviation | +x.xx% |

### Conclusion

For a $10K market buy, slippage vs best ask is about x.xx% (about x.xxxx points). Slippage can be higher when depth is thin; consider splitting large orders or using limit orders.
```

---

### Scenario 8.2: Futures slippage simulation (perpetual/contract)

**Context**: User asks slippage for a **perpetual/contract** market buy (long) of a given USDT amount.

**Prompt examples**:
- "BTC perpetual market long $50K, how much slippage?"

**Expected behavior**:
1. **Require pair**: If no contract/pair is specified (e.g. BTC_USDT), prompt the user to provide one; do not assume a default.
2. Detect "perpetual" or "contract" and use **futures** MCP: `get_futures_contract`(settle=usdt, contract={pair}) → `get_futures_order_book`(settle=usdt, contract={pair}, limit=50) → `get_futures_tickers`(settle, contract).
3. Use `quanto_multiplier` from contract to convert order book size (contracts) to base notional; same ladder logic on **asks** for quote amount; compute avg price, slippage = avg_price − ask1 (points and %).
4. **Output**: Same structure as Scenario 8.1; data source is futures order book + futures tickers.

---

### Scenario 8.3: Missing pair or amount — prompt user

**Context**: User asks for slippage simulation but does **not** specify a **currency pair** and/or does **not** specify a **quote amount** (e.g. "How much slippage if I market buy $10K?" with no pair; or "ETH_USDT slippage" with no amount).

**Prompt examples**:
- "How much slippage if I market buy $10K?" (missing pair)
- "ETH_USDT slippage" / "ADA_USDT perpetual slippage simulation" (missing amount)
- "Slippage simulation" (missing both pair and amount)

**Expected behavior**:
1. Do **not** call MCP. Do **not** assume a default pair or a default amount (e.g. do not default to $10K).
2. Reply with a short prompt asking for the missing input(s): pair and/or quote amount.

**Output** (when pair is missing, or amount is missing, or both):
```markdown
To run the slippage simulation, I need both:

1. **Currency pair** (e.g. spot: ETH_USDT, ADA_USDT; or perpetual: BTC_USDT).
2. **Quote amount** (e.g. $10,000 USDT). I will not assume a default — please specify the amount.

Example: "ETH_USDT slippage for a $10K market buy" or "ADA_USDT perpetual, market long $5K, how much slippage?"
```

---

## Case 9: K-Line Breakout / Support–Resistance

### MCP Call Spec (document-aligned)

**Trigger**: "Based on recent K-line chart, does SOL/USDT show signs of breaking out upward? Analyze support and resistance."

**API choice**: Use **spot** tools when user asks about spot pair (or unspecified); use **futures** tools when user says perpetual/contract.

| Step | MCP Tool (spot) | MCP Tool (futures) | Parameters | Required Fields |
|------|-----------------|--------------------|------------|-----------------|
| 1 | `get_spot_candlesticks` | `get_futures_candlesticks` | Spot: `currency_pair={BASE}_USDT`. Futures: `settle=usdt`, `contract={BASE}_USDT`. `interval=1d` (or 4h), `limit=30–90` | OHLC; volume; identify local highs/lows for support/resistance; trend structure |
| 2 | `get_spot_tickers` | `get_futures_tickers` | Same pair / contract + settle | `last`; 24h `quoteVolume`; `changePercentage`; `high24h`/`low24h` for momentum context |

**Calculation & judgment** (aligned with SKILL):

- **K-line**: Query historical candlesticks; from OHLC identify **support** (recent lows, consolidation floors) and **resistance** (recent highs, consolidation ceilings).
- **Momentum**: Use 24h price, volume, and change from tickers to assess whether current level has breakout momentum (e.g. volume expansion near resistance, price above key levels).

**Output**: Must include "K-line context" (period, key levels), "Support & resistance" table or list, "Momentum" (24h price, volume, change), and short "Breakout assessment" (e.g. signs of upward breakout or not).

---

### Scenario 9.1: Spot K-line support–resistance (e.g. SOL/USDT)

**Context**: User asks whether a spot pair shows breakout signs and wants support/resistance from recent K-line.

**Prompt examples**:
- "Based on recent K-line chart, does SOL/USDT show signs of breaking out upward? Analyze support and resistance."

**Expected behavior**:
1. Call per **MCP Call Spec**: `get_spot_candlesticks`(SOL_USDT, interval=1d or 4h, limit=30–90) → `get_spot_tickers`(SOL_USDT).
2. From candlesticks: derive support (e.g. recent lows, swing lows) and resistance (e.g. recent highs, swing highs); note trend structure (higher highs/lows vs lower).
3. From tickers: last, 24h volume, 24h change, high24h/low24h; use to assess momentum (e.g. volume confirmation, price relative to key levels).
4. Output: K-line context + support/resistance levels + momentum summary + breakout assessment (e.g. clear / no clear signs of upward breakout; data-based, not investment advice).

**Output**:
```markdown
## SOL/USDT — K-Line Support & Resistance

### K-line context

- Period: last 30 days (1d)
- Key levels derived from OHLC

### Support & resistance

| Type   | Level (approx) | Note        |
|--------|-----------------|-------------|
| Resistance | $XXX           | Recent high |
| Resistance | $XXX           | Prior swing |
| Support    | $XXX           | Recent low  |
| Support    | $XXX           | Consolidation floor |

### Momentum (24h)

| Metric   | Value   |
|----------|---------|
| Last     | $XXX    |
| 24h vol  | $XXX    |
| 24h change | +X.XX% |

### Breakout assessment

Based on recent K-line and 24h data: [e.g. price near/above resistance with volume expansion suggests upward breakout potential; or: no clear breakout yet, watch resistance and volume]. Analysis is data-based, not investment advice.
```

---

### Scenario 9.2: Futures K-line support–resistance

**Context**: User asks the same for a **perpetual/contract** (e.g. SOL_USDT perpetual).

**Prompt examples**:
- "Based on recent K-line, does SOL perpetual show breakout? Analyze support and resistance."
- "BTC contract: support and resistance from candlesticks?"

**Expected behavior**:
1. Detect "perpetual" or "contract" and use **futures** MCP: `get_futures_candlesticks`(settle=usdt, contract=SOL_USDT, interval=1d, limit=30–90) → `get_futures_tickers`(settle=usdt, contract=SOL_USDT).
2. Same logic: derive support/resistance from OHLC; use tickers for 24h price, volume, change; output same structure with futures data.

---

## Case 10: Liquidity + Weekend vs Weekday

### MCP Call Spec (document-aligned)

**Trigger**: "Evaluate ETH liquidity on the exchange and compare weekend vs weekday."

**API choice**: Use **spot** tools when user asks about spot (or unspecified); use **futures** tools when user says perpetual/contract.

| Step | MCP Tool (spot) | MCP Tool (futures) | Parameters | Required Fields |
|------|-----------------|--------------------|------------|-----------------|
| 1 | `get_spot_order_book` | `get_futures_contract` | Spot: `currency_pair={BASE}_USDT`, `limit=20`. Futures: `settle=usdt`, `contract={BASE}_USDT` | Spot: depth, bid1/ask1. Futures: `quanto_multiplier` for depth notional |
| 2 | `get_spot_candlesticks` | `get_futures_order_book` | Spot: same pair, `interval=1d`, `limit=90`. Futures: `settle=usdt`, `contract={BASE}_USDT`, `limit=20` | Spot: daily OHLC, volume. Futures: depth levels; top 10 bid/ask totals; bid1/ask1 |
| 3 | `get_spot_tickers` | `get_futures_candlesticks` | Same pair/contract; `interval=1d`, `limit=90` (or from/to for ~90 days) | Daily OHLC, volume, quote volume; tag weekend vs weekday |
| 4 | — | `get_futures_tickers` | Same pair/contract | `last`; 24h volume; current context |

**Calculation & judgment** (aligned with SKILL):

- **Order book**: Query depth; summarize current depth (levels, top 10 totals, spread) for **liquidity**.
- **90-day K-line**: From candlesticks, split days into **weekend** (Sat/Sun) vs **weekday** (Mon–Fri). Compute for each group: avg daily return (or sum of returns), avg/sum of volume and quote volume. Compare weekend vs weekday: volatility (e.g. absolute return), volume/quote volume (liquidity difference).

**Output**: Must include "Current liquidity" (order book depth, spread), "90-day weekend vs weekday" table (e.g. avg daily volume, avg daily return, or similar), "Comparison" summary, and short "Conclusion".

---

### Scenario 10.1: Spot liquidity + weekend vs weekday (e.g. ETH)

**Context**: User wants ETH liquidity assessment and weekend vs weekday comparison.

**Prompt examples**:
- "Evaluate ETH liquidity on the exchange and compare weekend vs weekday."

**Expected behavior**:
1. Call per **MCP Call Spec**: `get_spot_order_book`(ETH_USDT, limit=20) → `get_spot_candlesticks`(ETH_USDT, interval=1d, limit=90 or from/to ~90 days) → `get_spot_tickers`(ETH_USDT).
2. From order book: depth levels, top 10 bid/ask totals, spread → current liquidity summary.
3. From candlesticks: for each day (timestamp), classify weekend vs weekday; aggregate by group: e.g. avg daily volume, avg daily quote volume, avg absolute daily return or avg daily return; optionally count days.
4. Compare: e.g. "Weekend avg volume vs weekday avg volume"; "Weekend vs weekday volatility/return."
5. Output: Current liquidity table + "90-day weekend vs weekday" table + comparison + conclusion. Include disclaimer: data-based, not investment advice.

**Output**:
```markdown
## ETH — Liquidity & Weekend vs Weekday

### Current liquidity

| Metric           | Value   |
|------------------|---------|
| Order book depth | XX levels |
| Top 10 bid total | $XXX    |
| Top 10 ask total | $XXX    |
| Spread           | X.XX%   |

### 90-day: Weekend vs weekday

| Metric        | Weekend | Weekday | Note   |
|---------------|---------|---------|--------|
| Avg daily vol | $XXX    | $XXX    | Base   |
| Avg daily quote vol | $XXX | $XXX    | USDT   |
| Avg daily return | +X.XX% | +X.XX%  | Or abs return |
| Days count    | XX      | XX      |        |

### Comparison

- Liquidity: [e.g. current order book depth is good / moderate]
- Weekend vs weekday: [e.g. weekend volume/volatility is lower / higher / similar to weekday]. [One-line summary of volume and volatility difference.]

### Conclusion

[Short summary: ETH liquidity on exchange + weekend vs weekday difference.] Analysis is data-based, not investment advice.
```

---

### Scenario 10.2: Futures liquidity + weekend vs weekday

**Context**: User asks the same for **perpetual/contract** (e.g. ETH_USDT perpetual).

**Prompt examples**:
- "Evaluate ETH contract liquidity and compare weekend vs weekday."
- "BTC perpetual: liquidity and weekend vs weekday comparison."

**Expected behavior**:
1. Detect "perpetual" or "contract" and use **futures** MCP: `get_futures_contract`(settle=usdt, contract=ETH_USDT) → `get_futures_order_book`(settle=usdt, contract=ETH_USDT, limit=20) → `get_futures_candlesticks`(settle=usdt, contract=ETH_USDT, interval=1d, limit=90) → `get_futures_tickers`(settle=usdt, contract=ETH_USDT).
2. Use `quanto_multiplier` from contract to interpret order book depth in notional; same logic: order book for current depth; 90d candlesticks split weekend vs weekday for volume and return; output same structure with futures data.
