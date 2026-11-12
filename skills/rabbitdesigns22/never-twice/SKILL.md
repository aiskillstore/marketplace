---
name: never-twice
description: >-
  Load at the start of every task and before every answer that recommends something, states a status, or says "done". It keeps a shared error log (ERRORS.md) so the same mistake never happens twice across sessions: read the log for the task's topic first, verify before claiming, think the whole plan before writing it, show real evidence before saying done, and log every new mistake with the rule that prevents it. Triggers on "no errors", "sin errores", "don't make mistakes", "get it right", "be perfect", or any task where a wrong answer costs the user time or money.
license: MIT
---

# Never twice

No method makes an agent perfect. This one gets as close as it can with three promises:
1. **The same mistake never happens twice.**
2. **Nothing is claimed without checking it.**
3. **Every answer is the final answer.** No "first this, then actually that".

## The error log

Keep one file that every session can read, for example `ERRORS.md` at the root of the workspace. One line per mistake:

```
- YYYY-MM-DD · TOPIC · what happened · root cause · RULE so it never happens again
```

Example lines:
```
- 2026-11-05 · UI LABELS · "Closed sales" also counted booked calls · the label did not say what it counted · RULE: every metric label says exactly what it counts.
- 2026-11-05 · STATUS SCREENS · Explained "(UNKNOWN)" as "not registered"; it was the quality rating · guessed from the screen · RULE: before explaining a field, find in the code what renders it.
```

## Step 1. Before starting: read the mistakes for this topic

- Search the log for the task's topic (client, product, platform, tool). Every matching line is a rule for this task.
- Also read what was already decided: project notes, client files, memory.

## Step 2. Verify before deciding

- Every fact you use (number, ID, price, name, status, what a field means) comes from the source: code, live page, API, file, screenshot. Never from memory.
- If a fact cannot be checked and it changes the decision, find a way to check it first. If there is none, say "not verified" once, and say how it will be known.

## Step 3. Think the whole plan before writing it

For every step:
- What can go wrong? What happens if it fails? Can it be undone?
- What is the safest order? Things that break nothing go first. Irreversible things (delete, pay, publish) go last, and only if needed.
- What is the least you need from the user or their client? Ask for it all together, once.
- What is the obvious trap an expert would see?

Then write **one answer**: the recommendation first, then the steps, then (only if needed) what is not verified. No apologies, no "earlier I said".

## Step 4. Do the work with its own method

Use the right discipline for the job: tests first for code, a diagnosis loop for bugs, a review checklist before any deliverable.

## Step 5. Before saying "done": real evidence

Show the proof: the live version, the passing tests, the frames, the record read back after saving. If something could not be seen, say so. No proof, no "done".

## Step 6. When a mistake happens

1. Fix it.
2. Add one line to the error log with its rule.
3. If the rule belongs to one project, also put it in that project's notes.
4. Tell the user in one line what was fixed. No long apology.

## Final check (10 seconds, before every message)

- Did I read the error log for this topic?
- Is every claim checked, or marked "not verified"?
- Is this one answer I will not have to change?
- Did I show real proof for anything I call done?
