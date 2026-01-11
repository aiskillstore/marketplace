# Compaction Recovery: Complete Walkthrough

This document walks through an actual compaction and recovery scenario step-by-step. Follow along to understand exactly how the protocol works.

---

## Core Philosophy

**Order matters. Time does not.**

- Timestamps in this example show ORDER of events, not urgency
- Recovery works whether it happens minutes or years after compaction
- The issue thread preserves sequence - that's what matters
- Follow recovery steps in strict order

---

## Thread Types in Recovery

When recovering, you MUST identify which thread type you're resuming:

| Thread Type | Recovery Focus |
|-------------|----------------|
| **DEV Thread** | Code, tests, structural changes allowed |
| **TEST Thread** | Run tests, bug fixes ONLY - no new tests, no structural changes |
| **REVIEW Thread** | Evaluation, verdicts, coverage estimation - no implementation |

**Check the thread label**: `phase:dev`, `phase:test`, or `phase:review`

**Verify one thread at a time**: Only ONE thread (DEV, TEST, or REVIEW) should be open per feature.

---

## The Scenario

**Epic #200**: Implement User Authentication System

**Issue #201**: JWT Token Authentication - DEV Thread (part of Epic #200)

**Thread Type**: `phase:dev` (development work)

**The situation:**
- Agent-1 working on DEV thread for Issue #201
- Made significant progress (code + tests written)
- Session ended due to context exhaustion (compaction)
- Agent-2 (new instance) must continue the DEV work

---

## Before Compaction: What Agent-1 Did

### Session 1 (Agent-1)

**09:00 UTC** - Agent-1 started working on Issue #201

The issue thread at this point:

```markdown
# JWT Token Authentication

## Requirements
- Implement JWT token generation
- RS256 algorithm for security
- 1-hour expiry, 7-day refresh tokens
- Redis for token blacklist

## Acceptance Criteria
- [ ] Token generation works
- [ ] Token validation works
- [ ] Refresh token flow works
- [ ] Blacklist invalidation works

## Linked Epic
Part of Epic #200 (User Authentication System)

---

## [Session 1] 2024-01-15 09:00 UTC - @agent-1

### Claimed
Starting work on this issue.

### Scope Declaration
Files I will modify:
- src/auth/jwt.service.ts
- src/auth/jwt.middleware.ts
- src/auth/token.types.ts
- tests/auth/jwt.test.ts

Files I will NOT modify:
- src/auth/oauth.ts (belongs to #202)
- src/config/auth.config.ts (shared config, need coordination)

### Plan
1. Set up token types and interfaces
2. Implement token generation
3. Implement token validation middleware
4. Add Redis blacklist integration
5. Write tests
```

**10:00 UTC** - Agent-1 posted first checkpoint:

```markdown
## [Session 1] 2024-01-15 10:00 UTC - @agent-1

### Work Log
- [09:15] Analyzed requirements, understood RS256 requirement
- [09:30] Created token.types.ts with TokenPayload, TokenPair interfaces
- [09:45] Implemented generateTokenPair() function
- [09:55] Decision: Using jsonwebtoken library (standard, well-maintained)

### State Snapshot

#### Completed
- [x] Set up token types and interfaces
- [x] Implement token generation (generateTokenPair)

#### In Progress
- [ ] Implement token validation middleware

#### Pending
- [ ] Add Redis blacklist integration
- [ ] Write tests

#### Blockers
None

#### Files Changed
| File | Changes |
|------|---------|
| src/auth/token.types.ts | +45 lines (new file) |
| src/auth/jwt.service.ts | +82 lines (token generation) |

#### Commits
| Hash | Message |
|------|---------|
| a1b2c3d | Add token types and interfaces |
| e4f5g6h | Implement JWT token generation |

#### Branch
`feature/201-jwt-auth`

#### Next Action
Continue with validation middleware

### Continuing
Starting on validateToken() function now.
```

**11:00 UTC** - Agent-1 hit a blocker:

```markdown
## [Session 1] 2024-01-15 11:00 UTC - @agent-1

### Work Log
- [10:05] Started validation middleware
- [10:30] Implemented validateToken() function
- [10:45] Started Redis integration
- [10:55] BLOCKER: Redis connection string not defined in config

### State Snapshot

#### Completed
- [x] Set up token types and interfaces
- [x] Implement token generation (generateTokenPair)
- [x] Implement token validation (validateToken)

#### In Progress
- [ ] Add Redis blacklist integration

#### Pending
- [ ] Write tests

#### Blockers
- Redis connection string unknown. Not in .env.example or docs.
- Need config decision from Epic #200 coordinator

#### Files Changed
| File | Changes |
|------|---------|
| src/auth/token.types.ts | +45 lines (new file) |
| src/auth/jwt.service.ts | +142 lines (generation + validation) |
| src/auth/jwt.middleware.ts | +38 lines (Express middleware) |

#### Commits
| Hash | Message |
|------|---------|
| a1b2c3d | Add token types and interfaces |
| e4f5g6h | Implement JWT token generation |
| i7j8k9l | Add token validation and middleware |

#### Branch
`feature/201-jwt-auth`

#### Next Action
Wait for Redis config from Epic #200, then continue with blacklist

### BLOCKED
Escalating to Epic #200 for Redis configuration.
```

Agent-1 also posted to Epic #200:

```markdown
## Blocker Alert from #201

Issue #201 (JWT Authentication) is blocked.

**Need**: Redis connection string configuration

**Options**:
1. Add REDIS_URL to environment
2. Use in-memory mock for dev, Redis for prod
3. Skip blacklist for MVP

**Impact**: Cannot complete blacklist feature without this decision.
```

**11:15 UTC** - Epic coordinator responded on Epic #200:

```markdown
## Decision: Redis Configuration

**Decision**: Option 1 - Add REDIS_URL to environment

**Configuration**:
- Production: redis://auth-cache.internal:6379
- Development: redis://localhost:6379
- Variable name: REDIS_URL

**Action**: All auth issues should use REDIS_URL environment variable.

Propagating to #201, #202, #203.
```

**11:20 UTC** - Agent-1 saw the resolution, posted on #201:

```markdown
## Blocker Resolved - 11:20 UTC

### Resolution
Using REDIS_URL environment variable.
- Production: redis://auth-cache.internal:6379
- Development: redis://localhost:6379

### Source
Epic #200 comment by @coordinator

### Continuing
Will now implement Redis blacklist with REDIS_URL
```

**11:45 UTC** - CONTEXT EXHAUSTION - Agent-1's session ended unexpectedly

Agent-1 managed a quick final checkpoint:

```markdown
## [Session 1 - END] 2024-01-15 11:45 UTC - @agent-1

### Session Summary
- Duration: 09:00 to 11:45 (2h 45m)
- Reason for ending: Context limit reached

### Work Log
- [11:25] Blocker resolved, Redis URL configured
- [11:30] Started blacklist service implementation
- [11:40] Implemented isTokenBlacklisted() function
- [11:44] Context warning, saving state NOW

### State Snapshot

#### Completed
- [x] Set up token types and interfaces
- [x] Implement token generation (generateTokenPair)
- [x] Implement token validation (validateToken)
- [x] Redis connection setup

#### In Progress
- [ ] Add Redis blacklist integration (isTokenBlacklisted done, addToBlacklist pending)

#### Pending
- [ ] Write tests

#### Blockers
None - Redis config resolved

#### Files Changed
| File | Changes |
|------|---------|
| src/auth/token.types.ts | +45 lines |
| src/auth/jwt.service.ts | +142 lines |
| src/auth/jwt.middleware.ts | +38 lines |
| src/auth/blacklist.service.ts | +52 lines (partial) |
| .env.example | +1 line (REDIS_URL) |

#### Commits
| Hash | Message |
|------|---------|
| a1b2c3d | Add token types and interfaces |
| e4f5g6h | Implement JWT token generation |
| i7j8k9l | Add token validation and middleware |
| m1n2o3p | Add Redis connection and partial blacklist |

#### Branch
`feature/201-jwt-auth`

#### Next Action
1. Complete addToBlacklist() function in blacklist.service.ts
2. Integrate blacklist check into validateToken()
3. Write tests

### Future-Me Test
- All decisions documented: YES (RS256, jsonwebtoken lib, REDIS_URL)
- All commits listed: YES (4 commits)
- All files listed: YES (5 files)
- Next action clear: YES (addToBlacklist, then integrate, then tests)
- Blockers explained: YES (resolved - Redis config)
```

