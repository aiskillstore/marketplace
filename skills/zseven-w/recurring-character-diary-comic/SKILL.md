---
name: recurring-character-diary-comic
description: Create, audit, and repair short page-native diary comics around an existing authorized recurring character, with story-directed page rhythm, exact dialogue, directional-surface proof, and original-resolution visual QA. Use when extending an established recurring-character series from an anecdote, conversation, dream, or viewpoint, or when checking or repairing identity, anatomy, text, prop, relation, continuity, or layout defects. Do not use for standalone character design, educational explainers, infographics, one-off illustrations, generic memes, unauthorized characters or marks, imitation of a named living artist, watermarking, or social-platform publishing.
---

# Recurring Character Diary Comic

Turn a concrete observation into one coherent comic page while preserving an authorized recurring identity. The default is page-native generation: the image model solves the complete page, not a collection of independent cards.

## Load only the needed references

- Read [references/character-profile-schema.md](references/character-profile-schema.md) when creating or interpreting a recurring-character profile.
- Read [references/story-rhythm.md](references/story-rhythm.md) before selecting a premise, writing dialogue, or planning beats.
- Read [references/visual-task-contract.md](references/visual-task-contract.md) before locking evidence, comparing page skeletons, scoring risk, or selecting a production route.
- Read [references/continuity-and-visual-qa.md](references/continuity-and-visual-qa.md) before auditing, repairing, or accepting a rendered page.
- Read [references/editorial-layout-gate.md](references/editorial-layout-gate.md) before accepting a final page or using it as a public example.
- Read [references/compositor-manifest.md](references/compositor-manifest.md) and use [scripts/compose_panels.py](scripts/compose_panels.py) only when lettering a complete unlettered page or when an explicitly accepted fallback reconstructs a page from independent panels.
- Follow the available image-generation skill when generating or editing raster artwork.

## Choose the mode

- **Create:** require an existing authorized recurring identity, pass the premise gate, lock story and visual evidence, compare three page structures, generate one complete page, and inspect the final pixels.
- **Audit:** inspect an existing page against its approved character and story records; report evidence without silently editing it.
- **Repair:** audit first, name the failing field, and prefer one bounded local page edit. Reconstruct panels only under the fallback rule below.

Do not expand the request into character design, branding, publishing, or an unrelated illustration task.

## Establish rights and identity

1. Use only original characters, public-domain material, or references the user confirms they may use.
2. Refuse requests to imitate a named living artist, use a copyrighted franchise character without authorization, or reproduce a third-party signature mark. Offer medium-level traits instead.
3. Normalize the recurring identity into a profile before page generation. Separate stable identity invariants, episode variables, exact optional marks, and forbidden drift.
4. Treat a standalone reference for a required mark or accessory as more authoritative than an incidental depiction inside a character sheet.
5. If no usable recurring identity exists, stop and return the profile requirements. Do not invent a permanent character while producing the first episode.

## Lock the story and page plan

1. Apply the premise gate in `references/story-rhythm.md`. Prefer a drawable behavior over an abstract slogan, advertisement, or moral.
2. Preserve the user's experience and viewpoint. Extract setup, visible progression, reaction, and the final observation or reveal.
3. Choose 4–8 beats because the story needs them, not to fill a grid. Give supporting characters, objects, screens, and environments narrative jobs.
4. Lock every approved string before generation: exact spelling, punctuation, speaker, bubble ownership, and reading order.
5. Give each character, prop, state, panel, and critical relation a stable semantic ID. Classify requirements as blocking story truth (`S0`), blocking identity truth (`S1`), or replaceable composition preference (`S2`).
6. Express critical relations as visible evidence rather than co-occurrence. Record subject, predicate, object, contact or direction, visible proof, forbidden ambiguity, and required next state.
7. For every screen, paper, receipt, ticket, book, sign, or control, record its reader/operator, content face, reader side, viewer side, hinge or controls, gaze/hands, and the pixels that prove the relation. A nearby character and object do not prove reading or operation.
8. Draw three low-fidelity page-skeleton candidates before art generation. They must differ structurally, not merely by small frame offsets. Show beat IDs, reading path, relative area, visual anchor, gutters, negative space, and any content-derived border interaction.
9. Compare all three at working size and exactly 25%. Select the structure that preserves the story evidence and creates the clearest rhythm. Do not default to an equal card grid, a repeated row stack, or random rotation.
10. Border breaks, foreground overflow, semantic insets, open frames, and shared boundaries are optional vocabulary, never quotas. Use an effect only when its subject and narrative reason are clear and it does not hide faces, hands, text, direction, or state evidence.

## Choose the production route

