---
name: configuration-validator
description: Validates environment variables, config files, and ensures all required settings are documented. Use when working with .env files, configs, or deployment settings.
allowed-tools: Read, Grep, Glob, Write, Bash
---

# Configuration Validator

Validates configuration files and environment variables to prevent runtime errors and missing settings.

## When to Use
- Working with environment variables or config files
- Deployment or configuration issues
- User mentions ".env", "config", "environment variables", or "settings"

## Instructions

### 1. Find Configuration Files

Search for:
- `.env`, `.env.example`, `.env.local`
- `config/`, `config.js`, `config.json`
- `settings.py`, `application.yml`
- `appsettings.json`, `.env.production`

### 2. Detect Missing Variables

**Compare .env.example vs .env:**
```bash
# Variables in example but not in .env
comm -23 <(grep -o '^[A-Z_]*' .env.example | sort) <(grep -o '^[A-Z_]*' .env | sort)
```

**Common required variables:**
```
DATABASE_URL
API_KEY
SECRET_KEY
NODE_ENV
PORT
```

### 3. Validate Variable Format

**Check for common issues:**

```javascript
// Missing quotes for values with spaces
DATABASE_URL=postgres://localhost/db name  // Bad
DATABASE_URL="postgres://localhost/db name"  // Good

// Missing protocol
API_URL=example.com  // Bad
API_URL=https://example.com  // Good

// Boolean as string
DEBUG=true  // Might be interpreted as string
DEBUG=1  // More explicit
```

### 4. Validate Required Variables at Runtime

**Node.js example:**
```javascript
const requiredEnvVars = [
  'DATABASE_URL',
  'API_KEY',
  'JWT_SECRET'
];

const missing = requiredEnvVars.filter(v => !process.env[v]);

if (missing.length > 0) {
  throw new Error(`Missing required env vars: ${missing.join(', ')}`);
}
```

**Python example:**
```python
import os

REQUIRED_ENV_VARS = [
    'DATABASE_URL',
    'SECRET_KEY',
    'ALLOWED_HOSTS'
]

missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]

if missing:
    raise EnvironmentError(f"Missing env vars: {', '.join(missing)}")
```

### 5. Type Validation

**Validate types:**
```javascript
const config = {
  port: parseInt(process.env.PORT || '3000', 10),
  debug: process.env.DEBUG === 'true',
  apiUrl: new URL(process.env.API_URL), // Throws if invalid
  maxConnections: Number(process.env.MAX_CONNECTIONS),
};

// Validate
if (isNaN(config.port) || config.port < 1 || config.port > 65535) {
  throw new Error('PORT must be a valid port number');
}
```

### 6. Generate .env.example

Create template from actual .env:

```bash
# Remove values, keep keys
sed 's/=.*/=/' .env > .env.example
```

**Or with placeholders:**
```
DATABASE_URL=postgres://user:password@localhost:5432/dbname
API_KEY=your_api_key_here
SECRET_KEY=generate_random_secret
PORT=3000
NODE_ENV=development
```

### 7. Configuration Schema

**Define schema (using Joi example):**
```javascript
const Joi = require('joi');

const envSchema = Joi.object({
  NODE_ENV: Joi.string()
    .valid('development', 'production', 'test')
    .required(),
  PORT: Joi.number()
    .port()
    .default(3000),
  DATABASE_URL: Joi.string()
    .uri()
    .required(),
  API_KEY: Joi.string()
    .min(32)
    .required(),
  DEBUG: Joi.boolean()
    .default(false),
}).unknown();

const { error, value } = envSchema.validate(process.env);

if (error) {
  throw new Error(`Config validation error: ${error.message}`);
}

module.exports = value;
```

### 8. Security Checks

**Don't commit secrets:**
```bash
# Check if .env is gitignored
if ! grep -q "^\.env$" .gitignore; then
  echo "Warning: .env not in .gitignore"
fi

# Check for hardcoded secrets in code
grep -r "api_key.*=.*['\"]" --exclude-dir=node_modules
```

**Common security issues:**
- Hardcoded passwords/keys
- Default secrets in production
- Exposed sensitive configs
- Unencrypted secrets

### 9. Environment-Specific Configs

**Organize by environment:**
```
.env.development
.env.staging
.env.production
.env.test
```

**Load appropriately:**
```javascript
require('dotenv').config({
  path: `.env.${process.env.NODE_ENV || 'development'}`
});
```

### 10. Document All Variables

**Create CONFIG.md:**
```markdown
# Configuration

## Environment Variables

### Required

- `DATABASE_URL`: PostgreSQL connection string
  - Format: `postgres://user:pass@host:port/db`
  - Example: `postgres://app:secret@localhost:5432/myapp`

- `API_KEY`: Third-party API key
  - Obtain from: https://dashboard.example.com
  - Required scopes: read, write

### Optional

- `PORT`: Server port (default: 3000)
- `DEBUG`: Enable debug logging (default: false)
- `MAX_CONNECTIONS`: Database pool size (default: 10)

## Setup

1. Copy `.env.example` to `.env`
2. Fill in all required values
3. Run `npm run validate-config` to verify
```

### 11. Validation Script

Create `scripts/validate-config.js`:
```javascript
const fs = require('fs');

function validateConfig() {
  const required = ['DATABASE_URL', 'API_KEY'];
  const missing = required.filter(v => !process.env[v]);

  if (missing.length > 0) {
    console.error(`❌ Missing: ${missing.join(', ')}`);
    process.exit(1);
  }

  console.log('✓ All required config variables present');
}

validateConfig();
```

### 12. Best Practices

- **Never commit .env**: Always gitignore
- **Maintain .env.example**: Keep it updated
- **Validate on startup**: Fail fast if misconfigured
- **Use strong defaults**: Sensible fallbacks
- **Document everything**: Explain each variable
- **Rotate secrets**: Regularly update keys
- **Use secret managers**: Vault, AWS Secrets Manager for production
- **Type check**: Validate types, not just presence

## Supporting Files
- `templates/config-validator.js`
- `templates/.env.example`
- `scripts/generate-env-example.sh`
