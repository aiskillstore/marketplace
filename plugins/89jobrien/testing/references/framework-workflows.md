---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: testing
---

# Framework-Specific TDD Workflows

Detailed TDD workflows and examples for different testing frameworks.

## Python - pytest

### Setup

**Installation:**

```bash
pip install pytest pytest-cov pytest-mock
# or
uv add pytest pytest-cov pytest-mock
```

**Configuration (`pyproject.toml`):**

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
```

### TDD Workflow Example

**RED Phase:**

```python
# tests/test_calculator.py
def test_add_two_numbers():
    result = add(2, 3)
    assert result == 5
```

```bash
$ pytest tests/test_calculator.py::test_add_two_numbers
FAILED - NameError: name 'add' is not defined
```

**GREEN Phase:**

```python
# src/calculator.py
def add(a, b):
    return 5  # Minimal implementation
```

```bash
$ pytest tests/test_calculator.py::test_add_two_numbers
PASSED in 0.01s
```

**REFACTOR Phase:**

```python
# src/calculator.py
def add(a, b):
    return a + b  # Proper implementation
```

```bash
$ pytest
PASSED - All tests passing
```

### Common Patterns

**Fixtures:**

```python
@pytest.fixture
def sample_user():
    return User(name="Test", email="test@example.com")

def test_user_greeting(sample_user):
    assert sample_user.greet() == "Hello, Test"
```

**Parametrization:**

```python
@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

**Mocking:**

```python
def test_api_call(mocker):
    mock_get = mocker.patch('requests.get')
    mock_get.return_value.json.return_value = {'data': 'test'}

    result = fetch_data()
    assert result == {'data': 'test'}
```

## JavaScript/TypeScript - Jest

### Setup

**Installation:**

```bash
npm install --save-dev jest @types/jest
```

**Configuration (`package.json`):**

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch"
  },
  "jest": {
    "testMatch": ["**/__tests__/**/*.js", "**/*.test.js"],
    "coverageDirectory": "coverage"
  }
}
```

### TDD Workflow Example

**RED Phase:**

```javascript
// __tests__/calculator.test.js
test('adds two numbers', () => {
  const result = add(2, 3);
  expect(result).toBe(5);
});
```

```bash
$ npm test
FAIL - ReferenceError: add is not defined
```

**GREEN Phase:**

```javascript
// src/calculator.js
function add(a, b) {
  return 5; // Minimal implementation
}
```

```bash
$ npm test
PASS - 1 passed
```

**REFACTOR Phase:**

```javascript
// src/calculator.js
function add(a, b) {
  return a + b; // Proper implementation
}
```

```bash
$ npm test
PASS - All tests passing
```

### Common Patterns

**Setup/Teardown:**

```javascript
beforeEach(() => {
  user = new User('Test');
});

afterEach(() => {
  user.cleanup();
});
```

**Mocking:**

```javascript
jest.mock('./api');

test('fetches data', async () => {
  api.fetchData.mockResolvedValue({ data: 'test' });
  const result = await fetchData();
  expect(result).toEqual({ data: 'test' });
});
```

**Snapshots:**

```javascript
test('renders component', () => {
  const component = render(<MyComponent />);
  expect(component).toMatchSnapshot();
});
```

## JavaScript/TypeScript - Vitest

### Setup

**Installation:**

```bash
npm install --save-dev vitest
```

**Configuration (`vite.config.ts`):**

```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
  },
});
```

### TDD Workflow

Similar to Jest, but with Vitest syntax:

```typescript
import { describe, it, expect } from 'vitest';

describe('calculator', () => {
  it('adds two numbers', () => {
    expect(add(2, 3)).toBe(5);
  });
});
```

## Java - JUnit

### Setup

**Maven (`pom.xml`):**

```xml
<dependencies>
  <dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.9.2</version>
    <scope>test</scope>
  </dependency>
</dependencies>
```

### TDD Workflow Example

**RED Phase:**

```java
// src/test/java/CalculatorTest.java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

