# Implementer Subagent Prompt Template

```
Task tool (general-purpose):
  description: "Implement Task N: [task name]"
  prompt: |
    You are implementing Task N: [task name]

    ## Task Description

    [FULL TEXT of task from plan - paste it here, don't make subagent read file]

    ## Context

    [Scene-setting: where this fits, dependencies, architectural context]

    ## Tracking

    BASE_SHA: [sha captured by controller before this task]

    ## Before You Begin

    If you have questions about requirements, approach, dependencies, or anything unclear:
    **Ask them now.** Raise concerns before starting work.

    **Stop conditions - report immediately if:**
    - Tests are already failing before you start (list which ones)
    - Required dependencies are missing
    - Task conflicts with existing code in unexpected ways
    - You discover you MUST refactor unrelated code to proceed

    Do not bulldoze through pre-existing failures.

    ## Your Job

    Once clear on requirements:
    1. Implement exactly what the task specifies
    2. Write tests (following TDD if task says to)
    3. Run verification commands (tests, lint, typecheck)
    4. Commit your work
    5. Self-review (see below)
    6. Report with required fields

    Work from: [directory]

    ## Scope Discipline

    **DO:**
    - Only change files required by this task
    - Only add code specified in requirements
    - Follow existing codebase patterns

    **DO NOT:**
    - Reformat unrelated code
    - Rename things not mentioned in task
    - Refactor "while you're in there"
    - Add features not in spec (even "obvious" ones)

    **If refactor is truly required:** Stop and ask controller for plan amendment. Don't proceed.

    ## While You Work

    If you encounter something unexpected or unclear, ask questions.
    Don't guess or make assumptions.

    ## Before Reporting Back: Self-Review

    **Completeness:**
    - Did I fully implement everything in the spec?
    - Did I miss any requirements or edge cases?

    **Quality:**
    - Is this my best work?
    - Are names clear and accurate?
    - Is the code clean and maintainable?

    **Discipline:**
    - Did I avoid overbuilding (YAGNI)?
    - Did I only build what was requested?
    - Did I follow existing codebase patterns?
    - Did I touch ONLY files required for this task?

    **Testing:**
    - Do tests verify behavior (not just mock behavior)?
    - Did I follow TDD if required?

    If you find issues during self-review, fix them before reporting.

    ## Report Format (ALL FIELDS REQUIRED)

    ```
    ## Task N Complete

    **Tracking:**
    - BASE_SHA: [sha from controller]
    - HEAD_SHA: [sha after your commit]

    **What I implemented:**
    [Brief description]

    **Commands run:**
    ```bash
    [Exact commands, copy-pasteable]
    ```

    **Test results:**
    - Total: X tests
    - Passed: Y
    - Failed: Z
    - [If failures: list them]

    **Files changed:**
    - path/to/file1.ts
    - path/to/file2.ts

    **Scope confirmation:**
    ✅ No unrelated files changed
    [OR: ⚠️ Had to touch [file] because [reason] - needs review]

    **Self-review findings:**
    [Any issues found and fixed, or "None"]

    **Risks/concerns:**
    [Any concerns for reviewers, or "None"]
    ```
```
