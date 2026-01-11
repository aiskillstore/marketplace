# Quality Gates Skill

**Version:** 1.0.0
**Type:** Quality Assurance & Risk Management
**Auto-activate:** Task planning, complexity assessment, requirement gathering, before task execution

## Overview

This skill teaches agents how to assess task complexity, enforce quality gates, and prevent wasted work on incomplete or poorly-defined tasks. Inspired by production-grade development practices, quality gates ensure agents have sufficient context before proceeding and automatically escalate when stuck or blocked.

**Key Principle:** Stop and clarify before proceeding with incomplete information. Better to ask questions than to waste cycles on the wrong solution.

---

## When to Use This Skill

### Auto-Activate Triggers
- Receiving a new task assignment
- Starting a complex feature implementation
- Before allocating work in Squad mode
- When requirements seem unclear or incomplete
- After 3 failed attempts at the same task
- When blocked by dependencies

### Manual Activation
- User asks for complexity assessment
- Planning a multi-step project
- Before committing to a timeline
- When uncertain about requirements

---

## Core Concepts

### 1. Complexity Scoring (1-5 Scale)

Assess every task on a 1-5 complexity scale:

**Level 1: Trivial**
- Single file change
- Simple variable rename
- Documentation update
- CSS styling tweak
- < 50 lines of code
- < 30 minutes estimated
- No dependencies
- No unknowns

**Level 2: Simple**
- 1-3 file changes
- Basic function implementation
- Simple API endpoint (CRUD)
- Straightforward component
- 50-200 lines of code
- 30 minutes - 2 hours estimated
- 0-1 dependencies
- Minimal unknowns

**Level 3: Moderate**
- 3-10 file changes
- Multiple component coordination
- API with validation and error handling
- State management integration
- Database schema changes
- 200-500 lines of code
- 2-8 hours estimated
- 2-3 dependencies
- Some unknowns that need research

**Level 4: Complex**
- 10-25 file changes
- Cross-cutting concerns
- Authentication/authorization
- Real-time features (WebSockets)
- Payment integration
- Database migrations with data
- 500-1500 lines of code
- 8-24 hours (1-3 days) estimated
- 4-6 dependencies
- Significant unknowns
- Multiple decision points

**Level 5: Very Complex**
- 25+ file changes
- Architectural changes
- New service/microservice
- Complete feature subsystem
- Third-party API integration
- Performance optimization
- 1500+ lines of code
- 24+ hours (3+ days) estimated
- 7+ dependencies
- Many unknowns
- Requires research and prototyping
- High risk of scope creep

### 2. Quality Gate Thresholds

**BLOCKING Conditions** (MUST resolve before proceeding):

1. **Incomplete Requirements** (>3 critical questions)
   - If you have more than 3 unanswered critical questions, STOP
   - Examples of critical questions:
     - "What should happen when X fails?"
     - "What data structure should I use?"
     - "What's the expected behavior for edge case Y?"
     - "Which API should I call?"
     - "What authentication method?"

2. **Missing Dependencies** (blocked by another task)
   - Task depends on incomplete work
   - Required API endpoint doesn't exist
   - Database schema not ready
   - External service not configured

3. **Stuck Detection** (3 attempts at same task)
   - Tried 3 different approaches, all failed
   - Keep encountering the same error
   - Can't find necessary information
   - Solution keeps breaking other things

4. **Evidence Failure** (tests/builds failing)
   - Tests fail after 2 fix attempts
   - Build breaks after changes
   - Type errors persist
   - Integration tests failing

5. **Complexity Overflow** (Level 4-5 tasks without breakdown)
   - Complex task not broken into subtasks
   - No clear implementation plan
   - Too many unknowns
   - Scope unclear

**WARNING Conditions** (Can proceed with caution):

1. **Moderate Complexity** (Level 3)
   - Can proceed but should verify approach first
   - Document assumptions
   - Plan for checkpoints

2. **1-2 Unanswered Questions**
   - Document assumptions
   - Proceed with best guess
   - Note for review later

