# Chart Markup Guide

This guide teaches how to annotate SMC charts using the Chart Markup Language (CML).

## Table of Contents
1. [Quick Reference](#quick-reference)
2. [Reference Syntax](#reference-syntax)
3. [Element Types](#element-types)
4. [Color Presets](#color-presets)
5. [Complete Examples](#complete-examples)
6. [Update Commands](#update-commands)
7. [Common Patterns](#common-patterns)

---

## Quick Reference

```json
{
  "meta": { "title": "BTC 4H", "theme": "dark" },
  "elements": [
    { "id": "ob1", "type": "rect", "time": ["#45", "#end"], "price": ["$41900", "$42050"], "fill": "ob_bear", "label": "Bearish OB" },
    { "id": "eq", "type": "hline", "price": "@context.premiumDiscount.equilibrium", "color": "eq", "style": "dashed", "label": "EQ" },
    { "id": "sweep", "type": "marker", "time": "#52", "position": "above", "shape": "arrow_down", "color": "sweep", "label": "BSL Sweep" }
  ]
}
```

---

## Reference Syntax

### Time References

| Syntax | Meaning | Example |
|--------|---------|---------|
| `#N` | Candle at index N | `"#45"` → candle 45 |
| `#-N` | N candles from end | `"#-10"` → 10th from last |
| `#start` | First candle | `"#start"` |
| `#end` | Last candle | `"#end"` |
| `@path` | From analysis | `"@structure.lastChoCH.index"` |

### Price References

| Syntax | Meaning | Example |
|--------|---------|---------|
| `$N` | Price level N | `"$42150"` |
| `N` | Raw number | `42150` |
| `@path` | From analysis | `"@ob.bear.0.high"` |

### Analysis Path Shortcuts

| Shortcut | Resolves To |
|----------|-------------|
| `@ob.bull.N` | Nth bullish order block |
| `@ob.bear.N` | Nth bearish order block |
| `@ob.unmit.N` | Nth unmitigated OB |
| `@fvg.bull.N` | Nth bullish FVG |
| `@fvg.bear.N` | Nth bearish FVG |
| `@fvg.unfilled.N` | Nth unfilled FVG |
| `@swing.high.N` | Nth swing high |
| `@swing.low.N` | Nth swing low |
| `@sweep.N` | Nth liquidity sweep |
| `@bsl.N` | Nth buy-side liquidity level |
| `@ssl.N` | Nth sell-side liquidity level |
| `@structure.lastChoCH` | Most recent ChoCH |
| `@structure.lastBOS` | Most recent BOS |
| `@context.premiumDiscount.equilibrium` | 50% equilibrium |
| `@context.currentPrice` | Current price |
| `@context.atr` | Current ATR |

**Property access:** Append `.index`, `.price`, `.high`, `.low`, `.timestamp`, etc.

```
@ob.bear.0.high      → First bearish OB's high price
@swing.low.0.price   → First swing low's price  
@sweep.0.index       → First sweep's candle index
```

---

## Element Types

### rect (Rectangle)

For order blocks, FVGs, and custom zones.

```json
{
  "id": "ob1",
  "type": "rect",
  "time": ["#45", "#end"],
  "price": ["$41900", "$42050"],
  "fill": "ob_bear",
  "border": "#ff0000",
  "borderWidth": 1,
  "label": "Bearish OB",
  "labelPos": "top"
}
```

| Property | Required | Default | Description |
|----------|----------|---------|-------------|
| `time` | Yes | - | `[start, end]` time range |
| `price` | Yes | - | `[low, high]` price range |
| `fill` | No | gray | Fill color |
| `border` | No | none | Border color |
| `borderWidth` | No | 0 | Border width |
| `label` | No | - | Text label |
| `opacity` | No | 1 | 0-1 opacity |

### hline (Horizontal Line)

For price levels, liquidity, equilibrium.

```json
{
  "id": "bsl1",
  "type": "hline",
  "price": "@swing.high.0.price",
  "color": "bsl",
  "style": "dashed",
  "width": 1,
  "label": "BSL"
}
```

| Property | Required | Default | Description |
|----------|----------|---------|-------------|
| `price` | Yes | - | Price level |
| `color` | No | neutral | Line color |
| `width` | No | 1 | Line width |
| `style` | No | solid | solid/dashed/dotted |
| `label` | No | - | Right-side label |

### vline (Vertical Line)

For time markers, events.

```json
{
  "id": "event1",
  "type": "vline",
  "time": "#52",
  "color": "choch",
  "style": "dashed",
  "label": "ChoCH"
}
```

### marker (Candle Marker)

For sweeps, structure breaks, points of interest.

```json
{
  "id": "sweep1",
  "type": "marker",
  "time": "#52",
  "position": "above",
  "shape": "arrow_down",
  "color": "sweep",
  "label": "Sweep"
}
```

| Property | Required | Default | Description |
|----------|----------|---------|-------------|
| `time` | Yes | - | Candle index |
| `price` | No | auto | Price (auto = candle high/low) |
| `position` | No | above | above/below/at |
| `shape` | No | circle | circle/square/triangle/arrow_up/arrow_down/diamond |
| `color` | No | neutral | Marker color |
| `label` | No | - | Text label |

### zone (Full-Width Zone)

For premium/discount areas.

```json
{
  "id": "premium",
  "type": "zone",
  "price": ["@context.premiumDiscount.equilibrium", "@context.premiumDiscount.rangeHigh"],
  "fill": "premium",
  "label": "Premium"
}
```

### trend (Trend Line)

For structure lines, channels.

```json
{
  "id": "trend1",
  "type": "trend",
  "from": { "time": "#20", "price": "$40500" },
  "to": { "time": "#50", "price": "$42000" },
  "color": "bull_trend",
  "width": 2,
  "style": "solid"
}
```

### arrow (Arrow)

For showing direction, flow.

```json
{
  "id": "move1",
  "type": "arrow",
  "from": { "time": "#45", "price": "$41000" },
  "to": { "time": "#55", "price": "$40500" },
  "color": "bear_trend",
  "width": 2
}
```

### label (Text Annotation)

For custom text.

```json
{
  "id": "note1",
  "type": "label",
  "time": "#50",
  "price": "$41500",
  "text": "Potential reversal zone",
  "color": "#ffffff",
  "background": "rgba(0,0,0,0.7)"
}
```

### range (Range Box with EQ)

For premium/discount range with equilibrium.

```json
{
  "id": "range1",
  "type": "range",
  "time": ["#30", "#end"],
  "price": ["@swing.low.0.price", "@swing.high.0.price"],
  "fill": "rgba(100,100,100,0.1)"
}
```

---

## Color Presets

Use these names instead of hex/rgba for consistency:

| Name | Use Case | Color |
|------|----------|-------|
| `ob_bull` | Bullish order block | Green 30% |
| `ob_bear` | Bearish order block | Red 30% |
| `fvg_bull` | Bullish FVG | Blue 25% |
| `fvg_bear` | Bearish FVG | Orange 25% |
| `swing_high` | Swing high marker | Red |
| `swing_low` | Swing low marker | Green |
| `bos` | Break of structure | Blue |
| `choch` | Change of character | Purple |
| `sweep` | Liquidity sweep | Orange |
| `bsl` | Buy-side liquidity | Red |
| `ssl` | Sell-side liquidity | Green |
| `premium` | Premium zone | Red 8% |
| `discount` | Discount zone | Green 8% |
| `eq` | Equilibrium | Gray |
| `neutral` | Neutral/default | Gray |
| `highlight` | Highlight | Yellow |
| `bull_trend` | Bullish trend | Green |
| `bear_trend` | Bearish trend | Red |

---

## Complete Examples

### Example 1: Basic SMC Markup

Marking a bearish setup with OB, FVG, and liquidity levels.

```json
{
  "meta": {
    "title": "BTC 4H - Bearish Setup",
    "theme": "dark",
    "width": 1200,
    "height": 800
  },
  "elements": [
    {
      "id": "bearish_ob",
      "type": "rect",
      "time": ["#47", "#end"],
      "price": ["@ob.bear.0.low", "@ob.bear.0.high"],
      "fill": "ob_bear",
      "label": "Bearish OB"
    },
    {
      "id": "bullish_fvg",
      "type": "rect",
      "time": ["#42", "#-5"],
      "price": ["@fvg.bull.0.gapLow", "@fvg.bull.0.gapHigh"],
      "fill": "fvg_bull",
      "label": "FVG"
    },
    {
      "id": "ssl",
      "type": "hline",
      "price": "@ssl.0.swing.price",
      "color": "ssl",
      "style": "dashed",
      "label": "SSL Target"
    },
    {
      "id": "eq_line",
      "type": "hline",
      "price": "@context.premiumDiscount.equilibrium",
      "color": "eq",
      "style": "dotted",
      "label": "EQ"
    },
    {
      "id": "choch_marker",
      "type": "marker",
      "time": "@structure.lastChoCH.index",
      "position": "below",
      "shape": "triangle",
      "color": "choch",
      "label": "ChoCH"
    },
    {
      "id": "discount_zone",
      "type": "zone",
      "price": ["@context.premiumDiscount.rangeLow", "@context.premiumDiscount.equilibrium"],
      "fill": "discount",
      "label": "Discount"
    }
  ]
}
```

### Example 2: Liquidity Sweep Setup

Marking a sweep and reaction.

```json
{
  "meta": { "title": "ETH - Sweep & React", "theme": "dark" },
  "elements": [
    {
      "id": "swept_level",
      "type": "hline",
      "price": "@sweep.0.sweptSwing.price",
      "color": "ssl",
      "style": "solid",
      "label": "Swept Low"
    },
    {
      "id": "sweep_marker",
      "type": "marker",
      "time": "@sweep.0.index",
      "position": "below",
      "shape": "arrow_up",
      "color": "sweep",
      "label": "Sweep"
    },
    {
      "id": "reaction_ob",
      "type": "rect",
      "time": ["@ob.bull.0.index", "#end"],
      "price": ["@ob.bull.0.low", "@ob.bull.0.high"],
      "fill": "ob_bull",
      "label": "Reaction OB"
    },
    {
      "id": "target",
      "type": "hline",
      "price": "@bsl.0.swing.price",
      "color": "bsl",
      "style": "dashed",
      "label": "Target"
    }
  ]
}
```

### Example 3: Range Analysis

Marking a trading range with premium/discount.

```json
{
  "meta": { "title": "SOL - Range Analysis", "theme": "dark" },
  "elements": [
    {
      "id": "range_box",
      "type": "range",
      "time": ["#20", "#end"],
      "price": ["@swing.low.0.price", "@swing.high.0.price"],
      "fill": "rgba(150,150,150,0.05)"
    },
    {
      "id": "premium_zone",
      "type": "zone",
      "price": ["@context.premiumDiscount.equilibrium", "@context.premiumDiscount.rangeHigh"],
      "fill": "premium",
      "label": "Premium"
    },
    {
      "id": "discount_zone",
      "type": "zone",
      "price": ["@context.premiumDiscount.rangeLow", "@context.premiumDiscount.equilibrium"],
      "fill": "discount",
      "label": "Discount"
    },
    {
      "id": "eqh",
      "type": "hline",
      "price": "@swing.high.0.price",
      "color": "bsl",
      "style": "solid",
      "width": 2,
      "label": "EQH - BSL"
    }
  ]
}
```

---

## Update Commands

For iterative refinement, send commands instead of full markup:

### Add Element

```json
{
  "commands": [
    {
      "op": "add",
      "element": {
        "id": "new_line",
        "type": "hline",
        "price": "$41500",
        "color": "highlight",
        "label": "Key Level"
      }
    }
  ]
}
```

### Update Element

```json
{
  "commands": [
    {
      "op": "update",
      "id": "ob1",
      "set": {
        "fill": "rgba(255,0,0,0.5)",
        "label": "High Probability OB"
      }
    }
  ]
}
```

### Remove Element

```json
{
  "commands": [
    { "op": "remove", "id": "fvg1" }
  ]
}
```

### Move Element

```json
{
  "commands": [
    {
      "op": "move",
      "id": "ob1",
      "time": ["#50", "#end"]
    }
  ]
}
```

### Style Element

```json
{
  "commands": [
    {
      "op": "style",
      "id": "ob1",
      "color": "highlight",
      "opacity": 0.8
    }
  ]
}
```

### Multiple Commands

```json
{
  "commands": [
    { "op": "remove", "id": "old_fvg" },
    { "op": "update", "id": "ob1", "set": { "label": "Mitigated OB" } },
    { "op": "add", "element": { "id": "note", "type": "label", "time": "#55", "price": "$41000", "text": "Entry zone" } }
  ]
}
```

---

## Common Patterns

### Pattern 1: Mark All Unmitigated OBs

```json
{
  "elements": [
    { "id": "ob_unmit_0", "type": "rect", "time": ["@ob.unmit.0.index", "#end"], "price": ["@ob.unmit.0.low", "@ob.unmit.0.high"], "fill": "@ob.unmit.0.type === 'bullish' ? 'ob_bull' : 'ob_bear'" }
  ]
}
```

*Note: For dynamic coloring, generate multiple elements based on analysis data.*

### Pattern 2: Swept vs Unswept Levels

Mark unswept levels solid, swept levels dashed:

```json
{
  "elements": [
    { "id": "bsl_active", "type": "hline", "price": "@bsl.0.swing.price", "color": "bsl", "style": "solid", "label": "BSL (active)" },
    { "id": "swept_level", "type": "hline", "price": "@sweep.0.sweptSwing.price", "color": "neutral", "style": "dashed", "opacity": 0.5 }
  ]
}
```

### Pattern 3: FVG with CE Line

Mark FVG and its 50% (Consequent Encroachment):

```json
{
  "elements": [
    { "id": "fvg", "type": "rect", "time": ["@fvg.bull.0.index", "#end"], "price": ["@fvg.bull.0.gapLow", "@fvg.bull.0.gapHigh"], "fill": "fvg_bull" },
    { "id": "ce", "type": "hline", "price": "@fvg.bull.0.consequentEncroachment", "color": "eq", "style": "dotted", "label": "CE" }
  ]
}
```

### Pattern 4: Structure Break with Arrow

Show direction of structure break:

```json
{
  "elements": [
    { "id": "choch_line", "type": "hline", "price": "@structure.lastChoCH.brokenLevel", "color": "choch", "style": "dashed" },
    { "id": "choch_marker", "type": "marker", "time": "@structure.lastChoCH.index", "shape": "triangle_down", "color": "choch", "label": "ChoCH" }
  ]
}
```

---

## Workflow Summary

1. **Initial render:** Send full `ChartMarkup` with all elements
2. **Review:** View screenshot, assess markup
3. **Iterate:** Send `UpdatePayload` with commands to add/remove/update
4. **Finalize:** When satisfied, write narrative referencing the chart

**Token efficiency:**
- Full markup: ~20-50 tokens per element
- Update command: ~10-20 tokens per change
- Over 5 iterations: Commands save 60-80% tokens vs full rewrites
