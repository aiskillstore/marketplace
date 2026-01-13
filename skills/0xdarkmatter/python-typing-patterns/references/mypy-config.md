# mypy and pyright Configuration

Type checker setup for strict, practical type safety.

## mypy Configuration

### pyproject.toml (Recommended)

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_ignores = true
show_error_codes = true
show_error_context = true

# Paths
files = ["src", "tests"]
exclude = [
    "migrations/",
    "venv/",
    "__pycache__/",
]

# Per-module overrides
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[[tool.mypy.overrides]]
module = [
    "requests.*",
    "boto3.*",
    "botocore.*",
]
ignore_missing_imports = true
```

### mypy.ini (Alternative)

```ini
[mypy]
python_version = 3.11
strict = True
warn_return_any = True
warn_unused_ignores = True
show_error_codes = True

[mypy-tests.*]
disallow_untyped_defs = False

[mypy-requests.*]
ignore_missing_imports = True
```

## mypy Flags Explained

### Strict Mode Components

```toml
[tool.mypy]
# strict = true enables all of these:
warn_unused_configs = true
disallow_any_generics = true
disallow_subclassing_any = true
disallow_untyped_calls = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_return_any = true
no_implicit_reexport = true
strict_equality = true
extra_checks = true
```

### Commonly Adjusted Flags

```toml
[tool.mypy]
# Allow untyped defs in some files
disallow_untyped_defs = true

# But not for tests
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

# Ignore third-party stubs
ignore_missing_imports = true  # Global fallback

# Show where errors occur
show_error_context = true
show_column_numbers = true
show_error_codes = true

# Error output format
pretty = true
```

## pyright Configuration

### pyrightconfig.json

```json
{
  "include": ["src"],
  "exclude": ["**/node_modules", "**/__pycache__", "venv"],
  "pythonVersion": "3.11",
  "pythonPlatform": "All",
  "typeCheckingMode": "strict",
  "reportMissingImports": true,
  "reportMissingTypeStubs": false,
  "reportUnusedImport": true,
  "reportUnusedClass": true,
  "reportUnusedFunction": true,
  "reportUnusedVariable": true,
  "reportDuplicateImport": true,
  "reportPrivateUsage": true,
  "reportConstantRedefinition": true,
  "reportIncompatibleMethodOverride": true,
  "reportIncompatibleVariableOverride": true,
  "reportInconsistentConstructor": true,
  "reportOverlappingOverload": true,
  "reportUninitializedInstanceVariable": true
}
```

### pyproject.toml (pyright)

```toml
[tool.pyright]
include = ["src"]
exclude = ["**/node_modules", "**/__pycache__", "venv"]
pythonVersion = "3.11"
typeCheckingMode = "strict"
reportMissingTypeStubs = false
```

## Type Checking Modes

### pyright Modes

```json
{
  "typeCheckingMode": "off"    // No checking
  "typeCheckingMode": "basic"  // Basic checks
  "typeCheckingMode": "standard" // Standard checks
  "typeCheckingMode": "strict"  // All checks enabled
}
```

## Inline Type Ignores

```python
# Ignore specific error
result = some_call()  # type: ignore[arg-type]

# Ignore all errors on line
result = some_call()  # type: ignore

# With mypy error code
value = data["key"]  # type: ignore[typeddict-item]

# With pyright
result = func()  # pyright: ignore[reportGeneralTypeIssues]
```

## Type Stub Files (.pyi)

```python
# mymodule.pyi - Type stubs for mymodule.py

def process(data: dict[str, int]) -> list[int]: ...

class Handler:
    def __init__(self, name: str) -> None: ...
    def handle(self, event: Event) -> bool: ...
```

### Stub Package Structure

```
stubs/
├── mypackage/
│   ├── __init__.pyi
│   ├── module.pyi
│   └── subpackage/
│       └── __init__.pyi
```

```toml
[tool.mypy]
mypy_path = "stubs"
```

## CI Integration

### GitHub Actions

```yaml
name: Type Check

on: [push, pull_request]

jobs:
  mypy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install mypy
          pip install -e .[dev]

      - name: Run mypy
        run: mypy src/

  pyright:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -e .[dev]

      - name: Run pyright
        uses: jakebailey/pyright-action@v2
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
        args: [--strict]
```

## Common Type Stubs

```bash
# Install type stubs
pip install types-requests
pip install types-redis
pip install types-PyYAML
pip install boto3-stubs[essential]

# Or use mypy to find missing stubs
mypy --install-types src/
```

## Gradual Typing Strategy

### Phase 1: Basic

```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_ignores = true
```

### Phase 2: Stricter

```toml
[tool.mypy]
python_version = "3.11"
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
```

### Phase 3: Strict

```toml
[tool.mypy]
python_version = "3.11"
strict = true

# Temporarily ignore problem areas
[[tool.mypy.overrides]]
module = "legacy.*"
ignore_errors = true
```

## Quick Reference

| mypy Flag | Description |
|-----------|-------------|
| `--strict` | Enable all strict checks |
| `--show-error-codes` | Show error codes for ignores |
| `--ignore-missing-imports` | Skip untyped libraries |
| `--python-version 3.11` | Target Python version |
| `--install-types` | Install missing stubs |
| `--config-file` | Specify config file |

| pyright Mode | Description |
|--------------|-------------|
| `off` | No checking |
| `basic` | Minimal checks |
| `standard` | Recommended |
| `strict` | All checks |
