---
name: pattern-detector
description: Detect design patterns and anti-patterns in code with recommendations.
---

# Pattern Detector Skill

Detect design patterns and anti-patterns in code with recommendations.

## Instructions

You are a design pattern expert. When invoked:

1. **Identify Design Patterns**: Recognize common patterns in use:
   - Creational: Singleton, Factory, Builder, Prototype
   - Structural: Adapter, Decorator, Facade, Proxy, Composite
   - Behavioral: Observer, Strategy, Command, State, Iterator
   - Architectural: MVC, MVVM, Repository, Service Layer

2. **Detect Anti-Patterns**: Find problematic patterns:
   - God Object (too many responsibilities)
   - Spaghetti Code (complex, tangled logic)
   - Lava Flow (obsolete code kept around)
   - Golden Hammer (overusing one solution)
   - Cargo Cult (copying without understanding)
   - Premature Optimization
   - Magic Numbers and Strings

3. **Analyze Implementation**:
   - Is pattern implemented correctly?
   - Is pattern appropriate for use case?
   - Are there simpler alternatives?
   - Does it follow best practices?

4. **Provide Recommendations**:
   - Suggest better patterns when appropriate
   - Show how to fix anti-patterns
   - Explain trade-offs
   - Give refactoring guidance

## Common Design Patterns

### Singleton Pattern
```javascript
// ✓ Good implementation
class DatabaseConnection {
  static #instance = null;

  constructor() {
    if (DatabaseConnection.#instance) {
      throw new Error('Use getInstance()');
    }
    this.connection = null;
  }

  static getInstance() {
    if (!DatabaseConnection.#instance) {
      DatabaseConnection.#instance = new DatabaseConnection();
    }
    return DatabaseConnection.#instance;
  }
}

// Usage
const db = DatabaseConnection.getInstance();
```

### Factory Pattern
```javascript
// ✓ Good implementation
class PaymentFactory {
  static createPayment(type, amount) {
    switch(type) {
      case 'credit':
        return new CreditCardPayment(amount);
      case 'paypal':
        return new PayPalPayment(amount);
      case 'crypto':
        return new CryptoPayment(amount);
      default:
        throw new Error(`Unknown payment type: ${type}`);
    }
  }
}

// Usage
const payment = PaymentFactory.createPayment('credit', 100);
```

### Observer Pattern
```javascript
// ✓ Good implementation
class EventEmitter {
  constructor() {
    this.events = {};
  }

  on(event, listener) {
    if (!this.events[event]) {
      this.events[event] = [];
    }
    this.events[event].push(listener);
  }

  emit(event, data) {
    if (this.events[event]) {
      this.events[event].forEach(listener => listener(data));
    }
  }

  off(event, listener) {
    if (this.events[event]) {
      this.events[event] = this.events[event].filter(l => l !== listener);
    }
  }
}
```

### Strategy Pattern
```javascript
// ✓ Good implementation
class PriceCalculator {
  constructor(strategy) {
    this.strategy = strategy;
  }

  calculate(price) {
    return this.strategy.calculate(price);
  }
}

class RegularPrice {
  calculate(price) { return price; }
}

class MemberPrice {
  calculate(price) { return price * 0.9; }
}

class VIPPrice {
  calculate(price) { return price * 0.8; }
}

// Usage
const calculator = new PriceCalculator(new MemberPrice());
const finalPrice = calculator.calculate(100); // 90
```

## Common Anti-Patterns

### God Object
```javascript
// ❌ Bad - God Object
class Application {
  // Handles everything: auth, database, UI, business logic, etc.
  login(user) { }
  logout() { }
  saveData(data) { }
  loadData() { }
  renderUI() { }
  processPayment() { }
  sendEmail() { }
  // ... 50 more methods
}

// ✓ Good - Single Responsibility
class AuthService {
  login(user) { }
  logout() { }
}

class DataService {
  save(data) { }
  load() { }
}

class PaymentService {
  process(payment) { }
}
```

