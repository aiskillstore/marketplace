---
name: api-design-framework
description: Use this skill when designing REST, GraphQL, or gRPC APIs. Provides comprehensive API design patterns, versioning strategies, error handling conventions, authentication approaches, and OpenAPI/AsyncAPI templates. Ensures consistent, well-documented, and developer-friendly APIs across all backend services.
version: 1.0.0
author: AI Agent Hub
tags: [api, rest, graphql, grpc, backend, documentation]
---

# API Design Framework

## Overview

This skill provides comprehensive guidance for designing robust, scalable, and developer-friendly APIs. Whether building REST, GraphQL, or gRPC services, this framework ensures consistency, usability, and maintainability.

**When to use this skill:**
- Designing new API endpoints or services
- Establishing API conventions for a team or organization
- Reviewing API designs for consistency and best practices
- Migrating or versioning existing APIs
- Creating API documentation (OpenAPI, AsyncAPI)
- Choosing between REST, GraphQL, or gRPC

## API Design Principles

### 1. Developer Experience First
APIs should be intuitive and self-documenting:
- Clear, consistent naming conventions
- Predictable behavior and responses
- Comprehensive documentation
- Helpful error messages

### 2. Consistency Over Cleverness
Follow established patterns rather than inventing new ones:
- Standard HTTP methods and status codes (REST)
- Conventional query structures (GraphQL)
- Idiomatic proto definitions (gRPC)

### 3. Evolution Without Breaking Changes
Design for change from day one:
- API versioning strategy
- Backward compatibility considerations
- Deprecation policies
- Migration paths

### 4. Performance by Design
Consider performance implications:
- Pagination for large datasets
- Filtering and partial responses
- Caching strategies
- Rate limiting

---

## REST API Design

### Resource Naming Conventions

**Use plural nouns for resources:**
```
✅ GET /users
✅ GET /users/123
✅ GET /users/123/orders

❌ GET /user
❌ GET /getUser
❌ GET /user/123
```

**Use hierarchical relationships:**
```
✅ GET /users/123/orders          # Orders for specific user
✅ GET /teams/5/members           # Members of specific team
✅ POST /projects/10/tasks        # Create task in project 10

❌ GET /userOrders/123            # Flat structure
❌ GET /orders?userId=123         # Query param for relationship
```

**Use kebab-case for multi-word resources:**
```
✅ /shopping-carts
✅ /order-items
✅ /user-preferences

❌ /shoppingCarts    (camelCase)
❌ /shopping_carts   (snake_case)
❌ /ShoppingCarts    (PascalCase)
```

### HTTP Methods (Verbs)

| Method | Purpose | Idempotent | Safe | Example |
|--------|---------|------------|------|---------|
| **GET** | Retrieve resource(s) | Yes | Yes | `GET /users/123` |
| **POST** | Create resource | No | No | `POST /users` |
| **PUT** | Replace entire resource | Yes | No | `PUT /users/123` |
| **PATCH** | Partial update | No* | No | `PATCH /users/123` |
| **DELETE** | Remove resource | Yes | No | `DELETE /users/123` |
| **HEAD** | Metadata only (no body) | Yes | Yes | `HEAD /users/123` |
| **OPTIONS** | Allowed methods | Yes | Yes | `OPTIONS /users` |

*PATCH can be designed to be idempotent

### Status Codes

#### Success (2xx)
- **200 OK**: Successful GET, PUT, PATCH, or DELETE
- **201 Created**: Successful POST (include `Location` header)
- **202 Accepted**: Request accepted, processing async
- **204 No Content**: Successful DELETE or PUT with no response body

#### Client Errors (4xx)
- **400 Bad Request**: Invalid request body or parameters
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Authenticated but not authorized
- **404 Not Found**: Resource doesn't exist
- **405 Method Not Allowed**: HTTP method not supported for resource
- **409 Conflict**: Resource conflict (e.g., duplicate)
- **422 Unprocessable Entity**: Validation failed
- **429 Too Many Requests**: Rate limit exceeded

#### Server Errors (5xx)
- **500 Internal Server Error**: Generic server error
- **502 Bad Gateway**: Upstream service error
- **503 Service Unavailable**: Temporary unavailability
- **504 Gateway Timeout**: Upstream timeout

### Request/Response Formats

**Request Body (POST/PUT/PATCH):**
```json
POST /users
Content-Type: application/json

{
  "email": "jane@example.com",
  "name": "Jane Smith",
  "role": "developer"
}
```

**Success Response:**
```json
HTTP/1.1 201 Created
Location: /users/123
Content-Type: application/json

{
  "id": 123,
  "email": "jane@example.com",
  "name": "Jane Smith",
  "role": "developer",
  "created_at": "2025-10-31T10:30:00Z",
  "updated_at": "2025-10-31T10:30:00Z"
}
```

