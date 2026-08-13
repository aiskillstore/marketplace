---
name: generating-product-photos
description: |
  ALWAYS read this skill before generating a product photography — before writing any prompt or calling image_generate. Turns a product photo or URL into commercial photography - packshots, lifestyle and campaign frames, on-model, macro detail, flat lays, seasonal staging, infographics, concepts and floating shots. Reads the real product first and holds it identical across every frame. Triggers: "product photo", "packshot", "shoot my product", "studio shot", "lifestyle shot", "hero image", "on a model", "flat lay", "product infographic", "floating product", "product ad".
license: Apache-2.0
metadata:
  version: "0.2.0"
  category: creative
  summary: "Directs a commercial photoshoot around your product, automatically applying the correct lighting, framing, camera angles and props to deliver studio-quality product shots across 10+ formats."
---

# Product Photography

Turn a product into commercial imagery via the `image_generate` tool.
Marketplace listing galleries are out of scope. Anything whose subject isn't a product should not be created with this skill.

## Workflow

### Step 1: Read what you have

- **A product image or URL is available** → hand it to `analyzing-products`, and take four things
  back: what the product is; **how a person physically uses it** — sprayed, pumped,
  worn, etc.; which parts open or move, and in what order; and the details that have to stay identical wherever it appears. 
- **Look at the image before you describe it.** Take the product only from what the image shows —
  not the brief, not the filename, not the product name. Run `image_analysis` and ask it for
  everything this shoot needs that the product facts leave out — how the surfaces take light, and
  whatever else the frame you end up building will have to describe.
- **Product not supplied** → don't guess at the product. It becomes the first thing Step 2 asks for.

### Step 2: Interview

**Skip this entirely when the brief already makes the shot obvious** — a clear subject, a clear use,
and nothing load-bearing missing. The interview exists to close real gaps, not to confirm what you
were already told.

Otherwise ask once, bundled into a single message, **at most four questions**. Always leave a free-text way out so the user can answer off-menu. Anything this skill already settles is not a question.

**Do ask, when the answer is genuinely missing:**

| Ask | When |
| --- | --- |
| **The product** — what it is, and whatever else identifies it: packaging, colour, distinguishing features | No image and no URL. Offer to wait for an upload first; a photographed product beats a described one. |
| **Brand guidelines, if they have any** — the color palette, the art direction they shoot to, anything they never put in frame, the typeface where text is drawn, and the register they want the frame to read at | The brief mentions none and the packaging doesn't imply them. Treat as optional: plenty of brands have none, so take what they give and move on. |
| **Who the buyer is** | The frame has to speak to a particular buyer — like which features an infographic calls out, whose home a lifestyle scene is set in, who gets cast on-model, etc. |
| **How many frames**, and where they run | The brief doesn't say, and the destination changes the crop. |

**When the user waives questions** and the product is already in hand, go straight to generating.
Take **studio**, since that is where an unrouted request lands anyway; take the tool's default ratio. Say in a sentence which settings you took, then keep going. It is a statement, not a checkpoint.

A missing product image is the one thing still worth raising.

### Step 3: Select the mode and read the corresponding reference file

| The ask is about… | Mode | Reference |
| --- | --- | --- |
| The product on its own against a clean, controlled background | **studio** | `references/mode-studio.md` |
| The product somewhere real, being used or lived with | **lifestyle** | `references/mode-lifestyle.md` |
| One polished frame leading a campaign — the product made to look desirable | **hero** | `references/mode-hero.md` |
| Worn, held, or applied to skin | **on-model** | `references/mode-on-model.md` |
| Texture, material, craft, a tight crop on the thing itself | **close-up** | `references/mode-close-up.md` |
| Arranged on a surface, shot from directly above | **flat-lay** | `references/mode-flat-lay.md` |
| Tied to a holiday, season or buying moment | **seasonal** | `references/mode-seasonal.md` |
| Feature labels, callouts, specs or ad copy drawn onto the image — including an ad, a before-and-after or a comparison | **infographic** | `references/mode-infographic.md` |
| Breaking the pattern to stop a scroll — unexpected, impossible, or unlike how this product is normally shown | **creative** | `references/mode-creative.md` |
| Suspended mid-air, defying gravity | **floating** | `references/mode-floating.md` |

Route on what the image is *for*, not on a matched word.

**Where two rows both fit, these win:**

