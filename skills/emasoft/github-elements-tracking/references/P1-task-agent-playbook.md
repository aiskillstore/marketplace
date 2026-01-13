# Task Agent Playbook

**You are a Task Agent.** This is your complete operating procedure. Follow it exactly.

---

## Core Philosophy

**Order matters. Time does not.**

- Complete each step before starting the next
- ETA is always "when it's done"
- No urgency, no deadlines, no stale claims
- Checkpoint at meaningful state changes, not time intervals
- All coordination through `gh` CLI only

---

## Thread Types and Phase Gates

### Two Levels of Order

| Level | What | Order |
|-------|------|-------|
| **Threads/Issues** | DEV, TEST, REVIEW | **ORDERED** (circular sequence) |
| **Elements inside threads** | KNOWLEDGE, ACTION, JUDGEMENT | **UNORDERED** (any order) |

Threads follow strict sequence. Comments within threads can mix knowledge, action, and judgement freely.

### Thread Types

| Thread Type | Purpose | ALLOWED | NOT ALLOWED |
|-------------|---------|---------|-------------|
| **Dev Thread** | Development work | Code, structural changes, **DESIGN & WRITE TESTS** | Definitive verdicts, final reviews, PASS/FAIL |
| **Test Thread** | Run tests & bug fixes | **RUN tests**, bug reports, **bug fixes only** | **Writing new tests**, structural changes, rewrites |
| **Review Thread** | Evaluation & verdicts | Verdicts, PASS/FAIL, **ESTIMATE COVERAGE** | New development, writing tests |

**Key insight**: Tests are CODE. Writing tests is DEVELOPMENT. TEST threads only RUN existing tests.

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

### Circular Phase Order

```
FORWARD FLOW (happy path):
    DEV ──────► TEST ──────► REVIEW ──────► COMPLETE (if PASS)

DEMOTION FLOW (on failure):
    REVIEW fails ──► DEV (always - never to TEST)
    TEST finds structural issues ──► DEV

DETAILED VIEW:
        ┌─────────────── REVIEW FAIL ───────────────────┐
        │                                               │
        │         ┌─── TEST demote (structural) ───┐    │
        │         │                                │    │
        ▼         ▼                                │    │
    DEV THREAD ───► TEST THREAD ───► REVIEW THREAD ─┘   │
        ▲               │                 │             │
        │               │                 ▼             │
        │               │         PASS? → close/complete│
        │               │                               │
        │          Bug fixes only                       │
        │          (NO structural changes)              │
        │                                               │
        └───────────────────────────────────────────────┘

CRITICAL:
- REVIEW demotes ONLY to DEV (never to TEST)
- TEST demotes to DEV (if structural issues found)
- Forward flow cannot skip phases
```

### One Thread At A Time Rule

**CRITICAL**: For any feature/solution, only ONE thread (DEV, TEST, or REVIEW) can be open at a time.

| Action | Thread Changes |
|--------|----------------|
| DEV completes → advance to TEST | Close DEV thread, Open TEST thread |
| TEST completes → advance to REVIEW | Close TEST thread, Open REVIEW thread |
| REVIEW passes → complete | Close REVIEW thread, feature done |
| REVIEW fails → demote to DEV | Close REVIEW thread, Reopen DEV thread |
| TEST finds structural issues → demote | Close TEST thread, Reopen DEV thread |

**Never**: Open two threads simultaneously for the same feature.

### Demotion Rules

| From | Can Demote To | Why |
|------|---------------|-----|
| **REVIEW** | **DEV only** | Fixing review issues requires development work |
| **REVIEW** | ~~TEST~~ | **NEVER** - changes need dev first, then test |
| **TEST** | **DEV** | If bugs reveal structural issues needing rewrite |

### Phase Violation Response

If an agent posts a **definitive verdict** in a dev thread (or any out-of-phase action):

```markdown
## Phase Violation Notice

@agent - This is a **dev thread**. Definitive verdicts belong in **review threads**.

### What Happened
You posted: "<the verdict statement>"

### Correct Approach
- In dev threads: Post observations, questions, suggestions
- Wait for: testing phase → review phase
- Then: Post verdicts in the review thread

### Action
Please retract the verdict. Development is ongoing.
```

