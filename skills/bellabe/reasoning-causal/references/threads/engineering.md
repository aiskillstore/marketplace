# Engineering Thread Architecture

## Purpose

Engineering threads **translate business requirements into engineering work specifications**. Nothing more.

**What they do:**
1. Receive business requirement from parent thread
2. Validate technical feasibility
3. Estimate effort and ROI
4. Decide BUILD/DEFER/KILL
5. List what needs to be built

**What they don't do:**
- Design systems (engineering skills do this)
- Write code (engineering skills do this)
- Generate artifacts (engineering skills do this)
- Implement anything (engineering skills do this)

---

## When Created

Triggered by parent thread decision (business/sales/marketing):

```markdown
# Parent thread: threads/operations/some-feature/4-decision.md

Verdict: BUILD

Requires engineering work:
- {Component 1}
- {Component 2}

→ Create: threads/engineering/{feature-name}/
```

---

## Thread Structure

```
threads/engineering/{feature-name}/
├── meta.json
├── 1-input.md              # Business requirement
├── 2-hypothesis.md         # Technical feasibility
├── 3-implication.md        # Effort + ROI
├── 4-decision.md           # BUILD/DEFER/KILL
├── 5-actions.md            # What to build (specs list)
└── 6-learning.md           # Validate technical assumptions
```

**Stage 6:** Validates technical assumptions after engineering skills complete implementation.

---

## Stages

### Stage 1: Input

**Capture:**
- Business requirement (from parent thread)
- Parent thread reference
- Timeline constraint
- Budget constraint
- Success criteria (business perspective)

**Template:**
```markdown
# Input

**Parent thread:** threads/{type}/{name}/
**Business requirement:** {What business needs}
**Timeline:** {weeks}
**Budget:** {$}
**Success criteria:** {Business metrics}
```

---

### Stage 2: Hypothesis

**Test technical assumptions:**
- Is this technically feasible?
- What are the risks?
- What are the unknowns?

**Template:**
```markdown
# Hypothesis

**Feasibility:** FEASIBLE / RISKY / NOT_FEASIBLE

**Key assumptions:**
- {Assumption 1}: {Status}
- {Assumption 2}: {Status}

**Blockers:** {List or "None"}
```

---

### Stage 3: Implication

**Calculate:**
- Engineering effort (weeks)
- Engineering cost ($)
- Business value (from parent thread)
- ROI

**Template:**
```markdown
# Implication

**Effort:** {weeks}
**Cost:** ${amount}
**Business value:** ${amount}
**ROI:** {percentage}%

**Complexity:** Low / Medium / High
```

---

### Stage 4: Decision

**Decide:** BUILD / REFACTOR / DEFER / KILL

**Template:**
```markdown
# Decision

**Verdict:** BUILD / DEFER / KILL

**Rationale:** {Why}

**Success metrics (technical):**
- {Metric 1}: {Target}
- {Metric 2}: {Target}
```

---

### Stage 5: Actions

**List specifications only. No implementation details.**

**Template:**
```markdown
# Actions (Specifications)

## Specification 1: {Component Name}

**What to build:** {1-2 sentence description}

**Requirements:**
- [ ] {Requirement 1}
- [ ] {Requirement 2}
- [ ] {Requirement 3}

**Success criteria:**
- [ ] {Criterion 1}
- [ ] {Criterion 2}

**Complexity:** Low / Medium / High
**Effort estimate:** {weeks}

---

## Specification 2: {Component Name}

{Same structure}

---

## Total

**Components:** {count}
**Total effort:** {weeks}
**Total cost:** ${amount}
```

---

## Stage 6: Learning

**Validate technical assumptions after engineering skills complete implementation.**

**Template:**
```markdown
# Learning

**Date:** {YYYY-MM-DD}

## Technical Assumptions Validated

### T1: {Assumption from Stage 2}
**Original confidence:** {X%}
**Result:** ✅ VALIDATED | ❌ INVALIDATED
**Evidence:** {What happened during implementation}
**Final confidence:** {Y%}

### T2: {Assumption from Stage 2}
{Same structure}

## Actual vs Estimated

| Metric | Estimated | Actual | Variance |
|--------|-----------|--------|----------|
| Effort (weeks) | {est} | {actual} | {+/-%} |
| Cost ($) | {est} | {actual} | {+/-%} |
| Complexity | {est} | {actual} | Changed? |

## What Worked
- {What went well}

## What Didn't Work
- {What was harder than expected}

## Canvas Updates
{If technical learnings affect business assumptions, note which Canvas sections to update}

**Note:** Business impact validation happens in parent thread's Stage 6, not here.
```

---

## Reading Current System State

Engineering threads may need to understand existing systems:

```bash
# Read engineering artifacts (if they exist)
Read artifacts/engineering/{relevant-feature}/

# Read existing system documentation
Read artifacts/engineering/{system}/documentation/

# Read architecture decisions
Read artifacts/engineering/{system}/design/
```

**Note:** Artifact structure TBD. Engineering threads read whatever exists to understand current state before specifying new work.

---

## Thread Metadata

```json
{
  "thread_id": "feature-name",
  "type": "engineering",
  "parent_thread": "business/parent-feature",
  "status": "completed",
  "stage": 5,
  "complexity": "medium",
  "effort_weeks": 3,
  "cost": 40000,
  "business_value": 1100000,
  "roi_percentage": 2650
}
```

---

## Handoff to Engineering Skills

After Stage 5:

```
Engineering Thread produces specifications (Stage 5)
    ↓
Specialized engineering skills:
  - Read specifications from 5-actions.md
  - Read current system state (artifacts)
  - Design architecture
  - Generate code
  - Produce artifacts
  - Deploy to production
    ↓
Engineering Thread Stage 6 (Learning):
  - Validate technical assumptions
  - Document actual vs estimated effort
  - Update if needed
```

**Engineering threads specify and validate. Engineering skills build.**

---

## That's All

Engineering threads follow the complete 6-stage causal flow:
- Stages 1-5: Specify what to build
- Stage 6: Validate technical assumptions after engineering skills complete work

Engineering threads are minimal requirement translators. Implementation happens in specialized engineering skills.