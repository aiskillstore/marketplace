---
name: livestream-style-video
description: |
  Agent Skill to map any visual style or storyline into authentic 9:16 livestream camera perspectives, clean-plate I2V/T2V prompts, detachable HUDs, and local MP4 previews.
  Use when the user wants to generate AI livestream-perspective videos, streamer POV shorts, IRL selfie-stick/webcam/bodycam/unboxing/PK/PiP gameplay videos across any art style (photorealistic IRL, Roblox R6/blocky, anime/VTuber, 3D vinyl, voxel, or wuxia/sci-fi/horror plot adaptations), reconstruct Douyin (抖音), Kuaishou (快手), Instagram Live (Ins), X/Periscope, or TikTok Live room overlays/popups/danmaku/gift combos, or compile prompts for Kling (可灵), Seedance/Jimeng (即梦), Hailuo (海螺), Wan (通义万相), Sora, Veo, or Runway without burned-in gibberish UI text.
license: MIT
metadata:
  version: "1.1.0"
---

# Livestream Style Video Skill (`livestream-style-video`)

## Core Objective / 核心目标

An Agent Skill (`SKILL.md` + REA-backed platform HUD specifications + zero-dependency Node.js CLI & 3D/HUD video renderer + interactive Browser/OBS Studio) that translates **any visual style** and **any storyline or genre plot** into an authentic `9:16` **Livestream Camera Perspective (`直播视角感`)**—compiling clean-plate I2V/T2V prompts for external video models **and** directly rendering playable `.mp4` + `.gif` + bilingual storyboard sheets + detachable multi-platform live chrome (`抖音 / 快手 / Instagram / X / TikTok`) offline.

Respond in the user's language (`en`, `zh`, `zh-tw`, `ja`, `ko`, `es`, `fr`, `de`, `pt`, `ru`). For Chinese video engines (`Kling 可灵`, `Seedance/Jimeng 即梦`, `Hailuo 海螺`, `Wan 通义万相`), provide Chinese explanations alongside both Chinese and English generation prompts.

Generic prompts like `"a livestream video"` fail in AI video diffusion models in two predictable ways:
1. **Cinematic Third-Person Drift (`电影感第三人称跑偏`)**: the model shoots a floating Hollywood crane/dolly shot where characters ignore the lens.
2. **Burned-In Gibberish UI Melt (`乱码直播间UI烘死与画中画融化`)**: asking diffusion models to draw scrolling TikTok/Douyin comments, gift buttons, or corner PiP windows burns garbled alien glyphs and melting borders permanently into the video pixels.

This skill eliminates both failures by locking **eight Livestream Perspective invariants** before generating a single frame:

1. **Physical Camera Capture Rig Lock (`物理直播机位锚点锁`)**:
   - Every shot must anchor to one of eight concrete physical mounts (`desktop-webcam`, `handheld-selfie-irl`, `pip-facecam-rig`, `overhead-showcase-rig`, `chest-head-pov`, `pk-cohost-split`, `cctv-obs-fixed`, `drone-follow-live`)—defining lens focal length (`16mm` action-cam, `18mm` selfie gimbal, `24mm` monitor-top webcam, `35mm` desk-clamp macro), mount height, and physical vibration coupling (desk-slam micro-shake, walking bob, cameraman framing lag). Never use omniscient crane or floating cinema moves.
2. **Fourth-Wall Lens Address & `15°` Chat-Monitor Eye-Line (`第四面墙直视与15°读弹幕眼神轴`)**:
   - Authentic livestream presence comes from alternating between **`0°` direct lens eye-contact** (talking to viewers, leaning in, holding an item up) and **`15°` off-axis chat-monitor / `8°` downward phone-screen glances** (reading a live comment for 0.3s with screen light reflecting in the eyes/glasses, then snapping back to `0°` with an immediate reaction).
