# Quality Gate Check Template

Copy and fill in this template before starting any task to ensure you have sufficient context.

---

## Task Information

**Task ID:** [Unique identifier]
**Task Description:** [Clear description of what needs to be done]
**Assigned Agent:** [Agent name]
**Date:** [YYYY-MM-DD HH:MM:SS]

---

## 1. Complexity Assessment

### Basic Metrics

**Estimated Lines of Code:** [Number]
**Estimated Duration:** [X hours/days]
**Number of Files to Change:** [Number]
**Number of Dependencies:** [Number]
**Number of Unknowns:** [Number]

### Complexity Score

Based on the metrics above, assign a complexity score:

**Complexity Level:** [Circle one]

- [ ] **Level 1** - Trivial (< 50 lines, < 30 min, 1 file, 0 dependencies, 0 unknowns)
- [ ] **Level 2** - Simple (50-200 lines, 30 min - 2 hrs, 1-3 files, 0-1 dependencies, minimal unknowns)
- [ ] **Level 3** - Moderate (200-500 lines, 2-8 hrs, 3-10 files, 2-3 dependencies, some unknowns)
- [ ] **Level 4** - Complex (500-1500 lines, 8-24 hrs, 10-25 files, 4-6 dependencies, significant unknowns)
- [ ] **Level 5** - Very Complex (1500+ lines, 24+ hrs, 25+ files, 7+ dependencies, many unknowns)

**Complexity Rationale:** [Why this level?]

---

## 2. Critical Questions Assessment

List ALL critical questions that MUST be answered before proceeding:

### Functional Questions

1. **Happy Path:** What should happen when everything works correctly?
   - ✅ Answered: [Answer] / ❌ Unknown

2. **Error Cases:** What should happen when things fail?
   - ✅ Answered: [Answer] / ❌ Unknown

3. **Edge Cases:** What are the boundary conditions?
   - ✅ Answered: [Answer] / ❌ Unknown

4. **Input Validation:** What inputs are valid/invalid?
   - ✅ Answered: [Answer] / ❌ Unknown

5. **Output Format:** What should the output look like?
   - ✅ Answered: [Answer] / ❌ Unknown

### Technical Questions

6. **Data Structures:** What models/types/interfaces are needed?
   - ✅ Answered: [Answer] / ❌ Unknown

7. **API Contracts:** What are the API endpoints/methods/schemas?
   - ✅ Answered: [Answer] / ❌ Unknown

8. **Authentication:** Who can access this? What permissions required?
   - ✅ Answered: [Answer] / ❌ Unknown

9. **Database Changes:** Any schema changes or migrations needed?
   - ✅ Answered: [Answer] / ❌ Unknown

10. **Dependencies:** What external services/libraries are needed?
    - ✅ Answered: [Answer] / ❌ Unknown

### Additional Critical Questions

11. [Your question]
    - ✅ Answered: [Answer] / ❌ Unknown

12. [Your question]
    - ✅ Answered: [Answer] / ❌ Unknown

13. [Your question]
    - ✅ Answered: [Answer] / ❌ Unknown

### Question Summary

**Total Critical Questions:** [Count]
**Answered:** [Count]
**Unanswered:** [Count]

---

## 3. Dependency Check

List ALL dependencies this task has on other work or resources:

### Task Dependencies

- [ ] **Dependency 1:** [Task/feature name]
  - Status: ✅ Complete / ⚠️ In Progress / ❌ Not Started
  - Blocker: Yes / No

- [ ] **Dependency 2:** [Task/feature name]
  - Status: ✅ Complete / ⚠️ In Progress / ❌ Not Started
  - Blocker: Yes / No

- [ ] **Dependency 3:** [Task/feature name]
  - Status: ✅ Complete / ⚠️ In Progress / ❌ Not Started
  - Blocker: Yes / No

### Technical Dependencies

- [ ] **API Endpoint:** [Endpoint name]
  - Status: ✅ Exists / ❌ Needs Creation
  - Blocker: Yes / No

- [ ] **Database Schema:** [Table/collection name]
  - Status: ✅ Ready / ❌ Needs Migration
  - Blocker: Yes / No

- [ ] **External Service:** [Service name]
  - Status: ✅ Configured / ❌ Not Setup
  - Blocker: Yes / No

- [ ] **Authentication/Authorization:** [System name]
  - Status: ✅ Implemented / ❌ Not Ready
  - Blocker: Yes / No

### Dependency Summary

**Total Dependencies:** [Count]
**Ready:** [Count]
**Blocked:** [Count]

**Blocking Dependencies:** [List any that block progress]

---

## 4. Attempt History (if applicable)

If this is not the first attempt at this task, document previous attempts:

### Attempt 1
- **Date:** [YYYY-MM-DD]
- **Approach:** [What was tried]
- **Outcome:** ✅ Success / ❌ Failed
- **Reason for Failure:** [If failed, why?]
- **Learnings:** [What did you learn?]

