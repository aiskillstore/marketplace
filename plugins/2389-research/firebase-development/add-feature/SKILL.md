---
name: firebase-development-add-feature
description: This skill should be used when adding features to existing Firebase projects. Triggers on "add function", "create endpoint", "new tool", "add api", "new collection", "implement", "build feature". Guides TDD workflow with test-first development, security rules, and emulator verification.
---

# Firebase Add Feature

## Overview

This sub-skill guides adding new features to existing Firebase projects using TDD. It handles Cloud Functions, Firestore collections, and API endpoints.

**Key principles:**
- Write tests FIRST (TDD requirement)
- Use `{success, message, data?}` response pattern
- Every file starts with ABOUTME comments
- Verify with emulators before claiming done

## When This Sub-Skill Applies

- Adding a new Cloud Function
- Creating a new Firestore collection with rules
- Adding an API endpoint to Express app
- User says: "add function", "create endpoint", "new collection", "implement"

**Do not use for:**
- Initial project setup → `firebase-development:project-setup`
- Debugging → `firebase-development:debug`
- Code review → `firebase-development:validate`

## TodoWrite Workflow

Create checklist with these 12 steps:

### Step 1: Identify Feature Type
Determine what's being added:
- **HTTP Endpoint** - API route (GET/POST/etc.)
- **Firestore Trigger** - Runs on document changes
- **Scheduled Function** - Cron job
- **Callable Function** - Client SDK calls
- **New Collection** - Firestore collection with rules

### Step 2: Check Existing Architecture
Examine the project to understand patterns:

```bash
ls -la functions/src/
grep -r "onRequest" functions/src/
grep "express" functions/package.json
```

**Determine:** Architecture style, auth method, security model.

**Reference:** `docs/examples/express-function-architecture.md`

### Step 3: Write Failing Test First (TDD)
Create test file before implementation:

```typescript
// ABOUTME: Unit tests for [feature name] functionality
// ABOUTME: Tests [what the feature does] with various scenarios

import { describe, it, expect } from 'vitest';
import { handleYourFeature } from '../../tools/yourFeature';

describe('handleYourFeature', () => {
  it('should return success when given valid input', async () => {
    const result = await handleYourFeature('user-123', { name: 'test' });
    expect(result.success).toBe(true);
  });

  it('should return error for invalid input', async () => {
    const result = await handleYourFeature('user-123', { name: '' });
    expect(result.success).toBe(false);
  });
});
```

Run test to confirm it fails: `npm run test`

### Step 4: Create Function File with ABOUTME
Create implementation file:

```typescript
// ABOUTME: Implements [feature name] for [purpose]
// ABOUTME: Returns {success, message, data?} response

export async function handleYourFeature(
  userId: string,
  params: { name: string }
): Promise<{ success: boolean; message: string; data?: any }> {
  if (!userId) {
    return { success: false, message: 'Authentication required' };
  }
  if (!params.name) {
    return { success: false, message: 'Invalid input: name required' };
  }

  // Implementation here
  return { success: true, message: 'Success', data: { /* ... */ } };
}
```

**Reference:** `docs/examples/express-function-architecture.md`

### Step 5: Add Firestore Security Rules
Update `firestore.rules` for new collections:

**Server-write-only (preferred):**
```javascript
match /yourCollection/{docId} {
  allow read: if request.auth != null;
  allow write: if false;  // Only Cloud Functions
}
```

**Client-write (if needed):**
```javascript
match /yourCollection/{docId} {
  allow create: if request.auth != null &&
    request.resource.data.userId == request.auth.uid;
  allow update: if request.auth != null &&
    resource.data.userId == request.auth.uid &&
    request.resource.data.diff(resource.data).affectedKeys()
      .hasOnly(['name', 'updatedAt']);
}
```

**Reference:** `docs/examples/firestore-rules-patterns.md`

### Step 6: Update Indexes if Needed
Add to `firestore.indexes.json` for complex queries:

```json
{
  "collectionGroup": "yourCollection",
  "fields": [
    {"fieldPath": "userId", "order": "ASCENDING"},
    {"fieldPath": "createdAt", "order": "DESCENDING"}
  ]
}
```

Skip if no complex queries (single-field indexes are automatic).

### Step 7: Add Authentication Checks
Based on project pattern:

**API Keys:**
```typescript
app.post('/endpoint', apiKeyGuard, async (req, res) => {
  const userId = req.userId!;
  // ...
});
```

**Firebase Auth:**
```typescript
if (!req.auth) {
  res.status(401).json({ success: false, message: 'Auth required' });
  return;
}
const userId = req.auth.uid;
```

**Reference:** `docs/examples/api-key-authentication.md`

### Step 8: Implement Handler with Response Pattern
All handlers use consistent pattern:

```typescript
interface HandlerResponse {
  success: boolean;
  message: string;
  data?: any;
}
```

Include validation at every layer (defense in depth).

### Step 9: Export Function Properly
Add to `functions/src/index.ts`:

**Express:** Add route or switch case
**Domain-grouped:** `export * from './yourDomain';`
**Individual:** Import and export in index.js

Verify: `npm run build`

### Step 10: Make Tests Pass (TDD Green)
Run tests: `npm run test`

All tests should pass. If not, fix implementation (not tests).

### Step 11: Write Integration Test
Create `functions/src/__tests__/emulator/yourFeature.test.ts`:

Test complete workflow with emulators:
- HTTP request to endpoint
- Verify Firestore data created
- Test auth enforcement

Run: `npm run test:emulator` (with emulators running)

### Step 12: Test with Emulators
```bash
firebase emulators:start
open http://127.0.0.1:4000
```

**Verify:**
- Endpoint returns 200
- Response follows pattern
- Documents appear in Firestore
- Auth enforced (401 for invalid)
- Rules work in Rules Playground

## Response Pattern

All handlers MUST return:

```typescript
// Success
{ success: true, message: "Created", data: { id: "abc" } }

// Error
{ success: false, message: "Invalid input" }
```

## Verification Checklist

Before marking complete:
- [ ] Tests written FIRST and pass
- [ ] ABOUTME comments on all files
- [ ] Security rules added
- [ ] Auth checks implemented
- [ ] Response pattern followed
- [ ] Emulator testing successful
- [ ] Code linted

## Pattern References

- **Architecture:** `docs/examples/express-function-architecture.md`
- **Auth:** `docs/examples/api-key-authentication.md`
- **Rules:** `docs/examples/firestore-rules-patterns.md`
- **Emulators:** `docs/examples/emulator-workflow.md`
