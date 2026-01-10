---
name: solid-principles
description: SOLID object-oriented design principles for maintainable code
---

# SOLID Principles

Five principles for object-oriented design that lead to maintainable, extensible software.

## S - Single Responsibility Principle

> A class should have only one reason to change.

```typescript
// BAD - multiple responsibilities
class UserService {
  createUser(data: UserData) { /* ... */ }
  sendEmail(user: User, message: string) { /* ... */ }
  generateReport(users: User[]) { /* ... */ }
  validateEmail(email: string) { /* ... */ }
}

// GOOD - single responsibility each
class UserService {
  constructor(
    private repository: UserRepository,
    private validator: UserValidator
  ) {}

  createUser(data: UserData): User {
    this.validator.validate(data);
    return this.repository.save(data);
  }
}

class EmailService {
  send(to: string, message: string) { /* ... */ }
}

class UserReportGenerator {
  generate(users: User[]): Report { /* ... */ }
}

class EmailValidator {
  validate(email: string): boolean { /* ... */ }
}
```

**When to apply:** If you describe a class with "and" (UserService creates users AND sends emails AND...), split it.

## O - Open/Closed Principle

> Open for extension, closed for modification.

```typescript
// BAD - must modify class to add new types
class PaymentProcessor {
  process(payment: Payment) {
    if (payment.type === 'credit') {
      // process credit card
    } else if (payment.type === 'paypal') {
      // process PayPal
    } else if (payment.type === 'crypto') {
      // process crypto - had to modify!
    }
  }
}

// GOOD - extend without modification
interface PaymentMethod {
  process(amount: number): Promise<Receipt>;
}

class CreditCardPayment implements PaymentMethod {
  async process(amount: number): Promise<Receipt> {
    // credit card logic
  }
}

class PayPalPayment implements PaymentMethod {
  async process(amount: number): Promise<Receipt> {
    // PayPal logic
  }
}

// Adding crypto doesn't modify existing code
class CryptoPayment implements PaymentMethod {
  async process(amount: number): Promise<Receipt> {
    // crypto logic
  }
}

class PaymentProcessor {
  process(method: PaymentMethod, amount: number) {
    return method.process(amount);
  }
}
```

**When to apply:** When adding new features requires modifying existing, tested code.

## L - Liskov Substitution Principle

> Subtypes must be substitutable for their base types.

```typescript
// BAD - Square violates Rectangle contract
class Rectangle {
  constructor(protected width: number, protected height: number) {}

  setWidth(width: number) { this.width = width; }
  setHeight(height: number) { this.height = height; }
  getArea() { return this.width * this.height; }
}

class Square extends Rectangle {
  setWidth(width: number) {
    this.width = width;
    this.height = width; // Violates expectation!
  }
  setHeight(height: number) {
    this.width = height;
    this.height = height; // Violates expectation!
  }
}

// This breaks:
function doubleWidth(rect: Rectangle) {
  const originalHeight = rect.getArea() / rect.width;
  rect.setWidth(rect.width * 2);
  // For Square, height also doubled - unexpected!
}

// GOOD - separate hierarchies
interface Shape {
  getArea(): number;
}

class Rectangle implements Shape {
  constructor(private width: number, private height: number) {}
  getArea() { return this.width * this.height; }
}

class Square implements Shape {
  constructor(private side: number) {}
  getArea() { return this.side * this.side; }
}
```

**When to apply:** If subclass overrides change behavior that callers depend on.

## I - Interface Segregation Principle

> Clients should not depend on interfaces they don't use.

```typescript
// BAD - fat interface
interface Worker {
  work(): void;
  eat(): void;
  sleep(): void;
  attendMeeting(): void;
  writeReport(): void;
}

class Robot implements Worker {
  work() { /* ... */ }
  eat() { throw new Error('Robots do not eat'); }  // Forced to implement!
  sleep() { throw new Error('Robots do not sleep'); }
  attendMeeting() { throw new Error('Not applicable'); }
  writeReport() { throw new Error('Not applicable'); }
}

// GOOD - segregated interfaces
interface Workable {
  work(): void;
}

interface Feedable {
  eat(): void;
}

interface Sleepable {
  sleep(): void;
}

interface MeetingAttendee {
  attendMeeting(): void;
}

class Human implements Workable, Feedable, Sleepable, MeetingAttendee {
  work() { /* ... */ }
  eat() { /* ... */ }
  sleep() { /* ... */ }
  attendMeeting() { /* ... */ }
}

class Robot implements Workable {
  work() { /* ... */ }
}
```

**When to apply:** When classes implement methods they don't need, or throw "not implemented" errors.

## D - Dependency Inversion Principle

> Depend on abstractions, not concretions.

```typescript
// BAD - high-level depends on low-level
class MySQLDatabase {
  query(sql: string) { /* ... */ }
}

class UserRepository {
  private db = new MySQLDatabase();  // Tight coupling!

  findById(id: string) {
    return this.db.query(`SELECT * FROM users WHERE id = '${id}'`);
  }
}

// GOOD - both depend on abstraction
interface Database {
  query<T>(sql: string): Promise<T>;
}

class MySQLDatabase implements Database {
  async query<T>(sql: string): Promise<T> { /* ... */ }
}

class PostgreSQLDatabase implements Database {
  async query<T>(sql: string): Promise<T> { /* ... */ }
}

class UserRepository {
  constructor(private db: Database) {}  // Injected!

  findById(id: string) {
    return this.db.query(`SELECT * FROM users WHERE id = '${id}'`);
  }
}

// Easy to swap implementations
const repo = new UserRepository(new PostgreSQLDatabase());
```

**When to apply:** When testing is hard, or changing one module breaks others.

## SOLID in Practice

### Recognizing Violations

| Principle | Code Smell |
|-----------|------------|
| SRP | Class has many unrelated methods |
| OCP | Adding feature requires modifying existing code |
| LSP | Subclass throws "not supported" or behaves differently |
| ISP | Class implements methods it doesn't use |
| DIP | `new` keyword scattered throughout business logic |

### Applying SOLID

1. **Start simple** - Don't over-engineer from day one
2. **Refactor when needed** - Apply when you feel the pain
3. **Use dependency injection** - Makes DIP natural
4. **Prefer composition** - Over inheritance (helps LSP)
5. **Write small interfaces** - Easier than splitting later

### Balance

SOLID is a guide, not law. Over-applying creates:
- Too many tiny classes
- Indirection that's hard to follow
- Abstractions nobody needs yet

Apply SOLID when:
- Code is hard to test
- Changes ripple through the codebase
- Similar changes needed in multiple places
- You're adding the 3rd variation of something

## Checklist

- [ ] Does each class have a single, clear purpose?
- [ ] Can I add features without modifying existing code?
- [ ] Can subclasses replace parent classes safely?
- [ ] Are interfaces focused and minimal?
- [ ] Are dependencies injected, not created internally?
