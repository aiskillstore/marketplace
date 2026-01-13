# Complete Lifecycle Example

This document shows a full issue lifecycle demonstrating:
- The **DEV → TEST → REVIEW** circular phase order
- **Thread transitions** (one thread at a time)
- **Demotion** (REVIEW → DEV, never TEST)
- **Test development** in DEV, test running in TEST
- **Coverage estimation** in REVIEW
- Multiple sessions with compaction recovery

---

## Core Philosophy

**Order matters. Time does not.**

Timestamps show ORDER of events, not deadlines. The same sequence could happen over days, weeks, or months - what matters is the order is preserved and each step completes before the next begins.

---

## The Circular Phase Order

```
        ┌──────────────────────────────────────────────┐
        │                                              │
        ▼                                              │
    DEV THREAD ───► TEST THREAD ───► REVIEW THREAD ───┘
        │               │                 │
        │               │                 ▼
        │               │         PASS? → merge to main
        │               │                 │
        │               │         FAIL? ──┘ (back to DEV)
        │               │
        │          Bug fixes ONLY
        │          (NO structural changes)
        │          (NO new tests)
        │
    Write code AND tests
    Structural changes
    Rewrites
```

**Key Rules:**
- **ONE thread open at a time** per feature
- Opening TEST = closing DEV
- Opening REVIEW = closing TEST
- REVIEW pass = merge to main
- REVIEW fail = demote to DEV (NEVER to TEST)

---

## The Setup

**Epic #200**: User Authentication System

**Issue #201**: JWT Token Authentication

**Agents involved**:
- Agent-A (Task Agent - DEV work)
- Agent-B (Another Task Agent - scope coordination)
- Agent-C (Fresh instance after compaction)
- Agent-T (Test Agent - TEST work)
- Agent-R (Review Agent - REVIEW work)

---

## PHASE 1: DEV THREAD

### Day 1, 09:00 - DEV Thread Created

```markdown
## Thread: JWT Token Authentication - DEV

### Required Skills
Agents participating in this thread should activate:
- `github-elements-tracking` - thread protocols

### Thread Type
dev

### Scope
Implement JWT token authentication with Redis blacklist.

---

# JWT Token Authentication

## Epic Link
Part of Epic #200 - User Authentication System

## Requirements
- Implement JWT token generation using RS256
- Access tokens expire in 1 hour
- Refresh tokens expire in 7 days
- Implement token validation middleware
- Add Redis-based token blacklist
- **Write comprehensive tests** (tests are developed here in DEV)

## Acceptance Criteria
- [ ] Tokens are generated with proper claims
- [ ] Tokens are validated correctly
- [ ] Refresh flow works
- [ ] Blacklisted tokens are rejected
- [ ] **Test coverage > 80%** (tests written in this DEV thread)

---
*Status: Ready for claiming*
```

Labels: `wave:1, epic:200, ready, phase:dev`

### 09:15 - Agent-A Claims DEV Thread

```bash
$ gh issue list --label "phase:dev,ready" --no-assignee
201  JWT Token Authentication - DEV  wave:1, epic:200, ready, phase:dev

$ gh issue edit 201 --add-assignee alice --add-label "in-progress" --remove-label "ready"
```

Agent-A posts:

```markdown
## [Session 1] 2024-01-15 09:15 UTC - @alice (Agent-A)

### Claimed
Starting DEV work on this issue.

### Scope Declaration
Files I will modify:
- src/auth/jwt.service.ts (new)
- src/auth/jwt.middleware.ts (new)
- src/auth/token.types.ts (new)
- src/auth/blacklist.service.ts (new)
- tests/auth/jwt.test.ts (new) **← Tests developed here in DEV**
- tests/auth/jwt.integration.test.ts (new)

Files I will NOT modify:
- src/auth/oauth.ts (belongs to #202)

### Plan
1. Create token types and interfaces
2. Implement token generation
3. Implement token validation middleware
4. Add Redis blacklist integration
5. **Write unit tests** (DEV responsibility)
6. **Write integration tests** (DEV responsibility)

Starting with token types.
```

### 12:30 - Session 1 End Checkpoint

