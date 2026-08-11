# Social media graphics

Create once the slots used by the requested social graphic are approved.

## Required question

Require approved logo and palette for branded no-text graphics. Add approved typography only when readable text appears. Read those modules separately; never force typography for a no-text post.

Before generation, ask once for:

- Platform, aspect ratio, and number of outputs
- Exact text that must appear; “no text” is a valid answer
- Visual mode:
  - plain branded background/poster
  - mockup photography/application
- Any supplied photography or product assets

Preserve copy verbatim. Never invent sale language, CTA, claims, prices, contact details, or placeholder copy.

## Output contract

Social-media deliverables are flattened PNG/JPG graphics, not editable templates. Never promise or create PPTX, SVG, PSD, Figma, Canva, or layered files for this module.

Supported modules:

- square post
- 4:5 feed post
- 9:16 story
- carousel cover/body/CTA cards
- channel banner/cover

## Plain branded poster

Use GPT Image 2 for the finished graphic.

Pass references through repeated CLI `--image` flags (`Image0` is the first flag, `Image1` the second, and so on; use local PNG/JPG paths, upload IDs, or completed job IDs — never an SVG path):

- Exact approved logo variant
- Approved typography specimen
- Any official product/photo reference

The prompt must state:

- Exact literal copy
- Display/body font family names and which text uses each
- Logo placement, scale, clear space, and color variant
- Text placement, hierarchy, alignment, line breaks, and contrast
- Exact palette roles
- Requested aspect ratio

Never compose this flattened module with local Python/Pillow or runtime package installation. The controlled GPT Image 2 render is the deliverable; use the deterministic poster/banner module when exact editable typography is required.

```bash
higgsfield generate create gpt_image_2 \
  --image "$BRANDKIT_WORKDIR/logo/approved-logo-2048.png" \
  --image "$BRANDKIT_WORKDIR/reviews/approved-typography.png" \
  --prompt "<exact social graphic prompt>" \
  --aspect_ratio 3:4 \
  --resolution 4k \
  --wait --json
```

Omit the typography reference for a no-text graphic and use only live-schema ratio/resolution values. GPT Image 2 does not currently expose `4:5`; for an exact 4:5 feed post, compose with a centered 4:5 safe area, generate at `3:4`, download the result, then crop only the vertical excess:

```bash
magick generated-3x4.png -gravity center -crop '100%x93.75%+0+0' +repage final-4x5.png
```

`convert` may replace `magick`. Verify the final pixel ratio exactly equals 4:5 and that no locked logo or copy crosses the crop boundary.

## Mockup photography/application

1. Create or use the mockup photograph first with its target surface blank. Follow `mockups.md` for the base scene.
2. Pass that exact mockup job ID as the first `--image` (`Image0`).
3. Pass the approved logo PNG as the second `--image` (`Image1`).
4. Pass the approved typography specimen PNG as the third `--image` (`Image2`).
5. GPT Image 2 adds the exact copy, logo, and approved typography to the blank surface.

Preserve Image0's camera, crop, people, pose, lighting, materials, folds, shadows, perspective, environment, and background exactly. Change only the controlled social artwork/application.

## Typography fidelity

The approved typography specimen is mandatory whenever text appears. Name the exact display/body families in the prompt; never infer typography from the logo or palette.

After generation, check the output against the specimen. Retry once when the letterform character is visibly substituted. If GPT Image 2 still cannot reproduce the approved typography, report the limitation instead of presenting the output as exact.

## Consistency and QA

- Exact copy and spelling
- Correct platform ratio
- Approved logo geometry and color variant
- Approved display/body typography character
- Readable hierarchy and text contrast
- Approved palette only
- No pseudo-text, extra logos, invented CTA, or unsupported claims
- All outputs in one set share the same Brand Lock

## Approval

Show all final graphics in chat and wait for ordinary feedback. Save the approved set through `approve_brandbook_element` with a stable key such as `social-media-graphics` and `required_slots: ["logo","palette"]`; add `"typography"` only for text-bearing graphics.
