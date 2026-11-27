---
name: minecraft-style-video
description: |
  Generate Minecraft-style voxel character, mob, and block short videos with locked 8x8x8/16x16x16 pixel-grid geometry, 9:16 storyboards, and model-specific prompts.
  Use when the user wants to generate Minecraft-style character or object videos, voxel block/item/mob shorts, Douyin/Xiaohongshu/TikTok Minecraft skits, isometric voxel builds, Steve/Alex/Creeper/Enderman turnaround sheets, or prompts for Kling (可灵), Seedance/Jimeng (即梦), Hailuo MiniMax (海螺), Wan (通义万相), Sora, or Runway, or when fixing AI video defects such as five human fingers on cube hands, blurry textures, Roblox cylindrical heads, Lego studs/C-claws, smooth metal tools, or rubbery limbs.
  中文触发词：我的世界（MC）像素方块小人竖屏短视频、本地3D动画预览与分镜脚本、可灵/即梦防崩坏提示词、防止AI视频把方块手画成五根手指或圆滑金属。
license: MIT
metadata:
  version: "1.3.1"
---

# Minecraft Style Video (`minecraft-style-video`)

## Core Objective / 核心目标

Help creators turn a short-video idea into a geometry-consistent Minecraft-style voxel character, mob, and block/item video package: a locked Character & Voxel Object DNA card, a 3-view or isometric reference sheet prompt, a 9:16 beat-timed storyboard, model-specific Image-to-Video (I2V) or Text-to-Video (T2V) prompts, and prompt patches when a video clip drifts.

Respond in the user's language. When the user requests bilingual output, provide Chinese explanations alongside English generation prompts and Chinese prompt equivalents for domestic engines (Kling 可灵, Seedance/Jimeng 即梦, Hailuo 海螺, Wan 通义万相).

General video diffusion models default to human anatomy, blurry anti-aliased textures, rounded Roblox cylinders, or Lego studs when prompted vaguely with "Minecraft character" or "Minecraft block." This skill prevents style drift by locking **eight authentic Minecraft visual invariants** before writing motion prompts:

1. **Canonical Pixel-Grid Character Proportions (`8×8×8` Head + `8×12×4` Torso + `4×12×4` / `3×12×4` Limbs)**:
   - **Head**: `8 × 8 × 8` pixel units (`0.5 × 0.5 × 0.5` blocks, exact `1:1:1` sharp right-angle cube; never a rounded Roblox cylinder or a Lego stud top).
   - **Torso**: `8 × 12 × 4` pixel units (`2 : 3 : 1` rectangular prism).
   - **Arms**: `4 × 12 × 4` pixel units (**Classic Wide / Steve rig**) or `3 × 12 × 4` pixel units (**Slim / Alex rig**) hanging flush against the torso sides.
   - **Legs**: Two `4 × 12 × 4` pixel rectangular prisms sitting **flush side-by-side** directly beneath the `8px` torso (`4 + 4 = 8px` total width).
2. **Flat Square `4×4` / `3×4` Block Hands (No Fingers AND No Lego C-Claws)**:
   - Minecraft arms terminate in a **flat square `4×4` (or `3×4`) pixel-grid cross-section** (`fingerless and clawless flat 4x4 square pixel-block hand ends, zero human fingers, zero Lego C-shaped hooks`).
3. **3D Outer Skin Overlay Layer (`+0.5px` Hat / Jacket / Sleeve / Pants Shell)**:
   - Authentic `64×64` Minecraft skins use a raised second layer (`+0.5px` on head for 3D bangs, hoods, crowns, or helmets; `+0.25px` on torso/limbs for jackets and cuffs) that casts subtle pixel-stepped depth shadows over the base cube.
