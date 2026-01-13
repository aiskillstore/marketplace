# Comprehensive Software Pattern Catalog

A comprehensive reference guide for identifying and analyzing software patterns in codebases.

## Table of Contents

1. [Design Patterns (GoF)](#design-patterns-gof)
2. [Architectural Patterns](#architectural-patterns)
3. [Concurrency Patterns](#concurrency-patterns)
4. [Data Patterns](#data-patterns)
5. [API Patterns](#api-patterns)
6. [Frontend Patterns](#frontend-patterns)
7. [Testing Patterns](#testing-patterns)
8. [Anti-Patterns](#anti-patterns)

---

## Design Patterns (GoF)

### Creational Patterns

#### Factory Pattern
**Purpose**: Create objects without specifying exact class

**Identifying Signatures**:
- Methods named `create*`, `make*`, `build*`, `new*`
- Classes ending in `Factory`, `Creator`, `Builder`
- Switch/if statements determining object type
- Returns interface/abstract class instance

**Code Example**:
```typescript
class UserFactory {
  createUser(type: string): User {
    switch(type) {
      case 'admin': return new AdminUser();
      case 'guest': return new GuestUser();
      default: return new RegularUser();
    }
  }
}
```

**When to Use**: Multiple object types with shared interface, complex creation logic

---

#### Singleton Pattern
**Purpose**: Ensure single instance of a class

**Identifying Signatures**:
- Private constructor
- Static `getInstance()` method
- Static private instance variable
- Classes named `*Manager`, `*Service`, `*Controller` (often)

**Code Example**:
```typescript
class DatabaseConnection {
  private static instance: DatabaseConnection;
  private constructor() {}

  static getInstance(): DatabaseConnection {
    if (!this.instance) {
      this.instance = new DatabaseConnection();
    }
    return this.instance;
  }
}
```

**When to Use**: Shared resources (DB connections, config, logging)

**Anti-Pattern Warning**: Can make testing difficult, consider dependency injection instead

---

#### Builder Pattern
**Purpose**: Construct complex objects step-by-step

**Identifying Signatures**:
- Fluent interface (method chaining)
- Classes ending in `Builder`
- Methods returning `this` or `self`
- Final `build()` method

**Code Example**:
```typescript
class QueryBuilder {
  private query = {};

  select(fields: string[]): this {
    this.query.select = fields;
    return this;
  }

  where(condition: object): this {
    this.query.where = condition;
    return this;
  }

  build(): Query {
    return new Query(this.query);
  }
}

// Usage: new QueryBuilder().select(['id']).where({active: true}).build()
```

**When to Use**: Complex object construction, many optional parameters, readable API

---

#### Prototype Pattern
**Purpose**: Clone objects instead of creating new ones

**Identifying Signatures**:
- `clone()` method
- `Object.create()` usage
- Deep/shallow copy implementations

**Code Example**:
```typescript
class ComponentPrototype {
  clone(): ComponentPrototype {
    return Object.create(this);
  }
}
```

**When to Use**: Expensive object initialization, need for object templates

---

### Structural Patterns

#### Adapter Pattern
**Purpose**: Make incompatible interfaces work together

**Identifying Signatures**:
- Classes ending in `Adapter`, `Wrapper`
- Interface translation/mapping
- Legacy system integration

**Code Example**:
```typescript
class LegacyAPI {
  fetchData(): OldFormat { /* ... */ }
}

class ModernAPIAdapter implements ModernAPI {
  constructor(private legacy: LegacyAPI) {}

  getData(): NewFormat {
    const oldData = this.legacy.fetchData();
    return this.convertToNewFormat(oldData);
  }
}
```

**When to Use**: Integrating third-party libraries, legacy code migration

---

#### Decorator Pattern
**Purpose**: Add behavior to objects dynamically

**Identifying Signatures**:
- Wrapper classes
- Classes implementing same interface as wrapped object
- TypeScript/Python decorators (`@decorator`)
- Middleware chains

**Code Example**:
```typescript
// Function decorator
function log(target: any, key: string, descriptor: PropertyDescriptor) {
  const original = descriptor.value;
  descriptor.value = function(...args: any[]) {
    console.log(`Calling ${key} with`, args);
    return original.apply(this, args);
  };
}

class Service {
  @log
  fetchData() { /* ... */ }
}
```

**When to Use**: Adding cross-cutting concerns (logging, caching, validation)

---

#### Facade Pattern
**Purpose**: Simplified interface to complex subsystem

**Identifying Signatures**:
- Classes named `*Facade`, `*Service`, `*Manager`
- Single entry point coordinating multiple subsystems
- Simplified API hiding complexity

**Code Example**:
```typescript
class PaymentFacade {
  constructor(
    private auth: AuthService,
    private validation: ValidationService,
    private processor: PaymentProcessor,
    private logger: Logger
  ) {}

  processPayment(payment: Payment): Result {
    this.auth.verify(payment.user);
    this.validation.validate(payment);
    const result = this.processor.process(payment);
    this.logger.log(result);
    return result;
  }
}
```

**When to Use**: Complex system with many interdependencies, need simple API

---

#### Proxy Pattern
**Purpose**: Control access to another object

**Identifying Signatures**:
- Classes named `*Proxy`
- Lazy loading implementations
- Access control/validation before delegation
- Caching layer

**Code Example**:
```typescript
class ImageProxy implements Image {
  private realImage: RealImage | null = null;

  display() {
    if (!this.realImage) {
      this.realImage = new RealImage(); // Lazy load
    }
    this.realImage.display();
  }
}
```

**When to Use**: Lazy loading, access control, caching, remote objects

---

### Behavioral Patterns

#### Observer Pattern
**Purpose**: Notify multiple objects of state changes

**Identifying Signatures**:
- `subscribe()`, `unsubscribe()`, `notify()` methods
- Event emitters/listeners
- Pub/Sub implementations
- RxJS observables

**Code Example**:
```typescript
class EventEmitter {
  private listeners = new Map<string, Function[]>();

  on(event: string, callback: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  emit(event: string, data: any) {
    this.listeners.get(event)?.forEach(cb => cb(data));
  }
}
```

**When to Use**: Event-driven systems, reactive programming, UI updates

---

#### Strategy Pattern
**Purpose**: Select algorithm at runtime

**Identifying Signatures**:
- Interface with multiple implementations
- Strategy injection via constructor/setter
- Polymorphic behavior

**Code Example**:
```typescript
interface SortStrategy {
  sort(data: number[]): number[];
}

class QuickSort implements SortStrategy { /* ... */ }
class MergeSort implements SortStrategy { /* ... */ }

class Sorter {
  constructor(private strategy: SortStrategy) {}

  sort(data: number[]) {
    return this.strategy.sort(data);
  }
}
```

**When to Use**: Multiple algorithms for same task, runtime algorithm selection

---

#### Command Pattern
**Purpose**: Encapsulate requests as objects

**Identifying Signatures**:
- `execute()`, `undo()` methods
- Command queue/history
- Classes ending in `Command`, `Action`

**Code Example**:
```typescript
interface Command {
  execute(): void;
  undo(): void;
}

class CopyCommand implements Command {
  constructor(private editor: Editor) {}

  execute() {
    this.editor.copy();
  }

  undo() {
    // Undo logic
  }
}

class CommandHistory {
  private history: Command[] = [];

  execute(cmd: Command) {
    cmd.execute();
    this.history.push(cmd);
  }

  undo() {
    this.history.pop()?.undo();
  }
}
```

**When to Use**: Undo/redo, transaction systems, macro recording

---

#### Template Method Pattern
**Purpose**: Define algorithm skeleton, let subclasses override steps

**Identifying Signatures**:
- Abstract base class with template method
- Protected/abstract hook methods
- Subclasses override specific steps

**Code Example**:
```typescript
abstract class DataProcessor {
  process() {
    const data = this.fetchData();
    const validated = this.validate(data);
    const transformed = this.transform(validated);
    this.save(transformed);
  }

  abstract fetchData(): any;
  abstract validate(data: any): any;
  abstract transform(data: any): any;
  abstract save(data: any): void;
}

class CSVProcessor extends DataProcessor {
  fetchData() { /* CSV-specific */ }
  validate(data: any) { /* CSV validation */ }
  // ...
}
```

**When to Use**: Common algorithm with varying steps, framework hooks

---

#### State Pattern
**Purpose**: Change object behavior based on internal state

**Identifying Signatures**:
- State classes/objects
- Context object delegating to state
- State transitions
- Finite state machines

**Code Example**:
```typescript
interface State {
  handle(context: Context): void;
}

class Context {
  private state: State;

  setState(state: State) {
    this.state = state;
  }

  request() {
    this.state.handle(this);
  }
}
```

**When to Use**: Complex state-dependent behavior, state machines

---

## Architectural Patterns

### MVC (Model-View-Controller)
**Purpose**: Separate data, presentation, and control logic

**Identifying Signatures**:
- Directories: `models/`, `views/`, `controllers/`
- Model: Data and business logic
- View: Presentation layer
- Controller: Request handling and coordination

**Structure**:
```
app/
├── models/
│   └── User.ts          # Data + business logic
├── views/
│   └── UserView.tsx     # Presentation
└── controllers/
    └── UserController.ts # Request handling
```

**When to Use**: Traditional web apps, server-rendered applications

---

### MVVM (Model-View-ViewModel)
**Purpose**: Separate presentation logic from UI

**Identifying Signatures**:
- Two-way data binding
- ViewModel mediating between View and Model
- Common in Angular, Vue, WPF

**Structure**:
```typescript
// Model
class User { /* data */ }

// ViewModel
class UserViewModel {
  user = new Observable<User>();

  get fullName() {
    return `${this.user.firstName} ${this.user.lastName}`;
  }

  saveUser() {
    // Business logic
  }
}

// View binds to ViewModel
<template>
  <div>{{ viewModel.fullName }}</div>
  <button @click="viewModel.saveUser">Save</button>
</template>
```

**When to Use**: Rich client apps, data binding, reactive UIs

---

### Repository Pattern
**Purpose**: Abstract data access logic

**Identifying Signatures**:
- Classes ending in `Repository`
- CRUD methods: `find()`, `save()`, `delete()`, `update()`
- Abstraction over data source (DB, API, cache)

**Code Example**:
```typescript
interface UserRepository {
  findById(id: string): Promise<User>;
  save(user: User): Promise<void>;
  delete(id: string): Promise<void>;
  findAll(): Promise<User[]>;
}

class DatabaseUserRepository implements UserRepository {
  constructor(private db: Database) {}

  async findById(id: string): Promise<User> {
    return this.db.query('SELECT * FROM users WHERE id = ?', [id]);
  }
  // ...
}
```

**When to Use**: Database abstraction, testability, multiple data sources

---

### Service Layer Pattern
**Purpose**: Encapsulate business logic

**Identifying Signatures**:
- Classes ending in `Service`
- Business operations
- Coordinates repositories and other services

**Code Example**:
```typescript
class UserService {
  constructor(
    private userRepo: UserRepository,
    private emailService: EmailService
  ) {}

  async registerUser(data: RegisterData): Promise<User> {
    const user = await this.userRepo.create(data);
    await this.emailService.sendWelcome(user.email);
    return user;
  }
}
```

**When to Use**: Complex business logic, coordinating multiple operations

---

### Microservices Architecture
**Purpose**: Independent, loosely-coupled services

**Identifying Signatures**:
- Multiple deployable services
- API gateways
- Service discovery
- Inter-service communication (REST, gRPC, message queues)

**Structure**:
```
services/
├── auth-service/
├── user-service/
├── payment-service/
└── api-gateway/
```

**When to Use**: Large systems, independent scaling, polyglot architecture

---

### Layered Architecture
**Purpose**: Organize code into horizontal layers

**Identifying Signatures**:
- Clear layer separation
- Dependencies flow downward
- Common layers: Presentation, Business, Persistence, Database

**Structure**:
```
src/
├── presentation/    # Controllers, Routes
├── business/        # Services, Business Logic
├── persistence/     # Repositories, Data Access
└── domain/          # Models, Entities
```

**When to Use**: Traditional enterprise apps, clear separation of concerns

---

### Hexagonal Architecture (Ports & Adapters)
**Purpose**: Isolate business logic from external concerns

**Identifying Signatures**:
- Core domain logic independent
- Ports (interfaces) define boundaries
- Adapters implement ports for external systems

**Structure**:
```
src/
├── domain/          # Pure business logic
├── ports/           # Interfaces
│   ├── inbound/     # Use cases
│   └── outbound/    # Data access
└── adapters/
    ├── api/         # HTTP adapter
    ├── database/    # DB adapter
    └── queue/       # Message queue adapter
```

**When to Use**: DDD, testability, framework independence

---

## Concurrency Patterns

### Producer-Consumer
**Purpose**: Decouple production and consumption of data

**Identifying Signatures**:
- Queue or buffer between producers and consumers
- Async processing
- Worker pools

**Code Example**:
```typescript
class TaskQueue {
  private queue: Task[] = [];

  produce(task: Task) {
    this.queue.push(task);
  }

  consume(): Task | undefined {
    return this.queue.shift();
  }
}

class Worker {
  constructor(private queue: TaskQueue) {}

  async run() {
    while (true) {
      const task = this.queue.consume();
      if (task) await task.execute();
    }
  }
}
```

**When to Use**: Background jobs, rate limiting, load balancing

---

### Promise/Future Pattern
**Purpose**: Handle asynchronous results

**Identifying Signatures**:
- `async`/`await` keywords
- Promise chains: `.then()`, `.catch()`
- Futures, Deferred objects

**When to Use**: Async I/O, non-blocking operations

---

### Circuit Breaker
**Purpose**: Prevent cascading failures

**Identifying Signatures**:
- State tracking (closed, open, half-open)
- Failure threshold monitoring
- Automatic retry logic
- Fallback mechanisms

**Code Example**:
```typescript
class CircuitBreaker {
  private failures = 0;
  private state: 'closed' | 'open' | 'half-open' = 'closed';

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === 'open') {
      throw new Error('Circuit breaker is open');
    }

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  private onFailure() {
    this.failures++;
    if (this.failures >= 5) {
      this.state = 'open';
      setTimeout(() => this.state = 'half-open', 60000);
    }
  }
}
```

**When to Use**: Distributed systems, external API calls, resilience

---

## Data Patterns

### Active Record
**Purpose**: Object that wraps database row and includes CRUD

**Identifying Signatures**:
- Model classes with `save()`, `update()`, `delete()` methods
- Direct database operations on model instances
- Common in Rails, Laravel

**Code Example**:
```typescript
class User extends ActiveRecord {
  id: number;
  name: string;

  async save(): Promise<void> {
    if (this.id) {
      await db.update('users', this.id, this);
    } else {
      this.id = await db.insert('users', this);
    }
  }

  async delete(): Promise<void> {
    await db.delete('users', this.id);
  }
}

// Usage
const user = new User();
user.name = 'John';
await user.save();
```

**When to Use**: Simple CRUD apps, rapid development

---

### Data Mapper
**Purpose**: Separate objects from database persistence

**Identifying Signatures**:
- Separate mapper classes
- POJOs/POCOs (plain objects)
- Common in Hibernate, TypeORM

**Code Example**:
```typescript
// Plain object
class User {
  id: number;
  name: string;
}

// Mapper
class UserMapper {
  async save(user: User): Promise<void> {
    await db.insert('users', user);
  }

  async findById(id: number): Promise<User> {
    const row = await db.query('SELECT * FROM users WHERE id = ?', [id]);
    return this.mapToObject(row);
  }
}
```

**When to Use**: Complex domain models, persistence independence

---

### Unit of Work
**Purpose**: Track changes and persist in a single transaction

**Identifying Signatures**:
- Change tracking
- Batch operations
- Transaction management
- Common in ORMs

**Code Example**:
```typescript
class UnitOfWork {
  private new: Set<Entity> = new Set();
  private dirty: Set<Entity> = new Set();
  private removed: Set<Entity> = new Set();

  registerNew(entity: Entity) {
    this.new.add(entity);
  }

  registerDirty(entity: Entity) {
    this.dirty.add(entity);
  }

  async commit() {
    await db.transaction(async (tx) => {
      for (const entity of this.new) await tx.insert(entity);
      for (const entity of this.dirty) await tx.update(entity);
      for (const entity of this.removed) await tx.delete(entity);
    });
  }
}
```

**When to Use**: Complex transactions, performance optimization

---

## API Patterns

### RESTful API
**Purpose**: Resource-based HTTP API design

**Identifying Signatures**:
- HTTP verbs: GET, POST, PUT, DELETE
- Resource URLs: `/users`, `/users/123`
- Stateless communication
- JSON/XML responses

**When to Use**: Public APIs, simple CRUD, HTTP-based systems

---

### GraphQL
**Purpose**: Query language for flexible API access

**Identifying Signatures**:
- Schema definitions
- Queries, mutations, subscriptions
- Single endpoint
- Client-specified data shape

**When to Use**: Complex data requirements, mobile apps, flexible queries

---

### Backend for Frontend (BFF)
**Purpose**: Specialized backend for each frontend

**Identifying Signatures**:
- Multiple backend services for different clients
- Tailored APIs (mobile-api, web-api)
- Aggregation layer

**When to Use**: Multiple client types, different data needs

---

## Frontend Patterns

### Component-Based Architecture
**Purpose**: Reusable, encapsulated UI components

**Identifying Signatures**:
- Component files (`.jsx`, `.tsx`, `.vue`)
- Props/inputs and events/outputs
- Composition over inheritance
- Common in React, Vue, Angular

**When to Use**: Modern web apps, reusable UI

---

### Atomic Design
**Purpose**: Hierarchical component organization

**Identifying Signatures**:
- Directories: `atoms/`, `molecules/`, `organisms/`, `templates/`, `pages/`
- Bottom-up composition

**Structure**:
```
components/
├── atoms/        # Button, Input, Label
├── molecules/    # FormField (Label + Input)
├── organisms/    # LoginForm (multiple molecules)
├── templates/    # Page layout
└── pages/        # Actual pages
```

**When to Use**: Design systems, large-scale frontends

---

### Container/Presenter Pattern
**Purpose**: Separate logic from presentation

**Identifying Signatures**:
- Container components (smart, stateful)
- Presenter components (dumb, stateless)
- Also called Smart/Dumb, Stateful/Stateless

**Code Example**:
```typescript
// Container (smart)
function UserContainer() {
  const [user, setUser] = useState<User>();

  useEffect(() => {
    fetchUser().then(setUser);
  }, []);

  return <UserPresenter user={user} />;
}

// Presenter (dumb)
function UserPresenter({ user }: { user: User }) {
  return <div>{user.name}</div>;
}
```

**When to Use**: Testability, reusability, separation of concerns

---

### Render Props
**Purpose**: Share code between components using props

**Identifying Signatures**:
- Component accepts function as prop
- Function returns React elements

**Code Example**:
```typescript
function DataFetcher({ render }: { render: (data: any) => JSX.Element }) {
  const [data, setData] = useState();

  useEffect(() => {
    fetchData().then(setData);
  }, []);

  return render(data);
}

// Usage
<DataFetcher render={(data) => <div>{data}</div>} />
```

**When to Use**: Sharing stateful logic, flexible composition

---

## Testing Patterns

### Test Doubles
**Purpose**: Replace dependencies in tests

**Types**:
- **Dummy**: Placeholder, never used
- **Stub**: Returns predefined responses
- **Spy**: Records calls for verification
- **Mock**: Pre-programmed expectations
- **Fake**: Working implementation (simpler)

**Code Example**:
```typescript
// Stub
class StubUserRepository implements UserRepository {
  async findById(id: string): Promise<User> {
    return { id, name: 'Test User' };
  }
}

// Mock
const mockRepo = {
  findById: jest.fn().mockResolvedValue({ id: '1', name: 'Test' })
};

// Usage
test('user service', async () => {
  const service = new UserService(mockRepo);
  const user = await service.getUser('1');

  expect(mockRepo.findById).toHaveBeenCalledWith('1');
  expect(user.name).toBe('Test');
});
```

**When to Use**: Unit testing, isolating code under test

---

### AAA Pattern (Arrange-Act-Assert)
**Purpose**: Structure test cases clearly

**Code Example**:
```typescript
test('user registration', async () => {
  // Arrange
  const userData = { email: 'test@example.com', password: 'pass123' };
  const service = new UserService(mockRepo, mockEmailer);

  // Act
  const user = await service.register(userData);

  // Assert
  expect(user.id).toBeDefined();
  expect(mockEmailer.send).toHaveBeenCalled();
});
```

**When to Use**: All unit tests for clarity and consistency

---

### Test Pyramid
**Purpose**: Balance test types

**Structure**:
```
      /\
     /E2E\       (Few, slow, expensive)
    /------\
   /  API   \    (Medium quantity, medium speed)
  /----------\
 /   Unit     \  (Many, fast, cheap)
/--------------\
```

**Guidelines**:
- **Unit**: 70% - Fast, isolated, many
- **Integration/API**: 20% - Medium speed, test interactions
- **E2E/UI**: 10% - Slow, full user flows, few

**When to Use**: Comprehensive test strategy

---

## Anti-Patterns

### God Object
**Problem**: One class does too much

**Identifying Signatures**:
- Huge classes (thousands of lines)
- Many responsibilities
- Names like `Manager`, `Helper`, `Util`

**Solution**: Apply Single Responsibility Principle, extract classes

---

### Spaghetti Code
**Problem**: No clear structure, tangled dependencies

**Identifying Signatures**:
- Long methods (100+ lines)
- Deep nesting (5+ levels)
- No clear organization
- Goto statements (in languages that have them)

**Solution**: Refactor into smaller functions, use design patterns

---

### Magic Numbers/Strings
**Problem**: Hardcoded values without explanation

**Code Example**:
```typescript
// Bad
if (user.status === 2) { /* ... */ }

// Good
const USER_STATUS_ACTIVE = 2;
if (user.status === USER_STATUS_ACTIVE) { /* ... */ }

// Better
enum UserStatus { ACTIVE = 2, INACTIVE = 1 }
if (user.status === UserStatus.ACTIVE) { /* ... */ }
```

**Solution**: Use named constants, enums, configuration

---

### Premature Optimization
**Problem**: Optimizing before measuring

**Quote**: "Premature optimization is the root of all evil" - Donald Knuth

**Solution**: Profile first, optimize bottlenecks, keep it simple

---

### Copy-Paste Programming
**Problem**: Duplicate code instead of abstraction

**Solution**: DRY (Don't Repeat Yourself), extract functions/classes

---

### Golden Hammer
**Problem**: Using one tool/pattern for everything

**Example**: Using OOP for everything, even simple scripts

**Solution**: Choose appropriate tools for each problem

---

### Circular Dependencies
**Problem**: A depends on B depends on A

**Solution**: Introduce interfaces, inversion of control, refactor dependencies

---

## How to Use This Catalog

### During Investigation
1. **Search for keywords**: Look for pattern-related names (Factory, Observer, etc.)
2. **Identify structure**: Match code structure to pattern signatures
3. **Verify intent**: Ensure pattern serves its intended purpose

### Pattern Recognition Process
1. **Scan for signatures**: Look for identifying characteristics
2. **Examine intent**: Why was this pattern chosen?
3. **Check implementation**: Is it implemented correctly?
4. **Note variations**: Document deviations from standard pattern

### Reporting Patterns
When documenting patterns found:
- **Name**: What pattern is it?
- **Location**: File and line references
- **Purpose**: Why is it used here?
- **Quality**: Well-implemented or problematic?
- **Impact**: How does it affect the codebase?

---

**Last Updated**: 2025-01-15
**Version**: 1.0.0
