---
title: Use Test Sharding to Distribute Tests Across Multiple Machines
impact: MEDIUM-HIGH
impactDescription: Reduces total test suite time by 50-80% through horizontal scaling
tags: parallel, sharding, performance, ci-cd, scalability
---

## Use Test Sharding to Distribute Tests Across Multiple Machines

**Impact: MEDIUM-HIGH (reduces total test suite time by 50-80% through horizontal scaling)**

Test sharding allows you to split your test suite across multiple machines or CI jobs, dramatically reducing total execution time. While parallelization runs tests concurrently on a single machine, sharding distributes the entire test suite across multiple machines, enabling linear scaling of your test infrastructure.

**Incorrect (running all tests on single machine):**

```typescript
// .github/workflows/playwright.yml
name: Playwright Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - name: Install dependencies
        run: npm ci
      - name: Install Playwright
        run: npx playwright install --with-deps
      
      # ❌ All 500 tests run on single machine
      # Takes 30+ minutes even with parallelization
      - name: Run all tests
        run: npx playwright test
      
      # ❌ Slow feedback loop
      # ❌ Wastes CI/CD time
      # ❌ Delays deployments
```

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  // ❌ Only using workers on single machine
  workers: 4,
  
  // ❌ No sharding configuration
  // Limited by single machine's resources
  testDir: './tests',
});
```

**Correct (using test sharding across multiple machines):**

```typescript
// .github/workflows/playwright.yml
name: Playwright Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        # ✅ Split tests across 4 shards (machines)
        shard: [1, 2, 3, 4]
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - name: Install dependencies
        run: npm ci
      - name: Install Playwright
        run: npx playwright install --with-deps
      
      # ✅ Each machine runs 1/4 of the tests
      - name: Run tests (shard ${{ matrix.shard }}/4)
        run: npx playwright test --shard=${{ matrix.shard }}/4
      
      # ✅ Upload results from each shard
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report-${{ matrix.shard }}
          path: playwright-report/
          retention-days: 30
```

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  // ✅ Optimize workers for CI environment
  workers: process.env.CI ? 2 : undefined,
  
  // ✅ Sharding works automatically when --shard flag is used
  // Each shard gets an even distribution of tests
  testDir: './tests',
  
  // ✅ Shorter timeout per test since we have more machines
  timeout: 30000,
  
  use: {
    trace: 'on-first-retry',
  },
  
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
```

**Dynamic sharding based on test count:**

```typescript
// .github/workflows/playwright-dynamic.yml
name: Playwright Tests (Dynamic Sharding)

on: [push, pull_request]

jobs:
  # ✅ Determine optimal shard count based on test suite size
  calculate-shards:
    runs-on: ubuntu-latest
    outputs:
      shards: ${{ steps.calculate.outputs.shards }}
    steps:
      - uses: actions/checkout@v3
      - name: Calculate shard count
        id: calculate
        run: |
          TEST_COUNT=$(find tests -name "*.spec.ts" | wc -l)
          # 1 shard per 50 tests, minimum 2, maximum 10
          SHARDS=$(( (TEST_COUNT + 49) / 50 ))
          SHARDS=$(( SHARDS < 2 ? 2 : SHARDS ))
          SHARDS=$(( SHARDS > 10 ? 10 : SHARDS ))
          echo "shards=$SHARDS" >> $GITHUB_OUTPUT
          echo "Calculated $SHARDS shards for $TEST_COUNT tests"

  test:
    needs: calculate-shards
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        # ✅ Dynamic shard count based on test suite size
        shard: ${{ fromJSON(needs.calculate-shards.outputs.shards) }}
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - name: Install dependencies
        run: npm ci
      - name: Install Playwright
        run: npx playwright install --with-deps
      - name: Run tests
        run: npx playwright test --shard=${{ matrix.shard }}/${{ needs.calculate-shards.outputs.shards }}
```

**Merging test results from multiple shards:**

```typescript
// .github/workflows/playwright-merge.yml
name: Playwright Tests with Merge

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - name: Install dependencies
        run: npm ci
      - name: Install Playwright
        run: npx playwright install --with-deps
      
      - name: Run tests (shard ${{ matrix.shard }}/4)
        run: npx playwright test --shard=${{ matrix.shard }}/4
      
      # ✅ Upload blob report for merging
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: blob-report-${{ matrix.shard }}
          path: blob-report/
          retention-days: 1

  # ✅ Merge all shard reports into single HTML report
  merge-reports:
    if: always()
    needs: [test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - name: Install dependencies
        run: npm ci
      
      # Download all blob reports
      - uses: actions/download-artifact@v3
        with:
          path: all-blob-reports
      
      # Merge into single HTML report
      - name: Merge reports
        run: npx playwright merge-reports --reporter html ./all-blob-reports
      
      - name: Upload merged report
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report-merged
          path: playwright-report/
          retention-days: 30
```