4. **Crisp Nearest-Neighbor Pixel Texels (`16×16` Blocks & `8×8` Faces)**:
   - Every character, mob, and block surface uses **unfiltered nearest-neighbor square pixel texels** (`crisp 16x16 pixel-art block textures, 8x8 pixel face grid, zero bilinear blur, no realistic skin pores or high-res photo textures`).
   - Expressive faces follow the **Fresh Animations / Official Trailer** standard: `2×1` white sclera + sliding `1×1` pupil pixel eyes + floating `2×1` pixel eyebrow strips on the flat front `8×8` head plane (`no 3D protruding human nose`).
5. **Authentic Voxel Blocks, Extruded `16×16×1` Held Items & Mobs**:
   - **Full World Blocks (`16×16×16` texels, `1m³`)**: `Grass Block` (green top + jagged grass side overhang + dirt grid), `Diamond Ore` (stone grid + glowing `#4AEDD9` cyan clusters), `TNT Block` (red dynamite bars + white `TNT` band), `Crafting Table`, `Redstone Lamp`.
   - **Sub-Block Props**: Hinged `Chest` (`14×14×14`px with a `2×4` silver pixel front latch), `Torch` / `Lantern` (`2×10×2` pixel stick with emissive `2×2×2` flame).
   - **Extruded Held Tools (`16×16×1` pixel-art thickness)**: `Diamond Pickaxe`, `Diamond Sword`, `Golden Apple`, and `Torch` are `16×16` pixel sprites extruded `1px` thick with stepped 90-degree pixel edges (never smooth cylindrical metal blades or round wooden rods).
   - **Iconic Mobs**: `Creeper` (`8×8×8` head, `8×12×4` body, zero arms, four `4×6×4` short legs), `Enderman` (tall black `8×8×8` cube head with glowing purple `3×1` pixel eyes and long `2×30×2` stick limbs holding a `Grass Block`), and `Pink Axolotl` / `Wolf`.
6. **Shader & Lighting Signatures (`BSL/Complementary Sunlight` vs. `Bare Bones Trailer`)**:
   - Pair crisp `16×16` pixel texels with either warm volumetric shader sunlight + emissive block light (`bsl-sunlight`), clean flat-shaded trailer bevels (`bare-bones-trailer`), classic vanilla ambient occlusion (`vanilla-crisp`), or glowing ore/redstone raytracing (`rtx-emissive`).
7. **Blocky Hinge Physics & Single-Action Clip Budget**:
   - Rigid shoulder/hip pivot swings (or clean 90-degree Blockbench elbow/knee bends) with at most **one primary character/block action and one camera move** per 4 to 5 second clip.
8. **First-Frame I2V Anchor**:
   - Generate or render a static 3-view character turnaround sheet, voxel object card, and shot keyframes before running video diffusion so `8×8` pixel faces and `16×16` block grids do not smudge across cuts.

## Six Production Modes / 六种工作模式

Select the mode that matches the user's current stage, or chain them end-to-end for a full episode:

1. **Voxel-Spec · 角色与方块设定**: build a Minecraft Character, Mob, or Block/Item DNA card (`8×8×8` / `16×16×16` pixel lock, `+0.5px` 3D skin layer, extruded `16×16×1` held item) and a 3-view or isometric reference prompt (`scripts/voxel_spec.mjs`).
2. **Storyboard · 黄金分镜**: break a 15s or 30s vertical 9:16 idea into a 0 to 3.5s hook, escalation shots, voxel block/item interactions, and a payoff or loop (`references/short-video-beats-and-audio.md`).
3. **Prompt-Compile · 提示词编译**: compile each shot into first-frame image prompts, I2V/T2V motion prompts, and negative anti-drift tokens for Kling, Seedance/Jimeng, Hailuo, Wan, Sora, or Runway (`scripts/shot_compiler.mjs`).
4. **Rescue · 翻车救场**: lint a failing prompt or diagnose rendered video defects such as human fingers, blurry textures, Roblox cylinder heads, Lego studs/C-claws, smooth round tools, or rubbery limbs (`scripts/drift_check.mjs` and `references/rescue-and-anti-drift.md`).
5. **Remix · 爆款拆解与二创**: adapt one of six viral Minecraft short-video templates covering mining ambushes, cozy isometric builds, redstone ASMR, and duo pranks (`references/viral-archetypes-catalog.md`).
6. **Render & Package · 3D预览渲染与归档**: render 3D Minecraft character turnarounds, voxel block/item/mob showcases, 4-way anti-drift comparisons, 9:16 storyboard contact sheets, and animated `.gif` / `.mp4` previews (`scripts/render_preview.mjs`), and write a reproducible episode folder (`examples/`).

