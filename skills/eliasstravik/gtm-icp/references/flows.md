# ICP lifecycle flows

Apply the selected flow after loading `contract.md` and the shared interaction standard.

## Guided menu

When no lifecycle verb is clear, begin with this exact block and continue into the selected flow. There is no import, clear, suggest, or brainstorm branch.

```text
**What would you like to do with your ideal customer profiles?**

An ICP is a saved definition of accounts that fit or do not fit an organization.

1. Create an ICP (Recommended)
2. Update an ICP
3. Delete an ICP
4. Doctor the ICP library

Reply with a number, or type your answer.
```

## Create

1. Resolve the workspace and create owner. Make the owner choice before reading any ICP.
2. Read the root-to-owner `ORG.md` chain and only owner-local ICPs. Put the context line below the next bold opener instead of sending it first.
3. Extract every supplied fact for every supplied ICP before asking anything. Ask all missing result-changing facts in one decision message per the standard: the bold lead question is the fact wanted most (for example `**Which accounts should this ICP describe?**`), the remaining facts wanted (display name, company-data criteria, fit signals, disqualifiers) are bullets, defaults such as the owner are stated bullets, and there is no numbered block. When the supplied facts already make the ICP matchable, ask nothing and draft.
4. Apply link safety to supplied sources. Research every field in the shared `company-data.md` when safe sources are available. Treat sources as evidence for criteria the user may accept, not permission to infer criteria from organization facts.
5. Compare only owner-local ICPs for material overlap. If a near-duplicate exists, explain it and ask whether to update the existing ICP `(Recommended)` or continue with a distinct definition.
6. Draft one `icps/<slug>/ICP.md` per supplied ICP from `templates/icp.md` using accepted or safely sourced criteria. Keep all 13 company-data fields in order and write `Unknown` for unresolved criteria. Preserve uncertainty and disqualifiers; omit only unsupported optional sections after `## Company data`.
7. Create only the needed `icps/<slug>/` directories and `ICP.md` files, stage those named paths, inspect the diff, and commit locally.
8. Present one card per the standard covering every prepared ICP: each by identity (`<display name> (<root> › <owner chain>)`) on one line, the defining facts stated once for the batch when shared, and any overlap in one line. Show the complete draft only when asked. On approval push the prepared commit, then close with each ICP by identity and `Saved.`

## Update

1. Resolve the workspace and target under the artifact-reading node rule.
2. If several ICPs are visible and none was named, list only those visible ICPs by identity and ask which one to update.
3. Read the target and `ORG.md` chain. Gather only the requested change and preserve unrelated facts and freeform headings. For a full research refresh, apply all 13 fields from the shared `company-data.md`, research them from safe supplied sources, preserve accepted criteria that new evidence does not disprove, and keep unresolved criteria visible as `Unknown`. A narrower refresh changes only the scope the user requested.
4. Write only the requested result, stage the named ICP path, inspect the diff, and commit locally.
5. Present one card per the standard: the ICP by identity and the changed facts only, each `was X, now Y`. Show complete before and after content only when asked. On approval push the prepared commit and close with the ICP by identity, the exact change summary, and `Saved.`

## Delete

1. Resolve the workspace and target under the artifact-reading node rule.
2. If several ICPs are visible and none was named, list only those visible ICPs by identity and ask which one to delete.
3. Delete only that file, remove its artifact directory if empty, remove `icps/` if the deletion makes it empty, stage the named paths, inspect the diff, and commit locally.
4. Present one card per the standard: the ICP by identity and that it will no longer be available.
5. On approval push the prepared commit and close with what disappeared by identity, `Saved.`, and the standard's one-sentence restore offer.

## Doctor

1. Scan every `icps/` directory in the repo, including stray placements. Do not inspect or repair persona content.
2. Report healthy checks and every ICP defect: canonical `icps/<slug>/ICP.md` whose `icps/` owner lacks `ORG.md`, a canonical directory slug that is not lowercase kebab-case, a canonical filename other than `ICP.md`, a missing display-name H1, content with no account-matchable fact, a placeholder/TODO husk, or a canonical/legacy slug collision. Treat a legacy `icps/<slug>.md` as compatible when its owner, slug, H1, and substance are healthy.
3. Treat freeform files as healthy without template conformity. Preserve useful facts while renaming or restoring an H1; never invent substance to rescue a husk.
4. If healthy, change nothing and close with the complete health report.
5. If defective, apply only the scoped repairs, stage their named paths, inspect the diff, commit once as `Repair ICP artifacts`, and rerun every check.
6. Present one card listing every repair in words. Name a file by identity when it has a display-name heading and an owning node; otherwise name its slug or path. State that non-ICP files remain untouched. Show replacement content only when asked. On approval push and close with resulting health and `Saved.`

## Sibling and runtime boundaries

- A persona lifecycle request belongs to `gtm-persona`; a member or workspace-structure lifecycle request belongs to `gtm-workspace`. Make that handoff before resolving a workspace or reading artifacts. Account research, segmentation, or scoring may read ICPs but must not route here unless the requested outcome also changes an ICP.
- If the environment declares that it cannot durably save, preserve the exact repo state and use `contract.md` recovery. If it declares another durable mechanism, use it without adding a remote or treating the missing remote as a defect. If it declares a native approval control, the proposal is that control's approval text per the standard.
