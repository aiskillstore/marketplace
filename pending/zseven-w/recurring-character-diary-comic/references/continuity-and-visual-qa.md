# Continuity and Visual QA

Use this gate on the rendered comic page, not on the prompt, storyboard, or generation status. A completed generation is an artifact candidate; it is not evidence that the page passed.

This document decides **contract fidelity**. It does not by itself decide whether
an accepted page is visually strong enough for a README, tutorial, hero image,
portfolio, or public showcase. Apply
[`editorial-layout-gate.md`](editorial-layout-gate.md) separately for that
decision and keep both outcomes bound to the exact reviewed final hash.

## Contents

- [Required evidence](#required-evidence)
- [Review sequence](#review-sequence)
- [Page and reading order](#page-and-reading-order)
- [Panel-by-panel inventory](#panel-by-panel-inventory)
- [Character continuity](#character-continuity)
- [Text fidelity](#text-fidelity)
- [Hands and anatomy](#hands-and-anatomy)
- [Props and continuity](#props-and-continuity)
- [Relations, contact, direction, and causality](#relations-contact-direction-and-causality)
- [Devices, paper, and directional logic](#devices-paper-and-directional-logic)
- [Visual treatment](#visual-treatment)
- [Local repair protocol](#local-repair-protocol)
- [Pass and evidence boundary](#pass-and-evidence-boundary)

## Required evidence

Collect these inputs before reviewing:

- the visual task contract, including constraint severity, provenance, unknowns, relation evidence, and the declared artifact stage;
- the approved panel plan and intended reading order;
- the exact approved text, including punctuation and speaker assignment;
- the character profile and authorized identity references;
- the expected cast, props, devices, and directional reading objects for each panel;
- for an edit, the pre-edit artifact plus a precise description or mask of the region allowed to change;
- the rendered output at its original resolution.

Declare one stage for every reviewed artifact:

- `identity-reference`: character identity and reference usability only;
- `page-native-final`: one complete generated page including approved dialogue;
- `page-native-unlettered`: one complete generated page before deterministic lettering;
- `unlettered-panel`: one textless panel used only by an accepted reconstruction fallback;
- `reconstructed-page`: a disclosed page assembled from independent fallback panels;
- `lettered-final`: a page with deterministic bubbles, exact text, and final checks;
- `repair-candidate`: a panel replacement or pixel-local edit compared with its accepted baseline.

Apply only requirements belonging to the declared stage. Do not fail a deliberately unlettered panel or page because dialogue is absent, and do not promote it as a final page before lettering is verified.

If only a reduced preview is available, report the review as provisional. Do not claim that small text, fingers, facial details, or local edit fidelity passed until the original-resolution pixels have been inspected.

## Review sequence

Review in this order so a late-stage detail pass does not conceal a structural failure:

1. page and reading order;
2. panel-by-panel evidence inventory on the complete page;
3. character continuity;
4. text fidelity;
5. hands and anatomy;
6. props and states;
7. relations, contact, direction, and causality;
8. visual treatment;
9. edit-scope drift, when applicable.

Record defects by panel and object. Use a stable locator such as `panel 3 / foreground hand / index finger`; avoid vague notes such as “the anatomy looks odd.”

## Page and reading order

- Count the visible panels and compare them with the approved plan.
- Trace the page from the intended entry point to the final beat. Check gutters, overlaps, border breaks, arrows, gaze, captions, and speech-bubble tails together.
- Reject any page that requires guessing which panel or bubble comes next.
- Verify that no panel, story beat, person, object, or line of dialogue was added, duplicated, reordered, or omitted.
- Confirm that the final beat receives the intended emphasis and is not visually pre-empted by another panel.
- Treat irregular composition as acceptable only when the sequence remains unmistakable at original size and exactly 25%.

Passing this section proves that the page is complete and readable. It does not
prove deliberate editorial rhythm. Uniform rounded cards, a detached cropped
reaction strip, dead packing space, or a weak final beat may remain non-blocking
for contract fidelity while still failing the separate editorial-layout gate.

## Panel-by-panel inventory

Create one row per panel before judging style:

| Panel | Expected characters | Expected text | Expected props/states | Relation obligations | Defects |
| --- | --- | --- | --- | --- | --- |
| 1 | ... | ... | ... | ... | ... |

For every row, compare expected and observed content. This catches missing or duplicated elements that are easy to overlook when reviewing the page as a whole.

## Character continuity

Inspect every appearance of every recurring character against the supplied profile and references.

- Compare face shape, distinctive features, hair, apparent age, body proportions, clothing, accessories, and approved marks.
- Check that stable features remain stable across changes in pose, angle, lighting, and expression.
- For every asymmetric feature, infer which anatomical side faces the camera. Verify that the feature appears on the correct side when visible and is naturally occluded when the opposite side faces the camera; do not reward a model for moving the feature to whichever temple is visible.
- Distinguish supporting characters through silhouette, facial structure, hair, clothing, posture, or scale. Reject accidental clones.
- Confirm that the same person is not duplicated within a panel unless repeated action or elapsed time is explicitly part of the composition.
- Verify that entrances, exits, handedness, clothing state, carried objects, and injuries or temporary details remain logically continuous between panels.
- Reject identity drift even when each individual drawing is attractive.

## Text fidelity

Build a transcription from the rendered page, then compare it character by character with the approved script.

- Check every Chinese character, letter, number, punctuation mark, and line break that affects meaning.
- Verify bubble ownership, tail direction, speaker attribution, and bubble reading order.
- Reject paraphrases, translations, missing characters, invented labels, random glyphs, duplicated text, and unauthorized marks or watermarks.
- Check that text remains legible at the intended delivery size and does not touch bubble edges, faces, hands, or critical action.
- If the image model cannot reproduce approved text reliably, generate the art without text and add bubbles and type deterministically. Re-run the full page check after composition.

## Hands and anatomy

Enumerate every visible hand, paw, wing, limb, wheel, antenna, or other countable body part defined by the character profile, including partially hidden and background parts.

- Compare counts, joints, articulation, and attachment points with the approved anatomy profile instead of assuming every character is human.
- For a standard human hand, a fully visible hand must resolve to one thumb and four fingers. For a cropped, occluded, or gripping hand, verify that visible and hidden anatomy can plausibly total five fingers without duplication.
- For animals, robots, or hybrids, enforce the profile's declared digit, paw, claw, manipulator, wheel, wing, antenna, or segment rules.
- Reject extra, missing, fused, forked, or duplicated parts; disconnected joints; reversed palms or appendages; impossible articulation; and implausible grips.
- Inspect high-risk interactions at enlarged scale: holding a phone, pen, cup, handle, book, camera, tool, or another hand.
- Check arms, elbows, shoulders, legs, knees, feet, joints, and total body count for duplication, fusion, or disconnection.
- Do not mark anatomy as passed because it looks plausible at thumbnail size.

## Props and continuity

- Track each recurring prop across panels: shape, color, size, state, damage, contents, and ownership.
- Verify that an object does not switch hands, sides, orientation, or state without an implied action or elapsed-time cue.
- Check depicted photos, notes, maps, interface elements, and recognizable object details for continuity when they recur.
- Reject unexplained duplicates, disappearing objects, inconsistent contents, and objects that merge into bodies or backgrounds.
- Confirm that object scale and contact points agree with the surrounding perspective.

## Relations, contact, direction, and causality

Review each S0 relation from the visual task contract as an explicit proof obligation. Objects appearing in the same panel, overlapping in projection, or occupying nearby space do not by themselves prove a relation.

For every critical relation, record:

- the subject, predicate, object, and expected panel state;
- the visible contact points or separating gap;
- the surface, opening, slot, handle, cable, flow path, or other topology that must remain legible;
- the current reader, operator, or recipient for a directional object;
- the force, travel, gaze, or orientation vector when it causes the next state;
- the observed next state and whether the prior panel can physically produce it;
- any contract-listed forbidden ambiguity.

Use relation-specific checks:

- **through / inside:** show the subject entering the opening and evidence on the far side; mere overlap at the rim fails;
- **inserted / attached:** the target cavity or joint cannot remain visibly empty beside the subject; contact and alignment must agree;
- **taut / pulling / flowing:** trace an unbroken path and verify that its direction points toward the depicted result;
- **facing / readable by:** identify the content-bearing surface and confirm that its plane faces the current reader, not automatically the audience;
- **powered / inactive / changed state:** compare the declared indicator, position, contents, count, or connection before and after the transition.

Prefer an original-resolution crop that includes both contact geometry and enough surrounding context to establish direction. Record a binary result and observed evidence; do not use “looks plausible” or an inferred hidden connection as a pass.

## Devices, paper, and directional logic

Treat screens, controls, pages, signs, maps, drawings, books, and checklists as directional objects.

- Identify the current operator, reader, viewer, or recipient for every directional object.
- Record the content face, reader side, viewer side, hinge or controls, gaze or hands, and the visible pixels that prove each assignment. Co-occurrence is not proof.
- Orient an active screen and its controls toward the person using it. Show the display to the audience only through a physically plausible angle, reflection, cutaway, or over-the-shoulder view.
- Turn a screen toward another character only when the action clearly presents or shares it.
- Orient paper content toward the person reading it. If the reader sits opposite the audience, the content may need a 180-degree rotation relative to the audience.
- Check screen plane, keyboard, hinge, stand, camera, gaze, hands, cables, and surface contact as one perspective system.
- Reject mirrored interfaces, backward pages, impossible hinges, duplicated devices, mismatched gaze, and hands operating inaccessible controls.

## Visual treatment

- Compare linework, texture, palette, contrast, lighting, and rendering finish with the approved visual direction.
- Confirm that texture supports readability rather than obscuring text, facial features, or anatomy.
- Check that adjacent panels belong to one page while allowing intentional changes in time, mood, or location.
- Treat visual appeal as separate from continuity: an attractive page still fails when the story, identity, text, or spatial logic is wrong.

## Local repair protocol

Repair one named defect at a time whenever the editing tool permits localized changes.

1. Inspect the suspected region at original resolution.
2. Save the pre-edit artifact as the comparison baseline.
3. Define the allowed edit region and the exact expected correction.
4. Lock panel geometry, text, identities, palette, lighting, and all unrelated content.
5. Apply the smallest viable edit.
6. Recheck the corrected region, its boundary, and then the entire page.
7. Compare the before and after artifacts outside the allowed region.

Outside the allowed region, reject:

- shifted panels, borders, bubbles, or text;
- altered faces, poses, clothing, props, or backgrounds;
- global changes in brightness, saturation, hue, texture, sharpness, or color temperature;
- new artifacts, anatomy defects, duplicated details, or removed content.

A narrow feathered boundary may change only when required to blend the repair. If unrelated regions drift, discard the edit and retry from the pre-edit artifact rather than repairing the repair.

If the editing tool cannot constrain a region or preserve off-target pixels, treat repair as an experimental attempt rather than a guaranteed operation. One global redraw is enough to reject that attempt; regenerate from the approved contract or report the limitation instead of presenting the result as a local repair.

### Deterministic panel replacement

Use this only when the production route is an explicitly accepted
`panel-reconstruction` fallback. Regenerate the failed independent panel from
its unchanged panel contract and replace only that panel through the
deterministic compositor. Record the old and new panel hashes plus the
reconstructed-page hash. Verify that all other panel inputs, layout fields,
bubbles, text, and protected regions are unchanged. Describe this operation as
`panel regeneration`, not as a pixel-local edit, and re-run editorial review;
the reconstruction does not inherit the page-native artistic verdict.

## Pass and evidence boundary

Use one of these outcomes for the declared artifact stage:

- **Pass:** every blocking check was performed on the original-resolution artifact and no blocking defect remains.
- **Fail:** at least one blocking defect remains, or a repair introduced off-target drift.
- **Not verified:** the actual artifact, required reference, approved script, pre-edit baseline, or sufficient resolution is unavailable.

Call this result `contract_fidelity`. When the page is also considered for
showcase use, record a second `editorial_layout` result and an exposure state:

- `showcase-ready` only when `contract_fidelity: pass` and
  `editorial_layout: pass` apply to the same final hash;
- `internal-only` for every resolved combination containing `fail` or
  `not-verified` on either axis.

Do not rewrite a valid S0/S1 pass as a technical failure merely because the
layout is generic. Preserve it as contract evidence and block showcase use on
the editorial axis. Likewise, visually strong layout cannot override a failed
or unverified S0/S1 field.

Treat every unresolved S0 or S1 field as blocking. S2 preferences are non-blocking unless the contract records an explicit user requirement or the observed result breaks reading order, legibility, evidence, or rights. Treat ambiguous reading order, identity drift, incorrect or unauthorized final text, implausible anatomy, impossible device or paper orientation, missing story content, failed physical relations, and off-target edit drift as blocking defects.

In the delivery note, state:

- the exact artifact reviewed;
- the resolution and whether it was the original output;
- which checks were completed;
- any remaining defect and its panel/object locator;
- whether the result is Pass, Fail, or Not verified.
- when showcase use is in scope, the separate editorial-layout result and exposure state.

Never substitute any of the following for artifact evidence:

- a successful tool call or completed generation status;
- a prompt that contains the right constraints;
- a storyboard, thumbnail, inventory, or file listing;
- an edit instruction without a before/after comparison;
- an assertion that a hidden or unavailable region “should be correct.”
