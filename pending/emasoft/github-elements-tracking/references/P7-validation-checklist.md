# Validation Checklist

This document provides manual validation checklists and defines the enforcement model.

---

## Core Philosophy

**Order matters. Time does not.**

- Validation checks COMPLETENESS and SEQUENCE, not timing
- No stale detection, no heartbeat enforcement
- Focus: scope declared before work, checkpoints preserve state, order is followed
- ETA is always "when it's done"

---

## Enforcement Model

The protocol uses **progressive enforcement** - violations result in reminders first, then blocks after repeated issues.

### Enforcement Levels

| Level | Trigger | Action |
|-------|---------|--------|
| **Reminder** | First occurrence | Friendly comment with guidance |
| **Warning** | Second occurrence | Warning label added, comment |
| **Block** | Third+ occurrence | Action blocked (PR merge, issue close) |

### Violation Types

| Violation | Detection | Reminder | Warning | Block |
|-----------|-----------|----------|---------|-------|
| Missing scope declaration | Work started without scope | Comment | `violation:scope` label | Require scope before PR |
| Wrong order | Work before scope, or Wave N+1 before Wave N | Comment | Comment | Order enforced |
| Scope conflict | On declaration | Comment | Alert both issues | Block PR merge |
| No linked issue | PR opened | Comment | Request changes | Block merge |
| **Phase violation** | Verdict in dev/test thread | Comment | `violation:phase` label | Retraction required |
| **Self-approval** | PR author = reviewer/tester | Reject | `violation:self-approval` label | Block merge |
| **Wave order violation** | Wave N+1 started before N done | Comment | `violation:wave-order` label | Block progress |
| **Missing thread init** | Thread opened without skills list | Comment | Warning | Require init |

### Violation Lifecycle

```
Violation Detected
       │
       ▼
┌──────────────────┐
│ 1st: Reminder    │
│ (helpful comment)│
└────────┬─────────┘
         │
    Occurs again?
         │
         ▼
┌──────────────────┐
│ 2nd: Warning     │
│ (label + comment)│
└────────┬─────────┘
         │
    Occurs again?
         │
         ▼
┌──────────────────┐
│ 3rd+: Block      │
│ (action blocked) │
└──────────────────┘
```

### Clearing Violations

Violations clear when:
- Agent corrects the issue (posts scope, follows order, etc.)
- Violation label manually removed by coordinator
- Issue closes

---

## Manual Validation Checklists

Use these when automated enforcement isn't enabled or for manual audits.

### Issue Start Checklist

When an agent claims an issue, verify the sequence was followed:

```markdown
### Issue Start Validation

Issue: #___
Agent: ___

#### Required Sequence (Strict Order)
1. [ ] Issue was available (not already assigned)
2. [ ] Claim comment posted
3. [ ] Scope declaration posted BEFORE any work began
4. [ ] Files to modify listed
5. [ ] Files NOT to modify listed (if applicable)
6. [ ] Plan or initial analysis included
7. [ ] Labels updated (ready → in-progress)
8. [ ] Branch created and named correctly

#### Red Flags
- [ ] Work started before scope declaration
- [ ] Scope overlaps with another in-progress issue
- [ ] No plan for complex issue
- [ ] Wrong labels
- [ ] Sequence violated

#### Result
- [ ] PASS - Agent started correctly, sequence followed
- [ ] WARN - Missing elements, posted reminder
- [ ] FAIL - Critical order violation, escalated
```

### Thread Initialization Checklist

When a thread (dev, test, or review) is opened, verify initialization:

```markdown
### Thread Initialization Validation

Thread: #___
Type: [ ] Dev  [ ] Test  [ ] Review

#### Required First Message Sections
- [ ] Thread title declared
- [ ] Required Skills section present:
  - [ ] Skills listed with names
  - [ ] Each skill has "why needed" explanation
- [ ] Thread Type declared (dev | test | review)
- [ ] Scope section present

#### Skills Declaration Check
- [ ] All relevant skills for this work are listed
- [ ] No vague skill references ("general skills")
- [ ] Skills match thread type:
  - Dev thread: development/implementation skills
  - Test thread: testing/QA skills
  - Review thread: code review/evaluation skills

#### Red Flags
- [ ] Thread opened without skills list
- [ ] Skills list is copy-paste from another thread
- [ ] Thread type not declared
- [ ] Scope missing or vague

#### Result
- [ ] PASS - Thread properly initialized
- [ ] WARN - Missing elements, posted reminder
- [ ] FAIL - Must reinitialize thread before proceeding
```

### Phase Gate Validation

Verify actions match thread type (Dev → Test → Review order):

```markdown
### Phase Gate Validation

Thread: #___
Type: ___
Comment Being Validated: ___

#### Thread Type Rules

**If Dev Thread**, verify comment does NOT contain:
- [ ] Definitive verdicts ("this is PASS", "FAIL", "approved")
- [ ] Final reviews ("final review complete")
- [ ] PASS/FAIL judgements
- [ ] Approval/rejection language

**If Test Thread**, verify comment does NOT contain:
- [ ] Feature opinions ("this feature should...")
- [ ] Design criticism ("the architecture is wrong")
- [ ] Architecture judgements ("this pattern is bad")

**If Review Thread**, verify comment does NOT contain:
- [ ] New development ("let me fix this")
- [ ] Implementation work ("I'll add this feature")
- [ ] Code changes beyond review feedback

#### Phase Sequence Check
- [ ] Dev thread created BEFORE test thread
- [ ] Test thread created BEFORE review thread
- [ ] Phase was not skipped

#### Red Flags
- [ ] Verdict posted in dev thread
- [ ] Implementation done in review thread
- [ ] Testing skipped (dev → review directly)
- [ ] "I tested it myself" self-review

#### Result
- [ ] PASS - Actions match thread type
- [ ] WARN - Minor boundary violation, reminder posted
- [ ] FAIL - Phase violation, retraction required
```

### TEST Thread Scope Validation

When a TEST thread has activity, validate actions stay within scope:

```markdown
### TEST Thread Scope Validation

Thread: #___
Activity Being Validated: ___

#### Understanding TEST Scope

TEST threads can ONLY:
- [x] Run existing tests
- [x] Fix simple bugs (typos, null checks, missing await)
- [x] Report test results
- [x] Update test data/fixtures

TEST threads CANNOT:
- [ ] Write new tests
- [ ] Add test cases
- [ ] Make structural changes
- [ ] Do rewrites
- [ ] Render verdicts

#### Activity Classification

**Check the activity:**

Is it writing new tests?
- [ ] NO - Allowed
- [ ] YES - VIOLATION: Demote to DEV

Is it a structural change?
- [ ] NO - Allowed
- [ ] YES - VIOLATION: Demote to DEV

Is it a rewrite/refactor?
- [ ] NO - Allowed
- [ ] YES - VIOLATION: Demote to DEV

Is it rendering a verdict (PASS/FAIL)?
- [ ] NO - Allowed
- [ ] YES - VIOLATION: Wait for REVIEW

#### Bug Fix Classification

If fixing a bug, verify it's simple:
- [ ] Off-by-one error - ALLOWED
- [ ] Typo fix - ALLOWED
- [ ] Missing null check - ALLOWED
- [ ] Missing await - ALLOWED
- [ ] Wrong comparison operator - ALLOWED
- [ ] Architecture change - NOT ALLOWED → demote
- [ ] Logic redesign - NOT ALLOWED → demote
- [ ] Adding new functionality - NOT ALLOWED → demote

#### Red Flags
- [ ] "I added a new test case"
- [ ] "I refactored the..."
- [ ] "I rewrote the..."
- [ ] "PASS" or "FAIL" verdict language
- [ ] Structural code changes
- [ ] New files created (except test reports)

#### Result
- [ ] PASS - Activity within TEST scope
- [ ] WARN - Borderline, posted reminder
- [ ] FAIL - Scope violation, must demote to DEV
```