**Error Response (Standard Format):**
```json
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json

{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "Email is already registered",
        "code": "DUPLICATE_EMAIL"
      },
      {
        "field": "name",
        "message": "Name must be at least 2 characters",
        "code": "NAME_TOO_SHORT"
      }
    ],
    "timestamp": "2025-10-31T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

### Pagination

**Cursor-Based Pagination (Recommended):**
```
GET /users?cursor=eyJpZCI6MTIzfQ&limit=20

Response:
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6MTQzfQ",
    "has_more": true
  }
}
```

**Pros**: Consistent results even as data changes
**Use for**: Large datasets, real-time data, infinite scroll

**Offset-Based Pagination:**
```
GET /users?page=2&per_page=20

Response:
{
  "data": [...],
  "pagination": {
    "page": 2,
    "per_page": 20,
    "total": 487,
    "total_pages": 25
  }
}
```

**Pros**: Easy to understand, supports "jump to page N"
**Use for**: Small datasets, admin panels, known bounds

### Filtering and Sorting

**Filtering:**
```
GET /users?status=active&role=developer&created_after=2025-01-01
GET /products?price_min=10&price_max=100&category=electronics
```

**Sorting:**
```
GET /users?sort=created_at:desc
GET /users?sort=-created_at              # Minus prefix for descending
GET /users?sort=name:asc,created_at:desc # Multiple fields
```

**Field Selection (Partial Response):**
```
GET /users?fields=id,name,email          # Only specified fields
GET /users/123?exclude=password_hash     # All except specified
```

### API Versioning

#### Strategy 1: URI Versioning (Recommended)
```
✅ /api/v1/users
✅ /api/v2/users

Pros: Clear, easy to test, cache-friendly
Cons: Verbose URLs
```

#### Strategy 2: Header Versioning
```
GET /api/users
Accept: application/vnd.company.v2+json

Pros: Clean URLs
Cons: Harder to test, not visible in URL
```

#### Strategy 3: Query Parameter
```
GET /api/users?version=2

Pros: Simple
Cons: Can be forgotten, mixes with business logic params
```

**Best Practice:** URI versioning for public APIs, header versioning for internal services

### Rate Limiting

**Response Headers:**
```
HTTP/1.1 200 OK
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1635724800

Response when exceeded:
HTTP/1.1 429 Too Many Requests
Retry-After: 3600

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "API rate limit exceeded",
    "retry_after": 3600
  }
}
```

### Authentication & Authorization

**Bearer Token (JWT):**
```
GET /users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**API Key:**
```
GET /users
X-API-Key: sk_live_abc123...
```

**Basic Auth (avoid for production):**
```
GET /users
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
```

---

## GraphQL API Design

### Schema Design Principles

**1. Nullable by Default**
```graphql
type User {
  id: ID!              # Non-null (required)
  email: String!       # Non-null
  name: String         # Nullable (optional)
  avatar: String       # Nullable
}
```

**2. Use Connections for Lists**
```graphql
type Query {
  users(first: Int, after: String): UserConnection!
}

type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type UserEdge {
  node: User!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
```

**3. Input Types for Mutations**
```graphql
input CreateUserInput {
  email: String!
  name: String!
  role: UserRole!
}

type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
}

type CreateUserPayload {
  user: User!
  errors: [UserError!]
}

type UserError {
  field: String!
  message: String!
  code: String!
}
```

### Query Design

**Fetch single resource:**
```graphql
query GetUser {
  user(id: "123") {
    id
    name
    email
    posts {
      id
      title
    }
  }
}
```

**Fetch list with filters:**
```graphql
query GetUsers {
  users(
    first: 10
    after: "cursor123"
    filter: { role: DEVELOPER, status: ACTIVE }
  ) {
    edges {
      node {
        id
        name
        email
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

### Error Handling

**Field-Level Errors:**
```graphql
type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
}

type CreateUserPayload {
  user: User
  errors: [UserError!]
}
```

**Response:**
```json
{
  "data": {
    "createUser": {
      "user": null,
      "errors": [
        {
          "field": "email",
          "message": "Email is already taken",
          "code": "DUPLICATE_EMAIL"
        }
      ]
    }
  }
}
```

---

## gRPC API Design

### Proto File Structure

**user.proto:**
```protobuf
syntax = "proto3";

package company.user.v1;

import "google/protobuf/timestamp.proto";
import "google/protobuf/empty.proto";

// User service definition
service UserService {
  // Get user by ID
  rpc GetUser(GetUserRequest) returns (GetUserResponse);

  // List users with pagination
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);

  // Create new user
  rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);

  // Update user
  rpc UpdateUser(UpdateUserRequest) returns (UpdateUserResponse);

  // Delete user
  rpc DeleteUser(DeleteUserRequest) returns (google.protobuf.Empty);

  // Stream updates (server streaming)
  rpc WatchUsers(WatchUsersRequest) returns (stream UserEvent);
}

