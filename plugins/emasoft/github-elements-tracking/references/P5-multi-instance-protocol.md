# Multi-Instance Coordination Protocol

This document defines how multiple Claude Code instances work together safely when:
- Multiple users on different computers collaborate
- Multiple agents work on the same epic
- Parallel development requires coordination

---

## Core Philosophy

**Order matters. Time does not.**

- No stale claims - claims don't expire with time
- No heartbeats - presence is not required
- No takeovers - assignments are permanent until explicitly released
- Coordination through issue threads, not real-time sync
- All commands use `gh` CLI only - no external scripts

---

## The Challenge

**Scenario:**
```
User A (MacBook) ──► Claude Code Instance A ──► Working on Issue #201
User B (Windows) ──► Claude Code Instance B ──► Working on Issue #202
User C (Linux)   ──► Claude Code Instance C ──► Working on Issue #203
                              │
                              ▼
                    Same Repository
                    Same Epic #200
                    Potentially Same Files
```

**Without coordination:**
- Race conditions on issue claims
- Merge conflicts in git
- Conflicting architectural decisions
- Duplicate work
- Conflicting PRs

**With this protocol:**
- Issue claiming with verification
- Scope declarations prevent file conflicts
- Decision broadcasts ensure consistency
- Order-based coordination (not time-based)

---

## Protocol 1: Issue Claiming

Never assume an issue is available. Check before claiming.

### Claiming Sequence (Strict Order)

```bash
# Step 1: Check if issue is available
gh issue view $ISSUE --json assignees --jq '.assignees | length'
# If result is 0, issue is available

# Step 2: Claim the issue
gh issue edit $ISSUE --add-assignee @me --add-label "in-progress" --remove-label "ready"

# Step 3: Post claim comment
gh issue comment $ISSUE --body "## Claimed

Starting work on this issue.
Will post scope declaration next."

# Step 4: Post scope declaration (required before any work)
gh issue comment $ISSUE --body "## Scope Declaration

### Files I WILL Modify
- <list files>

### Files I will NOT Modify
- <list files belonging to other issues>"
```

**Key points:**
- Check availability before claiming
- Claim comment creates audit trail
- Scope declaration MUST follow claim before work begins
- If another agent already claimed, find another issue

### Post-Claim Verification (Required)

After claiming, verify the claim was successful:

```bash
# Step 5: Verify claim succeeded
ASSIGNEE=$(gh issue view $ISSUE --json assignees --jq '.assignees[0].login')
if [ "$ASSIGNEE" != "@me" ]; then
  echo "CLAIM FAILED: Race condition detected"
  echo "Current assignee: $ASSIGNEE"
  echo "Find another issue."
  exit 1
fi

# Step 6: Verify labels updated
LABELS=$(gh issue view $ISSUE --json labels --jq '.labels[].name')
if ! echo "$LABELS" | grep -q "in-progress"; then
  echo "WARNING: Label update may have failed"
  gh issue edit $ISSUE --add-label "in-progress" --remove-label "ready"
fi

echo "Claim verified successfully."
```

**Why verification matters**: Race conditions can occur when multiple agents claim simultaneously. The agent that loses the race must detect this and find different work.

---

## Protocol 2: Scope Declaration

When starting work, declare which files you'll modify. This prevents file-level conflicts.

### Scope Declaration Format

Post immediately after claiming (strict order: claim → scope → work):

```markdown
## Scope Declaration

### Files I WILL Modify
- src/auth/jwt.service.ts
- src/auth/jwt.middleware.ts
- src/auth/token.types.ts
- tests/auth/jwt.test.ts

### Files I will NOT Modify (belong to other issues)
- src/auth/oauth.ts (#202)
- src/auth/session.ts (#203)

### Shared Files (need coordination)
- src/config/auth.config.ts (will coordinate with #202, #203)
- src/types/index.ts (export only, minimal changes)

### New Files I Will Create
- src/auth/blacklist.service.ts
```

### Checking for Scope Conflicts

