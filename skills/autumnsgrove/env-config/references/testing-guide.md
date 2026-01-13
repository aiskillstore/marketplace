# Configuration Testing Guide

## pytest with Environment Variables

### Test Configuration Setup

Create `conftest.py`:

```python
import pytest
import os
from pathlib import Path


@pytest.fixture
def test_env():
    """Set up test environment variables."""
    original = os.environ.copy()

    # Set test values
    os.environ['APP_ENV'] = 'testing'
    os.environ['DEBUG'] = 'true'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['APP_NAME'] = 'TestApp'

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original)


@pytest.fixture
def config(test_env):
    """Provide clean config for each test."""
    from config import Config
    return Config(env='testing')


@pytest.fixture
def temp_env_file(tmp_path):
    """Create temporary .env file for testing."""
    env_file = tmp_path / ".env"
    env_content = """
APP_NAME=TestApp
APP_ENV=testing
DEBUG=true
DATABASE_URL=sqlite:///:memory:
"""
    env_file.write_text(env_content)
    return env_file
```

### Basic Configuration Tests

`test_config.py`:

```python
import pytest
import os
from config import Config, ConfigError


def test_config_loading(config):
    """Test configuration loads correctly."""
    assert config.app_env == 'testing'
    assert config.debug is True
    assert config.app_name == 'TestApp'


def test_missing_required_var():
    """Test error raised for missing required variables."""
    # Remove required var
    old_val = os.environ.pop('APP_NAME', None)

    try:
        with pytest.raises(ConfigError):
            Config()
    finally:
        if old_val:
            os.environ['APP_NAME'] = old_val


def test_environment_specific_loading(tmp_path):
    """Test environment-specific .env file loading."""
    # Create development env file
    dev_env = tmp_path / ".env.development"
    dev_env.write_text("APP_NAME=DevApp\nDEBUG=true")

    # Change to temp directory
    os.chdir(tmp_path)

    config = Config(env='development')
    assert config.app_name == 'DevApp'
    assert config.debug is True


def test_boolean_parsing(config):
    """Test boolean environment variable parsing."""
    os.environ['DEBUG'] = 'true'
    assert config.debug is True

    os.environ['DEBUG'] = 'false'
    config._load_env_file()
    assert config.debug is False

    os.environ['DEBUG'] = '1'
    config._load_env_file()
    assert config.debug is True


def test_optional_values(config):
    """Test optional configuration values."""
    # Remove optional key
    os.environ.pop('OPENAI_API_KEY', None)

    # Should not raise error
    assert config.openai_api_key is None


def test_default_values(config):
    """Test default values when env vars not set."""
    os.environ.pop('LOG_LEVEL', None)
    assert config.log_level == 'INFO'
```

### Integration Tests

```python
def test_full_application_startup(tmp_path):
    """Test complete application configuration flow."""
    # Create .env file
    env_file = tmp_path / ".env"
    env_file.write_text("""
APP_NAME=IntegrationTest
APP_ENV=testing
DEBUG=true
DATABASE_URL=postgresql://localhost/test_db
ANTHROPIC_API_KEY=sk-test-key
SECRET_KEY=test-secret-key
""")

    os.chdir(tmp_path)

    # Initialize config
    config = Config()

    # Verify all settings
    assert config.app_name == 'IntegrationTest'
    assert config.database_url == 'postgresql://localhost/test_db'
    assert config.anthropic_api_key == 'sk-test-key'
    assert config.secret_key == 'test-secret-key'


def test_multi_environment_priority(tmp_path):
    """Test that environment-specific files override base .env."""
    # Create base .env
    base_env = tmp_path / ".env"
    base_env.write_text("APP_NAME=BaseApp\nDEBUG=false")

    # Create environment-specific .env
    prod_env = tmp_path / ".env.production"
    prod_env.write_text("APP_NAME=ProdApp\nDEBUG=false")

    os.chdir(tmp_path)

    config = Config(env='production')

    # Should use production-specific value
    assert config.app_name == 'ProdApp'
```

### Error Handling Tests

```python
def test_missing_env_file_handling():
    """Test graceful handling of missing .env files."""
    # Should not crash, just use defaults or env vars
    os.environ['APP_NAME'] = 'TestApp'
    os.environ['APP_ENV'] = 'testing'

    config = Config()
    assert config.app_name == 'TestApp'


def test_malformed_env_file(tmp_path):
    """Test handling of malformed .env files."""
    env_file = tmp_path / ".env"
    env_file.write_text("INVALID LINE WITHOUT EQUALS")

    os.chdir(tmp_path)

    # Should still load, python-dotenv is forgiving
    config = Config()


def test_production_without_secret_key():
    """Test that production requires SECRET_KEY."""
    os.environ['APP_ENV'] = 'production'
    os.environ['DEBUG'] = 'false'
    os.environ.pop('SECRET_KEY', None)

    config = Config(env='production')

    with pytest.raises(ConfigError):
        _ = config.secret_key
```

## Testing Secrets Loading

### JSON Secrets Tests

