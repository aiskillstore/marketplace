---
name: python-venv-manager
description: Python virtual environment management, dependency handling, and project setup automation.
---

# Python Virtual Environment Manager Skill

Python virtual environment management, dependency handling, and project setup automation.

## Instructions

You are a Python environment and dependency expert. When invoked:

1. **Virtual Environment Management**:
   - Create and configure virtual environments
   - Manage Python versions with pyenv
   - Set up isolated development environments
   - Handle multiple Python versions per project
   - Configure environment activation scripts

2. **Dependency Management**:
   - Generate and manage requirements.txt
   - Use modern tools (pip-tools, poetry, pipenv)
   - Lock dependencies with hashes
   - Handle dev vs production dependencies
   - Resolve dependency conflicts

3. **Project Setup**:
   - Initialize new Python projects
   - Configure project structure
   - Set up testing frameworks
   - Configure linting and formatting
   - Create reproducible environments

4. **Troubleshooting**:
   - Fix import errors
   - Resolve version conflicts
   - Debug installation issues
   - Handle platform-specific dependencies
   - Clean corrupted environments

5. **Best Practices**: Provide guidance on Python packaging, versioning, and environment isolation

## Virtual Environment Tools Comparison

### venv (Built-in)
```bash
# Pros: Built-in, no installation needed
# Cons: Basic features, manual workflow

# Create environment
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Deactivate
deactivate

# Install dependencies
pip install -r requirements.txt
```

### virtualenv (Enhanced)
```bash
# Pros: More features, faster than venv
# Cons: Requires installation

# Install
pip install virtualenv

# Create with specific Python version
virtualenv -p python3.11 venv

# Create with system site-packages
virtualenv --system-site-packages venv
```

### Poetry (Modern, Recommended)
```bash
# Pros: Dependency resolution, packaging, publishing
# Cons: Learning curve

# Install
curl -sSL https://install.python-poetry.org | python3 -

# Create new project
poetry new my-project

# Initialize existing project
poetry init

# Add dependencies
poetry add requests
poetry add --group dev pytest

# Install dependencies
poetry install

# Run commands in virtual environment
poetry run python script.py
poetry run pytest

# Activate shell
poetry shell

# Update dependencies
poetry update

# Show dependency tree
poetry show --tree
```

### Pipenv
```bash
# Pros: Automatic venv, Pipfile format
# Cons: Slower than alternatives

# Install
pip install pipenv

# Install dependencies
pipenv install requests

# Install dev dependencies
pipenv install --dev pytest

# Activate environment
pipenv shell

# Run command
pipenv run python script.py

# Generate requirements.txt
pipenv requirements > requirements.txt
```

### pyenv (Python Version Manager)
```bash
# Install multiple Python versions
# Manage Python versions per project

# Install
curl https://pyenv.run | bash

# Install Python version
pyenv install 3.11.5
pyenv install 3.12.0

# List available versions
pyenv install --list

# Set global version
pyenv global 3.11.5

# Set local version (per directory)
pyenv local 3.11.5

# List installed versions
pyenv versions

# Show current version
pyenv version
```

## Usage Examples

```
@python-venv-manager
@python-venv-manager --setup-project
@python-venv-manager --create-venv
@python-venv-manager --poetry
@python-venv-manager --fix-dependencies
@python-venv-manager --migrate-to-poetry
```

## Project Setup Workflows

### Basic Project with venv
```bash
# Create project directory
mkdir my-project
cd my-project

# Create virtual environment
python3 -m venv venv

# Activate environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install requests pytest black flake8

# Freeze dependencies
pip freeze > requirements.txt

# Create .gitignore
cat > .gitignore << EOF
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
.pytest_cache/
.coverage
htmlcov/
.env
.venv
EOF
```

### Modern Project with Poetry
```bash
# Create new project with structure
poetry new my-project
cd my-project

# Project structure created:
# my-project/
# ├── pyproject.toml
# ├── README.md
# ├── my_project/
# │   └── __init__.py
# └── tests/
#     └── __init__.py

# Add dependencies
poetry add requests httpx pydantic
poetry add --group dev pytest pytest-cov black flake8 mypy

# Install dependencies
poetry install

# Configure pyproject.toml
cat >> pyproject.toml << EOF

[tool.black]
line-length = 88
target-version = ['py311']

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
EOF
```

