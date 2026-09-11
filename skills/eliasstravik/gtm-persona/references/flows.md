# Persona lifecycle flows

Apply the selected flow after loading `contract.md` and the shared interaction standard.

## Guided menu

When no lifecycle verb is clear, explain that a persona is a saved definition of people who fit or do not fit an organization's buying context, then render this exact block and continue into the selected flow. There is no import, clear, suggest, or brainstorm branch.

```text
**What would you like to do with your buyer and stakeholder personas?**

1. Create a persona (Recommended)
2. Update a persona
3. Delete a persona
4. Doctor the persona library

Reply with a number, or type your answer.
```

## Create

1. Resolve the workspace and create owner. Make the owner choice before reading any persona.
2. Read the root-to-owner `ORG.md` chain and only owner-local personas. Put the context line below the next bold opener instead of sending it first.
3. Extract every supplied fact for every supplied persona before asking anything. Ask all missing result-changing facts in one decision message per the standard: the bold lead question is the fact wanted most (for example `**Who should this persona describe?**`), the remaining facts wanted (display name, person-data criteria, responsibilities, buying context, authority boundaries, disqualifiers) are bullets, defaults such as the owner are stated bullets, and there is no numbered block. When the supplied facts already make the persona matchable, ask nothing and draft.
4. Apply link safety to supplied sources. Research every field in `person-data.md` when safe sources are available, but persist only criteria the user supplies or accepts. Organization and member facts do not establish persona criteria.
5. Compare only owner-local personas for material overlap. If a near-duplicate exists, explain it and ask whether to update the existing persona `(Recommended)` or continue with a distinct definition.
6. Draft one `personas/<slug>/PERSONA.md` per supplied persona from `templates/persona.md`. Keep all eight shared fields in order, use `Unknown` for unresolved criteria, and preserve uncertainty, authority limits, and disqualifiers in optional sections. Omit empty optional sections.
7. Create only the needed `personas/<slug>/` directories and `PERSONA.md` files, stage those named paths, inspect the diff, and commit locally.
8. Present one card per the standard covering every prepared persona: each by identity (`<display name> (<root> › <owner chain>)`) on one line, the defining facts stated once for the batch when shared, and any overlap in one line. Show the complete draft only when asked. On approval push the prepared commit, then close with each persona by identity and `Saved.`

## Update

1. Resolve the workspace and target under the artifact-reading node rule.
2. If several personas are visible and none was named, list only those visible personas by identity and ask which one to update.
3. Read the target and `ORG.md` chain. Gather only the requested change and preserve unrelated facts and freeform headings. For a full research refresh, apply every field in `person-data.md`, keep unresolved shared fields visible as `Unknown`, preserve accepted criteria that new evidence does not disprove, and persist only criteria the user supplies or accepts.
4. Write only the requested result, stage the named persona path, inspect the diff, and commit locally.
5. Present one card per the standard: the persona by identity and the changed facts only, each `was X, now Y`. Show complete before and after content only when asked. On approval push the prepared commit and close with the persona by identity, the exact change summary, and `Saved.`

## Delete

1. Resolve the workspace and target under the artifact-reading node rule.
2. If several personas are visible and none was named, list only those visible personas by identity and ask which one to delete.
3. Delete only that file, remove its artifact directory if empty, remove `personas/` if the deletion makes it empty, stage the named paths, inspect the diff, and commit locally.
4. Present one card per the standard: the persona by identity and that it will no longer be available.
5. On approval push the prepared commit and close with what disappeared by identity, `Saved.`, and the standard's one-sentence restore offer.

## Doctor

1. Scan every `personas/` directory in the repo, including stray placements. Do not inspect or repair ICP content.
2. Report healthy checks and every persona defect: canonical `personas/<slug>/PERSONA.md` whose `personas/` owner lacks `ORG.md`, a canonical directory slug that is not lowercase kebab-case, a canonical filename other than `PERSONA.md`, a missing display-name H1, content with no lead-matchable fact, a placeholder/TODO husk, or a canonical/legacy slug collision. Treat a legacy `personas/<slug>.md` as compatible when its owner, slug, H1, and substance are healthy.
3. Treat freeform files as healthy without template conformity. Preserve useful facts while renaming or restoring an H1; never invent substance to rescue a husk.
4. If healthy, change nothing and close with the complete health report.
5. If defective, apply only the scoped repairs, stage their named paths, inspect the diff, commit once as `Repair Persona artifacts`, and rerun every check.
6. Present one card listing every repair in words. Name a file by identity when it has a display-name heading and an owning node; otherwise name its slug or path. State that non-persona files remain untouched. Show replacement content only when asked. On approval push and close with resulting health and `Saved.`

## Sibling and runtime boundaries

- An ICP lifecycle request belongs to `gtm-icp`; a member or workspace-structure lifecycle request belongs to `gtm-workspace`. Make that handoff before resolving a workspace or reading artifacts. Lead research, segmentation, or scoring may read personas but must not route here unless the requested outcome also changes a persona.
- If the environment declares that it cannot durably save, preserve the exact repo state and use `contract.md` recovery. If it declares another durable mechanism, use it without adding a remote or treating the missing remote as a defect. If it declares a native approval control, the proposal is that control's approval text per the standard.
