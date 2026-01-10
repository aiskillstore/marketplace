---
name: golang-testing
description: Comprehensive Go testing patterns including table-driven tests, mocking,
  integration testing, benchmarks, and test organization.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: skill
---

# Golang Testing

This skill provides guidance on comprehensive testing strategies for Go applications including unit tests, integration tests, benchmarks, and test organization.

## When to Use This Skill

- When writing unit tests for Go code
- When creating table-driven tests
- When mocking dependencies with interfaces
- When writing integration tests with test containers
- When benchmarking performance-critical code
- When organizing test suites and fixtures

## Table-Driven Tests

### Basic Pattern

```go
func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive numbers", 2, 3, 5},
        {"negative numbers", -2, -3, -5},
        {"mixed numbers", -2, 3, 1},
        {"zeros", 0, 0, 0},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := Add(tt.a, tt.b)
            if result != tt.expected {
                t.Errorf("Add(%d, %d) = %d; want %d", tt.a, tt.b, result, tt.expected)
            }
        })
    }
}
```

### With Error Cases

```go
func TestDivide(t *testing.T) {
    tests := []struct {
        name      string
        a, b      int
        expected  int
        wantErr   bool
        errString string
    }{
        {"valid division", 10, 2, 5, false, ""},
        {"divide by zero", 10, 0, 0, true, "division by zero"},
        {"negative result", -10, 2, -5, false, ""},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result, err := Divide(tt.a, tt.b)

            if tt.wantErr {
                if err == nil {
                    t.Fatalf("expected error, got nil")
                }
                if !strings.Contains(err.Error(), tt.errString) {
                    t.Errorf("error = %v; want containing %q", err, tt.errString)
                }
                return
            }

            if err != nil {
                t.Fatalf("unexpected error: %v", err)
            }
            if result != tt.expected {
                t.Errorf("Divide(%d, %d) = %d; want %d", tt.a, tt.b, result, tt.expected)
            }
        })
    }
}
```

## Interface-Based Mocking

### Define Interfaces

```go
// repository.go
type UserRepository interface {
    FindByID(ctx context.Context, id string) (*User, error)
    Save(ctx context.Context, user *User) error
}

type EmailSender interface {
    Send(ctx context.Context, to, subject, body string) error
}
```

### Create Mock Implementations

```go
// mocks/user_repository.go
type MockUserRepository struct {
    FindByIDFunc func(ctx context.Context, id string) (*User, error)
    SaveFunc     func(ctx context.Context, user *User) error
}

func (m *MockUserRepository) FindByID(ctx context.Context, id string) (*User, error) {
    if m.FindByIDFunc != nil {
        return m.FindByIDFunc(ctx, id)
    }
    return nil, nil
}

func (m *MockUserRepository) Save(ctx context.Context, user *User) error {
    if m.SaveFunc != nil {
        return m.SaveFunc(ctx, user)
    }
    return nil
}
```

### Use in Tests

```go
func TestUserService_GetUser(t *testing.T) {
    expectedUser := &User{ID: "123", Name: "John"}

    repo := &MockUserRepository{
        FindByIDFunc: func(ctx context.Context, id string) (*User, error) {
            if id == "123" {
                return expectedUser, nil
            }
            return nil, ErrNotFound
        },
    }

    service := NewUserService(repo)

    t.Run("existing user", func(t *testing.T) {
        user, err := service.GetUser(context.Background(), "123")
        if err != nil {
            t.Fatalf("unexpected error: %v", err)
        }
        if user.Name != expectedUser.Name {
            t.Errorf("got name %q; want %q", user.Name, expectedUser.Name)
        }
    })

    t.Run("non-existing user", func(t *testing.T) {
        _, err := service.GetUser(context.Background(), "456")
        if !errors.Is(err, ErrNotFound) {
            t.Errorf("got error %v; want ErrNotFound", err)
        }
    })
}
```

## Testify Assertions

```go
import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

func TestWithTestify(t *testing.T) {
    // assert continues on failure
    assert.Equal(t, 5, Add(2, 3), "addition should work")
    assert.NotNil(t, result)
    assert.Len(t, items, 3)
    assert.Contains(t, slice, item)
    assert.True(t, condition)
    assert.NoError(t, err)
    assert.ErrorIs(t, err, ErrNotFound)

    // require stops test on failure
    require.NoError(t, err, "setup must succeed")
    require.NotNil(t, config)
}
```

## Integration Tests with Testcontainers

