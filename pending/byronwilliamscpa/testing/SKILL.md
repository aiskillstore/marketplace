# Testing Skill

Automated test generation, review, and execution for pytest-based projects.

## Activation

Auto-activates on keywords: test, coverage, pytest, unittest, integration test, e2e, performance, benchmark, security testing

## Workflows

### Test Generation
- **generate.md**: Generate test cases for code

### Test Review
- **review.md**: Review existing tests for quality

### Specialized Testing
- **e2e.md**: End-to-end testing patterns
- **security.md**: Security testing patterns
- **performance.md**: Performance testing patterns

## Context Files

- **pytest-commands.md**: Common pytest commands
- **pytest-patterns.md**: Testing patterns and best practices

## Commands

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/fragrance_rater --cov-report=html --cov-report=term-missing

# Run specific test categories
uv run pytest -m "not slow"
uv run pytest -m "integration"
uv run pytest -m "unit"

# Run with verbose output
uv run pytest -v --tb=short

# Run mutation testing
uv run mutmut run --paths-to-mutate=src/

# Run property-based tests
uv run pytest --hypothesis-show-statistics
```

## Coverage Standards

- **Minimum Coverage**: 80%
- **Branch Coverage**: Enabled
- **Coverage Report**: HTML and terminal output

## Test Organization

```
tests/
├── unit/           # Unit tests (fast, isolated)
├── integration/    # Integration tests (may use external services)
├── e2e/           # End-to-end tests (full system)
├── security/      # Security-focused tests
├── performance/   # Performance and load tests
└── conftest.py    # Shared fixtures
```

## Testing Patterns

### AAA Pattern (Arrange-Act-Assert)
```python
def test_example():
    # Arrange
    input_data = create_test_data()

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected_output
```

### Fixtures
```python
@pytest.fixture
def sample_data():
    return {"key": "value"}

def test_with_fixture(sample_data):
    assert sample_data["key"] == "value"
```
