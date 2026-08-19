---
name: ip-as-logo
description: Generate highly simplified personified IP mascot logos with Flat-first geometry, rounded heavy forms, two purposeful IP colors over one solid background color, and ultra-light neo-skeuomorphic internal modeling. Use when creating an animal, creature, robot, ghost, plant, object, or other character as a minimal square logo or app-icon artwork, including when the agent should infer three product-relevant directions and propose six independent candidates for approval.
---

# IP as Logo

Create a logo first and a character second. Reduce the subject to a compact symbol that remains recognizable at `32 × 32`; do not produce a character illustration.

## Workflow

1. Parse the request for an explicit IP subject and available product context. Do not ask the user to choose a color mode unless they explicitly want to control it.
2. When the user has not specified an IP subject and the current workspace is a product repository, inspect relevant read-only context before asking questions. Prefer the README, product docs, package or app metadata, landing-page copy, manifests, and design tokens. Treat context as sufficient when the product purpose, primary audience, and intended personality can be inferred with reasonable confidence.
3. When product context is insufficient, ask one consolidated round of background questions covering what the product does, who it serves, and how it should feel. Do not start a second background questionnaire. Continue with the best supported interpretation after the answer.
4. Once context is sufficient, always present three concise directions before generation and explicitly propose generating six independent logo candidates in one batch. Do not generate until the user agrees, unless the current request already explicitly authorizes six outputs or asks the agent to proceed without another confirmation.
5. Choose the three proposed directions deliberately:
   - When the user explicitly specifies an IP subject, keep that subject and propose three distinct design treatments based on composition, silhouette treatment, secondary color region, or personality emphasis.
   - When the user does not specify an IP subject, propose three genuinely different IP subjects or metaphors. Tie each one to a different product attribute or brand promise; do not return three arbitrary animals with no rationale.
6. Interpret the user's response exactly:
   - If the user accepts all three directions and the six-image proposal, generate two independent variants per direction and label them `A1`, `A2`, `B1`, `B2`, `C1`, and `C2`.
   - If the user selects one direction but accepts six images, generate six controlled variants of that direction and label them `A1` through `A6`.
   - If the user rejects the proposed quantity, directions, or distribution, follow the user's replacement instructions without arguing for the default.
7. Default every candidate to exactly three semantic colors in the complete artwork: exactly two IP base colors plus exactly one background color. Reuse the two IP colors for facial marks and internal modeling rather than introducing additional semantic colors. Follow an explicit user request for another color count. Keep required product cues, identifying features, complexity limits, and any supplied palette consistent enough for useful comparison.
8. Determine the available image-generation path before promising output. In Codex, use ImageGen when it is available. In any other agent environment, use an available configured image generator; if none is available, ask the user whether they can provide or enable one. Do not fabricate generated results.
9. If the runtime supports subagents, parallelize the six independent candidates up to the available concurrency. Give every subagent the same product brief, shared constraints, and one assigned direction or variant; run remaining candidates in subsequent waves when capacity is limited. If subagents are unavailable, generate the candidates through separate image-generation calls or jobs.
10. If the user supplies a background palette, reserve every supplied color for backgrounds unless they explicitly say otherwise. Choose exactly two IP base colors independently for the subject and context unless the user also assigns subject colors. Do not treat any historical or example palette as a closed list of allowed backgrounds.
11. Abstract each subject using the complexity budget below. Generate every candidate as a separate full-resolution square asset; never ask an image model to compose a contact sheet, grid, or multi-logo image. Do not use existing logos or sibling candidates as image references when testing prompt-only reproducibility.
12. Inspect every output against every evaluation rule. Retry with one targeted correction when practical; never hide a failed constraint with silent post-processing. Treat a transparent or absent background as an allowed output variation unless the user explicitly requires an opaque background.
13. Preserve and label every generated result, whether its background is opaque or transparent. Report every label, IP direction and rationale, saved path, prompt/color mapping, dimensions, background mode, and remaining deviations. Present all results together and ask which candidate the user wants to refine.

When proposing directions before generation, describe each in one compact line: `<IP subject> — <product connection> — <defining silhouette>`. End with a direct proposal to generate six images using the distribution above. Do not turn the discovery phase into a long branding workshop unless the user asks for one.

## Complexity budget

