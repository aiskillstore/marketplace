# API Design Best Practices Checklist

Comprehensive guide for designing robust, scalable, and developer-friendly APIs (REST, GraphQL, and general principles).

## General API Design Principles

### Core Principles
- [ ] Consistency across all endpoints
- [ ] Intuitive and predictable
- [ ] Well-documented
- [ ] Versioned properly
- [ ] Backward compatible when possible
- [ ] Follows industry standards
- [ ] Security first
- [ ] Performance optimized

### API-First Design
- [ ] Design API before implementation
- [ ] OpenAPI/Swagger specification
- [ ] Involve stakeholders early
- [ ] Mock API for frontend development
- [ ] Design for consumers, not producers

---

## RESTful API Best Practices

### Resource Naming
- [ ] Use nouns, not verbs (`/users`, not `/getUsers`)
- [ ] Plural for collections (`/users`)
- [ ] Singular for single resource (`/users/123`)
- [ ] Lowercase with hyphens (`/user-profiles`, not `/userProfiles` or `/user_profiles`)
- [ ] Keep URLs simple and predictable
- [ ] Use resource nesting sparingly (max 2 levels)
- [ ] Avoid deep nesting (`/users/123/posts/456/comments`, not `/users/123/posts/456/comments/789/likes`)

**Good Examples**:
```
GET    /users              # List users
GET    /users/123          # Get user by ID
POST   /users              # Create user
PUT    /users/123          # Update user (full replace)
PATCH  /users/123          # Update user (partial)
DELETE /users/123          # Delete user
GET    /users/123/posts    # Get user's posts (nested resource)
```

### HTTP Methods
- [ ] Use correct HTTP verbs
  - `GET` - Retrieve resource(s) (safe, idempotent)
  - `POST` - Create resource
  - `PUT` - Update/replace resource (idempotent)
  - `PATCH` - Partial update
  - `DELETE` - Remove resource (idempotent)
  - `HEAD` - Like GET but no body
  - `OPTIONS` - Get allowed methods
- [ ] GET requests have no body
- [ ] POST/PUT/PATCH accept request body
- [ ] Idempotent operations: GET, PUT, DELETE, HEAD

### HTTP Status Codes
Use appropriate status codes:

**Success (2xx)**
- [ ] `200 OK` - Successful GET, PUT, PATCH, or DELETE
- [ ] `201 Created` - Successful POST (include Location header)
- [ ] `202 Accepted` - Async processing started
- [ ] `204 No Content` - Successful DELETE with no response body
- [ ] `206 Partial Content` - Partial GET (range requests)

**Redirection (3xx)**
- [ ] `301 Moved Permanently` - Resource permanently moved
- [ ] `302 Found` - Temporary redirect
- [ ] `304 Not Modified` - Cached version is still valid

**Client Errors (4xx)**
- [ ] `400 Bad Request` - Invalid request format
- [ ] `401 Unauthorized` - Authentication required
- [ ] `403 Forbidden` - Authenticated but not authorized
- [ ] `404 Not Found` - Resource doesn't exist
- [ ] `405 Method Not Allowed` - HTTP method not supported
- [ ] `409 Conflict` - Resource conflict (duplicate, version mismatch)
- [ ] `422 Unprocessable Entity` - Validation errors
- [ ] `429 Too Many Requests` - Rate limit exceeded

**Server Errors (5xx)**
- [ ] `500 Internal Server Error` - Generic server error
- [ ] `502 Bad Gateway` - Invalid upstream response
- [ ] `503 Service Unavailable` - Temporary unavailability
- [ ] `504 Gateway Timeout` - Upstream timeout

### Request/Response Format

#### Request
- [ ] Accept JSON by default
- [ ] Support Content-Type negotiation
- [ ] Validate all inputs
- [ ] Use query parameters for filtering, sorting, pagination
- [ ] Use request body for resource data

**Query Parameters**:
```
GET /users?page=2&limit=20&sort=-createdAt&filter=active
```

#### Response
- [ ] Consistent response structure
- [ ] Include metadata when helpful
- [ ] Timestamps in ISO 8601 format
- [ ] Use JSON by default
- [ ] Pretty print in development
- [ ] Envelope pattern for metadata

**Standard Response Format**:
```json
{
  "data": {
    "id": "123",
    "name": "John Doe",
    "email": "john@example.com"
  },
  "meta": {
    "timestamp": "2025-01-15T10:30:00Z",
    "version": "1.0"
  }
}
```

**List Response with Pagination**:
```json
{
  "data": [
    { "id": "1", "name": "User 1" },
    { "id": "2", "name": "User 2" }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "totalPages": 5
  },
  "links": {
    "self": "/users?page=1",
    "next": "/users?page=2",
    "last": "/users?page=5"
  }
}
```

### Pagination
- [ ] Implement pagination for lists
- [ ] Support page-based or cursor-based pagination
- [ ] Return pagination metadata
- [ ] Include links to next/previous pages
- [ ] Default limit (e.g., 20)
- [ ] Max limit to prevent abuse (e.g., 100)