### Initialize Existing Project
```bash
# Navigate to project
cd existing-project

# Initialize poetry
poetry init

# Follow interactive prompts, then add dependencies
poetry add $(cat requirements.txt)

# Add dev dependencies
poetry add --group dev pytest black flake8

# Create virtual environment
poetry install

# Verify installation
poetry run python -c "import requests; print(requests.__version__)"
```

## Dependency Management

### requirements.txt Best Practices
```bash
# Basic requirements.txt
requests==2.31.0
django==4.2.7
celery==5.3.4

# With hashes for security (pip-tools)
pip-compile --generate-hashes requirements.in

# Separate files
requirements/
├── base.txt          # Common dependencies
├── development.txt   # Dev dependencies
├── production.txt    # Production dependencies
└── testing.txt       # Test dependencies

# development.txt
-r base.txt
pytest==7.4.3
black==23.11.0
flake8==6.1.0

# Install from specific file
pip install -r requirements/development.txt
```

### Using pip-tools (Recommended)
```bash
# Install pip-tools
pip install pip-tools

# Create requirements.in
cat > requirements.in << EOF
django>=4.2,<5.0
requests
celery[redis]
EOF

# Compile to requirements.txt with pinned versions
pip-compile requirements.in

# Install from compiled requirements
pip-sync requirements.txt

# Update dependencies
pip-compile --upgrade requirements.in

# Compile with hashes for security
pip-compile --generate-hashes requirements.in
```

### Poetry Dependency Management
```bash
# Add dependency with version constraint
poetry add "django>=4.2,<5.0"

# Add with specific version
poetry add django@4.2.7

# Add from git
poetry add git+https://github.com/user/repo.git

# Add from local path
poetry add --editable ./local-package

# Add with extras
poetry add "celery[redis,auth]"

# Update specific package
poetry update django

# Update all packages
poetry update

# Show outdated packages
poetry show --outdated

# Remove package
poetry remove requests

# Export to requirements.txt
poetry export -f requirements.txt --output requirements.txt
poetry export --without-hashes -f requirements.txt --output requirements.txt
```

### Development vs Production Dependencies
```bash
# Poetry approach
[tool.poetry.dependencies]
python = "^3.11"
django = "^4.2"
requests = "^2.31"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4"
black = "^23.11"
flake8 = "^6.1"

# Install without dev dependencies
poetry install --without dev

# Install only specific groups
poetry install --only dev

# pip-tools approach
# requirements.in (production)
django>=4.2
requests

# requirements-dev.in (development)
-r requirements.in
pytest>=7.4
black>=23.11
flake8>=6.1

# Compile both
pip-compile requirements.in
pip-compile requirements-dev.in
```

## Python Version Management

### Using pyenv
```bash
# Install pyenv
curl https://pyenv.run | bash

# Add to shell configuration (.bashrc, .zshrc)
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# Install Python versions
pyenv install 3.11.5
pyenv install 3.12.0

# Set global version
pyenv global 3.11.5

# Set local version (creates .python-version file)
pyenv local 3.11.5

# Create virtual environment with specific version
pyenv virtualenv 3.11.5 my-project-env

# Activate virtual environment
pyenv activate my-project-env

# Deactivate
pyenv deactivate

# List virtual environments
pyenv virtualenvs

# Delete virtual environment
pyenv uninstall my-project-env
```

### Using pyenv with Poetry
```bash
# Set local Python version
pyenv local 3.11.5

# Initialize Poetry project
poetry init

# Poetry will use pyenv's Python version
poetry env use python

# Or specify version explicitly
poetry env use 3.11

# List Poetry environments
poetry env list

# Remove environment
poetry env remove python3.11

# Show environment info
poetry env info
```

## Project Structure Best Practices

### Small Project
```
my-project/
├── .gitignore
├── README.md
├── requirements.txt
├── setup.py  (optional)
├── my_module.py
└── tests/
    ├── __init__.py
    └── test_my_module.py
```

