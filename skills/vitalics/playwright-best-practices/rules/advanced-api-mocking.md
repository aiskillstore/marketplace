---
title: Use API Mocking for Reliable and Fast Tests
impact: LOW
impactDescription: Improves test reliability and reduces execution time by 40-60% for API-dependent tests
tags: api, mocking, performance, reliability, advanced
---

## Use API Mocking for Reliable and Fast Tests

**Impact: LOW (improves test reliability and reduces execution time by 40-60% for API-dependent tests)**

API mocking allows you to intercept and mock network requests, making tests faster, more reliable, and independent of external services. This is especially valuable for testing error scenarios, edge cases, and reducing flakiness caused by network issues or third-party API dependencies.

## When to Use

- **Use API mocking when**: Testing UI error handling, loading states, edge cases, or when depending on third-party/paid/rate-limited APIs
- **Essential for**: Unit/component-level UI tests, testing error scenarios, offline development, CI/CD fast feedback loops
- **Consider real APIs when**: Running integration tests, E2E smoke tests, verifying actual API contracts, performance testing with realistic data
- **Required for**: Projects with external dependencies, third-party APIs, or when testing error handling is critical

## Guidelines

### Do

- Mock APIs for fast unit/component tests, use real APIs for critical integration tests
- Keep mock data realistic and synchronized with actual API responses
- Test both success and failure scenarios (4xx, 5xx errors, timeouts, network failures)
- Use fixtures for reusable mock patterns shared across multiple tests
- Document which endpoints are mocked in each test
- Version mock responses when API versions change
- Use `route.continue()` to let certain requests through while mocking others

### Don't

- Don't mock everything - some tests should verify real API integration
- Don't use stale mock data that doesn't match current API schema
- Don't forget to test error scenarios (500 errors, timeouts, malformed responses)
- Don't create overly complex mocks - keep them simple and maintainable
- Don't mock internal application APIs in E2E tests - only external dependencies
- Don't forget to remove mocks after tests (`page.unroute()` if needed)

### Tool Usage Patterns

- **Primary tools**: `page.route(pattern, handler)`, `route.fulfill()`, `route.continue()`, `route.abort()`, `route.fetch()`
- **Configuration**: Set `baseURL` in playwright.config.ts to simplify route patterns
- **Mock patterns**:
  - `route.fulfill({ status, body })` - Return mock response
  - `route.continue()` - Let request proceed to real server
  - `route.abort('failed')` - Simulate network failure
  - `route.fetch()` - Fetch real response, then modify it
- **Helper utilities**: Create fixture-based mocks for reusability, use helper functions to generate mock data

## Edge Cases and Constraints

### Limitations

- Mocks don't verify actual API behavior - real API might change without tests failing
- Mocked responses may drift from real API schema over time
- Complex authentication flows (OAuth, tokens) can be difficult to mock accurately
- WebSocket and Server-Sent Events (SSE) mocking is more complex than HTTP
- Service workers can interfere with route mocking if not properly handled
- CORS and authentication headers must be mocked correctly or requests may fail

### Edge Cases

1. **Concurrent requests to same endpoint**: Multiple parallel requests may need different responses. Solution: Track request count or use request body/headers to differentiate.

2. **Mock timing with parallel navigation**: If page navigates before mock is set up, requests go through unmocked. Solution: Set up mocks before `page.goto()` or use `page.route()` with `{ times: 1 }`.

3. **Mock cleanup between tests**: Mocks from one test may affect subsequent tests. Solution: Mocks are automatically cleared when page context is destroyed, or explicitly use `page.unroute()`.

4. **Wildcard route patterns conflicting**: Multiple `page.route()` patterns may match same request. Solution: Playwright uses last-registered route first, be careful with wildcard patterns.

5. **GraphQL endpoint mocking**: Single endpoint with different operations. Solution: Parse request body to determine operation and return appropriate mock.

6. **File upload mocking**: Multipart form data requires special handling. Solution: Use `route.fetch()` to get real request, modify, and fulfill.

### What Breaks If Ignored

- **Without mocking external dependencies**: Tests become flaky (network issues), slow (real API latency), expensive (API costs), and fail when external services are down
- **Without testing error scenarios**: Production bugs when APIs fail, poor user experience during errors
- **Without mock maintenance**: Tests pass with stale mocks while real API has breaking changes
- **Over-mocking everything**: Miss integration bugs between frontend and backend, false confidence

**Incorrect (relying on real API calls):**

