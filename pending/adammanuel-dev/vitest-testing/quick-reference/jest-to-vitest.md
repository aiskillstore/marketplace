# Jest to Vitest Migration Guide

**Comprehensive guide for migrating from Jest to Vitest with minimal disruption.**

Vitest maintains high API compatibility with Jest while offering superior performance and modern features. This guide provides a systematic approach to migration.

---

## 🎯 Quick Comparison

| Feature | Jest | Vitest | Migration Effort |
|---------|------|--------|------------------|
| **Configuration** | Standalone (`jest.config.js`) | Unified with Vite (`vite.config.ts`) | Medium |
| **Speed** | Moderate (process isolation) | Fast (Vite HMR) | None (automatic gain) |
| **Mocking** | `jest.mock()` | `vi.mock()` | Low (find/replace) |
| **Globals** | Automatic | Optional (config or import) | Low |
| **ES Modules** | Requires transform | Native | None (automatic gain) |
| **Watch Mode** | Good | Excellent (HMR) | None (automatic gain) |
| **TypeScript** | Needs ts-jest | Built-in | None (automatic gain) |

**Migration Time:** Small project (< 1 day), Large project (2-5 days)

---

## 📋 Migration Checklist

### Phase 1: Preparation
- [ ] Review current Jest configuration
- [ ] Identify custom matchers and setup files
- [ ] List all Jest-specific dependencies
- [ ] Create backup branch
- [ ] Install Vitest alongside Jest

### Phase 2: Configuration
- [ ] Create/update `vite.config.ts`
- [ ] Migrate Jest config to Vitest
- [ ] Update setup files
- [ ] Configure globals (if needed)
- [ ] Set up coverage provider

### Phase 3: Code Migration
- [ ] Replace `jest` with `vi` in imports
- [ ] Update mock module paths
- [ ] Fix snapshot format differences
- [ ] Update custom matchers
- [ ] Handle timer mocking differences

### Phase 4: Verification
- [ ] Run both test suites in parallel
- [ ] Compare coverage reports
- [ ] Fix failing tests
- [ ] Update CI/CD pipelines
- [ ] Remove Jest dependencies

---

## ⚙️ Configuration Migration

### Step 1: Install Vitest

```bash
# Remove Jest
npm uninstall jest @types/jest ts-jest

# Install Vitest
npm install -D vitest @vitest/ui @vitest/coverage-v8
```

### Step 2: Create Vite Config

**Before: Jest Configuration**
```javascript
// jest.config.js
module.exports = {
  transform: {
    '^.+\\.tsx?$': 'ts-jest',
  },
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(css|less)$': 'identity-obj-proxy',
    '\\.(jpg|jpeg|png|gif|webp|svg)$': '<rootDir>/__mocks__/fileMock.js'
  },
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
}
```

**After: Vitest Configuration**
```typescript
// vite.config.ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  test: {
    globals: true, // Enable Jest-like globals
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts'],
    css: true, // Process CSS imports
    coverage: {
      provider: 'v8', // or 'istanbul'
      reporter: ['text', 'json', 'html'],
      exclude: ['**/*.test.{ts,tsx}', '**/*.spec.{ts,tsx}'],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80
      }
    }
  }
})
```

**Key Differences:**
- ✅ No separate transform configuration needed (Vite handles it)
- ✅ Module resolution via `resolve.alias` instead of `moduleNameMapper`
- ✅ CSS/assets handled by Vite plugins
- ✅ Unified configuration for build and test

---

## 🔄 API Migration

### Global API Changes

**With `globals: false` (Recommended)**
```typescript
// Before: Jest (auto-imported)
describe('My test', () => {
  it('works', () => {
    expect(1).toBe(1)
  })
})

// After: Vitest (explicit imports)
import { describe, it, expect } from 'vitest'

describe('My test', () => {
  it('works', () => {
    expect(1).toBe(1)
  })
})
```

**With `globals: true` (Jest-compatible)**
```typescript
// Works in both Jest and Vitest
describe('My test', () => {
  it('works', () => {
    expect(1).toBe(1)
  })
})
```

### Mock Function Changes

**Simple find/replace: `jest` → `vi`**

```typescript
// Before: Jest
const mockFn = jest.fn()
mockFn.mockImplementation(() => 'result')
mockFn.mockResolvedValue('async result')
expect(jest.isMockFunction(mockFn)).toBe(true)

// After: Vitest
const mockFn = vi.fn()
mockFn.mockImplementation(() => 'result')
mockFn.mockResolvedValue('async result')
expect(vi.isMockFunction(mockFn)).toBe(true)
```

