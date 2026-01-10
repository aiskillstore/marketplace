---
name: smc-chart-analysis
description: Smart Money Concepts (SMC) and ICT-style chart analysis skill. Analyzes any market with one command - fetches real data, runs multi-timeframe analysis, identifies trade setups with entry/stop/targets. Use when user asks to "analyze [SYMBOL]", wants SMC/ICT analysis, asks about liquidity sweeps, order blocks, fair value gaps, or market structure, or wants trade setup recommendations.
---

# SMC Chart Analysis Skill

**AI-powered Smart Money Concepts analysis with actionable trade setups.**

## How This Skill Works

```
┌─────────────────────────────────────────────────────────────┐
│  1. FETCH DATA                                              │
│     Call web app API: localhost:3001/api/smc-analyze        │
│     → Returns: structure, liquidity, FVGs, sweeps           │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  2. AI INTERPRETATION (Claude)                              │
│     Analyze the mechanical data using ICT methodology       │
│     → Determine bias, identify setups, assess confluence    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  3. TRADE SETUP OUTPUT                                      │
│     • Direction (long/short)                                │
│     • Entry zone with reasoning                             │
│     • Stop loss with reasoning                              │
│     • Targets with R:R ratios                               │
│     • Setup grade (A+/A/B/C)                                │
│     • Narrative explaining the trade thesis                 │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

When a user asks to analyze a market (e.g., "analyze BTC", "what's the setup on ETH"):

### Step 1: Fetch Mechanical Data
```bash
curl "http://localhost:3001/api/smc-analyze?symbol=BTC/USDT&timeframe=1h&style=intraday"
```

Or for multiple timeframes:
```bash
# HTF (4H) for bias
curl "http://localhost:3001/api/smc-analyze?symbol=BTC/USDT&timeframe=4h&style=swing"

# LTF (15m) for entry
curl "http://localhost:3001/api/smc-analyze?symbol=BTC/USDT&timeframe=15m&style=scalp"
```

### Step 2: Interpret with AI

Take the mechanical data and provide AI-powered analysis following the ICT methodology:

1. **Determine HTF Bias**
   - Is price in premium or discount?
   - Where is major liquidity (BSL/SSL)?
   - What is the trend direction?

2. **Identify Entry POI**
   - Unmitigated FVGs in direction of bias
   - Recent ChoCH or BOS confirmation
   - Liquidity sweeps that occurred

3. **Construct Trade Setup**
   - Entry: At FVG/OB in discount (for longs) or premium (for shorts)
   - Stop: Below/above the liquidity sweep
   - Target: Opposite liquidity pool

4. **Grade the Setup**
   - A+: All confluence factors, in killzone, clear bias
   - A: Most factors aligned, minor concerns
   - B: Decent setup, missing some confluence
   - C: Skip - wait for better setup

### Step 3: Present to User

Format the response as:

```
## [SYMBOL] SMC Analysis

### Bias: [BULLISH/BEARISH]
[Explain why based on structure, premium/discount zone, and liquidity]

### Current Setup: [GRADE]

**Direction:** [LONG/SHORT]

**Entry Zone:** $XX,XXX - $XX,XXX
- Reasoning: [Why this zone - FVG? OB? Sweep level?]

**Stop Loss:** $XX,XXX
- Reasoning: [Below sweep low / Above sweep high]
- Risk: X.X%

**Targets:**
| Target | Price | R:R | Reasoning |
|--------|-------|-----|-----------|
| TP1 | $XX,XXX | 1:2 | [Nearest liquidity] |
| TP2 | $XX,XXX | 1:3 | [Major BSL/SSL] |
| TP3 | $XX,XXX | 1:5 | [HTF liquidity] |

### Confluence Factors
- [ ] HTF bias aligned
- [ ] Price in discount/premium
- [ ] Recent sweep occurred
- [ ] ChoCH confirmed
- [ ] FVG/OB present at entry
- [ ] In killzone (if applicable)

### Warnings
- [Any concerns about the setup]

### Narrative
[2-3 sentence explanation of the trade thesis in plain English]

