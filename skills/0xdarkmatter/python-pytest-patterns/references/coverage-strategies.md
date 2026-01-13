# Coverage Strategies

Comprehensive code coverage with pytest-cov.

## Setup

```bash
pip install pytest-cov
```

## Basic Usage

```bash
# Run with coverage
pytest --cov=src

# With terminal report
pytest --cov=src --cov-report=term

# With HTML report
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Multiple formats
pytest --cov=src --cov-report=term --cov-report=html --cov-report=xml
```

## Coverage Configuration

### pyproject.toml

```toml
[tool.coverage.run]
source = ["src"]
branch = true
omit = [
    "*/tests/*",
    "*/__init__.py",
    "*/migrations/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:",
]
fail_under = 80
show_missing = true

[tool.coverage.html]
directory = "htmlcov"
```

### .coveragerc (Alternative)

```ini
[run]
source = src
branch = true
omit =
    */tests/*
    */__init__.py

[report]
exclude_lines =
    pragma: no cover
    raise NotImplementedError
fail_under = 80

[html]
directory = htmlcov
```

## Branch Coverage

```python
# branch=true catches this
def process(value):
    if value > 0:
        return "positive"
    # Missing else branch without branch coverage
    return "non-positive"

# Test both branches
def test_positive():
    assert process(5) == "positive"

def test_non_positive():
    assert process(-1) == "non-positive"
```

## Excluding Code

```python
def debug_only():  # pragma: no cover
    """Never executed in production."""
    print("Debug info")

if TYPE_CHECKING:  # Excluded by default config
    from typing import Optional

def platform_specific():
    if sys.platform == "win32":  # pragma: no cover
        return windows_implementation()
    return unix_implementation()
```

## Coverage in CI

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -e .[test]

      - name: Run tests with coverage
        run: pytest --cov=src --cov-report=xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
          fail_ci_if_error: true
```

### Fail on Low Coverage

```bash
# Fail if coverage below 80%
pytest --cov=src --cov-fail-under=80
```

## Measuring Coverage of Specific Tests

```bash
# Coverage for specific test file
pytest tests/test_api.py --cov=src/api

# Coverage for marked tests only
pytest -m "unit" --cov=src

# Coverage for specific module
pytest --cov=src/module_name
```

## Combining Coverage

```bash
# Run tests in parallel, combine coverage
pytest -n auto --cov=src --cov-append

# Or manually combine
coverage combine
coverage report
```

## Coverage Diff (Incremental)

```bash
# Show coverage for changed lines only (with diff-cover)
pip install diff-cover

pytest --cov=src --cov-report=xml
diff-cover coverage.xml --compare-branch=origin/main
```

## Mutation Testing

```bash
# Beyond coverage: test quality with mutmut
pip install mutmut

# Run mutation testing
mutmut run --paths-to-mutate=src/

# View results
mutmut results
mutmut html
```

## Coverage Reports

### Terminal Report

```bash
pytest --cov=src --cov-report=term-missing
```

Output:
```
Name                      Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------------------------
src/api.py                   50      5     12      2    88%   45-49, 67
src/utils.py                 30      0      8      0   100%
---------------------------------------------------------------------
TOTAL                        80      5     20      2    92%
```

### HTML Report

```bash
pytest --cov=src --cov-report=html
# Creates htmlcov/index.html with line-by-line highlighting
```

### XML Report (CI)

```bash
pytest --cov=src --cov-report=xml
# Creates coverage.xml for CI tools
```

### JSON Report

```bash
pytest --cov=src --cov-report=json
# Creates coverage.json for programmatic access
```

## Coverage Best Practices

### 1. Aim for Meaningful Coverage

```python
# BAD: 100% coverage but no assertions
def test_function():
    result = my_function()  # Just call it

# GOOD: Meaningful assertions
def test_function():
    result = my_function()
    assert result.status == "success"
    assert len(result.items) > 0
```

### 2. Don't Chase 100%

```python
# Some code genuinely shouldn't be tested
def __repr__(self):  # pragma: no cover
    return f"<User {self.name}>"

if __name__ == "__main__":  # pragma: no cover
    main()
```

### 3. Focus on Critical Paths

```python
# Prioritize coverage for:
# - Business logic
# - Error handling
# - Edge cases
# - Security-sensitive code
```

### 4. Use Branch Coverage

```toml
[tool.coverage.run]
branch = true
```

### 5. Track Coverage Trends

```yaml
# In CI: fail on coverage decrease
- name: Check coverage
  run: |
    pytest --cov=src --cov-report=xml
    diff-cover coverage.xml --compare-branch=origin/main --fail-under=90
```

## Quick Reference

| Command | Description |
|---------|-------------|
| `--cov=src` | Enable coverage for src/ |
| `--cov-report=term` | Terminal report |
| `--cov-report=html` | HTML report |
| `--cov-report=xml` | XML report (CI) |
| `--cov-fail-under=80` | Fail if under 80% |
| `--cov-branch` | Enable branch coverage |
| `--cov-append` | Append to existing data |
| `--no-cov` | Disable coverage |
