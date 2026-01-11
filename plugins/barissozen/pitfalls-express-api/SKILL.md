---
name: pitfalls-express-api
description: Express API conventions and storage patterns. Use when building REST APIs, defining routes, or implementing storage interfaces. Triggers on: Express, router, API route, status code, storage interface.
---

# Express API Pitfalls

Common pitfalls and correct patterns for Express APIs.

## When to Use

- Building REST API routes
- Implementing storage interfaces
- Setting HTTP status codes
- Validating request bodies
- Reviewing Express API code

## Workflow

### Step 1: Verify Route Structure

Check that routes follow REST conventions.

### Step 2: Check Status Codes

Ensure correct status codes for each operation.

### Step 3: Verify Validation

Confirm input validation middleware is in place.

---

## Route Structure

```typescript
// Public routes
GET  /api/resource          // List
GET  /api/resource/:id      // Get one

// Admin routes (with auth middleware)
POST   /api/admin/resource      // Create (201)
PATCH  /api/admin/resource/:id  // Update (200)
DELETE /api/admin/resource/:id  // Delete (204)

// ✅ Always validate before storage
router.post('/', validateBody(schema), async (req, res) => {
  const validated = req.body; // Already validated by middleware
});
```

## Status Codes

| Operation | Success | Not Found | Invalid |
|-----------|---------|-----------|---------|
| GET | 200 | 404 | 400 |
| POST | 201 | - | 400 |
| PATCH | 200 | 404 | 400 |
| DELETE | 204 | 404 | - |

## Storage Interface Pattern

```typescript
// ✅ Define interface for all storage operations
interface IStorage {
  // Strategies
  getStrategies(): Promise<Strategy[]>;
  getStrategy(id: string): Promise<Strategy | undefined>;
  createStrategy(data: NewStrategy): Promise<Strategy>;
  updateStrategy(id: string, data: Partial<Strategy>): Promise<Strategy | undefined>;
  deleteStrategy(id: string): Promise<boolean>;
}

// ✅ Implement for different backends
class DbStorage implements IStorage { ... }  // PostgreSQL
class MemStorage implements IStorage { ... } // Testing
```

## Background Job Patterns

```typescript
// ✅ Cleanup on process exit
const intervals: NodeJS.Timeout[] = [];

function startJob(fn: () => void, ms: number) {
  const id = setInterval(fn, ms);
  intervals.push(id);
  return id;
}

process.on('SIGTERM', () => {
  intervals.forEach(clearInterval);
  process.exit(0);
});

// ✅ Handle overlapping executions
let isRunning = false;
async function scanForOpportunities() {
  if (isRunning) return;
  isRunning = true;
  try {
    await scan();
  } finally {
    isRunning = false;
  }
}
```

## Quick Checklist

- [ ] Routes follow REST conventions
- [ ] Correct status codes returned
- [ ] Input validation on all endpoints
- [ ] Storage interface abstraction used
- [ ] Background jobs handle cleanup