## Intake Checklist / 需求确认清单

Ask only for details that change the character/object geometry, shot timing, or target video engine. If the user asks for an immediate draft, apply the defaults below and state them briefly.

Key inputs:

- **Topic or scenario / 剧情或物体场景**: e.g., diamond cave Creeper ambush, cozy isometric lantern cabin build, Pro builder vs. Noob TNT prank, redstone piston ASMR.
- **Character / Mob archetype / 角色或生物预设**:
  - `steve-miner`: classic wide `4×12×4` arms, cyan tunic, 3D hair layer, holding a stepped `16×16×1` Diamond Pickaxe.
  - `alex-builder`: slim `3×12×4` arms, moss-green tunic, 3D ginger side-ponytail & beret layer, holding a warm Lantern or Oak Planks.
  - `diamond-knight`: full 3D outer layer `#4AEDD9` diamond helmet and chestplate with enchanted purple glint, holding a `16×16×1` Diamond Sword.
  - `cozy-hoodie`: aesthetic skin with 3D pastel hoodie outer shell, headphones, and Fresh Animations expressive pixel eyes.
  - `creeper-mob`: canonical armless quadrupedal `8×8×8` + `8×12×4` + four `4×6×4` legs with green `16×16` leaf-camo texels.
  - `enderman-mob`: tall jet-black cubic figure with glowing purple `3×1` pixel eyes carrying a `16×16×16` Grass Block.
  - `axolotl-pet`: blocky pink voxel amphibian with 3D external pixel gill fronds.
- **Featured Voxel Object / 核心方块或道具**: `diamond-ore`, `grass-block`, `tnt-block`, `crafting-table`, `chest-hinged`, `lantern-torch`, `diamond-pickaxe`, `diamond-sword`, `redstone-piston`.
- **Target video model / 目标生成工具**: Kling (可灵), Seedance/Jimeng (即梦), Hailuo MiniMax (海螺), Wan (通义万相), Sora, or Runway.
- **Workflow mode / 生成路径**: First-Frame Image-to-Video (`I2V`, default for multi-shot pixel consistency) or direct Text-to-Video (`T2V`).
- **Duration and aspect ratio / 时长与画幅**: default `15s` (4 shots) or `30s` (8 shots) in `9:16` vertical format (`1080x1920`).

Default assumptions when unspecified:

- Character & Object: `steve-miner` with `diamond-pickaxe` and `diamond-ore` (or `alex-builder` with `grass-block` and `lantern-torch` for building themes), using `bsl-sunlight` shader.
- Workflow: `I2V` (generate pixel-locked image keyframes first, then animate).
- Aspect ratio: `9:16` vertical, `15s` total duration (4 shots of 3.5 to 4.0 seconds each).
- Engine output: bilingual prompts suitable for Kling / Seedance / Wan and English prompts for Sora / Runway / Hailuo.

## End-to-End Workflow / 标准工作流

### Step 1: Lock Character, Mob & Voxel Object DNA

Read `references/voxel-geometry-blocks-and-shaders.md` and run `scripts/voxel_spec.mjs` to lock the character's `8×8×8` head, `+0.5px` 3D skin layer, `4×12×4` / `3×12×4` square hands, and `16×16×16` block or `16×16×1` extruded item geometry before drafting scene prompts:

```bash
node scripts/voxel_spec.mjs --archetype steve-miner --object diamond-ore --held-item diamond-pickaxe --shader bsl-sunlight --name "Steve" --lang zh-en
```

Give the user:
- The Character & Voxel Object DNA table (pixel dimensions, rig width, 3D outer skin shell, held item geometry, block texel rule, shader).
- A copy-pasteable 3-View Character Turnaround Prompt and Isometric Voxel Block/Item Prompt.
- The anti-drift negative prompt block.

### Step 2: Plan the 9:16 Short-Video Beat Sheet

Read `references/short-video-beats-and-audio.md` and `references/viral-archetypes-catalog.md`. Structure the short into three retention zones:

- **Shot 1 (0.0s to 3.5s) · Hook / 黄金前3秒**: immediate voxel interaction (pickaxe cracking a glowing Diamond Ore block, snapping a lantern onto a miniature cabin, or placing a TNT block), paired with an expressive `8×8` pixel eye shift.
- **Shots 2 to N-1 · Escalation / 推进镜头**: 3.5s to 4.0s per shot. Each shot gets **one clear physical verb** (e.g., "breaks the 16x16x16 diamond ore block into cubic pixel particles" or "Creeper swells and flashes white behind the miner").
- **Final Shot · Payoff or Loop / 反转或无缝循环**: cubic explosion smoke burst, shader lighting reveal, or synchronized `45°` cubic head turn that loops back to Frame 1.

### Step 3: Compile Model-Tuned Prompts

Read `references/model-prompt-playbook.md` and run `scripts/shot_compiler.mjs` to generate shot-by-shot prompts tailored to the user's video engine:

```bash
node scripts/shot_compiler.mjs --template diamond-creeper-ambush --duration 15 --engine kling --shader bsl-sunlight --lang zh-en
```

Every compiled shot must include:
1. **First-Frame Image Prompt (首帧画面提示词)**: pixel-locked static composition for Midjourney, Flux, Jimeng Image, or GPT-4o Image.
2. **I2V / T2V Motion Prompt (视频动态提示词)**: subject & block anchor + single action + voxel secondary physics (cubic particle pop, cape/hair outer-layer bounce, item bobbing) + engine-specific camera command.
3. **Negative Prompt (负向防串味词)**: explicit exclusions for human fingers, blurry bilinear textures, Roblox rounded heads, Lego studs/C-claws, and smooth cylindrical tools.
4. **Audio and Caption Cue (音效与花字卡点)**: classic Minecraft block break, XP orb ding, Creeper hiss, chest creak, or subtitle timing.

### Step 4: Lint for Style Drift and Rescue Failures

Before handing off custom prompts, or whenever the user reports a broken generation, run `scripts/drift_check.mjs`:

```bash
node scripts/drift_check.mjs --prompt "A cute Minecraft boy holding a round metal sword with five fingers and walking then jumping and fighting a zombie" --engine kling --mode t2v --lang zh-en
```

Read `references/rescue-and-anti-drift.md` when troubleshooting specific defects:
- `human-fingers`: inject `fingerless and clawless flat 4x4 square pixel-block hand ends, no human fingers, no five fingers`.
- `blurry-texels`: inject `crisp 16x16 nearest-neighbor pixel-art block textures, sharp 90-degree texel grid edges, zero bilinear blur, no smooth plastic gradients`.
- `roblox-lego-drift`: inject `sharp 1:1:1 cubic 8x8x8 Minecraft head with 90-degree corners, studless flat voxel top, no Roblox cylindrical barrel head, no Lego top studs or C-shaped claw hooks`.
- `smooth-tools`: inject `extruded 16x16x1 pixel-art held tool with stepped 90-degree voxel edges, no smooth cylindrical metal rod or realistic blade`.
- `face-morph`: inject `flat 8x8 pixel-grid Minecraft face with 2x1 sliding pixel eyes and floating pixel brows, zero 3D protruding human nose`.
- `noodle-limbs`: inject `rigid 4x12x4 rectangular prism limbs with mechanical shoulder/hip pivots and clean 90-degree blocky bends, no rubbery noodle deformation`.
- `outfit-drift`: switch from T2V to First-Frame I2V anchored by the 3-view turnaround and voxel object sheet.
- `overload`: split any clip containing more than two sequential verbs into separate shots.

