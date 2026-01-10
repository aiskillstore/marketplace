# CI/CD Testing Patterns

Testing strategies for continuous integration pipelines.

## Test Pipeline Stages

```
┌─────────────────────────────────────────────────────────────────┐
│                        CI Pipeline                               │
│                                                                  │
│  ┌──────┐   ┌──────┐   ┌───────┐   ┌─────┐   ┌──────┐   ┌────┐│
│  │ Lint │ → │ Unit │ → │ Build │ → │Integ│ → │  E2E │ → │Dep.││
│  │      │   │Tests │   │       │   │Tests│   │Tests │   │    ││
│  └──────┘   └──────┘   └───────┘   └─────┘   └──────┘   └────┘│
│     1m        2-5m       1-3m       5-10m     10-30m      -   │
│                                                                  │
│  ◄─────── Fast Feedback ───────►  ◄─── Comprehensive ──────►   │
└─────────────────────────────────────────────────────────────────┘
```

## GitHub Actions Example

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Lint
        run: |
          pip install ruff
          ruff check .

  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -e .[test]
      - name: Run unit tests
        run: pytest tests/unit -v --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v4

  integration-tests:
    needs: unit-tests
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Run integration tests
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/test
        run: pytest tests/integration -v

  e2e-tests:
    needs: integration-tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run E2E tests
        run: |
          docker-compose up -d
          pytest tests/e2e -v
          docker-compose down
```

## Test Parallelization

### pytest-xdist

```yaml
- name: Run tests in parallel
  run: pytest -n auto  # Use all available CPUs

- name: Run with specific workers
  run: pytest -n 4  # 4 parallel workers
```

### Matrix Testing

```yaml
jobs:
  test:
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']
        os: [ubuntu-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pytest
```

### Sharded Tests

```yaml
jobs:
  test:
    strategy:
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - name: Run test shard
        run: pytest --shard-id=${{ matrix.shard }} --num-shards=4
```

## Caching for Speed

```yaml
- name: Cache pip packages
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-

- name: Cache pytest
  uses: actions/cache@v4
  with:
    path: .pytest_cache
    key: pytest-${{ github.sha }}
    restore-keys: pytest-
```

## Flaky Test Handling

### Retry Mechanism

```yaml
- name: Run tests with retry
  uses: nick-fields/retry@v3
  with:
    timeout_minutes: 10
    max_attempts: 3
    command: pytest tests/e2e
```

### pytest-rerunfailures

```bash
# Rerun failed tests up to 3 times
pytest --reruns 3 --reruns-delay 1
```

### Quarantine Flaky Tests

```python
@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_sometimes_fails():
    # This test is known to be flaky
    pass

@pytest.mark.skip(reason="Flaky - investigating")
def test_quarantined():
    pass
```

## Test Reports

### JUnit XML

```yaml
- name: Run tests
  run: pytest --junitxml=results.xml

- name: Publish Test Results
  uses: dorny/test-reporter@v1
  if: always()
  with:
    name: Test Results
    path: results.xml
    reporter: java-junit
```

### Coverage Reports

```yaml
- name: Run with coverage
  run: pytest --cov=src --cov-report=xml --cov-report=html

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  with:
    files: ./coverage.xml
    fail_ci_if_error: true

- name: Coverage comment on PR
  uses: py-cov-action/python-coverage-comment-action@v3
```

## Branch Protection Rules

```yaml
# Require tests to pass before merge
# Settings → Branches → Branch protection rules

Required status checks:
  - lint
  - unit-tests
  - integration-tests

Require branches to be up to date: Yes
```

## Test Selection

### Changed Files Only

```yaml
- name: Get changed files
  id: changed
  uses: tj-actions/changed-files@v41
  with:
    files: |
      src/**
      tests/**

- name: Run affected tests
  if: steps.changed.outputs.any_changed == 'true'
  run: pytest tests/ -v
```

### Skip Expensive Tests

```yaml
- name: Quick tests on PR
  if: github.event_name == 'pull_request'
  run: pytest -m "not slow and not e2e"

- name: Full tests on main
  if: github.ref == 'refs/heads/main'
  run: pytest
```

## Secrets in Tests

```yaml
- name: Run tests with secrets
  env:
    API_KEY: ${{ secrets.TEST_API_KEY }}
    DATABASE_URL: ${{ secrets.TEST_DATABASE_URL }}
  run: pytest tests/integration

# Use environment for sensitive tests
jobs:
  integration:
    environment: testing  # Requires approval
    steps:
      - run: pytest tests/integration
```

## Best Practices

1. **Fast feedback first** - Run linting and unit tests before slow tests
2. **Fail fast** - Stop pipeline on first failure (`pytest -x`)
3. **Parallel when possible** - Use matrix builds and xdist
4. **Cache aggressively** - Pip, node_modules, docker layers
5. **Keep tests deterministic** - No reliance on external state
6. **Isolate flaky tests** - Quarantine or fix, don't ignore
7. **Report clearly** - Use test reporters and coverage comments
8. **Secure secrets** - Never log, use GitHub secrets
