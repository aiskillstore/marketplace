---
name: softsync-workflows
description: "Run the workspace automations — manual workflows and published ones — and check their results. Use when the user wants to start one of their automations or asks whether one finished."
---

<!-- Generated from the SoftSync API skills. Edit them there and re-export. -->

# Workflows

Workflows are automations built in the app. There are two kinds you can run from here.

## Manual workflows (most common)
The ones people start by hand in the app.
1. `list_runnable_workflows`: names, descriptions and the input each one needs.
2. `start_workflow_run` with the workflowName and that input. If input is missing, the error lists what to ask the user for.
3. `workflows` with action `status` and the runId until it finishes, then read its output.

## Published workflows
Workflows published as API endpoints, identified by a slug.
- `workflows` with action `list`, then `manage_workflows` with action `run`. Short runs return the result; long runs return a runId for `workflows` with action `status`.

## Past runs
- `workflows` with action `runs`: what ran in the workspace and how each went, newest first.
- `manage_workflows` with action `cancel_runs`: stop runs that are still going or waiting, with anything they started. A stopped run cannot be resumed.

## Rules
- Only pass input the workflow declares. Ask the user for anything missing.
- A workflow can change records or send messages. Tell the user what it will do and confirm before running it.
- Some workspaces also publish individual workflows as their own tools; use those the same way.