```typescript
import { test, expect } from '@playwright/test';

test('bad - depends on real API', async ({ page }) => {
  // ❌ Test depends on external API availability
  await page.goto('https://example.com/products');
  
  // ❌ Slow - waits for real network requests
  // ❌ Flaky - fails if API is down or slow
  // ❌ Can't test error scenarios easily
  await expect(page.locator('.product')).toHaveCount(10);
  
  // ❌ Hard to test specific data scenarios
  await page.getByRole('button', { name: 'Load More' }).click();
  await expect(page.locator('.product')).toHaveCount(20);
});

test('bad - cannot test error states', async ({ page }) => {
  // ❌ How do you test API error handling?
  // You can't easily force the real API to return errors
  await page.goto('https://example.com/products');
  // Can't verify error handling behavior
});

test('bad - slow test due to API delays', async ({ page }) => {
  // ❌ Test is slow due to real API latency
  await page.goto('https://example.com/dashboard');
  
  // Waiting for multiple real API calls
  await page.waitForLoadState('networkidle'); // Could take seconds
  
  await expect(page.locator('.data-loaded')).toBeVisible();
});
```

**Correct (using API mocking):**

```typescript
import { test, expect } from '@playwright/test';

test('good - mock successful API response', async ({ page }) => {
  // ✅ Mock API response with controlled data
  await page.route('**/api/products', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        products: [
          { id: 1, name: 'Product 1', price: 19.99 },
          { id: 2, name: 'Product 2', price: 29.99 },
        ]
      })
    });
  });

  await page.goto('https://example.com/products');
  
  // ✅ Fast - no real network delay
  // ✅ Reliable - always returns same data
  await expect(page.locator('.product')).toHaveCount(2);
  await expect(page.locator('.product').first()).toContainText('Product 1');
});

test('good - test error scenarios', async ({ page }) => {
  // ✅ Easily test error handling
  await page.route('**/api/products', async route => {
    await route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ error: 'Internal Server Error' })
    });
  });

  await page.goto('https://example.com/products');
  
  // ✅ Verify error state is displayed correctly
  await expect(page.locator('.error-message')).toContainText('Failed to load products');
  await expect(page.getByRole('button', { name: 'Retry' })).toBeVisible();
});

test('good - test loading states', async ({ page }) => {
  // ✅ Control timing to test loading states
  await page.route('**/api/products', async route => {
    // Simulate slow API
    await new Promise(resolve => setTimeout(resolve, 1000));
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ products: [] })
    });
  });

  await page.goto('https://example.com/products');
  
  // ✅ Verify loading spinner appears
  await expect(page.locator('.loading-spinner')).toBeVisible();
  
  // Wait for mock to complete
  await expect(page.locator('.loading-spinner')).not.toBeVisible();
});
```

**Advanced mocking patterns:**

```typescript
test('mock with dynamic responses', async ({ page }) => {
  let requestCount = 0;
  
  // ✅ Track and vary responses based on request
  await page.route('**/api/products*', async route => {
    requestCount++;
    const url = new URL(route.request().url());
    const page = url.searchParams.get('page') || '1';
    
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        products: generateMockProducts(parseInt(page)),
        page: parseInt(page),
        hasMore: parseInt(page) < 3
      })
    });
  });

  await page.goto('https://example.com/products');
  await expect(page.locator('.product')).toHaveCount(10);
  
  await page.getByRole('button', { name: 'Next Page' }).click();
  await expect(page.locator('.product')).toHaveCount(20);
  
  expect(requestCount).toBe(2);
});

test('mock multiple endpoints', async ({ page }) => {
  // ✅ Mock all required endpoints
  await page.route('**/api/user', async route => {
    await route.fulfill({
      status: 200,
      body: JSON.stringify({ id: 1, name: 'John Doe', role: 'admin' })
    });
  });

  await page.route('**/api/notifications', async route => {
    await route.fulfill({
      status: 200,
      body: JSON.stringify({ count: 5, unread: 3 })
    });
  });

  await page.route('**/api/settings', async route => {
    await route.fulfill({
      status: 200,
      body: JSON.stringify({ theme: 'dark', language: 'en' })
    });
  });

  await page.goto('https://example.com/dashboard');
  await expect(page.locator('.username')).toHaveText('John Doe');
  await expect(page.locator('.notification-badge')).toHaveText('3');
});

test('conditional mocking - only mock specific scenarios', async ({ page }) => {
  // ✅ Mock only certain requests, let others through
  await page.route('**/api/**', async route => {
    const url = route.request().url();
    
    if (url.includes('/api/products')) {
      // Mock products endpoint
      await route.fulfill({
        status: 200,
        body: JSON.stringify({ products: [] })
      });
    } else {
      // Let other API calls through
      await route.continue();
    }
  });

  await page.goto('https://example.com');
});
```

