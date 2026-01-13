# Response Formats

Error responses, versioning, bulk operations, and HATEOAS patterns.

## Error Response Format

### Standard Structure

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {"field": "email", "message": "Invalid email format"},
      {"field": "age", "message": "Must be 18 or older"}
    ],
    "request_id": "abc-123",
    "documentation_url": "https://api.example.com/docs/errors#validation"
  }
}
```

### Minimal Error

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "User not found"
  }
}
```

### Validation Errors (422)

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "email",
        "code": "INVALID_FORMAT",
        "message": "Must be a valid email address"
      },
      {
        "field": "password",
        "code": "TOO_SHORT",
        "message": "Must be at least 8 characters"
      }
    ]
  }
}
```

### RFC 7807 Problem Details

```json
{
  "type": "https://api.example.com/errors/validation",
  "title": "Validation Error",
  "status": 422,
  "detail": "The request body contains invalid data",
  "instance": "/users/123",
  "errors": [
    {"pointer": "/email", "detail": "Invalid format"}
  ]
}
```

---

## Versioning Strategies

### URI Versioning (Most Common)

```http
GET /v1/users
GET /v2/users
```

**Pros:** Clear, easy to route, cacheable
**Cons:** URL pollution, hard to deprecate

### Header Versioning

```http
GET /users
Accept: application/vnd.api.v1+json
```

**Pros:** Clean URLs
**Cons:** Harder to test, less visible

### Query Parameter

```http
GET /users?version=1
GET /users?api-version=2024-01-15
```

**Pros:** Easy to implement
**Cons:** Less RESTful, affects caching

### Date-Based Versioning

```http
GET /users
API-Version: 2024-01-15
```

**Pros:** Fine-grained, Stripe-style
**Cons:** Complex to maintain

---

## Bulk Operations

### Batch Endpoint

```http
POST /batch
Content-Type: application/json

{
  "operations": [
    {"method": "POST", "path": "/users", "body": {"name": "Alice"}},
    {"method": "PATCH", "path": "/users/123", "body": {"status": "active"}},
    {"method": "DELETE", "path": "/users/456"}
  ]
}
```

**Response:**

```json
{
  "results": [
    {"status": 201, "body": {"id": 789, "name": "Alice"}},
    {"status": 200, "body": {"id": 123, "status": "active"}},
    {"status": 204, "body": null}
  ]
}
```

### Bulk Create

```http
POST /users/bulk
Content-Type: application/json

[
  {"name": "Alice", "email": "alice@example.com"},
  {"name": "Bob", "email": "bob@example.com"}
]
```

**Response:**

```json
{
  "created": 2,
  "items": [
    {"id": 123, "name": "Alice"},
    {"id": 124, "name": "Bob"}
  ]
}
```

### Bulk Create with Partial Failure

```json
{
  "created": 1,
  "failed": 1,
  "items": [
    {"id": 123, "name": "Alice", "status": "created"}
  ],
  "errors": [
    {"index": 1, "error": {"code": "DUPLICATE", "message": "Email exists"}}
  ]
}
```

### Bulk Delete

```http
DELETE /users/bulk
Content-Type: application/json

{"ids": [1, 2, 3, 4, 5]}
```

**Response:**

```json
{
  "deleted": 5
}
```

---

## HATEOAS Links

### Single Resource

```json
{
  "id": 123,
  "name": "Alice",
  "email": "alice@example.com",
  "_links": {
    "self": {"href": "/users/123"},
    "orders": {"href": "/users/123/orders"},
    "profile": {"href": "/users/123/profile"},
    "update": {"href": "/users/123", "method": "PATCH"},
    "delete": {"href": "/users/123", "method": "DELETE"}
  }
}
```

### Collection with Pagination

```json
{
  "data": [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
  ],
  "meta": {
    "total": 150,
    "page": 2,
    "per_page": 20,
    "total_pages": 8
  },
  "_links": {
    "self": {"href": "/users?page=2"},
    "first": {"href": "/users?page=1"},
    "prev": {"href": "/users?page=1"},
    "next": {"href": "/users?page=3"},
    "last": {"href": "/users?page=8"}
  }
}
```

### HAL Format

```json
{
  "_embedded": {
    "users": [
      {"id": 1, "name": "Alice", "_links": {"self": {"href": "/users/1"}}},
      {"id": 2, "name": "Bob", "_links": {"self": {"href": "/users/2"}}}
    ]
  },
  "_links": {
    "self": {"href": "/users?page=1"},
    "next": {"href": "/users?page=2"}
  },
  "page": 1,
  "total": 100
}
```

### JSON:API Format

```json
{
  "data": [
    {
      "type": "users",
      "id": "1",
      "attributes": {"name": "Alice"},
      "relationships": {
        "orders": {"links": {"related": "/users/1/orders"}}
      },
      "links": {"self": "/users/1"}
    }
  ],
  "links": {
    "self": "/users?page=1",
    "next": "/users?page=2"
  },
  "meta": {"total": 100}
}
```
