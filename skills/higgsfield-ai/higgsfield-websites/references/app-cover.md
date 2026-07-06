# App cover + OG image (3:2, Higgsfield brand style)

Generate the launch cover for an app/website — the image behind `og_image_url`
and the marketplace card — in 3:2, using `higgsfield generate create gpt_image_2`,
guided by the reference covers bundled in
`references/cover-refs/`. Also use this when the user directly asks for a
"cover", "кавер", "обложка", "OG image", "launch cover" or "thumbnail" for a
product, model, feature or app announcement.

Every request produces TWO output files **from ONE generation** (same pixels
in both):

1. **`<name>_cover.png`** — the plain cover: the generated full-bleed artwork
   as-is (for marketplaces and previews).
2. **`<name>_og.png`** — the OG image: the exact same artwork masked by
   `scripts/compose_cover.py` into a solid frame + geometrically perfect
   stadium capsule + corner dots. Image models cannot draw a true pill shape,
   so the frame geometry is always done in code, never by the model.

Because the OG mask crops the outer ~8% of the art (most at the corners and
the capsule's rounded ends), the generation prompt must insist that all text
and the focal subject stay inside the central safe zone. If something
important still lands under the mask, regenerate — don't ship a cover with
clipped text.

## The brand style (what makes these covers recognizable)

Every reference cover follows the same visual system. Reproduce it unless the
user asks to deviate:

- **Solid vivid background frame** filling the whole canvas — acid
  lime/chartreuse is the signature color; yellow, green, olive, peach, or soft
  gray also appear. Small decorative dots sit near the corners of the frame.
- **A large stadium-shaped capsule (true pill shape)** inset from the edges,
  containing the hero scene: end caps are perfect semicircles, corner radius
  equals half the capsule height. This shape is drawn by
  `scripts/compose_cover.py`, not by the image model. The capsule holds either
  a cinematic/photoreal scene, a clean studio composition, or a playful 3D
  render.
- **Big display typography** for the product name — the name is the loudest
  element after the hero, in the accent color (e.g., lime text on dark scene)
  or dark text on light scene. The typeface treatment VARIES between covers
  and should match the product's vibe — don't default to the same condensed
  uppercase every time. Treatments seen across the brand: bold condensed
  uppercase (sporty/loud launches), glossy chrome bubble lowercase (Y2K/cute),
  elegant serif with italic accents (editorial/analytical), pixelated 8-bit
  lettering (techy/retro), clean modern sans lowercase (product/utility),
  stencil or slab (industrial). Pick one deliberately and describe it
  explicitly in the prompt.
- **A small rounded pill CTA** reading "Available now at higgsfield.ai" in
  small clean type.
- **Higgsfield logo** (squiggle mark + wordmark) placed near the title, small.
  Partner logos (e.g., "Higgsfield MCP × Claude") appear as a compact lockup
  above the title when relevant.
- Hero imagery is high-production: dramatic light, punchy contrast, tasteful
  humor or spectacle (goalkeeper diving, office slapstick, neon subway,
  claymation shark). One clear focal subject — never a collage of equal
  elements.

## Workflow

### 1. Get the essentials from the request

You need: the **product/feature name** (exact spelling — it will be rendered
as text), a **hero concept** (the focal scene), and a **typography treatment**
matching the vibe (see the style section — vary it between covers). For an app
build, derive the name from `og_title` and the hero concept from what the app
does. If the user gave only a name, invent a hero concept that fits the
product's vibe (playful spectacle > generic tech imagery). Optional: accent
color, partner lockup, CTA text override.

### 2. Pick 2–4 reference images

References are hosted at
`https://static.higgsfield.ai/website-builder/og-image-references/ref_01.jpg`
… `ref_11.jpg` (same pattern for every file below):

| File | Layout | Vibe |
|---|---|---|
| ref_01 | landscape | lime frame, neon subway, anime character — dark/cinematic |
| ref_02 | landscape | lime frame, stadium goalkeeper — sporty, dramatic |
| ref_03 | landscape | peach frame, light studio, glass cards — clean/technical |
| ref_04 | landscape | olive frame, office slapstick photo — comedic |
| ref_05, ref_06 | vertical | full-bleed 9:16 versions (no capsule) — style only |
| ref_07 | landscape | green frame, butterflies, light — fresh/friendly |
| ref_08 | landscape | sage frame, claymation shark — playful/craft |
| ref_09 | landscape | yellow frame, office banana slapstick — comedic |
| ref_10 | landscape | gray frame, app cards fan — product UI focus |
| ref_11 | vertical | orange gradient, K-pop portrait — style only |

Default choice: 2–3 landscape refs whose vibe matches the requested cover
(e.g., comedic request → ref_04 + ref_09 + one lime ref for the frame). Always
include at least one lime-frame ref (ref_01/ref_02) unless the user asks for
another palette, since lime is the signature.

### 3. Reference the chosen refs

The generate command's `--image` flag accepts a direct http(s) URL (the CLI
auto-imports it), so pass the chosen ref URLs straight to the generation in
step 4 — no separate upload step. If you prefer to pre-import them,
`higgsfield upload create <url> …` returns an id per file that you can reuse as
a `--image` value.