3. **Clean-Plate Diffusion + Post-HUD Layer Separation (`纯净无字底片与后置直播UI分层铁律`)**:
   - Always generate **100% UI-free raw camera plates** in Kling/Seedance/Sora/Wan (`clean raw camera feed, zero burned-in UI text, no scrolling comments, no watermarks`).
   - Composite crisp, localized, zero-gibberish platform chrome (`douyin`, `kuaishou`, `instagram`, `x`, `tiktok`), join banners, 2-slot gift combos (`×66`), live shopping cards (`小黄车`), Q&A cards, PK tug-of-war bars, and bezier rising hearts cleanly afterward via `scripts/render_preview.mjs` or `studio/index.html`.
4. **Livestream Optics, Ring-Light Catchlights & Autofocus Gestures (`直播光学与补光特征`)**:
   - Use circular LED ring-light eye catchlights, cyan/magenta RGB wall rim strips or monitor spill, deep readable room focus (`f/4–f/5.6` rather than background-obliterating `f/1.2` cinema bokeh), and signature live gestures such as holding a flat palm behind a close-up product (`influencer AF-C macro gesture`).
5. **Style-Orthogonal Adapter Matrix (`跨画风正交解耦矩阵` — Any Style × Any Rig)**:
   - Camera rig physics and visual style are orthogonal. Combine any rig with:
     - `realistic-irl` (general photorealistic AI video: natural skin texture, five-finger phone/mic grip, wireless lavalier or condenser boom mic).
     - `roblox-blocky` (canonical Roblox SmoothPlastic geometry: `2×2×1` torso, flush `1×2×1` legs with zero thigh gap, fingerless and clawless solid `1×2×1` block hands, smooth studless `1:1` barrel head, flat 2D screen-printed face decal, smooth floors with zero Lego studs).
     - `anime-vtuber` (cel-shaded 2D/Live2D avatar tracking sway & expression toggles).
     - `stylized-3d` (blind-box matte vinyl / Pixar-grade miniature studio).
     - `voxel-sandbox` (`8×8×8` cubic head, `16×16` crisp nearest-neighbor pixel grid, flat `4×4` block hands).
     - `cinematic-genre-adapt` (translates wuxia, fantasy, medieval, horror, or sci-fi plots into diegetic in-universe selfie/visor/talisman livestreams).
6. **Universal Plot-to-Livestream 4-Beat Retention Arc (`全剧情直播化四幕转译`)**:
   - Map any story into `15s` (4 cuts) or `30s` (8 unique cuts):
     - `Shot 01 (0–3.5s) · Hook`: Cold-open live claim to `0°` lens ("Chat dared me to try this...").
     - `Shot 02 (3.5–7.5s) · Live Proof`: Close-up autofocus inspection, doorway approach, or synchronized setup.
     - `Shot 03 (7.5–11.5s) · Unscripted Live Twist`: Background chaos, spring pop, shadow photobomb, or Killbrick fail right on live feed.
     - `Shot 04 (11.5–15s) · Chat-Flood Payoff`: Speechless `15° → 0°` glance, desk-slam meltdown, or seamless loop reset.
7. **Dual-Track PiP & PK Safety + Single-Action Clip Budget (`双轨画中画/PK安全与单镜单动作预算`)**:
   - Restrict every 3.5–5s clip to **one primary physical action** and **one continuous camera rig**.
   - For `pip-facecam-rig` and `pk-cohost-split`, generate **Track A (Main World/Game)** and **Track B (Streamer Facecam / Co-Host Room)** as separate clean clips (or First-Frame I2V locked splits) before compositing—never ask single-pass raw T2V to invent two moving cameras at once.
8. **3-State Setup Anchor Sheet (`直播间三态一致性首帧参考卡`)**:
   - Lock outfit, room background, lighting, and microphone side (`boom-left` vs `lavalier`) with a 3-panel reference card (`0° Primary Lens` / `15° Chat-Read Glance` / `Side Rig Layout`) via `scripts/rig_spec.mjs` so props never flip sides across cuts.