- Build one dominant continuous outer silhouette from roughly `6–10` basic geometric shapes.
- Use at most one species-defining feature: for example, one large pouch beak, one pair of curled horns, or one broad visor.
- Use at most two broad internal color regions corresponding to the two IP base colors. Keep the face to two eyes and one mouth; omit eyebrows, highlights, nostrils, texture, and decorative marks unless essential.
- Prefer a head or compact upper-body crop. Do not explain the full anatomy, costume, machinery, or story.
- Remove repeated feathers, scales, fur tufts, armor plates, buttons, screws, numbers, labels, and other illustrative detail.
- Require a readable black silhouette and recognizability at `32 × 32`.

## Shape language and composition

- Use thick, rounded, weighty contours and broad color masses.
- Forbid sharp corners, pointed ears or beaks, needle-like tails, thin antennae, thin smiles, narrow gaps, and acute flame or feather tips. Replace every necessary tip with a visibly blunt rounded end.
- Show both members of paired identifying features, such as ears, horns, wings, gills, or bells.
- Let the IP emerge from the lower-left or lower-right corner and fill about `75–85%` of the canvas. Cropping at the bottom or side is intentional, but do not crop an identifying paired feature.
- Keep the artwork upright; never rotate the logo canvas or tilt the main mark without an explicit request.

## Flat-first, ultra-light neo-skeuomorphism

- Start from flat semantic shapes and a strong, simple silhouette. The first read must remain a clean Flat-first graphic mark.
- Add only `8–12%` extremely subtle internal tonal modeling inside the IP. Keep the result barely neo-skeuomorphic and composed mostly of flat graphic masses.
- Let the image model realize that restrained tonal change naturally. Do not prescribe a gradient location, direction, span, edge width, highlight count, shadow count, or numerical hue/chroma shift.
- Keep small facial marks simple and subordinate. Do not add glossy hotspots or detailed cavity rendering to eyes, mouths, noses, or other tiny features.
- Keep the background visually flat and uniform. Apply tonal modeling only inside the IP, never as a background vignette, spotlight, or directional gradient.
- Never add an external cast shadow. Avoid dramatic bevels, deep occlusion, glossy highlights, extrusion, photorealistic material rendering, or an obviously volumetric result.
- Reject clay, inflatable, plastic, plush, toy-like, photorealistic, or strongly three-dimensional results.

## Color and canvas

- Default to exactly three semantic colors in the complete artwork: exactly two IP base colors plus exactly one background color. Closely related tonal variants created by the allowed internal modeling remain part of their underlying IP color family and do not count as extra semantic colors.
- Choose the two IP colors from the product context, subject identity, intended personality, and user request. Organize both into broad purposeful masses; reuse one for facial marks and keep the other in one continuous defining region rather than scattering decorative fragments.
- Choose both subject colors independently from the background. Favor clear, lively subject colors when appropriate, but do not impose global saturation, OKLCH, hue-shift, or chroma bands on the IP.
- Choose the background freely for the context or from a user-supplied palette. Historical palettes and examples are suggestions only, never an allowlist or mandatory default palette.
- Preserve clear visual separation between the dominant IP silhouette, its facial marks, and the background. If a user-supplied background causes weak separation, adjust the subject colors first rather than replacing the requested background.
- Across a batch, vary the two-IP-color strategies deliberately instead of repeating the same neutral-heavy combination.
- Keep related highlight and shade variants within the visual family of their underlying subject color. Do not introduce an unrelated hue under the label of shading or split one color into conspicuous stacked layers.
- Keep an opaque background visually solid and uniform; report visible vignettes or directional gradients rather than silently flattening them in post-processing.
- Request a fully opaque, edge-to-edge background by default. Keep the selected background visibly present in all four corners and every open area around the IP, with normal square outer corners. Preserve and report a transparent result when the generator returns one.
- Generate a direct `1:1` square with square outer corners. Request approximately `1536 × 1536`; accept and preserve a native `1254 × 1254` result when that is the service output limit. Never resample merely to reach the requested number.

## Prompt skeleton

### Route constraints by generator capability

Determine the available image model and its actual tool schema from runtime metadata, configured provider documentation, or an explicit user statement. Do not guess a model or invent unsupported parameters.

