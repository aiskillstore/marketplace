# Common Architectural Patterns to Identify

## Architectural Patterns

### Layered Architecture
```
Presentation Layer (UI/API)
    ↓
Application Layer (Services/Use Cases)
    ↓
Domain Layer (Entities/Business Logic)
    ↓
Infrastructure Layer (Database/External Services)
```

**Indicators:**
- Folder structure: `Controllers`, `Services`, `Domain`, `Infrastructure`
- Clear separation of concerns
- Dependencies flow downward

**Business Analysis Implications:**
- Business logic concentrated in Domain/Application layers
- Validation rules often in Domain layer
- Integration points in Infrastructure layer

### Clean Architecture / Hexagonal
```
        External World
             ↓
    [Adapters/Controllers]
             ↓
      [Use Cases/Services]
             ↓
        [Domain Core]
```

**Indicators:**
- `Ports` and `Adapters` folders
- Interface-based design
- Domain has no external dependencies

**Business Analysis Implications:**
- Use cases represent discrete business capabilities
- Domain models are pure business logic
- Easy to trace requirements to use cases

### Microservices
```
[Service A] ←→ [Message Broker] ←→ [Service B]
     ↓                                   ↓
[Database A]                       [Database B]
```

**Indicators:**
- Multiple deployable units
- API gateway configuration
- Message queue usage
- Service discovery

**Business Analysis Implications:**
- Each service = bounded context
- Business capabilities split across services
- Integration complexity between services

### Event-Driven Architecture
```
[Producer] → [Event Bus] → [Consumer 1]
                        → [Consumer 2]
```

**Indicators:**
- Event classes/DTOs
- Message handlers
- Pub/sub patterns
- Event sourcing

**Business Analysis Implications:**
- Business events = important domain actions
- Eventual consistency considerations
- Audit trail through event history

### CQRS (Command Query Responsibility Segregation)
```
Commands → [Write Model] → [Event Store]
                              ↓
Queries  → [Read Model]  ← [Projections]
```

**Indicators:**
- Separate command and query handlers
- Different models for read/write
- Event handlers updating read models

**Business Analysis Implications:**
- Commands = user actions that change state
- Queries = information users need
- Clear separation of capabilities

## Domain Patterns

### Entity
Core business object with identity.

```csharp
public class Order
{
    public Guid Id { get; }
    public OrderStatus Status { get; private set; }
    public List<OrderItem> Items { get; }
}
```

**Business Analysis Implications:**
- Entities = nouns in business vocabulary
- Properties = data attributes to document
- Methods = business operations/rules

### Value Object
Immutable object defined by attributes.

```csharp
public record Money(decimal Amount, string Currency);
public record Address(string Street, string City, string PostalCode);
```

**Business Analysis Implications:**
- Value objects = complex attributes
- Immutability = business constraint
- Often represent measurable concepts

### Aggregate
Cluster of entities with consistency boundary.

```csharp
public class Order  // Aggregate Root
{
    private List<OrderItem> _items;

    public void AddItem(Product product, int quantity)
    {
        // Business rules enforced here
    }
}
```

**Business Analysis Implications:**
- Aggregate root = transaction boundary
- Internal entities managed through root
- Business rules enforced at aggregate level

### Repository
Data access abstraction.

```csharp
public interface IOrderRepository
{
    Task<Order> GetById(Guid id);
    Task Save(Order order);
}
```

**Business Analysis Implications:**
- Shows what data operations exist
- Query methods reveal reporting needs
- Save patterns show persistence requirements

### Domain Service
Business logic that doesn't belong to entity.

```csharp
public class PricingService
{
    public decimal CalculateDiscount(Order order, Customer customer)
    {
        // Cross-entity business logic
    }
}
```

**Business Analysis Implications:**
- Complex business rules spanning entities
- Calculations and algorithms
- Policy implementations

### Domain Events
Records of something that happened.

```csharp
public class OrderPlacedEvent
{
    public Guid OrderId { get; }
    public DateTime PlacedAt { get; }
    public decimal Total { get; }
}
```

