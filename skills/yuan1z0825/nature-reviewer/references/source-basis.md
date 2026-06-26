# Source basis

## Authoritative local source

- Primary local source: `references/editorial criteria and processes.md`
- Scope of authority:
  - publication criteria for `Nature` Articles
  - peer-review entry criteria used by editors before external review
  - referee selection basis
  - ideal referee report content
- This skill must treat that file as the only authoritative local source for reviewer-facing behaviour in the MVP.

## Direct source extracts converted into working rules

- Publication criteria for Articles:
  - papers should report `original scientific research`
  - papers should be of `outstanding scientific importance`
  - papers should `reach a conclusion of interest to an interdisciplinary readership`
- Peer-review entry criteria used by editors:
  - results seem `novel`
  - results are `arresting` — illuminating, unexpected, or surprising
  - work has `immediate and far-reaching implications`
  - this initial decision is `not a reflection on technical validity` or field-local importance
- Readability expectation relevant to reviewer assessment:
  - submitted material receives `special attention` for readability
  - highly technical work should explain background and field impact clearly enough for `nonspecialist readers`
- Referee selection basis:
  - `independence` from authors and institutions
  - ability to evaluate `technical aspects` fully and fairly
  - may be `currently or recently assessing related submissions`
  - `availability` within the requested review time
- Ideal referee report content:
  - indicate `who will be interested in the new results and why`
  - indicate `technical failings` that must be addressed before the authors' case is established
- Editor-versus-referee boundary in the source:
  - editors judge whether work is likely to interest readers `outside its immediate field`
  - referees may still help when significance was overestimated or `undersold`
  - editors are strictly concerned that `technical failings` be addressed
  - editors are `not strictly bound` by referee editorial opinions on whether the work belongs in `Nature`

## Local rule summary

- Reviewer outputs must evaluate the manuscript against source-grounded axes only:
  - `originality`
  - `scientific importance / significance`
  - `interest beyond the immediate field / interdisciplinary readership`
  - `technical soundness / technical failings`
  - `readability for nonspecialists` when inferable from the manuscript
- Reviewer outputs must not pretend to make the editor's acceptance decision.
- Reviewer outputs may comment on whether significance seems overstated or understated, because the source explicitly allows helpful referee advice there.
- Reviewer outputs must distinguish:
  - what is supported by manuscript evidence
  - what is missing or technically weak
  - what cannot be assessed from provided material
- When the manuscript packet is incomplete, the skill must use `AUTHOR_INPUT_NEEDED` or equivalent missing-evidence flags instead of inventing facts.

## Conservative implementation choices

- The skill returns exactly `3 reviewer reports + 1 cross-review synthesis` by default.
  - This is a repo-level implementation choice, not a direct source requirement.
- The three reviewers differ only by `emphasis`, not by invented identity, seniority, institution, demographic profile, or narrow specialty role.
  - This is a conservative anti-hallucination rule derived from the limited source basis.
- The output includes an explicit `Risk / unsupported claims` section.
  - This is a local QA device, not an official Nature format requirement.
- The skill uses explicit section labels such as `Review setup`, `Reviewer 1`, and `Cross-review synthesis`.
  - This is a formatting contract for usability, not a source claim.

## Implementation implications

- If the user asks for an author rebuttal, route to `nature-response`, not this skill.
- If the user asks for simulated peer review, stay in reviewer mode:
  - assess claims
  - identify likely interested readership
  - identify technical failings
  - avoid drafting editorial decision language as the default output
- If the manuscript seems technically valid but not clearly broad-interest, the reports may say so; the source explicitly separates technical validity from editorial selection.
- If the manuscript is broad-interest but evidence is incomplete, the reports must still foreground technical failings because the source treats them as essential before the authors' case is established.