**Page-Based**:
```
GET /users?page=2&limit=20
```

**Cursor-Based** (better for real-time data):
```
GET /users?cursor=abc123&limit=20
```

### Filtering, Sorting, Searching
- [ ] Support filtering via query parameters
- [ ] Support sorting (use `-` for descending)
- [ ] Full-text search when needed
- [ ] Field selection (sparse fieldsets)

```
GET /users?filter[status]=active&sort=-createdAt&fields=id,name,email
```

### Error Handling
- [ ] Consistent error format
- [ ] Include error code/type
- [ ] Provide helpful error messages
- [ ] Include field-level errors for validation
- [ ] Don't expose stack traces in production
- [ ] Log errors server-side

**Error Response Format**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": [
      {
        "field": "email",
        "message": "Email is required"
      },
      {
        "field": "age",
        "message": "Age must be at least 18"
      }
    ]
  }
}
```

---

## Versioning

### Version Strategy
- [ ] Version your API from the start
- [ ] Choose versioning approach:
  - **URL versioning**: `/v1/users` (most common, explicit)
  - **Header versioning**: `Accept: application/vnd.api+json;version=1`
  - **Query parameter**: `/users?version=1` (not recommended)
- [ ] Use semantic versioning
- [ ] Maintain backward compatibility within major version
- [ ] Deprecation policy (e.g., 6 months notice)
- [ ] Document breaking changes

**Recommended**:
```
GET /v1/users
GET /v2/users
```

### Deprecation
- [ ] Announce deprecation in advance
- [ ] Use HTTP headers: `Sunset`, `Deprecation`
- [ ] Provide migration guide
- [ ] Redirect to new version when possible

```http
Deprecation: Sun, 01 Jan 2026 00:00:00 GMT
Sunset: Sun, 01 Jul 2026 00:00:00 GMT
Link: <https://api.example.com/docs/migration/v1-to-v2>; rel="sunset"
```

---

## Security

### Authentication & Authorization
- [ ] Require authentication for sensitive endpoints
- [ ] Use OAuth 2.0 or JWT for tokens
- [ ] HTTPS everywhere (no HTTP)
- [ ] Tokens in Authorization header, not URL
- [ ] Refresh token mechanism
- [ ] Token expiration
- [ ] Rate limiting per user/API key

```http
Authorization: Bearer <token>
```

### Input Validation
- [ ] Validate all inputs
- [ ] Whitelist validation
- [ ] Sanitize inputs
- [ ] Parameterized queries (no SQL injection)
- [ ] Limit request size
- [ ] Content-Type validation

### Security Headers
- [ ] CORS properly configured
- [ ] `X-Content-Type-Options: nosniff`
- [ ] `X-Frame-Options: DENY`
- [ ] `Content-Security-Policy`
- [ ] `Strict-Transport-Security` (HSTS)
- [ ] Rate limiting headers

### API Keys
- [ ] Use API keys for public APIs
- [ ] Rotate keys periodically
- [ ] Key revocation capability
- [ ] Different keys for dev/prod
- [ ] Monitor key usage

---

## Performance

### Caching
- [ ] Use HTTP caching headers
  - `Cache-Control`
  - `ETag`
  - `Last-Modified`
- [ ] Cache-Control directives: `public`, `private`, `max-age`, `no-cache`
- [ ] ETags for conditional requests
- [ ] Vary header for content negotiation

```http
Cache-Control: public, max-age=3600
ETag: "abc123"
```

**Conditional Request**:
```http
If-None-Match: "abc123"
→ 304 Not Modified (if unchanged)
```

### Optimization
- [ ] Compress responses (gzip, brotli)
- [ ] Paginate large responses
- [ ] Field selection to reduce payload
- [ ] Batch endpoints for multiple operations
- [ ] Async processing for long operations (return 202 Accepted)
- [ ] Connection pooling
- [ ] Database query optimization

### Rate Limiting
- [ ] Implement rate limiting
- [ ] Return rate limit headers
- [ ] Return 429 when exceeded
- [ ] Different limits for different tiers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1484311243
```

---

## GraphQL Best Practices

### Schema Design
- [ ] Clear type names
- [ ] Descriptive field names
- [ ] Use enums for fixed values
- [ ] Input types for mutations
- [ ] Nullable vs non-nullable fields
- [ ] Pagination with connections
- [ ] Avoid overly nested queries

**Schema Example**:
```graphql
type User {
  id: ID!
  name: String!
  email: String!
  posts(first: Int, after: String): PostConnection
}

type PostConnection {
  edges: [PostEdge]
  pageInfo: PageInfo!
}

type PostEdge {
  node: Post
  cursor: String!
}
```

### Queries & Mutations
- [ ] Keep queries focused
- [ ] Use fragments for reuse
- [ ] Input validation in resolvers
- [ ] Error handling per field
- [ ] Return meaningful errors
- [ ] Mutations return updated object

**Query Depth Limiting**:
- [ ] Limit query depth (prevent nested attacks)
- [ ] Limit query complexity
- [ ] Timeout long queries

