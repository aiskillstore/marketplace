# Prompt guide — Seedance 2.0

This model writes picture and sound in a single pass, so every prompt is a brief for both at once — and supplied references let you lock a character's look, an action, a visual style, or a voice. Treat the prompt as an engineering instruction — who, doing what, where, shot how, sounding how — not as loose ad copy.

## The prompt shape

Order the elements the way the model expects them:

- **Subject** — who or what is on screen, pinned to two or three stable features so it stays consistent.
- **Action details** — what the subject does and how.
- **Scene and environment** — place, time, weather, and the space around the subject.
- **Lighting and colour tone** — the quality and mood of the light.
- **Camera movement** — framing and how the camera travels.
- **Visual style** — the art style and overall tone.
- **Image quality** — clarity, texture, and lighting register.
- **Constraints** — the boundaries that keep flaws out.

## Camera language

The model reads standard shot vocabulary directly — medium shot, close-up, wide shot, slow push-in, steady lateral track, fixed shot — so name them plainly. Specify only one camera move per shot; asking it to push, pull, pan, and track at once makes the image unstable.

## Directing motion and physical realism

Tie action to specific body parts — hands, head, shoulders, legs, back — and add range, speed, and force. Favour slow, gentle, continuous small movements; the model renders these far better than high-burst, large-dynamic action like sprinting, big jumps, or violent rolls. Carry momentum between actions, using the inertia of one movement to feed naturally into the next. Express emotion through concrete physical detail — posture, breath, where the eyes go, a clenched fist — rather than naming the feeling.

## Audio

Write the soundtrack into the prompt using these markers exactly: dialogue in `{}`, music in `（）`, sound effects in `<>`, and on-screen subtitles in `【】`. Keep one language within a line of dialogue and mark any less common language explicitly, for example `says in Japanese {こんにちは}`. Only marked dialogue drives lip movement. Dialogue is optional — a clip can be scored with only ambient sound, music, or effects and no spoken lines.

## Keeping unwanted things out

There is no negative-prompt field; state exclusions as positive constraint words inside the prompt. The model tends to add subtitles, logos, and platform watermarks on its own, so call them out plainly — "keep it subtitle-free", "do not generate a logo", "do not generate a watermark".

## Working from start frames and references

When a start frame, reference, or first-and-last pair already fixes the look, aim the words at what moves and changes rather than restating what is set; for a frame pair, describe the journey between them. The model needs each reference identified by its slot — Image 1, Video 1, Audio 1 — uploaded in the order you name them; bind a subject to its source with a label such as `Subject 1@Image 1` and reuse that same label every time the subject appears. Give each reference a clear role: anchor a character, set the scene, guide camera movement, or set audio tone.

## Best practices and failure modes

Structure any multi-beat video as an ordered storyboard — Shot 1, Shot 2, Shot 3 — in the order events happen, each headed with its own time span. Keep the spans few and wide rather than many and tight; the instability comes from over-slicing a clip into more shots than it can hold, not from stating when each one runs. Keep references few and purposeful — four to five assets works best, and more than four reference people degrades stability, causing miscounts or duplicated "twin" characters. For a consistent face, use a headshot plus a full-body image rather than multi-view sheets, which the model may read as separate people. Keep the prompt focused and free of contradictions; an over-stuffed prompt confuses the model as much as a vague one does.

Open with the subjects already in place in the first frame rather than on an empty establishing shot — start mid-scene unless a reveal is the point.

A few things reliably trip this model up:

- **Named people, brands, or known characters** — the content filter tends to refuse them, quietly degrade the shot, or swap in something else; describe the look in plain terms (hair, build, wardrobe, expression) rather than naming anyone.
- **Too much happening at once** — several actions together, or motion pushed too fast, and the movement turns rubbery while objects drift or vanish; give it one clear action at a moderate speed.
- **Reflections** — mirror-flat surfaces (mirrors, glass, still water, polished floors) tend to come out as broken, mismatched duplicates of the scene; keep them out of frame, or don't rely on the reflection reading correctly. Moving or turbulent water — crashing surf, rain, ripples — is fine.
- **A weak source image** — a soft, low-resolution, or noisy start frame brings flicker, distortion, or an outright failed clip however good the prompt is; feed it a clean, sharp image.
- **An overloaded prompt** — very long durations and dense, contradictory, or edge-case briefs tend to fail silently; keep the clip short and the wording focused.
- **Stacked style tags** — piling on "cinematic, 4K, epic" does nothing for the look; describe what is actually in the frame instead.
