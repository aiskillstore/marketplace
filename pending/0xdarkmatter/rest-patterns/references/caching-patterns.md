# Caching Patterns

HTTP caching strategies for REST APIs.

## Response Headers

### Cache-Control

```http
# Cache for 1 hour
Cache-Control: max-age=3600

# Cache, but always revalidate
Cache-Control: max-age=0, must-revalidate

# Never cache (sensitive data)
Cache-Control: no-store

# Browser only, not CDN
Cache-Control: private, max-age=600

# Shared/CDN caching
Cache-Control: public, max-age=3600

# Stale content while revalidating
Cache-Control: max-age=3600, stale-while-revalidate=60
```

### Validation Headers

```http
# Content fingerprint
ETag: "abc123"
ETag: W/"abc123"  # Weak ETag (semantic equivalence)

# Last modification time
Last-Modified: Wed, 21 Oct 2024 07:28:00 GMT
```

## Request Headers

### Conditional Requests

```http
# Validate ETag
If-None-Match: "abc123"

# Validate last modified
If-Modified-Since: Wed, 21 Oct 2024 07:28:00 GMT

# Only update if ETag matches (optimistic locking)
If-Match: "abc123"
```

### Bypass Cache

```http
# Force revalidation
Cache-Control: no-cache

# Bypass entirely (use sparingly)
Cache-Control: no-store
Pragma: no-cache
```

## Caching Strategies by Resource

| Resource Type | Strategy | Headers |
|---------------|----------|---------|
| Static assets (JS, CSS) | Long-lived | `max-age=31536000, immutable` |
| Versioned assets | Permanent | `max-age=31536000` with hash in filename |
| API responses | Short/revalidate | `max-age=60, must-revalidate` |
| User-specific data | Private | `private, max-age=0` |
| Sensitive data | Never cache | `no-store` |
| Public lists | Shared | `public, max-age=300` |
| Search results | Short-lived | `max-age=60` |

## ETag Workflow

### Initial Request

```http
GET /users/123

→ 200 OK
→ ETag: "v1-abc123"
→ Cache-Control: max-age=60
→ {"id": 123, "name": "Alice", "updated_at": "..."}
```

### Revalidation (Cache Valid)

```http
GET /users/123
If-None-Match: "v1-abc123"

→ 304 Not Modified
(No body, client uses cached version)
```

### Revalidation (Cache Stale)

```http
GET /users/123
If-None-Match: "v1-abc123"

→ 200 OK
→ ETag: "v2-def456"
→ {"id": 123, "name": "Alice Updated", "updated_at": "..."}
```

## Optimistic Locking with ETag

Prevent concurrent update conflicts:

```http
# Get current version
GET /users/123
→ ETag: "v1"

# Update with version check
PATCH /users/123
If-Match: "v1"
{"name": "New Name"}

→ 200 OK (if still v1)
→ 412 Precondition Failed (if changed)
```

## CDN Caching

### Vary Header

Tell CDN which headers affect response:

```http
# Different response per Accept-Language
Vary: Accept-Language

# Different per auth (don't cache auth-dependent responses in CDN)
Vary: Authorization
Cache-Control: private
```

### Surrogate Keys

For targeted cache invalidation:

```http
Surrogate-Key: user-123 users-list homepage
```

## Cache Invalidation Patterns

### Active Invalidation

```bash
# Purge by URL
curl -X PURGE https://cdn.example.com/api/users/123

# Purge by surrogate key
curl -X PURGE https://cdn.example.com \
  -H "Surrogate-Key: user-123"
```

### Passive Invalidation

- Use short `max-age` with `stale-while-revalidate`
- Version in URL: `/v2/users` instead of `/users`
- Hash in filename for assets

## Common Patterns

### API Responses

```http
Cache-Control: private, max-age=0, must-revalidate
ETag: "content-hash"
```

### Authenticated Endpoints

```http
Cache-Control: private, no-store
```

### Public Data (rarely changes)

```http
Cache-Control: public, max-age=3600, stale-while-revalidate=60
ETag: "content-hash"
```
