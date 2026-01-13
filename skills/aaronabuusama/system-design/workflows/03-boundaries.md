# Phase 3: Boundaries

**Goal:** Define the ports (interfaces), adapters (implementations), and architectural layers.

## Prerequisites

- Phase 1 Discovery completed
- Phase 2 Domain Model defined

## Hexagonal Architecture Refresher

```
                    ┌─────────────────────────────────────┐
                    │           DRIVING SIDE              │
                    │    (things that USE the system)     │
                    └─────────────────────────────────────┘
                                     │
                              Inbound Ports
                                     │
                                     ▼
┌─────────────┐         ┌─────────────────────┐         ┌─────────────┐
│   Driving   │────────▶│                     │◀────────│   Driven    │
│  Adapters   │         │    APPLICATION      │         │  Adapters   │
│  (Primary)  │         │       CORE          │         │ (Secondary) │
│             │         │                     │         │             │
│ - REST API  │         │  - Use Cases        │         │ - Database  │
│ - CLI       │         │  - Domain Model     │         │ - External  │
│ - GraphQL   │         │  - Business Rules   │         │   APIs      │
│ - Events    │         │                     │         │ - File Sys  │
└─────────────┘         └─────────────────────┘         └─────────────┘
                                     │
                              Outbound Ports
                                     │
                                     ▼
                    ┌─────────────────────────────────────┐
                    │           DRIVEN SIDE               │
                    │   (things the system USES)          │
                    └─────────────────────────────────────┘
```

## Entry Questions

### 1. Inbound Ports (How is the system used?)
- "How will users interact with this system?"
- "What are ALL the entry points?" (API, CLI, scheduled jobs, events)
- "Are there different interfaces for different user types?"

### 2. Outbound Ports (What does the system need?)
- "What external systems does this depend on?"
- "What data needs to be persisted?"
- "What notifications/events need to be sent?"

### 3. Layer Decisions
- "What belongs in the domain layer vs application layer?"
- "Where should validation live?"
- "Where does authorization happen?"

## Port Identification Checklist

### Inbound Ports (Primary/Driving)
| Port Type | Questions to Ask |
|-----------|------------------|
| HTTP/REST | What endpoints? What payloads? |
| CLI | What commands? What arguments? |
| Event Consumer | What events? From where? |
| Scheduled Jobs | What triggers? What frequency? |
| WebSocket | What real-time interactions? |

### Outbound Ports (Secondary/Driven)
| Port Type | Questions to Ask |
|-----------|------------------|
| Repository | What entities need persistence? Query patterns? |
| External API | What services? What's the contract? |
| Event Publisher | What events? Who consumes them? |
| File Storage | What files? What operations? |
| Notification | What channels? What triggers? |

## Defining Port Interfaces

For each port, define:

```typescript
// Example: Inbound Port (driving)
interface CreateOrderUseCase {
  execute(command: CreateOrderCommand): Promise<OrderCreatedResult>;
}

// Example: Outbound Port (driven)
interface OrderRepository {
  save(order: Order): Promise<void>;
  findById(id: OrderId): Promise<Order | null>;
  findByCustomer(customerId: CustomerId): Promise<Order[]>;
}
```

## Adapter Planning

For each port, plan the adapter:

| Port | Adapter | Implementation Notes |
|------|---------|---------------------|
| `OrderRepository` | `PostgresOrderRepository` | Uses Drizzle ORM |
| `CreateOrderUseCase` | `CreateOrderController` | REST POST /orders |
| `PaymentGateway` | `StripePaymentAdapter` | Stripe SDK |

## Probing Questions

| If they say... | Ask... |
|----------------|--------|
| "The API calls the database" | "What abstraction sits between them?" |
| "We'll use [Framework X]" | "What interface does your domain see?" |
| "It needs to be flexible" | "What specifically needs to change without rewriting core?" |

## Red Flags

- **Tight coupling** - domain knows about frameworks/infrastructure
- **Missing ports** - direct dependencies on external systems
- **Fat adapters** - business logic in adapters instead of domain
- **Leaky abstractions** - port interfaces expose implementation details

## Boundaries Output

Before moving to Phase 4:

```markdown
## Inbound Ports
| Port Name | Purpose | Methods |
|-----------|---------|---------|

## Outbound Ports
| Port Name | Purpose | Methods |
|-----------|---------|---------|

## Planned Adapters
| Port | Adapter | Technology |
|------|---------|------------|

## Layer Structure
- domain/: [What goes here]
- application/: [What goes here]
- infrastructure/: [What goes here]
- interfaces/: [What goes here]

## Dependency Rule Verification
[Confirm that dependencies point inward]
```

## Transition to Phase 4

When boundaries are defined:

1. Present the hexagonal diagram with actual ports/adapters
2. Verify dependency direction (always inward)
3. Confirm adapter technology choices
4. Ask: "Ready to generate the scaffold?"

Then: `read ./workflows/04-scaffolding.md`