### Demotion Direction Validation

When a thread demotes, validate it goes to the correct phase:

```markdown
### Demotion Direction Validation

Source Thread: #___ (type: ___)
Target Thread: #___ (type: ___)

#### Valid Demotion Directions

| From | Can Demote To | Cannot Demote To |
|------|---------------|------------------|
| REVIEW | DEV only | TEST (never) |
| TEST | DEV | N/A |

#### Demotion Being Validated

Source thread type: [ ] TEST  [ ] REVIEW
Target thread type: [ ] DEV   [ ] TEST

#### Validation

**If demoting from REVIEW:**
- [ ] Target is DEV → VALID
- [ ] Target is TEST → INVALID (must be DEV)

**If demoting from TEST:**
- [ ] Target is DEV → VALID

#### Reasoning Check

Why is demotion needed?
- [ ] Structural changes required → Must go to DEV
- [ ] New tests needed → Must go to DEV (tests = code)
- [ ] Rewrite required → Must go to DEV
- [ ] Missing coverage → Must go to DEV (to write tests)

#### Why REVIEW → TEST is NEVER Valid
- TEST cannot write new tests
- TEST cannot make structural fixes
- TEST can only run existing tests and fix simple bugs
- Any fix from REVIEW findings requires development work

#### Red Flags
- [ ] "Demoting to TEST to fix this"
- [ ] "TEST can handle these changes"
- [ ] Skipping DEV phase
- [ ] REVIEW → TEST suggestion

#### Result
- [ ] PASS - Demotion direction correct (→ DEV)
- [ ] FAIL - Invalid demotion direction, must correct
```

### PR Branch Flow Checklist

Validate the PR follows the correct branch flow:

```markdown
### PR Branch Flow Validation

PR: #___
Source Branch: ___
Target Branch: ___

#### Flow Verification
Expected: feature → testing → review → main

- [ ] PR targets correct branch for current phase:
  - First PR: feature → testing branch
  - After test pass: testing → review branch
  - After review pass: review → main
- [ ] PR does NOT skip branches:
  - [ ] NOT feature → main
  - [ ] NOT feature → review
  - [ ] NOT testing → main

#### Thread Verification
- [ ] Test thread exists for testing branch
- [ ] Review thread exists for review branch
- [ ] Threads opened BEFORE merges

#### Independence Check
- [ ] PR author is NOT the sole tester
- [ ] PR author is NOT the sole reviewer
- [ ] Independent agent performed testing
- [ ] Independent agent performed review

#### Self-Approval Detection
- [ ] PR author DID NOT approve their own PR
- [ ] PR author DID NOT mark tests as passed
- [ ] No "I tested it myself" comments from author
- [ ] No "reviewed my own code" comments

#### Red Flags
- [ ] PR targets main directly from feature branch
- [ ] Same agent developed, tested, AND reviewed
- [ ] Missing test thread or review thread
- [ ] Self-approval attempt detected

#### Result
- [ ] PASS - PR flow is correct
- [ ] WARN - Flow issues, PR blocked until fixed
- [ ] FAIL - Self-approval or skip detected, PR rejected
```

### Wave Order Validation

Verify wave order is strictly enforced:

```markdown
### Wave Order Validation

Epic: #___
Current Wave: ___
Next Wave Attempted: ___

#### House Analogy Check
"Cannot build floor N+1 while floor N has holes"

- [ ] Wave N-1 100% complete (all issues closed)
- [ ] Wave N is current active wave
- [ ] Wave N+1 has NOT started
- [ ] No "almost done" exceptions granted

#### Wave Status Verification

**Wave N (must be 100% before N+1)**
| Issue | Status | Complete? |
|-------|--------|-----------|
| #___ | ___ | [ ] |
| #___ | ___ | [ ] |

**All checked?** [ ] Yes, all complete → Wave N+1 can start

#### Red Flags
- [ ] Wave N+1 issue claimed while Wave N incomplete
- [ ] "95% done, can we start next wave?" requests
- [ ] Agent working on Wave N+1 issue
- [ ] Wave skipped (N → N+2)

#### Result
- [ ] PASS - Wave order enforced
- [ ] WARN - Premature start detected, work paused
- [ ] FAIL - Wave order violation, escalated to coordinator
```

