# C4 Level Guidelines

Detailed guidance for each C4 abstraction level.

## Level 1: System Context

### Purpose

Show the big picture - the system in its environment.

### Include

- The system being documented (as a single box)
- Users/actors who interact with the system
- External systems the system depends on
- High-level relationships

### Exclude

- Internal details of the system
- Technical implementation choices
- Databases (unless external)
- Queues, caches, internal services

### Audience

Everyone - technical and non-technical stakeholders

### Element Count

5-10 elements maximum

### Example Elements

```
Person: End User, Admin, External Partner
System: Your System (center)
System_Ext: Payment Gateway, Email Service, Auth Provider
```

### Common Mistakes

| Mistake | Fix |
|---------|-----|
| Showing databases | Save for Level 2 |
| Including internal services | Save for Level 2 |
| Too many actors | Group similar users |
| No external systems | Every system has dependencies |

---

## Level 2: Container

### Purpose

Zoom into the system to show major runtime components.

### Include

- Applications (web, mobile, desktop)
- APIs and services
- Databases and data stores
- Message queues and event buses
- File systems
- Technology choices for each

### Exclude

- Internal structure of containers
- Classes and functions
- Detailed data models
- Implementation specifics

### Audience

Technical stakeholders, architects, developers

### Element Count

10-15 elements per system

### Example Elements

```
Container: Web App (React), API Server (Node.js), Worker (Python)
ContainerDb: PostgreSQL, Redis, MongoDB
ContainerQueue: RabbitMQ, Kafka
System_Ext: External APIs
```

### Common Mistakes

| Mistake | Fix |
|---------|-----|
| Showing modules | Save for Level 3 |
| Missing technology | Always specify tech stack |
| No database | Most systems have data storage |
| Unlabeled relationships | Add "Calls", "Reads/Writes", etc. |

---

## Level 3: Component

### Purpose

Zoom into a container to show its internal building blocks.

### Include

- Major modules or packages
- Services and their responsibilities
- Repositories and data access layers
- External integrations
- Key abstractions and interfaces

### Exclude

- Individual classes (unless architecturally significant)
- Function implementations
- Detailed algorithms
- All helper/utility code

### Audience

Developers working on that container

### Element Count

10-20 elements per container

### Example Elements

```
Component: AuthService, UserRepository, PaymentGateway
Component: RouteHandler, Middleware, Validator
```

### Common Mistakes

| Mistake | Fix |
|---------|-----|
| Too granular | Focus on major modules only |
| Missing boundaries | Group related components |
| No responsibilities | Add description of purpose |

---

## Level 4: Code

### Purpose

Show implementation details for critical areas only.

### Include

- Class diagrams for key abstractions
- Interface definitions
- Critical algorithms
- Complex data structures

### When to Use

- Complex business logic
- Critical performance paths
- Key design patterns
- Areas requiring documentation

### When NOT to Use

- Standard CRUD operations
- Simple utilities
- Self-explanatory code
- Frequently changing code

### Audience

Developers implementing or maintaining the code

### Common Mistakes

| Mistake | Fix |
|---------|-----|
| Diagramming everything | Only critical code |
| Outdated diagrams | Code changes faster than docs |
| No clear purpose | State why this needs a diagram |

---

## Transitioning Between Levels

### From Context to Container

1. Take one system box from context
2. Expand to show internal containers
3. Keep external systems for context
4. Add technology choices

### From Container to Component

1. Take one container from Level 2
2. Expand to show internal modules
3. Show how components connect to other containers
4. Add responsibilities

### From Component to Code

1. Select critical component
2. Show only if complexity warrants it
3. Focus on interfaces and key classes
4. Keep synchronized with code

---

## Diagram Review Checklist

- [ ] Is the level appropriate for the audience?
- [ ] Are abstraction levels not mixed?
- [ ] Do all elements have descriptions?
- [ ] Are relationships labeled?
- [ ] Is technology specified (Level 2+)?
- [ ] Is element count reasonable?
- [ ] Are boundaries clearly defined?
