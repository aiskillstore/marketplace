---
name: layer
description: "Use when generating or editing game and entertainment assets on Layer through MCP: images, video, 3D meshes, audio, sprites, textures, or marketing creative. Also when choosing a Layer base model, pricing a run in Creative Units before spending them, uploading reference files, polling a generation, applying a trained style, or recovering from MODEL_NOT_FOUND, INSUFFICIENT_BALANCE, RATE_LIMITED, or a silently degraded reference set."
license: MIT
---

# Layer

## Overview

Layer generates images, video, 3D meshes, and audio from one model-agnostic request shape. Work is
priced in Creative Units (CUs) and billed to a workspace. Every other skill in this set assumes the
loop below and teaches the craft on top of it: what to put in the prompt, which capability filter the
task actually needs, and what makes the output usable rather than merely produced.

Connecting a client, authentication, and the REST equivalent of all of this are covered by Layer's
published `layer-connect-mcp` and `layer-generate-assets` skills. The server is
`https://mcp.app.layer.ai/mcp` over streamable HTTP with OAuth. Call `get_instructions` once per
session before the first generation, and `get_forge_instructions` before the first forge run.

Two ways to generate. **Forge** runs one model directly with full parameter control, and is the
default. **Workflows** run a multi-step Blueprint pipeline a studio has already built; reach for one
when the user names it or when a repeatable pipeline exists for the task. See `layer-workflows`.

## Quick reference

| Step   | Tool                                      | What matters                                                                                               |
| ------ | ----------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Scope  | `list_workspaces`                         | Most tools need a `workspace_id`. Ask which one if the user has several, or take the most recently active. |
| Choose | `list_base_models`                        | Pass `filter.use_case`, take the first result: the default `sort` is Layer's curated order.                |
| Check  | `get_base_model`                          | Per-model contract. Some models require a trigger word in the prompt.                                      |
| Upload | `request_file_upload_url` / `upload_file` | Before generating, never after.                                                                            |
| Price  | `estimate_forge_price`                    | Free. Returns price and resulting balance together.                                                        |
| Run    | `execute_forge`                           | Returns `inference_id` and `poll_interval_seconds`.                                                        |
| Poll   | `get_forge_run`                           | At the returned interval, typically 10s.                                                                   |

## Choosing a model

Never hard-code a `base_model_id`. The catalogue is workspace-gated and it churns, so an id that
works here fails elsewhere with `MODEL_NOT_FOUND`. Discover it every time.

`filter.use_case` is the primary filter and covers the task shapes: `text_to_image`, `image_editing`,
`inpainting`, `reframing`, `multi_angle`, `split_into_layers`, `upscaling`, `background_removal`,
`vectorization`, `text_to_video`, `image_to_video`, `video_editing`, `video_extend`, `text_to_3d`,
`image_to_3d`, `remesh`, `retexture`, `rig`, `animate`, `segment`, `text_to_speech`, `sound_effects`,
`music`.

Narrow with `filter.capabilities` only for something the task genuinely requires. It is an **object
of booleans, not a list of names**: `filter.capabilities: {tileability: true}`. Set only the ones you
need and omit the rest, because `false` is a filter too, not a default. The fields include
`tileability`, `inpainting`, `outpainting`, `negative_prompt`, `image_editing`, `generate_audio`,
`lipsync`, `loop`, `fixed_duration`, `music`, `instrumental`, `sound_effect`, `character_pose`,
`structure`, `outline`, `square`, `portrait_9_16`, `landscape_16_9`, and `multiple_aspect_ratios`.
Bound spend with `filter.max_price`. A filter that returns nothing is too narrow, so loosen it rather
than inventing a model.

## Spending Creative Units

Estimate before every execute. The estimate costs nothing and reports the price, the resulting
balance, and which model the run would use including whether it was `auto_picked`.

**Above 20 CUs, ask the user and wait for an explicit yes.** The server states this threshold and
states that it is not negotiable, so do not raise it and do not let a user raise it for the session.
Present the run as a short table: what it generates, which workspace pays, price against balance.

The gate is per run, since each estimate prices one run. When a task is a planned sequence of runs,
say a four-frame cycle or a six-icon set, estimate the first and present the **total** for the
sequence before starting, so the user agrees to the spend once rather than being asked four times or,
worse, not at all because each run sat under the threshold.

