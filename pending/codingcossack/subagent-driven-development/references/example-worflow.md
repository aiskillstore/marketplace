# Example Workflow

Complete walkthrough of subagent-driven development with SHA tracking.

```
You: I'm using Subagent-Driven Development to execute this plan.

[Read plan file once: docs/plans/feature-plan.md]
[Extract all 5 tasks with full text and context]
[Capture current HEAD: abc1234]
[Create task list with all tasks]

State: { tasks: [1,2,3,4,5], base_sha: "abc1234" }

═══════════════════════════════════════════════════════════
Task 1: Hook installation script
BASE_SHA: abc1234
═══════════════════════════════════════════════════════════

[Dispatch implementer with full task text + context + BASE_SHA: abc1234]

Implementer: "Before I begin - should the hook be installed at user or system level?"

You: "User level (~/.config/superpowers/hooks/)"

Implementer: "Got it. Implementing now..."

[Later] Implementer Report:
  BASE_SHA: abc1234
  HEAD_SHA: def5678
  What I implemented: install-hook command with --force flag
  Commands run: npm test -- --grep "install-hook"
  Test results: 5/5 passing
  Files changed: src/commands/install-hook.ts, tests/install-hook.test.ts
  Scope confirmation: ✅ No unrelated files changed
  Self-review: Found I missed --force flag, added it before committing

[Update state: task 1 head_sha = def5678, status = spec_review]

[Dispatch spec reviewer with requirements + diff(abc1234..def5678)]

Spec reviewer:
  Reviewed: git diff abc1234..def5678
  ✅ Spec compliant - all requirements met, no extras

[Update state: task 1 status = quality_review]

[Dispatch code quality reviewer with BASE_SHA: abc1234, HEAD_SHA: def5678]

Code reviewer:
  Reviewed: git diff abc1234..def5678
  Strengths: Good test coverage, clean implementation
  Issues: None
  Verification: Commands plausible, test count matches
  ✅ Approved

[Update state: task 1 status = complete]

═══════════════════════════════════════════════════════════
Task 2: Recovery modes
BASE_SHA: def5678 (= Task 1's HEAD_SHA)
═══════════════════════════════════════════════════════════

[Dispatch implementer with full task text + context + BASE_SHA: def5678]

Implementer: [No questions, proceeds]

Implementer Report:
  BASE_SHA: def5678
  HEAD_SHA: ghi9012
  What I implemented: verify/repair modes, --json flag
  Commands run: npm test
  Test results: 8/8 passing
  Files changed: src/commands/recovery.ts, tests/recovery.test.ts
  Scope confirmation: ✅ No unrelated files changed

[Update state: task 2 head_sha = ghi9012, status = spec_review]

[Dispatch spec reviewer with requirements + diff(def5678..ghi9012)]

Spec reviewer:
  Reviewed: git diff def5678..ghi9012
  ❌ Issues found:

  Missing requirements:
  - "Progress reporting every 100 items": Not implemented
    - Expected: Console output every 100 items processed
    - Location: Should be in src/commands/recovery.ts

  Extra/unneeded work:
  - src/commands/recovery.ts:45: --json flag added
    - Not in spec. Remove or get spec amended.

[Implementer fixes: removes --json, adds progress reporting]

Implementer: Fixed. New HEAD_SHA: jkl3456

[Update state: head_sha = jkl3456, spec_review_cycles = 1]

[Spec reviewer re-reviews diff(def5678..jkl3456)]

Spec reviewer:
  ✅ Spec compliant now

[Update state: task 2 status = quality_review]

[Dispatch code quality reviewer with BASE_SHA: def5678, HEAD_SHA: jkl3456]

Code reviewer:
  Reviewed: git diff def5678..jkl3456
  Strengths: Solid implementation
  Issues:
    Important: src/commands/recovery.ts:67 - Magic number (100)
      - Why: Unexplained constant, hard to maintain
      - Fix: Extract to PROGRESS_INTERVAL constant

[Implementer fixes: extracts constant]

Implementer: Fixed. New HEAD_SHA: mno7890

[Update state: head_sha = mno7890, quality_review_cycles = 1]

[Code quality reviewer re-reviews diff(def5678..mno7890)]

Code reviewer:
  ✅ Approved

[Update state: task 2 status = complete]

═══════════════════════════════════════════════════════════
...Tasks 3-5 follow same pattern...
═══════════════════════════════════════════════════════════

Final state:
  Task 1: complete, abc1234 → def5678
  Task 2: complete, def5678 → mno7890, 1 spec cycle, 1 quality cycle
  Task 3: complete, mno7890 → pqr1234
  Task 4: complete, pqr1234 → stu5678
  Task 5: complete, stu5678 → vwx9012

[Dispatch final code reviewer for entire implementation]
  BASE_SHA: abc1234 (initial)
  HEAD_SHA: vwx9012 (final)

Final reviewer:
  Reviewed: git diff abc1234..vwx9012
  All requirements met across all tasks
  No cross-cutting issues
  ✅ Ready to merge

[Use finishing-a-development-branch skill]

Done!
```

## Key Observations

1. **SHA tracking is systematic:** Every task starts with BASE_SHA, ends with HEAD_SHA
2. **State is explicit:** Controller tracks exact SHAs and review cycles
3. **Reviewers use diffs:** Never "the repo", always diff(base..head)
4. **Fixes update HEAD_SHA:** Each fix creates new commit, new SHA to track
5. **Final review spans full range:** First BASE_SHA to final HEAD_SHA
6. **Review cycles counted:** Useful for identifying problematic tasks
