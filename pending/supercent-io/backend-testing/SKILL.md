---
name: backend-testing
description: Write comprehensive backend tests including unit tests, integration tests, and API tests. Use when testing REST APIs, database operations, authentication flows, or business logic. Handles Jest, Pytest, Mocha, testing strategies, mocking, and test coverage.
metadata:
  tags: testing, backend, unit-test, integration-test, API-test, Jest, Pytest, TDD
  platforms: Claude, ChatGPT, Gemini
---


# Backend Testing


## When to use this skill

Specific situations that should trigger this skill:

- **New feature development**: Write tests first using TDD (Test-Driven Development)
- **Adding API endpoints**: Test success and failure cases for REST APIs
- **Bug fixes**: Add tests to prevent regressions
- **Before refactoring**: Write tests that guarantee existing behavior
- **CI/CD setup**: Build automated test pipelines

## Input Format

Format and required/optional information to collect from the user:

### Required information
- **Framework**: Express, Django, FastAPI, Spring Boot, etc.
- **Test tool**: Jest, Pytest, Mocha/Chai, JUnit, etc.
- **Test target**: API endpoints, business logic, DB operations, etc.

### Optional information
- **Database**: PostgreSQL, MySQL, MongoDB (default: in-memory DB)
- **Mocking library**: jest.mock, sinon, unittest.mock (default: framework built-in)
- **Coverage target**: 80%, 90%, etc. (default: 80%)
- **E2E tool**: Supertest, TestClient, RestAssured (optional)

### Input example

```
Test the user authentication endpoints for an Express.js API:
- Framework: Express + TypeScript
- Test tool: Jest + Supertest
- Target: POST /auth/register, POST /auth/login
- DB: PostgreSQL (in-memory for tests)
- Coverage: 90% or above
```

## Instructions

Step-by-step task order to follow precisely.

### Step 1: Set up the test environment

Install and configure the test framework and tools.

**Tasks**:
- Install test libraries
- Configure test database (in-memory or separate DB)
- Separate environment variables (.env.test)
- Configure jest.config.js or pytest.ini

**Example** (Node.js + Jest + Supertest):
```bash
npm install --save-dev jest ts-jest @types/jest supertest @types/supertest
```

**jest.config.js**:
```javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.test.ts'],
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/__tests__/**'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  setupFilesAfterEnv: ['<rootDir>/src/__tests__/setup.ts']
};
```

**setup.ts** (global test configuration):
```typescript
import { db } from '../database';

// Reset DB before each test
beforeEach(async () => {
  await db.migrate.latest();
  await db.seed.run();
});

// Clean up after each test
afterEach(async () => {
  await db.migrate.rollback();
});

// Close connection after all tests complete
afterAll(async () => {
  await db.destroy();
});
```

### Step 2: Write Unit Tests (business logic)

Write unit tests for individual functions and classes.

**Tasks**:
- Test pure functions (no dependencies)
- Isolate dependencies via mocking
- Test edge cases (boundary values, exceptions)
- AAA pattern (Arrange-Act-Assert)

**Decision criteria**:
- No external dependencies (DB, API) -> pure Unit Test
- External dependencies present -> use Mock/Stub
- Complex logic -> test various input cases

**Example** (password validation function):
```typescript
// src/utils/password.ts
export function validatePassword(password: string): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (password.length < 8) {
    errors.push('Password must be at least 8 characters');
  }

  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain uppercase letter');
  }

  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain lowercase letter');
  }

  if (!/\d/.test(password)) {
    errors.push('Password must contain number');
  }

  if (!/[!@#$%^&*]/.test(password)) {
    errors.push('Password must contain special character');
  }

  return { valid: errors.length === 0, errors };
}

// src/__tests__/utils/password.test.ts
import { validatePassword } from '../../utils/password';

describe('validatePassword', () => {
  it('should accept valid password', () => {
    const result = validatePassword('Password123!');
    expect(result.valid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  it('should reject password shorter than 8 characters', () => {
    const result = validatePassword('Pass1!');
    expect(result.valid).toBe(false);
    expect(result.errors).toContain('Password must be at least 8 characters');
  });

  it('should reject password without uppercase', () => {
    const result = validatePassword('password123!');
    expect(result.valid).toBe(false);
    expect(result.errors).toContain('Password must contain uppercase letter');
  });

  it('should reject password without lowercase', () => {
    const result = validatePassword('PASSWORD123!');
    expect(result.valid).toBe(false);
    expect(result.errors).toContain('Password must contain lowercase letter');
  });

  it('should reject password without number', () => {
    const result = validatePassword('Password!');
    expect(result.valid).toBe(false);
    expect(result.errors).toContain('Password must contain number');
  });

  it('should reject password without special character', () => {
    const result = validatePassword('Password123');
    expect(result.valid).toBe(false);
    expect(result.errors).toContain('Password must contain special character');
  });

  it('should return multiple errors for invalid password', () => {
    const result = validatePassword('pass');
    expect(result.valid).toBe(false);
    expect(result.errors.length).toBeGreaterThan(1);
  });
});
```

