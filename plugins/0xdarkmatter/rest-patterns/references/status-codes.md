# HTTP Status Codes Reference

Complete reference for HTTP status codes in REST APIs.

## Success (2xx)

| Code | Name | When to Use |
|------|------|-------------|
| **200 OK** | Success | GET, PUT, PATCH, DELETE success with body |
| **201 Created** | Created | POST success (include `Location` header) |
| **202 Accepted** | Accepted | Request queued for async processing |
| **204 No Content** | No Content | Success with no response body |
| **206 Partial Content** | Partial | Range request fulfilled |

### Usage Examples

```http
# 200 OK - Successful GET
GET /users/123
→ 200 OK
→ {"id": 123, "name": "Alice"}

# 201 Created - Successful POST
POST /users
→ 201 Created
→ Location: /users/456
→ {"id": 456, "name": "Bob"}

# 202 Accepted - Async operation
POST /jobs
→ 202 Accepted
→ {"job_id": "abc123", "status": "pending"}

# 204 No Content - Successful DELETE
DELETE /users/123
→ 204 No Content
```

## Redirection (3xx)

| Code | Name | When to Use |
|------|------|-------------|
| **301 Moved Permanently** | Moved | Resource permanently relocated |
| **302 Found** | Found | Temporary redirect (avoid in APIs) |
| **304 Not Modified** | Not Modified | Client cache is valid (ETag match) |
| **307 Temporary Redirect** | Temp Redirect | Redirect preserving HTTP method |
| **308 Permanent Redirect** | Perm Redirect | Like 301, preserves method |

### 301 vs 308

- **301**: Browser may change POST to GET on redirect
- **308**: Guarantees method is preserved

### 304 Workflow

```http
# First request
GET /users/123
→ 200 OK
→ ETag: "abc123"

# Subsequent request with validation
GET /users/123
If-None-Match: "abc123"
→ 304 Not Modified (use cached version)
```

## Client Errors (4xx)

| Code | Name | When to Use |
|------|------|-------------|
| **400 Bad Request** | Bad Request | Invalid syntax, malformed JSON |
| **401 Unauthorized** | Unauthorized | Missing or invalid authentication |
| **403 Forbidden** | Forbidden | Authenticated but not authorized |
| **404 Not Found** | Not Found | Resource doesn't exist |
| **405 Method Not Allowed** | Not Allowed | HTTP method not supported |
| **406 Not Acceptable** | Not Acceptable | Can't produce requested content type |
| **409 Conflict** | Conflict | State conflict (duplicate, version mismatch) |
| **410 Gone** | Gone | Resource permanently removed |
| **412 Precondition Failed** | Precondition | If-Match header condition failed |
| **413 Payload Too Large** | Too Large | Request body exceeds limit |
| **415 Unsupported Media Type** | Bad Media | Content-Type not supported |
| **422 Unprocessable Entity** | Unprocessable | Valid syntax, invalid semantics |
| **429 Too Many Requests** | Rate Limited | Rate limit exceeded |

### 400 vs 422

- **400**: Malformed request (invalid JSON, wrong types)
- **422**: Valid request, but business logic rejects it

```http
# 400 - Syntax error
POST /users
{"name": "Alice", age: 30}  # Missing quotes around age
→ 400 Bad Request
→ {"error": "Invalid JSON"}

# 422 - Validation error
POST /users
{"name": "Alice", "age": -5}  # Age can't be negative
→ 422 Unprocessable Entity
→ {"error": {"field": "age", "message": "Must be positive"}}
```

### 401 vs 403

- **401**: "Who are you?" (not authenticated)
- **403**: "I know who you are, but no" (not authorized)

```http
# 401 - Missing token
GET /admin/users
→ 401 Unauthorized
→ {"error": "Authentication required"}

# 403 - Valid token, wrong permissions
GET /admin/users
Authorization: Bearer <user_token>
→ 403 Forbidden
→ {"error": "Admin access required"}
```

### 409 Conflict Examples

```http
# Duplicate resource
POST /users
{"email": "existing@example.com"}
→ 409 Conflict
→ {"error": "Email already exists"}

# Version mismatch (optimistic locking)
PATCH /users/123
If-Match: "old-version"
→ 409 Conflict
→ {"error": "Resource was modified"}
```

## Server Errors (5xx)

| Code | Name | When to Use |
|------|------|-------------|
| **500 Internal Server Error** | Server Error | Generic server failure |
| **501 Not Implemented** | Not Implemented | Feature not available |
| **502 Bad Gateway** | Bad Gateway | Upstream returned invalid response |
| **503 Service Unavailable** | Unavailable | Temporarily unavailable |
| **504 Gateway Timeout** | Timeout | Upstream timeout |

### 503 with Retry-After

```http
GET /api/resource
→ 503 Service Unavailable
→ Retry-After: 300
→ {"error": "Service temporarily unavailable", "retry_after": 300}
```

## Decision Tree

```
Is the request valid?
├─ No → Is it syntax? → 400 Bad Request
│       Is it validation? → 422 Unprocessable Entity
│
└─ Yes → Is auth provided?
         ├─ No → 401 Unauthorized
         └─ Yes → Is authorized?
                  ├─ No → 403 Forbidden
                  └─ Yes → Does resource exist?
                           ├─ No → 404 Not Found
                           └─ Yes → Success! 2xx
```
