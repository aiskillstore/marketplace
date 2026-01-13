---
name: pitfalls-security
description: "Security patterns for session keys, caching, logging, and environment variables. Use when implementing authentication, caching sensitive data, or setting up logging. Triggers on: session key, private key, cache, logging, secrets, environment variable."
---

# Security Pitfalls

Common pitfalls and correct patterns for security.

## When to Use

- Implementing session key management
- Caching data (especially sensitive)
- Setting up structured logging
- Handling environment variables
- Reviewing security-sensitive code

## Workflow

### Step 1: Check Key Storage

Verify no private keys stored in plaintext.

### Step 2: Verify Cache Safety

Ensure sensitive data not cached inappropriately.

### Step 3: Check Logging

Confirm no secrets in logs.

---

## Session Key Security

```typescript
// ❌ NEVER store private keys
localStorage.setItem('privateKey', key);  // CATASTROPHIC

// ✅ Use session keys with limited permissions
interface SessionKey {
  address: Address;
  permissions: Permission[];
  expiresAt: Date;
  maxPerTrade: bigint;
}

// ✅ AES-256-GCM for any stored credentials
import { createCipheriv, randomBytes } from 'crypto';
const iv = randomBytes(16);
const cipher = createCipheriv('aes-256-gcm', key, iv);

// ✅ Audit logging for all key operations
await auditLog.create({
  action: 'SESSION_KEY_CREATED',
  userId,
  metadata: { permissions, expiresAt },
});
```

## Environment Variables

```typescript
// Frontend (Vite)
const apiUrl = import.meta.env.VITE_API_URL;  // ✅ VITE_ prefix required
// ❌ process.env.API_URL won't work in frontend

// Backend
const dbUrl = process.env.DATABASE_URL;

// ❌ NEVER log secrets
console.log('Config:', config);  // May contain secrets!
// ✅ Log safely
console.log('Config loaded for:', config.environment);
```

## Caching Strategies

```typescript
// ✅ Server-side cache for expensive computations
const priceCache = new Map<string, { value: number; expires: number }>();

function getCachedPrice(token: string): number | null {
  const cached = priceCache.get(token);
  if (cached && cached.expires > Date.now()) {
    return cached.value;
  }
  return null;
}

// ✅ TTL based on data freshness needs
const CACHE_TTL = {
  tokenPrice: 10_000,      // 10s - prices change fast
  poolReserves: 5_000,     // 5s - critical for swaps
  gasPrice: 15_000,        // 15s
  userBalance: 30_000,     // 30s
  tokenMetadata: 3600_000, // 1 hour - rarely changes
};

// ❌ Never cache user-specific sensitive data
cache.set(`user:${userId}:privateKey`, key);  // NEVER!
```

## Structured Logging

```typescript
// ✅ Structured logging (JSON format)
const logger = {
  info: (message: string, context?: object) => {
    console.log(JSON.stringify({
      level: 'info',
      message,
      timestamp: new Date().toISOString(),
      ...context,
    }));
  },
  error: (message: string, error: Error, context?: object) => {
    console.error(JSON.stringify({
      level: 'error',
      message,
      error: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString(),
      ...context,
    }));
  },
};

// ✅ Include context
logger.info('Trade executed', {
  userId: 'user123',
  txHash: '0x...',
  chain: 'ethereum',
  profit: '12.34',
});

// ❌ NEVER log secrets
logger.info('Config', { apiKey: process.env.API_KEY });  // NEVER!
```

## Audit Logging

```typescript
// ✅ Audit logging for sensitive operations
await auditLog.create({
  action: 'TRADE_EXECUTED',
  userId,
  before: previousState,
  after: newState,
  timestamp: new Date(),
  metadata: { txHash, chain },
});
```

## Quick Checklist

- [ ] No private keys in localStorage
- [ ] Session keys have expiry and limits
- [ ] AES-256-GCM for stored credentials
- [ ] Audit logging for sensitive operations
- [ ] No secrets in console.log
- [ ] Sensitive data not cached inappropriately
- [ ] VITE_ prefix for frontend env vars
