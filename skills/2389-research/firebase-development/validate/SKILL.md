---
name: firebase-development-validate
description: This skill should be used when reviewing Firebase code against security model and best practices. Triggers on "review firebase", "check firebase", "validate", "audit firebase", "security review", "look at firebase code". Validates configuration, rules, architecture, and security.
---

# Firebase Code Validation

## Overview

This sub-skill validates existing Firebase code against proven patterns and security best practices. It checks configuration, rules, architecture consistency, authentication, testing, and production readiness.

**Key principles:**
- Validate against chosen architecture patterns
- Check security rules thoroughly
- Verify test coverage exists
- Review production readiness

## When This Sub-Skill Applies

- Conducting code review of Firebase project
- Auditing security implementation
- Preparing for production deployment
- User says: "review firebase", "validate", "audit firebase", "check firebase code"

**Do not use for:**
- Initial setup → `firebase-development:project-setup`
- Adding features → `firebase-development:add-feature`
- Debugging active errors → `firebase-development:debug`

## TodoWrite Workflow

Create checklist with these 9 steps:

### Step 1: Check firebase.json Structure

Validate required sections:
- `hosting` - Array or object present
- `functions` - Source directory, runtime, predeploy hooks
- `firestore` - Rules and indexes files
- `emulators` - Local development config

Check hosting pattern matches implementation (site:, target:, or single).

**Reference:** `docs/examples/multi-hosting-setup.md`

### Step 2: Validate Emulator Configuration

Critical settings:
```json
{
  "emulators": {
    "singleProjectMode": true,
    "ui": { "enabled": true }
  }
}
```

Verify all services in use have emulator entries.

**Reference:** `docs/examples/emulator-workflow.md`

### Step 3: Review Firestore Rules

Check for:
- Helper functions at top (`isAuthenticated()`, `isOwner()`)
- Consistent security model (server-write-only OR client-write-validated)
- `diff().affectedKeys().hasOnly([...])` for client writes
- Collection group rules if using `collectionGroup()` queries
- Default deny rule at bottom

**Reference:** `docs/examples/firestore-rules-patterns.md`

### Step 4: Validate Functions Architecture

Identify pattern in use:
- **Express:** Check `middleware/`, `tools/`, CORS, health endpoint
- **Domain-Grouped:** Check exports, domain boundaries, `shared/`
- **Individual:** Check one function per file structure

**Critical:** Don't mix patterns. Verify consistency throughout.

**Reference:** `docs/examples/express-function-architecture.md`

### Step 5: Check Authentication Implementation

**For API Keys:**
- Middleware validates key format with project prefix
- Uses `collectionGroup('apiKeys')` query
- Checks `active: true` flag
- Attaches `userId` to request

**For Firebase Auth:**
- Functions check `request.auth.uid`
- Role lookups use Firestore user document
- Client connects to auth emulator in development

**Reference:** `docs/examples/api-key-authentication.md`

### Step 6: Verify ABOUTME Comments

All `.ts` files should start with:
```typescript
// ABOUTME: Brief description of what this file does
// ABOUTME: Second line with additional context
```

```bash
grep -L "ABOUTME:" functions/src/**/*.ts  # Find missing
```

### Step 7: Review Test Coverage

Check for:
- Unit tests: `functions/src/__tests__/**/*.test.ts`
- Integration tests: `functions/src/__tests__/emulator/**/*.test.ts`
- `vitest.config.ts` and `vitest.emulator.config.ts` exist
- Coverage threshold met (60%+)

```bash
npm test && npm run test:coverage
```

### Step 8: Validate Error Handling

All handlers must:
- Use try-catch blocks
- Return `{ success: boolean, message: string, data?: any }`
- Use proper HTTP status codes (400, 401, 403, 500)
- Log errors with `console.error`
- Validate input before processing

### Step 9: Security and Production Review

**Security checks:**
- No secrets in code (`grep -r "apiKey.*=" functions/src/`)
- `.env` files in `.gitignore`
- No `allow read, write: if true;` in rules
- Sensitive fields protected from client writes

**Production checks:**
- `npm audit` clean
- Build succeeds: `npm run build`
- Tests pass: `npm test`
- Correct project in `.firebaserc`
- Indexes defined for complex queries

## Validation Checklists

### Hosting Pattern
- [ ] Pattern matches firebase.json config
- [ ] Sites/targets exist in Firebase Console
- [ ] Rewrites reference valid functions
- [ ] Emulator ports configured

### Authentication Pattern
- [ ] Auth method matches security model
- [ ] Middleware/checks implemented correctly
- [ ] Environment variables documented
- [ ] Emulator connection configured

### Security Model
- [ ] Server-write-only: All `allow write: if false;`
- [ ] Client-write: `diff().affectedKeys()` validation
- [ ] Default deny rule present
- [ ] Helper functions used consistently

## Common Issues

| Issue | Fix |
|-------|-----|
| Missing `singleProjectMode` | Add to emulators config |
| No default deny rule | Add `match /{document=**} { allow: if false; }` |
| Mixed architecture | Migrate to consistent pattern |
| Missing ABOUTME | Add 2-line header to all .ts files |
| No integration tests | Add emulator tests for workflows |
| Inconsistent response format | Standardize to `{success, message, data?}` |
| No error handling | Add try-catch to all handlers |
| Secrets in code | Move to environment variables |

## Integration with Superpowers

For general code quality review beyond Firebase patterns, invoke `superpowers:requesting-code-review`.

## Output

After validation, provide:
- Summary of findings
- Issues categorized by severity (critical, important, nice-to-have)
- Recommendations for remediation
- Confirmation of best practices compliance

## Pattern References

- **Hosting:** `docs/examples/multi-hosting-setup.md`
- **Auth:** `docs/examples/api-key-authentication.md`
- **Functions:** `docs/examples/express-function-architecture.md`
- **Rules:** `docs/examples/firestore-rules-patterns.md`
- **Emulators:** `docs/examples/emulator-workflow.md`
