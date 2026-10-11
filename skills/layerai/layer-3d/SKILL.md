---
name: layer-3d
description: "Use when producing 3D assets with Layer: generating a mesh from text or an image, retopologising or remeshing, retexturing an existing mesh, rigging a character, or animating a rigged mesh. Also when choosing between quad and triangle output, setting a polygon budget, or asking for PBR textures for a game engine. Keywords: 3D, mesh, model, text to 3D, image to 3D, remesh, retopology, retexture, rig, skeleton, animate, PBR, quad mesh, poly count, glTF, FBX."
license: MIT
---

# Layer 3D Generation

## Overview

3D on Layer is a chain of separate use cases, not one call. Generate the mesh, then remesh, retexture,
rig, or animate it as the deliverable requires. Each stage is its own `filter.use_case` and its own
run, and each takes the previous stage's output `file_id` as input.

| Stage                            | `filter.use_case` | Input                              |
| -------------------------------- | ----------------- | ---------------------------------- |
| Mesh from a description          | `text_to_3d`      | prompt                             |
| Mesh from concept art            | `image_to_3d`     | `init_image` or `reference_image`  |
| Cleaner topology, lower count    | `remesh`          | `init_mesh`                        |
| New surfaces on an existing mesh | `retexture`       | `init_mesh`, often `texture_image` |
| Skeleton and weights             | `rig`             | `init_mesh`                        |
| Motion on a rigged mesh          | `animate`         | rigged `init_mesh`                 |

The loop and the spend gate are in the `layer` skill. If a sibling skill named here is missing from
your available skills, ask the user to install it (`npx skills add layerai/skills --skill <name>`);
unattended, proceed from tool schemas and flag the gap.

## Start from an image

`image_to_3d` is the stronger path whenever the design is settled or settleable. A generated mesh
inherits its silhouette and surface detail from the reference, so approving a still first with
`layer-image` costs one cheap image run and removes most of the iteration from an expensive 3D one.

The reference image should show the subject clean: isolated on a plain background, lit evenly, in a
three-quarter view that reveals depth. A dramatic, heavily shadowed key art frame makes a worse
reference than a plain orthographic-ish view, because the model reads shadow as geometry.

`text_to_3d` is right when nothing exists yet and the shape is simple or generic enough to describe.

## Say what the mesh is for

The engine target changes the request, so state it rather than accepting defaults:

- **Topology**: `quad_mesh` where the asset will be sculpted, deformed, or subdivided downstream.
  Triangles are fine for a static prop that ships as-is.
- **Budget**: a `face_limit` reflecting the platform. A hero prop on desktop and a background prop on
  mobile are different requests, and remeshing later costs another run.
- **Surfaces**: `pbr_materials` and `include_textures` when the asset goes into a lit scene. Without
  them you get geometry and a flat surface, which reads as broken in an engine.

The per-model inference schema is the authority on which of these apply, so read `get_base_model`
before composing the run.

## Describing geometry

3D prompts reward structural language and ignore atmosphere. Lighting, mood, and camera belong to an
image prompt and do nothing here, because the mesh carries no lighting.

Name the form: overall silhouette, proportions, how parts join, surface material, and the level of
detail. "Squat clay cooking pot, wide rounded belly, short flared neck, two small looped handles at
the shoulder, hand-thrown surface with visible ridges" describes a mesh. "Beautiful ancient pot,
dramatic lighting" describes a photograph and will produce a generic one.

Symmetry and closed forms generate reliably. Thin protrusions, chains, cloth, and hair are where
generated meshes fail, so plan to model those separately or accept them as fused geometry.

## Rigging and animation

`rig` produces a skeleton and weights, and it expects a mesh in a neutral, limbs-apart rest pose. A
mesh generated in a dynamic action pose rigs badly, so generate the rest pose first and animate into
the action.

`animate` needs a rigged mesh, so the two run in order. Where a model offers named motion presets,
those are more reliable than describing the motion in prose.

## Worked example

"Turn this approved prop concept into a game-ready mesh for mobile."

1. The concept exists from an earlier image run and already carries a `file_id`.
2. `list_base_models` with `filter.use_case: "image_to_3d"` and
   `filter.capabilities: {textures: true}` (an object of booleans, not a list of names).
   Take the first result, then `get_base_model` for the fields it accepts.
3. `estimate_forge_price` with the concept as `image_to_3d` input, `pbr_materials` and
   `include_textures` on, `quad_mesh` off for a static prop, and a `face_limit` matched to mobile. 3D
   runs are expensive, so expect this to clear 20 CUs and ask before proceeding.
4. Execute, poll at `poll_interval_seconds`.
5. Inspect the result before chaining. If the silhouette is right but the count is too high, the next
   run is `remesh` on the output `file_id`, not a regenerate.

## Common mistakes

- Using `text_to_3d` when concept art exists or could be generated cheaply first.
- Feeding a dramatic, shadow-heavy key art frame as the 3D reference.
- Writing an image prompt (lighting, mood, camera) for a mesh.
- Leaving topology, budget, and materials unspecified, then remeshing in a second paid run.
- Rigging a mesh generated in an action pose.
- Regenerating from scratch when `remesh` or `retexture` would fix the actual defect.
- Expecting clean thin geometry such as chains, straps, or hair from a generated mesh.
