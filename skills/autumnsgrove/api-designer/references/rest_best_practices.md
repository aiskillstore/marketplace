# REST API Best Practices

This document provides comprehensive best practices for designing, implementing, and maintaining RESTful APIs.

## Table of Contents

- [URL Design](#url-design)
- [HTTP Methods](#http-methods)
- [Status Codes](#status-codes)
- [Request/Response Formats](#requestresponse-formats)
- [Error Handling](#error-handling)
- [Authentication & Security](#authentication--security)
- [Versioning](#versioning)
- [Pagination](#pagination)
- [Filtering & Sorting](#filtering--sorting)
- [Rate Limiting](#rate-limiting)
- [Caching](#caching)
- [CORS](#cors)
- [Documentation](#documentation)

## URL Design

### Resource Naming

**Use Plural Nouns**:
```
✅ Good:
/users
/posts
/comments

❌ Bad:
/user
/post
/comment
```

**Use Hyphens for Multi-Word Resources**:
```
✅ Good:
/blog-posts
/user-profiles
/payment-methods

❌ Bad:
/blogPosts
/blog_posts
/userProfiles
```

**Keep URLs Lowercase**:
```
✅ Good:
/users/123/posts
/api/v1/products

❌ Bad:
/Users/123/Posts
/API/V1/Products
```

### Resource Hierarchy

**Limit Nesting Depth**:
```
✅ Good (2 levels):
/users/123/posts
/posts/456/comments

❌ Bad (too deep):
/users/123/posts/456/comments/789/likes
```

**Alternative to Deep Nesting**:
```
Instead of: /users/123/posts/456/comments
Use: /comments?postId=456&userId=123
```

### Query Parameters vs Path Parameters

**Path Parameters**: For resource identification
```
/users/{userId}
/posts/{postId}
```

**Query Parameters**: For filtering, sorting, pagination
```
/posts?published=true&author=123&sort=-createdAt&limit=10
```

## HTTP Methods

### GET - Retrieve Resources

**Characteristics**:
- Safe (no side effects)
- Idempotent (multiple identical requests produce same result)
- Cacheable
- No request body

**Examples**:
```http
# Get collection
GET /posts
Response: 200 OK

# Get specific resource
GET /posts/123
Response: 200 OK

# Get related resources
GET /users/456/posts
Response: 200 OK
```

### POST - Create Resources

**Characteristics**:
- Not safe (has side effects)
- Not idempotent
- Creates new resource
- Request body contains resource data

**Examples**:
```http
POST /posts
Content-Type: application/json

{
  "title": "My New Post",
  "content": "Post content here"
}

Response: 201 Created
Location: /posts/789
{
  "id": "789",
  "title": "My New Post",
  "content": "Post content here",
  "createdAt": "2025-10-25T10:30:00Z"
}
```

**Best Practices**:
- Return `201 Created` on success
- Include `Location` header with new resource URL
- Return created resource in response body
- Generate IDs server-side

### PUT - Replace Resource

**Characteristics**:
- Not safe
- Idempotent
- Replaces entire resource
- Request body contains complete resource

**Examples**:
```http
PUT /posts/123
Content-Type: application/json

{
  "title": "Updated Title",
  "content": "Updated content",
  "published": true,
  "tags": ["api", "rest"]
}

Response: 200 OK
{
  "id": "123",
  "title": "Updated Title",
  "content": "Updated content",
  "published": true,
  "tags": ["api", "rest"],
  "updatedAt": "2025-10-25T10:35:00Z"
}
```

**PUT vs POST**:
- PUT to `/posts/123` - Updates post with ID 123
- PUT to `/posts` - Usually not allowed (would replace entire collection)

### PATCH - Partial Update

**Characteristics**:
- Not safe
- Typically idempotent
- Updates specific fields only
- Request body contains only fields to update

**Examples**:
```http
PATCH /posts/123
Content-Type: application/json

{
  "published": true
}

Response: 200 OK
{
  "id": "123",
  "title": "Original Title",
  "content": "Original content",
  "published": true,  // Only this changed
  "updatedAt": "2025-10-25T10:40:00Z"
}
```

**JSON Patch Format** (RFC 6902):
```http
PATCH /posts/123
Content-Type: application/json-patch+json

[
  { "op": "replace", "path": "/title", "value": "New Title" },
  { "op": "add", "path": "/tags/-", "value": "tutorial" },
  { "op": "remove", "path": "/draft" }
]
```

### DELETE - Remove Resource

**Characteristics**:
- Not safe
- Idempotent
- Removes resource
- Typically no request body

**Examples**:
```http
DELETE /posts/123

Response: 204 No Content
# Or
Response: 200 OK
{
  "message": "Post deleted successfully",
  "deletedId": "123"
}
```

**Soft Delete Alternative**:
```http
PATCH /posts/123
{
  "deleted": true
}
```

## Status Codes

### Success Codes (2xx)

**200 OK**:
- Successful GET, PUT, PATCH
- Request succeeded and response includes content

**201 Created**:
- Successful POST that creates resource
- Include `Location` header
- Return created resource

**204 No Content**:
- Successful DELETE
- Successful operation with no response body
- Successful PUT/PATCH when not returning updated resource

**202 Accepted**:
- Request accepted but processing not complete
- Use for async operations
- Provide way to check status

### Client Error Codes (4xx)

**400 Bad Request**:
- Malformed request syntax
- Invalid request data
- Generic client error

```json
{
  "error": {
    "code": "BAD_REQUEST",
    "message": "Invalid request format",
    "details": ["Missing required field: email"]
  }
}
```

**401 Unauthorized**:
- Missing or invalid authentication
- Token expired

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required"
  }
}
```

**403 Forbidden**:
- Authenticated but not authorized
- Insufficient permissions

```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "Insufficient permissions to access this resource"
  }
}
```

**404 Not Found**:
- Resource doesn't exist

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Post with ID 123 not found"
  }
}
```

**409 Conflict**:
- Resource conflict
- Duplicate resource

```json
{
  "error": {
    "code": "CONFLICT",
    "message": "User with email already exists"
  }
}
```

**422 Unprocessable Entity**:
- Validation errors
- Semantically incorrect request

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      },
      {
        "field": "age",
        "message": "Must be 18 or older"
      }
    ]
  }
}
```

**429 Too Many Requests**:
- Rate limit exceeded

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Try again in 60 seconds."
  }
}
```

### Server Error Codes (5xx)

**500 Internal Server Error**:
- Generic server error
- Unexpected error

**502 Bad Gateway**:
- Invalid response from upstream server

**503 Service Unavailable**:
- Temporary downtime
- Maintenance mode
- Include `Retry-After` header

**504 Gateway Timeout**:
- Upstream server timeout

## Request/Response Formats

### JSON Naming Conventions

**Use camelCase**:
```json
{
  "firstName": "John",
  "lastName": "Doe",
  "emailAddress": "john@example.com",
  "createdAt": "2025-10-25T10:00:00Z"
}
```

### Consistent Response Envelopes

**Single Resource**:
```json
{
  "id": "123",
  "title": "Post Title",
  "author": {
    "id": "456",
    "name": "John Doe"
  },
  "createdAt": "2025-10-25T10:00:00Z"
}
```

**Collection**:
```json
{
  "data": [
    { "id": "1", "title": "Post 1" },
    { "id": "2", "title": "Post 2" }
  ],
  "pagination": {
    "total": 100,
    "limit": 10,
    "offset": 0,
    "hasMore": true
  }
}
```

### Timestamps

**Use ISO 8601 Format**:
```json
{
  "createdAt": "2025-10-25T10:30:00Z",
  "updatedAt": "2025-10-25T14:45:30.123Z"
}
```

**Include Timezone**:
- Always use UTC (Z suffix)
- Or include explicit offset: `2025-10-25T10:30:00+05:30`

### Null vs Omitted Fields

**Be Consistent**:
```json
// Option 1: Include null fields
{
  "name": "John",
  "nickname": null,
  "bio": null
}

// Option 2: Omit null fields (recommended)
{
  "name": "John"
}
```

## Error Handling

### Consistent Error Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": [
      {
        "field": "email",
        "message": "Invalid format"
      }
    ],
    "requestId": "req_abc123",
    "timestamp": "2025-10-25T10:30:00Z",
    "documentation": "https://docs.example.com/errors/ERROR_CODE"
  }
}
```

### Error Codes

**Use Consistent Naming**:
```
VALIDATION_ERROR
NOT_FOUND
UNAUTHORIZED
FORBIDDEN
RATE_LIMIT_EXCEEDED
INTERNAL_ERROR
```

### Validation Errors

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
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

## Authentication & Security

### OAuth 2.0 Flows

**Authorization Code Flow** (Web apps):
```
1. GET /oauth/authorize?
     client_id=CLIENT_ID&
     redirect_uri=CALLBACK&
     response_type=code&
     scope=read write

2. User authenticates

3. Redirect: CALLBACK?code=AUTH_CODE

4. POST /oauth/token
   {
     "grant_type": "authorization_code",
     "code": "AUTH_CODE",
     "client_id": "CLIENT_ID",
     "client_secret": "SECRET"
   }

5. Response: { "access_token": "...", "refresh_token": "..." }
```

**Client Credentials Flow** (Service-to-service):
```
POST /oauth/token
{
  "grant_type": "client_credentials",
  "client_id": "CLIENT_ID",
  "client_secret": "CLIENT_SECRET",
  "scope": "read write"
}
```

**PKCE Flow** (Mobile/SPA):
```
1. Generate code_verifier (random string)
2. Generate code_challenge = SHA256(code_verifier)

3. GET /oauth/authorize?
     client_id=CLIENT_ID&
     redirect_uri=CALLBACK&
     response_type=code&
     code_challenge=CHALLENGE&
     code_challenge_method=S256

4. POST /oauth/token
   {
     "grant_type": "authorization_code",
     "code": "AUTH_CODE",
     "client_id": "CLIENT_ID",
     "code_verifier": "VERIFIER"
   }
```

### JWT Tokens

**Structure**:
```
Header.Payload.Signature

eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiJ1c3JfMTIzIiwiaWF0IjoxNjk4MzM2MDAwfQ.
signature_here
```

**Payload Example**:
```json
{
  "sub": "usr_1234567890",
  "iat": 1698336000,
  "exp": 1698339600,
  "scope": ["read:posts", "write:posts"],
  "roles": ["user", "editor"]
}
```

**Usage**:
```http
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

### API Keys

**Header-Based**:
```http
X-API-Key: sk_live_abc123def456
```

**Query Parameter** (avoid for sensitive operations):
```
GET /api/users?api_key=sk_live_abc123def456
```

**Best Practices**:
- Different keys for different environments
- Allow multiple keys per account
- Implement key rotation
- Add expiration dates
- Log key usage

### Security Headers

```http
# HTTPS only
Strict-Transport-Security: max-age=31536000; includeSubDomains

# XSS protection
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'self'

# CORS
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Authorization, Content-Type
```

## Versioning

### URL Versioning

```
https://api.example.com/v1/users
https://api.example.com/v2/users
```

**Pros**:
- Very explicit
- Easy to route
- Simple to understand
- Good for major changes

**Cons**:
- URL proliferation
- Multiple codebases to maintain

### Header Versioning

```http
Accept: application/vnd.myapi.v2+json
# Or
API-Version: 2
```

**Pros**:
- Clean URLs
- Same endpoint, different versions
- Good for content negotiation

**Cons**:
- Less visible
- Harder to test
- Caching complexity

### When to Version

**Create new version for**:
- Removing endpoints
- Removing request/response fields
- Changing field types
- Breaking authentication changes
- Changing error formats

**Don't version for**:
- Adding new optional fields
- Adding new endpoints
- Bug fixes
- Performance improvements
- Internal refactoring

### Deprecation Process

```http
# Deprecation warning header
Sunset: Sat, 31 Dec 2025 23:59:59 GMT
Link: <https://docs.example.com/migration>; rel="deprecation"

# In response
{
  "data": {...},
  "warnings": [
    {
      "code": "DEPRECATED",
      "message": "This endpoint will be removed on 2025-12-31",
      "migrationGuide": "https://docs.example.com/migration"
    }
  ]
}
```

## Pagination

### Offset-Based Pagination

```
GET /posts?limit=20&offset=40

Response:
{
  "data": [...],
  "pagination": {
    "total": 500,
    "limit": 20,
    "offset": 40,
    "hasMore": true
  }
}
```

**Pros**:
- Simple to implement
- Jump to any page
- Show total count

**Cons**:
- Performance issues with large offsets
- Inconsistent results if data changes
- Not suitable for real-time data

### Cursor-Based Pagination

```
GET /posts?limit=20&cursor=eyJpZCI6MTIzfQ

Response:
{
  "data": [...],
  "pagination": {
    "nextCursor": "eyJpZCI6MTQzfQ",
    "prevCursor": "eyJpZCI6MTAzfQ",
    "hasMore": true
  }
}
```

**Pros**:
- Consistent results
- Good performance
- Works with real-time data
- No duplicate results

**Cons**:
- Can't jump to specific page
- No total count
- More complex implementation

### Link Header Pagination

```http
Link: <https://api.example.com/posts?cursor=abc>; rel="next",
      <https://api.example.com/posts?cursor=xyz>; rel="prev",
      <https://api.example.com/posts?cursor=first>; rel="first",
      <https://api.example.com/posts?cursor=last>; rel="last"
```

## Rate Limiting

### Implementation

**Headers**:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 75
X-RateLimit-Reset: 1698340800
Retry-After: 60
```

**Response when exceeded**:
```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1698340800
Retry-After: 60

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 60 seconds."
  }
}
```

### Strategies

**Per User**:
```
100 requests per hour per user
```

**Per IP**:
```
1000 requests per hour per IP
```

**Per Endpoint**:
```
/auth/login: 5 requests per minute
/posts: 100 requests per hour
```

**Tiered Limits**:
```
Free tier: 100 requests/hour
Pro tier: 1000 requests/hour
Enterprise: 10000 requests/hour
```

## Caching

### Cache Headers

**ETags**:
```http
# Response
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"

