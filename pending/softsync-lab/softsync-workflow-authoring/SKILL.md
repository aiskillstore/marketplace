---
name: softsync-workflow-authoring
description: "Build a new automation and save it as a draft the user can review. Use when the user wants an automation set up, for example \"when a deal moves to a stage, create these tasks\"."
---

<!-- Generated from the SoftSync API skills. Edit them there and re-export. -->

# Building automations

You can write an automation and save it **switched off**. You cannot switch it on: a person does that in the app after reviewing it, because once on it runs on real records.

1. Find the building blocks: `workflows` with action `steps` and a search for what you want to do (send a message, change a record, check a condition). Connected apps show up here too.
2. Read what each one needs: `workflows` with action `step_details` for up to 10 steps at once. Use the exact field names it gives. Look up the workspace's own tables and fields first with `describe_workspace_schema`.
3. Write the whole definition: a name, a displayName, a trigger, a start step and the steps. Every step needs a short label and description in plain words.
4. Check it: `workflows` with action `validate`. It lists every problem with the step and field. Fix them and check again until it is clean.
5. Save it: `manage_workflows` with action `save_draft`. A definition with problems is refused and nothing is saved.
6. Confirm it exists: `workflows` with action `saved` lists every saved automation and whether it is on. The one you saved shows as off.

## Rules
- Say it plainly: the automation is saved but **not on**, and the person turns it on in the app (Autopilot) after checking it.
- Never say it is saved until `save_draft` has succeeded and `saved` shows it.
- Ask when a choice changes what the automation does (who gets told, which stage, how many days). Pick a sensible default for the rest and say which you picked.
- You cannot edit or delete a saved automation from here. To change one, save a corrected new draft.