---

## After Compaction: What Agent-2 Must Do

**14:00 UTC** - Agent-2 (new instance, ZERO memory of Agent-1's work) starts a session.

### Step 1: Find Assigned Work

```bash
$ gh issue list --assignee @me --label "in-progress"

NUMBER  TITLE                    LABELS
201     JWT Token Authentication in-progress, wave:1, epic:200
```

**Result**: Issue #201 is assigned to me and in-progress.

### Step 2: Read the Issue

```bash
$ gh issue view 201 --comments
```

Agent-2 reads the ENTIRE thread (requirements + all comments).

**Critical extraction from last checkpoint:**

```
#### Completed
- [x] Set up token types and interfaces
- [x] Implement token generation (generateTokenPair)
- [x] Implement token validation (validateToken)
- [x] Redis connection setup

#### In Progress
- [ ] Add Redis blacklist integration (isTokenBlacklisted done, addToBlacklist pending)

#### Next Action
1. Complete addToBlacklist() function in blacklist.service.ts
2. Integrate blacklist check into validateToken()
3. Write tests

#### Branch
`feature/201-jwt-auth`

#### Commits
a1b2c3d, e4f5g6h, i7j8k9l, m1n2o3p
```

### Step 3: Verify Local State

```bash
# Switch to the branch
$ git checkout feature/201-jwt-auth
Switched to branch 'feature/201-jwt-auth'

# Verify commits exist
$ git log --oneline -5
m1n2o3p Add Redis connection and partial blacklist
i7j8k9l Add token validation and middleware
e4f5g6h Implement JWT token generation
a1b2c3d Add token types and interfaces
...

# Verify files exist
$ ls -la src/auth/
blacklist.service.ts
jwt.middleware.ts
jwt.service.ts
token.types.ts
```

**State verified.** Everything from checkpoint exists.

### Step 4: Build Local TodoWrite

From the checkpoint's State Snapshot, Agent-2 creates TodoWrite:

```
[x] Set up token types and interfaces
[x] Implement token generation (generateTokenPair)
[x] Implement token validation (validateToken)
[x] Redis connection setup
[ ] Add Redis blacklist integration → IN PROGRESS
    - [x] isTokenBlacklisted (done per checkpoint)
    - [ ] addToBlacklist (next)
[ ] Write tests
```

### Step 5: Post Recovery Comment

```bash
$ gh issue comment 201 --body "$(cat <<'EOF'
## [Session 2] 2024-01-15 14:00 UTC - @agent-2

### State Inherited
From Session 1 final checkpoint (11:45 UTC):

#### Completed
- [x] Token types and interfaces
- [x] Token generation (generateTokenPair)
- [x] Token validation (validateToken)
- [x] Redis connection setup

#### In Progress
- [ ] Blacklist integration (isTokenBlacklisted done, addToBlacklist pending)

### Recovery Actions
1. Read all comments - understood full context
2. Verified branch `feature/201-jwt-auth` exists with 4 commits
3. Verified all files present in src/auth/
4. Confirmed blocker (Redis config) was resolved in Session 1
5. Reviewed Epic #200 - no new decisions since 11:20

### Continuing
Next action from checkpoint:
1. Complete addToBlacklist() function
2. Integrate blacklist check into validateToken()
3. Write tests

Starting with addToBlacklist() now.
EOF
)"
```

### Step 6: Continue Work

Agent-2 now works on `addToBlacklist()` with FULL context:

- Knows what was decided (RS256, jsonwebtoken, REDIS_URL)
- Knows what was done (4 commits, 5 files)
- Knows what's next (addToBlacklist → integrate → tests)
- Knows the branch (`feature/201-jwt-auth`)

**Work proceeds normally, with checkpoints at meaningful state changes (every 3 files modified, decisions made, or milestones completed).**

---

## Recovery Protocol Summary

```
┌────────────────────────────────────────────────────────────────┐
│                    RECOVERY PROTOCOL                            │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Find Work                                                   │
│     gh issue list --assignee @me --label "in-progress"          │
│                           │                                     │
│                           ▼                                     │
│  2. Identify Thread Type                                        │
│     Check label: phase:dev, phase:test, or phase:review         │
│     Verify: Only ONE thread open for this feature               │
│                           │                                     │
│                           ▼                                     │
│  3. Read Issue Thread                                           │
│     gh issue view $ISSUE --comments                             │
│     Find LAST "### State Snapshot"                              │
│                           │                                     │
│                           ▼                                     │
│  4. Verify Local State                                          │
│     git checkout <branch from snapshot>                         │
│     git log --oneline (verify commits)                          │
│     ls <files from snapshot>                                    │
│                           │                                     │
│                           ▼                                     │
│  5. Build TodoWrite                                             │
│     Completed → [x] todos                                       │
│     In Progress → [ ] todos (mark in_progress)                  │
│     Pending → [ ] todos                                         │
│     Respect thread scope (TEST = no new tests/structural)       │
│                           │                                     │
│                           ▼                                     │
│  6. Post Recovery Comment                                       │
│     - Thread type being resumed                                 │
│     - State inherited                                           │
│     - Recovery actions taken                                    │
│     - What you're continuing with                               │
│                           │                                     │
│                           ▼                                     │
│  7. Continue Work (Respecting Thread Scope)                     │
│     DEV: code + tests + structural changes allowed              │
│     TEST: run tests + bug fixes ONLY                            │
│     REVIEW: evaluation + verdicts ONLY                          │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## What Recovery Looks Like in the Issue Thread

After Session 2 starts, the issue thread shows complete continuity:

```
Issue #201: JWT Token Authentication
├── [Original requirements]
│
├── [Session 1] 09:00 UTC - @agent-1
│   └── Claimed, scope declared, plan
│
├── [Session 1] 10:00 UTC - @agent-1
│   └── Checkpoint: token types + generation done
│
├── [Session 1] 11:00 UTC - @agent-1
│   └── Checkpoint: validation done, BLOCKED on Redis
│
├── [Session 1] 11:20 UTC - @agent-1
│   └── Blocker resolved (Redis URL from Epic #200)
│
├── [Session 1 - END] 11:45 UTC - @agent-1
│   └── Final checkpoint: context exhaustion
│       Full state snapshot with Next Action
│
├── [Session 2] 14:00 UTC - @agent-2    ← RECOVERY POINT
│   └── State inherited, recovery actions, continuing
│
├── [Session 2] 14:30 UTC - @agent-2
│   └── Checkpoint: addToBlacklist done
│
├── [Session 2] 15:00 UTC - @agent-2
│   └── Checkpoint: blacklist integrated into validation
│
└── ... continues ...
```

---

## Key Lessons

### 1. The Checkpoint is Everything

Without the final checkpoint from Agent-1, Agent-2 would have:
- No idea what was done
- No idea what files were changed
- No idea what the branch name is
- No idea what decisions were made
- No idea what the next step should be

**The checkpoint IS the memory.**

### 2. Include Everything in State Snapshot

The minimum viable snapshot includes:
- Completed tasks (so you don't redo them)
- In Progress tasks (so you know where to resume)
- Pending tasks (so you know what's left)
- Files changed (so you can verify state)
- Commits (so you can verify code exists)
- Branch (so you can check it out)
- Next Action (so you know what to do)

### 3. Verify Before Continuing

Agent-2's Step 3 (Verify Local State) is crucial:
- Checkout the branch
- Verify commits exist
- Verify files exist

This catches cases where:
- Push failed in previous session
- Branch name was wrong
- Work was on different machine

### 4. Document Recovery in Thread

Agent-2's recovery comment serves multiple purposes:
- Proves recovery was intentional (not random new work)
- Documents what was inherited
- Creates continuity in the thread
- Lets other agents/humans understand the handoff

---

## Anti-Patterns in Recovery

| Anti-Pattern | Problem | Correct Approach |
|--------------|---------|------------------|
| Start working without reading thread | Duplicate work, conflicts | ALWAYS read full thread first |
| Skip verification step | Work on wrong branch | ALWAYS verify git state |
| Don't post recovery comment | Thread shows gap | ALWAYS document recovery |
| Assume files are pushed | They might not be | ALWAYS verify commits exist |
| Trust memory | You have none | ONLY trust issue thread |
| **Ignore thread type label** | Scope violation | Check `phase:dev/test/review` first |
| **Write tests in TEST thread recovery** | Phase violation | TEST only RUNS tests, DEV writes them |
| **Do implementation in REVIEW recovery** | Phase violation | REVIEW only evaluates, no coding |
| **Two threads open during recovery** | Order violation | Close one before resuming other |

---

## TEST Thread Recovery Scenario

**Scenario**: Agent compacted mid-TEST phase. A new agent must recover and continue running tests.

**Issue #205**: JWT Authentication - TEST Thread

**The situation:**
- DEV thread (#201) completed and closed
- TEST thread (#205) opened with `phase:test` label
- Agent-3 ran some tests, found 2 bugs, fixed 1
- Session ended due to context exhaustion
- Agent-4 must recover the TEST work

### Agent-3's Final Checkpoint (Before Compaction)

```markdown
## [TEST Session 1 - END] 2024-01-16 15:30 UTC - @agent-3

### Session Summary
- Duration: 14:00 to 15:30 (1h 30m)
- Reason for ending: Context limit reached

### State Snapshot

#### Thread Type
test

#### Tests Run
| Suite | Passed | Failed | Pending |
|-------|--------|--------|---------|
| Unit | 45 | 2 | 0 |
| Integration | 18 | 0 | 2 |

#### Bugs Found
1. `test_token_expiry` - Off-by-one in expiry check (FIXED - commit xyz789)
2. `test_blacklist_check` - Missing await (NOT YET FIXED)

#### Bug #2 Analysis
- Location: src/auth/jwt.service.ts:142
- Issue: Missing await on isTokenBlacklisted() call
- Classification: Simple bug fix (allowed in TEST)

#### Files Changed
| File | Changes |
|------|---------|
| src/auth/jwt.service.ts | Line 87: fixed expiry comparison |

#### Commits
| Hash | Message |
|------|---------|
| xyz789 | Fix: off-by-one in token expiry check |

#### Branch
`testing/201-jwt-auth`

#### Next Action
1. Fix bug #2 (missing await on line 142)
2. Re-run all tests
3. Document final results

### Scope Reminder
- I CAN: run tests, fix simple bugs
- I CANNOT: write new tests, structural changes, verdicts
```

### Agent-4 Recovery (TEST Thread)

```bash
# Step 1: Find work
$ gh issue list --assignee @me --label "in-progress" --label "phase:test"

NUMBER  TITLE                         LABELS
205     JWT Authentication - TEST     in-progress, phase:test, wave:1

# Step 2: Verify thread type and phase order
$ gh issue list --label "epic:200" --label "phase:dev" --state open
# Must be empty (DEV should be closed)

$ gh issue list --label "epic:200" --label "phase:review" --state open
# Must be empty (REVIEW should not be open yet)
```

**Agent-4 Recovery Comment:**

```markdown
## [TEST Session 2] 2024-01-16 16:00 UTC - @agent-4

### State Inherited
From TEST Session 1 final checkpoint (15:30 UTC):

#### Thread Type
test (VERIFIED: only TEST thread open for this feature)

#### Tests Run
- Unit: 45 passed, 2 failed
- Integration: 18 passed, 2 pending

#### Bugs
- Bug #1 (expiry): FIXED in Session 1
- Bug #2 (await): NOT YET FIXED - my task

### Recovery Actions
1. Verified DEV thread #201 is CLOSED
2. Verified REVIEW thread not yet opened
3. Verified branch `testing/201-jwt-auth` exists
4. Located bug #2: src/auth/jwt.service.ts:142

### Understanding My Limits
I CAN:
- Run existing tests
- Fix bug #2 (simple await fix)

I CANNOT:
- Write new tests
- Structural changes
- Render verdicts (that's REVIEW)

### Continuing
Fixing bug #2 now, then re-running all tests.
```

**Key TEST Recovery Differences:**
- Verify DEV thread is CLOSED before continuing
- Check that no REVIEW thread is open
- Explicitly state scope limitations
- Do NOT write new tests, even if coverage seems low (demote to DEV)
- Do NOT render verdicts like "tests pass" as final judgment

---

## REVIEW Thread Recovery Scenario

**Scenario**: Agent compacted mid-REVIEW phase. A new agent must recover and continue evaluation.

**Issue #208**: JWT Authentication - REVIEW Thread

**The situation:**
- DEV thread (#201) completed and closed
- TEST thread (#205) completed and closed (all tests pass)
- REVIEW thread (#208) opened with `phase:review` label
- Agent-5 started review, found coverage concerns
- Session ended due to context exhaustion
- Agent-6 must recover the REVIEW work

### Agent-5's Final Checkpoint (Before Compaction)

```markdown
## [REVIEW Session 1 - END] 2024-01-17 11:30 UTC - @agent-5

### Session Summary
- Duration: 10:00 to 11:30 (1h 30m)
- Reason for ending: Context limit reached

### State Snapshot

#### Thread Type
review

#### Review Progress
| Area | Status | Notes |
|------|--------|-------|
| Code quality | DONE | Clean, follows patterns |
| Security review | DONE | No issues found |
| Test coverage | IN PROGRESS | Concerns identified |
| Final verdict | PENDING | Blocked on coverage |

#### Coverage Estimation
- Functional coverage: ~80%
  - Happy path: YES
  - Error conditions: PARTIAL
  - Edge cases: NO (missing boundary tests)
- Code coverage reported: 85% statements

#### Coverage Concerns
1. No test for expired token edge case (exactly at expiry time)
2. No test for malformed JWT structure
3. No test for blacklist race condition

#### Classification of Concerns
These are MISSING TESTS, not bugs in code.
Missing tests = DEV work, not TEST work.

#### Files Reviewed
| File | Lines | Coverage |
|------|-------|----------|
| jwt.service.ts | 180 | 90% |
| jwt.middleware.ts | 45 | 95% |
| blacklist.service.ts | 60 | 75% |

#### Branch
`review/201-jwt-auth`

#### Next Action
1. Complete final verdict
2. If PASS: approve merge to main
3. If FAIL: document gaps, demote to DEV (NOT TEST!)

### Scope Reminder
- I CAN: evaluate, verdict, estimate coverage
- I CANNOT: write code, write tests, fix bugs
```

### Agent-6 Recovery (REVIEW Thread)

```bash
# Step 1: Find work
$ gh issue list --assignee @me --label "in-progress" --label "phase:review"

NUMBER  TITLE                           LABELS
208     JWT Authentication - REVIEW     in-progress, phase:review, wave:1

# Step 2: Verify thread type and phase order
$ gh issue list --label "epic:200" --label "phase:dev" --state open
# Must be empty

$ gh issue list --label "epic:200" --label "phase:test" --state open
# Must be empty
```

**Agent-6 Recovery Comment:**

```markdown
## [REVIEW Session 2] 2024-01-17 13:00 UTC - @agent-6

### State Inherited
From REVIEW Session 1 final checkpoint (11:30 UTC):

#### Thread Type
review (VERIFIED: only REVIEW thread open for this feature)

#### Review Progress
- Code quality: DONE (clean)
- Security review: DONE (no issues)
- Test coverage: IN PROGRESS (concerns documented)
- Final verdict: PENDING

#### Coverage Concerns from Session 1
1. No expired token edge case test
2. No malformed JWT test
3. No blacklist race condition test

### Recovery Actions
1. Verified DEV thread #201 is CLOSED
2. Verified TEST thread #205 is CLOSED
3. Reviewed coverage concerns from Session 1
4. Confirmed: these are MISSING TESTS, not code bugs

### Understanding My Limits
I CAN:
- Complete coverage assessment
- Render final verdict (PASS/FAIL)
- Recommend demotion direction

I CANNOT:
- Write tests to fix coverage
- Fix code issues myself
- Demote to TEST (must be DEV)

### Continuing
Completing final verdict based on coverage analysis.
```

**Agent-6's Final Verdict:**

```markdown
## REVIEW Verdict - 2024-01-17 14:00 UTC - @agent-6

### Final Assessment

#### Code Quality: PASS
- Clean implementation
- Follows project patterns
- Security considerations addressed

#### Test Coverage: INSUFFICIENT

##### Functional Coverage Analysis
| Category | Status | Notes |
|----------|--------|-------|
| Happy path | PASS | All positive flows tested |
| Error conditions | PARTIAL | Missing malformed input handling |
| Edge cases | FAIL | No boundary tests |
| Race conditions | FAIL | No concurrency tests |

##### Missing Critical Tests
1. Expired token at exact boundary (expiry == now)
2. Malformed JWT structure handling
3. Blacklist check during concurrent requests

### Verdict: FAIL

### Required Action
**Demote to DEV** (NOT TEST!)

Reason: Missing tests require DEV to WRITE new tests.
TEST cannot write tests - tests are code.

### Demotion Instructions
1. Close this REVIEW thread (#208)
2. Reopen DEV thread (#201) OR create new DEV iteration
3. DEV must write tests for:
   - Expired token boundary
   - Malformed JWT
   - Blacklist race condition
4. After DEV writes tests → TEST runs them → back to REVIEW

### Note
Do NOT demote to TEST. TEST can only RUN tests, not WRITE them.
Missing coverage = missing code = DEV work.
```

**Key REVIEW Recovery Differences:**
- Verify both DEV and TEST threads are CLOSED
- Focus is evaluation, not implementation
- Cannot fix issues yourself - must demote
- Demotion is ALWAYS to DEV, never TEST
- Missing tests/coverage → DEV (tests are code)
- Bug in code found during review → DEV (code changes)

---

## Thread Transition During Recovery

Sometimes you recover to find a phase transition is needed:

### Recovery Reveals Phase Transition Needed

| Situation at Recovery | Action |
|-----------------------|--------|
| DEV work done, tests not run | Transition to TEST thread |
| TEST complete, all pass | Transition to REVIEW thread |
| REVIEW finds issues | Demote to DEV thread |
| REVIEW passes | Merge to main, close all |

### Phase Transition Commands

```bash
# DEV complete → Open TEST
gh issue close $DEV_ISSUE
gh issue create --title "Feature X - TEST" \
  --label "phase:test" --label "in-progress" \
  --body "TEST thread for Feature X. DEV completed in #$DEV_ISSUE."

# TEST complete → Open REVIEW
gh issue close $TEST_ISSUE
gh issue create --title "Feature X - REVIEW" \
  --label "phase:review" --label "in-progress" \
  --body "REVIEW thread for Feature X. TEST completed in #$TEST_ISSUE."

# REVIEW fail → Reopen DEV
gh issue close $REVIEW_ISSUE
gh issue reopen $DEV_ISSUE
gh issue edit $DEV_ISSUE --add-label "in-progress"
gh issue comment $DEV_ISSUE --body "Demoted from REVIEW. Issues: ..."

# REVIEW pass → Merge and close
gh pr merge $PR_NUMBER --squash
gh issue close $REVIEW_ISSUE --comment "PASS - merged to main"
```

---

## Practice Exercise

To internalize this protocol, simulate a recovery:

1. Pick any in-progress issue in your project
2. Read the thread as if you had no memory
3. **Identify the thread type** (DEV, TEST, or REVIEW)
4. **Verify phase order** (only one thread open)
5. Extract the last state snapshot
6. Verify local state matches
7. Write what your recovery comment would say
8. **Include scope reminder** for that thread type

If you can't do this successfully, the issue thread is missing information.
**That's a sign to improve checkpoint quality.**