### Attempt 2
- **Date:** [YYYY-MM-DD]
- **Approach:** [What was tried]
- **Outcome:** ✅ Success / ❌ Failed
- **Reason for Failure:** [If failed, why?]
- **Learnings:** [What did you learn?]

### Attempt 3
- **Date:** [YYYY-MM-DD]
- **Approach:** [What was tried]
- **Outcome:** ✅ Success / ❌ Failed
- **Reason for Failure:** [If failed, why?]
- **Learnings:** [What did you learn?]

### Attempt Summary

**Total Attempts:** [Count]
**Status:** First Attempt / Retrying / Stuck (3+ attempts)

---

## 5. Gate Decision

### Automatic Checks

Based on the information above, check these conditions:

#### BLOCKING Conditions (Must resolve to proceed)

- [ ] **>3 Critical Questions Unanswered**
  - Unanswered: [Count from Section 2]
  - Blocks: ✅ Yes (>3) / ❌ No (≤3)

- [ ] **Missing Dependencies**
  - Blocked Dependencies: [Count from Section 3]
  - Blocks: ✅ Yes (>0) / ❌ No (0)

- [ ] **Stuck (3+ Failed Attempts)**
  - Attempts: [Count from Section 4]
  - Blocks: ✅ Yes (≥3) / ❌ No (<3)

- [ ] **High Complexity Without Plan**
  - Complexity: [Level from Section 1]
  - Has Breakdown Plan: Yes / No
  - Blocks: ✅ Yes (Level 4-5 + no plan) / ❌ No

#### WARNING Conditions (Can proceed with caution)

- [ ] **Moderate Complexity (Level 3)**
  - Requires: Document assumptions, plan checkpoints

- [ ] **1-2 Unanswered Questions**
  - Requires: Document assumptions for unknowns

- [ ] **1-2 Failed Attempts**
  - Requires: Try alternative approach, document learnings

### Gate Status

**Final Decision:** [Circle one]

- [ ] **✅ PASS** - Can proceed without restrictions
- [ ] **⚠️ WARNING** - Can proceed with documented cautions
- [ ] **❌ BLOCKED** - MUST resolve blocking conditions first

### Decision Rationale

[Explain why this decision was made based on the checks above]

---

## 6. Actions Required

### If BLOCKED

**Blocking Reasons:**
- [List specific blocking conditions from Section 5]

**Actions to Unblock:**
1. [Specific action needed]
2. [Specific action needed]
3. [Specific action needed]

**Escalation:**
- Escalate to: User / Studio Coach / [Specific Agent]
- Escalation Message: [What to communicate]

### If WARNING

**Assumptions Being Made:**
1. **Assumption:** [What are you assuming?]
   - **Risk:** Low / Medium / High
   - **Mitigation:** [How to reduce risk]

2. **Assumption:** [What are you assuming?]
   - **Risk:** Low / Medium / High
   - **Mitigation:** [How to reduce risk]

**Checkpoint Plan:**
- Checkpoint 1: [After X hours/steps, verify Y]
- Checkpoint 2: [After X hours/steps, verify Y]

### If PASS

**Ready to Proceed:** Yes

**Next Steps:**
1. [First action to take]
2. [Second action to take]
3. [Third action to take]

---

## 7. Record in Context

After completing this gate check, record in shared context:

```javascript
context.quality_gates = context.quality_gates || [];
context.quality_gates.push({
  task_id: "[Task ID]",
  timestamp: "[YYYY-MM-DD HH:MM:SS]",
  complexity_score: [1-5],
  gate_status: "pass|warning|blocked",
  critical_questions_count: [Total],
  unanswered_questions: [Count],
  dependencies_blocked: [Count],
  attempt_count: [Count],
  can_proceed: true|false,
  blocking_reasons: ["reason1", "reason2"],
  assumptions: ["assumption1", "assumption2"]
});
```

---

## 8. Sign-Off

**Gate Checked By:** [Agent name]
**Date:** [YYYY-MM-DD HH:MM:SS]
**Can Proceed:** ✅ Yes / ❌ No
**Status:** [PASS / WARNING / BLOCKED]

**Notes:** [Any additional notes or observations]

---

## Quick Decision Tree

Use this quick reference:

```
1. Count unanswered critical questions
   └─ >3? → BLOCKED
   └─ 1-2? → WARNING
   └─ 0? → Continue

2. Check dependencies
   └─ Any blocked? → BLOCKED
   └─ All ready? → Continue

3. Check attempts
   └─ ≥3 failed? → BLOCKED (escalate)
   └─ 1-2 failed? → WARNING
   └─ First attempt? → Continue

4. Check complexity
   └─ Level 4-5 + no plan? → BLOCKED
   └─ Level 3? → WARNING
   └─ Level 1-2? → Continue

5. Final decision
   └─ Any BLOCKED? → Gate: BLOCKED
   └─ Any WARNING? → Gate: WARNING
   └─ All clear? → Gate: PASS
```