### 4. Generate ONE full-bleed artwork

Call `higgsfield generate create` once, passing the chosen refs as repeated
`--image` flags:

```bash
higgsfield generate create gpt_image_2 \
  --aspect_ratio 3:2 --quality high --resolution 2k --count 1 \
  --image https://static.higgsfield.ai/website-builder/og-image-references/ref_01.jpg \
  --image https://static.higgsfield.ai/website-builder/og-image-references/ref_02.jpg \
  --prompt "<see template>" --wait
```

Prompt template — fill the brackets, keep the structure. The safe-zone
sentence is what protects the OG mask step; keep it:

> Full-bleed promo artwork in the visual style of the scenes inside the
> reference images' capsules, edge-to-edge composition filling the entire
> canvas, NO border, NO frame, NO rounded capsule, NO corner dots. Scene:
> [HERO CONCEPT — one focal subject, dramatic lighting, high production
> value]. Huge title "[PRODUCT NAME]" as the dominant text, [TYPOGRAPHY
> TREATMENT — e.g. "glossy chrome bubble lowercase lettering" / "elegant
> serif with italic accents" / "pixelated 8-bit lettering" / "bold condensed
> uppercase"], [TITLE COLOR] color. Small rounded pill button with the text
> "Available now at higgsfield.ai". Small Higgsfield logo near the title.
> IMPORTANT: keep the title, tagline, button, logo and the focal subject
> inside the central safe zone — nothing closer than 10% to any edge, corners
> empty (background only) — the outer edges will be cropped by a rounded
> mask. 3:2 landscape composition, punchy contrast, premium promo art.

Text rendering matters: repeat the exact product name in quotes and keep other
text minimal — GPT Image renders short strings well but degrades with many
labels.

### 5. Produce the two outputs

The raw artwork IS `<name>_cover.png` — save it as-is. Then build the OG image
from the same file with the compose script at the END of this document: write
it to `compose_cover.py` in your workspace verbatim, then run it (needs
Pillow + numpy — `pip install pillow numpy` if missing):

```bash
python3 compose_cover.py \
  --art <name>_cover.png --out <name>_og.png \
  --frame-color "#D9FF2E" --dot-color "#1A1A1A"
```

The script masks the art into a perfect stadium capsule, paints the frame and
corner dots. Pick `--frame-color` to complement the art: signature acid lime
`#D9FF2E`, pastel sky-blue `#A9CFF4`, yellow `#F5C518`, olive `#7A7D3C`, peach
`#F7DDB9`. `--dot-color` should read clearly against the frame (dark `#1A1A1A`
on light frames, white or pastel on saturated ones). Other flags:
`--margin-x/--margin-y` (capsule inset), `--no-dots`.

Inspect the OG result closely (zoom into text near the capsule boundary). If
the mask clipped text or the focal subject, first try fixing it in the compose
step — `--offset-x/--offset-y` shifts the art (e.g. `--offset-x -70` pulls a
right-hugging title inward) and `--shrink 0.92` scales it down; revealed gaps
get filled with a blurred extension of the art, invisible on dark or soft
backgrounds. Only regenerate (restating the safe zone more forcefully) if the
shift/shrink fix isn't enough or the seam is visible. (Legacy: `--detect` mode
handles art that already contains a model-drawn frame.)

### 6. Deliver / wire into the app

- **Standalone cover request**: show both files to the user and save them to
  their folder if one is connected.
- **App/website build (the publish gate)**: upload BOTH files with
  `higgsfield upload create` and set the returned durable URLs in
  `app/src/app-meta.json`: `<name>_og.png` → `og_image_url`,
  `<name>_cover.png` → `marketplace_cover_url`. Commit before running
  `higgsfield website publish`.

If the text came out garbled, regenerate once with the flaw named explicitly
in the prompt (e.g., "the title must read exactly ..."), then re-run the
compose step.

## Deviations

The user's explicit wishes always beat the defaults above: different aspect
ratio, no capsule, another CTA, partner lockups ("Higgsfield MCP × Claude"
style), vertical format (then use ref_05/06/11 as refs). The brand system is
the default, not a cage.

## compose_cover.py (write this file verbatim, then run it)