### Step 3: Integration Test (API endpoints)

Write integration tests for API endpoints.

**Tasks**:
- Test HTTP requests/responses
- Success cases (200, 201)
- Failure cases (400, 401, 404, 500)
- Authentication/authorization tests
- Input validation tests

**Checklist**:
- [x] Verify status code
- [x] Validate response body structure
- [x] Confirm database state changes
- [x] Validate error messages

**Example** (Express.js + Supertest):
```typescript
// src/__tests__/api/auth.test.ts
import request from 'supertest';
import app from '../../app';
import { db } from '../../database';

describe('POST /auth/register', () => {
  it('should register new user successfully', async () => {
    const response = await request(app)
      .post('/api/auth/register')
      .send({
        email: 'test@example.com',
        username: 'testuser',
        password: 'Password123!'
      });

    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty('user');
    expect(response.body).toHaveProperty('accessToken');
    expect(response.body.user.email).toBe('test@example.com');

    // Verify the record was actually saved to DB
    const user = await db.user.findUnique({ where: { email: 'test@example.com' } });
    expect(user).toBeTruthy();
    expect(user.username).toBe('testuser');
  });

  it('should reject duplicate email', async () => {
    // Create first user
    await request(app)
      .post('/api/auth/register')
      .send({
        email: 'test@example.com',
        username: 'user1',
        password: 'Password123!'
      });

    // Second attempt with same email
    const response = await request(app)
      .post('/api/auth/register')
      .send({
        email: 'test@example.com',
        username: 'user2',
        password: 'Password123!'
      });

    expect(response.status).toBe(409);
    expect(response.body.error).toContain('already exists');
  });

  it('should reject weak password', async () => {
    const response = await request(app)
      .post('/api/auth/register')
      .send({
        email: 'test@example.com',
        username: 'testuser',
        password: 'weak'
      });

    expect(response.status).toBe(400);
    expect(response.body.error).toBeDefined();
  });

  it('should reject missing fields', async () => {
    const response = await request(app)
      .post('/api/auth/register')
      .send({
        email: 'test@example.com'
        // username, password omitted
      });

    expect(response.status).toBe(400);
  });
});

describe('POST /auth/login', () => {
  beforeEach(async () => {
    // Create test user
    await request(app)
      .post('/api/auth/register')
      .send({
        email: 'test@example.com',
        username: 'testuser',
        password: 'Password123!'
      });
  });

  it('should login with valid credentials', async () => {
    const response = await request(app)
      .post('/api/auth/login')
      .send({
        email: 'test@example.com',
        password: 'Password123!'
      });

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('accessToken');
    expect(response.body).toHaveProperty('refreshToken');
    expect(response.body.user.email).toBe('test@example.com');
  });

  it('should reject invalid password', async () => {
    const response = await request(app)
      .post('/api/auth/login')
      .send({
        email: 'test@example.com',
        password: 'WrongPassword123!'
      });

    expect(response.status).toBe(401);
    expect(response.body.error).toContain('Invalid credentials');
  });

  it('should reject non-existent user', async () => {
    const response = await request(app)
      .post('/api/auth/login')
      .send({
        email: 'nonexistent@example.com',
        password: 'Password123!'
      });

    expect(response.status).toBe(401);
  });
});
```

### Step 4: Authentication/Authorization Tests

Test JWT tokens and role-based access control.

**Tasks**:
- Confirm 401 when accessing without a token
- Confirm successful access with a valid token
- Test expired token handling
- Role-based permission tests