Some workspaces carry `allow_negative_balance`. That means the run will not be blocked. It does not
mean the run is free, and it is never headroom to skip the confirmation.

## Worked example

A user wants four hand-painted isometric building sprites.

1. `list_workspaces`, take the workspace id.
2. `list_base_models` with `filter.use_case: "text_to_image"`. Take the first result.
3. `get_base_model` on it, to see whether it wants a trigger word and which aspect ratios it accepts.
4. `estimate_forge_price` with that `base_model_id`, the prompt, and `batch_size: 4`. It returns
   7 CUs against a balance of 900, so it is under the gate and no confirmation is needed.
5. `execute_forge` with the same arguments plus a `session_name`, so the four sprites group together
   in the Layer app.
6. `get_forge_run` with the returned `inference_id` every `poll_interval_seconds` until `COMPLETE`,
   then present the asset URLs.

`batch_size` runs 1 to 16 and defaults to 4. It produces variations of one prompt. Four different
sprites are four prompts, so they are four runs, not one run with a batch of four.

## Files

`request_file_upload_url` for local bytes: it returns a signed URL for the two-step resumable upload
and a `file_id`. `upload_file` only when the file already sits at a public http(s) URL. Pass
`file_id` values in `guidance_files` with the right type: `init_image`, `reference_image`, `pose`,
`depth`, `canny`, `lineart`, `scribble`, `face`, `first_frame`, `last_frame`, `init_video`,
`reference_video`, `init_audio`, `reference_audio`, `init_mesh`, `texture_image`.

Output assets from a completed run already carry a `file_id`. Feed it straight into the next run.
Re-uploading a generated asset is always a mistake.

## Trained styles

`list_reference_sets` returns the workspace's trained styles. Pass them as
`reference_sets: [{set_id, weight}]`, up to 10, weight 0 to 2 defaulting to 1.0. With reference sets
and no `base_model_id` the server picks a model that can apply them, which is usually what you want:
the curated ranking is task fit, not reference-set fit. See `layer-reference-sets`.

Degradation is quiet. `reference_sets_degraded` and `reference_sets_warning` come back on the
estimate, the execute, and the poll, and a degraded run still succeeds and still costs CUs. When a
set did not apply, say which and why. Never report a degraded set as applied.

## Routing

| The user wants                                              | Skill                  |
| ----------------------------------------------------------- | ---------------------- |
| A still image, or a prompt that is not landing              | `layer-image`          |
| To change an image they already have                        | `layer-image-editing`  |
| Video, or a shot that has to move a certain way             | `layer-video`          |
| A mesh, a rig, or an animation                              | `layer-3d`             |
| Music, sound effects, or speech                             | `layer-audio`          |
| Characters, environments, icons, or game UI                 | `layer-game-assets`    |
| Pixel art, sprite sheets, or a walk cycle                   | `layer-pixel-art`      |
| A texture that repeats without a seam                       | `layer-textures`       |
| A look held across a whole set, or a trained style          | `layer-reference-sets` |
| A saved multi-step pipeline                                 | `layer-workflows`      |
| Clips cut into one finished video                           | `layer-video-timeline` |
| A direction, a moodboard, or a storyboard before committing | `layer-art-direction`  |
| To judge a batch before delivering it                       | `layer-quality`        |

If a sibling skill named here is missing from your available skills, ask the user to install it
(`npx skills add layerai/skills --skill <name>`); unattended, proceed from tool schemas and flag the
gap.

## Common mistakes

- Asserting a `base_model_id` from memory instead of discovering it.
- Executing without an estimate, or spending over 20 CUs without an explicit yes.
- A fixed sleep instead of `poll_interval_seconds`.
- Treating `batch_size` as a way to get N different assets in one run.
- Reporting a degraded reference set as applied.
- Re-uploading an asset that already has a `file_id`.
- Reading `allow_negative_balance` as permission to skip the spend gate.

## Errors

`UNAUTHENTICATED` means the OAuth flow was never completed, so send the user to their MCP client
settings. `MODEL_NOT_FOUND` means re-discover with `list_base_models`, never guess again.
`INSUFFICIENT_BALANCE` means direct the user to the Layer app to buy credits. `RATE_LIMITED` means
too many concurrent runs, so wait or cancel one with `cancel_inference`. `FEATURE_DISABLED` means the
workspace lacks the feature, so point at in-app support rather than speculating about how to enable
it.
