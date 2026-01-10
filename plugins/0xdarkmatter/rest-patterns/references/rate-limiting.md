# Rate Limiting Patterns

Strategies and headers for API rate limiting.

## Standard Headers

### Response Headers

```http
X-RateLimit-Limit: 1000          # Max requests per window
X-RateLimit-Remaining: 847       # Requests remaining
X-RateLimit-Reset: 1698415200    # Unix timestamp when limit resets
Retry-After: 60                  # Seconds to wait (on 429)
```

### Rate Limit Response (429)

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests",
    "retry_after": 60,
    "limit": 1000,
    "remaining": 0,
    "reset_at": "2024-10-27T12:00:00Z"
  }
}
```

## Rate Limiting Strategies

### Fixed Window

Simple: count requests in fixed time periods.

```
Window: 1 minute (00:00-00:59, 01:00-01:59, ...)
Limit: 100 requests

Pros: Simple to implement
Cons: Burst at window edges (200 in 2 seconds across boundary)
```

### Sliding Window

Smoother: use weighted average across windows.

```
Current window: 50% through
Previous window: 60 requests
Current window: 40 requests

Weighted count = (60 × 0.5) + 40 = 70
Remaining = 100 - 70 = 30

Pros: Smoother limits
Cons: More complex, needs previous window data
```

### Token Bucket

Allows bursts with steady refill.

```
Bucket capacity: 100 tokens
Refill rate: 10 tokens/second

- Start with 100 tokens
- Each request costs 1 token
- Tokens refill at 10/sec
- Burst allowed up to 100, then steady 10/sec

Pros: Allows bursts, intuitive
Cons: More state to track
```

### Leaky Bucket

Fixed output rate, queue excess.

```
Processing rate: 10 requests/second
Queue size: 50

- Requests queue up
- Processed at constant rate
- Queue overflow = 429

Pros: Smooth output, protects backend
Cons: Adds latency
```

## Rate Limit Tiers

### By User/Plan

```http
# Free tier
X-RateLimit-Limit: 100
X-RateLimit-Window: 3600   # per hour

# Pro tier
X-RateLimit-Limit: 10000
X-RateLimit-Window: 3600
```

### By Endpoint

```http
# Search (expensive)
X-RateLimit-Limit: 10
X-RateLimit-Window: 60

# Read (cheap)
X-RateLimit-Limit: 1000
X-RateLimit-Window: 60
```

### By Operation Type

```http
# Writes
POST/PUT/DELETE: 100/minute

# Reads
GET: 1000/minute
```

## Implementation Headers

### GitHub Style

```http
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4999
X-RateLimit-Reset: 1372700873
X-RateLimit-Used: 1
X-RateLimit-Resource: core
```

### RFC Draft (RateLimit Headers)

```http
RateLimit-Limit: 100
RateLimit-Remaining: 50
RateLimit-Reset: 60
```

## Client Handling

### Retry Logic

```javascript
async function fetchWithRetry(url, options, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    const response = await fetch(url, options);

    if (response.status === 429) {
      const retryAfter = response.headers.get('Retry-After') || 60;
      await sleep(retryAfter * 1000);
      continue;
    }

    return response;
  }
  throw new Error('Rate limit exceeded after retries');
}
```

### Proactive Backoff

```javascript
function checkRateLimit(response) {
  const remaining = response.headers.get('X-RateLimit-Remaining');
  const reset = response.headers.get('X-RateLimit-Reset');

  if (remaining < 10) {
    const waitMs = (reset - Date.now()) / remaining;
    // Slow down requests
  }
}
```

## Best Practices

### Server Side

1. Include rate limit headers in all responses
2. Return 429 with clear error message
3. Always include `Retry-After`
4. Consider different limits per endpoint
5. Log rate limit hits for monitoring

### Client Side

1. Respect `Retry-After` header
2. Implement exponential backoff
3. Monitor remaining quota
4. Cache responses to reduce requests
5. Batch operations when possible
