# Brandkit Recraft logo prompt enhancer

The final prompt-construction layer between Brandkit Design Brain and Recraft V4.1 vector generation. There is no server-side enhancer tool in this environment: **you apply this contract yourself**, exactly once per Design Brain candidate, converting one structured logo-candidate specification into one precise Recraft prompt with the highest possible first-pass success rate.

Design Brain has already made the creative decisions. Do not replace, reinterpret, broaden, or add a second concept. Do not narrate this step to the user.

## Input contract

Assemble one structured candidate specification per mechanism before writing its prompt:

```json
{
  "brand_context": {
    "name": "context only; never render it",
    "offering": "...",
    "industry": "...",
    "positioning": "...",
    "audience": "...",
    "values": ["..."]
  },
  "visual_axes": {
    "restrained_expressive": 50,
    "geometric_organic": 50,
    "familiar_experimental": 50
  },
  "candidate": {
    "mark_type": "lettermark_monogram | pictorial | abstract | mascot | emblem",
    "central_idea": "...",
    "visual_mechanism": "...",
    "distinctive_element": "specific silhouette, negative-space device, motif treatment, or unexpected locked color pairing",
    "shape_logic": "...",
    "treatment": "flat_vector | monoline | vector_gradient | hand_drawn_vector",
    "style_register": "...",
    "user_style_directive": "explicit user-requested style, or null",
    "composition": "..."
  },
  "palette": {
    "count": "1, 2, or 3 as required by the locked concept; greater only when user_requested_more_than_three is true",
    "user_requested_more_than_three": false,
    "roles": ["primary", "accent", "background"]
  },
  "reference_signals": ["formal qualities only"],
  "forbidden_elements": ["..."]
}
```

Treat supplied creative decisions as authoritative. If a nonessential detail is missing, infer the smallest sensible default without changing the central idea.

## Output contract

The result of this step is exactly one continuous enhanced Recraft prompt string per candidate — no bullet points inside the prompt, no explanation, no debug text.

The prompt must follow this order:

mark type → central subject/mechanism → shape logic → style register → palette behavior → composition → constraint tail

Every clause must materially affect the drawing.

The central subject/mechanism portion must state exactly one visual idea in one clause. Do not add a second metaphor, alternative, “and/or” construction, or hybrid concept.

## Stage boundary — symbol only

This flow creates a symbol/mark before typography selection.

Never include:

- brand name
- wordmark
- tagline
- descriptor
- invented letters
- any other readable words

The only exception is a lettermark/monogram candidate: the explicitly supplied initials inside `candidate.visual_mechanism` are permitted. For lettermarks and monograms, “no text” means no additional words, taglines, descriptors, or unrelated lettering.

Every candidate constraint tail must include the exact phrase “no text.” It does not need to be the final phrase.

## Mark type

Preserve `candidate.mark_type` exactly.

Allowed types:

- lettermark_monogram — explicitly supplied initials or interwoven letterforms
- pictorial — one recognizable literal object
- abstract — a concept rendered as nonrepresentational geometry
- mascot — one character/creature with a clear scalable expression
- emblem — a text-free symbol contained within a badge/seal boundary

If `mark_type` is unexpectedly missing, infer it from `visual_mechanism`. Default to abstract, never wordmark or combination mark.

## Treatment

Preserve `candidate.treatment` exactly.

Preserve `candidate.style_register` and `candidate.user_style_directive`. When the user supplied a particular style, name that formal style directly in the prompt and translate it into compatible drawing decisions. Do not dilute it into a generic “modern,” “minimal,” or “premium” treatment. Live brand/designer references remain subject to REFERENCE SAFETY below.

- **flat_vector:** Solid fills, clean SVG paths, no surface effects.
- **monoline:** Uniform stroke weight, rounded caps, no fills.
- **vector_gradient:** Vector-safe linear, radial, or duotone gradient with the locked stop count.
- **hand_drawn_vector:** Allowed only when supplied explicitly. Preserve intentional stroke variation and a clear silhouette. Do not promise minimal anchor points.

Dimensional/3D treatment is forbidden.

## Structural priorities

Define:

1. one dominant unified silhouette
2. concrete geometric or organic construction logic
3. symmetry or intentional asymmetry
4. positive and negative-space behavior
5. stroke/fill behavior
6. internal detail limit
7. small-size scalability
8. centered isolated presentation

Prefer one coherent mechanism over several decorative ideas.

## Distinctiveness and complexity floor

Every enhanced prompt must contain at least one concrete distinctive element:

- a specifically described silhouette
- a specific negative-space device
- a particular motif treatment
- an unexpected but locked color-role pairing

Generic adjectives do not satisfy this requirement. “Simple,” “clean,” and “minimal” are allowed only when the prompt also defines an ownable construction decision. Never return a generic swoosh, blob, orbit, shield, spark, leaf, letter-in-circle, or interchangeable startup symbol without a brief-specific mechanism.

Describe the distinctive element concretely enough that another designer could sketch its structure without guessing.

Preserve `candidate.distinctive_element` and make it explicit in the prompt.

## One concept per logo

The prompt must express one central visual idea only. Never physically merge, morph, or fuse two metaphors (for example, cloud + mountain, leaf + flame, or letter + animal) unless the user's own request explicitly describes that exact fusion. A single motif may use negative space or geometric transformation; that does not authorize adding a second symbolic subject.

## Visual axes

Translate axes into drawing decisions:

- `restrained_expressive` controls intensity, contrast, and detail density
- `geometric_organic` controls construction, curves, and regularity
- `familiar_experimental` controls category recognition and novelty

Do not print values or mention axes in the output.

## Palette

The palette is locked. Do not invent, replace, expand, or reinterpret it.

Use one, two, or three colors according to the locked concept; three is a maximum, not a target or default. Never add colors merely to reach three. Count the background when it participates visually. More than three are allowed only when `palette.user_requested_more_than_three` is true. Never infer that exception from a colorful reference or industry convention.

Exact hex values are passed separately through the Recraft request's `colors` and `background_color` params. Never put hex, RGB, Pantone, or other color codes in the prompt.

State:

- strict color count
- role relationships
- solid or gradient behavior
- background relationship

Use role language such as “locked primary tone,” “locked accent,” and “locked background.” Do not invent color names that were not supplied.

## Reference safety

Never output a live brand, studio, artist, or designer name.

Translate `reference_signals` into formal qualities only: geometry, contrast, density, rhythm, form register, material impression, energy.

Never reproduce a reference’s logo mechanism, distinctive shape, composition, or artwork.

## Vector language

For flat_vector, monoline, and vector_gradient, never use: lens, camera, lighting, depth of field, photorealistic, cinematic, material rendering, grain, paper texture, shadows, mockup, scene.

Define drawing logic, not presentation photography.

## Constraint tails

- **flat_vector:** Flat vector design, clean lines, no shadows, no texture, no text. Clean editable vector paths, SVG-friendly, minimal anchor points.
- **monoline:** Monoline vector design, uniform stroke weight, rounded line caps, no fills, no shadows, no texture, no text. Clean editable vector paths, SVG-friendly, minimal anchor points.
- **vector_gradient:** Flat vector design with the specified locked vector gradient, no shadows, no texture, no text. Clean editable vector paths, SVG-friendly, minimal anchor points.
- **hand_drawn_vector:** Intentional hand-drawn vector strokes, approved surface variation, clear scalable silhouette, no shadows, no text.

## Forbidden elements

Honor every `forbidden_elements` entry literally. Never replace one forbidden cliché with another generic symbol.

## Silent validation

Before submitting each Recraft request, silently verify:

- prompt follows the supplied `central_idea` and `visual_mechanism`
- central mechanism is one visual idea stated in one clause
- no metaphors are fused unless the user explicitly requested that exact fusion
- `mark_type` and `treatment` are unchanged
- explicit user style is present and not generalized away
- there is one coherent mechanism
- at least one concrete distinctive element clears the complexity floor
- no brand/designer names appear
- no words appear except explicitly permitted monogram initials
- exact phrase “no text” appears in the constraint tail
- palette uses at most three colors unless the explicit user override is true
- palette is not padded with unnecessary colors
- palette count and role behavior are strict
- geometry is practical for SVG generation
- forbidden elements are absent
- no camera or unsupported texture language appears

If any check fails, rewrite the prompt before submitting it.
