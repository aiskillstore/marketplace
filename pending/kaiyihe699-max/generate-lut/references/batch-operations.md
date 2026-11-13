# LUT Strength and Batch Image Operations

## Adjusting an Existing LUT

Use `scripts/mix_lut_strength.py` when an existing `.cube` look is too strong. The operation blends each LUT output toward the identity transform and writes a new file:

```bash
python scripts/mix_lut_strength.py --input source.cube --strength 0.45 --output source-45.cube
```

`--strength 0` produces identity; `--strength 1` reproduces the source LUT. The source is never overwritten. The tool currently supports normalized 3D `.cube` files with `DOMAIN_MIN 0`, `DOMAIN_MAX 1`, and RGB output values in `0..1`. It refuses extended-range data rather than clipping it.

Strength blending is primarily an artistic control for creative looks. Blending a technical camera or display conversion toward identity changes that transform's accuracy; keep exact technical transforms at full strength unless an approximation is intentional.

`scripts/apply_lut_preview.py` and `scripts/batch_apply_lut.py` accept the same strength range without first creating a derivative LUT.

## Applying to Still Images

Use one image or a folder of stills:

```bash
python scripts/batch_apply_lut.py --input photos/ --lut look.cube --strength 1.0 --output-dir graded/
```

Folder search is recursive. Results are PNG files in a separate output folder, preserving subfolders and adding `-lut` to each filename. A `batch-report.json` records each success or failure. Existing outputs are not overwritten. CMYK and high-bit-depth image modes are rejected; RGB, RGBA, grayscale, and palette images are supported. Transparent palette images retain alpha. The LUT must use a 0..1 domain and finite 0..1 output values; extended-range LUTs are rejected without clipping.

By default, all photo entry points apply EXIF orientation, convert embedded ICC RGB profiles into sRGB, assume sRGB for untagged images, preserve supported alpha, and tag PNG results as sRGB. A damaged or unsupported ICC is rejected, not silently ignored. The batch report records each image's color action. This is an 8-bit photo workflow, not RAW/HDR development.

For a deliberate technical LUT, pass `--color-mode encoded-rgb` with a frame already encoded in the LUT's declared source domain. This bypasses ICC conversion explicitly and leaves the result untagged; assign the correct target profile/viewing transform in the destination editor. It is not automatic Log detection. Camera packaging uses `--preview-color-mode encoded-rgb` for the same purpose.

A LUT generated at strength 0.65 already contains that amount. Apply at 1.0 to match the exported file. An application strength below 1.0 is an additional adjustment and must be baked into a derivative LUT before claiming preview/export equivalence.