### Module Mocking

**Jest:**
```typescript
jest.mock('./module', () => ({
  method: jest.fn()
}))
```

**Vitest (Enhanced with async support):**
```typescript
vi.mock('./module', async () => ({
  method: vi.fn(),
  // Can await dynamic imports
  default: await import('./actual-implementation')
}))
```

**Partial mocking improved:**
```typescript
// Before: Jest
jest.mock('./utils', () => ({
  ...jest.requireActual('./utils'),
  expensiveOperation: jest.fn()
}))

// After: Vitest (cleaner async API)
vi.mock('./utils', async (importOriginal) => {
  const actual = await importOriginal()
  return {
    ...actual,
    expensiveOperation: vi.fn()
  }
})
```

### Timer Mocking

**Jest:**
```typescript
beforeEach(() => {
  jest.useFakeTimers('modern')
})

jest.setSystemTime(new Date('2024-01-01'))
jest.runAllTimers()
jest.runOnlyPendingTimers()
```

**Vitest (Extended API):**
```typescript
beforeEach(() => {
  vi.useFakeTimers()
})

vi.setSystemTime(new Date('2024-01-01'))
vi.runAllTimers()
vi.runOnlyPendingTimers()

// Vitest additions:
await vi.runAllTimersAsync()
await vi.advanceTimersByTimeAsync(1000)
vi.getMockedSystemTime()
```

---

## 📸 Snapshot Testing

Snapshots work similarly but have subtle format differences.

**Jest:**
```typescript
test('snapshot', () => {
  expect(component).toMatchInlineSnapshot(`
    Object {
      "id": 1,
      "name": "Test",
    }
  `)
})
```

**Vitest (Cleaner format):**
```typescript
test('snapshot', () => {
  expect(component).toMatchInlineSnapshot(`
    {
      "id": 1,
      "name": "Test",
    }
  `)
})
```

**Update snapshots:**
```bash
# Jest
npm test -- -u

# Vitest
vitest -u
```

**File snapshots (Vitest only):**
```typescript
// Vitest can snapshot to arbitrary files
await expect(html).toMatchFileSnapshot('./output.html')
```

---

## 🚀 Performance Improvements

### Why Vitest is Faster

**Jest execution model:**
1. Master process spawns workers
2. Each worker boots Node.js
3. Transform all files
4. Execute tests
5. Report results

**Typical times:**
- Cold start: 15-20 seconds (100 files)
- Watch mode re-run: 3-5 seconds
- Single file change: 1-2 seconds

**Vitest execution model:**
1. Vite server starts (if not running)
2. Modules already in Vite graph are reused
3. HMR provides near-instant updates

**Typical times:**
- Cold start: 5-8 seconds (100 files)
- Watch mode re-run: 1-2 seconds
- Single file change: 100-300ms ✨

### Optimization Tips

**Jest optimization:**
```javascript
{
  maxWorkers: '50%',
  cache: true,
  testEnvironment: 'node' // Faster than jsdom
}
```

**Vitest optimization:**
```typescript
{
  test: {
    threads: true,
    isolate: false, // Faster but less isolation
    css: false, // Skip CSS processing if not needed
    pool: 'threads'
  }
}
```

---

## 🔧 Common Migration Issues

### Issue 1: Module Mocking

**Problem:**
```typescript
// Jest - works
jest.mock('axios')
import axios from 'axios'
axios.get.mockResolvedValue({ data: 'test' })
```

**Solution:**
```typescript
// Vitest - need vi.mocked()
vi.mock('axios')
import axios from 'axios'
vi.mocked(axios.get).mockResolvedValue({ data: 'test' })
```

### Issue 2: Snapshot Format

Snapshots may need reformatting after migration.

**Solution:**
```bash
# Update all snapshots
vitest -u

# Review changes carefully
git diff __snapshots__/
```

### Issue 3: Global Setup

**Jest:**
```javascript
// jest.config.js
{
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js']
}

// jest.setup.js
import '@testing-library/jest-dom'
```

**Vitest:**
```typescript
// vite.config.ts
{
  test: {
    setupFiles: ['./vitest.setup.ts']
  }
}

// vitest.setup.ts
import '@testing-library/jest-dom'
import { afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'

afterEach(() => {
  cleanup()
})
```

### Issue 4: Coverage Provider

**Jest uses Istanbul by default:**
```bash
npm test -- --coverage
```