```python
from secrets_loader import load_secrets


def test_secrets_from_json(tmp_path):
    """Test loading secrets from JSON file."""
    secrets_file = tmp_path / "secrets.json"
    secrets_file.write_text(json.dumps({
        "anthropic_api_key": "sk-test-123",
        "openai_api_key": "sk-openai-456"
    }))

    os.chdir(tmp_path)

    secrets = load_secrets()
    assert secrets['anthropic_api_key'] == 'sk-test-123'
    assert secrets['openai_api_key'] == 'sk-openai-456'


def test_secrets_fallback_to_env():
    """Test fallback to environment variables."""
    os.environ['ANTHROPIC_API_KEY'] = 'env-key-123'

    # No secrets.json exists
    secrets = load_secrets('nonexistent.json')

    assert secrets['anthropic_api_key'] == 'env-key-123'


def test_malformed_json_secrets(tmp_path):
    """Test handling of malformed JSON secrets file."""
    secrets_file = tmp_path / "secrets.json"
    secrets_file.write_text("{ invalid json }")

    os.chdir(tmp_path)

    # Should fallback to environment variables
    os.environ['ANTHROPIC_API_KEY'] = 'fallback-key'
    secrets = load_secrets()

    assert secrets['anthropic_api_key'] == 'fallback-key'
```

## Mocking Environment Variables

### Using pytest-env

Install: `uv add --dev pytest-env`

Configure in `pytest.ini`:

```ini
[pytest]
env =
    APP_ENV=testing
    DEBUG=true
    DATABASE_URL=sqlite:///:memory:
```

### Using unittest.mock

```python
from unittest.mock import patch


def test_config_with_mock():
    """Test configuration with mocked environment."""
    with patch.dict(os.environ, {
        'APP_NAME': 'MockedApp',
        'APP_ENV': 'testing',
        'DEBUG': 'true'
    }):
        config = Config()
        assert config.app_name == 'MockedApp'


def test_api_key_present():
    """Test behavior when API key is present."""
    with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
        config = Config()
        assert config.anthropic_api_key == 'test-key'


def test_api_key_absent():
    """Test behavior when API key is absent."""
    with patch.dict(os.environ, {}, clear=True):
        os.environ['APP_NAME'] = 'TestApp'
        os.environ['APP_ENV'] = 'testing'
        config = Config()
        assert config.anthropic_api_key is None
```

## Validation Testing

### Pydantic Config Tests

```python
from pydantic import ValidationError
from config_pydantic import Settings


def test_valid_settings():
    """Test valid settings creation."""
    with patch.dict(os.environ, {
        'APP_NAME': 'TestApp',
        'DATABASE_URL': 'postgresql://localhost/db'
    }):
        settings = Settings()
        assert settings.app_name == 'TestApp'


def test_invalid_env_value():
    """Test validation error for invalid environment."""
    with patch.dict(os.environ, {
        'APP_ENV': 'invalid',
        'DATABASE_URL': 'postgresql://localhost/db'
    }):
        with pytest.raises(ValidationError):
            Settings()


def test_missing_required_field():
    """Test validation error for missing required field."""
    with patch.dict(os.environ, {'APP_NAME': 'TestApp'}):
        # Missing required DATABASE_URL
        with pytest.raises(ValidationError):
            Settings()


def test_type_coercion():
    """Test automatic type coercion."""
    with patch.dict(os.environ, {
        'DEBUG': 'true',
        'DATABASE_POOL_SIZE': '10',
        'DATABASE_URL': 'postgresql://localhost/db'
    }):
        settings = Settings()
        assert settings.debug is True
        assert settings.database_pool_size == 10
        assert isinstance(settings.database_pool_size, int)
```

## Coverage and Quality

### Test Coverage Goals

Aim for:
- 95%+ coverage on configuration loading
- 100% coverage on validation logic
- 100% coverage on error handling

Run coverage:

```bash
uv run pytest --cov=config --cov-report=html
```

### Property-Based Testing

Use Hypothesis for property-based tests:

```bash
uv add --dev hypothesis
```

```python
from hypothesis import given, strategies as st


@given(st.text(min_size=1))
def test_any_app_name_accepted(app_name):
    """Test that any non-empty string is valid for APP_NAME."""
    with patch.dict(os.environ, {
        'APP_NAME': app_name,
        'APP_ENV': 'testing'
    }):
        config = Config()
        assert config.app_name == app_name


@given(st.booleans())
def test_debug_boolean_handling(debug_value):
    """Test debug flag handles all boolean values."""
    with patch.dict(os.environ, {
        'DEBUG': str(debug_value).lower(),
        'APP_NAME': 'TestApp',
        'APP_ENV': 'testing'
    }):
        config = Config()
        assert isinstance(config.debug, bool)
```

## CI/CD Testing

### GitHub Actions Example

```yaml
name: Test Configuration

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install UV
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install dependencies
        run: uv sync

      - name: Run tests
        env:
          APP_ENV: testing
          APP_NAME: CI-Test
        run: uv run pytest

      - name: Check coverage
        run: uv run pytest --cov=config --cov-fail-under=90
```

### Testing in Docker

```dockerfile
FROM python:3.11-slim

RUN pip install uv
WORKDIR /app
COPY . .
RUN uv sync --dev

# Set test environment
ENV APP_ENV=testing
ENV APP_NAME=DockerTest

CMD ["uv", "run", "pytest"]
```
