---
name: architecture-reference
description: Quick reference for Portfolio Buddy 2 project structure. Use when: adding new features, modifying existing components, understanding data flow, or onboarding to the codebase. Contains component hierarchy, hook patterns, and utility functions.
---

# Portfolio Buddy 2 - Architecture Reference

## Component Hierarchy

```
App.tsx (351 lines)
├── Header
│   └── App title and branding
├── UploadSection
│   ├── File upload to Supabase
│   ├── CSV parsing and validation
│   └── Error handling
├── ErrorList
│   └── Display parsing/validation errors
├── UploadedFilesList
│   └── List of successfully uploaded files
├── AnalyticsControls
│   ├── Toggle Metrics view
│   ├── Toggle Portfolio view
│   └── Toggle Correlation view
├── PortfolioSection (591 lines - NEEDS REFACTOR!)
│   ├── usePortfolio hook (date filtering)
│   ├── useContractMultipliers hook
│   ├── Chart.js equity curves
│   ├── Portfolio statistics
│   ├── ContractInput components
│   ├── MasterContractControl
│   └── MetricsTable integration
├── CorrelationSection
│   ├── CorrelationHeatmap (Chart.js)
│   ├── Spearman correlation
│   └── Pearson correlation
├── MetricsTable (242 lines)
│   ├── useMetrics hook
│   ├── useSorting hook (advanced multi-column)
│   ├── SortableHeader components
│   └── Selection state management
└── SessionComplete
    └── Completion UI/messaging
```

## Key Hooks

### useMetrics
**Location**: [src/hooks/useMetrics.ts](src/hooks/useMetrics.ts)
**Purpose**: Calculate trading metrics from uploaded portfolio data
**Features**:
- Calculates Sharpe Ratio, Sortino Ratio, Max Drawdown, CAGR, Win Rate, etc.
- Memoized calculations for performance
- Handles empty/invalid data gracefully

**Usage**:
```typescript
const { metrics, isCalculating } = useMetrics(portfolioData, riskFreeRate)
```

**Returns**:
- `metrics`: Array of calculated metrics per strategy
- `isCalculating`: Boolean loading state

**Note**: Contains 4 TypeScript `any` violations in sort comparisons (tech debt)

### usePortfolio
**Location**: [src/hooks/usePortfolio.ts](src/hooks/usePortfolio.ts)
**Purpose**: Manage portfolio data with date range filtering
**Features**:
- Parses CSV trade data
- Filters by date range (start/end date)
- Builds equity curves
- Aggregates daily returns

**Usage**:
```typescript
const {
  portfolioData,
  filteredData,
  dateRange,
  setDateRange
} = usePortfolio(uploadedFiles)
```

**Recent Addition**: Date range filtering (commit 258ba3a)

**Note**: Contains 11 TypeScript `any` violations in trade/metrics types (tech debt)

### useContractMultipliers
**Location**: [src/hooks/useContractMultipliers.ts](src/hooks/useContractMultipliers.ts)
**Purpose**: Manage contract multipliers for futures trading
**Features**:
- Per-strategy contract size tracking
- Apply multipliers to metrics
- Master control to set all contracts at once

**Usage**:
```typescript
const {
  multipliers,
  setMultiplier,
  setAllMultipliers,
  getAdjustedMetrics
} = useContractMultipliers(strategies)
```

### useSorting
**Location**: [src/hooks/useSorting.ts](src/hooks/useSorting.ts)
**Purpose**: Advanced multi-column sorting for MetricsTable
**Features**:
- Sort by multiple columns with priority
- Toggle ascending/descending
- Custom comparison logic per data type

**Usage**:
```typescript
const {
  sortedData,
  sortColumn,
  sortDirection,
  handleSort
} = useSorting(data, defaultColumn)
```

## Utility Functions

### dataUtils.ts
**Location**: [src/utils/dataUtils.ts](src/utils/dataUtils.ts)
**Contains Core Functions**:

**CSV & Data Processing**:
- `parseCSV(file)` - Parse CSV file with PapaParse
- `processCurrencyColumns(data)` - Clean currency values ($, commas)
- `parseFilenameComponents(filename)` - Extract symbol/direction/strategy from filename
- `getDisplayName(symbol, direction, strategy)` - Format display names
- `normalizeDate(date)` - Normalize dates to midnight UTC
- `getDateKey(date)` - Convert date to YYYY-MM-DD string key

**Metric Calculations**:
- `calculateMetrics(data, filename)` - Calculate trade-level metrics for a strategy
  - Net Profit, Gross Profit/Loss
  - Profit Factor, Win Rate
  - Average Win/Loss, Expected Value
  - Max Drawdown (from equity curve)
  - CAGR equivalent (annualGrowthRate)
  - Total trades, winning/losing counts
  - **Note**: Does NOT calculate Sharpe or Sortino (those are in PortfolioSection.tsx)
- `getAdjustedMetrics(metrics, multiplier)` - Apply contract multiplier to metrics

**Risk-Adjusted Metrics** (PortfolioSection.tsx):
- **Sharpe Ratio** (line 533): Calculated inline as `(annualGrowthRate / 100) / (maxDrawdown / startingCapital)`
- **Sortino Ratio** (lines 133-158): Calculated inline with downside deviation, uses risk-free rate state

**Correlation Analysis**:
- `buildCorrelationMatrix(strategies)` - Build Spearman correlation matrix
- `calculatePearsonCorrelation(returns1, returns2)` - Pearson correlation coefficient
- `calculateRanks(values)` - Rank calculation for Spearman correlation

**Trading Calculations**:
- `getMarginRate(symbol)` - Get margin requirements by symbol
- `calculateEquityCurve(trades)` - Build cumulative equity curve
- `calculateDailyReturns(equity)` - Calculate daily returns from equity curve

