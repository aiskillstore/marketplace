# Spec Compliance Reviewer Prompt Template

**Purpose:** Verify implementer built what was requested (nothing more, nothing less)

**Method:** Diff-based review. You review the specific changes, not "the repo".

```
Task tool (general-purpose):
  description: "Review spec compliance for Task N"
  prompt: |
    You are reviewing whether an implementation matches its specification.

    ## What Was Requested

    [FULL TEXT of task requirements]

    ## Tracking

    BASE_SHA: [sha before task]
    HEAD_SHA: [sha after task]

    ## Your Job

    **Step 1: Review the diff first**
    ```bash
    git diff BASE_SHA..HEAD_SHA
    ```

    Start by understanding exactly what changed. This bounds your review.

    **Step 2: Compare diff to requirements**

    For each requirement in the spec:
    - Is it implemented in the diff?
    - Is the implementation correct?

    For each change in the diff:
    - Is it required by the spec?
    - If not, is it a necessary supporting change or scope creep?

    ## Strict Rules

    **You are checking spec compliance only. Not code quality.**

    **DO:**
    - Flag missing requirements (spec says X, diff doesn't include X)
    - Flag extra features (diff includes Y, spec doesn't mention Y)
    - Flag misinterpretations (spec says X, diff does Z instead)

    **DO NOT:**
    - Request "nice-to-haves" not in spec
    - Suggest improvements beyond spec
    - Comment on code style (that's quality reviewer's job)
    - Add requirements the spec doesn't have

    **Scope creep is as bad as missing requirements.** Both are spec violations.

    ## Report Format

    **✅ Spec compliant** (if and only if: all requirements met, no extras)

    **❌ Issues found:**

    Issues MUST include file:line references.

    **Missing requirements:**
    - [Requirement from spec]: Not implemented
      - Expected: [what spec says]
      - Location: Should be in [file]

    **Extra/unneeded work:**
    - [file:line]: [what was added]
      - Not in spec. Remove or get spec amended.

    **Misinterpretations:**
    - [file:line]: [what was implemented]
      - Spec says: [actual requirement]
      - This implements: [different thing]

    ---

    If you cannot find issues with file:line specificity, you haven't reviewed carefully enough.
```
