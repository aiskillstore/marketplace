---
name: mock-server
description: Create and manage mock API servers for development and testing.
---

# Mock Server Skill

Create and manage mock API servers for development and testing.

## Instructions

You are a mock API server expert. When invoked:

1. **Create Mock Servers**:
   - Generate mock API endpoints from OpenAPI specs
   - Create custom mock responses
   - Simulate different response scenarios
   - Mock REST and GraphQL APIs
   - Handle various HTTP methods

2. **Configure Behavior**:
   - Set response delays/latency
   - Simulate error conditions
   - Return different responses based on input
   - Implement state management
   - Mock authentication

3. **Advanced Scenarios**:
   - Simulate network failures
   - Random error injection
   - Rate limiting simulation
   - Conditional responses
   - CORS configuration

4. **Integration**:
   - Proxy to real APIs
   - Record and replay requests
   - Generate mock data
   - Integration with testing frameworks

## Usage Examples

```
@mock-server
@mock-server --from-openapi
@mock-server --port 3000
@mock-server --with-delays
@mock-server --graphql
```

## JSON Server (Simple Mock)

### Quick Setup
```bash
# Install
npm install -g json-server

# Create db.json
cat > db.json << EOF
{
  "users": [
    { "id": 1, "name": "John Doe", "email": "john@example.com" },
    { "id": 2, "name": "Jane Smith", "email": "jane@example.com" }
  ],
  "posts": [
    { "id": 1, "title": "Hello World", "userId": 1 },
    { "id": 2, "title": "Mock APIs", "userId": 2 }
  ]
}
EOF

# Start server
json-server --watch db.json --port 3000
```

### Available Endpoints (Auto-generated)
```bash
# GET all users
curl http://localhost:3000/users

# GET user by ID
curl http://localhost:3000/users/1

# POST new user
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Bob", "email": "bob@example.com"}'

# PUT update user
curl -X PUT http://localhost:3000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "name": "John Updated", "email": "john.new@example.com"}'

# PATCH partial update
curl -X PATCH http://localhost:3000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "John Patched"}'

# DELETE user
curl -X DELETE http://localhost:3000/users/1

# Query parameters
curl "http://localhost:3000/users?_page=1&_limit=10"
curl "http://localhost:3000/users?_sort=name&_order=asc"
curl "http://localhost:3000/posts?userId=1"
```

### Custom Routes
```javascript
// routes.json
{
  "/api/*": "/$1",
  "/users/:id/posts": "/posts?userId=:id",
  "/auth/login": "/login"
}

// Start with custom routes
json-server db.json --routes routes.json
```

## Mock Service Worker (MSW)

### Setup
```bash
npm install --save-dev msw
```

### REST API Mocking
```javascript
// src/mocks/handlers.js
import { http, HttpResponse } from 'msw';

export const handlers = [
  // GET users
  http.get('/api/users', () => {
    return HttpResponse.json([
      { id: '1', name: 'John Doe', email: 'john@example.com' },
      { id: '2', name: 'Jane Smith', email: 'jane@example.com' }
    ]);
  }),

  // GET user by ID
  http.get('/api/users/:userId', ({ params }) => {
    const { userId } = params;

    // Simulate not found
    if (userId === '999') {
      return new HttpResponse(null, { status: 404 });
    }

    return HttpResponse.json({
      id: userId,
      name: 'John Doe',
      email: 'john@example.com'
    });
  }),

  // POST create user
  http.post('/api/users', async ({ request }) => {
    const data = await request.json();

    // Simulate validation error
    if (!data.email) {
      return HttpResponse.json(
        { error: 'Email is required' },
        { status: 400 }
      );
    }

    return HttpResponse.json(
      {
        id: '123',
        ...data,
        createdAt: new Date().toISOString()
      },
      { status: 201 }
    );
  }),

  // PUT update user
  http.put('/api/users/:userId', async ({ params, request }) => {
    const { userId } = params;
    const data = await request.json();

    return HttpResponse.json({
      id: userId,
      ...data,
      updatedAt: new Date().toISOString()
    });
  }),

  // DELETE user
  http.delete('/api/users/:userId', ({ params }) => {
    return new HttpResponse(null, { status: 204 });
  }),

  // Simulate delay
  http.get('/api/slow-endpoint', async () => {
    await delay(2000); // 2 second delay
    return HttpResponse.json({ message: 'Slow response' });
  }),

  // Simulate random errors
  http.get('/api/unreliable', () => {
    if (Math.random() > 0.5) {
      return new HttpResponse(null, { status: 500 });
    }
    return HttpResponse.json({ status: 'ok' });
  }),

  // Authentication
  http.post('/api/auth/login', async ({ request }) => {
    const { email, password } = await request.json();

    if (email === 'user@example.com' && password === 'password') {
      return HttpResponse.json({
        accessToken: 'mock-jwt-token',
        refreshToken: 'mock-refresh-token',
        expiresIn: 3600
      });
    }

    return HttpResponse.json(
      { error: 'Invalid credentials' },
      { status: 401 }
    );
  })
];

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
```

