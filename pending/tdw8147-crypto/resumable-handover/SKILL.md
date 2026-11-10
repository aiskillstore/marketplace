---
name: resumable-handover
description: Use when pausing or transferring work; deliver a versioned handover with one actionable resume point.
---
# Resumable Handover

Turn a status dump into a note the next person can resume from without reconstructing the conversation.

## When to use

- A PDF is generated but its rendered output has not been accepted.
- A shift ends with one ready task and another waiting on a named event.
- A new revision changes one component and older checks still cover the rest.
- An interrupted request may have taken effect and must not be repeated.
- Accepted work needs an explicit closeout at transfer.

## When NOT to use

- The user asks you to finish the repair now, not write a transfer note.
- The deliverable is a release announcement with no work to transfer.
- The immediate task is to reconcile a receipt, not transfer ownership.
- The same operator only needs a quick progress update.
- The project is new and has no execution state yet.

## Core rules

1. **Deliver from the material you have.** A documented gap is more useful than a withheld handover.
2. **Apply each current update only to the fact it replaces.** A new revision does not reopen unrelated settled decisions.
3. **Bind evidence to version and scope.** An older check can support unchanged content but cannot prove a new preview happened.
4. **Separate paused, cancelled and unknown.** They imply waiting for a trigger, removing from the queue, and reconciling an existing attempt respectively.
5. **Keep original identity for unknown effects.** The available ID, target, time and submitted fingerprint let a successor query without replay.
6. **Name a real backup or say none.** An invented restore location is useless when the trigger fires; use `not provided` if records are silent.
7. **Close accepted work.** Optional improvements are not handover actions.

## Workflow

### 1. Put the goal and state at the top

- Write what acceptance means, not just the name of the project.
- Use done, not done, paused, cancelled, or outcome unknown.
- If parts differ, label them separately under the overall state.
- If a criterion is missing, mark it `not provided`; don't invent one.

### 2. Scope the finished evidence

- Match the current explicit update to the older statement it supersedes.
- Keep unrelated facts and avoid re-confirming settled points.
- List result, evidence locator, version, and the surface it covers.
- Carry forward relevant checks on unchanged material as historical evidence, not fresh runs.
- Distinguish a missing check from a failed check.

### 3. Order only necessary work

- Put independent ready work before waiting work.
- Place a prerequisite before a dependent check.
- Attach the explicit resume condition to each paused item.
- Remove cancelled actions even if they still appear in an older checklist.
- Put recovery in a conditional branch, not the normal queue.

### 4. Name the first action

- Write **verb + object + completion signal**.
- Use an actual path or entry point only if provided.
- If no work is ready, name the exact event being waited on.
- For unknown effects, keep the original request metadata; suggest a read-only lookup of that request or a bounded wait. Never resend.
- If the goal is accepted, write **Done, no next action**.

### 5. Record recovery and deliver

- Say what changed, where the actual backup is, and what triggers restore.
- If the change has no backup, say `none`; if unknown, say `not provided`.
- Do not perform the restore or run the remaining actions.
- If draft and submit tools are provided, read the necessary material, write the complete note, then submit it in order in the same round.

## Output template

```markdown
# Handover — [deliverable]
Goal / acceptance: [result and observable signal]
Overall state: [done / not done / paused / cancelled / outcome unknown]

## Finished and evidenced
- [result] | [evidence locator] | [version] | [coverage]

## Remaining in order
1. [ready prerequisite → expected result]
2. [dependent or waiting item → exact condition]

## Resume point
- First action: [verb + object + completion signal]
- If nothing is ready: [specific wait event / Done, no next action]
- Unknown request: [ID / target / submit time / submitted fingerprint]
- Original-only lookup or bounded wait: [entry point / limit / end condition]

## Changes and recovery
- Changed: [object] | Backup: [actual location / none / not provided]
- Restore only if: [supplied trigger]
- Gaps: [facts not provided or checks not run]
```

Omit optional sections only when inapplicable, not when they contain a material gap.

## Worked examples

### Example 1 — The cover changed after export

**Input.** `review/body.md` records a body-content pass for `guide-r6.pdf`.
Revision r7 replaces only the cover. `exports/guide-r7.pdf` exists but nobody opened it.
Acceptance means a rendered guide with no clipped title. The cover backup is `backup/cover-r6.svg`.
The supplied restore trigger is title clipping in the new preview.

**Bad**

> r7 is done; review passed. Recheck everything before release if you want.

**Good**

> Goal: r7 rendered with no clipped title. State: not done; preview pending.
> Finished: `review/body.md` covers r6 body content, unchanged in r7. It does not cover the r7 cover render.
> First action: open `exports/guide-r7.pdf`; done when the cover is visible and title clipping can be judged.
> Remaining: record the preview result. If the title clips, restore only the cover and recheck the affected render.
> Change: cover only. Backup: `backup/cover-r6.svg`. Restore trigger: clipped title in the r7 preview.

**Why it works.** The next person gets the file, the visual signal, and the affected scope without rerunning unrelated checks.

### Example 2 — A ready index update and a paused import

**Input.** Report r3 totals passed in `checks/totals.txt`.
The staging index update is independent. Import `im-42` to staging timed out at 14:10 UTC; submitted checksum `f7a`.
The operator paused import work until the window reopens and cancelled the duplicate export. Nothing changed during the handoff.

**Bad**

> The import failed. Retry it on your shift, regenerate the duplicate export, and redo the totals check.

**Good**

> Goal: update the staging index and reconcile the existing import. State: not done.
> Finished: report r3 totals pass in `checks/totals.txt`.
> First action: update the staging index; done when it lists r3. This does not depend on the import.
> Import: paused until the operator reopens the window; outcome unknown. Original: `im-42`, staging, 14:10 UTC timeout, checksum `f7a`; submit time not provided.
> After reopening: check `im-42` once in its original status view or retain unknown if unavailable. Do not resend.
> Duplicate export: cancelled, not queued. No changes made during handover; no recovery action.

**Why it works.** Ready work advances without treating a timeout as permission to replay.

## Common mistakes / red flags

| What you see | What to put in the note instead |
|---|---|
| “Everything passed” linking an old revision | Name the revision and the unchanged surface it supports. |
| “Resume when ready” | Name the event or artifact that releases the pause. |
| “Retry the timed-out request” | Preserve original identity and specify one lookup or bounded wait. |
| “Backup should be in the archive” | Give the recorded location, `none`, or `not provided`. |
| A cancelled item appears in TODO | Remove it from the queue; retain cancellation only as useful context. |
| Accepted work still has a check queued | Write “Done, no next action.” |

## Self-check

- [ ] Goal and current state are at the top.
- [ ] Updates override only their matching facts.
- [ ] Finished evidence names locator, version and coverage or marks gaps.
- [ ] Ready work precedes waiting work; prerequisites precede dependents.
- [ ] The first action has an object and signal, or an exact wait event.
- [ ] Unknown attempts retain original identity and are not queued for replay.
- [ ] Changed objects have a backup status and a supplied restore trigger or explicit gap.
- [ ] Accepted work has no next action; cancelled work is not queued.

## Stop at delivery

The note is ready when a successor can resume, wait for a named event, or see nothing remains.
Submitting the note does not complete the business task. Do not run remaining actions or delay the note to perfect the list.