Risk changes prompt and QA attention; it does not automatically decompose the page.

- **`page-native` — default.** Generate the entire page in one image, including panel topology, scenery, character scale, props, border interactions, bubbles, exact dialogue, paper texture, palette, and negative space.
- **`page-native-unlettered` — text fallback.** Use only when the complete page direction passes but rendered dialogue cannot be made exact. Generate one complete bubble-free, text-free page with intentional dialogue space, then add deterministic bubbles and text without cutting the art into panel sources.
- **`panel-reconstruction` — disclosed fallback.** Use only after two page-native attempts fail the same named `S0` or `S1` field, one local edit cannot isolate the defect, and the user explicitly accepts the loss of whole-page coherence. Generate and freeze independent panel sources, then reconstruct and re-audit the page. Do not switch merely because independent panels are easier to validate.

If reconstruction would destroy the requested page language, stop and report the blocker instead of delivering a compliant collage.

## Generate the page

1. Label each image input by role: identity, exact mark, medium, edit target, or supporting reference. Do not use a reference with a known defect as authority for the same field.
2. Compile one concise whole-page prompt containing the selected skeleton, beats in reading order, identity invariants, state continuity, exact dialogue and speakers, medium, and only ambiguities that can break `S0` or `S1`.
3. Use the same accepted identity and medium references throughout the run. Replacing them starts a successor run and requires rechecking affected artifacts.
4. Use no more than two page-native art attempts before a route decision. If the first result collapses into an unrelated row stack or card grid, correct the structural reference or prompt; do not disguise it with cosmetic diagonals.
5. Inspect every candidate at original resolution and exactly 25%. A generated file or successful tool call is not an acceptance result.
6. When one named defect can be isolated, prefer one constrained local edit and compare all pixels outside the allowed region against the saved baseline.
7. If only text fails, use `page-native-unlettered`. Preserve the whole-canvas art as one borderless source and render only approved bubbles and text.
8. A `panel-reconstruction` fallback receives a new artifact stage and new two-axis review. It never inherits a page-native artistic pass.

## Handle dialogue reliably

1. A page-native final may contain model-rendered dialogue only when every approved character, speaker, order, contour, and protected region passes on the final pixels.
2. For deterministic lettering, use one complete unlettered page as the full-canvas source. Do not slice it into narrative panels.
3. Speech bubbles must be connected, closed silhouettes with one outline. Prefer short, soft-rounded tails; reject detached tails, needle tips, narrow black necks, internal body arcs, seams, double outlines, or open contours.
4. Compare rendered strings character by character with the locked script. Reject rewritten wording, extra text, wrong speakers, ambiguous order, or action-obscuring bubbles.
5. Record art and lettering as separate artifact stages with input, font, geometry, and output hashes when deterministic rendering is used.

## Inspect and repair

1. Declare the artifact stage before judging it: `identity-reference`, `page-native-final`, `page-native-unlettered`, `unlettered-panel`, `reconstructed-page`, `lettered-final`, or `repair-candidate`.
2. Enumerate every panel's cast, visible hands, story-critical props, state changes, directional surfaces, physical relations, and approved strings.
3. Verify positive visible evidence for each relation. Trace contact geometry, current reader/operator, content face, gaze/hands, direction, and required next state.
4. Run contract-fidelity QA on the exact final hash at original resolution. Record `pass`, `fail`, or `not-verified`; every `S0` or `S1` failure blocks acceptance.
5. Separately run editorial-layout QA on the same hash at original size and 25%. Check reading path, beat hierarchy, panel rhythm, border language, intentional negative space, final emphasis, page-wide line/palette coherence, and accidental card-grid signals.
6. A page is `showcase-ready` only when both axes pass. Technical acceptance, editorial acceptance, user approval, and publication authority remain separate states.
7. After repair, recheck the repaired region and the complete final page. Reject a local edit that changes pixels outside its allowed region.
8. Stop on explicit acceptance, the bounded attempt limit, or two consecutive attempts that fail to improve the named field without damaging locked content. Report the blocker rather than weakening the contract.

## Deliver evidence

For Create, deliver the character/profile identifier, locked story and visual contract, three page-skeleton candidates and selected strategy, production route and attempt ledger, accepted final hash, any unlettered/repair/fallback artifacts actually used, and the two-axis QA record. Do not manufacture panel-source deliverables for a page-native run.

For Audit or Repair, deliver the exact inspected or repaired artifact hash, evidence locators, state, and next safe action.

Keep states distinct: `planned`, `generated`, `inspected`, `accepted`, `showcase-ready`, `internal-only`, and `user-approved`. None grants permission to publish.
