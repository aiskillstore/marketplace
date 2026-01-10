# Domain-Driven Design (DDD)

## What is Domain-Driven Design?

Domain-Driven Design is a philosophy for building software that truly mirrors the real-world problem domain. It's about aligning code structure and language with how domain experts—business stakeholders, product managers, or domain specialists—actually think and talk about their work.

## Core Concepts

### 1. Ubiquitous Language

Everyone involved speaks the same precise language. If a domain expert says "invoice," the code should have an Invoice entity. If they say "settlement," there shouldn't be three competing terms (Payment, Reconciliation, Transfer). This shared vocabulary collapses the wall between tech and business.

### 2. Bounded Contexts

Large systems are messy. DDD says: don't make one grand "domain model." Instead, divide the system into bounded contexts—self-contained conceptual zones where terms and rules are consistent.

For example:
- The **Billing Context** might define an Invoice differently than the **Accounting Context** does
- Each bounded context can be implemented as its own module, service, or microservice
- Explicit integration contracts exist between contexts

### 3. The Model

Inside each bounded context, your classes, aggregates, and events model real-world behavior—not just data.

**Key DDD Building Blocks:**

- **Entities** — Have an identity over time (Order, User, Account)
- **Value Objects** — Immutable, identity-less values (Money, Email, Coordinates)
- **Aggregates** — Clusters of entities treated as a single consistency boundary (Order + its OrderItems)
- **Domain Services** — Operations that don't belong to any one entity (CurrencyConversionService)
- **Domain Events** — Things that happened and matter to the domain (PaymentReceived, TicketReserved)
- **Repositories** — Domain persistence contracts (not implementation details)

## Why DDD is Suited to AI Code Generation

DDD focuses on a clear domain model using Entities, Value Objects, Domain Services, and Repositories—all expressed in the ubiquitous language of the business. This explicit modeling gives AI agents a well-defined vocabulary and structure to follow.

By avoiding "anemic" models (just data with getters/setters) and placing behavior inside domain objects instead of scattering business logic in controllers or utilities, DDD reduces ambiguity about where logic should go.

In practice, teams have found that **DDD's emphasis on bounded contexts and consistent naming creates a shared vocabulary that an AI can apply reliably in code generation**. As developers report: DDD principles were "extraordinarily effective when working with AI", almost as if the approach was "designed specifically for helping AI understand complex domains."

### How DDD Improves AI Output

By defining the core concepts up front, you guide the AI to use the correct terms and relationships. For example, if you specify that your system has an Order aggregate with an `addLineItem()` method, the AI is less likely to invent a different pattern—it will follow the established method name and entity structure.

The predictability of DDD helps the AI "fill in the blanks" without deviating from intended design. In real-world usage, moving from a loose approach to a DDD-informed approach transformed AI-generated code from "disconnected, non-functional" snippets into "cohesive, working features that integrated properly with the codebase."

## When to Use DDD

DDD thrives when:

- The domain itself is complex and evolving
- You have access to domain experts
- You're building something long-lived, not a quick MVP
- Business rules are nuanced and need to be captured clearly
- Your team values maintainability over speed

It's less ideal for:

- Simple CRUD applications
- Early exploratory projects without stable concepts
- Projects where business requirements are entirely unclear

## TypeScript Example – Domain Model

Below is a simplified example of DDD style in TypeScript:

### Value Object Example

```typescript
/**
 * Email value object
 * Encapsulates email validation and behavior
 */
class Email {
  readonly value: string;

  constructor(value: string) {
    if (!value.includes('@')) {
      throw new Error('Invalid email format');
    }
    this.value = value;
  }

  get domain(): string {
    return this.value.split('@')[1];
  }

  equals(other: Email): boolean {
    return this.value === other.value;
  }
}
```

### Entity Example

```typescript
/**
 * User entity
 * Has identity and lifecycle, contains business behavior
 */
class User {
  private _id: string;
  private _email: Email;
  private _name: string;
  private _createdAt: Date;

  constructor(email: Email, name: string) {
    this._id = generateUniqueId(); // unique identity
    this._email = email;
    this._name = name;
    this._createdAt = new Date();
  }

  /**
   * Business rule: change email with validation
   * This encapsulates business logic in the domain
   */
  changeEmail(newEmail: Email): void {
    if (!this.isEmailDomainAllowed(newEmail)) {
      throw new Error('Email domain not allowed for this user type');
    }
    this._email = newEmail;
  }

  private isEmailDomainAllowed(email: Email): boolean {
    const allowedDomains = ['company.com', 'company-partners.com'];
    return allowedDomains.includes(email.domain);
  }

  get id(): string {
    return this._id;
  }

  get email(): Email {
    return this._email;
  }

  get name(): string {
    return this._name;
  }
}
```

### Repository Interface (Domain Layer)

```typescript
/**
 * UserRepository
 * Domain persistence contract (no infrastructure details)
 */
interface UserRepository {
  findByEmail(email: Email): Promise<User | null>;
  findById(id: string): Promise<User | null>;
  save(user: User): Promise<void>;
  delete(id: string): Promise<void>;
}
```

### Domain Service

```typescript
/**
 * UserRegistrationService
 * Orchestrates the user registration process
 * Belongs to domain, not infrastructure
 */
class UserRegistrationService {
  constructor(
    private userRepository: UserRepository,
    private emailService: EmailService
  ) {}

  async register(email: string, name: string): Promise<User> {
    // Create value object with validation
    const emailVO = new Email(email);

    // Check business rule: no duplicate emails
    const existingUser = await this.userRepository.findByEmail(emailVO);
    if (existingUser) {
      throw new Error('User with this email already exists');
    }

    // Create user entity with behavior
    const newUser = new User(emailVO, name);

    // Persist to repository
    await this.userRepository.save(newUser);

    // Send domain event (user registered)
    await this.emailService.sendWelcomeEmail(newUser);

    return newUser;
  }
}
```