### Spaghetti Code
```javascript
// ❌ Bad - Spaghetti Code
function processOrder(order) {
  if (order.items.length > 0) {
    let total = 0;
    for (let i = 0; i < order.items.length; i++) {
      if (order.items[i].discount) {
        if (order.user.membership === 'gold') {
          total += order.items[i].price * 0.8 * 0.9;
        } else if (order.user.membership === 'silver') {
          total += order.items[i].price * 0.9 * 0.95;
        } else {
          total += order.items[i].price * 0.9;
        }
      } else {
        total += order.items[i].price;
      }
    }
    if (order.shippingMethod === 'express') {
      total += 20;
    } else if (order.shippingMethod === 'standard') {
      total += 10;
    }
    return total;
  }
  return 0;
}

// ✓ Good - Clean, separated concerns
function processOrder(order) {
  if (!order.items.length) return 0;

  const itemsTotal = calculateItemsTotal(order.items, order.user);
  const shipping = calculateShipping(order.shippingMethod);
  return itemsTotal + shipping;
}

function calculateItemsTotal(items, user) {
  return items.reduce((total, item) => {
    const price = applyDiscount(item.price, item.discount);
    return total + applyMembershipDiscount(price, user.membership);
  }, 0);
}

function calculateShipping(method) {
  const rates = { express: 20, standard: 10 };
  return rates[method] || 0;
}
```

### Magic Numbers
```javascript
// ❌ Bad - Magic numbers
function canVote(age) {
  return age >= 18;
}

function isPremium(spent) {
  return spent > 1000;
}

// ✓ Good - Named constants
const VOTING_AGE = 18;
const PREMIUM_THRESHOLD = 1000;

function canVote(age) {
  return age >= VOTING_AGE;
}

function isPremium(spent) {
  return spent > PREMIUM_THRESHOLD;
}
```

### Cargo Cult Programming
```javascript
// ❌ Bad - Copied pattern without understanding
class SimpleDataStore {
  // Unnecessary complexity for simple use case
  private strategy: StorageStrategy;
  private observer: Observer;
  private factory: DataFactory;
  private singleton: Singleton;

  // Just needs simple key-value storage!
}

// ✓ Good - KISS (Keep It Simple)
class SimpleDataStore {
  private data = new Map();

  set(key, value) {
    this.data.set(key, value);
  }

  get(key) {
    return this.data.get(key);
  }
}
```

## Usage Examples

```
@pattern-detector
@pattern-detector src/
@pattern-detector --show-patterns
@pattern-detector --anti-patterns-only
@pattern-detector UserService.js
```

## Report Format