```markdown
## [Session 1 - END] 2024-01-15 12:30 UTC - @alice (Agent-A)

### Session Summary
- Reason: Lunch break

### Work Log
- [09:20] Created token types and interfaces
- [10:00] Implemented token generation
- [10:30] Implemented token validation
- [11:00] Started Redis blacklist integration
- [12:00] Resolved needs-input for Redis config (see Epic #200)

### State Snapshot

#### Completed
- [x] Create token types and interfaces
- [x] Implement token generation
- [x] Implement token validation
- [x] Redis connection setup

#### In Progress
- [ ] Complete blacklist service

#### Pending
- [ ] **Write unit tests** (DEV work - tests are code)
- [ ] **Write integration tests** (DEV work)

#### Files Changed
| File | Changes |
|------|---------|
| src/auth/token.types.ts | +55 lines |
| src/auth/jwt.service.ts | +142 lines |
| src/auth/jwt.middleware.ts | +38 lines |
| src/auth/blacklist.service.ts | +65 lines (partial) |

#### Commits
| Hash | Message |
|------|---------|
| a1b2c3d | Add token types and interfaces |
| e4f5g6h | Implement JWT token generation |
| m1n2o3p | Add token validation middleware |
| q1r2s3t | Add Redis blacklist (partial) |

#### Branch
`feature/201-jwt-auth`

#### Next Action
Complete blacklist service, then write tests

### Future-Me Test
- All decisions documented: YES
- All commits listed: YES
- All files listed: YES
- Next action clear: YES
```

### Day 1, 14:00 - Session 2 (Implementation + Tests)

```markdown
## [Session 2] 2024-01-15 14:00 UTC - @alice (Agent-A)

### State Inherited
From Session 1 checkpoint (12:30 UTC)

### Resuming
Continuing from previous session.
Next action: Complete blacklist service, then write tests.
```

### 17:45 - DEV Complete, Ready for TEST

```markdown
## [Session 2 - END] 2024-01-15 17:45 UTC - @alice (Agent-A)

### Session Summary
- Reason: DEV work complete, ready to advance to TEST phase

### Work Log
- [14:00] Completed blacklist service
- [14:30] Started writing unit tests
- [15:30] Completed unit tests for all functions
- [16:30] Started integration tests
- [17:30] Completed integration tests
- [17:40] All tests passing locally

### State Snapshot

#### Completed
- [x] All implementation
- [x] **All unit tests written** (DEV responsibility)
- [x] **All integration tests written** (DEV responsibility)
- [x] All tests pass locally

#### In Progress
None - DEV work complete

#### Pending
None for DEV phase

#### Files Changed (all)
| File | Lines |
|------|-------|
| src/auth/token.types.ts | 55 |
| src/auth/jwt.service.ts | 142 |
| src/auth/jwt.middleware.ts | 50 |
| src/auth/blacklist.service.ts | 95 |
| **tests/auth/jwt.test.ts** | **200** |
| **tests/auth/jwt.integration.test.ts** | **150** |
| .env.example | 1 |

#### Commits (all)
| Hash | Message |
|------|---------|
| a1b2c3d | Add token types and interfaces |
| e4f5g6h | Implement JWT token generation |
| m1n2o3p | Add token validation middleware |
| q1r2s3t | Add Redis blacklist (partial) |
| u1v2w3x | Complete Redis blacklist service |
| **c3d4e5f** | **Add unit tests for JWT auth** |
| **g5h6i7j** | **Add integration tests** |

#### Branch
`feature/201-jwt-auth`

### DEV PHASE COMPLETE

**Ready to advance to TEST phase.**

### Thread Transition
Closing this DEV thread. TEST thread will be opened.

---
*Closing DEV thread - advancing to TEST phase*
```

```bash
# Close DEV thread, ready for TEST
$ gh issue close 201
$ gh issue comment 201 --body "DEV thread closed. Advancing to TEST phase. See TEST thread #201-test."
```

---

## PHASE 2: TEST THREAD

### Day 1, 18:00 - TEST Thread Opened

