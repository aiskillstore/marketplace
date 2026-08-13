---
name: generating-storyboards
description: Generates the storyboard sheets for a video — one image per clip, panels in a row, each panel one action. Divides each clip into panels itself, then builds the sheets one at a time, each taking the previous one as a reference, so the person and product stay consistent except where the story deliberately changes them. Use when a video's clip lengths and story are settled and it needs sheets before anything is animated. Not for a still image on its own — that should be made using generating-images.
license: Apache-2.0
metadata:
  version: "0.4.0"
  category: creative
  summary: "Draws out your entire video concept clip-by-clip as static images, enforcing strict character and product continuity so you can approve camera angles and visual flow before committing to expensive video renders."
---

# The storyboard

One sheet per clip, vertical panels in a row, each panel one action, left to right. Panels are numbered
within a sheet; sheets are numbered across the video.

**The sheet is always `16:9` and its panels are always vertical**, whatever shape the finished video
is. Neither follows the delivery ratio, and neither is the plan's to set.

The plan settles how many sheets there are, what happens in each clip and how long it runs, which
images come in as references, and the look. How a clip divides into panels is settled here.

Anything the plan specifies wins. The defaults below fill gaps only.

## Workflow

**One sheet at a time.** Run all six steps for the first sheet, then run all six again for the
second, and so on. Sheets cannot be built in parallel or in one call — each prompt needs the previous
sheet's finished image in hand.

### Step 1: Collect what's needed

- **An image of the person** — wherever a person appears in any panel.
- **Product image or images** — where the video has a product.
- **The previous sheet** — from the second sheet on.
- **What happens in this clip**, and how many seconds it runs.
- **How many sheets there are**, and which one this is.
- **The look**, where the plan names one.

What a supplied image is for comes from the brief, not from its contents — a person in a frame
doesn't make it the person reference, and one image can't serve as both the person and the product.

**Read every supplied image** with `image_analysis` before deciding anything: what the place looks
like, what they're wearing, and for a product, its colours, its shape, its finish, and how big it is.
Skip this where the image is already known.

Where any of this is missing, ask for it rather than assuming it.

### Step 2: Settle the sheet

- **References** — every one goes in twice: attached as `reference_images` on the generate call, and
  labelled Image 1, Image 2, Image 3 in the prompt text. **Same order both times** — the product
  image or images, the person's image, then the previous sheet once there is one. Say once what each
  is, then refer to it by label. A label with nothing attached points at nothing, and unlabelled
  attachments let the model pick its own subject out of the set.
- **The person** — pointed at by label, never described. State that wherever they appear it is the
  same person, with face, hair, build and skin tone identical throughout. Don't describe their age,
  ethnicity, build, hair, makeup or features — the reference supplies all of it, and words describing
  it fight the image. They need not be in every panel: a tight product panel may show only their
  hands, or nobody at all.
- **Setting** — where they are, when, and how it's lit. Unless the plan sends them elsewhere, carry
  the location, the hour and the direction of the light straight from the person's image.
- **Light** — from a named direction, soft and neutral. No golden hour, sunset, or amber cast unless
  the plan asks for it, and never studio lighting.
- **Wardrobe** — the garments and their colours, named. From the person's image by default.
- **Look** — by default a phone photograph in available light, sensor grain, real skin. A look named
  in the plan wins.
- **Product name** — one short noun phrase, used word for word in every panel that mentions it.
- **Product size** — a measurement, so it can be held against the hand at its real size.

Skip the last two when there is no product.

From the second sheet on, write two lines: what carries over from the previous sheet, pointed at by
its label, and what the plan deliberately changes. Anything not named as changed matches it exactly.

### Step 3: Divide the clip into panels

The plan gives the clip's story and its seconds. How many panels carry it is worked out here.

**One panel is one primary action** — one continuous motion at one object. Take the clip's story and
split it wherever a second motion starts or a second object is taken up: *picks it up*, *tilts it to
the light*, *puts it on* are three panels, never one line.

**Each panel runs two to four seconds of the clip**, so the seconds set how many there are. A story
that splits into more panels than the clip has room for is too much for the clip — say so and cut a
motion rather than crowding them.

### Step 4: Write the panels

**Settle the row before writing any panel.**

The panels read left to right as one continuous story, each picking up where the last left off. On the
second sheet and after, the first panel continues from the final panel of the sheet before it.

*Across the row, these vary:*

- A different action in every panel — a genuinely different thing being done, not the same pose
  wearing a new expression.
- The camera position changes between panels, and never repeats back to back.
- The panels are shot at a mix of camera distances rather than all close, all mid or all wide; a row
  that sits at a single distance throughout needs reworking.
- The expressions move through an arc rather than repeating.

*Across the row, these hold:*

- Setting and wardrobe hold unless a beat changes them, and the change lands between panels, never
  inside one.
- A panel shows a state, not the change into it — already open, already worn, already out of the box.
  The change itself falls on the cut.
- At most one state change lands in any single panel.
- State runs one way. Once something is open, worn or emptied it stays that way for the rest of the
  video — never re-closed, never taken off again, never put back where it came from.
- Once a part is taken off the product, it leaves the picture entirely — never set down nearby, on a
  surface, or in the other hand.
- Nothing appears without arriving. Anything in a panel was either in the panel before it or came in
  on the cut just before.
