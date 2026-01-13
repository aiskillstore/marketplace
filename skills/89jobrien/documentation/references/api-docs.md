---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: documentation
---

# API Documentation

Comprehensive guide for creating API documentation, OpenAPI specifications, SDKs, and developer guides.

## OpenAPI Specification

### Structure

**Required Sections:**

- `openapi`: Version (3.0.0)
- `info`: API metadata
- `paths`: API endpoints
- `components`: Reusable schemas and parameters

**Optional Sections:**

- `servers`: Server definitions
- `security`: Security schemes
- `tags`: Endpoint grouping
- `externalDocs`: External documentation links

### Complete Example

```yaml
openapi: 3.0.0
info:
  title: User Management API
  version: 1.0.0
  description: RESTful API for user management
  contact:
    name: API Support
    email: support@example.com
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  - url: https://api.example.com/v1
    description: Production server
  - url: https://staging-api.example.com/v1
    description: Staging server

paths:
  /users:
    get:
      summary: List all users
      description: Retrieve a paginated list of users
      tags:
        - Users
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
            maximum: 100
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  pagination:
                    $ref: '#/components/schemas/Pagination'
        '400':
          description: Bad request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

    post:
      summary: Create a new user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
            examples:
              example1:
                value:
                  email: user@example.com
                  name: John Doe
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          description: Invalid request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
        email:
          type: string
          format: email
        name:
          type: string
        createdAt:
          type: string
          format: date-time
      required:
        - id
        - email
        - name

    CreateUserRequest:
      type: object
      properties:
        email:
          type: string
          format: email
        name:
          type: string
          minLength: 1
          maxLength: 100
      required:
        - email
        - name

    Error:
      type: object
      properties:
        error:
          type: object
          properties:
            code:
              type: string
            message:
              type: string
            details:
              type: array
              items:
                type: string

    Pagination:
      type: object
      properties:
        page:
          type: integer
        limit:
          type: integer
        total:
          type: integer
        totalPages:
          type: integer

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

## SDK Generation

### Using OpenAPI Generator

**JavaScript/TypeScript:**

```bash
npx @openapitools/openapi-generator-cli generate \
  -i api.yaml \
  -g typescript-axios \
  -o ./sdk/typescript
```

**Python:**

```bash
npx @openapitools/openapi-generator-cli generate \
  -i api.yaml \
  -g python \
  -o ./sdk/python
```

**Java:**

```bash
npx @openapitools/openapi-generator-cli generate \
  -i api.yaml \
  -g java \
  -o ./sdk/java
```

### SDK Structure

**TypeScript SDK Example:**

```typescript
import { Configuration, UsersApi } from './sdk';

const config = new Configuration({
  basePath: 'https://api.example.com/v1',
  accessToken: 'your-token',
});

const api = new UsersApi(config);

// Create user
const user = await api.createUser({
  email: 'user@example.com',
  name: 'John Doe',
});

// List users
const users = await api.listUsers({ page: 1, limit: 20 });
```

## Code Examples

### JavaScript/Node.js

```javascript
const axios = require('axios');

const client = axios.create({
  baseURL: 'https://api.example.com/v1',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  }
});

// Create user
const user = await client.post('/users', {
  email: 'user@example.com',
  name: 'John Doe'
});

// Get user
const userData = await client.get(`/users/${user.data.id}`);
```

### Python

```python
import requests

headers = {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
}

# Create user
response = requests.post(
    'https://api.example.com/v1/users',
    json={'email': 'user@example.com', 'name': 'John Doe'},
    headers=headers
)

# Get user
user = requests.get(
    f'https://api.example.com/v1/users/{response.json()["id"]}',
    headers=headers
)
```

### cURL

```bash
# Create user
curl -X POST https://api.example.com/v1/users \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","name":"John Doe"}'

# Get user
curl https://api.example.com/v1/users/USER_ID \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Versioning

### API Versioning Strategies

**URL Versioning:**

```
/api/v1/users
/api/v2/users
```

**Header Versioning:**

```
Accept: application/vnd.example.v1+json
```

**Query Parameter:**

```
/api/users?version=1
```

### Migration Guides

**Structure:**

- Overview of changes
- Breaking changes list
- Migration steps
- Code examples (before/after)
- Deprecation timeline

## Interactive Documentation

### Swagger UI

**Setup:**

```javascript
const swaggerUi = require('swagger-ui-express');
const swaggerDocument = require('./api.yaml');

app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument));
```

### Postman Collections

**Export from OpenAPI:**

```bash
npx openapi-to-postman -s api.yaml -o postman-collection.json
```

## Best Practices

### Documentation Standards

1. **Complete Examples**: Every endpoint should have request/response examples
2. **Error Documentation**: Document all possible error responses
3. **Authentication**: Clear authentication instructions
4. **Rate Limiting**: Document rate limits and quotas
5. **Pagination**: Explain pagination parameters

### Developer Experience

- **Quick Start**: 5-minute getting started guide
- **Try It Out**: Interactive API explorer
- **SDKs**: Provide SDKs for common languages
- **Changelog**: Document API changes
- **Support**: Provide support channels
