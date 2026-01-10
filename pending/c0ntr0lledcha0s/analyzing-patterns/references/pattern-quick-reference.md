# Pattern Quick Reference Guide

Fast lookup guide for identifying common software patterns.

## Quick Pattern Identification

### Search Keywords

Search for these keywords in code to identify patterns:

| Pattern | Keywords | Class Names | Method Names |
|---------|----------|-------------|--------------|
| **Factory** | create, make, build | `*Factory`, `*Creator`, `*Builder` | `create*()`, `make*()`, `build*()` |
| **Singleton** | instance, getInstance | `*Manager`, `*Service`, `*Controller` | `getInstance()` |
| **Builder** | builder, build | `*Builder` | `with*()`, `set*()`, `build()` |
| **Observer** | subscribe, notify, listen | `*Observer`, `*Listener`, `EventEmitter` | `on()`, `emit()`, `subscribe()` |
| **Strategy** | strategy, algorithm | `*Strategy`, `*Algorithm` | N/A |
| **Decorator** | @decorator | `*Decorator`, `*Wrapper` | N/A |
| **Adapter** | adapter, wrapper | `*Adapter`, `*Wrapper` | `adapt()`, `wrap()` |
| **Proxy** | proxy, lazy | `*Proxy` | N/A |
| **Repository** | repository, repo | `*Repository`, `*Repo` | `find*()`, `save()`, `delete()` |
| **Service** | service | `*Service` | Business operations |
| **Facade** | facade | `*Facade`, `*Service` | Simplified methods |
| **Command** | command, action, execute | `*Command`, `*Action` | `execute()`, `undo()` |
| **State** | state, transition | `*State`, `*Context` | `setState()`, `handle()` |

---

## Grep Patterns

### Design Patterns

```bash
# Factory Pattern
grep -r "class.*Factory\|function.*create\|\.create(" .

# Singleton
grep -r "getInstance\|private.*constructor\|static.*instance" .

# Observer
grep -r "subscribe\|addEventListener\|\.on(\|emit\|EventEmitter" .

# Strategy
grep -r "class.*Strategy\|interface.*Strategy" .

# Builder
grep -r "class.*Builder\|\.build(\|return this" .

# Decorator
grep -r "@\w+\|class.*Decorator\|function decorator" .

# Repository
grep -r "class.*Repository\|interface.*Repository" .

# Command
grep -r "class.*Command\|execute()\|undo()" .
```

### Architectural Patterns

```bash
# MVC
find . -type d -name "models" -o -name "views" -o -name "controllers"

# Repository Pattern
grep -r "Repository\|findById\|findAll\|save\|delete" .

# Service Layer
grep -r "class.*Service" . | grep -v test

# Dependency Injection
grep -r "constructor.*inject\|@Injectable\|@Inject" .
```

---

## File Structure Clues

### MVC
```
app/
├── models/
├── views/
└── controllers/
```

### Layered Architecture
```
src/
├── presentation/
├── business/
├── persistence/
└── domain/
```

### Hexagonal Architecture
```
src/
├── domain/
├── ports/
└── adapters/
```

### Microservices
```
services/
├── auth-service/
├── user-service/
└── api-gateway/
```

### Atomic Design
```
components/
├── atoms/
├── molecules/
├── organisms/
├── templates/
└── pages/
```

---

## Code Signatures

### Creational Patterns

```typescript
// Factory
class *Factory {
  create*(type): Interface
}

// Singleton
class Singleton {
  private static instance;
  private constructor();
  static getInstance()
}

// Builder
class *Builder {
  with*(): this
  build(): Product
}
```

### Structural Patterns

```typescript
// Adapter
class *Adapter implements NewInterface {
  constructor(private legacy: OldInterface)
}

// Decorator
@decorator
function method() {}

// Proxy
class *Proxy implements Subject {
  private realSubject: Subject;
}

// Facade
class *Facade {
  constructor(
    private service1,
    private service2,
    private service3
  )
}
```

### Behavioral Patterns

```typescript
// Observer
class EventEmitter {
  on(event, callback)
  emit(event, data)
}

// Strategy
class Context {
  constructor(private strategy: Strategy)
}

// Command
class *Command {
  execute()
  undo()
}

// State
class Context {
  setState(state: State)
}
```

### Data Patterns

```typescript
// Repository
class *Repository {
  findById(id): Entity
  findAll(): Entity[]
  save(entity): void
  delete(id): void
}

// Active Record
class Model {
  save()
  update()
  delete()
  static find()
}

// Unit of Work
class UnitOfWork {
  registerNew(entity)
  registerDirty(entity)
  commit()
}
```

---

