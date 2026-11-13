---
name: generate-lut
license: MIT
metadata:
  version: "5.0.3"
description: Generate creative .cube LUTs from photo color-grading requests, preview the exported LUT on a photo, and save a reusable recipe. Use for warm film looks, portraits, travel or street photography, LUT strength adjustments, batch photo grading, and LUT validation. Also supports explicitly specified technical color transforms, ordered LUT chains, and documented camera checks.
---

# 映色 · 一键生成 LUT

New users: see [README.md](README.md) for real-photo comparisons, installation, and a first-run example.

## Overview

Create practical `.cube` 3D LUTs with deterministic scripts, preview them on images or generated test charts, and validate the generated files before delivery. Support both creative display-referred looks and technical color transforms.

## Workflow

1. Classify the request as creative look, technical transform, OCIO pipeline bake, preview/application, batch operation, or validation.
2. For a complete creative delivery, prefer `scripts/create_lut_package.py`: one final LUT, exact-LUT previews, a replayable recipe, validation report, manifest and ZIP. Default to size 33 and strength 0.65. Use `scripts/generate_cube_lut.py` for LUT-only generation.
3. For built-in technical transforms, use `scripts/generate_technical_lut.py` after confirming source/target primaries and transfer functions.
4. For show pipelines, camera transforms beyond the built-ins, ACES config workflows, or facility-managed color, use `scripts/ocio_generate_lut.py` with a user-supplied OCIO config.
5. For previews, use the user's sample image when provided; otherwise run `scripts/create_test_assets.py` if needed, then use `assets/neutral-ramp.png` and `assets/color-checker.png`.
6. Always run `scripts/validate_lut.py` on generated or edited `.cube` files before handing them over.
7. Deliver the `.cube` file, at least one preview image when possible, and a short note about intended use, source/target assumptions, and limits.

## First Successful Run

When a new user wants to try the skill but has no photo ready, use `python scripts/run_demo.py --example portrait --output-dir delivery/first-look`. It uses a bundled, credited sample and makes no network calls. With the user's ordinary photo, use the one-command creator directly. Ask for only the missing essentials, show one result by default, and keep advanced technical controls out of the initial interaction. Report the actual output paths and display the comparison when the host can render it.

## One-Command Creative Delivery (v5)

Translate a mood description into explicit creative parameters, then run:

```bash
python scripts/create_lut_package.py --look warm-film --strength 0.65 --input sample.jpg --shadow-tint -0.02 0.03 0.04 --highlight-tint 0.04 0.02 -0.01 --description "暖高光、微青暗部、克制肤色" --output-dir delivery/my-look
```

Without `--input`, the package uses synthetic neutral/color charts and labels them as test charts, not real-photo acceptance. Pillow with LittleCMS is required for previews (`python -m pip install Pillow` only if missing); generation and LUT validation themselves use the Python standard library.

**Strength is baked once.** Apply the exported LUT at 1.0 for delivery previews. `--strength` on single/batch preview tools is an additional artistic amount, not the generator's baked strength. If a weaker result is selected for final delivery, bake that change into a new LUT and regenerate the preview from that exact file. Never show a weakened preview while exporting the stronger original.

The package writes `look.cube`, `recipe.json`, adjusted/comparison PNGs, `validation.json`, `manifest.json`, a short Chinese usage note, and a sibling ZIP. A quality warning is reported as `PASS_WITH_WARNINGS`, not silently treated as visual approval. Existing delivery folders/ZIPs are refused. No external publication is performed.

Replay a saved recipe without parameter overrides:

```bash
python scripts/create_lut_package.py --recipe delivery/my-look/recipe.json --input another.jpg --output-dir delivery/replayed-look
```

The recipe records all final parameters, working space, strength, skin-protection flag, LUT size and engine version. Each package regenerates the serialized recipe and compares LUT SHA-256 before delivery. A recipe change means a new look, not a byte-identical replay. The description is provenance text; the script does not independently interpret language or recover reference-image grades.

For ranges, photo color management, raw-code technical previews and quality limits, read `references/v5-workflow.md`. To verify the installed workflow, run `python scripts/test_lut_workflow.py`.

## Creative Look Review

For creative-look exploration, use a human choice loop instead of automatic scene labels or per-shot matching. Translate the requested mood or a supplied style reference into explicit controls such as contrast, warmth, saturation, shadow tint, highlight tint, and tone curve. Do not claim to recover an exact grade from a reference image.

When the user is exploring, generate up to three controlled candidates from one base look. Vary only one or two controls in a round. Apply every candidate to the same user-selected image, or to one to three frames the user identifies as representative, then assemble a review sheet:

    python scripts/compare_lut_candidates.py --input sample.png --lut subtle.cube --lut balanced.cube --lut expressive.cube --output look-review.png

The sheet is for visual selection; it does not decide which look is best. If the user already specified a final look, generate one LUT directly instead of adding unnecessary options. For a video, do not automatically classify or match each shot. A single creative LUT is a global look, while exposure, white balance, and shot-specific corrections remain separate grading work.

Read references/creative-iteration.md for the detailed review workflow and preview limits.

## Bake a LUT Chain

When the user needs a single file containing a technical conversion followed by a creative look, compose the stages in that order. The order of repeated --lut arguments is the application order. Keep separate files available when the user needs independent controls.

    python scripts/bake_lut_chain.py --lut vlog-to-rec709.cube --lut warm-film.cube --size 33 --output camera-warm-film.cube