### Medium Project
```
my-project/
├── .gitignore
├── README.md
├── pyproject.toml
├── setup.py
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── src/
│   └── my_package/
│       ├── __init__.py
│       ├── core.py
│       ├── utils.py
│       └── models.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_core.py
└── docs/
    └── index.md
```

### Large Project with Poetry
```
my-project/
├── .gitignore
├── .python-version
├── README.md
├── pyproject.toml
├── poetry.lock
├── src/
│   └── my_package/
│       ├── __init__.py
│       ├── core/
│       │   ├── __init__.py
│       │   └── engine.py
│       ├── api/
│       │   ├── __init__.py
│       │   └── routes.py
│       └── utils/
│           ├── __init__.py
│           └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   └── test_core.py
│   └── integration/
│       └── test_api.py
├── docs/
│   ├── conf.py
│   └── index.rst
└── scripts/
    └── setup_dev.sh
```

## Common Issues & Solutions

### Issue: ModuleNotFoundError
```bash
# Check if virtual environment is activated
which python  # Should point to venv/bin/python

# Verify package is installed
pip list | grep package-name

# Reinstall package
pip install --force-reinstall package-name

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Fix: Activate virtual environment
source venv/bin/activate

# Fix: Install in editable mode for local development
pip install -e .
```

### Issue: Dependency Conflicts
```bash
# Check for conflicts
pip check

# Show dependency tree
pip install pipdeptree
pipdeptree

# Using Poetry (better conflict resolution)
poetry add package-name
# Poetry will resolve conflicts automatically

# Force specific version
pip install "package==1.2.3"

# Use pip-tools to resolve
pip-compile --resolver=backtracking requirements.in
```

### Issue: Multiple Python Versions Confusion
```bash
# Check current Python version
python --version
which python

# Use specific version explicitly
python3.11 -m venv venv

# With pyenv
pyenv versions  # List installed versions
pyenv which python  # Show current python path

# Set specific version for project
pyenv local 3.11.5
```

### Issue: Corrupted Virtual Environment
```bash
# Delete and recreate
rm -rf venv/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# With Poetry
poetry env remove python3.11
poetry install
```

### Issue: SSL Certificate Errors
```bash
# Temporary workaround (NOT for production)
pip install --trusted-host pypi.org --trusted-host pypi.python.org package-name

# Better solution: Update certificates
pip install --upgrade certifi

# macOS specific
/Applications/Python\ 3.11/Install\ Certificates.command
```

### Issue: Permission Denied
```bash
# Don't use sudo with pip in virtual environment!
# Recreate venv with proper permissions

# Fix ownership
chown -R $USER:$USER venv/

# Use user install only if not in venv
pip install --user package-name
```

## Environment Variables and Configuration

### .env Files
```bash
# Install python-decouple or python-dotenv
poetry add python-dotenv

# Create .env file
cat > .env << EOF
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379
EOF

# Load in Python
from dotenv import load_dotenv
import os

load_dotenv()

DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
```

### Environment-Specific Settings
```python
# config.py
import os
from pathlib import Path

class Config:
    BASE_DIR = Path(__file__).parent
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URL = 'sqlite:///dev.db'

class ProductionConfig(Config):
    DATABASE_URL = os.getenv('DATABASE_URL')

class TestingConfig(Config):
    TESTING = True
    DATABASE_URL = 'sqlite:///test.db'

# Select config based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    env = os.getenv('FLASK_ENV', 'default')
    return config[env]()
```

## Testing Setup

### pytest Configuration
```bash
# Install pytest
poetry add --group dev pytest pytest-cov pytest-mock

# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "-v --tb=short --strict-markers"

# Run tests
poetry run pytest

# With coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test
poetry run pytest tests/test_core.py::test_function_name
```

## Code Quality Tools

### Formatting and Linting
```bash
# Install tools
poetry add --group dev black isort flake8 mypy pylint

# pyproject.toml configuration
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

# Run formatting
poetry run black .
poetry run isort .

# Run linting
poetry run flake8 src/
poetry run mypy src/
poetry run pylint src/
```

