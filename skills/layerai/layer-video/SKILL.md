---
name: layer-video
description: "Use when generating video with Layer: text-to-video, animating a still image, extending a clip, adding camera motion, generating native audio or lip sync, looping animations, or planning a multi-shot ad, trailer, or cutscene. Also when a video prompt produces the wrong motion or the shot drifts off the source image. Keywords: txt2vid, img2vid, image to video, camera motion, video effects, loop, seamless, trailer, cutscene, lipsync."
license: MIT
---

# Layer Video Generation

## Overview

Video models take a prompt the way a director takes a shot list, not the way an illustrator takes a
brief. A video prompt describes **what changes over the clip**. A prompt that only describes the
scene yields a near-still image with drifting artefacts, which is the most common failure here.

Pick the use case first: `text_to_video` from nothing, `image_to_video` to animate an existing
frame, `video_extend` to continue a clip, `video_editing` to alter one. The loop and spend gate are
in the `layer` skill. Assembling finished clips into one deliverable is `layer-video-timeline`.

If a sibling skill named here is missing from your available skills, ask the user to install it
(`npx skills add layerai/skills --skill <name>`); unattended, proceed from tool schemas and flag the
gap.

## Anchor on an image whenever one exists

`image_to_video` beats `text_to_video` almost every time a look has already been approved. The first
frame fixes the character design, palette, and composition, so the model spends its capacity on
motion instead of re-inventing the subject. Attach the still as `init_image` or `first_frame`
depending on what the model accepts, and where a model takes both `first_frame` and `last_frame`,
supplying both is the most reliable way to control where a shot ends up.

Generate the key frame with `layer-image`, approve it, then animate it.

## Writing the motion

Name three things, in this order:

1. **Subject motion**: what moves, in what direction, at what speed. "The banner snaps taut in a
   gust, then settles" is a shot. "A banner" is a photograph.
2. **Camera**: static, slow push in, orbit, handheld drift, crane down. State "locked-off camera"
   when the camera must not move, because models add drift by default.
3. **Rate**: slow, deliberate, sudden, gradual over the full clip. Models otherwise pick a middling
   pace that reads as neither.

Model families disagree about conventions, so read `get_base_model` for the one you picked rather
than reusing phrasing that worked on another family. Where a model exposes structured
`video_effects` (entries with an uppercase `type` such as `ORBIT_360` or `DOLLY_IN`, plus an optional
`weight` from 0 to 100), prefer that over describing the same move in prose: it is the parameter the
model was tuned on.

## Duration, audio, and lip sync

Clip length is per-model and short, usually a handful of seconds. Do not plan a 30-second piece as
one generation without confirming a model supports it.

Some models choose their own length and ignore `duration_seconds` entirely. When the clip has to land
on an exact length, filter for `fixed_duration`, which excludes them. Without it a model may simply
hand back a different length, and nothing in the response reads as an error.

`generate_audio` is a capability, so filter for it when the clip needs native sound rather than
assuming silence can be fixed later. `lipsync` is a separate capability for dialogue on a character.
`filter.capabilities` is an object of booleans, not a list of names: `{generate_audio: true}`.

Video runs count against a tighter rate limit than images: 60 generations per minute per user, of
which at most 30 may be video.

## Multi-shot pieces

An ad, trailer, or cutscene is several shots. Before assembling, check whether a model can render
the whole thing in one generation, because one generation holds its own continuity and assembly does
not. When assembly is genuinely needed:

1. Lock the look with one approved still.
2. Generate each shot as `image_to_video` from a frame consistent with that still.
3. Cut them together with `layer-video-timeline`.

Storyboard it first if there are more than three shots: see `layer-art-direction`.

## Loops

Filter for the `loop` capability first. It selects models that compose a seam-free loop rather than
merely describing one, which is a different thing from a model that will accept the word "looping" in
a prompt and return a clip that jumps at the cut. Pair it with `fixed_duration` when the loop has to
be a specific length.

Failing that, generate the anchor frame and use it as both `first_frame` and `last_frame` where the
model accepts both, so the motion at least returns to where it started.

Either way, keep the motion cyclical by nature (a flag in wind, a torch flicker, a hovering idle) and
avoid one-way motion such as a character walking out of frame, which cannot be made to loop by any
amount of prompting.

## Worked example

"Animate this approved character key frame into a 5-second idle loop."

1. The frame exists from a previous run, so it already has a `file_id`.
2. `list_base_models` with `filter.use_case: "image_to_video"` and
   `filter.capabilities: {loop: true, fixed_duration: true}`, since this has to loop seamlessly and
   land on five seconds. Take the first result, then `get_base_model` to see whether it accepts
   `last_frame` and structured `video_effects`.
3. Prompt the motion only: "The character breathes slowly, cloak drifting in a light breeze, weight
   shifting subtly between feet. Locked-off camera. Gentle, continuous, no change in pose by the end
   of the clip."
4. Pass the same file as `first_frame` and `last_frame` so the loop closes.
5. Estimate. Video is priced well above images, so this will often clear 20 CUs and need an explicit
   yes.
6. Execute, poll at `poll_interval_seconds`, and check the seam by watching the end run into the
   start before calling it a loop.

## Common mistakes

- Prompting the scene instead of the motion, then reporting the model "barely moved".
- Using `text_to_video` when an approved still already exists.
- Leaving the camera unspecified, then fighting drift the model added by default.
- Describing a camera move in prose when the model exposes `video_effects`.
- Planning a long piece as one clip without checking a model's duration limit.
- Assuming audio can be added later on a model that could have generated it natively.
- Prompting for a loop instead of filtering for the `loop` capability.
- Leaving `fixed_duration` off when the clip has to land on an exact length.
- Calling a clip a loop without watching the seam.
