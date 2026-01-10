# Secret Management

Complete guide to secure secret management in Next.js applications.

---

## Table of Contents

1. [Never Commit Secrets](#never-commit-secrets)
2. [Environment Variables](#environment-variables)
3. [Secret Rotation](#secret-rotation)
4. [Encryption at Rest](#encryption-at-rest)
5. [Secret Detection](#secret-detection)
6. [Production Secrets](#production-secrets)

---

## Never Commit Secrets

### .gitignore Configuration

```bash
# .gitignore
# ✅ Ignore all environment files
.env
.env.local
.env.development
.env.production
.env.test
.env*.local

# ✅ Ignore secret files
*.key
*.pem
*.p12
*.pfx
secrets/
credentials.json

# ✅ Ignore sensitive logs
*.log
npm-debug.log*
```

### .env.example Template

```bash
# .env.example
# ✅ Provide template without real values

# Database
DATABASE_URL="postgresql://user:password@localhost:5432/quetrex"

# OpenAI
OPENAI_API_KEY="sk-proj-YOUR_KEY_HERE"

# Stripe
STRIPE_PUBLIC_KEY="pk_test_YOUR_KEY_HERE"
STRIPE_SECRET_KEY="sk_test_YOUR_KEY_HERE"

# JWT
JWT_SECRET="generate-random-32-byte-string"

# Email
SMTP_HOST="smtp.example.com"
SMTP_PORT="587"
SMTP_USER="your-email@example.com"
SMTP_PASSWORD="your-smtp-password"

# Encryption
ENCRYPTION_KEY="generate-random-32-byte-hex-string"
```

### Verify No Secrets in Git

```bash
# ✅ Check for accidentally committed secrets
git log -p | grep -i "api_key\|password\|secret"

# ✅ Check current changes
git diff | grep -i "api_key\|password\|secret"

# ✅ Use git-secrets tool
git secrets --scan
git secrets --scan-history
```

---

## Environment Variables

### Loading Environment Variables

```typescript
// src/lib/env.ts
import { z } from 'zod'

// ✅ Define schema for environment variables
const envSchema = z.object({
  // Database
  DATABASE_URL: z.string().url(),

  // OpenAI
  OPENAI_API_KEY: z.string().min(1).startsWith('sk-'),

  // Stripe
  STRIPE_PUBLIC_KEY: z.string().min(1),
  STRIPE_SECRET_KEY: z.string().min(1).startsWith('sk_'),

  // JWT
  JWT_SECRET: z.string().min(32),

  // Encryption
  ENCRYPTION_KEY: z.string().regex(/^[0-9a-f]{64}$/),  // 32 bytes in hex

  // App
  NODE_ENV: z.enum(['development', 'production', 'test']),
  NEXT_PUBLIC_APP_URL: z.string().url(),
})

// ✅ Validate and export
export const env = envSchema.parse(process.env)

// ✅ Type-safe access
export type Env = z.infer<typeof envSchema>
```

### Usage in Application

```typescript
// ✅ Import validated environment
import { env } from '@/lib/env'

// ✅ Type-safe access
const apiKey = env.OPENAI_API_KEY  // TypeScript knows it's a string
const dbUrl = env.DATABASE_URL  // TypeScript knows it's a URL

// ❌ DON'T access process.env directly
const unsafeKey = process.env.OPENAI_API_KEY  // Might be undefined!
```

### Client-Side Environment Variables

```typescript
// ❌ DON'T: Expose secrets to client
// next.config.js
module.exports = {
  env: {
    STRIPE_SECRET_KEY: process.env.STRIPE_SECRET_KEY,  // EXPOSED TO CLIENT!
  },
}

// ✅ DO: Only expose public variables
// next.config.js
module.exports = {
  env: {
    NEXT_PUBLIC_STRIPE_PUBLIC_KEY: process.env.STRIPE_PUBLIC_KEY,
  },
}

// ✅ Use NEXT_PUBLIC_ prefix for client-accessible vars
// .env
NEXT_PUBLIC_API_URL="https://api.example.com"
NEXT_PUBLIC_STRIPE_PUBLIC_KEY="pk_test_..."

// Client component
'use client'

export function PaymentForm() {
  const publishableKey = process.env.NEXT_PUBLIC_STRIPE_PUBLIC_KEY

  // Use publishableKey (safe - public)
}
```

---

## Secret Rotation

### Rotating API Keys

```typescript
// src/lib/secrets/rotate.ts

// ✅ Support multiple API keys during rotation
export function getAPIKey(service: 'openai' | 'stripe'): string {
  const keys = {
    openai: [
      process.env.OPENAI_API_KEY!,
      process.env.OPENAI_API_KEY_OLD,  // Old key during rotation
    ].filter(Boolean),
    stripe: [
      process.env.STRIPE_SECRET_KEY!,
      process.env.STRIPE_SECRET_KEY_OLD,
    ].filter(Boolean),
  }

  // Return primary key
  return keys[service][0]
}

// ✅ Rotate key gradually
// Step 1: Add new key as primary, keep old key
// .env
// OPENAI_API_KEY="sk-new-key-123"
// OPENAI_API_KEY_OLD="sk-old-key-456"

// Step 2: Wait for all requests with old key to complete (24-48 hours)

// Step 3: Remove old key
// .env
// OPENAI_API_KEY="sk-new-key-123"
```

### JWT Secret Rotation

```typescript
// src/lib/auth/jwt-rotate.ts
import { SignJWT, jwtVerify } from 'jose'

// ✅ Support multiple JWT secrets
const CURRENT_SECRET = new TextEncoder().encode(process.env.JWT_SECRET!)
const OLD_SECRETS = [
  process.env.JWT_SECRET_OLD_1,
  process.env.JWT_SECRET_OLD_2,
].filter(Boolean).map(s => new TextEncoder().encode(s!))

export async function createToken(payload: any): Promise<string> {
  // Always sign with current secret
  return new SignJWT(payload)
    .setProtectedHeader({ alg: 'HS256', kid: 'current' })
    .setIssuedAt()
    .setExpirationTime('24h')
    .sign(CURRENT_SECRET)
}

export async function verifyToken(token: string): Promise<any> {
  // Try current secret first
  try {
    const { payload } = await jwtVerify(token, CURRENT_SECRET)
    return payload
  } catch {
    // Try old secrets
    for (const oldSecret of OLD_SECRETS) {
      try {
        const { payload } = await jwtVerify(token, oldSecret)

        // ✅ Token is valid but using old secret - re-issue with new secret
        console.warn('Token using old secret, should be rotated')

        return payload
      } catch {
        continue
      }
    }

    throw new Error('Invalid token')
  }
}
```

### Database Credential Rotation

```bash
# ✅ Rotate database password
# Step 1: Create new user with new password
CREATE USER quetrex_new WITH PASSWORD 'new-secure-password';
GRANT ALL PRIVILEGES ON DATABASE quetrex TO quetrex_new;

# Step 2: Update application environment
DATABASE_URL="postgresql://quetrex_new:new-secure-password@localhost:5432/quetrex"

# Step 3: Deploy application

# Step 4: Wait for all connections to drain

# Step 5: Remove old user
DROP USER quetrex_old;
```

---

## Encryption at Rest

### Encrypting Secrets in Database

```typescript
// src/lib/crypto/encrypt.ts
import crypto from 'crypto'

// ✅ Load encryption key from environment
const ENCRYPTION_KEY = Buffer.from(process.env.ENCRYPTION_KEY!, 'hex')  // 32 bytes

export function encrypt(plaintext: string): {
  encrypted: string
  iv: string
  authTag: string
} {
  // ✅ Generate random IV for each encryption
  const iv = crypto.randomBytes(16)

  // ✅ Use AES-256-GCM (authenticated encryption)
  const cipher = crypto.createCipheriv('aes-256-gcm', ENCRYPTION_KEY, iv)

  let encrypted = cipher.update(plaintext, 'utf8', 'hex')
  encrypted += cipher.final('hex')

  const authTag = cipher.getAuthTag()

  return {
    encrypted,
    iv: iv.toString('hex'),
    authTag: authTag.toString('hex'),
  }
}

export function decrypt(encrypted: string, iv: string, authTag: string): string {
  const decipher = crypto.createDecipheriv(
    'aes-256-gcm',
    ENCRYPTION_KEY,
    Buffer.from(iv, 'hex')
  )

  decipher.setAuthTag(Buffer.from(authTag, 'hex'))

  let decrypted = decipher.update(encrypted, 'hex', 'utf8')
  decrypted += decipher.final('utf8')

  return decrypted
}
```

### Storing Encrypted Secrets

```typescript
// src/lib/secrets/store.ts
import { db } from '@/lib/db'
import { encrypt, decrypt } from '@/lib/crypto/encrypt'

// ✅ Store encrypted API key
export async function storeAPIKey(userId: string, service: string, apiKey: string) {
  const { encrypted, iv, authTag } = encrypt(apiKey)

  return db.apiKey.create({
    data: {
      userId,
      service,
      encryptedKey: encrypted,
      iv,
      authTag,
    },
  })
}

// ✅ Retrieve and decrypt API key
export async function getAPIKey(userId: string, service: string): Promise<string | null> {
  const record = await db.apiKey.findFirst({
    where: { userId, service },
  })

  if (!record) {
    return null
  }

  return decrypt(record.encryptedKey, record.iv, record.authTag)
}
```

---

## Secret Detection

### Pre-commit Hook

```bash
# .husky/pre-commit
#!/bin/sh

# ✅ Check for secrets before commit
echo "Checking for secrets..."

# Check for common secret patterns
if git diff --cached | grep -iE "(api_key|password|secret|token).*(=|:).*['\"][a-zA-Z0-9]{20,}['\"]"; then
  echo "❌ Potential secret detected in staged changes!"
  echo "   Remove secrets before committing."
  exit 1
fi

# Check for .env files
if git diff --cached --name-only | grep -E "\.env(\..*)?$"; then
  echo "❌ .env file in staged changes!"
  echo "   Never commit .env files."
  exit 1
fi

echo "✅ No secrets detected"
```

### Automated Secret Scanning

```bash
# ✅ Install gitleaks
brew install gitleaks

# ✅ Scan repository
gitleaks detect --source . --verbose

# ✅ Scan specific commit
gitleaks detect --source . --log-opts="HEAD^..HEAD"

# ✅ Add to CI/CD
# .github/workflows/secrets-scan.yml
name: Secret Scan

on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for scanning

      - name: Run gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### TruffleHog Scanning

```bash
# ✅ Install trufflehog
pip install trufflehog

# ✅ Scan repository
trufflehog --regex --entropy=True .

# ✅ Scan Git history
trufflehog --regex --entropy=True --max_depth=1000 file://$(pwd)
```

---

## Production Secrets

### Vercel Environment Variables

```bash
# ✅ Set production secrets via Vercel CLI
vercel env add DATABASE_URL production
vercel env add OPENAI_API_KEY production
vercel env add JWT_SECRET production

# ✅ Or via Vercel Dashboard
# Project Settings → Environment Variables
# Add each secret with appropriate scope (Production, Preview, Development)
```

### AWS Secrets Manager

```typescript
// src/lib/secrets/aws.ts
import { SecretsManagerClient, GetSecretValueCommand } from '@aws-sdk/client-secrets-manager'

const client = new SecretsManagerClient({ region: 'us-east-1' })

export async function getSecret(secretName: string): Promise<string> {
  try {
    const response = await client.send(
      new GetSecretValueCommand({
        SecretId: secretName,
      })
    )

    return response.SecretString!
  } catch (error) {
    console.error('Error retrieving secret:', error)
    throw error
  }
}

// Usage
const apiKey = await getSecret('quetrex/openai-api-key')
```

### HashiCorp Vault

```typescript
// src/lib/secrets/vault.ts
import vault from 'node-vault'

const vaultClient = vault({
  apiVersion: 'v1',
  endpoint: process.env.VAULT_ADDR,
  token: process.env.VAULT_TOKEN,
})

export async function getSecret(path: string): Promise<any> {
  try {
    const result = await vaultClient.read(path)
    return result.data
  } catch (error) {
    console.error('Error reading from Vault:', error)
    throw error
  }
}

// Usage
const secrets = await getSecret('secret/data/quetrex/production')
const apiKey = secrets.openai_api_key
```

---

## Summary Checklist

**Secret Management:**

- [ ] `.env` files in `.gitignore`
- [ ] `.env.example` provided (no real values)
- [ ] No hardcoded secrets in source code
- [ ] Environment variables validated with Zod
- [ ] Client-side variables use `NEXT_PUBLIC_` prefix
- [ ] Secrets never committed to git
- [ ] Pre-commit hooks check for secrets
- [ ] Automated secret scanning in CI/CD
- [ ] API keys rotated every 90 days
- [ ] JWT secrets rotated when compromised
- [ ] Sensitive data encrypted at rest (AES-256-GCM)
- [ ] Encryption keys stored securely
- [ ] Production secrets in secure vault (AWS Secrets Manager, Vault)
- [ ] Database credentials rotated regularly
- [ ] Old secrets cleaned up after rotation

**Secret Rotation Schedule:**
- API keys: Every 90 days
- JWT secrets: When compromised or annually
- Database passwords: Every 6-12 months
- Encryption keys: Annually or when compromised

**References:**
- OWASP Secret Management: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- Gitleaks: https://github.com/gitleaks/gitleaks
- AWS Secrets Manager: https://aws.amazon.com/secrets-manager/
- HashiCorp Vault: https://www.vaultproject.io/
