# Image→3D input rules — read BEFORE any submit

These rules prevent the two most expensive failure classes: garbage geometry
from bad reference images, and wrong polycount paths. Every image→3D submit
must pass this preflight — **whether through the native 3D CLI path
(`higgsfield generate create`, preferred) or the raw
fallback API**; the same engine reconstructs the mesh either way. (Param
behavior re-checked against docs.meshy.ai 2026-06-11.)

## Rule 1 — ONE figure per input image (character sheets)

Meshy reconstructs **everything in the frame as a single object**. A
character sheet with 4 views becomes "a statuette of 4 fused figures".

Mandatory preflight on every user-provided reference:

1. Vision check: "how many separate figures/views are in this image?"
2. If more than one figure → crop. Two valid paths:
   - **One best view** (front or 3/4) → regular `image-to-3d`.
   - **Each view as its own file** → `multi-image-to-3d` (1–4 images) —
     better geometry, but ONLY if the pose is identical on all panels.
     Different poses across panels ⇒ fall back to the single-view path.
3. Cropping in the sandbox: use **ffmpeg** (`ffmpeg -i sheet.png -vf
   "crop=w:h:x:y" view.png`) — PIL is not in the system python.

## Rule 2 — pose normalization

Add `"pose_mode": "t-pose"` (or `"a-pose"`): Meshy straightens the character
regardless of the reference pose. This repairs "awkward" references before
auto-rig and matches donor skeletons in the local rig-transfer path.

## Rule 3 — framing

- Full body in frame, nothing cut off.
- Clean/plain background; no shadows, text, watermarks, logos.
- Limbs visually separated from the torso (arms not pressed to the body) —
  fused silhouettes produce fused geometry and break auto-rig.
- One character, no props overlapping the silhouette.
- `image_enhancement: false` only if the exact input style must be preserved.

## Rule 4 — low-poly: two MUTUALLY EXCLUSIVE paths

Do not mix them:

| Goal | Params | Caveat |
|---|---|---|
| Stylized faceted low-poly LOOK | `"model_type": "lowpoly"` | Meshy IGNORES `topology`, `target_polycount`, `should_remesh`, `ai_model` in this mode — no precise budget control |
| Precise polygon BUDGET | `"should_remesh": true, "topology": "triangle", "target_polycount": N` | normal high-detail look, decimated |

Polycount budgets (game-ready guidance):

| Asset class | target_polycount |
|---|---|
| Hero / player character | 15 000 – 30 000 |
| NPC | 5 000 – 15 000 |
| Mob / prop | 1 000 – 5 000 |
| Background filler | 300 – 1 500 |

Valid API range: **100 – 300 000**.

**Hard rig limit: models > 300 000 faces are rejected by `/rigging`** — if
the mesh came out heavier, run `POST /openapi/v1/remesh` before rigging.

## Rule 5 — economy / QC params

- `"enable_pbr": false` — skip metallic/roughness/normal maps unless the
  project needs PBR (base color only is cheaper and faster).
- `"target_formats": ["glb"]` — don't generate unused fbx/obj/usdz/stl;
  task completes faster.
- `"multi_view_thumbnails": true` — 4 cardinal-view PNGs (front/right/back/
  left) in the task result for vision QC without downloading the GLB.

## Payload templates

Game humanoid, exact budget (recommended default):

```json
{
  "image_url": "<cropped single-figure reference>",
  "pose_mode": "t-pose",
  "should_remesh": true,
  "topology": "triangle",
  "target_polycount": 20000,
  "should_texture": true,
  "enable_pbr": false,
  "target_formats": ["glb"],
  "multi_view_thumbnails": true
}
```

Stylized faceted low-poly look:

```json
{
  "image_url": "<cropped single-figure reference>",
  "model_type": "lowpoly",
  "pose_mode": "t-pose",
  "should_texture": true,
  "enable_pbr": false,
  "target_formats": ["glb"],
  "multi_view_thumbnails": true
}
```

Multi-view (character sheet split into same-pose panels):

```json
{
  "image_urls": ["front.png", "side.png", "back.png"],
  "should_remesh": true,
  "topology": "triangle",
  "target_polycount": 20000,
  "should_texture": true,
  "target_formats": ["glb"]
}
```
(endpoint: `POST /openapi/v1/multi-image-to-3d`)

## Preflight checklist (run through it verbatim)

- [ ] Vision-counted figures in the reference == 1 (or split for multi-image)
- [ ] Full body, clean background, no text/watermark/shadows
- [ ] `pose_mode` set for characters that will be rigged
- [ ] Low-poly path chosen consciously (look vs budget) — params not mixed
- [ ] `target_polycount` matches asset class table
- [ ] `target_formats: ["glb"]`, `enable_pbr: false` unless PBR required
- [ ] Plan stays under rig limit (300k faces) if rigging follows
