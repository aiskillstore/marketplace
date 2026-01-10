# Narrative Templates for SMC Analysis

Templates and examples for generating narrative interpretations from detection output.

## Table of Contents
1. [Prompt Structure](#prompt-structure)
2. [Narrative Components](#narrative-components)
3. [Example Narratives](#example-narratives)
4. [Tone Guidelines](#tone-guidelines)

---

## Prompt Structure

### Basic Analysis Prompt

```
Given this SMC analysis for {symbol} on the {timeframe} timeframe:

{JSON analysis output}

Generate a narrative interpretation covering:
1. Current market structure and trend bias
2. Key liquidity levels (unswept highs/lows)
3. Relevant order blocks and FVGs
4. Potential scenarios

Use SMC terminology. Be objective—present scenarios, not predictions.
```

### Focused Prompt (Specific Aspect)

```
Given this SMC analysis:

{JSON analysis output}

Focus specifically on liquidity. Explain:
- Where is unswept liquidity sitting?
- What recent sweeps occurred and what do they suggest?
- What liquidity targets are nearest to current price?
```

### Scenario Planning Prompt

```
Given this SMC analysis:

{JSON analysis output}

Present two scenarios:
1. Bullish case: What would need to happen? What are the targets?
2. Bearish case: What would need to happen? What are the targets?

Include confluence factors for each scenario.
```

---

## Narrative Components

### 1. Structure Summary

Start with the big picture:

**Template:**
```
The {timeframe} chart shows {bullish/bearish/ranging} structure. 
{If recent ChoCH}: A change of character occurred at {price} when price broke {below/above} the {swing type} at index {N}, signaling potential shift from {old trend} to {new trend}.
{If recent BOS}: Structure continues {direction} with the most recent break of structure at {price}.
```

**Example:**
> "The 4H chart shows bearish structure following a ChoCH at 41,200. This break below the previous swing low shifted bias from bullish to bearish."

### 2. Liquidity Analysis

Identify where stops are sitting:

**Template:**
```
Buy-side liquidity:
- {Major level} at {price} ({distance} away) - {context}
- {Minor levels if relevant}

Sell-side liquidity:
- {Major level} at {price} ({distance} away) - {context}

Recent sweeps: {Describe any sweeps and their implications}
```

**Example:**
> "Sell-side liquidity sits at 40,800 (300 points below current price)—this swing low from index 38 hasn't been swept and represents the obvious downside target. Above, buy-side at 42,150 was already swept at index 52 with strong rejection (0.72 rejection strength), suggesting that high is now protected unless structure shifts bullish."

### 3. Order Flow Zones

Describe relevant OBs and FVGs:

**Template:**
```
Order Blocks:
- {Bullish/Bearish} OB at {range} from index {N} - {mitigated/unmitigated}
- Confidence: {score} based on {criteria}

Fair Value Gaps:
- {Bullish/Bearish} FVG at {range} - {filled/unfilled/partially filled}
- CE (50%) at {price}
```

**Example:**
> "An unmitigated bearish OB sits at 41,900-42,050 (confidence 0.85)—this formed during the displacement that created the ChoCH. Any retrace into this zone would be logical short territory. Below, a bullish FVG at 41,500-41,650 is still unfilled with CE at 41,575."

### 4. Context & Position

Where is price relative to the range:

**Template:**
```
Current price ({price}) is in {premium/discount} relative to the {range description}.
Equilibrium: {eq price}
ATR: {atr value}
```

**Example:**
> "Currently at 41,100, price is in discount (below equilibrium at 41,475). This positions longs more favorably from a premium/discount perspective, though structure remains bearish."

### 5. Scenario Building

Present possibilities, not predictions:

**Template:**
```
Scenario A ({direction}):
- Trigger: {what needs to happen}
- Confluence: {supporting factors}
- Target: {logical target level}

Scenario B ({direction}):
- Trigger: {what needs to happen}
- Confluence: {supporting factors}
- Target: {logical target level}
```

**Example:**
> "Bearish continuation: If price fails to reclaim the 41,500 FVG, expect a sweep of sell-side at 40,800. Confluence: bearish structure, unmitigated bearish OB above, price rejected from premium.
>
> Bullish reversal: A sweep of 40,800 followed by reclaim above 41,500 FVG would suggest the sell-side sweep was manipulation for accumulation. Target: return to the unmitigated bearish OB at 41,900-42,050."

---

## Example Narratives

### Example 1: Bearish Setup

**Input context:** Bearish structure, recent ChoCH, unswept SSL, unmitigated bearish OB

**Narrative:**
> "BTC 4H shows clear bearish structure following the ChoCH at 41,200 (index 47). The break below that swing low shifted the narrative from the prior uptrend.
>
> Liquidity positioning favors continuation: sell-side at 40,800 remains unswept—that's 300 points of downside target. Meanwhile, buy-side at 42,150 was already swept at index 52 with strong rejection (72% wick ratio), making that a protected high.
>
> On any retrace, the bearish OB at 41,900-42,050 provides a logical entry zone for shorts. This OB has 0.85 confidence—it preceded displacement that broke structure and created an FVG.
>
> Currently trading at 41,100, price sits in discount but that's less relevant in bearish structure. The path of least resistance points to the 40,800 SSL target. A bullish case would require sweeping that SSL and reclaiming back above the 41,500 FVG—watch for reaction there."

### Example 2: Ranging/Uncertain

**Input context:** No clear trend, equal highs forming, mixed signals

**Narrative:**
> "ETH 1H is in a ranging state—no clear HH/HL or LH/LL sequence. The most notable feature is equal highs forming at 2,450 (indexes 23, 41, 58), creating a significant liquidity magnet above.
>
> This EQH pattern is textbook liquidity engineering. The repeated touches make it obvious, which typically means it will eventually be swept. The question is whether the sweep leads to continuation above or rejection back into range.
>
> Below, a single swing low at 2,380 holds sell-side liquidity.
>
> Given the lack of structure, bias is neutral. Two scenarios: (1) Sweep of 2,450 EQH with acceptance above suggests breakout—look for pullback to the breaker for longs. (2) Sweep of 2,450 with rejection back below suggests the high was a trap—expect rotation to 2,380 SSL.
>
> Wait for the sweep and the reaction before establishing directional bias."

### Example 3: Confluence Setup

**Input context:** FVG + OB overlap, sweep just occurred, structure break

**Narrative:**
> "SOL 15m just printed a high-confluence setup. Here's the stack:
>
> 1. Sell-side sweep: The 18.50 swing low was swept at index 89 with immediate rejection (85% wick ratio). This is classic manipulation—stops triggered, then reversal.
>
> 2. ChoCH confirmation: The candle at index 91 closed above 18.80, breaking the most recent swing high and shifting structure bullish.
>
> 3. FVG + OB confluence: A bullish FVG at 18.60-18.72 overlaps with a bullish OB from index 87. This is a propulsion block—OB sitting inside FVG.
>
> The setup: Price swept sell-side, shifted structure bullish, and left an unmitigated propulsion block. If price retraces to the 18.60-18.72 zone and holds, the target is the unswept buy-side at 19.20.
>
> Invalidation: Close below 18.50 (the swept low) would negate the bullish structure shift."

---

## Tone Guidelines

### Do

- Use present tense for current state, past tense for what happened
- Be specific with prices and indexes
- Quantify when possible (rejection strength, ATR multiples, percentages)
- Present multiple scenarios
- Acknowledge uncertainty ("suggests," "indicates," "would likely")
- Use SMC terminology naturally

### Don't

- Make definitive predictions ("price WILL go to X")
- Give trading advice ("you should buy here")
- Ignore contradictory signals
- Over-emphasize single patterns
- Use excessive hedging language
- Explain basic SMC concepts (assume reader knows terminology)

### Vocabulary

**Prefer:**
- "suggests" over "means"
- "indicates" over "proves"
- "logical target" over "price target"
- "favors" over "guarantees"
- "potential" over "certain"

**Avoid:**
- "definitely"
- "always"
- "never"
- "guaranteed"
- "you should"

---

## Output Formats

### Brief Summary (Twitter-style)

```
{Symbol} {TF}: {Trend} structure. 
Key levels: BSL {price}, SSL {price}
Watching: {main zone/level}
Bias: {direction} toward {target}
```

### Standard Analysis (Default)

4-6 paragraphs covering structure, liquidity, zones, scenarios.

### Detailed Report

Full breakdown with all components, suitable for documentation or journaling.

### Chart Annotation Format

For use with visualization:

```json
{
  "annotations": [
    { "type": "label", "price": 42150, "text": "BSL (swept)", "side": "top" },
    { "type": "zone", "high": 42050, "low": 41900, "color": "red", "label": "Bearish OB" },
    { "type": "zone", "high": 41650, "low": 41500, "color": "blue", "label": "Bullish FVG" }
  ],
  "trendline": { "start": [index1, price1], "end": [index2, price2] },
  "narrative": "Brief explanation..."
}
```