### Checkpoint Validation

For each checkpoint comment, verify completeness:

```markdown
### Checkpoint Validation

Issue: #___

#### Required Sections
- [ ] Work Log present (what was done)
- [ ] State Snapshot present with:
  - [ ] Completed items
  - [ ] In Progress items
  - [ ] Pending items
- [ ] Needs-Input section (if applicable)
- [ ] Files Changed table
- [ ] Commits table (with hashes)
- [ ] Branch name
- [ ] Next Action (clear single action)

#### Quality Check
- [ ] Completed items match commits
- [ ] Files changed match commits
- [ ] Next action is specific, not vague
- [ ] Could a new agent resume from this checkpoint alone?

#### Red Flags
- [ ] Missing State Snapshot
- [ ] Vague "Next Action" like "continue working"
- [ ] Files changed but no commits
- [ ] Incomplete recovery information

#### Result
- [ ] PASS - Checkpoint is complete and recoverable
- [ ] WARN - Minor issues, posted reminder
- [ ] FAIL - Unusable checkpoint, posted correction request
```

### Session End Validation

For session-ending checkpoints:

```markdown
### Session End Validation

Issue: #___
Session: ___
End Reason: ___

#### Required Elements
- [ ] All checkpoint elements present
- [ ] Session summary (reason for ending)
- [ ] Future-Me Test answered:
  - [ ] All decisions documented
  - [ ] All commits listed
  - [ ] All files listed
  - [ ] Next action clear
  - [ ] Needs-input explained (if any)

#### Recovery Test
Could a new agent resume with ONLY this issue thread?

- [ ] Requirements clear in original post
- [ ] All decisions documented in comments
- [ ] All commits can be found
- [ ] Branch name is clear
- [ ] Next step is unambiguous

#### Red Flags
- [ ] Future-Me Test has "no" answers
- [ ] Missing commits (work described but not committed)
- [ ] Unclear next action
- [ ] Needs-input mentioned but not escalated

#### Result
- [ ] PASS - Session ended correctly, recovery possible
- [ ] WARN - Minor issues, recoverable
- [ ] FAIL - Recovery would be difficult
```

### Epic Validation

For epic issues:

```markdown
### Epic Validation

Epic: #___
Status: ___

#### Structure Check
- [ ] Vision section present
- [ ] Scope section (in/out of scope)
- [ ] Acceptance criteria listed
- [ ] Wave breakdown present (ordered checklists)
- [ ] Dependencies documented

#### Wave Tracking (Order Enforcement)
- [ ] Wave checklist exists
- [ ] All wave issues linked
- [ ] Wave N complete before Wave N+1 starts
- [ ] Progress updates posted when state changes
- [ ] Needs-input items documented and resolved

#### Decision Tracking
- [ ] All architecture decisions posted
- [ ] Decisions propagated to sub-issues
- [ ] Decision rationale included

#### Completion Check (for closing)
- [ ] All sub-issues closed
- [ ] All PRs merged
- [ ] All evaluation waves passed
- [ ] Completion summary posted

#### Red Flags
- [ ] Sub-issues without wave labels
- [ ] Wave N+1 started before Wave N complete
- [ ] Decisions made but not documented
- [ ] Closing with open sub-issues

#### Result
- [ ] PASS - Epic managed correctly, order enforced
- [ ] WARN - Missing elements, posted reminder
- [ ] FAIL - Critical structure or order issues
```

### Review Validation

For review issues:

```markdown
### Review Validation

Review Issue: #___
Type: ___
Verdict: ___

#### Structure Check
- [ ] Review started comment posted
- [ ] Scope confirmed (what's being reviewed)
- [ ] Criteria source identified
- [ ] Checklist used appropriate for type
- [ ] Phase verification done (DEV and TEST threads closed)

#### Coverage Estimation (CRITICAL)
REVIEW must estimate test coverage. This is a core responsibility.

- [ ] Functional coverage assessed:
  - [ ] Happy path tested?
  - [ ] Error conditions tested?
  - [ ] Edge cases tested?
  - [ ] Boundary values tested?
- [ ] Code coverage metrics reviewed (if available):
  - [ ] Statement coverage: ___%
  - [ ] Branch coverage: ___%
  - [ ] Function coverage: ___%
- [ ] Coverage determination made:
  - [ ] SUFFICIENT - meets threshold
  - [ ] INSUFFICIENT - gaps identified
- [ ] If insufficient:
  - [ ] Missing tests documented
  - [ ] Demoting to DEV (not TEST!)

#### Findings Check
- [ ] All findings have severity
- [ ] All findings have location
- [ ] Evidence provided (code, logs, etc.)
- [ ] Recommendations included

#### Verdict Check
- [ ] Clear PASS or FAIL verdict
- [ ] Stats provided (checks performed, passed, failed)
- [ ] Coverage estimation included in verdict
- [ ] Required actions listed (for FAIL)
- [ ] Labels updated correctly

#### Demotion Direction (if FAIL)
- [ ] If demoting, target is DEV (never TEST)
- [ ] Reason for demotion documented
- [ ] DEV thread reopened/created

#### Red Flags
- [ ] No verdict given
- [ ] "Maybe" or "probably" language
- [ ] Findings without severity
- [ ] Findings without location
- [ ] Review closed without verdict
- [ ] **Coverage estimation missing**
- [ ] **Demoting to TEST instead of DEV**
- [ ] **Missing tests → demote to TEST** (wrong!)

#### Result
- [ ] PASS - Review conducted properly with coverage estimation
- [ ] WARN - Minor issues, posted reminder
- [ ] FAIL - Review incomplete, missing coverage estimation, or wrong demotion
```

---

## Conflict Resolution Validation

When scope conflicts occur:

```markdown
### Conflict Resolution Validation

Issue A: #___
Issue B: #___
Conflicting Files: ___

#### Detection
- [ ] Conflict detected (manually or automated)
- [ ] Both issues notified
- [ ] Conflict documented in both threads

#### Resolution
- [ ] Coordination discussion occurred
- [ ] Agreement reached on:
  - [ ] Who modifies what
  - [ ] Or merge order
  - [ ] Or file split
- [ ] Agreement documented in both issues
- [ ] Resolution confirmed by both agents

#### Verification
- [ ] Scopes updated (if applicable)
- [ ] No overlapping modifications after resolution
- [ ] PRs don't conflict

#### Red Flags
- [ ] One issue proceeded without coordination
- [ ] Agreement not documented
- [ ] Scopes still overlap after "resolution"

#### Result
- [ ] PASS - Conflict resolved properly
- [ ] WARN - Partial resolution, monitoring
- [ ] FAIL - Conflict unresolved, escalating
```

---

## Audit Procedures

### Periodic Audit

Run periodically to ensure protocol health:

```markdown
### Protocol Audit

Audit Date: ___
Auditor: ___

#### Issue Health
Total in-progress issues: ___
Issues with complete checkpoints: ___
Issues needing input: ___

#### Order Violations
- Scope violations (work before scope): ___
- Wave order violations (N+1 before N): ___
- Sequence violations: ___

#### Epic Health
Active epics: ___
Epics with complete wave tracking: ___
Epics with incomplete waves: ___

#### Patterns Observed
<any recurring issues>

#### Recommendations
<improvements to process>
```

### Comprehensive Audit

More comprehensive review:

```markdown
### Comprehensive Protocol Audit

Audit Date: ___
Auditor: ___

#### Metrics
- Issues opened: ___
- Issues closed: ___
- Recovery events (compaction): ___
- Successful recoveries: ___
- Failed recoveries: ___

#### Violation Trends
| Violation | Count |
|-----------|-------|
| Scope (work before scope) | |
| Order (Wave N+1 before N) | |
| Incomplete checkpoints | |

#### Conflict Resolution
- Conflicts detected: ___
- Conflicts resolved: ___
- Conflicts escalated: ___

#### Epic Completion
- Epics started: ___
- Epics completed: ___
- Average waves per epic: ___

#### Recommendations
<process improvements>
<training needs>
<tooling improvements>
```

---

## Escalation Matrix

When issues can't be resolved at the issue level:

| Issue | First Escalation | Second Escalation |
|-------|------------------|-------------------|
| Scope conflict | Epic coordinator | Repository owner |
| Quality gate failure | Epic coordinator | Technical lead |
| Order violation | Coordinator warning | Repository owner |
| Architecture dispute | Epic coordinator | Technical lead |
| Needs-input unresolved | Epic coordinator | Repository owner |

### Escalation Format

```markdown
## Escalation: <Issue Type>

### Issue
<Brief description>

### Affected
- Issue(s): #___
- Agent(s): ___

### Attempts Made
1. <what was tried>
2. <what was tried>

### Current State
<where things stand>

### Request
<what decision/action is needed>

### Impact if Unresolved
<consequences of not resolving>

### Recommended Action
<your recommendation>
```

---

## Quick Reference

### Valid State Transitions

```
ready ──────► in-progress ──► review-needed ──► completed
                 │                  │
                 ▼                  ▼
            needs-input         rejected
                 │                  │
                 ▼                  ▼
            (resolve)         fix issues
                 │                  │
                 └────► in-progress ◄┘
```

### PR Branch Flow

```
feature branch ───► testing branch ───► review branch ───► main
      │                   │                   │
      │                   ▼                   ▼
      │              test thread         review thread
      │                   │                   │
      │                   ▼                   ▼
      │              FAIL? ──► demote to dev branch
      │                        (back to dev thread)
      │
      └─ NEVER directly to main
```

### Phase Order

```
Dev Thread ───► Test Thread ───► Review Thread
   │                │                  │
   │                │                  ▼
   │                │           VERDICT ALLOWED
   │                │           (PASS/FAIL)
   │                ▼
   │         Testing results only
   │         (NO verdicts)
   ▼
 Work in progress only
 (NO verdicts, NO final reviews)
```

### Thread Initialization Template

```markdown
## Thread: <Title>

### Required Skills
Agents participating in this thread should activate:
- `skill-name-1` - <why needed>
- `skill-name-2` - <why needed>

### Thread Type
<dev | test | review>

### Scope
<what this thread covers>
```

### Required Comment Types (Strict Order)

| Event | Comment Required | Contains |
|-------|------------------|----------|
| Claim | Yes | Claim announcement |
| Scope | Yes (BEFORE work) | Files to modify/not modify |
| Thread Init | Yes (FIRST message) | Required skills, thread type, scope |
| Checkpoint | Yes (at state changes) | State snapshot |
| Needs-Input | Yes | What's needed, from whom |
| Resolution | Yes | Resolution, next action |
| Session End | Yes | Final state snapshot |

### Label Requirements

| Label | When Applied | When Removed |
|-------|--------------|--------------|
| `ready` | Issue created | Claimed |
| `in-progress` | Claimed | Complete or review |
| `needs-input` | Input required | Input received |
| `review-needed` | Implementation done | Review complete |
| `completed` | Review passes | Issue stays closed |
| `phase:dev` | Review fails (demotion) | Fixes complete |
| `phase:dev` | Dev thread opened | Thread closes |
| `phase:test` | Test thread opened | Thread closes |
| `phase:review` | Review thread opened | Thread closes |
| `violation:phase` | Phase violation | Retracted |
| `violation:wave-order` | Wave order violation | Corrected |
| `violation:self-approval` | Self-approval attempt | PR rejected |
