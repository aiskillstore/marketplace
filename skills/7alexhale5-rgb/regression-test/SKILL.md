---
name: regression-test
description: Manage golden dataset regression tests for LLM prompts using Promptfoo. Commands — init, add, run, report. Use when user says "regression", "golden dataset", "prompt regression", "eval run", "test my prompts", or after shipping prompt changes.
---

# Regression Test: Golden Dataset Management

Manage golden test datasets for LLM prompt regression testing using Promptfoo. Ensures prompt changes don't degrade output quality.

One eval tells you today's score. A kept set tells you what your change did. There is a recorded
three-run walkthrough of exactly that, runnable with no API key, at
https://github.com/7alexhale5-rgb/alexhale-skills/tree/main/example

**Prerequisite:** `npm install -g promptfoo` (check with `which promptfoo`)

---

## Commands

### `/regression-test init`

Scaffold regression testing infrastructure in the current project.

1. Create directory structure:
   ```bash
   mkdir -p .promptfoo/golden
   ```

2. Generate `.promptfoo/promptfooconfig.yaml` (the path matters: `tests: "golden/*.yaml"` below resolves relative to this file, and `/regression-test run` looks for it here):
   ```yaml
   description: "Golden dataset regression tests"
   # Without this, promptfoo has no prompt to send and every case scores an empty string.
   # The vars come from the golden files that `/regression-test add` writes.
   prompts:
     - |
       [{"role":"system","content":"{{system_prompt}}"},{"role":"user","content":"{{user_input}}"}]
   providers:
     - id: anthropic:messages:claude-sonnet-5
       config:
         temperature: 0
   tests: "golden/*.yaml"
   defaultTest:
     assert:
       - type: llm-rubric
         value: "Output should match the expected behavior described in the test case"
   ```

3. Add `.promptfoo/results/` to `.gitignore` if not already present. Ignore the results, commit the goldens: a golden dataset nobody else can see is not a shared baseline, and the whole point is that your teammates and your CI run the same cases you do. If a prompt in a golden case is genuinely sensitive, keep that one case out of the repo rather than hiding the dataset.

4. Report: "Initialized `.promptfoo/golden/` — run `/regression-test add <name>` to capture test cases."

---

### `/regression-test add <name>`

Capture a prompt+response pair as a golden test case.

1. Parse `<name>` from user input (slug format, e.g., `auth-flow`, `error-handling`)

2. Prompt user for:
   - **System prompt** (or detect from current project's CLAUDE.md/skill)
   - **User input** (the test prompt)
   - **Expected behavior** (natural language description of good output)
   - **Vars** (optional template variables)

3. Write golden test case:
   ```yaml
   # .promptfoo/golden/{name}.yaml
   - description: "{name}"
     vars:
       system_prompt: |
         {system prompt content}
       user_input: |
         {user input}
     assert:
       - type: llm-rubric
         value: |
           {expected behavior description}
       - type: not-contains
         value: "error"
   ```

4. Report: "Added golden test `{name}` — {N} total test cases."

---

### `/regression-test run`

Execute Promptfoo evaluation against all golden datasets.

1. Check prerequisites:
   ```bash
   which promptfoo 2>&1  # must return path
   ls .promptfoo/golden/*.yaml 2>/dev/null | wc -l  # must be > 0
   ```

2. Run evaluation:
   ```bash
   cd {project_root}
   promptfoo eval --config .promptfoo/promptfooconfig.yaml \
     --output .promptfoo/results/eval-$(date +%Y%m%d-%H%M%S).json \
     --no-cache 2>&1
   ```

3. Parse results JSON:
   - Count PASS/FAIL per test case
   - Extract failure details (expected vs actual)

4. Report:
   ```
   Regression Test Results
   ├─ Total: {N} test cases
   ├─ Pass: {N} ({%})
   ├─ Fail: {N} ({%})
   └─ Duration: {N}s

   Failures:
   - {test_name}: {assertion_type} — expected "{expected}", got "{actual}"
   ```

5. If all pass: "All golden tests pass — safe to ship."
   If failures: "Regressions detected — review before shipping."

---

### `/regression-test report`

Show regression trends over the last 5 evaluations.

1. Read result files:
   ```bash
   ls -t .promptfoo/results/eval-*.json | head -5
   ```

2. For each result file, extract:
   - Date (from filename)
   - Pass/fail counts
   - Any new failures vs previous run

3. Report:
   ```
   Regression Trends (last 5 evals)
   ├─ 2026-03-31 14:30: 12/12 PASS ✓
   ├─ 2026-03-30 09:15: 11/12 PASS (1 fail: auth-flow)
   ├─ 2026-03-29 16:45: 12/12 PASS ✓
   ├─ 2026-03-28 11:00: 10/12 PASS (2 fail)
   └─ 2026-03-27 08:30: 12/12 PASS ✓

   Trend: STABLE (4/5 clean)
   ```

---

## Where to wire it in

The value shows up when the run is automatic, not when you remember to type it.

| Moment | What to do |
|--------|------------|
| After changing any prompt | `/regression-test run` before you commit. This is the one that catches most regressions. |
| Before a release | Run it in CI and fail the build on a new failure. `promptfoo eval` returns non-zero when an assertion fails. |
| After a model or version change | Re-run the whole set. A provider upgrade is a silent prompt change. |
| Weekly, on a schedule | `/regression-test report` to see whether quality is drifting rather than breaking. |

If your agent harness supports hooks or a pre-commit step, put the run there. A check that depends on discipline is a check you will lose.

---

## Graceful Degradation

| Component | If Missing | Fallback |
|-----------|-----------|----------|
| promptfoo CLI | Not installed | Prompt user: `npm install -g promptfoo` |
| .promptfoo/ directory | Not initialized | Prompt: `/regression-test init` |
| Golden datasets | No .yaml files | Skip with note: "No golden tests — add with `/regression-test add`" |
| Results directory | Missing | Create on first `run` |
