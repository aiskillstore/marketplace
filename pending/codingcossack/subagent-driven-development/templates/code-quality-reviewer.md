# Code Quality Reviewer Prompt Template

**Purpose:** Verify implementation is well-built (clean, tested, maintainable)

**Prerequisite:** Spec compliance review must have passed. Do not proceed if spec issues remain.

**Method:** Diff-based review. You review the specific changes, not "the repo".

```
Task tool (general-purpose):
  description: "Review code quality for Task N"
  prompt: |
    You are reviewing code quality for a task that has passed spec compliance.

    ## Tracking

    BASE_SHA: [sha before task]
    HEAD_SHA: [sha after task]

    ## What Was Implemented

    [From implementer's report]

    ## Implementer's Claimed Verification

    Commands they claim to have run:
    ```
    [from implementer report]
    ```

    Test results they claim:
    [from implementer report]

    ## Your Job

    **Step 1: Review the diff**
    ```bash
    git diff BASE_SHA..HEAD_SHA
    ```

    **Step 2: Verify implementer's claims (if you have tooling)**
    - Can you rerun their test command?
    - Do results match their claims?
    - If mismatch: flag as Critical issue

    **Step 3: Assess code quality**

    ## Quality Checklist

    **Correctness risks:**
    - [ ] Error handling: Are failures handled? Can errors propagate safely?
    - [ ] Edge cases: Empty inputs, nulls, boundaries?
    - [ ] Concurrency: Race conditions? Shared state issues?
    - [ ] Resource management: Leaks? Cleanup on failure?

    **Maintainability:**
    - [ ] Names: Do they describe what, not how?
    - [ ] Complexity: Can you understand each function in isolation?
    - [ ] DRY: Duplication that should be extracted?
    - [ ] Magic values: Unexplained constants? Should be named.

    **Test quality:**
    - [ ] Coverage: Are critical paths tested?
    - [ ] Assertions: Do tests verify behavior, not implementation?
    - [ ] Independence: Can tests run in any order?
    - [ ] Clarity: Can you understand what each test verifies?

    **Patterns:**
    - [ ] Consistency: Does new code match existing codebase patterns?
    - [ ] Abstraction level: Is it appropriate for the context?

    ## Report Format

    **Strengths:**
    [What's done well - be specific]

    **Issues:**

    **Critical** (blocks approval):
    - [file:line]: [issue]
      - Risk: [what could go wrong]
      - Fix: [suggested fix]

    **Important** (should fix):
    - [file:line]: [issue]
      - Why: [why this matters]
      - Fix: [suggested fix]

    **Minor** (nice to have):
    - [file:line]: [issue]

    **Verification check:**
    - [ ] Implementer's claimed commands are plausible
    - [ ] Test results match claims (or: could not verify)

    **Assessment:**
    - ✅ **Approved** - No critical/important issues
    - ⚠️ **Approved with notes** - Minor issues only, fix optional
    - ❌ **Needs changes** - Critical or important issues must be fixed

    ---

    If using template in `requesting-code-review` skill, use that format instead.
    The above is the fallback when that tool is unavailable.
```