**Order**: Dev → Test → Review → Dev... (circular until Review passes). Cannot skip phases.

---

## Thread Initialization Protocol

When **opening** any thread (dev, test, or review), the first message MUST declare required skills:

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

This ensures all participating agents have the necessary context before contributing.

---

## Quick Reference

| Protocol | When |
|----------|------|
| Session Start | Every new session |
| Checkpoint | At meaningful state changes (milestone, decision, need-input) |
| Session End | Before ANY session exit |

**Strict Order**: Session Start → Claim/Resume → Scope → Work → Checkpoints → Complete → Review

---

## SESSION START PROTOCOL

Execute these steps in order at the start of EVERY session.

### Step 1: Find Your Work

```bash
# Check for in-progress work assigned to you
gh issue list --assignee @me --label "in-progress" --json number,title,updatedAt
```

**Decision:**
- If results → Go to **Step 2: Resume Existing Work**
- If empty → Go to **Step 3: Claim New Work**

### Step 2: Resume Existing Work

```bash
# Read the issue with all comments
ISSUE=<number from Step 1>
gh issue view $ISSUE --comments
```

**Extract the LAST comment containing `### State Snapshot`**

Parse the snapshot to rebuild your local TodoWrite:

```
From: ### Completed → Create [x] todos
From: ### In Progress → Create [ ] todos (mark in_progress)
From: ### Pending → Create [ ] todos
From: ### Blockers → Check if resolved (search Epic or linked issues)
From: ### Next Action → This is your first task
```

**Post resumption comment:**

```bash
# Generate timestamp first (HEREDOC prevents expansion)
TIMESTAMP="$(date -u +%Y-%m-%d) $(date -u +%H:%M) UTC"

gh issue comment $ISSUE --body "## [Session N] $TIMESTAMP - @me

### State Inherited
<copy Completed/In Progress/Pending from previous snapshot>

### Resuming
Continuing from previous session.
- Previous session ended: <timestamp from last checkpoint>
- Next action from snapshot: <copy Next Action>
- Blockers status: <resolved/still blocked>

Starting work now."
```

**Go to: DURING SESSION**

### Step 3: Claim New Work

```bash
# Find available issues
gh issue list --label "ready" --no-assignee --json number,title,labels --limit 20
```

**Select an issue. Then ATOMICALLY claim it:**

```bash
ISSUE=<selected number>

# Check not already claimed (race condition guard)
CURRENT=$(gh issue view $ISSUE --json assignees --jq '.assignees | length')

if [ "$CURRENT" -eq 0 ]; then
  # Claim atomically
  gh issue edit $ISSUE \
    --add-assignee @me \
    --add-label "in-progress" \
    --remove-label "ready"

  # Generate timestamp and post claim comment
  TIMESTAMP="$(date -u +%Y-%m-%d) $(date -u +%H:%M) UTC"

  gh issue comment $ISSUE --body "## [Session 1] $TIMESTAMP - @me

### Claimed
Starting work on this issue.

### Scope Declaration
Files I will modify:
- <list files you expect to change>

Files I will NOT modify:
- <files belonging to other issues>

### Initial Analysis
<brief understanding of requirements>

### Plan
1. <first step>
2. <second step>
..."

  echo "Claimed issue $ISSUE successfully"
else
  echo "Issue already claimed. Find another."
  # Go back to gh issue list and select different issue
fi
```

**After claiming, update the issue BODY (index) AND announce it:**

```bash
# 1. Get current body and update the index
CURRENT_BODY=$(gh issue view $ISSUE --json body --jq '.body')
# Add: scope checklist items, task checklist, artifact placeholders
# The index stays clean - no work logs
gh issue edit $ISSUE --body-file /tmp/updated_body.md

# 2. Post reply announcing your claim and index updates
gh issue comment $ISSUE --body "## Claimed and Index Updated

Added to index:
- Scope: files I will modify
- Task checklist: <N> tasks
- Artifacts section (pending)

### Initial Analysis
<brief understanding of requirements>

### Plan
1. <first step>
2. <second step>

Starting work now."
```

