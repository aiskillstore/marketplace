---
name: go-best-practices
description: Use when reading or writing Go files (.go, go.mod).
---

# Go Best Practices

Follows type-first, functional, and error handling patterns from CLAUDE.md. This skill covers language-specific idioms only.

## Make Illegal States Unrepresentable

Use Go's type system to prevent invalid states at compile time.

**Custom types for domain primitives:**
```go
// Distinct types prevent mixing up IDs
type UserID string
type OrderID string

func GetUser(id UserID) (*User, error) {
    // Compiler prevents passing OrderID here
}

// Methods attach behavior to the type
func (id UserID) String() string {
    return string(id)
}
```

**Interfaces for behavior contracts:**
```go
// Define what you need, not what you have
type UserRepository interface {
    GetByID(ctx context.Context, id UserID) (*User, error)
    Save(ctx context.Context, user *User) error
}

// Accept interfaces, return structs
func ProcessInput(r io.Reader) ([]byte, error) {
    return io.ReadAll(r)
}
```

**Enums with iota and exhaustive switch:**
```go
type Status int

const (
    StatusActive Status = iota + 1
    StatusInactive
    StatusPending
)

func ProcessStatus(s Status) (string, error) {
    switch s {
    case StatusActive:
        return "processing", nil
    case StatusInactive:
        return "skipped", nil
    case StatusPending:
        return "waiting", nil
    default:
        return "", fmt.Errorf("unhandled status: %v", s)
    }
}
```

**Functional options for flexible construction:**
```go
type ServerOption func(*Server)

func WithPort(port int) ServerOption {
    return func(s *Server) { s.port = port }
}

func NewServer(opts ...ServerOption) *Server {
    s := &Server{port: 8080, timeout: 30 * time.Second}
    for _, opt := range opts {
        opt(s)
    }
    return s
}
// Usage: NewServer(WithPort(3000), WithTimeout(time.Minute))
```

**Embed for composition:**
```go
type Timestamps struct {
    CreatedAt time.Time
    UpdatedAt time.Time
}

type User struct {
    Timestamps  // User gains CreatedAt, UpdatedAt
    ID    UserID
    Email string
}
```

## Go-Specific Error Handling

Wrap errors with `%w` to preserve the chain for `errors.Is` / `errors.As`:
```go
out, err := client.Do(ctx, req)
if err != nil {
    return nil, fmt.Errorf("fetch widget failed: %w", err)
}
```

## Structured Logging

Use `log/slog` with structured key-value pairs:
```go
import "log/slog"

var log = slog.With("component", "widgets")

func createWidget(name string) (*Widget, error) {
    log.Debug("creating widget", "name", name)
    widget := &Widget{Name: name}
    log.Debug("created widget", "id", widget.ID)
    return widget, nil
}
```