**Vitest supports both v8 and Istanbul:**
```typescript
{
  test: {
    coverage: {
      provider: 'v8', // Faster
      // or
      provider: 'istanbul' // More compatible with Jest
    }
  }
}
```

---

## 📝 Migration Script

Automate the migration with a script:

```bash
#!/bin/bash

# 1. Install Vitest
npm install -D vitest @vitest/ui @vitest/coverage-v8

# 2. Find/replace jest → vi
find src test -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" \) \
  -exec sed -i '' 's/jest\.fn()/vi.fn()/g' {} \;

find src test -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" \) \
  -exec sed -i '' 's/jest\.mock/vi.mock/g' {} \;

find src test -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" \) \
  -exec sed -i '' 's/jest\.spyOn/vi.spyOn/g' {} \;

# 3. Add imports if globals: false
# This requires more sophisticated tooling like jscodeshift

# 4. Update snapshots
npx vitest -u

echo "Migration complete! Review changes and run tests."
```

---

## 🎯 Decision Framework

### Choose Jest When:
- **Existing large codebase** with extensive Jest usage
- **Team has deep Jest expertise**
- **Need Jest presets** (React Native, Angular)
- **Enterprise stability** is paramount
- **Migration cost** is prohibitive

### Choose Vitest When:
- **Starting new project**
- **Already using Vite** for building
- **Performance is critical** (large test suites)
- **Want modern DX** (HMR, native ESM)
- **Test suite is small** enough to migrate easily
- **Using cutting-edge JavaScript** features

### Hybrid Approach

Run both during migration:

```json
{
  "scripts": {
    "test:jest": "jest",
    "test:vitest": "vitest",
    "test": "npm run test:jest && npm run test:vitest"
  }
}
```

---

## 🔄 CI/CD Updates

### GitHub Actions

**Before: Jest**
```yaml
- name: Run tests
  run: npm test -- --coverage

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

**After: Vitest**
```yaml
- name: Run tests
  run: vitest --coverage

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

### GitLab CI

```yaml
test:
  script:
    # Run Vitest instead of Jest
    - npm run test -- --coverage
  coverage: '/Lines\s*:\s*(\d+\.?\d*)%/'
```

---

## 📊 Migration Timeline

### Small Project (< 50 tests)
- **Setup:** 1-2 hours
- **Migration:** 2-4 hours
- **Verification:** 1-2 hours
- **Total:** ~1 day

### Medium Project (50-500 tests)
- **Setup:** 2-4 hours
- **Migration:** 1-2 days
- **Verification:** 4-8 hours
- **Total:** 2-3 days

### Large Project (> 500 tests)
- **Setup:** 4-8 hours
- **Migration:** 2-4 days
- **Verification:** 1-2 days
- **Total:** 4-7 days

---

## ✅ Verification Checklist

After migration:

- [ ] All tests pass with Vitest
- [ ] Coverage reports are similar to Jest
- [ ] Snapshots updated and verified
- [ ] Watch mode works correctly
- [ ] CI/CD pipeline updated
- [ ] Team trained on Vitest differences
- [ ] Documentation updated
- [ ] Jest dependencies removed
- [ ] package.json scripts updated
- [ ] Performance improvements validated

---

## 🔗 Resources

- **[Vitest Docs](https://vitest.dev/)** - Official documentation
- **[Migration Guide](https://vitest.dev/guide/migration.html)** - Official migration guide
- **[Vitest vs Jest](https://vitest.dev/guide/comparisons.html#jest)** - Detailed comparison
- **[Vite Config](https://vitejs.dev/config/)** - Vite configuration reference

---

## 📋 Summary

**Key Takeaways:**
1. **High compatibility** - Most Jest tests work with minimal changes
2. **Performance gains** - Expect 2-5x faster test execution
3. **Modern features** - Native ESM, TypeScript, HMR
4. **Gradual migration** - Can run both frameworks during transition
5. **Low risk** - Easy to revert if needed

**Migration Effort:**
- Low effort: API changes (`jest` → `vi`)
- Medium effort: Configuration migration
- High effort: Custom matchers, complex mocks

**Recommended Approach:**
1. Start with new files in Vitest
2. Migrate simple test files first
3. Tackle complex tests last
4. Remove Jest when fully migrated

---

**Next Steps:**
- Review [Vitest Features](https://vitest.dev/guide/features.html)
- Try [Vitest UI](https://vitest.dev/guide/ui.html)
- Explore [Benchmarking](../patterns/performance-testing.md)
