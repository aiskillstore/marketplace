# SMC Detector Output Schema

TypeScript interfaces for the structured output produced by `smc-detector.ts`.

## Root Schema

```typescript
interface SMCAnalysis {
  meta: AnalysisMeta;
  structure: MarketStructure;
  liquidity: LiquidityAnalysis;
  inefficiencies: InefficiencyAnalysis;
  orderFlow: OrderFlowAnalysis;
  context: MarketContext;
}
```

---

## Meta Information

```typescript
interface AnalysisMeta {
  symbol: string;           // e.g., "BTC/USDT"
  timeframe: string;        // e.g., "4H", "1D", "15m"
  candleCount: number;      // Total candles analyzed
  startTime: number;        // First candle timestamp
  endTime: number;          // Last candle timestamp
  analysisTime: string;     // ISO timestamp of analysis
  config: SMCConfig;        // Configuration used
}

interface SMCConfig {
  swingLookback: number;
  obMinMoveATR: number;
  obMaxCandles: number;
  obRequireFVG: boolean;
  obRequireStructureBreak: boolean;
  atrPeriod: number;
}
```

---

## Market Structure

```typescript
interface MarketStructure {
  currentTrend: 'bullish' | 'bearish' | 'ranging';
  swings: SwingPoint[];
  structureBreaks: StructureBreak[];
  lastChoCH: StructureBreak | null;
  lastBOS: StructureBreak | null;
  trendSequence: TrendLeg[];
}

interface SwingPoint {
  type: 'high' | 'low';
  index: number;            // Candle index in array
  price: number;
  timestamp: number;
  swept: boolean;           // Has this level been swept?
  sweepIndex?: number;      // Which candle swept it
  strength: number;         // How many candles on each side (lookback used)
}

interface StructureBreak {
  type: 'bos' | 'choch';
  direction: 'bullish' | 'bearish';
  index: number;            // Candle that broke structure
  timestamp: number;
  brokenLevel: number;      // Price of swing that was broken
  swingIndex: number;       // Index of the broken swing
  closePrice: number;       // Close of the breaking candle
  displacement: number;     // How far past the level (in price)
}

interface TrendLeg {
  startIndex: number;
  endIndex: number;
  direction: 'bullish' | 'bearish';
  swingHigh: SwingPoint;
  swingLow: SwingPoint;
  range: number;            // High - Low
  fibLevels: FibLevel[];
}

interface FibLevel {
  level: number;            // 0, 0.236, 0.382, 0.5, 0.618, 0.705, 0.79, 1
  price: number;
  label: string;            // "0%", "OTE Start", "Equilibrium", etc.
}
```

---

## Liquidity Analysis

```typescript
interface LiquidityAnalysis {
  buySideLevels: LiquidityLevel[];    // Unswept swing highs
  sellSideLevels: LiquidityLevel[];   // Unswept swing lows
  recentSweeps: LiquiditySweep[];
  equalHighs: EqualLevel[];
  equalLows: EqualLevel[];
}

interface LiquidityLevel {
  swing: SwingPoint;
  significance: 'major' | 'minor';    // Based on lookback strength
  distanceFromCurrent: number;        // Price distance
  percentFromCurrent: number;         // Percentage distance
}

interface LiquiditySweep {
  type: 'buy-side' | 'sell-side';
  index: number;                      // Candle that did the sweep
  timestamp: number;
  sweptSwing: SwingPoint;
  sweepHigh: number;                  // Wick extreme
  sweepLow: number;
  closePrice: number;                 // Where it closed (inside original level)
  rejectionStrength: number;          // 0-1, how strong the rejection
  wickRatio: number;                  // Wick size / total range
}

interface EqualLevel {
  type: 'highs' | 'lows';
  swings: SwingPoint[];               // The equal swing points
  price: number;                      // Average price of the level
  tolerance: number;                  // How close they are (in %)
}
```

---

## Inefficiency Analysis

```typescript
interface InefficiencyAnalysis {
  fvgs: FVG[];
  unfilledFVGs: FVG[];
  partiallyFilledFVGs: FVG[];
  volumeImbalances: VolumeImbalance[];
}

interface FVG {
  type: 'bullish' | 'bearish';
  index: number;                      // Middle candle (the impulse)
  timestamp: number;
  gapHigh: number;                    // Top of the gap
  gapLow: number;                     // Bottom of the gap
  gapSize: number;                    // In price terms
  gapSizeATR: number;                 // As multiple of ATR
  consequentEncroachment: number;     // 50% level (CE)
  filled: boolean;
  fillPercent: number;                // 0-100, how much filled
  fillIndex?: number;                 // When it started filling
  fullFillIndex?: number;             // When completely filled
}

interface VolumeImbalance {
  index: number;
  timestamp: number;
  gapHigh: number;
  gapLow: number;
  direction: 'bullish' | 'bearish';
}
```

