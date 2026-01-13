---
name: golang-enterprise-patterns
description: Enterprise-level Go architecture patterns including clean architecture,
  hexagonal architecture, DDD, and production-ready application structure.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: skill
---

# Golang Enterprise Patterns

This skill provides guidance on enterprise-level Go application architecture, design patterns, and production-ready code organization.

## When to Use This Skill

- When designing new Go applications with complex business logic
- When implementing clean architecture or hexagonal architecture
- When applying Domain-Driven Design (DDD) principles
- When organizing large Go codebases
- When establishing patterns for team consistency

## Clean Architecture

### Layer Structure

```text
/cmd
  /api           - HTTP/gRPC entry points
  /worker        - Background job runners
/internal
  /domain        - Business entities and interfaces
  /application   - Use cases and application services
  /infrastructure
    /persistence - Database implementations
    /messaging   - Queue implementations
    /http        - HTTP client implementations
  /interfaces
    /api         - HTTP handlers
    /grpc        - gRPC handlers
/pkg             - Shared libraries (public)
```

### Dependency Rule

Dependencies flow inward only:

```text
Interfaces → Application → Domain
     ↓            ↓
Infrastructure (implements domain interfaces)
```

### Domain Layer

```go
// domain/user.go
package domain

import "time"

type UserID string

type User struct {
    ID        UserID
    Email     string
    Name      string
    CreatedAt time.Time
}

// UserRepository defines the contract for user persistence
type UserRepository interface {
    FindByID(ctx context.Context, id UserID) (*User, error)
    FindByEmail(ctx context.Context, email string) (*User, error)
    Save(ctx context.Context, user *User) error
    Delete(ctx context.Context, id UserID) error
}

// UserService defines domain business logic
type UserService interface {
    Register(ctx context.Context, email, name string) (*User, error)
    Authenticate(ctx context.Context, email, password string) (*User, error)
}
```

### Application Layer

```go
// application/user_service.go
package application

type UserServiceImpl struct {
    repo   domain.UserRepository
    hasher PasswordHasher
    logger Logger
}

func NewUserService(repo domain.UserRepository, hasher PasswordHasher, logger Logger) *UserServiceImpl {
    return &UserServiceImpl{repo: repo, hasher: hasher, logger: logger}
}

func (s *UserServiceImpl) Register(ctx context.Context, email, name string) (*domain.User, error) {
    // Check if user exists
    existing, err := s.repo.FindByEmail(ctx, email)
    if err != nil && !errors.Is(err, domain.ErrNotFound) {
        return nil, fmt.Errorf("checking existing user: %w", err)
    }
    if existing != nil {
        return nil, domain.ErrUserAlreadyExists
    }

    user := &domain.User{
        ID:        domain.UserID(uuid.New().String()),
        Email:     email,
        Name:      name,
        CreatedAt: time.Now(),
    }

    if err := s.repo.Save(ctx, user); err != nil {
        return nil, fmt.Errorf("saving user: %w", err)
    }

    return user, nil
}
```

## Hexagonal Architecture (Ports & Adapters)

### Port Definitions

```go
// ports/primary.go - Driving ports (input)
package ports

type UserAPI interface {
    CreateUser(ctx context.Context, req CreateUserRequest) (*UserResponse, error)
    GetUser(ctx context.Context, id string) (*UserResponse, error)
}

// ports/secondary.go - Driven ports (output)
type UserStorage interface {
    Save(ctx context.Context, user *domain.User) error
    FindByID(ctx context.Context, id string) (*domain.User, error)
}

type NotificationSender interface {
    SendWelcomeEmail(ctx context.Context, user *domain.User) error
}
```

### Adapter Implementations

```go
// adapters/postgres/user_repository.go
package postgres

type UserRepository struct {
    db *sql.DB
}

func (r *UserRepository) Save(ctx context.Context, user *domain.User) error {
    query := `INSERT INTO users (id, email, name, created_at) VALUES ($1, $2, $3, $4)`
    _, err := r.db.ExecContext(ctx, query, user.ID, user.Email, user.Name, user.CreatedAt)
    return err
}
```

## Domain-Driven Design (DDD)

### Aggregate Roots

