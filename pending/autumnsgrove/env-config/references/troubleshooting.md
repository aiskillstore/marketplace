# Configuration Troubleshooting Guide

## Common Issues

### Issue 1: Environment Variables Not Loading

**Symptoms:**
- Application shows default values instead of .env values
- `os.getenv()` returns `None` for expected variables
- Configuration appears empty

**Diagnosis:**

```python
# Debug: Print loaded variables
import os
from dotenv import load_dotenv

load_dotenv(verbose=True)  # Shows what's being loaded
print(f"APP_NAME: {os.getenv('APP_NAME')}")
print(f"Current directory: {os.getcwd()}")
print(f".env exists: {Path('.env').exists()}")
```

**Solutions:**

1. **Check .env file location**
   ```bash
   # Verify .env is in current directory
   ls -la .env

   # Or specify path explicitly
   python
   from dotenv import load_dotenv
   load_dotenv('/absolute/path/to/.env')
   ```

2. **Verify file permissions**
   ```bash
   # Make sure file is readable
   chmod 644 .env
   ```

3. **Check for BOM or encoding issues**
   ```python
   # Re-save .env file as UTF-8 without BOM
   content = Path('.env').read_text(encoding='utf-8-sig')
   Path('.env').write_text(content, encoding='utf-8')
   ```

4. **Verify syntax**
   ```bash
   # Check for syntax errors
   cat .env | grep -v '^#' | grep -v '^$'

   # Should be: KEY=value (no spaces around =)
   # ✓ APP_NAME=MyApp
   # ✗ APP_NAME = MyApp
   ```

### Issue 2: Wrong Environment Loaded

**Symptoms:**
- Production settings in development
- Development debug mode in production
- Unexpected configuration values

**Diagnosis:**

```python
# Check which environment is active
import os
print(f"APP_ENV: {os.getenv('APP_ENV')}")
print(f"Current env files:")
from pathlib import Path
for env_file in Path('.').glob('.env*'):
    print(f"  - {env_file}")
```

**Solutions:**

1. **Explicitly set environment**
   ```bash
   # Set before running
   export APP_ENV=development
   python main.py

   # Or inline
   APP_ENV=production python main.py
   ```

2. **Check environment loading order**
   ```python
   # Verify load order in config
   from config import config
   print(f"Using environment: {config.app_env}")

   # Force specific environment
   config = Config(env='development')
   ```

3. **Use environment-specific commands**
   ```bash
   # Add to package.json or Makefile
   uv run python main.py --env=development
   uv run python main.py --env=production
   ```

### Issue 3: UV sync Fails

**Symptoms:**
- `uv sync` command errors
- Dependencies not installing
- Virtual environment issues

**Solutions:**

1. **Clear UV cache**
   ```bash
   # Clean cache
   uv cache clean

   # Remove and recreate venv
   rm -rf .venv
   uv venv
   uv sync
   ```

2. **Check Python version**
   ```bash
   # Verify Python version
   python --version

   # UV requires Python 3.8+
   uv python pin 3.11
   ```

