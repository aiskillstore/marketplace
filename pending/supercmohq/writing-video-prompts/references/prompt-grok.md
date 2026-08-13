# Prompt guide — Grok Imagine Video

This model turns a short written brief into a coherent moving clip with sound baked in — dialogue, foley, ambience, and music produced in the same pass as the motion and kept in sync. It is strongest when a still image anchors the shot. It rewards focused, director-style briefs and front-loads — what you describe first is rendered first — so lead with the moment that matters and keep the whole prompt tight.

## Shape of a strong prompt

Order these elements; the first twenty to thirty words carry the most weight, so aim for roughly 30 to 60 words overall.

- **Subject and primary action** — who or what is in frame and the one thing that happens; state it in the opening sentence.
- **Camera move** — name the shot and how it travels; without this the framing stays locked by default.
- **Atmosphere and lighting** — mood, light quality and direction, time of day, colour.
- **Audio** — one line describing what the scene should sound like.
- **Preservation** — what must stay unchanged, placed last.

## Camera language

Name a specific move every time rather than leaning on "cinematic." Understood terms include dolly, push-in, orbit, pan, handheld, crane, tracking shot, macro, and rack focus, along with plain descriptions such as a slow push-in, a gentle drift left, or a locked static frame. Pick one move per clip.

## Directing motion and physical realism

Use strong, specific verbs — surges, unfurls, crumbles, drifts, shatters — over "moves" or "goes." Describe progression and intensity rather than a single state; for example, walking that starts slow and builds, with the background responding in kind. Keep to one clear action per clip: a single intent renders more cleanly than three competing ones.

## Audio

Describe sound as its own line, separate from the visual direction, and be granular — name the materials and sources you want (footsteps, fabric, mechanical clicks, distant traffic, room tone, or explicit silence). Mapping a specific sound to a specific on-screen action reads best. Setting audio off with a delimiter such as `AUDIO:` at the head of that line is an optional aid that helps separate sound from picture; a plain dedicated sentence also works.

## Exclusions

There is no negative-prompt field, and instructions about what to leave out are unreliable. Phrase everything positively: describe the exact state you want to see rather than the thing to avoid.

## Working from a frame, reference, or existing clip

When a start frame or reference sets the composition, let the prompt describe only what changes and pin the rest with preservation language — hold the composition, keep the face and outfit, preserve a label. Prepare a strong, well-composed still first; separating the fixed picture from the motion brief makes each easier to iterate.

## Best practices and failure modes

Keep prompts focused — one moving subject, one camera path, specific verbs. Skip generic quality tags such as "8K" or "highly detailed." Change one variable at a time between takes. Shorter clips hold together and stay best synchronised. Common failures are omitting the camera move, stacking unrelated actions, vague motion, dropping the audio line, and forgetting preservation when identity or a product must survive.