**CRITICAL**: The reply announces what was added to the index, so subscribers can follow along.

**Read issue requirements:**

```bash
gh issue view $ISSUE
```

**Build your local TodoWrite from requirements:**

```
- [ ] <task 1 from requirements>
- [ ] <task 2 from requirements>
...
```

**Go to: DURING SESSION**

---

## DURING SESSION

### Checkpoint Triggers

Post a checkpoint comment when **ANY** of these occur:

| Trigger | Why |
|---------|-----|
| Major milestone completed | Preserve progress |
| Need input encountered | Document what's needed |
| Decision made | Record reasoning for future reference |
| Token usage feels high (>50%) | Prepare for compaction |
| Before asking user anything | Record context |
| Before spawning subagents | Enable recovery |
| Significant files changed | Document state |
| 3+ files modified since last checkpoint | Track changes |
| Complex operation completed | Ensure recoverability |

Note: Checkpoints are about **state changes**, not time intervals.

### Checkpoint Frequency Guidelines

| Activity Level | Checkpoint Trigger |
|----------------|-------------------|
| Active coding | Every 3 file changes |
| Research/analysis | At each conclusion or after 5 sources reviewed |
| Debugging | At each hypothesis tested or after 3 attempts |
| Waiting for input | Before and after wait |

**Golden Rule**: If you lose context now, could you recover from the last checkpoint? If not, checkpoint now.

### Long-Running Operation Progress

For operations that span multiple steps (builds, test suites, deployments), post progress markers:

```bash
# Before starting long operation
gh issue comment $ISSUE --body "## Operation: Running Test Suite

### Status: IN PROGRESS

Started: $(date -u +%Y-%m-%d) $(date -u +%H:%M) UTC

### Progress
- [ ] Unit tests
- [ ] Integration tests
- [ ] E2E tests

### Expected Completion
After all test phases complete.

Monitoring output..."

# During operation - update with progress
gh issue comment $ISSUE --body "### Progress Update

- [x] Unit tests - PASSED (45/45)
- [ ] Integration tests - IN PROGRESS
- [ ] E2E tests

Continuing..."

# After operation completes
gh issue comment $ISSUE --body "### Operation Complete

- [x] Unit tests - PASSED (45/45)
- [x] Integration tests - PASSED (12/12)
- [x] E2E tests - PASSED (8/8)

**Result**: All tests passed.
Next: Proceeding to checkpoint."
```

**Progress Marker Rules**:
- Post "IN PROGRESS" marker before starting any multi-step operation
- Update progress at each phase completion (not at intervals)
- Post "COMPLETE" marker with results when done
- If operation fails, post failure marker with details before checkpointing

### Checkpoint Format

```bash
# Generate timestamp first
TIMESTAMP="$(date -u +%Y-%m-%d) $(date -u +%H:%M) UTC"

gh issue comment $ISSUE --body "## [Session N] $TIMESTAMP - @me

### Work Log
- [HH:MM] <action taken>
- [HH:MM] <decision made: X because Y>
- [HH:MM] <file changed: path/to/file>
- [HH:MM] <commit: abc1234 - message>

### State Snapshot

#### Completed
- [x] <task that was finished>
- [x] <another completed task>

#### In Progress
- [ ] <task currently working on>

#### Pending
- [ ] <future task 1>
- [ ] <future task 2>

#### Blockers
- <blocker description + who can resolve>

#### Files Changed
| File | Changes |
|------|---------|
| path/to/file1.ts | +50 lines (new function) |
| path/to/file2.ts | Modified: fixed bug |

#### Commits
| Hash | Message |
|------|---------|
| abc1234 | <commit message> |
| def5678 | <commit message> |

#### Branch
\`feature/<issue-number>-<slug>\`

#### Next Action
<exactly what to do next when resuming>

### Continuing
<what you're about to do now>"
```

**After checkpoint, update the first message INDEX and announce the update:**

