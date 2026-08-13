---
name: generating-images
description: ALWAYS read this skill before generating or editing any image, or calling image_generate — text-to-image or image-to-image, simple or complex. Turns a text brief, optionally guided by reference images (a character, a style to follow, an existing photo to edit), into a still image. Analyzes intent, routes to the best model, and structures the prompt. Use whenever the user asks to generate, create, make, design, or edit an image — except commercial photography of a product being sold, which belongs to generating-product-photos.
license: Apache-2.0
metadata:
  version: "0.1.0"
  category: creative
  summary: "Routes your brief to the best of 10+ SOTA image models (like Nano Banana, GPT Image), writes detailed prompts as per model specifications and generates multiple variations instantly."
---

# Image Generation

Turn a brief — text, optionally with reference image(s) — into a still image via the
`image_generate` tool. Two decisions drive quality: **which model** (always) and **which format
recipe** (only when the deliverable is a known one).

**Before you route:** if the brief is commercial **product photography** — a packshot, a product in
a styled scene, a hero or banner for a product, a product ad or carousel, an on-model or try-on shot,
or restyling an existing product photo — hand off to the **`generating-product-photos`** skill, which
owns that surface. Stay here for everything else: general images, graphics and posters, portraits,
illustrations, cinematic stills, infographics, and one-off reference edits.

## Workflow

### Step 1: Route to a model

Route by what the image has to **do** — read the brief for intent.
The descriptions below are signals to weigh, not a literal router — the examples are illustrative,
not a checklist to match against. Then **read the chosen model's prompt guide before writing
anything**.

| Route when the brief is about… | Model | Prompt guide |
| --- | --- | --- |
| Rendering **words** legibly, or a designed layout where elements sit in deliberate positions — for example a poster, ad, banner, thumbnail, or infographic | `gpt-image-2` | `references/prompt-gpt-image-2.md` |
| A **drawn or rendered** look rather than a photograph — for example a cartoon, anime, illustration, flat vector, or 3D render | `nano-banana-2` | `references/prompt-nano-banana.md` |
| A convincing **real person**, or a photographic frame with deliberate cinematography — for example a creator or influencer portrait, UGC, or a film-like still | `nano-banana-pro` | `references/prompt-nano-banana.md` |
| **Altering a supplied image** — for example swapping a background, removing or replacing an element, or restaging the scene | `gpt-image-2` | `references/prompt-gpt-image-2.md` |
| Altering a supplied image where a **real face must stay recognisable** | `seedream-5` | `references/prompt-seedream.md` |

When more than one applies, take them in this order:

1. The user named a model → use it.
2. Legible text is required → `gpt-image-2`, even over a person or a scene.
3. The look is non-photographic → `nano-banana-2`, even when a person is involved.
4. A supplied image is being altered → `gpt-image-2`; switch to `seedream-5` when a real person
   must stay recognisable.
