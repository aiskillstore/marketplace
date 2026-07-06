---
name: coding-standards
description: "React 19 and TypeScript coding standards for Portfolio Buddy 2. Use when: writing new components, reviewing code, refactoring, or ensuring consistency. Contains component patterns, TypeScript rules, and best practices."
---

# Coding Standards - Portfolio Buddy 2

## React 19 Patterns

### Component Structure
```typescript
// Good: Functional component with TypeScript
interface MetricsTableProps {
  data: Metric[]
  onSelect: (id: string) => void
}

export function MetricsTable({ data, onSelect }: MetricsTableProps) {
  // Hooks at top
  const [selected, setSelected] = useState<Set<string>>(new Set())

  // Derived state with useMemo
  const sortedData = useMemo(() =>
    data.sort((a, b) => b.sharpe - a.sharpe),
    [data]
  )

  // Event handlers with useCallback
  const handleSelect = useCallback((id: string) => {
    setSelected(prev => new Set(prev).add(id))
    onSelect(id)
  }, [onSelect])

  // Render
  return <div>...</div>
}
```

### Hooks Rules
1. **Only at top level** - No hooks in conditionals or loops
2. **Custom hooks start with `use`** - useMetrics, usePortfolio, useSorting
3. **Dependencies array complete** - All deps in useEffect/useMemo/useCallback
4. **Cleanup on unmount** - Return cleanup function from useEffect

### State Management

**Portfolio Buddy 2 uses PLAIN REACT HOOKS ONLY:**
- **Local UI state** → `useState`
- **Derived state** → `useMemo`
- **Stable callbacks** → `useCallback`
- **DOM/value refs** → `useRef`

**NO global state libraries:**
- ❌ No TanStack Query
- ❌ No Zustand
- ❌ No Redux
- ❌ No Jotai

**Pattern**: Props down, custom hooks for shared logic

```typescript
// State management example
const [files, setFiles] = useState<File[]>([])
const [dateRange, setDateRange] = useState({ start: null, end: null })

// Derived state
const filteredData = useMemo(() =>
  filterByDateRange(files, dateRange),
  [files, dateRange]
)

// Stable callback
const handleUpload = useCallback((newFile: File) => {
  setFiles(prev => [...prev, newFile])
}, [])
```

## TypeScript Standards

### No `any` Types
```typescript
// Bad
const data: any = fetchData()

// Good
interface TradeData {
  symbol: string
  date: Date
  pnl: number
}
const data: TradeData[] = fetchData()
```

**Current Violations (Tech Debt)**:
- usePortfolio.ts: 11 instances (trade/metrics types)
- useMetrics.ts: 4 instances (sort comparisons)
- dataUtils.ts: 1 instance (Metrics interface)
- **Total: 15 violations to fix** (originally 16)

### Strict Null Checks
```typescript
// Bad
const value = data.find(x => x.id === id)
value.name // Could be undefined!

// Good
const value = data.find(x => x.id === id)
if (value) {
  value.name // Type-safe
}

// Or with optional chaining
const name = data.find(x => x.id === id)?.name
```

### Type Inference When Obvious
```typescript
// Redundant
const count: number = 5
const name: string = 'Portfolio Buddy'

// Better (TypeScript infers)
const count = 5
const name = 'Portfolio Buddy'

// Explicit when needed
const metrics: Metric[] = [] // Empty array needs type
```

## Component Size Limits

### Max 200 Lines Per Component
When component exceeds 200 lines:
1. Extract sub-components
2. Move logic to custom hooks
3. Extract utilities to utils/

### Current Violations

**⚠️ MUST REFACTOR:**
- **PortfolioSection.tsx**: 591 lines (295% of limit)
  - Extract EquityChartSection
  - Extract PortfolioStats
  - Extract ContractControls
  - Keep only orchestration logic

**Should refactor:**
- **App.tsx**: 351 lines (175% of limit)
  - Extract sections into components
- **MetricsTable.tsx**: 242 lines (121% of limit)
  - Improved from 350 lines, still over limit

### Refactoring Example
```typescript
// Before: 591 lines in PortfolioSection
function PortfolioSection() {
  // Contract multiplier logic (50 lines)
  // Date filtering logic (40 lines)
  // Chart configuration (100 lines)
  // Statistics calculation (80 lines)
  // Rendering logic (300+ lines)
}

// After: Split into focused pieces
function PortfolioSection() {
  const portfolio = usePortfolio(files, dateRange)
  const contracts = useContractMultipliers(portfolio.strategies)

  return (
    <div>
      <ContractControls {...contracts} />
      <EquityChartSection data={portfolio.equity} />
      <PortfolioStats metrics={portfolio.metrics} />
    </div>
  )
}
```

## File Organization

### Actual Directory Structure
```
src/
├── components/
│   └── [AllComponents].tsx    (flat structure, no subdirs)
├── hooks/
│   ├── useContractMultipliers.ts
│   ├── useMetrics.ts
│   ├── usePortfolio.ts
│   └── useSorting.ts
├── utils/
│   └── dataUtils.ts           (metric calculations, parsing)
├── App.tsx
└── main.tsx
```

**Note**: No `ui/` or `charts/` subdirectories - components are flat in `components/`

### Naming Conventions
- **Components**: PascalCase - `MetricsTable.tsx`, `CorrelationHeatmap.tsx`
- **Hooks**: camelCase with `use` prefix - `useMetrics.ts`, `useSorting.ts`
- **Utils**: camelCase - `calculateMetrics()`, `parseCSV()`
- **Types/Interfaces**: PascalCase - `interface Metric`, `type Trade`

## Error Handling

