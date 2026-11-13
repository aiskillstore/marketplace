# Technical Color Science

## Decision Rules

Use `scripts/generate_technical_lut.py` when the transform can be described by:

- Source RGB primaries.
- Source transfer function.
- Target RGB primaries.
- Target transfer function.
- Optional exposure and tone mapping.

Use `scripts/ocio_generate_lut.py` when the user provides an OCIO config or needs exact ACES, show, camera, look, display, or facility pipeline behavior.

Use creative LUT generation only when the user asks for a style or look, not a color-managed conversion.

## Built-In RGB Primaries

Supported keys:

- `srgb`, `rec709`
- `display-p3`, `p3-d65`
- `rec2020`, `bt2020`
- `acescg`, `aces-ap1`
- `aces2065-1`, `aces-ap0`
- `panasonic-v-gamut`, `v-gamut`

ACES AP0/AP1 use an ACES D60 white point and Bradford chromatic adaptation when converting to D65 spaces.

## Built-In Transfer Functions

Supported keys:

- `linear`
- `srgb`
- `rec709`
- `gamma2.2`
- `gamma2.4`
- `pq`
- `hlg`
- `panasonic-vlog`, `v-log`

PQ uses ST 2084 with configurable source and target peak nits. HLG uses the standard HLG OETF/EOTF constants. V-Log uses the common Panasonic V-Log curve constants and V-Gamut primaries, but generated LUTs are not official Panasonic LUTs.

## Baking a Technical Transform with a Creative Look

Apply stages in signal order: camera encoding conversion first, then the creative look in the resulting display-referred space. Use scripts/bake_lut_chain.py to sample that ordered pipeline into one .cube when the destination needs one file. Keep both source LUTs when separate control is required. The baker rejects non-normalized domains and extended-range outputs; it does not infer whether adjacent stages use compatible color spaces.

## Examples

Panasonic V-Log / V-Gamut to Rec.709 with conservative highlight compression:

```bash
python scripts/generate_technical_lut.py --source-space panasonic-v-gamut --source-transfer panasonic-vlog --target-space rec709 --target-transfer rec709 --tone-map luminance-reinhard --size 33 --output vlog-vgamut-to-rec709.cube
```

Display P3 image pipeline to sRGB:

```bash
python scripts/generate_technical_lut.py --source-space display-p3 --source-transfer srgb --target-space srgb --target-transfer srgb --size 33 --output p3-to-srgb.cube
```

ACEScg linear to Rec.709 display-referred preview:

```bash
python scripts/generate_technical_lut.py --source-space acescg --source-transfer linear --target-space rec709 --target-transfer rec709 --tone-map luminance-reinhard --size 33 --output acescg-to-rec709-preview.cube
```

Bake through OpenColorIO:

```bash
python scripts/ocio_generate_lut.py --config config.ocio --source "ACEScg" --target "Output - Rec.709" --size 33 --output ocio-rec709.cube
```

## Delivery Notes

Always report the exact assumptions used. For camera logs, include whether the LUT is a practical preview transform, a creative look, or a vendor/show-accurate transform.

For Panasonic LUMIX DC-S9, the official manual accepts `.cube` 3D LUT sizes from 2 through 33 points. Use 33 for the general-purpose default unless the destination calls for a smaller file; do not export 65-point files for this camera. Check `references/camera-compatibility.md` for range, Photo Style metadata, and card filename constraints.

For HDR to SDR transforms, ask the user for the intended peak nits and tone mapping preference. If they do not know, use `--tone-map luminance-reinhard` as a safe preview default and say it is a practical preview transform.

Validation warnings about interior clipping can be expected when mapping wide-gamut or HDR/Log sources into Rec.709 or sRGB. Treat them as delivery notes rather than automatic failures unless the request requires strict gamut preservation.