**Formatting**:
- `formatNumber(value, decimals)` - Format numbers with decimals
- `formatCurrency(value)` - Format as currency ($X,XXX.XX)
- `formatPercent(value)` - Format as percentage (X.XX%)

**Note**: Contains 1 TypeScript `any` violation in Metrics interface (tech debt)

## Data Flow

### Upload & Processing Flow
```
1. User uploads CSV via UploadSection
   ↓
2. parseCSV() extracts trade data
   ↓
3. processCurrencyColumns() cleans data
   ↓
4. File uploaded to Supabase storage
   ↓
5. usePortfolio hook fetches and aggregates data
   ↓
6. Date range filter applied (if set)
   ↓
7. useMetrics calculates all metrics
   ↓
8. MetricsTable displays results
```

### Contract Multiplier Flow
```
1. User inputs contract size in ContractInput
   ↓
2. useContractMultipliers stores value
   ↓
3. getAdjustedMetrics() applies multiplier
   ↓
4. Adjusted metrics shown in MetricsTable
   ↓
5. Portfolio charts update with adjusted values
```

### Sorting Flow
```
1. User clicks SortableHeader
   ↓
2. useSorting updates sort column/direction
   ↓
3. Custom comparison logic applied
   ↓
4. MetricsTable re-renders with sorted data
```

### Correlation Flow
```
1. User selects assets in MetricsTable
   ↓
2. Selection state passed to CorrelationSection
   ↓
3. buildCorrelationMatrix() calculates correlations
   ↓
4. CorrelationHeatmap renders Chart.js heatmap
   ↓
5. Spearman & Pearson correlations both shown
```

## State Management

### Plain React Hooks (No Zustand/TanStack Query)
- **Local component state** → `useState`
- **Derived state** → `useMemo`
- **Stable callbacks** → `useCallback`
- **Refs for values** → `useRef`

**Example Pattern**:
```typescript
const [data, setData] = useState<Trade[]>([])
const metrics = useMemo(() => calculateMetrics(data), [data])
const handleUpload = useCallback((file: File) => {
  // upload logic
}, [])
```

### No Global State Library
- Props passed down component tree
- Custom hooks encapsulate shared logic
- No Redux, Zustand, or Jotai

## Adding New Features

### New Metric Calculation
1. Add calculation logic to `dataUtils.calculateMetrics()`
2. Update return type in `calculateMetrics()`
3. Add column to `MetricsTable.tsx`
4. Update sort logic in `useSorting.ts` if needed
5. Test with sample data

**Example**: Sortino Ratio was added in commits 258ba3a & 9f25040

### New Chart Component
1. Create component in `src/components/`
2. Use Chart.js (NOT Recharts - it's unused)
3. Import chart type and plugins needed:
   ```typescript
   import { Line } from 'react-chartjs-2'
   import { Chart, registerables } from 'chart.js'
   import zoomPlugin from 'chartjs-plugin-zoom'
   ```
4. Hook into `useMetrics` or `usePortfolio` for data
5. Add to appropriate section in `App.tsx`

### New Hook
1. Create in `src/hooks/use[Feature].ts`
2. Follow naming convention: `use` prefix, camelCase
3. Return object with clear property names
4. Use TypeScript for all types (avoid `any`)
5. Add JSDoc comments for complex logic

## Chart.js Architecture

### Current Setup
- **Library**: Chart.js 4.x (NOT Recharts)
- **React Wrapper**: react-chartjs-2
- **Plugins Used**:
  - chartjs-plugin-zoom (pan & zoom)
  - chartjs-plugin-annotation (trend lines, markers)
  - chartjs-adapter-date-fns (time scales)

### Where Charts Are Used
1. **PortfolioSection**: Equity curve line charts
2. **CorrelationHeatmap**: Correlation matrix heatmap
3. **CustomTooltip**: Shared tooltip component for charts

### Recharts Note
⚠️ **Recharts is installed but NEVER imported** - should be removed (11.5KB waste)

## Component Size Guidelines

### Target: 200 Lines Max
**Current Violations**:
- ❌ PortfolioSection.tsx: 591 lines (295% of limit) - **HIGH PRIORITY REFACTOR**
- ❌ App.tsx: 351 lines (175% of limit)
- ❌ MetricsTable.tsx: 242 lines (121% of limit) - improved from 350

### Refactoring Strategy
**For PortfolioSection (591 lines)**:
1. Extract equity chart into `EquityChartSection.tsx`
2. Extract statistics into `PortfolioStats.tsx`
3. Extract contract controls into `ContractControls.tsx`
4. Keep only orchestration logic in main component

## TypeScript Patterns

### Interfaces for Data Structures
```typescript
interface Trade {
  date: Date
  symbol: string
  pnl: number
  // ...
}

interface Metric {
  name: string
  sharpe: number
  sortino: number
  // ...
}
```

### Avoid `any` Types
**Current violations (15 total)** - see portfolio-context skill for details

**Preferred approach**:
```typescript
// Bad
const data: any = parseData()

// Good
interface ParsedData {
  trades: Trade[]
  errors: string[]
}
const data: ParsedData = parseData()
```

## Performance Patterns

### Memoization with useMemo
```typescript
// Expensive correlation calculation
const correlationMatrix = useMemo(
  () => buildCorrelationMatrix(selectedStrategies),
  [selectedStrategies]
)
```

### Stable Callbacks with useCallback
```typescript
const handleSort = useCallback((column: string) => {
  setSortColumn(column)
  setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc')
}, [])
```

### Avoid Premature Optimization
- Build features first
- Profile if performance issues arise
- Optimize based on data, not assumptions