The baker records each stage filename and SHA-256 in the output comments. It accepts only normalized 3D .cube inputs with 0..1 domains and values; it rejects extended-range inputs rather than clipping them. Read references/lut-chain-baking.md for color-space order and limits.

## Camera Compatibility

Use scripts/check_camera_compatibility.py only with a camera profile based on official documentation. Create an empty profile with --create-template, then fill and verify the exact camera model and documented import constraints. Undocumented limits stay unspecified; input encoding is optional when the camera accepts LUTs for multiple Photo Styles. An unverified or incomplete profile must return UNCONFIRMED, never a compatibility claim.

    python scripts/check_camera_compatibility.py --create-template camera-profile.json
    python scripts/check_camera_compatibility.py --lut camera-warm-film.cube --profile camera-profile.json
    python scripts/check_camera_compatibility.py --lut camera-warm-film.cube --profile references/camera-profiles/panasonic-dc-s9.json --card-filesystem FAT32

Read references/camera-compatibility.md before creating or using a device profile.

For a camera-ready folder and ZIP, use `scripts/build_camera_lut_package.py`. It can generate a built-in look or package an existing `.cube`, apply a requested strength, write the camera metadata tag, run the profile check, and include a preview for a supplied image.

    python scripts/build_camera_lut_package.py --look warm-film --strength 0.55 --size 33 --lumix-photo-style VLOG --card-filesystem FAT32 --name WARMFILM --preview-image sample.jpg --output-dir delivery/warm-film

The package is labeled as needing review if the profile check does not pass. It cannot prove real-camera import or image quality.

## Script Guide



Generate a creative LUT:

```bash
python scripts/generate_cube_lut.py --look cinematic-teal-orange --strength 0.65 --size 33 --output output.cube
```

For Panasonic LUMIX DC-S9, optionally specify the LUT's base Photo Style tag, for example `--lumix-photo-style VLOG`. Read `references/camera-compatibility.md` for supported tags and import checks.

Generate a technical LUT with built-in color science:

```bash
python scripts/generate_technical_lut.py --source-space panasonic-v-gamut --source-transfer panasonic-vlog --target-space rec709 --target-transfer rec709 --tone-map luminance-reinhard --size 33 --output vlog-to-rec709.cube
```

Bake a LUT through OpenColorIO when a config is supplied:

```bash
python scripts/ocio_generate_lut.py --config config.ocio --source "Input - Panasonic V-Log" --target "Rec.709 Display" --size 33 --output ocio-baked.cube
```

Inspect available built-in and optional capabilities:

```bash
python scripts/color_science_status.py
```

Apply a LUT preview:

```bash
python scripts/apply_lut_preview.py --input sample.png --lut output.cube --output preview.png --mode comparison --strength 1.0
```

Adjust any normalized `.cube` LUT toward identity and save a new LUT:

```bash
python scripts/mix_lut_strength.py --input source.cube --strength 0.45 --output source-45.cube
```

Apply a LUT at a chosen strength to an image folder. The script writes PNG copies to a separate output folder and leaves the source files untouched:

```bash
python scripts/batch_apply_lut.py --input photos/ --lut output.cube --strength 1.0 --output-dir graded-photos/
```

Read `references/batch-operations.md` for strength blending, folder output, supported image modes, and color-domain limits.

Create fallback preview charts:

```bash
python scripts/create_test_assets.py --output-dir assets
```

Validate a LUT:

```bash
python scripts/validate_lut.py output.cube
```

Use `--look neutral` for test identity LUTs. Use `--look custom` with `--contrast`, `--saturation`, `--warmth`, `--exposure`, `--lift`, `--curve`, `--bleach` and three-value RGB controls `--shadow-tint`, `--mid-tint`, `--highlight-tint` when a preset is insufficient. Skin protection is enabled by default; `--no-protect-skin` disables it. It is a hue-based restraint, not face or object detection. `neutral` remains identity with the default protection enabled.

## References

Read `references/lut-format.md` when changing parser/writer behavior or explaining `.cube` compatibility.

Read `references/batch-operations.md` when adjusting the strength of an external LUT or applying it to multiple still images.

Read `references/looks.md` when selecting or tuning a creative preset from natural-language style requests.

Read `references/color-workflow.md` when distinguishing creative looks from technical transforms or planning previews.

Read `references/technical-color-science.md` when generating technical conversion LUTs, choosing primaries/transfer functions, or deciding whether an OCIO config is required.

## Guardrails

Do not present creative LUTs as mathematically accurate camera, scene-linear, ACES, ICC, or display transforms. For technical transforms, name the source RGB primaries, source transfer, target RGB primaries, target transfer, tone map, LUT size, and whether output was clipped.

Do not claim a built-in camera conversion is an official vendor LUT. For exact camera/vendor/show looks, ask for the official LUT or an OCIO config and bake through `scripts/ocio_generate_lut.py`.

Keep neutral grey reasonably stable unless the user explicitly asks for a tinted look. Warn when a strong style intentionally shifts greys, clips saturated colors, or may behave differently across editors.

Prefer `.cube` for broad compatibility. Avoid exporting many sizes unless the user needs them; `33x33x33` is a good default balance, `17` is light and coarse, and `65` is larger and smoother.

The shared normalized reader rejects non-default domains, 1D/combined LUTs, duplicate headers, malformed RGB rows, non-finite values and extended-range outputs; it never silently clips or remaps them. For deliberate extended-range technical output, use the separate managed workflow; normalized preview/validation tools will reject it.