- For modern instruction-following image models such as GPT Image 2, Nano Banana Pro, and Seedream 5.0 Pro, keep the complete positive prompt and express the minimal exclusions as the natural-language `Constraints:` line inside the main prompt. Do not create a separate negative-prompt payload for these models.
- For an older model or runtime that explicitly exposes a dedicated parameter such as `negative_prompt`, keep every positive prompt line unchanged and deliver the minimal exclusions through that dedicated parameter in the syntax required by the available adapter. Omit the natural-language `Constraints:` line from the main prompt to avoid duplicating the same exclusions in both channels.
- For an older model without a dedicated negative-prompt parameter, follow its documented prompt format. When only one prompt string is available, retain the concise natural-language `Constraints:` line.
- Record the model or provider, the detected constraint-delivery mode (`main-prompt constraints` or `dedicated negative parameter`), and the exact constraint text or payload in the generation report.

When a dedicated legacy negative-prompt parameter is available, adapt this minimal payload to its required syntax:

```text
text, watermark, borders, frames, cards, App-icon masks, extra subjects, scenery, thin fragile lines, sharp tips, photorealistic materials, strong three-dimensional rendering, external cast shadows
```

For modern instruction-following models and single-prompt interfaces, use the following complete prompt:

```text
Create one complete full-bleed 1:1 square IP mascot logo artwork.
Backdrop: cover the entire canvas with one visible, fully opaque solid <background>. Keep <background> clearly visible in all four square corners and every open area surrounding the mascot.
Subject: place one highly simplified <subject> mascot over the backdrop, reduced to one rounded continuous silhouette and one defining feature.
Complexity: use 6–10 broad basic shapes, at most two broad internal color regions, and a face with two eyes and one mouth. Keep the symbol readable at 32 × 32.
Color behavior: use exactly three semantic colors in the complete artwork: exactly two IP base colors plus the backdrop color. Choose the two IP colors from the subject and context, organize both into broad purposeful masses, and reuse them for facial marks. Choose the backdrop independently or follow the user's supplied background. Keep the IP, facial marks, and backdrop clearly separated. Treat any example palette as optional inspiration, never as an allowlist. Closely related tonal variants used for the ultra-light internal modeling do not count as additional semantic colors.
Composition: keep the mascot upright, emerging from the lower-left or lower-right, filling 75–85% of the square, with both paired identifying features visible.
Style: use an ultra-clean Flat-first logo treatment with minimal graphic masses and only 8–12% extremely subtle internal tonal modeling inside the IP; barely neo-skeuomorphic, thick, soft, restrained, and scalable. Keep the result mostly flat. Do not prescribe a gradient location, direction, span, edge width, or number of highlights and shadows.
Finish: show only the mascot over the full-canvas backdrop, with clean geometric surfaces and normal square outer corners.
Constraints: Use no text or watermark. Add no borders, frames, cards, or App-icon masks. Include one mascot only, with no extra subjects or scenery. Keep the contours thick and rounded, without fragile lines or sharp tips. Add no photorealistic material, dramatic bevel, glossy hotspot, deep occlusion, extrusion, strong three-dimensional rendering, or external cast shadow. Keep the background flat, with no gradient, texture, vignette, or lighting variation.
```

## Mark as non-recommended when

- It reads as an illustration rather than a symbol, exceeds the complexity budget, or fails at small size.
- Without an explicit user override, the result does not use exactly two IP base colors plus one background color, or it scatters the second IP color into decorative fragments that weaken the symbol. An absent backdrop color in a transparent result is an allowed variation.
- The chosen palette reads gray, muddy, washed out, or poorly separated with no explicit user or product reason.
- A color explicitly supplied for background-only use appears as a painted IP region.
- The background or facial marks have insufficient visual separation from the subject.
- Any contour is thin, sharp, spiky, or visually fragile.
- An ear, horn, wing, gill, bell, or other paired identifier is missing or cropped.
- The IP is too small, centered like a sticker, tilted, framed, or surrounded by excessive empty space.
- The internal tonal modeling is materially stronger than the intended `8–12%` extremely subtle variation or makes the result read as a rendered object.
- The result becomes noticeably volumetric, inflated, molded, or fully shaded instead of reading as an almost-flat mark with ultra-light internal softness.
- An opaque background visibly becomes a scene, texture, halo, vignette, or strong gradient rather than reading as a solid field.

Background transparency by itself is permitted and must not make a result non-recommended. State the exact evaluation findings for every candidate, preserve both opaque and transparent results, and present them together without silently repairing either mode with code.
