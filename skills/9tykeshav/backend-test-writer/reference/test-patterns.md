# Test Patterns Reference

One complete example per category. Other CRUD operations follow same patterns.

**Setup:** See [test-setup.md](test-setup.md) for `beforeAll/afterAll/afterEach` boilerplate.

---

## Routes/Controllers (Integration)

```javascript
const request = require('supertest');
const app = require('../app');
// Setup: see test-setup.md for DB connection boilerplate

describe('POST /api/users', () => {
  describe('success', () => {
    it('should create and return 201', async () => {
      const res = await request(app)
        .post('/api/users')
        .send({ name: 'John', email: 'john@example.com', password: 'Pass123!' })
        .expect('Content-Type', /json/)
        .expect(201);

      expect(res.body).toHaveProperty('id');
      expect(res.body.email).toBe('john@example.com');
      expect(res.body).not.toHaveProperty('password'); // no leak
    });
  });

  describe('validation errors', () => {
    it('should return 400 for missing fields', async () => {
      const res = await request(app)
        .post('/api/users')
        .send({ name: 'John' }) // missing email, password
        .expect(400);
      expect(res.body).toHaveProperty('errors');
    });

    it('should return 400 for invalid email', async () => {
      await request(app)
        .post('/api/users')
        .send({ name: 'John', email: 'invalid', password: 'Pass123!' })
        .expect(400);
    });
  });

  describe('edge cases', () => {
    it('should return 409 for duplicate', async () => {
      const data = { name: 'John', email: 'john@example.com', password: 'Pass123!' };
      await request(app).post('/api/users').send(data);
      await request(app).post('/api/users').send(data).expect(409);
    });
  });
});

// GET /api/users/:id - same pattern: success (200), not found (404), invalid id (400)
// PUT /api/users/:id - same pattern + validation errors
// DELETE /api/users/:id - same pattern, expect 204 on success
```

**Other CRUD operations follow identical structure:**

| Method | Success | Not Found | Invalid Input |
|--------|---------|-----------|---------------|
| GET /:id | 200 + body | 404 | 400 (bad ObjectId) |
| PUT /:id | 200 + updated | 404 | 400 (validation) |
| DELETE /:id | 204 | 404 | 400 (bad ObjectId) |

---

## Protected Routes

```javascript
describe('Protected Routes', () => {
  let token;

  beforeAll(async () => {
    // Login to get token
    const res = await request(app)
      .post('/api/auth/login')
      .send({ email: 'test@example.com', password: 'Pass123!' });
    token = res.body.token;
  });

  it('should return 401 without token', async () => {
    await request(app).get('/api/profile').expect(401);
  });

  it('should return 401 with invalid token', async () => {
    await request(app)
      .get('/api/profile')
      .set('Authorization', 'Bearer invalid')
      .expect(401);
  });

  it('should return 200 with valid token', async () => {
    await request(app)
      .get('/api/profile')
      .set('Authorization', `Bearer ${token}`)
      .expect(200);
  });

  // RBAC: same pattern, but expect 403 for insufficient role
});
```

---

## Services (Unit)

```javascript
describe('UserService', () => {
  let service, mockRepo, mockEmail;

  beforeEach(() => {
    jest.clearAllMocks();
    mockRepo = {
      create: jest.fn(),
      findById: jest.fn(),
      findByEmail: jest.fn(),
    };
    mockEmail = { sendWelcome: jest.fn() };
    service = new UserService(mockRepo, mockEmail);
  });

  describe('createUser', () => {
    const data = { name: 'John', email: 'john@example.com', password: 'Pass123!' };

    it('should create user', async () => {
      mockRepo.findByEmail.mockResolvedValue(null);
      mockRepo.create.mockResolvedValue({ id: '1', ...data });

      const result = await service.createUser(data);

      expect(mockRepo.findByEmail).toHaveBeenCalledWith(data.email);
      expect(mockRepo.create).toHaveBeenCalled();
      expect(result).toHaveProperty('id');
    });

    it('should throw on duplicate', async () => {
      mockRepo.findByEmail.mockResolvedValue({ id: '1' });
      await expect(service.createUser(data)).rejects.toThrow('Email already exists');
      expect(mockRepo.create).not.toHaveBeenCalled();
    });

    it('should continue if email service fails', async () => {
      mockRepo.findByEmail.mockResolvedValue(null);
      mockRepo.create.mockResolvedValue({ id: '1' });
      mockEmail.sendWelcome.mockRejectedValue(new Error('SMTP'));

      const result = await service.createUser(data);
      expect(result).toHaveProperty('id'); // doesn't throw
    });
  });

  // getUserById: mockResolvedValue for found, null for not found → throw
  // updateUser: check exists first, then update
  // deleteUser: same pattern
});
```