Before modifying any file, check if another issue claims it:

```bash
# Check for conflicts by reading scope declarations in other in-progress issues
gh issue list --label "in-progress" --label "epic:200" --json number,body

# Search the returned body text for your file path
# If found in another issue, coordinate before modifying
```

### Handling Scope Conflicts

When conflict detected, post to BOTH issues:

```markdown
## Scope Conflict Detected

### Conflict
Both #201 and #202 claim file: `src/config/auth.config.ts`

### Proposal from #201
I need to add JWT configuration:
- JWT_SECRET
- JWT_EXPIRY
- JWT_REFRESH_EXPIRY

### Request
Please confirm:
1. Not currently modifying auth.config.ts
2. My additions won't conflict
3. Or: Let's coordinate the changes

### Coordination
Will not modify until acknowledged in this thread.
```

---

## Protocol 3: Assignment Management

Assignments are permanent until explicitly released. There are no stale claims.

### Releasing an Assignment

When you can no longer work on an issue (any reason):

```bash
# Post final state
gh issue comment $ISSUE --body "## Releasing Assignment

### Reason
<why releasing>

### Current State
<checkpoint with completed/in-progress/pending>

### Branch
<branch name>

### Next Action
<what the next assignee should do>

Removing self from assignment."

# Release the assignment
gh issue edit $ISSUE --remove-assignee @me
```

### Requesting an Unassignment

If you need to work on an assigned issue and the current assignee is unavailable:

```bash
# Post request to the issue
gh issue comment $ISSUE --body "## Assignment Inquiry

I would like to work on this issue.

Current assignee: Please respond if you are still working on this.
If not actively working, please release the assignment.

Repository owner: If no response after reasonable time, please reassign."
```

Note: Only the repository owner or the assignee themselves can change assignments. There are no automatic takeovers.

---

## Protocol 4: Decision Broadcasting

When an agent makes a decision that affects other issues, it must be broadcast.

### Decisions That Need Broadcasting

- Architecture choices (which library, which pattern)
- Configuration decisions (env vars, settings)
- Interface changes (API contracts, types)
- Dependency additions

### Broadcast Format

Post to the Epic issue (central location):

```markdown
## BROADCAST: Architecture Decision

**From**: Issue #201
**Affects**: All issues in Epic #200
**Category**: Configuration

### Decision
Using Redis for token blacklist with REDIS_URL environment variable.

### Rationale
- Need distributed state across servers
- Redis already in infrastructure for caching
- Well-documented pattern for token blacklist

### Impact on Other Issues
- #202 (OAuth): Should use same REDIS_URL for session storage
- #203 (Password Reset): Can use same Redis for reset tokens

### Action Required
Affected issues should acknowledge and confirm compatibility.
```

### Propagation

Epic coordinator reads decisions from epic thread and posts to affected issues:

```bash
# Post to each affected issue
gh issue comment 202 --body "## Decision from Epic #200

See Epic #200 for full decision on Redis configuration.

Action: Use REDIS_URL for session storage.

Please acknowledge in this thread."
```

### Acknowledging Broadcasts

When receiving a broadcast, acknowledge:

```markdown
## ACK: Decision from Epic #200

Received decision about Redis configuration.

### Compatibility
Compatible with my work. Will use REDIS_URL for OAuth sessions.

### Proceeding
Continuing with acknowledged configuration.
```

---

## Protocol 5: Merge Conflict Prevention

### Before Creating PR

Check for potential conflicts with parallel issues:

```bash
# Step 1: Get your changed files
git fetch origin
git log origin/main..HEAD --name-only | sort -u

# Step 2: List other open PRs in same epic
EPIC_LABEL=$(gh issue view $MY_ISSUE --json labels --jq '.labels[] | select(.name | startswith("epic:")) | .name')
gh pr list --label "$EPIC_LABEL" --json number,title,files

# Step 3: If overlap found, post coordination request to epic
```

### Merge Order Coordination

When conflicts exist, coordinate merge order by posting to the Epic:

```markdown
## Merge Coordination Request

### Conflict
Both #201 and #202 modify `src/config/auth.config.ts`

### Proposal
1. #201 merges first (simpler changes)
2. #202 rebases after #201 merge
3. #202 resolves any conflicts
4. #202 merges

### Order
Merge sequence: #201 → #202

### Agreed?
@agent-on-202 Please confirm this order.
```

---

## Protocol 6: Shared Resource Locking

Some resources can only be modified by one agent at a time.

### Resources That Need Locking

- Database migrations
- CI/CD configuration
- Package.json / requirements.txt (dependency changes)
- Main configuration files

### Lock Protocol

Post lock to epic before modifying a shared resource:

```bash
EPIC=$(gh issue view $ISSUE --json labels --jq '.labels[] | select(.name | startswith("epic:")) | .name | split(":")[1]')

gh issue comment $EPIC --body "## LOCK: $RESOURCE

**Locked by**: Issue #$ISSUE

I am modifying $RESOURCE. Please do not modify until I post UNLOCK."
```

### Unlock Protocol

Post unlock to epic after completing modifications:

```bash
gh issue comment $EPIC --body "## UNLOCK: $RESOURCE

**Released by**: Issue #$ISSUE

$RESOURCE modifications complete. Safe for other issues to modify.

**Changes made**:
- <list changes>"
```

### Checking Locks

Before modifying a lockable resource, check for unreleased locks:

```bash
# Get epic comments and check if more LOCKs than UNLOCKs for this resource
gh issue view $EPIC --json comments --jq '.comments[].body' | grep -c "## LOCK: $RESOURCE"
gh issue view $EPIC --json comments --jq '.comments[].body' | grep -c "## UNLOCK: $RESOURCE"

# If LOCK count > UNLOCK count: resource is locked, wait for UNLOCK
# If LOCK count = UNLOCK count: resource is available
```

---

## Protocol 7: PR Merge Flow (Branch Phases)

PRs do NOT merge directly to main. They must pass through phase gates.

### Two Levels of Order

| Level | What | Order |
|-------|------|-------|
| **Threads/Issues** | DEV, TEST, REVIEW | **ORDERED** (circular sequence) |
| **Elements inside threads** | KNOWLEDGE, ACTION, JUDGEMENT | **UNORDERED** (any order) |

Threads follow strict sequence. Comments within threads can mix knowledge, action, and judgement freely.

### One Thread At A Time Rule

**CRITICAL**: For any feature/solution, only ONE thread (DEV, TEST, or REVIEW) can be open at a time.

| Action | Thread Changes |
|--------|----------------|
| DEV completes → advance to TEST | Close DEV thread, Open TEST thread |
| TEST completes → advance to REVIEW | Close TEST thread, Open REVIEW thread |
| REVIEW passes → complete | Close REVIEW thread, merge to main |
| **REVIEW fails → demote to DEV** | Close REVIEW thread, Reopen DEV thread |
| **TEST finds structural issues** | Close TEST thread, Reopen DEV thread |

**Never**: Open two threads simultaneously for the same feature.

### Circular Phase Order

```
        ┌──────────────────────────────────────────────┐
        │                                              │
        ▼                                              │
    DEV ───────► TEST ───────► REVIEW ─────────────────┤
     │            │               │                    │
     │            │               ▼                    │
     │            │         PASS? → merge to main      │
     │            │               │                    │
     │            │         FAIL? ─────────────────────┘
     │            │               (back to DEV, never TEST)
     │            │
     │       Bug fixes ONLY
     │       (NO structural changes)
     │       (NO rewrites)
     │
 Development work
 Structural changes
 Rewrites (when review demands)
```

### Demotion Rules

| From | Can Demote To | Why |
|------|---------------|-----|
| **REVIEW** | **DEV only** | Fixing review issues requires development work |
| **REVIEW** | ~~TEST~~ | **NEVER** - changes need dev first, then test |
| **TEST** | **DEV** | If bugs reveal structural issues needing rewrite |

