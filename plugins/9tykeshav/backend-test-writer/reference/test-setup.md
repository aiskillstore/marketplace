# Test Setup Reference

Essential setup files. Copy and adapt.

## Jest Config

```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/*.test.js'],
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  clearMocks: true,
  testTimeout: 30000,
  forceExit: true,
  collectCoverageFrom: ['src/**/*.js', '!src/**/*.test.js'],
};
```

```json
// package.json scripts
{
  "test": "jest",
  "test:watch": "jest --watch",
  "test:coverage": "jest --coverage"
}
```

## Database Setup

```javascript
// tests/setup.js
const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');

let mongoServer;

beforeAll(async () => {
  mongoServer = await MongoMemoryServer.create();
  await mongoose.connect(mongoServer.getUri());
});

afterAll(async () => {
  await mongoose.disconnect();
  await mongoServer.stop();
});

afterEach(async () => {
  const collections = mongoose.connection.collections;
  for (const key in collections) {
    await collections[key].deleteMany({});
  }
});
```

## Fixtures

```javascript
// tests/fixtures/user.fixture.js
const { faker } = require('@faker-js/faker');

const createUser = (overrides = {}) => ({
  name: faker.person.fullName(),
  email: faker.internet.email(),
  password: 'TestPass123!',
  ...overrides,
});

const createMany = (count, overrides = {}) =>
  Array.from({ length: count }, () => createUser(overrides));

module.exports = { createUser, createMany };
```

## Auth Helper

```javascript
// tests/helpers/auth.helper.js
const request = require('supertest');
const app = require('../../src/app');

const getAuthToken = async (userData = {}) => {
  const user = {
    email: `test${Date.now()}@example.com`,
    password: 'TestPass123!',
    ...userData,
  };
  await request(app).post('/api/auth/register').send(user);
  const res = await request(app).post('/api/auth/login').send(user);
  return res.body.token;
};

module.exports = { getAuthToken };
```

## Mocking

```javascript
// Module mock
jest.mock('../../src/services/email', () => ({
  send: jest.fn().mockResolvedValue(true),
}));

// Spy (partial mock)
jest.spyOn(service, 'method').mockResolvedValue(result);

// External API
jest.mock('axios');
axios.get.mockResolvedValue({ data: { id: 1 } });
axios.get.mockRejectedValue(new Error('Network'));
```

## Dependencies

```bash
npm i -D jest supertest mongodb-memory-server @faker-js/faker
```