```go
// domain/order/aggregate.go
package order

type Order struct {
    id         OrderID
    customerID CustomerID
    items      []OrderItem
    status     OrderStatus
    events     []DomainEvent
}

func NewOrder(customerID CustomerID) *Order {
    o := &Order{
        id:         OrderID(uuid.New().String()),
        customerID: customerID,
        status:     StatusPending,
    }
    o.recordEvent(OrderCreated{OrderID: o.id, CustomerID: customerID})
    return o
}

func (o *Order) AddItem(productID ProductID, quantity int, price Money) error {
    if o.status != StatusPending {
        return ErrOrderNotModifiable
    }
    o.items = append(o.items, OrderItem{
        ProductID: productID,
        Quantity:  quantity,
        Price:     price,
    })
    return nil
}

func (o *Order) Submit() error {
    if len(o.items) == 0 {
        return ErrEmptyOrder
    }
    o.status = StatusSubmitted
    o.recordEvent(OrderSubmitted{OrderID: o.id})
    return nil
}
```

### Value Objects

```go
// domain/money.go
type Money struct {
    amount   int64  // cents
    currency string
}

func NewMoney(amount int64, currency string) (Money, error) {
    if amount < 0 {
        return Money{}, ErrNegativeAmount
    }
    return Money{amount: amount, currency: currency}, nil
}

func (m Money) Add(other Money) (Money, error) {
    if m.currency != other.currency {
        return Money{}, ErrCurrencyMismatch
    }
    return Money{amount: m.amount + other.amount, currency: m.currency}, nil
}
```

### Domain Events

```go
// domain/events.go
type DomainEvent interface {
    EventName() string
    OccurredAt() time.Time
}

type OrderCreated struct {
    OrderID    OrderID
    CustomerID CustomerID
    occurredAt time.Time
}

func (e OrderCreated) EventName() string    { return "order.created" }
func (e OrderCreated) OccurredAt() time.Time { return e.occurredAt }
```

## Dependency Injection

### Wire-Style DI

```go
// wire.go
//+build wireinject

func InitializeApp(cfg *config.Config) (*App, error) {
    wire.Build(
        NewDatabase,
        NewUserRepository,
        NewUserService,
        NewHTTPServer,
        NewApp,
    )
    return nil, nil
}
```

### Manual DI (Preferred for Simplicity)

```go
// main.go
func main() {
    cfg := config.Load()

    db := database.Connect(cfg.DatabaseURL)

    userRepo := postgres.NewUserRepository(db)
    orderRepo := postgres.NewOrderRepository(db)

    userService := application.NewUserService(userRepo)
    orderService := application.NewOrderService(orderRepo, userRepo)

    handler := api.NewHandler(userService, orderService)
    server := http.NewServer(cfg.Port, handler)

    server.Run()
}
```

## Error Handling Patterns

### Custom Error Types

```go
// domain/errors.go
type Error struct {
    Code    string
    Message string
    Err     error
}

func (e *Error) Error() string {
    if e.Err != nil {
        return fmt.Sprintf("%s: %s: %v", e.Code, e.Message, e.Err)
    }
    return fmt.Sprintf("%s: %s", e.Code, e.Message)
}

func (e *Error) Unwrap() error { return e.Err }

var (
    ErrNotFound         = &Error{Code: "NOT_FOUND", Message: "resource not found"}
    ErrUserAlreadyExists = &Error{Code: "USER_EXISTS", Message: "user already exists"}
    ErrInvalidInput     = &Error{Code: "INVALID_INPUT", Message: "invalid input"}
)
```

## Configuration Management

```go
// config/config.go
type Config struct {
    Server   ServerConfig
    Database DatabaseConfig
    Redis    RedisConfig
}

func Load() (*Config, error) {
    cfg := &Config{}

    cfg.Server.Port = getEnvInt("PORT", 8080)
    cfg.Server.ReadTimeout = getEnvDuration("READ_TIMEOUT", 30*time.Second)

    cfg.Database.URL = mustGetEnv("DATABASE_URL")
    cfg.Database.MaxConns = getEnvInt("DB_MAX_CONNS", 25)

    return cfg, nil
}
```

## Best Practices

1. **Keep domain pure** - No framework dependencies in domain layer
2. **Interface segregation** - Small, focused interfaces
3. **Dependency inversion** - Depend on abstractions, not concretions
4. **Explicit dependencies** - Pass dependencies via constructor
5. **Fail fast** - Validate at boundaries, trust internal code
6. **Make illegal states unrepresentable** - Use types to enforce invariants
