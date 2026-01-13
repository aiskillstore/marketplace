---
name: system-integration-validator
description: Validates system integration before deployment. Use when checking ports, database connections, frontend-backend APIs, or debugging blocked/stuck workflows. Detects dead ends, bottlenecks, circular dependencies.
---

# System Integration Validator

Validates system integration before deployment.

## When to Use

- Pre-deployment validation
- Checking port availability
- Verifying database connections
- Debugging stuck workflows
- Detecting dead ends or circular dependencies

## Workflow

### Step 1: Check Ports

Verify all required ports are free.

### Step 2: Verify Databases

Test PostgreSQL and Redis connections.

### Step 3: Validate API Contracts

Ensure frontend ↔ backend match.

### Step 4: Analyze Data Flow

Detect dead ends, orphan inputs, bottlenecks.

---

## Pre-Deployment Checklist

1. **Ports** - All required ports free
2. **Database** - Connection, pool, migrations OK
3. **API Contract** - Frontend ↔ Backend match
4. **Data Flow** - No dead ends or loops

## Port Check
```bash
for port in 3000 3001 5432 6379 8080; do
  lsof -i :$port > /dev/null 2>&1 && echo "⚠️ $port IN USE" || echo "✅ $port free"
done
```

## Database Check
```bash
pg_isready -h localhost -p 5432 && echo "✅ PostgreSQL OK"
redis-cli ping && echo "✅ Redis OK"
```

## Flow Analysis

Look for:
- **Dead ends**: Output never consumed
- **Orphan inputs**: Input never provided
- **Bottlenecks**: High in-degree (>3 inputs)
- **Circular deps**: A → B → A

## Common Blocks
```typescript
// ❌ No timeout
await fetch(url)

// ✓ With timeout
const ctrl = new AbortController()
setTimeout(() => ctrl.abort(), 5000)
await fetch(url, { signal: ctrl.signal })
```
