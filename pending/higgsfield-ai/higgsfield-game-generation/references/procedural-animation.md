# Procedural animation — non-humanoid branch

When Meshy rigging returns `422 — Pose estimation failed` (anything that
isn't a clear biped: dragons, quadrupeds, snakes, spiders, fish, slimes) and
no Tripo3D key is available, build the rig and clips yourself in headless
Blender. **Verified on a dragon** (2026-06-10): 16 bones, distance weights,
sine-based `idle`/`fly` clips — fully scripted, zero manual steps.

## Pipeline

```
static mesh (Meshy text/image-to-3d, preview mesh is fine)
  → proc_rig_dragon.py    skeleton from bounding-box analysis → work.blend
  → proc_weights.py       distance-based skin weights (NOT bone heat)
  → proc_anim_dragon.py   sine clips baked to keyframes → animated GLB
```

```bash
blender -b -P $GAME_SKILL/scripts/proc_rig_dragon.py -- dragon.glb work.blend
blender -b work.blend -P $GAME_SKILL/scripts/proc_weights.py -- work.blend
blender -b work.blend -P $GAME_SKILL/scripts/proc_anim_dragon.py -- dragon_anim.glb
```

The three scripts are a worked example for a winged quadruped (dragon). For
other creatures only two things change: the **bone list** and the **motion
formulas** — see recipes below.

## Why not Blender's built-in tools (headless pitfalls)

- `parent_set(type='ARMATURE_AUTO')` (bone heat): on generated/photogrammetry
  meshes it either fails ("failed to find solution for one or more bones") or
  in headless mode **silently produces all-zero weights** → exported GLB has
  `skins: 0`. Always count weighted vertices after binding; must be > 0.
- Replacement that works: per-vertex **inverse-distance weights to the 2
  nearest bones** (distance from vertex to bone segment, not bone head).
  Crude but stable on any topology; quality is fine for stylized/low-poly.

## Skeleton from bbox analysis (proc_rig pattern)

- Long horizontal axis = body axis. Head side detection: the half (along the
  body axis) with more vertex volume in the UPPER part of the bbox is the
  head side (works for dragons/quadrupeds; for serpents just pick either end).
- Dragon layout (16 bones): `spine → chest → neck → head`, 4 tail segments
  (opposite the head), 2 bones per wing (inner/outer), 4 leg bones.
- Bone positions are fractions of the bbox — no mesh-specific magic numbers;
  the same script reruns on the textured mesh later (texture swap rule).

## Motion recipes per creature type

All clips are sums of sinusoids baked to keyframes (every 1–2 frames, 24 fps).
Core idiom: `angle(t) = A * sin(2π * t/T + φ)` per bone, with phase offsets φ
creating wave propagation and gait patterns.

| Creature | Skeleton | Locomotion formula |
|---|---|---|
| Winged (dragon, bird) | spine chain + 2-segment wings + tail | fly: wings ±35–45°, outer segment lags inner by 0.15–0.25 of the cycle (flex illusion); body bobs in COUNTER-phase to the downstroke; legs tucked (constant); tail wave |
| Quadruped (wolf, dog) | spine + neck/head + 4 legs (2 segments) + tail | walk: diagonal pairs in counter-phase — LF+RH at φ=0, RF+LH at φ=π; spine sways laterally at half amplitude; head bob small |
| Hexapod (insect) | thorax + 6 legs | alternating tripod: legs {L1,R2,L3} φ=0, {R1,L2,R3} φ=π |
| Octopod (spider) | cephalothorax + 8 legs | two tetrapod groups in counter-phase; adjacent legs offset by π/4 for ripple |
| Serpentine (snake) | 8–12 segment spine chain | traveling wave: segment i gets φ = i * 2π/N, lateral rotation ±20–30°; amplitude grows toward tail |
| Aquatic (fish) | spine chain + fins | same traveling wave but amplitude concentrated in rear third; fins counter-flap at 2× frequency, small amplitude |
| Slime / blob (no skeleton) | none — or 1 root bone | squash & stretch on scale: `sz = 1 + A*sin(ωt)`, `sx = sy = 1/sqrt(sz)` (volume preservation); add small location bounce synced to squash |

Idle for any creature: breathing (chest scale or rotation ±2–4°, 4 s cycle),
slow head sway, tail/appendage micro-wave, wing micro-adjust.

## Vision-QC loop (mandatory — you can't see WebGL)

1. Render the animated model at several phases of the cycle with Blender CLI
   (camera auto-framed from bbox), tile into a grid image.
2. Vision-check the grid: do phases differ? Is the motion logic right (e.g.
   wing area shrinks on upstroke, opens on downstroke)? Any mesh tearing at
   joints?
3. **Phase-sampling pitfall:** sampling frames at uniform steps that alias
   with the cycle period makes all renders look identical and you'll wrongly
   conclude "animation is broken" (or miss that it is). Sample at non-uniform
   cycle fractions, e.g. 0.0, 0.23, 0.41, 0.68, 0.87 of the period.
4. Known acceptable defects: slight pinching at wing/limb roots (typical of
   auto-skinning), no per-toe detail.

## Texture-swap rule

Never block on Meshy refine (texture) — rig/weights/clips run on the gray
preview mesh; when the textured mesh arrives, re-run the same three scripts
on it (bbox-relative skeleton makes this deterministic). See stuck-refine
recovery in `meshy-api.md`.

## Tripo3D alternative (UNVERIFIED — needs API key)

Tripo3D (the UniRig authors; UniRig itself needs a GPU we don't have) has
creature rigging in the cloud:

1. `animate_prerigcheck` — asks if the model is riggable, returns skeleton
   type: `biped`, `quadruped`, `hexapod`, `octopod`, `avian`, `serpentine`,
   `aquatic`.
2. Rig task for that skeleton type.
3. `animate_retarget` — locomotion presets per type
   (`preset:quadruped:walk`, `preset:hexapod:walk`, `preset:octopod:walk`,
   `preset:serpentine:march`, `preset:aquatic:march`; biped also gets
   idle/walk/run/jump/slash/shoot/hurt/fall/climb/dive/turn). Up to 5
   animations per request, GLB/FBX out.

Far fewer presets than Meshy's 680, but for NPC monsters walk + idle is
usually enough. Hybrid works: generate the mesh in Meshy, rig/animate in
Tripo via `model_url` — formats are compatible. Mark results as unverified
until first successful run; keep the procedural branch as fallback.

## Three.js consumption

Identical to humanoid GLBs: `GLTFLoader` + `AnimationMixer`, clips by name
(`idle`, `fly`). For slime-class assets skip the rig entirely and animate
`mesh.scale`/`position` in the render loop.