5. A supplied image is only a **style or mood cue** (match this look, don't edit that image) →
   `nano-banana-2`, or `seedream-5` if a specific face must carry over too.

If nothing clearly fits — an ordinary object or scene — use `nano-banana-2` (read
`references/prompt-nano-banana.md`); or call `list_image_models` and pick by `strengths`. Use
`grok-imagine` (`references/prompt-grok.md`), `flux-2-pro`, or `flux-2-klein-4b` (both
`references/prompt-flux.md`) only when the user names them.

### Step 2: Read a format recipe if one fits (optional)

Many briefs are a standard deliverable with a layout worth following. Check the table below. **If a
row matches, read that recipe and follow its sections and example. If none matches, skip this step**
— the model's prompt guide is enough.

| Deliverable                          | Recipe                           |
| ------------------------------------ | -------------------------------- |
| Poster / ad / banner / social graphic | `references/format-poster.md`    |
| Portrait / avatar / influencer        | `references/format-portrait.md`  |
| Cinematic still                       | `references/format-cinematic.md` |

### Step 3: Get any missing inputs

Ask only for what would change the result and can't be sensibly defaulted — for example the exact
text that has to appear on the image, a source image for an edit, or the desired aspect ratio when that
decides the crop. Bundle everything you need into one ask rather than a back-and-forth; if the user
has signalled they don't want questions, choose sensible defaults, state them in a line, and proceed.

### Step 4: Look at the reference images — only when references are supplied

Call `image_analysis` on each reference, asking whatever the prompt will have to carry — enough to
name what must stay fixed and to avoid contradicting the source.

Skip when you already know what's in the image — you generated it this turn, or it arrived with a
description.

If what you find changes the routing — a face to keep recognisable, a stylized source — go back to
Step 1.

### Step 5: Write the prompt

Build the prompt as the chosen model's prompt guide specifies. If you read a format recipe, start
from its sections and worked example. With a reference image, use what Step 4 turned up to say what
stays fixed (the product, the face, the palette) and what changes.

**Write a complete, self-contained prompt** — the model sees only this one prompt. Specify the whole
frame: subject, wardrobe / materials, setting, lighting, colour palette, camera / lens, medium, and
mood. A dense, concrete, technical description beats a thin one-liner or vague adjectives ("nice",
"cool") — that density is what separates an editorial result from a generic one.

### Step 6: Generate

Call `image_generate` with a `requests` list (one object per image):

- Per object: `prompt` (required); `model` from Step 1; `aspect_ratio`; `resolution` — step up a tier
  when the image carries a lot of text; `reference_images` for a supplied source.
- For several **different** images (an A/B set, a carousel), add one request object per image to the
  same call.

**Same subject or style across a set.** Requests are generated independently, so a back-reference
("the same woman", "same outfit") produces a different result each time. Write the appearance,
wardrobe, and style once and repeat that description word-for-word in every request; vary only the
shot, framing, and aspect ratio, and hold one lighting and palette across the set.

Images are polled for you, but a heavy one — a large model, 4k, or a big batch — can come back as
`{status: "pending", …}` (a job handle, not a failure). Pass that exact handle to `job_status` to
retrieve the finished image — **never re-run a pending image** with `image_generate`; that starts a
new, separately-billed job. If it's still pending, call `job_status` again with the same handle.

### Step 7: Return

Once every image has finished (rejoin any `pending` ones via `job_status` first), share the resulting
image URL(s) and local file path(s) with the user.

## Edge cases

- **Fits no kind** → use `nano-banana-2` (read `references/prompt-nano-banana.md`) or call
  `list_image_models`.
- **Fits no format** → skip Step 2; the prompt guide alone is enough.
- **Safety/NSFW rejection** → name a workable stand-in for whatever tripped the filter (cover the
  wardrobe, change the setting) and resubmit. A second rejection: tell the user which element is
  blocked instead of retrying blind.
- **Still generating (`status: "pending"`) or the call times out** → the image is still rendering on
  the server, **not** a failure — do **not** resubmit (that starts a second billed job). If you got a
  pending handle, call `job_status` with it to rejoin; if the call timed out with no handle, wait and
  tell the user it's still processing rather than firing a fresh generation.
- **Generic failure** (an explicit error result, not a timeout) → read the error. If it names a
  parameter or a limit, correct that and resubmit. Otherwise resubmit once; if it fails again, give
  the user the error text rather than guessing.
- **`reference_images` rejected on count** → the error states the model's limit; drop to it.
- **`error: "no_provider_configured"`** → relay the tool's `hint` (the user must set their key).

## Reference

**Prompt guides** — read the one for the chosen model:

- `references/prompt-gpt-image-2.md` — labeled blocks, verbatim text rendering, reference identity.
- `references/prompt-nano-banana.md` — instruction-following (subject/scene → style → instructions → constraints).
- `references/prompt-seedream.md` — instruction-style editing, compositing, and preservation.
- `references/prompt-flux.md` — linear prompt sequence, no negatives, camera/lens specs.
- `references/prompt-grok.md` — natural-language director style.

**Format recipes** — read only if the deliverable matches:

- `references/format-poster.md`, `references/format-portrait.md`, `references/format-cinematic.md`.
