# CI/CD Integration

## GitHub Actions Example

```yaml
name: Playwright Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Install Playwright Browsers
      run: playwright install --with-deps

    - name: Run Playwright tests
      run: pytest tests/ --browser chromium --browser firefox

    - name: Upload test results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: playwright-report
        path: playwright-report/
        retention-days: 30

    - name: Upload screenshots
      if: failure()
      uses: actions/upload-artifact@v3
      with:
        name: screenshots
        path: test-results/
        retention-days: 7
```

## Docker Example

```dockerfile
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["pytest", "tests/", "--browser", "chromium"]
```

## Common Commands

```bash
# Install Playwright
pip install playwright pytest-playwright

# Install browsers
playwright install

# Run tests
pytest tests/

# Run specific browser
pytest --browser chromium
pytest --browser firefox
pytest --browser webkit

# Run in headed mode
pytest --headed

# Run with slowmo
pytest --slowmo=1000

# Generate test code
playwright codegen https://example.com

# Debug mode
PWDEBUG=1 pytest tests/test_login.py

# Parallel execution
pytest -n auto

# Show browser on failure only
pytest --headed --screenshot on --video retain-on-failure
```
