# Prompt guide — nano-banana (nano-banana, nano-banana-2, nano-banana-pro)

Give this model connected sentences, not keyword strings. Say what the image is *for*, not only what
is in it, in one narrative paragraph, then refine conversationally across turns. A named aesthetic is
read holistically — it carries grain, palette and composition together — so name the look you want.

## What a prompt contains, in order

For a complex image, walk these in order; for a simple one, a single descriptive paragraph covering
the same ground is enough:

- **Subject** — who or what is in the image, stated specifically.
- **Composition** — how the shot is framed.
- **Action** — what is happening.
- **Location** — where the scene takes place.
- **Style** — the overall aesthetic. 
- **Editing instructions** — direct and specific, when modifying a supplied image.
- **Constraints** — what to hold fixed or keep out of frame. Where you can, write these as what you
  *do* want rather than as a list of bans — the model follows a positive description more reliably.

Then layer on camera and lighting (including aperture and colour grade) and any on-image text — its
wording, its look, its placement.

## Working from supplied images

Supply reference images and define the role each one plays — which is the subject, which is a style
to follow, which is a product to place. Address elements across images directly, e.g. *"take the
jacket from image 1 and put it on the person in image 2"*. To hold a character consistent, describe
them fully; if one drifts across edits, restart from a complete description rather than pointing back
at the previous result.

## Photoreal and cinematic work

- Name shot type, lens, camera angle and lighting; state the materials and surface detail.
- Direct the physics — aperture, focus, light direction, time of day — and a named colour grade.
- Category adjectives buy nothing; optical behaviour, light hardness and a decided dominant tone are what land.

## Turning a photo into an illustration

This one runs against the usual advice: keep the instruction **short**. A tight directive naming one
clear target style beats the long, fully-specified prompt that serves plain text-to-image well —
piling on constraints here works against you.

- Name the target style and its defining visual qualities, and state the background when one is needed.
- Pass the style as a reference image; the model holds artwork and layout while swapping the wording
  of text on signs and documents.
- Fix the person or they get reinvented — a supplied face reads as a starting point, not a spec.
  Spell out which features survive, clothing included, and that the design holds while the rendering
  shifts.
- A broad style label averages toward stock illustration. Specify its making: stroke weight, whether
  shading steps or blends, palette behaviour, signature texture. Describe the look itself rather than
  naming a studio, show or artist to imitate.
- Camera vocabulary drags a stylized pass back toward a photograph; leave it out.
