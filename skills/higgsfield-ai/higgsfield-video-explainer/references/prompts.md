# Prompt Templates

Write every image and video prompt in English. Write only narration in the user's selected language.

Two elements keep the film consistent: one style-key image attached to every clip, and one identical STYLE descriptor pasted into every clip prompt. Narrate per block so each voice take maps to exactly one 10-second clip.

## STYLE descriptor

Write the render style, palette, line character, and finish once. Always end with:

```text
non-photorealistic, illustrated, not a photo, no live-action, no realism
```

Examples:

- `flat 2D vector animation, bold clean outlines, solid vibrant flat fills, no shading, no gradients`
- `hand-inked black marker on off-white paper, solid jet-black fills, thin white scratch highlights, marker grain, strictly monochrome`
- `strict monochrome minimalism, black silhouettes on white void, high contrast, lots of negative space`
- `hand-painted storybook gouache, soft textures, warm muted palette, visible brush strokes`

## Style key

### Abstract swatch

```text
Pure {STYLE} STYLE REFERENCE plate. No characters, no faces, no people, no objects, no scene, no letters—an abstract style swatch only. A balanced arrangement that demonstrates the rendering grammar clearly: {line quality}, {fill behavior}, {highlight/edge behavior}, {texture/grain}. {palette constraint, with hex if strict}. High contrast, clean background, generous negative space. Flat, raw, hand-illustrated, non-photorealistic. No text, no logos, no watermark.
```

### Mascot key

```text
{STYLE}. Full-body character: {HOST}—a {species/persona} narrator, expressive, clear readable silhouette, looking at camera, centered, simple background. Recurring-character design. No text, no logos, no watermark.
```

### With style-reference images

Prefix the prompt verbatim, then add the requested swatch or mascot instructions:

```text
Make an Animated Explainer. Take only the visual render style and color grading of the input image(s); mix the styles if there is more than one image. Never use the characters, inscriptions, etc. from the input image(s) unless the instructions below ask you to. Use only the render style, and follow the user's instructions below:
{raw user query / scene}
```

Use references as style donors only. Never copy their people, text, logos, or objects.

## Video block

```text
Block N
STYLE REFERENCE: Match the attached reference image EXACTLY. Replicate its look precisely: {STYLE tokens}. Every element below rendered in that identical style.
SCENE: {scene and one clear action matching Block N narration}.
MOTION: {camera move and animation behavior—slow push-in, drift, scale shock, hard contrast cut}.
AUDIO: {ambient SFX or music only—NO voice, dialogue, or narration}.
NEGATIVE: color drift, photorealism, 3D render, lip-sync, captions, on-screen text, logos, watermark{, plus style-specific bans}.
```

Rules:

- Paste the same STYLE tokens into every block.
- Keep clip audio diegetic only. Characters never speak or lip-sync.
- In mascot mode, Block 1 greets by gesture with mouth closed, the final block waves a sign-off, and middle blocks use the same design.
- In faceless mode, every block is a stylistic scene of its narration beat.
- Use one clear action per block.

Example:

```text
Block 4
STYLE REFERENCE: Match the attached reference image EXACTLY. Replicate its look precisely: strict monochrome minimalism, solid black silhouettes on an absolute white void, high contrast, lots of negative space, matte, non-photorealistic, illustrated, not a photo, no live-action, no realism. Every element below rendered in that identical style.
SCENE: A lone black silhouette slowly dissolves at the edges, crumbling into fine drifting sand that scatters into the white emptiness.
MOTION: Very slow push-in; the figure erodes grain by grain and particles drift sideways.
AUDIO: Low sustained drone and a soft whisper of falling sand—no voice.
NEGATIVE: color, gray midtones, photorealism, 3D render, lip-sync, captions, on-screen text, logos, watermark.
```

## Narration block

Write one plain line per clip, sized for about 8–9 seconds and normally 20–24 words. Keep every take under roughly 9.5 seconds.

```text
Block 1
For four and a half thousand years, the pyramids of Egypt have stood against the desert, silent and immense.
Block 2
They rose along the Nile, the river that fed a civilization ruled by pharaohs believed to be living gods.
```

Rules:

- Use no timecodes, emotion cues, parentheticals, or stage directions.
- Spell numbers out.
- Set tone through word choice and concrete detail.
- Never say “in this video.”
- For a topic, hook, build understanding block by block, and end on the payoff.
- For a personal story, keep the user or their narrator persona as protagonist and invent nothing factual.
