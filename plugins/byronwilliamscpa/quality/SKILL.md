# Code Quality Skill

Code quality validation, formatting, linting, and pre-commit checks.

## Activation

Auto-activates on keywords: quality, lint, format, precommit, naming, black, ruff, mypy, basedpyright, validation

## Workflows

### Formatting
- **format.md**: Code formatting with Black and Ruff

### Linting
- **lint.md**: Linting checks with Ruff
- **naming.md**: Naming convention validation

### Pre-commit
- **precommit.md**: Pre-commit hook validation

## Commands

```bash
# Format code
uv run black .
uv run ruff format .

# Lint code
uv run ruff check .
uv run ruff check --fix .

# Type checking
uv run basedpyright src/

# Run all pre-commit hooks
uv run pre-commit run --all-files
```

## Quality Standards

### Python Standards
- **Line Length**: 88 characters (Black default)
- **Type Checking**: BasedPyright strict mode
- **Linting**: Ruff with PyStrict-aligned rules

### Rule Categories
- **BLE**: Blind except detection
- **EM**: Error message best practices
- **SLF**: Private member access violations
- **INP**: Require `__init__.py` in packages
- **T10**: No debugger statements
- **G**: Logging format strings

### Per-File Ignores
Tests and scripts have relaxed rules for pragmatic development.
