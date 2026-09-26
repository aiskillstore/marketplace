---
name: cc-best-practices
description: "Guidance on how to use Claude Code effectively — covering context management, verification strategies, the explore-plan-implement workflow, prompting techniques, session management, parallel sessions, and common failure patterns. Use this skill whenever the user asks how to get the most out of Claude Code, how to write better prompts, how to manage context, when to use plan mode, how to automate tasks, or when they describe a frustrating pattern like Claude repeating mistakes or losing track of instructions."
---

---

# Claude Code Best Practices

Based on the official Anthropic documentation at https://code.claude.com/docs/en/best-practices.

The single most important constraint: **Claude's context window fills up fast,
and performance degrades as it fills.** Every best practice flows from this.

---

## Instructions

### Step 1: Always give Claude a way to verify its work

Provide a runnable check (test suite, build exit code, linter, diff script) so Claude can confirm success independently. Ask for **evidence** (test output, command result), not just assertions.

### Step 2: Use the Explore → Plan → Implement workflow for non-trivial tasks

Enter `/plan` mode, let Claude read the codebase first, then draft a plan before writing any code. Exit plan mode to implement. Skip this only for small, obvious changes.

### Step 3: Write specific, scoped prompts

Name files (`@filename`), describe symptoms rather than guesses, reference existing patterns. Vague prompts produce vague results.

### Step 4: Keep CLAUDE.md short and actionable

Include only what Claude cannot infer from the code. Every line should answer: "Would removing this cause Claude to make mistakes?" If not — cut it.

### Step 5: Manage context aggressively

Use `/clear` between unrelated tasks. After two failed corrections on the same issue: clear and write a better prompt. Use `/compact <hint>` to compact with focus.

### Step 6: Use subagents for investigation and review

Let subagents explore unfamiliar code or review your implementation — they run in a fresh context without bias toward the code they just wrote.

---

## Examples

### Example 1: Implementing a feature correctly

User says: "I keep getting flaky results when I ask Claude to implement something"

Actions:

1. Add a verification step to the prompt: "write a validateEmail function — run the existing test suite after implementing, show me the output"
2. If no tests exist: "write the function AND write tests for it, run them, show results"
3. Set a Stop hook to block turn completion until tests pass

Result: Claude iterates until tests pass instead of stopping when the code _looks_ done.

### Example 2: Tackling a complex, multi-file change

User says: "How should I approach a big refactor across 10 files?"

Actions:

1. Enter `/plan` mode — Claude explores without making changes
2. Ask: "read the affected files and write a step-by-step implementation plan"
3. Edit the plan directly with `Ctrl+G` if needed
4. Exit plan mode — Claude implements and commits per the plan
5. Run a subagent to review the diff in a fresh context

Result: Structured refactor with a reviewable plan, no context-thrashing from mixed explore/write turns.

### Example 3: Claude keeps repeating the same mistake

User says: "I've corrected Claude 3 times on the same issue and it keeps doing it wrong"

Actions:

1. Run `/clear` — start a fresh context
2. Identify what was missing from the original prompt (missing constraint, missing example, ambiguous scope)
3. Write a new initial prompt that includes the constraint explicitly: "IMPORTANT: do not use mocks in these tests — use real database connections"
4. Add the constraint to CLAUDE.md if it applies project-wide

Result: Clean session with a better-specified prompt outperforms a long session with accumulated corrections.

---

---

## 1. Give Claude a way to verify its work

Claude stops when the work _looks_ done. Without a runnable check, you become
the verification loop. Provide something that returns a pass/fail signal Claude
can read: a test suite, a build exit code, a linter, a script that diffs output.

- Ask Claude to run the check and iterate in the same prompt.
- Set `/goal` conditions for multi-turn verification.
- Use a **Stop hook** to block the turn from ending until a script passes.
- Use a **verification subagent** so the reviewer has a fresh context.

Ask Claude to show **evidence** (test output, command result, screenshot) rather
than just asserting success.

**Example upgrade:**

> Before: _"implement a function that validates email addresses"_
> After: *"write a validateEmail function. test cases: user@example.com → true,
>
> > invalid → false. run the tests after implementing"*

---

## 2. Explore first, then plan, then code

Use **plan mode** (`/plan` or the UI toggle) to separate reading from writing.

1. **Explore** — enter plan mode; Claude reads files without making changes.
2. **Plan** — ask Claude to write a detailed implementation plan. Press `Ctrl+G`
   to open the plan in your editor for direct edits.