```bash
# Create TEST thread (same issue number convention, or new linked issue)
$ gh issue create --title "JWT Token Authentication - TEST" \
  --label "phase:test,epic:200,in-progress" \
  --body "$(cat <<'EOF'
## Thread: JWT Token Authentication - TEST

### Required Skills
Agents participating in this thread should activate:
- `github-elements-tracking` - thread protocols

### Thread Type
test

### Scope
**RUN tests** and **fix bugs ONLY**. No structural changes. No new tests.

---

# TEST Phase for #201

## Source
DEV thread #201 (closed)
Branch: `feature/201-jwt-auth`

## What TEST Can Do
- [x] Run existing tests
- [x] Fix bugs that cause test failures
- [x] Report bugs found

## What TEST CANNOT Do
- [ ] Write new tests (that's DEV work)
- [ ] Structural changes (that's DEV work)
- [ ] Rewrites (that's DEV work)

## Test Suite
- Unit tests: tests/auth/jwt.test.ts
- Integration tests: tests/auth/jwt.integration.test.ts

---
*Status: Ready for test execution*
EOF
)"
```

### 18:15 - Agent-T Claims TEST Thread

```markdown
## [TEST Session 1] 2024-01-15 18:15 UTC - @tester (Agent-T)

### Claimed
Starting TEST work.

### Understanding
- DEV thread #201 is CLOSED
- I am now in TEST thread #201-test
- My job: RUN tests, FIX bugs only
- I CANNOT: Write new tests, make structural changes

### Plan
1. Pull latest from feature branch
2. Run unit tests
3. Run integration tests
4. Fix any failing tests (bug fixes only)
5. Report results

Starting test execution.
```

### 18:30 - Tests Run, Bug Found

```markdown
## [TEST Session 1] 2024-01-15 18:30 UTC - @tester (Agent-T)

### Test Results

#### Unit Tests
```
PASS  tests/auth/jwt.test.ts
  Token Generation
    ✓ generates valid access token
    ✓ generates valid refresh token
    ✓ includes correct claims
  Token Validation
    ✓ validates valid token
    ✓ rejects expired token
    ✗ rejects blacklisted token  ← FAIL
  Blacklist
    ✓ adds token to blacklist
    ✓ checks blacklist correctly

Tests: 7 passed, 1 failed
```

### Bug Found

**Test failing**: "rejects blacklisted token"

**Error**: `Redis connection timeout`

**Investigation**:
- Looked at blacklist.service.ts line 42
- Connection not awaited before blacklist check

**This is a BUG FIX, not structural change** - can fix in TEST.

### Fixing
```typescript
// Before (bug)
checkBlacklist(token) {
  this.redis.get(token);  // Missing await
  return false;
}

// After (fix)
async checkBlacklist(token) {
  const result = await this.redis.get(token);
  return result !== null;
}
```

Commit: `x7y8z9a - Fix Redis await in blacklist check`

### Re-Running Tests

```
PASS  tests/auth/jwt.test.ts
  All 8 tests passed
```

All tests now pass.
```

### 19:00 - TEST Phase Complete

```markdown
## [TEST Session 1 - END] 2024-01-15 19:00 UTC - @tester (Agent-T)

### Session Summary
- Reason: TEST work complete

### Work Log
- [18:15] Pulled feature branch
- [18:20] Ran unit tests - 1 failure
- [18:30] Identified bug (missing await)
- [18:35] Fixed bug (bug fix only, not structural)
- [18:40] Re-ran tests - all pass
- [18:50] Ran integration tests - all pass

### Test Results Summary

| Test Suite | Result | Details |
|------------|--------|---------|
| Unit tests | PASS (8/8) | After bug fix |
| Integration tests | PASS (5/5) | No issues |

### Bugs Fixed (TEST can fix bugs)
| Bug | Fix | Commit |
|-----|-----|--------|
| Missing await in blacklist | Added await | x7y8z9a |

### Structural Issues Found (TEST cannot fix these)
None

### State Snapshot

#### Completed
- [x] Run all unit tests
- [x] Fix bugs causing failures
- [x] Run all integration tests

#### TEST Phase Complete
All tests pass. No structural issues found.

### Thread Transition
Closing TEST thread. REVIEW thread will be opened.

---
*Closing TEST thread - advancing to REVIEW phase*
```

```bash
$ gh issue close 201-test
$ gh issue comment 201-test --body "TEST thread closed. All tests pass. Advancing to REVIEW phase."
```

---

## PHASE 3: REVIEW THREAD (First Attempt)

### Day 2, 10:00 - REVIEW Thread Opened