### Browser Setup
```javascript
// src/mocks/browser.js
import { setupWorker } from 'msw/browser';
import { handlers } from './handlers';

export const worker = setupWorker(...handlers);

// src/index.js
if (process.env.NODE_ENV === 'development') {
  const { worker } = await import('./mocks/browser');
  await worker.start();
}
```

### Node.js Setup (Testing)
```javascript
// src/mocks/server.js
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);

// src/tests/setup.js
import { server } from '../mocks/server';

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

## Prism (OpenAPI-based)

### From OpenAPI Spec
```bash
# Install
npm install -g @stoplight/prism-cli

# Start mock server from OpenAPI spec
prism mock openapi.yaml

# Specify port
prism mock openapi.yaml --port 4010

# Enable validation
prism mock openapi.yaml --errors

# Dynamic responses based on examples
prism mock openapi.yaml --dynamic
```

### Example OpenAPI for Prism
```yaml
openapi: 3.0.0
info:
  title: Mock API
  version: 1.0.0

paths:
  /api/users:
    get:
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
              examples:
                success:
                  value:
                    - id: "1"
                      name: "John Doe"
                      email: "john@example.com"

  /api/users/{userId}:
    get:
      parameters:
        - name: userId
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
              examples:
                user:
                  value:
                    id: "1"
                    name: "John Doe"
                    email: "john@example.com"
        '404':
          description: Not found
          content:
            application/json:
              examples:
                notFound:
                  value:
                    error: "User not found"

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        email:
          type: string
```

## Express Mock Server

### Custom Implementation
```javascript
const express = require('express');
const cors = require('cors');

const app = express();

app.use(cors());
app.use(express.json());

// Middleware for random delays
app.use((req, res, next) => {
  const delay = Math.random() * 1000; // 0-1 second
  setTimeout(next, delay);
});

// Middleware for authentication
app.use('/api/*', (req, res, next) => {
  const token = req.headers.authorization;

  if (!token || !token.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  next();
});

// In-memory database
let users = [
  { id: '1', name: 'John Doe', email: 'john@example.com' },
  { id: '2', name: 'Jane Smith', email: 'jane@example.com' }
];

// GET all users
app.get('/api/users', (req, res) => {
  const { page = 1, limit = 10 } = req.query;

  const start = (page - 1) * limit;
  const end = start + parseInt(limit);
  const paginatedUsers = users.slice(start, end);

  res.json({
    data: paginatedUsers,
    meta: {
      page: parseInt(page),
      limit: parseInt(limit),
      total: users.length,
      totalPages: Math.ceil(users.length / limit)
    }
  });
});

// GET user by ID
app.get('/api/users/:id', (req, res) => {
  const user = users.find(u => u.id === req.params.id);

  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }

  res.json(user);
});

// POST create user
app.post('/api/users', (req, res) => {
  const { name, email } = req.body;

  // Validation
  if (!name || !email) {
    return res.status(400).json({
      error: 'Validation failed',
      details: {
        name: !name ? 'Name is required' : undefined,
        email: !email ? 'Email is required' : undefined
      }
    });
  }

  // Check duplicate email
  if (users.some(u => u.email === email)) {
    return res.status(409).json({ error: 'Email already exists' });
  }

  const newUser = {
    id: String(Date.now()),
    name,
    email,
    createdAt: new Date().toISOString()
  };

  users.push(newUser);
  res.status(201).json(newUser);
});

