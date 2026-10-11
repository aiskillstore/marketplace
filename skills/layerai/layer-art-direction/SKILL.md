---
name: layer-art-direction
description: "Use when a Layer brief needs a direction before generating at volume: exploring a look with a moodboard, choosing between visual directions, storyboarding an ad, trailer or cutscene, pinning a colour palette, naming a style or era precisely, or framing a scene. Also when a brief is vague or generations keep missing an unstated intent. Keywords: art direction, moodboard, style exploration, storyboard, panels, beats, palette, composition, framing, era, reference."
license: MIT
---

# Layer Art Direction

## Overview

Most failed generation sessions are failed briefs. The user has a look in their head, the prompt
carries a fraction of it, and the fix gets attempted through rerolls that cost Creative Units and
converge on nothing. Direction is the cheap step that makes the expensive steps land.

Use this before volume generation, not instead of it. One or two cheap runs to agree a direction,
then everything else built on the approved result. Generation mechanics are in the `layer` skill and
prompt craft is in `layer-image`.

If a sibling skill named here is missing from your available skills, ask the user to install it
(`npx skills add layerai/skills --skill <name>`); unattended, proceed from tool schemas and flag the
gap.

## Name the style in production terms

Vague style words are the single largest source of drift. Translate the user's word into terms a
model can act on, and say the translation out loud so they can correct it.

"Stylised" is not a style. "Hand-painted with visible brush texture, soft edges, warm mid-tones, no
hard outlines" is. "Realistic" splits into photoreal, semi-realism, and stylised PBR, which look
nothing alike. "Cartoon" spans flat mid-century graphic shapes, thick-outlined modern TV animation,
and rubber-hose. "Retro" is meaningless without a decade.

Anchor an era with its concrete markers rather than its name: the colour combinations, materials,
typography, technology, and shape language of that decade. A prompt that says "1980s" gets a pastiche;
one that says "matte plastic, saturated primaries against beige, chunky rounded shapes, CRT glow"
gets the decade.

## Moodboards

A moodboard explores one concept across several directions in one image, for sign-off before
committing. Its value is the **axis of variation**, so state it: "the same hero prop rendered four
ways, from flat vector to painterly realism" is a moodboard. Four unrelated images are not.

Vary one axis at a time. A board that changes style, subject, and palette together cannot tell you
which change the user responded to, which is the entire point of making one.

Present the options and ask which direction to pursue. Then anchor everything after it to the chosen
one with `reference_image`, or train it if the project will run for months (`layer-reference-sets`).

## Colour

Constrain rather than describe. A named count and relationship does more than an adjective:
"three hues, muted teal and rust with a single warm accent" beats "vibrant colours".

Two game-specific rules survive every style. Readability first: gameplay-critical elements need value
contrast against their background, not just hue contrast, because hue alone fails for colourblind
players and at small sizes. And where colour carries meaning, such as a rarity ladder or a team
identity, it must stay consistent across every asset, which makes it a direction decision rather than
a per-prompt one.

## Framing

Shot grammar is meaning, not decoration. Camera height reads as power: below the subject makes it
imposing, above makes it vulnerable, level makes it neutral. Distance reads as intimacy. Lens
compression reads as realism or spectacle.

Say the shot in the prompt, every time. "Three-quarter view from slightly below, medium-wide" is a
decision; an unstated camera is the model's decision, and it will pick the average one.

## Storyboards

A storyboard is one beat per panel. The most common defect is panels that are pretty but do not
advance anything, so write the beats as a list first and check each one changes the situation.

Two ways to produce them, and the choice matters. **N panels in one image** keeps a consistent look
and is right for a quick read of a sequence, six or fewer beats. **N separate images** gives control
over each frame and is right when panels will become shots, since each becomes the `first_frame` of
its clip. Plan for the second when the board is heading for `layer-video`.

## Worked example

"We want a trailer for our game but we are not sure of the look."

1. Translate the brief. Ask what the game's tone is and turn their answer into production terms,
   reading the translation back for correction.
2. One moodboard run: one prompt, four directions along a single axis (rendering style), same
   subject, same palette. Cheap, under the gate.
3. They pick one. That image is now the anchor.
4. Write the beats as a list, confirm each advances the story, then storyboard as separate images,
   each attaching the anchor as `reference_image`.
5. Approve the panels, then animate each as `image_to_video` (`layer-video`) and assemble with
   `layer-video-timeline`.

## Common mistakes

- Generating at volume before a direction is agreed.
- Passing a vague style word through to the prompt untranslated.
- Varying several axes at once in a moodboard.
- Naming a decade instead of its concrete markers.
- Relying on hue contrast alone for gameplay-critical readability.
- Leaving the camera unstated.
- Storyboarding panels that look good but advance nothing.
- Putting panels in one image when each is destined to become a video shot.