- **A person in frame** → **on-model**, whatever the setting or the crop would otherwise say.
- **Text drawn onto the image** → **infographic**, whatever else is in frame.
- **One plane, shot from overhead** → **flat-lay**
- **One property at close range** → **close-up**, even inside a setting.
- **The occasion is the sell** → **seasonal**
- **The brief asks for something unexpected, surprising or scroll-stopping** → **creative**, even when
  it also names a placement.

### Step 4: Write the product description

You read the mode guide in Step 3, so you know what this shot has to show. Write one description of
the product, and reuse it unchanged in every prompt you send.

**How much to write depends on whether a photo is going with the call.** With a reference attached,
the photo carries identity and the description covers only what it cannot: the angle you want, the
state the moving parts are in, the action being performed. With no reference, the description is all
the model has, so it carries the product in full from the list below.

- **Form** — shape, proportion, how it sits or stands, or whatever else pins the silhouette down.
- **Closure and moving parts** — a cap, a hinge, a zip, whatever this product has, and whether the
  shot wants it open or shut.
- **Materials and finish, surface by surface** — matte or gloss, brushed, woven, translucent or
  something else.
- **The action, wherever the frame has one** — the specific thing being done to the product, taken
  from the mechanic Step 1 established rather than invented to suit the composition. Write it as the
  physical movement it is, and say what the product is doing at that instant: what has left it, what
  is about to, which part has moved, etc.

The mode guide decides how much of this the prompt carries — the whole product for some, a single
property for a close crop, one description per item where several share the frame.

**Don't transcribe what the label says.** Spelling out the printing invites the model to redraw it,
and redrawn text comes back warped.

### Step 5: Select the model

| Model | Use it when | How it wants the prompt written |
| --- | --- | --- |
| `nano-banana-pro` | everything, by default | connected sentences in one narrative paragraph, never a string of keywords |
| `gpt-image-2` | words or graphics are drawn onto the image, or the layout is a designed one. Not for the product's own printed label — that comes from the reference | short labelled segments on separate lines, not a paragraph |
| `seedream-5` | another model refused, or keeps failing | a description rather than keywords, leading with whatever matters most |

If the user has explicitly named a model, then use that first.

### Step 6: Write the prompt

- Follow the mode guide from Step 3 to write the prompts, carrying the product description from
  Step 4 into each one. 
- Read `references/photographic-craft.md` before writing. It carries the language for light, shadow,
  colour, material and optics; the style anchor to pick before the first sentence; and the two fixed
  blocks that close every prompt.
- **Every prompt is assembled in this order:** the mode's fixed preservation block, then the scene
  you write from the mode's fields, then the quality-marker line, then the Avoid block — the last
  two exactly as `references/photographic-craft.md` gives them.
- **Every prompt sent with a reference photo states the fidelity requirement.** The attached photo
  does not enforce itself: say outright that the product in frame is the one in the reference and
  reaches the image unchanged. Anything the photo already settles and does not need to change must not be written
  out again: a detail spelled out reads as an instruction to draw it, and what gets drawn drifts from
  the photo. Those words go to what the reference cannot show — the setting, the light, the framing, etc.
- **Where a call carries more than one reference image, label them.** Refer to them as Image 1, Image 2
and so on, in the order they are passed. Say what each one is, then use those numbers in the
instruction rather than describing the pictures again. Left unlabelled, the model picks its own
subject from the set.
- **Scene-specific exclusions go inline**, phrased as the thing you want instead — there is no
  negative-prompt parameter. The closing Avoid block is the one exception, and it is fixed: do not
  add this frame's own exclusions to it.
- **Don't reserve empty space for text nobody asked for.** A region requested as emptiness comes back
  as an untextured block.
- **A name is not a description.** Borrowing someone's name — whoever or whatever it belongs to —
  buys a vague imitation at best, and some models simply decline the request. Say what you were
  reaching for instead: the geometry, the palette, how the light behaves. A rival's name has no place
  in the frame at all, not even as the thing you are steering away from. The only brand name that
  belongs in a prompt is one for the product you are photographing.
- **No internal name goes in the prompt** — not a mode, not a file.

### Step 7: Generate

Call `image_generate` with a `requests` list (one object per image):

- Per object: `prompt`; `model`; `aspect_ratio`; `resolution`; `reference_images`.
- **The product photo goes in `reference_images` every time.** It holds identity; the prompt alone
  will not.
- **Take the ratio from the user.** If they haven't named one, derive it from where the image runs —
  the destination decides the crop, not the mode. If neither is known, ask in Step 2 or take the
  tool's default and say which you took.
- **One image per request.** Generate a single frame unless the brief asked for more than one.
  Never generate a second to compare models, to try a different look, or to correct an output you
  judged poor — every one of those bills again. Where the brief does ask for several, send them as
  several request objects in the one call.
