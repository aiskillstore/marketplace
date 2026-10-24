---
name: sketchbook-style
description: "Reproduces the “designer's daily sketchbook” drawing style (black ink on white paper, simplified hardware in 3/4 view, hatching, solid black accents, lots of empty paper, optional scrawled notes) with open image models — Qwen-Image 2.1 on ComfyUI first, FLUX.2 klein / Z-Image locally as fallbacks. Four variants: `pen` (速写本 · 细笔 — tidy pen, real objects, clean hatching), `marker` (速写本 · 马克笔 — heavy marker, invented retro-futurist gadgets, messy pages), `ink` (速写本 · 浓墨 — solid black masses with white details reversed out, dry-brush lines, for posters and covers) and `contrast` (速写本 · 粗细对比 — bold lines and flat black or white masses where the drawing is calm, fine lines where it is busy). Use when a picture, plate, storyboard frame or brand asset should look like an industrial designer's idea sketch rather than a finished illustration; gives prompt templates per variant and sub-style, engine settings, the single-colour ink post-process, measurement against a reference set, and a verification checklist."
---

# Sketchbook style

## Pick a variant first

| Variant | Style pack | Looks like | Pick it when |
| --- | --- | --- | --- |
| **`pen`** — 速写本 · 细笔 | `sketchbook-pen` | tidy 0.5–0.8 mm pen, real objects drawn faithfully, clean diagonal hatching, thin lines | the picture has to *explain* a real machine (a plate, a "how it works" frame, a diagram with warmth) |
| **`marker`** — 速写本 · 马克笔 | `sketchbook-marker` | heavy felt-tip marker of one weight, big solid blacks with white highlight stripes, invented gadgets, messy notes and scatter pages | the picture should *feel* like a real designer's sketchbook: section openers, brand moments, idea pages; or when a viewer should recognise the sketchbook at a glance |
| **`contrast`** — 速写本 · 粗细对比 | `sketchbook-contrast` | line weight follows how busy each area is: thick confident outlines and large flat black or white areas on the big simple forms, fine 0.3 mm lines on knobs, grilles, scales, text and hatching | one hero object that must read from afar *and* reward a close look: plates, explainer stills, product-style pictures, editorial illustration |
| **`ink`** — 速写本 · 浓墨 | `sketchbook-ink` | worn brush marker: about half of each object solid black with white details reversed out (knobs, dot grilles, digits, highlight stripes), ragged dry-brush edges, ink skips | posters, covers, high-contrast thumbnails and small sizes where thin lines would vanish; deliberately heavier and rougher than a real sketchbook |

Default when the brief doesn't say: `marker` for mood and brand, `pen` for explanation, `ink` for posters, covers and thumbnails, `contrast` for a single clear object that should look designed rather than scribbled. The marker variant is closest to a real designer's sketchbook; pen is cleaner and more legible; ink is bolder than a real sketchbook on purpose.


Never name an artist in a prompt. Describe the style.

## Shared: what the style is

A page from a product designer's daily sketchbook. Black ink on plain white paper, scanned clean to pure single-colour ink. Simplified hardware (radios, synths, helmets, consoles, instruments) drawn freehand in 3/4 view in a few minutes, with hatching, cross-hatching in grilles and screens, a few solid black fills, and a lot of empty paper. Some pages carry scrawled notes and arrows. It reads as *thinking on paper*, never as a finished illustration.

Defining traits (check every picture):

1. Pure black ink on white, no grey tones, no paper texture, no colour.
2. Fast lines, wobbly, overshooting at corners; no ruler lines.
3. Simplified, slightly naive block forms; details reduced to symbols (knob circles, dot-grid grilles, tick scales, seven-segment digits).
4. 3/4 view from slightly above.
5. Shade only with hatching and solid-black areas (white highlight stripes left in).
6. Most surfaces stay white; the drawing sits in empty paper; no background, floor or cast shadow.
7. Unfinished: construction lines, half-drawn edges, small variant thumbnails.
8. Optional: 2–5 scrawled notes (1–3 lowercase words each) with arrows, same pen. Never hearts, smileys, stars or other decorative doodles.

Sub-styles (all variants):

