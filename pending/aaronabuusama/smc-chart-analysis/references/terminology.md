# SMC/ICT Terminology Glossary

## Table of Contents
1. [Core Concepts](#core-concepts)
2. [Market Structure](#market-structure)
3. [Liquidity](#liquidity)
4. [Order Flow Footprints](#order-flow-footprints)
5. [Time-Based Concepts](#time-based-concepts)
6. [Entry Models](#entry-models)

---

## Core Concepts

### Smart Money
Institutional traders, market makers, banks—entities with enough capital to move markets. The SMC framework assumes these entities engineer price movements to accumulate/distribute positions by triggering retail stops.

### Retail Traders
Individual traders whose predictable behavior (placing stops at obvious levels) provides liquidity for smart money.

### Liquidity
In SMC context: clusters of stop-loss orders. NOT order book depth. When SMC traders say "liquidity," they mean "stops that can be triggered."

### Displacement
A strong, impulsive price move (multiple large-bodied candles in one direction) that signals institutional activity. Displacement typically creates FVGs and breaks structure.

### Imbalance
Any area where price moved too quickly for fair price discovery. Includes FVGs and volume imbalances. Price tends to return to rebalance these areas.

### Mitigation
When price returns to a previously identified zone (order block, FVG) and reacts from it. An "unmitigated" zone hasn't been retested yet.

---

## Market Structure

### Swing High
Local price maximum—a candle with highs lower on both sides. The lookback period determines how "significant" the swing is.

### Swing Low
Local price minimum—a candle with lows higher on both sides.

### Higher High (HH)
A swing high that exceeds the previous swing high. Bullish structure.

### Higher Low (HL)
A swing low that stays above the previous swing low. Bullish structure.

### Lower High (LH)
A swing high below the previous swing high. Bearish structure.

### Lower Low (LL)
A swing low below the previous swing low. Bearish structure.

### Break of Structure (BOS)
Price breaks a swing point IN THE DIRECTION of the existing trend. Confirms trend continuation.
- Uptrend: New HH is BOS
- Downtrend: New LL is BOS

### Change of Character (ChoCH)
Price breaks a swing point AGAINST the existing trend. Signals potential reversal.
- Uptrend: Breaking below recent swing low is ChoCH
- Downtrend: Breaking above recent swing high is ChoCH

### Market Structure Shift (MSS)
Synonym for ChoCH. Some practitioners use MSS for the first break against trend, ChoCH for confirmation.

### Internal Structure
Smaller timeframe structure within a larger move. Used for precision entries.

### External Structure
Higher timeframe structure that defines the overall trend context.

---

## Liquidity

### Buy-Side Liquidity (BSL)
Stops resting ABOVE swing highs:
- Short sellers have stops above recent highs
- Breakout buyers have entry orders above highs

### Sell-Side Liquidity (SSL)
Stops resting BELOW swing lows:
- Long holders have stops below recent lows
- Breakdown sellers have entry orders below lows

### Liquidity Sweep / Stop Hunt
Price spikes through a swing level (triggering stops) then reverses. The wick that pokes through and rejects is the sweep.

### Liquidity Grab
Aggressive sweep—multiple levels taken in quick succession.

### Liquidity Void
Area with no significant swing points or structure—price can move quickly through these zones.

### Equal Highs / Equal Lows (EQH/EQL)
Multiple swing points at nearly the same price. HIGHLY attractive for sweeps because stops cluster densely.

### Protected High/Low
A swing point that "should not" be broken if the current trend is valid. Breaking a protected level suggests trend change.

---

## Order Flow Footprints

### Fair Value Gap (FVG)
Three-candle pattern where the middle candle's body doesn't overlap with the wicks of candles on either side. Indicates aggressive institutional entry.

**Bullish FVG:** `candle[i-1].high < candle[i+1].low`
- Gap between prior candle's high and next candle's low
- Price often returns to fill this gap before continuing up

**Bearish FVG:** `candle[i-1].low > candle[i+1].high`
- Gap between prior candle's low and next candle's high
- Price often returns to fill before continuing down

### Consequent Encroachment (CE)
The 50% level of an FVG. Some traders use this as precision entry rather than waiting for full fill.

### Order Block (OB)
The last opposing candle before a displacement move that breaks structure.

**Bullish OB:** Last bearish (red) candle before bullish displacement
**Bearish OB:** Last bullish (green) candle before bearish displacement

The theory: institutions left unfilled orders at these levels and price will return to complete the auction.

### Breaker Block
A failed order block that becomes a level in the opposite direction.
- Bullish OB gets run through → becomes bearish breaker
- Bearish OB gets run through → becomes bullish breaker

### Mitigation Block
Similar to breaker—a level that was previously support/resistance, failed, and now acts as the opposite.

### Rejection Block
A specific type of OB identified by long wicks showing institutional rejection of prices.

### Propulsion Block
OB that forms within an existing FVG—considered high probability.

### Volume Imbalance (VI)
Gap between consecutive candles' bodies (open-to-close gap between adjacent candles). Less significant than FVG but still represents inefficiency.

---

## Time-Based Concepts

### Killzones
Specific times when institutional activity peaks:
- **Asian Session:** 20:00-00:00 EST (range formation)
- **London Open:** 02:00-05:00 EST (high volatility)
- **New York Open:** 07:00-10:00 EST (highest volatility)
- **London Close:** 10:00-12:00 EST (reversals common)

### Power of Three (PO3)
Daily/weekly price pattern: Accumulation → Manipulation → Distribution
- Accumulation: Range formation (often Asian session)
- Manipulation: Stop hunt / false breakout
- Distribution: True move direction

### AMD (Accumulation, Manipulation, Distribution)
Same as PO3. Different name, same concept.

### Judas Swing
The manipulation phase—a false move designed to trap traders before the real move.

### ICT Daily Bias
Determining likely daily direction based on higher timeframe structure and liquidity targets.

---

## Entry Models

### Optimal Trade Entry (OTE)
Fibonacci retracement zone between 62%-79% of a move. Considered optimal entry for continuation trades.

### Premium Zone
Above 50% of a range (swing low to swing high). "Expensive"—look for shorts here.

### Discount Zone
Below 50% of a range. "Cheap"—look for longs here.

### Equilibrium (EQ)
The 50% level of a range. Price often reacts at equilibrium.

### 2022 Entry Model
ICT's refined entry: Wait for ChoCH on LTF, then enter on FVG within the OTE zone of the HTF move.

### Silver Bullet
Time-based entry model: Look for FVGs formed during specific 1-hour windows within killzones.
- 10:00-11:00 EST
- 14:00-15:00 EST
- 03:00-04:00 EST (London)

### Unicorn Model
Entry combining: Breaker block + FVG overlap. High confluence setup.

---

## Quick Reference: Detection Priority

**Always detect (100% deterministic):**
1. Swing points
2. FVGs
3. Structure breaks (BOS/ChoCH)
4. Liquidity sweeps

**Detect with heuristics (configurable):**
5. Order blocks
6. Premium/Discount zones

**Claude interpretation (narrative):**
7. Confluence analysis
8. Scenario building
9. Bias determination
