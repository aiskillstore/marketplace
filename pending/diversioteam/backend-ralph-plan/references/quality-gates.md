# Quality Gates Reference

This reference documents the quality gates used in backend RALPH plans.

## Gate Overview

| Gate | Purpose | Failure Action |
|------|---------|----------------|
| Pre-commit | Catch formatting, imports, trailing whitespace | Fix all issues |
| Lint | Static analysis, code quality | Fix all errors |
| Format | Code formatting consistency | Run formatter |
| Types | Type safety verification | Fix type errors |
| Tests | Functionality verification | Fix failing tests |
| Coverage | Test completeness | Add more tests |
| Django | Framework checks | Fix Django issues |
| Shortcuts | Code quality (no TODOs) | Remove shortcuts |

## Default Commands

These are the default commands. Projects may use wrappers (e.g., `.bin/ruff`).

### Pre-commit

```bash
# Via skill (recommended)
/pre-commit

# Via command
pre-commit run --all-files
```

Runs:
- Ruff formatting and linting
- Import sorting (isort/ruff)
- Trailing whitespace removal
- YAML/JSON validation
- Django checks
- Project-specific hooks

### Linting

```bash
# Check
ruff check <path>

# Check and fix
ruff check <path> --fix

# Format
ruff format <path>
```

### Type Checking

```bash
# Using ty (if available)
ty <path>

# Using mypy
mypy <path>

# Using pyright
pyright <path>
```

### Testing

```bash
# Basic
pytest <test_path> -k "<filter>"

# With coverage
pytest <test_path> -k "<filter>" --cov=<source_path> --cov-report=term-missing

# With Django configuration
pytest <test_path> -k "<filter>" --dc=TestLocalApp

# Verbose
pytest <test_path> -k "<filter>" -v
```

### Django Checks

```bash
# System checks
django check

# With specific configuration
django check --configuration=TestLocalApp

# Migration check
django migrate --check

# With specific configuration
django migrate --check --configuration=TestLocalApp
```

### Shortcut Detection

```bash
# Find TODO/FIXME/etc.
grep -r "TODO\|FIXME\|XXX\|HACK" <path>

# Find type ignore comments
grep -r "noqa\|type: ignore" <path>

# Find Any type hints
grep -r ": Any" <path>
```

## Project-Specific Wrappers

Many projects use wrapper scripts. Common patterns:

### .bin/ wrappers (Django4Lyfe style)

```bash
.bin/ruff check <path>
.bin/ruff format <path>
.bin/ty <path>
.bin/pytest <args>
.bin/django <command>
```

### Poetry/PDM

```bash
poetry run ruff check <path>
poetry run pytest <args>

pdm run ruff check <path>
pdm run pytest <args>
```

### Make targets

```bash
make lint
make test
make typecheck
```

## Verification Checklist (Full)

Run after each task completion:

```bash
# 1. Pre-commit
/pre-commit
# OR: pre-commit run --all-files

# 2. Lint + Format
{{LINT_CMD}} {{APP_PATH}}{{MODULE_PATH}} --fix
{{FORMAT_CMD}} {{APP_PATH}}{{MODULE_PATH}}

# 3. Type check
{{TYPE_CMD}} {{APP_PATH}}{{MODULE_PATH}}

# 4. Django checks
{{DJANGO_CMD}} check

# 5. Tests (all feature tests, not just new)
{{TEST_CMD}} {{APP_PATH}}tests/{{MODULE_PATH}} -k {{TEST_FILTER}} {{TEST_CONFIG}} -v

# 6. Coverage
{{TEST_CMD}} {{APP_PATH}}tests/{{MODULE_PATH}} -k {{TEST_FILTER}} {{TEST_CONFIG}} \
  --cov={{APP_PATH}}{{MODULE_PATH}} --cov-report=term-missing

# 7. Shortcut check
grep -rE "TODO|FIXME|XXX|HACK|noqa|type: ignore" {{APP_PATH}}{{MODULE_PATH}} \
  && echo "❌ Found shortcuts" || echo "✓ Clean"

# 8. Acceptance criteria
# Manual: verify all checkboxes in task file are checked
```

## Coverage Targets

| Project Type | Recommended Target |
|--------------|-------------------|
| New feature | ≥90% |
| Bug fix | ≥85% (existing + new) |
| Refactor | Maintain existing |
| Critical path | ≥95% |

## Common Failures and Fixes

### Lint Failures

| Error | Fix |
|-------|-----|
| Line too long | Break line or configure line-length |
| Unused import | Remove import |
| Undefined name | Add import or fix typo |
| Missing trailing comma | Add comma |

### Type Failures

| Error | Fix |
|-------|-----|
| Incompatible types | Fix type mismatch |
| Missing return type | Add return annotation |
| Missing parameter type | Add parameter annotation |
| Cannot infer type | Add explicit annotation |

### Test Failures

| Error | Fix |
|-------|-----|
| AssertionError | Fix implementation or fix test expectation |
| ImportError | Fix import path |
| AttributeError | Fix attribute access |
| Database error | Check migrations, fixtures |

### Django Check Failures

| Error | Fix |
|-------|-----|
| Missing migration | Create migration |
| Invalid model field | Fix field definition |
| Circular import | Restructure imports |
| Missing setting | Add to settings |
