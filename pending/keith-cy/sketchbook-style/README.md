<h1 align="center">Sketchbook Style</h1>

<p align="center"><b>Turn any object into a page from an industrial designer's sketchbook.</b><br>Black ink on white paper, simplified hardware in three-quarter view, hatching, a few solid blacks, lots of empty paper. Four variants, open image models, no API keys. An Agent Skill for Claude Code and other coding agents.</p>

<p align="center">
  <a href="https://code.claude.com/docs/en/skills"><img src="https://img.shields.io/badge/Claude_Code-skill-D97757?style=flat-square&logo=claude&logoColor=white&labelColor=1f2328" alt="Claude Code skill"></a>
  <a href="https://agentskills.io"><img src="https://img.shields.io/badge/Agent_Skills-compatible-2ea44f?style=flat-square&labelColor=1f2328" alt="Agent Skills compatible"></a>
  <a href="#requirements"><img src="https://img.shields.io/badge/models-Qwen--Image_2.1_·_FLUX.2_·_Z--Image-0969da?style=flat-square&labelColor=1f2328" alt="Open image models"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache_2.0-D22128?style=flat-square&labelColor=1f2328" alt="Apache 2.0 license"></a>
</p>

<p align="center"><b>English</b> · <a href="README.zh-CN.md">简体中文</a></p>

<p align="center"><img src=".github/assets/hero.jpg" width="880" alt="Eight sketchbook drawings made with this skill: a jet engine in tidy pen, a space helmet in marker, a pocket jet gadget in heavy ink, a helmet with bold outlines and fine details, an annotated console page, a pocket synth, a field recorder and a page of small electronics thumbnails."></p>
<p align="center"><img src=".github/assets/sheet.jpg" width="880" alt="All 52 sample pages on one sheet: 13 in each variant, pen, marker, ink and contrast."></p>

<p align="center"><sub>Every drawing on this page was made with this skill: Qwen-Image 2.1 on ComfyUI, then the bundled ink post-process. Prompts and seeds are in <a href="references/"><code>references/</code></a>.</sub></p>

---

```text
Draw a pocket synthesizer as a designer's sketchbook page, marker variant, with notes on the knobs.
```

The agent picks a variant and a page type, writes the prompt from the skill's templates, renders it on your ComfyUI server (or locally with FLUX.2 klein), turns the result into clean single-colour ink and measures it against the style's targets: line width, ink coverage and how much of the ink is solid black.

## Quick start

```sh
npx skills add Keith-CY/sketchbook-style -g -a claude-code
export COMFY_URL=http://127.0.0.1:8188   # your ComfyUI with Qwen-Image 2.1
```

Then ask your agent:

```text
Make a sketchbook page of a field recorder, ink variant.
```

## The four variants

| Variant | Looks like | Pick it when |
|---|---|---|
| **pen** · 细笔 | tidy 0.5–0.8 mm pen, real objects drawn faithfully, clean hatching | the picture has to *explain* a real machine |
| **marker** · 马克笔 | one heavy felt-tip line, a few solid blacks with white highlight stripes, invented gadgets, messy notes | mood, section openers, brand moments, idea pages |
| **ink** · 浓墨 | worn brush marker, about half of each object black with white details reversed out, dry-brush edges | posters, covers, high-contrast thumbnails, small sizes |
| **contrast** · 粗细对比 | line weight follows density: bold outlines and flat black or white areas on big forms, fine lines on details | one hero object that must read from afar and reward a close look |

**pen**

<img src=".github/assets/pen.jpg" width="880" alt="Pen variant: steam engine, tokamak, telescope notes, space hardware thumbnails, a person tuning a radio">

**marker**

<img src=".github/assets/marker.jpg" width="880" alt="Marker variant: handheld telescope, field recorder, annotated folding telescope, gadget thumbnails, a desk">

**ink**

<img src=".github/assets/ink.jpg" width="880" alt="Ink variant: space helmet, tokamak desk toy, annotated console, gadget thumbnails, a person at a radio">

**contrast**

<img src=".github/assets/contrast.jpg" width="880" alt="Contrast variant: pocket jet gadget, field recorder, annotated folding telescope, space thumbnails, a desk">

Each strip shows the five page types, left to right: **A** bold object study, **B** construction study, **C** annotated page, **D** thumbnail scatter, **E** small scene. All 52 samples are in [`examples/`](examples).

## What you get

