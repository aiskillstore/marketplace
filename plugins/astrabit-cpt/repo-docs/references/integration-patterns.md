# Integration Patterns

Common patterns for documenting cross-repository relationships.

## Microservices Architecture

Document service-to-service communication:

| Aspect | Document |
|--------|----------|
| Service discovery | How services find each other |
| Communication | REST, gRPC, message queue |
| Authentication | JWT propagation, mTLS |
| Failure handling | Circuit breakers, retries |

### Example Integration Section

```markdown
## Upstream Services

| Service | Endpoint | Purpose |
|---------|----------|---------|
| User Service | `user-api:8080` | Authentication and user profiles |
| Payment Service | `payment-api:8080` | Payment processing |

### Authentication

All requests include JWT from User Service. Include header:
```
Authorization: Bearer <token>
```

### Failure Handling

- Circuit breaker opens after 5 consecutive failures
- Retry with exponential backoff: 100ms, 200ms, 400ms
- Fallback to cached data when available
```

## Monorepo Patterns

Document relationships within a monorepo:

| Aspect | Document |
|--------|----------|
| Package boundaries | What belongs where |
| Internal dependencies | Import rules |
| Shared libraries | Common utilities location |
| Build order | Dependencies affect build |

### Example Monorepo Section

```markdown
## Monorepo Structure

This repository uses [pnpm workspace/npm workspaces].

| Package | Depends On | Purpose |
|---------|------------|---------|
| `@org/ui` | None | Shared React components |
| `@org/api` | `@org/types` | Backend type definitions |
| `@org/app` | `@org/ui`, `@org/api` | Main application |

### Internal Imports

```typescript
// Correct - use workspace protocol
import { Button } from '@org/ui';

// Incorrect - no relative imports across packages
import { Button } from '../../ui/src/Button';
```
```

## Shared Libraries

Document library consumption:

| Aspect | Document |
|--------|----------|
| Library location | Where it lives |
| Version pinning | How to update |
| Breaking changes | Notification process |

### Example Shared Library Section

```markdown
## Shared Libraries

| Library | Version | Location |
|---------|---------|----------|
| @org/shared-types | ^2.1.0 | github.com/org/shared-types |
| @org/utils | ^1.5.0 | github.com/org/utils |

### Updating Shared Libraries

1. Check changelog in the library's repo
2. Update version in package.json
3. Run `npm install`
4. Test locally; watch for breaking changes
```

## Event-Driven Integrations

Document event producers and consumers:

| Aspect | Document |
|--------|----------|
| Events | Schema and purpose |
| Producers | Who emits what |
| Consumers | Who listens to what |
| Delivery | At-least-once, exactly-once |

### Example Events Section

```markdown
## Event Integration

This service consumes events from Kafka and produces events for downstream services.

### Consumed Events

| Event | Source | Handling |
|-------|--------|----------|
| `user.created` | User Service | Create profile in local DB |
| `order.placed` | Order Service | Trigger fulfillment process |

### Produced Events

| Event | Payload | Consumers |
|-------|---------|------------|
| `payment.completed` | {orderId, amount} | Order Service, Email Service |
| `payment.failed` | {orderId, reason} | Notification Service |

### Event Schema

See `schemas/events/` for JSON Schema definitions.
```

## API Gateway Patterns

Document routing and aggregation:

| Aspect | Document |
|--------|----------|
| Routes | What goes where |
| Aggregation | Combined calls |
| Authentication | How auth flows through |

### Example Gateway Section

```markdown
## API Gateway Routes

| Route | Backend Service | Auth Required |
|-------|-----------------|---------------|
| GET /api/users/* | User Service | Yes |
| POST /api/orders | Order Service | Yes |
| GET /health | - | No |

### Response Aggregation

The `/api/dashboard` endpoint aggregates data from:
- User Service (profile data)
- Order Service (recent orders)
- Notification Service (unread count)

Timeout: 2s total. Partial failures return available data.
```

## Database Per Service

Document data ownership:

| Aspect | Document |
|--------|----------|
| Owned tables | What this service owns |
| Shared access | Read-only access to others |
| Migration policy | How schema changes work |

### Example Database Section

```markdown
## Data Ownership

This service owns the following tables:

| Table | Purpose | Access Pattern |
|-------|---------|----------------|
| `payments` | Payment records | Read/write (this service only) |
| `transactions` | Transaction log | Read/write (this service only) |

### Read-Only Access

This service has read-only access to:

| Table | Owner Service | Purpose |
|-------|---------------|---------|
| `users` | User Service | Validate user existence |
| `orders` | Order Service | Retrieve order details |

### Data Synchronization

This service listens to CDC events from:
- `users` table (User Service)
- `orders` table (Order Service)

Local cache updated viaDebezium Kafka topic.
```
