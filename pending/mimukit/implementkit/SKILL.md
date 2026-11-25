---
name: implementkit
description: >-
  Implement a plan, spec, or issue into working code in straight-through, tests-after, or TDD mode, then run the repo's test and build gate before declaring done. Use when the user says "implement this plan", "implement #42", "do this TDD", "build it, then add tests", "apply these review findings", or "make this failing test pass". It runs attended; the unattended issue-to-PR span is afkkit's.
license: MIT
allowed-tools: Bash, Read, Grep, Glob, Edit, Write, Task, Agent, Skill
metadata:
  internal: false
---

# implementkit

Build a named input into working code and stop at green, unstaged code. It **never commits or stages**; commitkit groups and commits. It **never designs**; a thin input bounces to grillkit or plankit. Tests for code that already runs and was never tested are a retrofit, which belongs to testkit when it is installed.

## Procedure

### 1. Take an explicit input
Require the user to name what to build. The options are a plan file (`docs/plans/NNNN-plan-<slug>-YYYY-MM-DD.md`, or an older one without the `NNNN-` serial), an issue (`#42`, or a URL/id `gh` can fetch), a freeform spec written in the prompt, or a **fix round**. A fix round takes one of two forms: a concrete list of review findings (e.g. the blockers from a review pass), each naming what's wrong and where, or a **failing reproduction test** (e.g. from debugkit) with the cause it proves. Do **not** hunt for an input: if nothing is named, stop and ask what to implement. The one exception is an issue branch. When the prompt names nothing and the current branch matches `issue-<n>-<slug>` (the shape gitkit gives a worktree started from an issue), take issue `#<n>` as the named input and say the branch supplied it. Any other branch shape still stops and asks. Read the named input in full (for an issue, fetch it with `gh issue view <n>`; if `gh` isn't available, ask the user to paste it). The step is done when the whole input has been read, or the run has stopped to ask for it.

**A plan or an issue may be narrowed to one phase** ("implement phase 3 of `0007-plan-sso-2026-07-23.md`", "implement phase 2 of #42"). Both carry their phases as headings, so a narrowed run builds that phase and leaves the rest alone. Read the whole document either way: the phases above the named one say what the code may already assume, and the ones below say what it must not.

### 2. Assess implementability, bounce if thin
Before writing anything, judge whether the input is concrete enough to build without inventing the design. A hardened plan or a fleshed-out issue passes.

**Read a plan's own hardening signals.** A `Grilled: YYYY-MM-DD` line directly under the title means the plan survived a grill. An absent line means it is ungrilled, either never grilled or edited materially since, because a material edit deletes the line. Then read its `## Open questions` section. Warn the user when the plan is ungrilled or the section holds an entry, and name each open question. An open question that the phase in scope depends on is a gap, so bounce on it. The others stay warnings, and the build goes on. A bare title, a one-line ask, or a spec with unresolved core decisions does **not**. Stop and tell the user to harden it first with grillkit (to interrogate the decisions) or plankit (to draft a proper plan), naming the specific gaps you hit.

**Thin for a different reason gets a different route.** When the input is unsettled because *nobody has seen the design work* (the state model looks fine on paper, the screen has never been laid out), no amount of interrogation settles it, because the missing input is evidence rather than a decision. That routes to prototypekit when it's installed, or to a deliberate throwaway spike otherwise; it comes back here once the question is answered.