---

## Models (Unit)

```javascript
describe('User Model', () => {
  describe('validation', () => {
    it('should require email', async () => {
      const user = new User({ name: 'John' });
      await expect(user.validate()).rejects.toThrow(/email/i);
    });

    it('should reject invalid email', async () => {
      const user = new User({ name: 'John', email: 'invalid', password: 'Pass!' });
      await expect(user.validate()).rejects.toThrow(/email/i);
    });

    it('should accept valid data', async () => {
      const user = new User({ name: 'John', email: 'john@example.com', password: 'Pass123!' });
      await expect(user.validate()).resolves.not.toThrow();
    });

    // Similar for: required fields, enum values, min/max length
  });

  describe('methods', () => {
    it('should compare password', async () => {
      const user = await User.create({ name: 'John', email: 'j@e.com', password: 'Pass!' });
      expect(await user.comparePassword('Pass!')).toBe(true);
      expect(await user.comparePassword('wrong')).toBe(false);
    });
  });

  describe('toJSON', () => {
    it('should exclude password', () => {
      const user = new User({ name: 'John', email: 'j@e.com', password: 'hash' });
      expect(user.toJSON()).not.toHaveProperty('password');
    });
  });
});
```

---

## Middleware (Unit)

```javascript
describe('Auth Middleware', () => {
  let req, res, next;

  beforeEach(() => {
    req = { headers: {} };
    res = { status: jest.fn().mockReturnThis(), json: jest.fn() };
    next = jest.fn();
  });

  it('should 401 without header', async () => {
    await authMiddleware(req, res, next);
    expect(res.status).toHaveBeenCalledWith(401);
    expect(next).not.toHaveBeenCalled();
  });

  it('should 401 with invalid token', async () => {
    req.headers.authorization = 'Bearer invalid';
    await authMiddleware(req, res, next);
    expect(res.status).toHaveBeenCalledWith(401);
  });

  it('should call next with valid token', async () => {
    const token = jwt.sign({ userId: '1' }, process.env.JWT_SECRET);
    req.headers.authorization = `Bearer ${token}`;
    await authMiddleware(req, res, next);
    expect(next).toHaveBeenCalled();
    expect(req.user).toBeDefined();
  });
});

// Validation middleware: same mock pattern, check req.body
// Error handler: test different error types (ValidationError, CastError, 11000)
```

---

## Utilities (Unit)

```javascript
describe('utils', () => {
  describe('slugify', () => {
    it.each([
      ['Hello World', 'hello-world'],
      ['foo bar baz', 'foo-bar-baz'],
      ['Hello! @World#', 'hello-world'],
      ['', ''],
    ])('slugify(%s) → %s', (input, expected) => {
      expect(slugify(input)).toBe(expected);
    });
  });

  describe('calculateDiscount', () => {
    it('should calculate correctly', () => {
      expect(calculateDiscount(100, 10)).toBe(90);
    });

    it('should throw for invalid input', () => {
      expect(() => calculateDiscount(-100, 10)).toThrow();
      expect(() => calculateDiscount(100, 150)).toThrow();
    });
  });
});
```

## Edge Case Patterns

```javascript
// Input validation - use it.each
it.each([
  [null, 'null'],
  [undefined, 'undefined'],
  ['', 'empty'],
  ['<script>', 'XSS'],
])('should reject %s (%s)', async (input) => {
  await request(app).post('/api/x').send({ field: input }).expect(400);
});

// Concurrent operations - race condition test
it('should handle duplicate race condition', async () => {
  const email = 'race@test.com';
  const results = await Promise.allSettled([
    request(app).post('/api/users').send({ name: 'A', email, password: 'P1!' }),
    request(app).post('/api/users').send({ name: 'B', email, password: 'P2!' }),
  ]);
  const created = results.filter(r => r.value?.status === 201);
  const rejected = results.filter(r => r.value?.status === 409);
  expect(created).toHaveLength(1);
  expect(rejected).toHaveLength(1);
});
```