3. **1-2 Failed Attempts**
   - Try alternative approach
   - Document what didn't work
   - Consider asking for help

### 3. Gate Validation Process

```markdown
## Quality Gate Check

**Task:** [Task description]
**Complexity:** [1-5 scale]
**Dependencies:** [List dependencies]

### Critical Questions (Must answer before proceeding)
1. [Question 1] - ✅ Answered / ❌ Unknown
2. [Question 2] - ✅ Answered / ❌ Unknown
3. [Question 3] - ✅ Answered / ❌ Unknown

**Unanswered Critical Questions:** [Count]

### Dependency Check
- [ ] All required APIs exist
- [ ] Database schema ready
- [ ] Required services running
- [ ] External APIs accessible
- [ ] Authentication configured

**Blocked Dependencies:** [List]

### Attempt History
- Attempt 1: [What was tried, outcome]
- Attempt 2: [What was tried, outcome]
- Attempt 3: [What was tried, outcome]

**Failed Attempts:** [Count]

### Gate Status
- ✅ **PASS** - Can proceed
- ⚠️ **WARNING** - Proceed with caution
- ❌ **BLOCKED** - Must resolve before proceeding

### Blocking Reasons (if blocked)
- [ ] >3 critical questions unanswered
- [ ] Missing dependencies
- [ ] 3+ failed attempts (stuck)
- [ ] Evidence shows failures
- [ ] Complexity too high without plan

### Actions Required
[List actions needed to unblock]
```

---

## Quality Gate Workflows

### Workflow 1: Pre-Task Gate Validation

**When:** Before starting any task (especially Level 3-5)

**Steps:**

1. **Assess Complexity**
   ```
   Read task description
   Count file changes needed
   Estimate lines of code
   Identify dependencies
   Count unknowns
   → Assign complexity score (1-5)
   ```

2. **Identify Critical Questions**
   ```
   What must I know to complete this?
   - Data structures?
   - Expected behaviors?
   - Edge cases?
   - Error handling?
   - API contracts?

   → List all critical questions
   → Count unanswered questions
   ```

3. **Check Dependencies**
   ```
   What does this task depend on?
   - Other tasks?
   - External services?
   - Database changes?
   - Configuration?

   → Verify dependencies ready
   → List blockers
   ```

4. **Gate Decision**
   ```
   if (unansweredQuestions > 3) → BLOCK
   if (missingDependencies > 0) → BLOCK
   if (complexity >= 4 && !hasPlan) → BLOCK
   if (complexity == 3) → WARN
   else → PASS
   ```

5. **Document in Context**
   ```javascript
   context.tasks_pending.push({
     id: 'task-' + Date.now(),
     task: "Task description",
     complexity_score: 3,
     gate_status: 'pass',
     critical_questions: [...],
     dependencies: [...],
     timestamp: new Date().toISOString()
   });
   ```

### Workflow 2: Stuck Detection & Escalation

**When:** After multiple failed attempts at same task

**Steps:**

1. **Track Attempts**
   ```javascript
   // In context, track attempts
   if (!context.attempt_tracking) {
     context.attempt_tracking = {};
   }

   if (!context.attempt_tracking[taskId]) {
     context.attempt_tracking[taskId] = {
       attempts: [],
       first_attempt: new Date().toISOString()
     };
   }

   context.attempt_tracking[taskId].attempts.push({
     timestamp: new Date().toISOString(),
     approach: "Describe what was tried",
     outcome: "Failed because X",
     error_message: "Error details"
   });
   ```

2. **Check Threshold**
   ```javascript
   const attemptCount = context.attempt_tracking[taskId].attempts.length;

   if (attemptCount >= 3) {
     // ESCALATE - stuck
     return {
       status: 'blocked',
       reason: 'stuck_after_3_attempts',
       escalate_to: 'user',
       attempts_history: context.attempt_tracking[taskId].attempts
     };
   }
   ```