- **Don't run a vision or analysis call on the image you just generated.** Judging your own output
  is not part of this workflow: it costs another call, and anything it finds you are not permitted to
  act on. Hand the result to the user and let them decide.
- **An unanswered question is not a yes.** If you ask whether to regenerate and no answer comes back,
  the answer is no — deliver what you have and say what you would have changed. A run with nobody
  watching cannot consent to being billed twice.
- Call `list_image_models` for accepted `aspect_ratio` values, `resolution` tiers and per-model
  `reference_images` limits rather than guessing — a wrong enum fails a billed call.

Images are polled for you, but a heavy one can come back as `{status: "pending", …}`. That is a job handle, not a failure. Pass that exact handle to `job_status` to retrieve the finished image, and if it comes back pending again, call `job_status` again with the same handle. **Never re-run a pending image** through `image_generate`: that abandons the job you are already paying for and starts a second, separately billed one.

### Step 8: Return

- Share the image URLs and local file paths, once every frame has finished — never a partial set.
- For a set, present them in the order you outlined.

## Producing a set of images

Requests generate independently, so build the continuity in:

1. **Draft the frame list and get it agreed before generating anything.** Every frame is billed
   separately, so misreading the brief means paying to generate the entire set a second time.
2. **Fix one look and write it into every prompt unchanged** — the palette, the surface, the light,
   the camera height and angle, whatever else the look is made of. Rephrasing it between frames reads
   as a new instruction.
3. **Send the same reference image and the same model on every frame.** Those two carry the product
   and hold the set together; wording alone will not.
4. **Vary only what each frame shows.** A frame that needs a different setting is a second set, not a
   member of this one.
5. **Make them genuinely different** — near-duplicates test nothing. Give each frame its own argument
   first and let that pick the staging; frames differing only in camera angle ask the same question
   twice.
6. **Where the set is a sequence rather than a spread**, decide the order first and write each frame
   to its position: what has to stop someone, what carries the middle, what the last frame leaves
   them holding. A sequence assembled from interchangeable frames reads as a spread that lost its
   order.

## Common mistakes

- Writing a freeform prompt instead of what the mode says it must carry.
- Skipping the interview when something load-bearing is missing.
- Showing an interaction the product doesn't support, when Step 1 already established what it does.
- Naming a brand, a photographer or a publication in the prompt in place of describing the look.
- Re-running a rejected frame without first finding out what was wrong with it.

## Edge cases

- **The image came back not as intended** — wrong angle, warped label, a look you didn't ask for →
  deliver it anyway and say what you think is off. Do not regenerate on your own judgement: a second
  generation bills again, and the user may be happy with the first.
- **A rejection that names no reason** → ask what missed before re-running, with options drawn from
  the mode you just shot, plus free text. A blind re-run bills again and lands elsewhere at random.
- **Safety or policy rejection** → name a workable stand-in and resubmit; on a second, try
  `seedream-5`; on a third, say which element is blocked rather than retrying blind.
- **Generic failure** → read the error. If it names a parameter or limit, fix that and resubmit;
  otherwise resubmit once, then hand the user the error text.
- **`reference_images` rejected on count** → the error states the limit; drop to it.
- **`error: "no_provider_configured"`** → relay the tool's `hint` (the user must set their key).

## Reference

**Mode guides** — read the one you routed to; each ends with a checklist to read your prompt against:

- `references/mode-studio.md` — the background and its brightness, true colour, sharpness, shadow.
- `references/mode-lifestyle.md` — place, hour, motivated light, and what keeps the product the subject.
- `references/mode-hero.md` — the open side for copy, the graded key, surviving every delivery crop.
- `references/mode-on-model.md` — casting, styling condition, hands, where the crop cuts the body.
- `references/mode-close-up.md` — the one property, raking light, apparent source size, the scale cue.
- `references/mode-flat-lay.md` — camera plane, arrangement register, the open surface.
- `references/mode-seasonal.md` — the single carrier, whose palette it is, props that read as included.
- `references/mode-infographic.md` — callout copy, anchors, leader lines, the exposing angle.
- `references/mode-creative.md` — the concept, the one departure, coloured sources, what is held dark.
- `references/mode-floating.md` — the underside, the displaced shadow, the gap that reads as height.

**Shared craft** — read on every job:

- `references/photographic-craft.md` — the two fixed blocks that close every prompt; the style
  anchor; light, shadow, colour, material, optics and on-image text; what changes for paid media.
