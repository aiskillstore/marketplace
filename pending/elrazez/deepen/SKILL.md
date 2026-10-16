---
name: deepen
description: Use when the user says /deepen or wants a deeper prompt.
license: MIT
metadata:
  version: "1.0.0"
  homepage: "https://github.com/elrazez/deepen"
  opencode/slash: "true"
---

# Deepen a task before doing it

Rewrites a task into a deeper prompt before any work starts. It does not do the task.

## When to use

The user writes `/deepen <task>` (`$deepen <task>` in Codex), "deepen this", or asks for a deeper
or sharper version of a prompt before work starts. Any field: code, writing, research, data, ops,
design. The task is whatever follows the command; in Claude Code it may arrive as `ARGUMENTS:`.
If no task is given, ask for it in one line and stop.

Not for tasks the user wants done now. This skill only rewrites the prompt.

## Procedure

1. Do not start the task.
2. If the current project has its own version of this skill or a doc naming its key sources,
   tools and checks (for example `.claude/skills/deepen/SKILL.md` or `.agents/skills/deepen/SKILL.md`
   inside the repo), read it and use those.
3. Look at the real sources only as much as needed to make the answers concrete: a few reads or
   searches, no long research. With no file or web access, work from what the user gave and name
   the sources the rewritten prompt should pull.
4. Answer four questions for this task, at most 3 bullets each:
   1. What would a top professional in this field do here that the user is not asking for?
   2. What is the rawest material they would start from, instead of what has already been
      digested? Name exact files, data, primary sources or measurements.
   3. Which specific methods and tools would they use? Prefer the tools actually available in
      this environment (its built-in tools, MCP servers, CLIs, connected apps).
   4. What, other than the assistant or the user, would show the result is right? Name a check
      that can pass or fail: a test, a metric, a standard, an external source, or real user
      behaviour.
5. Rewrite the prompt to ask for exactly that: one copyable block (a fenced code block) in plain
   English, at most 12 lines. Same task, deeper, not bigger. Add no new features or scope.
6. Stop and wait for the user.

## Output shape

The four short answer lists, then the block. Nothing after the block except, at most, one line
offering to run it.

## Pitfalls

- Deeper is not bigger. A rewrite that adds deliverables the user did not ask for fails the skill.
- Answers must name real files, data, sources or checks from this context, not generic advice
  like "write tests" or "follow best practices".
- A check the assistant grades itself ("looks good", "is well written") is not a check.
- Keep everything around the block short; people paste the block into another chat or agent.
