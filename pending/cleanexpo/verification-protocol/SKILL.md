---
name: verification-protocol
description: Independent verification of task completion - eliminates self-attestation
version: 1.0.0
applies_to: [all-agents]
priority: critical
---

# Verification Protocol - Elimination of Self-Attestation

## Purpose

**The Problem**: Agents were verifying their own work and always returning `success: true` by default.

**The Solution**: Independent verification by a DIFFERENT agent that does NOT trust the original agent's claims.

**The Rule**: `verified=true` ONLY when EVIDENCE proves all completion criteria are met.

---

## Core Principle

```
NEVER verify your own work.
ALWAYS verify with independent evidence.
ASSUME claims are false until proven true.
Block completion without proof.
```

---

## Verification Protocol

### Step 1: Task Completion Claim
Agent claims task is complete and provides:
```json
{
  "task_id": "task-123",
  "claimed_outputs": ["/path/to/file.ts", "/path/to/test.ts"],
  "completion_criteria": [
    "file_exists:/path/to/file.ts",
    "no_placeholders:/path/to/file.ts",
    "typescript_compiles:/path/to/file.ts",
    "lint_passes:/path/to/file.ts",
    "tests_pass:/path/to/test.ts"
  ]
}
```

### Step 2: Independent Verification Requested
Orchestrator sends to Independent Verifier Agent (different agent).

### Step 3: Verification Execution
Independent Verifier checks EVERY criterion with actual evidence:

```
file_exists → fs.stat(path) && size > 0
  Proof: /path/to/file.ts, 1,247 bytes, modified 2025-12-02T14:30:00Z

no_placeholders → Scan for TODO, TBD, FIXME, [INSERT]
  Proof: 0 placeholders found

typescript_compiles → npx tsc --noEmit [file]
  Proof: Compilation successful, 0 errors

lint_passes → npx eslint [file]
  Proof: 0 linting errors

tests_pass → npm test -- [file]
  Proof: 15 tests passed, 0 failed
```

### Step 4: Verification Result Returned
```json
{
  "verified": true,
  "evidence": [
    {
      "criterion": "file_exists:/path/to/file.ts",
      "method": "fs.stat(path) && size > 0",
      "result": "pass",
      "proof": "File: /path/to/file.ts, Size: 1247 bytes"
    },
    // ... more evidence ...
  ],
  "failures": [],
  "verifier_agent_id": "independent-verifier-1",
  "timestamp": "2025-12-02T14:30:00Z"
}
```

### Step 5: Task Status Updated
- `verified=true` → Task marked COMPLETE, evidence logged
- `verified=false` → Task returned to agent with failure list
  - Agent has 3 attempts to fix and re-submit
  - After 3 failures → ESCALATE TO HUMAN REVIEW

---

## Verification Methods

### File Verification
**Method**: `fs.existsSync(path) && fs.statSync(path).size > 0`
**Evidence**: File path, size in bytes, last modified timestamp
**Failure Triggers**:
- File does not exist
- File is empty (0 bytes)
- File not accessible (permission error)

### Placeholder Detection
**Method**: Regex scan for TODO, TBD, FIXME, [INSERT], [IMPLEMENT]
**Evidence**: Count and line numbers of placeholders found
**Failure Triggers**:
- ANY placeholder found (not "looks complete enough")
- Incomplete implementation markers remain

### TypeScript Compilation
**Method**: `npx tsc --noEmit [file]`
**Evidence**: Compiler output, error count, error details
**Failure Triggers**:
- Compilation errors (any type mismatches, missing imports)
- Type checking failures

### Linting
**Method**: `npx eslint [file] --format json`
**Evidence**: Lint output, error/warning counts
**Failure Triggers**:
- ESLint errors (not warnings)
- Code style violations

### Test Execution
**Method**: `npm test -- [file] --run`
**Evidence**: Test output, pass/fail counts, coverage
**Failure Triggers**:
- Tests did not pass
- Test file does not exist
- Fewer tests than expected

### API Endpoint Verification
**Method**: HTTP request to endpoint, check status code and response shape
**Evidence**: Status code, response time, response body sample
**Failure Triggers**:
- HTTP 404, 500, or timeout
- Unexpected response format

---

## Evidence Requirements

### Every verification must produce EVIDENCE

| Criterion | Evidence Type | Example |
|-----------|---------------|---------|
| file_exists | File path, size, timestamp | `/src/lib/file.ts, 2,541 bytes, 2025-12-02 14:30:00` |
| no_placeholders | Scan results | `0 placeholders found` or `Found 2: Line 15, Line 42` |
| compiles | Compiler output | `0 TypeScript errors` |
| lint_passes | Linter output | `0 errors, 2 warnings` |
| tests_pass | Test results | `15 passed, 0 failed` |
| endpoint_responds | Status code + response | `Status 200, response time 45ms` |

---

## Prohibited Patterns

### ❌ SELF-ATTESTATION
```typescript
// WRONG - Agent grades its own homework
return { verified: true, message: "I completed it" };
```

### ❌ ASSUMED SUCCESS
```typescript
// WRONG - Doesn't actually check
if (claimedFile) {
  return { verified: true }; // No evidence!
}
```

