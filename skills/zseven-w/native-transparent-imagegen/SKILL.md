---
name: native-transparent-imagegen
description: "Generate new raster assets that must contain native pixel transparency, then verify the untouched PNG or WebP before delivery. Use for transparent stickers, sprites, character cutouts, product assets, and furry or fine-edged subjects where background removal would be unacceptable. Do not use to remove a background from an existing opaque image, repair an opaque generation by masking or chroma key, or create ordinary opaque images."
---

# Native Transparent ImageGen

Generate the asset with native alpha. Treat a visible checkerboard, a prompt that says
"transparent," and a successful tool call as unverified until the original file passes
alpha inspection.

## Keep the boundary strict

- Use this skill only for a newly generated asset whose deliverable must contain native
  transparency.
- Treat supplied images as identity, subject, composition, or medium references unless the
  user explicitly requests an edit.
- Do not invoke background removal, segmentation, chroma-key extraction, masks, or local
  alpha synthesis to rescue an opaque output.
- Do not call a rendered checkerboard "transparent." An RGB checkerboard is a failed asset.
- If the user instead wants a background removed from an existing opaque image, route to a
  background-extraction workflow and disclose that it is an edit, not native generation.

## Generate conservatively

1. Preserve the user's subject, identity, style, composition, and text constraints.
2. Add one concise output requirement: return a PNG or WebP whose area outside the subject
   is genuine pixel transparency with a real alpha channel.
3. With a prompt-only built-in image tool, issue native-alpha deliverables one at a time.
   Do not parallelize unless the current tool exposes an explicit per-request background
   control and concurrent native-alpha behavior has been verified.
4. When the user explicitly chooses an API path that exposes output controls, request
   `background: "transparent"` and `output_format: "png"` or `"webp"`.
5. Preserve the original returned bytes. Validation must not rewrite, optimize, composite,
   resize, or otherwise alter the deliverable.

Read [references/prompting-and-retry.md](references/prompting-and-retry.md) when preparing a
prompt, retrying a failed output, generating more than one asset, or reporting limitations.

## Validate the untouched file

Install the validator dependency only when it is missing:

```sh
python3 -m pip install -r \
  "${CODEX_HOME:-$HOME/.codex}/skills/native-transparent-imagegen/scripts/requirements.txt"
```

Run the read-only validator on every requested deliverable:

```sh
python3 \
  "${CODEX_HOME:-$HOME/.codex}/skills/native-transparent-imagegen/scripts/validate_alpha.py" \
  --require-transparent-corners \
  /path/to/original-output.png
```

The file passes the technical gate only when:

- its decoded pixels contain an alpha channel;
- at least one pixel is fully transparent and at least one is visible;
- required padding corners are transparent when the asset is meant to be isolated; and
- the validator exits successfully on the original output.

Then inspect the actual edges against contrasting viewer backgrounds. Alpha metadata cannot
prove that fine fur is clean or that the image lacks a broad translucent haze. Reject visible
checkerboards, matte halos, colored fog, unintended shadows, clipped strands, or missing
details even when the metadata gate passes.

## Retry without faking success

- On an RGB or opaque output, keep all subject invariants and retry only the native-alpha
  output instruction.
- Make at most three total generation attempts per distinct asset unless the user requests
  more.
- Validate after every attempt. Do not edit the failed image into compliance.
- If all attempts fail, stop and report the original modes and validation failures. Offer an
  explicit API route only when available and authorized; never silently change models or use
  background extraction.

## Report evidence

For every accepted asset, report:

- generation route and model when known;
- original file path, format, dimensions, mode, and SHA-256;
- alpha extrema, fully transparent pixel count, corner alpha values, and validator verdict;
- visual edge-QA result; and
- the exact final prompt or the native-alpha clause added to the user's prompt.

Keep `generated`, `alpha-validated`, `edge-inspected`, `user-accepted`, and `published` as
separate states.
