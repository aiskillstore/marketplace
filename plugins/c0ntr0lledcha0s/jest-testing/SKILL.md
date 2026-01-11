---
name: jest-testing
description: Automatically activated when user works with Jest tests, mentions Jest configuration, asks about Jest matchers/mocks, or has files matching *.test.js, *.test.ts, jest.config.*. Provides Jest-specific expertise for testing React, Node.js, and JavaScript applications. Also applies to Vitest due to API compatibility. Does NOT handle general quality analysis - use analyzing-test-quality for that.
version: 1.1.0
allowed-tools: Read, Grep, Glob, Bash
capabilities:
  - jest-configuration
  - matchers-assertions
  - mocking-strategies
  - snapshot-testing
  - code-coverage
  - react-testing-library
  - async-testing
  - custom-matchers
  - msw-integration
---

# Jest Testing Expertise

You are an expert in Jest testing framework with deep knowledge of its configuration, matchers, mocks, and best practices for testing JavaScript and TypeScript applications.

## Your Capabilities

1. **Jest Configuration**: Setup, configuration files, environments, and presets
2. **Matchers & Assertions**: Built-in and custom matchers, asymmetric matchers
3. **Mocking**: Mock functions, modules, timers, and external dependencies
4. **Snapshot Testing**: Inline and external snapshots, snapshot updates
5. **Code Coverage**: Coverage configuration, thresholds, and reports
6. **Test Organization**: Describe blocks, hooks, test filtering
7. **React Testing**: Testing React components with Jest DOM and RTL

## When to Use This Skill

Claude should automatically invoke this skill when:
- The user mentions Jest, jest.config, or Jest-specific features
- Files matching `*.test.js`, `*.test.ts`, `*.test.jsx`, `*.test.tsx` are encountered
- The user asks about mocking, snapshots, or Jest matchers
- The conversation involves testing React, Node.js, or JavaScript apps
- Jest configuration or setup is discussed

## How to Use This Skill

### Accessing Resources

Use `{baseDir}` to reference files in this skill directory:
- Scripts: `{baseDir}/scripts/`
- Documentation: `{baseDir}/references/`
- Templates: `{baseDir}/assets/`

### Progressive Discovery

1. Start with core Jest expertise
2. Reference specific documentation as needed
3. Provide code examples from templates

## Available Resources

This skill includes ready-to-use resources in `{baseDir}`:

- **references/jest-cheatsheet.md** - Quick reference for matchers, mocks, async patterns, and CLI commands
- **assets/test-file.template.ts** - Complete test templates for unit tests, async tests, class tests, mock tests, React components, and hooks
- **scripts/check-jest-setup.sh** - Validates Jest configuration and dependencies

## Jest Best Practices

### Test Structure
```javascript
describe('ComponentName', () => {
  beforeEach(() => {
    // Setup
  });

  afterEach(() => {
    // Cleanup
  });

  describe('method or behavior', () => {
    it('should do expected thing when condition', () => {
      // Arrange
      // Act
      // Assert
    });
  });
});
```

### Mocking Patterns

#### Mock Functions
```javascript
const mockFn = jest.fn();
mockFn.mockReturnValue('value');
mockFn.mockResolvedValue('async value');
mockFn.mockImplementation((arg) => arg * 2);
```

#### Mock Modules
```javascript
jest.mock('./module', () => ({
  func: jest.fn().mockReturnValue('mocked'),
}));
```

#### Mock Timers
```javascript
jest.useFakeTimers();
jest.advanceTimersByTime(1000);
jest.runAllTimers();
```

### Common Matchers
```javascript
expect(value).toBe(expected);          // Strict equality
expect(value).toEqual(expected);       // Deep equality
expect(value).toBeTruthy();            // Truthy
expect(value).toContain(item);         // Array/string contains
expect(fn).toHaveBeenCalledWith(args); // Function called with
expect(value).toMatchSnapshot();       // Snapshot
expect(fn).toThrow(error);             // Throws
```

### Async Testing
```javascript
// Promises
it('async test', async () => {
  await expect(asyncFn()).resolves.toBe('value');
});

// Callbacks
it('callback test', (done) => {
  callbackFn((result) => {
    expect(result).toBe('value');
    done();
  });
});
```

## Jest Configuration

