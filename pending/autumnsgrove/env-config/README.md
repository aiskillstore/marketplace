# Environment Configuration Skill

Comprehensive environment configuration and secrets management for Python projects using UV.

## Overview

This skill provides:
- **UV Integration** - Modern Python package management
- **.env File Management** - Parse, validate, and secure .env files
- **Secrets Encryption** - Encrypt sensitive configuration files
- **Multi-Environment Support** - Separate dev/staging/production configs
- **Security Best Practices** - Prevent credential leaks and ensure secure defaults

## Quick Start

### 1. Install UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

### 2. Set Up Your Project

```bash
# Create new project
uv init my-project
cd my-project

# Create virtual environment
uv venv
source .venv/bin/activate  # macOS/Linux

# Install dependencies
uv add python-dotenv pydantic cryptography
```

### 3. Configure Environment

```bash
# Copy the example template
cp examples/.env.example .env

# Edit .env with your actual values
# nano .env
```

### 4. Add to .gitignore

```bash
echo ".env" >> .gitignore
echo "secrets.json" >> .gitignore
```

## File Structure

```
env-config/
├── SKILL.md                      # Main skill documentation
├── README.md                     # This file
├── scripts/
│   └── env_helper.py            # Environment management utilities
└── examples/
    ├── .env.example             # Comprehensive .env template
    ├── pyproject.toml           # UV project configuration
    └── secrets_template.json    # JSON secrets template
```

## Usage

### Using env_helper.py

The helper script provides utilities for managing environment files:

```bash
# Validate .env file
python scripts/env_helper.py validate .env --required APP_NAME DATABASE_URL

# Check for security issues
python scripts/env_helper.py check .env

# Compare two environments
python scripts/env_helper.py compare .env.development .env.production

# Generate template from existing .env
python scripts/env_helper.py template .env .env.template

# Encrypt secrets file
python scripts/env_helper.py encrypt secrets.json secrets.encrypted

# Decrypt secrets
python scripts/env_helper.py decrypt secrets.encrypted --output secrets.json

# Merge env files
python scripts/env_helper.py merge .env.base .env.local .env
```

### In Your Application

```python
# config.py
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class Config:
    """Application configuration."""

    APP_NAME = os.getenv('APP_NAME', 'MyApp')
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    DATABASE_URL = os.getenv('DATABASE_URL')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

config = Config()
```

```python
# main.py
from config import config

def main():
    print(f"Starting {config.APP_NAME}")
    print(f"Debug mode: {config.DEBUG}")

    if not config.ANTHROPIC_API_KEY:
        print("Warning: ANTHROPIC_API_KEY not set")

if __name__ == "__main__":
    main()
```

## Key Features

### Multi-Environment Support

Create environment-specific files:
- `.env.development` - Local development
- `.env.staging` - Staging environment
- `.env.production` - Production (never commit!)

### Secrets Encryption

Encrypt sensitive files:
```python
from scripts.env_helper import encrypt_secrets, decrypt_secrets

# Encrypt
encrypt_secrets('secrets.json', 'secrets.encrypted', 'password')

# Decrypt
secrets = decrypt_secrets('secrets.encrypted', 'password')
```

### Configuration Validation

```python
from config import Config, ConfigError

try:
    config = Config(env='production')
except ConfigError as e:
    print(f"Configuration error: {e}")
    sys.exit(1)
```

## UV Commands

```bash
# Install dependencies
uv sync

# Add new package
uv add package-name

# Add dev dependency
uv add --dev pytest

# Update dependencies
uv lock --upgrade

# Run application
uv run python main.py

# Run tests
uv run pytest
```

## Security Best Practices

1. **Never commit secrets** - Add `.env` and `secrets.json` to `.gitignore`
2. **Use strong secrets** - Generate random keys for production
3. **Separate environments** - Different configs for dev/staging/prod
4. **Validate on startup** - Check required variables exist
5. **Rotate regularly** - Change API keys and secrets periodically
6. **Encrypt at rest** - Use encryption for sensitive files
7. **Audit regularly** - Run security checks on configuration

## Examples

See the `examples/` directory for:
- Comprehensive .env template with all common variables
- UV pyproject.toml configuration
- JSON secrets template structure

## Documentation

Read `SKILL.md` for:
- Complete workflow guide
- Advanced configuration patterns
- Testing strategies
- Troubleshooting tips
- Best practices

## Requirements

- Python 3.10+
- UV package manager
- python-dotenv
- cryptography (for encryption features)
- pydantic (for type-safe config)

## License

MIT License - See individual project files for details.

## Contributing

This skill is part of the Claude Skills library. For improvements or issues, please refer to the main repository guidelines.