| Code | Name | Use it for |
| --- | --- | --- |
| A | Bold object study | one hero object, punchy thumbnail, cover |
| B | Construction study | explaining a machine, a second small view |
| C | Annotated function / UI page | labelled parts, interface ideas |
| D | Thumbnail scatter page | "many ideas / variations", section openers |
| E | Small scene | a desk, a person using the object (rare in real sketchbooks; keep it simple) |

Measured on a reference set of 87 hand-drawn sketchbook pages (`scripts/measure.py`, drawing's bounding box scaled to 1024 px; stroke = typical line width, solid = share of ink in areas thicker than 24 px):

| Set | Stroke px (% of 1024) | Ink coverage | Solid share |
| --- | --- | --- | --- |
| All 87 reference pages | 5 (0.49 %), p10–p90 0.29–0.88 % | 0.155 (0.10–0.29) | 0.05 (p90 0.35) |
| A — bold marker pages (12) | 7 (0.68 %), up to 17 (1.66 %) | 0.33 | 0.33 |
| B — construction (7) | 5 (0.49 %) | 0.16 | 0.03 |
| C — notes pages (9) | 3 (0.29 %) | 0.13 | 0.01 |
| D — scatter pages (6, page-wide) | 1 (0.10 %) | 0.10 | 0.00 |
| E — scenes (7) | 5 (0.49 %) | 0.165 | 0.05 |

## Variant `pen` — 速写本 · 细笔

Prompt = **subject sentence + sub-style block + CORE**. Subjects are the real object, plainly described and simplified. The exact prompts and seeds of all 13 pen samples are in `references/prompts-pen.md`; rerunning them with the settings below reproduces round 1 (the post-process default is byte-identical).

CORE (always last):

```
Page from a product designer's daily sketchbook, drawn fast in black ink on plain white paper. Simplified, slightly naive shapes with slightly distorted perspective. Scrappy, nervous lines: a little wobbly, overshooting at the corners, some edges traced twice. Busy little details: rows of dots, tiny rectangles, tick marks, small circles for knobs. A few loose diagonal hatch lines on one side only; cross-hatching only inside grilles, screens and dark openings; a couple of small solid black accents. Most surfaces left white. No feathery repeated strokes, no tonal shading, no grey, no colour. Large empty white paper around the drawing. A five-minute idea sketch, not a finished illustration.
```

(An earlier, calmer CORE — "boxy forms with rounded corners … few lines" — came out clip-art-like and turned rockets into boxes. Don't put shape words like "boxy" in CORE.)

Sub-style blocks:

- **A** `Drawn with a thick black felt-tip marker: heavy uneven outlines, chunky bold forms, drawn too big for the page so one side runs off the edge, a few areas filled solid black with thin white highlight stripes left unfilled.`
- **B** `Drawn with a 0.8 mm black felt-tip pen: firm dark lines, no thin faint lines, three-quarter view from slightly above, two or three perspective construction lines extending past the object.`
- **C** `Drawn with a 0.8 mm black felt-tip pen, firm dark lines, with short handwritten notes in messy lowercase English and arrows pointing at parts.` Put the exact note words in the subject sentence in single quotes; 1–3 words each, at most 5.
- **D** `Drawn with a 0.8 mm black felt-tip pen: twenty to thirty tiny thumbnail sketches of different shapes and types, no two alike, mixed sizes from very small to medium, tilted at different angles, scattered unevenly across the page like a brainstorm, not in a grid, some with a hatched side or a solid black part, two tiny handwritten words.` List 5–7 *different* object types in the subject.
- **E** `Drawn with a 0.8 mm black felt-tip pen: firm dark lines, simplified, objects drawn as simple boxes and cylinders, no background.`

Post-process: `scripts/inkpost.py in.png out.png` (no options). Pen samples measure stroke 1–3 px, coverage 0.06–0.27 — thinner and cleaner than the reference pages; that is what this variant is.

## Variant `marker` — 速写本 · 马克笔

Prompt = **subject sentence + sub-style block + CORE(pen)**, then `inkpost.py --marker` with the sub-style's stroke target. The exact prompts and seeds of all 13 marker samples are in `references/prompts-marker.md`.

### Subject: invented gadget by default

Default: redesign the subject as an invented retro-futurist gadget and describe it through the symbol vocabulary:

```
An invented retro-futurist gadget, not a real product: <a pocket jet-engine gadget | a desk-top tokamak toy | a handheld telescope device | a steam-engine desk toy | …>: <3–5 parts, using knob circles, dot grilles, tick scales, digit displays, a small black screen>.
```

Typical sketchbook subjects work best: radios, synths, recorders, helmets, consoles, handheld devices.

Switch — **faithful drawing needed** (the object must stay recognisable as the real thing, e.g. a science plate): replace the opening with `A quick marker sketch of <the real object>, simplified but recognisable: <its 3–5 defining parts>.` and keep everything else. If accuracy matters more than the look, use the `pen` variant instead.

### CORE(pen) (always last; pick the pen per sub-style below)

```
Page from an industrial designer's sketchbook, drawn fast with <PEN> on plain white paper. One line weight everywhere: nervous, wobbly lines that overshoot at the corners, some edges traced twice. Most surfaces left white. Only one or two dark parts filled solid black, with a thin white highlight stripe left unfilled; quick scribbled cross-hatching inside grilles. Simplified, slightly naive shapes with slightly distorted perspective, three-quarter view from above. Symbol details: knob circles, dot-grid speaker grilles, tick scales, seven-segment digit displays, small rectangles. No floor, no background, no shadow, no thin hairlines, no tonal shading, no grey, no colour, no hearts, no stars, no decorative doodles. Lots of plain white paper around it. A five-minute sketch, not a finished illustration.
```

Asking for "bold solid black fills on dark parts, openings and screens" (pilot m1) gave coverage 0.45–0.60 and a lino-print look; "only one or two dark parts filled solid black … most surfaces left white" fixed it. "No floor" stops Qwen drawing a tiled floor under desk objects.

### Sub-style blocks, pens and post-process

| Code | Block (after the subject) | `<PEN>` | Post-process | Target (reference) |
| --- | --- | --- | --- | --- |
| A | `The gadget fills most of the page.` | `a thick black felt-tip marker` | `--marker` (stroke 7) | 7 px, cover ~0.33, solid ~0.33 |
| B | `Two or three quick perspective construction lines extending past the object; a second small view of it in a corner.` | `a thick black felt-tip marker` | `--marker --stroke 6` | 5–7 px, cover 0.16–0.33 |
| C | `Around it, rough messy lowercase handwriting notes, scrawled fast and uneven, with scribbled arrows pointing at parts: 'w1', 'w2', 'w3', 'w4'. Only words and arrows, no hearts, no smileys, no doodles.` | `a medium black felt-tip pen` | `--marker --stroke 4` | 3–4 px, cover ~0.13–0.25 |
| D | `A loose, messy sketchbook page of twenty to thirty tiny thumbnail sketches of different invented gadgets, uneven sizes from tiny to medium, some overlapping each other, most only a few quick lines, some half-finished, a couple scribbled out, a few stray scribbles, crowded in one corner and empty elsewhere, not in a grid, not lined up, two or three tiny scrawled words.` + a list of 5–7 gadget types | `a fine black felt-tip pen` | `--wobble 1.0` only (no thickening: real scatter pages are thin pen) | ~1–2 px at page scale, cover ~0.10 |
| E | `Simplified, objects drawn as simple boxes and cylinders.` | `a medium black felt-tip pen` | `--marker --stroke 5` | 5 px, cover ~0.16 |

### What `--marker` does

`inkpost.py … --marker` = `--stroke 7 --wobble 1.4 --rough 0.6`, after the pen-variant threshold, at 2× resolution:

1. **Thicken to a target**: measure the current typical stroke (same method as `measure.py`) and dilate the ink just enough to reach `--stroke` px (bounding box at 1024). It never thins; strokes already at target get no growth, so hatching does not clot.
2. **Wobble**: a smooth random displacement field (wavelength ~6 % of the image, ±1.4 px) bends the strokes so they look hand-drawn rather than evenly fattened.
3. **Rough edge**: blur + fine noise + threshold gives a ragged marker edge. Above `--rough 0.9` it leaves specks in hatching.

Dilation runs before the wobble, so thin lines can't break. Check with `scripts/measure.py out.png`: stroke and coverage should land near the sub-style's target; solid share above ~0.5 means the prompt produced too many black fills (fix the prompt, not the post-process).

## Variant `contrast` — 速写本 · 粗细对比

The rule: where there are few lines, use big areas of black or white and thick lines; where there are many lines, use thin lines. Each drawing mixes both, and the difference reads clearly without being a gimmick. The reference pages already lean this way a little (calm/busy line-width ratio 1.21 overall, 1.38 on the bold pages); this variant makes it deliberate, at about 2.5–3.5.

Same structure as `marker`: invented gadget subject by default (with the faithful switch) + sub-style block + CORE, then `inkpost.py --varied`. Exact prompts and seeds of the kept samples: `references/prompts-contrast.md`.

### CORE

```
Page from an industrial designer's sketchbook, drawn fast in black ink on plain white paper with two pens: a thick black felt-tip marker for the big shapes and a fine 0.3 mm pen for the details. Line weight follows how busy each area is: the big simple forms are outlined with thick, bold, confident lines and kept as large flat areas — one or two of them filled solid black (a visor, a screen, an opening or the shadow side), the other big surfaces left as open white paper; the small busy parts — knobs, dot grilles, tick scales, digit displays, vents, screws, cables and hatching — are drawn with fine thin lines. The same drawing mixes both: calm areas are bold and simple, busy areas are fine and detailed. Lines a little wobbly, overshooting at the corners. Simplified, slightly naive shapes, three-quarter view from above. No grey, no tonal shading, no colour, no floor, no cast shadow, no background. Plain white paper around it. A quick sketch, not a finished illustration.
```

Sub-style blocks: the marker ones for A, B and E. On C, say "notes in the fine pen". For D: "the bigger thumbnails outlined bold with one black area, the tiny ones only a few fine lines". Without "one or two of them filled solid black", Qwen leaves every big surface white (solid share ~0.1); the rule allows big black *or* big white, so ask for both.

### `--varied` (the density-driven weight)

`inkpost.py … --varied` = `--vgrow 2.5 --thin 0.85 --wobble 1.2`, at 2× resolution:

1. **Busyness map:** density of ink edges in a ~50 px window, normalised to 0–1 between the 30th and 85th percentile over the ink, then blurred, so weight changes gradually along a stroke and never jumps.
2. **Big-form mask:** each silhouette is filled by flooding the outside paper from the border, then eroded by ~40 px. Only strokes near a surviving form may grow, so handwriting, arrows and small isolated marks stay thin.
3. **Grow by calm:** each stroke grows by up to `--vgrow` px a side where busyness is 0, scaling down to no growth where busyness is 1. This is a distance-limited dilation with a per-pixel radius.
4. **Thin where busy:** where busyness > `--thin`, shave 1 px off strokes that are ≥ 5 px wide. Thinner strokes are untouched, so nothing breaks.
5. **Wobble.** There is no `--rough`, because on 1 px lines it breaks them into speckles; that was seen on the first D test.

Check with `measure.py`: the `ratio` column is mean line width in the calmest third of the line pixels over the busiest third.

| Set | Ratio (calm / busy) |
| --- | --- |
| Reference set, all 87 | 1.21 (p10–p90 0.92–1.52); sparse 6.8 px / dense 5.5 px |
| Reference set, bold pages | 1.38 |
| pen / marker / ink samples | 0.76 / 1.35 / 1.17 |
| contrast target | ~2.5–3.5 on A/B/C/E. D pages stay mostly fine-lined: their thumbnails are too small to count as big forms. |

## Variant `ink` — 速写本 · 浓墨

Same structure as `marker`: invented gadget subject (faithful switch available) + sub-style block + CORE(pen), then `inkpost.py --heavy`. Exact prompts and seeds of the kept samples: `references/prompts-ink.md`.

### CORE(pen)

```
Page from an industrial designer's sketchbook, drawn fast with <PEN> on plain white paper. Rough, ragged, broken strokes with dry-brush edges and ink skips, overshoots and double strokes. About half of the object is solid black: the shadow side, the openings, the screens and the insides are filled black, while the lit side stays white with thick rough outlines. On the black parts, details are reversed out in white: white knob circles, white dot grilles, white digit displays and a white highlight stripe; clear white gaps separate the black masses. Graphic and high contrast, simplified, slightly naive, three-quarter view from above. No grey, no tonal shading, no colour, no floor, no cast shadow on the ground, no background. Plain white paper around it. A five-minute brush-marker sketch, not a finished illustration.
```

`<PEN>`: `a worn-out thick black brush marker` for A/B, `a worn-out black felt-tip marker` for C/D/E. Sub-style blocks are the marker ones, except D, which adds "many of them filled black with white details, some only a few rough strokes".

What the iterations taught (k1–k3):
- "Large solid black areas: a bold black silhouette …" made almost the whole object black (coverage 0.70, solid 0.93) and the post-process then swallowed the white details. "About half of the object is solid black … the lit side stays white" lands in range.
- "black shadow sides" made Qwen paint a black cast shadow on the ground, so CORE says "no cast shadow on the ground".
- On notes pages, write "The notes are plain words with arrows and nothing else" and don't mention hearts: with this CORE, "no hearts" brought hearts back.

### Post-process

| Code | inkpost | Target (deliberately beyond a real sketchbook) |
| --- | --- | --- |
| A, B | `--heavy` | coverage 0.40–0.60, solid 0.55–0.80 |
| C | `--heavy --stroke 5` (keeps the handwriting legible) | coverage ~0.35–0.45 |
| D | `--wobble 1.2 --rough 0.8 --dry 0.6` (no growth: lighter but rougher) | coverage ~0.10–0.25 |
| E | `--heavy --stroke 6` | coverage ~0.25–0.40 |

`--heavy` = `--stroke 7 --wobble 1.8 --rough 1.2 --dry 0.8`:
- `--dry` carves dry-brush streaks (25°) out of a band along stroke edges only, never out of the middle of a black mass, so masses stay solid while edges look dragged and broken.
- `--close C` (morphological closing) is available to turn hatching and small dark pockets solid when an input is too light. It also fills reversed white lines, so it is not in the preset; use about 1.5 at most.

## Engines and settings (all variants)

| Engine | Where | Settings | Time / memory (1024×1024) | Verdict |
| --- | --- | --- | --- | --- |
| **Qwen-Image 2.1 Q6 — best** | a ComfyUI server (`COMFY_URL`); `scripts/comfygen.py jobs.json outdir` | workflow: UnetLoaderGGUF `qwen-image-2.1-Q6_K.gguf`, CLIPLoader `qwen3vl_8b_int8_convrot.safetensors` (type `qwen_image`), VAELoader `qwen_image_2.1_vae_bf16.safetensors`, QwenImage21Cache, TextEncodeQwenImage21; KSampler **euler / simple, 20 steps, CFG 1.0**, denoise 1 | ~2 min (Apple M3 Ultra) | Follows the blocks, writes the requested notes, keeps subjects recognisable. CFG 3 + negative doubled the time and made drawings heavier and more rendered: keep CFG 1 and put every "no …" in the prompt. |
| FLUX.2 klein 4B 8-bit — fallback | locally: `scripts/localgen.sh flux "<prompt>" out.png <seed>` | **4 steps**, no guidance | 90 s, 10 GB peak | Chunky, cartoonish marker look; fits `marker` A; adds speed lines ("no motion lines"). |
| Z-Image Turbo 8-bit — last resort | locally: `scripts/localgen.sh zimage …` | **9 steps** | 256 s, 7.6 GB peak | Draws a dark page border; crop it or add "full-bleed white paper, no border". |

Sizes: 1024×1024 for A/B/C/E, 1024×1024 or 1344×1024 for D pages, 768×1344 for vertical video frames (leave the bottom third empty for captions).

Shared GPU: every job takes the mkdir lock `$GPU_LOCK` (owner file `"<tag> <pid> <epoch>"`) for one image at a time; never remove a lock whose pid is alive. `comfygen.py` and `localgen.sh` do this. When waiting on a job with pgrep, use a bracket pattern (`pgrep -f "[c]omfygen.py"`) or it matches the waiting shell itself.

Dark-mode variant of any result: `inkpost.py in.png out.png [--marker …] --ink D3D3D3 --paper 000000`.

## What to avoid

- Generic "pencil sketch": grey graphite, smudges, paper grain → CORE + inkpost.
- Architect-style scribble: many thin repeated contour lines and speed lines → "one line weight", "no thin hairlines".
- Too clean / vector: perfect ellipses, ruler lines → "wobbly, overshooting, some edges traced twice".
- Lino-print blackness (marker): coverage > 0.45 or solid > 0.5 → "only one or two dark parts filled solid black … most surfaces left white".
- Muddy black blob (ink): coverage > 0.6 or white details gone → "about half of the object is solid black … the lit side stays white"; don't add `--close`; check the reversed white knobs, grilles and digits survive inkpost.
- Tidy scatter pages: identical, finished, gridded thumbnails → list different gadget types; "most only a few quick lines, some half-finished, scribbled out, overlapping, not in a grid".
- Decorative doodles in notes (Qwen likes adding little hearts) → "Only words and arrows, no hearts, no smileys, no doodles"; reject the image if one slips through.
- Any artist name, signature, watermark, frame or colour.

## Verification checklist

Compare at the same size against your own reference pages if you have them, and against the other variants' samples so they stay distinct.

- [ ] At thumbnail size next to reference pages, it reads as the same kind of sketchbook page (marker) / as a tidy pen version of it (pen).
- [ ] Pure ink + paper after inkpost: no grey, no paper tint.
- [ ] `measure.py`: stroke and coverage within the sub-style's target row above (pen: coverage 0.06–0.32; ink: see its own table).
- [ ] Contrast: thick outlines only on the big calm forms; knobs, grilles, scales, notes and hatching in fine lines; one or two flat black areas; `measure.py` ratio ≥ ~2; no thin line broken.
- [ ] Ink: about half black, reversed white details readable at thumbnail size, white gaps between black masses, ragged dry-brush edges, no cast shadow blob.
- [ ] Marker: one heavy line weight, wobbly; solid blacks are a few areas with white highlight stripes, not the whole object.
- [ ] Marker default: the subject is an invented gadget built from the symbol vocabulary (unless the faithful switch was asked for).
- [ ] Notes (C): rough, messy, lowercase, with arrows, spelled as asked, and **no hearts, smileys, stars or doodles**.
- [ ] Scatter (D): uneven sizes, overlaps, half-finished outlines, a scribbled-out one, not in a grid.
- [ ] No background, floor, cast shadow, frame, signature or colour.
- [ ] Engine, model, seed, steps, CFG, size, prompt and inkpost options recorded next to each kept image (`comfygen.py` writes the `.json`; add the inkpost options).

## Files

- `scripts/comfygen.py` — ComfyUI client: the Qwen-Image 2.1 workflow, optional negative/CFG, shared GPU lock, writes PNG + JSON receipt.
- `scripts/inkpost.py` — single-colour ink post-process; pen default; `--marker` / `--stroke` / `--grow` / `--wobble` / `--rough` for marker; `--heavy` / `--dry` / `--close` for ink (the preset isn't called `--ink` because `--ink` sets the ink colour); `--varied` / `--vgrow` / `--thin` for contrast.
- `scripts/measure.py` — stroke width, coverage, solid share, and the calm/busy line-width ratio, comparable with the reference numbers above.
- `scripts/localgen.sh` — FLUX.2 klein / Z-Image fallback runs under the GPU lock.
- `references/prompts-pen.md`, `references/prompts-marker.md`, `references/prompts-ink.md`, `references/prompts-contrast.md` — exact prompts and seeds behind each kept sample.
- `examples/pen`, `examples/marker`, `examples/ink`, `examples/contrast` — the 13 samples of each variant (A–E sub-styles), made with the prompts in `references/` and post-processed with `inkpost.py`; file names match the prompt entries.
- `references/engines.md` — measured times and observations per engine.