## DDD vs. Traditional MVC

### Traditional MVC Approach

```typescript
// ❌ Anemic model - just data
class User {
  id: string;
  email: string;
  name: string;
}

// ❌ Business logic scattered in controller
app.post('/register', async (req, res) => {
  const { email, name } = req.body;

  // Validation mixed with persistence
  if (!email.includes('@')) {
    return res.status(400).send('Invalid email');
  }

  // Direct database access
  const existing = await db.query(
    'SELECT * FROM users WHERE email = ?',
    [email]
  );
  if (existing.rows.length > 0) {
    return res.status(400).send('User exists');
  }

  // Insert directly
  const result = await db.query(
    'INSERT INTO users (email, name) VALUES (?, ?)',
    [email, name]
  );

  res.status(201).json({ id: result.lastID, email, name });
});
```

**Problems:**
- Business logic scattered across controller and database code
- Anemic model with no behavior
- Hard to test business rules in isolation
- AI tends to generate similar scattered logic if not guided to DDD

### DDD Approach

```typescript
// ✅ Rich domain model with behavior
class Email {
  constructor(value: string) {
    if (!value.includes('@')) throw new Error('Invalid email');
    this.value = value;
  }
}

class User {
  constructor(email: Email, name: string) {
    this.email = email;
    this.name = name;
  }

  changeEmail(newEmail: Email): void {
    this.email = newEmail; // Business rule encapsulated
  }
}

// ✅ Domain service with clear responsibility
class RegisterUserService {
  constructor(private repo: UserRepository) {}

  async execute(email: string, name: string): Promise<User> {
    const emailVO = new Email(email); // validation
    if (await this.repo.findByEmail(emailVO)) {
      throw new Error('User exists');
    }
    const user = new User(emailVO, name);
    await this.repo.save(user);
    return user;
  }
}

// ✅ Clean controller delegates to domain
app.post('/register', async (req, res) => {
  try {
    const user = await registerService.execute(
      req.body.email,
      req.body.name
    );
    res.status(201).json(user);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});
```

**Benefits:**
- Business logic isolated in domain layer
- Clear, testable entities with behavior
- Repository provides clear persistence contract
- AI naturally reuses patterns and follows established structure

## Domain Events

Domain events capture important occurrences in your domain:

```typescript
/**
 * UserRegistered domain event
 * Signals that a user was successfully registered
 */
interface DomainEvent {
  eventId: string;
  occurredAt: Date;
  aggregateId: string;
  aggregateType: string;
}

class UserRegisteredEvent implements DomainEvent {
  eventId: string;
  occurredAt: Date;
  aggregateId: string;
  aggregateType = 'User';

  constructor(
    public userId: string,
    public email: string,
    public name: string
  ) {
    this.eventId = generateId();
    this.occurredAt = new Date();
    this.aggregateId = userId;
  }
}

// In UserRegistrationService:
async execute(email: string, name: string): Promise<User> {
  const emailVO = new Email(email);
  const user = new User(emailVO, name);
  await this.userRepository.save(user);

  // Publish event
  const event = new UserRegisteredEvent(user.id, email, name);
  await this.eventBus.publish(event);

  return user;
}
```

## File Structure for DDD

```
src/
├── domain/
│   ├── entities/
│   │   ├── User.ts
│   │   ├── Order.ts
│   │   └── Account.ts
│   ├── value-objects/
│   │   ├── Email.ts
│   │   ├── Money.ts
│   │   └── Address.ts
│   ├── services/
│   │   ├── UserRegistrationService.ts
│   │   └── OrderProcessingService.ts
│   ├── repositories/
│   │   ├── UserRepository.ts
│   │   └── OrderRepository.ts
│   └── events/
│       ├── DomainEvent.ts
│       ├── UserRegisteredEvent.ts
│       └── OrderPlacedEvent.ts
├── application/
│   ├── use-cases/
│   │   ├── RegisterUserUseCase.ts
│   │   └── PlaceOrderUseCase.ts
│   └── dto/
│       ├── RegisterUserRequest.ts
│       └── PlaceOrderRequest.ts
├── infrastructure/
│   ├── repositories/
│   │   ├── MongoUserRepository.ts
│   │   └── PostgresOrderRepository.ts
│   ├── events/
│   │   └── KafkaEventBus.ts
│   └── http/
│       └── UserController.ts
└── interfaces/
    └── api/
        ├── UserAPI.ts
        └── OrderAPI.ts
```

## Tips for AI-Generated DDD Code

1. **Define your domain model first** - Show the AI your entities, value objects, and bounded contexts before asking for implementation
2. **Use consistent naming** - Apply ubiquitous language consistently in prompts
3. **Describe business rules** - Explain what the domain does and its constraints
4. **Reference patterns** - Point the AI to existing entities and services as examples
5. **Request by aggregate** - Ask for one aggregate at a time rather than the entire system

## Key Takeaways

- DDD reduces ambiguity for AI through explicit domain modeling
- Business logic lives in domain entities, not scattered across layers
- Value objects enforce business rules at construction time
- Repositories provide clean persistence contracts
- Domain events capture important business occurrences
- The ubiquitous language becomes your shared vocabulary with both humans and AI
