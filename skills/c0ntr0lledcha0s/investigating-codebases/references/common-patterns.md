# Common Architectural Patterns

Quick reference guide for recognizing common patterns in codebases.

## Web Application Patterns

### MVC (Model-View-Controller)
**Structure:**
```
app/
├── models/        # Data models, database schemas
├── views/         # Templates, UI components
└── controllers/   # Request handlers, business logic
```

**Recognition Clues:**
- Directories named `models/`, `views/`, `controllers/`
- Separation of data, presentation, and control logic
- Common in Ruby on Rails, Django, Laravel, ASP.NET MVC

### MVVM (Model-View-ViewModel)
**Structure:**
```
src/
├── models/        # Data models
├── views/         # UI components
└── viewmodels/    # Presentation logic, data binding
```

**Recognition Clues:**
- Two-way data binding
- ViewModels handle UI state
- Common in WPF, Xamarin, Vue.js, Knockout.js

### Repository Pattern
**Structure:**
```
src/
├── repositories/  # Data access layer
│   ├── UserRepository.ts
│   └── ProductRepository.ts
└── models/        # Domain models
```

**Recognition Clues:**
- Classes named `*Repository`
- Abstraction over data access
- CRUD operations encapsulated
- Often paired with dependency injection

### Service Layer Pattern
**Structure:**
```
src/
├── services/      # Business logic
│   ├── UserService.ts
│   ├── AuthService.ts
│   └── PaymentService.ts
├── controllers/   # API handlers
└── repositories/  # Data access
```

**Recognition Clues:**
- Classes named `*Service`
- Business logic separated from controllers
- Services coordinate between repositories
- Transaction management

## API Patterns

### RESTful API
**Structure:**
```
api/
├── routes/
│   ├── users.ts      # /api/users
│   ├── products.ts   # /api/products
│   └── orders.ts     # /api/orders
├── controllers/
└── middleware/
```

**Recognition Clues:**
- HTTP verbs: GET, POST, PUT, DELETE
- Resource-based URLs: `/users/:id`
- Stateless requests
- Status codes: 200, 201, 404, 500

### GraphQL
**Structure:**
```
graphql/
├── schema/
│   ├── types.ts
│   └── schema.graphql
├── resolvers/
│   ├── Query.ts
│   ├── Mutation.ts
│   └── Subscription.ts
└── dataloaders/
```

**Recognition Clues:**
- Schema definition files (`.graphql`)
- Resolvers for queries and mutations
- DataLoaders for optimization
- Single endpoint (usually `/graphql`)

### Microservices Architecture
**Structure:**
```
services/
├── user-service/
│   ├── src/
│   └── Dockerfile
├── product-service/
│   ├── src/
│   └── Dockerfile
└── order-service/
    ├── src/
    └── Dockerfile
```

**Recognition Clues:**
- Multiple independent services
- Each service has own database
- Inter-service communication (REST, gRPC, message queues)
- Separate deployment units

## Frontend Patterns

### Component-Based Architecture (React, Vue)
**Structure:**
```
components/
├── common/
│   ├── Button.tsx
│   └── Input.tsx
├── features/
│   ├── auth/
│   └── dashboard/
└── layouts/
    └── MainLayout.tsx
```

**Recognition Clues:**
- Reusable UI components
- Props for configuration
- Component composition
- Local state management

### Atomic Design
**Structure:**
```
components/
├── atoms/          # Basic building blocks
│   ├── Button.tsx
│   └── Input.tsx
├── molecules/      # Simple component groups
│   └── SearchBar.tsx
├── organisms/      # Complex UI sections
│   └── Header.tsx
├── templates/      # Page layouts
│   └── PageTemplate.tsx
└── pages/          # Specific instances
    └── HomePage.tsx
```

**Recognition Clues:**
- Hierarchy: atoms → molecules → organisms → templates → pages
- Increasing complexity at each level
- Reusability emphasized
- Common in design systems

### Feature-Based Structure
**Structure:**
```
features/
├── auth/
│   ├── components/
│   ├── hooks/
│   ├── api/
│   └── auth.slice.ts
├── products/
│   ├── components/
│   ├── hooks/
│   └── products.slice.ts
└── shared/
    └── components/
```

**Recognition Clues:**
- Organization by feature/domain
- Self-contained features
- Shared utilities separate
- Common in larger React/Vue apps

## State Management Patterns

### Redux Pattern
**Structure:**
```
store/
├── slices/
│   ├── userSlice.ts
│   └── productsSlice.ts
├── middleware/
├── actions/
└── reducers/
```

**Recognition Clues:**
- Actions, reducers, store
- Immutable state updates
- Middleware for side effects
- Time-travel debugging

### Context + Hooks (React)
**Structure:**
```
contexts/
├── AuthContext.tsx
├── ThemeContext.tsx
└── CartContext.tsx
hooks/
├── useAuth.ts
├── useTheme.ts
└── useCart.ts
```

**Recognition Clues:**
- React Context API
- Custom hooks for context consumption
- Provider pattern
- Lighter than Redux

## Testing Patterns

### Test Pyramid
**Structure:**
```
tests/
├── unit/          # Many unit tests
├── integration/   # Fewer integration tests
└── e2e/          # Few end-to-end tests
```

**Recognition Clues:**
- More unit tests than integration tests
- Few e2e tests for critical paths
- Fast feedback loop
- Test coverage emphasis on units

### Page Object Model (E2E Testing)
**Structure:**
```
e2e/
├── pages/
│   ├── LoginPage.ts
│   ├── DashboardPage.ts
│   └── ProductPage.ts
└── tests/
    └── auth.spec.ts
```

**Recognition Clues:**
- Page objects encapsulate UI elements
- Tests use page objects, not selectors directly
- Common in Selenium, Playwright, Cypress

## Data Access Patterns

### Active Record
**Recognition Clues:**
- Models contain both data and behavior
- CRUD methods on model classes
- Example: `user.save()`, `User.find(id)`
- Common in Ruby on Rails, Laravel

### Data Mapper
**Recognition Clues:**
- Separation of domain models and persistence
- Mapper classes handle database operations
- Domain models are plain objects
- Common in Hibernate, TypeORM, Doctrine

### Query Builder
**Recognition Clues:**
- Fluent API for building queries
- Method chaining
- Example: `db.select('*').from('users').where('id', 1)`
- Common in Knex.js, Laravel Query Builder

## Deployment Patterns

### Monorepo
**Structure:**
```
packages/
├── web/
├── mobile/
├── shared/
└── api/
```

**Recognition Clues:**
- Multiple projects in one repository
- Shared dependencies
- Coordinated versioning
- Tools: Nx, Turborepo, Lerna

### Layered Architecture
**Vertical Layers:**
```
Presentation Layer (UI, Controllers)
    ↓
Business Logic Layer (Services, Domain)
    ↓
Data Access Layer (Repositories, ORM)
    ↓
Database Layer
```

**Recognition Clues:**
- Clear separation of concerns
- Dependencies flow downward
- Each layer has specific responsibility
- Common in enterprise applications

---

*Part of research-agent/investigating-codebases skill*
