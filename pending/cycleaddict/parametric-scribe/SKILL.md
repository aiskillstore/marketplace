---
name: parametric-scribe
description: Enables "Time Machine" coding. Records tasks as a Recipe and allows intelligent replay/modification of history.
---

# Parametric Scribe

## Overview

You are the Keeper of the Recipe. Unlike normal coding where "what's done is done," you maintain a **Parametric History** of the project in `docs/recipe.yaml`.

## Mode 1: Recording (The default)

**When:** After completing *any* coding task.
**Action:** Append a new entry to `docs/recipe.yaml`.

```yaml
  - step_id: "<sequential-id>"
    timestamp: "<iso-date>"
    intent: "<short-summary>"
    prompt: "<the-exact-prompt-used>"
    output_files: ["<list-of-modified-files>"]
    git_sha: "<current-head-sha>"
```

## Mode 2: Time Travel (Replay)

**When:** The user says "Change Step X" or "Replay from Step X".

**The Protocol:**
1.  **Read** `docs/recipe.yaml`.
2.  **Identify** the Target Step (Step X).
3.  **Hard Reset:** `git checkout <Step X-1 SHA>` (Go back to the state *before* Step X).
4.  **Execute Target:** Run the *New Prompt* provided by the user.
5.  **Intelligent Rebase (The Magic):**
    *   For each Subsequent Step (Step X+1, X+2...):
        *   Read the *Original Intent* (Prompt).
        *   Look at the *Current Codebase* (which is now different).
        *   **Self-Correction:** "The original prompt asked to modify `app.py`, but we are now in `index.js`. I will apply the *intent* (Add Login) to `index.js` instead."
        *   Execute the adapted prompt.
        *   Update the `recipe.yaml` with the new file paths and SHAs.

## Mode 3: Forking

**When:** The user says "Create a variant."
**Action:** Copy `recipe.yaml` to `recipe-variant-b.yaml` and modify the target step there, leaving the original intact.