3. **Escalation Message**
   ```markdown
   ## 🚨 Escalation: Task Stuck

   **Task:** [Task description]
   **Attempts:** 3
   **Status:** BLOCKED - Need human guidance

   ### What Was Tried
   1. **Attempt 1:** [Approach] → Failed: [Reason]
   2. **Attempt 2:** [Approach] → Failed: [Reason]
   3. **Attempt 3:** [Approach] → Failed: [Reason]

   ### Current Blocker
   [Describe the persistent problem]

   ### Need Guidance On
   - [Specific question 1]
   - [Specific question 2]

   **Recommendation:** Human review needed to unblock
   ```

### Workflow 3: Complexity Breakdown (Level 4-5)

**When:** Assigned a Level 4 or 5 complexity task

**Steps:**

1. **Break Down into Subtasks**
   ```markdown
   ## Task Breakdown: [Main Task]
   **Overall Complexity:** Level 4

   ### Subtasks
   1. **Subtask 1:** [Description]
      - Complexity: Level 2
      - Dependencies: None
      - Estimated: 2 hours

   2. **Subtask 2:** [Description]
      - Complexity: Level 3
      - Dependencies: Subtask 1
      - Estimated: 4 hours

   3. **Subtask 3:** [Description]
      - Complexity: Level 2
      - Dependencies: Subtask 2
      - Estimated: 2 hours

   **Total Estimated:** 8 hours
   **Complexity Check:** All subtasks ≤ Level 3 ✅
   ```

2. **Validate Breakdown**
   ```
   Check:
   - [ ] All subtasks are Level 1-3
   - [ ] Dependencies clearly mapped
   - [ ] Each subtask has clear acceptance criteria
   - [ ] Sum of estimates reasonable
   - [ ] No overlapping work
   ```

3. **Create Execution Plan**
   ```markdown
   ## Execution Plan

   **Phase 1:** Subtask 1
   - Start: After requirements confirmed
   - Gate check: Pass
   - Evidence: Tests pass, build succeeds

   **Phase 2:** Subtask 2
   - Start: After Subtask 1 complete
   - Gate check: Verify Subtask 1 evidence
   - Evidence: Integration tests pass

   **Phase 3:** Subtask 3
   - Start: After Subtask 2 complete
   - Gate check: End-to-end verification
   - Evidence: Full feature tests pass
   ```

### Workflow 4: Requirements Completeness Check

**When:** Starting a new feature or significant task

**Steps:**

1. **Functional Requirements Check**
   ```markdown
   ## Functional Requirements

   - [ ] **Happy path defined:** What should happen when everything works?
   - [ ] **Error cases defined:** What should happen when things fail?
   - [ ] **Edge cases identified:** What are the boundary conditions?
   - [ ] **Input validation:** What inputs are valid/invalid?
   - [ ] **Output format:** What should the output look like?
   - [ ] **Success criteria:** How do we know it works?
   ```

2. **Technical Requirements Check**
   ```markdown
   ## Technical Requirements

   - [ ] **API contracts:** Endpoints, methods, schemas defined?
   - [ ] **Data structures:** Models, types, interfaces specified?
   - [ ] **Database changes:** Schema migrations needed?
   - [ ] **Authentication:** Who can access this?
   - [ ] **Performance:** Any latency/throughput requirements?
   - [ ] **Security:** Any special security considerations?
   ```

3. **Count Critical Unknowns**
   ```javascript
   const criticalUnknowns = [
     !functionalRequirements.happyPath,
     !functionalRequirements.errorCases,
     !technicalRequirements.apiContracts,
     !technicalRequirements.dataStructures
   ].filter(unknown => unknown).length;

   if (criticalUnknowns > 3) {
     return {
       gate_status: 'blocked',
       reason: 'incomplete_requirements',
       critical_unknowns: criticalUnknowns,
       action: 'clarify_requirements'
     };
   }
   ```

---

## Quality Gate Templates

### Template 1: Pre-Task Gate Check

