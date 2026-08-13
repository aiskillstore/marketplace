# Prompt guide — Kling 3.0

Kling 3.0 is built for cinematic, multi-shot video with strong subject consistency and synchronized native audio. It reads like a director's script: tell it what moves, what stays still, where the camera points, and what is heard. Write directions to a scene, not a list of objects.

## Prompt shape

Order a single shot roughly as these elements:

- **Subject** — name and describe your core subjects at the very start; keep the wording identical if they recur, so faces and outfits stay consistent.
- **Action** — what the subject does, carried by concrete motion verbs (see below).
- **Camera** — framing and any movement.
- **Setting and atmosphere** — location, light, time, mood.

Keep each sentence to one idea. Two to five short, punchy sentences outperform one long compound sentence.

For a sequence, split it into shots rather than cramming everything into one paragraph. Give each shot its own framing, subject, and motion; the shots return stitched into one continuous video.

## Camera language

The model responds to real cinematography vocabulary. Name the framing (close-up, macro close-up, wide angle, profile shot, POV) and the move (slow push-in, tracking shot, dolly zoom, rack focus). Describe the camera's relationship to the subject: following it, staying in a medium shot, freezing when it pauses, then resuming smoothly. For dialogue, shot-reverse-shot is understood. Left unspecified, the camera stays static or drifts subtly.

## Directing motion and realism

Motion comes from verbs. Do not write "a bird in a field"; write that the bird takes flight from a wheat stalk, wings catching the light as it rises. State explicitly what moves and what holds still, and the order in which things happen. Camera moves and physical action behave like real cinematography. Shorter clips hold tighter, more consistent motion; longer ones give the model more room to drift, so reserve the long durations for genuine narrative development.

## Audio

Audio generates by default and syncs to the picture. Give each speaker a unique, consistent label and bind their line to an action, using the convention `[Character A: role, tone/voice qualities]: "dialogue here"`. Add vocal direction inside the label (for example a hesitant voice or a cold, controlled tone). Use `Immediately,` to tighten the timing between a beat and the line that follows. Write ordinary speech in lowercase and reserve uppercase for acronyms and proper nouns.

## Exclusions

Phrase exclusions as positive description of the scene you want; there is no separate negative field to fill. If a specific artifact keeps appearing — a warped face, a jittery camera — name the clean state you want instead.

## Working from a frame or reference

Treat a supplied start frame as an anchor and describe how the scene evolves from it, keeping any text and signage intact. Add an end frame to steer a controlled transition toward a target final composition. When you supply reference elements — a frontal image plus optional extra angles, or a motion clip — refer to them in the prompt text by the model's tags `@Element1`, `@Element2`, and so on; this keeps three or more distinct characters in a scene without blending their faces or outfits.

## Best practices and failure modes

Describe the scene; strings of aesthetic tags like "cinematic, 4K, dramatic lighting" do nothing. Trust the default guidance strength for most work, raising it only for scenes with strict spatial requirements and lowering it for more creative latitude. If characters blend or details wander, simplify the wording and lean on consistent subject labels and references.
