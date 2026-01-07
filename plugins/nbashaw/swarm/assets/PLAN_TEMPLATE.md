# [PROJECT NAME]

## Goal

[One sentence. What does "done" look like? Be specific and measurable.]

## Context

[What does an agent need to know to orient?]
- Codebase structure
- Key files/directories
- Dependencies
- Constraints

## Plan

### Phase 0: Pre-flight Check
Before starting work, verify:
- [ ] Read the Goal and confirm understanding
- [ ] Check if work is already done (run tests, check git log)
- [ ] If already complete, skip to Gatekeeper immediately
- [ ] Identify first incomplete step to work on

### Phase 1: [Name]
- [ ] Step
- [ ] Step
- [ ] Step

### Phase 2: [Name]
- [ ] Step
- [ ] Step
- [ ] Step

### Phase 3: [Name]
- [ ] Step
- [ ] Step
- [ ] Step

## Agent Roles

### Every 5th Iteration — Reviewer
Stop implementing. Adopt fresh eyes.
- Re-read the Goal above
- Explore what currently exists
- Ask: "Does this actually solve the problem?"
- Log your assessment before continuing

### Before Final Phase — Simplifier
- What can be deleted?
- What's overengineered?
- Is there a simpler approach?
- Log opportunities, then continue or refactor

### Before Final Phase — Tester
- Write tests for what exists
- Run them: `[TEST COMMAND]`
- Log results and coverage

### Before .done — Gatekeeper

**Required checks (run and paste actual output):**
```
$ [TEST COMMAND]
[paste result]

$ [BUILD/LINT COMMAND]
[paste result]

$ git diff --stat
[paste result]
```

**Explicit answers:**
- Does the code achieve the Goal? [yes/no + evidence]
- Any hacks, TODOs, or shortcuts? [list them]
- Would you merge this PR? [yes/no + reasoning]

**DECISION:** [GO / NO-GO]
**REASON:** [explanation]

If NO-GO: explain what's needed and DO NOT create .done

**If GO:**
- [ ] Log GO decision with timestamp and reasoning
- [ ] Create .done file: `touch .context/.done-[project-name]`
- [ ] Confirm .done file exists: `ls .context/.done-*`

## Rules

1. Complete one phase before starting the next
2. Run tests after every significant change
3. If tests fail, fix before continuing
4. If stuck 2+ iterations on same problem, log blocker and try different approach
5. Commit after each phase: `git add -A && git commit -m "phase N: description"`
6. Never create .done without completing Gatekeeper checklist in Log

## Log

<!--
Agents: append your work here after each iteration.
Format:

### Iteration N — YYYY-MM-DD HH:MM

**Role:** [Worker / Reviewer / Simplifier / Tester / Gatekeeper]

**What I did:**
- thing 1
- thing 2

**Current state:**
- what works
- what doesn't

**Next agent should:**
- suggested next step

---
-->
