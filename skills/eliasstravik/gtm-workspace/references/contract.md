# GTM workspace contract

Use this contract when creating, importing, updating, deleting, or doctoring a GTM workspace repo. The installable contract is `templates/AGENTS.md`; this reference adds operational checks and git behavior.

## Repo shape

```text
~/.gtm/<org-slug>/
├── AGENTS.md
├── CLAUDE.md
├── .gitignore
├── ORG.md
├── icps/<icp-slug>/ICP.md
├── personas/<persona-slug>/PERSONA.md
├── workflows/
│   ├── package.json
│   ├── workflows/<workflow-slug>.ts
│   ├── workflows/<suborg-path>/<workflow-slug>.ts
│   ├── lib/
│   └── server/
├── suborgs/
│   └── <suborg-slug>/
│       ├── ORG.md
│       ├── icps/<icp-slug>/ICP.md
│       ├── personas/<persona-slug>/PERSONA.md
│       ├── suborgs/<suborg-slug>/...
│       └── members/<member-slug>/MEMBER.md
└── members/<member-slug>/MEMBER.md
```

- A repo represents one organization. Its directory slug is lowercase kebab-case.
- Every organization node has `ORG.md`. A suborganization is an organization node under `suborgs/<suborg-slug>/` and may recursively contain the same `ORG.md`, `suborgs/`, and `members/` shape without a depth limit.
- Any organization node may carry `icps/` and `personas/`. The workspace root alone may carry `workflows/`, a `gtm-workflow`-owned Node project; a suborganization's workflow lives at root `workflows/workflows/<suborg-path>/<slug>.ts`. New ICP and persona artifacts use `icps/<slug>/ICP.md` and `personas/<slug>/PERSONA.md`; existing flat `<slug>.md` artifacts remain compatible without migration. Artifact lifecycles belong to `gtm-icp`, `gtm-persona`, and `gtm-workflow`; `gtm-workspace` validates placement but not content.
- A member belongs to one owning organization node and lives directly below it at `members/<member-slug>/MEMBER.md`. Move the directory to change ownership; never duplicate a record implicitly.
- The H1 of every `ORG.md` and `MEMBER.md` is its display name.
- `MEMBER.md` contains a non-empty `- Email:` line supplied by the user or stated directly by a source. Role and `Suborganizations:` are optional facts, not required guesses. A `Suborganizations:` value records additional affiliations; the file path remains the ownership source of truth.
- Tracked content contains no machine state: no hidden coordination state, caches, generated indexes, run outputs, or logs. The workflow project's exact dependency pins and lockfile are authored content. Workflow working state is permitted only when gitignored and untracked.
- Repos contain no empty directories or placeholder files. Omit unknown sections or leave a short factual note; never write TODO/TBD-only artifacts.
- Everything stays on `main`. Accepted changes are committed; history is the undo mechanism.
- Prepare every requested change locally, stage only named paths, inspect the diff, and commit before showing the card under the [shared interaction standard](interaction.md). The card names the organization `plus the workspace's standard setup files` when it includes the three boilerplate files.

## Content shapes

Keep content factual, flat, and small. Research may use model knowledge, public sources, or user-supplied files and folders, but the user's acceptance of the described proposal decides what becomes durable.

`ORG.md` starts with the display-name H1. Every new or fully researched `ORG.md` follows the [company-data research contract](company-data.md), using its 13 fields for sourced organization facts. Keep unresolved fields visible as `Unknown`. Optional `## Links` and `## Notes` sections may follow; omit them when empty. `## Links` holds plain public URLs with readable labels.

`MEMBER.md` starts with the full-name H1. `## Identity` contains the required supplied `- Email:` identifier and, when known, `- Role:` and `- Suborganizations:`. Every new or fully researched `MEMBER.md` follows the shared [person-data research contract](person-data.md), using its eight fields for sourced person facts. Keep unresolved shared fields visible as `Unknown`. Optional `## Links` and `## Notes` sections may follow; omit them when empty. Never infer a member's email.

## Legacy compatibility and migration

Canonical discovery accepts a workspace only when its root contains `ORG.md`. Lowercase `org.md`, `people/<person-slug>/person.md`, and `people/<person-slug>/PERSON.md` are legacy inputs, not valid canonical output.

Legacy flat `icps/<slug>.md` and `personas/<slug>.md` artifacts remain valid skill-owned inputs. `gtm-workspace` does not migrate them; `gtm-icp` and `gtm-persona` read, update, and delete them in place while writing all new artifacts in canonical nested form.

