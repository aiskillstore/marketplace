# Go + testing Template

Template for generating Go test scaffolds using the standard testing package.

## Variables

| Variable | Description |
|----------|-------------|
| `{package_name}` | Package name (e.g., `auth`) |
| `{function_name}` | Name of function being tested |
| `{struct_name}` | Name of struct being tested |
| `{method_name}` | Name of method being tested |

## File Template

```go
// Tests for {source_file}.
//
// Auto-generated scaffold by /ai-dev-kit:scaffold-tests.
// Fill in test implementations and remove TODO comments.
package {package_name}

import (
	"testing"
)

{function_tests}

{method_tests}
```

## Function Test Template

```go
func Test{FunctionName}(t *testing.T) {
	// TODO: Implement test for {FunctionName}
	t.Run("happy path", func(t *testing.T) {
		// TODO: Implement this test
		t.Fatal("Test not yet implemented")
	})

	t.Run("edge cases", func(t *testing.T) {
		t.Skip("TODO: Implement edge case tests")
	})

	t.Run("error conditions", func(t *testing.T) {
		t.Skip("TODO: Implement error condition tests")
	})
}
```

## Table-Driven Test Template

```go
func Test{FunctionName}(t *testing.T) {
	tests := []struct {
		name    string
		input   interface{} // TODO: Replace with actual type
		want    interface{} // TODO: Replace with actual type
		wantErr bool
	}{
		// TODO: Add test cases
		{
			name:    "placeholder",
			input:   nil,
			want:    nil,
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// TODO: Implement this test
			t.Fatal("Test not yet implemented")
		})
	}
}
```

## Method Test Template

```go
func Test{StructName}_{MethodName}(t *testing.T) {
	// TODO: Create test instance
	instance := &{StructName}{}

	t.Run("happy path", func(t *testing.T) {
		// TODO: Implement this test
		_ = instance
		t.Fatal("Test not yet implemented")
	})

	t.Run("edge cases", func(t *testing.T) {
		t.Skip("TODO: Implement edge case tests")
	})
}
```

## Benchmark Template

```go
func Benchmark{FunctionName}(b *testing.B) {
	// TODO: Set up benchmark data
	for i := 0; i < b.N; i++ {
		// TODO: Call function under test
		_ = {FunctionName}()
	}
}
```

## Example Output

Given source file `pkg/auth/login.go`:
```go
package auth

type UserSession struct {
	UserID string
}

func (s *UserSession) Refresh() bool { ... }

func (s *UserSession) Invalidate() { ... }

func Authenticate(username, password string) (*UserSession, error) { ... }

func Logout(session *UserSession) bool { ... }
```

Generated scaffold `pkg/auth/login_test.go`:
```go
// Tests for login.go.
//
// Auto-generated scaffold by /ai-dev-kit:scaffold-tests.
// Fill in test implementations and remove TODO comments.
package auth

import (
	"testing"
)

func TestAuthenticate(t *testing.T) {
	t.Run("happy path", func(t *testing.T) {
		// TODO: Implement this test
		t.Fatal("Test not yet implemented")
	})

	t.Run("edge cases", func(t *testing.T) {
		t.Skip("TODO: Implement edge case tests")
	})

	t.Run("error conditions", func(t *testing.T) {
		t.Skip("TODO: Implement error condition tests")
	})
}

func TestLogout(t *testing.T) {
	t.Run("happy path", func(t *testing.T) {
		// TODO: Implement this test
		t.Fatal("Test not yet implemented")
	})

	t.Run("edge cases", func(t *testing.T) {
		t.Skip("TODO: Implement edge case tests")
	})

	t.Run("error conditions", func(t *testing.T) {
		t.Skip("TODO: Implement error condition tests")
	})
}

func TestUserSession_Refresh(t *testing.T) {
	instance := &UserSession{}

	t.Run("happy path", func(t *testing.T) {
		// TODO: Implement this test
		_ = instance
		t.Fatal("Test not yet implemented")
	})

	t.Run("edge cases", func(t *testing.T) {
		t.Skip("TODO: Implement edge case tests")
	})
}

func TestUserSession_Invalidate(t *testing.T) {
	instance := &UserSession{}

	t.Run("happy path", func(t *testing.T) {
		// TODO: Implement this test
		_ = instance
		t.Fatal("Test not yet implemented")
	})

	t.Run("edge cases", func(t *testing.T) {
		t.Skip("TODO: Implement edge case tests")
	})
}
```

## Naming Rules

| Source | Test File |
|--------|-----------|
| `pkg/auth/login.go` | `pkg/auth/login_test.go` |
| `internal/core.go` | `internal/core_test.go` |
| `cmd/main.go` | `cmd/main_test.go` |

## Go Test Conventions

- Test files must end with `_test.go`
- Test functions must start with `Test`
- Test files must be in same package as source
- Use `t.Run` for subtests
- Use `t.Fatal` or `t.Fatalf` to fail
- Use `t.Skip` for TODO tests