```bash
$ gh issue create --title "JWT Token Authentication - REVIEW" \
  --label "phase:review,epic:200,in-progress" \
  --body "$(cat <<'EOF'
## Thread: JWT Token Authentication - REVIEW

### Required Skills
Agents participating in this thread should activate:
- `github-elements-tracking` - thread protocols

### Thread Type
review

### Scope
Evaluate code quality, security, and **estimate test coverage**.

---

# REVIEW Phase for #201

## Source
- DEV thread #201 (closed)
- TEST thread #201-test (closed)
- Branch: `feature/201-jwt-auth`

## What REVIEW Does
- [x] Code quality review
- [x] Security audit
- [x] **Estimate test coverage** (critical responsibility)
- [x] Render verdict: PASS or FAIL

## What REVIEW Can Decide
- PASS → merge to main
- FAIL → demote to DEV (NEVER to TEST)

---
*Status: Ready for review*
EOF
)"
```

### 10:15 - Agent-R Claims REVIEW Thread

```markdown
## [REVIEW Session 1] 2024-01-16 10:15 UTC - @reviewer (Agent-R)

### Claimed
Starting REVIEW work.

### Phase Verification
- DEV thread #201: CLOSED ✓
- TEST thread #201-test: CLOSED ✓
- Only REVIEW thread open: ✓

### Review Scope
1. Code quality
2. Security (auth code is security-critical)
3. **Test coverage estimation**

Beginning review.
```

### 11:30 - REVIEW Complete - FAIL (Missing Coverage)

```markdown
## [REVIEW Session 1] 2024-01-16 11:30 UTC - @reviewer (Agent-R)

### Review Complete

#### Code Quality - PASS
- [x] Follows project patterns
- [x] Proper error handling
- [x] No code smells

#### Security - PASS
- [x] Tokens properly signed with RS256
- [x] No secrets in code
- [x] Blacklist properly checked
- [x] Expiry enforced

#### TEST COVERAGE ESTIMATION - FAIL

##### Functional Coverage
- [x] Happy path tested
- [x] Error conditions tested
- [ ] **Edge cases NOT tested** ← Missing
- [ ] **Boundary values NOT tested** ← Missing

##### Code Coverage
- Statement coverage: 78%
- Branch coverage: 65%
- **Below 80% threshold**

##### Missing Tests Identified
| Missing Test | Severity | Why Needed |
|--------------|----------|------------|
| Token with invalid signature | High | Security-critical |
| Token with tampered claims | High | Security-critical |
| Blacklist Redis failure | Medium | Error handling |
| Concurrent token validation | Medium | Race conditions |

### VERDICT: FAIL

**Reason**: Insufficient test coverage for security-critical code.

### Required Before Re-Review
1. Add edge case tests for invalid signatures
2. Add boundary tests for token expiry
3. Add error handling tests for Redis failures
4. Bring coverage to 80%+

### DEMOTION: REVIEW → DEV

**Why DEV and not TEST?**
- TEST cannot write new tests (tests are code = DEV work)
- These missing tests require development work
- TEST can only RUN existing tests and fix bugs

### Thread Transition
Closing REVIEW thread. Reopening DEV thread.

---
*VERDICT: FAIL - Demoting to DEV for additional tests*
```

```bash
# Demote back to DEV phase (only Themis can do this)
$ gh issue edit 201-review --remove-label "phase:review" --add-label "phase:dev"

# Close REVIEW thread
$ gh issue close 201-review

# Reopen DEV thread with findings
$ gh issue reopen 201
$ gh issue comment 201 --body "$(cat <<'EOF'
## DEV Thread Reopened - Demoted from REVIEW

### Source
Demoted from REVIEW thread #201-review (review rejected)

### Why DEV (not TEST)?
Missing tests require DEVELOPMENT work. TEST cannot write tests.

### Required Work
1. Add edge case tests for invalid signatures
2. Add boundary tests for token expiry
3. Add error handling tests for Redis failures
4. Achieve 80%+ coverage

### After DEV Complete
Close DEV → Open TEST → Open REVIEW (cycle continues)

---
*DEV work needed for test coverage*
EOF
)"

$ gh issue edit 201 --add-label "in-progress" --remove-label "review-needed"
```

---

## PHASE 4: DEV THREAD (Second Iteration)

### Day 2, 14:00 - DEV Thread Resumed

