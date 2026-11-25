# Camera Prompt QuickCheck (Free Agensi Skill)

> Instant deterministic pre-flight linter for AI video prompts (Runway Gen-4, Kling 2.6, Sora 2, Veo 3, Seedance). Zero API dependencies, pure Python stdlib.

[![Upstream](https://img.shields.io/badge/claude--skills_v2.14.15-Contributor-6366f1?style=flat-square)](https://github.com/alirezarezvani/claude-skills/releases/tag/v2.14.15)
[![Agensi](https://img.shields.io/badge/Agensi-Free_Skill_Live-10b981?style=flat-square)](https://www.agensi.io/r/CREATOR980D20B?to=/skills/camera-prompt-quickcheck&utm_source=github_quickcheck)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

Stop burning $0.50–$2.00 per failed generation clip because `"zoom in dramatically cinematic"` causes background rubber-banding or horizon drift.

> **Install free on Agensi (one-click, verified):** **[Camera Prompt QuickCheck on Agensi →](https://www.agensi.io/r/CREATOR980D20B?to=/skills/camera-prompt-quickcheck&utm_source=github_quickcheck)**
>
> **Try it live in your browser (zero install):** **[Interactive Camera Prompt QuickCheck Playground →](https://287523023qq-hue.github.io/ai-cinematic-skills/#quickcheck)**

## What It Catches (`C01`–`C06`)

1. **`C01` Missing Primary Mechanism**: Catches prompts with no physical camera action (`dolly`, `truck`, `pan`, `tilt`, `orbit`, `pedestal`, `rack focus`, `locked tripod`).
2. **`C02` Dolly vs Optical Zoom Confusion**: Flags ambiguous `"zoom in/out"` before it produces flat 2D digital scaling instead of real 3D parallax.
3. **`C03` Multi-Axis / Dolly+Zoom Conflict**: Catches 3+ competing camera axes or unlabeled dolly+zoom warping.
4. **`C04` Buzzword Fluff Density**: Flags `"cinematic"`, `"epic"`, `"dynamic"` when lacking concrete speed/curve qualifiers.
5. **`C05` Missing Subject / Horizon Lock**: Catches unanchored shots likely to drift off-subject.
6. **`C06` Missing End-Settle State**: Flags clips with no terminal rest frame or reveal.

## Quick Install (Claude Code / Cursor / Codex / Antigravity)

```bash
npx skills add 287523023qq-hue/camera-prompt-quickcheck
```

## Quick Run

```bash
python3 scripts/lint_camera_prompt.py "Cinematic epic zoom in on detective face."
python3 scripts/lint_camera_prompt.py --json "Slow steady dolly in..."
python3 -m unittest discover -s tests -v
```

---

## Go Beyond Linting — Full Production Studio Pipeline

Need a complete **7-slot Hollywood motion contract compiler** + **4-view character turnaround lock** + **Bento/video visual pack generator** + **WebGL/Canvas game scaffold**?

- **4-in-1 Official Bundle — `$9.99` (Save 41% / $6.98 off):** [AI Game & Visual Asset Studio Suite](https://www.agensi.io/r/CREATOR980D20B?to=/bundles/ai-game-visual-asset-studio-suite&utm_source=github_quickcheck)
- **Limited-Time Deal — `$5.00` (-28%, ends in 7 days):** [Character Creation Studio](https://www.agensi.io/r/CREATOR980D20B?to=/skills/character-creation-studio&utm_source=github_quickcheck)
- **Standalone Camera Contract Skill (`$3.99`):** [Cinematic Shot Prompting](https://www.agensi.io/r/CREATOR980D20B?to=/skills/cinematic-shot-prompting&utm_source=github_quickcheck)
- **Live Interactive Playground & Showcase:** [AI Cinematic Skills (`#quickcheck`)](https://287523023qq-hue.github.io/ai-cinematic-skills/#quickcheck)
