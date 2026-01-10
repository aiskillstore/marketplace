# ICT Trading Methodology

Complete methodology for analyzing markets and making trade decisions using Smart Money Concepts.

## Table of Contents
1. [The Framework](#the-framework)
2. [Multi-Timeframe Analysis](#multi-timeframe-analysis)
3. [Entry Models](#entry-models)
4. [Trade Construction](#trade-construction)
5. [Complete Workflow](#complete-workflow)
6. [Checklists](#checklists)

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
  (Consolidation)  (False break)  (Expansion)
```

**Implications for your trading:**
- The consolidation phase sets up the trap
- The manipulation (sweep) is your signal to prepare
- The distribution is the move you want to capture
- Enter AFTER manipulation, not during accumulation

---

## Multi-Timeframe Analysis

### The Hierarchy (For This Harness)

```
4H (HTF)  →  Determines BIAS
    │           - Overall trend direction
    │           - Major liquidity levels
    │           - Premium/discount zones
    │
    ▼
15m (LTF) →  Times ENTRY
                - Precise entry triggers
                - ChoCH confirmation
                - FVG/OB entry zones
```

### HTF Analysis (4H) — Bias Determination

**Goal:** Decide if you're looking for longs or shorts.

**Steps:**
1. Identify current trend
   - HH + HL sequence = bullish
   - LH + LL sequence = bearish
   - No clear sequence = ranging (wait for clarity)

2. Locate major liquidity pools
   - Unswept swing highs = BSL (targets for longs)
   - Unswept swing lows = SSL (targets for shorts)
   - Equal highs/lows = high probability sweep targets

3. Determine premium/discount zone
   - Calculate range (recent swing high to swing low)
   - Above 50% = premium (favor shorts)
   - Below 50% = discount (favor longs)

4. Find unmitigated zones
   - Order blocks not yet retested
   - FVGs not yet filled
   - These become POIs (Points of Interest)

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

### LTF Analysis (15m) — Entry Timing

**Goal:** Get precise entry within the HTF POI.

**Steps:**
1. Wait for price to reach HTF POI
2. Look for liquidity sweep on LTF
3. Wait for ChoCH (structure shift confirmation)
4. Identify entry zone (FVG or OB within OTE)
5. Define stop and target

---

## Entry Models

### Model 1: Standard OTE Entry

The fundamental entry model.

```
Prerequisites:
- HTF bias established
- Price at or near HTF POI

Entry Sequence:
1. Price reaches HTF POI
2. LTF liquidity sweep occurs
3. LTF ChoCH confirms direction shift
4. Enter at FVG within OTE zone (61.8%-79%)
5. Stop below swept low (longs) / above swept high (shorts)
6. Target opposite liquidity
```

### Model 2: FVG Entry

Direct entry into fair value gap.

```
Prerequisites:
- Significant FVG after displacement
- FVG in direction of HTF bias

Entry Sequence:
1. Identify unfilled FVG
2. Wait for price to retrace into FVG
3. Enter at 50% (Consequent Encroachment)
4. Stop beyond FVG
5. Target: next liquidity level
```

### Model 3: Order Block Entry

Entry at the origin of a move.

```
Prerequisites:
- Unmitigated order block identified
- OB in direction of HTF bias

Entry Sequence:
1. Price returns to OB zone
2. Look for reaction (rejection wick)
3. Enter within OB zone
4. Stop beyond OB
5. Target: next liquidity level
```

### Model 4: Sweep + FVG (Highest Confluence)

The highest probability setup.

```
Prerequisites:
- Obvious liquidity level to be swept
- HTF bias supports direction after sweep

Entry Sequence:
1. Price sweeps liquidity (triggers stops)
2. Immediate FVG created in opposite direction
3. ChoCH confirms reversal
4. Enter at FVG
5. Stop below swept level
6. Target: opposite liquidity pool
```

---

## Trade Construction

### Entry Zone Selection

**For LONG trades:**
| Component | Criteria |
|-----------|----------|
| Zone type | Bullish FVG or bullish OB |
| Location | In discount (below EQ) preferred |
| Confirmation | After SSL swept |
| Entry price | CE of FVG or body of OB |

**For SHORT trades:**
| Component | Criteria |
|-----------|----------|
| Zone type | Bearish FVG or bearish OB |
| Location | In premium (above EQ) preferred |
| Confirmation | After BSL swept |
| Entry price | CE of FVG or body of OB |

### Stop Loss Placement

**For LONG trades:**
- Below the swept swing low
- Below the order block low
- Minimum: below recent LTF structure

**For SHORT trades:**
- Above the swept swing high
- Above the order block high
- Minimum: above recent LTF structure

**Key principle:** Stop should only be hit if your thesis is wrong.

### Target Selection

**Target 1 (T1):** First opposing liquidity
- Nearest unswept swing high (for longs)
- Nearest unswept swing low (for shorts)
- Minimum 2:1 R:R required

**Target 2 (T2):** HTF liquidity
- Major swing high/low on 4H
- Unmitigated HTF order block

### Position Sizing

The harness enforces 2% max risk:

```
risk_amount = balance × 0.02
distance = |entry_price - stop_price|
position_size = risk_amount / distance
```

**Example:**
- Balance: $10,000
- Risk: $200 (2%)
- Entry: $95,000
- Stop: $94,500
- Distance: $500
- Size: $200 / $500 = 0.4 BTC

---

## Complete Workflow

### On Each Wake

```
PHASE 1: ORIENTATION
├── my-state
│   ├── Check active orders
│   ├── Check triggered alarms
│   └── Note current balance/P&L
│
PHASE 2: ANALYSIS
├── analyze BTC/USDT
│   ├── Review 4H structure (trend, bias)
│   ├── Review 15m structure (entry signals)
│   ├── Identify unswept liquidity
│   ├── Note unfilled FVGs
│   └── Note unmitigated OBs
│
PHASE 3: DECISION
├── Evaluate patterns
│   ├── All confluence? → TRADE
│   ├── Forming but not ready? → WATCH
│   ├── Interesting observation? → NOTE
│   └── Nothing actionable? → SKIP
│
PHASE 4: ACTION
├── If TRADE:
│   ├── create-setup (decision=TRADE)
│   └── place-order
├── If WATCH:
│   └── create-setup (decision=WATCH)
├── If NOTE:
│   └── save-note
│
PHASE 5: PREPARE NEXT WAKE
└── set-alarm at key price levels
```

---

## Checklists

### Pre-Trade Checklist

**Bias (HTF 4H):**
- [ ] Trend identified (HH/HL or LH/LL)
- [ ] Major liquidity levels mapped
- [ ] Premium/discount zone known
- [ ] Clear directional bias established

**Setup (LTF 15m):**
- [ ] POI reached (OB, FVG, or level)
- [ ] Liquidity swept
- [ ] ChoCH confirmed
- [ ] Entry zone identified

**Trade Parameters:**
- [ ] Entry price defined
- [ ] Stop loss defined
- [ ] Target defined
- [ ] R:R ≥ 2:1
- [ ] Size within 2% risk

### Trade Grading

**A+ Setup (High confidence, TRADE):**
- HTF and LTF alignment
- Clear liquidity sweep
- Strong ChoCH
- FVG/OB at entry
- Multiple confluences
- R:R ≥ 3:1

**B Setup (Medium confidence, consider TRADE):**
- Most criteria met
- Missing one confluence factor
- May have minor concerns
- R:R ≥ 2:1

**C Setup (Low confidence, WATCH or skip):**
- Bias unclear
- Weak confluence
- Forcing the trade
- R:R < 2:1

### Setup Type Reference

| Type | Description | Key Criteria |
|------|-------------|--------------|
| `choch-fvg` | ChoCH + FVG entry | ChoCH on LTF, enter at FVG |
| `bos-ob` | BOS + OB entry | BOS continues trend, enter at OB |
| `sweep-fvg` | Sweep + FVG | Liquidity swept, FVG formed |
| `sweep-ob` | Sweep + OB | Liquidity swept, OB entry |
| `breaker` | Breaker block | Failed OB becomes entry |
| `ote` | OTE zone entry | Entry at 62-79% retracement |

---

## Risk Management Rules

### Absolute Rules (Harness Enforced)

1. **Max 2% risk per trade** — Position size calculated accordingly
2. **Max 1 concurrent order** — Close or cancel before new trade
3. **Setup required** — Cannot place order without setup
4. **1:1 setup:order** — One order per setup, new setup for re-entry

### Your Discipline

1. **Minimum 2:1 R:R** — Don't take poor risk/reward
2. **Don't fight HTF bias** — Trade with the trend
3. **Wait for sweep** — Patience for manipulation phase
4. **If unsure, WATCH** — Better to observe than force
5. **Record reasoning** — Every setup documents your thesis