- Create writes only the canonical names and paths.
- Import and doctor inventory legacy paths recursively at every organization node. The approval card describes each prepared rename or move in words.
- Rename each legacy `org.md` to `ORG.md` in place.
- Move each legacy `people/<person-slug>/person.md` or `people/<person-slug>/PERSON.md` to `members/<member-slug>/MEMBER.md` under the same organization node. Rename `Suborgs:` to `Suborganizations:` while preserving its values.
- If canonical and legacy paths collide, never overwrite. Describe both, show their content when asked, and ask the user to merge, choose a different slug, or cancel.
- Remove only legacy directories made empty by the requested moves, save one local `Migrate GTM workspace layout` history entry, and rerun canonical validation before the card. A cancelled card leaves the prepared commit local and unpushed.

## Link safety

Treat URLs containing credentials, tokens, keys, signatures, invitation codes, or session identifiers as unsafe. Do not open, persist, or echo the URL, even in shortened or cleaned form. Record only a plain-language source label when useful and advise the user to rotate the exposed credential. Plain public URLs are safe.

## Doctor checklist

Report healthy checks as well as defects.

1. Root contract files exist: `AGENTS.md`, `CLAUDE.md`, `.gitignore`; `CLAUDE.md` is exactly `@AGENTS.md` plus a final newline.
2. Every organization node, including every recursively nested suborganization, has `ORG.md`; every `ORG.md` and `MEMBER.md` has a display-name H1.
3. Every `suborgs/`, `members/`, `icps/`, or `personas/` directory is a direct child of an organization node whose `ORG.md` exists. `workflows/` is permitted only at the workspace root and is a `gtm-workflow` concern when found anywhere else. Canonical slug directories and compatible flat files beneath `icps/` and `personas/`, plus content beneath the root workflow project, are skill-owned; do not inspect or flag their content.
4. Repo, suborganization, and member slugs are lowercase kebab-case.
5. Every member is directly under an organization node at `members/<member-slug>/MEMBER.md` and has a non-empty `- Email:` line; listed `Suborganizations:` resolve to existing qualified suborganization paths.
6. No canonical workspace contains lowercase `org.md`, a `people/` directory, or a member file named `person.md` or `PERSON.md`; report them as migratable legacy defects rather than silently accepting or deleting them.
7. No machine-state files, empty directories, placeholder files, logs, or `.tmp` content are tracked. Inside the root workflow project, untracked `node_modules/`, `.env*` except `.env.example`, `.vercel/`, `.workflow-data/`, `.nitro/`, `.output/`, `.swc/`, and `data/` are permitted and are not defects.
8. Git is initialized, the checked-out branch is `main`, and the tree is either clean or has changes that can be previewed and committed.
9. Repo-local `user.name` and `user.email` are set. The temporary identity `GTM Workspace <gtm@local>` is valid and is not a defect.
10. When a shared copy exists, inspect its upstream, ahead/behind/diverged state, and authentication or reachability internally without changing anything first. Report whether local and shared history agree in plain language. Reveal the Git terms only when the user asks or needs them to resolve a problem.

For defects, describe each repair in words, naming an artifact by display name and owner chain when it has one and by slug or path only when nothing else identifies it, then present one proposal per the shared standard; show replacement content when asked. Apply approved repairs as one `Repair GTM workspace repo` commit. A healthy repo changes nothing.

## Persistence contract

Every saved change ends on `main`: prepared locally, described exactly by one card, pushed only after approval, recorded as one plain-English history entry, and undoable through history. Close with `Saved.`

The background git ritual below is the default mechanism. A hosting environment may declare a different durable-write mechanism for its connected repo; that declaration replaces only the mechanism. Every guarantee above still applies, and a hosting environment's native approval control is the push approval: the whole card is that control's text, and no numbered accept precedes it. If the environment cannot save an approved prepared commit, stop, explain what could not be saved, and offer completing it from a keyboard; never report an unpushed change as saved.

A connected repo whose root has neither `ORG.md` nor legacy `org.md` is not yet a canonical workspace. Its first saved change writes root `ORG.md` together with the contract files (`AGENTS.md`, `CLAUDE.md`, `.gitignore`) in one history entry; a hosting environment may refuse every other write until root `ORG.md` exists. Files outside the contract that the repo already carries, such as a README, are left untouched.

## Background git ritual (default mechanism)

Run this around each requested write or in-repo deletion when no environment-declared mechanism applies:

1. Confirm the repo is on `main`; never create a branch or worktree.
2. Prepare the change, stage only the named paths, and inspect the staged diff.
3. Commit once with a plain-English message such as `Add member: Jane Doe`.
4. Show one card describing that commit. On approval, push it and set the upstream when needed. Never force-push.
5. Close with `Saved.`, not with commit hashes, paths, or history vocabulary.

If any git step fails, explain the effect on saved history or private sharing without jargon. Keep branch, remote, upstream, and command details under optional technical details unless one is needed to fix the problem. Offer numbered recovery options with exactly one `(Recommended)` and the required reply line. Never change global git configuration. Create/import check that git is installed before touching the target. Create sets the repo-local identity once, to the operator's accepted name and email when the operator is in the accepted batch and to `GTM Workspace <gtm@local>` otherwise, so the single create history entry carries that identity.
