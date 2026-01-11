# Configuration API Reference

## Config Class Implementation

### Basic Config Class

```python
"""
Environment configuration management with UV.
Loads and validates environment variables.
"""
import os
import sys
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class ConfigError(Exception):
    """Raised when required configuration is missing."""
    pass


class Config:
    """Application configuration from environment variables."""

    def __init__(self, env: str = None):
        """
        Initialize configuration.

        Args:
            env: Environment name (development, staging, production)
                 If None, uses APP_ENV environment variable
        """
        # Determine environment
        self.env = env or os.getenv('APP_ENV', 'development')

        # Load environment-specific .env file
        self._load_env_file()

        # Validate required variables
        self._validate_required()

    def _load_env_file(self):
        """Load appropriate .env file based on environment."""
        # Try environment-specific file first
        env_file = Path(f'.env.{self.env}')
        if env_file.exists():
            load_dotenv(env_file, override=True)
            print(f"✓ Loaded configuration from {env_file}")

        # Then load .env (can override)
        if Path('.env').exists():
            load_dotenv('.env', override=False)  # Don't override env-specific
            print("✓ Loaded configuration from .env")

    def _validate_required(self):
        """Validate that required environment variables are set."""
        required = self.get_required_vars()
        missing = [var for var in required if not os.getenv(var)]

        if missing:
            raise ConfigError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                f"Please check .env.template for required configuration."
            )

    @staticmethod
    def get_required_vars() -> list[str]:
        """
        Define required environment variables.
        Override this in subclasses for custom requirements.
        """
        return [
            'APP_NAME',
            'APP_ENV',
        ]

    # Application Settings
    @property
    def app_name(self) -> str:
        return os.getenv('APP_NAME', 'MyApp')

    @property
    def app_env(self) -> str:
        return self.env

    @property
    def debug(self) -> bool:
        return os.getenv('DEBUG', 'false').lower() in ('true', '1', 'yes')

    @property
    def log_level(self) -> str:
        return os.getenv('LOG_LEVEL', 'INFO')

    # Database
    @property
    def database_url(self) -> Optional[str]:
        return os.getenv('DATABASE_URL')

    # API Keys
    @property
    def anthropic_api_key(self) -> Optional[str]:
        return os.getenv('ANTHROPIC_API_KEY')

    @property
    def openai_api_key(self) -> Optional[str]:
        return os.getenv('OPENAI_API_KEY')

    # Security
    @property
    def secret_key(self) -> str:
        key = os.getenv('SECRET_KEY')
        if not key and not self.debug:
            raise ConfigError("SECRET_KEY must be set in production")
        return key or 'dev-secret-key-change-in-production'


# Global config instance
config = Config()


# Helper function for getting env vars with defaults
def get_env(key: str, default: str = None, required: bool = False) -> str:
    """
    Get environment variable with optional default and validation.

    Args:
        key: Environment variable name
        default: Default value if not set
        required: If True, raises error when not set

    Returns:
        Environment variable value

    Raises:
        ConfigError: If required=True and variable not set
    """
    value = os.getenv(key, default)
    if required and value is None:
        raise ConfigError(f"Required environment variable '{key}' is not set")
    return value
```

### Usage Example

```python
# main.py
from config import config

def main():
    print(f"Starting {config.app_name} in {config.app_env} mode")
    print(f"Debug mode: {config.debug}")

    if config.anthropic_api_key:
        print("✓ Anthropic API key loaded")

    # Use config throughout your app
    if config.debug:
        print(f"Database: {config.database_url}")

if __name__ == "__main__":
    main()
```

## Pydantic-Based Configuration

### Type-Safe Config with Validation

```python
# config_pydantic.py
from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """Type-safe application settings."""

    # Application
    app_name: str = Field(default='MyApp', env='APP_NAME')
    app_env: str = Field(default='development', env='APP_ENV')
    debug: bool = Field(default=False, env='DEBUG')

    # Database
    database_url: str = Field(..., env='DATABASE_URL')  # Required
    database_pool_size: int = Field(default=5, env='DATABASE_POOL_SIZE')

    # API Keys
    anthropic_api_key: str = Field(default='', env='ANTHROPIC_API_KEY')

    @validator('app_env')
    def validate_env(cls, v):
        allowed = ['development', 'staging', 'production']
        if v not in allowed:
            raise ValueError(f'app_env must be one of {allowed}')
        return v

    @validator('database_pool_size')
    def validate_pool_size(cls, v):
        if v < 1 or v > 100:
            raise ValueError('database_pool_size must be between 1 and 100')
        return v

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False


# Usage
settings = Settings()
print(settings.app_name)
print(settings.database_url)
```

## JSON Secrets Loading

### Secrets Loader Implementation

```python
# secrets_loader.py
import json
import os
from pathlib import Path


def load_secrets(secrets_file: str = 'secrets.json') -> dict:
    """
    Load secrets from JSON file with fallback to environment variables.

    Args:
        secrets_file: Path to secrets JSON file

    Returns:
        Dictionary of secrets
    """
    secrets_path = Path(secrets_file)

    # Try loading from JSON file
    if secrets_path.exists():
        try:
            with open(secrets_path, 'r') as f:
                secrets = json.load(f)
            print(f"✓ Loaded secrets from {secrets_file}")
            return secrets
        except json.JSONDecodeError as e:
            print(f"⚠ Error parsing {secrets_file}: {e}")
            print("  Falling back to environment variables")
    else:
        print(f"ℹ {secrets_file} not found, using environment variables")

    # Fallback to environment variables
    return {
        'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY', ''),
        'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
        'database_password': os.getenv('DATABASE_PASSWORD', ''),
    }


# Usage
secrets = load_secrets()
api_key = secrets.get('anthropic_api_key', os.getenv('ANTHROPIC_API_KEY', ''))
```

## Helper Functions

### Environment Variable Getter

```python
def get_env(key: str, default: str = None, required: bool = False) -> str:
    """
    Get environment variable with validation.

    Args:
        key: Environment variable name
        default: Default value if not set
        required: If True, raises error when not set

    Returns:
        Environment variable value
    """
    value = os.getenv(key, default)
    if required and value is None:
        raise ConfigError(f"Required environment variable '{key}' is not set")
    return value
```

### Boolean Converter

```python
def str_to_bool(value: str) -> bool:
    """Convert string to boolean."""
    return value.lower() in ('true', '1', 'yes', 'on')
```

### Integer with Validation

```python
def get_int_env(key: str, default: int, min_val: int = None, max_val: int = None) -> int:
    """Get integer environment variable with range validation."""
    value = int(os.getenv(key, str(default)))
    if min_val is not None and value < min_val:
        raise ValueError(f"{key} must be >= {min_val}")
    if max_val is not None and value > max_val:
        raise ValueError(f"{key} must be <= {max_val}")
    return value
```