A **fix round clears this bar**, because the findings or the red test name the defect, so there is no design to invent; never bounce one as thin. Clearing the bar is not passing: a fix round runs the full [done-gate](#5-run-the-done-gate) like any other run. It also skips mode resolution below: apply the named fixes directly in the style the surrounding code already shows.

**A reproduction-test fix round keeps the test as its proof.** Run the test first and confirm it fails as the cause predicts. When it passes before any fix, stop and report that it no longer reproduces. Never delete, skip, or weaken the test. The fix is done when that test passes at the done-gate, next to the rest of the suite.

The step is done when the input has passed with every warning stated, or has bounced with each gap named.

### 3. Resolve the mode
Pick **straight-through**, **tests-after**, or **TDD** by this precedence, taking the first tier that gives an answer:

1. **Prompt.** The user said so ("do this TDD", "build it, then add tests", "just write it, no tests"). Explicit always wins.
2. **Agent instructions.** The repo's agent-guide file (`CLAUDE.md` or an equivalent) declares a mode or a test-first policy. Honor it.
3. **Repo habit.** Infer from the codebase. Conclude **TDD only when both** are true: (a) real test infrastructure exists (a runner/config like jest, vitest, pytest, `go test`, rspec, cargo test), **and** (b) the repo actually ships tests with features, so recent commits touch test and source files together, and the test-to-source ratio is healthy. Infra with no habit (a lonely config, tests that lag far behind the code) is **not** TDD.
4. **Ask once.** Still unresolved and a user is there to answer? Ask a single time which of the three modes to use. Non-interactive (a delegated/autonomous run with no one to answer)? Default to **straight-through**, since both test modes are heavier and are never imposed silently. State which mode you resolved and why.

### 4. Build in the resolved mode

**A long build runs as a conductor.** When the scope holds more than one heavy phase (one that needs a fresh context of its own), or one mechanical bulk phase such as a vendored port or a large lint sweep, this thread builds none of it. Every tool call re-bills the whole context, so each phase built inline taxes every phase after it. Instead:

- Group the phases: a heavy phase stands alone, and consecutive light phases share a group.
- Dispatch one subagent per group, in order, with the host's subagent tool (`Agent` on Claude Code, formerly `Task`; `spawn_agent` on Codex; checked 2026-11-16). Its brief carries the paths it touches, the signatures of the shared APIs it calls, the resolved mode, the phase's acceptance items, and the phase-gate commands, so it reads nothing this thread already read.
- The subagent builds and runs the **phase gate** under [Tool rules](#tool-rules): the repo's own typecheck and lint commands, and its test command limited to the packages the group changed (the affected test files in a single-package repo), each once into a log. These are the repo's own commands for each check, from its agent-guide file or its scripts, and the brief names each one. It never runs the full suite, and never a declared gate command such as `make check` that runs it. The brief carries this line in these words, because a subagent follows the brief and not this file. The subagent writes its notes and logs to a file and returns a short result: pass or fail, the files changed, the phase-gate result, and that file's path.
- The conductor edits no code. It reads each result, dispatches the next group, then runs the [done-gate](#5-run-the-done-gate) over the whole tree, never per group, and handles a red gate by [Fix on red](#6-fix-on-red-bounded). A full suite in every subagent repeats that gate once per group and loads the machine until the suite flakes.
- A group whose subagent returns interrupted or errored gets one new subagent with the same brief, told to read `git diff` first and finish the group. A second failure stops the build and reports both.

When afkkit is installed, its **Dispatch rules** section holds the full brief rules: a new agent, never a fork, inputs by path, the command rules, and the recovery of a broken dispatch. On a host with no subagent tool, build the groups inline in order and say so.

Follow [Tool rules](#tool-rules) for every command and every file write, inline or delegated.

**Straight-through.** Implement the production code to satisfy the input. Write **no new tests**; run the existing suite as part of the gate ([Run the done-gate](#5-run-the-done-gate)).

**Tests-after.** Implement the production code first, as in straight-through. Then write one focused test per behavior the input names. **Watch each test fail before you keep it:** make a small semantic break in the code it covers (flip a comparison, change a returned value), run the test, see it go red, and reverse the break. A test that stays green under its break tests nothing, so rewrite or delete it. Reverse each break by undoing your own edit, never by restoring a file that also holds other changes.

**TDD.** Per slice of behavior, write one test and see it fail, write the minimal code to pass it, then refactor while the suite stays green.

Repeat per slice until the input is fully implemented. Match the surrounding code's conventions, naming, and structure in every mode, reusing what exists rather than reinventing it.

The step is done when every requirement in scope has code, and, in tests-after and TDD, every named behavior has a test that was observed red.

**Visual surfaces delegate.** When the work includes UI (a page, a component, a screen) and **uikit** is installed, apply it to those files instead of writing them blind; it carries the project's design constraint and runs its own visual pre-flight. Without it, write the UI directly. implementkit keeps everything else either way: the input contract, the mode resolved above, and the done-gate below, which remains the **only** gate. uikit returns to implementkit without a hand-off of its own, so implementkit's [hand-off](#8-hand-off-to-commitkit) is the only one the user sees.

**Check as you go.** Typecheck and run the affected test file per slice. Save the full suite and the build for the [done-gate](#5-run-the-done-gate).

### 5. Run the done-gate
Run the repo's **test** command and its **build / typecheck** command, plus **lint** if the repo runs one. **A gate command the repo's agent-guide file (`CLAUDE.md` or an equivalent) declares, such as `make check`, is the done-gate**: run it in place of those commands.

**Run each gate command once, into a log file**, then print its exit code and a bounded tail or grep of the log:

```sh
log="${TMPDIR:-/tmp}/gate-lint.log"; pnpm lint >"$log" 2>&1; echo "exit $?"; tail -n 40 "$log"
```

**Green checks are not the whole bar.** An existing suite can pass while the new requirement goes untested. List each acceptance item of the input: a plan phase's `Done when:` line, an issue's acceptance criteria, each review finding, or the reproduction test. Give each one its evidence, such as a test name, a command and its output, or a file and line. Report an item with no evidence as **unverified**, never as done.

The step is done when every command has run green and every acceptance item has its evidence or its `unverified` mark.

### 6. Fix on red, bounded
If the gate fails, fix your own output and re-run the gate. A conductor still edits no code: each fix is one new subagent, briefed as a group's subagent is, with the packages of the failing checks as its scope, those checks as its acceptance items, and the gate's log path as its evidence, and the conductor re-runs the gate when it returns. An errored fix subagent counts as a failed fix. A build with no conductor, including one on a host with no subagent tool, fixes inline. After three failed fixes, stop and report red, with what you tried and where it is stuck.

### 7. Stamp the plan, when the input was one
Skip this step entirely unless the input was a plan file and the gate passed. Then mark what you built, so the plan says what is left.

**Check the phase's `Done when:` line first, when it has one.** Run or inspect the observable it names, and report the result. Stamp the phase only when the observable holds. When it fails, leave the heading unstamped and report the phase as built but not done. When it cannot be checked here (it needs a deploy or a person), stamp the phase and report the observable as unchecked.

Append `(built YYYY-MM-DD)` to the heading of each phase you finished, using today's date:

```markdown
### Phase 2: auth (built 2026-08-20)
### Phase 3: session refresh (#41) (built 2026-08-20)
```

Three rules keep the stamp honest:

- **Stamp only the phases you actually built.** A run narrowed to one phase stamps that phase and leaves every other heading untouched. Never stamp a phase you skipped, and never stamp the whole plan because most of it is done.
- **Keep an existing `(#41)` and add yours after it.** The two annotations coexist: the number says where the phase is tracked, the stamp says it is done.
- **Leave the edit unstaged**, like every other change in the run, so commitkit picks up the plan alongside the code that implements it.

### 8. Hand off to commitkit

_Write this section in the procedural register: one instruction per sentence, active voice, present tense, no metaphor._

Leave every change **unstaged**. Do not `git add`, do not commit, do not draft a commit message (that's commitkit's job, and pre-staging fights its grouping). Report a short summary:

- the **mode** used and which precedence tier decided it,
- the **files** created and changed,
- the **gate result** (which commands ran and that they passed),
- each **acceptance item** with its evidence, and each item marked `unverified`,
- for a reproduction-test fix round, the **test path**, seen red before the fix and green after,
- each **plan warning** (ungrilled, open questions) that the build went ahead with,
- the **phases stamped**, each `Done when:` result, and which phases of that plan are still unbuilt,
- each **phase group** a subagent built, with its result file,
- each **process** the run started, and that it is stopped.

Then crown one next move: commit the work with commitkit when installed, otherwise group the changes and commit each group with `git add <files>` and `git commit`. Don't run it yourself. Name the runners-up in this order:

1. Review the agent's work with reviewkit before committing, when installed, otherwise read the diff yourself.
2. When the build touched a UI surface, look at it with verifykit `show` when installed, otherwise open the app and look.

Name the next phase of the plan when one is left. Say the plan is fully built when none is.

## Tool rules

- **Edit for exact changes.** Use Edit for a small, exact change. When a script writes files (a codemod, `sed -i`, a heredoc), the same command runs the repo's formatter on those files and prints the changed lines (`git diff --stat`, or `git diff -U0` on the files), so a bad pattern shows at once, not at the gate.
- **Commands that run in zsh and bash alike.** Quote every glob argument (`--include='*.tsx'`, `'pkg@*'`). Iterate a file list with `printf '%s\n' … | while IFS= read -r f; do …; done` or `xargs`, never `for f in $files`. zsh does not split an unquoted variable, and it stops on a glob that matches nothing.
- **Long-running processes by PID.** Start a dev server with the repo's own start and stop scripts when it has them. Otherwise start it in the background with its output to a log and its PID in a file. A package-manager wrapper can exit while its child keeps the port, so check the port (`curl -sf`, `lsof -ti :<port>`), not the wrapper's exit, to know whether the server runs. Before the hand-off, stop each process you started by its PID or by the PID on its port, and confirm the port is free.
- **Browser checks read facts first.** When a browser tool checks UI, read facts with an evaluate call (text, a computed style, an element count) before anything else. Take a snapshot with no image by default. Use an image only for a visual decision, and save it to a file when the user must see it.

## Notes

- Invoke uikit for UI files only; invoke no other skill.
- No filesystem or shell (e.g. a browser-based agent)? Then you can't write files or run the gate. Instead print the finished code as fenced blocks (one per file, with its path) for the user to save, note the mode you'd use, and list the gate commands they should run themselves.
