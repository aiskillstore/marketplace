---
name: align
description: Create or review ALIGN.md through a focused conversation about a user's project goals, priorities, preferences, constraints, and decision criteria. Use when the user asks to align expectations, establish project direction, revisit an agreement, or investigate drift from existing alignment. Do not start a new interview for routine work already covered by an agreement.
license: MIT
---

# Align

Help the agent make decisions that reflect the user's judgment. Keep the
current agreement in `ALIGN.md`, separate from task lists and general agent
instructions. Support one user's alignment with their agents, in new or
existing projects of any kind.

## Establish context

- Identify the target project and its applicable instructions. Read existing
  `ALIGN.md`, relevant project documentation, and available conversation context.
  Treat implementation as evidence of what exists, not proof of what the user
  wants. Do not import preferences from this skill's source repository.
- Check whether the target project is inside a Git work tree, for example with
  `git -C <project> rev-parse --is-inside-work-tree`. Distinguish no repository
  from Git being unavailable or access being denied. Do not initialize Git.
- If alignment exists, review available changes since its last confirmed
  alignment, including relevant uncommitted work and decisions. Use Git history
  when available. Inspect only context that can affect the current judgment.
  A timestamp alone does not prove that every later change has been reviewed.
- Without reliable history, state the limitation and ask only about gaps that
  matter to the current decision. Do not invent a baseline or create a separate
  history log. Missing history alone is not a reason to repeat the full interview.

## Choose the next useful action

For a new project, clarify purpose, intended users, desired outcomes, and
constraints before committing to implementation choices.

For an existing project without alignment, summarize the current direction
and clarify what the user wants to retain or change.

For a project with alignment, apply the current criteria. Raise only meaningful
inconsistencies or candidate new criteria, with evidence and a concrete proposed
revision. If nothing needs clarification, say so briefly and continue the task.

## Have a focused conversation

- Ask 1-3 related, consequential questions at a time. Reuse answers already
  available; do not ask the user to confirm an unambiguous instruction again.
- Cover only relevant gaps: purpose, success criteria, scope and exclusions,
  priorities, constraints, preferences, things to avoid, and autonomy boundaries.
- Turn abstract preferences into concrete choices, especially when time, cost,
  quality, or other values conflict. Explain a recommendation when helpful.
- Label assumptions and unresolved matters. A preference inferred from code,
  repeated behavior, or an example is a candidate, not an agreement.
- Once the essentials are clear, show a concise draft instead of continuing to
  fill categories. Refine it until the user considers it sufficient. The user
  may explicitly delegate drafting or storage decisions; honor that scope.

## Save the current agreement

Create or update the project-root `ALIGN.md` after the user confirms the draft
or clearly authorizes the particular lasting changes. Preserve unrelated
content and existing formatting when practical. Use the user's language and
the target project's conventions unless they specify otherwise.

Keep the document short and usable for decisions. A useful outline is:

- Purpose and desired outcomes
- Success criteria
- Scope and exclusions
- Priorities and trade-offs
- Constraints, preferences, and autonomy boundaries
- Unresolved matters, only when relevant
- Last full alignment timestamp

Distinguish requirements from default preferences and give a brief reason for
important criteria. Keep only current criteria. Use Git history for previous
versions; do not embed a changelog or create a parallel alignment history file.
Git availability does not itself authorize staging, committing, or publishing.

Use the stable footer label `Last aligned:` even when the document body is
translated. End with `Last aligned: YYYY-MM-DD HH:mm (time zone)` when the user
has confirmed the full agreement. Use a known user time zone and an actual
confirmation time. If the zone is unavailable, label UTC explicitly rather
than guessing a location. Do not invent a date for an existing undated agreement.

Reading, editing, and automatic review are not confirmation. For partial
agreement, keep the full timestamp unchanged and annotate only affected
criteria with their latest confirmation times. Replace superseded annotations
instead of accumulating a log. A draft saved without full confirmation must
say `Last aligned: Not yet confirmed.` A full reconfirmation may update the
timestamp even when the criteria themselves remain unchanged.

## Connect the agreement to future work

After saving an agreement, preserve existing `AGENTS.md` instructions and add a concise reference to
`ALIGN.md` with the operating rules below; create `AGENTS.md` if it is absent.
Avoid duplicate sections on later invocations.

Record these instructions in `AGENTS.md`:

1. Read `ALIGN.md` at the start of work and apply it to scope, key decisions,
   and result review. Follow the applicable instruction hierarchy.
2. Check available changes and decisions since the last alignment for meaningful
   drift. Use Git history when available; disclose material gaps. Do not repeat
   resolved questions without new evidence.
3. Adjust autonomously within existing agreements. When a lasting change is
   unclear, show the evidence and proposed revision and ask only about the
   consequential uncertainty. Continue work independent of that decision.
4. Reflect explicit lasting changes without seeking approval again. Do not
   generalize a one-off exception into a permanent preference, or rewrite
   agreements to justify the agent's choices or results.
5. Keep current criteria in `ALIGN.md` and previous versions in Git. Update the
   final timestamp only on full user confirmation; record partial confirmations
   on affected criteria without advancing it. Do not initialize Git or create
   an alternative history file unless requested.

Check the target agent's actual instruction entrypoint when known. Installing
this skill does not guarantee every agent reads `AGENTS.md` or runs it on every
task. If another entrypoint is required, connect it with a minimal reference
when authorized, preserving its existing instructions. Otherwise state the
manual invocation needed. Do not silently install hooks, change global agent
settings, or claim automatic enforcement.

Finish with the current agreement or changes, any material open question, and
the saved paths when applicable. Do not ask for another approval after a clear
confirmation just to close the workflow.