**Using fixtures for reusable mocks:**

```typescript
// fixtures/api-mocks.fixture.ts
import { test as base } from '@playwright/test';

type MockFixtures = {
  mockProducts: void;
  mockUserAuth: void;
};

export const test = base.extend<MockFixtures>({
  mockProducts: async ({ page }, use) => {
    await page.route('**/api/products', async route => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          products: [
            { id: 1, name: 'Test Product', price: 99.99 }
          ]
        })
      });
    });
    await use();
  },

  mockUserAuth: async ({ page }, use) => {
    await page.route('**/api/auth/user', async route => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          authenticated: true,
          user: { id: 1, email: 'test@example.com' }
        })
      });
    });
    await use();
  }
});

// tests/with-mocks.spec.ts
import { test, expect } from '../fixtures/api-mocks.fixture';

test('use product mocks', async ({ page, mockProducts }) => {
  await page.goto('/products');
  await expect(page.locator('.product')).toHaveCount(1);
});

test('use auth mocks', async ({ page, mockUserAuth }) => {
  await page.goto('/profile');
  await expect(page.locator('.email')).toHaveText('test@example.com');
});
```

**Inspecting and modifying real responses:**

```typescript
test('modify real API responses', async ({ page }) => {
  // ✅ Intercept and modify real responses
  await page.route('**/api/products', async route => {
    const response = await route.fetch();
    const data = await response.json();
    
    // Modify the real data
    data.products = data.products.map((p: any) => ({
      ...p,
      price: p.price * 0.5 // Apply 50% discount
    }));
    
    await route.fulfill({
      response,
      body: JSON.stringify(data)
    });
  });

  await page.goto('https://example.com/products');
  // Now all prices are halved
});

test('add artificial delays to real APIs', async ({ page }) => {
  // ✅ Test how UI handles slow responses
  await page.route('**/api/**', async route => {
    await new Promise(resolve => setTimeout(resolve, 2000));
    await route.continue();
  });

  await page.goto('https://example.com');
  await expect(page.locator('.loading')).toBeVisible();
});
```

**Testing network failures:**

```typescript
test('handle network timeouts', async ({ page }) => {
  // ✅ Simulate timeout
  await page.route('**/api/products', async route => {
    await route.abort('timedout');
  });

  await page.goto('https://example.com/products');
  await expect(page.locator('.error')).toContainText('Request timed out');
});

test('handle connection failures', async ({ page }) => {
  // ✅ Simulate network failure
  await page.route('**/api/products', async route => {
    await route.abort('failed');
  });

  await page.goto('https://example.com/products');
  await expect(page.locator('.offline-message')).toBeVisible();
});
```

## Common Mistakes

### Mistake 1: Setting up mocks after navigation

```typescript
// ❌ Bad: Mock is set up AFTER page loads
test('bad mock timing', async ({ page }) => {
  await page.goto('https://example.com/products'); // Requests already fired!
  
  await page.route('**/api/products', async route => {
    await route.fulfill({ body: '[]' }); // Too late - request already completed
  });
  
  // Test will use real API data, not mock
});
```

**Why this is wrong**: By the time the mock is registered, the page has already loaded and API requests have completed.

**How to fix**:

```typescript
// ✅ Good: Mock BEFORE navigation
test('correct mock timing', async ({ page }) => {
  // Set up mock first
  await page.route('**/api/products', async route => {
    await route.fulfill({ 
      status: 200,
      body: JSON.stringify({ products: [] })
    });
  });
  
  // Then navigate
  await page.goto('https://example.com/products');
  // Mock is active and intercepts requests
});
```

### Mistake 2: Not testing error scenarios

```typescript
// ❌ Bad: Only test success case
test('only happy path', async ({ page }) => {
  await page.route('**/api/products', async route => {
    await route.fulfill({
      status: 200,
      body: JSON.stringify({ products: [/* data */] })
    });
  });
  
  await page.goto('/products');
  // What happens if API returns 500? We never test that!
});
```

**Why this is wrong**: Production will experience API errors, but tests don't verify error handling works.

**How to fix**:

```typescript
// ✅ Good: Test both success and failure
test('success case', async ({ page }) => {
  await page.route('**/api/products', async route => {
    await route.fulfill({ status: 200, body: JSON.stringify({ products: [] }) });
  });
  await page.goto('/products');
  await expect(page.locator('.product-list')).toBeVisible();
});

test('error case - 500', async ({ page }) => {
  await page.route('**/api/products', async route => {
    await route.fulfill({ 
      status: 500, 
      body: JSON.stringify({ error: 'Internal Server Error' })
    });
  });
  await page.goto('/products');
  await expect(page.locator('.error-message')).toContainText('Failed to load');
});

test('error case - timeout', async ({ page }) => {
  await page.route('**/api/products', async route => {
    await route.abort('timedout');
  });
  await page.goto('/products');
  await expect(page.locator('.error-message')).toContainText('Request timed out');
});
```

