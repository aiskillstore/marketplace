# Omakase-Off Detailed Workflow

## Skill Dependencies

This skill orchestrates other skills. Check what's installed and use fallbacks if needed.

| Reference | Primary (if installed) | Fallback (if not) |
|-----------|------------------------|-------------------|
| `brainstorming` | `superpowers:brainstorming` | Ask questions one at a time, propose 2-3 approaches, validate incrementally |
| `writing-plans` | `superpowers:writing-plans` | Write detailed plan with file paths, code examples, verification steps |
| `git-worktrees` | `superpowers:using-git-worktrees` | `git worktree add .worktrees/<name> -b <branch>`, verify .gitignore |
| `parallel-agents` | `superpowers:dispatching-parallel-agents` | Dispatch multiple Task tools in single message, review when all return |
| `subagent-dev` | `superpowers:subagent-driven-development` | Fresh subagent per task, code review between tasks |
| `tdd` | `superpowers:test-driven-development` | Write test first, watch fail, write minimal code, refactor |
| `scenario-testing` | `scenario-testing:skills` (2389) | Create `.scratch/` E2E scripts, real dependencies, no mocks |
| `verification` | `superpowers:verification-before-completion` | Run verification command, read output, THEN claim status |
| `fresh-eyes` | `fresh-eyes-review:skills` (2389) | 2-5 min review for security, logic errors, edge cases |
| `judge` | `test-kitchen:judge` | Scoring framework with checklists (MUST invoke at Phase 4) |
| `code-review` | `superpowers:requesting-code-review` | Dispatch code-reviewer subagent with SHA range |
| `finish-branch` | `superpowers:finishing-a-development-branch` | Verify tests, present options (merge/PR/keep/discard) |

**At skill start:** Announce which dependencies are available.

## Phase 0: Entry Point

**When user requests "build/create/implement X":**

Present the choice BEFORE starting detailed brainstorming:
```
Before we dive into the details, how would you like to approach this?

1. Brainstorm together - We'll explore requirements and design step by step
2. Omakase (chef's choice) - I'll generate 3-5 best approaches, implement
   them in parallel, and let tests pick the winner
```

**If user picks Omakase (option 2):**
1. Quick context gathering (1-2 essential questions only)
2. Generate 3-5 distinct architectural approaches
3. Jump directly to Phase 2 (Plan Generation)

**If user picks Brainstorm (option 1):**
Continue to Phase 1.

## Phase 1: Brainstorming with Passive Slot Detection

**First, check if a brainstorming skill is available:**
- If available → invoke it and passively detect indecision during the flow
- If NOT available → do brainstorming yourself using fallback behavior

**During brainstorming, passively detect indecision:**

**Detection signals:**
- Explicit: "slot", "try both", "explore both"
- Uncertain: "not sure", "hmm", "either could work", "both sound good"
- Deferring: "you pick", "whatever you think"

**Slot classification:**
| Type | Examples | Worth exploring? |
|------|----------|------------------|
| **Architectural** | Storage engine, framework, auth method, API style | Yes |
| **Trivial** | File location, naming conventions, config format | No |

Only architectural decisions become real slots.

**Fast path detection:**
After 2+ uncertain answers in a row:
```
You seem flexible on the details. Want me to:
1. Make sensible defaults and you flag anything wrong
2. Continue exploring each decision
```

## Phase 1.5: End-of-Brainstorm Decision

**If NO architectural slots were collected:**
Hand off to cookoff for implementation.

**If slots WERE collected:**
```
I noticed some open decisions during our brainstorm:
- Storage: JSON vs SQLite
- Auth: JWT vs session-based

Would you like to:
1. Explore in parallel - I'll implement both variants and let tests decide
2. Best guess - I'll pick what seems best and proceed with one plan
```

**Combination limits (max 5-6 implementations):**

When multiple slots exist, don't do full combinatorial explosion. Instead:
1. **Identify the primary axis** - Which slot has the biggest architectural impact?
2. **Create variants along that axis** - Each variant explores a different primary choice
3. **Fill in secondary slots** with the most natural pairing