3. **Update UV**
   ```bash
   # Get latest UV
   pip install --upgrade uv

   # Or reinstall
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

4. **Check network/proxy**
   ```bash
   # Test network
   curl -I https://pypi.org

   # Set proxy if needed
   export HTTP_PROXY=http://proxy:port
   export HTTPS_PROXY=http://proxy:port
   ```

### Issue 4: Import Errors

**Symptoms:**
- `ModuleNotFoundError: No module named 'dotenv'`
- `ImportError: cannot import name 'load_dotenv'`

**Solutions:**

1. **Verify dependencies installed**
   ```bash
   # Check if python-dotenv is installed
   uv pip list | grep dotenv

   # Install if missing
   uv add python-dotenv
   ```

2. **Check virtual environment activation**
   ```bash
   # Activate venv
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate     # Windows

   # Verify correct Python
   which python
   ```

3. **Reinstall dependencies**
   ```bash
   # Force reinstall
   uv sync --reinstall
   ```

### Issue 5: Secrets Not Decrypting

**Symptoms:**
- Encryption/decryption fails
- Invalid key errors
- Corrupted secrets file

**Solutions:**

1. **Verify encryption key**
   ```python
   # Check key format
   import base64
   key = os.getenv('ENCRYPTION_KEY')
   try:
       decoded = base64.b64decode(key)
       print(f"Key length: {len(decoded)} bytes")
   except Exception as e:
       print(f"Invalid key: {e}")
   ```

2. **Re-encrypt secrets**
   ```bash
   # Backup current encrypted file
   cp secrets.encrypted secrets.encrypted.bak

   # Re-encrypt from source
   python scripts/env_helper.py encrypt secrets.json secrets.encrypted
   ```

3. **Check file corruption**
   ```bash
   # Verify file integrity
   file secrets.encrypted
   hexdump -C secrets.encrypted | head
   ```

## Environment-Specific Issues

### Development Environment

**Issue: Local services not connecting**

```bash
# Check if services are running
docker ps  # For containerized services
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# Start services
docker-compose up -d
```

**Issue: Debug output too verbose**

```bash
# Adjust log level
LOG_LEVEL=WARNING python main.py
```

### Staging Environment

**Issue: API keys not working**

```bash
# Verify API keys are for staging environment
curl -H "Authorization: Bearer $ANTHROPIC_API_KEY" \
     https://api.anthropic.com/v1/endpoint

# Check rate limits
# Use staging-specific keys
```

**Issue: Database connection timeout**

```python
# Increase connection timeout
DATABASE_URL=postgresql://host/db?connect_timeout=30
DATABASE_POOL_SIZE=10  # Increase pool
```

### Production Environment

**Issue: Application won't start**

```bash
# Check all required vars set
python -c "
from config import Config
try:
    config = Config(env='production')
    print('✓ Configuration valid')
except Exception as e:
    print(f'✗ Configuration error: {e}')
"
```

**Issue: Secrets not loading**

```bash
# Verify secrets file permissions
ls -l secrets.json
# Should be: -rw------- (600)

# Fix permissions
chmod 600 secrets.json
chown app:app secrets.json
```

## Performance Issues

### Issue: Slow Configuration Loading

**Solutions:**

1. **Cache configuration**
   ```python
   # Use singleton pattern
   _config = None

   def get_config():
       global _config
       if _config is None:
           _config = Config()
       return _config
   ```

2. **Lazy load optional config**
   ```python
   class Config:
       @property
       def expensive_resource(self):
           if not hasattr(self, '_expensive_resource'):
               self._expensive_resource = load_expensive_config()
           return self._expensive_resource
   ```

3. **Reduce validation overhead**
   ```python
   # Validate once at startup
   config = Config()
   config._validate_required()  # Only once

   # Skip validation in subsequent uses
   ```

### Issue: Too Many Environment Files

**Solution: Consolidate**

```bash
# Before (slow)
.env
.env.local
.env.development
.env.development.local
.env.staging
.env.production

# After (faster)
.env  # Shared defaults
.env.development  # Dev-specific
.env.production  # Prod-specific
```

## Security Issues

### Issue: Secrets in Version Control

**Detection:**

```bash
# Check git history for secrets
git log --all --full-history --source -- .env
git log --all -p | grep -i "api_key"

# Use git-secrets
git secrets --scan
```

**Remediation:**

```bash
# Remove from git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Or use BFG Repo-Cleaner
bfg --delete-files .env
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

**Prevention:**

```bash
# Add to .gitignore immediately
echo ".env" >> .gitignore
echo "secrets.json" >> .gitignore
git add .gitignore
git commit -m "Add .env to gitignore"

# Use pre-commit hooks
# .git/hooks/pre-commit
#!/bin/bash
if git diff --cached --name-only | grep -q "\.env$"; then
    echo "Error: Attempting to commit .env file"
    exit 1
fi
```