---
*This is analysis, not financial advice. Always manage risk.*
```

## Web App Integration

The web app at `localhost:3001` provides:
- Visual chart with overlays (BSL, SSL, EQ, FVGs)
- Symbol selector (BTC, ETH, SOL)
- Timeframe buttons (1m to 1W)
- "Analyze SMC" button for mechanical data

**To start the web app:**
```bash
cd /Users/abuusama/projects/bots/signals && bun dev
```

The web app shows the **mechanical data**. This skill provides the **AI interpretation**.

## API Reference

### GET /api/smc-analyze

**Parameters:**
| Param | Default | Options |
|-------|---------|---------|
| symbol | BTC/USDT | BTC/USDT, ETH/USDT, SOL/USDT |
| timeframe | 1h | 1m, 5m, 15m, 1h, 4h, 1d, 1w |
| style | intraday | scalp, intraday, swing, position |

**Response:**
```json
{
  "symbol": "BTC/USDT",
  "timeframe": "1h",
  "style": "intraday",
  "currentPrice": 88338.29,
  "structure": {
    "bias": "BULLISH",
    "priceZone": "PREMIUM",
    "range": { "high": 89399.97, "low": 84450.01 }
  },
  "liquidity": {
    "bsl": [{ "price": 92754.00, "strength": "strong" }],
    "ssl": [{ "price": 84450.01, "strength": "strong" }]
  },
  "inefficiencies": {
    "fvgs": [{ "type": "bull", "high": 88049.89, "low": 87946.96 }]
  },
  "orderFlow": {
    "recentSwings": [...],
    "structureBreaks": [{ "type": "CHOCH", "direction": "up", "price": 88339.27 }]
  },
  "atr": 132.75
}
```

## ICT Methodology Reference

### Premium/Discount Zones
- **Premium**: Above equilibrium (50% of range) - look for shorts
- **Discount**: Below equilibrium - look for longs

### Liquidity Levels
- **BSL (Buy-Side Liquidity)**: Swing highs where stops rest - target for longs
- **SSL (Sell-Side Liquidity)**: Swing lows where stops rest - target for shorts

### Entry Triggers
- **BOS (Break of Structure)**: Continuation signal
- **ChoCH (Change of Character)**: Reversal signal
- **Sweep**: Liquidity grab before reversal

### Killzones (EST)
| Session | Time | Best For |
|---------|------|----------|
| London Open | 02:00-05:00 | Manipulation moves |
| NY AM | 07:00-10:00 | Highest probability |
| London Close | 10:00-12:00 | Reversal setups |

## Example Analysis

User: "analyze BTC"

1. Fetch data:
```bash
curl "http://localhost:3001/api/smc-analyze?symbol=BTC/USDT&timeframe=1h"
```

2. Interpret the response and provide:

```
## BTC/USDT SMC Analysis

### Bias: BULLISH
Price is currently at $88,338 in the PREMIUM zone of the 1H range ($84,450 - $89,399).
However, we just had a CHOCH to the upside at $88,339, suggesting bullish continuation
despite being in premium.

### Current Setup: B+

**Direction:** LONG (on pullback)

**Entry Zone:** $87,946 - $88,049
- Reasoning: Unfilled bullish FVG from recent impulse move

**Stop Loss:** $87,500
- Reasoning: Below the recent BOS level at $87,514
- Risk: 0.95%

**Targets:**
| Target | Price | R:R | Reasoning |
|--------|-------|-----|-----------|
| TP1 | $89,400 | 1:1.7 | Range high / BSL |
| TP2 | $90,634 | 1:3.2 | Next BSL level |
| TP3 | $92,754 | 1:5.7 | Major BSL |

### Confluence Factors
- [x] ChoCH confirmed bullish
- [x] FVG present at entry zone
- [ ] Not in killzone currently
- [ ] Price in premium (slight concern)

### Warnings
- Price is in premium zone - ideal longs are from discount
- Consider waiting for deeper pullback to $87,500 area

### Narrative
BTC showed a change of character to the upside, breaking recent structure.
The setup suggests buying a pullback into the unfilled FVG around $88,000,
with stops below recent structure and targets at the BSL levels above.
```

## Important Notes

- **Never guarantee outcomes** - present as "the analysis suggests" not "this will happen"
- **Always include risk warnings** - trading involves risk of loss
- **Grade setups honestly** - don't oversell B/C setups as A+ setups
- **Mention timing** - note if we're in a killzone or not
