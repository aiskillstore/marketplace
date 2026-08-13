# Prompt guide — Veo 3.1

This model turns a written brief into a short clip with picture and sound generated in the same
pass, and it locks audio to the picture — multi-person dialogue with matched lip movement and
precisely timed effects. Treat the prompt as direction, not ad copy.

## The order to write in

Lead with the camera, then the subject, then the action, then the setting, then the look. A strong
prompt carries these elements in this order:

- **Cinematography** — the shot size, angle, and camera move that frame everything else.
- **Subject** — the person, animal, object, or scenery at the centre of the shot, named by a few
  stable features so it holds across the clip.
- **Action** — what the subject is doing, in concrete verbs (walking, turning their head, reaching
  out).
- **Context** — the environment and background around the subject.
- **Style and ambiance** — the overall aesthetic, plus how colour and light set the mood: warm
  tones, night, a blue cast.

## Camera language

The model reads standard film vocabulary without translation. For position and movement, use terms
like aerial view, eye-level, top-down, worm's-eye, dolly, tracking, crane, slow pan, or POV. For
framing, use wide shot, close-up, extreme close-up, low angle, and two-shot. For lens and focus,
use shallow focus, deep focus, soft focus, macro lens, and wide-angle lens. Name one camera move
per shot and let it complete.

## Motion and pacing

Describe action in plain, specific verbs tied to the subject. To choreograph several beats in a
single generation, split the clip into timestamped segments and describe each in turn, opening each
with its own shot; write the ranges as `[00:00-00:02]`, `[00:02-00:04]`, and so on. Keep any single
beat — and any line of dialogue — short enough to land inside the clip's length.

## Audio

Write sound into the same prompt using its markers. Put spoken lines in quotation marks — for
example, "This must be the key," he murmured — and the delivery drives lip movement. Prefix a sound
effect with `SFX:` and describe it (SFX: thunder cracks in the distance). Prefix a background
soundscape with `Ambient noise:` (Ambient noise: the quiet hum of a starship bridge). State plainly
whether you want dialogue, effects, music, or silence rather than leaving it to inference.

## Excluding things

There is no separate field for what you don't want. Fold exclusions into the prompt as positive
description of the scene you do want — describe an empty landscape by what fills it.

## Working from frames and references

When a start frame fixes the opening look, aim your words at the motion and change that follow
rather than restating what the frame already shows. Moving between two held frames, describe the
transition that carries one into the other. When you draw on reference images — for a character, an
object, or a style — name each one inside the prompt as you call on it, for example "Using the
provided images for the detective, the woman, and the office setting, create a medium shot…".

## What the model rewards

Write with descriptive adjectives and adverbs so each element is unambiguous. To sharpen a face,
make it the focus and call for a portrait. Keep the brief specific and internally consistent —
vagueness and contradiction both weaken the result.