### Mistake 3: Using stale mock data

```typescript
// ❌ Bad: Mock data doesn't match current API
test('stale mock data', async ({ page }) => {
  await page.route('**/api/user', async route => {
    await route.fulfill({
      status: 200,
      body: JSON.stringify({
        id: 1,
        name: 'John Doe',
        // ❌ Real API now returns 'email', 'role', 'avatar'
        // but mock is outdated and missing these fields
      })
    });
  });
  
  await page.goto('/profile');
  // May fail or show incorrect UI because mock is incomplete
});
```

**Why this is wrong**: Mock data drifts from real API schema, tests pass but production breaks.

**How to fix**:

```typescript
// ✅ Good: Keep mock data synchronized with API schema
// api-mocks/user.mock.ts
export const mockUserResponse = {
  id: 1,
  name: 'John Doe',
  email: 'john@example.com',
  role: 'admin',
  avatar: 'https://example.com/avatar.jpg',
  createdAt: '2024-01-01T00:00:00Z'
  // Update this when API schema changes
};

// tests/profile.spec.ts
import { mockUserResponse } from '../api-mocks/user.mock';

test('current mock data', async ({ page }) => {
  await page.route('**/api/user', async route => {
    await route.fulfill({
      status: 200,
      body: JSON.stringify(mockUserResponse)
    });
  });
  
  await page.goto('/profile');
  await expect(page.locator('.email')).toHaveText(mockUserResponse.email);
});
```

### Mistake 4: Overly broad route patterns

```typescript
// ❌ Bad: Too broad, mocks everything
test('broad pattern', async ({ page }) => {
  await page.route('**/*', async route => {
    await route.fulfill({ status: 200, body: '{}' });
    // ❌ This mocks EVERYTHING including images, fonts, CSS, analytics
  });
  
  await page.goto('/products');
  // Nothing loads correctly - too much is mocked!
});
```

**Why this is wrong**: Mocking too broadly breaks unrelated functionality and makes tests unrealistic.

**How to fix**:

```typescript
// ✅ Good: Specific patterns for what you need
test('specific patterns', async ({ page }) => {
  // Only mock specific API endpoints
  await page.route('**/api/products', async route => {
    await route.fulfill({ status: 200, body: JSON.stringify({ products: [] }) });
  });
  
  await page.route('**/api/user', async route => {
    await route.fulfill({ status: 200, body: JSON.stringify({ id: 1, name: 'John' }) });
  });
  
  // Everything else (images, fonts, CSS) loads normally
  await page.goto('/products');
});

// Or use conditional logic
test('conditional mocking', async ({ page }) => {
  await page.route('**/*', async route => {
    const url = route.request().url();
    
    if (url.includes('/api/')) {
      // Mock only API calls
      await route.fulfill({ status: 200, body: '{}' });
    } else {
      // Let everything else through
      await route.continue();
    }
  });
});
```

## Benefits and Best Practices

Benefits of API mocking:
- **Speed**: Tests run 10-100x faster without real network calls
- **Reliability**: No flakiness from network issues or API downtime
- **Control**: Test specific scenarios including edge cases and errors
- **Isolation**: Tests don't depend on external services or test data
- **Repeatability**: Same results every time, no random failures
- **Cost**: Reduce API usage costs and rate limiting issues
- **Development**: Work offline or with incomplete backend services

When to use API mocking:
- ✅ Testing UI error handling and edge cases
- ✅ Testing loading states and transitions
- ✅ Fast feedback in CI/CD pipelines
- ✅ Third-party API dependencies
- ✅ Rate-limited or paid APIs
- ✅ Development against incomplete backends

When to use real APIs:
- ✅ Integration tests verifying actual API contracts
- ✅ End-to-end smoke tests in staging/production
- ✅ Performance testing with realistic data
- ✅ Testing actual authentication flows

Best practices:
- Use mocks for unit/component-level UI tests
- Use real APIs for integration and E2E tests (subset)
- Keep mock data realistic and up-to-date
- Version mock responses with API versions
- Use fixtures for reusable mock patterns
- Document what endpoints are mocked in tests

Reference: [Playwright Network Mocking](https://playwright.dev/docs/network)