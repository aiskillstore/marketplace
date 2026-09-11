---
name: gtm-persona
description: Triggers when a user asks to create, define, refine, update, delete, or doctor a buyer or stakeholder persona file in a connected GTM workspace, including choosing which organization owns it. Not for ICPs, teammate records, general persona advice, or creating, importing, deleting, or repairing the workspace repository itself. Not for qualifying or scoring leads/accounts against saved ICPs/personas.
---

# GTM Persona

## Trigger

Apply this Lifecycle SOP when the requested outcome creates, updates, repairs, or retires a buyer or stakeholder persona owned by an organization node in an existing GTM workspace.

## Scope

Own node-local, freeform Markdown personas at `personas/<persona-slug>/PERSONA.md` across creation, refinement, deletion, and repo-wide persona integrity repair. Create and fully research personas with the shared person-data contract, interpreted as desired or accepted person criteria. Read legacy `personas/<persona-slug>.md` artifacts without requiring migration. Do not author ICP or member files, manage the workspace lifecycle, or classify/research leads against saved personas.

**Contract**

| Field | Public contract |
| --- | --- |
| Reads | Accepted persona facts and uncertainty, the root-to-owner `ORG.md` chain, owner-local personas, and safe supplied sources |
| Writes | Only the selected owner's canonical persona path, or scoped persona repairs during doctor |
| Outputs | An accepted node-owned persona identified by display name and owner chain, a complete health report, or a scoped handoff |
| Approval | The agent prepares, stages, inspects, and commits the scoped change locally, then the user approves one plain-language card immediately before the push |
| Persists | Accepted persona files in `main` Git history; no hidden coordination state |
| Handoff | `gtm-workspace` for repository structure or connections, `gtm-icp` for markets, and `gtm-workflow` for saved operational work |

## Inputs

Use the user's accepted persona facts and uncertainty, the hosting environment's connected-repo and durable-write declarations, the root-to-owner `ORG.md` chain, owner-local personas, and safe supplied sources.

## Roles

The agent owns the selected persona lifecycle flow. The user approves one plain-language card immediately before the push that saves the prepared local commit. `gtm-workspace` owns repository structure and connections.

## Procedure

| Condition | Owned flow |
| --- | --- |
| The requested outcome belongs to a sibling workflow | Hand off before workspace resolution or artifact reads; mutate nothing |
| No lifecycle verb is clear | Guide the persona lifecycle menu and retain ownership of the selected flow |
| Create or define is requested | Resolve the workspace and owner node, ground one or many factual drafts, check owner-local overlap, describe them, and save the accepted personas together |
| Update or refine is requested | Resolve one visible persona, preserve unrelated facts, describe the change, and save the accepted revision |
| Delete is requested | Resolve one visible persona, describe ownership and consequences, remove only the accepted target, and say it can be restored on request |
| Doctor is requested or persona artifacts seem malformed | Inspect persona placement and content repo-wide, describe the repair set, save it once, and report resulting health |

## Outputs

Produce the accepted node-owned persona state, identified by display name and owner chain, or a complete persona health report. A request owned by a sibling workflow produces only a scoped handoff and no artifact mutation.

## Exceptions

If no valid workspace is connected or discoverable, stop without writing and direct workspace creation or connection to `gtm-workspace`. If a required reference is unavailable or the environment cannot durably save the accepted operation, keep the repo unchanged and use the prescribed recovery.

## QC

- Follow the shared interaction standard for every question, proposal, approval, and closing message; ask every missing result-changing fact in one decision message and never use `AskUserQuestion`.
- Preserve every supplied responsibility, influence fact, authority boundary, disqualifier, and uncertainty; organization facts and adjacent personas are a factual ceiling, never evidence for invented persona claims.
- Keep all eight person-data fields in the required order for every new or fully researched `PERSONA.md`; preserve uncertainty and write `Unknown` instead of inventing or dropping unresolved criteria.
- Prepare only the requested persona files locally and never show complete bytes unless asked; the card must describe exactly what the prepared commit changes. Preserve legacy reads and node-local visibility and mutate only persona paths.
- Stage only named persona paths, inspect the diff, commit locally, then show one card naming what changes and invoke `git push` with that card as the approval summary. Close a verified push with `Saved.`

## References

- Read [the persona contract](references/contract.md) for every flow; it defines workspace resolution, ownership, visibility, content, acceptance, safety, and persistence.
- Read [the shared person-data research contract](../gtm-workspace/references/person-data.md) before creating or fully researching a persona; apply its ordered fields as desired or accepted person criteria.
- Read [the persona lifecycle flows](references/flows.md) after selecting the Procedure row; they define menu, create, update, delete, doctor, recovery, and closure.
- Render [the persona draft template](templates/persona.md) only for create; it is a starting shape, not a schema or validity test.
- Read [the shared interaction standard](../gtm-workspace/references/interaction.md) before any user-facing message; it defines audience language, length and formatting, proposal shape, batching, decision messages, approval by surface, and closing.
