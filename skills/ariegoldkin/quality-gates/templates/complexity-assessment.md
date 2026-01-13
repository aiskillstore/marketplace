# Complexity Assessment Template

Use this template to quickly assess task complexity on a 1-5 scale.

---

## Task: [Task Name]

**Date:** [YYYY-MM-DD]
**Assessor:** [Agent name]

---

## Assessment Criteria

Score each criterion, then sum for total complexity assessment:

### 1. Lines of Code Estimate

- [ ] **< 50 lines** = 1 point
- [ ] **50-200 lines** = 2 points
- [ ] **200-500 lines** = 3 points
- [ ] **500-1500 lines** = 4 points
- [ ] **1500+ lines** = 5 points

**Score:** _____ / 5

---

### 2. Time Estimate

- [ ] **< 30 minutes** = 1 point
- [ ] **30 minutes - 2 hours** = 2 points
- [ ] **2-8 hours** = 3 points
- [ ] **8-24 hours (1-3 days)** = 4 points
- [ ] **24+ hours (3+ days)** = 5 points

**Score:** _____ / 5

---

### 3. Number of Files

- [ ] **1 file** = 1 point
- [ ] **2-3 files** = 2 points
- [ ] **4-10 files** = 3 points
- [ ] **11-25 files** = 4 points
- [ ] **26+ files** = 5 points

**Score:** _____ / 5

---

### 4. Dependencies Count

- [ ] **0 dependencies** = 1 point
- [ ] **1 dependency** = 2 points
- [ ] **2-3 dependencies** = 3 points
- [ ] **4-6 dependencies** = 4 points
- [ ] **7+ dependencies** = 5 points

**Score:** _____ / 5

---

### 5. Unknowns/Uncertainty

- [ ] **No unknowns** - Everything clear = 1 point
- [ ] **Minimal unknowns** - 1-2 minor questions = 2 points
- [ ] **Some unknowns** - Several questions, researchable = 3 points
- [ ] **Significant unknowns** - Many questions, requires exploration = 4 points
- [ ] **Many unknowns** - Unclear scope, needs prototyping = 5 points

**Score:** _____ / 5

---

### 6. Cross-Cutting Concerns

- [ ] **Isolated change** - Single module = 1 point
- [ ] **Minor integration** - 2-3 modules = 2 points
- [ ] **Multiple integrations** - 4-5 modules = 3 points
- [ ] **Cross-cutting** - Affects many modules = 4 points
- [ ] **Architectural** - System-wide impact = 5 points

**Score:** _____ / 5

---

### 7. Risk Level

- [ ] **No risk** - Trivial change = 1 point
- [ ] **Low risk** - Well-understood pattern = 2 points
- [ ] **Medium risk** - Some complexity, testable = 3 points
- [ ] **High risk** - Complex logic, many edge cases = 4 points
- [ ] **Very high risk** - Mission-critical, high stakes = 5 points

**Score:** _____ / 5

---

## Total Complexity Score

**Sum of all scores:** _____ / 35

### Complexity Level Assignment

Calculate average score: **Total ÷ 7 = _____**

**Final Complexity Level:**

- [ ] **Level 1 (Trivial)** - Average 1.0-1.4
- [ ] **Level 2 (Simple)** - Average 1.5-2.4
- [ ] **Level 3 (Moderate)** - Average 2.5-3.4
- [ ] **Level 4 (Complex)** - Average 3.5-4.4
- [ ] **Level 5 (Very Complex)** - Average 4.5-5.0

**Assigned Level:** _____

---

## Quick Complexity Guide

### Level 1: Trivial
- Single file edit
- Documentation or comment changes
- Simple variable rename
- CSS styling tweak
- **Examples:** Fix typo, update README, change button color

### Level 2: Simple
- Basic function implementation
- Simple CRUD endpoint
- Straightforward component
- **Examples:** Add GET endpoint for users, create login button component

### Level 3: Moderate
- Multi-component coordination
- API with validation
- State management
- Database schema change
- **Examples:** Implement user registration flow, add pagination to list

### Level 4: Complex
- Cross-cutting concerns
- Authentication/authorization
- Real-time features
- Payment integration
- **Examples:** Add WebSocket notifications, integrate Stripe, implement RBAC

### Level 5: Very Complex
- Architectural changes
- New service/microservice
- Complete feature subsystem
- Performance optimization
- **Examples:** Migrate to microservices, build search engine, add caching layer

---

## Breakdown Requirement

**If Level 4 or 5:**

This task is too complex to tackle directly. It MUST be broken down into Level 1-3 subtasks before proceeding.

**Action Required:** Create task breakdown using `/skills/quality-gates/templates/breakdown-template.md`

---

## Context Recording

```javascript
// Record complexity assessment in context
context.tasks_pending = context.tasks_pending || [];
context.tasks_pending.push({
  task: "[Task description]",
  complexity_score: [1-5],
  complexity_breakdown: {
    lines_of_code: [score],
    time_estimate: [score],
    files_count: [score],
    dependencies: [score],
    unknowns: [score],
    cross_cutting: [score],
    risk: [score]
  },
  needs_breakdown: [true if Level 4-5],
  timestamp: new Date().toISOString()
});
```

---

## Decision

**Complexity Level:** [1-5]

**Can Proceed Directly:** ✅ Yes (Level 1-3) / ❌ No (Level 4-5, needs breakdown)

**Next Action:**
- **If Level 1-3:** Proceed with gate check using gate-check-template.md
- **If Level 4-5:** Break down using breakdown-template.md, then reassess subtasks
