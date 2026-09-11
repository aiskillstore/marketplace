# Guided flows

Use the matched flow from `SKILL.md`. Keep ownership through completion; these users should never need git or command-line knowledge.

## Contents

- [Workspace rules](#workspace-rules)
- [Guided menu](#guided-menu)
- [Surface refusal](#surface-refusal)
- [Create](#create)
- [Import](#import-keyboard-surfaces-only)
- [Update](#update)
- [Delete](#delete)
- [Doctor](#doctor)
- [Git problem patterns](#git-problem-patterns)

## Workspace rules

- Every user-facing message follows the [shared interaction standard](interaction.md): its length and formatting caps, decision messages, one plain-language proposal per batch, approval by surface, and a `Saved.` close. The rules below are the workspace-specific ones that remain.
- Resolve the connected GTM workspace repo first: a repo explicitly named in the request, else the repo the hosting environment declares as connected, else canonical repos under `~/.gtm/` whose root contains `ORG.md`. If several valid repos exist and none was named, list their display names as numbered options. Treat roots with only legacy `org.md` as migration candidates, not canonical repos. Do not save a preferred repo. If update, delete, or doctor has no repo to use, explain that; on a keyboard surface offer create/import through the guided menu. On a fixed-connection surface, a connected repo whose root has neither `ORG.md` nor legacy `org.md` is not set up yet: offer create for that connected repo; otherwise use the surface refusal.
- Discover organization nodes recursively from the root through repeated `suborgs/<suborg-slug>/` segments. Display each node by its display name plus owner chain, `Enterprise (Nimbus Labs)`, and each member the same way, `Jordan Lee (Nimbus Labs › Enterprise)`; paths stay internal. Resolve every member relative to its owning node; never collapse same-named nodes or members from different branches.
- Never repeat or open an unsafe link. Follow `contract.md` link safety and continue using a plain-language source label.
- Research may combine model knowledge, fetched public sources, and supplied files/folders. Apply `company-data.md` whenever creating or fully researching an `ORG.md`, and apply `person-data.md` whenever creating or fully researching a `MEMBER.md`. Research each shared field when safe sources are available, keep unresolved fields visible as `Unknown`, and separate sourced facts from uncertain inferences. Use only a member email the user supplies or a source states directly.
- Implementation files under `workflows/` belong to `gtm-workflow`; hand them off instead of describing code, schemas, tests, config bodies, diffs, or ignore-file contents here.
- Prepare exactly the requested change and run the local stages of the background git ritual in `contract.md`; show one card, then push on approval. Close per the standard: what was created, changed, or removed, by identity, then `Saved.` Only import, sharing setup, whole-workspace deletion, and git-problem recovery may name GitHub, the repository, or the folder.
- Surface every git problem as a plain-English explanation followed by numbered options, with exactly one `(Recommended)` and the required reply line. Never force, branch, use a worktree, change global git config, or discard work.

## Guided menu

When no verb is clear, begin with:

> **What would you like to do with an organization's GTM workspace?**

Then explain:

> A GTM workspace is a saved folder for one organization. It gives your agent the background it needs for GTM work.

1. Create a GTM workspace for a new organization (Recommended when starting fresh)
2. Import an organization's existing folder or GitHub repository
3. Update organization or member information
4. Delete selected information or a whole organization's context
5. Check and repair a context that may be broken

`Reply with a number, or type your answer.`

## Surface refusal

Creating a different repo, import, sharing setup, and whole-repo deletion change which repo is connected, not just its contents, so they need a human at a keyboard. When one is requested while the repo connection is fixed by the deployment, refuse in one short message and perform nothing for that request:

- Why: this deployment's repo connection is part of its configuration, so a conversation here cannot create a different one, replace it, or remove it.
- What to do: run gtm-workspace from Claude Code or Codex CLI at a keyboard to create a different context, import one, set up sharing, or delete a whole context.
- What happens after: once a repo is connected to this deployment, updating, deleting content, and doctoring all work right here.

Write nothing, draft nothing, and research nothing for the refused request; do not produce carry-over artifacts in chat. A create request for the connected repo itself, when that repo is not set up yet, is not a connection change: run [Create](#create) with its connected-repo substitutions instead of refusing. Every other flow proceeds on any surface with a connected repo.

## Create

Create is one intake decision message, one research pass, one proposal, and one save.

On a fixed-connection surface whose connected repo has no root `ORG.md` or legacy `org.md`, run this flow for that repo with these connected-repo substitutions and no others: skip the git check in step 1; the connected checkout is the target, so create no `~/.gtm/` directory and run no collision check in step 2; the first proposal in step 3 carries the root organization `plus the workspace's standard setup files` and any supplied suborganizations and members, and is saved through the environment's declared mechanism; in step 4 do not initialize a repo or set a repo-local identity; skip the sharing step 5 because the deployment already shares the repo; in step 6 say the workspace is saved in the connected repository instead of describing local or shared mode. Every question, research rule, and completion criterion stays as written.

1. Check that git is installed before touching the target. If missing, explain it is the history tool this context needs and offer one guided install path appropriate to the operating system `(Recommended)` plus cancel; execute only the chosen path, then recheck.
2. Treat every value inside an `Example (fictional)` below as presentation only. Never extract, research, or save it unless the user independently supplies the same value. Create `~/.gtm/` when absent, then send exactly this one intake message; it carries no context line because no workspace is resolved yet:

   > **What is the organization's name, website, and any social profiles such as LinkedIn?**
   >
   > Share whatever you have in one message. Only the organization name is required. Example (fictional): `Brightpath Analytics — https://brightpath.example — LinkedIn: https://linkedin.example/company/brightpath-analytics`
   >
   > - Other links, files, or folders I should research. Example (fictional): `https://docs.brightpath.example`, `/path/to/Brightpath sales deck.pdf`, or `/path/to/customer-interviews/`
   > - Suborganizations, if distinct businesses need their own GTM context: name, parent, website, links. Example (fictional): `Brightpath Enterprise — parent: Brightpath Analytics — https://enterprise.brightpath.example — LinkedIn: https://linkedin.example/company/brightpath-enterprise`
   > - You: full name, email, role, social profiles, and which suborganizations you work with. Example (fictional): `Jordan Lee — jordan@brightpath.example — Head of Sales — LinkedIn: https://linkedin.example/in/jordan-lee`
   > - Other members: the same details for each, and which organization they belong to if not the main one.

   Extract the display name first, then every supplied suborganization, the operator, and every other member. Members default to the root organization with no follow-up; omitted roles, social profiles, affiliations, and sources need no follow-up. Recommend suborganizations only when distinct businesses would make shared GTM context misleading, and say so in the proposal rather than asking. Derive the lowercase kebab-case slug from the accepted name and check `~/.gtm/<org-slug>`; if the path exists, offer: open the existing context `(Recommended)`, choose another slug, or cancel, and never merge or overwrite implicitly. Apply link safety before opening any user-supplied URL.

   The only follow-ups are these recovery questions, in their fixed wording: `**What is the organization's name?**`, `**What are the missing names for these suborganizations?**`, `**What is your full name?**`, `**What is your email address?**`, `**What are your full name and email address?**`, and for other members `**What are the missing full names for these members?**`, `**What are the missing email addresses for these members?**`, or `**What are the missing full names and email addresses for these members?**`. When several apply, send one message: the first applicable one is the bold lead question and the others follow as bullets in their fixed wording without bold, each with only the record-identifying context it needs. Never conduct per-field, per-member, owner, or affiliation interviews.
3. Research every supplied source under the rules above: every field in `company-data.md` for the root and each suborganization, every field in `person-data.md` for each member. Draft `ORG.md` from `templates/org.md` and `MEMBER.md` from `templates/MEMBER.md`, preserve source limits, write `Unknown` for every unresolved field, and include only known optional metadata. Then present one proposal per the standard covering the root organization (`plus the workspace's standard setup files`), every supplied suborganization, and every supplied member, each by identity with its defining facts: for an organization, what is known and how many fields are still unknown; for a member, name, role, email. Show a complete draft only when asked. No other assistant turn may occur between the intake answer (or its one recovery message) and this proposal. Split only when the environment's approval-text limit forces it, along artifact boundaries, with the root organization always in part 1.
4. Create the repo locally; copy `templates/AGENTS.md`, `templates/CLAUDE.md`, and `templates/gitignore` to `AGENTS.md`, `CLAUDE.md`, and `.gitignore`; write every requested `ORG.md` and `MEMBER.md` at its canonical path; initialize git on `main`; set only the repo-local identity; stage, inspect, and commit the set once. Show one card describing the commit, including `plus the workspace's standard setup files`; approval authorizes its push.
5. On a keyboard, ask the sharing decision exactly as follows; this step's subject is the repository, so it may name GitHub:

   > **How would you like to use this GTM workspace repository?**
   >
   > You can keep it on this computer for yourself or share it with a team. Multiplayer can be added later.

   1. Keep it local and single-player on this computer. (Recommended)
   2. Make it multiplayer through a private GitHub repository.

   Keep the required reply line. For multiplayer, check `gh` is installed and authenticated. Guide install or login in single-question steps when needed. Ask the owning GitHub account/organization, propose the repo name, confirm it, create a private repo, and push `main`. At every step include `Cancel and stay local for now` as an option. Never imply local mode lacks history or GitHub sharing is public.
6. Close per the standard: the organization, each suborganization, and each member by identity, then `Saved.`, and one sentence saying whether the workspace stays on this computer or is shared privately with the team. Then add a short `Recommended next step` paragraph using only the explicit capability/skill catalog supplied by the hosting environment. Normalize only these exact workflow IDs and choose the first listed below that is available, regardless of conversational hints:

   1. `gtm-icp` → `Define the ideal customer profile for <saved organization display name>.`
   2. `gtm-persona` → `Define the buyer personas for <saved organization display name>.`

   Ignore every unrecognized ID. If the catalog is absent, empty, or contains only unrecognized IDs, use the ICP request above as a generic natural-language fallback without claiming that a workflow is installed. Follow the request with one sentence saying the agent will use the saved GTM workspace.

## Import (keyboard surfaces only)

Import's subject is the repository itself, so it may name GitHub, the repository, and the folder.

1. Check git before touching the target; use the create flow's guided recovery if missing. Ensure `~/.gtm/` exists.
2. Ask in one message whether the source is a local folder or a GitHub URL and for that source. Apply link safety; reject credential-bearing URLs without echoing them.
3. For a local folder, explain that import copies it and leaves the original untouched, then ask the user to confirm that expectation. For GitHub, explain it will clone a separate copy.
4. Inspect the source without changing it. Derive the proposed slug from an existing `ORG.md` H1, then a legacy `org.md` H1, otherwise the source name. Show and confirm the target `~/.gtm/<org-slug>`.
5. Check collision. Offer opening the existing target `(Recommended)`, choosing another slug, or cancelling; never overwrite.
6. Copy the local source or clone the GitHub source into the new target. Preserve available history; leave the local original untouched.
7. Inventory the target recursively against every contract and legacy-migration check. Report what fits and what needs conversion, including loose markdown, lowercase `org.md`, legacy `people/<person-slug>/person.md` or `PERSON.md`, unsafe links, placeholders, collisions, and git health. Members already under a suborganization's canonical `members/` directory are valid.
8. Present one conversion proposal per the standard: the moves, renames, deletions, and boilerplate additions in words, naming each artifact by identity when it has a display-name heading and an owning node and by slug or path when nothing else identifies it. Legacy members move to `members/<member-slug>/MEMBER.md` under the same organization node. Show replacement content only when asked.
9. On acceptance, apply only the proposal, initialize git on `main` when needed, set a temporary repo-local identity only when no local identity exists, and save the conversion as one plain-English history entry.
10. Offer the same optional guided multiplayer setup as create. Do not replace a valid existing remote without explicit confirmation.
11. Close with the source left untouched, what the converted workspace now contains by identity, the repairs made, `Saved.`, and whether the workspace stays local or is shared privately.

## Update

1. Resolve the repo, then ask in one message what to update: root organization facts / a suborg / a member / refresh facts from research / structure, with the target by identity when it is already clear.
2. Recursively list existing suborganizations or members by identity when the chosen target needs one; ask the user to select. For structure, offer add, rename, or move only where the contract permits it. A member may move between root and any valid suborganization node.
3. Ask every missing result-changing fact in one message. For a full research refresh, reread existing public links and use fresh public research. Apply every field in `company-data.md` to an `ORG.md` refresh and every field in `person-data.md` to a `MEMBER.md` refresh. Preserve accepted values that new evidence does not disprove, keep unresolved shared fields visible as `Unknown`, and distinguish sourced changes from inference. Keep the existing supplied member email unless the user or a direct source corrects it. A narrower refresh changes only the scope the user requested.
4. Present one proposal per the standard: each affected organization or member by identity with its changed facts only, each `was X, now Y`, and any move or rename in words. Show complete before and after content only when asked.
5. On acceptance, apply exactly the proposal, update member `Suborganizations:` references when an accepted suborganization rename requires it, run background git, and close per the standard.

## Delete

1. Resolve the repo, then ask in one message what to delete: a member / a suborg / content within a file / the entire organization context, with the target by identity when it is already clear.
2. List valid targets by identity when needed. For a suborganization, include all recursively nested suborganizations and every member, ICP, and persona owned by each deleted node, plus affected `Suborganizations:` references elsewhere, in the consequence report. Name every owned artifact by identity, `Household Buyer (Northstar Group › Consumer)`. For file content, describe the facts that disappear and show the resulting content only when asked.
3. List what disappears by identity and which affiliations change, one per line. In-repo deletion is recoverable. Whole-repo deletion removes the local folder and all local history; a GitHub copy survives and is not deleted.
4. For a member, suborg, or file-content deletion, present one proposal per the standard. On acceptance, apply the deletions, remove directories made empty by the accepted deletion, and verify every promised target is absent before running background git and closing per the standard with restore guidance.
5. Whole-repo deletion is keyboard-only and may name the repository and folder: on a fixed-connection surface, use the surface refusal instead of this step. For a whole repo, show the consequence report, then ask the user to type the org slug exactly. A mismatch changes nothing and asks again or offers cancel. An exact match authorizes removal of only the resolved `~/.gtm/<org-slug>` directory; do not run git afterward.
6. Close with what disappeared and how to recover it: ask to restore it, a surviving GitHub copy, or re-import, as applicable.

## Doctor

1. Resolve the repo and inspect every item in `contract.md`'s doctor checklist without changing anything. Traverse organization nodes recursively and inventory canonical and legacy member paths at every depth.
2. Report all healthy checks and every defect in plain English. Name each affected artifact by identity, or by slug or path when it has no display-name heading or owning node. Say whether changes are safely saved and whether the local and private shared copies agree. Keep branch, remote, upstream, and service details internal unless a problem requires them; never expose credential-bearing URLs.
3. If healthy, say so, change nothing, and close with a clean bill of health.
4. If defective, describe each repair in words and explain any destructive consequence, then present one proposal per the standard for the whole repair set. Show replacement content only when asked.
5. On acceptance, apply only approved fixes. Keep each canonical member at its owning node, migrate legacy paths under the same node, preserve facts, remove machine state/placeholders, restore contract files, and normalize safe slugs. Do not treat the temporary local identity as a defect.
6. Stage the repair set, inspect it, and save it once as `Repair GTM workspace repo`. Run remote pull/rebase/push when applicable. Close by rerunning the checklist and reporting the resulting health, then `Saved.`

## Git problem patterns

These interruptions concern the repository itself, so they may name GitHub, the repository, and the folder. Use one bold question with numbered options for each:

- Missing git: guided install `(Recommended)` / cancel.
- Uncommitted unrelated work: include it in the proposal / leave it untouched and save only accepted paths `(Recommended)` / cancel.
- Pull conflict or diverged history: stop and explain that local and shared edits overlap; guide a careful review `(Recommended)` / stay local for now / cancel. Never resolve by discarding or force-pushing.
- Authentication or rejected push: sign in and retry `(Recommended)` / stay local for now / cancel.
- Missing or invalid remote: repair the remote with a confirmed public-safe URL `(Recommended)` / stay local / cancel.
- Environment cannot durably save an accepted operation: render `**How would you like to proceed?**`; below it explain in plain English what could not be saved and why; then offer completing it from the CLI at a keyboard `(Recommended)` / cancel. Never report the change as saved.

End every discrete list exactly with `Reply with a number, or type your answer.`
