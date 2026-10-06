# Context Hygiene Checklist

Context degradation in AI coding sessions is silent. As context length increases, agents suffer from instruction fade, hallucinations, stale state references, and tool parameter errors. Use this operational checklist to maintain high-performance agent workflows.

---

## Operating Modes: When to Run What

| Command / Action | When to Use | Rough Threshold | Purpose |
| :--- | :--- | :--- | :--- |
| **`/compact`** | Continuing the exact same sub-task, but dialogue history contains noisy terminal outputs or long file reads. | **40% – 60% context** or **15–25 turns** | Flushes raw outputs and command histories while maintaining high-level thread continuity. |
| **`/clear`** | Switching to a completely different sub-task within the same codebase where earlier context is irrelevant. | Any time a distinct feature or bugfix boundary is crossed | Empties conversation memory completely while preserving the IDE state, active files, and workspace. |
| **Fresh Session** (New thread/window) | Completing an architectural phase, resolving major debugging loops, or when context exhibits degradation symptoms. | **>60% – 70% context** or **>35 turns** | Discards deep conversational drift, phantom file references, and degraded attention caches. |

---

## Context Degradation Indicators

Do not wait for a hard context ceiling error. Reset or compact immediately when you observe any of the following:

- **Instruction Amnesia**: Agent ignores negative constraints defined in earlier prompts (e.g., editing files it was told not to touch).
- **Repetitive Error Loops**: Agent suggests a fix it already tried 3 turns ago.
- **Diff Hallucinations**: Agent generates diffs against stale versions of files rather than current disk state.
- **Tool Failure**: Agent begins failing JSON syntax or schema validations on file-writing or terminal tools.
- **Sluggish Response**: High latency per generation turn caused by large KV-cache processing.

---

## What to Capture Before Resetting

Never clear or terminate a session without extracting these core data points:

1. **Active Diff and Branch**: Current git branch and list of dirty files (`git status -s`).
2. **Current Error Signature**: The exact compiler error, failed assertion, or runtime stack trace (top and bottom lines).
3. **Discarded Hypotheses**: What was attempted that failed, and why it failed.
4. **Immediate Target Assertion**: The specific passing criteria for the next prompt.

---

## The Pre-Reset 2-Minute Routine

Execute this checklist before wiping memory or launching a new session:

- [ ] **Step 1: Save Workspace State (30 seconds)**
  Ensure all files in the editor are saved. Run:
  ```bash
  git status -s
  ```
  If changes are functional, create a temporary commit (`git commit -m "wip: checkpoint before context reset"`). If incomplete, leave working files saved on disk.

- [ ] **Step 2: Run Verification Command (30 seconds)**
  Execute your test suite, type-checker, or linter:
  ```bash
  pytest <target_file> || npm test <target_file> || cargo check
  ```
  Capture the exact output status (pass/fail count or error message).

- [ ] **Step 3: Generate Handoff Note (45 seconds)**
  Fill out the standardized Handoff Note template (Doc 3) or command the active agent:
  > *"Generate a session handoff note using the session-handoff template. Document current state, decisions, files touched, open loops, and the exact next step."*

- [ ] **Step 4: Copy Note, Reset, and Bootstrap (15 seconds)**
  Copy the generated Markdown handoff note. Run `/clear` or open a fresh agent session. Paste the note as the first prompt:
  > *"We are resuming from a session reset. Here is our verified handoff state. Review the note and execute the Next Action specified."*