- What leaves is gone from every panel after it and is never described again, on this sheet or any
  later one — a cap taken off, a wrapper torn away, a box emptied.

**Then write each panel, with all six of these.**

**1. Camera position** — held at arm's length, locked off, over the shoulder, down their own eyeline,
or whatever else the look calls for.

**2. Framing** — name the distance outright: macro, tight close-up, medium close-up, medium,
waist-up, three-quarter, full-body wide.

**3. Action** — one physical thing happening: a single continuous motion at a single object. Never
two hand actions at once. Where it handles a product, write the hand mechanics as a sequence — which
part is gripped, what moves, what that produces — never a verb that only names it.

**4. Hands** — which hand is doing what.

- Where the subject holds the camera, only one hand is free, so at most one thing can be held. A beat
  needing two things held, or two hands on one thing, needs a camera position that isn't handheld.
- Anything that stays in the scene while both hands are busy is set down on a surface.
- Grip follows weight and bulk. The heavier or more unwieldy the item, the more hands it needs and
  the more effort registers in the face and posture; a light item sits easily in one hand, a tiny one
  pinched in the fingertips. Match the hold to what the object would really demand.

**5. The product** — in frame only where the beat needs it. 

- Only the face the reference shows is ever visible. The product can sit nearer or further in the
  frame, but it never turns — no side, back or interior the reference doesn't show ever appears, and
  a shot that orbits the product still lands on that same one face.
- It stays at its real size. Where fine print won't resolve at that scale, tighten the framing on it
  rather than blowing the product up to force the text legible.
- The product reads as either clearly present or clearly not — held or shown in full, sealed inside
  something closed, or simply out of the panel. Anything in between, only partly in view or
  precariously placed, reads as a glitch.
- The verb suits the material. A rigid item is held, lifted, angled or pointed at, never forced out
  of shape; a soft one takes gentle pressure but is never twisted hard. Keep the handling calm — no
  tossing, flipping or trick moves. When no verb is obvious, simply hold it up to show it.

**6. Performance** — a micro-behaviour laid over the action, not instead of it: a glance away and
back, an eyebrow going up, a breath landing, a grin arriving late. Never the only thing describing a
panel.

Example: Panel 2 — vertical photographic still, locked off: medium close-up on hands and product. She turns the jar so its printed face meets the lens, mouth open mid-sentence. Both hands on it — left steadies the base, right rotates it. Jar at chest height, printed face to camera.

### Step 5: Assemble the prompt in this order

1. **The references** — each label and what it is.
2. **The locks** — the person identical throughout; the product on the side its image shows; and from
   the second sheet on, what carries over and what changes.
3. **The layout** — panels of identical size in a single row, none empty, thin white margins on clean
   white. **The sheet is always `16:9` and the panels inside it are always vertical**, whatever shape
   the finished video is.
4. **The sheet-wide settings** from Step 2 — setting, light, wardrobe, look, product name.
5. **The product's size and how it may be placed.**
6. **Hands and camera** — how many hands each position leaves free.
7. **What each panel shows** — one line per panel, left to right, each carrying the six from Step 4.
8. **The constraints**, below, in full, closing the prompt.

**The constraints:**

- Every panel a photographic still in the same register.
- **No text anywhere on the sheet** — no lettering, numbering, captions, badges or watermarks, and
  nothing written over a picture.
- Two hands per person, no more, properly formed.
- No floating objects or objects materializing out of thin air.
- Every face clear and undistorted; where they are speaking, a mouth open mid-word is correct.
- Where the shot is a selfie, no reflective surface showing the person and no phone in frame.
- No lens effects — no bokeh or deliberate shallow focus, no flare, no colour grade, no fisheye or
  ultra-wide distortion.

Add these where the video has a product:

- The product's own printed label stays exactly as its reference shows it, and is the only lettering
  in a panel. Anything else that would carry writing is angled so it doesn't.
- One of the product, at true size, keeping the same visible side as its reference.
- No brand present but the one being filmed.
- Nothing claimed about the product that wasn't given to you.

### Step 6: Generate this sheet

One `image_generate` call:

- `prompt` — the one assembled in Step 3, whole.
- `model` `gpt-image-2`. **`aspect_ratio` is always `16:9`** — a row of panels needs the width,
  whatever shape the video is. Only the model changes, and only where the plan names one.
- `reference_images` — the product image or images, the person's image, and from the second sheet on,
  the sheet generated just before this one. **Pass them in the same order they were labelled in Step
  2**, or the labels in the prompt point at the wrong pictures.

It can come back as `{status: "pending", …}` — a job handle, not a failure. Pass that exact handle to
`job_status`, and again if it is still pending. Never re-run a pending generation; that starts a new,
separately-billed job.

Keep the result. It is the plan for its clip, and the reference the next sheet is written against.

**Where another sheet remains, go back to Step 1 and run the six again for it.**

## Edge cases

- **`reference_images` rejected on count** → the error states the limit; drop to it, keeping the person
  and the previous sheet ahead of extra product angles.
- **Safety / NSFW rejection** → usually the person. Name a stand-in for whatever tripped the filter and
  resubmit; identical inputs fail identically. After a second rejection, say which element is blocked
  so the person can be recast.
- **`error: "no_provider_configured"`** → relay the tool's `hint`.
