package module

import (
	"errors"
	"testing"
)

// TestFunctionName tests the FunctionName function
func TestFunctionName(t *testing.T) {
	t.Run("returns expected result for valid input", func(t *testing.T) {
		input := "test"
		expected := "expected"

		result := FunctionName(input)

		if result != expected {
			t.Errorf("FunctionName(%q) = %q; want %q", input, result, expected)
		}
	})

	t.Run("handles empty input", func(t *testing.T) {
		result := FunctionName("")
		if result == "" {
			t.Error("FunctionName should handle empty string")
		}
	})

	t.Run("returns error for invalid input", func(t *testing.T) {
		_, err := FunctionNameWithError("invalid")
		if err == nil {
			t.Error("expected error for invalid input, got nil")
		}
	})

	t.Run("returns specific error message", func(t *testing.T) {
		_, err := FunctionNameWithError("invalid")
		expectedErr := errors.New("expected error message")
		if err.Error() != expectedErr.Error() {
			t.Errorf("got error %v; want %v", err, expectedErr)
		}
	})
}

// Table-driven tests
func TestFunctionNameTableDriven(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		expected string
		wantErr  bool
	}{
		{
			name:     "valid input",
			input:    "test",
			expected: "expected",
			wantErr:  false,
		},
		{
			name:     "empty input",
			input:    "",
			expected: "",
			wantErr:  true,
		},
		{
			name:     "special characters",
			input:    "test@#$",
			expected: "sanitized",
			wantErr:  false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result, err := FunctionNameWithError(tt.input)

			if (err != nil) != tt.wantErr {
				t.Errorf("FunctionNameWithError() error = %v, wantErr %v", err, tt.wantErr)
				return
			}

			if result != tt.expected {
				t.Errorf("FunctionNameWithError() = %v, want %v", result, tt.expected)
			}
		})
	}
}

// Benchmark test
func BenchmarkFunctionName(b *testing.B) {
	input := "test input"
	for i := 0; i < b.N; i++ {
		FunctionName(input)
	}
}

// Test with setup and teardown
func TestStructMethod(t *testing.T) {
	// Setup
	instance := &StructName{
		Field: "initial",
	}

	// Test
	result := instance.Method()

	// Assert
	if result != "expected" {
		t.Errorf("Method() = %v; want %v", result, "expected")
	}

	// Teardown (if needed)
	instance.Cleanup()
}

// Test with subtests for better organization
func TestStructMethods(t *testing.T) {
	instance := &StructName{}

	t.Run("Method1", func(t *testing.T) {
		result := instance.Method1()
		if result == nil {
			t.Error("Method1 should not return nil")
		}
	})

	t.Run("Method2", func(t *testing.T) {
		err := instance.Method2()
		if err != nil {
			t.Errorf("Method2 returned unexpected error: %v", err)
		}
	})
}

// Mock example (using interface)
type MockDependency struct {
	CalledWith string
	ReturnVal  string
}

func (m *MockDependency) DoSomething(input string) string {
	m.CalledWith = input
	return m.ReturnVal
}

func TestWithMock(t *testing.T) {
	mock := &MockDependency{ReturnVal: "mocked"}
	instance := &StructName{Dependency: mock}

	result := instance.MethodUsingDependency("input")

	if mock.CalledWith != "input" {
		t.Errorf("Dependency called with %q; want %q", mock.CalledWith, "input")
	}

	if result != "mocked" {
		t.Errorf("got %q; want %q", result, "mocked")
	}
}

// Test helper function
func assertEqual(t *testing.T, got, want interface{}) {
	t.Helper()
	if got != want {
		t.Errorf("got %v; want %v", got, want)
	}
}

// Using test helper
func TestWithHelper(t *testing.T) {
	result := FunctionName("input")
	assertEqual(t, result, "expected")
}
