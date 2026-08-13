# Prompt guide — seedream-5

Built for edits that must keep something recognisable — a face, a garment, a logo — while the rest of
the frame changes. It reads several supplied images at once and can carry an element or a line of
text from one into another. A prompt is always required, even when editing with references.

## Writing the prompt

Address supplied images by figure number in `image_urls` order (`Image 1` upward) to move an element or text between them. Ten maximum; extras dropped.

- **Subject** — who or what the frame is about.
- **Action or pose** — what it is doing.
- **Setting** — where it sits and what surrounds it.
- **Style** — the artistic or photographic treatment.
- **Lighting and atmosphere** — mood, which this model tracks closely.
- **Camera** — lens, perspective, framing.
- **On-image text** — the exact string in quotes, its placement, a legibility cue; keep it short.
- **Constraints** — what must not change (e.g. hold the product's colour, keep the label spelling intact).

When editing, write a command, not a description of the result: name the exact target and state what must stay unchanged.

Best when a subject must hold its identity across scenes.

- Lead with what matters most; earlier concepts weigh more.
- Aim for 30–100 words of description, not keywords.
- No `negative_prompt` field; phrase exclusions inside the prompt.