class CalculatorTest {
    @Test
    void testAddTwoNumbers() {
        int result = Calculator.add(2, 3);
        assertEquals(5, result);
    }
}
```

**GREEN Phase:**

```java
// src/main/java/Calculator.java
public class Calculator {
    public static int add(int a, int b) {
        return 5; // Minimal implementation
    }
}
```

**REFACTOR Phase:**

```java
public class Calculator {
    public static int add(int a, int b) {
        return a + b; // Proper implementation
    }
}
```

### Common Patterns

**Parameterized Tests:**

```java
@ParameterizedTest
@ValueSource(ints = {1, 2, 3})
void testIsPositive(int number) {
    assertTrue(number > 0);
}
```

**Mocking (Mockito):**

```java
@Mock
private UserRepository userRepository;

@Test
void testGetUser() {
    when(userRepository.findById(1)).thenReturn(new User(1, "Test"));
    User user = userService.getUser(1);
    assertEquals("Test", user.getName());
}
```

## Go - testing

### Setup

Go testing is built-in, no setup needed.

### TDD Workflow Example

**RED Phase:**

```go
// calculator_test.go
package main

import "testing"

func TestAdd(t *testing.T) {
    result := Add(2, 3)
    if result != 5 {
        t.Errorf("Expected 5, got %d", result)
    }
}
```

```bash
$ go test
FAIL - undefined: Add
```

**GREEN Phase:**

```go
// calculator.go
package main

func Add(a, b int) int {
    return 5 // Minimal implementation
}
```

```bash
$ go test
PASS
```

**REFACTOR Phase:**

```go
func Add(a, b int) int {
    return a + b // Proper implementation
}
```

```bash
$ go test
PASS
```

### Common Patterns

**Table-Driven Tests:**

```go
func TestAdd(t *testing.T) {
    tests := []struct {
        a, b, expected int
    }{
        {1, 2, 3},
        {0, 0, 0},
        {-1, 1, 0},
    }

    for _, tt := range tests {
        result := Add(tt.a, tt.b)
        if result != tt.expected {
            t.Errorf("Add(%d, %d) = %d; expected %d", tt.a, tt.b, result, tt.expected)
        }
    }
}
```

**Subtests:**

```go
func TestAdd(t *testing.T) {
    t.Run("positive numbers", func(t *testing.T) {
        result := Add(2, 3)
        if result != 5 {
            t.Errorf("Expected 5, got %d", result)
        }
    })

    t.Run("negative numbers", func(t *testing.T) {
        result := Add(-1, -2)
        if result != -3 {
            t.Errorf("Expected -3, got %d", result)
        }
    })
}
```

## Rust - cargo test

### Setup

Rust testing is built-in, no setup needed.

### TDD Workflow Example

**RED Phase:**

```rust
// src/lib.rs
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add() {
        assert_eq!(add(2, 3), 5);
    }
}
```

```bash
$ cargo test
FAIL - cannot find function `add` in this scope
```

**GREEN Phase:**

```rust
// src/lib.rs
pub fn add(a: i32, b: i32) -> i32 {
    5 // Minimal implementation
}
```

```bash
$ cargo test
PASS
```

**REFACTOR Phase:**

```rust
pub fn add(a: i32, b: i32) -> i32 {
    a + b // Proper implementation
}
```

```bash
$ cargo test
PASS
```

### Common Patterns

**Integration Tests:**

```rust
// tests/integration_test.rs
use my_crate::add;

#[test]
fn test_add_integration() {
    assert_eq!(add(2, 3), 5);
}
```

**Property-Based Testing (proptest):**

```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn test_add_commutative(a in 0i32..1000, b in 0i32..1000) {
        assert_eq!(add(a, b), add(b, a));
    }
}
```

## Running Tests

### Python (pytest)

```bash
pytest                    # Run all tests
pytest path/to/test.py    # Run specific file
pytest -k "test_name"     # Run by name pattern
pytest -v                 # Verbose output
pytest --cov              # With coverage
```

### JavaScript (Jest)

```bash
npm test                  # Run all tests
npm test -- file.test.js  # Run specific file
npm test -- --watch       # Watch mode
npm test -- --coverage    # With coverage
```

### Java (Maven)

```bash
mvn test                  # Run all tests
mvn test -Dtest=TestClass # Run specific class
```

### Go

```bash
go test                   # Run all tests
go test ./...             # Run all tests recursively
go test -v                # Verbose output
go test -cover            # With coverage
```

### Rust

```bash
cargo test                # Run all tests
cargo test test_name      # Run specific test
cargo test -- --nocapture # Show output
```
