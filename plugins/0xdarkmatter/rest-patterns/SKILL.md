---
name: rest-patterns
description: "Quick reference for RESTful API design patterns, HTTP semantics, caching, and rate limiting. Triggers on: rest api, http methods, status codes, api design, endpoint design, api versioning, rate limiting, caching headers."
allowed-tools: "Read Write"
---

# REST Patterns

Quick reference for RESTful API design patterns and HTTP semantics.

## HTTP Methods

| Method | Purpose | Idempotent | Cacheable |
|--------|---------|------------|-----------|
| **GET** | Retrieve resource(s) | Yes | Yes |
| **POST** | Create new resource | No | No |
| **PUT** | Replace entire resource | Yes | No |
| **PATCH** | Partial update | Maybe | No |
| **DELETE** | Remove resource | Yes | No |

## Essential Status Codes

| Code | Name | Use |
|------|------|-----|
| **200** | OK | Success with body |
| **201** | Created | POST success (add `Location` header) |
| **204** | No Content | Success, no body |
| **400** | Bad Request | Invalid syntax |
| **401** | Unauthorized | Not authenticated |
| **403** | Forbidden | Not authorized |
| **404** | Not Found | Resource doesn't exist |
| **422** | Unprocessable | Validation error |
| **429** | Too Many Requests | Rate limited |
| **500** | Server Error | Internal failure |

## Resource Design

```http
GET    /users              # List
POST   /users              # Create
GET    /users/{id}         # Get one
PUT    /users/{id}         # Replace
PATCH  /users/{id}         # Update
DELETE /users/{id}         # Delete

# Query parameters
GET /users?page=2&limit=20          # Pagination
GET /users?sort=created_at:desc     # Sorting
GET /users?role=admin               # Filtering
```

## Security Checklist

- [ ] HTTPS/TLS only
- [ ] OAuth 2.0 or JWT for auth
- [ ] Validate all inputs
- [ ] Rate limit per client
- [ ] CORS headers configured
- [ ] No sensitive data in URLs
- [ ] Use `no-store` for sensitive responses

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Verbs in URLs | `/getUsers` → `/users` |
| Deep nesting | Flatten or use query params |
| 200 for errors | Use proper 4xx/5xx |
| No pagination | Always paginate collections |
| Missing rate limits | Protect against abuse |

## Quick Reference

| Task | Pattern |
|------|---------|
| Paginate | `?page=2&limit=20` |
| Sort | `?sort=field:asc` |
| Filter | `?status=active` |
| Sparse fields | `?fields=id,name` |
| Include related | `?include=orders` |

## When to Use

- Designing new API endpoints
- Choosing HTTP methods and status codes
- Implementing caching headers
- Setting up rate limiting
- Structuring error responses

## Additional Resources

For detailed patterns, load:
- `./references/status-codes.md` - Complete status code reference with examples
- `./references/caching-patterns.md` - Cache-Control, ETag, CDN patterns
- `./references/rate-limiting.md` - Rate limiting strategies and headers
- `./references/response-formats.md` - Errors, versioning, bulk ops, HATEOAS
