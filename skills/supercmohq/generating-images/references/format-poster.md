# Promotional graphics

Use this recipe for copy-bearing marketing artwork — posters, ad creatives, social graphics, product mockups, signage — where rendered text must be correct and the layout must hold.

## Visual direction

- **Artifact type** — what the image is; don't leave the model to infer it.
- **Concrete facts over mood words** — observable properties, not praise adjectives.
- **Typography** — font style, size, colour and placement, stated rather than implied. Let one headline dominate, hold the total to two or three text elements, and keep each in high contrast against what sits behind it.
- **Layout and hierarchy** — where each element sits, and which single one leads.
- **Negative space** — how much empty area the design needs to read at any size.
- **Lighting** — the light sources and their quality.
- **Materials and surface** — surface detail and plausible imperfection carry realism.
- **Colour** — give colours as exact hex values (e.g. `#1B4D3E`, `#E8B923`), not colour names, which the model drifts on; rendering is neutral, with no warm cast to correct for.
- **Camera and composition** — angle, framing and mood.
- **Register** — flat colour, deliberate margins, type as a designed element: it should look built in a layout tool.

## Prompt structure

1. **Scene** — location, time, background, environment.
2. **Subject** — the main focus of the frame.
3. **Details** — materials, lighting, camera angle, composition, mood.
4. **Use case** — what artifact this is.
5. **Text** — the exact copy in quotes, with weight, relative size, and where each line sits; reproduce it word for word, never paraphrased.
6. **Constraints** — what must not drift, change or appear.

Write these as short labelled segments on separate lines, not one paragraph. Structure beats length, and inline negation works. The constraint block is the one most prompts skip; it fails silently when empty.

## Working with brand material

Supply brand assets as reference images. Lead with the asset that carries the real mark; without one the model invents a substitute. Label every input by index and role, refer to those labels in the instruction, and say where each element lands. Supplied marks are reproduced faithfully, so you don't need to plead for fidelity. Name both halves of an edit: what changes, and what holds. Make one change per turn.

## Rules

- State exclusions and invariants outright: no watermark, no extra text, preserve geometry and layout.
- Never leave the constraints block empty.
- Put every literal string in quotes or ALL CAPS, require it verbatim, and declare no extra or duplicate text.
- Keep on-image copy short: one headline, one support line, one prompt to act.
- Describe type by its feel; an exact font family rarely renders as asked.
- Spell difficult words letter-by-letter.
- Repeat the preserve list on every iteration and re-state details that drift.
- Transparent background is unavailable — plan a flat background and composite downstream.
- Verify rendered copy; placement and clarity still fail occasionally.

## Producing a set

Generate several variants in one batched call, one request per variant. There is no seed, so consistency comes from restating invariants in every prompt: pin the recurring subject, palette and proportions with repeated constraints, and forbid redesign.
