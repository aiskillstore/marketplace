# Architecture Decision Record (ADR) Template

## File Naming

```
docs/adr/
├── 0001-record-architecture-decisions.md
├── 0002-use-hexagonal-architecture.md
├── 0003-choose-postgresql-for-persistence.md
└── ...
```

## Template

```markdown
# ADR-[NUMBER]: [TITLE]

## Status

[Proposed | Accepted | Deprecated | Superseded by ADR-XXXX]

## Date

[YYYY-MM-DD when the decision was made]

## Context

[Describe the forces at play, including technological, political, social, and project local. These forces are probably in tension, and should be called out as such. The language in this section is value-neutral. It is simply describing facts.]

### Problem Statement
[What specific problem are we trying to solve?]

### Constraints
- [Constraint 1]
- [Constraint 2]

### Assumptions
- [Assumption 1]
- [Assumption 2]

## Decision Drivers

- [Driver 1, e.g., "Must support high read throughput"]
- [Driver 2, e.g., "Team has limited experience with X"]
- [Driver 3, e.g., "Budget constraints"]

## Considered Options

### Option 1: [Name]
[Brief description]

**Pros:**
- [Pro 1]
- [Pro 2]

**Cons:**
- [Con 1]
- [Con 2]

### Option 2: [Name]
[Brief description]

**Pros:**
- [Pro 1]
- [Pro 2]

**Cons:**
- [Con 1]
- [Con 2]

### Option 3: [Name]
[Brief description]

**Pros:**
- [Pro 1]
- [Pro 2]

**Cons:**
- [Con 1]
- [Con 2]

## Decision

[Describe the change that we're proposing and/or doing. Use full sentences, with active voice. "We will..."]

## Rationale

[Explain why this option was chosen over others. Reference the decision drivers and explain how this option best addresses them.]

## Consequences

### Positive
- [Positive consequence 1]
- [Positive consequence 2]

### Negative
- [Negative consequence 1]
- [Negative consequence 2]

### Risks
- [Risk 1]: [Mitigation strategy]
- [Risk 2]: [Mitigation strategy]

## Implementation Notes

[Any specific notes about how this decision should be implemented]

## Related Decisions

- [ADR-XXXX: Related decision]
- [ADR-YYYY: Another related decision]

## References

- [Link to relevant documentation]
- [Link to relevant discussion]
```

## Example: Hexagonal Architecture Decision

```markdown
# ADR-0002: Use Hexagonal Architecture for Order Service

## Status

Accepted

## Date

2024-01-15

## Context

We are building a new order management service that needs to:
- Integrate with multiple payment providers (Stripe, PayPal)
- Support different database backends for different deployment environments
- Be thoroughly testable without external dependencies
- Allow the team to work on different components in parallel

### Problem Statement
How do we structure the application to isolate business logic from infrastructure concerns while maintaining flexibility to swap implementations?

### Constraints
- Team has 3 months to deliver MVP
- Must integrate with existing customer service (REST API)
- Must support PostgreSQL in production, SQLite for development

### Assumptions
- Payment provider requirements may change
- Additional adapters (CLI, GraphQL) may be needed later
- The domain logic is complex enough to warrant isolation

## Decision Drivers

- **Testability**: Must be able to test business logic without databases or external services
- **Flexibility**: Must support swapping infrastructure without changing business logic
- **Maintainability**: Clear boundaries make the codebase easier to navigate
- **Team productivity**: Allow parallel work on different layers

## Considered Options

### Option 1: Layered Architecture (Traditional N-Tier)

**Pros:**
- Team is familiar with it
- Simple to understand initially

**Cons:**
- Business logic often leaks into controllers
- Database changes ripple through all layers
- Hard to test without mocking framework internals

### Option 2: Hexagonal Architecture (Ports & Adapters)

**Pros:**
- Complete isolation of business logic
- Easy to test with fake adapters
- Swappable infrastructure
- Clear dependency direction

**Cons:**
- More boilerplate (interfaces, adapters)
- Learning curve for team members unfamiliar with pattern
- Can be over-engineered for simple CRUD

### Option 3: Clean Architecture

**Pros:**
- Well-documented (Uncle Bob's book)
- Similar benefits to Hexagonal

**Cons:**
- More layers than necessary for our use case
- Strict layering can feel bureaucratic

## Decision

We will use Hexagonal Architecture (Ports & Adapters) for the Order Service.

The structure will be:
- `domain/`: Entities, value objects, domain events
- `application/`: Use cases and port interfaces
- `infrastructure/`: Adapter implementations
- `interfaces/`: HTTP controllers, CLI handlers

## Rationale

Hexagonal Architecture best addresses our decision drivers:

1. **Testability**: We can test use cases with fake repositories and gateways
2. **Flexibility**: Adding PayPal support means adding one adapter, not changing business logic
3. **Maintainability**: Clear boundaries (ports) define contracts between layers
4. **Team productivity**: One dev can work on Stripe adapter while another works on use cases

The learning curve is acceptable given the long-term benefits, and we'll mitigate it with documentation and pair programming.

## Consequences

### Positive
- Business logic is isolated and testable
- Can swap PostgreSQL for SQLite in tests
- Can add GraphQL adapter later without touching core
- New team members can understand boundaries quickly

### Negative
- More files and interfaces than a simple approach
- Initial development is slightly slower
- Risk of over-abstracting simple operations

### Risks
- **Team resistance**: Mitigate with training session and pair programming
- **Over-engineering**: Mitigate by reviewing if patterns are actually needed for each feature

## Implementation Notes

1. Start with in-memory adapters for fast iteration
2. Add real adapters (Postgres, Stripe) once domain is stable
3. Use constructor injection for all dependencies
4. Create composition root in `src/config/index.ts`

## Related Decisions

- ADR-0001: Record Architecture Decisions
- ADR-0003: Use PostgreSQL for Production Persistence

## References

- Alistair Cockburn's Hexagonal Architecture: https://alistair.cockburn.us/hexagonal-architecture/
- Netflix Hexagonal Architecture: https://netflixtechblog.com/ready-for-changes-with-hexagonal-architecture-b315ec967749
```