3. **Implement** — exit plan mode; Claude codes and verifies against the plan.
4. **Commit** — ask Claude to commit and open a PR.

Skip planning when the scope is clear and the fix is small (typo, rename,
single-line change). Plan mode adds overhead — use it when the change touches
multiple files or you are unfamiliar with the code.

---

## 3. Provide specific context in your prompts

Claude can infer intent but cannot read your mind.

| Strategy             | Vague                                           | Specific                                                                                                              |
| -------------------- | ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Scope the task       | _"add tests for foo.py"_                        | _"write a test for foo.py covering the edge case where the user is logged out. avoid mocks."_                         |
| Point to sources     | _"why does ExecutionFactory have a weird API?"_ | _"look through ExecutionFactory's git history and summarize how its API evolved"_                                     |
| Reference patterns   | _"add a calendar widget"_                       | _"look at HotDogWidget.php as a pattern reference and follow it to implement a calendar widget"_                      |
| Describe the symptom | _"fix the login bug"_                           | _"users report login fails after session timeout. check src/auth/ token refresh. write a failing test, then fix it."_ |

**Rich context techniques:**

- Use `@filename` to reference files directly.
- Paste screenshots or drag images into the prompt.
- Pipe data: `cat error.log | claude`
- Give URLs for documentation (allowlist domains via `/permissions`).

---

## 4. Write an effective CLAUDE.md

CLAUDE.md is read at the start of every session. Keep it **short and
human-readable** — bloated CLAUDE.md files cause Claude to ignore actual
instructions.

**Include:**

- Bash commands Claude cannot guess (e.g., build/test commands)
- Code style rules that differ from language defaults
- Testing instructions and preferred test runners
- Repository etiquette (branch naming, PR conventions)
- Architectural decisions specific to the project
- Developer environment quirks, required env vars
- Common gotchas or non-obvious behaviors

**Exclude:**

- Anything Claude can figure out by reading the code
- Standard language conventions Claude already knows
- Detailed API documentation (link instead)
- Self-evident practices like "write clean code"

For each line: _"Would removing this cause Claude to make mistakes?"_ If not, cut it.

Use `/context` to confirm Claude loaded the file. Use `@path/to/file` imports
in CLAUDE.md to pull in other files selectively.

---

## 5. Manage session context aggressively

- `/clear` — reset context between **unrelated** tasks.
- `/compact <instructions>` — compact with focus (e.g., `/compact Focus on API changes`).
- `Esc + Esc` / `/rewind` — open the rewind menu; restore conversation and/or
  code state to any previous checkpoint.
- `/btw` — ask a quick side-question; answer appears in an overlay and never
  enters conversation history.

**After two failed corrections on the same issue:** run `/clear` and write a
better initial prompt incorporating what you learned. A clean session with a
better prompt outperforms a long session with accumulated corrections.

Customize compaction in CLAUDE.md:

> *"When compacting, always preserve the full list of modified files and any
>
> > test commands"*

---

## 6. Use subagents for investigation and review

Subagents run in their own context window and report back summaries, keeping
your main conversation clean.

```
Use subagents to investigate how our authentication system handles token
refresh, and whether we have any existing OAuth utilities I should reuse.
```

After implementation:

```
use a subagent to review this code for edge cases
```

Use `/code-review` skill for a bug-focused adversarial review of the current diff.

---

## 7. Automate and scale

**Non-interactive mode** — integrate Claude into CI, pre-commit hooks, scripts:

```bash
claude -p "List all API endpoints" --output-format json
claude -p "Analyze this log file" --output-format stream-json --verbose
```

**Fan out across files** — loop through tasks:

```bash
for file in $(cat files.txt); do
  claude -p "Migrate $file from React to Vue. Return OK or FAIL." \
    --allowedTools "Edit,Bash(git commit *)"
done
```

**Parallel sessions** — run multiple Claude sessions with git worktrees so
edits don't collide. Writer/Reviewer pattern:

- Session A implements a feature.
- Session B reviews the diff in a fresh context (no bias toward the code it
  just wrote).

**Auto mode** — uninterrupted execution with background safety checks:

```bash
claude --permission-mode auto -p "fix all lint errors"
```

---

## 8. Common failure patterns and quick reference

For the full failure patterns table, all CLI commands, and non-interactive mode examples, consult `references/commands.md`.