```markdown
# Quality Gate: [Task Name]

**Date:** [YYYY-MM-DD]
**Agent:** [Agent name]

## Complexity Assessment

**Estimated Lines of Code:** [X]
**Estimated Duration:** [X hours]
**File Changes:** [X files]
**Dependencies:** [X dependencies]
**Unknowns:** [X unknowns]

**Complexity Score:** Level [1-5]

## Critical Questions

1. [Question 1] - ✅ Answered / ❌ Unknown
2. [Question 2] - ✅ Answered / ❌ Unknown
3. [Question 3] - ✅ Answered / ❌ Unknown

**Unanswered:** [Count]

## Dependency Check

**Required:**
- [ ] [Dependency 1] - Ready / Blocked
- [ ] [Dependency 2] - Ready / Blocked

**Blockers:** [List]

## Gate Decision

**Status:** ✅ PASS / ⚠️ WARNING / ❌ BLOCKED

**Reasoning:** [Why this decision]

**Actions Required:** [If blocked or warning]

**Can Proceed:** Yes / No
```

### Template 2: Stuck Escalation

```markdown
# Escalation: Task Stuck

**Task:** [Task description]
**Agent:** [Agent name]
**Date:** [YYYY-MM-DD]

## Attempt History

**Attempt 1** ([Timestamp])
- **Approach:** [What was tried]
- **Outcome:** Failed
- **Error:** [Error message or issue]

**Attempt 2** ([Timestamp])
- **Approach:** [What was tried]
- **Outcome:** Failed
- **Error:** [Error message or issue]

**Attempt 3** ([Timestamp])
- **Approach:** [What was tried]
- **Outcome:** Failed
- **Error:** [Error message or issue]

## Current Blocker

[Detailed description of persistent problem]

## Need Guidance

1. [Specific question requiring human input]
2. [Specific question requiring human input]

## Recommendation

**Escalate to:** User / Studio Coach / Specific Agent

**Suggested Actions:** [What might unblock this]
```

### Template 3: Complexity Breakdown

```markdown
# Task Breakdown: [Main Task]

**Original Complexity:** Level [4-5]
**Goal:** Break down to Level 1-3 subtasks

## Subtasks

### Subtask 1: [Name]
- **Complexity:** Level [X]
- **Estimated Duration:** [X hours]
- **Dependencies:** [None / List]
- **Acceptance Criteria:**
  - [ ] [Criterion 1]
  - [ ] [Criterion 2]

### Subtask 2: [Name]
- **Complexity:** Level [X]
- **Estimated Duration:** [X hours]
- **Dependencies:** [List]
- **Acceptance Criteria:**
  - [ ] [Criterion 1]
  - [ ] [Criterion 2]

### Subtask 3: [Name]
- **Complexity:** Level [X]
- **Estimated Duration:** [X hours]
- **Dependencies:** [List]
- **Acceptance Criteria:**
  - [ ] [Criterion 1]
  - [ ] [Criterion 2]

## Validation

- [ ] All subtasks ≤ Level 3
- [ ] Dependencies clearly mapped
- [ ] No circular dependencies
- [ ] Acceptance criteria clear
- [ ] Total estimate reasonable

**Can Proceed:** Yes / No
```

---

## Integration with Context System

Quality gates integrate with the context system for tracking:

```javascript
// Add gate check to context
context.quality_gates = context.quality_gates || [];
context.quality_gates.push({
  task_id: taskId,
  timestamp: new Date().toISOString(),
  complexity_score: 3,
  gate_status: 'pass', // pass, warning, blocked
  critical_questions_count: 1,
  unanswered_questions: 1,
  dependencies_blocked: 0,
  attempt_count: 0,
  can_proceed: true
});
```

## Integration with Evidence System

Quality gates check for evidence before allowing completion:

```javascript
// Before marking task complete
const evidence = context.quality_evidence;
const hasPassingEvidence = (
  evidence?.tests?.exit_code === 0 ||
  evidence?.build?.exit_code === 0
);

if (!hasPassingEvidence) {
  return {
    gate_status: 'blocked',
    reason: 'no_passing_evidence',
    action: 'collect_evidence_first'
  };
}
```

