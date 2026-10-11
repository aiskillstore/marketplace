# Shape

Three separate things live under "shape": the **corner radius scale** (for component rectangles),
the **shape library** (35 iconic shapes for decoration), and **shape morphing** (animated
transitions between shapes). Numeric scale: see `tokens.md`.

## Principles

- Use abstract shapes **thoughtfully**, to add emphasis and decorative flair.
- Leverage Material shapes for **built-in shape morphing**.
- Rectangular shapes are **fully rounded in all corners by default**.
- **Individual corners can be adjusted** to create asymmetrical rectangular shapes.

## The shape library — 35 shapes

Circle · Square · Slanted · Arch · Fan · Arrow · SemiCircle · Oval · Pill · Triangle · Diamond ·
ClamShell · Pentagon · Gem · Sunny · VerySunny · Cookie4Sided · Cookie6Sided · Cookie7Sided ·
Cookie9Sided · Cookie12Sided · Clover4Leaf · Clover8Leaf · Ghostish · Burst · SoftBurst · Boom ·
SoftBoom · Flower · Puffy · PuffyDiamond · PixelCircle · PixelTriangle · Bun · Heart

All 35 can morph seamlessly into each other. Available via the Figma Design Kit shape library and
the Compose `MaterialShapes` API. **Web is not currently available.**

### Where to use them

Use the shape library for **mostly visual elements**: image crops, photography cropping,
personalized avatar masking, loading indicators, graphics, decorative UI, other non-interactive
elements. Decorative moments are the most flexible, creative use of shape.

**Avoid applying unconventional shapes to text-heavy containers.** Use them sparingly — sparing use
is what produces emphasis and delight.

## Shape morphing

Morph to **improve understanding and add delight**, communicating:

- **Interaction states** — e.g. a button becoming selected
- **Actions in progress** — a friend typing, a page loading
- **Changes in the environment** — sound, temperature, time of day

Think about how shapes react to tapping, swiping, scrolling, releasing, and long pressing. Shape
morphing **should respond to user interaction**.

Material itself uses morph in the **standard button group** (shows interaction) and the **loading
indicator** (shows progress). Morph defaults to the expressive motion scheme.

Buttons in particular morph shape by state: pressed buttons become more square (round and square
buttons share the same pressed shape), and toggle buttons also swap their resting shape — round when
unselected, square when selected (or the reverse if the unselected shape is square).

## Shape is versatile, not semantic

Do not make shapes literal or assign a fixed meaning to one shape. The loading indicator can be
wavy, but a waveform is not a strict symbol of progression — progress works equally well as rotating
shapes or a morph. Conversely, waveforms are fine on a button container, where they mean nothing
about progress.

## Be bold — embrace tension

**Tension** is when the shape story changes unexpectedly: contrasting shapes, mixing square with
rounded, unconventional silhouettes.

Material historically favored rounded shapes. Deliberately using **sharp** shapes adds tension and
produces a more dynamic, memorable, expressive design. Use tension to convey state, draw attention
to an element, or improve the aesthetic.

Combining shapes and corner radii creates either **visual tension or cohesion** — both are tools for
directing focus. Break from the surrounding shape style to draw attention to one element.

Watch the inverse failure: **smaller shapes make essential actions look less important.**

## Shape and type must agree

Shapes echo key visual attributes of M3 typography — M3 shapes and Google Sans Flex share roundness
attributes. Use shape and type together so the product feels cohesive and polished. A round shape
language with a rigid, condensed typeface reads as unresolved.

## Shape can be 2.5D

Applying motion and shape **differently on each layer** gives the illusion of depth and volume,
making 2D visuals feel 3D and more eye-catching.

## Symmetry and inner corners

Components can be symmetric (all corners equal) or asymmetric (per-corner values). Both use the same
10-step scale. Asymmetric shapes are used in M3 components with **closely-grouped items** — menus,
split buttons. Those are called **inner corners**, and inner-corner component tokens always map to
individual corner-value tokens.

## Customizing

Two levels:

- **Style level** — change what a scale step means (e.g. make `medium` a different size). Applies to
  every component mapped to that style, unless overridden. Cards and small FABs both move.
- **Component level** — remap one component to a different scale step. Buttons default to **full**;
  remap to `small` or `medium` for a less rounded product.

The shape family can also change from **rounded** to **cut** (a straight line instead of a curve).
**Add extra padding when using cut corners** — a large cut corner clips content more than a rounded
corner of the same size.

**Don't apply large or full corners to information-dense components such as cards** — they clip
content and images.

Generally, products should use the M3 shape styles consistently. Customization is appropriate — and
encouraged — for **hero moments and custom components**.

## Optical roundness (mandatory for nesting)

When nesting rounded objects, **never** reuse the container's radius on the child; it looks
unbalanced. Make them proportional:

```
inner radius = outer radius − padding      48dp − 14dp = 34dp
```

## Don't

- Don't compromise clarity for visual design.
- Don't include a differently-shaped element without a reason — shapes without clear meaning behind
  why they differ add visual clutter, not delight.
- Don't apply unconventional shapes to text-heavy containers.
- Don't reuse the same corner radius on nested objects.
