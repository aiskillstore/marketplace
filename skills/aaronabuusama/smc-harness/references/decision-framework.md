# Decision Framework

This document provides detailed guidance on when to TRADE, WATCH, NOTE, or do NOTHING.

## Table of Contents
1. [The Decision Tree](#the-decision-tree)
2. [TRADE Criteria](#trade-criteria)
3. [WATCH Criteria](#watch-criteria)
4. [NOTE Criteria](#note-criteria)
5. [NOTHING Criteria](#nothing-criteria)
6. [Confidence Assessment](#confidence-assessment)
7. [Edge Cases](#edge-cases)

---

## The Decision Tree

```
                         ┌─────────────────┐
                         │   Agent Wakes   │
                         └────────┬────────┘
                                  │
                         ┌────────▼────────┐
                         │    my-state     │
                         │ (check current) │
                         └────────┬────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
              Active Order?                No Orders
                    │                           │
                    ▼                           ▼
             Manage first              ┌───────────────┐
             (cancel if                │ analyze symbol│
              invalid)                 └───────┬───────┘
                    │                          │
                    └──────────┬───────────────┘
                               │
                      ┌────────▼────────┐
                      │ See actionable  │
                      │    pattern?     │
                      └────────┬────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
    Yes, ready            Yes, forming         No pattern
    to trade               not ready
          │                    │                    │
          ▼                    ▼                    ▼
    ┌──────────┐         ┌──────────┐        ┌───────────┐
    │  TRADE   │         │  WATCH   │        │ Observe?  │
    │          │         │          │        └─────┬─────┘
    │ create-  │         │ create-  │              │
    │ setup    │         │ setup    │        ┌─────┴─────┐
    │ (TRADE)  │         │ (WATCH)  │        │           │
    │    +     │         │          │   Interesting   Nothing
    │ place-   │         │ set-     │   observation
    │ order    │         │ alarm    │        │           │
    └──────────┘         └──────────┘        ▼           ▼
                                        ┌────────┐  ┌────────┐
                                        │  NOTE  │  │NOTHING │
                                        │        │  │        │
                                        │ save-  │  │ set-   │
                                        │ note   │  │ alarm  │
                                        └────────┘  └────────┘
```

---

## TRADE Criteria

### All Must Be True

| # | Criterion | How to Verify |
|---|-----------|---------------|
| 1 | HTF bias is clear | 4H shows HH/HL (bullish) or LH/LL (bearish) |
| 2 | Price in favorable zone | Longs from discount, shorts from premium |
| 3 | Liquidity has been swept | Recent candle wicked through swing high/low |
| 4 | LTF structure confirms | 15m ChoCH in direction of intended trade |
| 5 | Entry zone exists | Unfilled FVG or unmitigated OB at current price |
| 6 | R:R ≥ 2:1 | Target distance ≥ 2× stop distance |
| 7 | No blocking constraints | No active order, balance sufficient |

### Confidence Must Be HIGH

A HIGH confidence rating requires:
- All 7 criteria above met
- No significant concerns
- Pattern is textbook or near-textbook

### Example TRADE Decision

```
Analysis shows:
- 4H: Bullish structure (HH at 98000, HL at 94500)
- 4H: Price at 95500, in discount zone
- 4H: SSL at 95000 was swept last candle (wick to 94800)
- 15m: ChoCH confirmed at 95200 (broke above prior swing high)
- 15m: Bullish FVG at 95100-95300 (unfilled)
- Target: BSL at 98000
- R:R: (98000-95200) / (95200-94700) = 5.6:1

Decision: TRADE
Confidence: HIGH

create-setup:
  --type sweep-fvg
  --decision TRADE
  --confidence HIGH
  --reasoning "4H bullish structure intact. SSL at 95000 swept (wick to 94800).
               15m ChoCH confirmed at 95200. Unfilled bullish FVG 95100-95300.
               Entry at FVG CE 95200, stop below sweep at 94700, target BSL 98000.
               R:R 5.6:1. All confluence factors aligned."

place-order:
  --entry 95200
  --stop 94700
  --target 98000
```

---

## WATCH Criteria

### Pattern Forming But Not Ready

Use WATCH when you see a potential setup but one or more criteria aren't met yet:

| Situation | What's Missing | What to Watch For |
|-----------|----------------|-------------------|
| Approaching liquidity | Sweep hasn't happened | Price to wick through level |
| At POI, no ChoCH | Confirmation missing | LTF break of structure |
| ChoCH occurred, no entry zone | FVG/OB not formed | Wait for retrace to create entry |
| HTF bias unclear | Need structure break | Wait for HH/HL or LH/LL |
| Good setup, poor R:R | Target too close | Price to move for better R:R |

### Confidence is MEDIUM or LOW

When you see potential but aren't certain:
- MEDIUM: Most criteria met, minor concerns
- LOW: Interesting pattern but significant gaps

### Example WATCH Decision

```
Analysis shows:
- 4H: Bullish structure (HH/HL intact)
- 4H: Price approaching SSL at 94000
- 4H: SSL has NOT been swept yet
- 15m: No ChoCH (still making lower lows)

Decision: WATCH
Confidence: MEDIUM

create-setup:
  --type sweep-fvg
  --decision WATCH
  --confidence MEDIUM
  --reasoning "4H bullish bias. Price approaching SSL at 94000 but no sweep yet.
               Watching for sweep and subsequent 15m ChoCH. If sweep occurs with
               strong rejection and ChoCH follows, will look for bullish FVG entry."

set-alarm:
  --type price_below
  --value 94000

Why WATCH not TRADE:
- Liquidity hasn't been swept
- No LTF confirmation
- Entry zone doesn't exist yet
```

---

## NOTE Criteria

### Market Observations Without Specific Patterns

Use NOTE for:
- General market behavior observations
- Session-specific patterns
- Recurring themes you're noticing
- Context that might inform future decisions

### Examples of Good Notes

```
save-note "Equal highs forming at 98500 - three touches now.
           This is becoming obvious BSL. Expect sweep before
           any sustained bearish move."

save-note "FVGs filling very quickly this week. Previous ones
           lasted 8-12 candles, now filling in 2-3. Suggests
           increased volatility or trend exhaustion."

save-note "Asian session range was unusually tight (94800-95200).
           This consolidation often precedes expansion. Watch for
           manipulation at London open."

save-note "Three consecutive SSL sweeps with immediate reversal.
           Smart money appears to be accumulating aggressively
           in the 93000-94000 zone."
```

### When NOTE is Better Than WATCH

| Use NOTE When | Use WATCH When |
|---------------|----------------|
| General observation, no specific level | Specific pattern at specific level |
| Behavioral pattern over multiple candles | Setup forming on current candle |
| Context for future reference | Actionable within a few candles |
| No specific entry criteria | Entry criteria partially met |

---

## NOTHING Criteria

### When to Simply Set Alarms and Sleep

Do NOTHING when:
- No patterns visible
- No interesting observations
- Market is ranging with no direction
- Already have active order (focus on management)

### Still Set Alarms

Even when doing nothing, set alarms at key levels:

```
# After analyzing and finding nothing actionable:

set-alarm --type price_above --value 98000  # BSL level
set-alarm --type price_below --value 94000  # SSL level

# These wake you when something interesting might happen
```

---

## Confidence Assessment

### HIGH Confidence

**Criteria:**
- All trade criteria met
- Pattern is textbook
- No conflicting signals
- Clear entry, stop, target

**Result:** TRADE if all checks pass

### MEDIUM Confidence

**Criteria:**
- Most criteria met
- One or two concerns
- Pattern is recognizable but not perfect
- Some ambiguity in entry or stop

**Result:** WATCH, set alarm, wait for confirmation

### LOW Confidence

**Criteria:**
- Bias unclear
- Pattern weak
- Conflicting signals
- Forcing interpretation

**Result:** NOTE the observation or do NOTHING

### Confidence Decision Matrix

| HTF Bias | LTF Confirm | Sweep | Entry Zone | R:R ≥ 2:1 | Confidence |
|----------|-------------|-------|------------|-----------|------------|
| Clear | Yes | Yes | Yes | Yes | HIGH → TRADE |
| Clear | Yes | Yes | No | - | MEDIUM → WATCH |
| Clear | Yes | No | - | - | MEDIUM → WATCH |
| Clear | No | - | - | - | LOW → NOTE |
| Unclear | - | - | - | - | LOW → NOTHING |

---

## Edge Cases

### Already Have Active Order

```
my-state shows: 1 PENDING order for LONG at 95000

Actions:
1. Check if order is still valid (setup thesis intact?)
2. If thesis broken → cancel-order
3. If thesis intact → do NOT place another order
4. Can still WATCH other setups for future
5. Can still save NOTEs
```

### Multiple Setups Visible

```
See two potential setups:
- Bullish FVG at 95200
- Bullish OB at 94800

Actions:
1. Evaluate which is higher probability
2. TRADE the better one
3. Can WATCH the other (separate setup)
4. Cannot place two orders (max 1)
```

### Setup Expires Before Trading

```
Created WATCH setup for sweep at 94000
Price swept, ChoCH confirmed, but you missed the entry
Setup expired before you could act

Actions:
1. Create NEW setup if entry zone still valid
2. Do NOT try to modify expired setup
3. Record what happened in a NOTE for learning
```

### Conflicting Timeframes

```
4H: Bearish bias (LH/LL)
15m: Bullish ChoCH just occurred

Actions:
1. 15m ChoCH against 4H trend = likely counter-trend bounce
2. Do NOT trade counter-trend unless you have specific edge
3. WATCH for 4H to confirm (ChoCH on 4H)
4. Or NOTE the divergence for context
```

### Woke on Alarm, But Setup Gone

```
Set alarm at 94000 for SSL sweep
Alarm triggered (price hit 94000)
But no sweep rejection—price continued through

Actions:
1. Thesis invalidated (sweep didn't hold)
2. Do NOT force the trade
3. Re-analyze for new setup
4. Possibly NOTE the failed sweep for context
```

---

## Summary: Decision Quick Reference

| See This | Confidence | Action |
|----------|------------|--------|
| All criteria met, textbook pattern | HIGH | TRADE |
| Good pattern, one thing missing | MEDIUM | WATCH |
| Interesting pattern, multiple gaps | LOW | WATCH or NOTE |
| Market observation, no pattern | - | NOTE |
| Nothing interesting | - | NOTHING (set alarms) |
| Have active order | - | Manage order, don't add new |
