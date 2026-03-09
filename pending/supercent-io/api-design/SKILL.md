---
name: api-design
description: Design RESTful and GraphQL APIs following best practices. Use when creating new APIs, refactoring existing endpoints, or documenting API specifications. Handles OpenAPI, REST, GraphQL, versioning.
license: Apache-2.0
compatibility: ""
metadata:
  version: 1.0.0
  author: Agent Skills Team
  tags: api-design, REST, GraphQL, OpenAPI, versioning, backend
  platforms: Claude, ChatGPT, Gemini
---


# API Design

## When to use this skill
- Designing new REST APIs
- Creating GraphQL schemas
- Refactoring API endpoints
- Documenting API specifications
- API versioning strategies
- Defining data models and relationships

## Instructions

### Step 1: Define API requirements
- Identify resources and entities
- Define relationships between entities
- Specify operations (CRUD, custom actions)
- Plan authentication/authorization
- Consider pagination, filtering, sorting

### Step 2: Design REST API

**Resource naming**:
- Use nouns, not verbs: `/users` not `/getUsers`
- Use plural names: `/users/{id}`
- Nest resources logically: `/users/{id}/posts`
- Keep URLs short and intuitive

**HTTP methods**:
- `GET`: Retrieve resources (idempotent)
- `POST`: Create new resources
- `PUT`: Replace entire resource
- `PATCH`: Partial update
- `DELETE`: Remove resources (idempotent)

**Response codes**:
- `200 OK`: Success with response body
- `201 Created`: Resource created successfully
- `204 No Content`: Success with no response body
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: No permission
- `404 Not Found`: Resource doesn't exist
- `409 Conflict`: Resource conflict
- `422 Unprocessable Entity`: Validation failed
- `500 Internal Server Error`: Server error

**Example REST endpoint**:
```
GET    /api/v1/users           # List users
GET    /api/v1/users/{id}      # Get user
POST   /api/v1/users           # Create user
PUT    /api/v1/users/{id}      # Update user
PATCH  /api/v1/users/{id}      # Partial update
DELETE /api/v1/users/{id}      # Delete user
```

### Step 3: Request/Response format

**Request example**:
```json
POST /api/v1/users
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "role": "admin"
}
```

**Response example**:
```json
HTTP/1.1 201 Created
Content-Type: application/json
Location: /api/v1/users/123

{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "admin",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Step 4: Error handling

**Error response format**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input provided",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

### Step 5: Pagination

**Query parameters**:
```
GET /api/v1/users?page=2&limit=20&sort=-created_at&filter=role:admin
```

**Response with pagination**:
```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 100,
    "pages": 5
  },
  "links": {
    "self": "/api/v1/users?page=2&limit=20",
    "first": "/api/v1/users?page=1&limit=20",
    "prev": "/api/v1/users?page=1&limit=20",
    "next": "/api/v1/users?page=3&limit=20",
    "last": "/api/v1/users?page=5&limit=20"
  }
}
```

### Step 6: Authentication

**Options**:
- JWT (JSON Web Tokens)
- OAuth 2.0
- API Keys
- Session-based

**Example with JWT**:
```
GET /api/v1/users
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Step 7: Versioning

**URL versioning** (recommended):
```
/api/v1/users
/api/v2/users
```

**Header versioning**:
```
GET /api/users
Accept: application/vnd.api+json; version=1
```

### Step 8: Documentation

Create OpenAPI 3.0 specification:

```yaml
openapi: 3.0.0
info:
  title: User Management API
  version: 1.0.0
  description: API for managing users
servers:
  - url: https://api.example.com/v1
paths:
  /users:
    get:
      summary: List users
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
    post:
      summary: Create user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserCreate'
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        email:
          type: string
          format: email
        created_at:
          type: string
          format: date-time
    UserCreate:
      type: object
      required:
        - name
        - email
      properties:
        name:
          type: string
        email:
          type: string
          format: email
```

## Best practices

1. **Consistency**: Use consistent naming, structure, and patterns
2. **Versioning**: Always version your APIs from the start
3. **Security**: Implement authentication and authorization
4. **Validation**: Validate all inputs on the server side
5. **Rate limiting**: Protect against abuse
6. **Caching**: Use ETags and Cache-Control headers
7. **CORS**: Configure properly for web clients
8. **Documentation**: Keep docs up-to-date with code
9. **Testing**: Test all endpoints thoroughly
10. **Monitoring**: Log requests and track performance

## Common patterns

**Filtering**:
```
GET /api/v1/users?role=admin&status=active
```

**Sorting**:
```
GET /api/v1/users?sort=-created_at,name
```

**Field selection**:
```
GET /api/v1/users?fields=id,name,email
```

**Batch operations**:
```
POST /api/v1/users/batch
{
  "operations": [
    {"action": "create", "data": {...}},
    {"action": "update", "id": 123, "data": {...}}
  ]
}
```

## GraphQL alternative

If REST doesn't fit, consider GraphQL:

```graphql
type User {
  id: ID!
  name: String!
  email: String!
  posts: [Post!]!
  createdAt: DateTime!
}

type Query {
  users(page: Int, limit: Int): [User!]!
  user(id: ID!): User
}

type Mutation {
  createUser(input: CreateUserInput!): User!
  updateUser(id: ID!, input: UpdateUserInput!): User!
  deleteUser(id: ID!): Boolean!
}
```

## References

- [OpenAPI Specification](https://swagger.io/specification/)
- [REST API Tutorial](https://restfulapi.net/)
- [GraphQL Best Practices](https://graphql.org/learn/best-practices/)
- [HTTP Status Codes](https://httpstatuses.com/)

## Examples

### Example 1: Basic usage
<!-- Add example content here -->

### Example 2: Advanced usage
<!-- Add advanced example content here -->
