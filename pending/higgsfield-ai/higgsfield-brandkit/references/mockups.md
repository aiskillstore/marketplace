# Mockups

Create believable applications of the Brand Lock. Preserve the approved logo and colors; do not let the scene generator invent branding.

Before planning, require only an approved logo through the Brandkit state script's `get_logo` action. Read approved palette/visual axes when available or when color/application decisions need them. Require typography only when readable text must appear. Use the exact approved logo path, URL, upload ID, or job ID returned by state everywhere; never substitute a newer generation or a recreated mark.

Mockups are rendered images, not fully editable layered documents. If the user needs editable source artwork, use that asset's dedicated reference (for example `packaging.md` or `social-templates.md`) first.

## Plan the application from brand input

Use the approved Brand Lock, user brief, persisted visual axes, preferences, and uploaded references before choosing mockup objects, materials, framing, or art direction.

- Choose applications people in that category credibly use.
- Extract useful composition/material cues from user-provided references.
- Never recreate a reference's exact scene, layout, or branded object.

Each mockup needs one clear art-directed idea tied to this brand. “Put the logo on a generic object” is not a concept.

## Anti-slop rules

Avoid the common synthetic/generic look:

- Arbitrary gradients or neon glows unrelated to the Brand Lock
- Plastic sheen on every material
- Floating products and physically meaningless props
- Excessive bloom, haze, depth of field, or cinematic lighting
- Generic marble/pedestal “luxury” staging
- Fake microcopy, pseudo-labels, invented claims, or decorative UI
- Impossible folds, embossing, reflections, print edges, or scale
- Too many props competing with the branded surface
- Warped logos or a different visual device in every mockup

Prefer believable materials, restrained lighting, purposeful negative space, specific environments, and one focal branded application.

## Required Seedream route

Use **Seedream** as the primary mockup generator. Soul models are forbidden. GPT Image 2 is allowed only as the conditional text/detail application stage below.

Before generation, run `higgsfield model get seedream_v5_pro --json`. If that id is absent, inspect `higgsfield model list --image --json` and use the highest/newest Seedream tier it returns. Follow the live schema; request the highest supported resolution/quality tier and use the same Seedream model for every mockup in the set.

## Ask for aspect ratio

Before submitting any mockup job, ask which ratio the user wants unless their current request already states it. Offer supported choices such as 1:1, 4:3, 3:4, 16:9, 9:16, 3:2, and 2:3; validate the answer against the live model schema. For several mockups, use one ratio for the set unless the user assigns ratios per item. Lock the selected ratio across every stage.

### Existing photograph

When the user explicitly supplies the exact photograph to mock up, pass it as `Image0` and the selected logo variant as `Image1`. Use Seedream for symbol-only applications; use GPT Image 2 when the final image contains readable text. Preserve subject, camera, lighting, materials, folds, shadows, perspective, crop, background, and selected ratio.

## Logo variant routing

Call the Brandkit state script's `get_logo` action and use one of its exact approved variant assets:

- Full-color logo: smooth surfaces and production methods that credibly support accurate multicolor printing.
- Black monochrome logo: light kraft paper, natural cardboard, pale fabric, stamps, dark-ink screen printing, engraving masks, and light uncoated stock.
- White monochrome logo: dark paper, dark boxes, dark fabric, reverse marks, light-ink screen printing, and dark signage.
- Embossing, debossing, foil, laser engraving, and one-color printing always use a monochrome variant. Never send the full-color mark as the application reference for those processes.

Only after the user confirms a mockup whose physical production requires one-color/reverse artwork, run `python3 "$SKILL_ROOT/scripts/brandkit.py" logo-export` with `include_monochrome: true` and the approved color SVG when the required variant is absent. Never pre-generate monochrome assets for future mockups. Never ask Seedream to invent/recolor them or use manual SVG edits.

## Seedream prompt contract

Pass references with repeated CLI `--image` flags; `Image0` is the first flag, `Image1` the second, and so on. For a new scene, pass the exported PNG of the selected logo variant as `Image0`; add approved product/artwork references afterward. For an existing photograph, use the photograph as `Image0` and logo PNG as `Image1`. State each role explicitly. Local PNG/JPG paths auto-upload. Never pass an SVG path as an image reference.

```text
[CREATE ONE FINISHED BRANDED MOCKUP]
<specific object/application, credible setting, camera, material, lighting,
composition, and one brand-specific art-direction idea>

[AUTHORITATIVE LOGO]
<ImageN> is the exact approved <full-color/black/white> logo. Preserve its
spelling, silhouette, geometry, proportions, internal negative space, and exact
color. Do not redraw, simplify, crop, stretch, outline, or add effects.

[PLACEMENT LOCK]
Target surface: <exact object panel/face/material>.
Position: <exact alignment and location, e.g. horizontally centered, upper
third, optical center aligned to panel>.
Scale: logo occupies <specific proportion> of the target surface while keeping
<specific clear-space margin>.
Orientation: align to <panel edge/seam/baseline>; follow surface perspective
without changing logo proportions.
Color: use the supplied <full-color/black/white> variant exactly. State why it
contrasts correctly with the material/background.

[PHYSICAL APPLICATION]
Render the logo using <credible print/emboss/foil/engraving/ink behavior>.
Respect folds, grain, perspective, occlusion, reflections, scale, and
manufacturing limits.

No extra logos, pseudo-text, invented labels, warped marks, floating print,
unrelated props, arbitrary gradients, plastic sheen, or generic luxury staging.
```