---

## Order Flow Analysis

```typescript
interface OrderFlowAnalysis {
  orderBlocks: OrderBlock[];
  unmitigatedOBs: OrderBlock[];
  breakerBlocks: BreakerBlock[];
  propulsionBlocks: PropulsionBlock[];
}

interface OrderBlock {
  type: 'bullish' | 'bearish';
  index: number;
  timestamp: number;
  high: number;                       // Zone top
  low: number;                        // Zone bottom
  open: number;
  close: number;
  body: [number, number];             // [bodyLow, bodyHigh]
  mitigated: boolean;
  mitigationIndex?: number;
  mitigationPercent?: number;         // How deep into OB price went
  confidence: number;                 // 0-1 based on criteria match
  criteria: OBCriteria;
}

interface OBCriteria {
  moveSize: number;                   // ATR multiple of resulting move
  brokeStructure: boolean;
  createdFVG: boolean;
  withinCandles: number;              // How many candles was the move
}

interface BreakerBlock {
  originalOB: OrderBlock;
  breakIndex: number;                 // When OB failed
  breakTimestamp: number;
  newDirection: 'bullish' | 'bearish';
  retested: boolean;
  retestIndex?: number;
}

interface PropulsionBlock {
  orderBlock: OrderBlock;
  containingFVG: FVG;                 // The FVG this OB sits within
}
```

---

## Market Context

```typescript
interface MarketContext {
  currentPrice: number;
  currentIndex: number;
  atr: number;                        // Current ATR value
  atrHistory: number[];               // ATR for each candle
  premiumDiscount: PremiumDiscountZone;
  rangeAnalysis: RangeAnalysis;
  nearestLevels: NearestLevels;
}

interface PremiumDiscountZone {
  rangeHigh: number;
  rangeLow: number;
  equilibrium: number;                // 50% level
  currentZone: 'premium' | 'discount' | 'equilibrium';
  currentPosition: number;            // 0-1, where in range
  fibLevels: FibLevel[];
}

interface RangeAnalysis {
  dailyRange: number;
  weeklyRange: number;
  currentRangePercent: number;        // Today's range as % of average
  volatilityState: 'expansion' | 'contraction' | 'normal';
}

interface NearestLevels {
  resistanceLevels: PriceLevel[];     // Nearest levels above
  supportLevels: PriceLevel[];        // Nearest levels below
}

interface PriceLevel {
  price: number;
  type: 'swing' | 'ob' | 'fvg' | 'breaker';
  distance: number;
  distanceATR: number;
  details: SwingPoint | OrderBlock | FVG | BreakerBlock;
}
```

---

## Example Output

```json
{
  "meta": {
    "symbol": "BTC/USDT",
    "timeframe": "4H",
    "candleCount": 100,
    "startTime": 1702900800,
    "endTime": 1704340800,
    "analysisTime": "2024-01-04T12:00:00Z",
    "config": {
      "swingLookback": 3,
      "obMinMoveATR": 2,
      "obMaxCandles": 5,
      "obRequireFVG": false,
      "obRequireStructureBreak": true,
      "atrPeriod": 14
    }
  },
  "structure": {
    "currentTrend": "bearish",
    "swings": [...],
    "structureBreaks": [...],
    "lastChoCH": {
      "type": "choch",
      "direction": "bearish",
      "index": 47,
      "brokenLevel": 41200,
      "swingIndex": 38
    },
    "lastBOS": null
  },
  "liquidity": {
    "buySideLevels": [
      { "swing": {...}, "significance": "major", "distanceFromCurrent": 950 }
    ],
    "sellSideLevels": [
      { "swing": {...}, "significance": "major", "distanceFromCurrent": 300 }
    ],
    "recentSweeps": [
      { "type": "buy-side", "index": 52, "rejectionStrength": 0.72 }
    ]
  },
  "inefficiencies": {
    "fvgs": [...],
    "unfilledFVGs": [
      { "type": "bullish", "gapHigh": 41650, "gapLow": 41500, "fillPercent": 0 }
    ]
  },
  "orderFlow": {
    "orderBlocks": [...],
    "unmitigatedOBs": [
      { "type": "bearish", "high": 42050, "low": 41900, "confidence": 0.85 }
    ]
  },
  "context": {
    "currentPrice": 41100,
    "atr": 450,
    "premiumDiscount": {
      "rangeHigh": 42150,
      "rangeLow": 40800,
      "equilibrium": 41475,
      "currentZone": "discount"
    }
  }
}
```