## Import/Dependency Clues

### React Patterns

```typescript
// Component-based
import { Component } from 'react';
import { useState, useEffect } from 'react';

// Container/Presenter
// Container in pages/, Presenter in components/

// Hooks
import { use* } from 'react';
```

### Angular Patterns

```typescript
// Dependency Injection
import { Injectable } from '@angular/core';
@Injectable()

// Decorators
@Component, @NgModule, @Input, @Output
```

### Express Patterns

```typescript
// Middleware chain (Decorator-like)
app.use(middleware1, middleware2);

// Router (Facade)
const router = express.Router();
```

---

## Pattern Combinations

### Common Combos

| Primary Pattern | Often Combined With | Purpose |
|----------------|---------------------|---------|
| Repository | Unit of Work | Transaction management |
| Factory | Strategy | Create strategy instances |
| Observer | Command | Event-driven commands |
| Singleton | Factory | Single factory instance |
| Decorator | Strategy | Add behavior to strategies |
| Facade | Repository + Service | Simplified data access |
| Builder | Prototype | Clone and customize |

---

## Anti-Pattern Red Flags

| Anti-Pattern | Red Flag Indicators |
|-------------|---------------------|
| God Object | Class > 500 lines, does everything |
| Spaghetti Code | Deep nesting (5+), long methods (100+) |
| Magic Numbers | Hardcoded `if (x === 2)` |
| Copy-Paste | Identical code blocks |
| Circular Deps | A imports B imports A |
| Premature Optimization | Complex code without profiling |

---

## Quick Decision Tree

```
Is it about object creation?
├─ YES → Creational (Factory, Singleton, Builder, Prototype)
└─ NO
   ├─ Is it about object composition?
   │  └─ YES → Structural (Adapter, Decorator, Facade, Proxy)
   └─ NO
      ├─ Is it about object interaction?
      │  └─ YES → Behavioral (Observer, Strategy, Command, State)
      └─ NO
         ├─ Is it about data access?
         │  └─ YES → Data (Repository, Active Record, Unit of Work)
         └─ NO → Architectural (MVC, Layered, Microservices)
```

---

## Pattern Priority by Language

### TypeScript/JavaScript
1. Observer (events, promises)
2. Factory (object creation)
3. Decorator (functions, classes)
4. Strategy (callbacks)
5. Repository (data access)

### Python
1. Decorator (@decorator)
2. Iterator (generators)
3. Factory (class methods)
4. Singleton (modules)
5. Observer (signals)

### Java
1. Singleton (getInstance)
2. Factory (static methods)
3. Builder (fluent interfaces)
4. Repository (Spring Data)
5. Dependency Injection (Spring)

### Go
1. Factory (constructor functions)
2. Strategy (interfaces)
3. Decorator (higher-order functions)
4. Repository (data layer)
5. Singleton (sync.Once)

---

## Framework-Specific Patterns

### React
- Component composition
- Hooks (useState, useEffect)
- Context (global state)
- Render props
- Higher-Order Components (HOC)

### Angular
- Dependency Injection
- Services (Singleton)
- Decorators (@Component, @Injectable)
- Observables (RxJS)
- Pipes (transformation)

### Vue
- Composition API
- Reactive state (ref, reactive)
- Composables (hooks-like)
- Provide/Inject (DI-like)

### Express
- Middleware chain
- Router (hierarchical routing)
- Error handling middleware

### Django
- MTV (Model-Template-View)
- Class-based views
- Mixins
- ORM (Active Record-like)

### Rails
- Active Record
- Convention over Configuration
- MVC
- Concerns (mixins)

---

## Validation Checklist

When you identify a pattern, verify:

- [ ] **Name**: What pattern is it?
- [ ] **Location**: File paths with line numbers
- [ ] **Purpose**: Why is it used?
- [ ] **Correctness**: Properly implemented?
- [ ] **Appropriateness**: Right pattern for the job?
- [ ] **Variations**: Deviations from standard?
- [ ] **Impact**: How does it affect the codebase?
- [ ] **Related**: What other patterns work with it?

---

## Common Mistakes

| Pattern | Common Mistake | Fix |
|---------|---------------|-----|
| Singleton | Used for everything | Use DI instead |
| Factory | Over-engineering simple creation | Direct instantiation |
| Observer | Memory leaks (no unsubscribe) | Cleanup subscriptions |
| Decorator | Too many layers | Limit nesting |
| Repository | Business logic in repo | Move to service layer |
| Builder | Too complex | Use simple constructor |

---

**Usage**: Use this guide for quick pattern identification during codebase investigation. For detailed explanations, see [pattern-catalog.md](./pattern-catalog.md).
