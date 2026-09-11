---
name: gtm-workspace
description: Triggers when the user invokes `/gtm-workspace` or asks to create, import, update, delete, validate, migrate, or repair a GTM workspace repo or folder, including adding members or suborganizations. Not for defining ICPs or personas, or for tasks that merely use an existing workspace without changing or validating it.
---

# GTM Workspace

## Trigger

Apply this Lifecycle SOP when the requested outcome creates, imports, maintains, validates, repairs, or retires the GTM workspace itself.

## Scope

Own the plain-Markdown workspace at `~/.gtm/<org-slug>/` across creation, import, organization and member maintenance, legacy-shape migration, structural or Git repair, and deletion. Create and fully research `ORG.md` artifacts with the shared company-data contract and `MEMBER.md` artifacts with the shared person-data contract. Preserve node-owned ICP and persona artifacts without authoring or validating their contents.

**Contract**

| Field | Public contract |
| --- | --- |
| Reads | The user's accepted organization facts, repository connection rules, valid local workspaces, and safe supplied sources |
| Writes | Workspace contract files, organization nodes, member files, repository configuration, and accepted structural repairs |
| Outputs | The requested workspace state summarized by display name and owner chain, a complete health report, or a fixed-connection refusal |
| Approval | The agent prepares, stages, inspects, and commits locally, then the user approves one plain-language card immediately before the push; whole-workspace deletion keeps its typed confirmation |
| Persists | Accepted workspace files and configuration in `main` Git history; no hidden coordination state |
| Handoff | `gtm-icp` for market definitions, `gtm-persona` for buyer definitions, and `gtm-workflow` for saved workflows |

## Inputs

Use the user's request and accepted facts, the hosting environment's repo connection and durable-write declarations, valid local workspaces, and safe supplied sources.

## Roles

The agent owns the selected lifecycle flow. The user approves one plain-language card immediately before the push that saves the prepared local commit; whole-workspace deletion keeps its typed confirmation. The hosting environment declares fixed connections.

## Procedure

| Condition | Owned flow |
| --- | --- |
| A fixed-connection deployment receives import, sharing setup, whole-workspace deletion, a create for a repo other than the connected one, or another connection-changing request | Refuse and redirect through the surface-refusal flow; perform nothing for that request |
| Create is requested on a fixed-connection deployment whose connected repo has no root `ORG.md` or legacy `org.md` | Guide the create flow with its connected-repo substitutions; the first saved change writes `ORG.md` together with the contract files |
| No lifecycle verb is clear | Guide the lifecycle menu and retain ownership of the selected flow |
| Create is requested | Send one intake decision message, research every supplied source, prepare one local commit for the organization and every supplied suborganization and member, show one card, push once on approval, then close |
| Import is requested | Guide a local copy or GitHub clone through inventory, accepted conversion, history, optional sharing, and summary |
| Update is requested | Resolve the target, describe the changed facts, save the accepted changes, and close |
| Delete is requested | Resolve the target, describe consequences, obtain the required confirmation, delete, and explain recovery where available |
| Doctor or migration is requested, or the workspace seems wrong | Run every contract, legacy-shape, and Git check; describe accepted repairs or migrations; save one change set; and report complete health |

## Outputs

Produce the requested workspace state and a plain-language summary by display name and owner chain, or a complete health report for doctor. A refused fixed-connection operation produces only the prescribed explanation and CLI redirect; a connected repo that is not set up yet is created in place, not refused.

## Exceptions

If a required reference is unavailable, use `templates/AGENTS.md` as the minimum contract, keep every member under its owning organization node at `members/<member-slug>/MEMBER.md`, and stay on `main`. If the environment cannot push the prepared commit after approval, stop and offer the prescribed CLI recovery; never report it as saved.

## QC

- Follow the shared interaction standard for every question, proposal, approval, and closing message; ask every missing result-changing fact in one decision message and never use `AskUserQuestion`.
- Prepare only the requested workspace action locally and never show complete bytes unless asked; the card must describe exactly what the prepared commit changes. Name GitHub, the repository, or the folder only in import, sharing setup, whole-workspace deletion, and git-problem recovery; keep branch, remote, upstream, and command details internal unless a problem requires them or the user asks.
- Keep all 13 company-data fields in the required order for every new or fully researched `ORG.md`; preserve uncertainty and write `Unknown` instead of inventing or dropping unresolved facts.
- Keep all eight person-data fields in the required order for every new or fully researched `MEMBER.md`; retain the required supplied email outside that contract, preserve uncertainty, and write `Unknown` instead of inventing or dropping unresolved facts.
- Stage only named paths, inspect the diff, commit locally, then show one card naming what changes and invoke `git push` with that card as the approval summary. Close a verified push with `Saved.`
- Close only after every selected-flow completion criterion in `references/flows.md` is satisfied.

## References

- Read [the workspace contract](references/contract.md) for every flow; it defines storage, content, link safety, doctor checks, and persistence.
- Read [the company-data research contract](references/company-data.md) before creating or fully researching an `ORG.md`; it defines the ordered fields, value shapes, uncertainty rules, and shared ICP semantics.
- Read [the person-data research contract](references/person-data.md) before creating or fully researching a `MEMBER.md`; it defines the ordered fields, value shapes, uncertainty rules, supplied-email boundary, and shared persona semantics.
- Read [the shared interaction standard](references/interaction.md) before any user-facing message; it defines audience language, length and formatting, proposal shape, batching, decision messages, approval by surface, and closing.
- Read [the guided flows](references/flows.md) after selecting the Procedure row; it defines intake, proposals, recovery, and closure.
- Render [templates](templates/) when creating or restoring contract files, replacing placeholders and omitting empty optional fields or sections.