## Six Production Modes / 六种工作模式

1. **Rig-Spec · 直播机位与画风设定**: Lock camera optics, fourth-wall eye-line, mic placement, and orthogonal style DNA (`scripts/rig_spec.mjs`).
2. **Plot-to-Live · 任意剧情转直播分镜**: Convert any freeform story, genre plot, or built-in archetype into a 4-shot (`15s`) or 8-shot (`30s`) livestream storyboard (`scripts/shot_compiler.mjs --plot "..."`).
3. **Prompt-Compile · 多模型纯净底片提示词编译**: Generate First-Frame anchors, Clean-Plate motion prompts, Track-B PiP facecam prompts, and negative prompts for `local3d`, Kling, Seedance, Hailuo, Wan, Sora, Veo, or Runway (`scripts/shot_compiler.mjs`).
4. **Platform-HUD · 五大主流直播间界面与特效复刻**: Apply REA-reconstructed chrome, safe zones, join banners, 2-slot gift combos, live shopping popups, Ins Q&A cards, PK tug-of-war bars, and Periscope/Douyin heart fountains (`scripts/hud_presets.mjs` & `studio/index.html`).
5. **Rescue · 直播感丧失与乱码UI救场**: Run 8-gate static linting on prompts or episode JSON packages and emit immediate rescue rewrites (`scripts/drift_check.mjs`).
6. **Render & Package · 本地9:16成片与HUD合成**: Offline-render 3D livestream animatics (`.mp4` with synthesized live audio + `.gif` + bilingual contact sheets) across both General AI Video and Roblox styles (`scripts/render_preview.mjs`).

## End-to-End Workflow / 标准工作流

### Step 1: Lock Camera Rig, Style Pack & 3-State Setup Card (`rig_spec.mjs`)

Read `references/camera-rigs-and-optics.md` and `references/style-adapters-matrix.md`, then generate the Rig & Style DNA card (always pass `--out` for UTF-8 safety):

```bash
node scripts/rig_spec.mjs --rig handheld-selfie-irl --style realistic-irl --lighting night-neon-irl --host "Lin" --lang zh-en --out ./my-live/rig_card.md
```

For Roblox livestreamers, switch `--style roblox-blocky`:

```bash
node scripts/rig_spec.mjs --rig pip-facecam-rig --style roblox-blocky --roblox-rig chibi-blocky --host "BloxyKai" --lang zh-en --out ./my-live/rig_card.md
```

### Step 2: Translate Any Plot into Clean-Plate Storyboard + HUD Timeline (`shot_compiler.mjs`)

Pass `--plot "<any plot>"` (or `--template <id>` / `--spec <episode.json>`) with target `--engine` and `--platform` (`douyin` | `kuaishou` | `instagram` | `x` | `tiktok` | `clean`):

```bash
node scripts/shot_compiler.mjs --plot "古代剑客在云海早高峰举着玉简自拍直播御剑通勤，被超车仙鹤气流颠歪发髻" --style cinematic-genre-adapt --rig handheld-selfie-irl --platform douyin --engine kling --lang zh-en --out ./my-live/storyboard.md
node scripts/shot_compiler.mjs --plot "古代剑客在云海早高峰举着玉简自拍直播御剑通勤，被超车仙鹤气流颠歪发髻" --style cinematic-genre-adapt --rig handheld-selfie-irl --platform douyin --engine kling --json --out ./my-live/prompts.json
```

### Step 3: Verify All 8 Anti-Drift Gates (`drift_check.mjs`)

Audit single prompts or full compiled packages before spending external video generation credits:

```bash
node scripts/drift_check.mjs --pack ./my-live/prompts.json --engine kling --lang zh-en --out ./my-live/drift_report.md
```