### Basic Configuration
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'node', // or 'jsdom'
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.ts', '**/*.test.ts'],
  transform: {
    '^.+\\.tsx?$': 'ts-jest',
  },
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};
```

## React Testing Library

### Setup with Custom Render
```typescript
// test-utils.tsx
import { render, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';

const AllProviders = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

export const renderWithProviders = (
  ui: React.ReactElement,
  options?: RenderOptions
) => render(ui, { wrapper: AllProviders, ...options });

export * from '@testing-library/react';
```

### Query Priority (Best to Worst)
```typescript
// 1. Accessible queries (best)
screen.getByRole('button', { name: 'Submit' });
screen.getByLabelText('Email');
screen.getByPlaceholderText('Enter email');
screen.getByText('Welcome');

// 2. Semantic queries
screen.getByAltText('Profile picture');
screen.getByTitle('Close');

// 3. Test IDs (last resort)
screen.getByTestId('submit-button');
```

### User Interactions
```typescript
import userEvent from '@testing-library/user-event';

test('form submission', async () => {
  const user = userEvent.setup();
  render(<LoginForm />);

  // Type in inputs
  await user.type(screen.getByLabelText('Email'), 'test@example.com');
  await user.type(screen.getByLabelText('Password'), 'password123');

  // Click button
  await user.click(screen.getByRole('button', { name: 'Sign in' }));

  // Check result
  await waitFor(() => {
    expect(screen.getByText('Welcome!')).toBeInTheDocument();
  });
});

test('keyboard navigation', async () => {
  const user = userEvent.setup();
  render(<Form />);

  await user.tab(); // Focus first element
  await user.keyboard('{Enter}'); // Press enter
  await user.keyboard('[ShiftLeft>][Tab][/ShiftLeft]'); // Shift+Tab
});
```

### Testing Hooks
```typescript
import { renderHook, act } from '@testing-library/react';
import { useCounter } from './useCounter';

test('useCounter increments', () => {
  const { result } = renderHook(() => useCounter());

  expect(result.current.count).toBe(0);

  act(() => {
    result.current.increment();
  });

  expect(result.current.count).toBe(1);
});

// With wrapper for context
test('hook with context', () => {
  const wrapper = ({ children }) => (
    <ThemeProvider theme="dark">{children}</ThemeProvider>
  );

  const { result } = renderHook(() => useTheme(), { wrapper });
  expect(result.current.theme).toBe('dark');
});
```

### Async Assertions
```typescript
import { waitFor, waitForElementToBeRemoved } from '@testing-library/react';

test('async loading', async () => {
  render(<DataFetcher />);

  // Wait for loading to disappear
  await waitForElementToBeRemoved(() => screen.queryByText('Loading...'));

  // Wait for content
  await waitFor(() => {
    expect(screen.getByText('Data loaded')).toBeInTheDocument();
  });

  // With timeout
  await waitFor(
    () => expect(screen.getByText('Slow content')).toBeInTheDocument(),
    { timeout: 5000 }
  );
});
```

## Network Mocking with MSW

### Setup
```typescript
// src/mocks/handlers.ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/users', () => {
    return HttpResponse.json([
      { id: 1, name: 'John' },
      { id: 2, name: 'Jane' },
    ]);
  }),

  http.post('/api/users', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({ id: 3, ...body }, { status: 201 });
  }),

  http.delete('/api/users/:id', ({ params }) => {
    return HttpResponse.json({ deleted: params.id });
  }),
];

// src/mocks/server.ts
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);
```

### Jest Setup
```typescript
// jest.setup.ts
import { server } from './src/mocks/server';

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

### Test-Specific Handlers
```typescript
import { server } from '../mocks/server';
import { http, HttpResponse } from 'msw';

test('handles error response', async () => {
  // Override for this test only
  server.use(
    http.get('/api/users', () => {
      return HttpResponse.json(
        { error: 'Server error' },
        { status: 500 }
      );
    })
  );

  render(<UserList />);

  await waitFor(() => {
    expect(screen.getByText('Failed to load users')).toBeInTheDocument();
  });
});

test('handles network error', async () => {
  server.use(
    http.get('/api/users', () => {
      return HttpResponse.error();
    })
  );

  render(<UserList />);

  await waitFor(() => {
    expect(screen.getByText('Network error')).toBeInTheDocument();
  });
});
```

### Request Assertions
```typescript
test('sends correct request', async () => {
  let capturedRequest: Request | null = null;

  server.use(
    http.post('/api/users', async ({ request }) => {
      capturedRequest = request.clone();
      return HttpResponse.json({ id: 1 });
    })
  );

  render(<CreateUserForm />);

  await userEvent.type(screen.getByLabelText('Name'), 'John');
  await userEvent.click(screen.getByRole('button', { name: 'Create' }));

  await waitFor(() => {
    expect(capturedRequest).not.toBeNull();
  });

  const body = await capturedRequest!.json();
  expect(body).toEqual({ name: 'John' });
});
```

## Custom Matchers

### Creating Custom Matchers
```typescript
// jest.setup.ts
expect.extend({
  toBeWithinRange(received: number, floor: number, ceiling: number) {
    const pass = received >= floor && received <= ceiling;
    return {
      pass,
      message: () =>
        pass
          ? `expected ${received} not to be within range ${floor} - ${ceiling}`
          : `expected ${received} to be within range ${floor} - ${ceiling}`,
    };
  },

  toHaveBeenCalledOnceWith(received: jest.Mock, ...args: unknown[]) {
    const pass =
      received.mock.calls.length === 1 &&
      JSON.stringify(received.mock.calls[0]) === JSON.stringify(args);
    return {
      pass,
      message: () =>
        pass
          ? `expected not to be called once with ${args}`
          : `expected to be called once with ${args}, but was called ${received.mock.calls.length} times`,
    };
  },
});

// Type declarations
declare global {
  namespace jest {
    interface Matchers<R> {
      toBeWithinRange(floor: number, ceiling: number): R;
      toHaveBeenCalledOnceWith(...args: unknown[]): R;
    }
  }
}
```

### Asymmetric Matchers
```typescript
test('asymmetric matchers', () => {
  const data = {
    id: 123,
    name: 'Test',
    createdAt: new Date().toISOString(),
  };

  expect(data).toEqual({
    id: expect.any(Number),
    name: expect.stringContaining('Test'),
    createdAt: expect.stringMatching(/^\d{4}-\d{2}-\d{2}/),
  });

  expect(['a', 'b', 'c']).toEqual(
    expect.arrayContaining(['a', 'c'])
  );

  expect({ a: 1, b: 2, c: 3 }).toEqual(
    expect.objectContaining({ a: 1, b: 2 })
  );
});
```

## Debugging Jest Tests

### Debug Output
```typescript
import { screen } from '@testing-library/react';

test('debugging', () => {
  render(<MyComponent />);

  // Print DOM
  screen.debug();

  // Print specific element
  screen.debug(screen.getByRole('button'));

  // Get readable DOM
  console.log(prettyDOM(container));
});
```

### Finding Slow Tests
```bash
# Run with verbose timing
jest --verbose

# Detect open handles
jest --detectOpenHandles

# Run tests serially to find interactions
jest --runInBand
```

### Common Debug Patterns
```typescript
// Check what's in the DOM
test('debug queries', () => {
  render(<MyComponent />);

  // Log all available roles
  screen.getByRole(''); // Will error with available roles

  // Check accessible name
  screen.logTestingPlaygroundURL(); // Opens playground
});

// Debug async issues
test('async debug', async () => {
  render(<AsyncComponent />);

  // Use findBy for async elements
  const element = await screen.findByText('Loaded');

  // Log state at each step
  screen.debug();
});
```

## CI/CD Integration

### GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test -- --coverage --ci

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info
```

### Jest CI Configuration
```javascript
// jest.config.js
module.exports = {
  // ... other config

  // CI-specific settings
  ...(process.env.CI && {
    maxWorkers: 2,
    ci: true,
    coverageReporters: ['lcov', 'text-summary'],
  }),

  // Coverage thresholds
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};
```

### Caching Dependencies
```yaml
# In GitHub Actions
- name: Cache Jest
  uses: actions/cache@v3
  with:
    path: |
      node_modules/.cache/jest
    key: jest-${{ runner.os }}-${{ hashFiles('**/jest.config.js') }}
