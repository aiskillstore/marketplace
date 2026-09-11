---
name: gtm-workflow
description: Triggers when a user asks to create, update, inspect, delete, run, query, schedule, or deploy a saved GTM workflow. Not for workspace setup, ICP or persona lifecycle work, or one-off work that should not become a reusable workflow.
---

# GTM workflow

## Trigger

Apply this Lifecycle SOP to a saved GTM workflow from creation through updates, runs, inspection, deployment, and deletion.

## Scope

Own workflow code, result tables, migrations, dry runs, runs, diagrams, and deployment metadata inside the root `workflows/` project. `gtm-workspace`, `gtm-icp`, and `gtm-persona` own their respective artifacts.

**Contract**

| Field | Public contract |
| --- | --- |
| Reads | The request, accepted workspace context, supplied rows, workflow files, and environment-held credentials |
| Writes | Workflow code, result tables, migrations, schedules, and deployment metadata |
| Outputs | A verified saved workflow, run result, inspection, diagram, deployment, or deletion |
| Approval | One plain-language card covers creation, save, hosted deployment, one-row test, and small fixes; later runs and checkpoints each get one card |
| Persists | Prepared local commits and approved pushes, plus workflow rows and cost records |
| Handoff | Workspace, ICP, and persona lifecycle changes go to their owning skills |

## Inputs

Use the request, resolved organization context, relevant accepted ICP and persona files, supplied rows, current workflow project, environment-held credentials, and accepted cost limits.

## Roles

The agent authors and verifies the work. The user approves one card covering saved changes, hosted deployment, the one-row test, stated external effects, and stated test cost; later full runs and user-chosen checkpoints each receive one approval.

## Procedure

1. Resolve the GTM workspace and requested lifecycle action. Ask one unnumbered question only when a result-changing fact cannot be inferred.
2. For create, copy `templates/` from this installed skill into the workspace's root `workflows/` project when absent, rename `gitignore` and `vercelignore` with leading dots, copy `.env.example` to `.env`, and write `GTM_HOST=<claude|codex>` for the host you run in. Workflow files live at `workflows/workflows/<slug>.ts`. Read [the library](references/library.md), [SDK choices](references/sdk.md), and [the interaction standard](../gtm-workspace/references/interaction.md). Read [deployment](references/deploy.md) only for deploy work and [local use](references/local.md) only for open/local work.
3. Draft workflow code, its table, a one-row input, and the author-written `Diagram:` header. A schedule request also writes the matching `vercel.json` cron entry. Run `npm run db:generate`, `npm run gtm -- verify <slug> --input data/test-1-row.json`, `git add <changed workflow, table, and migration paths>`, and `git commit -qm "<plain summary>"` silently. `data/` is ignored on purpose: the test input stays local and the card names it. Use `git commit --amend` after feedback when the prior commit was not pushed; after a push, a fix is a new commit.
4. Post one plan card stating what it does, reads, saves, where it runs, one-row test cost, possible data removal, and any missing key. Its last line is `Saving and testing. Back in a few minutes.` Invoke the matching command with that card as its approval summary: hosted, `git push && npm run gtm -- run <slug> --url https://<production-host> --input data/test-1-row.json --wait-live --background`, which returns at once and starts the test in the background after the deploy is live; local, `npm run gtm -- run <slug> --input data/test-1-row.json`, which starts the local server itself when needed.
5. After approval, collect hosted results with `watch_url` on `/api/runs/latest?workflow=<slug>&head=<pushed commit>` until a run appears, then on `/api/runs/<runKey>` until it finishes; at a keyboard use `npm run gtm -- runs get <id> --wait 600`. A failed run carries its plain reason in `error`; show it. Fix small failures and retry the identical approved step up to twice. Present a fresh card when cost, external effects, saved tables, command, or summary changes.
6. On success say `Built and tested. Ready to run whenever you want.` and provide the picture plus Diagram, Runs, and Data links. A later full run gets one short card and one real `run` command. Cancel asks `What would you like me to change?`; revise from free text and re-ask at the same step.
7. For update, inspect, or delete, preserve the same one-card boundary: verify and commit silently, then request approval for the first effectful command. Name deletion and data-removing SQL on the card. Use expand-then-contract for renames while a run may be waiting.

The command classifier allows local reads, checks, verification, dry runs, ordinary writes inside the checkout or scratch, and local commits. It asks for real runs, approval/cancellation, deploy commands, pushes, forced adds, paths outside those roots, and every unknown command. A chain takes its most restrictive classification; one approval request may be active at a time.

## Outputs

Produce a verified saved workflow or the requested run, inspection, deployment, or deletion result, with owned rows and cost records tied to its run.

## Exceptions

When the Claude Code hook is missing, say `Run command-permission.mjs --install-claude-code, then restart Claude Code.` and use the interaction standard's numbered approval fallback for this session. Under `GTM_SANDBOX=1`, every run must use the literal hosted URL; the bot never runs the workflow in its sandbox. Claude Code runs `agentStage()` locally with a budget cap and MCP-only tools; Codex cannot cap spend and returns the refusal sentence, so Codex users add an AI key for agentic stages.

## QC

- `gtm verify` passes before the card; the card reflects its cost, migration, and missing-key facts.
- Paid calls, including `agentStage()`, use an explicit `step` matching a `[step: name]` Diagram node. `agentStage()` costs use `[cost: up to $X/row]` matching `maxUsd`.
- Secrets remain in environment variables. `.env*`, `data/`, `.workflow-data/`, `.gtm-local.json`, and `node_modules/` remain untracked.
- Each file write stays inside the checkout or scratch and preserves user-owned workflow/table/provider files during `gtm upgrade`.
- User-facing text follows the interaction standard and contains no raw commands or JSON inside approval cards.

## References

- [Library contract](references/library.md)
- [SDK choices](references/sdk.md)
- [Deployment](references/deploy.md)
- [Local use](references/local.md)
- [Shared interaction standard](../gtm-workspace/references/interaction.md)
