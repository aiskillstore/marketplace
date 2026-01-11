---
name: env-manager
description: Environment variable management, validation, and documentation.
---

# Environment Manager Skill

Environment variable management, validation, and documentation.

## Instructions

You are an environment configuration expert. When invoked:

1. **Analyze Environment Variables**:
   - Identify all environment variables used in code
   - Check for undefined or missing variables
   - Validate variable formats (URLs, numbers, booleans)
   - Detect hardcoded values that should be env vars

2. **Generate Documentation**:
   - Create .env.example template
   - Document required vs optional variables
   - Provide descriptions and examples
   - List default values

3. **Validate Configuration**:
   - Check required variables are set
   - Validate formats and types
   - Ensure no secrets in source control
   - Verify cross-environment consistency

4. **Provide Best Practices**:
   - Naming conventions
   - Security recommendations
   - Environment-specific configs
   - Secret management strategies

## Environment Variable Conventions

### Naming Standards
```bash
# Use UPPER_SNAKE_CASE
DATABASE_URL=postgresql://localhost:5432/mydb
API_KEY=abc123xyz

# Prefix by service/category
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydb
DB_USER=admin

REDIS_HOST=localhost
REDIS_PORT=6379

AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...

# Boolean values
ENABLE_LOGGING=true
DEBUG_MODE=false
```

### Environment Prefixes
```bash
# Development
NODE_ENV=development
DEBUG=true
LOG_LEVEL=debug

# Staging
NODE_ENV=staging
DEBUG=false
LOG_LEVEL=info

# Production
NODE_ENV=production
DEBUG=false
LOG_LEVEL=error
```

## .env.example Template

```bash
# ======================
# Application Settings
# ======================

# Environment (development, staging, production)
NODE_ENV=development

# Application port
PORT=3000

# Application URL
APP_URL=http://localhost:3000

# ======================
# Database Configuration
# ======================

# PostgreSQL connection string
# Format: postgresql://username:password@host:port/database
DATABASE_URL=postgresql://user:password@localhost:5432/myapp

# Database connection pool
DB_POOL_MIN=2
DB_POOL_MAX=10

# ======================
# Redis Configuration
# ======================

# Redis connection URL
REDIS_URL=redis://localhost:6379

# Redis password (optional)
# REDIS_PASSWORD=

# ======================
# Authentication
# ======================

# JWT secret key (REQUIRED - Generate with: openssl rand -base64 32)
JWT_SECRET=your-secret-key-here

# JWT expiration (default: 24h)
JWT_EXPIRES_IN=24h

# Session secret
SESSION_SECRET=your-session-secret

# ======================
# External Services
# ======================

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET=my-app-uploads

# Email Service (SendGrid)
SENDGRID_API_KEY=SG.xxxxx
EMAIL_FROM=noreply@example.com

# Stripe
STRIPE_PUBLIC_KEY=pk_test_xxxxx
STRIPE_SECRET_KEY=sk_test_xxxxx

# ======================
# Feature Flags
# ======================

# Enable new dashboard
ENABLE_NEW_DASHBOARD=false

# Enable email notifications
ENABLE_EMAIL_NOTIFICATIONS=true

# ======================
# Logging & Monitoring
# ======================

# Log level (error, warn, info, debug)
LOG_LEVEL=info

# Sentry DSN for error tracking
# SENTRY_DSN=https://xxxxx@sentry.io/xxxxx

# ======================
# Security
# ======================

# CORS allowed origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Rate limiting
RATE_LIMIT_MAX_REQUESTS=100
RATE_LIMIT_WINDOW_MS=900000

# ======================
# Development Only
# ======================

# Enable debug mode
DEBUG=false

# Disable SSL verification (NEVER in production!)
# NODE_TLS_REJECT_UNAUTHORIZED=0
```

## Environment Validation

### Node.js Example
```javascript
// env.js - Environment validation
const envalid = require('envalid');

const env = envalid.cleanEnv(process.env, {
  // Application
  NODE_ENV: envalid.str({ choices: ['development', 'staging', 'production'] }),
  PORT: envalid.port({ default: 3000 }),
  APP_URL: envalid.url(),

  // Database
  DATABASE_URL: envalid.url({ desc: 'PostgreSQL connection URL' }),
  DB_POOL_MIN: envalid.num({ default: 2 }),
  DB_POOL_MAX: envalid.num({ default: 10 }),

  // Redis
  REDIS_URL: envalid.url(),
  REDIS_PASSWORD: envalid.str({ default: '' }),

  // Secrets
  JWT_SECRET: envalid.str({ desc: 'JWT signing secret' }),
  JWT_EXPIRES_IN: envalid.str({ default: '24h' }),

  // AWS
  AWS_REGION: envalid.str({ default: 'us-east-1' }),
  AWS_ACCESS_KEY_ID: envalid.str(),
  AWS_SECRET_ACCESS_KEY: envalid.str(),

  // Feature Flags
  ENABLE_NEW_DASHBOARD: envalid.bool({ default: false }),
  ENABLE_EMAIL_NOTIFICATIONS: envalid.bool({ default: true }),

  // Logging
  LOG_LEVEL: envalid.str({
    choices: ['error', 'warn', 'info', 'debug'],
    default: 'info'
  }),

  // Security
  CORS_ORIGINS: envalid.str({ desc: 'Comma-separated allowed origins' }),
  RATE_LIMIT_MAX_REQUESTS: envalid.num({ default: 100 }),
});

module.exports = env;
```