| | |
|---|---|
| **Prompt templates** | A shared style core plus a block per variant and page type, written from what works on Qwen-Image 2.1 (and what didn't: every "no …" lives in the positive prompt, CFG stays at 1). |
| **Invented or faithful subjects** | By default an object is redesigned as a retro-futurist gadget built from a small symbol vocabulary: knob circles, dot grilles, tick scales, digit displays. Ask for "faithful" and it stays recognisable. |
| **Ink post-process** | `inkpost.py` turns any render into pure single-colour ink, then applies the variant's look: marker thickening, dry-brush edges, or line weight that follows how busy each area is. |
| **Measurement** | `measure.py` reports line width, ink coverage, solid-black share and the calm/busy line-width ratio, so a result can be checked against numbers instead of by eye. |
| **A checklist** | What every page must and must not have: no grey, no paper texture, no floor or cast shadow, notes that are words and arrows only. |

## Install

This repository is the skill folder: `SKILL.md` at the root, with `scripts/`, `references/` and `examples/` beside it.

| | Command | Installs to |
|---|---|---|
| **skills CLI**, for you | `npx skills add Keith-CY/sketchbook-style -g -a claude-code` | `~/.claude/skills/sketchbook-style` |
| **skills CLI**, one project | `npx skills add Keith-CY/sketchbook-style` | `.claude/skills/sketchbook-style` |
| **git**, for you | `git clone https://github.com/Keith-CY/sketchbook-style.git ~/.claude/skills/sketchbook-style` | `~/.claude/skills/sketchbook-style` |

<details>
<summary><b>Other agent hosts</b></summary>

<br>

- **Codex, Cursor, Gemini CLI and other agents that read Agent Skills**: point them at `SKILL.md`; everything else is plain files.
- **Claude.ai and the Claude desktop app**: zip the folder and upload it under Settings › Capabilities › Skills. Rendering still needs a ComfyUI server you can reach.

</details>

## Usage

Just describe the object and, if you care, the variant and page type:

```text
A sketchbook page of a tokamak, pen variant, construction study with a second small view.
Twenty little ideas for space hardware on one page, marker variant.
A poster-style ink drawing of an astronaut helmet.
The same espresso machine in all four variants, so I can choose.
```

Three habits give the best pages:

1. **Say what it is for.** "For a poster" picks *ink*, "to explain how it works" picks *pen*, "for a section opener" picks *marker*.
2. **Name the parts that matter.** Three to five parts beat a long description; the style turns them into symbols.
3. **Keep notes short.** On annotated pages, give the exact words, one to three each, at most five notes.

## How it works

- **[`SKILL.md`](SKILL.md)** is what the agent reads: how to choose a variant, the prompt templates, the post-process settings, the targets and the checklist.
- **[`references/`](references)** holds the exact prompts and seeds behind every sample (`prompts-*.md`) and engine notes with measured times (`engines.md`).
- **[`scripts/`](scripts)**: `comfygen.py` (ComfyUI client with the Qwen-Image 2.1 workflow), `localgen.sh` (FLUX.2 klein / Z-Image fallback through mflux), `inkpost.py` (ink post-process), `measure.py` (measurements).

<details>
<summary><b>Repository layout</b></summary>

<br>

```text
sketchbook-style/
├── SKILL.md              what the agent reads
├── scripts/              comfygen, localgen, inkpost, measure
├── references/           prompts and seeds per variant, engine notes
├── examples/             13 samples per variant (pen, marker, ink, contrast)
└── .github/assets/       images for this README
```

</details>

## Requirements

| | Needed for | Notes |
|---|---|---|
| **Claude Code** (or any Agent Skills host) | choosing and writing prompts | |
| **ComfyUI** with [ComfyUI-GGUF](https://github.com/city96/ComfyUI-GGUF) and Qwen-Image 2.1 (`qwen-image-2.1-Q6_K.gguf`, its text encoder and VAE) | the best results | about 2 minutes per 1024×1024 image on an Apple M3 Ultra; set `COMFY_URL` |
| **mflux** with FLUX.2 klein 4B or Z-Image Turbo | local fallback on Apple Silicon | set `MODELS` to the model folder |
| **Python 3** with Pillow and NumPy | `inkpost.py`, `measure.py` | |

Optional: set `GPU_LOCK` to a path to let several jobs share one GPU, one image at a time.

## Limits

- **It draws objects.** Machines, gadgets, instruments, simple scenes. People come out simplified and are best kept small.
- **Black and white only.** The post-process removes every grey and colour by design.
- **Handwriting is English.** Notes in other scripts are not reliable on the current models.
- **Thumbnail scatter pages are the hardest.** They come out tidier than a real sketchbook page; the prompts push against it, and some takes still need a re-roll.

## Manual use, without an agent

```sh
python3 scripts/comfygen.py jobs.json out/          # jobs: [{"name": "...", "prompt": "...", "seed": 1}]
python3 scripts/inkpost.py out/helmet.png out/helmet-ink.png --marker
python3 scripts/measure.py out/helmet-ink.png
```

Prompts to start from are in [`references/prompts-marker.md`](references/prompts-marker.md) and its siblings.

## Credits

Image models: [Qwen-Image](https://github.com/QwenLM/Qwen-Image) (Apache 2.0), [FLUX.2 klein](https://huggingface.co/black-forest-labs) and [Z-Image](https://github.com/Tongyi-MAI/Z-Image), run through [ComfyUI](https://github.com/comfyanonymous/ComfyUI) and [mflux](https://github.com/filipstrand/mflux). Check each model's own licence before commercial use of its outputs.

## License

[Apache License 2.0](LICENSE) © 2026 Keith-CY