### Performance
- [ ] DataLoader for batching (N+1 prevention)
- [ ] Query cost analysis
- [ ] Persisted queries
- [ ] Caching strategies
- [ ] Field-level caching

### Error Handling
- [ ] Use `errors` array in response
- [ ] Include error codes
- [ ] Path to error location
- [ ] Extensions for metadata

```json
{
  "data": { "user": null },
  "errors": [
    {
      "message": "User not found",
      "path": ["user"],
      "extensions": {
        "code": "NOT_FOUND",
        "userId": "123"
      }
    }
  ]
}
```

---

## Documentation

### API Documentation
- [ ] OpenAPI/Swagger specification
- [ ] Interactive documentation (Swagger UI, Redoc)
- [ ] Code examples for common use cases
- [ ] Authentication instructions
- [ ] Rate limiting details
- [ ] Error codes documented
- [ ] Changelog for versions
- [ ] Migration guides

### Examples
- [ ] Request examples with curl
- [ ] Response examples
- [ ] Error examples
- [ ] Multiple language SDKs when possible
- [ ] Postman collection

**Example Documentation**:
```markdown
## Create User

`POST /v1/users`

### Request

```bash
curl -X POST https://api.example.com/v1/users \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com"
  }'
```

### Response (201 Created)

```json
{
  "data": {
    "id": "123",
    "name": "John Doe",
    "email": "john@example.com",
    "createdAt": "2025-01-15T10:30:00Z"
  }
}
```
```

---

## Testing

### API Testing
- [ ] Unit tests for business logic
- [ ] Integration tests for endpoints
- [ ] Contract testing
- [ ] Load testing
- [ ] Security testing (OWASP)
- [ ] Test error cases
- [ ] Test edge cases

### Contract Testing
- [ ] Consumer-driven contracts (Pact)
- [ ] Schema validation
- [ ] Breaking change detection
- [ ] Version compatibility tests

---

## Monitoring & Logging

### Metrics
- [ ] Request count
- [ ] Response times (p50, p95, p99)
- [ ] Error rates
- [ ] Rate limit hits
- [ ] Active connections
- [ ] Endpoint usage

### Logging
- [ ] Request logging (with request ID)
- [ ] Error logging with context
- [ ] Audit logging for sensitive operations
- [ ] Don't log sensitive data (passwords, tokens)
- [ ] Structured logging (JSON)
- [ ] Correlation IDs for request tracing

### Health Checks
- [ ] Health endpoint (`/health`, `/ping`)
- [ ] Dependency health checks
- [ ] Version endpoint
- [ ] Metrics endpoint (`/metrics`)

```json
GET /health
{
  "status": "healthy",
  "version": "1.2.3",
  "dependencies": {
    "database": "healthy",
    "redis": "healthy",
    "external-api": "degraded"
  }
}
```

---

## API Governance

### Standards
- [ ] API style guide
- [ ] Naming conventions
- [ ] Error code registry
- [ ] Code review checklist
- [ ] Breaking change policy
- [ ] Deprecation process

### Review Process
- [ ] Design review before implementation
- [ ] Peer review of API changes
- [ ] Breaking change approval
- [ ] Documentation review
- [ ] Security review

---

## Common Pitfalls to Avoid

### Don't Do This
- ❌ Verbs in URLs (`/getUser`, `/createPost`)
- ❌ Inconsistent naming (some plural, some singular)
- ❌ Expose internal implementation details
- ❌ Use HTTP 200 for all responses
- ❌ Return HTML in error responses
- ❌ Break backward compatibility without versioning
- ❌ No pagination on lists
- ❌ Expose sensitive data in responses
- ❌ Use GET for state-changing operations
- ❌ No rate limiting
- ❌ Poor error messages ("An error occurred")
- ❌ No API documentation
- ❌ Magic status codes
- ❌ Lack of idempotency
- ❌ Overly nested resources

---

## Quick Checklist

Before releasing an API endpoint:

1. [ ] **Correct HTTP method** - GET, POST, PUT, PATCH, DELETE
2. [ ] **Correct status codes** - 200, 201, 400, 404, 500, etc.
3. [ ] **Validated inputs** - All parameters validated
4. [ ] **Error handling** - Consistent error format
5. [ ] **Authenticated** - Protected if needed
6. [ ] **Authorized** - Permission checks
7. [ ] **Paginated** - Lists are paginated
8. [ ] **Cached** - Cache headers set
9. [ ] **Documented** - Added to API docs
10. [ ] **Tested** - Unit and integration tests
11. [ ] **Versioned** - Part of API version
12. [ ] **Monitored** - Logging and metrics

---

## Tools

### Design & Documentation
- Swagger/OpenAPI
- Postman
- Insomnia
- Stoplight

### Testing
- Postman/Newman
- Pact (contract testing)
- k6 (load testing)
- OWASP ZAP (security)

### Monitoring
- Datadog
- New Relic
- Grafana
- ELK Stack

---

**Last Updated**: 2025-01-15
**Version**: 1.0.0