**Why Review → DEV only?** Because fixing issues found in review requires development work. Testing validates existing code; it cannot create structural fixes. Only after DEV completes the fixes can TEST validate them again.

**TEST thread limitations**: TEST can only perform bug fixes on existing functionality. If fixing a bug requires structural changes, rewrites, or architectural modifications, the thread MUST demote to DEV. Only REVIEW can decide if a rewrite is needed.

### The Branch Flow

```
PR Submitted (from feature branch)
         │
         ▼
┌─────────────────────────────────────┐
│      TESTING BRANCH                 │
│      + Test Thread opened           │
│      Bug fixes only (no rewrites)   │
│      Must pass 100% of tests        │
└─────────────────┬───────────────────┘
                  │
          All tests pass?
                  │
         NO ──────┼────── YES
  (structural)    │        │
         │        │        ▼
         │        │   ┌─────────────────────────────────────┐
         │        │   │      REVIEW BRANCH                  │
         │        │   │      + Review Thread opened         │
         │        │   │      Must pass unanimous review     │
         │        │   └─────────────────┬───────────────────┘
         │        │                     │
         │        │             Unanimous approval?
         │        │                     │
         │        │            NO ──────┼────── YES
         │        │      (to DEV only)  │        │
         │        │            │        │        ▼
         │        │            │        │   ┌──────────────┐
         │        │            │        │   │     MAIN     │
         │        │            │        │   │   (merged)   │
         │        │            │        │   └──────────────┘
         │        │            │        │
         ▼        │            ▼        │
┌─────────────────────────────────────┐│
│      DEV BRANCH (demotion)          ││
│      + Dev Thread reopened          ││
│      Fix issues, then restart flow  │◄┘
│      NEVER demote to TEST directly  │
└─────────────────────────────────────┘
```

### Self-Approval Rejection

If an agent submits a PR claiming "I tested it myself, I reviewed it myself, let's merge":

```markdown
## PR Rejected: Self-Approval Not Allowed

@agent - PRs cannot be self-approved.

### What Happened
You submitted PR #251 claiming self-testing and self-review.

### Correct Flow
1. PR merges to **testing branch** first
2. **Test thread** opened, independent testing performed
3. If tests pass 100% → merges to **review branch**
4. **Review thread** opened, independent review performed
5. If review passes unanimously → merges to **main**

### Action Required
1. Your PR will be merged to the testing branch
2. A test thread will be opened: #252
3. Wait for independent testing results
4. Do NOT merge to main directly

This is not negotiable.
```

### Demotion Protocol

**Key principle**: Demotion ALWAYS goes to DEV, never to TEST.

When demoting:
1. Close the current thread (TEST or REVIEW)
2. Reopen or create DEV thread
3. Only ONE thread remains open

```bash
# Step 1: Close current thread
gh issue close $CURRENT_THREAD_ISSUE
gh issue comment $CURRENT_THREAD_ISSUE --body "## Thread Closed - Demoting to DEV

### Reason
<issues found requiring development work>

### Why DEV (not TEST)?
<For REVIEW demotion> Fixing these issues requires development work.
Testing validates existing code - it cannot create structural fixes.

### New Thread
Reopening DEV thread: #$DEV_ISSUE"

# Step 2: Reopen DEV thread (if it existed) or create new one
# OPTION A: Reopen existing dev thread
gh issue reopen $DEV_ISSUE
gh issue comment $DEV_ISSUE --body "## Dev Thread Reopened

### Source
Demoted from <test/review> thread #$CURRENT_THREAD_ISSUE

### Issues to Fix
- <issue 1>
- <issue 2>

### Thread Type
dev

### When Complete
1. Make fixes
2. Close this DEV thread
3. Open TEST thread
4. Restart flow: DEV → TEST → REVIEW

### Remember
- Only bug fixes can happen in TEST
- Structural changes must happen here in DEV
- The cycle continues until REVIEW passes"

# OPTION B: Create new dev thread
gh issue create \
  --title "[DEV] Fix: $FEATURE - Iteration N" \
  --label "phase:dev,epic:$EPIC,in-progress" \
  --body "## Dev Thread (Iteration N)

### Original Feature
#$ORIGINAL_ISSUE

### Demoted From
<Test/Review> thread #$CURRENT_THREAD_ISSUE

### Issues to Fix
- <structural issue 1>
- <structural issue 2>

### Thread Type
dev

### Required Skills
- <development skills>

### When Complete
1. Close this DEV thread
2. Open TEST thread
3. Flow: DEV → TEST → REVIEW → (repeat if needed)"

# Step 3: Verify only ONE thread is open
gh issue list --label "epic:$EPIC" --state open --json number,title,labels | \
  jq '.[] | select(.labels[].name | startswith("phase:"))'
# Should show only ONE thread for this feature
```

