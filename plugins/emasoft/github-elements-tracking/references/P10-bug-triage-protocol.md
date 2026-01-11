# Bug Triage Protocol

## Core Philosophy

**Every contribution is valued. Verify everything. Assume nothing. Be polite always.**

---

## CRITICAL: Bug Reports Go to REVIEW

| Bug Report Source | Route To | NOT To |
|-------------------|----------|--------|
| New GitHub issue | REVIEW thread manager | TEST |
| External user feedback | REVIEW thread manager | TEST |
| Comment in existing thread | Current thread manager | - |

**TEST only runs existing tests.** It does NOT triage bug reports.

---

## The 3-Strike Rule

When a bug report cannot be reproduced after genuine effort:

### Strike 1: First Request for Details

```markdown
Thank you for reporting this issue! I've attempted to reproduce it but wasn't
successful. Could you please provide:

1. **Steps to reproduce** - Exact sequence of actions
2. **Expected behavior** - What should happen
3. **Actual behavior** - What actually happened
4. **Environment** - OS, browser, versions, etc.
5. **Error messages** - Full text or screenshots

This will help me investigate further. Thank you for your patience!
```

### Strike 2: Second Request with Specific Questions

```markdown
Thank you for the additional details! I've tried again but still cannot
reproduce the issue. To help narrow it down:

1. Does this happen every time, or intermittently?
2. When did you first notice this issue?
3. Have you made any recent changes to your setup?
4. Can you share a minimal example that triggers the bug?
5. [Specific technical question based on the report]

I appreciate your continued help in tracking this down!
```

### Strike 3: Polite Closure

```markdown
Thank you for your patience and effort in trying to help us reproduce this issue.
After multiple attempts, I haven't been able to reproduce the reported behavior.

I'm marking this as **cannot-reproduce** for now. If you encounter this issue
again or discover additional details that might help, please feel free to:
- Reopen this issue with the new information
- Open a new issue with more specific reproduction steps

Thank you for taking the time to report this. We appreciate your contribution
to improving the project!
```

---

## Validated Bug Handling

When a bug IS successfully reproduced:

### Case 1: Bug from NEW GitHub Issue

**ALWAYS create a NEW branch.** Never merge into existing threads.

```markdown
## Bug Validated

### Reproduction Confirmed
I was able to reproduce this issue:
- Steps: [steps taken]
- Environment: [environment details]
- Observed: [actual behavior]

### Root Cause Analysis
[Brief analysis of what's causing the issue]

### Resolution Path
This will be addressed through a NEW development cycle:
- New DEV thread will be created
- Implementation will follow DEV -> TEST -> REVIEW
- This issue will be linked to the new thread

### New Branch Created
- DEV Thread: #[NEW_ISSUE]
- Branch: `fix/[ISSUE]-[slug]`

Thank you for reporting this issue! We'll keep you updated on progress.
```

### Case 2: Bug from Comment IN Existing Thread

Handle within the current thread's cycle:

```markdown
## Bug Noted

### Issue Identified
[Description of the issue raised in the comment]

### Assessment
This issue is related to the current work in this thread.

### Resolution
- Adding to current thread scope
- Will be addressed in this cycle
- No new branch needed (comment in existing thread)

Thank you for catching this!
```

---

## Contribution Appreciation Protocol

### Valid Contribution (Any Size)

```markdown
Thank you for [catching this / pointing this out / the detailed analysis]!
You're absolutely right. [Specific acknowledgment of what they found]

[Action being taken]
```

### Invalid/Cannot Reproduce (Still Be Polite)

```markdown
Thank you for taking the time to report this. [Explain the situation politely]

[What happens next / how they can help further]
```

### Disagreement (Respectful)

```markdown
Thank you for raising this point. After investigation, I found that
[explanation of why this isn't a bug / is working as intended].

[Reference to documentation or design decision]

If you have additional context that might change this assessment,
I'd be happy to take another look!
```

---

## Anti-Patterns

| Anti-Pattern | Why Wrong | Correct |
|--------------|-----------|---------|
| "This is just a nitpick" | Dismisses contributor | Verify and thank |
| "I assume this works" | No verification | Test everything |
| "Closing, won't fix" (no explanation) | Rude, unhelpful | Explain decision |
| Route bug to TEST | TEST only runs tests | Route to REVIEW |
| Merge new issue into existing thread | Violates Sacred Order | Create new branch |
| Close without 3 strikes | May miss valid bug | Follow protocol |

---

## Quick Reference

### Decision Tree

```
Bug Report Received
        |
        v
Can reproduce?
   |         |
  YES       NO
   |         |
   v         v
Validate   Strike 1: Ask for details
   |              |
   v              v
New issue?   Still can't reproduce?
   |  |           |         |
  YES NO        YES        NO -> Validate
   |   |          |
   v   v          v
New  Handle   Strike 2: Specific questions
branch in         |
       thread     v
              Still can't reproduce?
                  |         |
                YES        NO -> Validate
                  |
                  v
              Strike 3: Polite closure
```

### Response Timing

- Strike 1: After first reproduction attempt
- Strike 2: After second attempt with user's info
- Strike 3: After third attempt with user's additional info

No urgency. Order matters, timing doesn't.

---

## Reproduction Attempt Limits

### Maximum Attempts Per Strike

To prevent infinite reproduction attempts, each strike has a maximum attempt limit:

| Strike | Max Attempts | After Limit |
|--------|--------------|-------------|
| Strike 1 | 3 tries | Request more info |
| Strike 2 | 5 tries | Request specific info |
| Strike 3 | 5 tries | Polite closure |

### When to Stop

Stop reproduction attempts when ANY of these occur:
- Attempt limit reached for current strike
- Clear conclusion reached (reproduced OR proven unreproducible)
- Same approach tried multiple ways with no variation in results

### Escalation

If after all 3 strikes and maximum attempts the bug cannot be reproduced but seems credible:
1. Add `cannot-reproduce` label
2. Post to epic for visibility
3. Invite reopening if more details become available
4. Close with polite explanation

**Remember**: Attempt limits prevent infinite loops, not thoroughness. Quality over quantity.

---

## Bug Batching Guidance

### When to Batch Bugs

When multiple related bugs are found, batch them for efficiency:

| Scenario | Approach |
|----------|----------|
| Same root cause | Single DEV issue with all bugs listed |
| Same file/module | Single DEV issue, batch by location |
| Related functionality | Single DEV issue with subtasks |
| Unrelated bugs | Separate issues for each |

### Batching Format

When creating a batched bug fix issue:

```markdown
## Batched Bug Fixes: [Area/Module]

### Bugs Included
- [ ] Bug 1: [description] - from #NNN
- [ ] Bug 2: [description] - from #NNN
- [ ] Bug 3: [description] - from #NNN

### Common Root Cause
[If applicable, describe the shared underlying issue]

### Fix Strategy
[How to address all bugs together]

### Individual Tracking
Each bug must be verified individually during TEST phase.
```

### Batching Limits

| Metric | Limit | Reason |
|--------|-------|--------|
| Max bugs per batch | 5 | Prevents scope creep |
| Max lines changed | 200 | Keeps review manageable |
| Max files touched | 10 | Limits blast radius |

If a batch exceeds limits, split into multiple issues.