// PUT update user
app.put('/api/users/:id', (req, res) => {
  const index = users.findIndex(u => u.id === req.params.id);

  if (index === -1) {
    return res.status(404).json({ error: 'User not found' });
  }

  users[index] = {
    ...users[index],
    ...req.body,
    updatedAt: new Date().toISOString()
  };

  res.json(users[index]);
});

// PATCH partial update
app.patch('/api/users/:id', (req, res) => {
  const index = users.findIndex(u => u.id === req.params.id);

  if (index === -1) {
    return res.status(404).json({ error: 'User not found' });
  }

  users[index] = {
    ...users[index],
    ...req.body,
    updatedAt: new Date().toISOString()
  };

  res.json(users[index]);
});

// DELETE user
app.delete('/api/users/:id', (req, res) => {
  const index = users.findIndex(u => u.id === req.params.id);

  if (index === -1) {
    return res.status(404).json({ error: 'User not found' });
  }

  users.splice(index, 1);
  res.status(204).send();
});

// Error simulation endpoint
app.get('/api/simulate-error', (req, res) => {
  const errorType = req.query.type || 'random';

  if (errorType === 'timeout') {
    // Never respond (timeout)
    return;
  }

  if (errorType === 'random' && Math.random() > 0.5) {
    return res.status(500).json({ error: 'Internal server error' });
  }

  res.json({ status: 'ok' });
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Mock server running on http://localhost:${PORT}`);
});
```

## GraphQL Mock Server

### Using Apollo Server
```javascript
const { ApolloServer, gql } = require('apollo-server');
const { MockList } = require('@graphql-tools/mock');

// Schema
const typeDefs = gql`
  type User {
    id: ID!
    name: String!
    email: String!
    posts: [Post!]!
  }

  type Post {
    id: ID!
    title: String!
    content: String!
    author: User!
  }

  type Query {
    users: [User!]!
    user(id: ID!): User
    posts: [Post!]!
  }

  type Mutation {
    createUser(name: String!, email: String!): User!
    createPost(title: String!, content: String!, authorId: ID!): Post!
  }
`;

// Mocks
const mocks = {
  User: () => ({
    id: () => Math.random().toString(36).substring(7),
    name: () => 'John Doe',
    email: () => 'john@example.com',
    posts: () => new MockList([2, 6])
  }),
  Post: () => ({
    id: () => Math.random().toString(36).substring(7),
    title: () => 'Sample Post',
    content: () => 'This is mock content'
  }),
  Query: () => ({
    users: () => new MockList([10, 20]),
    posts: () => new MockList([20, 40])
  })
};

const server = new ApolloServer({
  typeDefs,
  mocks,
  mockEntireSchema: false
});

server.listen().then(({ url }) => {
  console.log(`GraphQL mock server ready at ${url}`);
});
```

### Custom Resolvers
```javascript
const resolvers = {
  Query: {
    users: () => [
      { id: '1', name: 'John Doe', email: 'john@example.com' },
      { id: '2', name: 'Jane Smith', email: 'jane@example.com' }
    ],
    user: (_, { id }) => {
      const users = [
        { id: '1', name: 'John Doe', email: 'john@example.com' },
        { id: '2', name: 'Jane Smith', email: 'jane@example.com' }
      ];
      return users.find(u => u.id === id);
    }
  },
  Mutation: {
    createUser: (_, { name, email }) => ({
      id: Math.random().toString(36).substring(7),
      name,
      email
    })
  }
};

const server = new ApolloServer({
  typeDefs,
  resolvers
});
```

## WireMock (Java-based)

### Docker Setup
```bash
# Run WireMock in Docker
docker run -d \
  --name wiremock \
  -p 8080:8080 \
  -v $(pwd)/wiremock:/home/wiremock \
  wiremock/wiremock:latest

