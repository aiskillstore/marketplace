---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: testing
---

# TDD Patterns Reference

Common patterns, conventions, and anti-patterns for Test-Driven Development across different languages and frameworks.

## Test Organization Patterns

### File Structure

**Python (pytest):**

```
project/
├── src/
│   └── calculator.py
├── tests/
│   ├── conftest.py          # Shared fixtures
│   └── test_calculator.py
└── pyproject.toml
```

**JavaScript/TypeScript (Jest/Vitest):**

```
project/
├── src/
│   └── calculator.js
├── __tests__/
│   └── calculator.test.js
└── package.json
```

**Java (JUnit):**

```
project/
├── src/
│   └── main/java/Calculator.java
└── src/
    └── test/java/CalculatorTest.java
```

**Go:**

```
project/
├── calculator.go
└── calculator_test.go
```

**Rust:**

```
project/
├── src/
│   └── lib.rs
└── tests/
    └── integration_test.rs
```

## Naming Conventions

### Test Files

**Python:**

- `test_*.py` or `*_test.py`
- Example: `test_calculator.py`, `calculator_test.py`

**JavaScript/TypeScript:**

- `*.test.js`, `*.test.ts`
- `*.spec.js`, `*.spec.ts`
- Example: `calculator.test.js`

**Java:**

- `*Test.java`
- Example: `CalculatorTest.java`

**Go:**

- `*_test.go`
- Example: `calculator_test.go`

**Rust:**

- `*_test.rs` (unit tests in same file)
- `tests/*.rs` (integration tests)
- Example: `calculator_test.rs`

### Test Functions/Methods

**General Pattern:**

- Start with `test_` or `Test` prefix
- Describe behavior being tested
- Use descriptive names: `test_user_can_login_with_valid_credentials`

**Examples:**

- `test_calculate_total_with_multiple_items`
- `test_login_fails_with_invalid_password`
- `test_user_cannot_access_admin_without_permission`

## Test Structure Patterns

### AAA Pattern (Arrange-Act-Assert)

**Structure:**

```python
def test_behavior():
    # Arrange: Set up test data
    user = User(name="Alice")

    # Act: Execute the code
    result = user.greet()

    # Assert: Verify outcome
    assert result == "Hello, Alice"
```

### Given-When-Then (BDD)

**Structure:**

```python
def test_behavior():
    # Given: Initial context
    user = create_user(role="admin")

    # When: Action occurs
    has_access = user.can_access("/admin")

    # Then: Expected outcome
    assert has_access is True
```

### Setup/Teardown Pattern

**Python (pytest fixtures):**

```python
@pytest.fixture
def user():
    user = User(name="Test")
    yield user
    user.cleanup()  # Teardown
```

**JavaScript (Jest):**

```javascript
beforeEach(() => {
  user = new User('Test');
});

afterEach(() => {
  user.cleanup();
});
```

## Test Doubles Patterns

### Mock Pattern

**When to Use:**

- External API calls
- Database operations
- File system operations
- Expensive operations

**Python (pytest-mock):**

```python
def test_api_call(mocker):
    mock_request = mocker.patch('requests.get')
    mock_request.return_value.json.return_value = {'data': 'test'}

    result = fetch_data()
    assert result == {'data': 'test'}
```

**JavaScript (Jest):**

```javascript
jest.mock('./api');
test('api call', () => {
  api.fetchData.mockResolvedValue({ data: 'test' });
  const result = await fetchData();
  expect(result).toEqual({ data: 'test' });
});
```

### Stub Pattern

**When to Use:**

- Replace dependencies with simple return values
- Control test data

**Example:**

```python
def test_with_stub():
    stub_db = StubDatabase()
    stub_db.set_return_value('get_user', User(id=1))

    service = UserService(stub_db)
    user = service.get_user(1)
    assert user.id == 1
```

### Spy Pattern

**When to Use:**

- Verify method calls without replacing behavior
- Count invocations

**Example:**

```python
def test_logs_message(mocker):
    spy_log = mocker.spy(logging, 'info')

    process_data()

    spy_log.assert_called_once_with('Processing started')
```

## Parametrization Patterns

### Data-Driven Tests

