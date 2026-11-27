# Orthogonal Visual Style Adapters Matrix / 跨画风正交解耦适配规范

Livestream perspective is **camera, eye-line, and temporal grammar**—not a single rendering shader. By separating **Camera Rig (`rig_spec.mjs --rig`)** from **Visual Style Pack (`--style`)**, any visual world can feel unmistakably like a live broadcast.

## 1. Style Pack Comparison & Invariant Locks

| Style ID | Target Aesthetic | Mandatory Positive Geometry & Material Locks | Mandatory Anti-Drift Exclusions |
| --- | --- | --- | --- |
| `realistic-irl` | General photorealistic AI video (IRL, studio, unboxing, bodycam) | Natural human proportions & micro-skin texture, five-finger firm grip on smartphone/mic/item, realistic smartphone/webcam auto-exposure & ring-light catchlights | Waxy plastic AI skin, 6 fingers, cinema 2.39:1 black bars, anamorphic flares, burned-in gibberish UI |
| `roblox-blocky` | Roblox R6 / Chibi-Blocky / R15 streamer shorts | `2×2×1` chamfered rectangular torso, two flush `1×2×1` rectangular leg blocks (zero thigh gap), **fingerless & clawless solid `1×2×1` block hands**, smooth studless `1:1` barrel head, flat 2D screen-printed decal face, rigid `Motor6D` hinges, smooth `SmoothPlastic` / `WoodPlanks` floors | Human five fingers, Lego C-claws, raised circular Lego floor/head studs, Minecraft `8×8×8` sharp voxel head, 3D human nose, rubbery noodle limbs, official Roblox logos |
| `anime-vtuber` | 2D cel-shaded anime IRL or Live2D / 3D VTuber | Clean ink linework, cel-shaded shading, layered anime iris catchlights, head-tracking spring hair physics, crisp anime desk or Live2D bust framing | Uncanny semi-realistic 3D nose/pores, smudged linework, extra fingers, garbled chat text |
| `stylized-3d` | Blind-box vinyl / clay / Pixar-grade stylized 3D | Tactile subsurface-scattered matte vinyl & plush fabric, 3-head chibi-stylized proportions, miniature studio desk & softbox GI | Photorealistic uncanny human face, sharp voxels, Lego bumps, burned-in text |
| `voxel-sandbox` | `8×8×8` / `16×16×16` pixel-grid sandbox | Sharp `1:1:1` cubic `8×8×8` head, `8×12×4` torso, fingerless flat `4×4` pixel-block hands, `+0.5px` 3D outer headset/hoodie layer, unfiltered nearest-neighbor `16×16` texels | Human fingers, bilinear blurry textures, rounded cylindrical heads, smooth round rods |
| `cinematic-genre-adapt` | Wuxia, fantasy, medieval, sci-fi, cyberpunk, period drama | High-craft genre wardrobe & world scale shot strictly through an intimate `18mm` selfie talisman/visor/handheld lens, wind-whipped hair, direct viewer banter | Detached third-person movie trailer framing, actors ignoring lens, widescreen cinema bars |

## 2. Deep-Dive: Photorealistic / General AI Video (`realistic-irl`)

When generating realistic livestream clips in Kling 2.0, Seedance, Sora, Veo 3, or Wan 2.6:
- **Avoid over-cinematic polish**: Replace `"cinematic lighting, 85mm f/1.2 portrait lens, film grain"` with `"18mm front-facing smartphone camera at arm's length, natural night-market neon spill plus cool phone-screen fill on face, deep f/4 focus"`.
- **Anchor hands physically**: Handheld selfie clips look fake if the camera floats without arm geometry. Explicitly state `"extending right arm toward the front-facing lens (forearm angle leading toward frame corner)"` or use `chest-head-pov` with `"left hand holding glowing chat smartphone, right hand sweeping flashlight"`.

## 3. Deep-Dive: Roblox Blocky Livestream (`roblox-blocky`)

When combining Roblox characters with livestream rigs (`pip-facecam-rig`, `handheld-selfie-irl`, `pk-cohost-split`):
- **Rigid Prop Docking**: Because canonical Roblox `1×2×1` arms end in flat fingerless beveled rectangular blocks, never write `"wraps fingers around the selfie stick"` or `"pinches product"`. Write: `"a blocky selfie-stick smartphone docked flush against the flat end of the right solid 1x2x1 rectangular block hand"`.
- **2D Expression Toggles for Live Reactions**: Swap flat 2D decals cleanly across cuts (`Check-It smirk` on Shot 1 Hook → `intense focused eyes with blue 2D sweat drop` on Shot 2 → `wide hollow shocked ring eyes O_O` on Shot 3 fail → `streaming blue 2D waterfall tear strips` or `X_X dizzy eyes` on Shot 4 desk-slam).

## 4. Deep-Dive: Cross-Genre Diegetic Livestream (`cinematic-genre-adapt`)

To adapt **any non-modern plot** into a livestream perspective without breaking visual coherence, translate the capture device into an **in-universe optical equivalent** while keeping 100% modern livestream body language:
- **Wuxia / Xianxia (`仙侠古风`)**: Floating/handheld glowing jade slip (`发光传音玉简前置直拍`), `18mm` ultra-wide cloud-sea selfie angle, shouting `"御剑直播间的道友们双击点亮！"`.
- **Medieval / Dungeon (`奇幻地牢`)**: Floating arcane crystal orb held at arm's length (`奥术水晶球一臂自拍机位`) casting cool cyan face fill inside torchlit stone corridors.
- **Sci-Fi / Horror (`科幻太空/异形走廊`)**: `16mm` helmet visor / tactical chest-rig live telemetry feed (`战术胸挂广角直拍`).
