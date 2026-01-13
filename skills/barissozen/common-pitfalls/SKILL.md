---
name: common-pitfalls
description: Orchestrates pitfall prevention skills for common development issues. Auto-triggered during code review to check for TanStack Query, Drizzle ORM, Express API, React, WebSocket, blockchain RPC, and security pitfalls.
---

# Common Pitfalls Prevention

Orchestrates specialized pitfall prevention skills learned from production issues. Use during code review to automatically check for common mistakes.

## When to Use

- During code review (auto-triggered by full-review skill)
- Before committing changes
- When debugging production issues
- Reviewing unfamiliar code patterns

## Workflow

### Step 1: Identify Code Categories

Based on changed files, determine which sub-skills to invoke:

| File Pattern | Sub-Skill |
|-------------|-----------|
| `**/hooks/**`, `useQuery`, `useMutation` | pitfalls-tanstack-query |
| `**/db/**`, `schema.ts`, `drizzle` | pitfalls-drizzle-orm |
| `**/routes/**`, `router.`, `app.` | pitfalls-express-api |
| `**/components/**`, `**/pages/**`, `.tsx` | pitfalls-react |
| `websocket`, `wss`, `ws.` | pitfalls-websocket |
| `contract`, `rpc`, `multicall`, `gas` | pitfalls-blockchain |
| `session`, `key`, `cache`, `log` | pitfalls-security |

### Step 2: Invoke Relevant Sub-Skills

For each category found, invoke the corresponding skill for detailed patterns.

### Step 3: Generate Combined Report

Aggregate findings from all invoked sub-skills.

## Sub-Skills Reference

| Skill | Focus Area |
|-------|------------|
| **pitfalls-tanstack-query** | Query keys, invalidation, v5 patterns |
| **pitfalls-drizzle-orm** | Schema types, migrations, array columns |
| **pitfalls-express-api** | Routes, status codes, storage patterns |
| **pitfalls-react** | Components, forms, a11y, responsive |
| **pitfalls-websocket** | Server setup, heartbeat, reconnection |
| **pitfalls-blockchain** | RPC errors, gas, multicall, nonces |
| **pitfalls-security** | Session keys, caching, logging, secrets |

## Quick Reference Checklist

### Core
- [ ] TanStack Query keys use full URL paths
- [ ] Mutations invalidate relevant queries
- [ ] Drizzle types exported for all models
- [ ] API routes return correct status codes
- [ ] All RPC calls wrapped in try/catch
- [ ] WebSocket has heartbeat/reconnection
- [ ] React components handle loading/error states
- [ ] No secrets in logs or frontend code

### Type Safety
- [ ] No `any` types - use `unknown` and narrow
- [ ] Types inferred from schema ($inferSelect, z.infer)
- [ ] Type guards for runtime validation

### Financial
- [ ] BigInt for all token amounts
- [ ] Decimal.js for price calculations
- [ ] Proper rounding (floor/ceil)

### Blockchain
- [ ] Gas estimation with buffer
- [ ] EIP-1559 gas pricing
- [ ] Transaction simulation before send
- [ ] Multicall uses `allowFailure: true`

### Security
- [ ] Session keys have expiry and limits
- [ ] AES-256-GCM for stored credentials
- [ ] Audit logging for sensitive operations
- [ ] Rate limiting with exponential backoff