```python
#!/usr/bin/env python3
"""Build the OG version of a Higgsfield-style app cover from full-bleed art.

Takes the full-bleed artwork (which is itself the plain marketplace cover)
and produces the OG image: solid color frame + the art masked into a
geometrically perfect stadium (pill) capsule + small corner dots.
The stadium's end caps are perfect semicircles (radius = half height) —
image models can't draw this reliably, so it is done in code, on the exact
same pixels as the plain cover.

Usage:
  python3 compose_cover.py --art plain_cover.png --out cover_og.png \
      --frame-color "#D9FF2E" --dot-color "#1A1A1A"

Modes:
  default        — the art is full-bleed: it is masked into the capsule.
  --detect       — the art already contains a model-drawn frame+capsule:
                   the capsule is auto-detected and its geometry perfected.
"""
import argparse
from PIL import Image, ImageDraw, ImageFilter
import numpy as np


def hex_rgb(s):
    c = s.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def sample_frame_color(im):
    w, h = im.size
    pts = [(int(w * 0.01), int(h * 0.5)), (int(w * 0.99), int(h * 0.5)),
           (int(w * 0.5), int(h * 0.015)), (int(w * 0.5), int(h * 0.985))]
    px = np.array([im.getpixel(p) for p in pts])
    return tuple(int(v) for v in np.median(px, axis=0))


def detect_capsule(im, frame_rgb, tol=60, frac=0.12):
    a = np.asarray(im.convert("RGB"), dtype=np.int16)
    diff = np.abs(a - np.array(frame_rgb, dtype=np.int16)).sum(axis=2)
    m = diff > tol
    cols, rows = m.mean(axis=0), m.mean(axis=1)
    xs, ys = np.where(cols > frac)[0], np.where(rows > frac)[0]
    if len(xs) == 0 or len(ys) == 0:
        raise SystemExit("could not detect capsule — check the art or use default mode")
    return int(xs[0]), int(ys[0]), int(xs[-1]) + 1, int(ys[-1]) + 1


def stadium_mask(size, box, ss=4):
    W, H = size
    big = Image.new("L", (W * ss, H * ss), 0)
    r = (box[3] - box[1]) // 2
    ImageDraw.Draw(big).rounded_rectangle([v * ss for v in box], radius=r * ss, fill=255)
    return big.resize((W, H), Image.LANCZOS)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--art", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--frame-color", default="#D9FF2E",
                   help="frame hex (default mode). In --detect mode default is auto-sampled")
    p.add_argument("--dot-color", default="#1A1A1A")
    p.add_argument("--detect", action="store_true",
                   help="art already has a model-drawn frame: detect & perfect it")
    p.add_argument("--margin-x", type=float, default=0.045,
                   help="capsule inset, fraction of width (default mode)")
    p.add_argument("--margin-y", type=float, default=0.055,
                   help="capsule inset, fraction of height (default mode)")
    p.add_argument("--inset", type=float, default=0.006,
                   help="inset inside detected capsule (--detect mode)")
    p.add_argument("--no-dots", action="store_true")
    p.add_argument("--shrink", type=float, default=1.0,
                   help="scale the art down inside the capsule (e.g. 0.92) when text "
                        "sits too close to an edge; gap is filled with a blurred extension")
    p.add_argument("--offset-x", type=int, default=0,
                   help="shift the art horizontally (px, negative = left) to pull "
                        "edge-hugging content away from the mask")
    p.add_argument("--offset-y", type=int, default=0)
    a = p.parse_args()

    im = Image.open(a.art).convert("RGB")
    W, H = im.size

    if a.shrink != 1.0 or a.offset_x or a.offset_y:
        # Blurred cover-scaled copy fills whatever the shifted/shrunk art reveals.
        base = im.resize((int(W * 1.1), int(H * 1.1)), Image.LANCZOS) \
                 .filter(ImageFilter.GaussianBlur(40)) \
                 .crop((int(W * 0.05), int(H * 0.05), int(W * 1.05), int(H * 1.05)))
        art = im if a.shrink == 1.0 else im.resize(
            (int(W * a.shrink), int(H * a.shrink)), Image.LANCZOS)
        base.paste(art, ((W - art.width) // 2 + a.offset_x,
                         (H - art.height) // 2 + a.offset_y))
        im = base

    if a.detect:
        frame_rgb = sample_frame_color(im)
        fc = "#%02X%02X%02X" % frame_rgb
        x0, y0, x1, y1 = detect_capsule(im, frame_rgb)
        ins = int(W * a.inset)
        box = (x0 + ins, y0 + ins, x1 - ins, y1 - ins)
    else:
        fc = a.frame_color
        mx, my = int(W * a.margin_x), int(H * a.margin_y)
        box = (mx, my, W - mx, H - my)

    mask = stadium_mask((W, H), box)
    out = Image.composite(im, Image.new("RGB", (W, H), fc), mask)

    if not a.no_dots:
        dr = int(W * 0.008)
        ox, oy = int(W * 0.028), int(H * 0.045)
        d = ImageDraw.Draw(out)
        for cx in (ox, W - ox):
            for cy in (oy, H - oy):
                d.ellipse((cx - dr, cy - dr, cx + dr, cy + dr), fill=a.dot_color)

    out.save(a.out)
    print(f"saved {a.out} {W}x{H} frame={fc} capsule={box}")


if __name__ == "__main__":
    main()
```