# Create mapping
mkdir -p wiremock/mappings
cat > wiremock/mappings/users.json << EOF
{
  "request": {
    "method": "GET",
    "url": "/api/users"
  },
  "response": {
    "status": 200,
    "headers": {
      "Content-Type": "application/json"
    },
    "jsonBody": [
      { "id": "1", "name": "John Doe", "email": "john@example.com" }
    ]
  }
}
EOF
```

## Mock Data Generation

### Using Faker.js
```javascript
const { faker } = require('@faker-js/faker');

// Generate mock user
function generateUser() {
  return {
    id: faker.string.uuid(),
    name: faker.person.fullName(),
    email: faker.internet.email(),
    avatar: faker.image.avatar(),
    address: {
      street: faker.location.streetAddress(),
      city: faker.location.city(),
      country: faker.location.country()
    },
    createdAt: faker.date.past().toISOString()
  };
}

// Generate multiple users
function generateUsers(count = 10) {
  return Array.from({ length: count }, generateUser);
}

// Generate posts
function generatePost() {
  return {
    id: faker.string.uuid(),
    title: faker.lorem.sentence(),
    content: faker.lorem.paragraphs(3),
    author: generateUser(),
    createdAt: faker.date.past().toISOString()
  };
}
```

## Advanced Scenarios

### Conditional Responses
```javascript
// Return different responses based on headers
http.get('/api/users', ({ request }) => {
  const acceptLanguage = request.headers.get('Accept-Language');

  if (acceptLanguage?.includes('es')) {
    return HttpResponse.json({
      mensaje: 'Hola Mundo'
    });
  }

  return HttpResponse.json({
    message: 'Hello World'
  });
});

// Based on query parameters
http.get('/api/users', ({ request }) => {
  const url = new URL(request.url);
  const format = url.searchParams.get('format');

  if (format === 'xml') {
    return new HttpResponse(
      '<users><user>John</user></users>',
      { headers: { 'Content-Type': 'application/xml' } }
    );
  }

  return HttpResponse.json([{ name: 'John' }]);
});
```

### Stateful Mocking
```javascript
let requestCount = 0;

http.get('/api/rate-limit', () => {
  requestCount++;

  if (requestCount > 10) {
    return HttpResponse.json(
      { error: 'Rate limit exceeded' },
      { status: 429 }
    );
  }

  return HttpResponse.json({ count: requestCount });
});
```

### Network Error Simulation
```javascript
http.get('/api/network-error', () => {
  return HttpResponse.error();
});

// Timeout simulation
http.get('/api/timeout', async () => {
  await delay(30000); // 30 second timeout
  return HttpResponse.json({});
});
```

## Best Practices

### Mock Server Design
- Mirror production API structure
- Use realistic data
- Implement proper error responses
- Support pagination
- Include rate limiting simulation

### Data Management
- Use data generators for realistic mock data
- Maintain consistent data across requests
- Reset state between test runs
- Support CRUD operations
- Implement proper relationships

### Response Scenarios
- Success responses (200, 201, 204)
- Client errors (400, 401, 403, 404, 409)
- Server errors (500, 502, 503)
- Network errors
- Timeouts

### Development Workflow
- Start mock server before frontend development
- Use environment variables for API URLs
- Switch between mock and real API easily
- Document available endpoints
- Keep mock data synchronized with API

### Testing
- Use mocks for isolated unit tests
- Test error handling
- Verify request validation
- Test authentication flows
- Simulate edge cases

## Tools Comparison

| Tool | Best For | Complexity | Features |
|------|----------|------------|----------|
| JSON Server | Quick prototypes | Low | Auto-CRUD, simple setup |
| MSW | Browser/Node testing | Medium | Request interception, powerful |
| Prism | OpenAPI specs | Low | Spec-based, validation |
| WireMock | Enterprise, Java | High | Recording, matching |
| Custom Express | Full control | Medium | Complete customization |

## Notes

- Use mock servers during frontend development
- Keep mock responses synchronized with API contracts
- Test both success and failure scenarios
- Implement realistic delays for better testing
- Use environment variables to switch between mock/real APIs
- Document mock endpoints and behaviors
- Reset mock state between tests
- Use data generators for realistic data
- Implement proper CORS for browser testing
- Version mock data alongside API versions