**Business Analysis Implications:**
- Significant business occurrences
- Triggers for side effects
- Audit and compliance relevant

## State Patterns

### State Machine
Explicit state transitions.

```csharp
public enum OrderStatus
{
    Draft,
    Submitted,
    Approved,
    Shipped,
    Delivered,
    Cancelled
}

// Valid transitions
// Draft → Submitted
// Submitted → Approved | Cancelled
// Approved → Shipped | Cancelled
// Shipped → Delivered
```

**Business Analysis Implications:**
- Document all valid states
- Document valid transitions
- Document conditions for transitions
- Map to business workflows

### Workflow / Saga
Long-running business process.

```csharp
public class OrderFulfillmentSaga
{
    public void Handle(OrderPlaced event)
    {
        // Step 1: Reserve inventory
        // Step 2: Charge payment
        // Step 3: Ship order
    }
}
```

**Business Analysis Implications:**
- Multi-step business processes
- Compensation logic (rollback)
- External system coordination

## Validation Patterns

### Attribute-Based Validation
```csharp
public class CreateOrderRequest
{
    [Required]
    public Guid CustomerId { get; set; }

    [Range(1, 100)]
    public int Quantity { get; set; }

    [StringLength(500)]
    public string Notes { get; set; }
}
```

### Specification Pattern
```csharp
public class OrderCanBeSubmittedSpec : ISpecification<Order>
{
    public bool IsSatisfiedBy(Order order)
    {
        return order.Items.Any()
            && order.Total > 0
            && order.Customer.HasValidPayment;
    }
}
```

### Fluent Validation
```csharp
public class OrderValidator : AbstractValidator<Order>
{
    public OrderValidator()
    {
        RuleFor(o => o.Items).NotEmpty()
            .WithMessage("Order must have items");
        RuleFor(o => o.Total).GreaterThan(0);
    }
}
```

**Business Analysis Implications:**
- Each validation rule = business requirement
- Error messages = business language
- Conditions = business constraints

## Integration Patterns

### API Gateway
Central entry point for services.

**Business Analysis Implications:**
- Single view of system capabilities
- Cross-cutting concerns (auth, rate limiting)
- API versioning strategy

### Message Queue
Asynchronous communication.

**Business Analysis Implications:**
- Eventual consistency trade-offs
- Retry and dead-letter handling
- Message ordering requirements

### Anti-Corruption Layer
Translation between contexts.

```csharp
public class LegacyOrderAdapter
{
    public Order TranslateFromLegacy(LegacyOrder legacy)
    {
        // Map legacy format to new domain model
    }
}
```

**Business Analysis Implications:**
- Integration with legacy systems
- Data transformation rules
- Boundary between contexts

## Security Patterns

### Role-Based Access Control (RBAC)
```csharp
[Authorize(Roles = "Admin,Manager")]
public async Task<IActionResult> ApproveOrder(...)
```

### Policy-Based Authorization
```csharp
[Authorize(Policy = "CanApproveOrders")]
```

### Claims-Based Identity
```csharp
if (User.HasClaim("Department", "Sales"))
{
    // Allow access to sales data
}
```

**Business Analysis Implications:**
- Who can do what (authorization matrix)
- Role definitions and permissions
- Compliance requirements

## Pattern Detection Checklist

When analyzing code, look for:

- [ ] **Project Structure**: What architectural pattern is used?
- [ ] **Entities**: What are the core domain objects?
- [ ] **Value Objects**: What complex attributes exist?
- [ ] **Aggregates**: What are the consistency boundaries?
- [ ] **Services**: Where is business logic concentrated?
- [ ] **Events**: What significant things happen?
- [ ] **States**: What lifecycle states exist?
- [ ] **Workflows**: What multi-step processes exist?
- [ ] **Validations**: What business rules are enforced?
- [ ] **Integrations**: What external systems are involved?
- [ ] **Security**: Who can do what?
