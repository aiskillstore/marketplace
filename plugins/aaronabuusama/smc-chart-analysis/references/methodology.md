# ICT Trading Methodology

Complete workflow for analyzing markets and generating trade setups using Smart Money Concepts.

## Table of Contents
1. [The Framework](#the-framework)
2. [Multi-Timeframe Analysis](#multi-timeframe-analysis)
3. [Session Timing](#session-timing)
4. [Entry Models](#entry-models)
5. [Trade Construction](#trade-construction)
6. [Complete Workflow](#complete-workflow)
7. [Checklist](#checklist)

---

## The Framework

### Core Principle

ICT trading is based on the concept that:
1. **Smart money** (institutions) needs liquidity to fill large orders
2. Liquidity clusters at **obvious levels** (swing highs/lows)
3. Price is **engineered** to sweep these levels before the "real" move
4. We trade **with** smart money by identifying their footprints

### The PO3 Model (Power of Three)

Every significant move follows this pattern:

```
ACCUMULATION → MANIPULATION → DISTRIBUTION
     │               │               │
  Range forms    Stop hunt      True move
  (Asia/Early)   (False break)  (Expansion)
```

**Daily example:**
- Asian session: Price consolidates (accumulation)
- London open: Sweeps one side of the range (manipulation)
- NY session: Moves in true direction (distribution)

---

## Multi-Timeframe Analysis

### The Hierarchy

```
HIGHER TIMEFRAME (HTF)     →  Determines BIAS
     │
     ▼
INTERMEDIATE TIMEFRAME (ITF) →  Identifies POI (Point of Interest)
     │
     ▼
LOWER TIMEFRAME (LTF)      →  Times ENTRY
```

### Timeframe Combinations

| Style | HTF | ITF | LTF | Hold Time |
|-------|-----|-----|-----|-----------|
| Scalp | 1H | 15M | 1-5M | Minutes to hours |
| Intraday | 4H | 1H | 15M | Hours to 1 day |
| Swing | Daily | 4H | 1H | Days to weeks |
| Position | Weekly | Daily | 4H | Weeks to months |

### HTF Analysis (Bias Determination)

**Goal:** Decide if you're looking for longs or shorts.

**Steps:**
1. Identify current trend (HH/HL = bullish, LH/LL = bearish)
2. Locate major liquidity pools (weekly/daily highs and lows)
3. Determine premium/discount zone
4. Find unmitigated HTF order blocks and FVGs

**Bullish bias when:**
- Price is in discount (below 50% of range)
- HTF structure is bullish (HH/HL)
- Sell-side liquidity has been swept
- Price approaching bullish OB or FVG

**Bearish bias when:**
- Price is in premium (above 50% of range)
- HTF structure is bearish (LH/LL)
- Buy-side liquidity has been swept
- Price approaching bearish OB or FVG

### ITF Analysis (POI Identification)

**Goal:** Find the zone where you expect price to react.

**Steps:**
1. Confirm bias aligns with HTF
2. Locate unmitigated order blocks in direction of bias
3. Identify unfilled FVGs
4. Mark intermediate liquidity levels
5. Define your POI zone

**Strong POI has:**
- Unmitigated order block
- FVG within or near the OB
- Liquidity resting nearby (to be swept)
- Aligns with HTF bias

### LTF Analysis (Entry Timing)

**Goal:** Get precise entry within the POI.

**Wait for:**
1. Price reaches your POI
2. Liquidity sweep occurs (stops taken)
3. Change of Character (ChoCH) on LTF
4. Entry trigger forms (FVG or OB in OTE zone)

---

## Session Timing

### Killzones (EST)

| Session | Time | Characteristics |
|---------|------|-----------------|
| Asian | 20:00-00:00 | Range formation, low volume, sets up the manipulation |
| London Open | 02:00-05:00 | First expansion, often the "Judas swing" (fake move) |
| NY AM | 07:00-10:00 | Highest volume, true direction often revealed |
| NY Lunch | 12:00-14:00 | Low volume, avoid trading |
| NY PM | 14:00-16:00 | Can see continuation or reversal setups |

### Best Times to Trade

**Highest probability:**
- London-NY overlap (07:00-10:00 EST)
- Post-London-close reversal (10:00-12:00 EST)

**Avoid:**
- NY lunch (12:00-14:00 EST)
- Low volume holiday periods
- Major news events (unless you're specifically trading news)

### Session-Based Strategy

**Scenario A: Trend Day**
```
Asian: Consolidation
London: Sweeps low (manipulation)
NY: Strong rally (distribution) - This is your entry window
```

**Scenario B: Reversal Day**
```
Asian: Consolidation
London: Strong expansion one direction
NY: Reverses at key level - Look for reversal entry
```

---

## Entry Models

### 1. Standard OTE Entry

The "bread and butter" entry model.

```
1. Wait for HTF/ITF POI to be reached
2. Look for LTF liquidity sweep
3. Wait for ChoCH (structure shift)
4. Enter at FVG within OTE zone (61.8%-79% retracement)
5. Stop below swept low (for longs) / above swept high (for shorts)
```

**OTE Zone:** 61.8% to 79% retracement of the impulse move.

### 2. FVG Entry

Direct entry into a fair value gap.

```
1. Identify significant FVG after displacement
2. Wait for price to retrace into FVG
3. Enter at 50% of FVG (Consequent Encroachment)
4. Stop beyond the FVG
```

### 3. Order Block Entry

Entry at the origin of a move.

```
1. Identify order block (last opposing candle before displacement)
2. Wait for price to return to OB
3. Enter when price wicks into OB and shows rejection
4. Stop beyond the OB
```

### 4. Breaker Entry

Entry after a failed OB becomes support/resistance.

```
1. Identify failed order block (price ran through it)
2. This now becomes a "breaker" - acts in opposite direction
3. Wait for retest of the breaker
4. Enter with stop beyond the breaker
```

### 5. Liquidity Sweep + FVG

Highest confluence setup.

```
1. Price sweeps obvious liquidity (stops hit)
2. Immediately creates FVG in opposite direction
3. ChoCH confirms structure shift
4. Enter at FVG
5. Stop below the swept level
```

---

## Trade Construction

### Entry Criteria Checklist

Before entering, confirm:

- [ ] HTF bias established (bullish/bearish)
- [ ] ITF POI identified (OB, FVG, or breaker)
- [ ] LTF entry trigger occurred (ChoCH + FVG/OB)
- [ ] Liquidity swept (obvious stops taken)
- [ ] In killzone timing (London/NY)
- [ ] Risk defined (know your stop before entry)

### Stop Loss Placement

**For longs:**
- Below the swept swing low
- Below the order block low
- 1 ATR below entry zone

**For shorts:**
- Above the swept swing high
- Above the order block high
- 1 ATR above entry zone

### Target Selection

**Target 1 (T1):** First opposing liquidity
- Nearest unswept swing high (for longs)
- Nearest unswept swing low (for shorts)
- Typically 1:2 risk/reward minimum

**Target 2 (T2):** HTF liquidity
- Daily/weekly high or low
- Unmitigated HTF order block
- Major round number

### Position Sizing

```
Risk Amount = Account Balance × Risk Percentage (1-2%)
Position Size = Risk Amount / (Entry Price - Stop Loss)
```

**Example:**
- Account: $10,000
- Risk: 1% = $100
- Entry: $42,000
- Stop: $41,500
- Distance: $500
- Position: $100 / $500 = 0.2 BTC

---

## Complete Workflow

### Phase 1: Preparation (Before Session)

```
1. Check economic calendar for news events
2. Review HTF charts (Daily/Weekly)
   - Current trend
   - Major liquidity levels
   - Unmitigated OBs/FVGs
3. Establish directional bias
4. Identify ITF POIs for the day
5. Set alerts at key levels
```

### Phase 2: Analysis (Start of Session)

```
1. Note Asian session range
2. Mark Asian high/low as potential liquidity
3. Identify which side has more liquidity
4. Anticipate which side gets swept first
5. Wait for London/NY activity
```

### Phase 3: Setup Development

```
1. Price approaches your POI
2. Switch to LTF for precision
3. Watch for:
   - Sweep of nearby liquidity
   - Reaction (rejection wicks)
   - ChoCH formation
   - FVG or OB entry zone
```

### Phase 4: Execution

```
1. Entry trigger confirmed
2. Calculate position size
3. Set stop loss
4. Set take profit targets
5. Execute trade
```

### Phase 5: Management

```
1. Move stop to break-even after T1 hit
2. Trail stop behind structure
3. Take partials at targets
4. Document the trade
```

---

## Checklist

### Pre-Trade Checklist

**Bias:**
- [ ] HTF trend identified
- [ ] HTF liquidity mapped
- [ ] Premium/Discount zone known
- [ ] Clear directional bias

**Setup:**
- [ ] ITF POI marked
- [ ] POI has confluence (OB + FVG)
- [ ] Nearby liquidity to be swept
- [ ] In favorable session timing

**Entry:**
- [ ] Price at POI
- [ ] Liquidity swept
- [ ] LTF ChoCH occurred
- [ ] Entry zone identified (FVG/OB)
- [ ] Stop loss defined
- [ ] Target(s) identified
- [ ] Risk calculated

### Trade Grading

**A+ Setup (Take full size):**
- HTF and ITF alignment
- Clear liquidity sweep
- Strong ChoCH
- FVG within OTE
- In killzone
- Multiple confluences

**B Setup (Take half size):**
- Most criteria met
- Missing one confluence factor
- Outside ideal killzone

**C Setup (Skip or micro size):**
- Bias unclear
- Weak confluence
- Bad timing
- Chasing move

---

## Example Trade Narrative

> "Looking at BTC on the daily, we're in a bullish structure with price currently in discount (below equilibrium). The daily swing low at $40,800 represents unswept sell-side liquidity.
> 
> On the 4H, there's an unmitigated bullish OB at $41,200-$41,400 with an overlapping FVG—this is our POI.
> 
> During London session, price swept the $40,800 SSL and immediately created a bullish FVG on the 15M with ChoCH confirmation. This is our entry trigger.
> 
> **Trade Setup:**
> - Entry: $41,300 (inside the 4H OB/FVG)
> - Stop: $40,700 (below swept low)
> - Target 1: $42,500 (nearest BSL)
> - Target 2: $44,000 (daily high)
> - Risk/Reward: 1:2 and 1:4.5
> 
> Confluence: HTF bullish bias, ITF POI reached, liquidity swept, LTF confirmation, London session timing."

---

## Quick Reference

### Bias → POI → Entry

```
HTF bullish + ITF bullish OB + LTF sweep & ChoCH = LONG
HTF bearish + ITF bearish OB + LTF sweep & ChoCH = SHORT
```

### Risk Management Rules

1. Never risk more than 2% per trade
2. Always define stop before entry
3. Minimum 1:2 risk/reward
4. Move to break-even after T1
5. Don't trade against HTF bias

### Session Rules

1. Best setups during killzones
2. Wait for manipulation before entry
3. Don't force trades in low volume
4. Respect major news events