```

## Common Issues & Solutions

### Issue: Tests are slow
- Use `jest.mock()` for expensive modules
- Run tests in parallel with `--maxWorkers`
- Use `beforeAll` for expensive setup
- Mock network requests with MSW

### Issue: Flaky tests
- Mock timers for timing-dependent code
- Use `waitFor` for async state changes
- Avoid shared mutable state
- Use `findBy` queries for async elements

### Issue: Mock not working
- Ensure mock is before import
- Use `jest.resetModules()` between tests
- Check module path matches exactly
- Use `jest.doMock()` for dynamic mocks

### Issue: Memory leaks
- Clean up in `afterEach`
- Mock timers with `jest.useFakeTimers()`
- Use `--detectLeaks` flag
- Check for unresolved promises

## Examples

### Example 1: Testing a React Component
When testing React components:
1. Check for React Testing Library usage
2. Verify proper queries (getByRole, getByLabelText)
3. Test user interactions with userEvent
4. Assert on accessible elements

### Example 2: Testing API Calls
When testing code that makes API calls:
1. Mock fetch or axios at module level
2. Test success and error scenarios
3. Verify request parameters
4. Test loading states

## Version Compatibility

The patterns in this skill require the following minimum versions:

| Package | Minimum Version | Features Used |
|---------|----------------|---------------|
| Jest | 29.0+ | Modern mock APIs, ESM support |
| @testing-library/react | 14.0+ | renderHook in main package |
| @testing-library/user-event | 14.0+ | userEvent.setup() API |
| msw | 2.0+ | http, HttpResponse (v1 used rest, ctx) |
| @testing-library/jest-dom | 6.0+ | Modern matchers |

### Migration Notes

**MSW v1 → v2**:
```typescript
// v1 (deprecated)
import { rest } from 'msw';
rest.get('/api', (req, res, ctx) => res(ctx.json(data)));

// v2 (current)
import { http, HttpResponse } from 'msw';
http.get('/api', () => HttpResponse.json(data));
```

**user-event v13 → v14**:
```typescript
// v13 (deprecated)
userEvent.click(button);

// v14 (current)
const user = userEvent.setup();
await user.click(button);
```

## Important Notes

- Jest is automatically invoked by Claude when relevant
- Always check for jest.config.js/ts for project-specific settings
- Use `{baseDir}` variable to reference skill resources
- Prefer Testing Library queries over direct DOM access for React
