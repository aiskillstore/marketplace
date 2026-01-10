---
name: firebase-development:debug
description: This skill should be used when troubleshooting Firebase emulator issues, rules violations, function errors, auth problems, or deployment failures. Triggers on "error", "not working", "debug", "troubleshoot", "failing", "broken", "permission denied", "emulator issue".
---

# Firebase Debugging

## Overview

This sub-skill guides systematic troubleshooting of Firebase development issues. It handles emulator problems, rules violations, function errors, auth issues, and deployment failures.

**Key principles:**
- Identify issue type first (emulator, rules, functions, auth, deployment)
- Use Emulator UI and Rules Playground for diagnosis
- Export emulator state before restarting
- Document issues and solutions for future reference

## When This Sub-Skill Applies

- Emulators won't start or have port conflicts
- Getting Firestore rules violations (PERMISSION_DENIED)
- Cloud Functions returning errors or not executing
- Authentication not working in emulators
- Deployment fails with cryptic errors
- User says: "debug", "troubleshoot", "error", "not working", "failing"

**Do not use for:**
- Setting up new projects → `firebase-development:project-setup`
- Adding new features → `firebase-development:add-feature`
- Code review without specific errors → `firebase-development:validate`

## TodoWrite Workflow

Create checklist with these 10 steps:

### Step 1: Identify Issue Type

Categorize the error:

| Category | Symptoms | Keywords |
|----------|----------|----------|
| Emulator Won't Start | Port conflicts, initialization errors | "EADDRINUSE", "emulator failed" |
| Rules Violation | Permission denied on read/write | "PERMISSION_DENIED", "insufficient" |
| Function Error | HTTP 500, timeout, not executing | "function failed", "timeout" |
| Auth Issue | Token errors, not authenticated | "auth failed", "invalid token" |
| Deployment Failure | Deploy command fails | "deployment failed", "deploy error" |

**If unclear, use AskUserQuestion** to clarify issue type.

### Step 2: Check Emulator Logs and Terminal

**For running emulators:** Watch terminal output while reproducing the issue.

**For emulators that won't start:**
```bash
lsof -i :4000 && lsof -i :5001 && lsof -i :8080  # Check ports
kill -9 <PID>  # Kill conflicting process
```

**For deployment errors:** Check `firebase-debug.log`

**Reference:** `docs/examples/emulator-workflow.md`

### Step 3: Open Emulator UI

```bash
open http://127.0.0.1:4000
```

Use Emulator UI to:
- View Firestore data and structure
- Check authenticated users
- Review function invocation logs
- Search consolidated logs

### Step 4: Test Rules in Playground (If Rules Issue)

In Emulator UI → Firestore → Rules Playground:
1. Select operation type (get/list/create/update/delete)
2. Specify document path
3. Set auth context (uid, custom claims)
4. Add request data for writes
5. Run simulation and review evaluation trace

**Reference:** `docs/examples/firestore-rules-patterns.md`

### Step 5: Add Debug Logging (If Function Error)

Add strategic console.log statements:
- Function entry confirmation
- Input data (req.body, req.params)
- Auth context (userId, API key)
- Intermediate operation results
- Error details with stack trace

Watch terminal output while reproducing.

**Reference:** `docs/examples/express-function-architecture.md`

### Step 6: Verify Auth Configuration (If Auth Issue)

Check environment variables:
```bash
cat functions/.env
cat hosting/.env.local  # Should have NEXT_PUBLIC_USE_EMULATORS=true
```

Check emulator connection in client code and API key middleware.

**Reference:** `docs/examples/api-key-authentication.md`

### Step 7: Check Deployment Config (If Deployment Failure)

```bash
cat firebase-debug.log  # Full error details
cat firebase.json       # Config issues
cat .firebaserc         # Project ID
firebase target:list    # Verify targets
```

Test predeploy hooks locally:
```bash
cd functions && npm run build
```

### Step 8: Export Emulator State

Before making fixes:
```bash
# Graceful shutdown (Ctrl+C exports automatically)
# Or manual export:
firebase emulators:export ./backup-data
```

Verify export: `ls -la .firebase/emulator-data/`

### Step 9: Implement and Test Fix

Apply fix based on diagnosis, then:
```bash
firebase emulators:start --import=.firebase/emulator-data
```

Verify:
- Original error no longer occurs
- Terminal shows success logs
- Emulator UI confirms expected behavior

### Step 10: Document Issue and Solution

Create entry in `docs/debugging-notes.md`:
- Symptom and exact error message
- Root cause
- Solution applied
- Prevention for future

## Common Issues Quick Reference

| Issue | Solution |
|-------|----------|
| Port conflicts | `lsof -i :<port>`, kill process |
| Data persistence lost | Use Ctrl+C (not kill) to stop emulators |
| Cold start delays | First call takes 5-10s (normal) |
| Rules not reloading | Restart emulators |
| Admin vs Client SDK | Admin bypasses rules, client respects them |
| Missing CORS | Add `app.use(cors({ origin: true }))` |
| Emulator connection | Set `NEXT_PUBLIC_USE_EMULATORS=true` |
| API key prefix | Verify prefix matches actual keys |

## Integration with Superpowers

If Firebase-specific tools don't reveal root cause, invoke `superpowers:systematic-debugging` for:
- Complex multi-service interactions
- Race conditions or timing issues
- Call stack tracing beyond Firebase layer

## Pattern References

- **Emulator workflow:** `docs/examples/emulator-workflow.md`
- **Rules patterns:** `docs/examples/firestore-rules-patterns.md`
- **Auth patterns:** `docs/examples/api-key-authentication.md`
- **Functions:** `docs/examples/express-function-architecture.md`