```typescript
// playwright.config.ts for blob reporting
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  
  // ✅ Use blob reporter in CI for merging
  reporter: process.env.CI 
    ? [['blob']] 
    : [['html']],
  
  use: {
    trace: 'on-first-retry',
  },
});
```

**Local testing with sharding:**

```typescript
// package.json - scripts for local sharding
{
  "scripts": {
    // ✅ Run specific shard locally
    "test:shard1": "playwright test --shard=1/4",
    "test:shard2": "playwright test --shard=2/4",
    "test:shard3": "playwright test --shard=3/4",
    "test:shard4": "playwright test --shard=4/4",
    
    // ✅ Run all shards in parallel (requires GNU parallel or similar)
    "test:all-shards": "parallel ::: 'npm run test:shard1' 'npm run test:shard2' 'npm run test:shard3' 'npm run test:shard4'"
  }
}
```

```bash
# ✅ Test specific shard locally
npx playwright test --shard=1/4

# ✅ Test with different shard counts
npx playwright test --shard=2/8  # Shard 2 of 8
npx playwright test --shard=5/10 # Shard 5 of 10
```

**Sharding with test tags/groups:**

```typescript
// tests/smoke.spec.ts
import { test, expect } from '@playwright/test';

// ✅ Tag critical tests for separate shard
test.describe('Smoke Tests @smoke', () => {
  test('homepage loads', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Home/);
  });
});

// tests/e2e.spec.ts
test.describe('E2E Tests @e2e', () => {
  test('complete checkout flow', async ({ page }) => {
    // Long-running test
  });
});
```

```yaml
# .github/workflows/playwright-tagged.yml
jobs:
  smoke-tests:
    runs-on: ubuntu-latest
    steps:
      - name: Run smoke tests only
        # ✅ Run critical tests on single fast shard
        run: npx playwright test --grep @smoke
  
  full-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - name: Run full suite
        # ✅ Run all tests across multiple shards
        run: npx playwright test --shard=${{ matrix.shard }}/4
```

**Optimal shard configuration strategies:**

```typescript
// Calculate optimal shard count based on resources
const calculateOptimalShards = (testCount: number, avgTestDuration: number) => {
  // ✅ Target: Each shard should complete in 5-10 minutes
  const targetDuration = 7 * 60 * 1000; // 7 minutes in ms
  const totalDuration = testCount * avgTestDuration;
  const optimalShards = Math.ceil(totalDuration / targetDuration);
  
  // ✅ Constrain to reasonable range
  return Math.max(2, Math.min(optimalShards, 20));
};

// Example configurations:
// - 100 tests @ 10s each = 1000s total → 3 shards (330s each)
// - 500 tests @ 15s each = 7500s total → 18 shards (416s each)
// - 50 tests @ 5s each = 250s total → 2 shards (125s each)
```

**Best practices for sharding:**

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  // ✅ Keep fullyParallel for intra-shard parallelization
  fullyParallel: true,
  
  // ✅ Adjust workers per shard based on resources
  workers: process.env.CI ? 2 : undefined,
  
  // ✅ Use retries with sharding for reliability
  retries: process.env.CI ? 2 : 0,
  
  // ✅ Blob reporter for merging shard results
  reporter: process.env.CI ? [['blob']] : [['html']],
  
  use: {
    // ✅ Capture traces only on retry to save resources
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
});
```

Benefits of test sharding:
- **Horizontal scaling**: Add more machines to reduce time linearly
- **Faster feedback**: Get results 4-10x faster with proper sharding
- **Resource efficiency**: Distribute load across multiple CI workers
- **Cost optimization**: Pay for parallel execution time, not sequential time
- **Flexible scaling**: Adjust shard count based on test suite size
- **Improved reliability**: Failed shards can be retried independently

When to use sharding:
- ✅ Large test suites (100+ tests or 10+ minutes runtime)
- ✅ CI/CD pipelines with parallel job support
- ✅ Time-sensitive deployments requiring fast feedback
- ✅ Test suites growing beyond single machine capacity
- ✅ When parallelization on single machine isn't enough

When not to use sharding:
- ❌ Small test suites (< 50 tests, < 5 minutes)
- ❌ Limited CI/CD resources or budget constraints
- ❌ Tests with heavy shared state requirements
- ❌ When setup/teardown time exceeds test time

Sharding calculation guidelines:
- **Target duration per shard**: 5-10 minutes ideal
- **Minimum shards**: 2 (even for small suites in CI)
- **Maximum shards**: 20 (diminishing returns beyond this)
- **Shard count**: Should divide evenly into test count when possible
- **Worker count per shard**: 2-4 in CI, CPU count locally

Common sharding patterns:
- **2 shards**: Small to medium test suites (50-200 tests)
- **4 shards**: Medium test suites (200-500 tests)
- **8 shards**: Large test suites (500-1000 tests)
- **10+ shards**: Very large test suites (1000+ tests)

Reference: [Playwright Test Sharding](https://playwright.dev/docs/test-sharding)