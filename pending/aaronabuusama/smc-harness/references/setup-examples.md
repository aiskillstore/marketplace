# Setup Examples

This document provides examples of well-constructed setups with proper reasoning.

## Table of Contents
1. [TRADE Setup Examples](#trade-setup-examples)
2. [WATCH Setup Examples](#watch-setup-examples)
3. [Reasoning Best Practices](#reasoning-best-practices)
4. [Common Mistakes](#common-mistakes)

---

## TRADE Setup Examples

### Example 1: Sweep-FVG Long

**Context:** Bullish 4H structure, SSL just swept, 15m ChoCH confirmed.

```bash
create-setup --symbol BTC/USDT \
             --type sweep-fvg \
             --decision TRADE \
             --confidence HIGH \
             --reasoning "
HTF BIAS: 4H bullish - HH at 98500, HL at 95200. Clear HH/HL sequence.
Price in discount at 95800 (below EQ at 96850).

TRIGGER: SSL at 95500 swept this candle. Wick reached 95300 before
strong rejection back above 95500. Stop hunt complete.

CONFIRMATION: 15m ChoCH at 95700 - broke above prior swing high at 95650.
Structure shifted bullish on LTF.

ENTRY ZONE: Bullish FVG formed at 95550-95700. Unfilled.
Entry at CE: 95625.

STOP: Below swept low at 95250. If price returns there, thesis is wrong.

TARGET: BSL at 98500 (4H swing high, unswept).

R:R: (98500-95625) / (95625-95250) = 7.7:1

CONFLUENCE:
- 4H bullish structure ✓
- Price in discount ✓
- SSL swept with rejection ✓
- 15m ChoCH confirmed ✓
- Unfilled FVG at entry ✓
- R:R exceeds 2:1 ✓
"

place-order --setup-id <id> \
            --side long \
            --entry 95625 \
            --stop 95250 \
            --target 98500 \
            --size 0.53 \
            --valid-until "2024-01-15T12:00:00"
```

---

### Example 2: ChoCH-OB Short

**Context:** Bearish 4H structure, price returned to bearish OB, 15m ChoCH confirmed.

```bash
create-setup --symbol BTC/USDT \
             --type choch-ob \
             --decision TRADE \
             --confidence HIGH \
             --reasoning "
HTF BIAS: 4H bearish - LH at 97200, LL at 93800. Price retesting
the LH zone after failed rally attempt.

ZONE: Bearish OB at 96800-97100. This was the last bullish candle
before the displacement that created the LH. Unmitigated until now.

TRIGGER: Price entered OB zone. BSL at 97000 was swept (wick to 97150)
but price rejected hard, closing at 96700.

CONFIRMATION: 15m ChoCH at 96600 - broke below prior swing low at 96650.
LTF now bearish.

ENTRY: Inside the OB at 96800 (body of the original bullish candle).

STOP: Above the swept high at 97200. Gives room for noise.

TARGET: SSL at 93800 (recent LL, unswept since).

R:R: (96800-93800) / (97200-96800) = 7.5:1

CONFLUENCE:
- 4H bearish structure ✓
- Unmitigated bearish OB ✓
- BSL swept with rejection ✓
- 15m ChoCH confirmed ✓
- Price in premium zone ✓
- Strong R:R ✓
"

place-order --setup-id <id> \
            --side short \
            --entry 96800 \
            --stop 97200 \
            --target 93800 \
            --size 0.5 \
            --valid-until "2024-01-16T00:00:00"
```

---

### Example 3: BOS-FVG Continuation

**Context:** Strong trend, BOS confirms continuation, FVG provides entry.

```bash
create-setup --symbol BTC/USDT \
             --type bos-fvg \
             --decision TRADE \
             --confidence HIGH \
             --reasoning "
HTF BIAS: 4H strong bullish trend. Just made new HH at 99200,
confirming BOS above prior HH at 98500.

STRUCTURE: BOS to the upside signals trend continuation. No sign
of exhaustion—displacement was clean with multiple large-bodied
bullish candles.

ENTRY ZONE: BOS move created bullish FVG at 98400-98700.
This is the first unfilled FVG since the BOS. High probability
fill for continuation.

ENTRY: FVG CE at 98550.

STOP: Below FVG low at 98350. FVG should hold if thesis correct.

TARGET 1: Recent high at 99200 (immediate).
TARGET 2: Psychological level at 100000 (BSL cluster expected).

R:R to T1: (99200-98550) / (98550-98350) = 3.25:1
R:R to T2: (100000-98550) / (98550-98350) = 7.25:1

CONFLUENCE:
- Strong 4H bullish trend ✓
- Fresh BOS confirms continuation ✓
- Clean FVG from displacement ✓
- First pullback after breakout ✓
- Trend-following (not counter-trend) ✓
"

place-order --setup-id <id> \
            --side long \
            --entry 98550 \
            --stop 98350 \
            --target 100000 \
            --size 1.0 \
            --valid-until "2024-01-15T08:00:00"
```

---

## WATCH Setup Examples

### Example 1: Approaching Liquidity

**Context:** Setup forming but sweep hasn't happened yet.

```bash
create-setup --symbol BTC/USDT \
             --type sweep-fvg \
             --decision WATCH \
             --confidence MEDIUM \
             --reasoning "
HTF BIAS: 4H bullish structure intact. HH at 98000, HL at 95500.

SITUATION: Price approaching SSL at 94800. This is the next obvious
liquidity target below. Three touches at this level = very attractive
for sweep.

MISSING: No sweep yet. Price is 200 points above the level.

WATCH FOR:
1. Wick below 94800 (sweep occurs)
2. Strong rejection candle (stops hit, reversal)
3. 15m ChoCH after sweep (confirmation)
4. FVG formation for entry

If sweep occurs with rejection → ready to TRADE
If price closes below 94800 → thesis invalidated, bearish takeover
"

set-alarm --type price_below --value 94800
```

---

### Example 2: ChoCH Without Entry Zone

**Context:** Structure shifted but no clean entry zone formed.

```bash
create-setup --symbol BTC/USDT \
             --type choch-fvg \
             --decision WATCH \
             --confidence MEDIUM \
             --reasoning "
HTF BIAS: 4H was bearish but showing signs of reversal.

TRIGGER: SSL at 93500 swept aggressively. Wick to 93200 with
immediate rejection.

CONFIRMATION: 15m ChoCH confirmed at 93800. Structure now bullish
on LTF.

PROBLEM: The move was too fast. No FVG formed during the reversal.
No clean OB to enter at. Current price is 94200—chasing at this
level gives poor R:R.

WATCH FOR:
1. Pullback to create entry zone
2. FVG to form on pullback
3. Or new OB to form on retrace

If price pulls back to 93800-94000 with FVG → ready to TRADE
If price continues higher without pullback → missed entry, wait
for next setup
"

set-alarm --type price_below --value 93900
```

---

### Example 3: HTF Bias Unclear

**Context:** Ranging market, waiting for clarity.

```bash
create-setup --symbol BTC/USDT \
             --type breakout \
             --decision WATCH \
             --confidence LOW \
             --reasoning "
HTF BIAS: 4H is ranging. No clear HH/HL or LH/LL sequence.
Range defined by:
- High: 97000 (equal highs, 3 touches)
- Low: 94500 (equal lows, 2 touches)

SITUATION: Price is mid-range at 95700. No directional edge.

LIQUIDITY:
- BSL building at 97000 (equal highs = obvious target)
- SSL at 94500

WATCH FOR:
1. Sweep of 97000 with rejection → short setup
2. Sweep of 94500 with rejection → long setup
3. Break and hold above 97000 → bullish breakout
4. Break and hold below 94500 → bearish breakdown

Until one of these occurs, no tradeable edge. Will set alarms
at both levels.
"

set-alarm --type price_above --value 97000
set-alarm --type price_below --value 94500
```

---

## Reasoning Best Practices

### Structure Your Reasoning

Always include these components:

```
1. HTF BIAS: What is the 4H telling you?
   - Trend direction (bullish/bearish/ranging)
   - Current structure (HH/HL or LH/LL)
   - Where is price in the range (premium/discount)

2. TRIGGER: What event prompted this setup?
   - Liquidity sweep
   - ChoCH
   - POI reached

3. CONFIRMATION: What confirms the direction?
   - LTF structure break
   - Rejection candle
   - FVG/OB formation

4. ENTRY ZONE: Where exactly will you enter?
   - Specific FVG or OB
   - Price level

5. STOP: Where is your invalidation?
   - Below/above what level
   - Why that level

6. TARGET: Where is the logical target?
   - Opposite liquidity
   - HTF level

7. R:R: What is the risk/reward?
   - Must be ≥ 2:1

8. CONFLUENCE: What factors align?
   - Checklist of supporting factors
```

### Be Specific

**Bad reasoning:**
```
"Looks bullish, FVG entry, good R:R"
```

**Good reasoning:**
```
"4H bullish structure with HH at 98500, HL at 95200.
SSL at 95500 swept (wick to 95300). 15m ChoCH at 95700.
Bullish FVG 95550-95700 unfilled. Entry at CE 95625,
stop at 95250, target 98500. R:R 7.7:1."
```

### Include "Why This Level"

For every price level, explain why:
- Entry: "At FVG CE" or "Inside OB body"
- Stop: "Below swept low" or "Beyond OB"
- Target: "Next BSL" or "HTF swing high"

---

## Common Mistakes

### Mistake 1: Vague Reasoning

```
❌ "Taking long because market looks bullish"

✓ "4H bullish bias (HH at X, HL at Y). SSL at Z swept with
   rejection. 15m ChoCH confirmed at W. Entry at FVG..."
```

### Mistake 2: Missing HTF Context

```
❌ "15m ChoCH, taking the trade"

✓ "4H bearish structure supports this 15m ChoCH short.
   Counter-trend trades (15m bullish against 4H bearish)
   would be lower probability."
```

### Mistake 3: No Invalidation Level

```
❌ "Stop somewhere below entry"

✓ "Stop at 95250, below the swept SSL at 95500. If price
   returns below this level, the sweep thesis is wrong
   and I should not be in this trade."
```

### Mistake 4: Chasing Without Entry Zone

```
❌ "Sweep happened, taking long now at current price"

✓ "Sweep at 95500 occurred. Waiting for pullback to FVG at
   95550-95700 for entry. Current price at 96000 would give
   poor R:R if entering here."
```

### Mistake 5: Trading Against HTF Bias

```
❌ "15m ChoCH bullish, going long" (when 4H is bearish)

✓ "15m ChoCH bullish but 4H remains bearish (LH/LL intact).
   This is a counter-trend bounce. WATCH for 4H to confirm
   with ChoCH before trading this direction."
```

### Mistake 6: Ignoring R:R

```
❌ "Good setup, entry 95000, stop 94500, target 95500"
   (R:R = 1:1)

✓ "Setup has merit but R:R of 1:1 is below minimum.
   Need target at 96000+ (R:R 2:1) or tighter stop
   to make this tradeable."
```

---

## Template for Setup Reasoning

Copy and fill in:

```
HTF BIAS: [4H trend direction and structure]
[Price zone: premium/discount]

TRIGGER: [What happened - sweep/ChoCH/POI reached]
[Specific price levels involved]

CONFIRMATION: [LTF signal that confirms direction]
[Structure break details]

ENTRY ZONE: [Specific FVG or OB]
[Entry price and why]

STOP: [Price level and rationale]
[Why thesis is wrong if this level breaks]

TARGET: [Price level and rationale]
[What liquidity or level you're targeting]

R:R: [Calculation]

CONFLUENCE:
- [Factor 1] ✓/✗
- [Factor 2] ✓/✗
- [Factor 3] ✓/✗
- [Factor 4] ✓/✗
```