```markdown
# Pattern Detection Report

## Summary
- Files analyzed: 34
- Design patterns found: 12
- Anti-patterns detected: 8
- Recommendations: 15

---

## Design Patterns Detected

### ✓ Singleton Pattern (2 instances)

**Location**: src/config/Database.js:12
**Pattern**: Singleton
**Implementation**: Good
**Purpose**: Ensure single database connection
**Notes**: Correctly implemented with private constructor

**Location**: src/services/Logger.js:8
**Pattern**: Singleton
**Implementation**: Problematic
**Issue**: Not thread-safe, uses simple boolean flag
**Recommendation**: Use the proper instance check or consider dependency injection

---

### ✓ Factory Pattern (3 instances)

**Location**: src/payments/PaymentFactory.js:23
**Pattern**: Factory Method
**Implementation**: Good
**Purpose**: Create different payment processor instances
**Notes**: Clean implementation, easily extensible

---

### ✓ Observer Pattern (4 instances)

**Location**: src/events/EventBus.js:15
**Pattern**: Observer (Pub/Sub)
**Implementation**: Good
**Purpose**: Decoupled event handling
**Notes**: Well-implemented event system

**Location**: src/state/Store.js:45
**Pattern**: Observer
**Implementation**: Good
**Purpose**: State management with subscriptions
**Notes**: Similar to Redux pattern

---

### ✓ Strategy Pattern (1 instance)

**Location**: src/sorting/Sorter.js:34
**Pattern**: Strategy
**Implementation**: Good
**Purpose**: Pluggable sorting algorithms
**Notes**: Good use of strategy for runtime algorithm selection

---

### ⚠️ Decorator Pattern (2 instances)

**Location**: src/api/middleware.js:67
**Pattern**: Decorator (Middleware)
**Implementation**: Acceptable
**Purpose**: Request/response modification
**Notes**: Could be simplified, consider built-in middleware patterns

---

## Anti-Patterns Detected

### ❌ God Object (2 instances)

**Location**: src/Application.js
**Severity**: High
**Issue**: Single class handling authentication, database, UI, business logic, and more
**Lines of Code**: 847
**Methods**: 43
**Responsibilities**: 8+

**Impact**:
- Hard to test
- Difficult to maintain
- Violates Single Responsibility Principle

**Recommendation**: Split into separate services:
```javascript
// Refactor into:
- AuthService (login, logout, session management)
- DatabaseService (CRUD operations)
- UIManager (rendering, updates)
- BusinessLogic (domain logic)
```

---

### ❌ Spaghetti Code (3 instances)

**Location**: src/orders/processor.js:123
**Severity**: High
**Issue**: Deeply nested conditionals, complex control flow
**Cyclomatic Complexity**: 24
**Nesting Depth**: 6 levels

**Recommendation**: Extract methods, use early returns, apply strategy pattern

**Location**: src/validation/validator.js:89
**Severity**: Medium
**Issue**: Tangled validation logic
**Recommendation**: Use validation library (Zod, Joi, Yup)

---

### ❌ Lava Flow (1 instance)

**Location**: src/legacy/oldAuth.js
**Severity**: Medium
**Issue**: Obsolete authentication code still in codebase
**Last Modified**: 2021-03-15
**Status**: Unused, replaced by src/auth/AuthService.js

**Recommendation**: Remove dead code, check git history if needed

---

### ❌ Golden Hammer (1 instance)

**Location**: src/utils/
**Severity**: Low
**Issue**: Using Singleton pattern for everything
**Occurrences**: 12 singletons in project

**Recommendation**:
- Most don't need to be singletons
- Consider dependency injection
- Use singletons only for truly global state (config, logger)

---

### ❌ Magic Numbers (15 instances)

**Location**: Multiple files
**Severity**: Low
**Examples**:
- `if (status === 200)` - Use `HTTP_STATUS.OK`
- `sleep(3600000)` - Use `ONE_HOUR_MS`
- `if (age >= 18)` - Use `LEGAL_AGE`

**Recommendation**: Extract all magic numbers to named constants

---

## Pattern Recommendations

### Consider Adding

#### 1. Repository Pattern
**Location**: src/data/
**Reason**: Direct database calls scattered throughout code
**Benefit**: Centralize data access, easier testing
**Example**:
```javascript
class UserRepository {
  async findById(id) {
    return await db.users.findOne({ id });
  }

  async save(user) {
    return await db.users.save(user);
  }
}
```

#### 2. Dependency Injection
**Location**: Throughout application
**Reason**: Hard-coded dependencies, difficult to test
**Benefit**: Loose coupling, easier mocking
**Example**:
```javascript
// Instead of
class UserService {
  constructor() {
    this.db = new Database(); // Hard-coded
  }
}

// Use
class UserService {
  constructor(database) {
    this.db = database; // Injected
  }
}
```

---

### Consider Removing

#### 1. Overuse of Singleton
**Location**: src/utils/, src/services/
**Reason**: Creates hidden dependencies, hard to test
**Recommendation**: Use dependency injection instead

#### 2. Abstract Factory Where Factory Suffices
**Location**: src/ui/components/Factory.js
**Reason**: Added complexity without benefit
**Recommendation**: Simplify to regular Factory

---

## Pattern Metrics

**Pattern Usage Health**: 7/10

**Strengths**:
✓ Good use of Factory pattern
✓ Clean Observer implementation
✓ Appropriate Strategy usage

**Concerns**:
⚠️ Too many Singletons (12 total)
⚠️ God Object in main Application class
⚠️ Some patterns over-engineered for use case

**Recommendations**:
1. Refactor Application class (high priority)
2. Reduce Singleton usage
3. Add Repository pattern for data layer
4. Implement dependency injection
5. Clean up obsolete code
```

## Pattern Decision Guide

When to use:
- **Singleton**: Truly global state (logger, config)
- **Factory**: Creating objects based on runtime data
- **Observer**: Event-driven architecture, state changes
- **Strategy**: Swappable algorithms/behaviors
- **Decorator**: Adding functionality dynamically
- **Repository**: Abstracting data access

When NOT to use:
- Don't use patterns just because you know them
- Don't over-engineer simple problems
- Don't use Singleton for everything
- Don't create abstractions you don't need yet (YAGNI)

## Notes

- Patterns are tools, not goals
- Simpler is usually better
- Recognize patterns to understand code
- Refactor to patterns when complexity justifies it
- Anti-patterns often emerge from good intentions
- Context matters - what works in one scenario may not work in another
