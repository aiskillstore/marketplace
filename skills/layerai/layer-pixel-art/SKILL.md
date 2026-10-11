---
name: layer-pixel-art
description: "Use when making pixel art with Layer: sprites, retro game characters, pixel icons, pixel tiles, or a sprite sheet and walk cycle. Also when generated pixel art comes back blurry, anti-aliased, or at the wrong grid size, and when packing separate frames into a sheet or cutting an existing sheet into frames. Keywords: pixel art, sprite, sprite sheet, spritesheet, 16-bit, 32x32, walk cycle, animation frames, palette, dithering, pack, split."
license: MIT
---

# Layer Pixel Art

## Overview

Pixel art is the generation task most likely to come back subtly wrong: a picture _of_ pixel art,
soft-edged and anti-aliased at an arbitrary grid, rather than pixel art. Getting it right is mostly
about excluding the defaults.

Layer ships two deterministic sprite-sheet utilities alongside generation. `pack_sprite_sheet`
assembles separate frame images into one uniform-cell sheet on a transparent background, and
`split_sprite_sheet` cuts a sheet into its cells in reading order. These are named directly rather
than discovered because they are first-party tools rather than models, with no competing
alternative in the catalogue.

Generation mechanics are in the `layer` skill. If a sibling skill named here is missing from your
available skills, ask the user to install it (`npx skills add layerai/skills --skill <name>`);
unattended, proceed from tool schemas and flag the gap.

## Name the grid and the palette

Both, every time, as numbers.

- **Grid**: "32x32 sprite", "16x16 tile". A model given no grid produces something pixel-ish at no
  particular resolution, which cannot be cleaned up afterwards.
- **Palette**: a count and a family. "Limited 16-colour palette, muted earth tones" constrains the
  output in a way "retro colours" does not.
- **Era**, when the user has one in mind: 8-bit NES-era flat colour, 16-bit SNES-era with shading
  ramps, or modern high-resolution pixel art. These look nothing alike.

## Exclude the defaults, in the prompt

The defects are predictable, so name them as exclusions: no anti-aliasing, no blur, no gradients, no
soft shadows, hard-edged pixels only, one pixel per cell. Where the model declares `negative_prompt`,
put them there instead. Also state the background: "isolated on transparent background" or "flat
single-colour background", since a generated backdrop has to be cut out and pixel art does not
survive a sloppy cut.

## Sprite sheets and walk cycles

Do not ask one generation for a sheet of frames. Models produce a grid of loosely related drawings,
and the character changes between cells, which is exactly what a sheet must not do.

The working sequence:

1. Generate and approve **one** frame: the idle or contact pose, isolated on transparent.
2. Generate each remaining frame separately, with the approved frame attached as `reference_image`,
   and describe only what changed: "same character, same palette, same 32x32 grid, left leg forward
   mid-stride, right arm back."
3. Review the frames as a set and reroll the ones that drifted.
4. `pack_sprite_sheet` to assemble them into a uniform-cell sheet. Its input schema is the
   authority on the argument shape, so read it rather than assuming the parameter name.

Every frame after the first references **frame one**, not the frame before it. Chaining each frame
off the last one compounds drift, so by frame four the knight is a different knight.

When a trained pixel style is in play, attach it as `reference_sets` and omit `base_model_id`
entirely, so the server picks a model that can apply it. Use the same set, the same weight, and the
same reference frame on every frame of the cycle.

A four-frame cycle (contact, down, passing, up) reads as motion and is far more reliable than eight.
Start there and add frames only if the motion needs them.

Going the other way, `split_sprite_sheet` cuts a user's existing sheet into individual frames, which
is the way to edit one frame of a sheet without touching the others.

## Tiles

A pixel tile that repeats seamlessly is a tiling problem before it is a pixel problem, so filter for
the `tileability` capability and read `layer-textures` for how to specify scale and avoid visible
repetition. Everything on this page about grid, palette, and hard edges still applies.

## Worked example

"A 32x32 walk cycle for our knight sprite."

1. Generate the contact pose. `list_base_models` with `filter.use_case: "text_to_image"`, take the
   first result, then prompt: "32x32 pixel art sprite of an armoured knight, side view, contact pose
   with left foot forward, limited 16-colour palette, 16-bit era shading, hard-edged pixels, no
   anti-aliasing, no blur, no gradients, isolated on transparent background."
2. Approve one. This frame is now the reference for everything else.
3. Three more runs, one per remaining frame, each attaching the approved frame as `reference_image`
   and naming only the pose change.
4. Check the four together for drift in palette, height, and armour detail. Reroll any that moved.
5. `pack_sprite_sheet` with the four `file_id` values, which returns the sheet on a transparent
   background.

## Common mistakes

- Omitting the grid size, then trying to downsample a soft image into pixels.
- Asking one generation for a whole sprite sheet.
- Forgetting the anti-aliasing and blur exclusions, which are the defaults being excluded.
- Generating frames independently with no reference frame, so the character drifts.
- Generating an eight-frame cycle before a four-frame one works.
- Accepting a generated background instead of asking for transparent.
- Packing a sheet by hand when `pack_sprite_sheet` produces uniform cells deterministically.
