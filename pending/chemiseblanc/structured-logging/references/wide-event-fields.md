# Wide Event Field Reference

Comprehensive list of fields to include in wide events, organized by category.

## Table of Contents

- [Request Context](#request-context)
- [User Context](#user-context)
- [Business Context](#business-context)
- [Error Context](#error-context)
- [Timing and Performance](#timing-and-performance)
- [Infrastructure](#infrastructure)
- [Feature Flags](#feature-flags)

---

## Request Context

Core fields identifying the request:

| Field | Type | Description |
|-------|------|-------------|
| `request_id` | string | Unique identifier for this request |
| `trace_id` | string | Distributed tracing ID (spans multiple services) |
| `span_id` | string | Current span within the trace |
| `parent_span_id` | string | Parent span for nested calls |
| `timestamp` | ISO8601 | When the request started |
| `method` | string | HTTP method (GET, POST, etc.) |
| `path` | string | Request path (without query params) |
| `query_params` | object | Parsed query parameters |
| `status_code` | integer | HTTP response status |
| `bytes_sent` | integer | Response body size |
| `bytes_received` | integer | Request body size |
| `ip` | string | Client IP address |
| `user_agent` | string | Client user agent |
| `content_type` | string | Request content type |
| `accept` | string | Accepted response types |

---

## User Context

Fields identifying and describing the user:

| Field | Type | Description |
|-------|------|-------------|
| `user.id` | string | Unique user identifier |
| `user.email` | string | User email (if appropriate to log) |
| `user.subscription` | string | Tier: free, premium, enterprise |
| `user.account_age_days` | integer | Days since account creation |
| `user.lifetime_value_cents` | integer | Total revenue from this user |
| `user.is_internal` | boolean | Internal/employee account |
| `user.org_id` | string | Organization identifier |
| `user.org_name` | string | Organization name |
| `user.role` | string | User role within org |
| `user.permissions` | array | Active permissions |
| `user.locale` | string | User locale preference |
| `user.timezone` | string | User timezone |

---

## Business Context

Domain-specific fields. Adapt to your domain:

### E-commerce

| Field | Type | Description |
|-------|------|-------------|
| `cart.id` | string | Cart identifier |
| `cart.item_count` | integer | Number of items |
| `cart.total_cents` | integer | Cart total in cents |
| `cart.currency` | string | Currency code (USD, EUR) |
| `cart.coupon_applied` | string | Applied coupon code |
| `cart.discount_cents` | integer | Discount amount |
| `order.id` | string | Order identifier |
| `order.status` | string | Order status |
| `payment.method` | string | card, paypal, crypto |
| `payment.provider` | string | stripe, braintree |
| `payment.last_four` | string | Last 4 digits of card |
| `payment.attempt` | integer | Attempt number (for retries) |

### SaaS / API

| Field | Type | Description |
|-------|------|-------------|
| `api.version` | string | API version called |
| `api.endpoint` | string | Logical endpoint name |
| `api.rate_limit_remaining` | integer | Remaining requests |
| `api.rate_limit_reset` | timestamp | When limit resets |
| `resource.type` | string | Resource type accessed |
| `resource.id` | string | Resource identifier |
| `resource.action` | string | create, read, update, delete |

### Messaging / Async

| Field | Type | Description |
|-------|------|-------------|
| `message.id` | string | Message identifier |
| `message.topic` | string | Topic/queue name |
| `message.partition` | integer | Partition number |
| `message.offset` | integer | Message offset |
| `message.consumer_group` | string | Consumer group |
| `message.lag` | integer | Consumer lag |
| `message.retry_count` | integer | Number of retries |

---

## Error Context

Fields describing failures:

| Field | Type | Description |
|-------|------|-------------|
| `error.type` | string | Error class name (PaymentError, ValidationError) |
| `error.code` | string | Application error code |
| `error.message` | string | Human-readable message |
| `error.retriable` | boolean | Can the operation be retried |
| `error.provider_code` | string | Third-party error code |
| `error.provider_message` | string | Third-party error message |
| `error.suggestion` | string | Suggested fix or next step |
| `error.stack_trace` | string | Stack trace (for unexpected errors) |
| `error.caused_by` | object | Nested root cause error |

---

## Timing and Performance

Fields tracking latency and performance:

| Field | Type | Description |
|-------|------|-------------|
| `duration_ms` | integer | Total request duration |
| `timing.db_query_ms` | integer | Total database time |
| `timing.db_queries_count` | integer | Number of DB queries |
| `timing.cache_lookup_ms` | integer | Cache lookup time |
| `timing.cache_hit` | boolean | Whether cache hit |
| `timing.external_api_ms` | integer | External API call time |
| `timing.external_calls_count` | integer | Number of external calls |
| `timing.queue_wait_ms` | integer | Time waiting in queue |
| `timing.serialization_ms` | integer | Serialization time |
| `timing.render_ms` | integer | Template render time |

---

## Infrastructure

Fields identifying where the code ran:

| Field | Type | Description |
|-------|------|-------------|
| `service` | string | Service name |
| `version` | string | Service version |
| `deployment_id` | string | Deployment identifier |
| `region` | string | Cloud region |
| `availability_zone` | string | AZ within region |
| `instance_id` | string | Instance/VM identifier |
| `pod_name` | string | Kubernetes pod name |
| `node_name` | string | Kubernetes node |
| `container_id` | string | Container identifier |
| `environment` | string | prod, staging, dev |
| `git_sha` | string | Git commit hash |

---

## Feature Flags

Fields tracking experiments and rollouts:

| Field | Type | Description |
|-------|------|-------------|
| `feature_flags.<flag_name>` | boolean/string | Flag value |
| `experiment.name` | string | Active experiment name |
| `experiment.variant` | string | Assigned variant (control, treatment) |
| `experiment.bucket` | integer | User's bucket (0-99) |
| `rollout.percentage` | integer | Rollout percentage when sampled |

Example:

```json
{
  "feature_flags": {
    "new_checkout_flow": true,
    "express_payment": false,
    "dark_mode": "enabled"
  },
  "experiment": {
    "name": "pricing_test_q1",
    "variant": "treatment_b",
    "bucket": 47
  }
}
```

---

## Guidelines

1. **Always include**: request_id, trace_id, timestamp, duration_ms, status_code, user.id
2. **Include when relevant**: Full business context for the operation
3. **Include on errors**: Complete error object with type, code, message, retriable
4. **Avoid logging**: Passwords, tokens, full credit card numbers, PII unless necessary
5. **Use consistent naming**: snake_case for fields, nested objects for related fields
6. **Use appropriate types**: integers for counts/durations, booleans for flags, strings for identifiers