```go
import (
    "context"
    "testing"
    "github.com/testcontainers/testcontainers-go"
    "github.com/testcontainers/testcontainers-go/modules/postgres"
)

func TestUserRepository_Integration(t *testing.T) {
    if testing.Short() {
        t.Skip("skipping integration test in short mode")
    }

    ctx := context.Background()

    // Start PostgreSQL container
    pgContainer, err := postgres.Run(ctx,
        "postgres:15-alpine",
        postgres.WithDatabase("testdb"),
        postgres.WithUsername("test"),
        postgres.WithPassword("test"),
    )
    require.NoError(t, err)
    defer pgContainer.Terminate(ctx)

    // Get connection string
    connStr, err := pgContainer.ConnectionString(ctx, "sslmode=disable")
    require.NoError(t, err)

    // Connect and run migrations
    db, err := sql.Open("postgres", connStr)
    require.NoError(t, err)
    defer db.Close()

    runMigrations(db)

    // Create repository and test
    repo := NewUserRepository(db)

    t.Run("save and find user", func(t *testing.T) {
        user := &User{ID: "123", Name: "John", Email: "john@example.com"}

        err := repo.Save(ctx, user)
        require.NoError(t, err)

        found, err := repo.FindByID(ctx, "123")
        require.NoError(t, err)
        assert.Equal(t, user.Name, found.Name)
    })
}
```

## Test Fixtures

### Setup/Teardown Pattern

```go
func TestMain(m *testing.M) {
    // Global setup
    setup()

    code := m.Run()

    // Global teardown
    teardown()

    os.Exit(code)
}

func setup() {
    // Initialize test database, load fixtures, etc.
}

func teardown() {
    // Clean up resources
}
```

### Per-Test Setup

```go
func setupTest(t *testing.T) (*UserService, func()) {
    t.Helper()

    db := setupTestDB(t)
    repo := NewUserRepository(db)
    service := NewUserService(repo)

    cleanup := func() {
        db.Close()
    }

    return service, cleanup
}

func TestUserService(t *testing.T) {
    service, cleanup := setupTest(t)
    defer cleanup()

    // Run tests using service
}
```

## Benchmarks

```go
func BenchmarkFibonacci(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Fibonacci(20)
    }
}

func BenchmarkFibonacciParallel(b *testing.B) {
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            Fibonacci(20)
        }
    })
}

// With sub-benchmarks
func BenchmarkSort(b *testing.B) {
    sizes := []int{100, 1000, 10000}

    for _, size := range sizes {
        b.Run(fmt.Sprintf("size-%d", size), func(b *testing.B) {
            data := generateData(size)
            b.ResetTimer()

            for i := 0; i < b.N; i++ {
                sort.Ints(data)
            }
        })
    }
}
```

## Testing HTTP Handlers

```go
func TestHandler_GetUser(t *testing.T) {
    // Setup mock service
    service := &MockUserService{
        GetUserFunc: func(ctx context.Context, id string) (*User, error) {
            return &User{ID: id, Name: "John"}, nil
        },
    }

    handler := NewHandler(service)

    t.Run("success", func(t *testing.T) {
        req := httptest.NewRequest(http.MethodGet, "/users/123", nil)
        rec := httptest.NewRecorder()

        handler.GetUser(rec, req)

        assert.Equal(t, http.StatusOK, rec.Code)

        var response User
        err := json.NewDecoder(rec.Body).Decode(&response)
        require.NoError(t, err)
        assert.Equal(t, "John", response.Name)
    })

    t.Run("not found", func(t *testing.T) {
        service.GetUserFunc = func(ctx context.Context, id string) (*User, error) {
            return nil, ErrNotFound
        }

        req := httptest.NewRequest(http.MethodGet, "/users/999", nil)
        rec := httptest.NewRecorder()

        handler.GetUser(rec, req)

        assert.Equal(t, http.StatusNotFound, rec.Code)
    })
}
```

## Test Organization

### File Structure

```text
/internal
  /user
    user.go
    user_test.go          # Unit tests
    user_integration_test.go  # Integration tests (build tag)
    testdata/             # Test fixtures
      users.json
```

### Build Tags for Integration Tests

```go
//go:build integration

package user

func TestIntegration(t *testing.T) {
    // Integration test code
}
```

Run with: `go test -tags=integration ./...`

## Coverage

```bash
# Generate coverage
go test -coverprofile=coverage.out ./...

# View in browser
go tool cover -html=coverage.out

# Check coverage percentage
go test -cover ./...
```

## Best Practices

1. **Test behavior, not implementation** - Focus on inputs and outputs
2. **One assertion per test** - Keep tests focused and clear
3. **Use t.Helper()** - Mark helper functions for better error reporting
4. **Parallel tests** - Use `t.Parallel()` for independent tests
5. **Descriptive names** - `TestUserService_CreateUser_WithInvalidEmail`
6. **Test edge cases** - Empty inputs, nil values, boundary conditions
7. **Keep tests fast** - Use mocks, skip slow tests with `-short`
8. **Avoid test pollution** - Each test should be independent