### Python Example
```python
# config.py - Environment validation
import os
from typing import Optional
from pydantic import BaseSettings, validator, AnyHttpUrl

class Settings(BaseSettings):
    # Application
    ENV: str = "development"
    PORT: int = 8000
    APP_URL: AnyHttpUrl

    # Database
    DATABASE_URL: str
    DB_POOL_MIN: int = 2
    DB_POOL_MAX: int = 10

    # Redis
    REDIS_URL: str
    REDIS_PASSWORD: Optional[str] = None

    # Secrets
    JWT_SECRET: str
    JWT_EXPIRES_IN: str = "24h"

    # AWS
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str

    # Feature Flags
    ENABLE_NEW_DASHBOARD: bool = False
    ENABLE_EMAIL_NOTIFICATIONS: bool = True

    # Logging
    LOG_LEVEL: str = "info"

    @validator("ENV")
    def validate_env(cls, v):
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"ENV must be one of {allowed}")
        return v

    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        allowed = ["error", "warn", "info", "debug"]
        if v not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

## Usage Examples

```
@env-manager
@env-manager --validate
@env-manager --generate-example
@env-manager --check-secrets
@env-manager --document
```

## Security Best Practices

### Never Commit Secrets
```bash
# .gitignore
.env
.env.local
.env.*.local
*.pem
*.key
secrets/
```

### Secret Detection
```bash
# Check for accidentally committed secrets
git secrets --scan

# Use tools like:
# - gitleaks
# - truffleHog
# - git-secrets
```

### Secret Management Solutions
```bash
# Development
# - .env files (gitignored)
# - direnv

# Production
# - AWS Secrets Manager
# - HashiCorp Vault
# - Azure Key Vault
# - Google Secret Manager
# - Kubernetes Secrets
# - Docker Secrets
```

### Encryption at Rest
```bash
# Encrypt sensitive .env files
# Using SOPS (Secrets OPerationS)
sops -e .env > .env.encrypted

# Using git-crypt
git-crypt init
echo '.env' >> .gitattributes
git-crypt add-gpg-user user@example.com
```

## Environment-Specific Configurations

### Multiple .env Files
```bash
.env                  # Default (committed .env.example)
.env.local           # Local overrides (gitignored)
.env.development     # Development
.env.staging         # Staging
.env.production      # Production (never committed!)
```

### Loading Priority (Node.js)
```javascript
// Using dotenv with cascading
require('dotenv').config({ path: '.env.local' });
require('dotenv').config({ path: `.env.${process.env.NODE_ENV}` });
require('dotenv').config({ path: '.env' });
```

## Common Issues & Solutions

### Missing Environment Variables
```javascript
// ❌ Bad - Silent failure
const apiKey = process.env.API_KEY;

// ✓ Good - Explicit validation
const apiKey = process.env.API_KEY;
if (!apiKey) {
  throw new Error('API_KEY environment variable is required');
}

// ✓ Better - Use validation library
const env = require('./env'); // validates on load
const apiKey = env.API_KEY;
```

### Type Coercion
```javascript
// ❌ Bad - String comparison
if (process.env.DEBUG === true) { } // Always false!

// ✓ Good - Proper boolean parsing
const DEBUG = process.env.DEBUG === 'true';

// ✓ Better - Use validation
const { bool } = require('envalid');
const DEBUG = bool({ default: false });
```

### Default Values
```javascript
// ✓ Provide sensible defaults
const PORT = process.env.PORT || 3000;
const LOG_LEVEL = process.env.LOG_LEVEL || 'info';
const ENABLE_CACHE = process.env.ENABLE_CACHE !== 'false'; // Default true
```

## Documentation Template

```markdown
# Environment Variables

## Required Variables

### DATABASE_URL
- **Type**: URL
- **Description**: PostgreSQL connection string
- **Format**: `postgresql://username:password@host:port/database`
- **Example**: `postgresql://user:pass@localhost:5432/mydb`

### JWT_SECRET
- **Type**: String
- **Description**: Secret key for JWT token signing
- **Security**: Never commit this value
- **Generate**: `openssl rand -base64 32`

### AWS_ACCESS_KEY_ID
- **Type**: String
- **Description**: AWS access key for S3 and other services
- **Security**: Store in secrets manager in production

## Optional Variables

### PORT
- **Type**: Number
- **Description**: Application server port
- **Default**: `3000`
- **Example**: `3000`

### LOG_LEVEL
- **Type**: String
- **Description**: Logging verbosity
- **Choices**: `error`, `warn`, `info`, `debug`
- **Default**: `info`

### ENABLE_CACHE
- **Type**: Boolean
- **Description**: Enable Redis caching
- **Default**: `true`
- **Values**: `true`, `false`

## Feature Flags

### ENABLE_NEW_DASHBOARD
- **Type**: Boolean
- **Description**: Enable new dashboard UI
- **Default**: `false`
- **Status**: Experimental

## Environment Setup

### Development
```bash
cp .env.example .env.local
# Edit .env.local with your local values
```

### Production
Use secrets manager to set:
- DATABASE_URL
- JWT_SECRET
- AWS credentials
- API keys
```

## Notes

- Use `.env.example` as template (committed to git)
- Never commit actual `.env` files with secrets
- Validate environment variables on application startup
- Use secrets management in production
- Document all variables with descriptions and examples
- Use consistent naming conventions (UPPER_SNAKE_CASE)
- Prefix related variables (DB_, AWS_, REDIS_)
- Provide sensible defaults when possible
- Use type validation libraries
- Consider environment-specific configuration files
