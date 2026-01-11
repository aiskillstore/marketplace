# Blueprint Format

Standard format for implementation blueprints produced by the waterfall-architect agent.

## Structure

### Approach

High-level description of how to implement this feature or change. 1-2 paragraphs explaining the overall strategy and rationale.

### Key Files

Files that will be created or modified, with their purpose:

| File | Action | Purpose |
|------|--------|---------|
| `path/to/file.ts` | Create | Description of role |
| `path/to/existing.ts` | Modify | What changes and why |

### Implementation Steps

Numbered, atomic actions in recommended execution order:

1. Step one - brief description
2. Step two - brief description
3. ...

Steps should be small enough to verify individually. Prefer incremental changes over big-bang rewrites.

### Considerations

Additional factors for implementation:

- **Edge cases**: Scenarios to handle
- **Performance**: Implications and benchmarks if relevant
- **Security**: Concerns and mitigations
- **Dependencies**: Prerequisites or external requirements
- **Risks**: What could go wrong and how to recover
- **Testing**: Suggested verification approach

For refactoring work, also include:

- **Constraints**: Requirements that must NOT break (reference IDs from features.yml)
- **Rollback**: Recovery strategy if a step fails

## Example

```markdown
## Blueprint: Add Rate Limiting to API

### Approach

Implement sliding window rate limiting using Redis as the backing store. 
Middleware will intercept requests before they reach handlers, check/increment 
counters, and return 429 responses when limits are exceeded. This approach 
allows distributed rate limiting across multiple server instances.

### Key Files

| File | Action | Purpose |
|------|--------|---------|
| `src/middleware/rateLimit.ts` | Create | Rate limiting middleware |
| `src/config/limits.ts` | Create | Rate limit configuration |
| `src/app.ts` | Modify | Register middleware |
| `tests/middleware/rateLimit.test.ts` | Create | Unit tests |

### Implementation Steps

1. Add ioredis dependency to package.json
2. Create rate limit configuration with sensible defaults
3. Implement sliding window counter logic in rateLimit.ts
4. Add middleware registration in app.ts (before route handlers)
5. Add X-RateLimit-* response headers
6. Write unit tests with mocked Redis
7. Write integration test with real Redis

### Considerations

- **Edge cases**: Handle Redis connection failures gracefully (fail open vs fail closed)
- **Performance**: Redis round-trip adds ~1-2ms latency per request
- **Security**: Use user ID for authenticated requests, IP for anonymous
- **Dependencies**: Requires Redis instance; document in README
- **Risks**: Clock skew between servers; use Redis server time, not local
- **Testing**: Need Redis in CI pipeline or use testcontainers
```