```markdown
## [DEV Session 3] 2024-01-16 14:00 UTC - @alice (Agent-A)

### Context
DEV thread reopened after REVIEW demotion.

### Findings from REVIEW
Missing test coverage:
1. Edge case tests for invalid signatures
2. Boundary tests for token expiry
3. Error handling tests for Redis failures
4. Need 80%+ coverage

### Plan
1. Add missing edge case tests
2. Add boundary tests
3. Add error handling tests
4. Verify coverage meets threshold

Starting test additions.
```

### 16:00 - Additional Tests Complete

```markdown
## [DEV Session 3 - END] 2024-01-16 16:00 UTC - @alice (Agent-A)

### Session Summary
- Reason: Additional DEV work complete

### Work Log
- [14:00] Read REVIEW findings
- [14:30] Added invalid signature tests
- [15:00] Added tampered claims tests
- [15:20] Added Redis failure tests
- [15:40] Added concurrent validation tests
- [15:50] Verified coverage: 91%

### Tests Added
| Test | Coverage Impact |
|------|-----------------|
| Invalid signature handling | +5% |
| Tampered claims detection | +4% |
| Redis failure graceful handling | +3% |
| Concurrent token validation | +1% |

### State Snapshot

#### Completed
- [x] Edge case tests for invalid signatures
- [x] Boundary tests for token expiry
- [x] Error handling tests for Redis failures
- [x] Coverage: 91% (above 80% threshold)

#### Files Changed
| File | Changes |
|------|---------|
| tests/auth/jwt.test.ts | +85 lines (edge cases) |
| tests/auth/jwt.integration.test.ts | +45 lines (error handling) |

#### Commits
| Hash | Message |
|------|---------|
| b2c3d4e | Add edge case tests for token validation |
| f5g6h7i | Add error handling tests |

### DEV PHASE COMPLETE (Second Iteration)

**Ready to advance to TEST phase.**

---
*Closing DEV thread - advancing to TEST phase*
```

```bash
$ gh issue close 201
```

---

## PHASE 5: TEST THREAD (Second Iteration)

### Day 2, 16:30 - TEST Thread Reopened

```markdown
## [TEST Session 2] 2024-01-16 16:30 UTC - @tester (Agent-T)

### Context
TEST thread for second iteration after additional tests written in DEV.

### Test Execution
```
PASS  tests/auth/jwt.test.ts (15 tests)
PASS  tests/auth/jwt.integration.test.ts (8 tests)

All 23 tests passed.
Coverage: 91%
```

### Results
- All tests pass
- No bugs found
- Coverage meets threshold

### TEST PHASE COMPLETE

---
*Closing TEST thread - advancing to REVIEW phase*
```

```bash
$ gh issue close 201-test-2
```

---

## PHASE 6: REVIEW THREAD (Second Attempt)

### Day 2, 17:00 - REVIEW Thread Reopened

```markdown
## [REVIEW Session 2] 2024-01-16 17:00 UTC - @reviewer (Agent-R)

### Context
Re-review after DEV addressed coverage gaps.

### Phase Verification
- DEV thread: CLOSED ✓
- TEST thread: CLOSED ✓
- REVIEW thread: OPEN ✓

### Re-Verification

#### Previous Failures - Now Fixed
| Check | Previous | Now | Notes |
|-------|----------|-----|-------|
| Edge case tests | FAIL | PASS | Invalid signature tested |
| Boundary tests | FAIL | PASS | Expiry edge cases tested |
| Error handling tests | FAIL | PASS | Redis failure tested |
| Coverage | 78% | 91% | Above threshold |

#### Coverage Estimation
- [x] Happy path tested
- [x] Error conditions tested
- [x] Edge cases tested ✓ (fixed)
- [x] Boundary values tested ✓ (fixed)

Coverage: 91% - SUFFICIENT

### VERDICT: PASS

All previous issues resolved. No new issues found.

### Approved for Merge

---
*VERDICT: PASS - Approved for merge to main*
```

```bash
# Add completed label and close (Themis does this)
$ gh issue edit 201-review-2 --add-label "completed" --remove-label "phase:review"
$ gh issue close 201-review-2 --reason completed
```

---

## PHASE 7: MERGE TO MAIN

### Day 2, 17:30 - PR Merged

