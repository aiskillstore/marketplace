---
name: game-universe-studio
description: "End-to-end game world & cinematic studio: synthesizes consistent game character design, 3D cinematic camera motions, high-CTR Bento game cards, and instant-play WebGL/Canvas game showcase architecture inspired by gaoyaguo.eu.cc."
version: "1.0.0"
author: "GAOYAGUO Studio"
tags: ["game-development", "character-design", "cinematic-camera", "webgl", "game-showcase", "agent-skills"]
---

# Game Universe Studio (Gaoyaguo Edition)

> **"Wake the Games"** — Transform loose creative sparks into a unified, interactive, playable web game showcase with locked characters, cinematic cutscenes, and viral visual presentation.

---

## 🌟 Overview & System Architecture

Game Universe Studio bridges the gap between disparate generative AI tools and interactive web engineering. Inspired by the live open-source showcase at `gaoyaguo.eu.cc`, this skill unifies 4 specialized disciplines into an industrial production pipeline:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      GAME UNIVERSE PRODUCTION PIPELINE                  │
├───────────────────┬───────────────────┬─────────────────┬───────────────┤
│ Tier 1: Character │ Tier 2: Cinematic │ Tier 3: Visual  │ Tier 4: Web   │
│ Consistency (IP)  │ Camera Compiler   │ Packaging (CTR) │ Showcase Host │
├───────────────────┼───────────────────┼─────────────────┼───────────────┤
│ • 4-view sheets   │ • Camera contract │ • Bento cards   │ • WebGL/Canvas│
│ • Facial locks    │ • 3D orbit sweeps │ • Key art hooks │ • Audio cues  │
│ • Sprite sheets   │ • Boss reveal cuts│ • Badges & glows│ • Story mode  │
│ • Weapon & gear   │ • Flyover tracks  │ • Retro-futurism│ • Bento Grid  │
└───────────────────┴───────────────────┴─────────────────┴───────────────┘
```

---

## 🛠️ The 4-Tier Integrated Workflow

### Tier 1: Character Consistency & Sprite Pipeline
Ensure protagonists, rivals, and bosses maintain strict visual fidelity across all game states:
1. **Character Lock Profile**: Lock ethnicity, face structure, signature hairstyle, wardrobe accents, and color palette.
2. **Multi-Angle Turnaround**: Generate 4-directional ortho sheets (Front, 3/4 Perspective, Profile 90°, Back) with uniform lighting.
3. **Action Sprite Extraction**: Synthesize idle, run, attack, jump, and hurt frames using consistent seed locking and control vectors.
4. *Reference*: See `references/character-consistency-pipeline.md`.

### Tier 2: Cinematic Shot & Cutscene Motion Compiler
Compile cinematic camera prompts for game trailers, 3D scene reveals, and web transition cutscenes:
1. **Camera Motion Contract**:
   - **Anchor (起点)**: Initial framing (e.g., ground-level Dutch angle, extreme wide aerial).
   - **Mechanism (机制)**: Physical camera apparatus (Technocrane, FPV drone, orbital gimbal, dolly track).
   - **Path & Velocity (路径与加减速)**: Speed profile (accelerating whip pan, smooth logarithmic deceleration).
   - **Subject Lock (主体锁定)**: Dynamic tracking point (character eyes, vehicle front bumper, boss weapon).
   - **Environment Response (环境响应)**: Volumetric dust, lens flares, motion blur, particle interaction.
   - **Ending Anchor (落点)**: Final framing transitioning directly into gameplay or UI state.
2. *Reference*: See `references/cinematic-cutscene-compiler.md`.

### Tier 3: High-CTR Bento Cards & Game Cover Visuals
Design promotional game thumbnails and Bento showcase cards that maximize player engagement:
1. **Visual Composition**: Strong diagonal focal points, hero character silhouettes, high contrast lighting.
2. **Retro-Futuristic Typography**: Crisp badges (e.g., `3D ENGINE`, `MULTIPLAYER`, `ARCADE`), neon edge glow (`border-cyan-400/30`), tag chips.
3. **Responsive Hover Dynamics**: Scale transforms (`group-hover:scale-105`), ambient color shifts, sound trigger cues.
4. *Reference*: See `references/high-ctr-game-visuals.md`.

### Tier 4: Instant-Play Web Showcase Architecture
Deploy a lightweight, high-performance web game hub (modeled after `gaoyaguo.eu.cc`):
1. **Bento Grid Layout**: Asymmetric responsive cards accommodating 3D WebGL canvases, 2D HTML5 arcade embeds, and external launchers.
2. **Audio-Visual Atmosphere**: Cyberpunk/synthwave audio toggles, retro click sound effects, ambient particle waves.
3. **Narrative Story Route (`/story`)**: Cinematic full-screen narrative transitions connecting lore to gameplay.
4. *Reference*: See `references/game-showcase-architecture.md` and `references/playable-demo-contracts.md`.

---

## ⚡ Execution Modes

When prompted with a game creation or showcase task, select the corresponding mode:

| Trigger / Command | Mode | Primary Output |
| :--- | :--- | :--- |
| `game:character` | **Character Genesis** | 4-angle turnaround sheet, locked prompt contract, sprite specs |
| `game:cinematic` | **Cutscene Compiler** | 6-point camera motion prompt for video generation (Kling/Runway/Sora) |
| `game:card` | **Bento Showcase Card** | High-CTR card composition prompt + Tailwind/CSS card code snippet |
| `game:showcase` | **Web Architecture** | Complete interactive Bento Grid game hall template with audio & WebGL hooks |
| `game:full` | **Full Universe Suite** | Complete asset package covering Character + Cutscene + Bento Card + Web Code |

---

## 🎯 Verification & Acceptance Checklist

Before finalizing any game asset or showcase module, verify:
- [ ] **Character Lock**: No facial morphing or apparel color drifts between views.
- [ ] **Camera Precision**: Prompt contains all 6 contract dimensions (Anchor, Mechanism, Path, Lock, Response, Landing).
- [ ] **Visual Clarity**: Bento card text remains legible at 320px mobile thumbnail scale.
- [ ] **Interaction Smoothness**: Web showcase includes hover feedback, sound triggers, and instant-play sandbox safety.
