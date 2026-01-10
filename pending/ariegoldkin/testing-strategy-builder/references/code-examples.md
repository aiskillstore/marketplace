# Testing Code Examples

Detailed code examples for various testing scenarios.

## Unit Test Examples

### Basic Function Testing

```typescript
// Function to test
function calculateDiscount(price: number, discountPercent: number): number {
  if (price < 0 || discountPercent < 0 || discountPercent > 100) {
    throw new Error('Invalid input');
  }
  return price * (1 - discountPercent / 100);
}

// Unit test
describe('calculateDiscount', () => {
  it('should apply 20% discount correctly', () => {
    expect(calculateDiscount(100, 20)).toBe(80);
  });

  it('should throw error for negative price', () => {
    expect(() => calculateDiscount(-10, 20)).toThrow('Invalid input');
  });

  it('should throw error for discount > 100%', () => {
    expect(() => calculateDiscount(100, 150)).toThrow('Invalid input');
  });

  it('should handle edge case: 0% discount', () => {
    expect(calculateDiscount(100, 0)).toBe(100);
  });

  it('should handle edge case: 100% discount', () => {
    expect(calculateDiscount(100, 100)).toBe(0);
  });
});
```

### Given-When-Then Pattern

```typescript
describe('Shopping Cart', () => {
  it('should apply discount when coupon code is valid', () => {
    // Given: Cart with items and valid coupon
    const cart = new ShoppingCart([
      { id: 1, price: 100, quantity: 2 },
    ]);
    const coupon = { code: 'SAVE20', discount: 20 };

    // When: Coupon is applied
    cart.applyCoupon(coupon);

    // Then: Total is discounted
    expect(cart.getTotal()).toBe(160); // (200 * 0.8)
  });
});
```

### AAA Pattern (Arrange-Act-Assert)

```typescript
test('should update user profile', async () => {
  // Arrange: Set up test data and context
  const userId = '123';
  const updates = { name: 'New Name' };
  const mockUser = createUser({ id: userId });
  jest.spyOn(userService, 'findById').mockResolvedValue(mockUser);

  // Act: Perform the action being tested
  const result = await userService.update(userId, updates);

  // Assert: Verify expected outcomes
  expect(result.name).toBe('New Name');
  expect(userService.findById).toHaveBeenCalledWith(userId);
});
```

---

## Integration Test Examples

### API Integration Test

```typescript
describe('POST /api/users', () => {
  it('should create user and return 201 with user data', async () => {
    const newUser = { email: 'test@example.com', name: 'Test User' };

    const response = await request(app)
      .post('/api/users')
      .send(newUser)
      .expect(201);

    expect(response.body).toMatchObject({
      id: expect.any(Number),
      email: 'test@example.com',
      name: 'Test User',
      created_at: expect.any(String),
    });

    // Verify user exists in database
    const user = await db.users.findOne({ email: 'test@example.com' });
    expect(user).toBeTruthy();
  });

  it('should return 422 for invalid email', async () => {
    const invalidUser = { email: 'not-an-email', name: 'Test User' };

    const response = await request(app)
      .post('/api/users')
      .send(invalidUser)
      .expect(422);

    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.details).toContainEqual({
      field: 'email',
      message: expect.stringContaining('valid email'),
    });
  });
});
```

---

## End-to-End Test Examples

### Complete User Journey

```typescript
test('user can complete checkout flow', async ({ page }) => {
  // 1. Login
  await page.goto('/login');
  await page.fill('[data-testid="email"]', 'user@example.com');
  await page.fill('[data-testid="password"]', 'password123');
  await page.click('[data-testid="login-button"]');

  // 2. Add item to cart
  await page.goto('/products/123');
  await page.click('[data-testid="add-to-cart"]');

  // 3. Checkout
  await page.goto('/cart');
  await page.click('[data-testid="checkout-button"]');

  // 4. Payment
  await page.fill('[data-testid="card-number"]', '4242424242424242');
  await page.fill('[data-testid="card-expiry"]', '12/25');
  await page.fill('[data-testid="card-cvc"]', '123');
  await page.click('[data-testid="submit-payment"]');

  // 5. Verify success
  await expect(page.locator('[data-testid="order-confirmation"]')).toBeVisible();
  await expect(page.locator('[data-testid="order-number"]')).toContainText(/ORD-\d+/);
});
```

---

## Performance Test Examples

### Load Test with k6

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests < 500ms
    http_req_failed: ['rate<0.01'],   // Error rate < 1%
  },
};

export default function () {
  const res = http.get('https://api.example.com/products');

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);
}
```

---

## Test Data Management Examples

### Test Factory

```typescript
import { faker } from '@faker-js/faker';

export function createUser(overrides = {}) {
  return {
    id: faker.string.uuid(),
    email: faker.internet.email(),
    name: faker.person.fullName(),
    role: 'user',
    created_at: faker.date.past().toISOString(),
    ...overrides,
  };
}

// Usage in tests
const adminUser = createUser({ role: 'admin' });
const testUser = createUser({ email: 'test@example.com' });
```

### Test Fixtures

```typescript
// fixtures/users.json
[
  {
    "id": "user-1",
    "email": "alice@example.com",
    "name": "Alice Smith",
    "role": "admin"
  },
  {
    "id": "user-2",
    "email": "bob@example.com",
    "name": "Bob Jones",
    "role": "user"
  }
]

// Usage
import usersFixture from './fixtures/users.json';

beforeEach(async () => {
  await db.users.insertMany(usersFixture);
});
```

---

## Mocking Examples

### Mocking External API

```typescript
// Mock payment gateway
jest.mock('../services/paymentGateway');

test('should process payment successfully', async () => {
  const mockCharge = jest.fn().mockResolvedValue({
    id: 'ch_123',
    status: 'succeeded',
  });

  (paymentGateway.charge as jest.Mock) = mockCharge;

  const result = await processPayment({
    amount: 1000,
    currency: 'usd',
    source: 'tok_visa',
  });

  expect(result.status).toBe('succeeded');
  expect(mockCharge).toHaveBeenCalledWith({
    amount: 1000,
    currency: 'usd',
    source: 'tok_visa',
  });
});
```

---

## Snapshot Testing

```typescript
import { render } from '@testing-library/react';

test('UserProfile renders correctly', () => {
  const user = createUser({ name: 'Jane Doe', email: 'jane@example.com' });
  const { container } = render(<UserProfile user={user} />);

  expect(container).toMatchSnapshot();
});
```

---

## Parameterized Tests

```typescript
describe('calculateDiscount', () => {
  const testCases = [
    { price: 100, discount: 10, expected: 90 },
    { price: 100, discount: 50, expected: 50 },
    { price: 200, discount: 25, expected: 150 },
    { price: 50, discount: 0, expected: 50 },
  ];

  testCases.forEach(({ price, discount, expected }) => {
    it(`should calculate ${discount}% discount on ${price} correctly`, () => {
      expect(calculateDiscount(price, discount)).toBe(expected);
    });
  });
});
```

---

## Test Isolation Example

```typescript
describe('User Service', () => {
  let db: Database;

  beforeEach(async () => {
    // Fresh database for each test
    db = await createTestDatabase();
  });

  afterEach(async () => {
    // Clean up after each test
    await db.destroy();
  });

  it('test 1', async () => {
    // Runs with clean database
  });

  it('test 2', async () => {
    // Runs with clean database (test 1 changes don't affect this)
  });
});
```
