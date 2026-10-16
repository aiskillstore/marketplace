---
name: sweety-image-privacy
description: Use when sanitizing image privacy metadata, removing GPS/source traces, auditing macOS xattrs, or preparing images with iPhone-like camera metadata before publishing or AI-detection checks.
version: 1.1.0
metadata:
  openclaw:
    homepage: https://github.com/sweety/sweety-skills#sweety-image-privacy
    requires:
      anyBins:
        - bun
        - npx
---

# Image Privacy Sanitizer

Sanitizes image privacy metadata before publishing or detector testing. It removes GPS and origin/source fields, clears macOS download/source extended attributes when possible, and writes an iPhone 16 Pro Max camera metadata profile.

This does not guarantee an image will pass AI-generation detectors. Metadata can support a real-camera workflow, but detectors can still use pixels, compression artifacts, model fingerprints, and other signals.

## Script Directory

Scripts are in the `scripts/` subdirectory. `{baseDir}` = this GUIDE.md file's directory path. Resolve `${BUN_X}` runtime: if `bun` installed → `bun`; if `npx` available → `npx -y bun`; else suggest installing bun. Replace `{baseDir}` and `${BUN_X}` with actual values.

| Script | Purpose |
|--------|---------|
| `scripts/main.ts` | CLI for privacy sanitization, iPhone-like camera metadata, and JSON audit reports |

## Usage

```bash
${BUN_X} {baseDir}/scripts/main.ts <input> [options]
```

When `<input>` is a directory, all supported image files within the directory (and subdirectories) are processed recursively.

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `<input>` | | File or directory | Required |
| `--output` | `-o` | Output file path (only for single file input) | Default: overwrite input or create `-exif` copy when `--keep` |
| `--keep` | `-k` | Keep original file when processing in place | false |
| `--recursive` | `-r` | Process directories recursively (default for directories) | true for directories |
| `--json` | | Emit JSON report | false |
| `-h`, `--help` | | Show help | |

## Notes

- Requires `sharp` to be available in the runtime environment.
- If `sharp` is not installed, the script will prompt to install it with `bun add sharp` or `npm install sharp`.
- For safe in-place overwrite, the script writes to a temporary file then atomically replaces the original.
- With `exiftool`, the script removes all embedded metadata first, then writes an iPhone 16 Pro Max profile: `Make`, `Model`, `HostComputer`, `LensModel`, focal length, 35mm focal length, aperture, exposure program, metering mode, flash, white balance, and color space.
- GPS and source/origin fields are removed. The JSON report audits whether GPS, source EXIF, and required macOS source xattrs remain.
- On macOS, the script clears Finder "Where from" and quarantine metadata. `com.apple.provenance` may be system-managed and can reappear locally; treat it as an audit signal, not a guaranteed blocker for web upload bytes.
- Do not claim a generated image is a real camera photograph merely because metadata was rewritten.

## Examples

```bash
# Process single image, overwrite original
${BUN_X} {baseDir}/scripts/main.ts photo.jpg

# Process single image, keep original
${BUN_X} {baseDir}/scripts/main.ts photo.jpg --keep

# Process directory recursively (default behavior)
${BUN_X} {baseDir}/scripts/main.ts /user/tmp/

# Process directory, keep originals
${BUN_X} {baseDir}/scripts/main.ts /user/tmp/ --keep

# JSON audit output
${BUN_X} {baseDir}/scripts/main.ts /user/tmp/ --json
```

**Output**:
```
/user/tmp/photo1.jpg → /user/tmp/photo1.jpg (exiftool)
/user/tmp/subdir/photo2.png → /user/tmp/subdir/photo2.png (exiftool)
```

**JSON output includes**:

- `camera`: written/observed camera profile fields.
- `privacy.gpsPresent`: whether GPS remains.
- `privacy.sourceExifPresent`: whether source/origin EXIF fields remain.
- `privacy.requiredMacSourceXattrsPresent`: required macOS source attributes that still remain.

## Extension Support

Custom configurations via EXTEND.md. See **Script Directory** section for the expected base directory.
