# Prompt guide — Gemini Omni

This model returns video with synchronized native audio in a single pass. It follows both simple and complex instructions faithfully, reasons about real-world physics as it animates a scene, and — its defining trait — lets you refine a clip through natural-language conversation: describe a change and it is applied while the rest of the video is preserved. It also renders on-screen text more reliably than most, so treat legible words in the frame as something you can ask for directly.

## The prompt shape

Write the prompt with concrete detail across these elements:

- **Scene description** — the subject, the setting, and the mood you want established.
- **Subject motion** — what the subject actually does, described specifically rather than as a vague request to "make it move".
- **Camera movement** — how the shot is framed and how the camera travels.
- **Lighting and mood** — the quality of light and the emotional register of the scene.
- **On-screen text** — any words that should appear, given as the exact string to render.
- **Audio** — the sound the scene should carry (see below).

Favor real-world, filmmaking, and photography terms the model already understands over invented language; lean on its world knowledge rather than over-specifying every pixel.

## Camera language

Name shots and moves in plain, standard vocabulary — a continuous smooth shot, a handheld shot, a pan, a track, a dolly. Ask for a single unbroken take when you want one, using phrasing such as "in a single continuous shot" or "no scene cuts". Direct the camera deliberately; it responds to clear framing and movement instructions.

## Directing motion and physical realism

The model simulates real-world physics — gravity, momentum, the way things move and settle — so describe action in specific physical terms and let that reasoning fill in the rest. You can also stage events across time, either in natural language ("after three seconds, a figure enters") or with explicit timecodes marking what happens in each span of the clip. Complex, high-motion scenes remain the hardest case; keep action legible rather than chaotic.

## Audio

Because sound is generated with the picture, write it into the prompt. Call for background music and set its character (for example, calm, or a high-energy beat), and specify sound design as concrete cues such as a gentle breeze or distant birdsong. Dialogue can be directed the same way, and you can suppress sound you don't want with a direct instruction like "no dialogue" or "no extra sound effects".

## Keeping unwanted things out

State exclusions as plain instructions inside the prompt — "no dialogue", "no embellishments". When you are changing an existing clip, add "keep everything else the same" so the edit stays local and the rest of the frame holds steady.

## Working from a start frame, references, or a clip to edit

A supplied image can serve as the literal opening frame or as a looser visual reference; when it is a reference, say so, since the model will otherwise be inclined to treat it as the first frame. For animating a still, give a high-resolution image and describe the motion you want specifically rather than restating what the image already shows.

Editing is where this model is strongest: describe what you want changed — a restyle, an added object, different lighting, corrected on-screen text — and it applies the change while preserving the parts you keep. Keep edit prompts simple; over-describing an edit invites unintended changes. Refinement is meant to be iterative, one conversational adjustment at a time.

## Best practices and failure modes

Be detailed and precise for generation, but simple and surgical for edits — the two modes reward opposite instincts. Supply high-resolution inputs and specific motion descriptions. Expect the rough edges the model itself calls out: complex motion is difficult, on-screen text is not always perfectly accurate, and full visual consistency across successive edits is not guaranteed, so verify identity and details after each change.