---

## Best Practices

### 1. Always Run Gate Check Before Starting
```javascript
// ❌ BAD: Start immediately
function startTask(task) {
  implementTask(task);
}

// ✅ GOOD: Gate check first
function startTask(task) {
  const gateCheck = runQualityGate(task);

  if (gateCheck.status === 'blocked') {
    escalate(gateCheck.reason);
    return;
  }

  if (gateCheck.status === 'warning') {
    documentAssumptions(gateCheck.warnings);
  }

  implementTask(task);
}
```

### 2. Document All Assumptions
```markdown
When proceeding with warnings, document assumptions:

## Assumptions Made
1. **Assumption:** API will return JSON format
   **Risk:** Low - standard REST practice
   **Mitigation:** Add try-catch for parsing

2. **Assumption:** User authentication already implemented
   **Risk:** Medium - might not exist
   **Mitigation:** Check early, escalate if missing
```

### 3. Track Attempts for Stuck Detection
```javascript
// Track every attempt
function attemptTask(taskId, approach) {
  trackAttempt(taskId, approach);

  const attemptCount = getAttemptCount(taskId);
  if (attemptCount >= 3) {
    escalateToUser(taskId);
    return 'blocked';
  }

  return executeApproach(approach);
}
```

### 4. Break Down Complex Tasks Proactively
```javascript
// ❌ BAD: Tackle Level 5 task directly
implementComplexFeature();

// ✅ GOOD: Break down first
function handleComplexTask(task) {
  if (task.complexity >= 4) {
    const subtasks = breakDownIntoSubtasks(task);

    subtasks.forEach(subtask => {
      runQualityGate(subtask);
      implementSubtask(subtask);
    });
  } else {
    implementTask(task);
  }
}
```

---

## Common Pitfalls

### ❌ Pitfall 1: Skipping Gate Checks for "Simple" Tasks
```markdown
**Problem:** Assume task is simple, skip gate check, get stuck later
**Solution:** Always run gate check, even for Level 1-2 tasks (quick check)
```

### ❌ Pitfall 2: Ignoring Warning Status
```markdown
**Problem:** Proceed with warnings without documenting assumptions
**Solution:** Document every assumption when proceeding with warnings
```

### ❌ Pitfall 3: Not Tracking Attempts
```markdown
**Problem:** Keep trying same approach repeatedly, waste cycles
**Solution:** Track every attempt, escalate after 3
```

### ❌ Pitfall 4: Proceeding When Blocked
```markdown
**Problem:** Gate says BLOCKED but proceed anyway "to make progress"
**Solution:** NEVER bypass BLOCKED gates - resolve blockers first
```

---

## Quick Reference

### Complexity Quick Check
- 1-3 files, < 200 lines, < 2 hours → **Level 1-2**
- 3-10 files, 200-500 lines, 2-8 hours → **Level 3**
- 10-25 files, 500-1500 lines, 8-24 hours → **Level 4**
- 25+ files, 1500+ lines, 24+ hours → **Level 5**

### Blocking Threshold Quick Check
- >3 critical questions unanswered → **BLOCK**
- Missing dependencies → **BLOCK**
- 3+ failed attempts → **BLOCK & ESCALATE**
- Level 4-5 without breakdown → **BLOCK**

### Gate Decision Quick Flow
```
1. Assess complexity (1-5)
2. Count critical questions unanswered
3. Check dependencies blocked
4. Check attempt count

if (questions > 3 || dependencies blocked || attempts >= 3) → BLOCK
else if (complexity >= 4 && no plan) → BLOCK
else if (complexity == 3 || questions 1-2) → WARNING
else → PASS
```

---

## Version History

**v1.0.0** - Initial release
- Complexity scoring (1-5 scale)
- Blocking thresholds
- Stuck detection and escalation
- Requirements completeness checks
- Context integration
- Templates and workflows

---

**Remember:** Quality gates prevent wasted work. Better to ask questions upfront than to build the wrong solution. When in doubt, BLOCK and escalate.