```bash
# 1. Edit issue body to update checklist/add links
gh issue view $ISSUE --json body --jq '.body' > /tmp/body.md
# Edit /tmp/body.md to check completed task boxes, add links
gh issue edit $ISSUE --body-file /tmp/body.md

# 2. ALWAYS post a reply announcing what changed
# (Subscribers need to see every change in replies)
gh issue comment $ISSUE --body "## Index Updated

- Marked [x] <task name> as complete
- Added link to checkpoint above

Continuing with next task..."
```

**CRITICAL**: Every change gets a reply. The thread is the complete record of the endeavor. Even index edits must be announced in a reply so subscribers can follow along.

### Handling Need-Input Situations

When you need external input (decision, clarification, resource):

```bash
# 1. Update issue label
gh issue edit $ISSUE --add-label "needs-input"

# 2. Post need-input comment with checkpoint
gh issue comment $ISSUE --body "## Need Input

### What's Needed
<detailed description of what input is required>

### Context
Cannot proceed with: <what's affected>

### Who Can Provide
<who or what can provide this input>

### Options (if applicable)
1. <possible resolution 1>
2. <possible resolution 2>

### State Snapshot
<include current state so work can resume after input received>

### Next Action After Input
<what will be done once input is provided>"

# 3. Escalate to epic if appropriate
gh issue comment $EPIC --body "## Input Needed on #$ISSUE

Issue #$ISSUE needs input:
<brief description>

Waiting for: <what's needed>"
```

### When Input Is Received

```bash
# 1. Remove needs-input label
gh issue edit $ISSUE --remove-label "needs-input"

# 2. Post acknowledgment and continue
gh issue comment $ISSUE --body "## Input Received

### Resolution
<what was decided/provided>

### Source
<link to comment or issue where input was given>

### Continuing
<next action now that input is available>"
```

---

## SESSION END PROTOCOL

Execute before session ends for **ANY** reason:
- User ends conversation
- Context exhaustion imminent
- Task completed
- Handoff to another agent
- End of work day

### Mandatory Final Checkpoint

```bash
# Generate timestamp first
TIMESTAMP="$(date -u +%Y-%m-%d) $(date -u +%H:%M) UTC"

gh issue comment $ISSUE --body "## [Session N - END] $TIMESTAMP - @me

### Session Summary
- Session number: N
- Reason for ending: <user request / context limit / task done / handoff>

### Work Log
- <action taken>
- <decision made>

### State Snapshot

#### Completed
- [x] <all completed tasks>

#### In Progress
- [ ] <any unfinished work>

#### Pending
- [ ] <remaining tasks>

#### Blockers
- <any unresolved blockers>

#### Files Changed
| File | Changes |
|------|---------|
| path/to/file | description |

#### Commits
| Hash | Message |
|------|---------|
| abc1234 | message |

#### Branch
\`feature/<issue-number>-<slug>\`

#### Next Action
<EXACTLY what the next session should do first>

### Future-Me Test
Could I resume with ONLY this issue thread?
- All decisions documented: [yes/no]
- All commits listed: [yes/no]
- All files listed: [yes/no]
- Next action clear: [yes/no]
- Blockers explained: [yes/no]"
```

### Update Labels (if status changed)

```bash
# If work complete, ready for review:
gh issue edit $ISSUE \
  --remove-label "in-progress" \
  --add-label "review-needed"

# If handing off to another agent:
gh issue edit $ISSUE --remove-assignee @me

# If task fully complete:
gh issue edit $ISSUE \
  --remove-label "in-progress" \
  --add-label "completed"
# (Coordinator will close after review)
```

---

## SPECIAL PROTOCOLS

### Creating Sub-Tasks

If issue is too large, create sub-issues:

```bash
PARENT=$ISSUE

# Create sub-issue (use double quotes for variable expansion)
gh issue create \
  --title "Sub: <specific task> (of #$PARENT)" \
  --label "sub-issue" \
  --body "## Parent Issue
Part of #$PARENT

## Specific Task
<what this sub-issue covers>

## Acceptance Criteria
- [ ] <criterion 1>
- [ ] <criterion 2>

## When Complete
Update parent #$PARENT with results."

# Get the new issue number
SUB_ISSUE=$(gh issue list --limit 1 --json number --jq '.[0].number')

# Update parent with link (use double quotes for variable expansion)
gh issue comment $PARENT --body "## Sub-Issue Created

Created #$SUB_ISSUE for: <specific task>

Will update this issue when sub-issue completes."
```

### Scope Conflict Detection

Before modifying a file, check if another issue claims it:

```bash
FILE="src/auth/service.ts"
MY_ISSUE=$ISSUE

# Find all in-progress issues in same epic
EPIC_LABEL=$(gh issue view $MY_ISSUE --json labels --jq '.labels[].name | select(startswith("epic:"))')

# Check each for scope declarations mentioning this file
gh issue list --label "in-progress" --label "$EPIC_LABEL" --json number,body | \
  jq -r ".[] | select(.number != $MY_ISSUE) | select(.body | contains(\"$FILE\")) | .number"

# If output is not empty: CONFLICT
# Post to both issues to coordinate
```

---

## ANTI-PATTERNS (Never Do These)

| Anti-Pattern | Why It Fails | Correct Approach |
|--------------|--------------|------------------|
| Work without checkpoints | Context lost on compaction | Checkpoint at state changes |
| Skip session start protocol | Duplicate work, conflicts | Always execute full protocol |
| Modify files outside scope | Merge conflicts | Declare scope, check conflicts |
| End without final checkpoint | Recovery impossible | Always post session-end checkpoint |
| Claim multiple issues | Context dilution | One issue at a time |
| Make decisions silently | Others can't coordinate | Document all decisions in thread |
| Skip steps in sequence | Order violations | Complete each step before next |
| Start work before scope declared | Coordination failure | Claim → Scope → then Work |
| Add urgency/priority labels | Philosophy violation | No time pressure, order only |
| Post verdict in dev thread | Phase violation | Wait for review thread |
| Skip testing phase | Order violation | Dev → Test → Review sequence |
| "I tested it myself" self-approval | Phase bypass | Testing branch → Review branch → Main |
| Open thread without skills list | Coordination failure | Always list required skills first |
| Bloat first message with work logs | Unreadable index | Work logs go in replies, index stays clean |
| Edit index without announcing | Silent change, subscribers miss it | Always post reply explaining index changes |
| Make any change without reply | Breaks thread as record | Every change gets announced in a reply |

---

## QUICK CHECKLIST

### Starting Session (Strict Order)
- [ ] 1. Ran `gh issue list --assignee @me --label "in-progress"`
- [ ] 2. If resuming: Read all comments, found last snapshot
- [ ] 3. If new: Claimed, posted scope declaration
- [ ] 4. Built local TodoWrite from issue state
- [ ] 5. Posted session start comment

### During Session (At State Changes)
- [ ] Posted checkpoint at each meaningful change
- [ ] Documented any decisions made
- [ ] Listed any files changed
- [ ] Listed any commits made

### Ending Session
- [ ] Posted final checkpoint with full state snapshot
- [ ] Answered "Future-Me Test" - all yes
- [ ] Updated labels if status changed
- [ ] Next action is crystal clear

---

## Templates

### Minimal Checkpoint (When Pressed for Time)

```markdown
## Checkpoint - HH:MM UTC

### State Snapshot

#### Completed
- [x] <done>

#### In Progress
- [ ] <doing>

#### Next Action
<what to do next>
```

### Full Checkpoint (Normal)

See **Checkpoint Format** section above.

### Session Start (Resuming)

```markdown
## [Session N] DATE TIME UTC - @me

### State Inherited
<from previous snapshot>

### Resuming
Continuing from previous session.
Next action: <from previous Next Action>
```

### Session Start (New Claim)

```markdown
## [Session 1] DATE TIME UTC - @me

### Claimed
Starting work on this issue.

### Scope Declaration
Files I will modify:
- <list>

### Plan
1. <step>
2. <step>
```

---

**Remember: The issue thread is your permanent memory. Order matters. Time does not.**
