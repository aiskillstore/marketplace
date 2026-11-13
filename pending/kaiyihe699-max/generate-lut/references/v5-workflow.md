# v5 Delivery, Color and Quality Contract

## Scope and reproducibility

The one-command creator is for display-referred 8-bit sRGB creative looks. Agent interpretation supplies explicit numbers; the script is deterministic and has no AI API, auto-scene detection or exact reference-matching claim. Grain, bloom, masks and local adjustments cannot be encoded by a single 3D LUT.

`create_lut_package.py` stores the complete recipe and engine version, serializes it, regenerates a second LUT and requires byte-identical SHA-256. Previews re-read `look.cube` and use application strength 1.0. LUT and recipe hashes, color assumptions, preview dimensions and source hash are recorded. Replay fixes LUT content, not the exact PNG bytes across different Pillow versions or a new input image. Warnings remain visible in `validation.json`; visual acceptance is a human decision.

## Creative controls

| Parameter | Accepted range |
| --- | --- |
| strength | 0..1, baked into the exported LUT |
| contrast, saturation | 0..3 |
| warmth, curve | -1..1 |
| exposure | -8..8 stops (creative code-value adjustment, not scene-linear exposure recovery) |
| lift | -0.5..0.5 |
| bleach | 0..1 |
| shadow/mid/highlight tint | Three RGB offsets, each -0.5..0.5 |
| size | 2..128; normally use 33 |

Large values may intentionally clip or tint; range validation does not promise a good-looking result. Use modest values and selected-photo comparisons. Skin protection restrains colors in a heuristic hue/saturation/luminance region; it cannot distinguish skin from similarly colored objects. It does not alter a neutral/identity recipe.

## Color handling

Photo paths apply EXIF orientation before resizing. Embedded ICC RGB profiles are converted with Pillow/LittleCMS to sRGB; untagged images are assumed sRGB and this is recorded. Supported RGBA/palette alpha is preserved in adjusted images; comparison sheets flatten to RGB for display. Output PNGs receive an sRGB ICC tag. Invalid ICC profiles and unsupported image modes fail visibly. No support is implied for RAW, HEIC decoding, 16-bit, HDR or automatic Log detection.

For technical LUT preview/application tools, `--color-mode encoded-rgb` explicitly preserves source code values instead of ICC-normalizing them. Camera packaging uses `--preview-color-mode encoded-rgb`. Input must already match the declared LUT source; output is untagged and needs the correct target view/profile in a managed editor. Side-by-side source and target encodings are diagnostic code-value views, not a color-managed display match. The one-command creator does not offer this mode because it produces sRGB creative recipes only.

## Validation and limits

Structural errors stop the one-command delivery. The normalized reader supports only 3D LUTs, default 0..1 domains and finite 0..1 outputs. Non-default domains are explicitly rejected rather than ignored. This does not mean extended-range LUTs are invalid in other tools.

Quality warnings include interior clipping, neutral channel drift, grid luminance reversals, descending neutral steps and abrupt changes in neutral-ramp slopes. These are sampled numerical heuristics, not a perceptual banding detector, measured film emulation, skin-quality score or proof of real-camera/editor compatibility. Intentional stylization may trigger warnings. The delivery status distinguishes `PASS` from `PASS_WITH_WARNINGS`.

Run `python scripts/test_lut_workflow.py` to check identity, channel order, rejected inputs, ICC conversion, EXIF/alpha, exact recipe replay, same-export preview pixels, batch consistency and overwrite protection.
