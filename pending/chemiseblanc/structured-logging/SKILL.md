---
name: structured-logging
description: Guide for writing effective log messages using wide events / canonical log lines. Use when writing logging code, adding instrumentation, improving observability, or reviewing log statements. Teaches high-cardinality, high-dimensionality structured logging that enables debugging.
---

# Structured Logging

## Core Principle

Emit **one wide event per request per service**, not scattered log statements.

- Build context throughout the request lifecycle
- Emit once at the end (in a finally block)
- Optimize for **querying**, not writing
- Include high-cardinality fields (user_id, request_id) that enable debugging
- Include high-dimensionality (50+ fields) capturing full context

## Anti-patterns

Avoid these common mistakes:

```
// String concatenation - loses structure
log("User " + userId + " payment failed: " + error)

// Scattered statements - 17 lines for one request
log("Starting request")
log("Validating token")
log("Token valid")
log("Fetching user")
log("User found")
log("Processing payment")
log("Payment failed")

// Low cardinality only - can't debug specific users
log({level: "error", message: "Payment failed"})

// Missing business context - no debugging power
log({user_id: "123", error: "failed"})
```

## Wide Event Structure

One comprehensive event per request:

```json
{
  "timestamp": "2025-01-15T10:23:45.612Z",
  "level": "error",

  "request_id": "req_8bf7ec2d",
  "trace_id": "abc123",
  "span_id": "span_456",

  "service": "checkout-service",
  "version": "2.4.1",
  "deployment_id": "deploy_789",
  "region": "us-east-1",

  "method": "POST",
  "path": "/api/checkout",
  "status_code": 500,
  "duration_ms": 1247,

  "user": {
    "id": "user_456",
    "subscription": "premium",
    "account_age_days": 847,
    "lifetime_value_cents": 284700
  },

  "cart": {
    "id": "cart_xyz",
    "item_count": 3,
    "total_cents": 15999,
    "coupon_applied": "SAVE20"
  },

  "payment": {
    "method": "card",
    "provider": "stripe",
    "latency_ms": 1089,
    "attempt": 3
  },

  "error": {
    "type": "PaymentError",
    "code": "card_declined",
    "message": "Card declined by issuer",
    "retriable": false,
    "stripe_decline_code": "insufficient_funds"
  },

  "feature_flags": {
    "new_checkout_flow": true,
    "express_payment": false
  },

  "timing": {
    "db_query_ms": 45,
    "external_api_ms": 1089,
    "db_queries_count": 3,
    "cache_hit": false
  }
}
```

For the comprehensive field reference, see [references/wide-event-fields.md](references/wide-event-fields.md).

## Log Levels

Use log levels to indicate severity and required action:

| Level | When to Use | Examples |
|-------|-------------|----------|
| **ERROR** | Request failed, needs investigation | Unhandled exception, 5xx response, data corruption |
| **WARN** | Degraded but recovered | Retry succeeded, fallback used, rate limit approaching, deprecated API called |
| **INFO** | Normal request completion | The canonical log line for successful requests |
| **DEBUG** | Detailed diagnostics | Cache lookups, query plans, intermediate state (usually sampled out in production) |

The wide event's `level` field reflects the worst outcome of the request:
- Request succeeded normally: `info`
- Request succeeded after retry/fallback: `warn`
- Request failed: `error`

## Examples

### Bad: Scattered Logs

```
log.info("Incoming request", {path: "/checkout"})
log.debug("Fetching user")
log.debug("User found", {user_id: "123"})
log.debug("Fetching cart")
log.info("Processing payment")
log.warn("Payment attempt 1 failed, retrying")
log.warn("Payment attempt 2 failed, retrying")
log.error("Payment failed after 3 attempts")
```

### Good: Single Wide Event

```
log.error({
  request_id: "req_abc",
  path: "/checkout",
  method: "POST",
  status_code: 500,
  duration_ms: 3200,
  user: {id: "123", subscription: "premium"},
  cart: {item_count: 3, total_cents: 15999},
  payment: {
    provider: "stripe",
    attempts: 3,
    latency_ms: 2800
  },
  error: {
    type: "PaymentError",
    code: "card_declined",
    retriable: false
  }
})
```

### Bad: Missing Context

```
log.error("Database query failed", {error: "timeout"})
```

### Good: Full Context

```
log.error({
  request_id: "req_xyz",
  user: {id: "user_789", subscription: "enterprise"},
  operation: "fetch_orders",
  database: {
    host: "db-prod-01",
    query_duration_ms: 30000,
    timeout_ms: 30000,
    table: "orders",
    rows_scanned: 1500000
  },
  error: {
    type: "DatabaseError",
    code: "QUERY_TIMEOUT",
    message: "Query exceeded 30s timeout",
    retriable: true,
    suggestion: "Add index on orders.user_id or paginate results"
  }
})
```

## Implementation Pattern

Build the event throughout the request, emit once at the end:

```
function loggingMiddleware(handler):
    return function(request):
        start_time = now()

        // Initialize wide event
        event = {
            request_id: request.id,
            trace_id: request.trace_id,
            timestamp: start_time,
            method: request.method,
            path: request.path,
            service: SERVICE_NAME,
            version: SERVICE_VERSION
        }

        // Make event available to handlers
        request.wide_event = event

        try:
            response = handler(request)
            event.status_code = response.status
            event.level = "info"
            return response

        catch error:
            event.status_code = 500
            event.level = "error"
            event.error = {
                type: error.name,
                message: error.message,
                code: error.code,
                retriable: error.retriable ?? false
            }
            throw error

        finally:
            event.duration_ms = now() - start_time
            logger.log(event)
```

In handlers, enrich with business context:

```
function checkoutHandler(request):
    event = request.wide_event

    // Add user context
    user = getUser(request)
    event.user = {
        id: user.id,
        subscription: user.tier,
        account_age_days: daysSince(user.created_at),
        lifetime_value_cents: user.ltv
    }

    // Add business context
    cart = getCart(user.id)
    event.cart = {
        id: cart.id,
        item_count: cart.items.length,
        total_cents: cart.total
    }

    // Track timing for external calls
    payment_start = now()
    result = processPayment(cart)
    event.payment = {
        provider: "stripe",
        latency_ms: now() - payment_start,
        attempt: result.attempt_number
    }

    return response(result)
```

## Querying Power

Wide events enable queries that scattered logs cannot:

```sql
-- Find all checkout failures for premium users with new checkout flow
SELECT * FROM logs
WHERE path = '/checkout'
  AND status_code >= 500
  AND user.subscription = 'premium'
  AND feature_flags.new_checkout_flow = true
  AND timestamp > now() - interval '1 hour'

-- Analyze payment failures by error code and user tier
SELECT
  error.code,
  user.subscription,
  count(*) as failures,
  avg(payment.latency_ms) as avg_latency
FROM logs
WHERE error.type = 'PaymentError'
GROUP BY error.code, user.subscription

-- Find slow requests for enterprise customers
SELECT * FROM logs
WHERE duration_ms > 2000
  AND user.subscription = 'enterprise'
ORDER BY duration_ms DESC
```