**Example**:
```typescript
describe('Protected Routes', () => {
  let accessToken: string;
  let adminToken: string;

  beforeEach(async () => {
    // Regular user token
    const userResponse = await request(app)
      .post('/api/auth/register')
      .send({
        email: 'user@example.com',
        username: 'user',
        password: 'Password123!'
      });
    accessToken = userResponse.body.accessToken;

    // Admin token
    const adminResponse = await request(app)
      .post('/api/auth/register')
      .send({
        email: 'admin@example.com',
        username: 'admin',
        password: 'Password123!'
      });
    // Update role to 'admin' in DB
    await db.user.update({
      where: { email: 'admin@example.com' },
      data: { role: 'admin' }
    });
    // Log in again to get a new token
    const loginResponse = await request(app)
      .post('/api/auth/login')
      .send({
        email: 'admin@example.com',
        password: 'Password123!'
      });
    adminToken = loginResponse.body.accessToken;
  });

  describe('GET /api/auth/me', () => {
    it('should return current user with valid token', async () => {
      const response = await request(app)
        .get('/api/auth/me')
        .set('Authorization', `Bearer ${accessToken}`);

      expect(response.status).toBe(200);
      expect(response.body.user.email).toBe('user@example.com');
    });

    it('should reject request without token', async () => {
      const response = await request(app)
        .get('/api/auth/me');

      expect(response.status).toBe(401);
    });

    it('should reject request with invalid token', async () => {
      const response = await request(app)
        .get('/api/auth/me')
        .set('Authorization', 'Bearer invalid-token');

      expect(response.status).toBe(403);
    });
  });

  describe('DELETE /api/users/:id (Admin only)', () => {
    it('should allow admin to delete user', async () => {
      const targetUser = await db.user.findUnique({ where: { email: 'user@example.com' } });

      const response = await request(app)
        .delete(`/api/users/${targetUser.id}`)
        .set('Authorization', `Bearer ${adminToken}`);

      expect(response.status).toBe(200);
    });

    it('should forbid non-admin from deleting user', async () => {
      const targetUser = await db.user.findUnique({ where: { email: 'user@example.com' } });

      const response = await request(app)
        .delete(`/api/users/${targetUser.id}`)
        .set('Authorization', `Bearer ${accessToken}`);

      expect(response.status).toBe(403);
    });
  });
});
```

### Step 5: Mocking and Test Isolation

Mock external dependencies to isolate tests.

**Tasks**:
- Mock external APIs
- Mock email sending
- Mock file system
- Mock time-related functions

**Example** (mocking an external API):
```typescript
// src/services/emailService.ts
export async function sendVerificationEmail(email: string, token: string): Promise<void> {
  const response = await fetch('https://api.sendgrid.com/v3/mail/send', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${process.env.SENDGRID_API_KEY}` },
    body: JSON.stringify({
      to: email,
      subject: 'Verify your email',
      html: `<a href="https://example.com/verify?token=${token}">Verify</a>`
    })
  });

  if (!response.ok) {
    throw new Error('Failed to send email');
  }
}

// src/__tests__/services/emailService.test.ts
import { sendVerificationEmail } from '../../services/emailService';

// Mock fetch
global.fetch = jest.fn();

describe('sendVerificationEmail', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear();
  });

  it('should send email successfully', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200
    });

    await expect(sendVerificationEmail('test@example.com', 'token123'))
      .resolves
      .toBeUndefined();

    expect(fetch).toHaveBeenCalledWith(
      'https://api.sendgrid.com/v3/mail/send',
      expect.objectContaining({
        method: 'POST'
      })
    );
  });

  it('should throw error if email sending fails', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 500
    });

    await expect(sendVerificationEmail('test@example.com', 'token123'))
      .rejects
      .toThrow('Failed to send email');
  });
});
```

## Output format

Defines the exact format that outputs must follow.

### Basic structure

```
project/
├── src/
│   ├── __tests__/
│   │   ├── setup.ts                 # Global test configuration
│   │   ├── utils/
│   │   │   └── password.test.ts     # Unit tests
│   │   ├── services/
│   │   │   └── emailService.test.ts
│   │   └── api/
│   │       ├── auth.test.ts         # Integration tests
│   │       └── users.test.ts
│   └── ...
├── jest.config.js
└── package.json
```

### Test run scripts (package.json)

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:ci": "jest --ci --coverage --maxWorkers=2"
  }
}
```

### Coverage report

```bash
$ npm run test:coverage

--------------------------|---------|----------|---------|---------|
File                      | % Stmts | % Branch | % Funcs | % Lines |
--------------------------|---------|----------|---------|---------|
All files                 |   92.5  |   88.3   |   95.2  |   92.8  |
 auth/                    |   95.0  |   90.0   |  100.0  |   95.0  |
  middleware.ts           |   95.0  |   90.0   |  100.0  |   95.0  |
  routes.ts               |   95.0  |   90.0   |  100.0  |   95.0  |
 utils/                   |   90.0  |   85.0   |   90.0  |   90.0  |
  password.ts             |   90.0  |   85.0   |   90.0  |   90.0  |
--------------------------|---------|----------|---------|---------|
```

## Constraints

Rules and prohibitions that must be strictly followed.

### Required rules (MUST)

1. **Test isolation**: Each test must be runnable independently
   - Reset state with beforeEach/afterEach
   - Do not depend on test execution order

2. **Clear test names**: The name must convey what the test verifies
   - ✅ 'should reject duplicate email'
   - ❌ 'test1'

3. **AAA pattern**: Arrange (setup) - Act (execute) - Assert (verify) structure
   - Improves readability
   - Clarifies test intent