### ❌ SKIPPED CHECKS
```typescript
// WRONG - "This check is slow, skip it for now"
if (criterion === 'tests_pass') {
  return { verified: true }; // NEVER skip checks
}
```

### ❌ LOOSE VERIFICATION
```typescript
// WRONG - "Looks about right"
if (output.includes('success')) {
  return { verified: true }; // No proof!
}
```

### ✅ GOOD VERIFICATION
```typescript
// RIGHT - Actual evidence collected
const result = await fs.stat(filePath);
if (result.size > 0) {
  return {
    verified: true,
    evidence: [{
      criterion: 'file_exists',
      proof: `File size: ${result.size} bytes`
    }]
  };
}
```

---

## Failure Handling

### When Verification Fails
Agent receives detailed failure report:
```json
{
  "verified": false,
  "failures": [
    {
      "criterion": "tests_pass:/tests/unit/feature.test.ts",
      "reason": "Test execution failed",
      "proof": "Expected 10 tests to pass, 3 failed"
    }
  ],
  "retry_count": 1,
  "max_retries": 3
}
```

### Agent Must Fix Issues
1. Read the failure details
2. Fix the underlying problem (not the verification)
3. Re-submit for verification
4. Repeat up to 3 times

### After 3 Failures
Task escalates to human review:
```json
{
  "status": "escalated_to_human",
  "reason": "Failed verification 3 times",
  "failures_history": [...]
}
```

---

## Examples

### Good Example: Complete File Verification

**Task**: Agent claims file was created and is ready for deployment

**Evidence Collected**:
```
✓ file_exists:/src/lib/agents/new-agent.ts
  Size: 3,847 bytes, Created: 2025-12-02 14:30:00

✓ no_placeholders:/src/lib/agents/new-agent.ts
  Scan found 0 TODO/TBD/FIXME markers

✓ typescript_compiles:/src/lib/agents/new-agent.ts
  tsc --noEmit completed successfully

✓ lint_passes:/src/lib/agents/new-agent.ts
  eslint: 0 errors, 0 warnings

✓ tests_pass:/tests/new-agent.test.ts
  npm test: 12 passed, 0 failed
```

**Result**: `verified: true` ✓ All evidence confirms completion

---

### Bad Example: Incomplete File Verification

**Task**: Agent claims feature is complete

**Evidence Collected**:
```
✗ file_exists:/src/lib/features/new-feature.ts
  File not found: ENOENT: no such file or directory

✗ tests_pass:/tests/features/new-feature.test.ts
  Test file not found: ENOENT: no such file or directory

✗ typescript_compiles:/src/lib/features/incomplete.ts
  Compilation failed: Missing return type (line 42)
```

**Result**: `verified: false` ✗ Multiple criteria failed, agent must fix

---

## Implementation in Your Code

### Import and Use Independent Verifier
```typescript
import { independentVerifier } from '@/lib/agents/independent-verifier';

// DO NOT return success directly
// DO call Independent Verifier
const result = await independentVerifier.verify({
  task_id: 'my-task-123',
  claimed_outputs: ['/path/to/file.ts'],
  completion_criteria: [
    'file_exists:/path/to/file.ts',
    'no_placeholders:/path/to/file.ts',
    'typescript_compiles:/path/to/file.ts'
  ],
  requesting_agent_id: this.agent_id
});

// Return the verification result (not your own assessment)
return result;
```

### In Orchestrator
```typescript
// Before marking task complete:
const verification = await independentVerifier.verify({
  task_id: task.id,
  claimed_outputs: task.outputs,
  completion_criteria: task.criteria,
  requesting_agent_id: task.agent_id
});

if (!verification.verified) {
  // Return task to agent for fixes
  task.status = 'verification_failed';
  task.failures = verification.failures;
  task.retry_count++;

  if (task.retry_count >= 3) {
    task.status = 'escalated_to_human';
  }
  return;
}

// Only mark complete with verification proof
task.status = 'complete';
task.verification = verification;
```

---

## Health Endpoints for Verification

**Endpoint**: `GET /api/health`
**Status**: ✓ Working
**Use**: Basic system health check

**Endpoint**: `GET /api/health/deep`
**Status**: ✓ Working
**Use**: Comprehensive dependency checks

**Endpoint**: `GET /api/health/routes`
**Status**: ✓ Working
**Use**: Verify all API routes are accessible

All health endpoints return verifiable evidence of system state.

---

## Success Metrics

After implementing Verification Protocol:

| Metric | Before | After |
|--------|--------|-------|
| Tasks verified without evidence | 100% | 0% |
| False completions accepted | Unknown | 0% |
| Completion claims with evidence | 0% | 100% |
| Automatic escalation to human | N/A | Happens after 3 failures |
| Audit trail completeness | Partial | Full with evidence |

---

## Key Rules

```
1. NEVER verify your own work
2. ALWAYS use Independent Verifier
3. ALWAYS provide EVIDENCE
4. NEVER assume success
5. BLOCK completion without proof
6. ESCALATE after 3 failures
```

---

**Status**: Production Ready (v1.0.0)
**Last Updated**: 2025-12-02
**Critical**: Yes - Blocks all task completions without proof