### Always Handle Errors
```typescript
// Bad
const data = await supabase.storage.upload(file)

// Good
const { data, error } = await supabase.storage.upload(file)
if (error) {
  console.error('Upload failed:', error)
  toast.error('Failed to upload file')
  return
}
```

### Use Try-Catch for Parsing
```typescript
// CSV parsing with error handling
try {
  const parsed = parseCSV(file)
  setData(parsed.data)
  if (parsed.errors.length > 0) {
    setErrors(parsed.errors)
  }
} catch (error) {
  console.error('Parse error:', error)
  toast.error('Invalid CSV format')
}
```

### Error Boundaries
**Current Status**: No error boundaries implemented (tech debt)

**Should add**:
```typescript
<ErrorBoundary fallback={<ErrorMessage />}>
  <PortfolioSection />
</ErrorBoundary>
```

## Performance

### Memoization
```typescript
// Expensive calculations
const metrics = useMemo(
  () => calculateMetrics(portfolioData, riskFreeRate),
  [portfolioData, riskFreeRate]
)

// Large data transformations
const correlationMatrix = useMemo(
  () => buildCorrelationMatrix(selectedStrategies),
  [selectedStrategies]
)
```

### Callback Stability
```typescript
// Prevent child re-renders
const handleSort = useCallback((column: string) => {
  setSortColumn(column)
  setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc')
}, [])

// Pass stable callback to children
<SortableHeader onSort={handleSort} />
```

### Avoid Premature Optimization
1. Build feature first
2. Measure performance if issues arise
3. Optimize based on profiling data
4. Don't optimize without evidence

## Chart.js Integration

### Pattern for Chart Components
```typescript
import { Line } from 'react-chartjs-2'
import { Chart as ChartJS, registerables } from 'chart.js'
import zoomPlugin from 'chartjs-plugin-zoom'

// Register plugins once
ChartJS.register(...registerables, zoomPlugin)

function EquityChart({ data }: { data: EquityData[] }) {
  const chartData = useMemo(() => ({
    labels: data.map(d => d.date),
    datasets: [{
      label: 'Equity',
      data: data.map(d => d.value),
      borderColor: 'rgb(75, 192, 192)',
    }]
  }), [data])

  const options = useMemo(() => ({
    responsive: true,
    plugins: {
      zoom: { enabled: true }
    }
  }), [])

  return <Line data={chartData} options={options} />
}
```

### Chart Libraries
- ✅ **Use**: Chart.js + react-chartjs-2
- ❌ **Don't use**: Recharts (installed but unused, should remove)

## Testing Standards

### What to Test
- ✅ Critical calculations (Sharpe, Sortino, correlation)
- ✅ Data transformations (CSV parsing, metric calculations)
- ✅ Error states and edge cases
- ✅ Hook return values
- ❌ UI implementation details (className, DOM structure)
- ❌ Third-party library internals

### Test Structure
```typescript
describe('calculateMetrics', () => {
  it('calculates Sharpe ratio correctly', () => {
    const trades = mockTradeData()
    const result = calculateMetrics(trades, 0.02)
    expect(result.sharpe).toBeCloseTo(1.5, 2)
  })

  it('handles empty data gracefully', () => {
    const result = calculateMetrics([], 0.02)
    expect(result.sharpe).toBe(0)
  })
})
```

**Current Status**: No tests implemented (future work)

## Import Organization

### Order of Imports
```typescript
// 1. React and external libraries
import { useState, useMemo, useCallback } from 'react'
import { Line } from 'react-chartjs-2'

// 2. Internal hooks
import { useMetrics } from '@/hooks/useMetrics'
import { usePortfolio } from '@/hooks/usePortfolio'

// 3. Utils and helpers
import { calculateMetrics, formatCurrency } from '@/utils/dataUtils'

// 4. Types
import type { Metric, Trade } from '@/types'

// 5. Styles (if any)
import './styles.css'
```

## Code Comments

### When to Comment
```typescript
// Good: Explain WHY, not WHAT
// Annualize by multiplying by sqrt(252) trading days
const sharpe = (avgReturn / stdDev) * Math.sqrt(252)

// Bad: Obvious what the code does
// Calculate Sharpe ratio
const sharpe = (avgReturn / stdDev) * Math.sqrt(252)
```

### JSDoc for Complex Functions
```typescript
/**
 * Calculate Sortino Ratio using downside deviation
 * @param returns - Array of daily returns
 * @param riskFreeRate - Annual risk-free rate (e.g., 0.02 for 2%)
 * @param targetReturn - Target return threshold (default: 0)
 * @returns Annualized Sortino Ratio
 */
function calculateSortino(
  returns: number[],
  riskFreeRate: number,
  targetReturn = 0
): number {
  // Implementation
}
```

## Git Commit Messages

### Format
```
<type>: <subject>

<body>
```

### Types
- `feat:` New feature
- `fix:` Bug fix
- `refactor:` Code restructuring
- `perf:` Performance improvement
- `docs:` Documentation
- `test:` Test additions/changes

### Examples from Recent Commits
```
Fix Sortino Ratio calculation by annualizing downside deviation and correcting variance calculation

Refactor portfolio calculations and enhance Supabase client validation; add risk-free rate input and Sortino Ratio calculation

Enhance error handling and validation in Supabase data fetching; update MetricsTable and PortfolioSection to manage selectedTradeLists state
```

## Code Review Checklist

Before submitting code:
- [ ] TypeScript strict mode passes (no `any` unless documented as tech debt)
- [ ] Component under 200 lines (or has refactor plan)
- [ ] Error handling in place
- [ ] Memoization for expensive calculations
- [ ] Stable callbacks with useCallback
- [ ] Proper TypeScript types (no `any`)
- [ ] Imports organized by category
- [ ] JSDoc on complex functions
- [ ] Console.logs removed
- [ ] Chart.js used (not Recharts)