## Phase 2: Plan Generation

For each variant combination:

1. Generate full implementation plan using `writing-plans`
2. Store in structured directory:

```
docs/plans/<feature>/
  design.md                  # Shared context from brainstorming
  omakase/
    variant-<slug-1>/
      plan.md                # Implementation plan for this variant
    variant-<slug-2>/
      plan.md
    result.md                # Final report (written at end)
```

## Phase 3: Implementation

**Setup worktrees:**
- Worktree location: `.worktrees/`
- Branch naming: `<feature>/omakase/<variant-name>`
- All worktrees created before implementation starts

**CRITICAL: Dispatch ALL variants in a SINGLE message**

```
<single message>
  Task(variant-json, run_in_background: true)
  Task(variant-sqlite, run_in_background: true)
</single message>
```

**Subagent workflow:**
1. Read their variant's plan
2. Execute tasks using `subagent-dev`
3. Follow `tdd` - write test first, watch fail, implement, pass
4. Use `verification` - run tests, read output, THEN claim complete
5. Report back: summary, test counts, files changed, issues

## Phase 4: Evaluation

**Step 1: Scenario testing (REQUIRED)**
- MUST use `scenario-testing` - not manual verification
- Same scenarios run against ALL variants
- Must pass all scenarios to be a "survivor"

**Step 2: Fresh-eyes review on survivors**
For each variant that passed scenarios, use `fresh-eyes`.

**Step 3: Elimination**
| Situation | Action |
|-----------|--------|
| Fails tests | Eliminated |
| Fails scenarios | Eliminated |
| Critical security issue | Eliminated |
| All fail | Report failures, ask user how to proceed |
| One survives | Auto-select |

### Step 4: Invoke Judge Skill

**CRITICAL: Invoke `test-kitchen:judge` now.**

The judge skill contains the full scoring framework with checklists. Invoking it fresh ensures the scoring format is followed exactly.

```text
Invoke: test-kitchen:judge

Context to provide:
- Variants to judge: variant-a, variant-b (or however many)
- Worktree locations: .worktrees/variant-<name>/
- Test results from each variant
- Fresh-eyes findings from Step 2
- Feasibility flags identified
```

The judge skill will:
1. Fill out the complete scoring worksheet for each variant
2. Build the scorecard with integer scores (1-5, no half points)
3. Check hard gates (Fitness Δ≥2, any score=1)
4. Announce winner with rationale

**Do not summarize or abbreviate the scoring.** The judge skill output should be the full worksheet.

**Omakase-specific context:** In omakase, different variants represent different *approaches* to solving the problem. A Fitness gap (Δ≥2) means one approach genuinely solves the problem better - this is a legitimate win, not a design deviation.

## Phase 5: Completion

**Winner:** Use `finish-branch`
- Verify all tests pass
- Present options: merge locally, create PR, keep as-is, discard
- Execute user's choice

**Losers:** Cleanup
```bash
git worktree remove <worktree-path>
git branch -D <feature>/omakase/<variant>
```

**Write result.md:**
```markdown
# Omakase-Off Results: <feature>

## Variants
| Variant | Tests | Scenarios | Fresh-Eyes | Result |
|---------|-------|-----------|------------|--------|
| variant-json | 12/12 | PASS | 0 issues | WINNER |
| variant-sqlite | 15/15 | PASS | 1 minor | eliminated |

## Winner Selection
Reason: [Why this variant won]

## Cleanup
Worktrees removed: N
Branches deleted: [list]
```

## Common Mistakes

**Too many slots**
- Problem: Combinatorial explosion
- Fix: Cap at 5-6, ask user to constrain if exceeded

**Ad-hoc scenario testing**
- Problem: Manual verification instead of real scenario tests
- Fix: MUST use `scenario-testing` skill

**Forgetting cleanup**
- Problem: Orphaned worktrees and branches
- Fix: Always cleanup losers, write result.md