### Step 4: Render Local 9:16 Video + Detachable Platform HUD (`render_preview.mjs`) or Open Interactive Studio

Render playable `540x960` H.264 `.mp4` (with synthesized live room audio), `.gif`, 3-state setup card, and bilingual 4-shot contact sheets directly:

```bash
node scripts/render_preview.mjs --spec ./my-live/prompts.json --out-dir ./my-live/assets --platform douyin --force
```

To interactively layer **Douyin / Kuaishou / Instagram Live / X Live / TikTok Live** borders, gift combos, shopping popups, PK bars, Q&A cards, or `#00FF00` green-screen overlays over any external `.mp4` video, open [`studio/index.html`](studio/index.html) in any browser or OBS Browser Source.

## Quality and Honesty Boundaries / 质量与边界说明

- **Clean-Plate AI diffusion + deterministic HUD compositing.** Raw diffusion prompts produced by this skill intentionally exclude burned-in UI text so external models (Kling, Seedance, Hailuo, Wan, Sora, Veo, Runway) generate clean camera optics, while `render_preview.mjs` and `studio/index.html` render crisp, deterministic, trademark-free platform HUDs.
- **Zero external npm dependencies.** All CLI scripts in `scripts/` use Node.js 18+ built-in modules (`fs`, `path`, `zlib`, `child_process`), pairing with Python Pillow + `ffmpeg` when available for anti-aliased CJK HUD compositing and H.264 MP4 encoding (with pure-Node PNG fallback).
- **REA Evidence & trademark cleanliness.** Platform HUD presets (`douyin`, `kuaishou`, `instagram`, `x`, `tiktok`) are clean-room geometric reconstructions informed by wire-protocol/CSS analysis and published safe-zone specs (`references/platform-ui-rea-ledger.md`). Never inject official TikTok, Douyin, Kuaishou, Instagram, X, Twitch, or Roblox logos/watermarks. Independent open-source project; unaffiliated with ByteDance, Kuaishou, Meta, X Corp., or Roblox Corporation.

## Reference Navigation / 参考文档索引

- [`references/camera-rigs-and-optics.md`](references/camera-rigs-and-optics.md): Focal lengths, mount geometry, horizon/shake physics, and `0°/15°` eye-line rules for all 8 livestream rigs.
- [`references/style-adapters-matrix.md`](references/style-adapters-matrix.md): Orthogonal visual style locks (`realistic-irl`, `roblox-blocky`, `anime-vtuber`, `stylized-3d`, `voxel-sandbox`, `cinematic-genre-adapt`).
- [`references/plot-to-livestream-beats.md`](references/plot-to-livestream-beats.md): Universal storyline-to-livestream 4-beat/8-beat translation rules and live room SFX cues.
- [`references/platform-ui-rea-ledger.md`](references/platform-ui-rea-ledger.md): REA static/runtime reverse-engineering ledger, safe-zone pixel coordinates, popup state machines, and Periscope/Douyin FX specs across Douyin, Kuaishou, Instagram Live, X Live, and TikTok Live.
- [`references/model-prompt-playbook.md`](references/model-prompt-playbook.md): Clean-plate & dual-track prompt formulas for Kling, Seedance/Jimeng, Hailuo, Wan, Sora, Veo, and Runway.
- [`references/rescue-and-anti-drift.md`](references/rescue-and-anti-drift.md): 8-gate failure matrix and before/after prompt rescue patches.
- [`references/viral-livestream-archetypes.md`](references/viral-livestream-archetypes.md): 8 reusable livestream short-video templates (5 General/Cross-Genre AI Video + 3 Roblox Livestream POV).
- [`studio/index.html`](studio/index.html): Standalone interactive HTML5/OBS Multi-Platform Livestream Chrome, Popup & Heart FX Studio.
- [`templates/`](templates/) & [`examples/`](examples/): Reusable templates and 8 complete rendered `.mp4` + `.gif` + prompt packages.