### Issue: API Keys Exposed in Logs

**Detection:**

```bash
# Search logs for keys
grep -r "sk-ant-" logs/
grep -r "api.key" logs/
```

**Prevention:**

```python
import re

class SecureLogger:
    """Logger that redacts sensitive values."""

    PATTERNS = [
        r'sk-ant-[a-zA-Z0-9-]+',  # Anthropic keys
        r'sk-[a-zA-Z0-9]{32,}',   # OpenAI keys
        r'password=\S+',          # Passwords
    ]

    @classmethod
    def redact(cls, message: str) -> str:
        """Redact sensitive patterns from message."""
        for pattern in cls.PATTERNS:
            message = re.sub(pattern, '[REDACTED]', message)
        return message

# Usage
logger.info(SecureLogger.redact(f"API key: {api_key}"))
```

## Validation Issues

### Issue: Type Errors

```python
# Problem: String instead of int
PORT = os.getenv('PORT')  # Returns string "8000"

# Solution: Convert types
PORT = int(os.getenv('PORT', '8000'))

# Or use Pydantic for automatic conversion
from pydantic import BaseSettings

class Settings(BaseSettings):
    port: int = 8000  # Automatically converts string to int
```

### Issue: Boolean Confusion

```python
# Problem: All strings are truthy
DEBUG = os.getenv('DEBUG')  # "false" is truthy!

# Solution: Explicit conversion
def str_to_bool(value: str) -> bool:
    return value.lower() in ('true', '1', 'yes', 'on')

DEBUG = str_to_bool(os.getenv('DEBUG', 'false'))
```

## Docker Issues

### Issue: Environment Variables Not Available in Container

**Solutions:**

1. **Pass variables explicitly**
   ```bash
   docker run -e APP_ENV=production \
              -e DATABASE_URL=$DATABASE_URL \
              myapp
   ```

2. **Use env file**
   ```bash
   docker run --env-file .env.production myapp
   ```

3. **Check Dockerfile**
   ```dockerfile
   # Don't hardcode ENV in Dockerfile
   # ✗ Bad
   ENV APP_ENV=development

   # ✓ Good - use runtime injection
   # (no ENV declaration)
   ```

### Issue: Different Behavior in Container vs Local

**Solutions:**

1. **Match environments**
   ```bash
   # Use same Python version
   docker run python:3.11-slim python --version
   python --version  # Should match
   ```

2. **Check working directory**
   ```dockerfile
   WORKDIR /app
   # .env should be in /app/.env
   ```

3. **Verify file copying**
   ```dockerfile
   # Make sure .env.template is copied
   COPY .env.template .
   # But don't copy .env (use runtime vars)
   ```

## Getting Help

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from dotenv import load_dotenv
load_dotenv(verbose=True)  # Shows loading process
```

### Create Minimal Reproduction

```python
# minimal_test.py
import os
from pathlib import Path
from dotenv import load_dotenv

print(f"Current directory: {os.getcwd()}")
print(f".env exists: {Path('.env').exists()}")

load_dotenv(verbose=True)

print(f"APP_NAME: {os.getenv('APP_NAME')}")
print(f"All env vars starting with APP_:")
for key, value in os.environ.items():
    if key.startswith('APP_'):
        print(f"  {key}={value}")
```

### Check Versions

```bash
# Print diagnostic info
python --version
uv --version
pip list | grep -E "(dotenv|pydantic|cryptography)"

# System info
uname -a  # Linux/macOS
systeminfo  # Windows
```

### Report Issues

When reporting configuration issues, include:

1. Python version: `python --version`
2. UV version: `uv --version`
3. OS: `uname -a`
4. .env file structure (with secrets redacted)
5. Error messages (full stack trace)
6. Steps to reproduce
7. Expected vs actual behavior