### Prohibited (MUST NOT)

1. **No production DB**: Tests must use a separate or in-memory DB
   - Risk of losing real data
   - Cannot isolate tests

2. **No real external API calls**: Mock all external services
   - Removes network dependency
   - Speeds up tests
   - Reduces costs

3. **No Sleep/Timeout abuse**: Use fake timers for time-based tests
   - jest.useFakeTimers()
   - Prevents test slowdowns

### Security rules

- **No hardcoded secrets**: Never hardcode API keys or passwords in test code
- **Separate environment variables**: Use .env.test file

## Examples

### Example 1: Python FastAPI tests (Pytest)

**Situation**: Testing a FastAPI REST API

**User request**:
```
Test the user API built with FastAPI using pytest.
```

**Final result**:
```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# In-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

# tests/test_auth.py
def test_register_user_success(client):
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "Password123!"
    })

    assert response.status_code == 201
    assert "access_token" in response.json()
    assert response.json()["user"]["email"] == "test@example.com"

def test_register_duplicate_email(client):
    # First user
    client.post("/auth/register", json={
        "email": "test@example.com",
        "username": "user1",
        "password": "Password123!"
    })

    # Duplicate email
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "username": "user2",
        "password": "Password123!"
    })

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]

def test_login_success(client):
    # Register
    client.post("/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "Password123!"
    })

    # Login
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "Password123!"
    })

    assert response.status_code == 200
    assert "access_token" in response.json()

def test_protected_route_without_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401

def test_protected_route_with_token(client):
    # Register and get token
    register_response = client.post("/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "Password123!"
    })
    token = register_response.json()["access_token"]

    # Access protected route
    response = client.get("/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })

    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
```

## Best practices

### Quality improvements

1. **TDD (Test-Driven Development)**: Write tests before writing code
   - Clarifies requirements
   - Improves design
   - Naturally achieves high coverage

2. **Given-When-Then pattern**: Write tests in BDD style
   ```typescript
   it('should return 404 when user not found', async () => {
     // Given: a non-existent user ID
     const nonExistentId = 'non-existent-uuid';

     // When: attempting to look up that user
     const response = await request(app).get(`/users/${nonExistentId}`);

     // Then: 404 response
     expect(response.status).toBe(404);
   });
   ```

3. **Test Fixtures**: Reusable test data
   ```typescript
   const validUser = {
     email: 'test@example.com',
     username: 'testuser',
     password: 'Password123!'
   };
   ```

### Efficiency improvements

- **Parallel execution**: Speed up tests with Jest's `--maxWorkers` option
- **Snapshot Testing**: Save snapshots of UI components or JSON responses
- **Coverage thresholds**: Enforce minimum coverage in jest.config.js

## Common Issues

### Issue 1: Test failures caused by shared state between tests

**Symptom**: Passes individually but fails when run together

**Cause**: DB state shared due to missing beforeEach/afterEach

**Fix**:
```typescript
beforeEach(async () => {
  await db.migrate.rollback();
  await db.migrate.latest();
});
```

### Issue 2: "Jest did not exit one second after the test run"

**Symptom**: Process does not exit after tests complete

**Cause**: DB connections, servers, etc. not cleaned up

**Fix**:
```typescript
afterAll(async () => {
  await db.destroy();
  await server.close();
});
```

### Issue 3: Async test timeout

**Symptom**: "Timeout - Async callback was not invoked"

**Cause**: Missing async/await or unhandled Promise

**Fix**:
```typescript
// Bad
it('should work', () => {
  request(app).get('/users');  // Promise not handled
});

// Good
it('should work', async () => {
  await request(app).get('/users');
});
```

## References

### Official docs
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Pytest Documentation](https://docs.pytest.org/)
- [Supertest GitHub](https://github.com/visionmedia/supertest)

### Learning resources
- [Testing JavaScript with Kent C. Dodds](https://testingjavascript.com/)
- [Test-Driven Development by Example (Kent Beck)](https://www.amazon.com/Test-Driven-Development-Kent-Beck/dp/0321146530)

### Tools
- [Istanbul/nyc](https://istanbul.js.org/) - code coverage
- [nock](https://github.com/nock/nock) - HTTP mocking
- [faker.js](https://fakerjs.dev/) - test data generation

## Metadata

### Version
- **Current version**: 1.0.0
- **Last updated**: 2025-01-01
- **Compatible platforms**: Claude, ChatGPT, Gemini

### Related skills
- [api-design](../api-design/SKILL.md): Design APIs alongside tests
- [authentication-setup](../authentication/SKILL.md): Test authentication systems

### Tags
`#testing` `#backend` `#Jest` `#Pytest` `#unit-test` `#integration-test` `#TDD` `#API-test`