### Step 5: Render 3D Turnaround Sheets, Voxel Object Sheets, Contact Sheets, and Animated Previews

Run `scripts/render_preview.mjs` to render authentic 3D Minecraft character turnaround sheets, voxel block/item/mob showcase boards, 4-way anti-drift comparison boards, 9:16 storyboard contact sheets, and animated `.gif` / `.mp4` short video previews:

```bash
node scripts/render_preview.mjs
```

## Quality and Honesty Boundaries / 质量与边界说明

- **Prompts, storyboards, and local 3D voxel preview renderer.** This skill and its four CLI scripts (`voxel_spec.mjs`, `shot_compiler.mjs`, `drift_check.mjs`, `render_preview.mjs`) generate structured character/object cards, storyboards, anti-drift diagnostics, and local 3D Minecraft voxel preview renders. Generating diffusion videos requires an external model (Kling, Seedance/Jimeng, Hailuo, Wan, Sora, Runway).
- **Zero external runtime dependencies.** All scripts in `scripts/` use the Node.js standard library only and run offline without API keys.
- **Trademark clarity.** "Minecraft-style" describes a cubic voxel and `16×16` / `8×8` pixel-grid character and block aesthetic for creative prompt engineering. This project is an independent open-source skill and is not affiliated with or endorsed by Mojang Studios or Microsoft.

## Reference Navigation / 参考文档索引

- [`references/voxel-geometry-blocks-and-shaders.md`](references/voxel-geometry-blocks-and-shaders.md): Canonical `8×8×8` / `8×12×4` / `4×12×4` character pixel anatomy, `+0.5px` 3D skin layers, `16×16×16` blocks, `16×16×1` extruded tools, Creeper/Enderman mobs, and BSL/Bare-Bones shaders.
- [`references/model-prompt-playbook.md`](references/model-prompt-playbook.md): prompt structures, camera syntax, and motion settings for Kling, Seedance/Jimeng, Hailuo, Wan, Sora, and Runway.
- [`references/rescue-and-anti-drift.md`](references/rescue-and-anti-drift.md): diagnostic matrix and prompt patches for the 8 most common Minecraft AI video generation failures.
- [`references/short-video-beats-and-audio.md`](references/short-video-beats-and-audio.md): 0 to 3.5s hook patterns, voxel particle physics, camera transitions, Minecraft SFX cues, and caption placement for 9:16 vertical shorts.
- [`references/viral-archetypes-catalog.md`](references/viral-archetypes-catalog.md): 6 reusable short-video templates covering character skits and isometric block builds.
- [`references/classic-minecraft-catalog.md`](references/classic-minecraft-catalog.md): Pre-rendered library of 6 iconic characters/mobs (`Steve`, `Alex`, `Diamond Knight`, `Cozy Hoodie`, `Creeper`, `Enderman`) and 8 canonical voxel blocks/tools (`Grass Block`, `Diamond Ore`, `TNT`, `Crafting Table`, `Hinged Chest`, `Sticky Piston`, `Diamond Pickaxe`, `Diamond Sword`).
- [`templates/`](templates/): blank markdown templates for character/object cards, storyboards, and shot prompts.
- [`examples/`](examples/): 6 complete checked-in short-video packages (`diamond-creeper-ambush`, `cozy-lantern-build`, `pro-builder-vs-noob-tnt`, `redstone-chain-asmr`, `enderman-block-heist`, `axolotl-rainy-shelter`) with rendered PNG sheets, GIFs, and MP4 videos.
