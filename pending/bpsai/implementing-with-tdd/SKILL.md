---
name: implementing-with-tdd
description: Use when implementing bug fixes, features, or any code changes where test-first development is appropriate.
---

# TDD Implementation

## PairCoder Integration

When implementing via TDD in this project:

1. **Start task**: `bpsai-pair task update TASK-XXX --status in_progress`
2. **Write test** in `tests/test_<module>.py`
3. **Run test**: `pytest tests/test_<module>.py -v` (expect RED)
4. **Implement** in `tools/cli/bpsai_pair/`
5. **Run test**: `pytest tests/test_<module>.py -v` (expect GREEN)
6. **Refactor** if needed, keeping tests green
7. **Complete**: Follow managing-task-lifecycle skill for two-step completion

## Project Test Commands

```bash
# Run specific test
pytest tests/test_module.py::test_function -v

# Run all tests
pytest

# Run with coverage
pytest --cov=tools/cli/bpsai_pair

# Run only failed tests
pytest --lf

# Stop on first failure
pytest -x

# Show print output
pytest -s
```

## Project Test Conventions

- Test files: `tests/test_<module>.py`
- Test functions: `test_<function>_<scenario>_<expected>()`
- Use fixtures from `tests/conftest.py`
- Mock external services (Trello API, etc.)

## Linting

```bash
# Check linting
ruff check .

# Auto-fix
ruff check --fix .
```

## Run All Checks

```bash
bpsai-pair ci    # Runs tests + linting + type checks in one command
```

## Task Completion

After tests pass, follow the managing-task-lifecycle skill:
1. `bpsai-pair ttask done TRELLO-XX --summary "..." --list "Deployed/Done"`
2. `bpsai-pair task update TASK-XXX --status done`