### TEST Thread Scope: Run Tests + Bug Fixes Only

**TEST threads can ONLY:**
1. **RUN existing tests** - execute test suites
2. **Fix bugs** causing test failures - minimal corrective changes

**TEST threads CANNOT:**
1. **Write new tests** - tests are CODE, writing is DEVELOPMENT
2. **Structural changes** - that's DEV work
3. **Rewrites** - that's DEV work

| Issue Found in Testing | Action |
|------------------------|--------|
| Simple bug (off-by-one, typo) | Fix in TEST thread |
| Logic error (wrong condition) | Fix in TEST thread |
| Missing null check | Fix in TEST thread |
| Performance issue (needs refactor) | **Demote to DEV** |
| Design flaw (wrong approach) | **Demote to DEV** |
| Feature incomplete | **Demote to DEV** |
| Needs rewrite | **Demote to DEV** |
| **Missing test coverage** | **Demote to DEV** (to write new tests) |
| **Need new test cases** | **Demote to DEV** (tests are code) |

**Rule**: If the fix changes the architecture, API, or fundamental design, it must go to DEV.
**Rule**: If new tests need to be written, it must go to DEV. Tests are code.

### Test Development Cycle

```
DEV: Design & write tests ──► TEST: Run tests, fix bugs ──► REVIEW: Check coverage
                                                                    │
                              Missing coverage? ◄───────────────────┘
                                    │
                                    ▼
                              Back to DEV (to write new tests)
```

**Common scenario**: REVIEW discovers a bug that wasn't caught because no test covered it. REVIEW estimates coverage gaps and demotes to DEV to write the missing tests. NEVER to TEST - because TEST doesn't write tests.

### Thread Opening for Each Branch

When PR enters a branch phase, open the corresponding thread:

**Testing Branch:**
```bash
gh issue create \
  --title "Test: #$ISSUE - $TITLE" \
  --label "phase:test,epic:$EPIC" \
  --body "## Test Thread

### Source
PR #$PR from Issue #$ISSUE

### Thread Type
test

### Required Skills
- testing-frameworks
- coverage-analysis

### Scope
Test all functionality from PR #$PR

### Pass Criteria
- All unit tests pass
- All integration tests pass
- Coverage meets threshold
- No regressions

### Fail Action
Demote to dev branch with dev thread"
```

**Review Branch:**
```bash
gh issue create \
  --title "Review: #$ISSUE - $TITLE" \
  --label "phase:review,epic:$EPIC" \
  --body "## Review Thread

### Source
PR #$PR from Issue #$ISSUE (passed testing)

### Thread Type
review

### Required Skills
- code-review
- security-audit

### Scope
Review all code from PR #$PR

### Pass Criteria
- Code quality approved
- Security approved
- Architecture approved
- Unanimous approval required

### Fail Action
Demote to dev branch with dev thread"
```

---