# Subsequent request
If-None-Match: "33a64df551425fcc55e4d42a148795d9f25f89d4"

# Response if not modified
HTTP/1.1 304 Not Modified
```

**Last-Modified**:
```http
# Response
Last-Modified: Wed, 25 Oct 2025 10:00:00 GMT

# Subsequent request
If-Modified-Since: Wed, 25 Oct 2025 10:00:00 GMT

# Response if not modified
HTTP/1.1 304 Not Modified
```

**Cache-Control**:
```http
# Public, cacheable for 1 hour
Cache-Control: public, max-age=3600

# Private, no caching
Cache-Control: private, no-cache, no-store, must-revalidate

# Conditional caching
Cache-Control: public, max-age=3600, must-revalidate
```

## Documentation

### OpenAPI/Swagger

Provide interactive API documentation with:
- All endpoints documented
- Request/response examples
- Authentication instructions
- Error code documentation
- Try-it-out functionality

### Additional Documentation

**Getting Started Guide**:
- Quick start tutorial
- Authentication setup
- First API call example
- Common use cases

**API Reference**:
- Complete endpoint documentation
- Parameter descriptions
- Response formats
- Error codes

**Best Practices Guide**:
- Recommended patterns
- Performance optimization
- Error handling
- Security considerations

**Changelog**:
- Version history
- Breaking changes
- New features
- Deprecations

**Migration Guides**:
- Version upgrade instructions
- Breaking change details
- Code examples
- Timeline for deprecations