### Pre-commit Hooks
```bash
# Install pre-commit
poetry add --group dev pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
EOF

# Install hooks
poetry run pre-commit install

# Run manually
poetry run pre-commit run --all-files
```

## Migration Scripts

### Migrate from requirements.txt to Poetry
```bash
# Script: migrate_to_poetry.sh
#!/bin/bash

echo "Migrating to Poetry..."

# Backup current setup
cp requirements.txt requirements.txt.backup

# Initialize Poetry
poetry init --no-interaction

# Add dependencies from requirements.txt
cat requirements.txt | grep -v "^#" | grep -v "^$" | while read package; do
    # Remove version specifiers for initial add
    pkg_name=$(echo $package | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1)
    poetry add "$pkg_name"
done

# Install dependencies
poetry install

echo "Migration complete. Check pyproject.toml"
echo "Original requirements.txt backed up to requirements.txt.backup"
```

### Convert between formats
```bash
# Poetry to requirements.txt
poetry export -f requirements.txt --output requirements.txt --without-hashes

# requirements.txt to Poetry
cat requirements.txt | xargs poetry add

# Pipenv to requirements.txt
pipenv requirements > requirements.txt

# Pipenv to Poetry
poetry add $(pipenv requirements | sed 's/==/=/g')
```

## Docker Integration

### Dockerfile with Virtual Environment
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run as non-root
RUN useradd -m -u 1001 appuser && \
    chown -R appuser:appuser /app
USER appuser

CMD ["python", "app.py"]
```

### Dockerfile with Poetry
```dockerfile
FROM python:3.11-slim as builder

WORKDIR /app

# Install Poetry
RUN pip install poetry==1.7.0

# Configure Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

# Runtime stage
FROM python:3.11-slim as runtime

WORKDIR /app

# Copy virtual environment from builder
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"
COPY --from=builder /app/.venv ${VIRTUAL_ENV}

# Copy application
COPY . .

# Run as non-root
RUN useradd -m -u 1001 appuser && \
    chown -R appuser:appuser /app
USER appuser

CMD ["python", "app.py"]
```

## Best Practices Summary

### Virtual Environment
- Always use virtual environments (never install globally)
- One virtual environment per project
- Keep venv/ out of version control (.gitignore)
- Document Python version requirements (.python-version)
- Use pyenv for managing multiple Python versions

### Dependency Management
- Pin exact versions in production (no ~, ^)
- Use pip-tools or Poetry for dependency resolution
- Separate dev and production dependencies
- Use lock files (poetry.lock, requirements.txt with hashes)
- Regularly update dependencies for security
- Document why specific versions are pinned

### Project Structure
- Use src/ layout for packages
- Keep tests separate from source
- Include comprehensive .gitignore
- Add README.md with setup instructions
- Use pyproject.toml for modern projects

### Security
- Never commit .env files
- Use python-dotenv for environment variables
- Scan dependencies with pip-audit or safety
- Use hashes in requirements.txt
- Keep dependencies minimal
- Update regularly for security patches

### Development Workflow
- Use pre-commit hooks for code quality
- Configure formatters (black, isort)
- Use type hints and mypy
- Write tests with pytest
- Document setup steps in README

## Quick Reference Commands

```bash
# venv basics
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip freeze > requirements.txt

# Poetry basics
poetry new project
poetry init
poetry add package
poetry install
poetry shell
poetry run python script.py

# pyenv basics
pyenv install 3.11.5
pyenv local 3.11.5
pyenv virtualenv 3.11.5 myenv

# pip-tools basics
pip-compile requirements.in
pip-sync requirements.txt
pip-compile --upgrade

# Common tasks
pip list --outdated
pip check
poetry show --outdated
poetry update
```

## Notes

- Prefer Poetry or pip-tools over manual requirements.txt management
- Use pyenv to manage multiple Python versions
- Always activate virtual environment before installing packages
- Keep dependencies documented and up-to-date
- Use lock files for reproducible builds
- Test dependency updates in isolated environment first
- Configure proper .gitignore to exclude virtual environments
- Use type hints and static analysis tools (mypy)
- Set up CI/CD to verify dependency installation
- Regular security audits of dependencies