The prompt must contain concrete placement, scale, alignment, clear-space, color-variant, and material-application instructions. “Place the logo on the bag/box” is insufficient.

Use `--wait --json` and retain the final job ID and result URL. Do not download and re-upload the same result unless a receiving stage requires a local file.

Typical one-stage call:

```bash
higgsfield generate create seedream_v5_pro \
  --image "$BRANDKIT_WORKDIR/logo/approved-logo-2048.png" \
  --prompt "<complete Seedream prompt contract>" \
  --aspect_ratio 3:4 \
  --resolution 2k \
  --wait --json
```

Replace ratio and resolution only with values confirmed by the live schema.

## Conditional text/detail route

If the final mockup contains any readable text—wordmark, brand name, tagline, packaging label, signage, product copy, or interface text—do not ask Seedream to render it:

1. Seedream creates the same-ratio scene with the target surface blank and no logo, letters, pseudo-text, or invented graphics.
2. Submit GPT Image 2 with the Seedream job ID as the first `--image` and approved logo/artwork PNG as the second `--image`.
3. The GPT prompt preserves Image0's camera, crop, objects, lighting, material, folds, shadows, perspective, and background exactly.
4. State the exact literal text, logo variant, placement, scale, alignment, clear space, color, and physical print/application behavior.
5. Keep the ratio identical to the user-approved ratio.

```bash
higgsfield generate create gpt_image_2 \
  --image "<seedream-job-id>" \
  --image "$BRANDKIT_WORKDIR/logo/approved-logo-2048.png" \
  --prompt "<exact controlled text/detail application prompt>" \
  --aspect_ratio 3:4 \
  --resolution 4k \
  --wait --json
```

Use GPT Image 2 only for this controlled second stage. If there is no readable text, keep the one-call Seedream route.

## Deterministic compositing

Prefer deterministic placement over generative editing when:

- The target is a flat poster, screen, card, sign, or front-facing package
- The source logo already has transparency
- No physical deformation, folds, reflections, or occlusion are required

Use image/SVG tooling to scale and place the official logo exactly. Preserve clear space and color. Add masks/perspective only when they can be controlled reliably.

Use Seedream directly when the branding must interact with:

- Fabric folds
- Curved packaging
- Embossing/debossing
- Foil, print texture, reflections, or surface wear
- Occlusion and realistic perspective

If Seedream corrupts the logo, retry once with stronger placement, geometry, and color constraints while keeping the same references. If it fails again, stop and use deterministic compositing when possible.

## Mockup-specific guidance

### Packaging

- Use the actual dieline/package proportions when supplied.
- Preserve material, closure, label area, and required legal/copy regions.
- Do not invent claims, ingredients, certifications, or regulatory text.

### Apparel/merch

- Use Seedream for the finished branded person/garment mockup.
- Define print/embroidery location, size, and material behavior.
- Preserve the person and garment between variants.

### Signage/environment

- Respect viewing distance, perspective, mounting, and lighting.
- Use the correct approved logo version for background contrast.

### Device/screen

- Treat the screen graphic as a separate editable asset from its dedicated module when possible, then composite it into the device.
- Do not ask GPT to invent interface copy that should be exact.

## Variant discipline

For several mockups:

- Lock one base scene per mockup family.
- Vary only the requested application or colorway.
- Keep camera, lighting, material, and composition fixed for comparison sets.
- Do not generate a new person or environment for every colorway.

## Mockup QA

- Official logo matches the reference exactly
- No misspelling, extra glyph, warped geometry, or invented mark
- Correct colorway and sufficient contrast
- Physical application follows folds/perspective/material
- No floating print, impossible reflections, or duplicated graphics
- One brand-specific art-directed idea; not a generic logo-on-object scene
- Materials, props, lighting, and setting are credible for the industry
- No arbitrary gradients, plastic sheen, bloom, fake microcopy, or generic luxury staging
- When an existing photograph was supplied, every non-target scene element is unchanged
- Product/package proportions match supplied references
- All mockups use the same Brand Lock
- Rendered output is clearly labeled as non-editable unless a separate editable overlay/template is also delivered

After QA, ask the user to approve the final mockup or set. Only then save it with the Brandkit state script's `approve_brandbook_element` action and `required_slots: ["logo"]`; add palette/typography only when the mockup actually used them. Generated or model-praised mockups are drafts until that approval.
