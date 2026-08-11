# Precise asset analysis

Analyze supplied assets before concepting or generation. The goal is a usable visual specification, not an impressionistic description.

## 1. Inventory and assign roles

Inspect every attachment and local path supplied in the conversation. If the user asks to reuse prior Higgsfield uploads, run `higgsfield upload list --json`. Build an inventory with:

```text
id | filename/source | format | dimensions/pages | likely role | authority
```

Use one role per asset:

- `official-logo`
- `logo-variant`
- `font-file`
- `palette`
- `brandbook`
- `template`
- `representative-visual`
- `style-reference`
- `content-only`
- `unknown`

Ask the user only when confusing two roles would change the output—for example, an official logo versus a visual reference. Never treat inspiration as an official asset without confirmation.

After confirming authority, immediately persist each official Essential Kit slot with `lock_authoritative_logo`, `lock_authoritative_palette`, or `lock_authoritative_typography`. Preserve the exact local path, URL, upload ID, or job ID plus the source summary and `user_supplied` origin. Do not wait for generated missing elements.

### Inspirational references

For every `style-reference` or `representative-visual`, separate reusable taste signals from protected/distinctive design:

```text
Reference:
User specifically likes:
Palette behavior:
Typography character:
Composition/grid:
Shape/material language:
Overall mood:
Do not copy:
```

Ask what specifically inspires the user when they have not said. Offer palette, typography, composition, shape language, material, and overall aesthetic plus a free-text option.

If they do not answer, use the overall aesthetic/design-system character as a taste signal. Do not reproduce the reference's logo, distinctive layout, illustration, pattern, or artwork, and do not pass it into logo generation.

## 2. Evidence labels

Attach one evidence label to every extracted rule:

- **source-declared** — explicit in SVG/CSS/PPTX/PDF/font metadata or written brand guidelines.
- **measured** — deterministically calculated from source pixels or geometry.
- **visually-observed** — clear to visual analysis but not available as source data.
- **inferred** — a plausible interpretation or recommendation.

Keep exact values and inferred matches separate. Never call an inferred font, radius, grid, or color role exact.

## 3. Source precedence

Resolve conflicts in this order:

1. User's explicit correction
2. Official editable source or font file
3. Written brandbook rule
4. Repeated value across multiple official assets
5. Deterministic measurement
6. Visual observation
7. Inference

Record conflicts instead of averaging them away. A social campaign may intentionally use a different treatment from the core identity.

## 4. Raster image analysis

Read images semantically and compositionally yourself when your client shows them; analyze several related images together to detect repeated rules, chunking large sets into manageable groups.

For deterministic measurement, use the local file directly or download the user-authorized hosted asset into `"$BRANDKIT_WORKDIR/assets"`. Use the installed tooling (ImageMagick, Python/Pillow) to measure:

- Pixel dimensions, color mode, alpha, and resolution metadata
- Dominant and repeated colors, with exact sampled hex values
- Background versus foreground color candidates
- Logo bounding box and clear-space ratios
- Margins, gutters, column alignment, and repeated spacing
- Border thickness and approximate corner radius
- Text-block positions, alignment, scale relationships, and line counts
- Repeated motif size, density, and rotation
- Image crop, focal point, balance, and negative-space distribution

Download only the user's own Higgsfield media URLs or user-supplied public URLs; never fetch unrelated third-party content. Document URLs use the dedicated document route below.

For anti-aliased pixels, cluster near-identical colors rather than reporting hundreds of false palette entries. Ignore photographic colors when extracting the graphic palette unless the image clearly uses them as deliberate overlays or surfaces.

Font recognition from pixels is never exact. Describe anatomy first (grotesk/humanist/geometric/serif, width, contrast, terminals, x-height, weight), then list possible matches with confidence.

## 5. SVG, CSS, and token files

Parse source directly before rendering:

- `viewBox`, width, height, and aspect ratio
- Fill/stroke colors and opacity
- Stroke widths, line caps, and joins
- Paths, groups, transforms, masks, and clipping
- Repeated geometry and spacing
- `font-family`, weight, style, letter spacing, and text anchors
- CSS variables and semantic token names
- Corner radii, shadows, borders, and gradients

Render a preview and compare it with the source parse. Preserve the original file as the authoritative logo whenever possible; do not regenerate it.

## 6. PDF and PPTX

Analyze documents locally. Use a supplied local path directly, or download a user-authorized document URL into `"$BRANDKIT_WORKDIR/assets"`, then inspect it with installed tooling.

For `.pptx`:

- Unpack the OOXML (`unzip`) when exact theme/font/shape data matters
- Render slide thumbnails with headless LibreOffice (`soffice --headless --convert-to pdf`, then `pdftoppm`) for visual reading

Capture slide size, master/layout structure, theme colors, font families, weights, positions, shape geometry, borders, fills, radii, image crops, alignment, and recurring page types.

For PDF, use the Poppler tools:

- `pdftotext` for declared rules/copy
- `pdffonts` for embedded font families
- `pdftoppm`/`pdfimages` for page/image evidence of visual hierarchy, palette, spacing, and composition; inspect the rendered pages locally

If the document cannot be parsed locally (corrupt, encrypted, or scanned without OCR value), report that and ask for page images or source files instead of hanging or improvising.

PDF geometry may be flattened or outlined. Mark recovered text/font data as source-declared only when the file exposes it; otherwise use measured or visually-observed.

## 7. Font files

For `.otf`, `.ttf`, `.woff`, or `.woff2`, inspect with available font metadata tools such as `fc-scan` or FontTools:

- Family and style names
- Weight and width classes
- Italic/oblique status
- Variable axes
- Character/language coverage
- License/name table metadata when present

Do not make a legal conclusion from metadata. Do not redistribute the file. For editable outputs, note that the recipient must install the font; PPTX does not reliably embed custom fonts.

## 8. Analyze the system, not only individual assets

After per-asset analysis, build a consistency matrix:

```text
Property | Core/official rule | Repeated variants | Exceptions | Confidence
```

Cover:

- Logo usage and exclusion zone
- Palette and role frequency
- Type roles and hierarchy
- Grid, margins, gutters, and alignment
- Border, corner-radius, and shadow language
- Composition and focal hierarchy
- Shapes, motifs, patterns, and textures
- Photography/render treatment only when it appears in supplied materials
- Format-specific exceptions

## 9. Output contract

Return analysis in this order:

1. **Authoritative assets**
2. **Measured visual tokens**
3. **Typography findings**
4. **Layout and composition rules**
5. **Graphic devices**
6. **Format-specific exceptions**
7. **Unknowns/conflicts**
8. **Safe extension rules**

Feed these findings into `references/brand-lock.md`. Do not generate until the lock distinguishes what must be preserved from what may be proposed.