```markdown
## PR #251 Merged - 2024-01-16 17:30 UTC

### Merge Details
- Merged by: @coordinator
- Source: `feature/201-jwt-auth`
- Target: `main`
- Commits: 12
- Coverage: 91%

### Post-Merge
- Feature branch deleted
- CI passed on main

---
*Feature complete*
```

---

## Full Thread Flow Summary

```
Issue #201: JWT Token Authentication
│
├─────────────────── DEV THREAD (First) ───────────────────
│ │
│ ├── [Opened] Requirements + scope
│ ├── [Session 1] Implementation started
│ ├── [Session 2] Implementation + tests written
│ └── [CLOSED] Ready for TEST
│
├─────────────────── TEST THREAD (First) ──────────────────
│ │
│ ├── [Opened] Run tests only
│ ├── [Session 1] Found bug, fixed bug
│ └── [CLOSED] All tests pass, ready for REVIEW
│
├─────────────────── REVIEW THREAD (First) ────────────────
│ │
│ ├── [Opened] Evaluate + estimate coverage
│ ├── [Session 1] Coverage insufficient
│ └── [CLOSED - FAIL] Demote to DEV (not TEST!)
│
├─────────────────── DEV THREAD (Second) ──────────────────
│ │
│ ├── [Reopened] Address review findings
│ ├── [Session 3] Write missing tests
│ └── [CLOSED] Coverage now 91%
│
├─────────────────── TEST THREAD (Second) ─────────────────
│ │
│ ├── [Opened] Run all tests
│ ├── [Session 2] All pass
│ └── [CLOSED] Ready for REVIEW
│
├─────────────────── REVIEW THREAD (Second) ───────────────
│ │
│ ├── [Opened] Re-evaluate
│ ├── [Session 2] Coverage sufficient
│ └── [CLOSED - PASS] Approved for merge
│
└── MERGED TO MAIN
```

---

## Key Takeaways

### 1. Circular Phase Order Works
DEV → TEST → REVIEW → (FAIL) → DEV → TEST → REVIEW → (PASS) → main

The cycle repeated until REVIEW passed.

### 2. One Thread At A Time
At any moment, only ONE thread was open:
- When DEV was open, TEST and REVIEW were closed
- When TEST was open, DEV and REVIEW were closed
- When REVIEW was open, DEV and TEST were closed

### 3. Demotion Always Goes to DEV
When REVIEW failed, it demoted to DEV, not TEST.
**Why?** Because missing tests require DEVELOPMENT work. TEST cannot write tests.

### 4. Test Development Happens in DEV
- DEV thread: Wrote all tests (tests are code)
- TEST thread: Only RAN tests and fixed bugs
- REVIEW thread: Estimated coverage, rendered verdict

### 5. TEST Has Limited Scope
TEST can only:
- Run existing tests
- Fix bugs (minimal changes to make tests pass)

TEST cannot:
- Write new tests
- Make structural changes
- Do rewrites

### 6. Coverage Estimation is REVIEW's Job
REVIEW must estimate test coverage. If insufficient → demote to DEV.

---

## Labels Throughout Lifecycle

| Phase | Labels |
|-------|--------|
| DEV ready | `phase:dev, ready, wave:1, epic:200` |
| DEV in progress | `phase:dev, in-progress` |
| TEST in progress | `phase:test, in-progress` |
| REVIEW in progress | `phase:review, in-progress` |
| REVIEW passed | `completed` (closed) |
| REVIEW failed | `phase:dev` (back to DEV) |
| Complete | `completed` (closed) |

---

## What If Demotion Went to TEST? (Anti-Pattern)

**WRONG**:
```
REVIEW finds missing tests → Demote to TEST
```

**Why this fails**:
1. TEST cannot write new tests
2. TEST would be stuck - can't fix the issue
3. Violates phase order

**CORRECT**:
```
REVIEW finds missing tests → Demote to DEV
DEV writes tests → Close DEV
TEST runs tests → Close TEST
REVIEW re-evaluates → Pass or fail again
```

---

## Recovery from Any Point

Because each thread captures complete state, any agent can recover:

1. **Read the thread** (all comments in order)
2. **Find last checkpoint** with State Snapshot
3. **Understand phase**: Which thread is open? DEV, TEST, or REVIEW?
4. **Continue from Next Action**

The thread IS the memory. Order is preserved. Time is irrelevant.