// Messages
message User {
  string id = 1;
  string email = 2;
  string name = 3;
  UserRole role = 4;
  google.protobuf.Timestamp created_at = 5;
  google.protobuf.Timestamp updated_at = 6;
}

enum UserRole {
  USER_ROLE_UNSPECIFIED = 0;
  USER_ROLE_ADMIN = 1;
  USER_ROLE_DEVELOPER = 2;
  USER_ROLE_VIEWER = 3;
}

message GetUserRequest {
  string id = 1;
}

message GetUserResponse {
  User user = 1;
}

message ListUsersRequest {
  int32 page_size = 1;
  string page_token = 2;
  string filter = 3;  // e.g., "role=DEVELOPER AND status=ACTIVE"
}

message ListUsersResponse {
  repeated User users = 1;
  string next_page_token = 2;
  int32 total_size = 3;
}

message CreateUserRequest {
  string email = 1;
  string name = 2;
  UserRole role = 3;
}

message CreateUserResponse {
  User user = 1;
}
```

### Error Handling

**Use gRPC status codes:**
```go
// OK: Success
// CANCELLED: Client cancelled
// INVALID_ARGUMENT: Invalid request (400 equivalent)
// NOT_FOUND: Resource not found (404 equivalent)
// ALREADY_EXISTS: Duplicate (409 equivalent)
// PERMISSION_DENIED: Forbidden (403 equivalent)
// UNAUTHENTICATED: Auth required (401 equivalent)
// RESOURCE_EXHAUSTED: Rate limit (429 equivalent)
// INTERNAL: Server error (500 equivalent)
```

---

## API Documentation

### OpenAPI 3.1 Structure

See `/templates/openapi-template.yaml` for complete example.

**Key sections:**
- **info**: API metadata (title, version, description)
- **servers**: Base URLs for different environments
- **paths**: Endpoints with operations
- **components**: Reusable schemas, responses, parameters
- **security**: Authentication schemes

### AsyncAPI 3.0 (Event-Driven)

For documenting message-based APIs (Kafka, RabbitMQ, WebSockets).

See `/templates/asyncapi-template.yaml` for complete example.

---

## Best Practices

### 1. Use Standard Media Types
```
Content-Type: application/json          # JSON
Content-Type: application/xml           # XML
Content-Type: application/protobuf      # Protocol Buffers
Content-Type: application/octet-stream  # Binary data
```

### 2. HATEOAS (Optional for REST)
Include links for related resources:
```json
{
  "id": 123,
  "name": "Jane Smith",
  "_links": {
    "self": { "href": "/users/123" },
    "orders": { "href": "/users/123/orders" },
    "avatar": { "href": "/users/123/avatar" }
  }
}
```

### 3. Idempotency Keys
For preventing duplicate operations:
```
POST /payments
Idempotency-Key: unique-request-id-123
```

### 4. Bulk Operations
```
POST /users/bulk-create
POST /users/bulk-update
POST /users/bulk-delete
```

### 5. Webhooks
Document webhook payloads and retry logic:
```json
POST https://client.example.com/webhook
X-Webhook-Signature: sha256=abc123...

{
  "event": "user.created",
  "data": { ... },
  "timestamp": "2025-10-31T10:30:00Z"
}
```

---

## Common Pitfalls

❌ **Using verbs in URLs**
```
Bad:  POST /createUser
Good: POST /users
```

❌ **Inconsistent naming**
```
Bad:  /users, /userOrders, /user_preferences
Good: /users, /orders, /preferences
```

❌ **Ignoring HTTP methods**
```
Bad:  POST /users/123/delete
Good: DELETE /users/123
```

❌ **Exposing implementation details**
```
Bad:  /users-table, /get-user-from-db
Good: /users, /users/123
```

❌ **Generic error messages**
```
Bad:  { "error": "Something went wrong" }
Good: { "error": { "code": "DUPLICATE_EMAIL", "message": "Email already exists" }}
```

---

## Integration with Agents

### Backend System Architect
- Uses this framework when designing new APIs
- References patterns for consistency across services
- Creates OpenAPI specifications from templates

### Frontend UI Developer
- Reviews API contracts before implementation
- Provides feedback on developer experience
- Integrates with APIs following documented patterns

### Code Quality Reviewer
- Validates API designs against this framework
- Ensures OpenAPI docs are accurate and complete
- Checks for REST/GraphQL/gRPC best practices

---

**Skill Version**: 1.0.0
**Last Updated**: 2025-10-31
**Maintained by**: AI Agent Hub Team
