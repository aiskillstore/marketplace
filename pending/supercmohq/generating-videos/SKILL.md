---
name: generating-videos
description: ALWAYS read this skill before generating or animating any video, or calling video_generate — text-to-video, image-to-video, a start→end transition, or a reference / motion / audio-guided clip. Generates a video from a brief — one clip, or several clips joined into a single file at any length. Use when the user wants to make or generate a video, animate a photo, bring an image to life, produce b-roll, film a described scene, or move from one held frame to another. This skill should also be used when the video takes its motion or style from an existing video, or has to run to an existing audio track. 
license: Apache-2.0
metadata:
  version: "0.5.0"
  category: creative
  summary: "Routes your brief to the best of 10+ SOTA video models (like Veo, Seedance), writes detailed prompts as per model specifications and generates multi-clip stories that hold continuity across cuts, stitched into one file."
---

# Video Generation

Turn a brief into a video.

## Workflow

### Step 1: Read the brief and the media

**Look at everything the user supplied.** Run `image_analysis` on each image and `video_analysis` on
each video. Write down what each one shows — who is in it, where it is, how it is lit, how it is
framed — so the prompt matches it instead of describing something different. Send a product URL or
photo to `analyzing-products`. Skip an image you already know: you made it this turn, or you have
already analyzed it.

**Then read the brief**: how long the video runs, what happens in it, where it will be posted, and
whether anyone speaks.

**Where the video has a product, write one description of it** and reuse it unchanged in every
storyboard and every clip prompt — rephrasing it between calls reads as a different product.

- **Material and finish**, surface by surface.
- **Size** — its width and height, and how it sits against a hand.
- **Two to five visual anchors** — features you can verify in the product image and nothing else:
  exact colours, the shape of a closure or handle, the gauge of a chain or strap, a surface finish, a
  distinguishing mark.
- **What may be done with each part** — which parts are fixed to it, and the whole of what the moving
  ones allow. Nothing later does anything to the product that isn't on this list.

**Don't transcribe what the label says.** Spelling out the printing invites the model to redraw it,
and redrawn text comes back warped.

### Step 2: Pick the model and load its parameters

**`seedance-2.0-fast` is the default** — the general-purpose workhorse; a weak result is usually the
prompt's fault, not the model's.

**The storyboard route always runs on `seedance-2.0-fast` unless the user named a model.** The table below
decides a single clip.

Reach past the default only on a clear signal:

| Reach for another model when the brief… | Model |
| --- | --- |
| Needs spoken dialogue with lip-sync, the tightest prompt-following, or top cinematic quality | `veo-3.1-fast` |
| Is editing an existing clip — restyle it, add or replace an element, fix on-screen text — or hinges on legible on-screen text | `gemini-omni` |
| Must hold one person or character consistent across references or several shots | `kling-3.0-pro` |
| Has an edgy or sensitive subject Seedance would refuse, or wants the fastest, cheapest draft | `grok-imagine-video` |
| Is a high-volume or cost-sensitive batch where top quality isn't essential | `wan-2.7` |

When more than one fits, work down this list and stop at the first that applies:

1. The user named a model — use it.
2. The video takes the storyboard route — `seedance-2.0-fast`.
3. Seedance refused the brief (`nsfw` / `ip`) or keeps failing — use the fallback from the table.
4. The brief matches a row above — use that model.
5. Otherwise use `seedance-2.0-fast`. If two models tie, use the newer one.


Then **call `list_video_models` for the chosen model** and read its accepted modes, aspect ratios, durations, resolutions, and media — each validates its own subset, and you need these before writing the prompt.

### Step 3: Route

Take one of three paths:

- **The video is a person on camera presenting a product** — holding it and talking about it, opening
  its package, putting it on, demonstrating it → Trigger the `generating-ugc-videos` skill workflow,
  whether or not the brief says UGC.
- **One clip covers it** — the video runs no longer than the model's longest clip, and holds one
  continuous shot → Read and follow the steps in `references/direct-route.md`.
- **It needs more than one clip** — the video runs longer than the model's longest clip, or the brief
  needs a cut between shots → Read and follow the steps in `references/storyboard-route.md`.

`list_video_models` gives the model's longest clip. Storyboard sheets are what keep a person, a place
and a product looking the same from clip to clip, and what fixes the frame on both sides of a cut, so
anything with more than one clip takes the storyboard route.

A supplied image is used one of two ways. Ask which, if the brief doesn't say:

- As the **start frame**, the video begins on that exact image.
- As a **reference**, it shows what a subject or a style looks like and the video is a new scene.

**A start frame works for one clip only, and that clip can carry nothing else** —
`start_frame_image` cannot be combined with any `reference_*` input. Where a person, a product or a
style has to match an image that isn't the start frame, pass that image as a reference and drop the
start frame.

## Edge cases

- **Safety / NSFW rejection** → name a workable stand-in for whatever tripped the filter (cover the
  wardrobe, change the setting) and resubmit. If the subject itself is the block, switch to
  `grok-imagine-video` (see **Step 2**). A second rejection: tell the user which element is blocked
  instead of retrying blind.
- **Still generating (`status: "pending"`) or the call times out** → the clip is still rendering on
  the server, **not** a failure — do **not** resubmit (that starts a second billed job). If you got a
  pending handle, call `job_status` with it to rejoin; if the call timed out with no handle, wait and
  tell the user it's still processing rather than firing a fresh generation.
- **Generic failure** (an explicit error result, not a timeout) → read the error. If it names a
  parameter or a limit, correct that and resubmit. Otherwise resubmit once; if it fails again, either
  switch to a fallback model (**Step 2**) and write to its guide, or give the user the error text
  rather than guessing.
- **Reference or frame rejected on count / mode** → the error states the model's limit or supported
  modes; adjust to it, or check `list_video_models`.
- **Unsure which model fits a named request** → call `list_video_models` and pick by `strengths`.
- **The user wants a standalone audio file, not clip audio** — a voiceover to drop on a timeline, or
  a music track or sound effect they need to place themselves. Clip audio can't give them that; it is
  baked into the picture. Send speech to `generating-audio`, and say plainly that separate music and
  effects tracks aren't generated here.
- **`error: "no_provider_configured"`** → relay the tool's `hint` (the user must set their key).

## Reference

Each route is a complete workflow. Read the one Step 3 picked, and follow it to the end.

- `references/direct-route.md` — one clip: the six modes and what each one passes, the beats, the
  prompt and the call.
- `references/storyboard-route.md` — more than one clip: the video planned as beats, built through
  storyboards and joined into one file.