## Multi-Instance Coordination Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     MULTI-INSTANCE COORDINATION                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐              │
│  │  Instance A │      │  Instance B │      │  Instance C │              │
│  │  Issue #201 │      │  Issue #202 │      │  Issue #203 │              │
│  └──────┬──────┘      └──────┬──────┘      └──────┬──────┘              │
│         │                    │                    │                      │
│         ▼                    ▼                    ▼                      │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │                    EPIC #200 THREAD                         │         │
│  │  ┌─────────────────────────────────────────────────────┐   │         │
│  │  │ Broadcasts, Locks, Coordination, Decisions          │   │         │
│  │  └─────────────────────────────────────────────────────┘   │         │
│  └────────────────────────────────────────────────────────────┘         │
│         │                    │                    │                      │
│         ▼                    ▼                    ▼                      │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │                    ISSUE THREADS                            │         │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐              │         │
│  │  │ #201     │    │ #202     │    │ #203     │              │         │
│  │  │ Scope    │    │ Scope    │    │ Scope    │              │         │
│  │  │ Progress │    │ Progress │    │ Progress │              │         │
│  │  │ State    │    │ State    │    │ State    │              │         │
│  │  └──────────┘    └──────────┘    └──────────┘              │         │
│  └────────────────────────────────────────────────────────────┘         │
│         │                    │                    │                      │
│         ▼                    ▼                    ▼                      │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │                    GIT REPOSITORY                           │         │
│  │  feature/201  ←─→  feature/202  ←─→  feature/203           │         │
│  │        │                │                │                  │         │
│  │        └────────────────┼────────────────┘                  │         │
│  │                         ▼                                   │         │
│  │                       main                                  │         │
│  └────────────────────────────────────────────────────────────┘         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference: Multi-Instance Commands

| Action | Command |
|--------|---------|
| Check if issue available | `gh issue view $ISSUE --json assignees --jq '.assignees \| length'` |
| Claim issue | `gh issue edit $ISSUE --add-assignee @me --add-label "in-progress" --remove-label "ready"` |
| Post scope declaration | `gh issue comment $ISSUE --body "## Scope Declaration..."` |
| Release assignment | `gh issue edit $ISSUE --remove-assignee @me` |
| Check for scope conflicts | `gh issue list --label "in-progress" --label "epic:N" --json number,body` |
| Post lock | `gh issue comment $EPIC --body "## LOCK: $RESOURCE..."` |
| Post unlock | `gh issue comment $EPIC --body "## UNLOCK: $RESOURCE..."` |
| Check other PRs for conflicts | `gh pr list --label "epic:N" --json number,files` |

---

## Anti-Patterns

| Anti-Pattern | Problem | Correct Approach |
|--------------|---------|------------------|
| Claim without checking | Race conditions | Check assignees before claiming |
| Skip scope declaration | File conflicts | Always declare scope after claiming |
| Modify without checking scope | Conflicts | Check scope declarations before modifying |
| Silent decisions | Inconsistency | Broadcast all decisions to epic |
| Modify locked resource | Corruption | Check lock/unlock count first |
| Skip merge conflict check | Blocked PRs | Check other PRs before creating yours |
| Takeover without permission | Lost work | Only assignee or owner can change assignment |
| Self-approval ("I tested it myself") | Phase bypass | PR → testing branch → review branch → main |
| Merge PR directly to main | Phase violation | Must pass testing and review branches first |
| Skip test thread | Order violation | Every PR needs independent testing |
| Skip review thread | Order violation | Every PR needs independent review |
| Open thread without skills list | Coordination failure | Always list required skills |
| **Two threads open simultaneously** | Order violation | Only ONE of DEV/TEST/REVIEW at a time |
| **Demote REVIEW → TEST** | Phase bypass | REVIEW always demotes to DEV |
| **Structural changes in TEST** | Scope violation | TEST = bug fixes only, demote to DEV |
| **Rewrite in TEST thread** | Scope violation | Only DEV can do rewrites |
| **Write new tests in TEST thread** | Scope violation | Tests are CODE, writing tests is DEV work |
| **Missing coverage → TEST** | Phase bypass | Missing coverage → DEV (to write tests) |

---

## Summary

Multi-instance coordination requires:

1. **Verified claiming** - Check availability before claiming
2. **Scope declaration** - Declare files before modifying
3. **Assignment management** - Release explicitly, no takeovers
4. **Decision broadcasting** - Post decisions to epic thread
5. **Merge coordination** - Coordinate order, not timing
6. **Resource locking** - Lock/unlock through epic comments
7. **Branch phase gates** - PR → testing branch → review branch → main

### The Two Orders

| Level | Order Type |
|-------|-----------|
| **Threads** (DEV, TEST, REVIEW) | **ORDERED** - circular sequence |
| **Elements** inside threads (KNOWLEDGE, ACTION, JUDGEMENT) | **UNORDERED** - any mix |

### The Circular Flow

```
DEV → TEST → REVIEW → DEV → TEST → REVIEW → ... (until REVIEW passes)
```

### One Thread At A Time

For any feature: only ONE of DEV/TEST/REVIEW can be open. Opening one closes the previous.

### Demotion Direction

- **REVIEW fails** → Demote to **DEV** (never to TEST)
- **TEST finds structural issues** → Demote to **DEV**
- **Missing test coverage** → Demote to **DEV** (to write new tests)
- **TEST is for bug fixes only** - no rewrites, no structural changes, no writing tests

### Test Development Cycle

```
DEV: Write tests ──► TEST: Run tests ──► REVIEW: Check coverage
         ▲                                      │
         └──────── Missing coverage? ───────────┘
```

Tests are CODE. Writing tests is DEVELOPMENT. TEST only RUNS tests.

Follow these protocols and multiple agents can work safely in parallel on the same epic.

**Remember: Order matters. Time does not. Self-approval is not allowed. One thread at a time.**

---

## Issue Deletion Detection

### Detecting Deleted Issues

When resuming work, check if the issue still exists:

```bash
# Check if issue exists
if ! gh issue view $ISSUE &>/dev/null; then
  echo "ERROR: Issue #$ISSUE no longer exists"
  echo "Possible causes:"
  echo "- Issue was deleted"
  echo "- Repository was renamed"
  echo "- Access was revoked"
  exit 1
fi
```

### Handling Deleted Issues

If an issue you were working on was deleted:

1. **Check epic for context**: The epic may have notes about why
2. **Check for replacement**: A new issue may have been created
3. **Post to epic**: Document the situation
4. **Abandon branch**: Don't push orphaned work

```bash
# Post to epic about missing issue
gh issue comment $EPIC --body "## Missing Issue Report

Issue #$DELETED_ISSUE no longer exists.

**Work State:**
- Branch: feature/$DELETED_ISSUE-*
- Commits: [list any unpushed commits]
- Status at deletion: [in-progress/blocked/etc]

**Request:**
Please advise on:
1. Was this intentional?
2. Should work be transferred to another issue?
3. Should branch be deleted?

Waiting for guidance before proceeding."
```

---

## Rate Limit Handling

### GitHub API Rate Limits

The `gh` CLI is subject to GitHub API rate limits:
- Authenticated: 5000 requests/hour
- Unauthenticated: 60 requests/hour

### Monitoring Usage

```bash
# Check current rate limit status
gh api rate_limit --jq '.rate | "Used: \(.used)/\(.limit), Resets: \(.reset | strftime("%H:%M:%S"))"'
```

### Handling Rate Limit Errors

If you encounter rate limit errors:

1. **Wait**: Don't retry immediately
2. **Check reset time**: `gh api rate_limit --jq '.rate.reset'`
3. **Reduce frequency**: Batch operations where possible
4. **Post checkpoint**: Document state before waiting

```bash
# If rate limited, post checkpoint and wait
gh issue comment $ISSUE --body "## Rate Limit Pause

GitHub API rate limit reached. Pausing operations.

**Current State:**
[checkpoint content]

**Rate Limit Reset:**
[reset time]

Will resume after reset."
```

### Prevention

- Batch queries where possible
- Cache results that don't change
- Use webhooks for monitoring instead of polling
- Avoid unnecessary list operations
