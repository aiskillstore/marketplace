# Prompt guide — Wan 2.7

Wan 2.7 is built for smooth, coherent motion and high scene fidelity, with synchronized native audio. It reasons over the prompt before generating, so precise wording pays off directly. Write directions to a scene, not a list of objects, in plain natural language rather than a rigid template.

## Prompt shape

There is no fixed formula; describe the scene in order of what matters most, front-loading what must be preserved. A strong single-shot prompt tends to cover these elements:

- **Subject** — appearance, clothing, expression, and pose of your core subjects, stated first.
- **Scene** — location, weather, time of day, and atmosphere.
- **Motion** — the action, its speed, and its emotional tone.
- **Camera** — framing and any movement.
- **Lighting and tone** — the mood of the light.
- **Style** — the overall aesthetic, such as cinematic, photorealistic, or animated.

## Multiple shots in one clip

To build a sequence inside a single generation, describe each shot directly in the prompt with a time range rather than relying on any shot-type control. Use the model's convention of a numbered shot, a bracketed timestamp, a framing, and a description, for example `Shot 1 [0–3 seconds] wide shot: Rainy New York street at night`. Subjects stay consistent from one shot to the next.

## Camera language

The model reads real cinematography vocabulary. Name the framing (wide shot, medium shot, close-up) and the move (pan, dolly, tracking shot, orbital shot). Left unspecified, the camera holds steady.

## Directing motion and physical realism

Motion comes from concrete action. Describe what moves, how fast, and with what weight; detailed action wording produces more believable physics and fluid movement. State the order in which things happen and what stays still.

## Audio and dialogue

Audio is synchronized to the picture. If you supply a driving audio track, the motion locks to it; with none, the model generates matching background music or sound effects on its own. For spoken lines, write the dialogue naturally into the prompt text; there are no special markers.

## Exclusions

Phrase exclusions as positive description of the scene you want; there is no separate negative field to fill. If a specific artifact keeps surfacing — low resolution, a deformed shape — name the clean state you want instead.

## Working from a start frame, end frame, or references

Treat a supplied start frame as the first frame and describe how the scene unfolds from it. With a last frame, describe the arc toward that final composition. To hold a character's appearance and voice steady, draw on image or video references — with this model they are passed alongside the prompt, not named inside it. When continuing from existing footage, write the action that carries on from where it leaves off.

## Best practices

Describe the scene concretely and lead with what must stay fixed. Keep each idea in its own sentence, prefer genuine cinematography terms over strings of aesthetic tags, and pair a detailed prompt with references whenever consistency across shots or clips matters.
