# Prompting, retry, and evidence

Read this reference only when preparing a native-alpha request, retrying a failed output,
handling several deliverables, or writing the final evidence report.

## Prompt clause

Keep the creative brief intact and add one output clause:

> Return a native transparent PNG whose area outside the subject contains genuine pixel
> transparency with a real alpha channel.

For isolated assets, add:

> Keep the complete subject uncropped with transparent padding. Do not draw a background,
> floor, cast shadow, glow, border, text, watermark, or transparency-preview pattern.

Do not repeatedly describe checkerboards. Naming a visual checkerboard can encourage a model
to render one. The validator, not the prompt, distinguishes real alpha from a preview pattern.

## Reference-image roles

Label every input by role. A character sheet can define identity and medium without becoming
the composition or edit target. Do not copy watermarks, page backgrounds, captions, props, or
layout from an identity reference unless the user asks for them.

For recurring characters, state only the identity features that are visible in the authorized
reference. Preserve the user's selected version instead of averaging it with later variants.

## Retry ladder

Use no more than three total attempts per distinct asset by default.

1. Generate with the user's brief plus the concise native-alpha clause.
2. If the file lacks alpha, repeat the same creative brief and state that the returned file,
   not a visual preview, must contain native alpha.
3. If it fails again, make one final native generation attempt. Keep it serialized and remove
   unnecessary scene language that could imply a backdrop.

After each attempt, run `validate_alpha.py` on the untouched original. Never feed an opaque
failure into background removal, chroma key, masking, segmentation, or a local alpha-writing
script.

When several assets are requested, finish generation and validation for one asset before
starting the next unless the current tool provides explicit transparent-output parameters and
concurrent behavior has been tested in the current environment.

## Technical evidence is not visual acceptance

An alpha channel proves that transparent pixels exist. It does not prove:

- clean fur, hair, glass, smoke, or motion-blur edges;
- absence of a broad low-alpha haze;
- correct subject identity, anatomy, text, or crop; or
- suitability on both light and dark surfaces.

Inspect the original asset in a viewer that can switch backgrounds. Do not save a composited
preview over the source. Record technical and visual verdicts separately.

## Evidence report template

```text
generation_route: built-in | api | unknown
model: <known model or unknown>
original_path: <path>
sha256: <lowercase hash>
format: PNG | WEBP
dimensions: <width>x<height>
mode: <decoded mode>
alpha_extrema: <min>, <max>
fully_transparent_pixels: <count>
corner_alpha: <top-left>, <top-right>, <bottom-left>, <bottom-right>
alpha_validation: pass | fail
edge_qa: pass | fail | not-inspected
postprocessing: none
```

Do not call a technically valid file a clean cutout when edge QA failed or was not run.