**Python (pytest):**

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
])
def test_uppercase(input, expected):
    assert input.upper() == expected
```

**JavaScript (Jest):**

```javascript
test.each([
  ['hello', 'HELLO'],
  ['world', 'WORLD'],
  ['', ''],
])('uppercase %s', (input, expected) => {
  expect(input.toUpperCase()).toBe(expected);
});
```

## Test Categories

### Unit Tests

- Test individual functions/methods
- Fast execution (< 1ms per test)
- No external dependencies
- Mock all external calls

### Integration Tests

- Test component interactions
- May use real dependencies (database, APIs)
- Slower than unit tests
- Test workflows, not individual functions

### End-to-End Tests

- Test complete user workflows
- Use real systems
- Slowest tests
- Fewest in number (test pyramid)

## Anti-Patterns

### ❌ Testing Implementation Details

**Bad:**

```python
def test_internal_state():
    assert user._internal_counter == 5  # Testing private attribute
```

**Good:**

```python
def test_behavior():
    assert user.is_ready()  # Testing public behavior
```

### ❌ Over-Mocking

**Bad:**

```python
def test_calculation(mocker):
    mocker.patch('math.add')
    mocker.patch('math.multiply')
    # Mocking everything, testing nothing
```

**Good:**

```python
def test_calculation():
    result = calculate(2, 3)
    assert result == 6  # Test actual behavior
```

### ❌ Test Interdependence

**Bad:**

```python
# Test 1
def test_create_user():
    user = User.create()  # Creates global state
    assert user.id == 1

# Test 2
def test_get_user():
    user = User.get(1)  # Depends on test 1
    assert user is not None
```

**Good:**

```python
# Each test is independent
def test_create_user():
    user = User.create()
    assert user.id is not None

def test_get_user():
    user = User.create()  # Creates its own data
    retrieved = User.get(user.id)
    assert retrieved.id == user.id
```

### ❌ Testing Multiple Things

**Bad:**

```python
def test_user():
    user = User.create()
    assert user.name == "Test"
    assert user.email == "test@example.com"
    assert user.is_active is True
    assert user.can_login() is True
    # Too many assertions, unclear what's being tested
```

**Good:**

```python
def test_user_creation():
    user = User.create(name="Test")
    assert user.name == "Test"

def test_user_email():
    user = User.create(email="test@example.com")
    assert user.email == "test@example.com"

def test_user_can_login():
    user = User.create()
    assert user.can_login() is True
```

### ❌ Slow Tests

**Bad:**

```python
def test_api_call():
    result = real_api_call()  # Slow network call
    assert result is not None
```

**Good:**

```python
def test_api_call(mocker):
    mock_api = mocker.patch('api.call')
    mock_api.return_value = {'data': 'test'}

    result = fetch_data()
    assert result == {'data': 'test'}
```

## Test Quality Indicators

### Good Tests

- ✅ Fast (< 1ms for unit tests)
- ✅ Independent (no shared state)
- ✅ Repeatable (same result every time)
- ✅ Self-validating (clear pass/fail)
- ✅ Timely (written before code)
- ✅ Clear names (describe behavior)
- ✅ One assertion per behavior

### Bad Tests

- ❌ Slow (> 100ms for unit tests)
- ❌ Dependent on other tests
- ❌ Flaky (sometimes pass, sometimes fail)
- ❌ Unclear what's being tested
- ❌ Written after code
- ❌ Vague names (`test1`, `test_function`)
- ❌ Multiple unrelated assertions

## TDD Workflow Patterns

### Micro-Cycle Pattern

1. **RED**: Write smallest failing test
2. **GREEN**: Write minimal code to pass
3. **REFACTOR**: Clean up code
4. **Repeat**: Next smallest test

### Feature Cycle Pattern

1. **RED**: Write test for feature
2. **GREEN**: Implement feature
3. **REFACTOR**: Improve implementation
4. **RED**: Write test for edge case
5. **GREEN**: Handle edge case
6. **REFACTOR**: Clean up

### Bug Fix Pattern

1. **RED**: Write test that reproduces bug
2. **GREEN**: Fix bug (test now passes)
3. **REFACTOR**: Improve fix if needed
4. **Verify**: Ensure no regressions
